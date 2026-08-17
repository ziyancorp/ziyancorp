from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    shopee_url TEXT,
    tiktok_url TEXT,
    other_links TEXT,
    drive_folder_id TEXT NOT NULL,
    drive_folder_url TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'READY',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS assets (
    asset_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL REFERENCES products(product_id),
    original_name TEXT NOT NULL,
    drive_file_id TEXT NOT NULL,
    drive_file_url TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE'
);
CREATE TABLE IF NOT EXISTS processed_messages (
    telegram_chat_id INTEGER NOT NULL,
    telegram_message_id INTEGER NOT NULL,
    product_id TEXT,
    PRIMARY KEY (telegram_chat_id, telegram_message_id)
);
CREATE INDEX IF NOT EXISTS idx_products_title ON products(title);
CREATE INDEX IF NOT EXISTS idx_assets_product_id ON assets(product_id);
"""


class Database:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def message_seen(self, chat_id: int, message_id: int) -> bool:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM processed_messages WHERE telegram_chat_id=? AND telegram_message_id=?",
                (chat_id, message_id),
            ).fetchone()
            return row is not None

    def mark_message(self, chat_id: int, message_id: int, product_id: str | None = None) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO processed_messages(telegram_chat_id, telegram_message_id, product_id) VALUES (?, ?, ?)",
                (chat_id, message_id, product_id),
            )

    def insert_product(self, values: tuple) -> None:
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO products(product_id,title,description,shopee_url,tiktok_url,other_links,
                   drive_folder_id,drive_folder_url,status,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                values,
            )

    def update_product(self, product_id: str, title: str, description: str, shopee_url: str | None,
                       tiktok_url: str | None, other_links: str | None, updated_at: str) -> None:
        with self.connect() as conn:
            conn.execute(
                """UPDATE products SET title=?,description=?,shopee_url=?,tiktok_url=?,other_links=?,updated_at=?
                   WHERE product_id=?""",
                (title, description, shopee_url, tiktok_url, other_links, updated_at, product_id),
            )

    def get_product(self, product_id: str):
        with self.connect() as conn:
            return conn.execute("SELECT * FROM products WHERE product_id=?", (product_id,)).fetchone()

    def search_products(self, query: str, limit: int = 10):
        pattern = f"%{query}%"
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM products WHERE product_id LIKE ? OR title LIKE ? ORDER BY created_at DESC LIMIT ?",
                (pattern, pattern, limit),
            ).fetchall()

    def insert_asset(self, values: tuple) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO assets(asset_id,product_id,original_name,drive_file_id,drive_file_url,asset_type,created_at,status) VALUES (?,?,?,?,?,?,?,?)",
                values,
            )

    def get_asset(self, asset_id: str):
        with self.connect() as conn:
            return conn.execute("SELECT * FROM assets WHERE asset_id=?", (asset_id,)).fetchone()

    def list_assets(self, product_id: str):
        with self.connect() as conn:
            return conn.execute("SELECT * FROM assets WHERE product_id=? AND status='ACTIVE' ORDER BY created_at", (product_id,)).fetchall()

    def mark_asset_deleted(self, asset_id: str) -> None:
        with self.connect() as conn:
            conn.execute("UPDATE assets SET status='TRASHED' WHERE asset_id=?", (asset_id,))
