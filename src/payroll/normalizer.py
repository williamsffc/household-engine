from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime


_MONEY_RE = re.compile(r"[-+]?\$?\s*\(?\s*[\d,]+(?:\.\d{2})?\s*\)?")


def parse_money(raw: str) -> float | None:
    s = (raw or "").strip()
    if not s:
        return None

    # Normalize parentheses negative.
    negative = False
    if "(" in s and ")" in s:
        negative = True
        s = s.replace("(", "").replace(")", "")

    s = s.replace("$", "").replace(",", "").strip()
    try:
        val = float(s)
    except ValueError:
        return None

    return -val if negative else val


def find_first_money(text: str) -> float | None:
    if not text:
        return None
    m = _MONEY_RE.search(text)
    if not m:
        return None
    return parse_money(m.group(0))


def parse_date_any(raw: str) -> str | None:
    """Return ISO date (YYYY-MM-DD) if parseable."""

    s = (raw or "").strip()
    if not s:
        return None

    # Try a few common formats seen on paystubs.
    fmts = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m/%d/%Y",
        "%m/%d/%y",
        "%m-%d-%Y",
        "%m-%d-%y",
        "%d-%b-%Y",  # 15-Apr-2026
        "%d-%B-%Y",  # 15-April-2026
        "%b %d, %Y",  # Apr 15, 2026
        "%B %d, %Y",  # April 15, 2026
        "%d %b %Y",  # 15 Apr 2026
        "%d %B %Y",  # 15 April 2026
    ]
    for fmt in fmts:
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue

    # Fallback: find a date-like token.
    m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", s)
    if m:
        return m.group(1)
    m = re.search(r"\b(\d{4}/\d{2}/\d{2})\b", s)
    if m:
        return parse_date_any(m.group(1).replace("/", "-"))
    m = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b", s)
    if m:
        mm, dd, yy = m.group(1), m.group(2), m.group(3)
        if len(yy) == 2:
            yy = "20" + yy
        try:
            return date(int(yy), int(mm), int(dd)).isoformat()
        except ValueError:
            return None

    return None


@dataclass(frozen=True)
class DraftPayrollLine:
    category: str  # earning, tax, deduction
    description: str
    amount: float
    ytd_amount: float | None = None
    display_order: int | None = None


@dataclass(frozen=True)
class DraftPaystub:
    pay_date: str
    period_start: str | None
    period_end: str | None
    gross_pay: float | None
    net_pay: float | None
    currency: str = "USD"
    lines: list[DraftPayrollLine] | None = None
