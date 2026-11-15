# -*- coding: utf-8 -*-
"""
TEST C – XÁC SUẤT ĐI TIẾP (continuation) qua các bậc thang Sq9.
Thang mức: L(j) = (√P + φ + j·δ)², δ = bước/180 (bước 45°, 90°, 180°), P = giá neo.
  sq9   : φ = 0 (đúng Sq9)
  shift : φ ~ U(0, δ) ngẫu nhiên cho mỗi neo (3 lần rút) – baseline 1
  eqpct : thang cách đều theo % với cùng khoảng cách quanh neo: L(j) = P(1 + j·g) – baseline 2
Sự kiện: close[t-1] >= A và close[t] < A − 0.1·ATR (phá xuống; ngược lại cho phá lên). A = mức gần close nhất
  vừa bị phá; B, C, D = 1, 2, 3 bậc tiếp theo cùng hướng phá. Mỗi mức chỉ tính lần phá đầu tiên cho mỗi neo.
Kết quả trong H nến (t+1..t+H): chạm B/C/D (bất kỳ lúc nào, và trước khi close lấy lại A), hồi chạm A,
  close lấy lại A, hồi ≥ 50% bậc A→B (từ đáy tạm), MFE/MAE (×ATR), số nến tới B.
Baseline 3 (vô điều kiện): xác suất một nến bất kỳ cùng trạng thái trend đi được cùng khoảng cách (×ATR)
  theo cùng hướng trong H nến.
Không nhìn trước: trend, ATR, neo đều chỉ dùng dữ liệu tới nến t.
"""
import numpy as np, pandas as pd, sys
sys.path.insert(0, ".")
from sq9_stats import anchor_events
from common2 import load as load_daily, atr_rma, pivots

STEPS = [45, 90, 180]
TOLX = 0.1
R_SHIFT = 3


def ema(x, n):
    a = 2 / (n + 1); out = np.empty(len(x)); out[0] = x[0]
    for i in range(1, len(x)): out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def trend_state(c, n):
    e = ema(c, n); sl = e - np.r_[np.full(5, np.nan), e[:-5]]
    s = np.zeros(len(c), int); s[(c > e) & (sl > 0)] = 1; s[(c < e) & (sl < 0)] = -1
    s[:n] = 0
    return s


def load_1h(tk):
    f = {"GC=F": "data_GCF_1h.pkl", "ES=F": "data_ESF_1h.pkl", "^GSPC": "data_GSPC_1h.pkl"}[tk]
    d = pd.read_pickle(f).dropna(subset=["Open", "High", "Low", "Close"])
    return d


def daily_trend_for_1h(d, fut):
    """Trend D1 (EMA50 + slope) của NGÀY ĐÃ ĐÓNG gần nhất, gán cho từng nến 1h."""
    idx = d.index.tz_convert("America/New_York")
    day = np.array((idx + pd.Timedelta(hours=6)).date if fut else idx.date)
    dc = pd.Series(d.Close.values, index=day).groupby(level=0).last()
    st = pd.Series(trend_state(dc.values, 50), index=dc.index)
    prev = st.shift(1)                        # ngày trước đã đóng
    return prev.reindex(day).fillna(0).astype(int).values


def setup(tk, tf):
    if tf == "1h":
        d = load_1h(tk); fut = tk != "^GSPC"
        c = d.Close.values.astype(float)
        trends = {"EMA200": trend_state(c, 200), "EMA50": trend_state(c, 50), "D1_EMA50": daily_trend_for_1h(d, fut)}
        anchors = {k: anchor_events(d, k, True, left=10, right=5, fut=fut) for k in ("pdc", "dopen", "swh", "swl")}
        Hs = [10, 24, 48]
        times = d.index.tz_convert("America/New_York").tz_localize(None)
        clus = (times.to_period("W").astype(str)).values
        mid = times[len(times) // 2]; period = np.where(times < mid, "IS", "OOS")
    else:
        d = load_daily(tk); fut = tk != "^GSPC"
        c = d.Close.values.astype(float)
        trends = {"EMA200": trend_state(c, 200), "EMA50": trend_state(c, 50)}
        h, l = d.High.values, d.Low.values
        ev = [(p + 20, h[p]) for p in pivots(h, 20, 20, True)] + [(p + 20, l[p]) for p in pivots(l, 20, 20, False)]
        ev = sorted(e for e in ev if e[0] < len(d))
        anchors = {"piv20": ev}
        Hs = [5, 10, 20]
        times = d.index
        clus = times.to_period("M").astype(str).values
        period = np.where(times < pd.Timestamp("2016-01-01"), "IS", "OOS")
    return d, trends, anchors, Hs, clus, period


def ladder_fns(P, kind, step, phi):
    dl = step / 180.0
    if kind == "eqpct":
        g = ((np.sqrt(P) + dl) ** 2 - P) / P
        lev = lambda j: P * (1 + j * g)
        idx = lambda x: (x / P - 1) / g
    else:
        s0 = np.sqrt(P) + phi
        lev = lambda j: np.where(s0 + j * dl > 0, (s0 + j * dl) ** 2, np.nan)
        idx = lambda x: (np.sqrt(np.maximum(x, 0)) - s0) / dl
    return lev, idx


def find_events(o, h, l, c, atr, anchors, kind, step, rng):
    """Trả về mảng sự kiện: t, dir, A, B, C, D, anchor_id."""
    n = len(c); ev_t = np.array([e[0] for e in anchors]); ev_p = np.array([e[1] for e in anchors])
    # neo hiệu lực cho nến t: neo có nến tạo <= t-1
    aid = np.searchsorted(ev_t, np.arange(n) - 1, side="right") - 1
    phis = rng.uniform(0, step / 180.0, len(ev_t)) if kind == "shift" else np.zeros(len(ev_t))
    rows = []; used = set()
    t_all = np.arange(1, n)
    for a in np.unique(aid[aid >= 0]):
        ts = t_all[aid[1:] == a]
        if len(ts) == 0: continue
        P = ev_p[a]
        if kind == "eqpct" and False: pass
        lev, idx = ladder_fns(P, "eqpct" if kind == "eqpct" else "sqrt", step, phis[a])
        cp, cc, tl = c[ts - 1], c[ts], TOLX * atr[ts]
        ok = np.isfinite(tl)
        # phá xuống: A = mức nhỏ nhất >= close+tol, cần A <= close[t-1]
        jA = np.ceil(idx(cc + tl)); A = lev(jA)
        dn = ok & (A <= cp)
        # phá lên: A = mức lớn nhất <= close-tol, cần A >= close[t-1]
        jU = np.floor(idx(cc - tl)); U = lev(jU)
        up = ok & (U >= cp)
        for k in np.flatnonzero(dn):
            key = (a, int(jA[k]), -1)
            if key in used: continue
            used.add(key); j = jA[k]
            rows.append((ts[k], -1, lev(j), lev(j - 1), lev(j - 2), lev(j - 3), a))
        for k in np.flatnonzero(up):
            key = (a, int(jU[k]), 1)
            if key in used: continue
            used.add(key); j = jU[k]
            rows.append((ts[k], 1, lev(j), lev(j + 1), lev(j + 2), lev(j + 3), a))
    return np.array(rows, float).reshape(-1, 7)


def outcomes(h, l, c, atr, E, Hs):
    """Tính kết quả cho mảng sự kiện E (đổi dấu cho phá lên để dùng chung logic phá xuống)."""
    n = len(c); Hm = max(Hs)
    t = E[:, 0].astype(int); keep = (t + Hm < n)
    E = E[keep]; t = t[keep]
    d = E[:, 1]; s = -d                                   # s = +1 nếu phá xuống: giá' = s·giá... dùng x' = −x cho phá lên
    sg = np.where(d == -1, 1.0, -1.0)                     # x' = sg·x : phá xuống giữ nguyên, phá lên đổi dấu
    idx = t[:, None] + 1 + np.arange(Hm)[None, :]
    LO = np.where(sg[:, None] > 0, l[idx], -h[idx]); HI = np.where(sg[:, None] > 0, h[idx], -l[idx])
    CL = sg[:, None] * c[idx]; c0 = sg * c[t]
    A, B, C, D = (sg * E[:, k] for k in (2, 3, 4, 5))
    at = atr[t]
    INF = 10**6
    def first(mask):
        return np.where(mask.any(1), mask.argmax(1), INF)
    fB, fC, fD = first(LO <= B[:, None]), first(LO <= C[:, None]), first(LO <= D[:, None])
    fRec = first(CL > A[:, None]); fTA = first(HI >= A[:, None])
    runmin = np.minimum.accumulate(np.c_[c0, LO[:, :-1]], axis=1)
    fRet = first((HI - runmin) >= 0.5 * (A - B)[:, None])
    out = {"t": t, "dir": d.astype(int), "aid": E[:, 6].astype(int),
           "dA": (A - c0) / at, "dB": (c0 - B) / at, "dC": (c0 - C) / at, "dD": (c0 - D) / at, "stepATR": (A - B) / at}
    for H in Hs:
        out[f"B_{H}"] = fB < H; out[f"C_{H}"] = fC < H; out[f"D_{H}"] = fD < H
        out[f"Bpre_{H}"] = (fB < H) & (fB <= fRec); out[f"Cpre_{H}"] = (fC < H) & (fC <= fRec); out[f"Dpre_{H}"] = (fD < H) & (fD <= fRec)
        out[f"touchA_{H}"] = fTA < H; out[f"closeA_{H}"] = fRec < H; out[f"ret50_{H}"] = fRet < H
        out[f"MFE_{H}"] = (c0 - LO[:, :H].min(1)) / at; out[f"MAE_{H}"] = (HI[:, :H].max(1) - c0) / at
        out[f"barsB_{H}"] = np.where(fB < H, fB + 1, np.nan)
    return pd.DataFrame(out)


def uncond(h, l, c, atr, trends, Hs, df):
    """Baseline 3: P(nến bất kỳ cùng trạng thái trend đi được ≥ khoảng cách sự kiện theo cùng hướng trong H)."""
    n = len(c); res = {}
    for H in Hs:
        valid = np.arange(n) + H < n
        lo = pd.Series(l[::-1]).rolling(H, min_periods=H).min().values[::-1]   # min l[t..t+H-1]
        hi = pd.Series(h[::-1]).rolling(H, min_periods=H).max().values[::-1]
        mlo = np.r_[lo[1:], np.nan]; mhi = np.r_[hi[1:], np.nan]                # t+1..t+H
        Dn = (c - mlo) / atr; Up = (mhi - c) / atr
        for tn, st in trends.items():
            for metric in ("B", "C", "D", "A"):
                res[f"u{metric}_{tn}_{H}"] = np.full(len(df), np.nan)
            for s in (-1, 1):
                m = valid & (st == s) & np.isfinite(Dn) & np.isfinite(Up)
                sDn, sUp = np.sort(Dn[m]), np.sort(Up[m]); N = len(sDn)
                if N == 0: continue
                ev = (st[df.t.values] == s)
                if not ev.any(): continue
                down = df.dir.values == -1
                for metric in ("B", "C", "D"):
                    dist = df["d" + metric].values
                    pdn = 1 - np.searchsorted(sDn, dist, "left") / N   # đi xuống được dist
                    pup = 1 - np.searchsorted(sUp, dist, "left") / N
                    v = np.where(down, pdn, pup)
                    res[f"u{metric}_{tn}_{H}"][ev] = v[ev]
                dist = df["dA"].values                                  # hồi ngược hướng phá
                v = np.where(down, 1 - np.searchsorted(sUp, dist, "left") / N, 1 - np.searchsorted(sDn, dist, "left") / N)
                res[f"uA_{tn}_{H}"][ev] = v[ev]
    return pd.DataFrame(res, index=df.index)


def main():
    rng = np.random.default_rng(5)
    allev = []
    for tf in ("1h", "1d"):
        for tk in ("GC=F", "ES=F", "^GSPC"):
            d, trends, anchors, Hs, clus, period = setup(tk, tf)
            o, h, l, c = (d[x].values.astype(float) for x in ("Open", "High", "Low", "Close"))
            atr = atr_rma(h, l, c)
            for an, evs in anchors.items():
                for step in STEPS:
                    for kind in ["sq9", "eqpct"] + ["shift"] * R_SHIFT:
                        E = find_events(o, h, l, c, atr, evs, kind, step, rng)
                        if len(E) == 0: continue
                        df = outcomes(h, l, c, atr, E, Hs)
                        if kind == "sq9":
                            df = pd.concat([df, uncond(h, l, c, atr, trends, Hs, df)], axis=1)
                        for tn, st in trends.items():
                            df["tr_" + tn] = st[df.t.values]
                        df["cluster"] = clus[df.t.values]; df["period"] = period[df.t.values]
                        df["ticker"], df["tf"], df["anchor"], df["step"], df["ladder"] = tk, tf, an, step, kind
                        allev.append(df)
                    print(tf, tk, an, step, "sự kiện sq9:", sum(len(x) for x in allev[-(2 + R_SHIFT):][:1]), flush=True)
    EV = pd.concat(allev, ignore_index=True)
    EV.to_parquet("results3/events.parquet") if False else EV.to_pickle("results3/events.pkl")
    print("Tổng sự kiện:", len(EV))


if __name__ == "__main__":
    main()
