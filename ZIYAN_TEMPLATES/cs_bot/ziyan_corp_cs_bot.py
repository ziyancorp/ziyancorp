#!/usr/bin/env python3
"""
ZIYAN AI CS Bot - Telegram customer service untuk layanan Job Hunter.
Dibekali knowledge: sales, marketing, closing, objection handling.
Wewenang: ambil keputusan (quote harga, tawarkan paket, arahkan daftar).
Model: 9router (openrouter/auto) via HTTP lokal.
PERSISTENT LOG: semua interaksi + keluhan dicatat ke ziyan_intake/cs_log.csv
"""
import os, json, csv, urllib.request, urllib.parse, time, threading
from datetime import datetime, timezone

BOT_TOKEN = open('ziyan_cs_bot.env').read().strip().split('=', 1)[1]
LOG_PATH = os.path.join('ziyan_intake', 'cs_log.csv')

COMPLAINT_KW = ["gak dijawab", "tidak dijawab", "gk dijawab", "komplain", "marah", "lambat",
                "error", "gagal", "mahal", "bingung", "gak jelas", "tidak jelas", "bug",
                "lemot", "rusak", "gak jalan", "gagal balas", "kok gak"]

SYSTEM_PROMPT = """Kamu adalah AI Customer Service resmi ZIYAN untuk layanan "AI Job Hunter".
PRODUK: Tim agent AI memantau job board 24/7, filter lowongan cocok vs CV user, kirim rekomendasi ke Telegram/WhatsApp.
PAKET: Rp99.000/bln (cancel kapan saja). Gratis trial 3 hari.

KOMPETENSI:
- SALES: identifikasi kebutuhan user (posisi apa, remote/WFH/on-site, lokasi)
- MARKETING: jelaskan nilai (hemat waktu, gak perlu scroll tiap hari, filter cerdas)
- CLOSING: kalau user tertarik, langsung arahkan ke daftar (minta email/nama) atau tawarkan trial
- OBJECTION HANDLING:
  * "mahal" -> bandingkan dengan biaya wasted time cari kerja manual; ada trial gratis
  * "gak yakin" -> kasih contoh hasil (skor kecocokan, link lamaran)
  * "data aman?" -> tegaskan hanya pakai CV yg user kasih, gak jual data
  * "cuma 1 produk?" -> iya, fokus terbaik di Job Hunter; bisa custom untuk perusahaan
  * "gak dijawab / lambat" -> minta maaf, bilang bot sedang stabil, balas sekarang
- ETIKA: jangan janjikan garansi dapat kerja. Janjikan REKOMENDASI + FILTER.

WEWENANG KEPUTUSAN:
- Beri quote harga resmi (Rp99rb/bln)
- Tawarkan trial 3 hari gratis
- Catat lead (nama, posisi dicari) ke respons
- Kalau user minta manusia, arahkan ke admin (tapi usahakan selesaikan dulu)

GAYA: ramah, singkat, bahasa Indonesia, proaktif tanya kebutuhan. Max 3 paragraf per balasan.
"""

def log_cs(cid, uname, umsg, creply):
    try:
        os.makedirs('ziyan_intake', exist_ok=True)
        cat = "KELUHAN" if any(k in (umsg + creply).lower() for k in COMPLAINT_KW) else "UMUM"
        hdr = ["waktu", "chat_id", "username", "pesan_user", "balasan_cs", "kategori"]
        if not os.path.exists(LOG_PATH):
            with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(hdr)
        with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
                cid, uname, umsg.replace("\n", " "), creply.replace("\n", " "), cat])
    except Exception as e:
        print("log err:", str(e)[:50])

def call_9router(user_msg, history):
    key = os.environ.get("HERMES_CUSTOM_9ROUTER_API_KEY", "")
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    msgs += history[-6:]
    msgs.append({"role": "user", "content": user_msg})
    body = json.dumps({"model": "kr/auto", "messages": msgs}).encode()
    req = urllib.request.Request("http://127.0.0.1:20128/v1/chat/completions",
        data=body, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        raw = urllib.request.urlopen(req, timeout=25).read().decode()
        # 9router balikin Server-Sent Events (SSE): "data: {json}\n\n"
        # tiap chunk punya choices[0].delta.content -> gabungkan
        parts = []
        for line in raw.splitlines():
            line = line.strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload in ("[DONE]", ""):
                continue
            try:
                obj = json.loads(payload)
                if "choices" in obj:
                    delta = obj["choices"][0].get("delta", {})
                    if delta.get("content"):
                        parts.append(delta["content"])
            except:
                pass
        if parts:
            return "".join(parts).strip()
        return "[CS gangguan: no content]"
    except Exception as ex:
        return f"[CS gangguan: {str(ex)[:40]}]"

def handle(cid, text, history):
    try:
        if text.startswith("/start"):
            reply = "Halo! Saya AI CS ZIYAN.\n\nLayanan kami:\n1. AI Job Hunter (Rp99rb/bln, trial 3 hari) - tim AI cariin lowongan cocok tiap hari ke HP kamu.\n\nMau cari posisi apa?"
        else:
            h = history.get(cid, [])
            reply = call_9router(text, h)
            h.append({"role": "user", "content": text})
            h.append({"role": "assistant", "content": reply})
            history[cid] = h[-6:]
        uname = str(cid)
        log_cs(cid, uname, text, reply)
        urllib.request.urlopen(urllib.request.Request(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data=urllib.parse.urlencode({"chat_id": cid, "text": reply}).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"}), timeout=15)
    except Exception as ex:
        print("handle err:", str(ex)[:60])

def main():
    offset = 0
    history = {}
    print("ZIYAN CS Bot jalan...")
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=20"
            upd = json.load(urllib.request.urlopen(url, timeout=25))
            for u in upd.get("result", []):
                offset = u["update_id"] + 1
                msg = u.get("message", {})
                text = msg.get("text", "")
                cid = msg.get("chat", {}).get("id")
                if not cid or not text:
                    continue
                threading.Thread(target=handle, args=(cid, text, history), daemon=True).start()
        except Exception as e:
            print("loop err:", str(e)[:60])
            time.sleep(3)

if __name__ == "__main__":
    main()
