# -*- coding: utf-8 -*-
"""
Hàm dùng chung cho VÒNG 7 (các hướng có cơ sở nghiên cứu: trend, mean-reversion, lịch, biến động/tin tức).
Nguyên tắc (giống vòng 1-6):
  * Tín hiệu tính ở CLOSE nến t (chỉ dùng dữ liệu <= t) -> khớp OPEN THẬT nến t+1 (mode 'open'),
    hoặc đúng giá close/open mà quy tắc chỉ định (mode 'close', hoặc chuỗi lợi nhuận tự dựng cho overnight/intraday).
  * Phí: spread (vàng 0.3, ES 0.25, ^GSPC 0.5, SPY 0.02 điểm) – trả 1/2 spread cho mỗi 1 đơn vị thay đổi vị thế
    (=> 1 lượt mua+bán = 1 spread).
  * IS/OOS: daily tách 2016-01-01; intraday chia đôi theo thời gian.
  * Đối chứng: Buy&Hold, Donchian20, EMA20/100, và "ngẫu nhiên cùng phơi nhiễm": dịch vòng (circular shift)
    chuỗi vị thế so với chuỗi giá -> giữ nguyên số lệnh, thời gian giữ, % thời gian có vị thế; chỉ phá timing.
"""
import numpy as np, pandas as pd
from common2 import atr_rma, bh_fdr, SPLIT

SPREAD = {"GC=F": 0.3, "ES=F": 0.25, "^GSPC": 0.5, "SPY": 0.02}
DFILE = {"GC=F": ("data_GCF_1d.pkl", "2008-01-01"), "ES=F": ("data_ESF_1d.pkl", "2000-01-01"),
         "^GSPC": ("data_GSPC_1d.pkl", "2000-01-01"), "SPY": ("data_SPY_1d.pkl", "2000-01-01")}
HFILE = {"GC=F": "data_GCF_1h.pkl", "ES=F": "data_ESF_1h.pkl", "^GSPC": "data_GSPC_1h.pkl"}
import os
N_RAND = int(os.environ.get("N_RAND", 5000))


def load_d(tk):
    f, start = DFILE[tk]
    d = pd.read_pickle(f)
    if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.droplevel(1)
    d = d.dropna(subset=["Open", "High", "Low", "Close"])
    d.index = pd.to_datetime(d.index).tz_localize(None).normalize()
    d = d[d.index >= start]
    if tk == "SPY":   # điều chỉnh cổ tức/chia tách cho cả OHLC (tỷ lệ Adj/Close)
        r = d["Adj Close"] / d["Close"]
        for c in ("Open", "High", "Low", "Close"): d[c] = d[c] * r
    d = d[(d.High >= d.Low) & (d.High > 0)]
    if tk == "GC=F": d = d[d.High > d.Low]
    d = d[["Open", "High", "Low", "Close"]].astype(float).copy()
    d["period"] = np.where(d.index < SPLIT, "IS", "OOS")
    return d


def load_h(tk):
    d = pd.read_pickle(HFILE[tk])
    if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.droplevel(1)
    d = d.dropna(subset=["Open", "High", "Low", "Close"])
    d.index = pd.to_datetime(d.index, utc=True).tz_convert("America/New_York")
    d = d[(d.High >= d.Low) & (d.High > 0)][["Open", "High", "Low", "Close"]].astype(float).copy()
    mid = d.index[0] + (d.index[-1] - d.index[0]) / 2
    d["period"] = np.where(d.index < mid, "IS", "OOS")
    return d


# ---------------- chỉ báo ----------------
def sma(x, n): return pd.Series(x).rolling(n).mean().values
def ema(x, n): return pd.Series(x).ewm(span=n, adjust=False).mean().values
def rsi(c, n):
    d = np.diff(c, prepend=np.nan); up = np.where(d > 0, d, 0.0); dn = np.where(d < 0, -d, 0.0)
    au = pd.Series(up).ewm(alpha=1 / n, adjust=False).mean().values; ad = pd.Series(dn).ewm(alpha=1 / n, adjust=False).mean().values
    with np.errstate(divide="ignore", invalid="ignore"): r = 100 - 100 / (1 + au / ad)
    r[:n] = np.nan; return r


def hold_state(entry, exitc):
    """Vị thế long 0/1: vào khi entry[t], giữ tới khi exitc[t] (đánh giá tại close)."""
    n = len(entry); w = np.zeros(n); s = 0
    for t in range(n):
        if s == 0 and entry[t]: s = 1
        elif s == 1 and exitc[t]: s = 0
        w[t] = s
    return w


def hold_n(entry, n_hold, exitc=None):
    """Long khi entry, giữ tối đa n_hold phiên (hoặc thoát sớm khi exitc)."""
    n = len(entry); w = np.zeros(n); left = 0
    for t in range(n):
        if left > 0:
            left -= 1
            if exitc is not None and exitc[t]: left = 0
        if left == 0 and entry[t]: left = n_hold
        w[t] = 1.0 if left > 0 else 0.0
    return w


# ---------------- lợi nhuận ----------------
def pnl_daily(d, w, spread, mode="open"):
    """w[t] = vị thế mục tiêu quyết định tại close t (dùng dữ liệu <= t).
    mode 'open' : vị thế giữ từ OPEN t+1 tới OPEN t+2 (khớp giá mở cửa thật).
    mode 'close': khớp tại CLOSE t (giữ close t -> close t+1) – chỉ dùng khi quy tắc chỉ định khớp ở close.
    Trả mảng lợi nhuận % theo vốn, gán cho ngày t+1 (ngày diễn ra)."""
    O, C = d.Open.values, d.Close.values; n = len(C); w = np.nan_to_num(np.asarray(w, float))
    out = np.zeros(n)
    if mode == "open":
        # ngày i (i>=1): giữ vị thế w[i-1] từ O[i] tới O[i+1]
        R = np.r_[O[1:] / O[:-1] - 1, 0.0]
        wp = np.r_[0.0, w[:-1]]; wpp = np.r_[0.0, wp[:-1]]
        out = wp * R - np.abs(wp - wpp) * (spread / 2) / O
    else:
        R = np.r_[0.0, C[1:] / C[:-1] - 1]
        wp = np.r_[0.0, w[:-1]]; wpp = np.r_[0.0, wp[:-1]]
        out = wp * R - np.abs(wp - wpp) * (spread / 2) / np.r_[C[0], C[:-1]]
    return out, wp


def trades_from(pos, pnl):
    """Tách lệnh = đoạn liên tiếp vị thế cùng dấu khác 0. Trả mảng lợi nhuận từng lệnh."""
    s = np.sign(pos); tr = []; cur = 0.0; on = False
    for i in range(len(s)):
        if s[i] != 0 and (not on or s[i] != s[i - 1]):
            if on: tr.append(cur)
            cur = 0.0; on = True
        if s[i] == 0 and on: tr.append(cur); on = False; cur = 0.0
        if on: cur += pnl[i]
    if on: tr.append(cur)
    return np.array(tr)


def metrics(pnl, pos, ann=252):
    pnl = np.asarray(pnl, float); pos = np.asarray(pos, float)
    if len(pnl) < 5 or np.std(pnl) == 0:
        return dict(sharpe=0.0, cagr=0.0, maxdd=0.0, pf=np.nan, trades=0, expo=0.0, tot=0.0, win=np.nan)
    sh = pnl.mean() / pnl.std() * np.sqrt(ann)
    eq = np.cumprod(1 + pnl); yrs = len(pnl) / ann
    cagr = eq[-1] ** (1 / yrs) - 1 if eq[-1] > 0 else -1
    dd = (1 - eq / np.maximum.accumulate(eq)).max()
    tr = trades_from(pos, pnl)
    pf = tr[tr > 0].sum() / max(1e-12, -tr[tr < 0].sum()) if len(tr) else np.nan
    return dict(sharpe=sh, cagr=100 * cagr, maxdd=100 * dd, pf=pf, trades=len(tr), expo=100 * np.mean(pos != 0),
                tot=100 * (eq[-1] - 1), win=100 * np.mean(tr > 0) if len(tr) else np.nan)


def rand_p(make_pnl, w, mask, rng, n=N_RAND, ann=252):
    """p-value ngẫu nhiên cùng phơi nhiễm: dịch vòng vị thế TRONG từng giai đoạn (mask) rồi tính lại PnL (có phí)."""
    idx = np.flatnonzero(mask); m = len(idx)
    if m < 50: return np.nan, np.nan
    pnl0, pos0 = make_pnl(w); s0 = metrics(pnl0[idx], pos0[idx], ann)["sharpe"]
    if np.all(w[idx] == w[idx][0]): return np.nan, s0
    null = []
    for _ in range(n):
        k = rng.integers(20, m - 20); ws = w.copy(); ws[idx] = np.roll(w[idx], k)
        p, ps = make_pnl(ws); q = p[idx]; sd = q.std()
        null.append(q.mean() / sd * np.sqrt(ann) if sd > 0 else 0.0)
    null = np.array(null)
    return (1 + (null >= s0).sum()) / (n + 1), null.mean()


def baselines(d, spread):
    """Buy&Hold, Donchian20 (long-only), EMA20/100 (long-only) – khớp open thật."""
    C, H, L = d.Close.values, d.High.values, d.Low.values
    hh = pd.Series(H).rolling(20).max().shift(1).values; ll = pd.Series(L).rolling(20).min().shift(1).values
    don = hold_state(C > hh, C < ll)
    e1, e2 = ema(C, 20), ema(C, 100); em = (e1 > e2).astype(float)
    return {"BH": np.ones(len(C)), "Donchian20": don, "EMA20/100": em}


def eval_daily(tk, d, w, mode, rng, name, direction, param, do_rand=True):
    """Đánh giá 1 chiến lược daily: chỉ số IS/OOS + p ngẫu nhiên + so với baseline."""
    sp = SPREAD[tk]
    mk = lambda ww: pnl_daily(d, ww, sp, mode)
    pnl, pos = mk(np.asarray(w, float))
    row = dict(direction=direction, ticker=tk, tf="1d", strategy=name, param=param, fill=mode)
    for per in ("IS", "OOS"):
        m = (d.period.values == per)
        mt = metrics(pnl[m], pos[m])
        for k, v in mt.items(): row[f"{per}_{k}"] = v
        if do_rand:
            p, nm = rand_p(mk, np.asarray(w, float), m, rng)
            row[f"{per}_p_rand"] = p; row[f"{per}_rand_sharpe"] = nm
    return row


def add_baseline_cols(df, bl):
    """bl: dict (ticker)->dict(name->(IS_sharpe, OOS_sharpe)). Thêm cột so sánh."""
    for c in ("BH", "Donchian20", "EMA20/100"):
        df[f"OOS_{c}_sh"] = df.ticker.map(lambda t: bl.get(t, {}).get(c, (np.nan, np.nan))[1])
        df[f"IS_{c}_sh"] = df.ticker.map(lambda t: bl.get(t, {}).get(c, (np.nan, np.nan))[0])
    return df
