# -*- coding: utf-8 -*-
"""
VÒNG 7 – HƯỚNG 1: TREND / MOMENTUM (daily). Lưới tham số khai báo TRƯỚC, không tối ưu:
  TSMOM 63/126/252 phiên; Donchian 20/55/100 (thoát ở kênh N/2 ngược); SMA 20/100, 50/200; lọc chế độ C>SMA200.
  Mỗi tín hiệu: Long-only (L) và Long/Short (LS); thêm biến thể vol-target 15%/năm (đòn bẩy tối đa 2x, vol 20 phiên).
  Khớp OPEN THẬT phiên kế tiếp, có spread.
"""
import numpy as np, pandas as pd, sys
from multiprocessing import Pool
from common7 import *

TICKERS = ["GC=F", "ES=F", "^GSPC"]


def signals(d):
    C, H, L = d.Close.values, d.High.values, d.Low.values; S = {}
    for lb in (63, 126, 252):
        mom = C / np.r_[np.full(lb, np.nan), C[:-lb]] - 1
        S[f"TSMOM{lb}"] = (np.sign(np.nan_to_num(mom)), lb)
    for N in (20, 55, 100):
        hh = pd.Series(H).rolling(N).max().shift(1).values; ll = pd.Series(L).rolling(N).min().shift(1).values
        hx = pd.Series(H).rolling(N // 2).max().shift(1).values; lx = pd.Series(L).rolling(N // 2).min().shift(1).values
        n = len(C); w = np.zeros(n); s = 0
        for t in range(n):
            if s <= 0 and C[t] > hh[t]: s = 1
            elif s >= 0 and C[t] < ll[t]: s = -1
            elif s == 1 and C[t] < lx[t]: s = 0
            elif s == -1 and C[t] > hx[t]: s = 0
            w[t] = s
        S[f"Donchian{N}"] = (w, N)
    for a, b in ((20, 100), (50, 200)):
        f, s_ = sma(C, a), sma(C, b); S[f"SMA{a}/{b}"] = (np.where(np.isnan(s_), 0, np.sign(f - s_)), b)
    s200 = sma(C, 200); S["C>SMA200"] = (np.where(np.isnan(s200), 0, np.sign(C - s200)), 200)
    return S


def voltarget(d, w, tgt=0.15, cap=2.0):
    r = np.r_[np.nan, np.diff(np.log(d.Close.values))]
    vol = pd.Series(r).rolling(20).std().values * np.sqrt(252)
    lev = np.clip(tgt / vol, 0, cap); return np.nan_to_num(w * lev)


def job(args):
    tk, nm, side, vt = args
    d = load_d(tk); S = signals(d); w, _ = S[nm]
    w = np.where(w > 0, 1.0, np.where(w < 0, -1.0 if side == "LS" else 0.0, 0.0))
    if nm == "C>SMA200" and side == "LS": return None
    if vt: w = voltarget(d, w)
    rng = np.random.default_rng(hash((tk, nm, side, vt)) % 2**32)
    return eval_daily(tk, d, w, "open", rng, nm + ("+VT15" if vt else ""), "1_trend", side)


def bl_job(tk):
    d = load_d(tk); rng = np.random.default_rng(1); rows = []
    for nm, w in baselines(d, SPREAD[tk]).items():
        rows.append(eval_daily(tk, d, w, "open", rng, "BL_" + nm, "baseline", "L", do_rand=(nm != "BH")))
    rows.append(eval_daily(tk, d, voltarget(d, np.ones(len(d))), "open", rng, "BL_BH+VT15", "baseline", "L", do_rand=False))
    return rows


if __name__ == "__main__":
    jobs = [(tk, nm, side, vt) for tk in TICKERS for nm in
            ["TSMOM63", "TSMOM126", "TSMOM252", "Donchian20", "Donchian55", "Donchian100", "SMA20/100", "SMA50/200", "C>SMA200"]
            for side in ("L", "LS") for vt in (False, True)]
    with Pool(8) as p:
        rows = [r for r in p.map(job, jobs) if r is not None]
        bl = sum(p.map(bl_job, TICKERS + ["SPY"]), [])
    pd.DataFrame(rows).to_csv("results7/h1_trend.csv", index=False)
    pd.DataFrame(bl).to_csv("results7/baselines_daily.csv", index=False)
    print(pd.DataFrame(bl)[["ticker", "strategy", "IS_sharpe", "OOS_sharpe", "IS_cagr", "OOS_cagr", "OOS_maxdd"]].round(2))
    print(len(rows), "chiến lược trend")
