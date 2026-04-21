from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


_REPO_ROOT = Path(__file__).resolve().parents[2]
_DB_PATH = _REPO_ROOT / "household.db"
_MIGRATIONS_DIR = _REPO_ROOT / "migrations"


def get_repo_root() -> Path:
    return _REPO_ROOT


def get_db_path() -> Path:
    return _DB_PATH


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _exec_pragmas(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")


def _ensure_migrations_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            name TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def _migration_applied(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM schema_migrations WHERE name = ? LIMIT 1;",
        (name,),
    ).fetchone()
    return row is not None


def _apply_migration(conn: sqlite3.Connection, name: str, sql_text: str) -> None:
    conn.executescript(sql_text)
    conn.execute("INSERT INTO schema_migrations (name) VALUES (?);", (name,))


def init_db() -> None:
    with connect() as conn:
        _exec_pragmas(conn)
        _ensure_migrations_table(conn)

        migration_files = sorted(_MIGRATIONS_DIR.glob("*.sql"))
        for migration_path in migration_files:
            migration_name = migration_path.name
            if _migration_applied(conn, migration_name):
                continue

            sql_text = migration_path.read_text(encoding="utf-8")
            _apply_migration(conn, migration_name, sql_text)


@contextmanager
def db_connection() -> Iterator[sqlite3.Connection]:
    conn = connect()
    try:
        _exec_pragmas(conn)
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()