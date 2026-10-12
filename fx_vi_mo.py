# -*- coding: utf-8 -*-
"""Vong 11: (1) danh muc 4 quy tac S&P song (CFD US500); (2) 13 quy tac FX/hang hoa/vi mo.
Dang ky truoc: reports/vong11_tien_dang_ky.md (commit bc9c6100). Holm tren MOI quy tac da thu (ca 8 cua vong 10).
MO PHONG, khong phai tien that.

Du lieu (mien phi, ngoai repo /workspace/du_lieu_ngay): Yahoo chart API (EURUSD/USDJPY/AUDUSD/NZDUSD/AUDJPY,
Brent BZ=F, vang GC=F, ^GSPC, ^TNX, ^VIX, ^IRX); lai suat chinh sach BIS WS_CBPOL (AU, JP, US, khu vuc euro, tu 1999;
NZ KHONG co -> gia dinh r_NZD = r_USD); US 2y: US Treasury; Duc 2y: Bundesbank (Svensson).
"""
from __future__ import annotations

import argparse
import json
import math

import numpy as np
import pandas as pd

import mua_vu as MV

DU = MV.DU
TRUOT = 0.5e-4
SPREAD = {"eurusd": 1.4e-4, "jpy": 1.46e-4, "audusd": 2.6e-4, "nzdusd": 2.9e-4, "audjpy": 2.8e-4,
          "xauusd_gcf": 2.0e-4, "bz": 4.0e-4, "spx": 1.0e-4}
#: tien te cua cap (X, Y) -> cot BIS; None = hang hoa/chi so (tai chinh hoa USD + 2,5 %)
CAP = {"eurusd": ("XM", "US"), "jpy": ("US", "JP"), "audusd": ("AU", "US"), "nzdusd": ("NZ", "US"),
       "audjpy": ("AU", "JP")}
MARKUP_FX = 0.01
NAM_CB = {"USD_CUOI_THANG": 2014, "CUOI_QUY_TAI_CAN_BANG": 2015, "CUOI_NAM_USD": 2000, "USD_THANG12_THANG1": 2000,
          "JPY_CUOI_NAM_TAI_KHOA": 2000, "VANG_THANG8_THANG2": 2010, "DAU_THANG2_THANG4": 2000,
          "CHENH_2Y_MY_DUC_EURUSD": 2000, "TNX_USDJPY": 2000, "TNX_VANG": 2000, "AUD_NZD_HOI_QUY": 1999,
          "CARRY_AUDJPY": 1990, "VIX_THAP_US500": 2005, "DANH_MUC_4_SPX": 2026}


def gia(ten):
    return MV.doc(f"{ten}_d1_yahoo.csv")


def bis(idx):
    b = pd.read_csv(DU / "bis_lai_suat_chinh_sach.csv", index_col=0, parse_dates=True)
    b = b.reindex(b.index.union(idx)).ffill().reindex(idx) / 100.0
    irx = MV.lai_suat(idx)
    b["US"] = b["US"].fillna(pd.Series(irx, index=idx))
    b["NZ"] = b["US"]                                       # gia dinh (khong co du lieu NZ mien phi)
    return b


def loi_rong(ten, e, he_so=1.0):
    g = gia(ten)
    idx = g.index
    e = np.asarray(e, dtype=float)
    r = g.pct_change().fillna(0.0).to_numpy()
    doi = np.abs(np.diff(np.r_[0.0, e]))
    ngay = np.r_[1.0, np.diff(idx.values).astype("timedelta64[D]").astype(float)]
    if ten in CAP:
        b = bis(idx)
        x, y = CAP[ten]
        dif = (b[x] - b[y]).fillna(0.0).to_numpy()
        fin = e * dif - np.abs(e) * MARKUP_FX
    else:
        rus = MV.lai_suat(idx)
        fin = -e * rus - np.abs(e) * 0.025
    return e * r - doi * (SPREAD[ten] * he_so / 2 + TRUOT) + fin * ngay / 365.0, idx


def _tre(x):
    return np.r_[np.nan, np.asarray(x, dtype=float)[:-1]]


def _cuoi(idx, k):
    return pd.Series(np.arange(len(idx)), index=idx).groupby([idx.year, idx.month]).cumcount(ascending=False).to_numpy() < k


def quy_tac(ten):
    """-> list[(tai_san, e)] (chan)."""
    if ten == "USD_CUOI_THANG":
        g = gia("eurusd"); return [("eurusd", _cuoi(g.index, 2).astype(float))]
    if ten == "CUOI_QUY_TAI_CAN_BANG":
        g = gia("eurusd"); idx = g.index
        spx = gia("spx")
        q = spx.groupby([spx.index.year, spx.index.quarter]).tail(1)
        qs = pd.Series(q.values, index=q.index)
        sp = spx.reindex(spx.index.union(idx)).ffill().reindex(idx).to_numpy()
        e = np.zeros(len(idx)); c = _cuoi(idx, 5)
        for i in range(1, len(idx)):
            if c[i] and idx[i].month in (3, 6, 9, 12):
                truoc = qs[qs.index < pd.Timestamp(idx[i].year, idx[i].month - 2, 1)]
                if len(truoc):
                    e[i] = 1.0 if sp[i - 1] / truoc.iloc[-1] - 1 > 0 else -1.0
        return [("eurusd", e)]
    if ten == "CUOI_NAM_USD":
        g = gia("eurusd"); return [("eurusd", (_cuoi(g.index, 10) & (g.index.month == 12)).astype(float))]
    if ten == "USD_THANG12_THANG1":
        g = gia("eurusd"); m = g.index.month
        return [("eurusd", np.where(m == 12, 1.0, np.where(m == 1, -1.0, 0.0)))]
    if ten == "JPY_CUOI_NAM_TAI_KHOA":
        g = gia("jpy"); return [("jpy", -(g.index.month == 3).astype(float))]
    if ten == "VANG_THANG8_THANG2":
        g = gia("xauusd_gcf"); return [("xauusd_gcf", np.isin(g.index.month, [8, 9, 10, 11, 12, 1, 2]).astype(float))]
    if ten == "DAU_THANG2_THANG4":
        g = gia("bz"); return [("bz", np.isin(g.index.month, [2, 3, 4]).astype(float))]
    if ten == "CHENH_2Y_MY_DUC_EURUSD":
        g = gia("eurusd"); idx = g.index
        us = pd.read_csv(DU / "us2y_treasury.csv", index_col=0, parse_dates=True)["us2y"]
        de = pd.read_csv(DU / "de2y_bundesbank.csv", index_col=0, parse_dates=True)["de2y"]
        ch = (us - de.reindex(us.index, method="ffill")).dropna()
        c = ch.reindex(ch.index.union(idx)).ffill().reindex(idx)
        d = _tre((c - c.shift(20)).to_numpy())
        return [("eurusd", np.where(d > 0, -1.0, np.where(d < 0, 1.0, 0.0)))]
    if ten in ("TNX_USDJPY", "TNX_VANG"):
        ts = "jpy" if ten == "TNX_USDJPY" else "xauusd_gcf"
        g = gia(ts); idx = g.index
        t = gia("tnx"); t = t.reindex(t.index.union(idx)).ffill().reindex(idx)
        d = _tre((t - t.shift(20)).to_numpy())
        return [(ts, (d > 0 if ts == "jpy" else d < 0).astype(float))]
    if ten == "AUD_NZD_HOI_QUY":
        a, nz = gia("audusd"), gia("nzdusd")
        idx = a.index.intersection(nz.index)
        x = np.log(a.reindex(idx)) - np.log(nz.reindex(idx))
        z = _tre(((x - x.rolling(60).mean()) / x.rolling(60).std()).to_numpy())
        s = np.zeros(len(idx)); cur = 0.0
        for i in range(len(idx)):
            if np.isfinite(z[i]):
                if cur == 0 and z[i] > 2: cur = -1.0
                elif cur == 0 and z[i] < -2: cur = 1.0
                elif cur != 0 and abs(z[i]) < 0.5: cur = 0.0
            s[i] = cur
        ea = pd.Series(0.5 * s, index=idx).reindex(a.index).fillna(0).to_numpy()
        en = pd.Series(-0.5 * s, index=idx).reindex(nz.index).fillna(0).to_numpy()
        return [("audusd", ea), ("nzdusd", en)]
    if ten == "CARRY_AUDJPY":
        g = gia("audjpy"); return [("audjpy", np.ones(len(g)))]
    if ten == "VIX_THAP_US500":
        g = MV.doc("spx_d1_yahoo.csv", "1950-01-01"); idx = g.index
        v = gia("vix"); med = v.rolling(252).median()
        ok = (v < med).reindex(idx).to_numpy()
        e = _tre(np.where(pd.isna(ok), 0.0, ok.astype(float) if ok.dtype != object else [bool(x) if x == x else False for x in ok]))
        return [("spx", np.nan_to_num(e))]
    if ten == "DANH_MUC_4_SPX":
        g = MV.doc("spx_d1_yahoo.csv", "1950-01-01")
        e = np.mean([MV.phoi_nhiem(k, g) for k in ("CHU_KY_BAU_CU_NAM3", "HALLOWEEN", "DAU_CUOI_THANG", "SANTA")], axis=0)
        return [("spx", e)]
    raise KeyError(ten)


def chay_qt(ten, he_so):
    chan = quy_tac(ten)
    ds = []
    for ts, e in chan:
        if ts == "spx":
            g = MV.doc("spx_d1_yahoo.csv", "1950-01-01")
            L = MV.chay(g, np.asarray(e, float), SPREAD["spx"], he_so); idx = g.index
        else:
            L, idx = loi_rong(ts, e, he_so)
        ds.append(pd.Series(L, index=idx))
    tong = pd.concat(ds, axis=1).fillna(0.0).sum(axis=1)
    e0 = np.asarray(chan[0][1], float)
    return tong, float(np.mean(np.abs(e0) > 0)), int(np.sum(np.diff(np.r_[0.0, np.abs(e0) > 0]) > 0))


TAT = ["DANH_MUC_4_SPX", "USD_CUOI_THANG", "CUOI_QUY_TAI_CAN_BANG", "CUOI_NAM_USD", "USD_THANG12_THANG1",
       "JPY_CUOI_NAM_TAI_KHOA", "VANG_THANG8_THANG2", "DAU_THANG2_THANG4", "CHENH_2Y_MY_DUC_EURUSD", "TNX_USDJPY",
       "TNX_VANG", "AUD_NZD_HOI_QUY", "CARRY_AUDJPY", "VIX_THAP_US500"]


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--ra"); a = ap.parse_args(argv)
    ra = []
    for ten in TAT:
        o = {"quy_tac": ten}
        for hs in (1.0, 1.5):
            L, giu, lenh = chay_qt(ten, hs)
            L = L[L.index >= L.index[0]]
            idx = L.index; v = L.to_numpy(); c = int(len(v) * 0.7)
            m = np.asarray(idx.year >= NAM_CB[ten])
            o[f"x{hs:g}"] = {"toan": MV.do(v, idx), "nm": MV.do(v[c:], idx[c:]),
                             "truoc_cong_bo": MV.do(v[~m], idx[~m]) if (~m).sum() > 250 else None,
                             "sau_cong_bo": MV.do(v[m], idx[m]) if m.sum() > 250 else None}
        o.update(tu=str(idx[0].date()), den=str(idx[-1].date()), ty_le_ngay_giu=round(giu, 3), so_lenh=lenh,
                 p=MV.p1(o["x1"]["toan"]["t"]))
        ra.append(o)
    v10 = json.load(open("reports/vong10_mua_vu.json"))["quy_tac"]
    ps = [o["p"] for o in ra] + [o["p"] for o in v10]
    ph = MV.holm(ps)
    for o, q in zip(ra, ph):
        o["p_holm_21"] = q
        x1, x15 = o["x1"], o["x1.5"]
        tc = {"lai_toan": x1["toan"]["loi_pct"] > 0, "dd_lt_80": x1["toan"]["maxdd_pct"] < 80,
              "nm_lai_x1": x1["nm"]["loi_pct"] > 0, "nm_lai_x1_5": x15["nm"]["loi_pct"] > 0,
              "sau_cong_bo": (x1["sau_cong_bo"] is None and o["quy_tac"] == "DANH_MUC_4_SPX") or
                             bool(x1["sau_cong_bo"] and x1["sau_cong_bo"]["sharpe"] > 0),
              "p_holm_lt_005": q < 0.05}
        o["tieu_chi"] = tc; o["song"] = all(tc.values())
    v10_holm = {o["quy_tac"]: q for o, q in zip(v10, ph[len(ra):])}
    out = {"nhan": "MO PHONG", "so_phep_thu_holm": len(ps), "quy_tac": ra, "vong10_p_holm_lai_22": v10_holm}
    for o in ra:
        print(o["quy_tac"], o["tu"], "giu", o["ty_le_ngay_giu"], "| x1", o["x1"]["toan"], "NM", o["x1"]["nm"]["loi_pct"],
              "x1.5NM", o["x1.5"]["nm"]["loi_pct"], "| CB", (o["x1"]["truoc_cong_bo"] or {}).get("sharpe"), "->",
              (o["x1"]["sau_cong_bo"] or {}).get("sharpe"), "| p %.4f holm %.4f" % (o["p"], o["p_holm_21"]), "SONG" if o["song"] else "-")
    print("vong 10 holm lai:", {k: round(v, 4) for k, v in v10_holm.items()})
    if a.ra:
        json.dump(out, open(a.ra, "w"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    main()
