from __future__ import annotations

import sqlite3
from datetime import date
from typing import Any


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {k: row[k] for k in row.keys()}


def get_monthly_expenses(conn: sqlite3.Connection, *, limit: int = 36) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT month, total_expenses, transaction_count
        FROM vw_monthly_expenses
        ORDER BY month DESC
        LIMIT ?;
        """,
        (int(limit),),
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_monthly_cashflow(conn: sqlite3.Connection, *, limit: int = 36) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT month, total_income, total_expenses, net_cashflow
        FROM vw_monthly_cashflow
        ORDER BY month DESC
        LIMIT ?;
        """,
        (int(limit),),
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_monthly_payroll_approved(conn: sqlite3.Connection, *, limit: int = 36) -> list[dict[str, Any]]:
    """Approved-only monthly payroll rows from vw_monthly_payroll.

    Note: This view is already approved-only by definition.
    """

    rows = conn.execute(
        """
        SELECT month, member_id, total_net_pay, total_gross_pay, paystub_count
        FROM vw_monthly_payroll
        ORDER BY month DESC, member_id ASC
        LIMIT ?;
        """,
        (int(limit),),
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / float(len(values))


def trailing_average(rows: list[dict[str, Any]], *, field: str, months: int) -> float:
    vals: list[float] = []
    for r in rows[:months]:
        v = r.get(field)
        try:
            vals.append(float(v or 0.0))
        except Exception:
            vals.append(0.0)
    return round(_mean(vals), 2)


def _next_month_yyyy_mm(month: str) -> str:
    y, m = month.split("-")
    d = date(int(y), int(m), 1)
    # add one month
    if d.month == 12:
        d2 = date(d.year + 1, 1, 1)
    else:
        d2 = date(d.year, d.month + 1, 1)
    return f"{d2.year:04d}-{d2.month:02d}"


def forecast_months(
    *,
    base_month: str,
    months_ahead: int,
    monthly_income: float,
    monthly_expenses: float,
    income_multiplier: float,
    expense_multiplier: float,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    m = base_month
    for _ in range(int(months_ahead)):
        m = _next_month_yyyy_mm(m)
        income = round(float(monthly_income) * float(income_multiplier), 2)
        expenses = round(float(monthly_expenses) * float(expense_multiplier), 2)
        out.append(
            {
                "month": m,
                "total_income": income,
                "total_expenses": expenses,
                "net_cashflow": round(income - expenses, 2),
            }
        )
    return out
