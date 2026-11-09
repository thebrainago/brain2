"""seeker_fetch: polite multi-method fetcher for Seeker sources (home PC).
Methods: requests (plain), curl_cffi (impersonate chrome TLS), playwright (headless/headed, optional persistent profile).
No credentials stored. Usage:
  python sf_fetch.py probe urls.txt            -> probe every URL with every method, write out/probe.json
  python sf_fetch.py get URL OUTFILE [--method curl|req|pw|pwh] [--profile DIR]
"""
import sys, time, json, random, os, re

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
HDR = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
       "Accept-Language": "en-US,en;q=0.9"}
BLOCK_PAT = re.compile(r"(<title>Just a moment|cf-chl-|Attention Required! \| Cloudflare|error code: 1015|<title>Access denied)", re.I)
MIN_GAP = float(os.environ.get("SF_MIN_GAP", "4"))
_last = {}

def pace(host):
    t = time.time() - _last.get(host, 0)
    if t < MIN_GAP:
        time.sleep(MIN_GAP - t + random.uniform(0.5, 2.0))
    _last[host] = time.time()

def classify(status, text):
    if status is None:
        return "error"
    if status in (429,) or "1015" in (text or "")[:5000] and "rate limit" in (text or "").lower():
        return "rate_limited"
    if status == 200 and not BLOCK_PAT.search((text or "")[:20000]):
        return "ok"
    if status == 200:
        return "challenge_200"
    return f"blocked_{status}"

def f_requests(url):
    import requests
    r = requests.get(url, headers=HDR, timeout=30)
    return r.status_code, r.text

# Home ISP (VNPT) DNS returns NXDOMAIN for myfxbook/fxblue and DPI resets TLS handshakes
# intermittently (~30% succeed).  Fixes: DNS-over-HTTPS inside curl + many short retries with a
# fresh connection + keep the session alive afterwards (keep-alive => no new handshake per request).
DOH = os.environ.get("SF_DOH", "https://1.1.1.1/dns-query").encode()
_cs = {}
def curl_session(host, fresh=False):
    from curl_cffi import requests as cr, CurlOpt
    if fresh or host not in _cs:
        _cs[host] = cr.Session(impersonate="chrome", curl_options={CurlOpt.DOH_URL: DOH})
    return _cs[host]

def f_curl(url, headers=None, conn_tries=int(os.environ.get("SF_CONN_TRIES", "10")), data=None):
    host = url.split("/")[2]
    last = None
    for i in range(conn_tries):
        s = curl_session(host, fresh=i > 0)
        try:
            h = {"Accept-Language": "en-US,en;q=0.9"}
            h.update(headers or {})
            r = s.post(url, data=data, headers=h, timeout=15) if data is not None else s.get(url, headers=h, timeout=15)
            return r.status_code, r.text
        except Exception as e:  # TLS reset / timeout from ISP DPI -> retry fresh
            last = e
            time.sleep(1 + random.random())
    raise last

def doh_a(host):
    from curl_cffi import requests as cr
    for _ in range(4):
        try:
            x = cr.get(f"https://1.1.1.1/dns-query?name={host}&type=A", headers={"accept": "application/dns-json"},
                       timeout=10, impersonate="chrome")
            return [a["data"] for a in x.json().get("Answer", []) if a["type"] == 1]
        except Exception:
            time.sleep(1)
    return []

def f_playwright(url, headed=False, profile=None, channel=None):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        kw = dict(headless=not headed, args=[])
        rules = os.environ.get("SF_HOST_RULES")  # e.g. "MAP www.myfxbook.com 104.18.22.170"
        if not rules and os.environ.get("SF_AUTO_DOH", "1") == "1":
            ips = doh_a(url.split("/")[2])
            rules = f"MAP {url.split('/')[2]} {ips[0]}" if ips else None
        if rules:
            kw["args"].append("--host-resolver-rules=" + rules)
        if channel:
            kw["channel"] = channel
        if profile:
            ctx = p.chromium.launch_persistent_context(profile, **kw)
        else:
            b = p.chromium.launch(**kw)
            ctx = b.new_context(user_agent=UA if not headed else None, locale="en-US")
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        resp = None
        for k in range(4):  # DPI resets -> net::ERR_CONNECTION_CLOSED, retry
            try:
                resp = pg.goto(url, wait_until="domcontentloaded", timeout=60000); break
            except Exception:
                if k == 3: raise
                time.sleep(2)
        st = resp.status if resp else None
        # give Cloudflare JS challenge a chance to resolve
        for _ in range(15):
            html = pg.content()
            if not BLOCK_PAT.search(html[:20000]):
                break
            pg.wait_for_timeout(2000)
        html = pg.content()
        if st != 200 and not BLOCK_PAT.search(html[:20000]) and len(html) > 5000:
            st = 200  # challenge passed after initial 403
        ctx.close()
        return st, html

def fetch(url, method="curl", tries=4, **kw):
    host = url.split("/")[2]
    fn = {"req": f_requests, "curl": f_curl,
          "pw": lambda u: f_playwright(u, False, **kw),
          "pwh": lambda u: f_playwright(u, True, **kw)}[method]
    back = 30
    for i in range(tries):
        pace(host)
        try:
            st, txt = fn(url)
        except Exception as e:
            st, txt = None, f"EXC {type(e).__name__}: {e}"
        c = classify(st, txt)
        if c == "rate_limited":
            time.sleep(back + random.uniform(0, 10)); back *= 2; continue
        return st, c, txt
    return st, c, txt

def main():
    a = sys.argv[1:]
    if a and a[0] == "probe":
        urls = [l.strip() for l in open(a[1]) if l.strip() and not l.startswith("#")]
        methods = (a[2].split(",") if len(a) > 2 else ["req", "curl", "pw", "pwh"])
        res = []
        for u in urls:
            for m in methods:
                st, c, txt = fetch(u, m, tries=1, channel=os.environ.get("SF_CHANNEL"))
                title = re.search(r"<title[^>]*>(.*?)</title>", txt or "", re.S | re.I)
                row = dict(url=u, method=m, status=st, cls=c, bytes=len(txt or ""),
                           title=(title.group(1).strip()[:80] if title else (txt or "")[:80]))
                print(json.dumps(row, ensure_ascii=False), flush=True)
                res.append(row)
        os.makedirs("out", exist_ok=True)
        json.dump(res, open("out/probe.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    elif a and a[0] == "get":
        m = "curl"; prof = None
        if "--method" in a: m = a[a.index("--method") + 1]
        if "--profile" in a: prof = a[a.index("--profile") + 1]
        kw = {"profile": prof} if m.startswith("pw") else {}
        st, c, txt = fetch(a[1], m, **kw)
        open(a[2], "w", encoding="utf-8").write(txt or "")
        print(st, c, len(txt or ""))
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
