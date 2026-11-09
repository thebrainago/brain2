"""myfxbook.py - PARSER OFFLINE cho bang History cua Myfxbook (HTML da luu san).
Lenh tai truc tuyen (goi XHR systemPageGetHistoryFirstPage.json / paging.html) DA VO HIEU HOA 10/11/2026:
day la endpoint noi bo khong co tai lieu; Myfxbook dang chan IP nha (Cloudflare 1015). Nguon hop le:
CSV export chinh thuc cua chu tai khoan / nut Export tren trang, hoac Myfxbook API chinh thuc (can tai khoan).
Chay offline:
  python myfxbook.py parse-html FILE.html|FILE.json [--out out.csv]   (JSON = {"content":{"history":HTML}} da luu)
  python myfxbook.py fetch ...  -> thoat ma 2 kem giai thich."""
import sys, os, re, json, csv, argparse
from bs4 import BeautifulSoup

# thu tu 12 o ma ban parser cu (gan cot co dinh) da ghi vao CSV
OLD = ["open_broker", "close_broker", "symbol", "action", "sl_pips", "tp_pips", "open_price", "close_price", "pips", "profit", "duration", "gain_pct"]
COLS = ["record", "open_time_ms", "close_time_ms", "open_broker", "close_broker", "symbol", "action", "lots",
        "sl_pips", "tp_pips", "open_price", "close_price", "pips", "profit", "duration", "gain_pct"]
# ten class cua <th> trong bang History -> cot chuan. Bo cot thay doi theo tai khoan (co/khong Lots, SL, TP...)
TH_MAP = {"openDate": "open_broker", "closeDate": "close_broker", "symbol": "symbol", "action": "action",
          "sizing": "lots", "lots": "lots", "size": "lots", "volume": "lots", "sl": "sl_pips", "tp": "tp_pips",
          "openPrice": "open_price", "closePrice": "close_price", "pips": "pips", "profits": "profit", "profit": "profit",
          "durations": "duration", "duration": "duration", "change": "gain_pct"}

def head_cols(h):
    """Doc thu tu cot tu <th> (bo th rong dau tien). Tra ve list ten cot chuan (None = cot bo qua)."""
    s = BeautifulSoup(h, "html.parser")
    tr = s.find("tr")
    if not tr: return None
    ths = tr.find_all("th")[1:]
    out = []
    for th in ths:
        cl = (th.get("class") or [""])[0]
        name = TH_MAP.get(cl)
        if not name:
            t = th.get_text(" ", strip=True).lower()
            name = "lots" if t.startswith(("lots", "size", "volume")) else None
        out.append(name)
    return out

def parse_rows(h, cols=None):
    cols = cols or head_cols(h) or ["open_broker", "close_broker", "symbol", "action", "sl_pips", "tp_pips",
                                    "open_price", "close_price", "pips", "profit", "duration", "gain_pct"]
    s = BeautifulSoup(h, "html.parser")
    out = []
    for tr in s.select("tr[data-record]"):
        tds = [td for td in tr.find_all("td", recursive=False) if "display:none" not in (td.get("style") or "").replace(" ", "")]
        sym = tr.select_one("td.symbol")
        txt = [td.get_text(" ", strip=True) for td in tds][1:]
        d = {k: "" for k in COLS}
        d.update(record=tr.get("data-record"), open_time_ms=(sym.get("opentime") if sym else ""), close_time_ms=(sym.get("closetime") if sym else ""))
        if len(txt) < len(cols) - 3:  # dong nap/rut tien (colspan): open, ..., loai, ..., so tien
            d["open_broker"] = txt[0] if txt else ""
            kind = next((x for x in txt if x in ("Deposit", "Withdrawal", "Credit", "Balance")), "")
            d["action"] = kind
            num = [x for x in txt if re.fullmatch(r"-?[\d,]+\.\d+", x)]
            d["profit"] = num[-1].replace(",", "") if num else ""
        else:
            for k, v in zip(cols, txt):
                if k: d[k] = v.replace("- - -", "").strip()
            d["profit"] = d["profit"].replace(",", ""); d["pips"] = d["pips"].replace(",", "")
        out.append(d)
    return out

def load_history_html(path):
    t = open(path, encoding="utf-8", errors="ignore").read()
    if t.lstrip().startswith("{"):
        return json.loads(t)["content"]["history"]
    return t

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["parse-html", "fetch"]); ap.add_argument("args", nargs="*")
    ap.add_argument("--out")
    a, _ = ap.parse_known_args()
    if a.cmd == "fetch":
        print(__doc__); sys.exit(2)
    for p in a.args:
        h = load_history_html(p); cols = head_cols(h); rows = parse_rows(h, cols)
        out = a.out or os.path.splitext(p)[0] + "_parsed.csv"
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)
        print(p, "cot:", cols, "dong:", len(rows), "->", out)
