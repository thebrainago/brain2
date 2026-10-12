# -*- coding: utf-8 -*-
"""Vong 14: quet lich (don + ghep 2), cheo tai san tre 1 ngay, su kien FOMC/NFP. Dang ky truoc reports/vong14_tien_dang_ky.md. MO PHONG."""
from __future__ import annotations

import datetime as dt
import itertools as it
import json
import math
import re
import sys

import numpy as np
import pandas as pd

import lich_su_kien as LS
import mua_vu as MV

TS = {"spx": ("gspc_ohlc_yahoo.csv", 1.0e-4, "cs"), "ndx": ("ndx_ohlc_yahoo.csv", 1.5e-4, "cs"), "gdaxi": ("gdaxi_ohlc_yahoo.csv", 1.0e-4, "cs"),
      "ftse": ("ftse_ohlc_yahoo.csv", 1.5e-4, "cs"), "n225": ("n225_ohlc_yahoo.csv", 2.6e-4, "cs"), "hsi": ("hsi_ohlc_yahoo.csv", 3.0e-4, "cs"),
      "vang": ("gcf_ohlc_yahoo.csv", 2.0e-4, "cs"), "dau": ("bz_d1_yahoo.csv", 4.0e-4, "cs"),
      "eurusd": ("eurusd_d1_yahoo.csv", 1.6e-4, "fx"), "gbpusd": ("gbpusd_ohlc_yahoo.csv", 1.6e-4, "fx"), "usdjpy": ("jpy_d1_yahoo.csv", 1.6e-4, "fx"),
      "audusd": ("audusd_d1_yahoo.csv", 2.0e-4, "fx"), "nzdusd": ("nzdusd_d1_yahoo.csv", 2.5e-4, "fx"), "usdchf": ("chf_ohlc_yahoo.csv", 2.0e-4, "fx"),
      "usdcad": ("cad_ohlc_yahoo.csv", 2.0e-4, "fx"), "audjpy": ("audjpy_d1_yahoo.csv", 2.5e-4, "fx")}
MARKUP = 0.025


def gia(t):
    s = MV.doc(TS[t][0], "1990-01-01").dropna()
    s = s[s > 0]; s = s[~s.index.duplicated(keep="last")]
    r = s.pct_change()
    return s[(r.abs() < 0.25) | r.isna()]          # bo diem hong cua Yahoo (>25 %/ngay)


def dac_trung(idx):
    s = pd.Series(np.arange(len(idx)), index=idx); g = s.groupby([idx.year, idx.month])
    dau = (s - g.transform("min")).to_numpy() + 1; cuoi = (g.transform("max") - s).to_numpy() + 1
    F = {}
    for d in range(5): F[f"thu{d}"] = idx.dayofweek == d
    for m in range(1, 13): F[f"thang{m}"] = idx.month == m
    for k in range(1, 6): F[f"dau{k}"] = dau == k; F[f"cuoi{k}"] = cuoi == k
    for c in range(4): F[f"chuky{c}"] = idx.year % 4 == c
    return {k: np.asarray(v) for k, v in F.items()}


def ho(k):
    return "".join(ch for ch in k if not ch.isdigit())


def p_o(r, mask, nua):
    a, b = mask & nua, mask & ~nua
    if a.sum() < 20 or b.sum() < 20: return None
    sg = 1.0 if r[a].mean() > 0 else -1.0
    x = sg * r[b]; sd = x.std(ddof=1)
    if sd == 0: return None
    return sg, MV.p1(x.mean() / sd * math.sqrt(len(x))), int(b.sum())


def quet():
    o = []; R = {t: gia(t) for t in TS}
    fomc = set(LS.fomc()); nfp = set(LS.nfp())
    for t, s in R.items():
        idx = s.index; r = s.pct_change().fillna(0).to_numpy(); nua = np.asarray(idx < idx[len(idx) // 2])
        F = dac_trung(idx)
        cells = [(k,) for k in F] + [(a, b) for a, b in it.combinations(F, 2) if ho(a) != ho(b) and not {ho(a), ho(b)} == {"dau", "cuoi"}]
        for c in cells:
            m = np.logical_and.reduce([F[k] for k in c]); q = p_o(r, m, nua)
            if q: o.append({"loai": "lich", "ts": t, "o": "+".join(c), "huong": q[0], "p": q[1], "n_kiem": q[2]})
        d = np.array([x.date() for x in idx])
        for ten, ev in (("fomc", fomc), ("nfp", nfp)):
            e = np.array([x in ev for x in d])
            for cs, m in (("truoc", np.r_[e[1:], False]), ("ngay", e), ("sau", np.r_[False, e[:-1]])):
                q = p_o(r, m, nua)
                if q: o.append({"loai": "su_kien", "ts": t, "o": f"{ten}_{cs}", "huong": q[0], "p": q[1], "n_kiem": q[2]})
        for a, sA in R.items():
            if a == t: continue
            rA = sA.pct_change()
            mo = idx[:-1] - pd.Timedelta(days=1)          # B mo o dong idx[j-1]; dung loi A cua ngay <= idx[j-1]-1
            sig = np.r_[np.nan, rA.reindex(rA.index.union(mo)).ffill().reindex(mo).to_numpy()]
            for dau_a in (1, -1):
                m = np.nan_to_num(np.sign(sig)) == dau_a; q = p_o(r, m, nua)
                if q: o.append({"loai": "cheo", "ts": t, "o": f"{a}{'len' if dau_a > 0 else 'xuong'}_t-1", "huong": q[0], "p": q[1], "n_kiem": q[2]})
    return o, R


def p_cu():
    v10 = json.load(open("reports/vong10_mua_vu.json"))["quy_tac"]; v11 = json.load(open("reports/vong11_fx_vi_mo.json"))["quy_tac"]
    b = json.load(open("reports/vong11b.json")); v12 = json.load(open("reports/vong12.json"))["quy_tac"]
    v13 = json.load(open("reports/vong13.json"))["ibs_tai_san"]
    return [x["p"] for x in v11] + [x["p"] for x in v10] + [b["vang_m30"][k]["x1"]["p"] for k in ("vn", "server", "gmt")] + \
        [b["ibs"]["p"]] + [x["p"] for x in v12] + [x["p"] for x in v13]


def bh(ps):
    m = len(ps); od = sorted(range(m), key=lambda i: ps[i]); q = [1.0] * m; c = 1.0
    for r in range(m - 1, -1, -1):
        i = od[r]; c = min(c, ps[i] * m / (r + 1)); q[i] = c
    return q


def xac_nhan(c, R, hs):
    s = R[c["ts"]]; idx = s.index; r = s.pct_change().fillna(0).to_numpy()
    o, _ = None, None
    F = dac_trung(idx)
    if c["loai"] == "lich":
        m = np.logical_and.reduce([F[k] for k in c["o"].split("+")])
    elif c["loai"] == "cheo":
        a = re.match(r"([a-z]+?)(len|xuong)_t-1", c["o"]); rA = R[a.group(1)].pct_change()
        mo = idx[:-1] - pd.Timedelta(days=1)
        sig = np.r_[np.nan, rA.reindex(rA.index.union(mo)).ffill().reindex(mo).to_numpy()]
        m = np.nan_to_num(np.sign(sig)) == (1 if a.group(2) == "len" else -1)
    else:
        return None
    e = c["huong"] * m.astype(float)
    doi = np.abs(np.diff(np.r_[0.0, e])); ngay = np.r_[1.0, np.diff(idx.values).astype("timedelta64[D]").astype(float)]
    tb = MV.lai_suat(idx) if TS[c["ts"]][2] == "cs" else 0.0
    qd = np.where(e > 0, tb + MARKUP, MARKUP) if TS[c["ts"]][2] == "cs" else MARKUP
    loi = e * r - doi * (TS[c["ts"]][1] * hs / 2 + MV.TRUOT) - np.abs(e) * qd * ngay / 365.0
    k = len(idx) // 2; m10 = np.asarray(idx.year >= 2010)
    return {"toan": MV.do(loi, idx), "kiem": MV.do(loi[k:], idx[k:]), "sau_2010": MV.do(loi[m10], idx[m10])}


def main(ra=None):
    o, R = quet(); cu = p_cu(); ps = cu + [x["p"] for x in o]
    H = MV.holm(ps); B = bh(ps)
    for x, h, q in zip(o, H[len(cu):], B[len(cu):]): x["p_holm"] = h; x["q_bh"] = q
    print("so o quet", len(o), "tong ho", len(ps), "holm<0.05", sum(x["p_holm"] < .05 for x in o), "bh<0.05", sum(x["q_bh"] < .05 for x in o))
    from collections import Counter
    print(Counter(x["loai"] for x in o))
    ung = sorted([x for x in o if x["q_bh"] < 0.05], key=lambda x: x["p"])
    for x in ung[:40]:
        print(x["loai"], x["ts"], x["o"], x["huong"], "n", x["n_kiem"], "p %.2e holm %.3f bh %.3f" % (x["p"], x["p_holm"], x["q_bh"]))
    song = []
    for x in [x for x in o if x["p_holm"] < 0.05]:
        k1, k15 = xac_nhan(x, R, 1.0), xac_nhan(x, R, 1.5)
        if k1 is None:
            x["xac_nhan"] = "cheo/su kien: xem rieng"; continue
        tc = {"lai_toan": k1["toan"]["loi_pct"] > 0, "dd": k1["toan"]["maxdd_pct"] < 80, "kiem_x1": k1["kiem"]["loi_pct"] > 0,
              "kiem_x1_5": k15["kiem"]["loi_pct"] > 0, "sau_2010": k1["sau_2010"]["sharpe"] > 0}
        x["xac_nhan"] = {"x1": k1, "x1.5": k15, "tieu_chi": tc}; x["song"] = all(tc.values())
        print("XN", x["ts"], x["o"], x["huong"], k1["toan"], "kiem", k1["kiem"]["loi_pct"], k15["kiem"]["loi_pct"], "s2010", k1["sau_2010"]["sharpe"], "SONG" if x["song"] else "-")
        if x["song"]: song.append(x)
    if ra:
        json.dump({"nhan": "MO PHONG", "so_o": len(o), "ho_holm": len(ps), "o": o, "song": song}, open(ra, "w"), ensure_ascii=False, default=float)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
