from __future__ import annotations

import json
import re
from pathlib import Path

from src.core.database import db_connection, get_repo_root
from src.payroll.extractor_ocr import OcrUnavailableError, ocr_image
from src.payroll.extractor_pdf import extract_text_from_pdf
from src.payroll.normalizer import DraftPayrollLine, DraftPaystub, find_first_money, parse_date_any, parse_money
from src.payroll.pii_scrubber import scrub_pii
from src.payroll.repository import delete_draft_for_document, fetch_document, insert_draft_lines, insert_draft_paystub
from src.payroll.validator import validate_paystub
from src.services.audit import write_audit_log


class PayrollIngestError(RuntimeError):
    pass


def _infer_basic_fields_from_text(text: str) -> tuple[str | None, str | None, str | None, float | None, float | None]:
    """Heuristic extraction to create a minimal draft without LLM (Step 5B).

    Returns: pay_date, period_start, period_end, gross_pay, net_pay
    """

    t = text or ""

    # Try pay date.
    pay_date = None
    pay_date_hits: list[str] = []

    # First: inline label anywhere in a line (many paystubs put multiple fields on one line).
    m = re.search(
        r"(?im)\bpay\s*date\b\s*[:\-]?\s*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4}|[A-Za-z]{3,9}\s+\d{1,2},\s+\d{4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})",
        t,
    )
    if m:
        raw = m.group(1).strip()
        pay_date_hits.append(raw)
        pay_date = parse_date_any(raw)

    pay_date_label_patterns = [
        # Common
        r"(?im)^\s*pay\s*date\s*[:\-]?\s*(.+?)\s*$",
        r"(?im)^\s*date\s*paid\s*[:\-]?\s*(.+?)\s*$",
        r"(?im)^\s*check\s*date\s*[:\-]?\s*(.+?)\s*$",
        r"(?im)^\s*payment\s*date\s*[:\-]?\s*(.+?)\s*$",
        r"(?im)^\s*paid\s*on\s*[:\-]?\s*(.+?)\s*$",
        r"(?im)^\s*payday\s*[:\-]?\s*(.+?)\s*$",
        # Variants seen in some stubs
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
        pay_date_hits.append(raw)
        pay_date = parse_date_any(raw)
        if pay_date:
            break
    if not pay_date:
        # fallback: first recognizable date in doc
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
            # Month-name fallback: e.g., "Apr 15, 2026"
            m = re.search(r"\b([A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})\b", t)
            if m:
                pay_date = parse_date_any(m.group(1))

    # Pay period.
    period_start = None
    period_end = None
    m = re.search(r"(?im)\bpay\s*period\b\s*[:\-]?\s*(.+)$", t)
    if m:
        # Try split "MM/DD/YYYY - MM/DD/YYYY"
        rhs = m.group(1).strip()
        m2 = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*(?:to|\-)\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", rhs)
        if m2:
            period_start = parse_date_any(m2.group(1))
            period_end = parse_date_any(m2.group(2))

    for label, target in [
        ("period start", "start"),
        ("start date", "start"),
        ("period end", "end"),
        ("end date", "end"),
    ]:
        m = re.search(rf"(?im)\b{re.escape(label)}\b\s*[:\-]?\s*(.+)$", t)
        if not m:
            continue
        d = parse_date_any(m.group(1))
        if not d:
            continue
        if target == "start" and not period_start:
            period_start = d
        if target == "end" and not period_end:
            period_end = d

    # Gross / net.
    gross_pay = None
    net_pay = None
    for pat in [
        r"(?im)\bgross\s*pay\b\s*[:\-]?\s*([$\(\)\d,.\s-]+)$",
        r"(?im)\btotal\s*gross\b\s*[:\-]?\s*([$\(\)\d,.\s-]+)$",
    ]:
        m = re.search(pat, t)
        if m:
            gross_pay = parse_money(m.group(1))
            if gross_pay is not None:
                break

    for pat in [
        r"(?im)\bnet\s*pay\b\s*[:\-]?\s*([$\(\)\d,.\s-]+)$",
        r"(?im)\btotal\s*net\b\s*[:\-]?\s*([$\(\)\d,.\s-]+)$",
    ]:
        m = re.search(pat, t)
        if m:
            net_pay = parse_money(m.group(1))
            if net_pay is not None:
                break

    return pay_date, period_start, period_end, gross_pay, net_pay


def _looks_like_scanned_pdf(*, page_count: int, extracted_text: str) -> bool:
    if page_count <= 0:
        return False
    txt = (extracted_text or "").strip()
    if len(txt) < 50:
        return True
    # Heuristic: very low alpha ratio suggests bad extraction.
    alpha = sum(1 for c in txt if c.isalpha())
    ratio = alpha / max(1, len(txt))
    return ratio < 0.05


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

    # Step 5B: no LLM extraction yet; keep lines empty, but preserve a minimal draft.
    draft_lines: list[DraftPayrollLine] = []
    lines_total_taxes_deductions = None

    validation = validate_paystub(
        pay_date=pay_date,
        period_start=period_start,
        period_end=period_end,
        gross_pay=gross_pay,
        net_pay=net_pay,
        lines_total_taxes_deductions=lines_total_taxes_deductions,
    )

    if not pay_date:
        # Schema requires pay_date for draft insert; we keep this strict so the DB doesn't fill with junk.
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

    # Store draft payroll rows (status=draft) and transition document to in_review (no approval flow yet).
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
            "lines": [],
        },
        "validation": {"ok": validation.ok, "warnings": validation.warnings},
    }
