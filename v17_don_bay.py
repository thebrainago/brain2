# -*- coding: utf-8 -*-
"""Vong 17 (2): don bay mua-giu CFD + loc thoi diem. Dang ky truoc reports/vong17_tien_dang_ky.md. MO PHONG."""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

import mua_vu as MV
import v15
import v16

RNG = np.random.default_rng(17)
CHUOI = {"US500_1950": ("gspc_dai_yahoo.csv", 1e-4, "1950-01-01"), "US500_1990": ("gspc_dai_yahoo.csv", 1e-4, "1990-01-01"),
         "UK100_1990": ("ftse_ohlc_yahoo.csv", 1.5e-4, "1990-01-01")}


def tai(ten):
    f, sp, tu = CHUOI[ten]; g = v16.doc(f, tu)
    ngay = np.r_[1.0, np.diff(g.index.values).astype("timedelta64[D]").astype(float)]
    fin = (MV.lai_suat(g.index) + MV.MARKUP_QUA_DEM) * ngay / 365.0
    return g, g.pct_change().fillna(0).to_numpy(), fin, sp


def rong_hang_ngay(r, fin, e, sp, hs=1.0):
    e = np.asarray(e, float); doi = np.abs(np.diff(np.r_[0.0, e])) + np.abs(e * (e - 1) * r)   # them luot can bang lai
    return e * r - doi * (sp * hs / 2 + MV.TRUOT) - e * fin


def von(loi):
    eq = np.cumprod(1 + np.maximum(loi, -1.0))
    if (eq <= 0).any(): eq[np.argmax(eq <= 0):] = 0.0
    return eq


def co_dinh(r, fin, L, sp):
    E, N = 1.0, L; out = np.empty(len(r)); out[0] = E - L * (sp / 2 + MV.TRUOT)
    E = out[0]
    for i in range(1, len(r)):
        if E <= 0: out[i:] = 0; break
        E = E + N * r[i] - N * fin[i]; N = N * (1 + r[i]); out[i] = max(E, 0.0)
    return out


def tk(eq, idx):
    nam = (idx[-1] - idx[0]).days / 365.25; dd = float(np.max(1 - eq / np.maximum.accumulate(np.maximum(eq, 1e-12)))) * 100
    lr = np.diff(np.log(np.maximum(eq, 1e-12))); sd = lr.std()
    return {"cagr_pct": round(float((max(eq[-1], 0) ** (1 / nam) - 1) * 100), 2), "maxdd_pct": round(dd, 1),
            "sharpe": round(float(lr.mean() / sd * 252 ** .5) if sd > 0 else 0, 3), "chay": bool(eq[-1] <= 0)}


def bootstrap(r, fin, L, sp, n=2000, T=2520, b=20):
    ruin = dd80 = 0
    for _ in range(n):
        st = RNG.integers(0, len(r) - b, T // b); ii = (st[:, None] + np.arange(b)).ravel()
        eq = von(rong_hang_ngay(r[ii], fin[ii], np.full(len(ii), L), sp))
        ruin += eq[-1] <= 0; dd80 += np.max(1 - eq / np.maximum.accumulate(np.maximum(eq, 1e-12))) > 0.8
    return round(ruin / n * 100, 2), round(dd80 / n * 100, 2)


def loc(ten, kieu, L, g, r):
    c = g.to_numpy()
    if kieu == "MA200":
        ma = pd.Series(c).rolling(200).mean().to_numpy(); s = np.r_[0, (c[:-1] > ma[:-1]).astype(float)]; return L * s
    if kieu == "VOL15":
        v = pd.Series(r).rolling(20).std().to_numpy() * 252 ** .5
        return np.nan_to_num(np.r_[0, np.minimum(3.0, L * 0.15 / np.maximum(v[:-1], 1e-6))])
    if kieu == "MUA_KHI_GIAM":
        dinh = pd.Series(c).rolling(252, min_periods=1).max().to_numpy(); s = np.r_[1, np.where(c[:-1] >= 0.9 * dinh[:-1], 1.0, 2.0)]; return L * s
    raise KeyError(kieu)


def main(ra=None):
    out = {"mua_giu": [], "loc": []}
    for ten in CHUOI:
        g, r, fin, sp = tai(ten)
        gia_tham_chieu = tk(np.cumprod(1 + r), g.index)
        for L in (1, 1.5, 2, 3):
            hn = tk(von(rong_hang_ngay(r, fin, np.full(len(r), L), sp)), g.index)
            cd = tk(co_dinh(r, fin, L, sp), g.index)
            ru, d8 = bootstrap(r, fin, L, sp)
            o = {"chuoi": ten, "L": L, "hang_ngay": hn, "co_dinh": cd, "bootstrap_10nam_chay_pct": ru, "bootstrap_10nam_dd80_pct": d8, "chi_so_gia": gia_tham_chieu}
            out["mua_giu"].append(o); print(ten, L, "HN", hn, "CD", cd, "ruin", ru, "dd>80", d8)
        print(ten, "chi so gia (khong phi)", gia_tham_chieu)
    bh1 = {t["chuoi"]: t["hang_ngay"]["cagr_pct"] for t in out["mua_giu"] if t["L"] == 1}
    ps0 = json.load(open("reports/vong16.json"))
    for ten in ("US500_1950", "UK100_1990"):
        g, r, fin, sp = tai(ten)
        for kieu in ("MA200", "VOL15", "MUA_KHI_GIAM"):
            for L in (1, 2):
                e = loc(ten, kieu, L, g, r); L_ = rong_hang_ngay(r, fin, e, sp); s = tk(von(L_), g.index)
                cs = [(1.0, g, e, lambda e, hs, r=r, fin=fin, sp=sp: rong_hang_ngay(r, fin, e, sp, hs))]
                thuc = v15.chuoi(cs, 1.0).mean(); hv = np.array([v15.chuoi(cs, 1.0, int(k)).mean() for k in RNG.integers(252, len(r) - 252, 1000)])
                z = (thuc - hv.mean()) / hv.std(ddof=1)
                o = {"chuoi": ten, "loc": kieu, "L": L, **s, "phoi_nhiem_tb": round(float(np.mean(e)), 2), "z": float(z), "p": MV.p1(z),
                     "vuot_mua_giu_khop": v15.vuot(cs, 1.0), "vuot_mua_giu_khop_x1_5": v15.vuot(cs, 1.5), "vuot_30cuoi": v15.vuot(cs, 1.0, 0.7),
                     "hon_mua_giu_1x": s["cagr_pct"] > bh1[ten] and s["maxdd_pct"] < 80}
                out["loc"].append(o); print(ten, kieu, L, s, "pn", o["phoi_nhiem_tb"], "z %.2f" % z, "vuot %.2f 30c %.2f" % (o["vuot_mua_giu_khop"], o["vuot_30cuoi"]), "hon1x" if o["hon_mua_giu_1x"] else "")
    if ra: json.dump(out, open(ra, "w"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
