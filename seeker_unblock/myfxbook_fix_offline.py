"""myfxbook_fix_offline.py CSV "c1,c2,..." - sua cot CSV ban cu khi biet thu tu cot (suy ra tu du lieu) ma khong goi mang.
Dung khi IP dang bi Myfxbook gioi han. Ghi lai meta: cols, sua_cot=offline."""
import sys, csv, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from myfxbook import OLD
import myfxbook as M
fn, cols = sys.argv[1], [c or None for c in sys.argv[2].split(",")]
rows = list(csv.DictReader(open(fn, encoding="utf-8"))); out = []
for r in rows:
    vals = [r.get(k, "") for k in OLD]
    x = {k: "" for k in M.COLS}; x.update(record=r["record"], open_time_ms=r["open_time_ms"], close_time_ms=r["close_time_ms"])
    if not any(v in ("Buy", "Sell") for v in vals):
        x["action"] = next((v for v in vals if v in ("Deposit", "Withdrawal", "Credit")), "")
        nums = [v for v in vals if v.replace(",", "").replace(".", "").replace("-", "").isdigit() and "." in v]
        x["profit"] = nums[-1].replace(",", "") if nums else ""
    else:
        for k, v in zip(cols, vals):
            if k: x[k] = v.replace(",", "") if k in ("profit", "pips") else v.replace("- - -", "").strip()
    out.append(x)
with open(fn, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=M.COLS); w.writeheader(); w.writerows(out)
mp = fn[:-4] + "_meta.json"; m = json.load(open(mp)); m.update(cols=cols, sua_cot="offline", trades=sum(1 for x in out if x["action"] in ("Buy", "Sell")))
json.dump(m, open(mp, "w"), ensure_ascii=False, indent=1)
tr = [x for x in out if x["action"] in ("Buy", "Sell")]
agree = sum(1 for x in tr if x["pips"] and x["profit"] and (float(x["pips"]) > 0) == (float(x["profit"]) > 0))
print(fn, "lenh", len(tr), "dau pips==dau lai:", agree, "/", len(tr)); print(tr[0])
