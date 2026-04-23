from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.core.database import db_connection, get_repo_root
from src.payroll.pii_scrubber import scrub_pii
from src.payroll.payroll_text_extract import extract_raw_payroll_text
from src.payroll.extractor_ocr import OcrUnavailableError
from src.payroll.repository import get_latest_paystub_for_document, list_lines_for_paystub
from src.payroll.review_artifacts import get_review_artifact_for_document, upsert_review_artifact
from src.services.review_queue import (
    ReviewQueueError,
    approve_payroll_review_item,
    reject_payroll_review_item,
    reopen_payroll_review_item,
)


router = APIRouter(prefix="/api/review-queue", tags=["review-queue"])


def _row_to_dict(row) -> dict[str, Any]:
    return {k: row[k] for k in row.keys()}


def _extract_and_scrub_redacted_text(*, storage_path: str) -> dict[str, Any]:
    """Regenerate redacted text on-demand (same path as payroll ingest: native PDF or OCR fallback)."""

    repo_root = get_repo_root()
    full_path = (repo_root / Path(storage_path)).resolve()
    if not full_path.exists():
        raise HTTPException(status_code=400, detail=f"Storage file not found: {storage_path}")

    try:
        bundle = extract_raw_payroll_text(full_path)
    except OcrUnavailableError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    scrub = scrub_pii(bundle.text)
    return {
        "redacted_text": scrub.redacted_text,
        "redaction_counts": scrub.redaction_counts,
        "text_chars": len(bundle.text or ""),
        "ocr_used_for_review": bundle.ocr_used,
        "extraction_source": bundle.extraction_source,
        "source": "regenerated_on_read",
    }


class RejectRequest(BaseModel):
    reason: str | None = None


class ReopenRequest(BaseModel):
    reason: str | None = None


@router.get("")
def list_review_queue() -> list[dict[str, Any]]:
    with db_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                id AS document_id,
                module_owner,
                original_filename,
                status,
                uploaded_at,
                ocr_used,
                notes
            FROM documents
            WHERE status = 'in_review'
            ORDER BY uploaded_at DESC, id DESC;
            """
        ).fetchall()
        return [_row_to_dict(r) for r in rows]


@router.get("/{document_id}")
def get_review_payload(document_id: int) -> dict[str, Any]:
    with db_connection() as conn:
        doc = conn.execute("SELECT * FROM documents WHERE id = ?;", (int(document_id),)).fetchone()
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found")

        doc_dict = _row_to_dict(doc)
        if str(doc_dict.get("status")) != "in_review":
            raise HTTPException(status_code=400, detail="Document is not in_review")

        module_owner = str(doc_dict.get("module_owner") or "")
        if module_owner != "payroll":
            raise HTTPException(status_code=400, detail="Review payload not implemented for this module_owner yet")

        paystub = get_latest_paystub_for_document(conn, int(document_id))
        if paystub is None:
            raise HTTPException(status_code=404, detail="No payroll paystub found for document")

        lines = list_lines_for_paystub(conn, int(paystub["id"]))

        artifact = get_review_artifact_for_document(conn, int(document_id))
        if artifact is None:
            # Build once, then persist for future views.
            regenerated = _extract_and_scrub_redacted_text(storage_path=str(doc_dict["storage_path"]))
            upsert_review_artifact(
                conn,
                document_id=int(document_id),
                paystub_id=int(paystub["id"]),
                redacted_text=str(regenerated.get("redacted_text") or ""),
                redaction_counts=dict(regenerated.get("redaction_counts") or {}),
                text_chars=int(regenerated.get("text_chars") or 0),
                ocr_used_for_review=bool(regenerated.get("ocr_used_for_review")),
                source="persisted_from_regeneration",
            )
            artifact = get_review_artifact_for_document(conn, int(document_id))
            if artifact is None:
                # Fallback (should not happen): remain honest and use regenerated payload.
                artifact = {
                    "redacted_text": regenerated.get("redacted_text") or "",
                    "redaction_counts": regenerated.get("redaction_counts") or {},
                    "source": "regenerated_on_read",
                }

    # Validation warnings: best-effort parse from validation_summary JSON string.
    warnings: list[str] = []
    extraction_source: str | None = None
    vs = paystub.get("validation_summary")
    if isinstance(vs, str) and vs.strip():
        try:
            parsed = json.loads(vs)
            if isinstance(parsed, dict):
                if isinstance(parsed.get("warnings"), list):
                    warnings = [str(w) for w in parsed.get("warnings") if w is not None]
                es = parsed.get("extraction_source")
                if isinstance(es, str) and es.strip():
                    extraction_source = es.strip()
        except Exception:
            warnings = []

    return {
        "document": {
            "id": doc_dict["id"],
            "module_owner": doc_dict["module_owner"],
            "original_filename": doc_dict["original_filename"],
            "status": doc_dict["status"],
            "uploaded_at": doc_dict.get("uploaded_at"),
            "ocr_used": doc_dict.get("ocr_used"),
        },
        "review": {
            "redacted_text": artifact.get("redacted_text") or "",
            "redaction_counts": artifact.get("redaction_counts") or {},
            "redacted_text_source": artifact.get("source") or "persisted",
            "extraction_source": extraction_source,
            "validation_warnings": warnings,
            "draft_paystub": paystub,
            "draft_lines": lines,
        },
    }


@router.post("/{document_id}/approve")
def approve_review_item(document_id: int) -> dict[str, Any]:
    with db_connection() as conn:
        try:
            return approve_payroll_review_item(conn, document_id=int(document_id), actor="user")
        except ReviewQueueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/{document_id}/reject")
def reject_review_item(document_id: int, body: RejectRequest) -> dict[str, Any]:
    with db_connection() as conn:
        try:
            return reject_payroll_review_item(
                conn,
                document_id=int(document_id),
                actor="user",
                reason=(body.reason if body else None),
            )
        except ReviewQueueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/{document_id}/reopen")
def reopen_review_item(document_id: int, body: ReopenRequest) -> dict[str, Any]:
    with db_connection() as conn:
        try:
            return reopen_payroll_review_item(
                conn,
                document_id=int(document_id),
                actor="user",
                reason=(body.reason if body else None),
            )
        except ReviewQueueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
