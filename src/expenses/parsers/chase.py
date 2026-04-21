from __future__ import annotations

"""Parser for Chase statement exports.

Ported from expense-recon with minimal adaptation.
"""

from collections import defaultdict
from datetime import datetime

import pandas as pd

from .base import BaseParser


class ChaseParser(BaseParser):
    @property
    def account_name(self) -> str:
        return "Chase Sapphire"

    @property
    def account_type(self) -> str:
        return "credit_card"

    @property
    def signature_columns(self) -> set:
        return {"Transaction Date", "Description", "Amount", "Category"}

    def sanitize(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        report: list[str] = []
        text_cols = [c for c in ["Description", "Memo"] if c in df.columns]
        df, regex_report = self.apply_regex_sanitization(df, text_cols)
        report.extend(regex_report)
        return df, report

    def parse(self, df: pd.DataFrame, source_file: str) -> pd.DataFrame:
        now = datetime.now().isoformat()
        records: list[dict] = []
        stmt_month = self.statement_month(source_file, df["Transaction Date"])
        id_counters: dict = defaultdict(int)

        for _, row in df.iterrows():
            cat_source = row.get("Category", "")
            cat_source_str = str(cat_source) if pd.notna(cat_source) else ""
            amount_raw = row["Amount"]
            # Chase exports: negative = charge (money out), positive = payment/credit
            amount = float(amount_raw)
            txn_type = self._classify(amount, row["Description"])
            date = pd.to_datetime(row["Transaction Date"])
            abs_amount = abs(amount)
            clean_merchant = self._clean_merchant(str(row["Description"]))
            id_base = (str(date.date()), clean_merchant, str(abs_amount), self.account_name)
            txn_id = self.make_txn_id(*id_base, counter=id_counters[id_base])
            id_counters[id_base] += 1
            record = {
                "id": txn_id,
                "date": date,
                "description": row["Description"],
                "merchant_clean": clean_merchant,
                "amount": abs_amount,
                "txn_type": txn_type,
                "category_source": cat_source_str,
                "account": self.account_name,
                "account_type": self.account_type,
                "is_recurring": False,
                "is_flagged": False,
                "flag_reason": "",
                "month": stmt_month,
                "source_file": source_file,
                "imported_at": now,
            }
            records.append(record)
        return pd.DataFrame(records)

    @staticmethod
    def _classify(amount: float, description: str) -> str:
        # Chase: negative amounts are charges (expenses), positive are inflows
        if amount < 0:
            return "expense"
        desc_upper = str(description).upper()
        if "PAYMENT" in desc_upper or "AUTOPAY" in desc_upper:
            return "payment"
        return "credit"

    @staticmethod
    def _clean_merchant(desc: str) -> str:
        import re

        if not isinstance(desc, str):
            return str(desc)
        s = desc.strip()
        # Strip trailing city/state patterns and extra whitespace
        s = re.sub(r"\s{2,}[\w\s]+\s{2,}[A-Z]{2}\s*$", "", s)
        s = re.sub(r"\s+[A-Z]{2}\s*$", "", s)
        s = re.sub(r"\s*\d{3}-\d{3}-\d{4}\s*", "", s)
        s = re.sub(r"\s*#\d+[\s\d]*", "", s)
        s = re.sub(r"\s+\d{4,}\s*", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s.title() if s else desc.strip().title()
