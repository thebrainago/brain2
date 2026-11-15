#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pre-registered 8-hypothesis test (frozen 2026-11-15 12:57 Asia/Saigon).

Parameters are taken from the published rules in
docs/evo/PREREG_GIA_THUYET_2026-11-15.md and are not tuned.
IS: date < 2016-01-01. OOS: date >= 2016-01-01, looked at once.
N_FDR = 8. 1x only. Demo / research; no live trading.

Reuse cost, metric, and random-shift helpers from ibs_cfd_my_backtest.py.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
DOCS = ROOT / "docs"
RESULTS = ROOT / "results" / "prereg_2026-11-15"
SPLIT = pd.Timestamp("2016-01-01")
N_RAND = 1000
RNG_SEED = 20261115
IBS_IN = 0.20
IBS_OUT = 0.80
IBS_MAX_BARS = 4  # closed D1 bars after entry; exit at open when held >= 4
RSI_N = 2
RSI_BUY = 10.0
RSI_SELL = 70.0
SMA_LEN = 200
N_LOW = 5
HOLD_LOW = 5
SIG_WIN = 20
SMA_MONTHS = 10


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


bt = _load("ibs_cfd_my_backtest", HERE / "ibs_cfd_my_backtest.py")
rf = _load("ibs_cfd_refine", HERE / "ibs_cfd_refine.py")

Trade = bt.Trade
load_daily = bt.load_daily
session_ibs = bt.session_ibs
rollover_units = bt.rollover_units
precompute_bar_units = bt.precompute_bar_units
costs_on_pos = bt.costs_on_pos
metrics = bt.metrics
ann_factor = bt.ann_factor
rand_p = bt.rand_p
bh_fdr = rf.bh_fdr
rsi_wilder = rf.rsi_wilder

FRI = 4
WED = 2


# ---------------------------------------------------------------------------
# Calendars
# ---------------------------------------------------------------------------
def easter_gregorian(year: int) -> date:
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def _observed_fixed(d: date, saturday_observed: bool) -> date:
    if d.weekday() == 5:  # Sat
        return (d - timedelta(days=1)) if saturday_observed else d
    if d.weekday() == 6:  # Sun
        return d + timedelta(days=1)
    return d


def nth_weekday(year, month, weekday, n):
    d = date(year, month, 1)
    off = (weekday - d.weekday()) % 7
    return d + timedelta(days=off + 7 * (n - 1))


def last_weekday(year, month, weekday):
    if month == 12:
        d = date(year, 12, 31)
    else:
        d = date(year, month + 1, 1) - timedelta(days=1)
    off = (d.weekday() - weekday) % 7
    return d - timedelta(days=off)


def nyse_holidays(y0: int, y1: int) -> set[date]:
    """Full NYSE holidays, as frozen in the pre-reg (Juneteenth from 2021)."""
    out: set[date] = set()
    for y in range(y0, y1 + 1):
        # New Year's Day: Sun → Monday; Sat is typically NOT observed on Friday
        ny = date(y, 1, 1)
        if ny.weekday() == 6:
            out.add(date(y, 1, 2))
        elif ny.weekday() < 5:
            out.add(ny)
        out.add(nth_weekday(y, 1, 0, 3))  # MLK, Monday
        out.add(nth_weekday(y, 2, 0, 3))  # Presidents
        out.add(easter_gregorian(y) - timedelta(days=2))  # Good Friday
        out.add(last_weekday(y, 5, 0))  # Memorial
        if y >= 2021:
            out.add(_observed_fixed(date(y, 6, 19), saturday_observed=True))
        out.add(_observed_fixed(date(y, 7, 4), saturday_observed=True))
        out.add(nth_weekday(y, 9, 0, 1))  # Labor
        out.add(nth_weekday(y, 11, 3, 4))  # Thanksgiving Thursday
        out.add(_observed_fixed(date(y, 12, 25), saturday_observed=True))
    return out


def load_fomc() -> list[pd.Timestamp]:
    p = DOCS / "calendars" / "fomc_scheduled_1985_2026.json"
    doc = json.loads(p.read_text(encoding="utf-8"))
    return [pd.Timestamp(d) for d in doc["dates"]]


# ---------------------------------------------------------------------------
# Series / costs
# ---------------------------------------------------------------------------
def load_us_costs():
    return json.loads((DOCS / "costs_xm_us_index.json").read_text(encoding="utf-8"))


def load_intl_costs():
    return json.loads((DOCS / "costs_xm_intl.json").read_text(encoding="utf-8"))


def pack_series(df: pd.DataFrame, spread, fin, triple) -> dict:
    df = df.copy()
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    df = df.sort_index()
    df = df.dropna(subset=["open", "high", "low", "close"])
    df = df[(df["high"] >= df["low"]) & (df["open"] > 0) & (df["close"] > 0)]
    n = len(df)
    open_ = df["open"].to_numpy(float)
    high = df["high"].to_numpy(float)
    low = df["low"].to_numpy(float)
    close = df["close"].to_numpy(float)
    dates = pd.DatetimeIndex(df.index)
    # next-open timestamps 09:30 ET (naive)
    t_open = dates + pd.Timedelta(hours=9, minutes=30)
    t_close = dates + pd.Timedelta(hours=16)
    r_close = np.zeros(n)
    r_close[1:] = np.where(close[:-1] > 0, close[1:] / close[:-1] - 1.0, 0.0)
    r_open = np.zeros(n)
    r_open[:-1] = np.where(open_[1:] > 0, np.where(open_[:-1] > 0, open_[1:] / open_[:-1] - 1.0, 0.0), 0.0)
    r_on = np.zeros(n)  # close[i] -> open[i+1]
    with np.errstate(divide="ignore", invalid="ignore"):
        r_on[:-1] = open_[1:] / close[:-1] - 1.0
        r_on[~np.isfinite(r_on)] = 0.0
        r_open[~np.isfinite(r_open)] = 0.0
        r_close[~np.isfinite(r_close)] = 0.0
    units_open = precompute_bar_units(t_open.to_pydatetime() if hasattr(t_open, "to_pydatetime") else t_open, triple)
    # overnight units: 16:00 day i -> 09:30 next session
    units_on = np.zeros(n, dtype=np.int16)
    for i in range(n - 1):
        units_on[i] = rollover_units(t_close[i], t_open[i + 1], triple)
    units_close = np.zeros(n, dtype=np.int16)
    for i in range(n - 1):
        units_close[i] = rollover_units(t_close[i], t_close[i + 1], triple)
    # causal 20-day close-to-close vol, known at open of bar i (uses r_close[i-20:i])
    sig = np.full(n, np.nan)
    # sig at open i uses 20 close-to-close returns ending at close i-1 (all known).
    for i in range(SIG_WIN + 1, n):
        w = r_close[i - SIG_WIN : i]
        if np.isfinite(w).sum() == SIG_WIN and float(np.nanstd(w, ddof=0)) > 1e-16:
            sig[i] = float(np.nanstd(w, ddof=0))
    ibs = session_ibs(high, low, close)
    return dict(
        dates=dates,
        open=open_,
        high=high,
        low=low,
        close=close,
        ibs=ibs,
        r_open=r_open,
        r_close=r_close,
        r_on=r_on,
        t_open=np.array(t_open, dtype="datetime64[ns]"),
        t_close=np.array(t_close, dtype="datetime64[ns]"),
        units_open=units_open,
        units_on=units_on,
        units_close=units_close,
        sig20=sig,
        spread=float(spread),
        fin=float(fin),
        triple=int(triple),
        n=n,
    )


def load_all():
    us = load_us_costs()["symbols"]
    intl = load_intl_costs()["symbols"]
    series = {}
    mapping = {
        "US100": ("ndx_daily.csv", us["US100"], FRI),
        "US500": ("gspc_daily.csv", us["US500"], FRI),
        "US30": ("dji_daily.csv", us["US30"], FRI),
        "GER40": ("gdaxi_daily.csv", intl["GER40"], intl["GER40"]["triple_weekday_python"]),
        "JP225": ("n225_daily.csv", intl["JP225"], intl["JP225"]["triple_weekday_python"]),
        "UK100": ("ftse_daily.csv", intl["UK100"], intl["UK100"]["triple_weekday_python"]),
        "XAU": ("xau_daily.csv", intl["XAU"], intl["XAU"]["triple_weekday_python"]),
        "AUDCAD": ("audcad_daily.csv", intl["AUDCAD"], intl["AUDCAD"]["triple_weekday_python"]),
    }
    for name, (fname, cost, triple) in mapping.items():
        df = load_daily(fname)
        series[name] = pack_series(df, cost["spread_pts_median"], cost["fin_long_annual"], triple)
        d0, d1 = series[name]["dates"][0], series[name]["dates"][-1]
        print(f"loaded {name:7} {str(d0.date())} .. {str(d1.date())}  n={series[name]['n']}  "
              f"spread={cost['spread_pts_median']} fin={cost['fin_long_annual']:.4f} triple={triple}")
    return series


# ---------------------------------------------------------------------------
# Rule engines — all fills at next open unless noted. No tuning.
# ---------------------------------------------------------------------------
def _trades_from_pos(pos, fill, r_fill, units, spread, fin) -> list:
    """Build Trade list from a 0/1 position on the fill grid (pos[i]=1 holds fill[i]→fill[i+1])."""
    n = len(pos)
    trades = []
    i = 0
    while i < n - 1:
        if pos[i] <= 0:
            i += 1
            continue
        j = i
        while j < n - 1 and pos[j] > 0:
            j += 1
        # hold i .. j-1, exit at fill[j]
        if j <= i or not np.isfinite(fill[i]) or not np.isfinite(fill[j]) or fill[i] <= 0:
            i = j + 1
            continue
        ru = int(units[i:j].sum())
        sf = spread / fill[i]
        ff = fin * ru / 365.0
        ret = (fill[j] - fill[i]) / fill[i] - sf - ff
        trades.append(Trade(1, i, j, float(ret), float(fill[i]), float(fill[j]), ru, float(sf), float(ff)))
        i = j
    return trades


def run_ibs(s: dict) -> tuple:
    """IBS < 0.20 at close, enter next open; exit IBS > 0.80 or after 4 closed D1 bars.
    No re-entry on the exit bar (matches IBS_US100.mq5)."""
    n = s["n"]
    ibs = s["ibs"]
    fill = s["open"]
    pos = np.zeros(n, dtype=float)
    t = 0
    while t < n - 1:
        if not (np.isfinite(ibs[t]) and ibs[t] < IBS_IN):
            t += 1
            continue
        entry = t + 1
        if entry >= n - 1 or not np.isfinite(fill[entry]) or fill[entry] <= 0:
            t += 1
            continue
        # at open of k, the just-closed bar is k-1; held closed bars = k - entry
        # exit when (k - entry) >= 4 or ibs[k-1] > 0.80, k >= entry+1
        exit_i = None
        for k in range(entry + 1, n):
            if not np.isfinite(fill[k]) or fill[k] <= 0:
                continue
            held = k - entry
            if (np.isfinite(ibs[k - 1]) and ibs[k - 1] > IBS_OUT) or held >= IBS_MAX_BARS:
                exit_i = k
                break
        if exit_i is None:
            break
        pos[entry:exit_i] = 1.0
        t = exit_i  # no same-bar re-entry; next signal is close of exit bar or later
    trades = _trades_from_pos(pos, fill, s["r_open"], s["units_open"], s["spread"], s["fin"])
    return pos, trades, fill, s["r_open"], s["t_open"], s["units_open"]


def tom_flags(dates: pd.DatetimeIndex) -> tuple[np.ndarray, np.ndarray]:
    """is_m1[i] True if session i is day -1 (last trading day of its calendar month).
    is_p4[i] True if session i is day +4 (4th trading day of its calendar month)."""
    n = len(dates)
    months = dates.month.to_numpy()
    years = dates.year.to_numpy()
    is_m1 = np.zeros(n, dtype=bool)
    is_p4 = np.zeros(n, dtype=bool)
    # last of month: next session is a later month (or end)
    for i in range(n):
        if i == n - 1 or (years[i + 1] > years[i] or months[i + 1] != months[i]):
            is_m1[i] = True
        # day number within month
    # +4: 4th session of a month
    count = 0
    prev = None
    for i in range(n):
        key = (int(years[i]), int(months[i]))
        if key != prev:
            count = 1
            prev = key
        else:
            count += 1
        if count == 4:
            is_p4[i] = True
    return is_m1, is_p4


def run_tom(s: dict) -> tuple:
    """Enter open of day -1, exit open of day +4."""
    n = s["n"]
    is_m1, is_p4 = tom_flags(s["dates"])
    fill = s["open"]
    pos = np.zeros(n, dtype=float)
    i = 0
    while i < n - 1:
        if not is_m1[i] or not np.isfinite(fill[i]) or fill[i] <= 0:
            i += 1
            continue
        # exit at first +4 strictly after entry i (the +4 of the *next* month)
        exit_i = None
        for k in range(i + 1, n):
            if is_p4[k] and np.isfinite(fill[k]) and fill[k] > 0:
                exit_i = k
                break
        if exit_i is None:
            break
        pos[i:exit_i] = 1.0
        i = exit_i
    trades = _trades_from_pos(pos, fill, s["r_open"], s["units_open"], s["spread"], s["fin"])
    return pos, trades, fill, s["r_open"], s["t_open"], s["units_open"]


def run_rsi2(s: dict) -> tuple:
    """RSI(2)<10 and close>SMA200 (hide first 199), enter next open; exit RSI(2)>70 next open."""
    n = s["n"]
    close = s["close"]
    fill = s["open"]
    rsi = rsi_wilder(close, RSI_N)
    sma = np.full(n, np.nan)
    csum = np.cumsum(close)
    for i in range(SMA_LEN - 1, n):
        # causal SMA of last 200 closes including i
        prev = csum[i - SMA_LEN] if i >= SMA_LEN else 0.0
        sma[i] = (csum[i] - prev) / SMA_LEN
    # hide first 199 bars (index 0..198): sma already nan there (need 200 points → first at 199)
    pos = np.zeros(n, dtype=float)
    t = 0
    while t < n - 1:
        ok = (np.isfinite(rsi[t]) and rsi[t] < RSI_BUY and np.isfinite(sma[t]) and close[t] > sma[t])
        if not ok:
            t += 1
            continue
        entry = t + 1
        if entry >= n - 1 or not np.isfinite(fill[entry]) or fill[entry] <= 0:
            t += 1
            continue
        exit_i = None
        for k in range(entry + 1, n):
            # decision at close k-1
            if np.isfinite(rsi[k - 1]) and rsi[k - 1] > RSI_SELL and np.isfinite(fill[k]) and fill[k] > 0:
                exit_i = k
                break
        if exit_i is None:
            break
        pos[entry:exit_i] = 1.0
        t = exit_i
    trades = _trades_from_pos(pos, fill, s["r_open"], s["units_open"], s["spread"], s["fin"])
    return pos, trades, fill, s["r_open"], s["t_open"], s["units_open"]


def run_nday_low(s: dict) -> tuple:
    """Close is the 5-day low (incl. today); enter next open; exit open after exactly 5 sessions."""
    n = s["n"]
    close = s["close"]
    fill = s["open"]
    pos = np.zeros(n, dtype=float)
    t = N_LOW - 1
    while t < n - 1:
        window = close[t - N_LOW + 1 : t + 1]
        if not (np.isfinite(close[t]) and np.isfinite(window).all() and close[t] <= np.min(window) + 1e-15):
            t += 1
            continue
        entry = t + 1
        exit_i = entry + HOLD_LOW
        if exit_i >= n or not np.isfinite(fill[entry]) or fill[entry] <= 0 or not np.isfinite(fill[exit_i]) or fill[exit_i] <= 0:
            t += 1
            continue
        pos[entry:exit_i] = 1.0
        t = exit_i  # no overlap / no same-bar re-entry
    trades = _trades_from_pos(pos, fill, s["r_open"], s["units_open"], s["spread"], s["fin"])
    return pos, trades, fill, s["r_open"], s["t_open"], s["units_open"]


def run_overnight(s: dict) -> tuple:
    """Long every close→next open. Spread each night. Financing if the hold crosses 17:00 ET."""
    n = s["n"]
    pos = np.zeros(n, dtype=float)
    pos[: n - 1] = 1.0  # hold close[i]→open[i+1] recorded on slot i; last bar incomplete
    # trades: one per night
    trades = []
    fill_entry = s["close"]
    fill_exit = np.concatenate([s["open"][1:], [np.nan]])
    for i in range(n - 1):
        if not (np.isfinite(fill_entry[i]) and fill_entry[i] > 0 and np.isfinite(fill_exit[i]) and fill_exit[i] > 0):
            pos[i] = 0.0
            continue
        ru = int(s["units_on"][i])
        sf = s["spread"] / fill_entry[i]
        ff = s["fin"] * ru / 365.0
        ret = (fill_exit[i] - fill_entry[i]) / fill_entry[i] - sf - ff
        trades.append(Trade(1, i, i + 1, float(ret), float(fill_entry[i]), float(fill_exit[i]), ru, float(sf), float(ff)))
    return pos, trades, s["close"], s["r_on"], s["t_close"], s["units_on"]


def run_holiday_fomc(s: dict, holidays: set[date], fomc: list[pd.Timestamp]) -> tuple:
    """Union of NYSE pre-holiday (open last session before holiday → next session open)
    and scheduled FOMC (close T-1 → close T)."""
    n = s["n"]
    dates = s["dates"]
    dlist = [ts.date() for ts in dates]
    dset = set(dlist)
    # map date -> index
    idx = {d: i for i, d in enumerate(dlist)}
    pos_open = np.zeros(n, dtype=float)  # on open-to-open grid for holiday
    # Holiday windows on the open grid
    hol_sorted = sorted(holidays)
    for i, d in enumerate(dlist):
        # last session before a full holiday: next calendar closed day(s) include a holiday
        # and the next *trading* session is after that holiday.
        if i >= n - 1:
            continue
        nxt = dlist[i + 1]
        # sessions skipped between d and nxt
        gap_days = (nxt - d).days
        if gap_days <= 1:
            continue
        # any full holiday strictly after d and before nxt?
        has = False
        dd = d + timedelta(days=1)
        while dd < nxt:
            if dd in holidays:
                has = True
                break
            dd += timedelta(days=1)
        if has:
            pos_open[i] = 1.0  # hold open[i] → open[i+1]

    # FOMC on the close grid: enter close of T-1, exit close of T
    # If T is not a trading day, use the previous session as T (announcement still 14:00; if market closed, skip).
    pos_close = np.zeros(n, dtype=float)
    for t in fomc:
        td = pd.Timestamp(t).date()
        if td not in idx:
            # if announcement falls on a closed day, skip (cannot exit at that close)
            continue
        j = idx[td]
        if j == 0:
            continue
        pos_close[j - 1] = 1.0  # hold close[j-1] → close[j]

    # Combine onto a daily open-to-open book? Returns/costs differ by fill grid.
    # Build a daily PnL by applying each book on its own grid, then union is the sum
    # of pnls minus double-counting on overlap. Cleaner: construct a per-bar long
    # exposure in "session + overnight" pieces.
    #
    # Holiday: long from open[i] to open[i+1] = regular session i (open→close) + overnight i (close→next open).
    # FOMC: long from close[j-1] to close[j] = overnight j-1 + session j (open→close).
    # We'll compute pnl directly as sum of event contributions with overlap cap at 1x.

    # session return open[i]→close[i]
    r_oc = np.zeros(n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r_oc = np.where(s["open"] > 0, s["close"] / s["open"] - 1.0, 0.0)
        r_oc[~np.isfinite(r_oc)] = 0.0
    # long_session[i] / long_on[i]
    long_sess = np.zeros(n, dtype=float)
    long_on = np.zeros(n, dtype=float)
    long_sess += pos_open  # holiday holds the session of day i
    long_on += pos_open    # and the overnight of day i
    long_on += pos_close   # FOMC holds overnight of T-1 (index j-1)
    # FOMC also holds the session of T (index j) = the day after the pos_close slot
    for i in range(n):
        if pos_close[i] > 0 and i + 1 < n:
            long_sess[i + 1] = 1.0
    long_sess = np.clip(long_sess, 0, 1)
    long_on = np.clip(long_on, 0, 1)

    # costs: spread once per contiguous exposure on the union path
    # Approximate implementable costs: charge a half-spread whenever the combined
    # position goes from flat to long or long to flat, using a timeline
    # open-session-close-overnight-open. Also financing on overnight holds.
    pnl = np.zeros(n)
    # We accumulate PnL on the overnight slot i (close i → open i+1) and on the
    # session of day i (at close of i). For reporting, put session pnl on bar i
    # as well (same daily bucket).
    # Spread: walk the timeline.
    # States at: open i, close i, open i+1, ...
    # position before open i = long_on[i-1]; session i = long_sess[i]; overnight i = long_on[i]
    px_open, px_close = s["open"], s["close"]
    spread, fin = s["spread"], s["fin"]

    def half_spread(px):
        return (spread / 2.0 / px) if (np.isfinite(px) and px > 0) else 0.0

    # start flat before first open
    prev = 0.0
    for i in range(n):
        # enter/exit at open i for session
        cur = long_sess[i]
        if cur > 0 and prev <= 0 and np.isfinite(px_open[i]) and px_open[i] > 0:
            pnl[i] -= half_spread(px_open[i])
        if cur <= 0 and prev > 0 and np.isfinite(px_open[i]) and px_open[i] > 0:
            pnl[i] -= half_spread(px_open[i])
        if cur > 0:
            pnl[i] += r_oc[i]
        prev = cur
        # enter/exit at close i for overnight
        cur = long_on[i]
        if cur > 0 and prev <= 0 and np.isfinite(px_close[i]) and px_close[i] > 0:
            pnl[i] -= half_spread(px_close[i])
        if cur <= 0 and prev > 0 and np.isfinite(px_close[i]) and px_close[i] > 0:
            pnl[i] -= half_spread(px_close[i])
        if cur > 0 and i < n - 1:
            pnl[i] += s["r_on"][i]
            pnl[i] -= fin * float(s["units_on"][i]) / 365.0
        prev = cur
    # leftover exit at last available price is dropped if still in (incomplete)

    # Build trades as contiguous union stretches on a daily "any exposure" flag
    # from first entry price to last exit, for PF reporting.
    held = ((long_sess + long_on) > 0).astype(float)
    # trade ret = sum of pnl over the stretch (already after costs)
    trades = []
    i = 0
    while i < n:
        if held[i] <= 0:
            i += 1
            continue
        j = i
        while j < n and held[j] > 0:
            j += 1
        ret = float(pnl[i:j].sum())
        # dummy prices
        trades.append(Trade(1, i, min(j, n - 1), ret, float(px_open[i]), float(px_open[min(j, n - 1)]), 0, 0.0, 0.0))
        i = j
    # For random-shift we will shift (long_sess, long_on) jointly — handled in evaluate_event_union
    aux = dict(long_sess=long_sess, long_on=long_on, r_oc=r_oc, held=held, pnl=pnl)
    return held, trades, s["open"], s["r_open"], s["t_open"], s["units_open"], aux


def run_sma10(s: dict) -> tuple:
    """Faber 10-month SMA, 1x. Month-end close vs SMA of last 10 month-end closes
    (including this month); long next month if above, else flat. Fill first open of next month."""
    n = s["n"]
    dates = s["dates"]
    close, fill = s["close"], s["open"]
    months = dates.month.to_numpy()
    years = dates.year.to_numpy()
    # month-end indices
    ends = []
    for i in range(n):
        if i == n - 1 or years[i + 1] > years[i] or months[i + 1] != months[i]:
            ends.append(i)
    ends = np.array(ends, dtype=int)
    me_close = close[ends]
    # first open of each month: first session of that month
    first = []
    prev = None
    for i in range(n):
        key = (int(years[i]), int(months[i]))
        if key != prev:
            first.append(i)
            prev = key
    first = np.array(first, dtype=int)
    # map (year,month) of a month-end to the first index of the *next* month
    first_of = {(int(years[i]), int(months[i])): i for i in first}
    pos = np.zeros(n, dtype=float)
    # signal at month-end e (need 10 month-end closes including e → index >= 9 in ends)
    for k in range(SMA_MONTHS - 1, len(ends)):
        sma = float(me_close[k - SMA_MONTHS + 1 : k + 1].mean())
        long_next = me_close[k] > sma
        e = ends[k]
        # next month key
        y, m = int(years[e]), int(months[e])
        if m == 12:
            ny, nm = y + 1, 1
        else:
            ny, nm = y, m + 1
        if (ny, nm) not in first_of:
            continue
        a = first_of[(ny, nm)]
        # exit at first open of the month after next (or end)
        if nm == 12:
            ey, em = ny + 1, 1
        else:
            ey, em = ny, nm + 1
        b = first_of.get((ey, em), None)
        if b is None:
            # incomplete last month: drop
            continue
        if long_next:
            pos[a:b] = 1.0
    trades = _trades_from_pos(pos, fill, s["r_open"], s["units_open"], s["spread"], s["fin"])
    return pos, trades, fill, s["r_open"], s["t_open"], s["units_open"]


# ---------------------------------------------------------------------------
# Pooling
# ---------------------------------------------------------------------------
def align_members(members: list[dict], names: list[str]):
    """Inner-join? No: union of dates, missing → no participation that day."""
    all_dates = sorted(set().union(*[set(m["dates"].date) for m in members]))
    # Use pandas for alignment on a common calendar: union, reindex member arrays
    cal = pd.DatetimeIndex(pd.to_datetime(all_dates)).normalize()
    packed = []
    for s in members:
        ix = pd.DatetimeIndex(s["dates"]).normalize()
        loc = ix.get_indexer(cal)  # -1 if missing
        packed.append(loc)
    return cal, packed


def member_arrays_on_cal(s, loc, key):
    arr = s[key]
    out = np.full(len(loc), np.nan if arr.dtype.kind == "f" else 0, dtype=float if arr.dtype.kind == "f" else arr.dtype)
    ok = loc >= 0
    if arr.dtype.kind not in "f":
        out = np.zeros(len(loc), dtype=arr.dtype)
    else:
        out = np.full(len(loc), np.nan, dtype=float)
    out_ok = np.zeros(len(loc), dtype=bool)
    out_ok[ok] = True
    if arr.dtype.kind in "f":
        tmp = np.full(len(loc), np.nan, dtype=float)
        tmp[ok] = arr[loc[ok]]
        return tmp, ok
    tmp = np.zeros(len(loc), dtype=arr.dtype)
    tmp[ok] = arr[loc[ok]]
    return tmp, ok


def equal_risk_pnl(member_pos, member_r_net, member_sig, member_ok):
    """w = 1/σ among members in a trade with valid σ; else equal among those in a trade. Sum w=1."""
    n_m = len(member_pos)
    n = len(member_pos[0])
    pnl = np.zeros(n)
    w_sum_store = np.zeros(n)
    for t in range(n):
        active = []
        for j in range(n_m):
            if member_ok[j][t] and member_pos[j][t] > 0 and np.isfinite(member_r_net[j][t]):
                active.append(j)
        if not active:
            continue
        sigs = []
        for j in active:
            sg = member_sig[j][t]
            sigs.append(sg if (np.isfinite(sg) and sg > 0) else np.nan)
        if np.isfinite(sigs).all():
            inv = np.array([1.0 / s for s in sigs])
        else:
            inv = np.ones(len(active))
        w = inv / inv.sum()
        acc = 0.0
        for k, j in enumerate(active):
            acc += w[k] * member_r_net[j][t]
        pnl[t] = acc
        w_sum_store[t] = 1.0
    return pnl, w_sum_store


def equal_weight_pnl(member_r_net, member_ok):
    """Equal weight among members with data that day (flat members contribute 0)."""
    n_m = len(member_r_net)
    n = len(member_r_net[0])
    pnl = np.zeros(n)
    for t in range(n):
        vals = []
        for j in range(n_m):
            if member_ok[j][t] and np.isfinite(member_r_net[j][t]):
                vals.append(member_r_net[j][t])
        if vals:
            pnl[t] = float(np.mean(vals))
    return pnl


def net_from_pos(s, pos, fill, r_fill, units):
    pnl = costs_on_pos(pos, r_fill, s["t_open"], fill, s["spread"], s["fin"], s["triple"], units)
    return pnl


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
def split_masks(dates, split=SPLIT):
    di = pd.DatetimeIndex(dates).tz_localize(None).normalize()
    is_m = di < split
    oos_m = di >= split
    return is_m, oos_m


def gate_event(row, prefix="OOS"):
    tr = row.get(f"{prefix}_trades") or 0
    sh = row.get(f"{prefix}_sharpe")
    pf = row.get(f"{prefix}_pf")
    avg = row.get(f"{prefix}_avg")
    p = row.get(f"{prefix}_p_rand")
    def fin(x):
        return x is not None and np.isfinite(x)
    if tr >= 30 and fin(avg) and avg > 0 and fin(pf) and pf >= 1.20 and fin(sh) and sh >= 0.30 and fin(p) and p <= 0.05:
        return True
    return False


def gate_cont(row, prefix="OOS"):
    sh = row.get(f"{prefix}_sharpe")
    p = row.get(f"{prefix}_p_rand")
    cagr = row.get(f"{prefix}_cagr")
    def fin(x):
        return x is not None and np.isfinite(x)
    return fin(sh) and sh >= 0.30 and fin(p) and p <= 0.05 and fin(cagr) and cagr > 0


def metrics_on(pnl, trades, dates, mask):
    idx = np.flatnonzero(mask)
    if len(idx) == 0:
        return dict(trades=0, win=np.nan, avg=np.nan, pf=np.nan, sharpe=0.0, cagr=0.0, maxdd=0.0, tot=0.0)
    sub_pnl = np.zeros_like(pnl)
    sub_pnl[idx] = pnl[idx]
    # trades wholly inside the window (entry and exit in mask)
    # use mid: entry in window
    sub_tr = []
    mset = set(idx.tolist())
    for tr in trades:
        if tr.entry_i in mset and tr.exit_i in mset:
            sub_tr.append(tr)
        elif tr.entry_i in mset and tr.exit_i not in mset:
            # clip: use sum of pnl in-window as the trade ret (descriptive)
            a, b = tr.entry_i, min(tr.exit_i, int(idx[-1]) + 1)
            sub_tr.append(Trade(1, a, b, float(pnl[a:b].sum()), tr.entry_px, tr.exit_px, 0, 0.0, 0.0))
    times = np.array(dates)[idx] if not isinstance(dates, np.ndarray) else dates[idx]
    ann = ann_factor(times)
    # metrics() uses all pnl; pass only the slice
    met = metrics(pnl[idx], sub_tr, times, ann)
    met["ann"] = ann
    return met


def overnight_pnl(s, pos):
    """pos[i]=1 means hold close[i]→open[i+1]. Charge spread every night + overnight units."""
    n = s["n"]
    pnl = np.zeros(n)
    for i in range(n - 1):
        if pos[i] <= 0:
            continue
        px = s["close"][i]
        if not (np.isfinite(px) and px > 0):
            continue
        pnl[i] = s["r_on"][i] - (s["spread"] / px) - s["fin"] * float(s["units_on"][i]) / 365.0
    return pnl


def overnight_rand_p(s, pos, mask, sharpe0, ann, rng):
    """Fallback when exposure is almost always on: circular-shift the raw overnight
    returns, keep the cost calendar (spread+Friday triples) fixed, recompute Sharpe."""
    idx = np.flatnonzero(mask)
    m = len(idx)
    if m < 80:
        return np.nan
    r = s["r_on"].copy()
    # costs calendar depends on pos (almost always 1) and weekday units / price
    def sharpe_from_r(rvec):
        pnl = np.zeros(s["n"])
        for i in range(s["n"] - 1):
            if pos[i] <= 0:
                continue
            px = s["close"][i]
            if not (np.isfinite(px) and px > 0):
                continue
            pnl[i] = rvec[i] - (s["spread"] / px) - s["fin"] * float(s["units_on"][i]) / 365.0
        q = pnl[idx]
        sd = q.std(ddof=0)
        return float(q.mean() / sd * np.sqrt(ann)) if sd > 0 else 0.0

    null = np.empty(N_RAND)
    r_m = r[idx]
    for j in range(N_RAND):
        k = int(rng.integers(20, m - 20))
        r2 = r.copy()
        r2[idx] = np.roll(r_m, k)
        null[j] = sharpe_from_r(r2)
    return float((1.0 + np.sum(null >= sharpe0)) / (N_RAND + 1.0))


def event_union_pnl(s, long_sess, long_on):
    n = s["n"]
    r_oc = np.zeros(n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r_oc = np.where(s["open"] > 0, s["close"] / s["open"] - 1.0, 0.0)
        r_oc[~np.isfinite(r_oc)] = 0.0
    pnl = np.zeros(n)
    px_open, px_close = s["open"], s["close"]
    spread, fin = s["spread"], s["fin"]

    def half(px):
        return (spread / 2.0 / px) if (np.isfinite(px) and px > 0) else 0.0

    prev = 0.0
    for i in range(n):
        cur = long_sess[i]
        if cur > 0 and prev <= 0:
            pnl[i] -= half(px_open[i])
        if cur <= 0 and prev > 0:
            pnl[i] -= half(px_open[i])
        if cur > 0:
            pnl[i] += r_oc[i]
        prev = cur
        cur = long_on[i]
        if cur > 0 and prev <= 0:
            pnl[i] -= half(px_close[i])
        if cur <= 0 and prev > 0:
            pnl[i] -= half(px_close[i])
        if cur > 0 and i < n - 1:
            pnl[i] += s["r_on"][i]
            pnl[i] -= fin * float(s["units_on"][i]) / 365.0
        prev = cur
    return pnl


def evaluate_standard(name, rule, s, pos, trades, fill, r_fill, times, units, rng, kind="event"):
    pnl = costs_on_pos(pos, r_fill, times, fill, s["spread"], s["fin"], s["triple"], units)
    dates = s["dates"]
    is_m, oos_m = split_masks(dates)
    row = {"name": name, "rule": rule, "kind": kind, "symbol": name}
    for prefix, mask in (("IS", is_m), ("OOS", oos_m)):
        met = metrics_on(pnl, trades, dates, mask)
        for k, v in met.items():
            if k == "ann":
                continue
            row[f"{prefix}_{k}"] = v
        ann = met["ann"]
        sh = met["sharpe"]
        if kind == "overnight":
            # always-on: standard pos-shift is degenerate
            p = overnight_rand_p(s, pos, mask, sh, ann, rng)
            row[f"{prefix}_p_mode"] = "shift_overnight_returns_keep_cost_calendar"
        else:
            p, _ = rand_p(pos, r_fill, times, fill, s["spread"], s["fin"], mask, sh, ann, rng,
                          n_rand=N_RAND, triple_weekday=s["triple"])
            row[f"{prefix}_p_mode"] = "shift_position"
        row[f"{prefix}_p_rand"] = p if (p is not None and np.isfinite(p)) else np.nan
        if kind in ("event",):
            row[f"{prefix}_pass_gate"] = gate_event(row, prefix)
        else:
            row[f"{prefix}_pass_gate"] = gate_cont(row, prefix)
    return row, pnl


def evaluate_overnight(name, rule, s, pos, trades, rng):
    pnl = overnight_pnl(s, pos)
    dates = s["dates"]
    is_m, oos_m = split_masks(dates)
    row = {"name": name, "rule": rule, "kind": "overnight", "symbol": name}
    for prefix, mask in (("IS", is_m), ("OOS", oos_m)):
        met = metrics_on(pnl, trades, dates, mask)
        for k, v in met.items():
            if k == "ann":
                continue
            row[f"{prefix}_{k}"] = v
        p = overnight_rand_p(s, pos, mask, met["sharpe"], met["ann"], rng)
        row[f"{prefix}_p_rand"] = p if (p is not None and np.isfinite(p)) else np.nan
        row[f"{prefix}_p_mode"] = "shift_overnight_returns_keep_cost_calendar"
        row[f"{prefix}_pass_gate"] = gate_cont(row, prefix)
    return row, pnl


def evaluate_union(name, rule, s, trades, aux, rng):
    pnl = aux["pnl"]
    dates = s["dates"]
    is_m, oos_m = split_masks(dates)
    row = {"name": name, "rule": rule, "kind": "event", "symbol": name}
    long_sess, long_on = aux["long_sess"], aux["long_on"]
    for prefix, mask in (("IS", is_m), ("OOS", oos_m)):
        met = metrics_on(pnl, trades, dates, mask)
        for k, v in met.items():
            if k == "ann":
                continue
            row[f"{prefix}_{k}"] = v
        # joint circular shift of (long_sess, long_on)
        idx = np.flatnonzero(mask)
        m = len(idx)
        sh0 = met["sharpe"]
        ann = met["ann"]
        if m < 80 or (long_sess[idx].sum() + long_on[idx].sum() == 0):
            p = np.nan
        else:
            null = np.empty(N_RAND)
            ls_m = long_sess[idx].copy()
            lo_m = long_on[idx].copy()
            for j in range(N_RAND):
                k = int(rng.integers(20, m - 20))
                ls = long_sess.copy(); lo = long_on.copy()
                ls[idx] = np.roll(ls_m, k)
                lo[idx] = np.roll(lo_m, k)
                pnl_s = event_union_pnl(s, ls, lo)
                q = pnl_s[idx]
                sd = q.std(ddof=0)
                null[j] = q.mean() / sd * np.sqrt(ann) if sd > 0 else 0.0
            p = float((1.0 + np.sum(null >= sh0)) / (N_RAND + 1.0))
        row[f"{prefix}_p_rand"] = p if (p is not None and np.isfinite(p)) else np.nan
        row[f"{prefix}_p_mode"] = "shift_union_exposure"
        row[f"{prefix}_pass_gate"] = gate_event(row, prefix)
    return row, pnl


def evaluate_pool(name, rule, cal, pnl, held, trades, rng, member_bundle, kind="event"):
    """member_bundle for rand: list of dicts with pos, r_fill, fill, spread, fin, units, sig, ok, t_open, triple.
    Jointly shift member pos, reapply costs, rebuild equal-risk (or equal-weight) pnl."""
    dates = cal
    is_m, oos_m = split_masks(dates)
    row = {"name": name, "rule": rule, "kind": kind, "symbol": name}
    mode = member_bundle.get("mode", "equal_risk")
    for prefix, mask in (("IS", is_m), ("OOS", oos_m)):
        met = metrics_on(pnl, trades, dates, mask)
        for k, v in met.items():
            if k == "ann":
                continue
            row[f"{prefix}_{k}"] = v
        idx = np.flatnonzero(mask)
        m = len(idx)
        sh0 = met["sharpe"]
        ann = met["ann"]
        members = member_bundle["members"]
        if m < 80:
            p = np.nan
        else:
            null = np.empty(N_RAND)
            pos_m = [mb["pos"][idx].copy() for mb in members]
            for j in range(N_RAND):
                k = int(rng.integers(20, m - 20))
                r_nets = []
                oks = []
                sigs = []
                poss = []
                for u, mb in enumerate(members):
                    pos_s = mb["pos"].copy()
                    pos_s[idx] = np.roll(pos_m[u], k)
                    r_net = costs_on_pos(pos_s, mb["r_fill"], mb["times"], mb["fill"], mb["spread"], mb["fin"], mb["triple"], mb["units"])
                    r_nets.append(r_net)
                    oks.append(mb["ok"])
                    sigs.append(mb["sig"])
                    poss.append(pos_s)
                if mode == "equal_weight":
                    pnl_s = equal_weight_pnl(r_nets, oks)
                else:
                    pnl_s, _ = equal_risk_pnl(poss, r_nets, sigs, oks)
                q = pnl_s[idx]
                sd = q.std(ddof=0)
                null[j] = q.mean() / sd * np.sqrt(ann) if sd > 0 else 0.0
            p = float((1.0 + np.sum(null >= sh0)) / (N_RAND + 1.0))
        row[f"{prefix}_p_rand"] = p if (p is not None and np.isfinite(p)) else np.nan
        row[f"{prefix}_p_mode"] = f"shift_member_pos_{mode}"
        if kind == "event":
            row[f"{prefix}_pass_gate"] = gate_event(row, prefix)
        else:
            row[f"{prefix}_pass_gate"] = gate_cont(row, prefix)
    return row


def book_trades_from_pnl(pnl, held, dates):
    trades = []
    n = len(pnl)
    i = 0
    while i < n:
        if held[i] <= 0:
            i += 1
            continue
        j = i
        while j < n and held[j] > 0:
            j += 1
        trades.append(Trade(1, i, min(j, n - 1), float(pnl[i:j].sum()), 1.0, 1.0, 0, 0.0, 0.0))
        i = j
    return trades


def fmt(x, nd=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "NA"
    if isinstance(x, (bool, np.bool_)):
        return "Y" if x else "N"
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    return f"{float(x):.{nd}f}"


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(RNG_SEED)
    print("loading series…")
    series = load_all()
    holidays = nyse_holidays(1970, 2027)
    fomc = load_fomc()
    print("NYSE holidays", len(holidays), "FOMC scheduled", len(fomc))

    rows = []
    confirm_rows = []

    # ---- (a) IBS equal-risk US100+US500+US30 vs US100 alone ----
    print("\n=== (a) IBS pool ===")
    ibs_run = {}
    for nm in ("US100", "US500", "US30"):
        ibs_run[nm] = run_ibs(series[nm])
        pos, trades, fill, r_fill, times, units = ibs_run[nm]
        row, _ = evaluate_standard(nm, "ibs_a", series[nm], pos, trades, fill, r_fill, times, units, rng, "event")
        if nm == "US100":
            row["role"] = "confirm_a_US100_alone"
            confirm_rows.append(row)
        else:
            row["role"] = f"confirm_a_{nm}"
            confirm_rows.append(row)
        print("  ", nm, "OOS", {k: row[k] for k in row if k.startswith("OOS_")})

    # pool on union calendar
    names_a = ["US100", "US500", "US30"]
    members_a = [series[n] for n in names_a]
    cal_a, locs_a = align_members(members_a, names_a)
    pos_a, rnet_a, sig_a, ok_a, bundle_a = [], [], [], [], []
    N = len(cal_a)
    for i, nm in enumerate(names_a):
        s = series[nm]
        loc = locs_a[i]
        pos_m, trades_m, fill, r_fill, times, units = ibs_run[nm]
        # map to calendar
        pos_c = np.zeros(N)
        r_fill_c = np.zeros(N)
        fill_c = np.full(N, np.nan)
        units_c = np.zeros(N, dtype=np.int16)
        sig_c = np.full(N, np.nan)
        ok = loc >= 0
        # only map indices that exist; r_fill/units at last native bar may be 0
        for t, j in enumerate(loc):
            if j < 0:
                continue
            pos_c[t] = pos_m[j]
            r_fill_c[t] = r_fill[j]
            fill_c[t] = fill[j]
            units_c[t] = units[j]
            sig_c[t] = s["sig20"][j]
        r_net = costs_on_pos(pos_c, r_fill_c, cal_a + pd.Timedelta(hours=9, minutes=30), fill_c,
                             s["spread"], s["fin"], s["triple"], units_c)
        # days without the name: not ok
        r_net = np.where(ok, r_net, 0.0)
        pos_c = np.where(ok, pos_c, 0.0)
        pos_a.append(pos_c); rnet_a.append(r_net); sig_a.append(sig_c); ok_a.append(ok)
        bundle_a.append(dict(pos=pos_c, r_fill=r_fill_c, fill=fill_c, spread=s["spread"], fin=s["fin"],
                             units=units_c, sig=sig_c, ok=ok, times=cal_a + pd.Timedelta(hours=9, minutes=30),
                             triple=s["triple"]))
    pnl_a, held_a = equal_risk_pnl(pos_a, rnet_a, sig_a, ok_a)
    tr_a = book_trades_from_pnl(pnl_a, held_a, cal_a)
    row_a = evaluate_pool("US100+US500+US30", "a_ibs_equal_risk", cal_a, pnl_a, held_a, tr_a, rng,
                          dict(mode="equal_risk", members=bundle_a), "event")
    row_a["role"] = "primary"
    row_a["hypothesis"] = "a"
    rows.append(row_a)
    print("  PRIMARY a", {k: row_a[k] for k in row_a if k.startswith("OOS_") or k.startswith("IS_")})

    # ---- (b) TOM equal-risk pool ----
    print("\n=== (b) TOM pool ===")
    tom_run = {}
    for nm in ("US100", "US500", "US30"):
        tom_run[nm] = run_tom(series[nm])
        pos, trades, fill, r_fill, times, units = tom_run[nm]
        row, _ = evaluate_standard(nm, "tom_b", series[nm], pos, trades, fill, r_fill, times, units, rng, "event")
        row["role"] = f"confirm_b_{nm}"
        confirm_rows.append(row)
        print("  ", nm, "OOS trades", row["OOS_trades"], "pf", row["OOS_pf"], "sh", row["OOS_sharpe"], "p", row["OOS_p_rand"])

    pos_b, rnet_b, sig_b, ok_b, bundle_b = [], [], [], [], []
    for i, nm in enumerate(names_a):
        s = series[nm]
        loc = locs_a[i]
        pos_m, trades_m, fill, r_fill, times, units = tom_run[nm]
        pos_c = np.zeros(N); r_fill_c = np.zeros(N); fill_c = np.full(N, np.nan)
        units_c = np.zeros(N, dtype=np.int16); sig_c = np.full(N, np.nan)
        ok = loc >= 0
        for t, j in enumerate(loc):
            if j < 0:
                continue
            pos_c[t] = pos_m[j]; r_fill_c[t] = r_fill[j]; fill_c[t] = fill[j]
            units_c[t] = units[j]; sig_c[t] = s["sig20"][j]
        r_net = costs_on_pos(pos_c, r_fill_c, cal_a + pd.Timedelta(hours=9, minutes=30), fill_c,
                             s["spread"], s["fin"], s["triple"], units_c)
        r_net = np.where(ok, r_net, 0.0); pos_c = np.where(ok, pos_c, 0.0)
        pos_b.append(pos_c); rnet_b.append(r_net); sig_b.append(sig_c); ok_b.append(ok)
        bundle_b.append(dict(pos=pos_c, r_fill=r_fill_c, fill=fill_c, spread=s["spread"], fin=s["fin"],
                             units=units_c, sig=sig_c, ok=ok, times=cal_a + pd.Timedelta(hours=9, minutes=30),
                             triple=s["triple"]))
    pnl_b, held_b = equal_risk_pnl(pos_b, rnet_b, sig_b, ok_b)
    tr_b = book_trades_from_pnl(pnl_b, held_b, cal_a)
    row_b = evaluate_pool("US100+US500+US30", "b_tom_equal_risk", cal_a, pnl_b, held_b, tr_b, rng,
                          dict(mode="equal_risk", members=bundle_b), "event")
    row_b["role"] = "primary"
    row_b["hypothesis"] = "b"
    rows.append(row_b)
    print("  PRIMARY b", {k: row_b[k] for k in row_b if k.startswith("OOS_")})

    # ---- (c) RSI2 US100 ----
    print("\n=== (c) RSI(2) ===")
    for nm, role in (("US100", "primary"), ("US500", "confirm_c_US500")):
        pos, trades, fill, r_fill, times, units = run_rsi2(series[nm])
        row, _ = evaluate_standard(nm, "c_rsi2", series[nm], pos, trades, fill, r_fill, times, units, rng, "event")
        row["role"] = role
        row["hypothesis"] = "c"
        (rows if role == "primary" else confirm_rows).append(row)
        print("  ", nm, role, "OOS", row["OOS_trades"], row["OOS_pf"], row["OOS_sharpe"], row["OOS_p_rand"], row["OOS_pass_gate"])

    # ---- (d) 5-day low ----
    print("\n=== (d) 5-day low ===")
    for nm, role in (("US100", "primary"), ("US500", "confirm_d_US500")):
        pos, trades, fill, r_fill, times, units = run_nday_low(series[nm])
        row, _ = evaluate_standard(nm, "d_5day_low", series[nm], pos, trades, fill, r_fill, times, units, rng, "event")
        row["role"] = role
        row["hypothesis"] = "d"
        (rows if role == "primary" else confirm_rows).append(row)
        print("  ", nm, role, "OOS", row["OOS_trades"], row["OOS_pf"], row["OOS_sharpe"], row["OOS_p_rand"], row["OOS_pass_gate"])

    # ---- (e) overnight ----
    print("\n=== (e) overnight ===")
    for nm, role in (("US100", "primary"), ("US500", "confirm_e_US500")):
        pos, trades, fill, r_fill, times, units = run_overnight(series[nm])
        row, _ = evaluate_overnight(nm, "e_overnight", series[nm], pos, trades, rng)
        row["role"] = role
        row["hypothesis"] = "e"
        (rows if role == "primary" else confirm_rows).append(row)
        print("  ", nm, role, "OOS sh", row["OOS_sharpe"], "cagr", row["OOS_cagr"], "p", row["OOS_p_rand"], row["OOS_pass_gate"])

    # ---- (f) holiday + FOMC ----
    print("\n=== (f) pre-holiday + FOMC ===")
    for nm, role in (("US100", "primary"), ("US500", "confirm_f_US500")):
        held, trades, fill, r_fill, times, units, aux = run_holiday_fomc(series[nm], holidays, fomc)
        row, _ = evaluate_union(nm, "f_holiday_fomc", series[nm], trades, aux, rng)
        row["role"] = role
        row["hypothesis"] = "f"
        (rows if role == "primary" else confirm_rows).append(row)
        print("  ", nm, role, "OOS", row["OOS_trades"], row["OOS_pf"], row["OOS_sharpe"], row["OOS_p_rand"], row["OOS_pass_gate"])

    # ---- (g) SMA 10m ----
    print("\n=== (g) SMA10 1x ===")
    for nm, role in (("US100", "primary"), ("US500", "confirm_g_US500")):
        pos, trades, fill, r_fill, times, units = run_sma10(series[nm])
        row, _ = evaluate_standard(nm, "g_sma10", series[nm], pos, trades, fill, r_fill, times, units, rng, "cont")
        row["role"] = role
        row["hypothesis"] = "g"
        (rows if role == "primary" else confirm_rows).append(row)
        print("  ", nm, role, "OOS sh", row["OOS_sharpe"], "cagr", row["OOS_cagr"], "p", row["OOS_p_rand"], "tr", row["OOS_trades"], row["OOS_pass_gate"])

    # ---- (h) IBS equal-weight GER40, JP225, UK100, XAU ----
    print("\n=== (h) IBS breadth pool + descriptive TOM/FX ===")
    names_h = ["GER40", "JP225", "UK100", "XAU"]
    ibs_h = {}
    for nm in names_h + ["AUDCAD"]:
        ibs_h[nm] = run_ibs(series[nm])
        pos, trades, fill, r_fill, times, units = ibs_h[nm]
        row, _ = evaluate_standard(nm, "ibs_h", series[nm], pos, trades, fill, r_fill, times, units, rng, "event")
        row["role"] = f"confirm_h_ibs_{nm}"
        confirm_rows.append(row)
        print("  IBS", nm, "OOS", row["OOS_trades"], row["OOS_pf"], row["OOS_sharpe"], row["OOS_p_rand"])
        pos, trades, fill, r_fill, times, units = run_tom(series[nm])
        row, _ = evaluate_standard(nm, "tom_h", series[nm], pos, trades, fill, r_fill, times, units, rng, "event")
        row["role"] = f"confirm_h_tom_{nm}"
        confirm_rows.append(row)
        print("  TOM", nm, "OOS", row["OOS_trades"], row["OOS_pf"], row["OOS_sharpe"], row["OOS_p_rand"])

    members_h = [series[n] for n in names_h]
    cal_h, locs_h = align_members(members_h, names_h)
    Nh = len(cal_h)
    rnet_h, ok_h, bundle_h, pos_h, sig_h = [], [], [], [], []
    for i, nm in enumerate(names_h):
        s = series[nm]
        loc = locs_h[i]
        pos_m, trades_m, fill, r_fill, times, units = ibs_h[nm]
        pos_c = np.zeros(Nh); r_fill_c = np.zeros(Nh); fill_c = np.full(Nh, np.nan)
        units_c = np.zeros(Nh, dtype=np.int16); sig_c = np.full(Nh, np.nan)
        ok = loc >= 0
        for t, j in enumerate(loc):
            if j < 0:
                continue
            pos_c[t] = pos_m[j]; r_fill_c[t] = r_fill[j]; fill_c[t] = fill[j]
            units_c[t] = units[j]; sig_c[t] = s["sig20"][j]
        r_net = costs_on_pos(pos_c, r_fill_c, cal_h + pd.Timedelta(hours=9, minutes=30), fill_c,
                             s["spread"], s["fin"], s["triple"], units_c)
        r_net = np.where(ok, r_net, 0.0); pos_c = np.where(ok, pos_c, 0.0)
        pos_h.append(pos_c); rnet_h.append(r_net); sig_h.append(sig_c); ok_h.append(ok)
        bundle_h.append(dict(pos=pos_c, r_fill=r_fill_c, fill=fill_c, spread=s["spread"], fin=s["fin"],
                             units=units_c, sig=sig_c, ok=ok, times=cal_h + pd.Timedelta(hours=9, minutes=30),
                             triple=s["triple"]))
    pnl_h = equal_weight_pnl(rnet_h, ok_h)
    # held if any member is long (for trade splits)
    held_h = (np.vstack(pos_h).sum(axis=0) > 0).astype(float)
    tr_h = book_trades_from_pnl(pnl_h, held_h, cal_h)
    row_h = evaluate_pool("GER40+JP225+UK100+XAU", "h_ibs_equal_weight", cal_h, pnl_h, held_h, tr_h, rng,
                          dict(mode="equal_weight", members=bundle_h), "event")
    row_h["role"] = "primary"
    row_h["hypothesis"] = "h"
    rows.append(row_h)
    print("  PRIMARY h", {k: row_h[k] for k in row_h if k.startswith("OOS_")})

    # ---- BH on the 8 primary OOS p-values (NaN → 1, keep N_FDR=8) ----
    prim = sorted(rows, key=lambda r: r["hypothesis"])
    assert [r["hypothesis"] for r in prim] == list("abcdefgh"), [r["hypothesis"] for r in prim]
    pvals = []
    for r in prim:
        p = r.get("OOS_p_rand")
        pvals.append(float(p) if (p is not None and np.isfinite(p)) else 1.0)
        if not (p is not None and np.isfinite(p)):
            r["OOS_p_rand_for_bh"] = 1.0
        else:
            r["OOS_p_rand_for_bh"] = float(p)
    q, n_bh = bh_fdr(pvals, alpha=0.05)
    for r, qi, p in zip(prim, q, pvals):
        r["OOS_q_bh"] = float(qi)
        r["OOS_survive"] = bool(r.get("OOS_pass_gate") and qi <= 0.05)
    print("\n==== PRIMARY FDR ====")
    for r in prim:
        print(r["hypothesis"], r["rule"], "p", r["OOS_p_rand_for_bh"], "q", r["OOS_q_bh"],
              "gate", r["OOS_pass_gate"], "survive", r["OOS_survive"])

    # serialize
    def _clean(x):
        if isinstance(x, dict):
            return {k: _clean(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [_clean(v) for v in x]
        if isinstance(x, (np.bool_, bool)):
            return bool(x)
        if isinstance(x, (np.integer,)):
            return int(x)
        if isinstance(x, (np.floating, float)):
            v = float(x)
            return v if np.isfinite(v) else None
        return x

    payload = {
        "as_of": "2026-11-15",
        "seed": RNG_SEED,
        "n_rand": N_RAND,
        "n_fdr": 8,
        "split": "2016-01-01",
        "primary": _clean(prim),
        "confirmations": _clean(confirm_rows),
        "n_survive": int(sum(1 for r in prim if r["OOS_survive"])),
        "data_windows": {k: {"start": str(v["dates"][0].date()), "end": str(v["dates"][-1].date()), "n": int(v["n"])} for k, v in series.items()},
        "notes": {
            "gold": "GC=F Yahoo daily from 2000-08-30 (1985 cash gold was not available). XM GOLD.i# D1 exists from 2010 but was not swapped in after seeing results.",
            "intl_indices": "GDAXI/N225/FTSE cash daily from 1999-01-04.",
            "dji": "US30 from 1992-01-02; earlier (a)(b) pool uses members with data.",
            "fx": "AUDCAD cash daily from 2003-12-01, descriptive only. No long EURUSD daily was on the box; EURUSD costs were measured but the pair is omitted from breadth tables.",
            "overnight_p": "Hypothesis (e) is long every overnight, so a position-shift test is degenerate. p is from a circular shift of overnight raw returns with the cost calendar held fixed.",
            "costs": "US indices: docs/costs_xm_us_index.json (15/11/2026). GER40/JP225/UK100/XAU/FX: docs/costs_xm_intl.json measured the same day on p4 DEMO, then p4 shut down.",
        },
    }
    (RESULTS / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # text table
    def line(r, extra=""):
        return (
            f"{r.get('hypothesis','-'):1} {r.get('role','')[:18]:18} {r.get('rule','')[:22]:22} {str(r.get('symbol',''))[:22]:22} "
            f"IS  n={fmt(r.get('IS_trades'),0):>5} pf={fmt(r.get('IS_pf')):>6} sh={fmt(r.get('IS_sharpe')):>6} "
            f"cagr={fmt(r.get('IS_cagr')):>7} dd={fmt(r.get('IS_maxdd')):>6} p={fmt(r.get('IS_p_rand'),3):>6}  "
            f"OOS n={fmt(r.get('OOS_trades'),0):>5} pf={fmt(r.get('OOS_pf')):>6} sh={fmt(r.get('OOS_sharpe')):>6} "
            f"cagr={fmt(r.get('OOS_cagr')):>7} dd={fmt(r.get('OOS_maxdd')):>6} p={fmt(r.get('OOS_p_rand'),3):>6} "
            f"q={fmt(r.get('OOS_q_bh'),3):>6} gate={fmt(r.get('OOS_pass_gate'))} surv={fmt(r.get('OOS_survive'))}"
        )

    lines = ["PRIMARY (N_FDR=8, BH α=0.05)", line.__doc__ or ""]
    header = (
        "H role               rule                   symbol                 "
        "IS n/pf/sh/cagr/dd/p                                  "
        "OOS n/pf/sh/cagr/dd/p / q / gate / survive"
    )
    lines = [header, "-" * 180]
    for r in prim:
        lines.append(line(r))
    lines += ["", "CONFIRMATIONS (not in FDR)", "-" * 180]
    for r in confirm_rows:
        lines.append(line(r))
    (RESULTS / "tables.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("\nwrote", RESULTS / "summary.json")


if __name__ == "__main__":
    main()
