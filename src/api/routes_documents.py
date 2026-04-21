from __future__ import annotations

import hashlib
import mimetypes
import sqlite3
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from src.core.database import db_connection, get_repo_root
from src.services.audit import write_audit_log


router = APIRouter(prefix="/api/documents", tags=["documents"])

_REPO_ROOT = get_repo_root()
_RAW_DIR = _REPO_ROOT / "data" / "raw"
_ALLOWED_MODULE_OWNERS = {"expenses", "payroll"}
_ALLOWED_EXTENSIONS = {
    ".pdf",
    ".csv",
    ".txt",
    ".xlsx",
    ".xls",
    ".png",
    ".jpg",
    ".jpeg",
}


class DocumentCreateResponse(BaseModel):
    document_id: int
    status: str
    module_owner: str


def _infer_mime_type(upload: UploadFile, original_filename: str) -> str | None:
    if upload.content_type:
        return upload.content_type
    guessed, _ = mimetypes.guess_type(original_filename)
    return guessed


def _make_safe_filename(original_filename: str) -> str:
    suffix = Path(original_filename).suffix.lower()
    return f"{uuid4().hex}{suffix}"


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {k: row[k] for k in row.keys()}


def _validate_module_owner(module_owner: str) -> str:
    normalized = module_owner.strip().lower()
    if normalized not in _ALLOWED_MODULE_OWNERS:
        raise HTTPException(
            status_code=400,
            detail="module_owner must be one of: expenses, payroll",
        )
    return normalized


def _validate_extension(filename: str) -> None:
    suffix = Path(filename).suffix.lower()
    if suffix not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension: {suffix or '[none]'}",
        )


async def _save_and_hash(upload: UploadFile, dest_path: Path) -> tuple[str, int]:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    hasher = hashlib.sha256()
    total_bytes = 0

    try:
        with dest_path.open("wb") as f:
            while True:
                chunk = await upload.read(1024 * 1024)
                if not chunk:
                    break
                hasher.update(chunk)
                f.write(chunk)
                total_bytes += len(chunk)
    finally:
        await upload.close()

    return hasher.hexdigest(), total_bytes


def _ensure_document(conn: sqlite3.Connection, document_id: int) -> sqlite3.Row:
    row = conn.execute(
        "SELECT * FROM documents WHERE id = ?;",
        (document_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return row


def _insert_processing_run(
    conn: sqlite3.Connection,
    *,
    document_id: int,
    module_owner: str,
    stage: str,
    outcome: str,
    message: str | None,
) -> None:
    conn.execute(
        """
        INSERT INTO processing_runs (document_id, module_owner, stage, outcome, message)
        VALUES (?, ?, ?, ?, ?);
        """,
        (document_id, module_owner, stage, outcome, message),
    )


@router.post("/upload", response_model=DocumentCreateResponse)
async def upload_document(
    file: UploadFile = File(...),
    module_owner: str = Form(...),
    member_id: int | None = Form(None),
    institution_id: int | None = Form(None),
) -> DocumentCreateResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    normalized_module_owner = _validate_module_owner(module_owner)
    _validate_extension(file.filename)

    original_filename = file.filename
    safe_filename = _make_safe_filename(original_filename)
    storage_path = _RAW_DIR / safe_filename

    file_hash, total_bytes = await _save_and_hash(file, storage_path)
    if total_bytes == 0:
        try:
            if storage_path.exists():
                storage_path.unlink()
        except OSError:
            pass
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    mime_type = _infer_mime_type(file, original_filename)

    with db_connection() as conn:
        try:
            cur = conn.execute(
                """
                INSERT INTO documents (
                    filename,
                    original_filename,
                    module_owner,
                    status,
                    file_hash,
                    mime_type,
                    storage_path,
                    member_id,
                    institution_id,
                    ocr_used,
                    uploaded_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                (
                    safe_filename,
                    original_filename,
                    normalized_module_owner,
                    "uploaded",
                    file_hash,
                    mime_type,
                    str(Path("data") / "raw" / safe_filename),
                    member_id,
                    institution_id,
                ),
            )
            document_id = int(cur.lastrowid)

            write_audit_log(
                conn,
                document_id=document_id,
                actor="system",
                action="uploaded",
                details=f"module_owner={normalized_module_owner}, original_filename={original_filename}",
            )

        except sqlite3.IntegrityError as e:
            try:
                if storage_path.exists():
                    storage_path.unlink()
            except OSError:
                pass

            msg = str(e).lower()
            if "documents.file_hash" in msg or "file_hash" in msg:
                raise HTTPException(status_code=409, detail="Duplicate file_hash") from e
            raise HTTPException(status_code=400, detail="Insert failed") from e

    return DocumentCreateResponse(
        document_id=document_id,
        status="uploaded",
        module_owner=normalized_module_owner,
    )


@router.get("")
def list_documents(
    module_owner: str | None = None,
    status: str | None = None,
    member_id: int | None = None,
) -> list[dict[str, Any]]:
    where: list[str] = []
    params: list[Any] = []

    if module_owner is not None:
        where.append("module_owner = ?")
        params.append(_validate_module_owner(module_owner))
    if status is not None:
        where.append("status = ?")
        params.append(status)
    if member_id is not None:
        where.append("member_id = ?")
        params.append(member_id)

    sql = "SELECT * FROM documents"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY uploaded_at DESC;"

    with db_connection() as conn:
        rows = conn.execute(sql, tuple(params)).fetchall()
        return [_row_to_dict(r) for r in rows]


@router.get("/{document_id}")
def get_document(document_id: int) -> dict[str, Any]:
    with db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE id = ?;",
            (document_id,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Document not found")
        return _row_to_dict(row)


@router.post("/{document_id}/process")
def process_document(document_id: int) -> dict[str, Any]:
    with db_connection() as conn:
        doc = _ensure_document(conn, document_id)
        module_owner = str(doc["module_owner"])

        _insert_processing_run(
            conn,
            document_id=document_id,
            module_owner=module_owner,
            stage="placeholder",
            outcome="success",
            message="Processing not implemented yet (stub).",
        )
        write_audit_log(
            conn,
            document_id=document_id,
            actor="system",
            action="process_requested",
            details="Processing stub invoked; no module pipeline implemented yet.",
        )

        return {
            "document_id": document_id,
            "status": str(doc["status"]),
            "module_owner": module_owner,
            "message": "Processing not implemented yet (stub).",
        }


@router.post("/{document_id}/reprocess")
def reprocess_document(document_id: int) -> dict[str, Any]:
    with db_connection() as conn:
        doc = _ensure_document(conn, document_id)
        module_owner = str(doc["module_owner"])

        _insert_processing_run(
            conn,
            document_id=document_id,
            module_owner=module_owner,
            stage="placeholder",
            outcome="success",
            message="Reprocessing not implemented yet (stub).",
        )
        write_audit_log(
            conn,
            document_id=document_id,
            actor="system",
            action="reprocess_requested",
            details="Reprocessing stub invoked; no module pipeline implemented yet.",
        )

        return {
            "document_id": document_id,
            "status": str(doc["status"]),
            "module_owner": module_owner,
            "message": "Reprocessing not implemented yet (stub).",
        }