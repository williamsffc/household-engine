from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.core.database import db_connection
from src.payroll.ingest import PayrollIngestError, ingest_payroll_document
from src.payroll.repository import get_monthly_payroll_summary, get_paystub_by_id, list_lines_for_paystub, list_paystubs
from src.services.audit import write_audit_log


router = APIRouter(prefix="/api/payroll", tags=["payroll"])


@router.post("/documents/{document_id}/ingest")
def ingest_payroll(document_id: int) -> dict:
    try:
        result = ingest_payroll_document(document_id)
    except PayrollIngestError as e:
        # Audit failed attempts too (useful for repeated use + troubleshooting).
        with db_connection() as conn:
            write_audit_log(
                conn,
                document_id=document_id,
                actor="system",
                action="payroll_ingest_failed",
                details=str(e),
            )
        raise HTTPException(status_code=400, detail=str(e)) from e

    # Audit: API-level event (separate from pipeline-internal entries).
    with db_connection() as conn:
        write_audit_log(
            conn,
            document_id=document_id,
            actor="system",
            action="payroll_ingest_requested",
            details="Ingest called via /api/payroll/documents/{id}/ingest",
        )

    return result


@router.get("/paystubs")
def list_payroll_paystubs(
    member_id: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    status: str | None = None,
    limit: int = 200,
) -> list[dict]:
    # Keep params intentionally lightweight; repository builds SQL safely with bind params.
    limit = max(1, min(int(limit), 500))
    with db_connection() as conn:
        return list_paystubs(
            conn,
            member_id=member_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            limit=limit,
        )


@router.get("/paystubs/{paystub_id}")
def get_payroll_paystub(paystub_id: int) -> dict:
    with db_connection() as conn:
        paystub = get_paystub_by_id(conn, paystub_id)
        if paystub is None:
            raise HTTPException(status_code=404, detail="Paystub not found")
        lines = list_lines_for_paystub(conn, paystub_id)

    return {"paystub": paystub, "lines": lines}


@router.get("/monthly")
def payroll_monthly() -> list[dict]:
    """View-backed monthly payroll summary (approved-only)."""
    with db_connection() as conn:
        return get_monthly_payroll_summary(conn)
