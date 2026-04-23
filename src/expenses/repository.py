from __future__ import annotations

import sqlite3
from typing import Any

import pandas as pd


def _as_sqlite_bool(v: Any) -> int:
    """Coerce pandas/numpy truthy and NaN to 0/1 for SQLite INTEGER flags."""
    if v is None:
        return 0
    try:
        if pd.isna(v):
            return 0
    except (TypeError, ValueError):
        pass
    return 1 if bool(v) else 0


def _flag_reason_text(v: Any) -> str | None:
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    s = str(v).strip()
    return s if s else None


def _txn_type_outflow(v: Any) -> str:
    """Persist expense vs fee; insert path only ever stores outflows."""
    s = (str(v).strip().lower() if v is not None and not (isinstance(v, float) and pd.isna(v)) else "") or "expense"
    return s if s in ("expense", "fee") else "expense"


def fetch_document(conn: sqlite3.Connection, document_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM documents WHERE id = ?;", (document_id,)).fetchone()


def delete_transactions_for_document(conn: sqlite3.Connection, document_id: int) -> int:
    cur = conn.execute("DELETE FROM expenses_transactions WHERE document_id = ?;", (document_id,))
    return int(cur.rowcount or 0)


def insert_transactions_from_dataframe(
    conn: sqlite3.Connection,
    *,
    document_id: int,
    institution_id: int | None,
    df: pd.DataFrame,
    currency: str = "USD",
) -> int:
    """Write normalized expense transactions into expenses_transactions.

    This keeps Step 3 minimal by:
    - deleting prior rows for the document_id (idempotent re-ingest)
    - inserting rows directly (no ORM)
    """

    if df is None or len(df) == 0:
        delete_transactions_for_document(conn, document_id)
        return 0

    delete_transactions_for_document(conn, document_id)

    records = df.to_dict("records")
    inserted = 0
    for rec in records:
        # Only store outflows (expense + fee) as expenses_transactions.
        if rec.get("txn_type") not in ("expense", "fee"):
            continue

        txn_date = pd.to_datetime(rec["date"]).strftime("%Y-%m-%d")
        acc = rec.get("account", "")
        account_label = str(acc).strip() if acc is not None and not (isinstance(acc, float) and pd.isna(acc)) else None
        if account_label == "":
            account_label = None

        conn.execute(
            """
            INSERT INTO expenses_transactions (
                document_id,
                institution_id,
                transaction_date,
                post_date,
                amount,
                merchant_raw,
                merchant_normalized,
                category,
                subcategory,
                currency,
                fingerprint,
                is_flagged,
                flag_reason,
                is_recurring,
                txn_type,
                account_label
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                document_id,
                institution_id,
                txn_date,
                None,
                float(rec["amount"]),
                str(rec.get("description", "")),
                str(rec.get("merchant_clean", "")),
                str(rec.get("category", "")) if rec.get("category") is not None else None,
                str(rec.get("subcategory", "")) if rec.get("subcategory") is not None else None,
                currency,
                str(rec.get("id", "")) or None,
                _as_sqlite_bool(rec.get("is_flagged")),
                _flag_reason_text(rec.get("flag_reason")),
                _as_sqlite_bool(rec.get("is_recurring")),
                _txn_type_outflow(rec.get("txn_type")),
                account_label,
            ),
        )
        inserted += 1

    return inserted


def list_transactions(
    conn: sqlite3.Connection,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    category: str | None = None,
    institution_id: int | None = None,
    limit: int = 500,
) -> list[dict[str, Any]]:
    where: list[str] = []
    params: list[Any] = []

    if start_date is not None:
        where.append("transaction_date >= ?")
        params.append(start_date)
    if end_date is not None:
        where.append("transaction_date <= ?")
        params.append(end_date)
    if category is not None:
        where.append("category = ?")
        params.append(category)
    if institution_id is not None:
        where.append("institution_id = ?")
        params.append(institution_id)

    sql = "SELECT * FROM expenses_transactions"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY transaction_date DESC, id DESC LIMIT ?;"
    params.append(int(limit))

    rows = conn.execute(sql, tuple(params)).fetchall()
    return [{k: row[k] for k in row.keys()} for row in rows]


def load_historical_for_anomaly_detection(conn: sqlite3.Connection) -> pd.DataFrame:
    """Load historical outflows into the schema expected by anomalies.run_all_checks."""

    rows = conn.execute(
        """
        SELECT
            transaction_date,
            amount,
            merchant_raw,
            merchant_normalized,
            category,
            subcategory,
            fingerprint,
            is_flagged,
            flag_reason,
            is_recurring,
            txn_type,
            account_label
        FROM expenses_transactions
        ORDER BY transaction_date ASC;
        """
    ).fetchall()

    if not rows:
        return pd.DataFrame()

    data = []
    for r in rows:
        date = r["transaction_date"]
        month = str(date)[:7]
        tt = (r["txn_type"] or "expense").strip().lower()
        if tt not in ("expense", "fee"):
            tt = "expense"
        fr = r["flag_reason"]
        if fr is None:
            fr = ""
        acc = r["account_label"] or ""
        data.append(
            {
                "id": r["fingerprint"] or "",
                "date": pd.to_datetime(date),
                "description": r["merchant_raw"],
                "merchant_clean": r["merchant_normalized"] or r["merchant_raw"],
                "amount": float(r["amount"]),
                "txn_type": tt,
                "category": r["category"] or "",
                "subcategory": r["subcategory"] or "",
                "account": acc,
                "account_type": "",
                "is_recurring": bool(r["is_recurring"]),
                "is_flagged": bool(r["is_flagged"]),
                "flag_reason": fr,
                "month": month,
                "source_file": "",
                "imported_at": "",
            }
        )

    return pd.DataFrame(data)


def get_monthly_expense_summary(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT month, total_expenses, transaction_count
        FROM vw_monthly_expenses
        ORDER BY month DESC;
        """
    ).fetchall()
    return [{k: row[k] for k in row.keys()} for row in rows]


def get_expense_category_breakdown(conn: sqlite3.Connection, *, limit: int = 50) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT
            COALESCE(category, 'Uncategorized') AS category,
            ROUND(SUM(amount), 2) AS total_amount,
            COUNT(*) AS transaction_count
        FROM expenses_transactions
        GROUP BY COALESCE(category, 'Uncategorized')
        ORDER BY total_amount DESC
        LIMIT ?;
        """,
        (int(limit),),
    ).fetchall()
    return [{k: row[k] for k in row.keys()} for row in rows]


def get_recent_expense_activity(conn: sqlite3.Connection, *, limit: int = 25) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT
            document_id,
            transaction_date,
            merchant_normalized,
            category,
            amount
        FROM expenses_transactions
        ORDER BY transaction_date DESC, id DESC
        LIMIT ?;
        """,
        (int(limit),),
    ).fetchall()
    return [{k: row[k] for k in row.keys()} for row in rows]


def get_latest_expense_month(conn: sqlite3.Connection) -> str | None:
    row = conn.execute(
        "SELECT month FROM vw_monthly_expenses ORDER BY month DESC LIMIT 1;"
    ).fetchone()
    if row is None:
        return None
    return str(row["month"])


def get_month_total_expenses(conn: sqlite3.Connection, *, month: str) -> float:
    row = conn.execute(
        "SELECT total_expenses FROM vw_monthly_expenses WHERE month = ? LIMIT 1;",
        (month,),
    ).fetchone()
    if row is None or row["total_expenses"] is None:
        return 0.0
    return float(row["total_expenses"])
