"""
Tiny SQLite user store. Deliberately not an ORM — one table, a handful of
queries, plain sqlite3 keeps this module's footprint small and self-contained.
Fully separate from app/jobs.py's in-memory job store; nothing here is
imported by, or imports from, the job/pipeline/export code.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from app.config import STORAGE_DIR

DB_PATH = STORAGE_DIR / "auth.db"


def _init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )


@contextmanager
def get_db():
    conn = sqlite3.connect(Path(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


_init_db()
