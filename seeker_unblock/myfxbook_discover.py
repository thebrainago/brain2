"""myfxbook_discover.py - quet danh sach https://www.myfxbook.com/systems/N (trang cong khai, requests thuong, nhip 5 s, DUNG NGAY khi bi chan; bo loc mac dinh cua Myfxbook:
tai khoan that, DD<=50%, giao dich trong 90 ngay) -> out/myfxbook/systems_list.csv (oid, ten, gain, dd, monthly, yearly).
Chay: python myfxbook_discover.py [--pages 40]"""
import re, csv, os, argparse
from bs4 import BeautifulSoup
from net import Net, SiteBan

def pct(s):
    m = re.search(r"[-+]?[\d,]+(?:\.\d+)?", s or ""); return float(m.group(0).replace(",", "")) if m else None

def parse(t):
    s = BeautifulSoup(t, "html.parser"); out = []
    for r in s.find_all("tr"):
        a = [x["href"] for x in r.find_all("a", href=True) if "/members/" in x["href"]]
        if not a: continue
        tds = [td.get_text(" ", strip=True) for td in r.find_all("td")]
        txt = r.get_text(" | ", strip=True)
        if txt.startswith(("FXiBot | AD",)) or " | AD | " in txt[:40]: continue  # quang cao
        m = re.search(r"/members/([^/]+)/([^/]+)/(\d+)", a[0])
        ps = [x for x in tds if re.fullmatch(r"[-+]?[\d,]+(?:\.\d+)?%", x)]
        out.append({"oid": m.group(3), "user": m.group(1), "slug": m.group(2), "name": tds[1] if len(tds) > 1 else "",
                    "gain_pct": pct(ps[0]) if len(ps) > 0 else None, "dd_pct": pct(ps[1]) if len(ps) > 1 else None,
                    "monthly_pct": pct(ps[2]) if len(ps) > 2 else None, "yearly_pct": pct(ps[3]) if len(ps) > 3 else None,
                    "url": a[0]})
    total = re.search(r"[?&]ts=(\d+)", t)
    return out, int(total.group(1)) if total else None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pages", type=int, default=0); ap.add_argument("--out", default="out/myfxbook")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    n = Net(min_gap=5); rows, seen = [], set()
    first, total = parse(n.get("https://www.myfxbook.com/systems").text)
    pages = a.pages or ((total or 15) + 14) // 15
    print("tong he:", total, "trang:", pages, flush=True)
    for p in range(1, pages + 1):
        got = first if p == 1 else parse(n.get(f"https://www.myfxbook.com/systems/{p}").text)[0]
        for x in got:
            if x["oid"] not in seen: seen.add(x["oid"]); rows.append(x)
        if p % 5 == 0: print(f"  trang {p}/{pages}: {len(rows)} he", flush=True)
    with open(os.path.join(a.out, "systems_list.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("xong", len(rows), n.stats)

if __name__ == "__main__":
    try: main()
    except SiteBan as e: print("DUNG (trang chan, khong thu lai):", e); raise SystemExit(3)
