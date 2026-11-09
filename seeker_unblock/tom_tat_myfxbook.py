"""tom_tat_myfxbook.py DIR -> DIR/tom_tat.csv: moi he 1 dong (so lenh, lenh/nam, pips TB, win%, ma chinh, giu lenh TB)."""
import sys, csv, json, glob, os, statistics as st, collections, re
d = sys.argv[1]; out = []
def dur_h(s):
    h = 0
    for v, u in re.findall(r"(\d+)\s*([dhm])", s or ""): h += int(v) * {"d": 24, "h": 1, "m": 1/60}[u]
    return h
for f in sorted(glob.glob(os.path.join(d, "*_meta.json"))):
    m = json.load(open(f)); oid = m["oid"]; c = os.path.join(d, f"{oid}.csv")
    row = {"oid": oid, "ten": m.get("title", "")[:70], "trang_thai": m.get("status"), "start": m.get("start", ""), "tong_dong": m.get("total_reported")}
    if os.path.exists(c):
        R = [r for r in csv.DictReader(open(c, encoding="utf-8")) if r["symbol"] and r["action"] in ("Buy", "Sell")]
        if R:
            pips = [float(r["pips"].replace(",", "")) for r in R if r["pips"] not in ("", "-")]
            ts = [int(r["close_time_ms"]) for r in R if r["close_time_ms"]]
            yrs = max((max(ts) - min(ts)) / 3.156e10, 0.05)
            sy = collections.Counter(r["symbol"] for r in R)
            row.update({"so_lenh_lay": len(R), "lenh_nam": round(len(R) / yrs, 1), "tu": min(ts) and __import__("datetime").datetime.utcfromtimestamp(min(ts)/1000).date().isoformat(),
                        "pips_tb": round(st.mean(pips), 2) if pips else "", "win_pct": round(100 * sum(p > 0 for p in pips) / len(pips), 1) if pips else "",
                        "lai_usd": round(sum(float((r["profit"] or "0").replace(",", "")) for r in R), 2), "giu_tb_gio": round(st.mean(dur_h(r["duration"]) for r in R), 1),
                        "ma_chinh": ";".join(f"{k}:{v}" for k, v in sy.most_common(3))})
    out.append(row)
keys = ["oid", "ten", "trang_thai", "start", "tong_dong", "so_lenh_lay", "tu", "lenh_nam", "pips_tb", "win_pct", "lai_usd", "giu_tb_gio", "ma_chinh"]
with open(os.path.join(d, "tom_tat.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore"); w.writeheader(); w.writerows(out)
print(len(out), "he;", sum(1 for r in out if r.get("so_lenh_lay")), "co lenh")
