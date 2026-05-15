"""Database utilities for Taiwan company crawler."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS companies (
    tax_id TEXT PRIMARY KEY,
    name TEXT,
    status TEXT,
    owner TEXT,
    capital TEXT,
    setup_date TEXT,
    address TEXT,
    business_scope TEXT,
    source TEXT,
    source_url TEXT,
    retrieved_at TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);
"""

UPSERT_SQL = """
INSERT INTO companies (
    tax_id, name, status, owner, capital, setup_date,
    address, business_scope, source, source_url, retrieved_at
)
VALUES (
    :tax_id, :name, :status, :owner, :capital, :setup_date,
    :address, :business_scope, :source, :source_url, :retrieved_at
)
ON CONFLICT(tax_id) DO UPDATE SET
    name=excluded.name,
    status=excluded.status,
    owner=excluded.owner,
    capital=excluded.capital,
    setup_date=excluded.setup_date,
    address=excluded.address,
    business_scope=excluded.business_scope,
    source=excluded.source,
    source_url=excluded.source_url,
    retrieved_at=excluded.retrieved_at,
    updated_at=datetime('now');
"""


def connect_db(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(SCHEMA_SQL)
    conn.commit()


def upsert_company(conn: sqlite3.Connection, row: dict) -> None:
    if not row.get("tax_id"):
        return
    conn.execute(UPSERT_SQL, row)
