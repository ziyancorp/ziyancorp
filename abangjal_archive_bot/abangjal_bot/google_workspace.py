from __future__ import annotations

import json
import mimetypes
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2 import credentials as user_credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload


SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]

PRODUCT_HEADERS = [
    "product_id", "title", "description", "shopee_url", "tiktok_url", "other_links",
    "drive_folder_url", "asset_count", "created_at", "updated_at", "status",
]
ASSET_HEADERS = [
    "asset_id", "product_id", "file_name", "drive_file_url", "asset_type", "created_at", "status",
]
LOG_HEADERS = ["timestamp", "event", "product_id", "details"]


class GoogleWorkspace:
    def __init__(self, credentials_file: Path, token_file: Path, root_folder_id: str, spreadsheet_id: str):
        self.root_folder_id = root_folder_id
        self.spreadsheet_id = spreadsheet_id
        self.credentials_file = credentials_file
        self.token_file = token_file
        creds = self._load_credentials()
        self.drive = build("drive", "v3", credentials=creds, cache_discovery=False)
        self.sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)
        self.ensure_headers()

    def _load_credentials(self):
        creds = None
        if self.token_file.exists():
            creds = user_credentials.Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            self.token_file.write_text(creds.to_json(), encoding="utf-8")
        if creds and creds.valid:
            return creds
        if not self.credentials_file.exists():
            raise RuntimeError(
                f"Kredensial Google belum ditemukan: {self.credentials_file}. "
                "Tempatkan OAuth client secret di file tersebut lalu jalankan scripts/google_auth.py."
            )
        raw = json.loads(self.credentials_file.read_text(encoding="utf-8"))
        if "type" in raw and raw["type"] == "service_account":
            return service_account.Credentials.from_service_account_file(str(self.credentials_file), scopes=SCOPES)
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_file), SCOPES)
        creds = flow.run_local_server(port=0)
        self.token_file.write_text(creds.to_json(), encoding="utf-8")
        return creds

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def ensure_headers(self) -> None:
        for sheet_name, headers in (
            ("PRODUCT_MASTER", PRODUCT_HEADERS),
            ("CONTENT_ASSETS", ASSET_HEADERS),
            ("PROCESS_LOG", LOG_HEADERS),
        ):
            result = self.sheets.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range=f"{sheet_name}!1:1"
            ).execute()
            values = result.get("values", [])
            if not values or values[0] != headers:
                self.sheets.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{sheet_name}!A1",
                    valueInputOption="RAW",
                    body={"values": [headers]},
                ).execute()

    def create_folder(self, name: str, parent_id: str) -> dict[str, Any]:
        return self.drive.files().create(
            body={"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]},
            fields="id,name,webViewLink,parents",
        ).execute()

    def find_or_create_folder(self, name: str, parent_id: str) -> dict[str, Any]:
        escaped = name.replace("'", "\\'")
        result = self.drive.files().list(
            q=f"name = '{escaped}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
            spaces="drive", fields="files(id,name,webViewLink,parents)", pageSize=10,
        ).execute()
        files = result.get("files", [])
        return files[0] if files else self.create_folder(name, parent_id)

    def upload_file(self, path: Path, parent_id: str, name: str | None = None) -> dict[str, Any]:
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        metadata = {"name": name or path.name, "parents": [parent_id]}
        media = MediaFileUpload(str(path), mimetype=mime_type, resumable=False)
        return self.drive.files().create(
            body=metadata, media_body=media, fields="id,name,mimeType,size,webViewLink,parents"
        ).execute()

    def upload_text(self, name: str, text: str, parent_id: str, mime_type: str = "text/plain") -> dict[str, Any]:
        import io
        media = MediaIoBaseUpload(io.BytesIO(text.encode("utf-8")), mimetype=mime_type, resumable=False)
        return self.drive.files().create(
            body={"name": name, "parents": [parent_id]}, media_body=media,
            fields="id,name,mimeType,size,webViewLink,parents",
        ).execute()

    def upsert_text(self, name: str, text: str, parent_id: str, mime_type: str = "text/plain") -> dict[str, Any]:
        import io
        escaped = name.replace("'", "\\'")
        result = self.drive.files().list(
            q=f"name = '{escaped}' and '{parent_id}' in parents and trashed = false",
            spaces="drive", fields="files(id,name,mimeType,size,webViewLink,parents)", pageSize=10,
        ).execute()
        media = MediaIoBaseUpload(io.BytesIO(text.encode("utf-8")), mimetype=mime_type, resumable=False)
        existing = result.get("files", [])
        if existing:
            return self.drive.files().update(
                fileId=existing[0]["id"], media_body=media,
                body={"name": name}, fields="id,name,mimeType,size,webViewLink,parents",
            ).execute()
        return self.drive.files().create(
            body={"name": name, "parents": [parent_id]}, media_body=media,
            fields="id,name,mimeType,size,webViewLink,parents",
        ).execute()

    def trash_file(self, file_id: str) -> None:
        self.drive.files().update(fileId=file_id, body={"trashed": True}).execute()

    def append_product(self, values: list[Any]) -> None:
        self.sheets.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id, range="PRODUCT_MASTER!A:K",
            valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS", body={"values": [values]},
        ).execute()

    def append_asset(self, values: list[Any]) -> None:
        self.sheets.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id, range="CONTENT_ASSETS!A:G",
            valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS", body={"values": [values]},
        ).execute()

    def append_log(self, event: str, product_id: str, details: str) -> None:
        self.sheets.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id, range="PROCESS_LOG!A:D",
            valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS",
            body={"values": [[self._now(), event, product_id, details]]},
        ).execute()

    def _find_row(self, sheet_name: str, key: str) -> int | None:
        result = self.sheets.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=f"{sheet_name}!A:A"
        ).execute()
        for row_number, row in enumerate(result.get("values", []), start=1):
            if row and row[0] == key:
                return row_number
        return None

    def update_product(self, product_id: str, values: list[Any]) -> None:
        row = self._find_row("PRODUCT_MASTER", product_id)
        if row is None:
            self.append_product(values)
            return
        self.sheets.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id, range=f"PRODUCT_MASTER!A{row}:K{row}",
            valueInputOption="USER_ENTERED", body={"values": [values]},
        ).execute()

    def update_asset_status(self, asset_id: str, status: str) -> None:
        row = self._find_row("CONTENT_ASSETS", asset_id)
        if row is None:
            return
        self.sheets.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id, range=f"CONTENT_ASSETS!G{row}",
            valueInputOption="USER_ENTERED", body={"values": [[status]]},
        ).execute()
