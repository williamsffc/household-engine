from __future__ import annotations

import sqlite3
from typing import Any


def get_recent_documents(conn: sqlite3.Connection, *, limit: int = 10) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT
            id AS document_id,
            module_owner,
            original_filename,
            status,
            uploaded_at
        FROM documents
        ORDER BY uploaded_at DESC, id DESC
        LIMIT ?;
        """,
        (int(limit),),
    ).fetchall()
    return [{k: row[k] for k in row.keys()} for row in rows]
