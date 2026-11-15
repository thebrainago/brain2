# -*- coding: utf-8 -*-
"""
TEST B – Sq9 THỜI GIAN từ neo lớn (pivot 20/20, 60/60, ATH, đỉnh/đáy năm, đã xác nhận) trên daily.
Mục tiêu (đếm từ NẾN PIVOT, chỉ tính mục tiêu nằm SAU nến xác nhận, tối đa 400):
  V1a spoke : n mà √n ≡ √P (mod 2)  – cùng "nan hoa" với giá pivot trên xoắn ốc Sq9
  V1b cross : n mà √n ≡ √P (mod 0.5) – các góc 90° tính từ vị trí giá pivot
  V2  spokes: các số nằm trên 8 nan hoa Sq9 (chéo + chữ thập): (2k+1)², 4k²+1, 4k²±2k+1, 4k²±k+1, 4k²±3k+1
  V3  p2t   : giá ↔ thời gian: |Sq9(Ps, góc) − Ps| với Ps = giá pivot đưa về [100,1000), góc 45..1440
Đơn vị: số nến giao dịch ("bars") và số ngày lịch ("cal").
Sự kiện: có pivot nhỏ 5/5 (đỉnh hoặc đáy) trong ±T (T = 1, 2) quanh mục tiêu.
Baseline: hoán vị – dời TOÀN BỘ tập mục tiêu của mỗi neo một đoạn ngẫu nhiên s ∈ [−30, 30], |s| > 2T
          (giữ nguyên khoảng cách giữa các mục tiêu), 2000 lần; p một phía = (1 + #null ≥ thực)/(1 + 2000).
Hợp lưu giá + thời gian: pivot nhỏ trùng mục tiêu thời gian có nằm gần mức giá Sq9 (±0.2 ATR) hơn pivot khác không?
"""
import numpy as np, pandas as pd
from scipy.stats import fisher_exact
from common2 import INSTR, SPLIT, load, atr_rma, major_anchors, pivots, sq9, bh_fdr

MAXN, NPERM, SMAX = 400, 2000, 30


def targets(P, variant):
    if variant in ("V1a", "V1b"):
        step = 2.0 if variant == "V1a" else 0.5
        f = np.sqrt(P) % step
        n = (f + step * np.arange(0, 60)) ** 2
    elif variant == "V2":
        k = np.arange(1, 11)[:, None]
        n = np.hstack([(2 * k + 1) ** 2, 4 * k**2 + 1, 4 * k**2 - 2 * k + 1, 4 * k**2 + 2 * k + 1,
                       4 * k**2 - k + 1, 4 * k**2 + k + 1, 4 * k**2 - 3 * k + 1, 4 * k**2 + 3 * k + 1]).ravel().astype(float)
    else:  # V3
        Ps = P
        while Ps >= 1000: Ps /= 10
        while Ps < 100: Ps *= 10
        A = np.arange(45.0, 1440.1, 45.0)
        n = np.abs(np.r_[sq9(Ps, A, 1), sq9(Ps, A, -1)] - Ps)
    n = np.unique(np.round(n[np.isfinite(n)]).astype(int))
    return n[(n >= 1) & (n <= MAXN)]


def near_array(flags, T):
    """near[i] = có sự kiện trong [i−T, i+T]."""
    cs = np.r_[0, np.cumsum(flags)]; n = len(flags); i = np.arange(n)
    return (cs[np.minimum(i + T + 1, n)] - cs[np.maximum(i - T, 0)]) > 0


def main():
    rng = np.random.default_rng(11)
    res, conf_rows = [], []
    for tk in INSTR:
        d = load(tk); h, l, c = d.High.values, d.Low.values, d.Close.values; n = len(c)
        atr = atr_rma(h, l, c)
        # neo lớn duy nhất theo (kind, p); conf = sớm nhất
        A = {}
        for a in major_anchors(d):
            key = (a["kind"], a["p"])
            if key not in A or a["conf"] < A[key]["conf"]: A[key] = a
        anchors = sorted(A.values(), key=lambda a: a["p"])
        # sự kiện: pivot nhỏ 5/5
        ph = pivots(h, 5, 5, True); pl = pivots(l, 5, 5, False)
        ev = np.zeros(n, bool); ev[ph] = True; ev[pl] = True
        day0 = d.index[0]; dayn = (d.index - day0).days.values; ND = dayn[-1] + 1
        evd = np.zeros(ND + MAXN + SMAX + 5, bool); evd[dayn[ev]] = True
        last_valid_bar = n - 1 - 5; last_valid_day = dayn[last_valid_bar]
        for unit in ("bars", "cal"):
            for var in ("V1a", "V1b", "V2", "V3"):
                # mảng (neo, mục tiêu): vị trí gốc, ngưỡng conf
                rows = []
                for ai, a in enumerate(anchors):
                    tg = targets(a["price"], var)
                    if unit == "bars": base, cf, lim = a["p"], a["conf"], last_valid_bar
                    else: base, cf, lim = dayn[a["p"]], dayn[a["conf"]], last_valid_day
                    per = 0 if d.index[a["conf"]] < SPLIT else 1
                    for t in tg: rows.append((ai, base + t, cf, lim, per))
                R = np.array(rows); aid, pos, cf, lim, per = R.T
                na_ = len(anchors)
                for T in (1, 2):
                    near = near_array(ev, T) if unit == "bars" else near_array(evd, T)
                    def hitstat(shift):
                        q = pos + shift
                        ok = (q > cf) & (q <= lim)
                        hv = np.zeros(len(q)); hv[ok] = near[q[ok]]
                        out = []
                        for pm in (None, 0, 1):
                            m = ok if pm is None else ok & (per == pm)
                            out.append((hv[m].sum(), m.sum()))
                        return out
                    obs = hitstat(np.zeros(len(pos), int))
                    nulls = np.zeros((NPERM, 3))
                    choices = np.r_[np.arange(-SMAX, -2 * T), np.arange(2 * T + 1, SMAX + 1)]
                    for b in range(NPERM):
                        s = rng.choice(choices, na_)[aid]
                        nulls[b] = [x / max(y, 1) for x, y in hitstat(s)]
                    for j, pname in enumerate(("ALL", "IS", "OOS")):
                        hr = obs[j][0] / max(obs[j][1], 1)
                        p = (1 + (nulls[:, j] >= hr).sum()) / (1 + NPERM)
                        res.append(dict(ticker=tk, unit=unit, variant=var, T=T, period=pname, targets=int(obs[j][1]),
                                        hit=100 * hr, base=100 * nulls[:, j].mean(), diff=100 * (hr - nulls[:, j].mean()),
                                        null_sd=100 * nulls[:, j].std(), p=p))
                print(tk, unit, var, "xong", flush=True)
        # ---- Hợp lưu giá + thời gian (bars, union mục tiêu V1a/V1b/V2/V3, T = 1) ----
        A_ = np.arange(45.0, 1440.1, 45.0)
        evidx = np.flatnonzero(ev)
        for a in anchors:
            tg = np.unique(np.concatenate([targets(a["price"], v) for v in ("V1a", "V1b", "V2", "V3")])) + a["p"]
            tflag = np.zeros(n + MAXN + 5, bool); tflag[tg] = True
            tnear = near_array(tflag, 1)
            lv_sq = np.r_[sq9(a["price"], A_, 1), sq9(a["price"], A_, -1)]
            lv_md = np.r_[sq9(a["price"], A_ - 22.5, 1), sq9(a["price"], A_ - 22.5, -1)]
            lv_sq = lv_sq[np.isfinite(lv_sq)]; lv_md = lv_md[np.isfinite(lv_md)]
            for e in evidx[(evidx > a["conf"]) & (evidx <= a["p"] + MAXN) & (evidx <= n - 6)]:
                px = h[e] if ev[e] and e in set(ph) else l[e]
                tol = 0.2 * atr[e]
                conf_rows.append(dict(ticker=tk, at_target=bool(tnear[e]),
                                      near_sq9=bool((np.abs(lv_sq - px) <= tol).any()),
                                      near_mid=bool((np.abs(lv_md - px) <= tol).any()),
                                      period="IS" if d.index[e] < SPLIT else "OOS"))
    R = pd.DataFrame(res); R["q_fdr"] = bh_fdr(R.p.values); R["p_bonf"] = np.minimum(1, R.p * len(R))
    R.round(4).to_csv("results2/testB_time_results.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
    print(R[R.period == "ALL"].round(3).to_string(index=False))
    print("Số phép thử:", len(R), " p<0.05:", (R.p < 0.05).sum(), " q<0.05:", (R.q_fdr < 0.05).sum(), " Bonf<0.05:", (R.p_bonf < 0.05).sum())
    Cf = pd.DataFrame(conf_rows); Cf.to_csv("results2/testB_confluence_pivots.csv", index=False)
    out = []
    for tk, g in Cf.groupby("ticker"):
        at, nt = g[g.at_target], g[~g.at_target]
        tab = [[at.near_sq9.sum(), len(at) - at.near_sq9.sum()], [nt.near_sq9.sum(), len(nt) - nt.near_sq9.sum()]]
        _, p1 = fisher_exact(tab, alternative="greater")
        # trong nhóm trùng mục tiêu: gần mức Sq9 vs gần mức lệch 22.5° (McNemar chính xác)
        b_ = int((at.near_sq9 & ~at.near_mid).sum()); c_ = int((~at.near_sq9 & at.near_mid).sum())
        from scipy.stats import binomtest
        p2 = binomtest(b_, b_ + c_, 0.5, alternative="greater").pvalue if b_ + c_ else 1.0
        out.append(dict(ticker=tk, pivots=len(g), at_target=len(at), near_sq9_at_target=100 * at.near_sq9.mean(),
                        near_sq9_not_target=100 * nt.near_sq9.mean(), near_mid_at_target=100 * at.near_mid.mean(),
                        p_target_vs_not=p1, p_sq9_vs_mid=p2))
    O = pd.DataFrame(out).round(4); O.to_csv("results2/testB_confluence.csv", index=False); print(O.to_string(index=False))


if __name__ == "__main__":
    main()
