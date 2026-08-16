#!/usr/bin/env python3
"""
Threads re-auth (TERPISAH dari fb_reauth.py).
Flow: Bos authorize -> code -> short token -> long token (60 hari) -> save vault.
Credential: Threads App ID/Secret (VAULT: threads_app_id.gpg / threads_app_secret.gpg).
Endpoint: graph.threads.com (BUKAN graph.facebook.com).
"""
import json, urllib.parse, urllib.request, sys, os, subprocess

def vault(k): return subprocess.check_output(['bash', '/c/Users/arija/bin/token_vault.sh', 'get', k]).decode().strip()
def vault_set(k, v): return subprocess.check_output(['bash', '/c/Users/arija/bin/token_vault.sh', 'set', k, v]).decode().strip()

REDIRECT = "https://localhost:8123/"

def req(url, data=None):
    r = urllib.request.urlopen(urllib.request.Request(url, data=data, method="POST" if data else "GET"))
    return json.loads(r.read())

def code_to_short(code, app_id, app_secret):
    url = (f"https://graph.threads.com/oauth/access_token"
           f"?client_id={app_id}&redirect_uri={urllib.parse.quote(REDIRECT)}"
           f"&client_secret={urllib.parse.quote(app_secret)}&code={urllib.parse.quote(code)}")
    return req(url).get("access_token")

def short_to_long(short, app_id, app_secret):
    url = (f"https://graph.threads.com/oauth/access_token"
           f"?grant_type=th_exchange_token&client_id={app_id}"
           f"&client_secret={urllib.parse.quote(app_secret)}&access_token={urllib.parse.quote(short)}")
    d = req(url)
    return d.get("access_token"), d.get("expires_in")

def refresh(long_token, app_id, app_secret):
    url = (f"https://graph.threads.com/oauth/access_token"
           f"?grant_type=th_refresh_token&client_id={app_id}"
           f"&client_secret={urllib.parse.quote(app_secret)}&refresh_token={urllib.parse.quote(long_token)}")
    d = req(url)
    return d.get("access_token")

if __name__ == "__main__":
    app_id = vault("threads_app_id")
    app_secret = vault("threads_app_secret")
    if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
        code = urllib.parse.parse_qs(urllib.parse.urlparse(sys.argv[1]).query).get("code", [None])[0]
        if not code:
            print("ERROR: gak ada code"); sys.exit(1)
        short = code_to_short(code, app_id, app_secret)
        long_tok, exp = short_to_long(short, app_id, app_secret)
        print(f"LONG TOKEN ({exp}s): {long_tok[:30]}...")
        # save ke vault + .env
        vault_set("threads_token", long_tok)
        # update .env
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        lines = open(env_path).read().splitlines()
        lines = [l for l in lines if not l.startswith("THREADS_USER_TOKEN=")]
        lines.append(f"THREADS_USER_TOKEN={long_tok}")
        open(env_path, "w").write("\n".join(lines) + "\n")
        print("SAVED to vault + .env")
        # test
        import requests
        r = requests.get("https://graph.threads.net/v1.0/me", params={"fields":"id,username","access_token":long_tok}, timeout=15)
        print("VALIDATE:", r.json() if r.status_code==200 else r.text[:100])
    else:
        url = (f"https://graph.threads.net/oauth/authorize?client_id={app_id}"
               f"&redirect_uri={urllib.parse.quote(REDIRECT)}"
               f"&scope=threads_basic%2Cthreads_content_publish&response_type=code")
        print("BUKA URL INI DI HP BOSS (login @celineaurel99):\n")
        print(url)
        print("\nCopy URL redirect lalu: python threads_reauth.py \"<URL>\"")
