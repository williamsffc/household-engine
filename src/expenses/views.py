from __future__ import annotations

"""Expense reporting helpers.

Ported from expense-recon/reports.py. Not wired into the app yet (backend-only Step 3).
"""

import json
import os

import pandas as pd


def _flag_severity(reason: str) -> str:
    r = reason.lower()
    if "confirmed duplicate" in r:
        return "critical"
    if "potential duplicate" in r or "large transaction" in r:
        return "warning"
    return "info"


def generate_summary(df: pd.DataFrame) -> str:
    outflows = df[df["txn_type"].isin(["expense", "fee"])]
    expenses = df[df["txn_type"] == "expense"]
    fees = df[df["txn_type"] == "fee"]
    credits = df[df["txn_type"] == "credit"]
    payments = df[df["txn_type"] == "payment"]

    date_min = pd.to_datetime(df["date"]).min()
    date_max = pd.to_datetime(df["date"]).max()
    month_label = date_max.strftime("%B %Y")
    accounts = df["account"].unique().tolist() if len(df) > 0 else []
    account = ", ".join(sorted(accounts)) if accounts else "Unknown"

    total_spend = outflows["amount"].sum()
    total_fees = fees["amount"].sum()
    total_credits = credits["amount"].sum()
    total_payments = payments["amount"].sum()
    n_days = max((date_max - date_min).days, 1)
    avg_daily = total_spend / n_days

    cat_summary = outflows.groupby("category")["amount"].sum().sort_values(ascending=False)
    cat_pcts = (cat_summary / total_spend * 100).round(1) if total_spend > 0 else cat_summary * 0

    top_merchants = outflows.groupby("merchant_clean")["amount"].sum().sort_values(ascending=False).head(5)
    flagged = df[df["is_flagged"] == True]
    recurring = df[(df["is_recurring"] == True) & (df["txn_type"] == "expense")]
    recurring_summary = recurring.groupby("merchant_clean").agg(count=("amount", "count"), avg=("amount", "mean")).sort_values(
        "avg", ascending=False
    )

    lines = [
        "=" * 50,
        f"  EXPENSE RECONCILIATION - {month_label}",
        f"  Account: {account}",
        "=" * 50,
        "",
        f"  Period: {date_min.strftime('%b %d, %Y')} -> {date_max.strftime('%b %d, %Y')}",
        f"  Total Transactions: {len(df)}",
        f"  Total Spending: ${total_spend:,.2f}",
        f"  Total Fees: ${total_fees:,.2f}",
        f"  Total Credits/Refunds: ${total_credits:,.2f}",
        f"  Total Payments: ${total_payments:,.2f}",
        f"  Avg Daily Spend: ${avg_daily:,.2f}",
        "",
        "  -- Spending by Category ----------------",
    ]
    for cat, amt in cat_summary.items():
        lines.append(f"  {cat:<22} ${amt:>9,.2f}  ({cat_pcts[cat]}%)")

    lines.append("")
    lines.append("  -- Top 5 Merchants ----------------------")
    for merch, amt in top_merchants.items():
        lines.append(f"  {merch:<22} ${amt:>9,.2f}")
    lines.append("")

    if len(flagged) > 0:
        lines.append(f"  -- Flags ({len(flagged)} items) -------------------")
        for _, row in flagged.iterrows():
            lines.append(f"  ! {row['merchant_clean']}: {row['flag_reason']}")
        lines.append("")

    if len(recurring_summary) > 0:
        lines.append("  -- Recurring Charges --------------------")
        for merch, row in recurring_summary.iterrows():
            lines.append(f"  {merch}: ${row['avg']:.2f} avg ({int(row['count'])}x this period)")
        lines.append("")

    lines.append("=" * 50)
    return "\n".join(lines)


def export_dashboard_json(df: pd.DataFrame, output_dir: str, month: str | None = None):
    os.makedirs(output_dir, exist_ok=True)

    outflows = df[df["txn_type"].isin(["expense", "fee"])]
    expenses = df[df["txn_type"] == "expense"]
    fees = df[df["txn_type"] == "fee"]
    dates = pd.to_datetime(df["date"])

    monthly = {
        "month": month or dates.max().strftime("%Y-%m"),
        "period": {"start": dates.min().strftime("%Y-%m-%d"), "end": dates.max().strftime("%Y-%m-%d")},
        "totals": {
            "spending": round(outflows["amount"].sum(), 2),
            "fees": round(fees["amount"].sum(), 2),
            "credits": round(df[df["txn_type"] == "credit"]["amount"].sum(), 2),
            "payments": round(df[df["txn_type"] == "payment"]["amount"].sum(), 2),
            "transactions": len(df),
        },
        "flags": [
            {
                "merchant": row["merchant_clean"],
                "amount": round(row["amount"], 2),
                "date": str(row["date"])[:10],
                "reason": row["flag_reason"],
                "flag_type": _flag_severity(row["flag_reason"]),
            }
            for _, row in df[df["is_flagged"] == True].iterrows()
        ],
        "recurring": [
            {
                "merchant": merch,
                "count": int(group["amount"].count()),
                "avg_amount": round(group["amount"].mean(), 2),
                "total": round(group["amount"].sum(), 2),
            }
            for merch, group in expenses[expenses["is_recurring"] == True].groupby("merchant_clean")
        ],
    }

    target_month = month or dates.max().strftime("%Y-%m")
    filepath = os.path.join(output_dir, f"month_{target_month}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(monthly, f, indent=2, default=str)

    return filepath


def export_compare_json(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    output_dir: str,
    label_a: str,
    label_b: str,
) -> str:
    """Ported from expense-recon for completeness (not wired yet)."""

    os.makedirs(output_dir, exist_ok=True)

    def spend(df: pd.DataFrame) -> float:
        return float(df[df["txn_type"].isin(["expense", "fee"])]["amount"].sum())

    def by_cat(df: pd.DataFrame) -> pd.Series:
        return df[df["txn_type"].isin(["expense", "fee"])].groupby("category")["amount"].sum()

    spend_a = spend(df_a)
    spend_b = spend(df_b)
    change_pct = ((spend_b - spend_a) / spend_a * 100) if spend_a > 0 else 0.0

    cats_a = by_cat(df_a)
    cats_b = by_cat(df_b)
    all_cats = set(cats_a.index) | set(cats_b.index)

    by_category = sorted(
        [
            {
                "category": cat,
                "amount_a": round(float(cats_a.get(cat, 0)), 2),
                "amount_b": round(float(cats_b.get(cat, 0)), 2),
                "change": round(float(cats_b.get(cat, 0) - cats_a.get(cat, 0)), 2),
                "change_pct": round(
                    (cats_b.get(cat, 0) - cats_a.get(cat, 0)) / cats_a.get(cat, 1) * 100, 1
                ),
            }
            for cat in all_cats
        ],
        key=lambda x: abs(x["change"]),
        reverse=True,
    )

    merchants_a = set(df_a["merchant_clean"].unique())
    merchants_b = set(df_b["merchant_clean"].unique())

    result = {
        "label_a": label_a,
        "label_b": label_b,
        "spending_a": round(float(spend_a), 2),
        "spending_b": round(float(spend_b), 2),
        "spending_change_pct": round(change_pct, 1),
        "by_category": by_category,
        "new_merchants": sorted(merchants_b - merchants_a),
        "dropped_merchants": sorted(merchants_a - merchants_b),
    }

    safe_label = label_b.replace(" ", "_")
    filepath = os.path.join(output_dir, f"compare_{safe_label}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    return filepath
