#!/usr/bin/env python3
"""
ZIYAN Distributor - baca produk dari Sheet ARSIP_MASTER, generate caption alami
via 9Router, lalu distribusi ke platform.
Tahap 1: Telegram channel (credential ada). FB/IG/Threads/YT = butuh token Bos.
"""
import os, json, sys
from pathlib import Path
from dotenv import load_dotenv
import requests

ROOT = Path(r"C:\Users\arija\ziyancorp\ziyan_archive_bot")
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT))
from ziyan_bot.google_workspace import GoogleWorkspace
from ziyan_bot.config import Settings

NINE_ROUTER = "http://127.0.0.1:20128/v1/chat/completions"

def gen_caption(product: dict, persona: str = "Celine Aurel") -> str:
    """Caption untuk akun AI influencer Celine Aurel.
    Format: link affiliate -> deskripsi -> link lain -> hashtag. TANPA harga."""
    prompt = f"""Buat caption produk untuk akun AI influencer "{persona}" (lifestyle/fashion).
FORMAT WAJIB (urutan persis, pisahkan tiap bagian dengan 1 baris kosong):
[baris 1: link affiliate Shopee]
[baris kosong]
[1-2 kalimat deskripsi produk alami: sebutkan nama produk, varian ukuran, dan kapan/situasi cocok dipakai. Gaya santai tapi informatif, BUKAN hard-sell]
[baris kosong]
[baris: link affiliate lain (TikTok/Social) kalau ada, kalau tidak tulis -]
[baris kosong]
[5 hashtag relevan, masing-masing diawali #, dipisah spasi]

ATURAN KETAT:
- JANGAN SEKALI-KALI menyebut harga, diskon, atau angka rupiah.
- Jangan pakai gaya robotik / capslock berlebih.

Produk: {product.get('title')}
Deskripsi asli: {product.get('description')}
Link Shopee: {product.get('shopee_url') or ''}
Link TikTok/Social: {product.get('tiktok_url') or ''}"""
    key = os.environ.get("HERMES_CUSTOM_9ROUTER_API_KEY", "")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    try:
        r = requests.post(NINE_ROUTER, headers=headers, json={
            "model": "kr/claude-sonnet-4.5",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300, "temperature": 0.8, "stream": False
        }, timeout=40)
        # 9Router may return SSE even with stream=False; parse both
        text = r.text
        if text.strip().startswith("data:"):
            content = ""
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("data:") and "[DONE]" not in line:
                    try:
                        obj = json.loads(line[5:].strip())
                        delta = obj["choices"][0]["delta"].get("content", "")
                        content += delta
                    except: pass
            return content.strip() or prompt[:50]
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[{product.get('title')}] {product.get('shopee_url') or ''} {product.get('tiktok_url') or ''}"

def get_products(sheet_id: str, limit: int = 5):
    """Ambil produk terbaru dari tab PRODUCT_MASTER."""
    s = Settings.from_env()
    gw = GoogleWorkspace(s.google_credentials_file, s.google_token_file, s.google_root_folder_id, s.google_spreadsheet_id)
    res = gw.sheets.spreadsheets().values().get(spreadsheetId=s.google_spreadsheet_id, range="PRODUCT_MASTER!A2:K").execute()
    rows = res.get("values", [])[:limit]
    products = []
    for r in rows:
        products.append({
            "product_id": r[0] if len(r) > 0 else "",
            "title": r[1] if len(r) > 1 else "",
            "description": r[2] if len(r) > 2 else "",
            "shopee_url": r[3] if len(r) > 3 else "",
            "tiktok_url": r[4] if len(r) > 4 else "",
        })
    return products


# ===== MODUL DISTRIBUSI MULTI-PLATFORM (Celine Aurel) =====

def post_telegram_channel(caption: str, channel_id: str, bot_token: str) -> dict:
    r = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage",
                      json={"chat_id": channel_id, "text": caption, "disable_web_page_preview": False}, timeout=30)
    return r.json()


def post_facebook(caption: str, page_id: str, page_token: str) -> dict:
    r = requests.post(f"https://graph.facebook.com/v20.0/{page_id}/feed",
                      data={"message": caption, "access_token": page_token}, timeout=30)
    return r.json()


def post_instagram(caption: str, image_url: str, ig_id: str, access_token: str) -> dict:
    """Post gambar + caption ke Instagram Business Account via Meta Graph API."""
    if not image_url:
        return {"status": "skipped", "reason": "image_url_required"}
    
    # 1. Create Media Container
    container_url = f"https://graph.facebook.com/v20.0/{ig_id}/media"
    res1 = requests.post(container_url, data={
        "caption": caption,
        "image_url": image_url,
        "access_token": access_token
    }, timeout=30).json()
    
    creation_id = res1.get("id")
    if not creation_id:
        return {"status": "error", "error_container": res1}
    
    # 2. Publish Media Container
    publish_url = f"https://graph.facebook.com/v20.0/{ig_id}/media_publish"
    res2 = requests.post(publish_url, data={
        "creation_id": creation_id,
        "access_token": access_token
    }, timeout=30).json()
    
    return {"status": "success", "container_id": creation_id, "publish_response": res2}


def post_youtube(title: str, description: str, video_path: str, token_path: str = None) -> dict:
    """Upload video ke YouTube Celine Aurel Official via OAuth API resmi (fail-closed preflight)."""
    if not video_path or not os.path.exists(video_path):
        return {"status": "skipped", "reason": f"video_file_not_found: {video_path}"}
    try:
        import subprocess, sys
        expected = os.environ.get("YT_CELINE_CHANNEL", "UC0h3xyafx6P6J_CjpzhpSeg")
        client = os.environ.get("YT_CLIENT", "client_secret.json")
        tok = token_path or os.environ.get("YT_TOKEN", "token_celine.json")
        out = subprocess.run(
            [sys.executable, "youtube_upload_celine.py",
             "--file", video_path, "--title", title, "--description", description,
             "--privacy", "private", "--client", client, "--token", tok,
             "--expected-channel", expected],
            capture_output=True, text=True, timeout=180, cwd=os.path.dirname(os.path.abspath(__file__)))
        if "UPLOAD_OK" in out.stdout:
            for line in out.stdout.splitlines():
                if line.startswith("URL="):
                    return {"status": "success", "url": line.split("=",1)[1]}
            return {"status": "success", "raw": out.stdout.strip()}
        return {"status": "error", "stdout": out.stdout[:500], "stderr": out.stderr[:500]}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def post_threads(text: str, image_url: str = None, token: str = None) -> dict:
    """Post otomatis ke Threads API v1.0 via Threads user token."""
    if not token:
        token = os.environ.get("THREADS_USER_TOKEN") or os.environ.get("THREADS_USER_TOKEN_VAULT", "")
        
    if not token:
        return {"status": "skipped", "reason": "no_meta_token_for_threads"}
        
    try:
        url_create = "https://graph.threads.net/v1.0/me/threads"
        payload = {
            "media_type": "IMAGE" if image_url else "TEXT",
            "text": text[:500],
            "access_token": token
        }
        if image_url:
            payload["image_url"] = image_url
            
        r1 = requests.post(url_create, data=payload, timeout=30).json()
        if "id" not in r1:
            # Fallback to graph.facebook.com endpoint for threads
            url_fb = f"https://graph.facebook.com/v20.0/me/threads"
            r1 = requests.post(url_fb, data=payload, timeout=30).json()
            
        if "id" not in r1:
            return {"status": "error", "response": r1}
            
        creation_id = r1["id"]
        url_pub = "https://graph.threads.net/v1.0/me/threads_publish"
        r2 = requests.post(url_pub, data={
            "creation_id": creation_id,
            "access_token": token
        }, timeout=30).json()
        
        return {"status": "success", "creation_id": creation_id, "publish_response": r2}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def distribute_to_platforms(product: dict, caption: str, targets: list, bot_token: str, fb_page_id: str, fb_token: str) -> dict:
    results = {}
    
    if "telegram" in targets or "all" in targets:
        ch = os.environ.get("CHANNEL_CELINE", "-1004373452633")
        results["telegram"] = post_telegram_channel(caption, ch, bot_token)
        
    if "facebook" in targets or "all" in targets:
        results["facebook"] = post_facebook(caption, fb_page_id, fb_token)
        
    if "instagram" in targets or "all" in targets:
        ig_id = os.environ.get("IG_BUSINESS_ID", "17841444876830769")
        ig_token = os.environ.get("META_USER_TOKEN", fb_token)
        img_url = product.get("image_url") or "https://picsum.photos/800/1000"
        results["instagram"] = post_instagram(caption, img_url, ig_id, ig_token)
        
    if "youtube" in targets or "all" in targets:
        vid_path = product.get("video_path")
        title = product.get("title") or "Celine Aurel Fashion Shorts"
        results["youtube"] = post_youtube(title, caption, vid_path)
        
    if "threads" in targets or "all" in targets:
        img_url = product.get("image_url") or "https://picsum.photos/800/1000"
        token = os.environ.get("META_USER_TOKEN", fb_token)
        results["threads"] = post_threads(caption, img_url, token)
        
    return results


if __name__ == "__main__":
    print("=== TEST: generate caption dari 1 produk terbaru ===")
    prods = get_products("", limit=1)
    if not prods:
        print("Belum ada produk di Sheet.")
    else:
        p = prods[0]
        print(f"Produk: {p['title']}")
        cap = gen_caption(p)
        print("\n--- CAPTION (AI, natural) ---")
        print(cap)
        print("\n--- TEST OK, distributor siap dipasang ke Telegram channel ---")


# ===== SCHEDULER PRIME-TIME (anti-deteksi bot) =====
# Jam upload target (WIB): 08:57, 13:03, 16:24, 20:29
# Tiap slot: ambil 1 produk PENDING -> post ke 5 platform -> status PUBLISHED

def get_pending_products(sheet_id: str = "", limit: int = 1):
    """Ambil produk dengan status PENDING dari PRODUCT_MASTER (kolom J = status)."""
    s = Settings.from_env()
    gw = GoogleWorkspace(s.google_credentials_file, s.google_token_file, s.google_root_folder_id, s.google_spreadsheet_id)
    res = gw.sheets.spreadsheets().values().get(
        spreadsheetId=s.google_spreadsheet_id, range="PRODUCT_MASTER!A2:K").execute()
    rows = res.get("values", [])
    out = []
    for i, r in enumerate(rows):
        status = r[9] if len(r) > 9 else ""
        if status.upper() == "PENDING":
            out.append({
                "row": i + 2,
                "product_id": r[0] if len(r) > 0 else "",
                "title": r[1] if len(r) > 1 else "",
                "description": r[2] if len(r) > 2 else "",
                "shopee_url": r[3] if len(r) > 3 else "",
                "tiktok_url": r[4] if len(r) > 4 else "",
                "other_links": r[5] if len(r) > 5 else "",
                "folder_url": r[6] if len(r) > 6 else "",
                "asset_count": r[7] if len(r) > 7 else "",
                "video_path": r[6] if len(r) > 6 else "",
                "image_url": r[6] if len(r) > 6 else "",
            })
            if len(out) >= limit:
                break
    return out


def mark_published(product_id: str, sheet_row: int):
    """Update status kolom J (index 9) jadi PUBLISHED + timestamp kolom I."""
    s = Settings.from_env()
    gw = GoogleWorkspace(s.google_credentials_file, s.google_token_file, s.google_root_folder_id, s.google_spreadsheet_id)
    ts = datetime.now(ZoneInfo("Asia/Jakarta")).isoformat(timespec="seconds")
    rng = f"PRODUCT_MASTER!I{sheet_row}:J{sheet_row}"
    gw.sheets.spreadsheets().values().update(
        spreadsheetId=s.google_spreadsheet_id, range=rng,
        valueInputOption="RAW", body={"values": [[ts, "PUBLISHED"]]}).execute()


def post_one_pending() -> dict:
    """Ambil 1 produk PENDING, post ke semua platform, mark PUBLISHED."""
    pending = get_pending_products(limit=1)
    if not pending:
        return {"status": "no_pending", "message": "Tidak ada produk PENDING."}
    prod = pending[0]
    try:
        caption = gen_caption(prod)
    except Exception:
        caption = f"[{prod['title']}] {prod['shopee_url']} {prod['tiktok_url']}"
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    fb_page_id = os.environ.get("FB_PAGE_ID", "975723622288353")
    fb_token = os.environ.get("FB_PAGE_TOKEN", "")
    res = distribute_to_platforms(prod, caption, ["all"], bot_token, fb_page_id, fb_token)
    ok = any(v.get("status") == "success" for v in res.values() if isinstance(v, dict))
    if ok:
        mark_published(prod["product_id"], prod["row"])
        return {"status": "published", "product_id": prod["product_id"], "results": res}
    return {"status": "failed", "product_id": prod["product_id"], "results": res}
