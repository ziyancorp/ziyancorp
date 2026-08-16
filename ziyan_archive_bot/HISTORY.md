# ZIYAN ARSIP BOT — Dokumentasi Pencapaian

**Tanggal:** 16 Agustus 2026
**Status:** ✅ PRODUCTION-READY (terverifikasi end-to-end)
**Owner:** Bos (arija) | **Maintainer:** Hermes (Orkestrator)

---

## 1. TUJUAN SISTEM

Bot Telegram `@Zynarsipbot` (username: `Zynarsipbot`, bot_id: `8684088993`) berfungsi sebagai **intake arsip produk affiliate**:
- Bos kirim file (foto/video) via Telegram → bot arsip ke **Google Drive** + **Google Sheets**
- Link affiliate dicatat kalau ada di caption
- Folder khusus: **"Celine Arsip"** (di Drive root bot)

Tujuannya: punya **gudang aset terstruktur** yang bisa dibaca agent lain (distribusi ke FB/IG/YT/Threads/Shopee/TikTok).

---

## 2. ARSITEKTUR SISTEM

```
Telegram (@Zynarsipbot)
    ↓ webhook/polling (python-telegram-bot 22.5)
ziyan_bot/bot.py  (ArchiveBot)
    ├── on_media()       → terima file, download, kumpul di session
    ├── finalize_batch() → timer 60dtk, panggil archive
    └── save_pending()   → info (auto-finalize, gak perlu tombol)
ziyan_bot/archive.py (ArchiveService)
    ├── archive_new_product() → buat folder Drive + upload + tulis Sheet
    └── add_files()           → tambah aset ke produk existing
ziyan_bot/parser.py (parse_caption)
    └── extract link Shopee/TikTok/Other dari caption
distributor.py (Settings, GoogleWorkspace, Database)
    └── Google API wrapper (Drive v3 + Sheets v4)
```

**Lokasi:**
- Repo: `C:\Users\arija\ziyancorp\ziyan_archive_bot\`
- Venv: `venv/Scripts/python.exe`
- Env: `.env` (TELEGRAM_BOT_TOKEN, GOOGLE_*, FB_PAGE_TOKEN via vault)
- DB lokal: `archive.db` (SQLite, cache)

---

## 3. STRUKTUR DRIVE & SHEET

### Drive
```
Celine Arsip/                    ← ROOT_FOLDER_ID (11m4fW0ChraDoDiESjI6WORbO5u5Q8pf5)
├── ARSIP_MASTER (Google Sheet)
└── 2026-08/
    ├── PROD-YYYYMMDD-XXX_Nama-Produk/
    │   ├── 01_VIDEO/  (video/*.mp4)
    │   ├── 02_FOTO/   (image/*.jpeg)
    │   ├── 03_OTHER/  (lainnya)
    │   ├── PRODUCT_INFO.txt
    │   └── AFFILIATE.json
    └── ...
```

### Sheet `ARSIP_MASTER`
- **PRODUCT_MASTER**: 1 baris per produk
  - `Product ID | Title | Description | Shopee | TikTok | Other Links | Folder URL | Jumlah Aset | Created | Updated | Status`
- **CONTENT_ASSETS**: 1 baris per file
  - `Asset ID | Product ID | Original Name | Drive URL | Tipe | Created | Status`

---

## 4. LOGIKA KERJA BOT

### Flow
1. **Bos kirim file** (foto/video/document) ke @Zynarsipbot
2. `on_media()` terima → download ke temp lokal → simpan ke `session.files`
3. Kalau ada **caption berisi link** → parse → simpan sebagai `draft`
4. **Reset timer 60 dtk** (`finalize-<chat_id>` job) setiap file masuk
5. Bos berhenti kirim → **60 dtk kemudian** → `finalize_batch()` jalan:
   - Ambil semua file di session
   - Buat 1 folder `PROD-YYYYMMDD-XXX`
   - Upload ke subfolder `01_VIDEO`/`02_FOTO`/`03_OTHER`
   - Tulis PRODUCT_MASTER + CONTENT_ASSETS
   - Balas ke Bos: "Produk berhasil diarsipkan, Product ID: ..."
6. Cleanup temp

### Aturan Khusus (request Bos 16 Aug)
- ✅ **Simpan file SELALU** — gak ada link pun tetap diarsip
- ✅ **Link ditulis HANYA kalau ada** di caption
- ✅ **4 file + 1 link** → ke-4 file dicatat berdasarkan 1 link itu (1 produk)
- ✅ **Window 1 menit** (BATCH_WINDOW_SECONDS=60)
- ✅ File dikirim pakai opsi **"Berkas"** (document) → gak terkompresi

### Format File
- `ON_MEDIA` handler: `filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.CAPTION`
- Document (Berkas) masuk sebagai `message.document` → asset_type `video`/`photo`/`other` by mime

---

## 5. BUG YANG DITEMUKAN & DIPERBAIKI (16 Aug)

| # | Bug | Lokasi | Dampak | Fix |
|---|-----|--------|--------|-----|
| 1 | `upload_file()` dikasih `str`, butuh `Path` | `archive.py:93` | Crash saat upload → produk gak kesimpan | Wrap `Path(local_file.path)` |
| 2 | `filters.Caption` (class) vs `filters.CAPTION` (const) | `bot.py` handler | Dispatcher crash → bot gak process update sama sekali | Ganti ke `filters.CAPTION` |
| 3 | `timeout=300` kwarg gak didukung `googleapiclient` | `google_workspace.py` | TypeError saat upload | Hapus kwarg, pakai non-resumable |
| 4 | `send_chat_action(UPLOAD_DOCUMENT)` di awal finalize | `bot.py:211` | `httpx.ReadError` (Telegram putus) → finalize gagal total | Hapus, balas user dijadikan best-effort |
| 5 | Orphan instance bot (8-10 process) | Runtime | `getUpdates` conflict 409 → bot "offline" | Kill all, launch 1 bersih |
| 6 | Folder "Celine Arsip" belum ada | Setup | Arsip masuk ke root, bukan folder khusus | Buat + pindahkan 2026-08 + Sheet ke dalamnya |

### PTB Version
- `requirements.txt` minta **22.5**, env terinstall 22.6 → downgrade ke **22.5** (yang jalan 15 Aug)

---

## 6. HASIL AKHIR (TERVERIFIKASI)

### Test End-to-End (16 Aug, live)
**Input:** Bos kirim 8 file (5 foto + 3 video) via "Berkas" + caption link `s.shopee.co.id/3LQ52qYeIq`

**Output:**
```
Celine Arsip/2026-08/PROD-20260816-260F26_Cek-KAOS-ATASAN-OBLONG-COWOK-.../
├── PRODUCT_INFO.txt
├── AFFILIATE.json
├── 01_VIDEO/  (3 file: Person_speaking_*.mp4)
└── 02_FOTO/   (5 file: *.jpeg)
```

**Sheet:**
| Product ID | Title | Aset | Link |
|---|---|---|---|
| `PROD-20260816-260F26` | Cek KAOS ATASAN OBLONG COWOK DEWASA... | 8 | https://s.shopee.co.id/3LQ52qYeIq |

✅ 8 file masuk utuh (gak terkompresi)
✅ Link tercatat di Sheet
✅ `finalize_batch` executed successfully (gak error)
✅ Agent lain bisa baca via `AFFILIATE.json` atau Sheet

---

## 7. CARA JALANKAN (OPERASIONAL)

### Start Bot (1 instance)
```bash
cd C:\Users\arija\ziyancorp\ziyan_archive_bot
FB_PAGE_TOKEN=$(bash /c/Users/arija/bin/token_vault.sh get fb_page_token 2>/dev/null | tr -d '\n') \
CHANNEL_CELINE="-1004373452633" \
GOOGLE_CREDENTIALS_FILE=client_secret.json \
HERMES_CUSTOM_9ROUTER_API_KEY="$HERMES_CUSTOM_9ROUTER_API_KEY" \
env -u PYTHONPATH ./venv/Scripts/python.exe -m ziyan_bot.bot
```

### Cek Instance (hindari orphan)
```powershell
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*ziyan_bot.bot*' }
```
**HARUS CUMA 1.** Kalau >1 → kill semua, launch 1.

### Monitor Log
```bash
tail -f bot_debug.log
# atau grep
grep -E "ON_MEDIA|finalize|DISPATCH ERROR|Produk berhasil" bot_debug.log
```

---

## 8. AKSES UNTUK AGENT LAIN

Agent distribusi (FB/IG/YT/Threads) bisa baca arsip via:

**A. Sheet `ARSIP_MASTER`** (PRODUCT_MASTER + CONTENT_ASSETS)
```python
from distributor import Settings, GoogleWorkspace
s = Settings.from_env()
gw = GoogleWorkspace(...)
rows = gw.sheets.spreadsheets().values().get(
    spreadsheetId=s.google_spreadsheet_id, range='PRODUCT_MASTER!A:K').execute()
```

**B. `AFFILIATE.json`** (di dalam folder produk Drive)
```json
{
  "product_id": "PROD-20260816-260F26",
  "title": "...",
  "affiliate": {"shopee": "...", "tiktok_shop": null, "other": []},
  "assets": [{"asset_id": "...", "file_name": "...", "drive_url": "..."}]
}
```

**Syarat:** Agent butuh `token.json` (OAuth Google) yang sama → dishare via vault terenkripsi.

---

## 9. PENCAPAIAN HARI INI

- ✅ Bot diperbaiki dari kondisi rusak (gak bisa arsip) → production-ready
- ✅ 6 folder hantu test dibersihkan, 3 produk asli (15 Aug) dipertahankan
- ✅ Folder "Celine Arsip" dibuat + struktur rapi
- ✅ Verifikasi end-to-end: 8 file → 1 produk utuh di Drive + Sheet
- ✅ Agent-ready (AFFILIATE.json + Sheet bisa dibaca agent lain)

---

## 10. CATATAN UNTUK HERMES (LESSONS LEARNED)

1. **Jangan muter tanpa verifikasi** — tiap claim "bot jalan" harus dibuktikan dengan test `process_update` / cek Sheet
2. **Orphan process** sering muncul tiap restart → selalu kill all sebelum launch
3. **`filters.Caption` vs `filters.CAPTION`** — PTB punya class & const, beda hasil
4. **`send_chat_action` di awal finalize** = risk tinggi kalau network flaky → best-effort saja
5. **File via "Berkas"** = document, gak dikompresi → prefer untuk aset original
6. **Test simulasi salah arah** (`sendPhoto` = bot→user, bukan user→bot) → pakai `process_update` untuk verifikasi handler

---

*Dokumentasi dibuat oleh Hermes — 16 Agustus 2026, 16:00 WIB*
