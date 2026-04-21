from __future__ import annotations

"""Discrepancy detection and anomaly flags.

Ported from expense-recon's discrepancies.py with minimal path adaptation.
"""

import os
from typing import Optional

import pandas as pd
import yaml


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "rules.yaml")


def load_rules(config_path: Optional[str] = None) -> dict:
    path = config_path or CONFIG_PATH
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return raw.get("rules", raw)


def check_duplicates(df: pd.DataFrame, rules: dict) -> dict:
    flags = {}
    cfg = rules.get("duplicate_detection", {})
    if not cfg.get("enabled", True):
        return {}
    day_tolerance = cfg.get("day_tolerance", 3)
    amount_tolerance = cfg.get("amount_tolerance", 0.0)

    for txn_type, tolerance in [("expense", day_tolerance), ("payment", 1)]:
        subset = df[df["txn_type"] == txn_type].copy()
        if subset.empty:
            continue
        for _, group in subset.groupby("merchant_clean"):
            if len(group) < 2:
                continue
            group = group.sort_values("date")
            rows = group.to_dict("records")
            indices = group.index.tolist()

            for i in range(1, len(rows)):
                days_diff = (rows[i]["date"] - rows[i - 1]["date"]).days
                amt_diff = abs(rows[i]["amount"] - rows[i - 1]["amount"])
                if days_diff <= tolerance and amt_diff <= amount_tolerance:
                    prev_date = rows[i - 1]["date"].strftime("%m/%d")
                    severity = "Confirmed" if days_diff == 0 else "Potential"
                    label = "payment" if txn_type == "payment" else "charge"
                    flags[indices[i]] = (
                        f"{severity} duplicate: identical ${rows[i]['amount']:.2f} {label} on {prev_date}"
                    )
    return flags


def detect_subscription_changes(df: pd.DataFrame, rules: dict) -> dict:
    flags = {}
    cfg = rules.get("subscription_change", {})
    if not cfg.get("enabled", True):
        return {}
    change_pct = cfg.get("change_percent", 0.05)
    min_occ = cfg.get("min_occurrences", 2)

    sub_categories = ["Subscriptions"]
    subs = df[(df["txn_type"] == "expense") & (df["category"].isin(sub_categories))].copy()

    for _, group in subs.groupby("merchant_clean"):
        if len(group) >= min_occ:
            group = group.sort_values("date")
            amounts = group["amount"].tolist()
            indices = group.index.tolist()

            for i in range(1, len(amounts)):
                old_amt = amounts[i - 1]
                new_amt = amounts[i]

                if old_amt != new_amt and old_amt > 0:
                    pct_change = abs(new_amt - old_amt) / old_amt
                    if pct_change >= change_pct:
                        flags[indices[i]] = f"Subscription change: ${old_amt:.2f} → ${new_amt:.2f}"
    return flags


def detect_large_transactions(df: pd.DataFrame, rules: dict) -> dict:
    cfg = rules.get("large_transaction", {})
    if not cfg.get("enabled", True):
        return {}
    threshold = cfg.get("threshold", 200.00)

    flags = {}
    large = df[(df["txn_type"] == "expense") & (df["amount"] > threshold)]
    for idx, row in large.iterrows():
        flags[idx] = f"Large transaction: ${row['amount']:.2f}"
    return flags


def detect_refund_anomaly(df: pd.DataFrame, rules: dict) -> dict:
    flags = {}
    cfg = rules.get("refund_anomaly", {})
    if not cfg.get("enabled", True):
        return {}
    threshold = cfg.get("threshold", 50.00)

    refunds = df[df["txn_type"] == "credit"]
    for idx, row in refunds.iterrows():
        if row["amount"] > threshold:
            flags[idx] = f"Refund anomaly: large credit of ${row['amount']:.2f}"
    return flags


def detect_recurring(df: pd.DataFrame, rules: dict) -> list:
    cfg = rules.get("recurring_detection", {})
    if not cfg.get("enabled", True):
        return []
    min_occ = cfg.get("min_occurrences", 2)
    variance_threshold = cfg.get("variance_threshold", 0.15)

    expenses = df[df["txn_type"] == "expense"]
    recurring_merchants = []

    for merchant, group in expenses.groupby("merchant_clean"):
        if len(group) >= min_occ:
            amounts = group["amount"]
            mean_amt = amounts.mean()

            if mean_amt == 0:
                continue

            cv = amounts.std() / mean_amt
            if pd.isna(cv) or cv < variance_threshold:
                recurring_merchants.append(merchant)

    return recurring_merchants


def detect_velocity_anomaly(
    df: pd.DataFrame,
    historical_df: pd.DataFrame,
    rules: dict,
) -> dict:
    flags = {}
    cfg = rules.get("velocity_anomaly", {})
    if not cfg.get("enabled", True):
        return {}
    z_threshold = cfg.get("z_threshold", 2.0)
    min_months = cfg.get("min_months", 2)

    if historical_df is None or len(historical_df) == 0:
        return {}

    hist = historical_df[historical_df["txn_type"].isin(["expense", "fee"])].copy()
    hist["date"] = pd.to_datetime(hist["date"])

    hist_monthly = hist.groupby(["month", "category"])["amount"].sum().reset_index()
    hist_stats = hist_monthly.groupby("category")["amount"].agg(mean="mean", std="std", n_months="count")

    curr = df[df["txn_type"].isin(["expense", "fee"])].copy()
    curr_by_cat = curr.groupby("category")["amount"].sum()

    for cat, current_spend in curr_by_cat.items():
        if cat not in hist_stats.index:
            continue
        n_months = hist_stats.loc[cat, "n_months"]
        if n_months < min_months:
            continue
        mean = hist_stats.loc[cat, "mean"]
        std = hist_stats.loc[cat, "std"]
        if pd.isna(std) or std == 0:
            continue
        z_score = (current_spend - mean) / std
        if z_score > z_threshold:
            pct_above = (current_spend - mean) / mean * 100 if mean > 0 else 0
            cat_rows = curr[curr["category"] == cat].sort_values("amount", ascending=False)
            if len(cat_rows) > 0:
                idx = cat_rows.index[0]
                flags[idx] = (
                    f"Spending velocity: {cat} is {pct_above:.0f}% above your avg "
                    f"(${current_spend:.0f} this month vs ${mean:.0f} avg)"
                )
    return flags


def run_all_checks(
    df: pd.DataFrame,
    config_path: Optional[str] = None,
    historical_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    rules = load_rules(config_path)

    dup = check_duplicates(df, rules)
    sub = detect_subscription_changes(df, rules)
    large = detect_large_transactions(df, rules)
    refund = detect_refund_anomaly(df, rules)
    velocity = detect_velocity_anomaly(df, historical_df if historical_df is not None else pd.DataFrame(), rules)
    recurring = detect_recurring(df, rules)

    all_flags: dict = {}
    for flags_dict in [dup, sub, large, refund, velocity]:
        for idx, reason in flags_dict.items():
            if idx in all_flags:
                all_flags[idx] += " | " + reason
            else:
                all_flags[idx] = reason

    df = df.copy()
    for idx, reason in all_flags.items():
        df.at[idx, "is_flagged"] = True
        df.at[idx, "flag_reason"] = reason

    df.loc[df["merchant_clean"].isin(recurring), "is_recurring"] = True
    return df
