from __future__ import annotations

"""Expense ingestion pipeline (Step 3).

Ported from expense-recon's pipeline.py with minimal adaptation:
- reads uploaded documents from Household Engine's `documents` table storage_path
- uses sqlite3 against the shared household.db
- writes to expenses_transactions
"""

import os
from pathlib import Path

import pandas as pd

from src.core.database import db_connection, get_repo_root
from src.services.audit import write_audit_log

from .anomalies import run_all_checks
from .categorizer import categorize
from .parsers import AmexParser, ChaseParser
from .repository import fetch_document, insert_transactions_from_dataframe, load_historical_for_anomaly_detection


class ExpenseIngestError(RuntimeError):
    pass


def _load_yaml(path: str) -> dict:
    import yaml

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _validate_config(repo_root: Path) -> list[str]:
    """Port of expense-recon/src/validators.py (minimal).

    Returns a list of error strings (empty list means OK).
    """

    errors: list[str] = []

    config_dir = repo_root / "config"
    categories_path = config_dir / "categories.yaml"
    rules_path = config_dir / "rules.yaml"
    accounts_path = config_dir / "accounts.yaml"

    # categories
    try:
        cfg = _load_yaml(str(categories_path))
    except FileNotFoundError:
        errors.append(f"categories.yaml not found at {categories_path}")
        cfg = {}
    except Exception as e:
        errors.append(f"categories.yaml: could not parse — {e}")
        cfg = {}

    if "mapping" not in cfg:
        errors.append("categories.yaml: missing required key 'mapping'")
    for k, v in (cfg.get("mapping", {}) or {}).items():
        if not isinstance(v, list) or len(v) != 2:
            errors.append(f"categories.yaml: mapping['{k}'] must be a 2-element list [category, subcategory]")
    if "default_category" not in cfg:
        errors.append("categories.yaml: missing required key 'default_category'")
    for k, v in (cfg.get("merchant_overrides", {}) or {}).items():
        if not isinstance(v, list) or len(v) != 2:
            errors.append(f"categories.yaml: merchant_overrides['{k}'] must be a 2-element list")

    # rules
    try:
        cfg = _load_yaml(str(rules_path))
    except FileNotFoundError:
        errors.append(f"rules.yaml not found at {rules_path}")
        cfg = {}
    except Exception as e:
        errors.append(f"rules.yaml: could not parse — {e}")
        cfg = {}

    rules = cfg.get("rules", cfg)
    required = ["duplicate_detection", "subscription_change", "large_transaction", "recurring_detection"]
    for r in required:
        if r not in rules:
            errors.append(f"rules.yaml: missing required rule section '{r}'")

    for rule_name, numeric_keys in [
        ("duplicate_detection", ["day_tolerance", "amount_tolerance"]),
        ("large_transaction", ["threshold"]),
        ("recurring_detection", ["min_occurrences", "variance_threshold"]),
        ("subscription_change", ["change_percent", "min_occurrences"]),
        ("velocity_anomaly", ["z_threshold", "min_months"]),
    ]:
        rule = rules.get(rule_name, {})
        for key in numeric_keys:
            if key in rule and not isinstance(rule[key], (int, float)):
                errors.append(f"rules.yaml: {rule_name}.{key} must be a number, got {type(rule[key]).__name__}")

    # accounts is optional
    try:
        cfg = _load_yaml(str(accounts_path))
    except FileNotFoundError:
        cfg = {}
    except Exception as e:
        errors.append(f"accounts.yaml: could not parse — {e}")
        cfg = {}

    for i, acct in enumerate(cfg.get("accounts", []) or []):
        if "nickname" not in acct:
            errors.append(f"accounts.yaml: account[{i}] missing required key 'nickname'")
        if "parser" not in acct:
            errors.append(f"accounts.yaml: account[{i}] missing required key 'parser'")

    return errors


def _detect_parser(df: pd.DataFrame):
    for parser_cls in [AmexParser, ChaseParser]:
        if parser_cls.can_parse(df):
            return parser_cls()
    return None


def _read_file(filepath: str) -> pd.DataFrame | None:
    import pdfplumber

    ext = os.path.splitext(filepath)[1].lower()
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(filepath)
    if ext == ".csv":
        for encoding in ["utf-8-sig", "latin-1", "cp1252"]:
            try:
                return pd.read_csv(filepath, encoding=encoding)
            except UnicodeDecodeError:
                continue
        return pd.read_csv(filepath)
    if ext == ".pdf":
        all_rows = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        clean_table = [row for row in table if any(row)]
                        if not clean_table:
                            continue
                        if all_rows and clean_table[0] == all_rows[0]:
                            clean_table = clean_table[1:]
                        all_rows.extend(clean_table)
        if not all_rows:
            return None
        max_cols = max(len(row) for row in all_rows)
        padded_rows = [row + [None] * (max_cols - len(row)) for row in all_rows]
        return pd.DataFrame(padded_rows[1:], columns=padded_rows[0])
    return None


def ingest_document(document_id: int) -> dict:
    """Ingest an uploaded expense document into expenses_transactions.

    Returns a small dict suitable for the API response.
    """

    repo_root = get_repo_root()
    config_errors = _validate_config(repo_root)
    if config_errors:
        raise ExpenseIngestError("Config validation failed: " + " | ".join(config_errors))

    with db_connection() as conn:
        doc = fetch_document(conn, document_id)
        if doc is None:
            raise ExpenseIngestError("Document not found")
        if str(doc["module_owner"]) != "expenses":
            raise ExpenseIngestError("Document module_owner must be 'expenses' for expense ingest")

        write_audit_log(
            conn,
            document_id=document_id,
            actor="system",
            action="expenses_ingest_started",
            details=f"storage_path={doc['storage_path']}",
        )

        storage_path = str(doc["storage_path"])
        full_path = (repo_root / Path(storage_path)).resolve()
        if not full_path.exists():
            raise ExpenseIngestError(f"Storage file not found: {storage_path}")

    # File read + parsing uses pandas; keep outside DB transaction.
    df = _read_file(str(full_path))
    if df is None:
        raise ExpenseIngestError("Could not read file (unsupported format or empty)")

    parser = _detect_parser(df)
    if not parser:
        raise ExpenseIngestError("Unrecognized statement format")

    clean_df, sanitize_report = parser.sanitize(df)
    txn_df = parser.parse(clean_df, os.path.basename(str(full_path)))
    txn_df = categorize(txn_df)

    with db_connection() as conn:
        historical_df = load_historical_for_anomaly_detection(conn)

    txn_df = run_all_checks(txn_df, historical_df=historical_df if len(historical_df) > 0 else None)

    with db_connection() as conn:
        doc = fetch_document(conn, document_id)
        if doc is None:
            raise ExpenseIngestError("Document not found")
        inserted = insert_transactions_from_dataframe(
            conn,
            document_id=document_id,
            institution_id=doc["institution_id"],
            df=txn_df,
        )

        write_audit_log(
            conn,
            document_id=document_id,
            actor="system",
            action="expenses_ingest_completed",
            details=f"inserted={inserted}, sanitizer_lines={len(sanitize_report)}",
        )

    return {
        "ok": True,
        "document_id": document_id,
        "inserted": inserted,
        "months": sorted([str(m) for m in txn_df.get("month", pd.Series([], dtype=str)).unique().tolist()]),
        "sanitize_report": sanitize_report,
    }
