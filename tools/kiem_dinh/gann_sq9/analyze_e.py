# -*- coding: utf-8 -*-
"""Phân tích Test E: bản đồ xác suất, ổn định IS/OOS, so với đường cong khoảng cách / mốc giả, điều kiện, scalp."""
import numpy as np, pandas as pd
from common2 import bh_fdr
rng = np.random.default_rng(2); NB = 1000
GRID = np.round(np.arange(0.05, 2.001, 0.05), 2)
T = pd.read_pickle("results5/targets.pkl"); Bh = pd.read_pickle("results5/behaviors.pkl")
G = pd.read_pickle("results5/grid.pkl"); S = pd.read_pickle("results5/scalp.pkl")
T["week"] = pd.to_datetime(T.date).dt.to_period("W").astype(str); Bh["week"] = pd.to_datetime(Bh.date).dt.to_period("W").astype(str)
S["week"] = pd.to_datetime(S.date).dt.to_period("W").astype(str)


def boot_p(x, cl):
    u, ii = np.unique(cl, return_inverse=True); K = len(u)
    s = np.bincount(ii, x, K); nn = np.bincount(ii, None, K)
    W = rng.multinomial(K, np.ones(K) / K, size=NB).astype(float); b = (W @ s) / np.maximum(W @ nn, 1)
    return max(min(1, 2 * min((b <= 0).mean(), (b >= 0).mean())), 1 / NB), np.percentile(b, 2.5), np.percentile(b, 97.5)


# ---------- 1. Đích (target) ----------
out = []
for (tk, mode, ses), g in T.groupby(["ticker", "mode", "session"]):
    gg = G[(G.ticker == tk) & (G["mode"] == mode) & (G.session == ses)]
    up = np.vstack(gg.up.values).mean(0); dn = np.vstack(gg.dn.values).mean(0)
    for tname, t in g.groupby("target"):
        d = t.dist_atr.values; hit = t.hit.values.astype(float)
        exp = np.where(d >= 0, np.interp(d, GRID, up, left=1.0), np.interp(-d, GRID, dn, left=1.0))
        exp = np.where(np.abs(d) <= 2.0, exp, np.nan); ok = np.isfinite(exp)
        rec = dict(ticker=tk, mode=mode, session=ses, target=tname, n=len(t), P=100 * hit.mean(),
                   P_IS=100 * t[t.period == "IS"].hit.mean(), P_OOS=100 * t[t.period == "OOS"].hit.mean(),
                   dist_atr_med=np.median(d), dist_pct_med=t.dist_pct.median(),
                   gio_toi_trung_vi=t.hours.median(), gio_toi_p80=t.hours.quantile(.8),
                   MAE_trung_vi=t.mae_atr.median(), MAE_p80=t.mae_atr.quantile(.8))
        if ok.sum() >= 50 and not tname.startswith(("+", "-")):
            p, lo, hi = boot_p((hit - exp)[ok], t.week.values[ok])
            rec.update(P_kc=100 * exp[ok].mean(), P_on_kc=100 * hit[ok].mean(), hon_kc=100 * (hit[ok] - exp[ok]).mean(), p_kc=p)
        out.append(rec)
TT = pd.DataFrame(out)
m = TT.p_kc.notna(); TT.loc[m, "q_kc"] = bh_fdr(TT.loc[m, "p_kc"].values)
TT["on_dinh"] = ((TT.P_IS - TT.P_OOS).abs() <= 7) & (TT.n >= 150)
TT.round(2).to_csv("results5/targets_map.csv", index=False)

# ---------- 2. Hành vi ----------
ob = []
for (tk, mode, ses, bname), g in Bh.groupby(["ticker", "mode", "session", "behavior"]):
    g = g[g.has == True]
    if len(g) < 50: continue
    hit = g.hit.astype(float).values
    rec = dict(ticker=tk, mode=mode, session=ses, behavior=bname, n=len(g), P=100 * hit.mean(),
               P_IS=100 * g[g.period == "IS"].hit.astype(float).mean(), P_OOS=100 * g[g.period == "OOS"].hit.astype(float).mean(),
               gio_toi_trung_vi=g.hours.median(), MAE_trung_vi=g.mae_atr.median(), MAE_p80=g.mae_atr.quantile(.8))
    br = g.base_rand.astype(float).values
    if np.isfinite(br).sum() > 50:
        ok = np.isfinite(br); p, lo, hi = boot_p((hit - br)[ok], g.week.values[ok])
        rec.update(P_moc_gia=100 * br[ok].mean(), hon_moc_gia=100 * (hit[ok] - br[ok]).mean(), p_moc_gia=p)
    ob.append(rec)
BB = pd.DataFrame(ob)
m = BB.p_moc_gia.notna(); BB.loc[m, "q_moc_gia"] = bh_fdr(BB.loc[m, "p_moc_gia"].values)
BB["on_dinh"] = ((BB.P_IS - BB.P_OOS).abs() <= 7) & (BB.n >= 150)
BB.round(2).to_csv("results5/behaviors_map.csv", index=False)

# ---------- 3. Có điều kiện (neo mở cửa ngày) ----------
cond = []
keyb = ["PDC_cham", "PDH_bi_vuot", "PDL_bi_thung", "PDM_cham", "mo_cua_duoc_cham_lai_sau_gio_dau", "dinh_gio_dau_bi_vuot", "day_gio_dau_bi_thung"]
X = Bh[(Bh.session == "day") & Bh.behavior.isin(keyb)].copy(); X["hit"] = X.hit.astype(float)
for cvar in ("gap", "open_pos", "atr_tercile", "dow", "fh_dir"):
    for (tk, mode, b, cv), g in X.groupby(["ticker", "mode", "behavior", cvar]):
        cond.append(dict(ticker=tk, mode=mode, behavior=b, dieu_kien=cvar, gia_tri=cv, n=len(g), P=100 * g.hit.mean(),
                         P_IS=100 * g[g.period == "IS"].hit.mean(), P_OOS=100 * g[g.period == "OOS"].hit.mean()))
CC = pd.DataFrame(cond).round(1); CC.to_csv("results5/conditional.csv", index=False)

# ---------- 4. Scalp ----------
sc = []
for (tk, mode, ses, st, sl), g in S.groupby(["ticker", "mode", "session", "strat", "SL"]):
    i, o = g[g.period == "IS"].R, g[g.period == "OOS"].R
    if len(i) < 30 or len(o) < 30: continue
    p, lo, hi = boot_p(o.values, g[g.period == "OOS"].week.values)
    sc.append(dict(ticker=tk, mode=mode, session=ses, strat=st, SL=sl, n_IS=len(i), n_OOS=len(o), win_IS=100 * (i > 0).mean(), win_OOS=100 * (o > 0).mean(),
                   R_IS=i.mean(), R_OOS=o.mean(), OOS_lo=lo, OOS_hi=hi, p_OOS=p))
SC = pd.DataFrame(sc); SC["q_fdr"] = bh_fdr(SC.p_OOS.values); SC.round(3).to_csv("results5/scalp_summary.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 300)
print(SC.sort_values("R_OOS", ascending=False).head(25).round(3).to_string(index=False))
print("scalp combos", len(SC), "R_IS>0 & R_OOS>0:", ((SC.R_IS > 0) & (SC.R_OOS > 0)).sum(), "q<0.05 dương:", ((SC.q_fdr < .05) & (SC.R_OOS > 0)).sum())
