"""Abstract base parser — all account-specific parsers inherit from this.

Ported from expense-recon with minimal path adaptation for Household Engine.
"""

from __future__ import annotations

import hashlib
import os
import re
from abc import ABC, abstractmethod

import pandas as pd
import yaml


MONTH_NAMES = {
    "january": "01",
    "february": "02",
    "march": "03",
    "april": "04",
    "may": "05",
    "june": "06",
    "july": "07",
    "august": "08",
    "september": "09",
    "october": "10",
    "november": "11",
    "december": "12",
    "jan": "01",
    "feb": "02",
    "mar": "03",
    "apr": "04",
    "jun": "06",
    "jul": "07",
    "aug": "08",
    "sep": "09",
    "oct": "10",
    "nov": "11",
    "dec": "12",
}


class BaseParser(ABC):
    """Base class for statement parsers."""

    @property
    @abstractmethod
    def account_name(self) -> str:
        """Account nickname (e.g., 'Amex Gold')."""

    @property
    @abstractmethod
    def account_type(self) -> str:
        """'credit_card' or 'bank_account'."""

    @property
    @abstractmethod
    def signature_columns(self) -> set:
        """Set of column names that identify this statement format."""

    @staticmethod
    def statement_month(source_file: str, dates: pd.Series) -> str:
        """Derive statement month from filename, fallback to latest date."""

        fname_no_ext = os.path.splitext(os.path.basename(source_file))[0].lower()

        m = re.search(r"(20\d{2})[-_]?(0[1-9]|1[0-2])", fname_no_ext)
        if m:
            return f"{m.group(1)}-{m.group(2)}"

        tokens = re.split(r"[-_\s]+", fname_no_ext)
        clean_dates = pd.to_datetime(dates, errors="coerce").dropna()
        year = int(clean_dates.max().year) if len(clean_dates) > 0 else pd.Timestamp.now().year
        for token in tokens:
            if token in MONTH_NAMES:
                return f"{year}-{MONTH_NAMES[token]}"

        if len(clean_dates) > 0:
            return clean_dates.max().strftime("%Y-%m")

        return pd.Timestamp.now().strftime("%Y-%m")

    @staticmethod
    def make_txn_id(date, description: str, amount: float, account: str, counter: int = 0) -> str:
        """Deterministic transaction ID — stable across re-imports."""

        key = f"{date}|{description}|{amount}|{account}|{counter}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]

    @classmethod
    def can_parse(cls, df: pd.DataFrame) -> bool:
        instance = cls()
        return instance.signature_columns.issubset(set(df.columns))

    def apply_regex_sanitization(
        self, df: pd.DataFrame, text_columns: list[str], dry_run: bool = False
    ) -> tuple[pd.DataFrame, list[str]]:
        """Universal PII scrubber using regex patterns from config."""

        config_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "config",
            "pii_patterns.yaml",
        )

        patterns: dict = {}
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                patterns = (yaml.safe_load(f) or {}).get("patterns", {})
        except FileNotFoundError:
            patterns = {}

        report: list[str] = []
        df = df.copy()

        for col in text_columns:
            if col not in df.columns:
                continue

            df[col] = df[col].astype(str)

            for name, config in patterns.items():
                action = config.get("action", "redact")
                regex = config["regex"]
                repl = config.get("replacement", "[REDACTED]")

                mask = df[col].str.contains(regex, regex=True, na=False)
                matches = int(mask.sum())

                if matches <= 0:
                    continue

                status = "[DRY-RUN] Would redact" if dry_run else "Redacted"
                if action == "redact":
                    if not dry_run:
                        df[col] = df[col].str.replace(regex, repl, regex=True)
                    report.append(f"{status} {matches} instances of {name} in '{col}' column.")
                elif action == "review":
                    report.append(f"[REVIEW] Found {matches} potential instances of {name} in '{col}'.")

        return df, report

    @abstractmethod
    def sanitize(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        """Strip PII. Returns (cleaned_df, report_lines)."""

    @abstractmethod
    def parse(self, df: pd.DataFrame, source_file: str) -> pd.DataFrame:
        """Parse and normalize transactions into the unified schema."""

