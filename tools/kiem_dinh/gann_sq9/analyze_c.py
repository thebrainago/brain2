# -*- coding: utf-8 -*-
"""Phân tích Test C: so sánh Sq9 với baseline (shift, eqpct, vô điều kiện), bootstrap theo cụm (tuần/tháng), FDR."""
import numpy as np, pandas as pd
from common2 import bh_fdr

NB = 1000
rng = np.random.default_rng(3)
EV = pd.read_pickle("results3/events.pkl")
PROP = ["B", "C", "D", "Bpre", "Cpre", "Dpre", "touchA", "closeA", "ret50"]
UNC = {"B": "uB", "C": "uC", "D": "uD", "touchA": "uA"}
HMID = {"1h": 24, "1d": 10}


def boot_diff(cl_x, x, cl_y, y, clusters):
    """Hiệu trung bình x − y, bootstrap cụm (cùng trọng số cụm cho 2 nhóm)."""
    ci = {c: i for i, c in enumerate(clusters)}; K = len(clusters)
    def sums(cl, v):
        ii = np.array([ci[c] for c in cl]); s = np.bincount(ii, v, K); n = np.bincount(ii, None, K); return s, n
    sx, nx = sums(cl_x, x); sy, ny = sums(cl_y, y)
    W = rng.multinomial(K, np.ones(K) / K, size=NB).astype(float)
    bx = (W @ sx) / np.maximum(W @ nx, 1); by = (W @ sy) / np.maximum(W @ ny, 1)
    diff = bx - by
    p = max(min(1.0, 2 * min((diff <= 0).mean(), (diff >= 0).mean())), 1 / NB)
    return x.mean() - y.mean(), np.percentile(diff, 2.5), np.percentile(diff, 97.5), p


def cells(EV, pool_anchor):
    rows = []
    keys = ["ticker", "tf", "step"] + ([] if pool_anchor else ["anchor"])
    for key, g in EV.groupby(keys):
        kd = dict(zip(keys, key)); tf = kd["tf"]
        Hs = [10, 24, 48] if tf == "1h" else [5, 10, 20]
        trends = ["EMA200", "EMA50", "D1_EMA50"] if tf == "1h" else ["EMA200", "EMA50"]
        for tn in trends:
            st = g["tr_" + tn].values
            for case in ("with", "counter"):
                m = (st != 0) & ((g.dir.values == st) if case == "with" else (g.dir.values == -st))
                G = g[m]
                if (G.ladder == "sq9").sum() < 30: continue
                S, SH, EQ = G[G.ladder == "sq9"], G[G.ladder == "shift"], G[G.ladder == "eqpct"]
                clusters = np.unique(G.cluster.values)
                for H in Hs:
                    base = dict(kd, trend=tn, case=case, H=H, n_sq9=len(S), n_shift=len(SH), n_eq=len(EQ),
                                n_IS=int((S.period == "IS").sum()), n_OOS=int((S.period == "OOS").sum()))
                    rec = dict(base)
                    for mt in PROP:
                        col = f"{mt}_{H}"
                        rec[mt] = 100 * S[col].mean(); rec[mt + "_shift"] = 100 * SH[col].mean(); rec[mt + "_eq"] = 100 * EQ[col].mean()
                        rec[mt + "_IS"] = 100 * S[S.period == "IS"][col].mean(); rec[mt + "_OOS"] = 100 * S[S.period == "OOS"][col].mean()
                    for mt, u in UNC.items():
                        rec[mt + "_unc"] = 100 * np.nanmean(S[f"{u}_{tn}_{H}"].values)
                    rec["MFE_med"] = S[f"MFE_{H}"].median(); rec["MAE_med"] = S[f"MAE_{H}"].median()
                    rec["barsB_med"] = np.nanmedian(S[f"barsB_{H}"].values) if S[f"B_{H}"].any() else np.nan
                    rec["stepATR_med"] = S.stepATR.median()
                    rows.append(rec)
    return pd.DataFrame(rows)


def tests(EV, pool_anchor):
    """Các phép kiểm định (chỉ H giữa để giới hạn số phép)."""
    out = []
    keys = ["ticker", "tf", "step"] + ([] if pool_anchor else ["anchor"])
    for key, g in EV.groupby(keys):
        kd = dict(zip(keys, key)); tf = kd["tf"]; H = HMID[tf]
        trends = ["EMA200", "EMA50", "D1_EMA50"] if tf == "1h" else ["EMA200", "EMA50"]
        for tn in trends:
            st = g["tr_" + tn].values
            for case in ("with", "counter"):
                m = (st != 0) & ((g.dir.values == st) if case == "with" else (g.dir.values == -st))
                G = g[m]; S = G[G.ladder == "sq9"]
                if len(S) < 30: continue
                clusters = np.unique(G.cluster.values)
                for per in ("ALL", "IS", "OOS"):
                    Gp = G if per == "ALL" else G[G.period == per]; Sp = Gp[Gp.ladder == "sq9"]
                    if len(Sp) < 30: continue
                    for mt in ["B", "C", "D", "Bpre", "touchA", "closeA", "ret50"]:
                        col = f"{mt}_{H}"
                        for bname in ("shift", "eqpct"):
                            Bp = Gp[Gp.ladder == bname]
                            dfx = boot_diff(Sp.cluster.values, Sp[col].values.astype(float), Bp.cluster.values, Bp[col].values.astype(float), clusters)
                            out.append(dict(kd, trend=tn, case=case, period=per, H=H, metric=mt, baseline=bname, n=len(Sp),
                                            sq9=100 * Sp[col].mean(), base=100 * Bp[col].mean(), diff=100 * dfx[0], lo=100 * dfx[1], hi=100 * dfx[2], p=dfx[3]))
                    for mt, u in UNC.items():
                        col = f"{mt}_{H}"; uu = Sp[f"{u}_{tn}_{H}"].values
                        ok = np.isfinite(uu); x = Sp[col].values.astype(float)[ok]; y = uu[ok]; cl = Sp.cluster.values[ok]
                        dfx = boot_diff(cl, x, cl, y, clusters)
                        out.append(dict(kd, trend=tn, case=case, period=per, H=H, metric=mt, baseline="uncond", n=int(ok.sum()),
                                        sq9=100 * x.mean(), base=100 * y.mean(), diff=100 * dfx[0], lo=100 * dfx[1], hi=100 * dfx[2], p=dfx[3]))
    T = pd.DataFrame(out)
    return T


if __name__ == "__main__":
    C1 = cells(EV, True); C1.round(2).to_csv("results3/lookup_pooled_anchors.csv", index=False)
    C2 = cells(EV, False); C2.round(2).to_csv("results3/lookup_by_anchor.csv", index=False)
    T1 = tests(EV, True); T2 = tests(EV, False)
    T1["level"] = "pooled"; T2["level"] = "by_anchor"
    T = pd.concat([T1, T2], ignore_index=True)
    T["q_fdr"] = bh_fdr(T.p.values); T["p_bonf"] = np.minimum(1, T.p * len(T))
    T.round(4).to_csv("results3/tests.csv", index=False)
    print("cells", len(C1), len(C2), "tests", len(T))
