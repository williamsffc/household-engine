from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any

from fastapi import APIRouter

from src.core.database import db_connection
from src.expenses.repository import get_latest_expense_month, get_month_total_expenses
from src.services.analytics import (
    forecast_months,
    get_monthly_cashflow,
    get_monthly_expenses,
    get_monthly_payroll_approved,
    trailing_average,
)
from src.services.portfolio import build_portfolio_summary
from src.services.documents import get_recent_documents


router = APIRouter(prefix="/api/overview", tags=["overview"])


def _has_any_approved_payroll(conn: sqlite3.Connection) -> bool:
    row = conn.execute(
        "SELECT 1 AS ok FROM payroll_paystubs WHERE status = 'approved' LIMIT 1;"
    ).fetchone()
    return row is not None


def _count_in_review_documents(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM documents WHERE status = 'in_review';"
    ).fetchone()
    return int(row["c"] if row else 0)


def _months_with_expense_activity(expense_rows: list[dict[str, Any]]) -> int:
    return sum(
        1
        for r in expense_rows
        if float(r.get("total_expenses") or 0) > 0 or int(r.get("transaction_count") or 0) > 0
    )


@router.get("/summary")
def overview_summary() -> dict:
    with db_connection() as conn:
        # Prefer the stable cashflow view when available (approved payroll only).
        row = conn.execute(
            "SELECT month, total_income, total_expenses, net_cashflow FROM vw_monthly_cashflow ORDER BY month DESC LIMIT 1;"
        ).fetchone()
        if row is not None:
            month = str(row["month"])
            total_income = float(row["total_income"] or 0.0)
            total_expenses = float(row["total_expenses"] or 0.0)
            net_cashflow = float(row["net_cashflow"] or 0.0)
        else:
            month = get_latest_expense_month(conn) or datetime.now().strftime("%Y-%m")
            total_expenses = get_month_total_expenses(conn, month=month)
            total_income = 0.0
            net_cashflow = round(float(total_income) - float(total_expenses), 2)

        pending_reviews = _count_in_review_documents(conn)
        payroll_ready = _has_any_approved_payroll(conn)

    return {
        "month": month,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_cashflow": net_cashflow,
        "pending_reviews": pending_reviews,
        "payroll_ready": payroll_ready,
    }


@router.get("/readiness")
def overview_readiness() -> dict[str, Any]:
    """Honest household data readiness for the Overview command center (Step 22).

    No scoring — only statuses derived from existing DB views and portfolio availability.
    """

    with db_connection() as conn:
        has_payroll = _has_any_approved_payroll(conn)
        expense_rows = get_monthly_expenses(conn, limit=36)
        months_exp = _months_with_expense_activity(expense_rows)
        pending = _count_in_review_documents(conn)
        portfolio = build_portfolio_summary(
            conn,
            trailing_months=3,
            liquidity_reserve_months=1.0,
        )

    if months_exp >= 3:
        exp_status = "ready"
        exp_detail = f"{months_exp} month(s) with expense activity in analytics (trailing views are meaningful)."
    elif months_exp >= 1:
        exp_status = "limited"
        exp_detail = (
            f"Only {months_exp} month(s) of expense history so far — summaries and trailing averages are thin."
        )
    else:
        exp_status = "missing"
        exp_detail = "No expense months in analytics yet. Upload and ingest expense files to build history."

    planning_ok = bool(portfolio.get("availability", {}).get("ok"))
    if planning_ok:
        planning_detail = (
            "Deployable-surplus estimates can use approved payroll plus normalized expense cashflow."
        )
    else:
        planning_detail = portfolio.get("availability", {}).get("reason") or "Portfolio inputs are limited."

    return {
        "approved_payroll": {
            "status": "ready" if has_payroll else "missing",
            "title": "Approved payroll",
            "detail": (
                "At least one approved paystub exists — household income analytics are grounded in payroll."
                if has_payroll
                else "No approved paystubs yet. Draft and in-review payroll does not count toward income."
            ),
        },
        "expense_history": {
            "status": exp_status,
            "months_with_activity": months_exp,
            "title": "Expense history",
            "detail": exp_detail,
        },
        "review_queue": {
            "status": "pending" if pending > 0 else "clear",
            "count": pending,
            "title": "Review queue",
            "detail": (
                f"{pending} document(s) waiting for approve/reject."
                if pending
                else "Nothing waiting in review."
            ),
        },
        "planning": {
            "status": "usable" if planning_ok else "limited",
            "title": "Planning / portfolio",
            "detail": planning_detail,
        },
    }


@router.get("/cashflow")
def overview_cashflow() -> list[dict]:
    with db_connection() as conn:
        return get_monthly_cashflow(conn, limit=36)


@router.get("/trends")
def overview_trends(limit: int = 24) -> dict:
    limit = max(1, min(int(limit), 60))
    with db_connection() as conn:
        cashflow = get_monthly_cashflow(conn, limit=limit)
        expenses = get_monthly_expenses(conn, limit=limit)
        payroll = get_monthly_payroll_approved(conn, limit=limit)

    # Aggregate approved payroll across members into per-month totals.
    income_by_month: dict[str, dict[str, float]] = {}
    for r in payroll:
        m = str(r["month"])
        income_by_month.setdefault(m, {"total_net_pay": 0.0, "total_gross_pay": 0.0, "paystub_count": 0.0})
        income_by_month[m]["total_net_pay"] += float(r.get("total_net_pay") or 0.0)
        income_by_month[m]["total_gross_pay"] += float(r.get("total_gross_pay") or 0.0)
        income_by_month[m]["paystub_count"] += float(r.get("paystub_count") or 0.0)

    income_trend = [
        {
            "month": m,
            "total_net_pay": round(v["total_net_pay"], 2),
            "total_gross_pay": round(v["total_gross_pay"], 2),
            "paystub_count": int(v["paystub_count"]),
        }
        for m, v in sorted(income_by_month.items(), key=lambda kv: kv[0], reverse=True)
    ][:limit]

    return {
        "notes": {
            "income_semantics": "Approved payroll only (draft/in_review excluded).",
            "expense_semantics": "From vw_monthly_expenses totals.",
            "cashflow_semantics": "From vw_monthly_cashflow (income approved-only).",
        },
        "income": {"rows": income_trend, "trailing_avg_net_3mo": trailing_average(income_trend, field="total_net_pay", months=3)},
        "expenses": {"rows": expenses, "trailing_avg_3mo": trailing_average(expenses, field="total_expenses", months=3)},
        "cashflow": {"rows": cashflow, "trailing_avg_net_3mo": trailing_average(cashflow, field="net_cashflow", months=3)},
    }


@router.get("/forecast")
def overview_forecast(months_ahead: int = 3, trailing_months: int = 3) -> dict:
    months_ahead = max(1, min(int(months_ahead), 12))
    trailing_months = max(1, min(int(trailing_months), 12))

    with db_connection() as conn:
        cashflow = get_monthly_cashflow(conn, limit=max(24, trailing_months))

    if not cashflow:
        # Honest empty state: no data means no forecast.
        return {
            "assumptions": {"trailing_months": trailing_months, "months_ahead": months_ahead},
            "base_month": None,
            "scenarios": {"conservative": [], "baseline": [], "optimistic": []},
        }

    base_month = str(cashflow[0]["month"])
    trailing_income = trailing_average(cashflow, field="total_income", months=trailing_months)
    trailing_expenses = trailing_average(cashflow, field="total_expenses", months=trailing_months)

    # Simple, understandable scenario multipliers. No fake precision.
    scenarios = {
        "conservative": {"income_multiplier": 0.9, "expense_multiplier": 1.1},
        "baseline": {"income_multiplier": 1.0, "expense_multiplier": 1.0},
        "optimistic": {"income_multiplier": 1.1, "expense_multiplier": 0.95},
    }

    return {
        "assumptions": {
            "months_ahead": months_ahead,
            "trailing_months": trailing_months,
            "income_source": "vw_monthly_cashflow.total_income (approved payroll only)",
            "expense_source": "vw_monthly_cashflow.total_expenses",
            "scenario_multipliers": scenarios,
            "note": "If approved payroll is absent, trailing income will be 0 and forecasts will reflect that.",
        },
        "base_month": base_month,
        "trailing_averages": {"monthly_income": trailing_income, "monthly_expenses": trailing_expenses},
        "scenarios": {
            name: forecast_months(
                base_month=base_month,
                months_ahead=months_ahead,
                monthly_income=trailing_income,
                monthly_expenses=trailing_expenses,
                income_multiplier=cfg["income_multiplier"],
                expense_multiplier=cfg["expense_multiplier"],
            )
            for name, cfg in scenarios.items()
        },
    }


@router.get("/recent-documents")
def overview_recent_documents(limit: int = 10) -> list[dict]:
    with db_connection() as conn:
        return get_recent_documents(conn, limit=limit)


@router.get("/portfolio")
def overview_portfolio(trailing_months: int = 3, liquidity_reserve_months: float = 1.0) -> dict:
    """Portfolio / deployable surplus (Step 12).

    Derived from normalized monthly cashflow (approved-only payroll income).
    """

    with db_connection() as conn:
        return build_portfolio_summary(
            conn,
            trailing_months=trailing_months,
            liquidity_reserve_months=liquidity_reserve_months,
        )
