# -*- coding: utf-8 -*-
"""Dữ liệu chung cho Test 6 (Fibo xoắn ốc + chart phi chuẩn)."""
import numpy as np, pandas as pd
from common2 import load, atr_rma, pivots, bh_fdr, SPLIT

FILES = {"GC=F": "GCF", "ES=F": "ESF", "^GSPC": "GSPC"}
SPREAD = {"GC=F": 0.3, "ES=F": 0.25, "^GSPC": 0.5}


def load_tf(tk, tf):
    """Trả về DataFrame OHLC + cột 'period' (IS/OOS). Daily: tách 2016; intraday: chia đôi theo thời gian."""
    if tf == "1d":
        d = load(tk)
        d = d[(d.High >= d.Low) & (d.High > 0)]
        if tk == "GC=F": d = d[d.High > d.Low]          # bỏ nến hỏng H=L
        per = np.where(d.index < SPLIT, "IS", "OOS")
    else:
        d = pd.read_pickle(f"data_{FILES[tk]}_{tf}.pkl").dropna(subset=["Open", "High", "Low", "Close"])
        d = d[(d.High >= d.Low) & (d.High > 0)]
        d.index = pd.to_datetime(d.index, utc=True).tz_convert("America/New_York")
        mid = d.index[0] + (d.index[-1] - d.index[0]) / 2
        per = np.where(d.index < mid, "IS", "OOS")
    d = d[["Open", "High", "Low", "Close"]].astype(float).copy()
    d["period"] = per
    d["atr"] = atr_rma(d.High.values, d.Low.values, d.Close.values)
    return d
