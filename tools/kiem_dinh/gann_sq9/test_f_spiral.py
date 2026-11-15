# -*- coding: utf-8 -*-
"""
TEST 6 – PHẦN 1: FIBONACCI (GOLDEN) SPIRAL từ pivot lớn (20/20, 60/60), không nhìn trước.
- Tâm = pivot (nến p), neo dùng được từ nến xác nhận conf = p + L.
- Bán kính ban đầu = chân sóng đầu tiên: từ pivot tới cực trị ngược lại trong (p, conf] (đã biết lúc conf).
- r(θ) = a · g^(2θ/π), g = φ (=1.618/¼ vòng); chiều quay: CCW và CW (cả hai quy ước).
- Tỷ lệ giá–thời gian: (A) 1 nến : 1 ATR(conf); (B) theo chân sóng (cao/thời gian chân sóng → góc 45°).
- Sự kiện giá: giá chạm đường xoắn (±0.2 ATR), lần chạm đầu trên mỗi nhánh, có hướng tiếp cận.
  Đo: giữ 5 nến (không close xuyên mức quá 0.2 ATR), hồi ≥1 ATR trong 10 nến trước khi phá.
- Mốc thời gian: nến xoắn ốc cắt trục ngang (giá = giá neo) sau conf; và hình chiếu bán kính khi cắt trục dọc
  (|y| quy ra số nến). Đo: có swing 10/10 trong ±3 nến không.
- Đối chứng (N_RAND lần/neo): g ngẫu nhiên U(1.3, 2.0) bỏ |g−φ|<0.05 ; xoay ngẫu nhiên δ∈U(−π/2,π/2) bỏ |δ|<0.1 ; cả hai.
"""
import sys, numpy as np, pandas as pd
from multiprocessing import Pool
from common6 import load_tf, pivots

PHI = (1 + 5 ** 0.5) / 2
W, TOL, M_HOLD, M_REV, TT = 250, 0.2, 5, 10, 3
import os
N_RAND = int(os.environ.get("N_RAND", 60))
PTS_PER_TURN = 720
FAMS = ["phi", "rand_g", "rand_rot", "rand_both"]


def spiral_xy(a, th0, sdir, g, rmax):
    tmax = min(12 * np.pi, (np.pi / 2) * np.log(max(rmax / a, 1.0001)) / np.log(g))
    npt = max(50, int(tmax / (2 * np.pi) * PTS_PER_TURN))
    th = np.linspace(0, tmax, npt)
    r = a * g ** (2 * th / np.pi); ang = th0 + sdir * th
    return r * np.cos(ang), r * np.sin(ang)


def crossings(x, y, xlo, xhi):
    """Giao của đường gấp khúc (x,y) với các đường thẳng đứng X nguyên trong [xlo,xhi]. Trả (X, Y, branch)."""
    x0, x1, y0, y1 = x[:-1], x[1:], y[:-1], y[1:]
    lo = np.maximum(np.ceil(np.minimum(x0, x1)), xlo); hi = np.minimum(np.floor(np.maximum(x0, x1)), xhi)
    cnt = (hi - lo + 1).astype(int); cnt[cnt < 0] = 0
    # bỏ điểm trùng ở đầu đoạn (tránh đếm 2 lần tại đỉnh nguyên)
    seg = np.flatnonzero(cnt)
    if len(seg) == 0: return np.empty(0), np.empty(0), np.empty(0, int)
    rep = np.repeat(seg, cnt[seg]); off = np.arange(len(rep)) - np.repeat(np.cumsum(cnt[seg]) - cnt[seg], cnt[seg])
    X = lo[rep] + off
    dx = x1[rep] - x0[rep]; dx = np.where(dx == 0, 1e-12, dx)
    Y = y0[rep] + (X - x0[rep]) * (y1[rep] - y0[rep]) / dx
    sgn = np.sign(x1 - x0); br = np.r_[0, np.cumsum(sgn[1:] != sgn[:-1])]
    B = br[rep]
    # bỏ trùng (cùng nhánh, cùng X)
    key = B * 100000 + X.astype(int)
    _, ui = np.unique(key, return_index=True); ui.sort()
    return X[ui], Y[ui], B[ui]


def time_targets(x, y, xlo, xhi):
    out = []
    s = np.sign(y); i = np.flatnonzero((s[:-1] * s[1:] < 0))      # cắt trục ngang
    for k in i:
        xc = x[k] + (x[k + 1] - x[k]) * (-y[k]) / (y[k + 1] - y[k] + 1e-12)
        if xlo <= xc <= xhi: out.append(int(round(xc)))
    s = np.sign(x); i = np.flatnonzero((s[:-1] * s[1:] < 0))      # cắt trục dọc → hình chiếu bán kính
    for k in i:
        rc = abs(y[k]); 
        if xlo <= rc <= xhi: out.append(int(round(rc)))
    return np.unique(out)


def eval_spiral(D, an, sc, sdir, g, dlt, acc, fam, draw):
    h, l, c, atr, piv, n = D["h"], D["l"], D["c"], D["atr"], D["pivcum"], D["n"]
    p, L, P0, unit, a, th0, per = an["p"], an["L"], an["P0"], an["unit"][sc], an["a"][sc], an["th0"][sc], an["per"]
    x, y = spiral_xy(a, th0 + dlt, sdir, g, rmax=W + L + 5)
    xlo, xhi = L + 1, min(L + W, n - 1 - M_REV - p)
    if xhi <= xlo: return
    X, Y, B = crossings(x, y, xlo, xhi)
    pi = 2 * (per == "OOS")
    base = (fam, draw, sc, (sdir + 1) // 2)
    if len(X):
        t = p + X.astype(int); Lv = P0 + Y * unit
        tl = TOL * atr[t - 1]
        tch = (l[t] - tl <= Lv) & (h[t] + tl >= Lv) & (Lv > 0)
        # lần chạm đầu trên mỗi nhánh, không phải điểm đầu của nhánh
        order = np.lexsort((X, B)); Bs, ts, Ls, ch, tls = B[order], t[order], Lv[order], tch[order], tl[order]
        first_of_branch = np.r_[True, Bs[1:] != Bs[:-1]]
        ub, start = np.unique(Bs, return_index=True)
        ev = []
        for bi, st in zip(ub, start):
            en = st + np.searchsorted(Bs[st:], bi, side="right")
            hits = np.flatnonzero(ch[st:en])
            if len(hits) == 0 or hits[0] == 0: continue
            k = st + hits[0]
            if abs(c[ts[k] - 1] - Ls[k]) <= tls[k]: continue
            ev.append(k)
        for k in ev:
            tb, Lk = ts[k], Ls[k]; d = 1.0 if c[tb - 1] > Lk else -1.0
            idx = np.arange(tb, tb + M_REV + 1)
            C, Hh, Ll, At = c[idx], h[idx], l[idx], atr[idx - 1]
            broke = (C < Lk - TOL * At) if d > 0 else (C > Lk + TOL * At)
            fb = broke.argmax() if broke.any() else 99
            ext = (Hh - Lk) if d > 0 else (Lk - Ll); ext = ext.copy(); ext[0] = (C[0] - Lk) * d
            mx = ext[:min(fb, M_REV + 1)].max() if fb > 0 else -1
            acc[base + (pi, 0)] += 1; acc[base + (pi, 1)] += fb > M_HOLD; acc[base + (pi, 2)] += mx >= At[0]
    for X in time_targets(x, y, xlo, xhi - TT - 5):
        tt = p + X
        acc[base + (pi, 3)] += 1; acc[base + (pi, 4)] += (piv[tt + TT + 1] - piv[tt - TT]) > 0


def run(args):
    tk, tf = args
    rng = np.random.default_rng(abs(hash((tk, tf))) % 2**32)
    d = load_tf(tk, tf); h, l, c, atr = (d[k].values for k in ("High", "Low", "Close", "atr")); n = len(c)
    ph, pl = pivots(h, 10, 10, True), pivots(l, 10, 10, False)
    pv = np.zeros(n); pv[ph] = 1; pv[pl] = 1; pivcum = np.r_[0, np.cumsum(pv)]
    D = dict(h=h, l=l, c=c, atr=atr, pivcum=pivcum, n=n)
    anchors = []
    for L in (20, 60):
        for kind, src in (("H", h), ("L", l)):
            for p in pivots(src, L, L, kind == "H"):
                cf = p + L
                if cf + 20 >= n or not np.isfinite(atr[cf]): continue
                seg = slice(p + 1, cf + 1)
                q = p + 1 + (np.argmin(l[seg]) if kind == "H" else np.argmax(h[seg]))
                P0 = src[p]; dyp = (l[q] if kind == "H" else h[q]) - P0; dx = q - p
                if dyp == 0: continue
                units = [atr[cf], abs(dyp) / dx]
                an = dict(p=p, L=L, P0=P0, unit=units, per=d.period.values[cf], a=[], th0=[])
                for u in units:
                    vx, vy = dx, dyp / u; an["a"].append(np.hypot(vx, vy)); an["th0"].append(np.arctan2(vy, vx))
                anchors.append(an)
    acc = np.zeros((4, N_RAND, 2, 2, 4, 5))   # fam, draw, scaling, dir, period(IS=0,OOS=2 → dùng 0/2), metric
    for an in anchors:
        for sc in (0, 1):
            for sdir in (-1, 1):
                eval_spiral(D, an, sc, sdir, PHI, 0.0, acc, 0, 0)
                for j in range(N_RAND):
                    gr = rng.uniform(1.3, 2.0)
                    while abs(gr - PHI) < 0.05: gr = rng.uniform(1.3, 2.0)
                    dl = rng.uniform(-np.pi / 2, np.pi / 2)
                    while abs(dl) < 0.1: dl = rng.uniform(-np.pi / 2, np.pi / 2)
                    eval_spiral(D, an, sc, sdir, gr, 0.0, acc, 1, j)
                    eval_spiral(D, an, sc, sdir, PHI, dl, acc, 2, j)
                    eval_spiral(D, an, sc, sdir, gr, dl, acc, 3, j)
    np.save(f"results6/spiral_acc_{tk.replace('^','').replace('=','')}_{tf}.npy", acc)
    return tk, tf, len(anchors)


if __name__ == "__main__":
    jobs = [("GC=F", "1d"), ("ES=F", "1d"), ("^GSPC", "1d"), ("GC=F", "1h"), ("ES=F", "1h"), ("^GSPC", "1h")]
    if len(sys.argv) > 1: jobs = [tuple(a.split(":")) for a in sys.argv[1:]]
    with Pool(min(6, len(jobs))) as P:
        for r in P.imap_unordered(run, jobs): print(r, flush=True)
