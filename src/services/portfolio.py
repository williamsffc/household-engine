from __future__ import annotations

import sqlite3
from typing import Any

from src.services.analytics import get_monthly_cashflow, trailing_average


def _has_any_approved_payroll(conn: sqlite3.Connection) -> bool:
    row = conn.execute(
        "SELECT 1 AS ok FROM payroll_paystubs WHERE status = 'approved' LIMIT 1;"
    ).fetchone()
    return row is not None


def build_portfolio_summary(
    conn: sqlite3.Connection,
    *,
    trailing_months: int = 3,
    liquidity_reserve_months: float = 1.0,
    allocation_split: float = 0.7,
) -> dict[str, Any]:
    """Modest, explainable deployable-surplus estimate.

    This intentionally does NOT pretend we know actual bank balances. It produces a
    flow-based estimate derived from normalized monthly cashflow (approved-only payroll income).
    """

    trailing_months = max(1, min(int(trailing_months), 12))
    liquidity_reserve_months = max(0.0, min(float(liquidity_reserve_months), 6.0))
    allocation_split = max(0.0, min(float(allocation_split), 1.0))

    cashflow = get_monthly_cashflow(conn, limit=max(36, trailing_months))
    base_month = str(cashflow[0]["month"]) if cashflow else None

    has_approved_payroll = _has_any_approved_payroll(conn)

    trailing_income = trailing_average(cashflow, field="total_income", months=trailing_months)
    trailing_expenses = trailing_average(cashflow, field="total_expenses", months=trailing_months)
    trailing_net = trailing_average(cashflow, field="net_cashflow", months=trailing_months)

    target_liquidity_reserve = round(trailing_expenses * liquidity_reserve_months, 2)

    # Deployable surplus is a flow estimate: how much "excess" cashflow per month exists
    # given trailing normalized household cashflow.
    # If payroll isn't approved yet, we treat income as unavailable for trusted surplus.
    if not has_approved_payroll:
        availability = {
            "ok": False,
            "reason": "No approved payroll data is available yet. Income-side assumptions are not trusted until payroll approval exists.",
        }
        deployable_surplus = 0.0
    else:
        availability = {"ok": True, "reason": None}
        deployable_surplus = max(0.0, float(trailing_net))

    available_for_allocation = round(deployable_surplus * allocation_split, 2)
    available_for_trading = round(deployable_surplus - available_for_allocation, 2)

    return {
        "as_of_month": base_month,
        "availability": availability,
        "assumptions": {
            "trailing_months": trailing_months,
            "income_semantics": "Approved payroll only (draft/in_review excluded).",
            "expense_semantics": "Expenses from vw_monthly_expenses; cashflow from vw_monthly_cashflow.",
            "deployable_surplus_definition": "Flow-based estimate derived from trailing average monthly net cashflow; does not use bank balances.",
            "liquidity_reserve_months_target": liquidity_reserve_months,
            "allocation_split": {
                "available_for_allocation": allocation_split,
                "available_for_trading": round(1.0 - allocation_split, 2),
            },
        },
        "inputs": {
            "cashflow_rows": cashflow[: max(1, trailing_months)],
            "trailing_averages": {
                "monthly_income": trailing_income,
                "monthly_expenses": trailing_expenses,
                "monthly_net_cashflow": trailing_net,
            },
        },
        "estimates": {
            "current_estimated_surplus": round(deployable_surplus, 2),
            "liquidity_reserve": target_liquidity_reserve,
            "available_for_allocation": available_for_allocation,
            "available_for_trading": available_for_trading,
        },
        "notes": [
            "This module is intentionally modest and explainable (V2+).",
            "If approved payroll is absent, deployable surplus is reported as 0 with an explicit reason.",
        ],
    }

