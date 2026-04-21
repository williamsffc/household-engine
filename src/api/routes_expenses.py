from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.core.database import db_connection
from src.services.audit import write_audit_log
from src.expenses.ingest import ExpenseIngestError, ingest_document
from src.expenses.repository import (
    get_expense_category_breakdown,
    get_monthly_expense_summary,
    get_recent_expense_activity,
    list_transactions,
)


router = APIRouter(prefix="/api/expenses", tags=["expenses"])


@router.get("/transactions")
def get_transactions(
    start_date: str | None = None,
    end_date: str | None = None,
    category: str | None = None,
    institution_id: int | None = None,
    limit: int = 500,
) -> list[dict]:
    with db_connection() as conn:
        return list_transactions(
            conn,
            start_date=start_date,
            end_date=end_date,
            category=category,
            institution_id=institution_id,
            limit=limit,
        )


@router.post("/documents/{document_id}/ingest")
def ingest_expense_document(document_id: int) -> dict:
    try:
        result = ingest_document(document_id)
    except ExpenseIngestError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    # Audit: API-level event (separate from pipeline-internal entries).
    with db_connection() as conn:
        write_audit_log(
            conn,
            document_id=document_id,
            actor="system",
            action="expenses_ingest_requested",
            details="Ingest called via /api/expenses/documents/{id}/ingest",
        )

    return result


@router.get("/monthly")
def get_monthly_expenses() -> list[dict]:
    with db_connection() as conn:
        return get_monthly_expense_summary(conn)


@router.get("/categories")
def get_expense_categories(limit: int = 50) -> list[dict]:
    with db_connection() as conn:
        return get_expense_category_breakdown(conn, limit=limit)


@router.get("/recent")
def get_expense_recent(limit: int = 25) -> list[dict]:
    with db_connection() as conn:
        return get_recent_expense_activity(conn, limit=limit)
