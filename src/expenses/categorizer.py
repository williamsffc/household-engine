from __future__ import annotations

"""Category mapping: bank-assigned categories → simplified hybrid taxonomy.

Ported from expense-recon with minimal path adaptation.
"""

import os
from typing import Optional

import pandas as pd
import yaml


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "categories.yaml")


def load_category_config(config_path: Optional[str] = None) -> dict:
    path = config_path or CONFIG_PATH
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def categorize(df: pd.DataFrame, config_path: Optional[str] = None) -> pd.DataFrame:
    config = load_category_config(config_path)
    mapping = config.get("mapping", {})
    overrides = config.get("merchant_overrides", {})
    default = config.get("default_category", "Other")

    categories: list[str] = []
    subcategories: list[str] = []

    for _, row in df.iterrows():
        source = str(row.get("category_source", "")).strip()
        merchant = str(row.get("merchant_clean", "")).upper()

        cat = default
        sub = ""

        override_found = False
        for keyword, (override_cat, override_sub) in overrides.items():
            if keyword.upper() in merchant:
                categories.append(override_cat)
                subcategories.append(override_sub)
                override_found = True
                break

        if override_found:
            continue

        if not source or pd.isna(source) or source == "nan":
            categories.append("Uncategorized")
            subcategories.append("")
            continue

        if source in mapping:
            cat, sub = mapping[source]
        else:
            matched = False
            for key, val in mapping.items():
                if key.lower() == source.lower():
                    cat, sub = val
                    matched = True
                    break
            if not matched:
                cat = default
                sub = source.split("-", 1)[-1].strip() if "-" in source else source

        categories.append(cat)
        subcategories.append(sub)

    df = df.copy()
    df["category"] = categories
    df["subcategory"] = subcategories

    payment_cat = config.get("payment_category", "Credit Card Payment")
    payment_sub = config.get("payment_subcategory", "Transfer")
    df.loc[df["txn_type"] == "payment", "category"] = payment_cat
    df.loc[df["txn_type"] == "payment", "subcategory"] = payment_sub

    return df
