# ZIYAN TEMPLATES - PAKET SIAP PAKAI
Semua file SIAP DIPAKAI. Credential dari ENV (lihat .env.example), TIDAK pakai token Orion.

## PAKET AFFILIATE (2 VERSI)
### v1 - Mode Langsung (Legacy)
File: affiliate/scheduler_v1_legacy.py
Cara: 1 file+1 link ke Telegram -> Orion enqueue -> post FB+YT+X tiap 77 mnt.
Cocok: Bos yang kirim urut, kontrol manual.

### v2 - Mode Sheet (Active)
File: affiliate/scheduler.py
Cara: Bos kirim banyak -> masuk Google Sheet (tab Antrian) -> sync 53 mnt -> publish 67 mnt.
Cocok: batch banyak file, anti-spam, terpusat di Sheet.

## PAKET CS BOT
File: cs_bot/ziyan_corp_cs_bot.py (token di cs_bot.env)
Fungsi: CS Telegram otomatis (sales/closing), log keluhan CSV.

## PAKET JOB HUNTER
File: job_hunter/ziyan_job_hunter.json (import n8n)
Butuh: RAPIDAPI_KEY (JSearch), TELEGRAM_CHAT_ID

## STRATEGI HARGA (riset kompetitor Fiverr/Upwork, kurs 16.5k)
Berdasar riset:
- Fiverr Basic (1 platform): $15-50 = Rp247rb-825rb
- Standard (2-3 platform): $50-150 = Rp825rb-2.47jt
- Premium (custom n8n): $150-400 = Rp2.47jt-6.6jt
- Expert/Agency: $400-1000+ = Rp6.6jt-16.5jt+

PENETAPAN HARGA ZIYAN (positioning: murah + dokumentasi lengkap):
| Paket | Isi | Harga |
|---|---|---|
| Basic | 1 versi scheduler (pilih v1/v2) + setup 1 platform | Rp500rb |
| Standard | 2 versi + FB+YT+X + Sheet | Rp1.5jt |
| Premium | Semua template + CS Bot + Job Hunter + custom | Rp5jt |
| Maintenance | Perbaikan/bimbingan bulanan | Rp300rb/bln |

## CARA JUAL
1. Marketplace gratis: Gumroad (template), Fiverr/Upwork (jasa setup)
2. Landing page: ziyancorp.github.io/#templates (tombol "Ambil Template" = raw GitHub)
3. Lead: CS Bot @Employeezynbot -> arahkan ke order
4. Bukti: tunjukkan video crop top / Madeline yg sudah live di FB/YT/X

## ETICA
- Jangan jual yg bikin klien rugi
- Bukti dulu sebelum janji
- Token/key milik klien sendiri (gak pakai punya Orion)
