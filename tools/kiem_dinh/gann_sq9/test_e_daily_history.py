# -*- coding: utf-8 -*-
"""Kiểm tra độ bền theo năm các hành vi ngày (chỉ cần OHLC ngày): GC 2008+, ES/^GSPC 2000+."""
import numpy as np, pandas as pd
from common2 import load, atr_rma
ROUND = {"GC=F": [10, 25, 50], "ES=F": [25, 50], "^GSPC": [25, 50]}
rows = []
for tk in ("GC=F", "ES=F", "^GSPC"):
    d = load(tk); o, h, l, c = (d[x].values for x in ("Open", "High", "Low", "Close"))
    d = d[(d.High > d.Low)]  # bỏ nến hỏng H=L
    o, h, l, c = (d[x].values for x in ("Open", "High", "Low", "Close"))
    atr = atr_rma(h, l, c)
    for i in range(20, len(d)):
        a = atr[i - 1]; pdh, pdl, pdc = h[i - 1], l[i - 1], c[i - 1]; pdm = (pdh + pdl) / 2; O = o[i]
        r = dict(ticker=tk, year=d.index[i].year,
                 PDC_cham=l[i] <= pdc <= h[i], PDH_bi_vuot=h[i] > pdh, PDL_bi_thung=l[i] < pdl,
                 PDH_hoac_PDL=(h[i] > pdh) or (l[i] < pdl), PDH_va_PDL=(h[i] > pdh) and (l[i] < pdl), PDM_cham=l[i] <= pdm <= h[i])
        for k in (0.25, 0.5):
            r[f"+{k}ATR"] = h[i] >= O + k * a; r[f"-{k}ATR"] = l[i] <= O - k * a
            r[f"±{k}ATR_mot_ben"] = r[f"+{k}ATR"] or r[f"-{k}ATR"]; r[f"±{k}ATR_ca_hai"] = r[f"+{k}ATR"] and r[f"-{k}ATR"]
        st = ROUND[tk][0]; up = np.ceil(O / st) * st; dn = np.floor(O / st) * st
        r[f"Tron{st}_gan_nhat_tren"] = h[i] >= (up if up > O else up + st); r[f"Tron{st}_gan_nhat_duoi"] = l[i] <= (dn if dn < O else dn - st)
        r["PDC_dist_atr"] = abs(pdc - O) / a
        rows.append(r)
D = pd.DataFrame(rows)
cols = [c for c in D.columns if c not in ("ticker", "year", "PDC_dist_atr")]
out = []
for tk, g in D.groupby("ticker"):
    by = g.groupby("year")[cols].mean() * 100
    for cname in cols:
        out.append(dict(ticker=tk, hanh_vi=cname, n=len(g), P=100 * g[cname].mean(), P_min_nam=by[cname].min(), P_max_nam=by[cname].max(),
                        sd_theo_nam=by[cname].std(), P_5nam_gan=100 * g[g.year >= g.year.max() - 4][cname].mean()))
O = pd.DataFrame(out).round(1); O.to_csv("results5/daily_history_by_year.csv", index=False)
pd.set_option("display.width", 200); print(O.to_string(index=False))
