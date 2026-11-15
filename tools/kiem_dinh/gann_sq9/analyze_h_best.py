# -*- coding: utf-8 -*-
"""Phân tích sâu ứng viên vòng 7: p gộp 2 nửa (Fisher) + FDR, theo năm, theo giai đoạn 5 năm (suy giảm), stress phí,
loại tuần roll (ES=F không điều chỉnh roll), so B&H cùng phơi nhiễm."""
import numpy as np, pandas as pd
from scipy import stats
from common7 import *
from test_h_meanrev import rule_w

df = pd.read_csv("results7/all_tests_fdr.csv")
pi, po = df.IS_p_rand.fillna(1).clip(1e-6, 1), df.OOS_p_rand.fillna(1).clip(1e-6, 1)
df["p_fisher"] = [stats.combine_pvalues([a, b], method="fisher").pvalue for a, b in zip(pi, po)]
df["q_fisher"] = bh_fdr(df.p_fisher.values)
df["PASS_fisher"] = df.pos_both & (df.q_fisher < 0.10) & (df.IS_p_rand < 0.05) & (df.OOS_p_rand < 0.05)
df.to_csv("results7/all_tests_fdr.csv", index=False)
pd.set_option("display.width", 250)
print("PASS (Fisher-FDR q<0.10, mỗi nửa p<0.05, dương cả 2 nửa):", df.PASS_fisher.sum())
print(df[df.PASS_fisher][["ticker", "strategy", "fill", "IS_sharpe", "OOS_sharpe", "IS_p_rand", "OOS_p_rand", "q_fisher", "beat_BH"]].round(4).to_string())

out = []
CANDS = [("ES=F", "IBS<0.2_1d", "open"), ("ES=F", "IBS<0.2_1d", "close"), ("^GSPC", "IBS<0.2_1d", "open"),
         ("SPY", "IBS<0.2_1d", "close"), ("SPY", "IBS<0.2_1d", "open"), ("ES=F", "IBS<0.1_1d", "close"),
         ("ES=F", "RSI2<10&>SMA200", "open"), ("ES=F", "Low10&>SMA200", "open")]
for tk, r, mode in CANDS:
    d = load_d(tk); w = rule_w(d, r)
    for mult in (1, 4):
        pnl, pos = pnl_daily(d, w, SPREAD[tk] * mult, mode)
        s = pd.Series(pnl, index=d.index)
        rec = dict(ticker=tk, rule=r, fill=mode, cost_x=mult)
        for p_ in ("IS", "OOS"):
            m = d.period.values == p_; mt = metrics(pnl[m], pos[m])
            rec.update({f"{p_}_{k}": mt[k] for k in ("sharpe", "cagr", "maxdd", "pf", "trades", "expo")})
        yr = s.groupby(s.index.year).apply(lambda x: (1 + x).prod() - 1)
        rec["years_pos_pct"] = 100 * (yr > 0).mean(); rec["n_years"] = len(yr)
        for a, b in ((2000, 2004), (2005, 2009), (2010, 2014), (2015, 2019), (2020, 2026)):
            x = s[(s.index.year >= a) & (s.index.year <= b)]
            if len(x) > 200: rec[f"Sh_{a}-{str(b)[2:]}"] = x.mean() / x.std() * np.sqrt(252)
        if tk == "ES=F":   # bỏ các ngày trong cửa sổ roll (ngày 8-21 của tháng 3/6/9/12)
            roll = d.index.month.isin([3, 6, 9, 12]) & (d.index.day >= 8) & (d.index.day <= 21)
            x = s[~roll]; rec["Sh_full_exRoll"] = x.mean() / x.std() * np.sqrt(252)
        rec["Sh_full"] = s.mean() / s.std() * np.sqrt(252)
        out.append(rec)
o = pd.DataFrame(out); o.to_csv("results7/best_candidates_detail.csv", index=False)
print(o.round(3).T.to_string())

# B&H cùng phơi nhiễm (đòn bẩy = expo) để so CAGR công bằng
for tk in ("ES=F", "^GSPC", "SPY"):
    d = load_d(tk); pnl, pos = pnl_daily(d, np.ones(len(d)), SPREAD[tk], "open")
    for p_ in ("IS", "OOS"):
        m = d.period.values == p_; print(tk, p_, "B&H", {k: round(v, 2) for k, v in metrics(pnl[m], pos[m]).items() if k in ("sharpe", "cagr", "maxdd")})
