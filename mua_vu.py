# -*- coding: utf-8 -*-
"""Vong 10: 8 quy tac mua vu / chu ky tan suat thap tren du lieu NGAY dai. Dang ky truoc:
reports/vong10_tien_dang_ky_mua_vu.md (commit 1927af67). MO PHONG, khong phai tien that.

    python mua_vu.py [--ra reports/vong10_mua_vu.json]
Du lieu: Yahoo chart API (^GSPC tu 1950, GC=F tu 2000-08 - chuoi vang dai hon khong lay duoc mien phi
tren box: Stooq/FRED tra trang thu thach chong bot), ^IRX (T-bill 13 tuan) cho phi qua dem.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

DU = Path("/workspace/du_lieu_ngay")
SPREAD = {"SPX": 1.0e-4, "XAU": 2.0e-4}      # khu hoi, tra MOT lan (nua moi chieu)
TRUOT = 0.5e-4                               # moi chieu
MARKUP_QUA_DEM = 0.025
NAM_CONG_BO = {"CHU_KY_BAU_CU_NAM3": 1967, "HALLOWEEN": 2002, "DAU_CUOI_THANG": 1987, "SANTA": 1972,
               "VANG_TRUOC_TET": 2010, "SPX_10THANG": 2007, "VANG_10THANG": 2007, "SPX_3TUAN_GIAM": 2000}


def doc(ten: str, tu: str | None = None) -> pd.Series:
    s = pd.read_csv(DU / ten, index_col=0, parse_dates=True)["close"]
    return s[s.index >= tu] if tu else s


def lai_suat(idx: pd.DatetimeIndex) -> np.ndarray:
    irx = doc("irx_d1_yahoo.csv") / 100.0
    r = irx.reindex(idx, method="ffill").to_numpy()
    return np.where(np.isfinite(r), r, 0.04)


def _vi_tri_trong_thang(idx):
    s = pd.Series(np.arange(len(idx)), index=idx)
    g = s.groupby([idx.year, idx.month])
    return g.cumcount().to_numpy(), (g.cumcount(ascending=False)).to_numpy()


def phoi_nhiem(ten: str, gia: pd.Series) -> np.ndarray:
    idx = gia.index
    n = len(idx)
    if ten == "CHU_KY_BAU_CU_NAM3":
        return (idx.year % 4 == 3).astype(float)
    if ten == "HALLOWEEN":
        return np.isin(idx.month, [11, 12, 1, 2, 3, 4]).astype(float)
    if ten == "DAU_CUOI_THANG":
        dau, cuoi = _vi_tri_trong_thang(idx)
        return ((cuoi == 0) | (dau <= 2)).astype(float)
    if ten == "SANTA":
        dau, cuoi = _vi_tri_trong_thang(idx)
        return (((idx.month == 12) & (cuoi <= 4)) | ((idx.month == 1) & (dau <= 1))).astype(float)
    if ten == "VANG_TRUOC_TET":
        from lunardate import LunarDate
        e = np.zeros(n)
        for y in range(idx[0].year, idx[-1].year + 2):
            try:
                tet = pd.Timestamp(LunarDate(y, 1, 1).to_solar_date())
            except Exception:                       # noqa: BLE001
                continue
            k = np.searchsorted(idx.values, tet.to_datetime64()) - 1   # phien cuoi TRUOC Tet
            if k >= 0 and idx[k] < tet and k + 1 < n + 1:
                e[max(0, k - 19):k + 1] = 1.0
        return e
    if ten in ("SPX_10THANG", "VANG_10THANG"):
        m = gia.groupby([idx.year, idx.month]).tail(1)
        tin = (m > m.rolling(10).mean()).to_numpy()
        e = np.zeros(n)
        ym = idx.year * 12 + idx.month
        bang = {int(t.year * 12 + t.month + 1): bool(v) for t, v in zip(m.index, tin)}
        for i in range(n):
            e[i] = 1.0 if bang.get(int(ym[i]), False) else 0.0
        return e
    if ten == "SPX_3TUAN_GIAM":
        iso = idx.isocalendar()
        khoa = (iso.year.to_numpy() * 100 + iso.week.to_numpy())
        w = gia.groupby(khoa).tail(1)
        wk = pd.Series(khoa, index=idx).groupby(khoa).tail(1).to_numpy()
        giam = (w.diff() < 0).to_numpy()
        tin = giam & np.r_[False, giam[:-1]] & np.r_[False, False, giam[:-2]]
        sau = {}
        for j in range(len(wk) - 1):
            sau[int(wk[j + 1])] = bool(tin[j])
        return np.array([1.0 if sau.get(int(k), False) else 0.0 for k in khoa])
    raise KeyError(ten)


def chay(gia: pd.Series, e_ngay: np.ndarray, spread: float, he_so: float = 1.0) -> np.ndarray:
    """Loi rong moi ngay. e_ngay[t] = co giu trong ngay t (dong t-1 -> dong t), biet tu dong t-1."""
    r = gia.pct_change().fillna(0.0).to_numpy()
    e = e_ngay.astype(float)
    doi = np.abs(np.diff(np.r_[0.0, e]))
    ngay = np.r_[1.0, np.diff(gia.index.values).astype("timedelta64[D]").astype(float)]
    tb = lai_suat(gia.index)
    phi = doi * (spread * he_so / 2.0 + TRUOT) + e * (tb + MARKUP_QUA_DEM) * ngay / 365.0
    return e * r - phi


def do(loi: np.ndarray, idx) -> dict:
    eq = np.cumprod(1 + loi)
    dd = float(np.max(1 - eq / np.maximum.accumulate(eq))) * 100 if len(eq) else 0.0
    nam = (idx[-1] - idx[0]).days / 365.25
    sd = float(np.std(loi))
    sh = float(np.mean(loi) / sd * math.sqrt(252)) if sd > 0 else 0.0
    return {"loi_pct": round(float(eq[-1] - 1) * 100, 2), "cagr_pct": round((eq[-1] ** (1 / nam) - 1) * 100, 3),
            "maxdd_pct": round(dd, 2), "sharpe": round(sh, 3), "nam": round(nam, 2),
            "t": round(sh * math.sqrt(nam), 3)}


def p1(t):
    return 0.5 * math.erfc(t / math.sqrt(2))


def holm(ps):
    m = len(ps); od = sorted(range(m), key=lambda i: ps[i]); ra = [1.0] * m; c = 0.0
    for r, i in enumerate(od):
        c = max(c, min(1.0, (m - r) * ps[i])); ra[i] = c
    return ra


QUY_TAC = [("CHU_KY_BAU_CU_NAM3", "SPX"), ("HALLOWEEN", "SPX"), ("DAU_CUOI_THANG", "SPX"), ("SANTA", "SPX"),
           ("VANG_TRUOC_TET", "XAU"), ("SPX_10THANG", "SPX"), ("VANG_10THANG", "XAU"), ("SPX_3TUAN_GIAM", "SPX")]


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--ra"); a = ap.parse_args(argv)
    gia = {"SPX": doc("spx_d1_yahoo.csv", "1950-01-01"), "XAU": doc("xauusd_gcf_d1_yahoo.csv")}
    ra = []
    for ten, ts in QUY_TAC:
        g = gia[ts]; idx = g.index
        e = phoi_nhiem(ten, g)
        n = len(idx); c = int(n * 0.7)
        o = {"quy_tac": ten, "tai_san": ts, "tu": str(idx[0].date()), "den": str(idx[-1].date()),
             "ty_le_ngay_giu": round(float(e.mean()), 3),
             "so_lenh": int(np.sum(np.diff(np.r_[0.0, e]) > 0))}
        for hs in (1.0, 1.5):
            L = chay(g, e, SPREAD[ts], hs)
            k = f"x{hs:g}"
            o[k] = {"toan": do(L, idx), "nm": do(L[c:], idx[c:])}
            nb = NAM_CONG_BO[ten]
            m = np.asarray(idx.year >= nb)
            o[k]["truoc_cong_bo"] = do(L[~m], idx[~m]) if (~m).sum() > 250 else None
            o[k]["sau_cong_bo"] = do(L[m], idx[m]) if m.sum() > 250 else None
        mh = chay(g, np.ones(n), SPREAD[ts])
        o["mua_giu"] = {"toan": do(mh, idx), "nm": do(mh[c:], idx[c:])}
        r = g.pct_change().fillna(0).to_numpy()
        tr, ng = r[e > 0], r[e == 0]
        se = math.sqrt(tr.var() / max(1, len(tr)) + ng.var() / max(1, len(ng)))
        o["welch_t_trong_ngoai"] = round(float((tr.mean() - ng.mean()) / se), 3) if se > 0 else None
        o["p"] = p1(o["x1"]["toan"]["t"])
        ra.append(o)
    for o, q in zip(ra, holm([o["p"] for o in ra])):
        o["p_holm"] = q
        x1, x15 = o["x1"], o["x1.5"]
        tc = {"lai_toan": x1["toan"]["loi_pct"] > 0, "dd_lt_80": x1["toan"]["maxdd_pct"] < 80,
              "nm_lai_x1": x1["nm"]["loi_pct"] > 0, "nm_lai_x1_5": x15["nm"]["loi_pct"] > 0,
              "sau_cong_bo_sharpe_gt0": bool(x1["sau_cong_bo"] and x1["sau_cong_bo"]["sharpe"] > 0),
              "p_holm_lt_005": q < 0.05}
        o["tieu_chi"] = tc; o["song"] = all(tc.values())
    out = {"nhan": "MO PHONG", "quy_tac": ra}
    for o in ra:
        print(o["quy_tac"], o["tai_san"], "giu", o["ty_le_ngay_giu"], "lenh", o["so_lenh"], "| x1", o["x1"]["toan"],
              "NM", o["x1"]["nm"]["loi_pct"], "x1.5 NM", o["x1.5"]["nm"]["loi_pct"],
              "| sau CB sh", (o["x1"]["sau_cong_bo"] or {}).get("sharpe"), "truoc", (o["x1"]["truoc_cong_bo"] or {}).get("sharpe"),
              "| p %.4f holm %.4f welch %s" % (o["p"], o["p_holm"], o["welch_t_trong_ngoai"]), "SONG" if o["song"] else "-",
              "| MH", o["mua_giu"]["toan"]["cagr_pct"], o["mua_giu"]["toan"]["maxdd_pct"])
    if a.ra:
        json.dump(out, open(a.ra, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
