# ZIYAN TEMPLATES - PAKET SIAP PAKAI
Semua file di sini SIAP DIPAKAI. Tinggal isi token/key, langsung jalan.

## PAKET 1: AUTO-AFFILIATE KIT
Fungsi: Bos kirim video/foto + link Shopee ke Telegram -> otomatis post FB+YT+X tiap 67 mnt, sinkron dari Google Sheet tiap 53 mnt.
File:
- ziyan_intake/scheduler.py  (engine utama, jalan: python scheduler.py loop)
- ziyan_intake/enqueue_*.py   (contoh masukin bahan ke Sheet)
Yang harus Bos punya:
- Token FB Page (60 hari) -> OneDrive/ziyan_pending/fb_page_token.txt
- Google token (Sheets+YT) -> AppData/Local/hermes/
- 9router jalan (untuk caption AI, optional)
Cara jalan: python ziyan_intake/scheduler.py loop

## PAKET 2: AI CS BOT KIT
Fungsi: Bot Telegram jawab otomatis (sales/closing), log keluhan ke CSV.
File:
- ziyan_corp_cs_bot.py
- ziyan_cs_bot.env (isi token @Employeezynbot)
Cara jalan: python ziyan_corp_cs_bot.py
Butuh: 9router hidup (kr/auto), token bot di env

## PAKET 3: JOB HUNTER KIT
Fungsi: Cari lowongan via JSearch, filter score, kirim ke Telegram.
File:
- ziyan_n8n_templates/ziyan_job_hunter.json (import ke n8n)
- ziyancorp.github.io (landing page, sudah live)
Butuh: RAPIDAPI_KEY (JSearch), TELEGRAM_CHAT_ID di env n8n
Cara: import JSON ke n8n, isi credential, activate

## STATUS MONETISASI
- Semua template GRATIS dibuat, siap dijual sebagai:
  - Setup service (3-15jt tergantung paket)
  - Subscription (300rb-1jt/bln maintenance)
- Platform: Gumroad / Fiverr / Upwork (gratis listing)
- Belum upload (menunggu Bos approve)

## ETICA
- Jangan jual yg bikin klien rugi
- Bukti dulu sebelum janji UMKM
