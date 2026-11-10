#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dịch ngược luật Kivenara/MCA100 + V1 walk-forward; Friday Pro vs B&H."""
from __future__ import annotations

import json
import math
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

import sys
sys.path.insert(0, "/workspace/quy_trinh_v3")
from phan_tich_mql5_hist import load_trades, load_phi, xm_cost_price, map_symbol

OUT = Path("/workspace/quy_trinh_v3")
DATA = OUT / "data"
DATA.mkdir(exist_ok=True)


# ---------- price loaders ----------
def load_nq_d1() -> pd.DataFrame:
    p = DATA / "nq_f_d1.csv"
    df = pd.read_csv(p, header=[0, 1])
    # yfinance quirky header
    df.columns = [str(c[0]).lower() if isinstance(c, tuple) else str(c).lower() for c in df.columns]
    dcol = [c for c in df.columns if "date" in c][0]
    df[dcol] = pd.to_datetime(df[dcol])
    df = df.rename(columns={dcol: "dt"}).set_index("dt").sort_index()
    for c in ("open", "high", "low", "close"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.dropna(subset=["close"])


def load_nq_h1() -> pd.DataFrame:
    import yfinance as yf
    df = yf.download("NQ=F", period="730d", interval="1h", auto_adjust=True, progress=False)
    df = df.reset_index()
    df.columns = [str(c[0]).lower() if isinstance(c, tuple) else str(c).lower() for c in df.columns]
    dcol = [c for c in df.columns if "date" in c or "time" in c][0]
    df[dcol] = pd.to_datetime(df[dcol], utc=True)
    df = df.rename(columns={dcol: "dt"}).set_index("dt").sort_index()
    for c in ("open", "high", "low", "close"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.dropna(subset=["close"])


def load_xau_h1() -> pd.DataFrame:
    """Ghép XAU H1 2008–2023 + M5→H1 2024–2026 nếu có."""
    frames = []
    p1 = Path("/workspace/du_lieu_fx/hd_dai/xauusd_h1_2008_2023_ny7.csv")
    if p1.exists():
        d = pd.read_csv(p1)
        # expect time,open,high,low,close or similar
        cols = {c.lower(): c for c in d.columns}
        print("xau h1 dai cols", list(d.columns)[:8])
        # normalize
        rename = {}
        for want in ("time", "datetime", "date", "dt"):
            for c in d.columns:
                if c.lower() == want or c.lower().startswith("time"):
                    rename[c] = "dt"
                    break
        for want in ("open", "high", "low", "close"):
            for c in d.columns:
                if c.lower() == want:
                    rename[c] = want
        d = d.rename(columns=rename)
        if "dt" in d.columns:
            d["dt"] = pd.to_datetime(d["dt"])
            d = d.set_index("dt")
            frames.append(d[["open", "high", "low", "close"]].astype(float))
    # recent m5
    p2 = Path("/workspace/du_lieu_fx/hd28/xauusd_m5_histdata_ny7_den202610.csv")
    if p2.exists():
        d = pd.read_csv(p2)
        print("xau m5 cols", list(d.columns)[:8], "n", len(d))
        rename = {}
        for c in d.columns:
            cl = c.lower()
            if cl in ("time", "datetime", "date", "dt") or "time" in cl:
                rename[c] = "dt"
            elif cl in ("open", "high", "low", "close"):
                rename[c] = cl
        d = d.rename(columns=rename)
        if "dt" in d.columns:
            d["dt"] = pd.to_datetime(d["dt"])
            d = d.set_index("dt").sort_index()
            ohlc = d[["open", "high", "low", "close"]].astype(float)
            h1 = ohlc.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
            frames.append(h1)
    if not frames:
        raise FileNotFoundError("no XAU data")
    out = pd.concat(frames).sort_index()
    out = out[~out.index.duplicated(keep="last")]
    return out


# ---------- Kivenara rule search ----------
def test_kivenara_rules():
    tr = sorted(load_trades(Path("/workspace/mql5_hist/2229059.csv")), key=lambda t: t.t_open)
    d1 = load_nq_d1()
    h1 = load_nq_h1()

    # Precompute D1 features
    d1 = d1.copy()
    d1["sma10"] = d1["close"].rolling(10).mean()
    d1["sma20"] = d1["close"].rolling(20).mean()
    d1["sma50"] = d1["close"].rolling(50).mean()
    d1["bull"] = (d1["close"] > d1["open"]).astype(int)
    d1["dir"] = np.sign(d1["close"] - d1["close"].shift(1))

    results = []

    def match_rate(pred_fn, use="d1"):
        ok = tot = 0
        details = []
        for t in tr:
            # skip if no data
            if use == "d1":
                # signal based on prior completed D1 before trade date
                day = pd.Timestamp(t.t_open.date())
                hist = d1.loc[: day - pd.Timedelta(days=1)]
                if len(hist) < 60:
                    continue
                pred = pred_fn(hist)
            else:
                # H1: broker 18:30, try offset hours to UTC
                pred = pred_fn(t, h1)
                if pred is None:
                    continue
            if pred == 0:
                continue
            tot += 1
            if pred == t.chieu:
                ok += 1
            details.append((t.t_open, t.chieu, pred))
        return (ok / tot if tot else 0.0), ok, tot

    # D1 rules
    rules = []
    rules.append(("d1_close_gt_sma20", lambda h: 1 if h.iloc[-1].close > h.iloc[-1].sma20 else -1))
    rules.append(("d1_close_gt_sma10", lambda h: 1 if h.iloc[-1].close > h.iloc[-1].sma10 else -1))
    rules.append(("d1_close_gt_sma50", lambda h: 1 if h.iloc[-1].close > h.iloc[-1].sma50 else -1))
    rules.append(("d1_sma10_gt_sma20", lambda h: 1 if h.iloc[-1].sma10 > h.iloc[-1].sma20 else -1))
    rules.append(("d1_prior_bull", lambda h: 1 if h.iloc[-1].close > h.iloc[-1].open else -1))
    rules.append(("d1_close_gt_prior", lambda h: 1 if h.iloc[-1].close > h.iloc[-2].close else -1))
    rules.append(("d1_close_gt_sma20_and_bull", lambda h: 1 if (h.iloc[-1].close > h.iloc[-1].sma20 and h.iloc[-1].close > h.iloc[-1].open) else (-1 if (h.iloc[-1].close < h.iloc[-1].sma20 and h.iloc[-1].close < h.iloc[-1].open) else 0)))

    for name, fn in rules:
        rate, ok, tot = match_rate(fn, "d1")
        results.append(dict(he="2229059", rule=name, match=round(rate, 4), ok=ok, tot=tot, khung="D1"))
        print(f"KIV {name}: {ok}/{tot} = {rate:.1%}")

    # H1 rules with best offset
    def make_h1_rule(off, mode):
        def fn(t, h1df):
            ts = (pd.Timestamp(t.t_open) - pd.Timedelta(hours=off)).tz_localize("UTC")
            if ts < h1df.index.min() or ts > h1df.index.max():
                return None
            # prior completed hour before entry
            loc = h1df.index.asof(ts - pd.Timedelta(minutes=1))
            if pd.isna(loc):
                return None
            i = h1df.index.get_loc(loc)
            if isinstance(i, slice):
                return None
            if i < 20:
                return None
            row = h1df.iloc[i]
            prev = h1df.iloc[i - 1]
            if mode == "bull_hour":
                return 1 if row.close > row.open else -1
            if mode == "vs_prev":
                return 1 if row.close > prev.close else -1
            if mode == "vs_sma20":
                sma = h1df["close"].iloc[i - 19 : i + 1].mean()
                return 1 if row.close > sma else -1
            if mode == "vs_sma50":
                sma = h1df["close"].iloc[i - 49 : i + 1].mean()
                return 1 if row.close > sma else -1
            return None
        return fn

    best = None
    for off in range(0, 10):
        for mode in ("bull_hour", "vs_prev", "vs_sma20", "vs_sma50"):
            rate, ok, tot = match_rate(make_h1_rule(off, mode), "h1")
            rec = dict(he="2229059", rule=f"h1_off{off}_{mode}", match=round(rate, 4), ok=ok, tot=tot, khung="H1")
            results.append(rec)
            if tot >= 100 and (best is None or rate > best[0]):
                best = (rate, rec)
    if best:
        print("KIV best H1", best[1])

    return results, tr, d1


def test_mca100_rules():
    tr = sorted(load_trades(Path("/workspace/mql5_hist/2153920.csv")), key=lambda t: t.t_open)
    xau = [t for t in tr if t.symbol == "XAUUSD"]
    print("MCA XAU trades", len(xau), "of", len(tr))
    h1 = load_xau_h1()
    print("XAU H1", len(h1), h1.index.min(), h1.index.max())

    # SL/TP structure measured
    sl = [abs(t.sl - t.price_open) for t in xau if t.sl]
    tp = [abs(t.tp - t.price_open) for t in xau if t.tp]
    import statistics as st
    sl_med = st.median(sl) if sl else None
    tp_med = st.median(tp) if tp else None

    # Pending stop offsets from raw file
    raw = Path("/workspace/mql5_hist/2153920.csv").read_text(encoding="utf-8-sig").splitlines()
    # filled buys/sells vs cancelled stops — analyze stop price vs prior H1 high/low at place time
    # For filled market trades, test: direction = break of prior N-bar high/low
    results = []

    def match(pred_fn):
        ok = tot = 0
        for t in xau:
            hist = h1.loc[: pd.Timestamp(t.t_open) - pd.Timedelta(seconds=1)]
            if len(hist) < 50:
                continue
            pred = pred_fn(hist, t)
            if pred is None or pred == 0:
                continue
            tot += 1
            if pred == t.chieu:
                ok += 1
        return (ok / tot if tot else 0.0), ok, tot

    def breakout_n(n):
        def fn(h, t):
            window = h.iloc[-n:]
            if t.chieu > 0:
                # expect break above prior high
                return 1 if t.price_open >= window.high.max() - 1e-9 else 0
            else:
                return -1 if t.price_open <= window.low.min() + 1e-9 else 0
        return fn

    # direction-only rules (predict chieu without using t.chieu in filter)
    def dir_breakout(n):
        def fn(h, t):
            window = h.iloc[-n - 1 : -1] if len(h) > n + 1 else h.iloc[:-1]
            if len(window) < n:
                return None
            # if price near high -> buy, near low -> sell
            hh, ll, mid = window.high.max(), window.low.min(), (window.high.max() + window.low.min()) / 2
            # use last close relative
            c = h.iloc[-1].close
            if c >= hh:
                return 1
            if c <= ll:
                return -1
            return 0
        return fn

    def dir_sma(n):
        def fn(h, t):
            sma = h.close.iloc[-n:].mean()
            c = h.iloc[-1].close
            return 1 if c > sma else -1
        return fn

    def dir_bull_bar():
        def fn(h, t):
            r = h.iloc[-1]
            return 1 if r.close > r.open else -1
        return fn

    for n in (1, 2, 4, 8, 12, 24):
        rate, ok, tot = match(dir_breakout(n))
        results.append(dict(he="2153920", rule=f"xau_h1_breakout_{n}", match=round(rate, 4), ok=ok, tot=tot, khung="H1"))
        print(f"MCA breakout{n}: {ok}/{tot}={rate:.1%}")
    for n in (10, 20, 50):
        rate, ok, tot = match(dir_sma(n))
        results.append(dict(he="2153920", rule=f"xau_h1_sma{n}", match=round(rate, 4), ok=ok, tot=tot, khung="H1"))
        print(f"MCA sma{n}: {ok}/{tot}={rate:.1%}")
    rate, ok, tot = match(dir_bull_bar())
    results.append(dict(he="2153920", rule="xau_h1_bull_bar", match=round(rate, 4), ok=ok, tot=tot, khung="H1"))
    print(f"MCA bull_bar: {ok}/{tot}={rate:.1%}")

    # Always-buy baseline (measured buy%=88)
    buy_pct = sum(1 for t in xau if t.chieu > 0) / len(xau)
    results.append(dict(he="2153920", rule="always_buy_baseline", match=round(buy_pct, 4), ok=sum(1 for t in xau if t.chieu > 0), tot=len(xau), khung="meta"))
    print(f"MCA always_buy baseline={buy_pct:.1%}")

    # Pending stop offset analysis on cancelled+filled stops from raw
    offsets = []
    for line in raw[1:]:
        p = line.split(";")
        if len(p) < 8:
            continue
        typ = p[1]
        if typ not in ("Buy Stop", "Sell Stop"):
            continue
        # need prior bar - skip cancelled price compare loosely
        try:
            px = float(p[4].replace(" ", "").replace(",", ""))
        except Exception:
            continue
        t_place = pd.to_datetime(p[0])
        hist = h1.loc[: t_place - pd.Timedelta(seconds=1)]
        if len(hist) < 5:
            continue
        prev = hist.iloc[-1]
        if typ == "Buy Stop":
            offsets.append(px - float(prev.high))
        else:
            offsets.append(float(prev.low) - px)
    if offsets:
        import statistics as st
        results.append(dict(he="2153920", rule="pending_stop_offset_vs_prevH1", match=None, med_offset=round(st.median(offsets), 4), n=len(offsets), khung="raw"))
        print(f"MCA pending offset med vs prev H1 extreme: {st.median(offsets):.4f} n={len(offsets)}")

    meta = dict(sl_med=sl_med, tp_med=tp_med, buy_pct=round(buy_pct, 4))
    return results, xau, h1, meta


# ---------- V1 walk-forward ----------
def cagr(equity: pd.Series, years: float) -> float:
    if years <= 0 or len(equity) < 2:
        return float("nan")
    v0, v1 = float(equity.iloc[0]), float(equity.iloc[-1])
    if v0 <= 0 or v1 <= 0:
        return float("nan")
    return (v1 / v0) ** (1 / years) - 1


def max_dd(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = (peak - equity) / peak.replace(0, np.nan)
    return float(dd.max()) if len(dd) else float("nan")


def sharpe_daily(rets: pd.Series) -> float:
    if len(rets) < 10 or rets.std() == 0:
        return float("nan")
    return float(rets.mean() / rets.std() * math.sqrt(252))


def simulate_kivenara_d1(d1: pd.DataFrame, rule_name: str, sl_pts=100.0, tp_pts=165.0, hold_cap_days=30, spread=None, swap_long=None, swap_short=None):
    """Enter at next D1 open after signal on prior close; US100 proxy = NQ=F.
    XM costs: use load_phi('US100') if available.
    """
    phi = load_phi("US100")
    d1 = d1.copy()
    d1["sma10"] = d1["close"].rolling(10).mean()
    d1["sma20"] = d1["close"].rolling(20).mean()
    d1["sma50"] = d1["close"].rolling(50).mean()

    def signal(i):
        row = d1.iloc[i]
        if rule_name == "d1_close_gt_sma20":
            if pd.isna(row.sma20):
                return 0
            return 1 if row.close > row.sma20 else -1
        if rule_name == "d1_sma10_gt_sma20":
            if pd.isna(row.sma10) or pd.isna(row.sma20):
                return 0
            return 1 if row.sma10 > row.sma20 else -1
        if rule_name == "d1_close_gt_sma50":
            if pd.isna(row.sma50):
                return 0
            return 1 if row.close > row.sma50 else -1
        if rule_name == "d1_prior_bull":
            return 1 if row.close > row.open else -1
        return 0

    # Walk-forward 12/3 months, optimize rule choice? For single accepted rule, still optimize SL/TP multipliers on train
    # Params on train: sl_mult in {0.5,1,1.5}, tp_mult in {1,1.5,2} relative to base 100/165
    idx = d1.index
    start = idx[60]
    # build month ends
    months = pd.period_range(idx.min(), idx.max(), freq="M")
    trades = []
    oos_equity = []
    equity = 10000.0
    eq_curve = []

    # Rolling WF: train 12m, test 3m
    # Convert to list of quarter starts
    q_starts = pd.date_range(start=max(pd.Timestamp("2009-01-01"), idx.min() + pd.DateOffset(years=1)), end=idx.max(), freq="QS")
    oos_rets = []
    param_hist = []

    def run_period(i0, i1, slm, tpm, record=False):
        nonlocal equity
        local_trades = []
        # i0,i1 integer positions
        for i in range(max(i0, 60), i1 - 1):
            sig = signal(i)
            if sig == 0:
                continue
            entry_i = i + 1
            if entry_i >= i1 or entry_i >= len(d1) - 1:
                break
            entry = float(d1.iloc[entry_i].open)
            sl = entry - sig * sl_pts * slm
            tp = entry + sig * tp_pts * tpm
            # simulate path day by day
            exit_px = None
            exit_i = None
            hold_days = 0
            for j in range(entry_i, min(len(d1), entry_i + hold_cap_days + 1)):
                bar = d1.iloc[j]
                hold_days = (d1.index[j] - d1.index[entry_i]).days
                if sig > 0:
                    if bar.low <= sl:
                        exit_px = sl
                        exit_i = j
                        break
                    if bar.high >= tp:
                        exit_px = tp
                        exit_i = j
                        break
                else:
                    if bar.high >= sl:
                        exit_px = sl
                        exit_i = j
                        break
                    if bar.low <= tp:
                        exit_px = tp
                        exit_i = j
                        break
                if hold_days >= hold_cap_days:
                    exit_px = float(bar.close)
                    exit_i = j
                    break
            if exit_px is None:
                continue
            gross = sig * (exit_px - entry)
            # XM cost in price
            if phi:
                sp, sw, _ = xm_cost_price(phi, max(hold_days, 0), sig, gia_tham=entry)
            else:
                sp, sw = 0.0, 0.0
            net = gross - sp + sw
            # USD: contract*lot — use 1 micro-equivalent: for US100 contract=10 from chi_phi, vol=0.01 → scale
            # Use fixed risk: 1% equity / SL distance
            risk_price = abs(entry - sl)
            if risk_price <= 0:
                continue
            risk_budget = 0.01 * equity
            # usd per point for vol=1 with contract: approx net_price * contract
            contract = phi.contract if phi else 1.0
            usd_per_point_per_vol = contract
            vol = risk_budget / (risk_price * usd_per_point_per_vol)
            pnl = net * usd_per_point_per_vol * vol
            equity = max(equity + pnl, 0.0)
            local_trades.append(dict(entry=d1.index[entry_i], exit=d1.index[exit_i], sig=sig, net_price=net, pnl=pnl, equity=equity, hold=hold_days))
            if record:
                eq_curve.append((d1.index[exit_i], equity))
            # skip overlapping: jump i to exit
            # caller uses sequential without overlap by setting i — handle by storing last exit
        return local_trades

    # non-overlap engine for WF
    def best_params(train_start, train_end):
        i0 = d1.index.searchsorted(train_start)
        i1 = d1.index.searchsorted(train_end)
        best = None
        for slm in (0.75, 1.0, 1.25):
            for tpm in (0.75, 1.0, 1.25, 1.5):
                eq0 = 10000.0
                # isolated sim
                e = eq0
                pnls = []
                last_exit_i = i0
                for i in range(max(i0, 60), i1 - 1):
                    if i < last_exit_i:
                        continue
                    sig = signal(i)
                    if sig == 0:
                        continue
                    entry_i = i + 1
                    if entry_i >= i1:
                        break
                    entry = float(d1.iloc[entry_i].open)
                    sl = entry - sig * sl_pts * slm
                    tp = entry + sig * tp_pts * tpm
                    exit_px = None
                    exit_i = None
                    hold_days = 0
                    for j in range(entry_i, min(i1, entry_i + hold_cap_days + 1)):
                        bar = d1.iloc[j]
                        hold_days = (d1.index[j] - d1.index[entry_i]).days
                        hit = False
                        if sig > 0:
                            if bar.low <= sl:
                                exit_px, exit_i, hit = sl, j, True
                            elif bar.high >= tp:
                                exit_px, exit_i, hit = tp, j, True
                        else:
                            if bar.high >= sl:
                                exit_px, exit_i, hit = sl, j, True
                            elif bar.low <= tp:
                                exit_px, exit_i, hit = tp, j, True
                        if hit:
                            break
                        if hold_days >= hold_cap_days:
                            exit_px, exit_i = float(bar.close), j
                            break
                    if exit_px is None:
                        continue
                    gross = sig * (exit_px - entry)
                    if phi:
                        sp, sw, _ = xm_cost_price(phi, max(hold_days, 0), sig, gia_tham=entry)
                    else:
                        sp = sw = 0.0
                    net = gross - sp + sw
                    risk_price = abs(entry - sl)
                    contract = phi.contract if phi else 1.0
                    vol = (0.01 * e) / (risk_price * contract) if risk_price > 0 else 0
                    pnl = net * contract * vol
                    e = max(e + pnl, 0)
                    pnls.append(pnl)
                    last_exit_i = exit_i + 1 if exit_i is not None else last_exit_i
                if not pnls:
                    score = -1e9
                else:
                    years = max((train_end - train_start).days / 365.25, 1e-9)
                    c = (e / eq0) ** (1 / years) - 1 if e > 0 else -1
                    # rough DD
                    # use final cagr as score with floor
                    score = c
                if best is None or score > best[0]:
                    best = (score, slm, tpm, e)
        return best

    # Full OOS stitch
    equity = 10000.0
    eq_series = []
    all_oos_trades = []
    last_exit_time = d1.index[0]
    for qs in q_starts:
        train_start = qs - pd.DateOffset(months=12)
        train_end = qs
        test_end = qs + pd.DateOffset(months=3)
        if train_start < d1.index.min() or qs > d1.index.max():
            continue
        bp = best_params(train_start, min(train_end, d1.index.max()))
        if bp is None:
            continue
        _, slm, tpm, _ = bp
        param_hist.append(dict(qs=str(qs.date()), slm=slm, tpm=tpm, train_score=bp[0]))
        # run test
        i0 = d1.index.searchsorted(qs)
        i1 = d1.index.searchsorted(min(test_end, d1.index.max()))
        last_exit_i = i0
        for i in range(max(i0, 60), i1 - 1):
            if i < last_exit_i:
                continue
            if d1.index[i] < last_exit_time:
                continue
            sig = signal(i)
            if sig == 0:
                continue
            entry_i = i + 1
            if entry_i >= i1:
                break
            entry = float(d1.iloc[entry_i].open)
            sl = entry - sig * sl_pts * slm
            tp = entry + sig * tp_pts * tpm
            exit_px = exit_i = None
            hold_days = 0
            for j in range(entry_i, min(len(d1), entry_i + hold_cap_days + 1)):
                bar = d1.iloc[j]
                hold_days = (d1.index[j] - d1.index[entry_i]).days
                if sig > 0:
                    if bar.low <= sl:
                        exit_px, exit_i = sl, j
                        break
                    if bar.high >= tp:
                        exit_px, exit_i = tp, j
                        break
                else:
                    if bar.high >= sl:
                        exit_px, exit_i = sl, j
                        break
                    if bar.low <= tp:
                        exit_px, exit_i = tp, j
                        break
                if hold_days >= hold_cap_days:
                    exit_px, exit_i = float(bar.close), j
                    break
            if exit_px is None:
                continue
            gross = sig * (exit_px - entry)
            if phi:
                sp, sw, _ = xm_cost_price(phi, max(hold_days, 0), sig, gia_tham=entry)
            else:
                sp = sw = 0.0
            net = gross - sp + sw
            risk_price = abs(entry - sl)
            contract = phi.contract if phi else 1.0
            vol = (0.01 * equity) / (risk_price * contract) if risk_price > 0 else 0
            pnl = net * contract * vol
            equity = max(equity + pnl, 0)
            all_oos_trades.append(dict(entry=str(d1.index[entry_i].date()), exit=str(d1.index[exit_i].date()), sig=sig, pnl=pnl, net_price=net, hold=hold_days, slm=slm, tpm=tpm))
            eq_series.append((d1.index[exit_i], equity))
            last_exit_i = exit_i + 1
            last_exit_time = d1.index[exit_i]

    if not eq_series:
        return dict(error="no OOS trades", rule=rule_name)

    eq = pd.Series({t: e for t, e in eq_series}).sort_index()
    # daily rets from equity steps
    rets = eq.pct_change().dropna()
    years = (eq.index[-1] - eq.index[0]).days / 365.25
    cagr_v = cagr(eq, years)
    dd = max_dd(eq)
    # bootstrap 500 on trade pnls
    pnls = np.array([t["pnl"] for t in all_oos_trades])
    boot_cagr = []
    rng = np.random.default_rng(42)
    for _ in range(500):
        sample = rng.choice(pnls, size=len(pnls), replace=True)
        # reconstruct rough final
        e = 10000.0
        for p in sample:
            e = max(e + p, 0)
        if e > 0 and years > 0:
            boot_cagr.append((e / 10000.0) ** (1 / years) - 1)
    # random-entry comparison: shuffle signals
    rand_pnls = []
    rng2 = np.random.default_rng(7)
    # 200 random entry sims: same number of trades, random direction & random days
    n_tr = len(all_oos_trades)
    rand_final = []
    for _ in range(200):
        e = 10000.0
        # sample random indices
        idxs = rng2.choice(range(60, len(d1) - 2), size=min(n_tr, 200), replace=False)
        for i in sorted(idxs):
            sig = rng2.choice([-1, 1])
            entry = float(d1.iloc[i].open)
            sl = entry - sig * sl_pts
            tp = entry + sig * tp_pts
            exit_px = None
            hold_days = 0
            for j in range(i, min(len(d1), i + hold_cap_days + 1)):
                bar = d1.iloc[j]
                hold_days = (d1.index[j] - d1.index[i]).days
                if sig > 0:
                    if bar.low <= sl:
                        exit_px = sl
                        break
                    if bar.high >= tp:
                        exit_px = tp
                        break
                else:
                    if bar.high >= sl:
                        exit_px = sl
                        break
                    if bar.low <= tp:
                        exit_px = tp
                        break
                if hold_days >= hold_cap_days:
                    exit_px = float(bar.close)
                    break
            if exit_px is None:
                continue
            gross = sig * (exit_px - entry)
            if phi:
                sp, sw, _ = xm_cost_price(phi, max(hold_days, 0), sig, gia_tham=entry)
            else:
                sp = sw = 0.0
            net = gross - sp + sw
            risk_price = abs(entry - sl)
            contract = phi.contract if phi else 1.0
            vol = (0.01 * e) / (risk_price * contract) if risk_price > 0 else 0
            e = max(e + net * contract * vol, 0)
        if years > 0 and e > 0:
            rand_final.append((e / 10000.0) ** (1 / years) - 1)

    trades_per_yr = len(all_oos_trades) / years if years else float("nan")
    verdict = "PASS" if (dd < 0.80 and cagr_v > 0.10) else "REJECT"
    return dict(
        rule=rule_name,
        n_oos_trades=len(all_oos_trades),
        years=round(years, 3),
        trades_per_yr=round(trades_per_yr, 2),
        cagr=round(cagr_v * 100, 3) if cagr_v == cagr_v else None,
        dd=round(dd * 100, 3) if dd == dd else None,
        sharpe=round(sharpe_daily(rets), 3) if len(rets) else None,
        final_equity=round(equity, 2),
        boot_cagr_p50=round(float(np.median(boot_cagr)) * 100, 3) if boot_cagr else None,
        boot_cagr_p05=round(float(np.percentile(boot_cagr, 5)) * 100, 3) if boot_cagr else None,
        random_entry_cagr_p50=round(float(np.median(rand_final)) * 100, 3) if rand_final else None,
        random_entry_cagr_p95=round(float(np.percentile(rand_final, 95)) * 100, 3) if rand_final else None,
        beat_random=(cagr_v > float(np.median(rand_final))) if rand_final and cagr_v == cagr_v else None,
        verdict=verdict,
        phi_nguon=(phi.nguon if phi else None),
        params_note="WF 12/3; SL/TP mult tối ưu trên train; risk 1%/lệnh; hold_cap=30d; NQ=F D1 proxy US100",
        n_wf_windows=len(param_hist),
    )


def friday_pro_vs_bh():
    tr = sorted(load_trades(Path("/workspace/mql5_hist/2344620.csv")), key=lambda t: t.t_open)
    # by symbol
    out = {}
    for sym in ("GBPJPY", "USDJPY"):
        ts = [t for t in tr if t.symbol == sym]
        if len(ts) < 10:
            continue
        t0, t1 = ts[0].t_open, ts[-1].t_close
        # B&H from first open to last close price of trades (ĐO từ chính CSV)
        # long B&H
        px0 = ts[0].price_open
        px1 = ts[-1].price_close
        years = (t1 - t0).total_seconds() / (365.25 * 86400)
        ret = px1 / px0 - 1
        cagr_px = (1 + ret) ** (1 / years) - 1 if years > 0 and ret > -1 else float("nan")
        # buy% and system net profit sum (broker)
        buy_pct = 100 * sum(1 for t in ts if t.chieu > 0) / len(ts)
        sys_profit = sum(t.profit + t.swap + t.commission for t in ts)
        # swap estimate continuous long 1.0 lot of fee table
        phi = load_phi(sym)
        swap_drag = None
        if phi and years:
            # nights
            dem = years * 365 * 7 / 5
            # price units then rough
            sw = phi.swap_mua * phi.point * dem  # POINTS mode price
            # convert to % of price mid
            mid = (px0 + px1) / 2
            swap_drag = sw / mid if mid else None
        out[sym] = dict(
            n=len(ts),
            years=round(years, 3),
            buy_pct=round(buy_pct, 2),
            bh_ret_pct=round(ret * 100, 3),
            bh_cagr_pct=round(cagr_px * 100, 3) if cagr_px == cagr_px else None,
            sys_profit_broker=round(sys_profit, 2),
            swap_long_price_drag=round(swap_drag, 6) if swap_drag is not None else None,
            px0=px0,
            px1=px1,
            note="B&H dùng giá vào lệnh đầu / giá đóng lệnh cuối trong CSV (ĐO); không phải series OHLC độc lập",
        )
    # overall buy
    buy_pct = 100 * sum(1 for t in tr if t.chieu > 0) / len(tr)
    out["ALL"] = dict(n=len(tr), buy_pct=round(buy_pct, 2), hang="pyramid", max_cung=5)
    return out


def main():
    print("=== KIVENARA rules ===")
    kiv_rules, kiv_tr, d1 = test_kivenara_rules()
    print("=== MCA100 rules ===")
    mca_rules, mca_tr, xau_h1, mca_meta = test_mca100_rules()
    print("=== Friday B&H ===")
    fri = friday_pro_vs_bh()
    print(json.dumps(fri, ensure_ascii=False, indent=2))

    # pick best kiv rule with tot>=200 and match>=0.6
    kiv_ok = [r for r in kiv_rules if (r.get("tot") or 0) >= 150 and (r.get("match") or 0) >= 0.60]
    kiv_ok.sort(key=lambda x: -x["match"])
    print("KIV accepted", kiv_ok[:5])

    mca_ok = [r for r in mca_rules if r.get("match") is not None and (r.get("tot") or 0) >= 100 and r["match"] >= 0.60]
    mca_ok.sort(key=lambda x: -x["match"])
    print("MCA accepted", mca_ok[:5])

    v1 = {}
    if kiv_ok:
        rule = kiv_ok[0]["rule"]
        # map H1 rules to nearest D1 for long WF
        d1_rule = rule if rule.startswith("d1_") else "d1_close_gt_sma20"
        if not rule.startswith("d1_"):
            # choose best d1 among accepted or top d1
            d1_cands = [r for r in kiv_rules if r["rule"].startswith("d1_") and (r.get("tot") or 0) >= 150]
            d1_cands.sort(key=lambda x: -x["match"])
            d1_rule = d1_cands[0]["rule"] if d1_cands else "d1_close_gt_sma20"
            v1["kivenara_note"] = f"H1 best={rule} match={kiv_ok[0]['match']}; V1 dài hạn chạy D1 proxy best={d1_rule} match={d1_cands[0]['match'] if d1_cands else 'n/a'}"
        print("=== V1 Kivenara", d1_rule, "===")
        v1["kivenara"] = simulate_kivenara_d1(d1, d1_rule)
        print(json.dumps(v1["kivenara"], ensure_ascii=False, indent=2))
    else:
        v1["kivenara"] = dict(verdict="KHONG_CO_LUAT", ly_do="không rule nào match>=60% với tot đủ lớn")

    if mca_ok and mca_ok[0]["rule"] != "always_buy_baseline":
        v1["mca100"] = dict(verdict="CHUA_CHAY_V1", ly_do="có rule đạt ngưỡng nhưng cần EA pending-stop; V1 đầy đủ để vòng sau", best=mca_ok[0])
    else:
        # always_buy may pass 60% but is not an entry rule
        real = [r for r in mca_ok if r["rule"] != "always_buy_baseline"]
        if not real:
            v1["mca100"] = dict(verdict="KHONG_CO_LUAT", ly_do="không rule hướng đạt >=60% ngoài baseline always_buy", best_baseline=mca_ok[0] if mca_ok else None, top=mca_rules[:8], meta=mca_meta)
        else:
            v1["mca100"] = dict(verdict="CHUA_CHAY_V1", best=real[0])

    out = dict(
        kiv_rules=kiv_rules,
        mca_rules=mca_rules,
        mca_meta=mca_meta,
        friday_bh=fri,
        v1=v1,
        kiv_accepted=kiv_ok[:5],
        mca_accepted=mca_ok[:5],
    )
    (OUT / "v1_dich_nguoc_ket_qua.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("wrote v1_dich_nguoc_ket_qua.json")


if __name__ == "__main__":
    main()
