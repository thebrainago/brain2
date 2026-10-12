# -*- coding: utf-8 -*-
"""Vong 24: kiem pooled da tai san cac ung vien khung lon. Dang ky: reports/vong24_tien_dang_ky.md. MO PHONG."""
from __future__ import annotations

import glob
import json
import math
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import norm

import mua_vu as MV
import v19
import v21
import v22
import v23

DV = "/workspace/du_lieu_ngay/v24/"
CHINH = {"EURUSD", "GBPUSD", "JPY", "AUDUSD", "NZDUSD", "USDCAD", "USDCHF"}
TACH = pd.Timestamp("2015-04-01"); QD = 0.025 / 365; RNG = np.random.default_rng(24)


def bps_of(ten):
    t = ten.replace("_X", "").replace("_F", "")
    if ten.endswith("_X"):
        if t in CHINH: return 1.5e-4
        return 3e-4 if any(k in t for k in ("EUR", "GBP", "JPY")) else 4e-4
    m = {"GC": 2, "SI": 5, "PL": 8, "CL": 4, "BZ": 4, "NG": 10, "HG": 6}
    if t in m: return m[t] * 1e-4
    if ten.endswith("_F"): return 8e-4
    if t in ("iGSPC", "iNDX", "iDJI", "iRUT"): return 1e-4
    if t in ("iGDAXI", "iFTSE", "iFCHI", "iSTOXX50E"): return 1.5e-4
    return 3e-4


def tai_d1():
    B = {}
    for f in sorted(glob.glob(DV + "*.csv")):
        ten = os.path.basename(f)[:-4]; d = pd.read_csv(f, index_col=0, parse_dates=True)
        d = d[(d.index >= "2004-01-01") & (d["high"] >= d["low"]) & (d["close"] > 0)].copy()
        d = d[(d["high"] > d["low"]) | (d["open"] != d["close"])]
        d["spread_open"] = d["close"] * bps_of(ten); d["so_tick"] = 1; B[ten] = d
    return B


def w1(d):
    return d.resample("W-FRI").agg({"open": "first", "high": "max", "low": "min", "close": "last", "spread_open": "last", "so_tick": "last"}).dropna()


def lenh(d, he, sp):
    h, l, c = (d[k].to_numpy() for k in ("high", "low", "close")); A = v23.atr(h, l, c)
    if he.startswith("PAXG"): return v23.sim(d, v23.paxg(d, "D1", A), sp, A)
    if he.startswith("TRENDBREAKER"): return v23.sim(d, v23.trendbreaker(d, "D1", A), sp, A)
    if he.startswith("EMA"):
        a21 = v21.atr_of(d); e = d["close"].ewm(span=20, adjust=False).mean().to_numpy(); z = np.zeros(len(d))
        sig = v21.tin(d, e, a21, "MR", 2.0, "KHONG", "KHONG", z, z, z, z); return v22.ema_chay(d, e, a21, sig, "MR", 2.0, sp)
    s, atr, _ = v19.tin_hieu(d); ten, th = he.split("_")[0], he.split("_")[1]
    return v22.chay(d, s[ten].astype(int), th, atr, sp)


def tra(L, drift, phi, slip_bps):
    return [(x[0], x[1] - ((x[5] * QD + 2 * slip_bps * 1e-4) if phi else 0) - x[2] * drift * x[3], x[0] + pd.Timedelta(days=max(x[5], 0))) for x in L]


def p_cum(t, r):
    """t mot phia, SE gom cum theo tuan vao lenh."""
    df = pd.DataFrame({"w": pd.DatetimeIndex(t).to_period("W"), "r": r}); n = len(df); m = df["r"].mean()
    g = df.groupby("w")["r"].apply(lambda x: (x - m).sum()); G = len(g)
    se = math.sqrt((g ** 2).sum() * G / max(G - 1, 1)) / n
    return float(1 - norm.cdf(m / se)) if se > 0 else 1.0, G


def p_boot(t, r, B=2000):
    df = pd.DataFrame({"w": pd.DatetimeIndex(t).to_period("W"), "r": r}); g = df.groupby("w")["r"].agg(["sum", "count"])
    s, c = g["sum"].to_numpy(), g["count"].to_numpy(); G = len(s); m0 = s.sum() / c.sum()
    idx = RNG.integers(0, G, (B, G)); mb = s[idx].sum(1) / c[idx].sum(1)
    return float(np.mean((mb - m0) >= m0))   # phan bo duoi H0 = bootstrap dich tam ve 0


def danh_gia(T, n_ts):
    t = np.array([x[0] for x in T]); r = np.array([x[1] for x in T]); te = np.array([x[2] for x in T])
    a, b = t < TACH_DONG[0], t >= TACH_DONG[0]
    if a.sum() < 30 or b.sum() < 30: return None
    p, G = p_cum(t[b], r[b]); pb = p_boot(t[b], r[b])
    s = pd.Series(r / n_ts, index=pd.DatetimeIndex(te)).groupby(level=0).sum().sort_index(); eq = 1 + s.cumsum()
    dd = float(np.max(1 - eq / np.maximum.accumulate(eq)) * 100)
    return {"n_ph": int(a.sum()), "n_kiem": int(b.sum()), "cum_tuan": G, "tb_ph_bps": float(r[a].mean() * 1e4), "tb_kiem_bps": float(r[b].mean() * 1e4),
            "p": p, "p_boot": pb, "maxdd_pct": dd, "lai_nam_kiem_pct": float(s[s.index >= TACH_DONG[0]].sum() / max((s.index[-1] - TACH_DONG[0]).days / 365.25, 1e-9) * 100)}


TACH_DONG = [TACH]
HE = ["PAXG_ST_D1", "TRENDBREAKER_D1", "TRENDBREAKER_H4", "RSI_TP_D1", "RSI_TR2_D1", "MRZ_TP_D1", "MRZ_TR2_D1", "RSI_TP_W1", "RSI_TR2_W1", "MRZ_TP_W1", "MRZ_TR2_W1", "EMA_MR20_D1"]


def bo_h4():
    B = {}
    for t in v23.CHUOI_NHO + ["us500_h1", "uk100_h1"]:
        d, _, _ = v23.lay(t, "H4"); d["so_tick"] = 1; B[t] = d
    return B


def chay_he(he, B):
    kq = {}
    for che, hs, sl in (("truoc", 0, 0), ("sau", 1, 0.5), ("sau_x15_s1", 1.5, 1.0)):
        T = []; theo = {}
        for ten, d0 in B.items():
            d = w1(d0) if he.endswith("W1") else d0
            if len(d) < 300: continue
            c = d["close"].to_numpy(); drift = float(np.mean(np.diff(np.log(c))[: len(c) // 2])) if he.endswith("H4") else \
                float(np.mean(np.diff(np.log(c[d.index < TACH])))) if (d.index < TACH).sum() > 50 else 0.0
            sp = d["spread_open"].to_numpy() * hs
            L = tra(lenh(d, he, sp), drift, che != "truoc", sl); T += L; theo[ten] = L
        kq[che] = (T, theo)
    return kq


def main(ra=None):
    D1 = tai_d1(); H4 = bo_h4(); out = []
    print("tai san D1:", len(D1), "H4:", len(H4))
    for he in HE:
        B = H4 if he.endswith("H4") else D1
        TACH_DONG[0] = TACH if not he.endswith("H4") else pd.Timestamp("2025-05-15")
        kq = chay_he(he, B); n_ts = len(B)
        r = {"he": he, "so_tai_san": n_ts, "tach": str(TACH_DONG[0].date())}
        for che, (T, theo) in kq.items():
            q = danh_gia(T, n_ts)
            if q: r[che] = q
        T, theo = kq["sau"]
        r["ty_le_ts_lai_kiem_pct"] = round(100 * np.mean([np.sum([x[1] for x in L if x[0] >= TACH_DONG[0]]) > 0 for L in theo.values() if any(x[0] >= TACH_DONG[0] for x in L)]), 1)
        nhom = {}
        for ten, L in theo.items():
            k = "FX" if ten.endswith("_X") else ("HANG_HOA" if ten.endswith("_F") else ("CHI_SO" if ten.startswith("i") else "H4"))
            nhom.setdefault(k, []).extend([x[1] for x in L if x[0] >= TACH_DONG[0]])
        r["kiem_theo_nhom_bps"] = {k: [round(float(np.mean(v)) * 1e4, 2), len(v)] for k, v in nhom.items() if v}
        out.append(r); print(he, json.dumps({k: r[k] for k in r if k not in ("he",)}, default=float)[:900], flush=True)
    cu = v23.v22_ho() + [x["p"] for x in json.load(open("reports/vong23.json"))["o"] if "p" in x]
    assert len(cu) == json.load(open("reports/vong23.json"))["ho_holm"], len(cu)
    v = [r for r in out if "sau" in r]; H = MV.holm(cu + [r["sau"]["p"] for r in v])
    for r, h in zip(v, H[len(cu):]):
        s = r["sau"]; x = r.get("sau_x15_s1")
        r["p_holm"] = h; r["song"] = bool(h < 0.05 and s["p_boot"] < 0.05 and s["tb_ph_bps"] > 0 and s["tb_kiem_bps"] > 0 and x and x["tb_kiem_bps"] > 0 and s["maxdd_pct"] < 80)
        print(r["he"], "p %.4g boot %.4g holm %.3f song %s" % (s["p"], s["p_boot"], h, r["song"]))
    print("ho", len(H))
    if ra: json.dump({"nhan": "MO PHONG", "ho_holm": len(H), "he": out}, open(ra, "w"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
