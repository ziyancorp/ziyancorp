#!/usr/bin/env python3
"""
ZIYAN Distribution Agent - eksekusi distribusi ke YT, FB, IG, Threads (PUBLIK).
Baca produk terbaru dari ARSIP_MASTER -> baca AFFILIATE.json di Drive ->
ambil aset ASLI (foto/video) -> generate caption (format Bos) ->
post ke semua platform PUBLIK -> mark PUBLISHED.
"""
import os, sys, json, re, io, tempfile
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, str(Path(__file__).parent))
from distributor import (
    post_facebook, post_instagram, post_youtube, post_threads,
    Settings, GoogleWorkspace
)
from ziyan_bot.config import Settings as Cfg
from ziyan_bot.google_workspace import GoogleWorkspace

ROOT = Path(r"C:\Users\arija\ziyancorp\ziyan_archive_bot")
TMP = ROOT / "tmp_assets"
TMP.mkdir(exist_ok=True)

def get_products_latest(limit=1):
    s = Cfg.from_env()
    gw = GoogleWorkspace(s.google_credentials_file, s.google_token_file,
                         s.google_root_folder_id, s.google_spreadsheet_id)
    res = gw.sheets.spreadsheets().values().get(
        spreadsheetId=s.google_spreadsheet_id, range="PRODUCT_MASTER!A2:K").execute()
    rows = res.get("values", [])
    out = []
    for r in reversed(rows):
        out.append({
            "product_id": r[0] if len(r) > 0 else "",
            "title": r[1] if len(r) > 1 else "",
            "description": r[2] if len(r) > 2 else "",
            "shopee_url": r[3] if len(r) > 3 else "",
            "tiktok_url": r[4] if len(r) > 4 else "",
            "other_links": r[5] if len(r) > 5 else "",
            "folder_url": r[6] if len(r) > 6 else "",
        })
        if len(out) >= limit: break
    return out

def get_pending_product():
    """Ambil 1 produk yang BELUM dipost (kolom J status != PUBLISHED)."""
    s = Cfg.from_env()
    gw = GoogleWorkspace(s.google_credentials_file, s.google_token_file,
                         s.google_root_folder_id, s.google_spreadsheet_id)
    res = gw.sheets.spreadsheets().values().get(
        spreadsheetId=s.google_spreadsheet_id, range="PRODUCT_MASTER!A2:J").execute()
    rows = res.get("values", [])
    for r in reversed(rows):  # dari terbaru
        if len(r) > 0 and r[0]:
            status = r[9] if len(r) > 9 else ""
            if status != "PUBLISHED":
                return {
                    "product_id": r[0],
                    "title": r[1] if len(r) > 1 else "",
                    "description": r[2] if len(r) > 2 else "",
                    "shopee_url": r[3] if len(r) > 3 else "",
                    "tiktok_url": r[4] if len(r) > 4 else "",
                    "other_links": r[5] if len(r) > 5 else "",
                    "folder_url": r[6] if len(r) > 6 else "",
                }
    return None

def get_affiliate_json(gw, product_id):
    """Cari folder produk di Drive, baca AFFILIATE.json -> return dict."""
    root = gw.root_folder_id
    r = gw.drive.files().list(q=f"'{root}' in parents and name='2026-08'",
                              fields="files(id,name)").execute()
    if not r.get("files"): return None
    f2026 = r["files"][0]["id"]
    r2 = gw.drive.files().list(q=f"'{f2026}' in parents and name contains '{product_id.split('-')[-1]}'",
                               fields="files(id,name)").execute()
    if not r2.get("files"): return None
    pid = r2["files"][0]["id"]
    r3 = gw.drive.files().list(q=f"'{pid}' in parents and name='AFFILIATE.json'",
                               fields="files(id,name)").execute()
    if not r3.get("files"): return None
    fid = r3["files"][0]["id"]
    data = gw.drive.files().get_media(fileId=fid).execute()
    return json.loads(data.decode())

def drive_id_from_url(url):
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url or "")
    return m.group(1) if m else None

def download_asset(gw, drive_url, suffix):
    fid = drive_id_from_url(drive_url)
    if not fid: return None
    path = TMP / f"asset_{suffix}"
    try:
        gw.drive.files().get_media(fileId=fid).download(path)
        return str(path)
    except Exception:
        # fallback: direct get_media execute
        data = gw.drive.files().get_media(fileId=fid).execute()
        path.write_bytes(data)
        return str(path)

def build_caption(prod, affiliate):
    import requests
    shopee = (affiliate or {}).get("affiliate", {}).get("shopee") or prod.get("shopee_url") or ""
    other_list = (affiliate or {}).get("affiliate", {}).get("other") or []
    other = other_list[0] if other_list else (prod.get("other_links") or prod.get("tiktok_url") or "")
    # bersihkan harga dari title/desc
    clean = re.sub(r"dengan harga Rp[0-9.]+", "", prod.get("title",""), flags=re.I).strip()
    clean = re.sub(r"\. Dapatkan di Shopee sekarang!.*", "", clean, flags=re.I).strip()
    prompt = f"""Buat deskripsi produk ALAMI (1-2 kalimat) untuk akun fashion/lifestyle.
HANYA sebutkan: nama produk, varian ukuran (kalau ada), dan kapan/situasi cocok dipakai.
JANGAN sebut harga, diskon, atau angka rupiah apa pun.
Produk: {clean}

Lalu buat PERSIS 4 hashtag relevan (masing-masing diawali #, dipisah spasi).
Format output persis:
[1 baris deskripsi natural]
[baris kosong]
[4 hashtag]"""
    key = os.environ.get("HERMES_CUSTOM_9ROUTER_API_KEY", "")
    try:
        r = requests.post("http://127.0.0.1:20128/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model":"kr/claude-sonnet-4.5","messages":[{"role":"user","content":prompt}],
                  "max_tokens":200,"temperature":0.8,"stream":False},timeout=40)
        ai_text = r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        ai_text = f"{clean}\n\n#fashion #ootd #indonesia #style"
    lines = ai_text.split("\n")
    for i,l in enumerate(lines):
        if l.strip().startswith("#"):
            tags=l.split()
            if len(tags)!=4: lines[i]=" ".join(tags[:4]) if tags else "#fashion #ootd #indonesia #style"
            break
    ai_text="\n".join(lines)
    caption = shopee
    if caption: caption += "\n\n"
    caption += ai_text
    if other and other != shopee:
        caption += f"\n\n{other}"
    return caption

def mark_published(product_id):
    s = Cfg.from_env()
    gw = GoogleWorkspace(s.google_credentials_file, s.google_token_file,
                         s.google_root_folder_id, s.google_spreadsheet_id)
    res = gw.sheets.spreadsheets().values().get(
        spreadsheetId=s.google_spreadsheet_id, range="PRODUCT_MASTER!A2:A").execute()
    for i, r in enumerate(res.get("values", [])):
        if r and r[0] == product_id:
            row = i + 2
            ts = datetime.now(ZoneInfo("Asia/Jakarta")).isoformat(timespec="seconds")
            gw.sheets.spreadsheets().values().update(
                spreadsheetId=s.google_spreadsheet_id, range=f"PRODUCT_MASTER!I{row}:J{row}",
                valueInputOption="RAW", body={"values": [[ts, "PUBLISHED"]]}).execute()
            return True
    return False

def post_youtube_public(title, desc, video_path):
    try:
        import subprocess
        expected = os.environ.get("YT_CELINE_CHANNEL", "UC0h3xyafx6P6J_CjpzhpSeg")
        client = os.environ.get("YT_CLIENT", "client_secret.json")
        tok = os.environ.get("YT_TOKEN", "token_celine.json")
        out = subprocess.run([sys.executable, "youtube_upload_celine.py",
            "--file", video_path, "--title", title, "--description", desc,
            "--privacy", "public", "--client", client, "--token", tok,
            "--expected-channel", expected],
            capture_output=True, text=True, timeout=600, cwd=str(ROOT))
        if "UPLOAD_OK" in out.stdout:
            for line in out.stdout.splitlines():
                if line.startswith("URL="): return {"status":"success","url":line.split("=",1)[1]}
            return {"status":"success","raw":out.stdout.strip()}
        return {"status":"error","stdout":out.stdout[:500],"stderr":out.stderr[:500]}
    except Exception as e:
        return {"status":"error","error":str(e)}

def main():
    prod = get_pending_product()
    if not prod:
        print("[AGENT] Tidak ada produk pending. Skip.")
        return {"status":"no_pending","msg":"Semua produk sudah PUBLISHED"}
    print(f"[AGENT] Produk pending: {prod['product_id']}")

    # Baca AFFILIATE.json dari Drive
    s = Cfg.from_env()
    gw = GoogleWorkspace(s.google_credentials_file, s.google_token_file,
                         s.google_root_folder_id, s.google_spreadsheet_id)
    affiliate = get_affiliate_json(gw, prod["product_id"])
    assets = (affiliate or {}).get("assets", [])
    photos = [a for a in assets if a["file_name"].lower().endswith((".jpeg",".jpg",".png"))]
    videos = [a for a in assets if a["file_name"].lower().endswith((".mp4",".mov"))]
    print(f"[AGENT] Aset: {len(photos)} foto, {len(videos)} video")

    # Download aset asli
    fb_page_id = os.environ.get("FB_PAGE_ID", "975723622288353")
    fb_token = os.environ.get("FB_PAGE_TOKEN", "")
    photo_local = download_asset(gw, photos[0]["drive_url"], "photo.jpg") if photos else None
    video_local = download_asset(gw, videos[0]["drive_url"], "video.mp4") if videos else None
    img_url = None
    if photo_local:
        # Upload foto asli ke FB Page -> dapet CDN URL (IG bisa fetch)
        try:
            import requests as _req
            _r = _req.post(f"https://graph.facebook.com/v20.0/{fb_page_id}/photos",
                           files={"source": open(photo_local, "rb")},
                           data={"published": "false", "access_token": fb_token}, timeout=30)
            if _r.status_code == 200:
                _pid = _r.json().get("id")
                _r2 = _req.get(f"https://graph.facebook.com/v20.0/{_pid}",
                               params={"fields": "source", "access_token": fb_token}, timeout=15)
                img_url = _r2.json().get("source")
        except Exception as e:
            print(f"[AGENT] WARN upload foto ke FB gagal: {e}")
    print(f"[AGENT] Photo: {photo_local}, Video: {video_local}, img_url: {img_url}")

    caption = build_caption(prod, affiliate)
    print(f"[AGENT] Caption:\n{caption}\n")

    # Threads: pakai THREADS_USER_TOKEN (valid), BUKAN META_USER_TOKEN (expired)
    threads_token = os.environ.get("THREADS_USER_TOKEN", "")
    # IG: butuh token IG terpisah (instagram_token expired) -> skip kalau gak ada
    ig_token = os.environ.get("INSTAGRAM_USER_TOKEN", "")
    ig_id = os.environ.get("IG_BUSINESS_ID", "17841444876830769")

    results = {}
    # Facebook (publik)
    results["facebook"] = post_facebook(caption, fb_page_id, fb_token)
    # Instagram (butuh image_url publik + token IG valid)
    if img_url and ig_token:
        results["instagram"] = post_instagram(caption, img_url, ig_id, ig_token)
    elif not ig_token:
        results["instagram"] = {"status":"skipped","reason":"no_ig_token"}
    else:
        results["instagram"] = {"status":"skipped","reason":"no_image"}
    # YouTube (publik, video asli)
    if video_local:
        yt_title = (prod.get("title") or f"Produk {prod['product_id']}").strip()
        if len(yt_title) > 95:
            yt_title = yt_title[:95].rsplit(" ", 1)[0] + "..."
        # Description YT: sederhana (hindari reject YT)
        shopee = prod.get("shopee_url") or (affiliate or {}).get("shopee_url", "")
        yt_desc = f"Produk fashion ZIYAN.\n\nBeli di Shopee: {shopee}" if shopee else "Produk fashion ZIYAN."
        results["youtube"] = post_youtube_public(yt_title, yt_desc, video_local)
    else:
        results["youtube"] = {"status":"skipped","reason":"no_video"}
    # Threads (publik, TEXT only - image Drive gak bisa di-fetch Meta)
    results["threads"] = post_threads(caption, None, threads_token)

    try:
        mark_published(prod["product_id"])
        print("[AGENT] Status PUBLISHED di Sheet.")
    except Exception as e:
        print(f"[AGENT] WARN mark failed: {e}")

    return {"status":"executed","product_id":prod["product_id"],"caption":caption,"results":results}

if __name__ == "__main__":
    out = main()
    print("\n=== HASIL EKSEKUSI ===")
    print(json.dumps(out, indent=2, default=str))
