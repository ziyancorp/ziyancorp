from __future__ import annotations

import json
import shutil
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .db import Database
from .google_workspace import GoogleWorkspace
from .parser import ProductDraft, safe_name


@dataclass
class LocalFile:
    path: Path
    original_name: str
    asset_type: str


class ArchiveService:
    def __init__(self, db: Database, google: GoogleWorkspace, timezone_name: str = "Asia/Jakarta"):
        self.db = db
        self.google = google
        self.tz = ZoneInfo(timezone_name)

    def _now(self) -> str:
        return datetime.now(self.tz).isoformat(timespec="seconds")

    def _ids(self) -> tuple[str, str]:
        stamp = datetime.now(self.tz).strftime("%Y%m%d")
        suffix = uuid.uuid4().hex[:6].upper()
        return f"PROD-{stamp}-{suffix}", f"AST-{stamp}-{uuid.uuid4().hex[:6].upper()}"

    @staticmethod
    def _folder_key(asset_type: str) -> str:
        return {"video": "01_VIDEO", "photo": "02_FOTO"}.get(asset_type, "03_OTHER")

    def _product_values(self, product_id: str, draft: ProductDraft, folder_url: str, count: int, created: str, status: str) -> list[str | int | None]:
        return [
            product_id, draft.title, draft.description, draft.shopee_url or "", draft.tiktok_url or "",
            " | ".join(draft.other_links), folder_url, count, created, self._now(), status,
        ]

    def _write_metadata(self, product_id: str, draft: ProductDraft, folder_id: str, asset_rows: list[dict]) -> None:
        payload = {
            "product_id": product_id,
            "title": draft.title,
            "description": draft.description,
            "affiliate": {
                "shopee": draft.shopee_url,
                "tiktok_shop": draft.tiktok_url,
                "other": draft.other_links,
            },
            "assets": asset_rows,
            "updated_at": self._now(),
        }
        self.google.upsert_text(
            "AFFILIATE.json", json.dumps(payload, ensure_ascii=False, indent=2), folder_id, "application/json"
        )
        readme = (
            f"Product ID: {product_id}\n"
            f"Title: {draft.title}\n"
            f"Description: {draft.description}\n"
            f"Shopee: {draft.shopee_url or '-'}\n"
            f"TikTok Shop: {draft.tiktok_url or '-'}\n"
            f"Other links: {' | '.join(draft.other_links) or '-'}\n"
            f"Assets: {len(asset_rows)}\n"
            f"Updated: {self._now()}\n"
        )
        self.google.upsert_text("PRODUCT_INFO.txt", readme, folder_id)

    def archive_new_product(self, draft: ProductDraft, files: list[LocalFile]) -> dict:
        product_id, _ = self._ids()
        created = self._now()
        month = datetime.now(self.tz).strftime("%Y-%m")
        month_folder = self.google.find_or_create_folder(month, self.google.root_folder_id)
        product_folder = self.google.create_folder(
            f"{product_id}_{safe_name(draft.title)}", month_folder["id"]
        )
        asset_rows: list[dict] = []
        db_assets: list[tuple] = []
        subfolders: dict[str, str] = {}
        for index, local_file in enumerate(files, start=1):
            key = self._folder_key(local_file.asset_type)
            if key not in subfolders:
                subfolders[key] = self.google.find_or_create_folder(key, product_folder["id"])["id"]
            extension = Path(local_file.original_name).suffix.lower()
            name = f"{index:02d}_{safe_name(Path(local_file.original_name).stem)}{extension}"
            uploaded = self.google.upload_file(Path(local_file.path), subfolders[key], name)
            asset_id = f"AST-{datetime.now(self.tz).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            asset_rows.append({"asset_id": asset_id, "file_name": uploaded.get("name", name), "drive_url": uploaded.get("webViewLink", "")})
            db_assets.append((asset_id, product_id, local_file.original_name, uploaded["id"], uploaded.get("webViewLink", ""), local_file.asset_type, created, "ACTIVE"))

        self._write_metadata(product_id, draft, product_folder["id"], asset_rows)
        self.google.append_product(self._product_values(product_id, draft, product_folder.get("webViewLink", ""), len(files), created, "READY"))
        for asset_row, db_row in zip(asset_rows, db_assets):
            self.google.append_asset([
                db_row[0], product_id, db_row[2], db_row[4], db_row[5], created, "ACTIVE"
            ])
            self.db.insert_asset(db_row)
        self.db.insert_product((
            product_id, draft.title, draft.description, draft.shopee_url, draft.tiktok_url,
            " | ".join(draft.other_links), product_folder["id"], product_folder.get("webViewLink", ""),
            "READY", created, created,
        ))
        self.google.append_log("CREATE_PRODUCT", product_id, f"Uploaded {len(files)} asset(s)")
        return {"product_id": product_id, "folder_url": product_folder.get("webViewLink", ""), "asset_count": len(files)}

    def add_files(self, product_id: str, files: list[LocalFile]) -> dict:
        product = self.db.get_product(product_id)
        if product is None:
            raise ValueError(f"Produk tidak ditemukan: {product_id}")
        existing = len(self.db.list_assets(product_id))
        created = self._now()
        asset_rows: list[dict] = []
        for index, local_file in enumerate(files, start=existing + 1):
            key = self._folder_key(local_file.asset_type)
            folder = self.google.find_or_create_folder(key, product["drive_folder_id"])
            extension = Path(local_file.original_name).suffix.lower()
            name = f"{index:02d}_{safe_name(Path(local_file.original_name).stem)}{extension}"
            uploaded = self.google.upload_file(local_file.path, folder["id"], name)
            asset_id = f"AST-{datetime.now(self.tz).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            self.google.append_asset([asset_id, product_id, local_file.original_name, uploaded.get("webViewLink", ""), local_file.asset_type, created, "ACTIVE"])
            self.db.insert_asset((asset_id, product_id, local_file.original_name, uploaded["id"], uploaded.get("webViewLink", ""), local_file.asset_type, created, "ACTIVE"))
            asset_rows.append({"asset_id": asset_id, "file_name": uploaded.get("name", name), "drive_url": uploaded.get("webViewLink", "")})
        self.google.append_log("ADD_ASSETS", product_id, f"Added {len(files)} asset(s)")
        return {"product_id": product_id, "folder_url": product["drive_folder_url"], "asset_count": existing + len(files), "assets": asset_rows}

    def update_product(self, product_id: str, draft: ProductDraft) -> dict:
        product = self.db.get_product(product_id)
        if product is None:
            raise ValueError(f"Produk tidak ditemukan: {product_id}")
        updated = self._now()
        assets = self.db.list_assets(product_id)
        self.db.update_product(product_id, draft.title, draft.description, draft.shopee_url, draft.tiktok_url, " | ".join(draft.other_links), updated)
        self.google.update_product(product_id, self._product_values(product_id, draft, product["drive_folder_url"], len(assets), product["created_at"], product["status"]))
        self._write_metadata(product_id, draft, product["drive_folder_id"], [{"asset_id": a["asset_id"], "file_name": a["original_name"], "drive_url": a["drive_file_url"]} for a in assets])
        self.google.append_log("UPDATE_PRODUCT", product_id, "Metadata updated")
        return {"product_id": product_id, "folder_url": product["drive_folder_url"], "asset_count": len(assets)}

    def trash_asset(self, asset_id: str) -> dict:
        asset = self.db.get_asset(asset_id)
        if asset is None:
            raise ValueError(f"Aset tidak ditemukan: {asset_id}")
        self.google.trash_file(asset["drive_file_id"])
        self.google.update_asset_status(asset_id, "TRASHED")
        self.db.mark_asset_deleted(asset_id)
        self.google.append_log("TRASH_ASSET", asset["product_id"], asset_id)
        return {"asset_id": asset_id, "product_id": asset["product_id"]}

    def cleanup(self, paths: list[Path]) -> None:
        for path in paths:
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                elif path.exists():
                    path.unlink()
            except OSError:
                pass

    def temp_dir(self) -> Path:
        return Path(tempfile.mkdtemp(prefix="abangjal_archive_"))
