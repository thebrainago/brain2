# -*- coding: utf-8 -*-
"""Cham ket qua MT5 lo khang_dinh theo tieu chi DA SUA (Evo 15/11/2026).
Vao: ket_qua_lo.json (optimization, 216 co che) + ket_qua_don.json (chay don cho nhom qua so bo).
Tieu chi: >=30 lenh, PF theo lenh >=1.2, Sharpe nam hoa theo lenh >=0.3, TB lenh >0  (MT5 2016->11/2026,
M15 open prices, XM demo, lot 0.1 co dinh). KHONG co placebo/p o day: day la pha 3 (MT5), khong phai pass that.
--ghi-db: dat khang_dinh.trang_thai='DA_KIEM_MT5' cho cac dong da chay (backup truoc)."""
import json, os, shutil, sqlite3, sys, time
D = os.path.dirname(os.path.abspath(__file__))
lo = json.load(open(os.path.join(D, "ket_qua_lo.json")))
don = {(r["ea"], r["i"]): r for r in json.load(open(os.path.join(D, "ket_qua_don.json")))}
moc = {}
for g in lo:
    for k in g.get("ket", []):
        if k["kd"] is None: moc.setdefault(g["ea"], {})[k["ten"]] = k
ra = []
for g in lo:
    for k in g.get("ket", []):
        if k["kd"] is None: continue
        d = don.get((g["ea"], k["i"]), {})
        r = {"kd": k["kd"], "template": k["template"], "ten": k["ten"], "symbol": g["symbol"], "khung": g["khung"],
             "lenh": k["lenh"], "pf_opt": round(k["pf"], 3), "tb_usd": round(k["ky_vong"], 2), "dd_pct": round(k["dd_pct"], 2),
             "sharpe_mt5_goc": round(k["sharpe_mt5"], 3)}
        for f in ("pf_lenh", "sharpe_nam", "pct_nam_von10k", "top10_pct_lai", "nam_duong", "nam"):
            if f in d: r[f] = d[f]
        m = moc.get(g["ea"], {})
        r["mua_giu_pf"] = round(m.get("__mua_giu__", {}).get("pf", 0), 3)
        sb = r["lenh"] >= 30 and r["pf_opt"] >= 1.2 and r["tb_usd"] > 0
        r["qua_so_bo"] = sb
        r["dat_4_tieu_chi"] = bool(sb and d and (d.get("lenh", 0) >= 30) and (d.get("pf_lenh") or 0) >= 1.2
                                   and (d.get("sharpe_nam") or 0) >= 0.3 and (d.get("tb_lenh_usd") or 0) > 0)
        r["vuong"] = ("0 lenh" if r["lenh"] == 0 else "<30 lenh" if r["lenh"] < 30 else "PF<1.2" if r["pf_opt"] < 1.2
                      else "TB<=0" if r["tb_usd"] <= 0 else ("chua chay don" if not d else
                      "Sharpe<0.3" if (d.get("sharpe_nam") or 0) < 0.3 else "" if r["dat_4_tieu_chi"] else "khac"))
        ra.append(r)
json.dump(ra, open(os.path.join(D, "ket_qua_mt5.json"), "w"), ensure_ascii=False, indent=1)
import collections
print("chay", len(ra), "qua so bo", sum(r["qua_so_bo"] for r in ra), "dat 4 tieu chi", sum(r["dat_4_tieu_chi"] for r in ra))
print(collections.Counter(r["vuong"] for r in ra))
top = sorted([r for r in ra if r["dat_4_tieu_chi"]], key=lambda r: -(r.get("sharpe_nam") or 0))
for r in top[:12]:
    print(r["symbol"], r["khung"], r["template"][:55], r["lenh"], r.get("pf_lenh"), r.get("sharpe_nam"), r.get("pct_nam_von10k"), r.get("top10_pct_lai"), r.get("nam_duong"), r["dd_pct"])
if "--ghi-db" in sys.argv:
    db = os.environ.get("NAO_DB", "/workspace/brain2/nao.db")
    bk = db + ".bak_evo_mt5_" + time.strftime("%Y%m%d%H%M")
    shutil.copy2(db, bk)
    c = sqlite3.connect(db)
    n = c.executemany("UPDATE khang_dinh SET trang_thai='DA_KIEM_MT5' WHERE id=? AND trang_thai='CHO_KIEM'",
                      [(r["kd"],) for r in ra]).rowcount
    c.commit(); print("ghi db", n, "dong; backup", bk)
