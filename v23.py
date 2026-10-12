# -*- coding: utf-8 -*-
"""Vong 23: 15 script TradingView (BAN DICH THEO MO TA CONG KHAI, khong dung ma Pine) + ghep cheo. Dang ky: reports/vong23_tien_dang_ky.md. MO PHONG."""
from __future__ import annotations

import json
import sys
from multiprocessing import Pool

import numpy as np
import pandas as pd

import mua_vu as MV
import v17_fx as F
import v19
import v22

NAN = np.nan


# ---------------- chi bao ----------------
def ema(x, n): return pd.Series(x).ewm(span=n, adjust=False).mean().to_numpy()
def sma(x, n): return pd.Series(x).rolling(n).mean().to_numpy()


def atr(h, l, c, n=14):
    pc = np.r_[c[0], c[:-1]]; tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    return pd.Series(tr).ewm(alpha=1 / n, adjust=False).mean().to_numpy()


def rsi(c, n):
    d = np.diff(c, prepend=c[0]); up = pd.Series(np.clip(d, 0, None)).ewm(alpha=1 / n, adjust=False).mean()
    dn = pd.Series(np.clip(-d, 0, None)).ewm(alpha=1 / n, adjust=False).mean(); return (100 - 100 / (1 + up / dn.replace(0, 1e-12))).to_numpy()


def supertrend(h, l, c, n, m):
    a = atr(h, l, c, n); hl = (h + l) / 2; ub = hl + m * a; lb = hl - m * a; N = len(c)
    fu, fl, d = ub.copy(), lb.copy(), np.ones(N)
    for i in range(1, N):
        fu[i] = ub[i] if (ub[i] < fu[i - 1] or c[i - 1] > fu[i - 1]) else fu[i - 1]
        fl[i] = lb[i] if (lb[i] > fl[i - 1] or c[i - 1] < fl[i - 1]) else fl[i - 1]
        d[i] = 1 if c[i] > fu[i - 1] else (-1 if c[i] < fl[i - 1] else d[i - 1])
    return d, np.where(d > 0, fl, fu)


def linreg(c, n):
    x = np.arange(n); xm = x.mean(); w = (x - xm) / ((x - xm) ** 2).sum()
    s = pd.Series(c); slope = s.rolling(n).apply(lambda y: (w * y).sum(), raw=True).to_numpy()
    return s.rolling(n).mean().to_numpy() + slope * (n - 1 - xm), slope


def dmi(h, l, c, n=14):
    up = np.diff(h, prepend=h[0]); dn = -np.diff(l, prepend=l[0])
    pdm = np.where((up > dn) & (up > 0), up, 0); mdm = np.where((dn > up) & (dn > 0), dn, 0); a = atr(h, l, c, n)
    f = lambda x: pd.Series(x).ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    return f(pdm) / a, f(mdm) / a


def pivots(h, l, n):
    """pivot cao/thap tai i-n, chi biet tai nen i (khong nhin truoc)."""
    H = pd.Series(h).rolling(2 * n + 1).max().to_numpy(); L = pd.Series(l).rolling(2 * n + 1).min().to_numpy()
    ph = np.r_[np.zeros(n, bool), (h[:-n] == H[n:])] if n else None; pl = np.r_[np.zeros(n, bool), (l[:-n] == L[n:])]
    ph = np.zeros(len(h), bool); pl2 = np.zeros(len(h), bool)
    for i in range(2 * n, len(h)):
        ph[i] = h[i - n] == H[i]; pl2[i] = l[i - n] == L[i]
    return ph, pl2   # ph[i]=True: nen i-n la pivot cao, xac nhan tai i


def gio_ny(idx):
    return idx - pd.Timedelta(hours=7)


def htf_ffill(d, quy, f):
    """f(df lon) -> mang; gia tri nen lon chi dung tu nen lon KE TIEP (da dong)."""
    g = d.resample(quy, label="left", closed="left").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    v = pd.Series(f(g), index=g.index).shift(1)
    return v.reindex(d.index, method="ffill").to_numpy()


LON = {"M5": "1h", "M15": "1h", "H1": "4h", "H4": "1D", "D1": "W-FRI"}
LON_HTF = {"M5": "4h", "M15": "4h", "H1": "4h", "H4": "1D", "D1": "W-FRI"}


# ---------------- may mo phong chung ----------------
def sim(d, S, sp, A):
    """S: sig, sl (muc gia), tp (muc gia/NaN), be_r, tr (None|('atr',m,startR)|('chand',n,m)|('line',arr)|('orb',)), ex (mang, -huong => thoat), H (so nen toi da)."""
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close"))
    ngay = d.index.normalize().asi8 // 86_400_000_000_000; n = len(c); out = []; i = 1
    sig, SL, TP = S["sig"], S["sl"], S["tp"]; be_r = S.get("be_r"); tr = S.get("tr"); ex = S.get("ex"); H = S.get("H", 500)
    while i < n - 2:
        s = sig[i]
        if s == 0 or not np.isfinite(A[i]): i += 1; continue
        j = i + 1; E = o[j] + sp[j] if s > 0 else o[j]; st = SL[i]
        if np.isfinite(st) and ((s > 0 and st >= E) or (s < 0 and st <= E)): i += 1; continue
        R = abs(E - st) if np.isfinite(st) else A[i]; tp = TP[i]
        if np.isfinite(tp) and ((s > 0 and tp <= E) or (s < 0 and tp >= E)): i += 1; continue
        if not np.isfinite(st): st = -np.inf if s > 0 else np.inf
        best = c[j]; k = j; X = None; be = False
        while k < n - 1:
            if s > 0:
                if l[k] <= st: X = min(st, o[k]) if k > j else st; break
                if np.isfinite(tp) and h[k] >= tp and k > j: X = max(tp, o[k]); break
            else:
                if h[k] + sp[k] >= st: X = max(st, o[k] + sp[k]) if k > j else st; break
                if np.isfinite(tp) and l[k] + sp[k] <= tp and k > j: X = min(tp, o[k] + sp[k]); break
            best = max(best, c[k]) if s > 0 else min(best, c[k]); a = A[k]; lai = (c[k] - E) * s
            keo = (lambda m: max(st, m)) if s > 0 else (lambda m: min(st, m))
            if be_r is not None and lai >= be_r * R: be = True
            if be: st = keo(E)
            if tr is not None:
                if tr[0] == "atr" and (best - E) * s >= tr[2] * R: st = keo(best - s * tr[1] * a)
                elif tr[0] == "chand":
                    w = slice(max(j, k - tr[1] + 1), k + 1); st = keo(h[w].max() - tr[2] * a if s > 0 else l[w].min() + tr[2] * a)
                elif tr[0] == "line" and np.isfinite(tr[1][k]): st = keo(tr[1][k])
                elif tr[0] == "orb":
                    m = 3 if lai < R else (2 if lai < 2 * R else 1); w = slice(max(0, k - 4), k + 1)
                    sw = l[w].min() if s > 0 else h[w].max(); at = best - s * m * a
                    st = keo(max(sw, at) if s > 0 else min(sw, at))
            thoat = ex is not None and (ex[k] == -s or ex[k] == 2)
            if thoat or k - j + 1 >= H: X = o[k + 1] if s > 0 else o[k + 1] + sp[k + 1]; k += 1; break
            k += 1
        if X is None: break
        r = (X - E) / E * s
        out.append((d.index[j], r, s, k - j + 1, E, int(ngay[k] - ngay[j]))); i = max(k, i + 1)
    return out


# ---------------- 14 ban dich ----------------
def htf_level(d, kh, A):
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close")); n = len(c)
    q = LON_HTF[kh]; pH = htf_ffill(d, q, lambda g: g["high"].to_numpy()); pL = htf_ffill(d, q, lambda g: g["low"].to_numpy())
    blk = d.index.floor(q).asi8 if q != "W-FRI" else d.index.to_period("W-FRI").start_time.asi8
    sig = np.zeros(n, int); tch_h = tch_l = None; done_l = done_s = False; cur = None
    for i in range(n):
        if blk[i] != cur: cur = blk[i]; tch_h = tch_l = None; done_l = done_s = False
        if not np.isfinite(pH[i]): continue
        if tch_h is None and h[i] >= pH[i]: tch_h = h[i]; continue
        if tch_l is None and l[i] <= pL[i]: tch_l = l[i]; continue
        if tch_h is not None and not done_l and c[i] > max(pH[i], tch_h): sig[i] = 1; done_l = True
        elif tch_l is not None and not done_s and c[i] < min(pL[i], tch_l): sig[i] = -1; done_s = True
    lo = pd.Series(l).rolling(10).min().to_numpy(); hi = pd.Series(h).rolling(10).max().to_numpy()
    sl = np.where(sig > 0, lo, hi); tp = c + 2 * (c - sl)
    return {"sig": sig, "sl": sl, "tp": tp}


def paxg(d, kh, A):
    h, l, c = (d[k].to_numpy() for k in ("high", "low", "close")); dr, _ = supertrend(h, l, c, 10, 4.0)
    up = (dr > 0) & (np.r_[0, dr[:-1]] < 0); sig = up.astype(int); ex = np.where((dr < 0) & (np.r_[0, dr[:-1]] > 0), -1, 0)
    return {"sig": sig, "sl": np.full(len(c), NAN), "tp": np.full(len(c), NAN), "ex": ex, "H": 10 ** 9}


def trendbreaker(d, kh, A):
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close")); n = len(c); N = 5
    ph, pl = pivots(h, l, N); hl2 = (h + l) / 2; ao = sma(sma(hl2, 5) - sma(hl2, 34), 3); aot = np.sign(ao - np.r_[NAN, ao[:-1]])
    sig = np.zeros(n, int); P_H, P_L = [], []; res = sup = None
    for i in range(n):
        if ph[i]:
            P_H.append((i - N, h[i - N]))
            if len(P_H) >= 2 and P_H[-1][1] < P_H[-2][1]:
                (i1, p1), (i2, p2) = P_H[-2], P_H[-1]; m = (p2 - p1) / (i2 - i1)
                ok = all(c[t] <= p2 + m * (t - i2) for t in range(i2, i + 1)); res = (i2, p2, m) if ok else None
        if pl[i]:
            P_L.append((i - N, l[i - N]))
            if len(P_L) >= 2 and P_L[-1][1] > P_L[-2][1]:
                (i1, p1), (i2, p2) = P_L[-2], P_L[-1]; m = (p2 - p1) / (i2 - i1)
                ok = all(c[t] >= p2 + m * (t - i2) for t in range(i2, i + 1)); sup = (i2, p2, m) if ok else None
        if res and i - res[0] <= 100 and c[i] > res[1] + res[2] * (i - res[0]) + 0.1 * A[i]:
            if aot[i] > 0: sig[i] = 1
            res = None
        elif sup and i - sup[0] <= 100 and c[i] < sup[1] + sup[2] * (i - sup[0]) - 0.1 * A[i]:
            if aot[i] < 0: sig[i] = -1
            sup = None
    sl = c - np.sign(sig) * 1.5 * A; tp = c + 2 * (c - sl)
    return {"sig": sig, "sl": sl, "tp": tp, "be_r": 1.0, "tr": ("atr", 2.0, 2.0)}


def ema_fib(d, kh, A):
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close")); e = ema(c, 50)
    q = {"M5": "1D", "M15": "1D", "H1": "1D", "H4": "W-FRI", "D1": "MS"}[kh]
    f = lambda g, k: ((g["high"] + g["low"] + g["close"]) / 3 + k * (g["high"] - g["low"])).to_numpy()
    R1 = htf_ffill(d, q, lambda g: f(g, 0.382)); S1 = htf_ffill(d, q, lambda g: f(g, -0.382))
    lg = (o <= np.minimum(e, R1)) & (c > np.maximum(e, R1)) & (c > o); sh = (o >= np.maximum(e, S1)) & (c < np.minimum(e, S1)) & (c < o)
    sig = np.where(lg, 1, np.where(sh, -1, 0)); sl = np.where(sig > 0, l, h); tp = c + 2 * (c - sl)
    return {"sig": sig, "sl": sl, "tp": tp}


def pullback(d, kh, A):
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close")); n = len(c)
    f, s = ema(c, 20), ema(c, 50); s10 = np.r_[np.full(10, NAN), s[:-10]]; up = (f > s) & (s > s10); dn = (f < s) & (s < s10); r = rsi(c, 4)
    sig = np.zeros(n, int); sl = np.full(n, NAN); arm = 0; t0 = -99; hd = 0
    for i in range(1, n):
        if up[i] and r[i] <= 30: arm, t0 = 1, i
        elif dn[i] and r[i] >= 70: arm, t0 = -1, i
        if arm and i - t0 <= 5 and i > t0:
            if arm == 1 and up[i] and c[i] > h[i - 1]: sig[i] = 1; sl[i] = l[t0 - 3:i + 1].min() - 0.5 * A[i]; arm = 0
            elif arm == -1 and dn[i] and c[i] < l[i - 1]: sig[i] = -1; sl[i] = h[t0 - 3:i + 1].max() + 0.5 * A[i]; arm = 0
        elif arm and i - t0 > 5: arm = 0
    return {"sig": sig, "sl": sl, "tp": np.full(n, NAN), "tr": ("atr", 3.0, 0.0)}


def diem_confluence(d):
    h, l, c = (d[k].to_numpy() for k in ("high", "low", "close")); A = atr(h, l, c)
    f, s = ema(c, 20), ema(c, 100); r = rsi(c, 14)
    er = (c - np.r_[np.full(20, NAN), c[:-20]]) / pd.Series(np.abs(np.diff(c, prepend=c[0]))).rolling(20).sum().to_numpy()
    pr = pd.Series(A).rolling(100).rank(pct=True).to_numpy()
    vol = np.where(pr < 0.2, pr / 0.2 * 20, np.where(pr > 0.8, (1 - pr) / 0.2 * 20, 20))
    def mot(sg):
        tr = 10 * (sg * (c - s) > 0) + 10 * (sg * (f - s) > 0); mo = np.clip(sg * (r - 50) / 20 * 20, 0, 20)
        ef = np.clip(sg * er / 0.4 * 20, 0, 20); return tr + mo + ef + vol + 10
    return mot(1), mot(-1)


def confluence(d, kh, A):
    c = d["close"].to_numpy(); L, S = diem_confluence(d); n = len(c)
    sig = np.where((L >= 70) & (np.r_[0, L[:-1]] < 70), 1, np.where((S >= 70) & (np.r_[0, S[:-1]] < 70), -1, 0))
    ex = np.where(L < 40, -1, 0); ex2 = np.where(S < 40, 1, 0)
    # ex: -huong => thoat. Lenh mua thoat khi L<40 (ex=-1); lenh ban thoat khi S<40 (ex=+1)
    exa = np.where(ex != 0, ex, ex2); exa = np.where((ex != 0) & (ex2 != 0), 2, exa)
    return {"sig": sig, "sl": c - np.sign(sig) * 3 * A, "tp": np.full(n, NAN), "tr": ("atr", 3.0, 0.0), "ex": exa}


def range_filter(c, per=100, m=2.5):
    r = ema(ema(np.abs(np.diff(c, prepend=c[0])), per), per * 2 - 1) * m; f = c.copy(); dr = np.zeros(len(c))
    for i in range(1, len(c)):
        f[i] = max(f[i - 1], c[i] - r[i]) if c[i] > f[i - 1] else min(f[i - 1], c[i] + r[i])
        dr[i] = 1 if f[i] > f[i - 1] else (-1 if f[i] < f[i - 1] else dr[i - 1])
    return dr


def ha_bull(g):
    o, h, l, c = (ema(g[k].to_numpy(), 10) for k in ("open", "high", "low", "close")); hc = (o + h + l + c) / 4; ho = np.empty(len(hc)); ho[0] = (o[0] + c[0]) / 2
    for i in range(1, len(hc)): ho[i] = (ho[i - 1] + hc[i - 1]) / 2
    return np.where(ema(hc, 10) > ema(ho, 10), 1.0, -1.0)


def apex(d, kh, A):
    h, l, c = (d[k].to_numpy() for k in ("high", "low", "close")); rf = range_filter(c); ha = ha_bull(d)
    hh = htf_ffill(d, LON[kh], ha_bull)
    H10, L10 = pd.Series(h).rolling(10).max().to_numpy(), pd.Series(l).rolling(10).min().to_numpy()
    rel = c - (H10 + L10) / 2; smi = 100 * ema(ema(np.nan_to_num(rel), 3), 3) / (0.5 * ema(ema(np.nan_to_num(H10 - L10), 3), 3) + 1e-12)
    al = (rf > 0) & (ha > 0) & (hh > 0); ash = (rf < 0) & (ha < 0) & (hh < 0)
    sig = np.where(al & ~np.r_[False, al[:-1]] & (smi < 60), 1, np.where(ash & ~np.r_[False, ash[:-1]] & (smi > -60), -1, 0))
    return {"sig": sig, "sl": c - np.sign(sig) * 2 * A, "tp": np.full(len(c), NAN), "tr": ("atr", 2.0, 0.0)}


def diem_engine(d):
    h, l, c = (d[k].to_numpy() for k in ("high", "low", "close")); dr, line = supertrend(h, l, c, 10, 2.0)
    eq, sl = linreg(c, 50); r = rsi(c, 14); pdi, mdi = dmi(h, l, c)
    sc = dr + np.sign(c - eq) + np.sign(sl) + np.sign(r - 50) + np.sign(r - sma(r, 14)) + np.sign(pdi - mdi)
    return dr, line, np.nan_to_num(sc)


def trend_engine(d, kh, A):
    c = d["close"].to_numpy(); dr, line, sc = diem_engine(d); pd_ = np.r_[dr[0], dr[:-1]]
    sig = np.where((dr > 0) & (pd_ < 0) & (sc >= 3), 1, np.where((dr < 0) & (pd_ > 0) & (sc <= -3), -1, 0))
    ex = np.where((dr < 0) & (pd_ > 0), -1, np.where((dr > 0) & (pd_ < 0), 1, 0))
    return {"sig": sig, "sl": line, "tp": np.full(len(c), NAN), "tr": ("line", line), "ex": ex}


def elliott(d, kh, A):
    h, l, c = (d[k].to_numpy() for k in ("high", "low", "close")); n = len(c); N = 5; ph, pl = pivots(h, l, N)
    P = []; sig = np.zeros(n, int); sl = np.full(n, NAN); tp = np.full(n, NAN)
    for i in range(n):
        nw = []
        if ph[i]: nw.append(("H", i - N, h[i - N]))
        if pl[i]: nw.append(("L", i - N, l[i - N]))
        for t in nw:
            if P and P[-1][0] == t[0]:
                if (t[0] == "H" and t[2] > P[-1][2]) or (t[0] == "L" and t[2] < P[-1][2]): P[-1] = t
                continue
            P.append(t)
            if len(P) < 6: continue
            p = [x[2] for x in P[-6:]]; ty = P[-1][0]; sg = 1 if ty == "H" else -1   # sg=1: song day tang, ket thuc o dinh
            q = [sg * x for x in p]; w1, w3, w5 = q[1] - q[0], q[3] - q[2], q[5] - q[4]
            ok = q[2] > q[0] and q[3] > q[1] and q[5] > q[3] and q[4] > q[1] and w3 >= min(w1, w5) and min(w1, w3, w5) > 0
            if ok and abs(p[5] - p[0]) >= 1.5 * A[i]:
                s_ = p[5] + sg * 0.1 * A[i]; t_ = p[5] - 0.5 * (p[5] - p[0])
                if abs(c[i] - t_) >= abs(s_ - c[i]) and (c[i] - t_) * sg > 0: sig[i] = -sg; sl[i] = s_; tp[i] = t_
    return {"sig": sig, "sl": sl, "tp": tp, "H": 100}


def crt(d, kh, A):
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close")); n = len(c)
    q = {"M5": "4h", "M15": "4h", "H1": "4h", "H4": "1D", "D1": "W-FRI"}[kh]
    dd = d.copy(); dd.index = gio_ny(d.index).tz_localize("America/New_York", ambiguous="NaT", nonexistent="NaT").tz_convert("UTC").tz_localize(None) if kh != "D1" else d.index
    dd = dd[~dd.index.isna()]
    def ok(g):
        rg = (g["high"] - g["low"]).replace(0, NAN); b = (g["close"] - g["open"]).abs() / rg
        uw = g["high"] - g[["open", "close"]].max(axis=1); lw = g[["open", "close"]].min(axis=1) - g["low"]
        imb = np.maximum(uw, lw) / np.minimum(uw, lw).replace(0, NAN)
        return ((b >= 0.1) & (b <= 0.9) & ~(imb > 4)).to_numpy().astype(float)
    def f(k): return lambda g: np.where(ok(g) > 0, g[k].to_numpy(), NAN)
    rH = htf_ffill(dd, q, f("high")); rL = htf_ffill(dd, q, f("low"))
    rH = pd.Series(rH, index=dd.index).reindex(range(0)) if False else rH
    if len(dd) != n: rH = np.r_[rH, np.full(n - len(rH), NAN)]; rL = np.r_[rL, np.full(n - len(rL), NAN)]
    _, slope = linreg(c, 50)
    sig = np.zeros(n, int); sl = np.full(n, NAN)
    for i in range(1, n):
        if not np.isfinite(rH[i]): continue
        lo = min(l[i], l[i - 1]) if l[i - 1] < rL[i] else l[i]; hi = max(h[i], h[i - 1]) if h[i - 1] > rH[i] else h[i]
        if lo < rL[i] and rL[i] < c[i] < rH[i] and c[i] > o[i] and slope[i] > 0: sig[i] = 1; sl[i] = lo
        elif hi > rH[i] and rL[i] < c[i] < rH[i] and c[i] < o[i] and slope[i] < 0: sig[i] = -1; sl[i] = hi
    return {"sig": sig, "sl": sl, "tp": c + 2 * (c - sl)}


def fvg_bos(d, kh, A):
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close")); n = len(c); N = 5; ph, pl = pivots(h, l, N)
    ny = gio_ny(d.index); mm = ny.hour * 60 + ny.minute; phien = (mm >= 9 * 60 + 45) & (mm < 11 * 60 + 45) if kh in ("M5", "M15", "H1") else np.ones(n, bool)
    sig = np.zeros(n, int); sl = np.full(n, NAN); lastH = lastL = None; trend = 0; lvl = None; ev = -1; fv = None
    for i in range(2, n):
        if ph[i]: lastH = h[i - N]
        if pl[i]: lastL = l[i - N]
        if lastH is not None and c[i] > lastH: trend, lvl, ev, lastH, fv = 1, lastH, i, None, None
        elif lastL is not None and c[i] < lastL: trend, lvl, ev, lastL, fv = -1, lastL, i, None, None
        if fv is None and ev >= 0 and i > ev:
            if trend == 1 and l[i] > h[i - 2] and 0.6 * A[i] <= l[i] - h[i - 2] <= 1.25 * A[i]: fv = [h[i - 2], l[i], l[i - 1], False]
            elif trend == -1 and h[i] < l[i - 2] and 0.6 * A[i] <= l[i - 2] - h[i] <= 1.25 * A[i]: fv = [h[i], l[i - 2], h[i - 1], False]
            continue
        if fv is not None:
            bot, top, mid_c, mit = fv
            if trend == 1:
                if l[i] <= (bot + top) / 2: fv[3] = True
                if fv[3] and c[i] > top and c[i] > lvl and phien[i]: sig[i] = 1; sl[i] = mid_c; fv = None; ev = -1
            else:
                if h[i] >= (bot + top) / 2: fv[3] = True
                if fv[3] and c[i] < bot and c[i] < lvl and phien[i]: sig[i] = -1; sl[i] = mid_c; fv = None; ev = -1
    tp = c + 3 * (c - sl)
    return {"sig": sig, "sl": sl, "tp": tp, "be_r": 1.5}


def _phien(d, tz, gio, phut, dai_phut):
    """moc phien theo gio dia phuong tz; tra ve (ma ngay phien, phut ke tu mo phien)."""
    t = gio_ny(d.index).tz_localize("America/New_York", ambiguous="NaT", nonexistent="NaT").tz_convert(tz)
    mm = (t.hour * 60 + t.minute - (gio * 60 + phut)).to_numpy().astype(float); day = t.normalize().asi8
    return np.where(np.isnan(np.asarray(t.hour, float)), NAN, mm), day, t


def orb(d, kh, A):
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close")); n = len(c)
    mm, day, _ = _phien(d, "Europe/London", 8, 0, 15); step = 5 if kh == "M5" else 15
    sig = np.zeros(n, int); sl = np.full(n, NAN); ex = np.zeros(n, int); cur = None; oh = ol = None; dl = ds = False
    for i in range(n):
        if day[i] != cur: cur = day[i]; oh = ol = None; dl = ds = False; hi_ = -np.inf; lo_ = np.inf
        if not np.isfinite(mm[i]): continue
        if 0 <= mm[i] < 15: hi_ = max(hi_, h[i]); lo_ = min(lo_, l[i]); continue
        if mm[i] >= 15 and oh is None and np.isfinite(hi_): oh, ol = hi_, lo_
        if mm[i] + step >= 360: ex[i] = 2
        if oh is None or (oh - ol) > 0.005 * c[i] or mm[i] >= 315: continue
        if not dl and c[i] > oh: sig[i] = 1; sl[i] = min(ol, c[i] - 1.5 * A[i]); dl = True
        elif not ds and c[i] < ol: sig[i] = -1; sl[i] = max(oh, c[i] + 1.5 * A[i]); ds = True
    rv = np.where((o - c) > A, -1, np.where((c - o) > A, 1, 0))     # nen nguoc > 1 ATR
    ex = np.where(ex == 2, 2, rv)
    return {"sig": sig, "sl": sl, "tp": np.full(n, NAN), "tr": ("orb",), "ex": ex}


def gold8pm(d, kh, A):
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close")); n = len(c)
    ny = gio_ny(d.index); mm = (ny.hour * 60 + ny.minute).to_numpy(); wd = ny.dayofweek.to_numpy(); dy = ny.normalize().asi8
    sig = np.zeros(n, int); sl = np.full(n, NAN); cur = None; rh = rl = boh = bol = None; dem = 0
    for i in range(n):
        if mm[i] == 20 * 60:
            cur = dy[i]; ok_day = wd[i] in (6, 0, 1, 2); rh, rl = (h[i], l[i]) if ok_day else (None, None); boh = bol = None; dem = 0; continue
        if rh is None or dy[i] != cur or mm[i] > 21 * 60 + 35 or dem >= 3: continue
        if boh is None and c[i] > rh: boh = h[i]; continue
        if bol is None and c[i] < rl: bol = l[i]; continue
        if boh is not None and c[i] > boh: sig[i] = 1; sl[i] = rl; dem += 1
        elif bol is not None and c[i] < bol: sig[i] = -1; sl[i] = rh; dem += 1
    return {"sig": sig, "sl": sl, "tp": c + 2.25 * (c - sl)}


def tlo(d, kh, A):
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close")); n = len(c)
    mm, day, _ = _phien(d, "Asia/Tokyo", 9, 0, 60)
    sig = np.zeros(n, int); sl = np.full(n, NAN); tp = np.full(n, NAN); cur = None; st = 0
    for i in range(n):
        if not np.isfinite(mm[i]): continue
        if 0 <= mm[i] < 60:
            if day[i] != cur: cur = day[i]; bh, bl = h[i], l[i]; st = 0; t0 = i
            else: bh, bl = max(bh, h[i]), min(bl, l[i])
            continue
        if cur is None or st == 9: continue
        if st == 0:
            if c[i] > bh: st, tb = 1, i
            elif c[i] < bl: st, tb = -1, i
        elif i - tb > 80: st = 9
        elif st in (1, -1):
            if st == 1 and l[i] <= bh + 0.12 * A[i]: st = 2
            elif st == -1 and h[i] >= bl - 0.12 * A[i]: st = -2
        if st == 2 and c[i] > bh and l[i] > bh - 10 * A[i]:
            if i > tb: sig[i] = 1; H_ = bh - bl; sl[i] = bh - 2 * H_; tp[i] = bh + H_; st = 9
        elif st == -2 and c[i] < bl:
            H_ = bh - bl; sig[i] = -1; sl[i] = bl + 2 * H_; tp[i] = bl - H_; st = 9
    return {"sig": sig, "sl": sl, "tp": tp, "be_r": 1.0}


SCRIPT = {"HTF_LEVEL": (htf_level, ["M15", "H1", "H4", "D1"]), "PAXG_ST": (paxg, ["M15", "H1", "H4", "D1"]),
          "TRENDBREAKER": (trendbreaker, ["M15", "H1", "H4", "D1"]), "EMA_FIB": (ema_fib, ["M15", "H1", "H4", "D1"]),
          "PULLBACK": (pullback, ["M15", "H1", "H4", "D1"]), "CONFLUENCE": (confluence, ["M15", "H1", "H4", "D1"]),
          "APEX": (apex, ["M5", "M15", "H1", "H4", "D1"]), "TREND_ENGINE": (trend_engine, ["M15", "H1", "H4", "D1"]),
          "ELLIOTT": (elliott, ["M15", "H1", "H4", "D1"]), "CRT": (crt, ["M5", "M15", "H1", "H4", "D1"]),
          "FVG_BOS": (fvg_bos, ["M5", "M15", "H1", "H4", "D1"]), "ORB_SMART": (orb, ["M5", "M15"]),
          "GOLD_8PM": (gold8pm, ["M5"]), "TLO_BOX": (tlo, ["M5", "M15", "H1"])}
GOC = {"HTF_LEVEL": None, "PAXG_ST": "H4", "TRENDBREAKER": None, "EMA_FIB": None, "PULLBACK": "H1", "CONFLUENCE": "H1", "APEX": "M5",
       "TREND_ENGINE": None, "ELLIOTT": "H1", "CRT": "M5", "FVG_BOS": "M5", "ORB_SMART": "M5", "GOLD_8PM": "M5", "TLO_BOX": None}
GHEP_TIN = ["HTF_LEVEL", "TRENDBREAKER", "EMA_FIB", "CRT", "FVG_BOS", "ELLIOTT"]


def loc(d, ten):
    h, l, c = (d[k].to_numpy() for k in ("high", "low", "close"))
    if ten == "ST": return supertrend(h, l, c, 10, 4.0)[0]
    if ten == "CONF":
        L, S = diem_confluence(d); return np.where(L >= 50, 1, 0) + np.where(S >= 50, -1, 0)
    if ten == "ENGINE":
        sc = diem_engine(d)[2]; return np.where(sc >= 3, 1, np.where(sc <= -3, -1, 0))
    if ten == "RF": return range_filter(c)
    f, s = ema(c, 20), ema(c, 50); s10 = np.r_[np.full(10, NAN), s[:-10]]
    return np.where((f > s) & (s > s10), 1, np.where((f < s) & (s < s10), -1, 0))


# ---------------- chay ----------------
CHUOI_NHO = [f"bo1_{c}" for c in F.CAP] + ["bo2_xauusd24"]
CHUOI_D1 = ["d1_eurusd", "d1_usdjpy", "d1_audusd", "d1_gbpusd", "d1_spx", "d1_vang"]


def lay(ten, kh):
    g, loai, dr = v22.nguon(ten)
    if ten.startswith("d1_"): d = g
    else: d = v22.gop(g, kh)
    d = d[d["high"] >= d["low"]].copy(); return d, loai, dr


def do(d, S, pip, drift, giua, A):
    sp1 = d["spread_open"].to_numpy() * v19.XM; sp0 = np.zeros(len(d))
    Lg, L1, L15 = sim(d, S, sp0, A), sim(d, S, sp1, A), sim(d, S, sp1 * 1.5, A)
    r = {}; g0 = v22.ket_qua(Lg, giua, drift, pip, False, 0); m = v22.ket_qua(L1, giua, drift, pip, True, 0.5)
    r["n_lenh"] = len(L1)
    if g0: r["truoc_phi"] = g0
    if m:
        r.update(m); r["kiem_slip1_pct"] = v22.ket_qua(L1, giua, drift, pip, True, 1.0)["kiem_pct"]
        q = v22.ket_qua(L15, giua, drift, pip, True, 1.0); r["kiem_x1_5_slip1_pct"] = q["kiem_pct"] if q else None
    return r


def lam(job):
    ten, kh, che = job
    d, loai, co_dr = lay(ten, kh)
    h, l, c = (d[k].to_numpy() for k in ("high", "low", "close")); A = atr(h, l, c)
    pip = v22.pip_of(ten); giua = d.index[len(d) // 2]
    drift = float(np.mean(np.diff(np.log(c))[: len(c) // 2])) if co_dr else 0.0
    out = []; base = {"chuoi": ten, "khung": kh, "spread": loai}
    if che == "don":
        for s, (f, kks) in SCRIPT.items():
            if kh not in kks: continue
            if s == "GOLD_8PM" and "xau" not in ten and "vang" not in ten and kh != "M5": continue
            S = f(d, kh, A); r = {**base, "script": s, "khung_goc": GOC[s] == kh, "so_tin": int((S["sig"] != 0).sum())}; r.update(do(d, S, pip, drift, giua, A)); out.append(r)
    else:
        LOC = {k: loc(d, k) for k in ("ST", "CONF", "ENGINE", "RF", "PB")}
        for s in GHEP_TIN:
            S0 = SCRIPT[s][0](d, kh, A)
            for lt, lv in LOC.items():
                sg = np.where(np.sign(S0["sig"]) == lv, S0["sig"], 0)
                for ql in ("GOC", "CHAND"):
                    S = dict(S0); S["sig"] = sg
                    if ql == "CHAND": S["tp"] = np.full(len(c), NAN); S["tr"] = ("chand", 22, 3.0); S.pop("be_r", None); S["H"] = 500
                    r = {**base, "script": f"{s}+{lt}+{ql}", "ghep": True}; r.update(do(d, S, pip, drift, giua, A)); out.append(r)
    print(ten, kh, che, "xong", flush=True); return out


def jobs():
    J = [(t, k, "don") for t in CHUOI_NHO for k in ("M5", "M15", "H1", "H4")]
    J += [(t, k, "don") for t in ("us500_h1", "uk100_h1") for k in ("H1", "H4")] + [(t, "D1", "don") for t in CHUOI_D1]
    J += [(t, k, "ghep") for t in CHUOI_NHO for k in ("M15", "H1")]
    return J


def main(ra=None):
    with Pool(3, maxtasksperchild=1) as P: R = P.map(lam, jobs(), chunksize=1)
    o = [r for x in R for r in x]; v = [r for r in o if "p" in r]
    J22 = json.load(open("reports/vong22.json")); cu_n = J22["ho_holm"]
    cu = v22_ho()
    assert len(cu) == cu_n, (len(cu), cu_n)
    H = MV.holm(cu + [r["p"] for r in v])
    for r, hh in zip(v, H[len(cu):]):
        r["p_holm"] = hh; x15 = r.get("kiem_x1_5_slip1_pct")
        r["song"] = bool(hh < 0.05 and r["ph_pct"] > 0 and r["kiem_pct"] > 0 and r["kiem_slip1_pct"] > 0 and x15 is not None and x15 > 0 and r["maxdd_pct"] < 80)
    print("ho", len(H), "o", len(o), "do duoc", len(v), "song", sum(r["song"] for r in v))
    if ra: json.dump({"nhan": "MO PHONG", "ban_dich": "THEO MO TA CONG KHAI", "ho_holm": len(H), "o": o}, open(ra, "w"), ensure_ascii=False, indent=0, default=float)


def v22_ho():
    J21 = json.load(open("reports/vong21.json")); J22 = json.load(open("reports/vong22.json"))
    cu = v19.ho_cu(); J = json.load(open("reports/vong19.json")); Jb = json.load(open("reports/vong19b.json")); J20 = json.load(open("reports/vong20.json"))
    cu += [r["p"] for r in J["o"] + J["ghep"] if "p" in r] + [r["p"] for r in Jb["o"] if "p" in r] + [r["p"] for r in J20["o"] if "p" in r]
    cu += [r["p"] for r in J21["o"] if "p" in r] + [r["p"] for r in J22["o"] if "p" in r]
    return cu


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
