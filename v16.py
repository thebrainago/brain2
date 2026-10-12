# -*- coding: utf-8 -*-
"""Vong 16: kiem sau 2 he song (lap lai chi so khac, S&P truoc 1950, tong loi nhuan, suy giam theo thap ky). MO PHONG."""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

import mua_vu as MV
import v15

DU = "/workspace/du_lieu_ngay/"
QT4 = ("CHU_KY_BAU_CU_NAM3", "HALLOWEEN", "DAU_CUOI_THANG", "SANTA")


def doc(tep, tu=None, den=None):
    s = pd.read_csv(DU + tep, index_col=0, parse_dates=True)["close"].dropna(); s = s[s > 0]
    s = s[~s.index.duplicated(keep="last")]
    r = s.pct_change(); s = s[(r.abs() < 0.25) | r.isna()]
    if tu: s = s[s.index >= tu]
    if den: s = s[s.index < den]
    return s


def e_he(he, g):
    return np.mean([MV.phoi_nhiem(k, g) for k in QT4], axis=0) if he == "DANH_MUC_4" else np.asarray(MV.phoi_nhiem("DAU_CUOI_THANG", g), float)


O = [("dji", "dji_dai_yahoo.csv", 2e-4, None, None), ("rut", "rut_dai_yahoo.csv", 3e-4, None, None),
     ("gdaxi", "gdaxi_ohlc_yahoo.csv", 1e-4, "1990-01-01", None), ("ftse", "ftse_ohlc_yahoo.csv", 1.5e-4, "1990-01-01", None),
     ("n225", "n225_ohlc_yahoo.csv", 2.6e-4, "1990-01-01", None), ("hsi", "hsi_ohlc_yahoo.csv", 3e-4, "1990-01-01", None),
     ("spx_truoc_1950", "gspc_dai_yahoo.csv", 1e-4, None, "1950-01-01"), ("sp500tr", "sp500tr_dai_yahoo.csv", 1e-4, None, None)]


def cs(he, tep, sp, tu, den):
    g = doc(tep, tu, den)
    return [(1.0, g, e_he(he, g), lambda e, hs, g=g, sp=sp: MV.chay(g, e, sp, hs))]


def kiem(c):
    n = len(c[0][2]); thuc = v15.chuoi(c, 1.0).mean()
    hv = np.array([v15.chuoi(c, 1.0, int(k)).mean() for k in v15.RNG.integers(252, n - 252, v15.NHOAN)])
    z = (thuc - hv.mean()) / hv.std(ddof=1); L = v15.chuoi(c, 1.0)
    o = {"z": float(z), "p": MV.p1(z), "maxdd_pct": MV.do(L.to_numpy(), L.index)["maxdd_pct"], "cagr_pct": float(MV.do(L.to_numpy(), L.index)["cagr_pct"]),
         "tu": str(L.index[0].date())}
    for hs in (1.0, 1.5):
        o[f"vuot_toan_x{hs:g}"] = v15.vuot(c, hs); o[f"vuot_30cuoi_x{hs:g}"] = v15.vuot(c, hs, 0.7)
    return o


def thap_ky(he):
    g = doc("gspc_dai_yahoo.csv"); c = cs(he, "gspc_dai_yahoo.csv", 1e-4, None, None)
    L = v15.chuoi(c, 1.0); bh = v15.chuoi([(1.0, g, np.ones(len(g)), c[0][3])], 1.0); e = c[0][2]
    out = {}
    for d in range(1920, 2030, 10):
        m = np.asarray((g.index.year >= d) & (g.index.year < d + 10))
        if m.sum() < 200: continue
        out[f"{d}s"] = round(float((L[m].mean() - np.mean(e[m]) * bh[m].mean()) * 252 * 100), 2)
    return out


def main(ra=None):
    cu = json.load(open("reports/vong15.json")); v14j = json.load(open("reports/vong14.json"))
    import v14
    ps0 = v14.p_cu() + [x["p"] for x in v14j["o"]] + [x["p"] for x in cu["he"]] + [x["p"] for x in cu["cpi"]]
    res = []
    for he in ("DANH_MUC_4", "DAU_CUOI_THANG"):
        for ten, *a in O:
            o = kiem(cs(he, *a)); o.update(he=he, chi_so=ten); res.append(o)
    H = MV.holm(ps0 + [o["p"] for o in res])
    for o, h in zip(res, H[len(ps0):]):
        vu = all(o[k] > 0 for k in o if k.startswith("vuot_"))
        o["p_holm"] = h; o["lap_lai"] = o["p"] < 0.05 and o["vuot_toan_x1"] > 0; o["song"] = h < 0.05 and vu and o["maxdd_pct"] < 80
        print(o["he"], o["chi_so"], o["tu"], "z %.2f p %.4f holm %.3f" % (o["z"], o["p"], h), "cagr", o["cagr_pct"], "DD", o["maxdd_pct"],
              "vuot %.2f/%.2f 30c %.2f/%.2f" % (o["vuot_toan_x1"], o["vuot_toan_x1.5"], o["vuot_30cuoi_x1"], o["vuot_30cuoi_x1.5"]),
              "LAP_LAI" if o["lap_lai"] else "", "SONG" if o["song"] else "")
    tk = {he: thap_ky(he) for he in ("DANH_MUC_4", "DAU_CUOI_THANG")}; print(tk)
    if ra:
        json.dump({"nhan": "MO PHONG", "ho_holm": len(H), "o": res, "thap_ky_vuot_mua_giu_pct_nam": tk}, open(ra, "w"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
