# -*- coding: utf-8 -*-
"""Vong 13: IBS < 0,2 tren 5 tai san khac. Dang ky truoc reports/vong13_tien_dang_ky.md. MO PHONG."""
from __future__ import annotations

import json
import sys

import numpy as np

import mua_vu as MV
import v12 as V12

TS = {"gdaxi": 1.0e-4, "n225": 2.6e-4, "ftse": 1.5e-4, "hsi": 3.0e-4, "gcf": 2.0e-4}


def main(ra=None):
    out = []
    for t, sp in TS.items():
        o = {"tai_san": t}
        for hs in (1.0, 1.5):
            L = V12.ibs_mot(t, sp, hs); v, idx = L.to_numpy(), L.index; c = int(len(v) * 0.7); m = np.asarray(idx.year >= 2010)
            o[f"x{hs:g}"] = {"toan": MV.do(v, idx), "nm": MV.do(v[c:], idx[c:]), "sau_2010": MV.do(v[m], idx[m])}
        o.update(tu=str(idx[0].date()), p=MV.p1(o["x1"]["toan"]["t"]))
        out.append(o)
    cu = json.load(open("reports/vong12.json"))["p_holm_29"]
    v12 = json.load(open("reports/vong12.json"))["quy_tac"]
    # p tho cua 29 quy tac cu: lay lai tu cac bao cao goc
    v10 = json.load(open("reports/vong10_mua_vu.json"))["quy_tac"]; v11 = json.load(open("reports/vong11_fx_vi_mo.json"))["quy_tac"]
    b = json.load(open("reports/vong11b.json"))
    ps = [x["p"] for x in v11] + [x["p"] for x in v10] + [b["vang_m30"][k]["x1"]["p"] for k in ("vn", "server", "gmt")] + \
        [b["ibs"]["p"]] + [x["p"] for x in v12]
    names = list(cu)
    ph = MV.holm(ps + [o["p"] for o in out])
    for o, q in zip(out, ph[len(ps):]):
        x1, x15 = o["x1"], o["x1.5"]
        tc = {"lai_toan": x1["toan"]["loi_pct"] > 0, "dd_lt_80": x1["toan"]["maxdd_pct"] < 80, "nm_x1": x1["nm"]["loi_pct"] > 0,
              "nm_x1_5": x15["nm"]["loi_pct"] > 0, "sau_2010": x1["sau_2010"]["sharpe"] > 0, "p_holm": q < 0.05}
        o["p_holm_34"] = q; o["tieu_chi"] = tc; o["song"] = all(tc.values())
        print("IBS", o["tai_san"], o["tu"], x1["toan"], "NM", x1["nm"]["loi_pct"], x15["nm"]["loi_pct"], "sau2010 sh", x1["sau_2010"]["sharpe"],
              "p %.4f holm %.4f" % (o["p"], q), "SONG" if o["song"] else "-")
    allp = dict(zip(names + ["IBS_" + o["tai_san"].upper() for o in out], ph))
    print({k: round(v, 4) for k, v in allp.items() if v < 0.06})
    if ra:
        json.dump({"nhan": "MO PHONG", "ho_holm": len(ph), "ibs_tai_san": out, "p_holm_34": allp}, open(ra, "w"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
