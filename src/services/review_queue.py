from __future__ import annotations

import sqlite3

from src.payroll.repository import get_latest_paystub_for_document
from src.services.audit import write_audit_log


class ReviewQueueError(RuntimeError):
    pass


def _require_payroll_reviewable_document(conn: sqlite3.Connection, document_id: int) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM documents WHERE id = ?;", (int(document_id),)).fetchone()
    if row is None:
        raise ReviewQueueError("Document not found")
    if str(row["module_owner"]) != "payroll":
        raise ReviewQueueError("Only payroll documents support approval workflow")
    if str(row["status"]) != "in_review":
        raise ReviewQueueError("Document is not in_review")
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
    doc = _require_payroll_reviewable_document(conn, document_id)
    paystub = get_latest_paystub_for_document(conn, int(document_id))
    if paystub is None:
        raise ReviewQueueError("No payroll paystub found for document")
    if str(paystub.get("status")) != "draft":
        raise ReviewQueueError("Latest paystub is not draft; cannot approve")

    # Keep ownership honest: paystub and document must match member_id.
    if int(paystub.get("member_id")) != int(doc["member_id"]):
        raise ReviewQueueError("Member ownership mismatch between document and paystub")

    conn.execute(
        """
        UPDATE payroll_paystubs
        SET
            status = 'approved',
            decided_at = CURRENT_TIMESTAMP,
            decision_actor = ?,
            rejection_reason = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?;
        """,
        (str(actor or "user"), int(paystub["id"])),
    )
    conn.execute(
        "UPDATE documents SET status = 'approved', updated_at = CURRENT_TIMESTAMP WHERE id = ?;",
        (int(document_id),),
    )

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
    doc = _require_payroll_reviewable_document(conn, document_id)
    paystub = get_latest_paystub_for_document(conn, int(document_id))
    if paystub is None:
        raise ReviewQueueError("No payroll paystub found for document")
    if str(paystub.get("status")) != "draft":
        raise ReviewQueueError("Latest paystub is not draft; cannot reject")

    if int(paystub.get("member_id")) != int(doc["member_id"]):
        raise ReviewQueueError("Member ownership mismatch between document and paystub")

    conn.execute(
        """
        UPDATE payroll_paystubs
        SET
            status = 'rejected',
            decided_at = CURRENT_TIMESTAMP,
            decision_actor = ?,
            rejection_reason = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?;
        """,
        (str(actor or "user"), (str(reason).strip() if reason is not None and str(reason).strip() else None), int(paystub["id"])),
    )
    conn.execute(
        "UPDATE documents SET status = 'rejected', updated_at = CURRENT_TIMESTAMP WHERE id = ?;",
        (int(document_id),),
    )

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

    doc = conn.execute("SELECT * FROM documents WHERE id = ?;", (int(document_id),)).fetchone()
    if doc is None:
        raise ReviewQueueError("Document not found")
    if str(doc["module_owner"]) != "payroll":
        raise ReviewQueueError("Only payroll documents support reopen workflow")
    if doc["member_id"] is None:
        raise ReviewQueueError("Payroll documents must have member_id")

    doc_status = str(doc["status"] or "")
    if doc_status not in {"approved", "rejected"}:
        raise ReviewQueueError("Only approved or rejected documents can be reopened")

    paystub = get_latest_paystub_for_document(conn, int(document_id))
    if paystub is None:
        raise ReviewQueueError("No payroll paystub found for document")

    ps_status = str(paystub.get("status") or "")
    if ps_status not in {"approved", "rejected"}:
        raise ReviewQueueError("Latest paystub is not approved/rejected; cannot reopen")

    if int(paystub.get("member_id")) != int(doc["member_id"]):
        raise ReviewQueueError("Member ownership mismatch between document and paystub")

    conn.execute(
        """
        UPDATE payroll_paystubs
        SET
            status = 'draft',
            decided_at = NULL,
            decision_actor = NULL,
            rejection_reason = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?;
        """,
        (int(paystub["id"]),),
    )
    conn.execute(
        "UPDATE documents SET status = 'in_review', updated_at = CURRENT_TIMESTAMP WHERE id = ?;",
        (int(document_id),),
    )

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
