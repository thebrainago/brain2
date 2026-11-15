# -*- coding: utf-8 -*-
"""
TEST A – Mức giá Sq9 từ neo LỚN (pivot 20/20, 60/60, ATH, đỉnh/đáy năm) trên daily.
Mức: góc 45°..1440° (4 vòng = 32 mức mỗi phía), sống 250 nến kể từ nến xác nhận neo (không nhìn trước).
Đo: touch (±0.2 ATR), giữ 5 / 10 nến (không close xuyên qua mức), hồi ≥1 / ≥2 ATR trong 10 nến (trước khi phá).
Đối chứng: (1) ctrlA: cùng neo, góc lệch ngẫu nhiên ±22.5° (3 mẫu/góc);
           (2) randAnc: neo ngẫu nhiên (high/low của 1 nến ngẫu nhiên, cùng độ trễ xác nhận), đúng góc Sq9 (3 neo/neo thật).
Ý nghĩa: bootstrap theo cụm (cluster = neo thật, 2000 lần) cho hiệu Sq9 − đối chứng; p hai phía; FDR (BH) + Bonferroni.
"""
import numpy as np, pandas as pd
from common2 import INSTR, SPLIT, load, atr_rma, major_anchors, sq9, bh_fdr

LIFE, TOL, MAXH, R1, R2, B = 250, 0.2, 10, 3, 3, 2000
ANG = np.arange(45.0, 1440.1, 45.0)
METRICS = ["touch", "hold5", "hold10", "rev1", "rev2"]


def eval_levels(o, h, l, c, atr, conf, Ls):
    """Trả về mảng (K, 5) các chỉ tiêu 0/1 (nan nếu không áp dụng) cho các mức Ls tạo tại nến conf."""
    n = len(c); s, e = conf + 1, conf + LIFE
    lo, hi, tl = l[s:e + 1], h[s:e + 1], TOL * atr[s:e + 1]
    T = (lo[None, :] <= Ls[:, None] + tl[None, :]) & (hi[None, :] >= Ls[:, None] - tl[None, :])
    touched = T.any(1); tb = s + T.argmax(1)
    out = np.full((len(Ls), 5), np.nan); out[:, 0] = touched
    k = np.flatnonzero(touched)
    if len(k) == 0: return out
    tbk = tb[k]; L = Ls[k]
    d = np.where(c[tbk - 1] >= L, 1.0, -1.0)
    idx = np.clip(tbk[:, None] + np.arange(MAXH + 1)[None, :], 0, n - 1)
    C, Hh, Ll, At = c[idx], h[idx], l[idx], atr[idx]
    tolm = TOL * At
    broke = np.where(d[:, None] == 1, C < L[:, None] - tolm, C > L[:, None] + tolm)
    first_brk = np.where(broke.any(1), broke.argmax(1), 99)
    out[k, 1] = first_brk > 5
    out[k, 2] = first_brk > 10
    ext = np.where(d[:, None] == 1, Hh - L[:, None], L[:, None] - Ll)
    ext[:, 0] = (C[:, 0] - L) * d                       # nến chạm: chỉ tính close
    mask = np.arange(MAXH + 1)[None, :] < np.minimum(first_brk, MAXH + 1)[:, None]
    mx = np.where(mask, ext, -np.inf).max(1)
    out[k, 3] = mx >= 1.0 * At[:, 0]
    out[k, 4] = mx >= 2.0 * At[:, 0]
    return out


def run_instrument(tk, rng):
    d = load(tk); o, h, l, c = (d[x].values.astype(float) for x in ("Open", "High", "Low", "Close"))
    atr = atr_rma(h, l, c); n = len(c)
    anchors = [a for a in major_anchors(d) if a["conf"] + LIFE + MAXH < n and np.isfinite(atr[a["conf"]])]
    rows = []
    for ai, a in enumerate(anchors):
        cf = a["conf"]; per = "IS" if d.index[cf] < SPLIT else "OOS"
        base = dict(ticker=tk, aid=ai, atype=a["type"], kind=a["kind"], p=a["p"], period=per)
        # 1) Sq9 thật
        angs = np.r_[ANG, ANG]; sides = np.r_[np.ones(len(ANG)), -np.ones(len(ANG))]
        Ls = sq9(a["price"], angs, sides); ok = np.isfinite(Ls)
        r = eval_levels(o, h, l, c, atr, cf, Ls[ok])
        rows.append(dict(base, group="sq9", **{m: r[:, j] for j, m in enumerate(METRICS)}))
        # 2) cùng neo, góc lệch ngẫu nhiên ±22.5°
        ja = np.repeat(angs, R1) + rng.uniform(-22.5, 22.5, len(angs) * R1)
        Ls = sq9(a["price"], ja, np.repeat(sides, R1)); ok = np.isfinite(Ls)
        r = eval_levels(o, h, l, c, atr, cf, Ls[ok])
        rows.append(dict(base, group="ctrlA", **{m: r[:, j] for j, m in enumerate(METRICS)}))
        # 3) neo ngẫu nhiên, đúng góc Sq9
        lag = cf - a["p"]
        rr = []
        for _ in range(R2):
            q = rng.integers(60, n - 1 - lag - LIFE - MAXH)
            pr = h[q] if a["kind"] == "H" else l[q]
            Ls = sq9(pr, angs, sides); ok = np.isfinite(Ls)
            if np.isfinite(atr[q + lag]): rr.append(eval_levels(o, h, l, c, atr, q + lag, Ls[ok]))
        r = np.vstack(rr)
        rows.append(dict(base, group="randAnc", **{m: r[:, j] for j, m in enumerate(METRICS)}))
    return rows


def agg(rows):
    """Bảng cụm: mỗi (neo, nhóm) -> tử/mẫu cho từng chỉ tiêu."""
    out = []
    for r in rows:
        rec = {k: r[k] for k in ("ticker", "aid", "atype", "kind", "p", "period", "group")}
        for m in METRICS:
            v = r[m]; v = v[np.isfinite(v)]
            rec[m + "_n"] = v.sum(); rec[m + "_d"] = len(v)
        out.append(rec)
    return pd.DataFrame(out)


def compare(D, rng, label):
    """D: bảng cụm cho 1 tập neo. Trả các dòng so sánh Sq9 vs ctrlA / randAnc."""
    res = []
    piv = {g: D[D.group == g].set_index("cid") for g in ("sq9", "ctrlA", "randAnc")}
    cids = piv["sq9"].index.values; C = len(cids)
    if C < 5: return res
    W = rng.multinomial(C, np.ones(C) / C, size=B).astype(float)
    for m in METRICS:
        S = piv["sq9"].loc[cids]; rs = S[m + "_n"].sum() / max(S[m + "_d"].sum(), 1)
        for g in ("ctrlA", "randAnc"):
            G = piv[g].loc[cids]; rg = G[m + "_n"].sum() / max(G[m + "_d"].sum(), 1)
            bs = (W @ S[m + "_n"].values) / np.maximum(W @ S[m + "_d"].values, 1)
            bg = (W @ G[m + "_n"].values) / np.maximum(W @ G[m + "_d"].values, 1)
            diff = bs - bg
            p = min(1.0, 2 * min((diff <= 0).mean(), (diff >= 0).mean()))
            p = max(p, 1.0 / B)
            res.append(dict(set=label, metric=m, baseline=g, anchors=C, n_sq9=int(S[m + "_d"].sum()),
                            sq9=100 * rs, base=100 * rg, diff=100 * (rs - rg),
                            ci_lo=100 * np.percentile(diff, 2.5), ci_hi=100 * np.percentile(diff, 97.5), p=p))
    return res


def main():
    rng = np.random.default_rng(7)
    allrows = []
    for tk in INSTR:
        rows = run_instrument(tk, rng); allrows += rows
        print(tk, "neo:", len(rows) // 3, flush=True)
    D = agg(allrows)
    # Cụm = neo duy nhất theo (mã, kind, p) để tránh đếm trùng pivot 20 và 60
    D["cid"] = D.ticker + "|" + D.kind + "|" + D.p.astype(str)
    D.to_csv("results2/testA_clusters.csv", index=False)
    res = []
    for tk in INSTR:
        X = D[D.ticker == tk]
        for per in ("ALL", "IS", "OOS"):
            Y = X if per == "ALL" else X[X.period == per]
            # gộp neo duy nhất: cộng dồn theo cid
            Z = Y.groupby(["cid", "group"], as_index=False)[[m + s for m in METRICS for s in ("_n", "_d")]].first()
            res += [dict(ticker=tk, period=per, **r) for r in compare(Z, rng, "ALL_MAJOR")]
        for at in sorted(X.atype.unique()):
            Y = X[X.atype == at]
            res += [dict(ticker=tk, period="ALL", **r) for r in compare(Y, rng, at)]
    R = pd.DataFrame(res)
    R["q_fdr"] = bh_fdr(R.p.values); R["p_bonf"] = np.minimum(1, R.p * len(R))
    R.round(4).to_csv("results2/testA_results.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
    print(R[R.set == "ALL_MAJOR"].round(3).to_string(index=False))
    print("Số phép thử:", len(R), " p<0.05:", (R.p < 0.05).sum(), " q<0.05:", (R.q_fdr < 0.05).sum(), " Bonf<0.05:", (R.p_bonf < 0.05).sum())


if __name__ == "__main__":
    main()
