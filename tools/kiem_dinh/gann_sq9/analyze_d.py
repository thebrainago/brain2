# -*- coding: utf-8 -*-
"""Phân tích Test D: bảng tra xác suất chạm, so sánh Sq9 vs góc lệch / đường cong khoảng cách ATR / Fib, scalp IS→OOS."""
import numpy as np, pandas as pd
from common2 import bh_fdr

rng = np.random.default_rng(1); NB = 1000
R = pd.read_pickle("results4/targets.pkl"); G = pd.read_pickle("results4/grid.pkl")
R = R[[c for c in R.columns if not (c.startswith("first_") and c.count("_") == 2)]]
for c in R.columns:
    if c.startswith(("t_", "cl_")): R[c] = R[c].astype(bool)
GRID = np.arange(0.25, 12.01, 0.25); NG = len(GRID)
HMID = {"1h": 24, "15m": 48, "5m": 144, "1d": 10}
HS = {"1h": [12, 24, 48], "15m": [24, 48, 96], "5m": [72, 144, 288], "1d": [5, 10, 20]}
KEYS = ["ticker", "tf", "D", "conf"]


def curve(g, H):
    M = np.vstack(g[f"g_{H}"].values).astype(float)    # (E, 2*NG): trên rồi dưới
    return M[:, :NG].mean(0), M[:, NG:].mean(0)


def boot_mean(x, cl):
    u, ii = np.unique(cl, return_inverse=True); K = len(u)
    s = np.bincount(ii, x, K); nn = np.bincount(ii, None, K)
    W = rng.multinomial(K, np.ones(K) / K, size=NB).astype(float)
    b = (W @ s) / np.maximum(W @ nn, 1)
    p = max(min(1, 2 * min((b <= 0).mean(), (b >= 0).mean())), 1 / NB)
    return x.mean(), np.percentile(b, 2.5), np.percentile(b, 97.5), p


look, tests = [], []
for key, g in R.groupby(KEYS):
    kd = dict(zip(KEYS, key)); tf = kd["tf"]
    gg = G[(G.ticker == kd["ticker"]) & (G.tf == tf) & (G.D == kd["D"]) & (G.conf == kd["conf"])]
    nev = len(gg)
    if nev < 20: continue
    for H in HS[tf]:
        up, dn = curve(gg, H)
        for (st, side, lab), t in g[g.set.isin(["sq9", "fib", "shift"])].groupby(["set", "side", "label"]):
            if st == "shift": continue
            d = t.dATR.values
            exp = np.interp(np.abs(d), GRID, up if side == "hoi" else dn)
            exp = np.where(np.abs(d) <= GRID[-1], exp, np.nan)   # ngoài lưới 12 ATR: không nội suy (tránh kẹp biên)
            sh = g[(g.set == "shift") & (g.side == side) & (g.label == lab)] if st == "sq9" else None
            rec = dict(kd, H=H, set=st, side=side, label=lab, n=len(t),
                       P=100 * t[f"t_{H}"].mean(), P_clean=100 * t[f"cl_{H}"].mean(),
                       P_shift=100 * sh[f"t_{H}"].mean() if sh is not None else np.nan,
                       P_curve=100 * np.nanmean(exp) if np.isfinite(exp).any() else np.nan,
                       dATR_med=np.median(d), pctDrop_med=100 * t.pctDrop.median(),
                       bars_med=t.loc[t[f"t_{H}"], "bars"].median(), MAE_med=t.loc[t[f"t_{H}"] & (t.bars <= H), "MAE"].median(),
                       MAE_p80=t.loc[t[f"t_{H}"] & (t.bars <= H), "MAE"].quantile(0.8),
                       valid=100 * t.valid.mean())
            if st == "sq9":
                fc = t[f"first_{H}"].value_counts(normalize=True) if f"first_{H}" in t and side == "hoi" else None
                if fc is not None:
                    for v in ("hoi", "tiep", "ca_hai", "khong"): rec["first_" + v] = 100 * fc.get(v, 0)
            look.append(rec)
            if H == HMID[tf]:
                x = t[f"t_{H}"].values.astype(float); cl = t.cluster.values
                okc = np.isfinite(exp)
                if okc.sum() >= 20:
                    m, lo, hi, p = boot_mean((x - exp)[okc], cl[okc])
                    tests.append(dict(rec, baseline="curve", diff=100 * m, lo=100 * lo, hi=100 * hi, p=p))
                if st == "sq9":
                    shm = sh.assign(_v=sh[f"t_{H}"].astype(float)).groupby("c")["_v"].mean()
                    xx = (x - shm.reindex(t.c.values).values).astype(float)
                    m, lo, hi, p = boot_mean(xx, cl)
                    tests.append(dict(rec, baseline="shift", diff=100 * m, lo=100 * lo, hi=100 * hi, p=p))
L_ = pd.DataFrame(look); L_.round(2).to_csv("results4/lookup.csv", index=False)
T_ = pd.DataFrame(tests); T_["q_fdr"] = bh_fdr(T_.p.values); T_.round(4).to_csv("results4/tests.csv", index=False)
print("lookup", len(L_), "tests", len(T_))
for b in ("shift", "curve"):
    for st in ("sq9", "fib"):
        x = T_[(T_.baseline == b) & (T_.set == st)]
        if len(x): print(b, st, "n", len(x), "p<.05", (x.p < .05).sum(), "q<.05", (x.q_fdr < .05).sum(), "q<.05 & dương", ((x.q_fdr < .05) & (x["diff"] > 0)).sum(), "hiệu TB", round(x["diff"].mean(), 2))

# ---------------- Scalp: chọn trên IS, kiểm tra OOS ----------------
sc = []
Rv = R[R.valid & R.set.isin(["sq9", "fib", "shift"])]
for key, g in Rv.groupby(KEYS + ["set", "side", "label"]):
    kd = dict(zip(KEYS + ["set", "side", "label"], key)); tf = kd["tf"]
    ks = [0.25, 0.5, 1.0] if kd["side"] == "hoi" else [0.5, 1.0, 2.0]
    for H in HS[tf]:
        for k in ks:
            col = f"R_{H}_{k}"
            if col not in g: continue
            v = g[col]; ok = v.notna()
            if kd["set"] == "shift":
                gi = g[ok]; vv = gi.groupby("c")[col].mean(); per = gi.groupby("c").period.first()
                isv, oosv = vv[per == "IS"], vv[per == "OOS"]
            else:
                isv, oosv = v[ok & (g.period == "IS")], v[ok & (g.period == "OOS")]
            if len(isv) < 30 or len(oosv) < 30: continue
            sc.append(dict(kd, H=H, SL=k, n_IS=len(isv), n_OOS=len(oosv), R_IS=isv.mean(), R_OOS=oosv.mean(),
                           win_IS=100 * (isv > 0).mean(), win_OOS=100 * (oosv > 0).mean()))
S = pd.DataFrame(sc); S.round(4).to_csv("results4/scalp_all.csv", index=False)
print("scalp combos", len(S))
for st in ("sq9", "fib", "shift"):
    x = S[S.set == st]
    print(st, "combos", len(x), "R_IS>0", (x.R_IS > 0).mean().round(3), "R_OOS>0", (x.R_OOS > 0).mean().round(3), "cả hai >0", ((x.R_IS > 0) & (x.R_OOS > 0)).mean().round(3), "R TB IS/OOS", x.R_IS.mean().round(3), x.R_OOS.mean().round(3))
# Mỗi mã/khung: combo tốt nhất IS (sq9/fib) -> OOS + bootstrap
best = []
for (tk, tf), g in S[S.set.isin(["sq9", "fib"])].groupby(["ticker", "tf"]):
    top = g.sort_values("R_IS", ascending=False).head(5)
    for _, r in top.iterrows():
        t = R[(R.ticker == tk) & (R.tf == tf) & (R.D == r.D) & (R.conf == r.conf) & (R.set == r.set) & (R.side == r.side) & (R.label == r.label) & R.valid & (R.period == "OOS")]
        v = t[f"R_{int(r.H)}_{r.SL}"].dropna()
        m, lo, hi, p = boot_mean(v.values, t.loc[v.index, "cluster"].values)
        best.append(dict(r.to_dict(), OOS_lo=lo, OOS_hi=hi, p_OOS=p))
B = pd.DataFrame(best); B["p_bonf"] = np.minimum(1, B.p_OOS * len(B)); B.round(3).to_csv("results4/scalp_best_IS_to_OOS.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
print(B[["ticker", "tf", "D", "conf", "set", "side", "label", "H", "SL", "n_IS", "n_OOS", "R_IS", "R_OOS", "win_IS", "win_OOS", "OOS_lo", "OOS_hi", "p_OOS"]].round(3).to_string(index=False))
