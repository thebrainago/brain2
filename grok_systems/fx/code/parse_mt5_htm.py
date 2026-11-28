#!/usr/bin/env python3
"""Parse an MT5 Strategy Tester HTML report: net/DD, baskets, worst day."""
from __future__ import annotations
import json, re, sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

def decode(raw: bytes) -> str:
    if raw[:2] == b"\xff\xfe":
        return raw.decode("utf-16-le")
    if raw[:2] == b"\xfe\xff":
        return raw.decode("utf-16-be")
    if len(raw) > 3 and raw[1:2] == b"\x00" and raw[0:1] != b"\x00":
        return raw.decode("utf-16-le")
    if raw[:3] == b"\xef\xbb\xbf":
        return raw.decode("utf-8-sig")
    return raw.decode("utf-8", "ignore")

def num(s):
    if s is None:
        return None
    s = str(s).replace("\xa0", " ").replace(" ", "").replace(",", "").strip()
    if s in ("", "-"):
        return None
    try:
        return float(s)
    except ValueError:
        return None

class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.convert_charrefs = True
        self.tables = []
        self.cur = None
        self.row = None
        self.cell = None
        self.in_td = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "table":
            self.cur = []
            self.tables.append(self.cur)
        elif tag == "tr" and self.cur is not None:
            self.row = []
            self.cur.append(self.row)
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []
            self.in_td = True
            self.row.append(self.cell)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in ("td", "th"):
            self.in_td = False
        if tag == "tr" and self.row is not None:
            for i, c in enumerate(self.row):
                if isinstance(c, list):
                    self.row[i] = re.sub(r"\s+", " ", " ".join(c)).strip()

    def handle_data(self, data):
        if self.in_td and self.cell is not None:
            self.cell.append(data)

def parse(path: str | Path) -> dict:
    raw = Path(path).read_bytes()
    t = decode(raw)
    p = Tables()
    p.feed(t)
    text = re.sub(r"<[^>]+>", " ", t)
    text = re.sub(r"\s+", " ", text)

    def grab(label, pat=r"(-?[\d ]+\.\d+)"):
        m = re.search(re.escape(label) + r"\s*" + pat, text)
        return num(m.group(1)) if m else None

    out = {
        "file": str(path),
        "net": grab("Total Net Profit:"),
        "pf": grab("Profit Factor:"),
        "trades": None,
        "deals_n": None,
        "quality": None,
        "eq_dd_abs": None,
        "eq_dd_pct": None,
        "bal_dd_abs": None,
        "bal_dd_pct": None,
        "largest_loss_trade": grab("Largest loss trade:"),
        "largest_profit_trade": grab("Largest profit trade:"),
        "max_consec_loss": None,
        "max_consec_loss_n": None,
    }
    m = re.search(r"Total Trades:\s*(\d+)", text)
    if m:
        out["trades"] = int(m.group(1))
    m = re.search(r"Total Deals:\s*(\d+)", text)
    if m:
        out["deals_n"] = int(m.group(1))
    m = re.search(r"History Quality:\s*([^B]+?)\s*Bars", text)
    if m:
        out["quality"] = m.group(1).strip()
    m = re.search(r"Equity Drawdown Maximal:\s*(-?[\d ]+\.\d+)\s*\(([\d.]+)%\)", text)
    if m:
        out["eq_dd_abs"] = num(m.group(1))
        out["eq_dd_pct"] = float(m.group(2))
    m = re.search(r"Balance Drawdown Maximal:\s*(-?[\d ]+\.\d+)\s*\(([\d.]+)%\)", text)
    if m:
        out["bal_dd_abs"] = num(m.group(1))
        out["bal_dd_pct"] = float(m.group(2))
    m = re.search(r"Maximal consecutive loss \(count\):\s*(-?[\d ]+\.\d+)\s*\((\d+)\)", text)
    if m:
        out["max_consec_loss"] = num(m.group(1))
        out["max_consec_loss_n"] = int(m.group(2))

    deals = []
    for tb in p.tables:
        start = None
        for i, row in enumerate(tb):
            if row and row[0] == "Deals" and i + 1 < len(tb) and tb[i + 1] and "Time" in tb[i + 1][0]:
                start = i + 2
                break
        if start is None:
            continue
        for row in tb[start:]:
            if not row or not row[0]:
                continue
            if not re.match(r"\d{4}\.\d{2}\.\d{2}", row[0]):
                break
            if len(row) < 11:
                continue
            typ = row[3].lower() if len(row) > 3 else ""
            if typ in ("balance", "credit", "charge"):
                continue
            deals.append({
                "time": row[0],
                "deal": row[1],
                "symbol": row[2],
                "type": typ,
                "dir": row[4].lower() if len(row) > 4 else "",
                "volume": num(row[5]) or 0.0,
                "price": num(row[6]) or 0.0,
                "comm": num(row[8]) or 0.0,
                "swap": num(row[9]) or 0.0,
                "profit": num(row[10]) or 0.0,
                "comment": row[12] if len(row) > 12 else "",
            })
        if deals:
            break

    baskets = []
    cur = None
    pos = 0.0
    for d in deals:
        if cur is None:
            cur = {"start": d["time"], "pnl": 0.0, "swap": 0.0, "comm": 0.0, "legs": 0, "side": d["type"], "comments": []}
        cur["pnl"] += d["profit"]
        cur["swap"] += d["swap"]
        cur["comm"] += d["comm"]
        if d["dir"] == "in":
            cur["legs"] += 1
            pos += d["volume"]
            if d["comment"]:
                cur["comments"].append(d["comment"])
        elif d["dir"] == "out":
            pos -= d["volume"]
        if abs(pos) < 1e-9 and cur is not None:
            cur["end"] = d["time"]
            cur["net"] = cur["pnl"] + cur["swap"] + cur["comm"]
            baskets.append(cur)
            cur = None
            pos = 0.0
    if cur is not None:
        cur["end"] = deals[-1]["time"] if deals else ""
        cur["net"] = cur["pnl"] + cur["swap"] + cur["comm"]
        baskets.append(cur)

    pnls = [b["net"] for b in baskets]
    daily = defaultdict(float)
    for d in deals:
        daily[d["time"][:10]] += d["profit"] + d["swap"] + d["comm"]
    out["n_baskets"] = len(baskets)
    out["n_wins"] = sum(1 for x in pnls if x > 0)
    out["n_loss"] = sum(1 for x in pnls if x < 0)
    out["basket_net_sum"] = round(sum(pnls), 2) if pnls else 0.0
    out["max_basket_loss"] = round(min(pnls), 2) if pnls else None
    out["max_basket_gain"] = round(max(pnls), 2) if pnls else None
    if pnls:
        w = min(baskets, key=lambda b: b["net"])
        out["worst_basket"] = {"start": w["start"], "end": w["end"], "net": round(w["net"], 2), "legs": w["legs"], "swap": round(w["swap"], 2), "side": w["side"]}
    else:
        out["worst_basket"] = None
    if daily:
        wd = min(daily.items(), key=lambda kv: kv[1])
        bd = max(daily.items(), key=lambda kv: kv[1])
        out["worst_day"] = {"date": wd[0], "pnl": round(wd[1], 2)}
        out["best_day"] = {"date": bd[0], "pnl": round(bd[1], 2)}
        out["n_days"] = len(daily)
    else:
        out["worst_day"] = out["best_day"] = None
        out["n_days"] = 0
    return out

if __name__ == "__main__":
    for a in sys.argv[1:]:
        print(json.dumps(parse(a), ensure_ascii=False, indent=2))
