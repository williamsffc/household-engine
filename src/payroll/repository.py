from __future__ import annotations

import sqlite3
from typing import Any

from src.payroll.normalizer import DraftPaystub, DraftPayrollLine


def fetch_document(conn: sqlite3.Connection, document_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM documents WHERE id = ?;", (document_id,)).fetchone()


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {k: row[k] for k in row.keys()}


def delete_draft_for_document(conn: sqlite3.Connection, document_id: int) -> None:
    # delete lines by joining via paystub id
    paystub_rows = conn.execute(
        "SELECT id FROM payroll_paystubs WHERE document_id = ? AND status = 'draft';",
        (document_id,),
    ).fetchall()
    paystub_ids = [int(r["id"]) for r in paystub_rows]
    for pid in paystub_ids:
        conn.execute("DELETE FROM payroll_lines WHERE paystub_id = ?;", (pid,))
    conn.execute("DELETE FROM payroll_paystubs WHERE document_id = ? AND status = 'draft';", (document_id,))


def insert_draft_paystub(
    conn: sqlite3.Connection,
    *,
    document_id: int,
    member_id: int,
    institution_id: int | None,
    draft: DraftPaystub,
    validation_summary: str | None,
) -> int:
    cur = conn.execute(
        """
        INSERT INTO payroll_paystubs (
            document_id,
            member_id,
            institution_id,
            status,
            pay_date,
            period_start,
            period_end,
            gross_pay,
            net_pay,
            currency,
            validation_summary,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, 'draft', ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
        """,
        (
            document_id,
            member_id,
            institution_id,
            draft.pay_date,
            draft.period_start,
            draft.period_end,
            draft.gross_pay,
            draft.net_pay,
            draft.currency,
            validation_summary,
        ),
    )
    return int(cur.lastrowid)


def insert_draft_lines(conn: sqlite3.Connection, *, paystub_id: int, lines: list[DraftPayrollLine]) -> int:
    inserted = 0
    for i, ln in enumerate(lines):
        conn.execute(
            """
            INSERT INTO payroll_lines (
                paystub_id,
                category,
                description,
                amount,
                ytd_amount,
                display_order,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
            """,
            (
                paystub_id,
                ln.category,
                ln.description,
                float(ln.amount),
                float(ln.ytd_amount) if ln.ytd_amount is not None else None,
                int(ln.display_order) if ln.display_order is not None else i,
            ),
        )
        inserted += 1
    return inserted


def list_paystubs(
    conn: sqlite3.Connection,
    *,
    member_id: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    status: str | None = None,
    limit: int = 200,
) -> list[dict[str, Any]]:
    where: list[str] = []
    params: list[Any] = []

    if member_id is not None:
        where.append("member_id = ?")
        params.append(int(member_id))
    if start_date is not None:
        where.append("pay_date >= ?")
        params.append(start_date)
    if end_date is not None:
        where.append("pay_date <= ?")
        params.append(end_date)
    if status is not None:
        where.append("status = ?")
        params.append(status)

    sql = "SELECT * FROM payroll_paystubs"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY pay_date DESC, id DESC LIMIT ?;"
    params.append(int(limit))

    rows = conn.execute(sql, tuple(params)).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_paystub_by_id(conn: sqlite3.Connection, paystub_id: int) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM payroll_paystubs WHERE id = ?;", (int(paystub_id),)).fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


def list_lines_for_paystub(conn: sqlite3.Connection, paystub_id: int) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT *
        FROM payroll_lines
        WHERE paystub_id = ?
        ORDER BY COALESCE(display_order, id) ASC, id ASC;
        """,
        (int(paystub_id),),
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_latest_paystub_for_document(conn: sqlite3.Connection, document_id: int) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT *
        FROM payroll_paystubs
        WHERE document_id = ?
        ORDER BY created_at DESC, id DESC
        LIMIT 1;
        """,
        (int(document_id),),
    ).fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


def get_monthly_payroll_summary(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT month, member_id, total_net_pay, total_gross_pay, paystub_count
        FROM vw_monthly_payroll
        ORDER BY month DESC, member_id ASC;
        """
    ).fetchall()
    return [_row_to_dict(r) for r in rows]
