"""MQL5 signal history export through a REAL Edge (CDP) with a dedicated persistent profile.
No credentials in code: the first run opens the MQL5 login page in profiles/mql5; a person (or a desktop agent
using the vault) logs in ONCE; the session then lives only in E:\\seeker_fetch\\profiles\\mql5 (never commit it).
Usage: python sf_mql5_export.py ids.txt [N]   -> out/mql5/{ID}.csv  (export = /en/signals/{ID}/export/history)
Env: SF_CDP_PORT_MQL5 (9334), SF_LOGIN_WAIT (seconds to wait for a manual login, default 0 = just report)
"""
import os, sys, time, random, subprocess, urllib.request

PORT = int(os.environ.get("SF_CDP_PORT_MQL5", "9334"))
WAIT = int(os.environ.get("SF_LOGIN_WAIT", "0"))
GAP = float(os.environ.get("SF_GAP", "8"))

def cdp_up():
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=2); return True
    except Exception:
        return False

def start_edge():
    if cdp_up(): return None
    edge = os.environ.get("SF_EDGE") or next(p for p in [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"] if os.path.exists(p))
    prof = os.path.abspath("profiles/mql5"); os.makedirs(prof, exist_ok=True)
    pr = subprocess.Popen([edge, f"--remote-debugging-port={PORT}", "--user-data-dir=" + prof,
                           "--no-first-run", "--no-default-browser-check", "about:blank"])
    os.makedirs("out", exist_ok=True); open("out/edge_mql5.pid", "w").write(str(pr.pid))
    print("EDGE_PID", pr.pid, flush=True)
    for _ in range(20):
        if cdp_up(): break
        time.sleep(1)
    return pr.pid

FETCH = """async (u)=>{const r=await fetch(u,{credentials:'include',redirect:'follow'});
 return {st:r.status,url:r.url,ct:r.headers.get('content-type'),t:await r.text()}}"""

def logged_in(pg):
    for k in range(4):
        try:
            pg.goto("https://www.mql5.com/en/signals", wait_until="domcontentloaded", timeout=60000); break
        except Exception as e:
            print("goto retry", str(e)[:60]); time.sleep(3)
    html = pg.content()
    return ("auth_logout" in html) or ("/en/users/" in html and "auth_login" not in html[:200000])

def main():
    from playwright.sync_api import sync_playwright
    ids = [l.strip() for l in open(sys.argv[1]) if l.strip()][: int(sys.argv[2]) if len(sys.argv) > 2 else None]
    start_edge()
    os.makedirs("out/mql5", exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
        ctx = b.contexts[0]; pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        ok = logged_in(pg)
        print("LOGGED_IN", ok, flush=True)
        if not ok and os.environ.get("SF_MQL5_USER") and os.environ.get("SF_MQL5_PASS"):
            # one-shot login: creds come only from env vars for this process (from the vault), never stored
            try:
                pg.goto("https://www.mql5.com/en/auth_login", wait_until="domcontentloaded", timeout=60000)
                pg.fill('input[name="Login"]', os.environ["SF_MQL5_USER"])
                pg.fill('input[name="Password"]', os.environ["SF_MQL5_PASS"])
                pg.click('#loginSubmit')
                pg.wait_for_timeout(8000)
                ok = logged_in(pg); print("LOGGED_IN after env login", ok, flush=True)
            except Exception as e:
                print("env login failed", str(e)[:120], flush=True)
        if not ok and WAIT:
            pg.goto("https://www.mql5.com/en/auth_login", wait_until="domcontentloaded", timeout=60000)
            t0 = time.time()
            while time.time() - t0 < WAIT and not ok:
                time.sleep(10); ok = "auth_login" not in pg.url and logged_in(pg)
            print("LOGGED_IN after wait", ok, flush=True)
        if not ok:
            r = pg.evaluate(FETCH, f"https://www.mql5.com/en/signals/{ids[0]}/export/history")
            print("NEED_LOGIN export ->", r["st"], r["url"][:120], flush=True)
            b.close(); return 2
        for sid in ids:
            dst = f"out/mql5/{sid}.csv"
            if os.path.exists(dst) and os.path.getsize(dst) > 100: continue
            for k in range(4):
                try:
                    r = pg.evaluate(FETCH, f"https://www.mql5.com/en/signals/{sid}/export/history")
                except Exception as e:
                    r = {"st": 0, "url": str(e)[:80], "ct": "", "t": ""}
                if r["st"] == 200 and "auth_login" not in r["url"] and "html" not in (r["ct"] or ""): break
                print(sid, "status", r["st"], r["url"][:100], r["ct"], "retry", k, flush=True)
                time.sleep(30 * (k + 1))
            if r["st"] == 200 and "html" not in (r["ct"] or ""):
                open(dst, "w", encoding="utf-8").write(r["t"]); print(sid, "OK bytes", len(r["t"]), flush=True)
            time.sleep(GAP + random.uniform(0, 4))
        b.close()

if __name__ == "__main__":
    sys.exit(main())
