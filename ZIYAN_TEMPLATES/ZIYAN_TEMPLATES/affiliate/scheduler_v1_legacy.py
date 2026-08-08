"""
ZIYAN Auto-Affiliate SCHEDULER v1 (LEGACY - Mode Langsung)
- Bos kirim 1 file + 1 link ke Telegram -> Orion enqueue manual -> post FB+YT+X tiap 77 mnt
- TIDAK PAKAI kredensial Bos: semua dari ENV (lihat .env.example)
- Ini template siap pakai: ganti env, jalan.

CARA PAKAI:
1. Copy .env.example -> .env, isi:
   FB_PAGE_TOKEN, PAGE_ID, YT_TOKEN_PATH, GOOGLE_TOKEN_PATH, GOOGLE_SECRET_PATH, HERMES_CUSTOM_9ROUTER_API_KEY
2. python scheduler_v1_legacy.py loop
"""
import os, json, time, subprocess, urllib.request, urllib.parse
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
QUEUE = os.path.join(BASE, "queue_v1.json")
INTERVAL = 77 * 60

# ENV-based (jangan hardcode)
FB_TOK = os.environ.get("FB_PAGE_TOKEN", "")
PAGE_ID = os.environ.get("PAGE_ID", "")
YT_TOK_PATH = os.environ.get("YT_TOKEN_PATH", "")
G_TOK_PATH = os.environ.get("GOOGLE_TOKEN_PATH", "")
G_SEC_PATH = os.environ.get("GOOGLE_SECRET_PATH", "")
N9R_KEY = os.environ.get("HERMES_CUSTOM_9ROUTER_API_KEY", "")

def enqueue(item: dict):
    q = json.load(open(QUEUE)) if os.path.exists(QUEUE) else []
    item.update({"enqueued_at": datetime.now(timezone.utc).isoformat(), "posted": False})
    q.append(item); json.dump(q, open(QUEUE, "w"), indent=2, ensure_ascii=False)
    print(f"QUEUED v1 ({len(q)}): {item.get('deskripsi','')[:40]}")

def _post_fb(caption, file_path=None):
    if not FB_TOK: return "NO_FB_TOK"
    if file_path and file_path.lower().endswith((".mp4",".mov",".webm")):
        cmd=["curl","-s","-m","60","-X","POST",f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos",
             "-F",f"description={caption}","-F",f"access_token={FB_TOK}",f"-F",f"source=@{file_path};type=video/mp4"]
    else:
        cmd=["curl","-s","-m","20","-X","POST",f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed",
             "-F",f"message={caption}","-F",f"access_token={FB_TOK}"]
    return subprocess.run(cmd,capture_output=True,text=True,timeout=70).stdout.strip()

def _post_yt(caption, file_path):
    if not (file_path and file_path.lower().endswith((".mp4",".mov",".webm"))): return "SKIP"
    if not YT_TOK_PATH or not os.path.exists(YT_TOK_PATH): return "NO_YT_TOK"
    tok=json.load(open(YT_TOK_PATH)).get("access_token","")
    meta={"snippet":{"title":(caption.split(chr(10))[1][:60] if len(caption.split(chr(10)))>1 else "ZIYAN"),
                    "description":caption},"status":{"privacyStatus":"public"}}
    tmp=os.path.join(BASE,"yt_meta.json"); json.dump(meta,open(tmp,"w"),ensure_ascii=False)
    cmd=["curl","-s","-m","90","-X","POST","https://www.googleapis.com/upload/youtube/v3/videos?part=snippet,status&uploadType=multipart",
         "-H",f"Authorization: Bearer {tok}",f"-F",f"metadata=<{tmp};type=application/json",f"-F",f"file=@{file_path};type=video/mp4"]
    out=subprocess.run(cmd,capture_output=True,text=True,timeout=100)
    try:
        r=json.loads(out.stdout); return r.get("id","ERR:"+str(r.get('error',{}).get('message',''))[:50])
    except: return "ERR:"+out.stdout[:50]

def _post_x(caption, file_path=None):
    try:
        from post_tweet_helpers import post_tweet as px
        return px(caption, file_path)
    except Exception as e:
        return f"XERR:{str(e)[:50]}"

def run_once():
    q=json.load(open(QUEUE)) if os.path.exists(QUEUE) else []
    for it in q:
        if not it.get("posted"):
            cap=it.get("caption") or it.get("deskripsi","")
            fb=_post_fb(cap,it.get("file_path")); yt=_post_yt(cap,it.get("file_path")); xt=_post_x(cap,it.get("file_path"))
            it.update({"posted":True,"fb":fb[:50],"yt":yt,"x":str(xt)[:50],"posted_at":datetime.now(timezone.utc).isoformat()})
            json.dump(q,open(QUEUE,"w"),indent=2,ensure_ascii=False)
            print(f"POSTED v1 FB={fb[:25]} YT={yt} X={xt}")
            return True
    return False

def loop():
    last=0
    while True:
        q=json.load(open(QUEUE)) if os.path.exists(QUEUE) else []
        if [i for i in q if not i.get("posted")] and (time.time()-last>=INTERVAL):
            run_once(); last=time.time()
        time.sleep(60)

if __name__=="__main__":
    import sys
    if len(sys.argv)>1 and sys.argv[1]=="loop": loop()
    elif len(sys.argv)>1 and sys.argv[1]=="once": run_once()
