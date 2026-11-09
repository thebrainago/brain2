"""mql5.py - lay thong ke cong khai trang signal MQL5 (khong can dang nhap).
Lich su lenh (/export/history, tab Trading history) BAT BUOC dang nhap -> khong ho tro tu dong (xem README).
requests thuong, nhip 4 s, dung ngay khi bi chan (403/429).
Chay: python mql5.py --ids-file mql5_dot2_ids.txt   -> out/mql5/stats.csv + out/mql5/{id}.json"""
import sys, os, re, json, csv, argparse, time
from bs4 import BeautifulSoup
from net import Net, SiteBan

def num(s):
    s = (s or "").replace("\u00a0", " ").replace(" ", "")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group(0)) if m else None

def parse(html_text, sid):
    s = BeautifulSoup(html_text, "html.parser")
    d = {"id": sid}
    t = s.find("title"); d["title"] = t.get_text(strip=True) if t else ""
    for it in s.select(".s-data-columns__item"):
        l = it.select_one(".s-data-columns__label"); v = it.select_one(".s-data-columns__value")
        if l and v:
            d[l.get_text(strip=True).rstrip(":")] = v.get_text(" ", strip=True)
    # cac o thong tin dau trang (Growth, Subscribers, Weeks, Leverage, broker...)
    for it in s.select(".s-list-info__item, .s-indicators__item, .s-plus-info__item"):
        l = it.select_one("[class*=label]"); v = it.select_one("[class*=value]")
        if l and v: d[l.get_text(strip=True).rstrip(":")] = v.get_text(" ", strip=True)
    g = s.select_one(".s-indicators__item-desc, .s-data-columns__value--growth")
    gm = re.search(r'Growth[^<]{0,40}</[^>]+>\s*<[^>]+>\s*([-+]?[\d\s.]+%)', html_text)
    if gm: d["growth_header"] = gm.group(1).replace(" ", "")
    # du lieu thang (bang tang truong theo nam) neu co
    yrs = {}
    for tr in s.select("table.signals-growth-table tr, .signals-chart-growth__table tr"):
        cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
        if cells and re.fullmatch(r"\d{4}", cells[0]): yrs[cells[0]] = cells[1:]
    if yrs: d["monthly_table"] = yrs
    d["need_login_for_history"] = "need-auth" in html_text
    # chi so suy ra cho cong phi: pips trung binh moi lenh
    gp = re.search(r"\(\s*([\d\s]+)\s*pips\)", d.get("Gross Profit", "")); gl = re.search(r"\(\s*([\d\s]+)\s*pips\)", d.get("Gross Loss", ""))
    tr_ = num(d.get("Trades", ""))
    if gp and gl and tr_:
        d["avg_points_per_trade"] = round((num(gp.group(1)) - num(gl.group(1))) / tr_, 2)
    return d

KEYS = ["id", "title", "Trades", "Profit Trades", "Profit Factor", "Expected Payoff", "Gross Profit", "Gross Loss",
        "avg_points_per_trade", "Sharpe Ratio", "Recovery Factor", "Monthly growth", "Annual Forecast", "By Balance",
        "By Equity", "Max deposit load", "Avg holding time", "Trades per week", "Algo trading", "Latest trade", "need_login_for_history"]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*"); ap.add_argument("--ids-file"); ap.add_argument("--gap", type=float, default=4)
    ap.add_argument("--out", default="out/mql5")
    a = ap.parse_args()
    ids = a.ids + ([l.strip() for l in open(a.ids_file) if l.strip()] if a.ids_file else [])
    os.makedirs(a.out, exist_ok=True)
    n = Net(min_gap=a.gap)
    rows = []
    for sid in ids:
        try:
            r = n.get(f"https://www.mql5.com/en/signals/{sid}")
            if r.status_code != 200:
                print(sid, "HTTP", r.status_code, flush=True); rows.append({"id": sid, "title": f"HTTP {r.status_code}"}); continue
            d = parse(r.text, sid)
            json.dump(d, open(os.path.join(a.out, f"{sid}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            rows.append(d); print(sid, d.get("Trades"), d.get("Profit Factor"), d.get("avg_points_per_trade"), d["title"][:60], flush=True)
        except SiteBan as e:
            print("DUNG:", e, flush=True); break
        except Exception as e:
            print(sid, "loi", e, flush=True); rows.append({"id": sid, "title": f"loi {e}"})
    with open(os.path.join(a.out, "stats.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=KEYS, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    print("xong", len(rows), n.stats)
