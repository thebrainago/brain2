"""Discover a site's data (XHR/fetch) endpoints through a REAL Edge over CDP.
Usage: python sf_sniff.py URL [click-text ...]   -> prints & saves out/sniff_<host>.json
Resolves the page host (+ SF_EXTRA_HOSTS, comma list) via DoH and maps them with --host-resolver-rules,
because the home ISP DNS NXDOMAINs several forex sites. Edge runs on SF_CDP_PORT_SNIFF (9335), own profile.
"""
import os, sys, json, time, subprocess, urllib.request
from sf_fetch import doh_a

PORT = int(os.environ.get("SF_CDP_PORT_SNIFF", "9335"))

def cdp_up():
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=2); return True
    except Exception:
        return False

def start_edge(hosts):
    if cdp_up(): return None
    rules = []
    for h in hosts:
        ips = doh_a(h)
        if ips: rules.append(f"MAP {h} {ips[0]}")
    edge = os.environ.get("SF_EDGE") or next(p for p in [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"] if os.path.exists(p))
    prof = os.path.abspath("profiles/sniff"); os.makedirs(prof, exist_ok=True)
    pr = subprocess.Popen([edge, f"--remote-debugging-port={PORT}", "--user-data-dir=" + prof, "--no-first-run",
                           "--no-default-browser-check", "--host-resolver-rules=" + ",".join(rules), "about:blank"])
    os.makedirs("out", exist_ok=True); open("out/edge_sniff.pid", "w").write(str(pr.pid))
    print("EDGE_PID", pr.pid, flush=True)
    for _ in range(20):
        if cdp_up(): break
        time.sleep(1)
    return pr.pid

def main():
    from playwright.sync_api import sync_playwright
    url = sys.argv[1]; clicks = sys.argv[2:]
    host = url.split("/")[2]
    extra = [h for h in os.environ.get("SF_EXTRA_HOSTS", "").split(",") if h]
    start_edge([host] + extra)
    seen = []
    def on(resp):
        rt = resp.request.resource_type
        if rt in ("xhr", "fetch"):
            try: n = len(resp.body())
            except Exception: n = -1
            seen.append(dict(st=resp.status, m=resp.request.method, url=resp.url, post=resp.request.post_data, bytes=n,
                             ct=resp.headers.get("content-type", "")))
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
        ctx = b.contexts[0]; pg = ctx.new_page(); pg.on("response", on)
        for k in range(4):
            try: pg.goto(url, wait_until="domcontentloaded", timeout=60000); break
            except Exception as e: print("goto retry", str(e)[:60]); time.sleep(2)
        pg.wait_for_timeout(8000)
        for _ in range(4):
            pg.mouse.wheel(0, 2500); pg.wait_for_timeout(1500)
        for t in clicks:
            try:
                pg.get_by_text(t, exact=False).first.click(timeout=8000); pg.wait_for_timeout(6000); print("clicked", t)
            except Exception as e: print("click fail", t, str(e)[:60])
        print("title", pg.title())
        pg.close(); b.close()
    for s in seen:
        print(s["st"], s["m"], s["bytes"], s["ct"][:30], s["url"][:220], (s["post"] or "")[:120])
    json.dump(seen, open(f"out/sniff_{host}.json", "w", encoding="utf-8"), indent=1)

if __name__ == "__main__":
    main()
