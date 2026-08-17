from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application, ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes,
    MessageHandler, filters,
)

from .archive import ArchiveService, LocalFile
from .config import Settings
from .db import Database
from .parser import ProductDraft, parse_caption

logger = logging.getLogger(__name__)


@dataclass
class UploadSession:
    mode: str = "new"
    product_id: str | None = None
    draft: ProductDraft | None = None
    files: list[LocalFile] = field(default_factory=list)
    temp_dir: Path | None = None
    close_job: Any = None


class ArchiveBot:
    def __init__(self, settings: Settings, archive: ArchiveService, db: Database):
        self.settings = settings
        self.archive = archive
        self.db = db
        self.sessions: dict[int, UploadSession] = {}
        self.pending_delete: dict[int, str] = {}

    def allowed(self, update: Update) -> bool:
        user = update.effective_user
        return bool(user and user.id in self.settings.allowed_user_ids)

    async def reject_if_unauthorized(self, update: Update) -> bool:
        logger.warning("REJECT_CHECK update_type=%s has_message=%s", type(update.callback_query).__name__ if update.callback_query else (update.message or update.channel_post or update.edited_message), bool(update.effective_message))
        user = update.effective_user
        uid = user.id if user else None
        chat = update.effective_chat
        # Log chat info untuk debug channel
        if chat:
            logger.warning("CHAT_DEBUG type=%s id=%s title=%s", chat.type, chat.id, getattr(chat, "title", ""))
        # Izinkan pesan dari channel (bot sebagai admin channel, bukan user)
        if chat and chat.type == "channel":
            return False
        # Log forward info untuk debug channel
        msg = update.effective_message
        if msg and getattr(msg, "forward_origin", None):
            fo = msg.forward_origin
            fc = getattr(fo, "chat", None)
            fc_id = fc.id if fc else None
            logger.warning("FORWARD_ORIGIN chat_id=%s type=%s", fc_id, type(fo).__name__)
        if uid in self.settings.allowed_user_ids:
            return False
        logger.warning("REJECTED user_id=%s (allowed=%s)", uid, sorted(self.settings.allowed_user_ids))
        if update.effective_message:
            await update.effective_message.reply_text("Akses ditolak.")
        return True

    def session(self, chat_id: int) -> UploadSession:
        if chat_id not in self.sessions:
            self.sessions[chat_id] = UploadSession(temp_dir=self.archive.temp_dir())
        return self.sessions[chat_id]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if await self.reject_if_unauthorized(update):
            return
        await update.effective_message.reply_text(
            "Bot arsip Ziyan siap. Kirim deskripsi produk + link affiliate, lalu kirim semua foto/video. "
            f"Batch otomatis diproses {self.settings.batch_window_seconds} detik setelah file terakhir.\n\n"
            "/new — mulai produk baru\n"
            "/cari kata kunci — cari produk\n"
            "/lihat PROD-ID — lihat aset\n"
            "/edit PROD-ID — ubah deskripsi/link\n"
            "/tambah PROD-ID — tambah file\n"
            "/hapus_asset AST-ID — pindahkan file ke Trash\n"
            "/batal — batalkan batch aktif"
        )

    async def new_product(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if await self.reject_if_unauthorized(update):
            return
        chat_id = update.effective_chat.id
        old = self.sessions.pop(chat_id, None)
        if old:
            self.archive.cleanup([old.temp_dir] if old.temp_dir else [])
        self.sessions[chat_id] = UploadSession(temp_dir=self.archive.temp_dir())
        await update.effective_message.reply_text("Batch produk baru dimulai. Kirim deskripsi/link, lalu file-file konten.")

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if await self.reject_if_unauthorized(update):
            return
        session = self.sessions.pop(update.effective_chat.id, None)
        if session:
            if session.close_job:
                session.close_job.schedule_removal()
            self.archive.cleanup([session.temp_dir] if session.temp_dir else [])
            await update.effective_message.reply_text("Batch dibatalkan. File belum diarsipkan.")
        else:
            await update.effective_message.reply_text("Tidak ada batch aktif.")

    async def on_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if await self.reject_if_unauthorized(update):
            return
        text = (update.effective_message.text or "").strip()
        chat_id = update.effective_chat.id
        session = self.session(chat_id)
        if session.mode == "edit" and session.product_id:
            try:
                draft = parse_caption(text)
                result = await asyncio.to_thread(self.archive.update_product, session.product_id, draft)
                self.sessions.pop(chat_id, None)
                await update.effective_message.reply_text(
                    f"Metadata diperbarui.\nProduct ID: {result['product_id']}\nFolder: {result['folder_url']}"
                )
            except Exception as exc:
                logger.exception("update product failed")
                await update.effective_message.reply_text(f"Gagal mengubah metadata: {exc}")
            return
        if session.mode == "add":
            await update.effective_message.reply_text("Mode tambah aset aktif. Kirim file; teks ini diabaikan. Gunakan /batal untuk keluar.")
            return
        session.draft = parse_caption(text)
        await update.effective_message.reply_text(
            f"Metadata diterima untuk: {session.draft.title}\nSekarang kirim semua foto/video."
        )

    async def on_media(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.warning("ON_MEDIA called chat=%s type=%s", update.effective_chat.id if update.effective_chat else None, update.effective_message.chat.type if update.effective_message else None)
        if await self.reject_if_unauthorized(update):
            return
        message = update.effective_message
        chat_id = update.effective_chat.id
        session = self.session(chat_id)
        if session.temp_dir is None:
            session.temp_dir = self.archive.temp_dir()
        if message.caption and session.mode == "new":
            session.draft = parse_caption(message.caption)
        if session.mode not in {"new", "add"}:
            await message.reply_text("Selesaikan edit metadata terlebih dahulu dengan mengirim teks.")
            return

        telegram_file = None
        original_name = None
        asset_type = "other"
        if message.photo:
            telegram_file = await context.bot.get_file(message.photo[-1].file_id)
            original_name = f"telegram_{message.message_id}.jpg"
            asset_type = "photo"
        elif message.video:
            telegram_file = await context.bot.get_file(message.video.file_id)
            original_name = message.video.file_name or f"telegram_{message.message_id}.mp4"
            asset_type = "video"
        elif message.document:
            telegram_file = await context.bot.get_file(message.document.file_id)
            original_name = message.document.file_name or f"telegram_{message.message_id}"
            mime = message.document.mime_type or ""
            asset_type = "video" if mime.startswith("video/") else "photo" if mime.startswith("image/") else "other"
        if telegram_file is None or original_name is None:
            return
        file_size = getattr(message.video or message.document or (message.photo[-1] if message.photo else None), "file_size", None)
        if file_size and file_size > self.settings.max_download_mb * 1024 * 1024:
            await message.reply_text(f"File terlalu besar. Batas saat ini {self.settings.max_download_mb} MB.")
            return
        target = session.temp_dir / f"{message.message_id}_{Path(original_name).name}"
        await telegram_file.download_to_drive(custom_path=target)
        session.files.append(LocalFile(target, original_name, asset_type))
        if session.close_job:
            session.close_job.schedule_removal()
        session.close_job = context.job_queue.run_once(
            self.finalize_batch, when=self.settings.batch_window_seconds,
            data={"chat_id": chat_id}, name=f"finalize-{chat_id}"
        )
        await message.reply_text(f"File diterima: {len(session.files)} file dalam batch. Menunggu file berikutnya {self.settings.batch_window_seconds} detik.")

    async def finalize_batch(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = context.job.data["chat_id"]
        session = self.sessions.get(chat_id)
        if not session or not session.files:
            # Ada draft (link) tapi belum ada file -> tunggu file menyusul, jangan buang.
            if session and session.draft and session.mode == "new":
                context.job_queue.run_once(
                    self.finalize_batch, when=60,
                    data={"chat_id": chat_id}, name=f"finalize-wait-{chat_id}")
                return
            return
        if session.mode == "new" and not session.draft:
            await context.bot.send_message(chat_id, "File sudah diterima, tetapi deskripsi produk/link belum ada. Kirim metadata lalu gunakan /simpan.")
            return
        session = self.sessions.pop(chat_id)
        # Bos rule: simpan file SELALU. Link dicatat HANYA jika ada.
        if session.mode == "new" and not session.draft:
            # Tidak ada caption/link sama sekali -> buat draft default (tanpa link)
            session.draft = ProductDraft(
                title="Tanpa judul", description="", shopee_url=None,
                tiktok_url=None, other_links=[]
            )
        try:
            if session.mode == "add" and session.product_id:
                result = await asyncio.to_thread(self.archive.add_files, session.product_id, session.files)
                message = (
                    f"Aset berhasil ditambahkan.\nProduct ID: {result['product_id']}\n"
                    f"Total aset: {result['asset_count']}\nFolder: {result['folder_url']}"
                )
            else:
                result = await asyncio.to_thread(self.archive.archive_new_product, session.draft, session.files)
                message = (
                    f"Produk berhasil diarsipkan.\nProduct ID: {result['product_id']}\n"
                    f"Jumlah aset: {result['asset_count']}\nFolder: {result['folder_url']}"
                )
            # Balas ke user (best-effort, jangan gagalkan arsip kalau Telegram error)
            try:
                await context.bot.send_message(chat_id, message)
            except Exception:
                logger.warning("gagal balas ke user, tapi arsip sukses")
        except Exception as exc:
            logger.exception("archive failed")
            try:
                await context.bot.send_message(chat_id, f"Pengarsipan gagal dan belum dianggap selesai: {exc}")
            except Exception:
                pass
        finally:
            self.archive.cleanup([session.temp_dir] if session.temp_dir else [])

    async def save_pending(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if await self.reject_if_unauthorized(update):
            return
        await update.effective_message.reply_text(f"Batch akan diproses otomatis {self.settings.batch_window_seconds} detik setelah file terakhir. Tidak perlu menekan tombol simpan.")

    async def search(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if await self.reject_if_unauthorized(update):
            return
        query = " ".join(context.args).strip()
        if not query:
            await update.effective_message.reply_text("Gunakan: /cari nama produk atau Product ID")
            return
        rows = self.db.search_products(query)
        if not rows:
            await update.effective_message.reply_text("Produk tidak ditemukan.")
            return
        lines = [f"{row['product_id']} — {row['title']} ({row['status']})" for row in rows]
        await update.effective_message.reply_text("Hasil pencarian:\n" + "\n".join(lines))

    async def show_product(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if await self.reject_if_unauthorized(update):
            return
        if not context.args:
            await update.effective_message.reply_text("Gunakan: /lihat PROD-ID")
            return
        product_id = context.args[0].upper()
        product = self.db.get_product(product_id)
        if not product:
            await update.effective_message.reply_text("Product ID tidak ditemukan.")
            return
        assets = self.db.list_assets(product_id)
        lines = [f"{a['asset_id']} — {a['original_name']} — {a['drive_file_url']}" for a in assets]
        await update.effective_message.reply_text(
            f"{product['product_id']}\n{product['title']}\n{product['description']}\n"
            f"Shopee: {product['shopee_url'] or '-'}\nTikTok: {product['tiktok_url'] or '-'}\n"
            f"Folder: {product['drive_folder_url']}\n\nAset:\n" + ("\n".join(lines) or "Tidak ada aset aktif.")
        )

    async def edit_product(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if await self.reject_if_unauthorized(update):
            return
        if not context.args:
            await update.effective_message.reply_text("Gunakan: /edit PROD-ID, lalu kirim teks metadata baru.")
            return
        product_id = context.args[0].upper()
        if not self.db.get_product(product_id):
            await update.effective_message.reply_text("Product ID tidak ditemukan.")
            return
        self.sessions[update.effective_chat.id] = UploadSession(mode="edit", product_id=product_id)
        await update.effective_message.reply_text("Kirim metadata baru dengan format Nama produk/Judul, Deskripsi, Shopee, dan TikTok.")

    async def add_assets(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if await self.reject_if_unauthorized(update):
            return
        if not context.args:
            await update.effective_message.reply_text("Gunakan: /tambah PROD-ID, lalu kirim file.")
            return
        product_id = context.args[0].upper()
        if not self.db.get_product(product_id):
            await update.effective_message.reply_text("Product ID tidak ditemukan.")
            return
        old = self.sessions.pop(update.effective_chat.id, None)
        if old:
            self.archive.cleanup([old.temp_dir] if old.temp_dir else [])
        self.sessions[update.effective_chat.id] = UploadSession(mode="add", product_id=product_id, temp_dir=self.archive.temp_dir())
        await update.effective_message.reply_text(f"Mode tambah aset aktif untuk {product_id}. Kirim file-file baru.")

    async def delete_asset(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if await self.reject_if_unauthorized(update):
            return
        if not context.args:
            await update.effective_message.reply_text("Gunakan: /hapus_asset AST-ID")
            return
        asset_id = context.args[0].upper()
        if not self.db.get_asset(asset_id):
            await update.effective_message.reply_text("Asset ID tidak ditemukan.")
            return
        self.pending_delete[update.effective_chat.id] = asset_id
        keyboard = [[InlineKeyboardButton("Pindahkan ke Trash", callback_data="confirm_delete"), InlineKeyboardButton("Batal", callback_data="cancel_delete")]]
        await update.effective_message.reply_text(f"Yakin memindahkan {asset_id} ke Trash Google Drive?", reply_markup=InlineKeyboardMarkup(keyboard))

    async def delete_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        if not self.allowed(update):
            await query.edit_message_text("Akses ditolak.")
            return
        asset_id = self.pending_delete.pop(update.effective_chat.id, None)
        if query.data == "cancel_delete" or not asset_id:
            await query.edit_message_text("Penghapusan dibatalkan.")
            return
        try:
            result = await asyncio.to_thread(self.archive.trash_asset, asset_id)
            await query.edit_message_text(f"Aset {result['asset_id']} dipindahkan ke Trash. Product ID: {result['product_id']}")
        except Exception as exc:
            logger.exception("trash asset failed")
            await query.edit_message_text(f"Gagal memindahkan aset ke Trash: {exc}")


    async def distribute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if await self.reject_if_unauthorized(update):
            return
        if not context.args:
            await update.effective_message.reply_text("Gunakan: /distribusi PROD-ID [channel]\nContoh: /distribusi PROD-20260815-2652CC")
            return
        product_id = context.args[0].upper()
        target = context.args[1] if len(context.args) > 1 else None
        await update.effective_message.reply_text(f"Membuat caption AI untuk {product_id}...")
        try:
            from distributor import get_products, gen_caption, distribute_to_platforms
            import os as _os
            prods = get_products("", limit=50)
            prod = next((p for p in prods if p.get("product_id") == product_id), None)
            if not prod:
                await update.effective_message.reply_text(f"Produk {product_id} tidak ditemukan di Sheet.")
                return
            caption = await asyncio.to_thread(gen_caption, prod)
            await update.effective_message.reply_text(f"--- PREVIEW CAPTION ---\n\n{caption}")
            if target and target.lower() in ("all", "celine"):
                ch = _os.environ.get("CHANNEL_CELINE", "")
                if ch.startswith("@") or ch.startswith("-100"):
                    try:
                        await context.bot.send_message(chat_id=ch, text=caption, disable_web_page_preview=False)
                        await update.effective_message.reply_text(f"Terkirim ke channel {ch}.")
                    except Exception as e:
                        await update.effective_message.reply_text(f"Gagal post ke channel: {e}")
            else:
                await update.effective_message.reply_text("(Kirim /distribusi PROD-ID all untuk post ke channel Celine Aurel)")
        except Exception as exc:
            logger.exception("distribute failed")
            await update.effective_message.reply_text(f"Gagal generate caption: {exc}")


def build_application(settings: Settings, archive: ArchiveService, db: Database) -> Application:
    bot = ArchiveBot(settings, archive, db)
    application = ApplicationBuilder().token(settings.telegram_bot_token).build()
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.start))
    application.add_handler(CommandHandler("new", bot.new_product))
    application.add_handler(CommandHandler("simpan", bot.save_pending))
    application.add_handler(CommandHandler("batal", bot.cancel))
    application.add_handler(CommandHandler("cari", bot.search))
    application.add_handler(CommandHandler("lihat", bot.show_product))
    application.add_handler(CommandHandler("edit", bot.edit_product))
    application.add_handler(CommandHandler("tambah", bot.add_assets))
    application.add_handler(CommandHandler("hapus_asset", bot.delete_asset))
    application.add_handler(CommandHandler("distribusi", bot.distribute))
    application.add_handler(CallbackQueryHandler(bot.delete_callback, pattern=r"^(confirm_delete|cancel_delete)$"))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.CAPTION, bot.on_media))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.on_text))

    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.error("DISPATCH ERROR: %s", context.error, exc_info=context.error)
    application.add_error_handler(error_handler)
    return application


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s %(message)s")
    settings = Settings.from_env()
    db = Database(settings.database_file)
    from .google_workspace import GoogleWorkspace
    google = GoogleWorkspace(settings.google_credentials_file, settings.google_token_file, settings.google_root_folder_id, settings.google_spreadsheet_id)
    archive = ArchiveService(db, google, os.getenv("TIMEZONE", "Asia/Jakarta"))
    application = build_application(settings, archive, db)
    logger.warning("HANDLERS REGISTERED: %d", len(application.handlers))
    application.run_polling()


if __name__ == "__main__":
    main()
