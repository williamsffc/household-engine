from __future__ import annotations

"""Parser for American Express statement exports.

Ported from expense-recon with minimal path adaptation for Household Engine.
"""

from collections import defaultdict
from datetime import datetime
import fnmatch
import os
import re

import pandas as pd
import yaml

from .base import BaseParser


JAMMED_CITIES = [
    "GRANADA HILLS",
    "MISSION HILLS",
    "NORTH HILLS",
    "NORTH HOLLYWO",
    "NORTH HOLLYWOOD",
    "SHERMAN OAKS",
    "LOS ANGELES",
    "SAN FERNANDO",
    "LONG BEACH",
    "PACOIMA",
    "PANORAMA CITY",
    "STUDIO CITY",
    "CHATSWORTH",
    "NORTHRIDGE",
    "BLACKHAWK",
    "SAN MARINO",
    "HOUSTON",
    "CANTON",
    "SYLMAR",
    "ENCINO",
    "ARLETA",
    "VAN NUYS",
    "BURBANK",
    "GLENDALE",
    "PASADENA",
    "TORRANCE",
    "INGLEWOOD",
    "DOWNEY",
    "WHITTIER",
    "POMONA",
    "ARCADIA",
    "MONROVIA",
    "AZUSA",
]


class AmexParser(BaseParser):
    def _resolve_account_name(self, source_file: str) -> str:
        config_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "config",
            "accounts.yaml",
        )
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            config = {}

        filename = os.path.basename(source_file).lower()
        for account in config.get("accounts", []):
            patterns = account.get("file_pattern", [])
            if isinstance(patterns, str):
                patterns = [patterns]
            for pattern in patterns:
                if fnmatch.fnmatch(filename, pattern.lower()):
                    return account.get("nickname", "Amex Unknown")

        if "biz" in filename:
            return "Amex Biz"
        if "gold" in filename:
            return "Amex Gold"
        return "Amex Unknown"

    @property
    def account_name(self) -> str:
        return "Amex"

    @property
    def account_type(self) -> str:
        return "credit_card"

    @property
    def signature_columns(self) -> set:
        return {"Date", "Description", "Amount", "Category"}

    def sanitize(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        report: list[str] = []

        if "Card Member" in df.columns:
            n = df["Card Member"].nunique()
            df = df.drop(columns=["Card Member"])
            report.append(f"Dropped Card Member column ({n} person names)")
        if "Appears On Your Statement As" in df.columns:
            df = df.drop(columns=["Appears On Your Statement As"])
            report.append("Dropped Appears On Your Statement As (redundant)")

        text_cols = ["Description", "Category"]
        df, regex_report = self.apply_regex_sanitization(df, text_cols)
        report.extend(regex_report)

        return df, report

    def parse(self, df: pd.DataFrame, source_file: str) -> pd.DataFrame:
        now = datetime.now().isoformat()
        records: list[dict] = []
        current_account = self._resolve_account_name(source_file)
        stmt_month = self.statement_month(source_file, df["Date"])
        id_counters: dict = defaultdict(int)

        for _, row in df.iterrows():
            cat_source = row.get("Category", "")
            cat_source_str = str(cat_source) if pd.notna(cat_source) else ""
            date = pd.to_datetime(row["Date"])
            amount = abs(row["Amount"])
            clean_merchant = self._clean_merchant(row["Description"])
            id_base = (str(date.date()), clean_merchant, str(amount), current_account)
            txn_id = self.make_txn_id(*id_base, counter=id_counters[id_base])
            id_counters[id_base] += 1
            record = {
                "id": txn_id,
                "date": date,
                "description": row["Description"],
                "merchant_clean": clean_merchant,
                "amount": amount,
                "txn_type": self._classify(row["Amount"], row["Description"], cat_source_str),
                "category_source": cat_source_str,
                "account": current_account,
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
    def _classify(amount: float, description: str, category_source: str) -> str:
        if amount > 0:
            if "Fees" in str(category_source):
                return "fee"
            return "expense"

        desc_upper = str(description).upper()
        if "PAYMENT" in desc_upper:
            return "payment"
        return "credit"

    @staticmethod
    def _clean_merchant(desc: str) -> str:
        if not isinstance(desc, str):
            return str(desc)
        s = desc.strip()

        s = re.sub(r"\[Redacted_[^\]]+\]", "", s, flags=re.IGNORECASE)

        if "ONLINE PAYMENT" in s.upper():
            return "Online Payment"
        if "AMEX" in s.upper() and "CREDIT" in s.upper():
            return s.strip().title()

        s = re.sub(r"^AplPay\s*", "", s, flags=re.IGNORECASE)

        parts = re.split(r"\s{3,}", s)
        if len(parts) > 1:
            s = parts[0].strip()
        else:
            s = re.sub(r"\s{2,}[\w\s]+\s{2,}[A-Z]{2}\s*$", "", s)
            for city in JAMMED_CITIES:
                s = re.sub(rf"(?i)\s*{re.escape(city)}\s*[A-Z]{{0,2}}\s*$", "", s)

        s = re.sub(r"\s+[A-Z]{2}\s*$", "", s)
        s = re.sub(r"\s*\d{3}-\d{3}-\d{4}\s*", "", s)
        s = re.sub(r"\s*#\d+[\s\d]*", "", s)
        s = re.sub(r"\s+\d{4,}\s*", " ", s)
        s = re.sub(r"\s+0+\s*$", "", s)
        s = re.sub(r"\s*\(.*$", "", s)
        s = re.sub(r"\s+", " ", s).strip()
        s = s.title()

        for old, new in {"Mcdonald'S": "McDonald's", "'S": "'s", "Cvs": "CVS"}.items():
            s = s.replace(old, new)

        return s if s else desc.strip().title()
