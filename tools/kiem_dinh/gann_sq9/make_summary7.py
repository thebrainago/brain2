# -*- coding: utf-8 -*-
"""Gộp kết quả vòng 7, FDR (Benjamini–Hochberg) trên TOÀN BỘ phép thử, so baseline, lọc ứng viên."""
import numpy as np, pandas as pd
from common7 import *

parts = [pd.read_csv(f"results7/{f}") for f in ("h1_trend.csv", "h2_meanrev.csv", "h3_calendar.csv", "h4_volnews.csv")]
df = pd.concat(parts, ignore_index=True)
bl = pd.read_csv("results7/baselines_daily.csv")
B = {(r.ticker, r.strategy): (r.IS_sharpe, r.OOS_sharpe) for r in bl.itertuples()}

# Baseline B&H cho cửa sổ 1h và ^GSPC 2014+ (cùng giai đoạn)
def bh_window(tk, kind):
    if kind == "1h":
        h = load_h(tk); h["date"] = h.index.date
        g = h.groupby("date").agg(c=("Close", "last"), per=("period", "first")); r = g.c.pct_change()
        return tuple(r[g.per == p].mean() / r[g.per == p].std() * np.sqrt(252) for p in ("IS", "OOS"))
    d = load_d("^GSPC"); d = d[d.index >= "2014-01-01"]; mid = d.index[0] + (d.index[-1] - d.index[0]) / 2
    r = d.Close.pct_change(); per = np.where(d.index < mid, "IS", "OOS")
    return tuple(r[per == p].mean() / r[per == p].std() * np.sqrt(252) for p in ("IS", "OOS"))

bh1h = {tk: bh_window(tk, "1h") for tk in ("GC=F", "ES=F")}
bhg14 = bh_window("^GSPC", "g14")

def bh_of(r):
    if r.tf == "1h": return bh1h[r.ticker]
    if r.ticker == "^GSPC" and str(r.param).startswith("từ 2014"): return bhg14
    return B.get((r.ticker, "BL_BH"), (np.nan, np.nan))

df["IS_BH_sh"] = [bh_of(r)[0] for r in df.itertuples()]
df["OOS_BH_sh"] = [bh_of(r)[1] for r in df.itertuples()]
df["OOS_trendBL_sh"] = [np.nanmax([B.get((r.ticker, "BL_Donchian20"), (np.nan, np.nan))[1], B.get((r.ticker, "BL_EMA20/100"), (np.nan, np.nan))[1]])
                        if r.tf == "1d" else np.nan for r in df.itertuples()]
df["IS_trendBL_sh"] = [np.nanmax([B.get((r.ticker, "BL_Donchian20"), (np.nan, np.nan))[0], B.get((r.ticker, "BL_EMA20/100"), (np.nan, np.nan))[0]])
                       if r.tf == "1d" else np.nan for r in df.itertuples()]
for p_ in ("IS", "OOS"):
    pv = df[f"{p_}_p_rand"].fillna(1.0).values
    df[f"{p_}_q"] = bh_fdr(pv)
df["pos_both"] = (df.IS_sharpe > 0) & (df.OOS_sharpe > 0)
df["beat_BH"] = (df.IS_sharpe > df.IS_BH_sh) & (df.OOS_sharpe > df.OOS_BH_sh)
df["beat_trendBL"] = (df.IS_sharpe > df.IS_trendBL_sh) & (df.OOS_sharpe > df.OOS_trendBL_sh)
df["FDR_OOS"] = df.OOS_q < 0.10
df["sig_IS"] = df.IS_p_rand < 0.05
df["PASS"] = df.pos_both & df.beat_BH & df.FDR_OOS & df.sig_IS
df["PASS_loose"] = df.pos_both & (df.OOS_p_rand < 0.05) & (df.IS_p_rand < 0.05)
df.to_csv("results7/all_tests_fdr.csv", index=False)
print("Tổng số phép thử:", len(df), "| OOS q<0.10:", df.FDR_OOS.sum(), "| PASS:", df.PASS.sum(), "| loose:", df.PASS_loose.sum())
pd.set_option("display.width", 280); pd.set_option("display.max_rows", 300)
c = ["direction", "ticker", "tf", "strategy", "param", "fill", "IS_sharpe", "OOS_sharpe", "IS_p_rand", "OOS_p_rand", "OOS_q",
     "IS_BH_sh", "OOS_BH_sh", "OOS_trendBL_sh", "OOS_pf", "OOS_trades", "OOS_maxdd", "beat_BH", "PASS"]
print(df[df.PASS_loose | df.FDR_OOS][c].round(3).to_string())
print(df.groupby("direction").agg(n=("PASS", "size"), pos_both=("pos_both", "sum"), fdr=("FDR_OOS", "sum"), passed=("PASS", "sum"), loose=("PASS_loose", "sum")))
