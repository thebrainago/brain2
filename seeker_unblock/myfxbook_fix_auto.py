"""myfxbook_fix_auto.py DIR - tu suy thu tu cot cho CSV ban cu (khong goi mang): thu cac mau cot,
chon mau co diem cao nhat (cot duration dung dinh dang + dau pips trung dau lai). Bo qua file da co 'cols'."""
import sys, os, re, csv, json, glob, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from myfxbook import OLD
T = {
 "A": "open_broker,close_broker,symbol,action,sl_pips,tp_pips,open_price,close_price,pips,profit,duration,gain_pct",
 "B": "open_broker,close_broker,symbol,action,lots,sl_pips,tp_pips,open_price,close_price,pips,profit,duration",
 "C": "close_broker,symbol,action,lots,open_price,close_price,pips,profit,duration,gain_pct",
 "D": "open_broker,close_broker,symbol,action,lots,open_price,close_price,pips,profit,duration,gain_pct",
 "E": "close_broker,symbol,action,sl_pips,tp_pips,open_price,close_price,pips,profit,duration,gain_pct",
 "F": "open_broker,close_broker,symbol,action,open_price,close_price,pips,profit,duration,gain_pct",
 "G": "close_broker,symbol,action,lots,sl_pips,tp_pips,open_price,close_price,pips,profit,duration,gain_pct",
 "H": "close_broker,symbol,action,open_price,close_price,pips,profit,duration,gain_pct",
}
DUR = re.compile(r"^(\d+[dhm]\s*)+$")
def f(v):
    try: return float(v.replace(",", ""))
    except Exception: return None
def score(rows, cols):
    c = cols.split(","); s = 0; n = 0
    for r in rows:
        vals = dict(zip(c, [r.get(k, "") for k in OLD]))
        if vals.get("action") not in ("Buy", "Sell"): s -= 1; continue
        n += 1
        if DUR.match(vals.get("duration", "")): s += 1
        p, q = f(vals.get("pips", "")), f(vals.get("profit", ""))
        if p is not None and q is not None and (p > 0) == (q > 0): s += 1
    return s / max(n, 1)
d = sys.argv[1]
for mp in sorted(glob.glob(os.path.join(d, "*_meta.json"))):
    m = json.load(open(mp)); fn = mp.replace("_meta.json", ".csv")
    if "cols" in m or not os.path.exists(fn): continue
    rows = [r for r in csv.DictReader(open(fn, encoding="utf-8")) if any(r.get(k) in ("Buy", "Sell") for k in OLD)][:300]
    if not rows: continue
    best = max(T, key=lambda k: score(rows, T[k])); sc = score(rows, T[best])
    print(os.path.basename(fn), "mau", best, f"diem {sc:.2f}", flush=True)
    if sc >= 1.6:
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "myfxbook_fix_offline.py"), fn, T[best]])
    else: print("  -> khong chac, bo qua")
