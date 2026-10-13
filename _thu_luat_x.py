# -*- coding: utf-8 -*-
"""MO PHONG: thu nhanh luat trich tu X (13/10/2026). Gia Yahoo D1 lam proxy gia XM + spread XM that (phi_xm_that.bps_of_xm),
swap XM nhom '#' = 0 (DISABLED). Tach phat hien 70% / holdout 30% theo thoi gian. Loc theo tang:
 T1 phat hien: n>=30, tb>0, PF>1.05 ; T2 holdout: tb>0, p(t mot phia)<0.05 ; T3 Holm cong don voi ho vong28 (12960) + moi o dem nay.
Ket qua: reports/vong29_x.json. Khong luu noi dung bai X, chi URL nguon."""
import json, math, sys
import numpy as np, pandas as pd
from scipy import stats
import phi_xm_that as PX

D = "/workspace/du_lieu_ngay/"
TS = {"iGSPC": "gspc_ohlc_yahoo.csv", "iNDX": "ndx_ohlc_yahoo.csv", "iGDAXI": "gdaxi_ohlc_yahoo.csv",
      "GC_F": "gcf_ohlc_yahoo.csv", "GBPUSD_X": "gbpusd_ohlc_yahoo.csv"}

def nap(t):
    d = pd.read_csv(D + TS[t], parse_dates=["date"]).set_index("date")
    d = d[d.index >= "2001-01-01"]
    return d[(d.high > d.low) | (d.close != d.open)].dropna()

def rsi(c, n):
    x = c.diff(); u = x.clip(lower=0).ewm(alpha=1/n, adjust=False).mean(); v = (-x.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    return 100 - 100 / (1 + u / v)

def lenh_dong(d, vao, thoat, max_giu=20):
    """vao/thoat: Series bool tai close; vao lenh tai close ngay t, thoat tai close ngay thoat dau tien (hoac max_giu)."""
    c = d.close.values; V = vao.values; X = thoat.values; R = []; i = 0; n = len(c)
    while i < n - 1:
        if V[i]:
            j = i + 1
            while j < n - 1 and not X[j] and j - i < max_giu: j += 1
            R.append((d.index[i], c[j] / c[i] - 1)); i = j + 1
        else: i += 1
    return R

def qua_dem(d, vao):
    """vao tai close t, ra tai open t+1."""
    o = d.open.values; c = d.close.values; V = vao.values
    return [(d.index[i], o[i+1] / c[i] - 1) for i in range(len(c) - 1) if V[i]]

def luat(t, d):
    c, h, l, o = d.close, d.high, d.low, d.open
    s200 = c.rolling(200).mean(); r5 = rsi(c, 5); r4 = rsi(c, 4); e100 = c.ewm(span=100).mean()
    ibs = (c - l) / (h - l).replace(0, np.nan)
    out = {}
    out["R1_rsi5_sma200_EmpiricaLab"] = lenh_dong(d, (c > s200) & (r5 < 30), r5 > 50)
    out["R2_rsi4_ema100rising_crowcaw_noVWAP"] = lenh_dong(d, (r4 < 30) & (e100 > e100.shift(5)), r4 > 50)
    tr = (r5 < 30) & (r5 < r5.shift(1)) & (r5.shift(1) < r5.shift(2)) & (r5.shift(2) < r5.shift(3)) & (r5.shift(3) < 60) & (c > s200)
    out["R3_triple_rsi_QuantifiedStrat"] = lenh_dong(d, tr, r5 > 50)
    m = d.index.to_period("M"); g = pd.Series(range(len(d)), index=d.index).groupby(m)
    tu_cuoi = g.transform(lambda x: len(x) - 1 - (x - x.iloc[0])); tu_dau = g.transform(lambda x: x - x.iloc[0])
    out["R4_turn_of_month_QuantifiedStrat"] = lenh_dong(d, tu_cuoi == 4, (tu_dau == 2), max_giu=10)
    out["R5_3_down_overnight_QuantifiedStrat"] = qua_dem(d, (c < c.shift(1)) & (c.shift(1) < c.shift(2)) & (c.shift(2) < c.shift(3)))
    out["R6_ibs_lt_0.2_exit_prevhigh"] = lenh_dong(d, ibs < 0.2, c > h.shift(1), max_giu=10)
    band = h.rolling(10).max() - 2.5 * (h - l).rolling(25).mean()
    out["R7_range_band_weakclose_EmpiricaLab"] = lenh_dong(d, (c < band) & (ibs < 0.3), c > h.shift(1), max_giu=10)
    out["R8_overnight_every_night_RB_QS"] = qua_dem(d, pd.Series(True, index=d.index))
    return out

def thong_ke(x):
    x = np.asarray(x); n = len(x)
    if n < 2: return {"n": n, "tb_bps": 0, "pf": 0, "p": 1.0}
    p = stats.ttest_1samp(x, 0, alternative="greater").pvalue
    g = x[x > 0].sum(); b = -x[x < 0].sum()
    return {"n": int(n), "tb_bps": float(round(x.mean() * 1e4, 2)), "pf": float(round(g / b, 2)) if b > 0 else 99, "p": float(p)}

def holm_ho(ps_moi):
    import v28
    cu = v28.holm_cu() + [x["sau"]["p"] if "sau" in x else 1.0 for x in json.load(open("reports/vong28.json"))["o"]]
    tat = cu + ps_moi; N = len(tat); thu = sorted(range(N), key=lambda i: tat[i]); adj = [1.0] * N; m = 0
    for k, i in enumerate(thu): m = max(m, min(1.0, (N - k) * tat[i])); adj[i] = m
    return adj[len(cu):], len(cu), N

O = []
for t in TS:
    d = nap(t); phi = max(PX.bps_of_xm(t, True), PX.bps_of_xm(t, False))
    for ten, R in luat(t, d).items():
        if not R: continue
        cat = d.index[int(len(d) * 0.7)]
        r = np.array([x for _, x in R]) - phi
        ngay = np.array([dt for dt, _ in R])
        ph, ho = r[ngay < cat], r[ngay >= cat]
        A, B = thong_ke(ph), thong_ke(ho)
        t1 = A["n"] >= 30 and A["tb_bps"] > 0 and A["pf"] > 1.05
        t2 = t1 and B["tb_bps"] > 0 and B["p"] < 0.05
        O.append({"luat": ten, "tai_san": t, "phi_bps_khu_hoi": round(phi * 1e4, 2), "cat": str(cat.date()), "phat_hien": A, "holdout": B, "T1": bool(t1), "T2": bool(t2)})
adj, n_cu, N = holm_ho([o["holdout"]["p"] if o["T2"] else 1.0 for o in O])
for o, a in zip(O, adj): o["p_holm_cong_don"] = a; o["T3_song"] = bool(o["T2"] and a < 0.05)
json.dump({"nhan": "MO PHONG", "nguon": "X (Twitter) 13/10/2026", "ho_holm_truoc": n_cu, "ho_holm": N, "so_o": len(O),
           "T1": sum(o["T1"] for o in O), "T2": sum(o["T2"] for o in O), "T3": sum(o["T3_song"] for o in O), "o": O},
          open("reports/vong29_x.json", "w"), ensure_ascii=False, indent=1, default=lambda v: v.item() if hasattr(v, "item") else str(v))
for o in O: print(o["tai_san"], o["luat"], o["phat_hien"], o["holdout"], o["T1"], o["T2"], "%.3g" % o["p_holm_cong_don"])
print("ho", n_cu, "->", N, "T1", sum(o["T1"] for o in O), "T2", sum(o["T2"] for o in O), "T3", sum(o["T3_song"] for o in O))
