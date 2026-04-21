from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    warnings: list[str]


def validate_paystub(
    *,
    pay_date: str | None,
    period_start: str | None = None,
    period_end: str | None = None,
    gross_pay: float | None,
    net_pay: float | None,
    lines_total_taxes_deductions: float | None = None,
) -> ValidationResult:
    warnings: list[str] = []

    if not pay_date:
        warnings.append("missing_required_field: pay_date")
    else:
        try:
            date.fromisoformat(str(pay_date))
        except ValueError:
            warnings.append("invalid_date: pay_date")

    if period_start:
        try:
            date.fromisoformat(str(period_start))
        except ValueError:
            warnings.append("invalid_date: period_start")
    if period_end:
        try:
            date.fromisoformat(str(period_end))
        except ValueError:
            warnings.append("invalid_date: period_end")
    if period_start and period_end:
        try:
            if date.fromisoformat(str(period_start)) > date.fromisoformat(str(period_end)):
                warnings.append("period_start_after_period_end")
        except ValueError:
            # already warned above
            pass

    if gross_pay is None:
        warnings.append("missing_field: gross_pay")
    if net_pay is None:
        warnings.append("missing_field: net_pay")

    # Basic plausibility checks.
    if gross_pay is not None and gross_pay < 0:
        warnings.append("gross_pay_negative")
    if net_pay is not None and net_pay < 0:
        warnings.append("net_pay_negative")
    if gross_pay is not None and net_pay is not None and net_pay > gross_pay:
        warnings.append("net_pay_greater_than_gross")

    # If we have an estimated taxes+deductions total, sanity-check net ≈ gross - (tax+ded).
    if (
        gross_pay is not None
        and net_pay is not None
        and lines_total_taxes_deductions is not None
        and lines_total_taxes_deductions >= 0
    ):
        expected_net = gross_pay - lines_total_taxes_deductions
        diff = abs(expected_net - net_pay)
        if diff > 2.0:
            warnings.append(f"net_mismatch_vs_lines: diff={round(diff,2)}")

    ok = not any(w.startswith("missing_required_field") for w in warnings)
    return ValidationResult(ok=ok, warnings=warnings)
