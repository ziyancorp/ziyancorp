from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    allowed_user_ids: frozenset[int]
    google_credentials_file: Path
    google_token_file: Path
    google_root_folder_id: str
    google_spreadsheet_id: str
    batch_window_seconds: int
    database_file: Path
    max_download_mb: int

    @classmethod
    def from_env(cls) -> "Settings":
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN belum diisi di file .env")

        raw_ids = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").strip()
        if not raw_ids:
            raise RuntimeError("TELEGRAM_ALLOWED_USER_IDS wajib diisi untuk keamanan")
        try:
            allowed_ids = frozenset(int(value.strip()) for value in raw_ids.split(",") if value.strip())
        except ValueError as exc:
            raise RuntimeError("TELEGRAM_ALLOWED_USER_IDS harus berupa angka dipisahkan koma") from exc

        def project_path(name: str, default: str) -> Path:
            value = os.getenv(name, default).strip()
            path = Path(value)
            return path if path.is_absolute() else PROJECT_DIR / path

        root_folder_id = os.getenv("GOOGLE_ROOT_FOLDER_ID", "").strip()
        spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID", "").strip()
        if not root_folder_id or not spreadsheet_id:
            raise RuntimeError("GOOGLE_ROOT_FOLDER_ID dan GOOGLE_SPREADSHEET_ID wajib diisi")

        return cls(
            telegram_bot_token=token,
            allowed_user_ids=allowed_ids,
            google_credentials_file=project_path("GOOGLE_CREDENTIALS_FILE", "credentials.json"),
            google_token_file=project_path("GOOGLE_TOKEN_FILE", "token.json"),
            google_root_folder_id=root_folder_id,
            google_spreadsheet_id=spreadsheet_id,
            batch_window_seconds=int(os.getenv("BATCH_WINDOW_SECONDS", "15")),
            database_file=project_path("DATABASE_FILE", "archive.db"),
            max_download_mb=int(os.getenv("MAX_DOWNLOAD_MB", "200")),
        )
