from __future__ import annotations

import sqlite3

from src.payroll.repository import get_latest_paystub_for_document
from src.services.audit import write_audit_log


class ReviewQueueError(RuntimeError):
    def __init__(self, message: str, *, status_code: int = 400):
        super().__init__(message)
        self.status_code = int(status_code)


def _begin_immediate(conn: sqlite3.Connection) -> None:
    # Make read-check-update sequences atomic enough for local SQLite concurrency.
    conn.execute("BEGIN IMMEDIATE;")


def _conflict(message: str) -> ReviewQueueError:
    return ReviewQueueError(message, status_code=409)


def _require_payroll_reviewable_document(conn: sqlite3.Connection, document_id: int) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM documents WHERE id = ?;", (int(document_id),)).fetchone()
    if row is None:
        raise ReviewQueueError("Document not found")
    if str(row["module_owner"]) != "payroll":
        raise ReviewQueueError("Only payroll documents support approval workflow")
    if str(row["status"]) != "in_review":
        raise _conflict("Document is not in_review")
    if row["member_id"] is None:
        # Should not happen for payroll ingest, but keep rule explicit.
        raise ReviewQueueError("Payroll documents must have member_id")
    return row


def approve_payroll_review_item(
    conn: sqlite3.Connection,
    *,
    document_id: int,
    actor: str = "user",
) -> dict:
    _begin_immediate(conn)
    doc = _require_payroll_reviewable_document(conn, document_id)
    paystub = get_latest_paystub_for_document(conn, int(document_id))
    if paystub is None:
        raise ReviewQueueError("No payroll paystub found for document")
    if str(paystub.get("status")) != "draft":
        raise _conflict("Latest paystub is not draft; cannot approve")

    # Keep ownership honest: paystub and document must match member_id.
    if int(paystub.get("member_id")) != int(doc["member_id"]):
        raise ReviewQueueError("Member ownership mismatch between document and paystub")

    cur_ps = conn.execute(
        """
        UPDATE payroll_paystubs
        SET
            status = 'approved',
            decided_at = CURRENT_TIMESTAMP,
            decision_actor = ?,
            rejection_reason = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND status = 'draft';
        """,
        (str(actor or "user"), int(paystub["id"])),
    )
    if int(cur_ps.rowcount or 0) != 1:
        # Someone else decided already; avoid writing duplicate audit rows.
        raise _conflict("Approve no-op: paystub is no longer draft")

    cur_doc = conn.execute(
        "UPDATE documents SET status = 'approved', updated_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'in_review';",
        (int(document_id),),
    )
    if int(cur_doc.rowcount or 0) != 1:
        raise _conflict("Approve no-op: document is no longer in_review")

    write_audit_log(
        conn,
        document_id=int(document_id),
        actor=str(actor or "user"),
        action="payroll_approved",
        details=f"paystub_id={int(paystub['id'])}, member_id={int(doc['member_id'])}",
    )

    return {"ok": True, "document_id": int(document_id), "paystub_id": int(paystub["id"]), "status": "approved"}


def reject_payroll_review_item(
    conn: sqlite3.Connection,
    *,
    document_id: int,
    actor: str = "user",
    reason: str | None = None,
) -> dict:
    _begin_immediate(conn)
    doc = _require_payroll_reviewable_document(conn, document_id)
    paystub = get_latest_paystub_for_document(conn, int(document_id))
    if paystub is None:
        raise ReviewQueueError("No payroll paystub found for document")
    if str(paystub.get("status")) != "draft":
        raise _conflict("Latest paystub is not draft; cannot reject")

    if int(paystub.get("member_id")) != int(doc["member_id"]):
        raise ReviewQueueError("Member ownership mismatch between document and paystub")

    cur_ps = conn.execute(
        """
        UPDATE payroll_paystubs
        SET
            status = 'rejected',
            decided_at = CURRENT_TIMESTAMP,
            decision_actor = ?,
            rejection_reason = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND status = 'draft';
        """,
        (str(actor or "user"), (str(reason).strip() if reason is not None and str(reason).strip() else None), int(paystub["id"])),
    )
    if int(cur_ps.rowcount or 0) != 1:
        raise _conflict("Reject no-op: paystub is no longer draft")

    cur_doc = conn.execute(
        "UPDATE documents SET status = 'rejected', updated_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'in_review';",
        (int(document_id),),
    )
    if int(cur_doc.rowcount or 0) != 1:
        raise _conflict("Reject no-op: document is no longer in_review")

    details = f"paystub_id={int(paystub['id'])}, member_id={int(doc['member_id'])}"
    if reason is not None and str(reason).strip():
        details += f", reason={str(reason).strip()}"

    write_audit_log(
        conn,
        document_id=int(document_id),
        actor=str(actor or "user"),
        action="payroll_rejected",
        details=details,
    )

    return {"ok": True, "document_id": int(document_id), "paystub_id": int(paystub["id"]), "status": "rejected"}


def reopen_payroll_review_item(
    conn: sqlite3.Connection,
    *,
    document_id: int,
    actor: str = "user",
    reason: str | None = None,
) -> dict:
    """Reopen an approved/rejected payroll item back into review (Step 25).

    This:
    - moves the document back to documents.status='in_review'
    - moves the latest paystub back to payroll_paystubs.status='draft'
    - clears terminal decision metadata on the paystub (audit log preserves history)
    """

    _begin_immediate(conn)
    doc = conn.execute("SELECT * FROM documents WHERE id = ?;", (int(document_id),)).fetchone()
    if doc is None:
        raise ReviewQueueError("Document not found")
    if str(doc["module_owner"]) != "payroll":
        raise ReviewQueueError("Only payroll documents support reopen workflow")
    if doc["member_id"] is None:
        raise ReviewQueueError("Payroll documents must have member_id")

    doc_status = str(doc["status"] or "")
    if doc_status not in {"approved", "rejected"}:
        raise _conflict("Only approved or rejected documents can be reopened")

    paystub = get_latest_paystub_for_document(conn, int(document_id))
    if paystub is None:
        raise ReviewQueueError("No payroll paystub found for document")

    ps_status = str(paystub.get("status") or "")
    if ps_status not in {"approved", "rejected"}:
        raise _conflict("Latest paystub is not approved/rejected; cannot reopen")

    if int(paystub.get("member_id")) != int(doc["member_id"]):
        raise ReviewQueueError("Member ownership mismatch between document and paystub")

    cur_ps = conn.execute(
        """
        UPDATE payroll_paystubs
        SET
            status = 'draft',
            decided_at = NULL,
            decision_actor = NULL,
            rejection_reason = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND status IN ('approved', 'rejected');
        """,
        (int(paystub["id"]),),
    )
    if int(cur_ps.rowcount or 0) != 1:
        raise _conflict("Reopen no-op: paystub is no longer approved/rejected")

    cur_doc = conn.execute(
        "UPDATE documents SET status = 'in_review', updated_at = CURRENT_TIMESTAMP WHERE id = ? AND status IN ('approved','rejected');",
        (int(document_id),),
    )
    if int(cur_doc.rowcount or 0) != 1:
        raise _conflict("Reopen no-op: document is no longer approved/rejected")

    details = (
        f"paystub_id={int(paystub['id'])}, member_id={int(doc['member_id'])}, "
        f"from_document_status={doc_status}, from_paystub_status={ps_status}"
    )
    if reason is not None and str(reason).strip():
        details += f", reason={str(reason).strip()}"

    write_audit_log(
        conn,
        document_id=int(document_id),
        actor=str(actor or "user"),
        action="payroll_reopened",
        details=details,
    )

    return {"ok": True, "document_id": int(document_id), "paystub_id": int(paystub["id"]), "status": "in_review"}
