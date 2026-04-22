from __future__ import annotations

import json
import re
from pathlib import Path

from src.core.database import db_connection, get_repo_root
from src.payroll.extractor_ocr import OcrUnavailableError, ocr_image
from src.payroll.extractor_pdf import extract_text_from_pdf
from src.payroll.normalizer import DraftPayrollLine, DraftPaystub, parse_date_any, parse_money
from src.payroll.pii_scrubber import scrub_pii
from src.payroll.repository import delete_draft_for_document, fetch_document, insert_draft_lines, insert_draft_paystub
from src.payroll.validator import validate_paystub
from src.services.audit import write_audit_log


class PayrollIngestError(RuntimeError):
    pass


# Money token: optional $, optional parens for negatives, commas, 2 decimal places.
_MONEY_TOKEN_RE = re.compile(
    r"\(?\$?\s*[\d,]+(?:\.\d{2})?\s*\)?",
    re.MULTILINE,
)

# Lines whose entire label is a table header (not a line item).
_HEADER_LABELS = frozenset(
    {
        "description",
        "amount",
        "current",
        "ytd",
        "rate",
        "hours",
        "this period",
        "year to date",
        "earnings",
        "deductions",
        "taxes",
        "tax",
        "before tax deductions",
        "after tax deductions",
        "employee",
        "employer",
        "totals",
        "total",
    }
)


def _nonempty_lines(text: str) -> list[str]:
    return [ln.strip() for ln in (text or "").splitlines() if ln.strip()]


def _line_has_ytd(line: str) -> bool:
    return bool(re.search(r"\bytd\b|\byear\s*to\s*date\b", line, re.I))


def _infer_pay_date(text: str) -> str | None:
    """Resolve pay / check date from stub text (native path)."""

    t = text or ""
    pay_date: str | None = None

    # Inline label (single line or wrapped).
    m = re.search(
        r"(?im)\b(?:pay|check|payment)\s*date\b\s*[:\-]?\s*"
        r"([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4}|[A-Za-z]{3,9}\s+\d{1,2},\s+\d{4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})",
        t,
    )
    if m:
        pay_date = parse_date_any(m.group(1).strip())

    pay_date_label_patterns = [
        r"(?im)^\s*pay\s*date\s*[:\-]?\s*(.+?)\s*$",
        r"(?im)^\s*date\s*paid\s*[:\-]?\s*(.+?)\s*$",
        r"(?im)^\s*check\s*date\s*[:\-]?\s*(.+?)\s*$",
        r"(?im)^\s*payment\s*date\s*[:\-]?\s*(.+?)\s*$",
        r"(?im)^\s*paid\s*on\s*[:\-]?\s*(.+?)\s*$",
        r"(?im)^\s*payday\s*[:\-]?\s*(.+?)\s*$",
        r"(?im)^\s*issue\s*date\s*[:\-]?\s*(.+?)\s*$",
        r"(?im)^\s*pay\s*date\s*/\s*check\s*date\s*[:\-]?\s*(.+?)\s*$",
    ]
    for pat in pay_date_label_patterns:
        if pay_date:
            break
        m = re.search(pat, t)
        if not m:
            continue
        raw = m.group(1).strip()
        pay_date = parse_date_any(raw)
        if pay_date:
            break

    if not pay_date:
        m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", t)
        if m:
            pay_date = parse_date_any(m.group(1))
        else:
            m = re.search(r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b", t)
            if m:
                pay_date = parse_date_any(m.group(1))
    if not pay_date:
        m = re.search(r"\b(\d{4}/\d{2}/\d{2})\b", t)
        if m:
            pay_date = parse_date_any(m.group(1))
    if not pay_date:
        m = re.search(r"\b([A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})\b", t)
        if m:
            pay_date = parse_date_any(m.group(1))

    return pay_date


def _infer_pay_period(text: str) -> tuple[str | None, str | None]:
    """Extract pay period start/end when present."""

    t = text or ""
    period_start: str | None = None
    period_end: str | None = None

    # Range on one line near "pay period" / "for period".
    m = re.search(
        r"(?is)(?:pay\s*period|period\s*(?:covered|ending)?|for\s+period)\s*[:.\s-]*"
        r"\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*(?:to|through|[-–—])\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        t,
    )
    if m:
        period_start = parse_date_any(m.group(1))
        period_end = parse_date_any(m.group(2))
        if period_start and period_end:
            return period_start, period_end

    m = re.search(r"(?im)\bpay\s*period\b\s*[:\-]?\s*(.+)$", t)
    if m:
        rhs = m.group(1).strip()
        m2 = re.search(
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*(?:to|\-|–|—)\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            rhs,
        )
        if m2:
            period_start = parse_date_any(m2.group(1))
            period_end = parse_date_any(m2.group(2))

    label_map = [
        ("period beginning", "start"),
        ("pay period start", "start"),
        ("period start", "start"),
        ("start date", "start"),
        ("begin date", "start"),
        ("period ending", "end"),
        ("pay period end", "end"),
        ("period end", "end"),
        ("end date", "end"),
    ]
    for label, slot in label_map:
        m = re.search(rf"(?im)\b{re.escape(label)}\b\s*[:\-]?\s*(.+)$", t)
        if not m:
            continue
        d = parse_date_any(m.group(1))
        if not d:
            continue
        if slot == "start" and not period_start:
            period_start = d
        if slot == "end" and not period_end:
            period_end = d

    return period_start, period_end


def _money_from_labeled_line(lines: list[str], patterns: list[str], *, skip_ytd_lines: bool) -> float | None:
    """Find the strongest match for gross or net across lines (prefer non-YTD rows, then 'total')."""

    best_val: float | None = None
    best_rank = -1

    for line in lines:
        if skip_ytd_lines and _line_has_ytd(line):
            continue
        lower = line.lower()
        for pat in patterns:
            m = re.search(pat, line, re.I)
            if not m:
                continue
            val = parse_money(m.group(1))
            if val is None:
                continue
            rank = 1
            if "total" in lower:
                rank = 3
            elif "gross" in lower or "net" in lower:
                rank = 2
            if rank > best_rank:
                best_rank = rank
                best_val = val
            break

    return best_val


def _infer_gross_pay(text: str, lines: list[str]) -> float | None:
    patterns = [
        r"(?i)\b(?:total\s+)?gross(?:\s+pay|\s+earnings)?\b\s*[:\-]?\s*(\(?\$?\s*[\d,]+(?:\.\d{2})?\s*\)?)",
        r"(?i)\bgross\s*(?:pay|earnings)\b\s*[:\-]?\s*(\(?\$?\s*[\d,]+(?:\.\d{2})?\s*\)?)",
        r"(?i)\btotal\s+earnings\b\s*[:\-]?\s*(\(?\$?\s*[\d,]+(?:\.\d{2})?\s*\)?)",
    ]
    v = _money_from_labeled_line(lines, patterns, skip_ytd_lines=True)
    if v is not None:
        return v

    for pat in [
        r"(?im)\bgross\s*pay\b\s*[:\-]?\s*([$\(\)\d,.\s-]+)$",
        r"(?im)\btotal\s*gross\b\s*[:\-]?\s*([$\(\)\d,.\s-]+)$",
    ]:
        m = re.search(pat, text or "")
        if m:
            got = parse_money(m.group(1))
            if got is not None:
                return got
    return None


def _infer_net_pay(text: str, lines: list[str]) -> float | None:
    patterns = [
        r"(?i)\bnet\s*pay\b\s*[:\-]?\s*(\(?\$?\s*[\d,]+(?:\.\d{2})?\s*\)?)",
        r"(?i)\btotal\s+net\b\s*[:\-]?\s*(\(?\$?\s*[\d,]+(?:\.\d{2})?\s*\)?)",
        r"(?i)\btake[\s-]*home(?:\s+pay)?\b\s*[:\-]?\s*(\(?\$?\s*[\d,]+(?:\.\d{2})?\s*\)?)",
        r"(?i)\bamount\s+payable\b\s*[:\-]?\s*(\(?\$?\s*[\d,]+(?:\.\d{2})?\s*\)?)",
        r"(?i)\bnet\s+amount\b\s*[:\-]?\s*(\(?\$?\s*[\d,]+(?:\.\d{2})?\s*\)?)",
    ]
    # Do not skip YTD-tagged lines: many stubs put Current and YTD on the same "Net pay" row.
    v = _money_from_labeled_line(lines, patterns, skip_ytd_lines=False)
    if v is not None:
        return v

    for pat in [
        r"(?im)\bnet\s*pay\b\s*[:\-]?\s*([$\(\)\d,.\s-]+)$",
        r"(?im)\btotal\s*net\b\s*[:\-]?\s*([$\(\)\d,.\s-]+)$",
    ]:
        m = re.search(pat, text or "")
        if m:
            got = parse_money(m.group(1))
            if got is not None:
                return got
    return None


def _infer_basic_fields_from_text(text: str) -> tuple[str | None, str | None, str | None, float | None, float | None]:
    """Heuristic extraction for draft paystub fields (native text, Step 23)."""

    lines = _nonempty_lines(text)
    pay_date = _infer_pay_date(text)
    period_start, period_end = _infer_pay_period(text)
    gross_pay = _infer_gross_pay(text, lines)
    net_pay = _infer_net_pay(text, lines)
    return pay_date, period_start, period_end, gross_pay, net_pay


def _normalize_line_description(raw: str) -> str:
    s = re.sub(r"\s+", " ", (raw or "").strip())
    return s.strip(" :.-—")


def _categorize_line(description: str) -> str:
    d = description.lower()
    if any(
        x in d
        for x in (
            "federal",
            "state inc",
            "state tax",
            "fica",
            "medicare",
            "social sec",
            "social security",
            "ss ee",
            "eic",
            "local tax",
            "city tax",
            "oasdi",
            "withholding tax",
        )
    ):
        return "tax"
    if " tax" in d or d.endswith("tax") or d.startswith("tax "):
        return "tax"
    if any(
        x in d
        for x in (
            "401",
            "403",
            "hsa",
            "fsa",
            "health ins",
            "medical",
            "dental",
            "vision",
            "life ins",
            "disability",
            "garnish",
            "child support",
            "union",
            "dues",
            "pension",
            "roth",
            "deferral",
            "cafeteria",
            "pre-tax",
            "pretax",
        )
    ):
        return "deduction"
    if any(
        x in d
        for x in (
            "regular",
            "salary",
            "hourly",
            "overtime",
            " ot",
            "bonus",
            "commission",
            "vacation",
            "pto",
            "sick",
            "holiday",
            "bereavement",
            "earning",
            "wage",
            "pay",
        )
    ):
        return "earning"
    return "earning"


def _parse_line_with_trailing_amounts(line: str) -> tuple[str, float, float | None] | None:
    """Parse 'Description  current [ytd]' when trailing tokens look like money."""

    matches = list(_MONEY_TOKEN_RE.finditer(line))
    if not matches:
        return None
    # Hours × rate × amount rows often expose 3+ currency-like tokens; skip to reduce junk lines.
    if len(matches) >= 3:
        return None

    if len(matches) >= 2:
        m_cur, m_ytd = matches[-2], matches[-1]
        desc = line[: m_cur.start()].strip()
        cur = parse_money(m_cur.group(0))
        ytd = parse_money(m_ytd.group(0))
    else:
        m0 = matches[-1]
        desc = line[: m0.start()].strip()
        cur = parse_money(m0.group(0))
        ytd = None

    if cur is None:
        return None

    desc_n = _normalize_line_description(desc)
    if len(desc_n) < 3:
        return None
    if desc_n.lower() in _HEADER_LABELS:
        return None
    if re.fullmatch(r"[\d\s$,.-]+", desc_n):
        return None
    if re.match(r"^(page|continued|www\.|http)\b", desc_n, re.I):
        return None

    return desc_n, cur, ytd


def _extract_payroll_lines_from_text(text: str, *, max_lines: int = 55) -> tuple[list[DraftPayrollLine], float | None]:
    """Extract draft line items from native stub text (conservative heuristics)."""

    lines_in = _nonempty_lines(text)
    out: list[DraftPayrollLine] = []
    seen: set[tuple[str, float]] = set()
    taxes_deds = 0.0
    have_td = False

    for raw_line in lines_in:
        if len(out) >= max_lines:
            break
        if _line_has_ytd(raw_line) and re.search(r"\b(total|gross|net)\b", raw_line, re.I):
            continue

        parsed = _parse_line_with_trailing_amounts(raw_line)
        if parsed is None:
            continue
        desc, amount, ytd_amount = parsed

        if abs(amount) > 9_999_999 or (ytd_amount is not None and abs(ytd_amount) > 9_999_999):
            continue
        if abs(amount) < 0.005 and (ytd_amount is None or abs(ytd_amount) < 0.005):
            continue

        key = (desc.lower(), round(amount, 2))
        if key in seen:
            continue
        seen.add(key)

        cat = _categorize_line(desc)
        if cat in ("tax", "deduction") and amount > 0:
            taxes_deds += amount
            have_td = True
        elif cat in ("tax", "deduction") and amount < 0:
            taxes_deds += abs(amount)
            have_td = True

        out.append(
            DraftPayrollLine(
                category=cat,
                description=desc,
                amount=amount,
                ytd_amount=ytd_amount,
                display_order=len(out),
            )
        )

    td_total = round(taxes_deds, 2) if have_td else None
    return out, td_total


def _looks_like_scanned_pdf(*, page_count: int, extracted_text: str) -> bool:
    if page_count <= 0:
        return False
    txt = (extracted_text or "").strip()
    if len(txt) < 50:
        return True
    alpha = sum(1 for c in txt if c.isalpha())
    ratio = alpha / max(1, len(txt))
    return ratio < 0.05


def _draft_lines_to_json(lines: list[DraftPayrollLine]) -> list[dict]:
    return [
        {
            "category": ln.category,
            "description": ln.description,
            "amount": ln.amount,
            "ytd_amount": ln.ytd_amount,
            "display_order": ln.display_order,
        }
        for ln in lines
    ]


def ingest_payroll_document(document_id: int) -> dict:
    repo_root = get_repo_root()

    with db_connection() as conn:
        doc = fetch_document(conn, document_id)
        if doc is None:
            raise PayrollIngestError("Document not found")
        if str(doc["module_owner"]) != "payroll":
            raise PayrollIngestError("Document module_owner must be 'payroll' for payroll ingest")
        if doc["member_id"] is None:
            raise PayrollIngestError("Payroll ingest requires document.member_id (upload with member_id)")

        write_audit_log(
            conn,
            document_id=document_id,
            actor="system",
            action="payroll_ingest_started",
            details=f"storage_path={doc['storage_path']}",
        )

        storage_path = str(doc["storage_path"])
        full_path = (repo_root / Path(storage_path)).resolve()

    if not full_path.exists():
        raise PayrollIngestError(f"Storage file not found: {storage_path}")

    raw_text = ""
    ocr_used = False
    suffix = full_path.suffix.lower()

    if suffix == ".pdf":
        pdf_res = extract_text_from_pdf(full_path)
        raw_text = pdf_res.text
        if not raw_text:
            raise PayrollIngestError(
                "No native PDF text found (likely scanned). OCR for scanned PDFs is not implemented yet. "
                "Try uploading an image (.png/.jpg) of the paystub for OCR, or install a PDF OCR pipeline."
            )
    elif suffix in {".png", ".jpg", ".jpeg"}:
        try:
            ocr_res = ocr_image(full_path)
            raw_text = ocr_res.text
            ocr_used = True
        except OcrUnavailableError as e:
            raise PayrollIngestError(str(e)) from e
    else:
        raise PayrollIngestError(f"Unsupported payroll file type: {suffix}")

    if not raw_text.strip():
        raise PayrollIngestError("Extracted text is empty")

    scrub = scrub_pii(raw_text)
    redacted_text = scrub.redacted_text

    pay_date, period_start, period_end, gross_pay, net_pay = _infer_basic_fields_from_text(redacted_text)
    draft_lines, lines_total_taxes_deductions = _extract_payroll_lines_from_text(redacted_text)

    validation = validate_paystub(
        pay_date=pay_date,
        period_start=period_start,
        period_end=period_end,
        gross_pay=gross_pay,
        net_pay=net_pay,
        lines_total_taxes_deductions=lines_total_taxes_deductions,
    )

    if not pay_date:
        pdf_diag = None
        if suffix == ".pdf":
            pdf_diag = {
                "page_count": getattr(pdf_res, "page_count", None),
                "text_chars": len(raw_text or ""),
                "likely_scanned": _looks_like_scanned_pdf(
                    page_count=int(getattr(pdf_res, "page_count", 0) or 0),
                    extracted_text=raw_text or "",
                ),
            }
        raise PayrollIngestError(
            "Could not infer pay_date from extracted text (required for draft paystub). "
            f"debug={{'file_type': '{suffix}', 'pdf': {pdf_diag}, 'redacted_chars': {len(redacted_text or '')}}}"
        )

    draft = DraftPaystub(
        pay_date=pay_date,
        period_start=period_start,
        period_end=period_end,
        gross_pay=gross_pay,
        net_pay=net_pay,
        currency="USD",
        lines=draft_lines,
    )

    with db_connection() as conn:
        doc = fetch_document(conn, document_id)
        if doc is None:
            raise PayrollIngestError("Document not found")

        member_id = int(doc["member_id"])
        institution_id = int(doc["institution_id"]) if doc["institution_id"] is not None else None

        delete_draft_for_document(conn, document_id)

        paystub_id = insert_draft_paystub(
            conn,
            document_id=document_id,
            member_id=member_id,
            institution_id=institution_id,
            draft=draft,
            validation_summary=json.dumps({"warnings": validation.warnings, "ok": validation.ok}),
        )
        inserted_lines = insert_draft_lines(conn, paystub_id=paystub_id, lines=draft_lines)

        conn.execute(
            "UPDATE documents SET status = ?, ocr_used = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;",
            ("in_review", 1 if ocr_used else 0, document_id),
        )

        write_audit_log(
            conn,
            document_id=document_id,
            actor="system",
            action="payroll_text_extracted",
            details=f"ocr_used={ocr_used}, chars={len(raw_text)}",
        )
        write_audit_log(
            conn,
            document_id=document_id,
            actor="system",
            action="payroll_pii_scrubbed",
            details=f"redactions={scrub.redaction_counts}",
        )
        write_audit_log(
            conn,
            document_id=document_id,
            actor="system",
            action="payroll_draft_stored",
            details=f"paystub_id={paystub_id}, lines={inserted_lines}, warnings={len(validation.warnings)}",
        )

    return {
        "ok": True,
        "document_id": document_id,
        "paystub_id": paystub_id,
        "document_status": "in_review",
        "ocr_used": ocr_used,
        "redaction_counts": scrub.redaction_counts,
        "draft": {
            "pay_date": draft.pay_date,
            "period_start": draft.period_start,
            "period_end": draft.period_end,
            "gross_pay": draft.gross_pay,
            "net_pay": draft.net_pay,
            "currency": draft.currency,
            "lines": _draft_lines_to_json(draft_lines),
        },
        "validation": {"ok": validation.ok, "warnings": validation.warnings},
    }
