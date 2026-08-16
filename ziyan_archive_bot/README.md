# ZIYAN Distribution Agent

Agent distribusi otomatis: 1 produk dari arsip → post ke **Facebook, Instagram, Threads, YouTube** (PUBLIK) sekaligus.

## Alur Kerja

```
Bos kirim Berkas + Link ke @Zynarsipbot (Telegram)
        ↓
Bot arsip simpan ke Google Drive (folder PROD-YYYYMMDD-XXXXXX) + Sheet PRODUCT_MASTER
        ↓
Cron ziyan-distribute-4x (08:57 / 12:34 / 16:08 / 20:13 WIB)
        ↓
distribute_agent.py:
  1. get_pending_product() → ambil 1 produk status != PUBLISHED
  2. Baca AFFILIATE.json dari Drive → dapat aset asli (foto/video)
  3. Generate caption: Link Shopee + deskripsi natural (TANPA HARGA) + 4 hashtag
  4. Post ke 4 platform PUBLIK
  5. mark_published() → kolom I:J = timestamp + "PUBLISHED"
```

## Platform & Endpoint (TERVERIFIKASI 16/8)

| Platform | Endpoint | Token (vault) | Catatan |
|---|---|---|---|
| Facebook | graph.facebook.com | `fb_page_token` | Post ke Page 975723622288353 |
| Instagram | **graph.instagram.com** | `instagram_user_token` | IG_BIZ_ID 17841444876830769. Image: upload foto ke FB Page dulu → CDN URL (Drive URL gak di-fetch IG) |
| Threads | graph.threads.net | `threads_user_token` | Text-only (image Drive gak di-fetch). Threads App ID 1346767533487099 |
| YouTube | youtube.googleapis.com | `token_celine.json` | Channel UC0h3xyafx6P6J_CjpzhpSeg. Title max 95 char |

## File

- `distribute_agent.py` — orchestrator utama
- `distributor.py` — engine post per-platform (`post_facebook`, `post_instagram`, `post_threads`, `post_youtube`)
- `youtube_upload_celine.py` — upload YT (scope youtube.upload)
- `run_distribute.sh` — wrapper cron (set env dari vault)
- `threads_reauth.py` — re-auth Threads (terpisah dari fb_reauth.py)

## Cara Re-Auth (kalau token expired)

- **Facebook**: `bash bin/token_vault.sh get fb_page_token` (valid lama, jarang expired)
- **Threads**: `python threads_reauth.py` → buka URL → paste redirect → tukar ke long-lived
- **Instagram**: Meta Console → App n8n → Use cases → Instagram → User Token Generator → @celineaurel99 → simpan ke vault `instagram_user_token`
- **YouTube**: `python oauth_channel_check.py --expected-channel UC0h3xyafx6P6J_CjpzhpSeg` → buka browser → authorize (scope youtube.upload)

## Pitfalls (jangan diulang)

1. IG token tes di `graph.facebook.com` → "Cannot parse". Pakai `graph.instagram.com`.
2. IG `image_url` harus hosting publik (FB CDN). Drive URL (`uc?export=view`) = HTML page, IG tolak.
3. YT title >100 char → reject. Agent potong 95 char.
4. YT description jangan pakai caption IG/Threads (bisa reject). Pakai description simpel.
5. Threads text-only. Image URL Drive gak di-fetch Meta.
6. JANGAN `fb_reauth.py` buat Threads — pakai `threads_reauth.py`.
7. FB App ID bener = `1994676317894733` (bukan `199467631784713`).

## Cron

```
Job: ziyan-distribute-4x (d9ee27fe41c3)
Schedule: 57 8,12,16,20 * * *  (08:57, 12:34, 16:08, 20:13 WIB)
Next run: 2026-08-17 08:57
```

## Test Manual

```bash
cd C:/Users/arija/ziyancorp/ziyan_archive_bot
bash run_distribute.sh
```
