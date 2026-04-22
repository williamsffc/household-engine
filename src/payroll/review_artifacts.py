from __future__ import annotations

import json
import sqlite3
from typing import Any


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {k: row[k] for k in row.keys()}


def get_review_artifact_for_document(conn: sqlite3.Connection, document_id: int) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT *
        FROM payroll_review_artifacts
        WHERE document_id = ?
        LIMIT 1;
        """,
        (int(document_id),),
    ).fetchone()
    if row is None:
        return None
    out = _row_to_dict(row)
    # Best-effort decode counts.
    rc = out.get("redaction_counts_json")
    if isinstance(rc, str) and rc.strip():
        try:
            out["redaction_counts"] = json.loads(rc)
        except Exception:
            out["redaction_counts"] = {}
    else:
        out["redaction_counts"] = {}
    return out


def upsert_review_artifact(
    conn: sqlite3.Connection,
    *,
    document_id: int,
    paystub_id: int | None,
    redacted_text: str,
    redaction_counts: dict[str, Any],
    text_chars: int | None,
    ocr_used_for_review: bool,
    source: str = "persisted",
) -> None:
    conn.execute(
        """
        INSERT INTO payroll_review_artifacts (
            document_id,
            paystub_id,
            redacted_text,
            redaction_counts_json,
            text_chars,
            ocr_used_for_review,
            source,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT(document_id) DO UPDATE SET
            paystub_id = excluded.paystub_id,
            redacted_text = excluded.redacted_text,
            redaction_counts_json = excluded.redaction_counts_json,
            text_chars = excluded.text_chars,
            ocr_used_for_review = excluded.ocr_used_for_review,
            source = excluded.source,
            updated_at = CURRENT_TIMESTAMP;
        """,
        (
            int(document_id),
            int(paystub_id) if paystub_id is not None else None,
            str(redacted_text or ""),
            json.dumps(redaction_counts or {}),
            int(text_chars) if text_chars is not None else None,
            1 if bool(ocr_used_for_review) else 0,
            str(source or "persisted"),
        ),
    )

