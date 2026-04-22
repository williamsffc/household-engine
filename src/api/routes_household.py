from __future__ import annotations

from fastapi import APIRouter

from src.core.database import db_connection


router = APIRouter(prefix="/api/household", tags=["household"])


def _row_to_dict(row) -> dict:
    return {k: row[k] for k in row.keys()}


@router.get("/members")
def list_household_members(active_only: bool = True) -> list[dict]:
    where = "WHERE is_active = 1" if bool(active_only) else ""
    with db_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT id, display_name, role, is_active, created_at
            FROM household_members
            {where}
            ORDER BY id ASC;
            """
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

