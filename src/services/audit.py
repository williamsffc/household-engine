from __future__ import annotations

import sqlite3


def write_audit_log(
    conn: sqlite3.Connection,
    *,
    document_id: int | None,
    actor: str,
    action: str,
    details: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO audit_log (document_id, actor, action, details)
        VALUES (?, ?, ?, ?);
        """,
        (document_id, actor, action, details),
    )