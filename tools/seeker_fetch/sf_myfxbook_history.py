"""Public Myfxbook trade history scraper (no login, no captcha).
Mechanism (measured 2026-11-09 on home PC, VNPT residential IP):
  * VNPT DNS NXDOMAINs myfxbook -> resolve via DoH (1.1.1.1) and pass --host-resolver-rules to Edge.
  * Cloudflare managed challenge blocks headless / Playwright-launched browsers ("Just a moment" loop),
    but a REAL Edge started normally with --remote-debugging-port passes it automatically
    (navigator.webdriver=false).  We attach with playwright.connect_over_cdp.
  * History data: POST /systemPageGetHistoryFirstPage.json (invitation=&accountOid=ID) -> JSON with HTML,
    then GET /paging.html?pt=4&p=N&...&id=ID (params copied from the paging buttons), 20 rows/page.
Usage: python sf_myfxbook_history.py OID [OID ...]   -> out/myfxbook/{OID}.csv
Env: SF_EDGE (path to msedge.exe), SF_CDP_PORT (9333), SF_GAP (seconds between pages, default 2.0)
"""
import os, sys, re, csv, json, time, html, random, subprocess

PORT = int(os.environ.get("SF_CDP_PORT", "9333"))
GAP = float(os.environ.get("SF_GAP", "2.0"))
HOSTS = ["www.myfxbook.com", "myfxbook.com", "static.mfbcdn.net", "websocket.mfbcdn.net"]

def doh(h):
    from curl_cffi import requests as r
    for _ in range(5):
        try:
            x = r.get(f"https://1.1.1.1/dns-query?name={h}&type=A", headers={"accept": "application/dns-json"},
                      timeout=10, impersonate="chrome")
            return [a["data"] for a in x.json().get("Answer", []) if a["type"] == 1]
        except Exception:
            time.sleep(1)
    return []

def cdp_up():
    import urllib.request
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=2); return True
    except Exception:
        return False

def start_edge():
    if cdp_up():
        return None
    rules = [f"MAP {h} {doh(h)[0]}" for h in HOSTS if doh(h)]
    edge = os.environ.get("SF_EDGE") or next(p for p in [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"] if os.path.exists(p))
    prof = os.path.abspath("profiles/mfb_cdp"); os.makedirs(prof, exist_ok=True)
    pr = subprocess.Popen([edge, f"--remote-debugging-port={PORT}", "--user-data-dir=" + prof, "--no-first-run",
                           "--no-default-browser-check", "--host-resolver-rules=" + ",".join(rules), "about:blank"])
    os.makedirs("out", exist_ok=True); open("out/edge_cdp.pid", "w").write(str(pr.pid))
    print("EDGE_PID", pr.pid, flush=True)
    for _ in range(20):
        if cdp_up(): break
        time.sleep(1)
    return pr.pid

FETCH_POST = """async (oid)=>{const r=await fetch('/systemPageGetHistoryFirstPage.json',{method:'POST',
 headers:{'content-type':'application/x-www-form-urlencoded; charset=UTF-8','x-requested-with':'XMLHttpRequest'},
 body:'invitation=&accountOid='+oid});return {st:r.status,t:await r.text()}}"""
FETCH_GET = """async (u)=>{const r=await fetch(u,{headers:{'x-requested-with':'XMLHttpRequest'}});return {st:r.status,t:await r.text()}}"""

def header_of(h):
    # column set differs per account (e.g. 'lots' vs 'sl','tp'); read it from the table header
    return re.findall(r'<th[^>]*class="([^"]*)"', h)

def parse_rows(h, header):
    out = []
    for r in re.findall(r'<tr class="commentRow[\s\S]*?</tr>', h):
        rec = re.search(r'data-record="(\d+)"', r)
        vals, user = [], []
        for attrs, t in re.findall(r"<td([^>]*)>([\s\S]*?)</td>", r):
            txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()
            if "tagWindow" in attrs or "sparkline" in attrs or "commentModal" in attrs:
                continue
            if "userTime" in attrs:
                user.append(txt); continue
            vals.append(txt)
        d = dict(zip(header, vals))
        d["record"] = rec.group(1) if rec else ""
        d["openDate_user"] = user[0] if user else ""
        d["closeDate_user"] = user[1] if len(user) > 1 else ""
        out.append(d)
    return out

def ensure_clearance(pg):
    for _ in range(5):
        try:
            pg.goto("https://www.myfxbook.com/", wait_until="domcontentloaded", timeout=60000); break
        except Exception as e:
            print("goto retry", str(e)[:60]); time.sleep(2)
    for _ in range(30):
        if "Just a moment" not in pg.title(): return True
        pg.wait_for_timeout(2000)
    return False

def ev(pg, js, arg, tries=8):
    # ISP DPI randomly resets connections -> "Failed to fetch"; retry with backoff
    for k in range(tries):
        try:
            return pg.evaluate(js, arg)
        except Exception as e:
            print("evaluate retry", k, str(e)[:60], flush=True); time.sleep(3 * (k + 1))
    return {"st": 0, "t": ""}

def scrape(pg, oid):
    r = ev(pg, FETCH_POST, oid)
    if r["st"] != 200:
        ensure_clearance(pg); r = ev(pg, FETCH_POST, oid)
    if r["st"] != 200: raise RuntimeError(f"first page {r['st']}")
    try:
        h = json.loads(r["t"])["content"]["history"]
    except Exception:
        raise RuntimeError(f"no history in response (status {r['st']}): {r['t'][:200]!r}")
    total = int((re.search(r'total="(\d+)"', h) or re.search(r"ts=(\d+)", h)).group(1))
    header = header_of(h)
    os.makedirs(f"out/myfxbook/raw_{oid}", exist_ok=True)
    open(f"out/myfxbook/raw_{oid}/p1.html", "w", encoding="utf-8").write(h)
    rows = parse_rows(h, header)
    btn = [html.unescape(x) for x in re.findall(r'class="btn paging-btn" params="([^"]+)"', h)]
    if btn:
        tmpl = btn[0]
        npages = (total + 19) // 20
        print(oid, "total", total, "pages", npages, flush=True)
        for p in range(2, npages + 1):
            u = "/paging.html" + re.sub(r"([?&])p=\d+", rf"\g<1>p={p}", tmpl, count=1)
            for k in range(6):
                time.sleep(GAP + random.uniform(0, 1.0))
                x = ev(pg, FETCH_GET, u)
                if x["st"] == 200 and "commentRow" in x["t"]: break
                print(oid, "page", p, "status", x["st"], "retry", k, flush=True)
                if x["st"] in (403, 503): ensure_clearance(pg)
                time.sleep(20 * (k + 1))
            open(f"out/myfxbook/raw_{oid}/p{p}.html", "w", encoding="utf-8").write(x["t"])
            rows += parse_rows(x["t"], header)
            if p % 20 == 0: print(oid, "page", p, "/", npages, "rows", len(rows), flush=True)
    os.makedirs("out/myfxbook", exist_ok=True)
    with open(f"out/myfxbook/{oid}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["record"] + header + ["openDate_user", "closeDate_user"], extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    print(oid, "DONE rows", len(rows), "of total", total, flush=True)

def main():
    from playwright.sync_api import sync_playwright
    start_edge()
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
        ctx = b.contexts[0]; pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        if "myfxbook.com" not in pg.url: ensure_clearance(pg)
        for oid in sys.argv[1:]:
            try: scrape(pg, oid)
            except Exception as e: print(oid, "FAIL", e, flush=True)
        b.close()

if __name__ == "__main__":
    main()
