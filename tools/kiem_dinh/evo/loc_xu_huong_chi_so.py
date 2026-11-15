# -*- coding: utf-8 -*-
"""Loc nhe cac ung vien xu huong chi so (D1, phi XM, vs mua-va-giu).

IS: ngay < 2016-01-01. OOS: >= 2016-01-01, nhin mot lan — khong chinh tham so.
Khong phai kiem dinh tien dang ky; khong tinh p placebo (toi tinh nhe).
Khong viet EA, khong gan demo.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

FRI = 4
ROLLOVER_HOUR_ET = 17
ANN = 252.0
OOS = pd.Timestamp("2016-01-01")
DATA_CANDIDATES = [
    Path("/workspace/ibs_cfd_my/data"),
    Path("/workspace/brain2/data"),
    Path(__file__).resolve().parents[3] / "data",
]
COST_CANDIDATES = [
    Path("/workspace/ibs_cfd_my/docs/costs_xm_us_index.json"),
    Path("/tmp/brain2-ibs/docs/kien-thuc-thong-ke/costs_xm_us_index.json"),
    Path(__file__).resolve().parents[3] / "docs" / "evo" / "costs_xm_us_index.json",
]

# fallback neu khong doc duoc file phi
FALLBACK = {
    "US500": {"spread_pts_median": 0.55, "fin_long_annual": 0.06487},
    "US100": {"spread_pts_median": 1.95, "fin_long_annual": 0.06478},
}


def rollover_units(entry, exit_, triple_weekday=FRI) -> int:
    e = pd.Timestamp(entry)
    x = pd.Timestamp(exit_)
    if x <= e:
        return 0
    units = 0
    d = e.normalize()
    end = x.normalize()
    while d <= end:
        wd = int(d.weekday())
        if wd < 5:
            inst = d + pd.Timedelta(hours=ROLLOVER_HOUR_ET)
            if e <= inst < x:
                units += 3 if wd == triple_weekday else 1
        d += pd.Timedelta(days=1)
    return units


def precompute_bar_units(times, triple_weekday=FRI):
    n = len(times)
    u = np.zeros(n, dtype=np.int16)
    for i in range(n - 1):
        u[i] = rollover_units(times[i], times[i + 1], triple_weekday)
    return u


def costs_on_pos(pos, r_fill, fill, spread_pts, fin_annual, bar_units):
    n = len(pos)
    pos = np.asarray(pos, float)
    px = np.where(np.asarray(fill) > 0, fill, np.nan)
    prev = np.empty(n, dtype=float)
    prev[0] = 0.0
    prev[1:] = pos[:-1]
    changed = pos != prev
    costs = np.zeros(n, dtype=float)
    close_old = changed & (prev != 0)
    open_new = changed & (pos != 0)
    idx = np.flatnonzero(close_old)
    if len(idx):
        src_px = px[idx]
        dest = np.clip(idx - 1, 0, n - 1)
        add = (spread_pts / 2.0) / src_px
        add = np.where(np.isfinite(add), add, 0.0)
        np.add.at(costs, dest, add)
    if open_new.any():
        add = (spread_pts / 2.0) / px
        add = np.where(open_new & np.isfinite(add), add, 0.0)
        costs += add
    if fin_annual:
        costs += np.where(pos != 0, fin_annual * bar_units / 365.0, 0.0)
    pnl = pos * r_fill - costs
    pnl[-1] = 0.0
    return np.where(np.isfinite(pnl), pnl, 0.0)


def n_trades(pos) -> int:
    pos = np.asarray(pos, float)
    if len(pos) == 0:
        return 0
    prev = np.r_[0.0, pos[:-1]]
    return int(np.sum((pos != 0) & (prev == 0)))


def metrics(pnl, pos, times):
    pnl = np.asarray(pnl, float)
    if len(pnl) < 2:
        return dict(n=0, cagr=np.nan, sharpe=np.nan, dd=np.nan, tot=np.nan,
                    exp=0.0, trades=0, years=0.0)
    sd = float(pnl.std(ddof=0))
    sharpe = float(pnl.mean() / sd * np.sqrt(ANN)) if sd > 0 else 0.0
    eq = np.cumprod(1.0 + np.clip(pnl, -0.99, 10.0))
    tot = 100.0 * (eq[-1] - 1.0) if eq[-1] > 0 else -100.0
    years = max((pd.Timestamp(times[-1]) - pd.Timestamp(times[0])).days / 365.25, 1e-6)
    cagr = 100.0 * (eq[-1] ** (1.0 / years) - 1.0) if eq[-1] > 0 else -100.0
    peak = np.maximum.accumulate(eq)
    dd = 100.0 * float(np.max(1.0 - eq / np.maximum(peak, 1e-12)))
    exp = float(np.mean(np.asarray(pos, float) != 0))
    return dict(n=len(pnl), cagr=cagr, sharpe=sharpe, dd=dd, tot=tot,
                exp=exp, trades=n_trades(pos), years=years)


def split_metrics(pnl, pos, times, dates):
    dates = pd.DatetimeIndex(dates)
    is_m = dates < OOS
    oos_m = dates >= OOS
    out = {}
    for name, m in (("IS", is_m), ("OOS", oos_m), ("ALL", np.ones(len(dates), bool))):
        if m.sum() < 20:
            out[name] = dict(n=int(m.sum()), cagr=np.nan, sharpe=np.nan, dd=np.nan,
                             tot=np.nan, exp=np.nan, trades=0, years=np.nan)
            continue
        # Fills: pos[i] earns r_fill[i] = open[i+1]/open[i]-1, so use same slice
        out[name] = metrics(pnl[m], pos[m], times[m])
    return out


def load_costs():
    for p in COST_CANDIDATES:
        if p.is_file():
            d = json.loads(p.read_text(encoding="utf-8"))
            return d["symbols"], str(p)
    return FALLBACK, "fallback"


def find_csv(name: str) -> Path:
    for root in DATA_CANDIDATES:
        p = root / name
        if p.is_file():
            return p
    raise FileNotFoundError(name)


def load_daily(fname: str) -> pd.DataFrame:
    p = find_csv(fname)
    df = pd.read_csv(p)
    col = "date" if "date" in df.columns else df.columns[0]
    df[col] = pd.to_datetime(df[col]).dt.tz_localize(None).dt.normalize()
    df = df.set_index(col).sort_index()
    for c in ("open", "high", "low", "close"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["open", "high", "low", "close"])
    df = df[(df["high"] >= df["low"]) & (df["open"] > 0) & (df["close"] > 0)]
    return df


def pack(df: pd.DataFrame, spread, fin):
    n = len(df)
    open_ = df["open"].to_numpy(float)
    high = df["high"].to_numpy(float)
    low = df["low"].to_numpy(float)
    close = df["close"].to_numpy(float)
    dates = pd.DatetimeIndex(df.index)
    t_open = dates + pd.Timedelta(hours=9, minutes=30)
    r_open = np.zeros(n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r_open[:-1] = open_[1:] / open_[:-1] - 1.0
        r_open[~np.isfinite(r_open)] = 0.0
    units = precompute_bar_units(np.array(t_open, dtype="datetime64[ns]"), FRI)
    return dict(
        dates=dates, open=open_, high=high, low=low, close=close,
        r_open=r_open, t_open=np.array(t_open, dtype="datetime64[ns]"),
        units=units, spread=float(spread), fin=float(fin), n=n,
    )


def apply(s, sig_close):
    """sig_close[t]=True => long from next open (pos[t+1]=1)."""
    n = s["n"]
    pos = np.zeros(n, dtype=float)
    sig = np.asarray(sig_close, dtype=bool)
    pos[1:] = np.where(sig[:-1], 1.0, 0.0)
    # drop incomplete last bar already handled by pnl[-1]=0
    pnl = costs_on_pos(pos, s["r_open"], s["open"], s["spread"], s["fin"], s["units"])
    return pos, pnl


def rsi_wilder(close, n=2):
    d = np.diff(close, prepend=close[0])
    gain = np.clip(d, 0, None)
    loss = np.clip(-d, 0, None)
    # seed with SMA of first n, then Wilder
    ag = np.zeros_like(close, float)
    al = np.zeros_like(close, float)
    if len(close) <= n:
        return np.full_like(close, np.nan)
    ag[n] = gain[1 : n + 1].mean()
    al[n] = loss[1 : n + 1].mean()
    alpha = 1.0 / n
    for i in range(n + 1, len(close)):
        ag[i] = (1 - alpha) * ag[i - 1] + alpha * gain[i]
        al[i] = (1 - alpha) * al[i - 1] + alpha * loss[i]
    rs = np.divide(ag, al, out=np.full_like(ag, np.nan), where=al > 1e-16)
    rsi = 100.0 - 100.0 / (1.0 + rs)
    rsi[:n] = np.nan
    return rsi


def atr(high, low, close, n=14):
    prev = np.r_[close[0], close[:-1]]
    tr = np.maximum(high - low, np.maximum(np.abs(high - prev), np.abs(low - prev)))
    out = np.full_like(tr, np.nan, dtype=float)
    if len(tr) <= n:
        return out
    out[n] = tr[1 : n + 1].mean()
    alpha = 1.0 / n
    for i in range(n + 1, len(tr)):
        out[i] = (1 - alpha) * out[i - 1] + alpha * tr[i]
    return out


def rolling_rank(x, win):
    """Causal percentile of x[i] among x[i-win+1:i+1], 0..1."""
    s = pd.Series(x)
    # pct=True average rank in window including current
    r = s.rolling(win, min_periods=win).apply(
        lambda w: pd.Series(w).rank(pct=True).iloc[-1], raw=False
    )
    return r.to_numpy(float)


def rule_buy_hold(s):
    sig = np.ones(s["n"], dtype=bool)
    sig[0] = False  # first close has no prior; enter at 2nd open after first close
    # actually BH: in from first valid open of sample after bar 0
    pos = np.ones(s["n"], dtype=float)
    pos[0] = 0.0
    pnl = costs_on_pos(pos, s["r_open"], s["open"], s["spread"], s["fin"], s["units"])
    return pos, pnl


def rule_sma200(s):
    sma = pd.Series(s["close"]).rolling(200, min_periods=200).mean().to_numpy()
    sig = s["close"] > sma
    sig[~np.isfinite(sma)] = False
    return apply(s, sig)


def rule_ema_cross(s, fast=50, slow=200):
    c = pd.Series(s["close"])
    e1 = c.ewm(span=fast, adjust=False).mean().to_numpy()
    e2 = c.ewm(span=slow, adjust=False).mean().to_numpy()
    sig = e1 > e2
    sig[: slow] = False
    return apply(s, sig)


def rule_faber(s, months=10):
    n = s["n"]
    dates = s["dates"]
    close = s["close"]
    months_a = dates.month.to_numpy()
    years = dates.year.to_numpy()
    ends = [i for i in range(n) if i == n - 1 or years[i + 1] > years[i] or months_a[i + 1] != months_a[i]]
    ends = np.array(ends, dtype=int)
    me_close = close[ends]
    first = []
    prev = None
    for i in range(n):
        key = (int(years[i]), int(months_a[i]))
        if key != prev:
            first.append(i)
            prev = key
    first_of = {(int(years[i]), int(months_a[i])): i for i in first}
    pos = np.zeros(n, dtype=float)
    for k in range(months - 1, len(ends)):
        sma = float(me_close[k - months + 1 : k + 1].mean())
        long_next = me_close[k] > sma
        e = ends[k]
        y, m = int(years[e]), int(months_a[e])
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        if (ny, nm) not in first_of:
            continue
        a = first_of[(ny, nm)]
        ey, em = (ny + 1, 1) if nm == 12 else (ny, nm + 1)
        b = first_of.get((ey, em))
        if b is None:
            continue  # drop incomplete last month (giong prereg)
        if long_next:
            pos[a:b] = 1.0
    pnl = costs_on_pos(pos, s["r_open"], s["open"], s["spread"], s["fin"], s["units"])
    return pos, pnl


def rule_rsi2_giu1(s, th=15.0, need_sma=False):
    rsi = rsi_wilder(s["close"], 2)
    sig = rsi < th
    sig[~np.isfinite(rsi)] = False
    if need_sma:
        sma = pd.Series(s["close"]).rolling(200, min_periods=200).mean().to_numpy()
        sig &= s["close"] > sma
        sig[~np.isfinite(sma)] = False
    # hold 1 bar after entry: signal at t -> pos[t+1]=1 only (giu=1)
    n = s["n"]
    pos = np.zeros(n, dtype=float)
    for t in range(n - 2):
        if sig[t]:
            pos[t + 1] = 1.0
    pnl = costs_on_pos(pos, s["r_open"], s["open"], s["spread"], s["fin"], s["units"])
    return pos, pnl


def rule_dip10_sma200(s, look=10, win=250, q=0.15, atr_q=0.5, hold=7):
    """Ban D1 cua ung vien H4: giam 10 bar thuoc 15% manh nhat / 250, ATR khong cao, tren SMA200, giu 7."""
    n = s["n"]
    close, high, low = s["close"], s["high"], s["low"]
    ret10 = np.full(n, np.nan)
    ret10[look:] = close[look:] / close[:-look] - 1.0
    rnk = rolling_rank(ret10, win)
    a = atr(high, low, close, 14)
    a_rnk = rolling_rank(a, win)
    sma = pd.Series(close).rolling(200, min_periods=200).mean().to_numpy()
    raw = (rnk <= q) & (a_rnk <= atr_q) & (close > sma) & np.isfinite(rnk) & np.isfinite(a_rnk) & np.isfinite(sma)
    pos = np.zeros(n, dtype=float)
    t = 0
    while t < n - 2:
        if raw[t] and t + 1 < n:
            a0 = t + 1
            b = min(a0 + hold, n - 1)
            pos[a0:b] = 1.0
            t = b  # khong chong lenh
        else:
            t += 1
    pnl = costs_on_pos(pos, s["r_open"], s["open"], s["spread"], s["fin"], s["units"])
    return pos, pnl


RULES = [
    ("mua_va_giu_1x", rule_buy_hold, "chuan: long CFD 1x, phi spread+fin XM"),
    ("faber_sma10_thang_1x", rule_faber, "Faber: long thang sau neu close cuoi thang > SMA 10 thang"),
    ("loc_sma200", rule_sma200, "Long khi close > SMA200 (vao/ra open sau)"),
    ("ema50_tren_ema200", rule_ema_cross, "Long khi EMA50 > EMA200 (golden cross, giu den cat xuong)"),
    ("rsi2_duoi_15_giu1", lambda s: rule_rsi2_giu1(s, 15.0, False), "Ung vien cu D1: RSI(2)<15, giu 1 phien"),
    ("dip10_sma200_giu7", rule_dip10_sma200, "Dich D1 cua mua_giam_10_bar...tren_sma200 (H4 cu)"),
]


def fmt(m):
    if m["years"] is None or (isinstance(m["years"], float) and not np.isfinite(m["years"])):
        return "n/a"
    return (f"n={m['trades']:>4}  CAGR {m['cagr']:+6.1f}%  Sharpe {m['sharpe']:+5.2f}  "
            f"DD {m['dd']:5.1f}%  exp {100*m['exp']:5.1f}%  {m['years']:.1f}y")


def beat(row, bh):
    """So voi mua-va-giu cung cua so: Sharpe cao hon, hoac CAGR tuong duong va DD thap hon."""
    if not np.isfinite(row["sharpe"]) or not np.isfinite(bh["sharpe"]):
        return False, "thieu so"
    sh = row["sharpe"] > bh["sharpe"] + 1e-6
    # same return with lower DD: CAGR within 1pp and DD lower by >= 1pp
    same_ret_low_dd = (row["cagr"] >= bh["cagr"] - 1.0) and (row["dd"] <= bh["dd"] - 1.0)
    # also flag if both sharpe and calmar-ish better
    if sh:
        return True, "Sharpe hon BH"
    if same_ret_low_dd:
        return True, "CAGR ~ BH va DD thap hon"
    return False, "khong thang BH"


def main():
    costs, cost_src = load_costs()
    mapping = {
        "US500": "gspc_daily.csv",
        "US100": "ndx_daily.csv",
    }
    rows = []
    lines = []
    lines.append(f"# Loc nhe xu huong chi so (D1, phi XM, vs mua-va-giu)")
    lines.append(f"Phi: {cost_src}")
    lines.append(f"IS < 2016-01-01; OOS >= 2016-01-01. Fill open ke tiep. Triple Friday. Khong p-placebo.")
    lines.append("")
    for name, fname in mapping.items():
        c = costs[name]
        df = load_daily(fname)
        s = pack(df, c["spread_pts_median"], c["fin_long_annual"])
        lines.append(f"## {name}  {s['dates'][0].date()} .. {s['dates'][-1].date()}  n={s['n']}  "
                     f"spread={c['spread_pts_median']} fin={c['fin_long_annual']:.4f}")
        packed = {}
        for rule_name, fn, desc in RULES:
            pos, pnl = fn(s)
            sm = split_metrics(pnl, pos, s["t_open"], s["dates"])
            packed[rule_name] = sm
            rows.append(dict(symbol=name, rule=rule_name, desc=desc, **{
                f"{k}_{kk}": vv for k, m in sm.items() for kk, vv in m.items()
            }))
        bh = packed["mua_va_giu_1x"]
        for rule_name, fn, desc in RULES:
            sm = packed[rule_name]
            lines.append(f"### {rule_name}")
            lines.append(f"  {desc}")
            for part in ("IS", "OOS"):
                ok, why = beat(sm[part], bh[part]) if rule_name != "mua_va_giu_1x" else (False, "chuan")
                flag = "THANG_BH" if ok else "—"
                lines.append(f"  {part:3} {fmt(sm[part])}  {flag} {why if rule_name!='mua_va_giu_1x' else ''}")
        lines.append("")
    text = "\n".join(lines) + "\n"
    out_dir = Path(__file__).resolve().parents[3] / "docs" / "evo"
    # if running from worktree this is repo root
    repo = Path(__file__).resolve().parents[3]
    # tools/kiem_dinh/evo -> parents[0]=evo [1]=kiem_dinh [2]=tools [3]=repo. Yes.
    out_txt = repo / "docs" / "evo" / "loc_xu_huong_chi_so_bang.txt"
    out_txt.write_text(text, encoding="utf-8")
    print(text)
    print(f"wrote {out_txt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
