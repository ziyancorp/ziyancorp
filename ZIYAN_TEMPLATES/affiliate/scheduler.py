"""
ZIYAN Intake Scheduler v3
- Bos kirim bahan -> enqueue() tulis ke Google Sheet tab "Antrian"
- Timer 53 mnt: sync Antrian -> queue lokal
- Timer 67 mnt: post 1 item dari queue -> FB/YT/X -> pindah ke tab "Posted"
"""
import os, json, time, subprocess, urllib.request, urllib.parse
from datetime import datetime, timezone

BASE = r"C:\Users\arija\ziyan_intake"
QUEUE = os.path.join(BASE, "queue.json")
FB_TOK = open(r"C:\Users\arija\OneDrive\ziyan_pending\fb_page_token.txt").read().strip()
PAGE_ID = "975723622288353"
SHEET_ID = "1wLqdaYcjdaxXD1nEXPIv9PHObFhQPCi80cSiUHqEG8w"
SYNC_INT = 53 * 60
PUB_INT = 67 * 60

def _gtok():
    d = json.load(open(r"C:\Users\arija\AppData\Local\hermes\ziyan_google_token.json"))
    sec = json.load(open(r"C:\Users\arija\AppData\Local\hermes\google_client_secret.json"))["installed"]
    return d.get("access_token"), d.get("refresh_token"), sec["client_id"], sec["client_secret"]

def _refresh():
    at, rt, cid, csec = _gtok()
    body = urllib.parse.urlencode({"client_id":cid,"client_secret":csec,"refresh_token":rt,"grant_type":"refresh_token"}).encode()
    r = json.loads(urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token",data=body,method="POST"),timeout=15).read())
    d = json.load(open(r"C:\Users\arija\AppData\Local\hermes\ziyan_google_token.json"))
    d["access_token"]=r["access_token"]; json.dump(d,open(r"C:\Users\arija\AppData\Local\hermes\ziyan_google_token.json","w"),indent=2)
    return r["access_token"]

def _sheets_get(tab, rng="A1:Z1000"):
    at,rt,cid,csec=_gtok()
    url=f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{tab}!{rng}?access_token={at}"
    try:
        return json.loads(urllib.request.urlopen(url,timeout=15).read()).get("values",[])
    except urllib.error.HTTPError:
        _refresh(); at,rt,cid,csec=_gtok()
        url=f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{tab}!{rng}?access_token={at}"
        return json.loads(urllib.request.urlopen(url,timeout=15).read()).get("values",[])

def _sheets_append(tab, row):
    at = _refresh()
    vals={"values":[row]}
    tmp=os.path.join(BASE,"sheet_tmp.json"); json.dump(vals,open(tmp,"w"),ensure_ascii=False)
    cmd=["curl","-s","-m","20","-X","POST",
         f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{tab}!A:G:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS",
         "-H",f"Authorization: Bearer {at}","-H","Content-Type: application/json","--data-binary",f"@{tmp}"]
    out=subprocess.run(cmd,capture_output=True,text=True,timeout=25)
    return "updates" in out.stdout

def _sheets_clear(tab):
    at=_refresh()
    cmd=["curl","-s","-m","20","-X","POST",
         f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{tab}!A2:G1000:clear",
         "-H",f"Authorization: Bearer {at}","-H","Content-Type: application/json"]
    subprocess.run(cmd,capture_output=True,text=True,timeout=25)

def ensure_tabs():
    # buat header kalau tab kosong
    for tab,hdr in [("Antrian",["enqueued_at","file_path","deskripsi","link_aff","caption","tipe","posted"]),
                    ("Posted",["posted_at","file_path","deskripsi","link_aff","fb","yt","x"])]:
        rows=_sheets_get(tab,"A1:G1")
        if not rows:
            _sheets_append(tab,hdr)

def enqueue(item: dict):
    item.update({"enqueued_at":datetime.now(timezone.utc).isoformat(),"posted":"FALSE"})
    _sheets_append("Antrian",[item.get("enqueued_at"),item.get("file_path",""),item.get("deskripsi",""),
                              item.get("link_aff",""),item.get("caption",""),item.get("tipe",""),"FALSE"])
    print("SHEET Antrian +1:", item.get("deskripsi","")[:40])

def sync_from_sheet():
    rows=_sheets_get("Antrian","A2:G1000")
    q=[]
    for r in rows:
        if len(r)<7 or r[6].upper()=="TRUE": continue
        q.append({"enqueued_at":r[0],"file_path":r[1] or None,"deskripsi":r[2],
                  "link_aff":r[3],"caption":r[4],"tipe":r[5],"posted":False})
    json.dump(q,open(QUEUE,"w"),indent=2,ensure_ascii=False)
    return len(q)

def _post_fb(caption, file_path=None):
    if file_path and file_path.lower().endswith((".mp4",".mov",".webm")):
        cmd=["curl","-s","-m","60","-X","POST",f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos",
             "-F",f"description={caption}","-F",f"access_token={FB_TOK}",f"-F",f"source=@{file_path};type=video/mp4"]
    else:
        cmd=["curl","-s","-m","20","-X","POST",f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed",
             "-F",f"message={caption}","-F",f"access_token={FB_TOK}"]
    return subprocess.run(cmd,capture_output=True,text=True,timeout=70).stdout.strip()

def _post_yt(caption, file_path):
    if not (file_path and file_path.lower().endswith((".mp4",".mov",".webm"))): return "SKIP"
    tok=json.load(open(r"C:\Users\arija\AppData\Local\hermes\ziyan_youtube_token.json"))["access_token"]
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
        import sys; sys.path.insert(0,BASE)
        from post_tweet_helpers import post_tweet as px
        return px(caption, file_path)
    except Exception as e:
        return f"XERR:{str(e)[:50]}"

def publish_one():
    q=json.load(open(QUEUE)) if os.path.exists(QUEUE) else []
    for it in q:
        if not it.get("posted"):
            cap=it.get("caption") or it.get("deskripsi","")
            fb=_post_fb(cap,it.get("file_path")); yt=_post_yt(cap,it.get("file_path")); xt=_post_x(cap,it.get("file_path"))
            # pindah ke Posted tab
            _sheets_append("Posted",[datetime.now(timezone.utc).isoformat(),it.get("file_path",""),it.get("deskripsi",""),
                                   it.get("link_aff",""),fb[:30],yt,str(xt)[:30]])
            it["posted"]=True
            # tandai di Antrian (clear lalu tulis ulang posted=TRUE) - simplifikasi: clear Antrian tiap sync
            print(f"PUBLISHED FB={fb[:25]} YT={yt} X={xt}")
            return True
    return False

def loop():
    ensure_tabs()
    last_sync=0; last_pub=0
    while True:
        t=time.time()
        q=json.load(open(QUEUE)) if os.path.exists(QUEUE) else []
        pending=[i for i in q if not i.get("posted")]
        if t-last_sync>=SYNC_INT:
            n=sync_from_sheet(); last_sync=t; print(f"SYNC sheet -> {n} item")
        if pending and t-last_pub>=PUB_INT:
            publish_one(); last_pub=t
            # setelah publish, clear Antrian agar gak dobel
            _sheets_clear("Antrian")
        time.sleep(60)

if __name__=="__main__":
    import sys
    if len(sys.argv)>1 and sys.argv[1]=="loop": loop()
    elif len(sys.argv)>1 and sys.argv[1]=="once":
        ensure_tabs(); sync_from_sheet(); publish_one()
