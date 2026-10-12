"""Doc bao cao HTML Strategy Tester MT5 (v24) -> reports/mt5_v24/tong_hop.json. BACKTEST MT5, khong phai tien that."""
import re, html, json, glob, os, sys
import numpy as np
D = sys.argv[1] if len(sys.argv) > 1 else "reports/mt5_v24"
def num(x): return float(x.replace(" ", "").replace("\xa0", "").split("(")[0]) if x else None
o = []
for f in sorted(glob.glob(D + "/*.htm")):
    t = open(f, "rb").read().decode("utf-16")
    cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", t, re.S)]
    def g(k):
        try: return cells[cells.index(k) + 1]
        except ValueError: return None
    r = dict(file=os.path.basename(f), expert=g("Expert:"), symbol=g("Symbol:"), period=g("Period:"), quality=g("History Quality:"),
             bars=g("Bars:"), ticks=g("Ticks:"), net=num(g("Total Net Profit:")), pf=g("Profit Factor:"), trades=num(g("Total Trades:")),
             dd_bal=g("Balance Drawdown Maximal:"), dd_eq=g("Equity Drawdown Maximal:"), leverage=g("Leverage:"))
    i = t.find(">Deals<"); rows = re.findall(r"<tr[^>]*>(.*?)</tr>", t[i:], re.S); ins = {}; bps = []; first = last = None
    for row in rows:
        c = [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(c) < 13 or c[4] not in ("in", "out"): continue
        p = float(c[6]); first = first or c[0]; last = c[0]
        if c[4] == "in": ins = dict(s=1 if c[3] == "buy" else -1, p=p)
        elif ins: bps.append(ins["s"] * (p - ins["p"]) / ins["p"] * 1e4); ins = {}
    r.update(deal_dau=first, deal_cuoi=last, n_lenh_deal=len(bps), tb_bps=round(float(np.mean(bps)), 2) if bps else None)
    o.append(r)
json.dump(o, open(D + "/tong_hop.json", "w"), indent=1, ensure_ascii=False)
for r in o: print(r["file"], r["symbol"], r["period"], r["quality"], r["net"], r["trades"], r["pf"], r["dd_eq"], r["tb_bps"], r["deal_dau"])
