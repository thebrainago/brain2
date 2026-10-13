# Quet DOC-ONLY nguon bi chan tren box, qua Chrome CDP 9224 (ho so moi, khong dang nhap). Khong dang/follow/like/nhan tin/join.
import json, re, time, random, sys
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
NGUON = [
 ("tradingview_strategies","https://www.tradingview.com/scripts/?script_type=strategies", r"tradingview\.com/script/[A-Za-z0-9]+-", 12),
 ("tradingview_scripts","https://www.tradingview.com/scripts/meanreversion/", r"tradingview\.com/script/[A-Za-z0-9]+-", 8),
 ("tradingview_breakout","https://www.tradingview.com/scripts/breakout/", r"tradingview\.com/script/[A-Za-z0-9]+-", 4),
 ("tradingview_ideas","https://www.tradingview.com/markets/currencies/ideas/", r"tradingview\.com/chart/[A-Z0-9_]+/[A-Za-z0-9]+-", 10),
 ("forexfactory_ea_threads","https://www.forexfactory.com/forum/71-trading-systems", r"forexfactory\.com/thread/\d+", 10),
 ("fxblue","https://www.fxblue.com/users", r"fxblue\.com/users/[^/?#]+$", 10),
 ("quantpedia","https://quantpedia.com/strategies/", r"quantpedia\.com/strategies/[a-z0-9-]+/?$", 8),
 ("quantifiedstrategies","https://www.quantifiedstrategies.com/forex-trading-strategies/", r"quantifiedstrategies\.com/[a-z0-9-]+/?$", 6),
 ("ssrn","https://papers.ssrn.com/sol3/results.cfm?txtKey_Words=currency+carry+momentum", r"papers\.ssrn\.com/sol3/papers\.cfm\?abstract_id=\d+", 6),
 ("ssrn2","https://papers.ssrn.com/sol3/results.cfm?txtKey_Words=FX+anomaly", r"papers\.ssrn\.com/sol3/papers\.cfm\?abstract_id=\d+", 4),
 ("babypips_forum","https://forums.babypips.com/c/trading-systems/", r"forums\.babypips\.com/t/[a-z0-9-]+/\d+", 3),
 ("arabictrader","https://www.arabictrader.com/ar/forum", r"arabictrader\.com/.*/(thread|topic|forum)/", 3),
 ("forex_nawigator","https://www.forex-nawigator.biz/forum/", r"forex-nawigator\.biz/forum/.+\.html?$", 3),
 ("quant_stackexchange","https://quant.stackexchange.com/questions/tagged/fx", r"quant\.stackexchange\.com/questions/\d+/", 3),
 ("tutim_fxmacrodata","https://www.fxmacrodata.com/rss.xml", None, 0),
 ("gestaltu","https://gestaltu.com/", r"gestaltu\.com/20\d\d/", 3),
]
CHAN = re.compile(r"just a moment|attention required|verify you are human|captcha|access denied", re.I)
def txt(pg, n):
    try: return re.sub(r"\s+"," ", pg.inner_text("body"))[:n]
    except Exception as e: return ""
out = []
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9224"); ctx = b.contexts[0]; pg = ctx.new_page()
    for ma, url, pat, n in NGUON:
        r = dict(ma=ma, url=url, trang_thai=None, muc=[])
        try:
            resp = pg.goto(url, wait_until="domcontentloaded", timeout=45000); time.sleep(5)
            st = resp.status if resp else None; body = txt(pg, 3000)
            r["http"] = st; r["tieu_de"] = pg.title()
            if (st and st >= 400) or CHAN.search(body[:1500] + r["tieu_de"]):
                r["trang_thai"] = "BI_CHAN"; r["trich"] = body[:300]; out.append(r); print(ma, r["trang_thai"], st, flush=True); continue
            if pat is None:
                r["trang_thai"] = "DOC_DUOC"; r["trich"] = body[:2500]; out.append(r); print(ma, "ok rss", flush=True); continue
            hrefs = pg.eval_on_selector_all("a[href]", "els=>els.map(e=>[e.href,(e.innerText||'').trim()])")
            seen = []; 
            for h, t in hrefs:
                h = h.split("#")[0]
                if re.search(pat, h) and h not in [s[0] for s in seen]: seen.append((h, t[:150]))
            for h, t in seen[:n]:
                time.sleep(random.uniform(4, 7))
                try:
                    rr = pg.goto(h, wait_until="domcontentloaded", timeout=45000); time.sleep(3)
                    bt = txt(pg, 3500)
                    if CHAN.search(bt[:1500]): r["muc"].append(dict(url=h, chan=True)); break
                    r["muc"].append(dict(url=h, ten=pg.title(), the_a=t, noi_dung=bt))
                except Exception as e: r["muc"].append(dict(url=h, loi=str(e)[:120]))
            r["trang_thai"] = "DOC_DUOC" if r["muc"] else "KHONG_THAY_MUC"; r["so_link"] = len(seen)
        except Exception as e:
            r["trang_thai"] = "LOI"; r["loi"] = str(e)[:200]
        out.append(r); print(ma, r["trang_thai"], len(r["muc"]), flush=True)
        json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        time.sleep(random.uniform(5, 9))
    pg.close()
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1); print("XONG", flush=True)
