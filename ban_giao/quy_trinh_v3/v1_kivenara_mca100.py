#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dich nguoc + V1: Kivenara 2229059, MCA100 2153920, Friday Pro 2344620 vs B&H."""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

import sys
sys.path.insert(0, "/workspace/quy_trinh_v3")
from phan_tich_mql5_hist import load_trades, load_phi, xm_cost_price

OUT = Path("/workspace/quy_trinh_v3")
DATA = OUT / "data"


def load_nq_d1() -> pd.DataFrame:
    df = pd.read_csv(DATA / "nq_f_d1.csv", skiprows=3, names=["dt", "close", "high", "low", "open", "volume"])
    df["dt"] = pd.to_datetime(df["dt"])
    return df.set_index("dt").sort_index().dropna(subset=["close"])


def load_nq_h1() -> pd.DataFrame:
    df = pd.read_csv(DATA / "nq_f_h1.csv", skiprows=3, names=["dt", "close", "high", "low", "open", "volume"])
    df["dt"] = pd.to_datetime(df["dt"], utc=True)
    return df.set_index("dt").sort_index().dropna(subset=["close"])


def load_xau_h1() -> pd.DataFrame:
    h1 = pd.read_csv("/workspace/du_lieu_fx/hd_dai/xauusd_h1_2008_2023_ny7.csv")
    h1["dt"] = pd.to_datetime(h1["time"])
    h1 = h1.set_index("dt")[["open", "high", "low", "close"]].astype(float)
    m5 = pd.read_csv("/workspace/du_lieu_fx/hd28/xauusd_m5_histdata_ny7_den202610.csv")
    m5["dt"] = pd.to_datetime(m5["time"])
    m5 = m5.set_index("dt")[["open", "high", "low", "close"]].astype(float)
    h1b = m5.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    out = pd.concat([h1, h1b]).sort_index()
    return out[~out.index.duplicated(keep="last")]


def cagr(eq: pd.Series, years: float) -> float:
    if years <= 0 or len(eq) < 2:
        return float("nan")
    v0, v1 = float(eq.iloc[0]), float(eq.iloc[-1])
    if v0 <= 0 or v1 <= 0:
        return float("nan")
    return (v1 / v0) ** (1 / years) - 1


def max_dd(eq: pd.Series) -> float:
    peak = eq.cummax()
    dd = (peak - eq) / peak.replace(0, np.nan)
    return float(dd.max()) if len(dd) else float("nan")


def sharpe_from_trade_pnls(pnls, years):
    if len(pnls) < 10 or years <= 0:
        return float("nan")
    # approximate: treat each trade as independent, annualize by trades/yr
    arr = np.array(pnls, dtype=float)
    if arr.std() == 0:
        return float("nan")
    tpy = len(arr) / years
    return float(arr.mean() / arr.std() * math.sqrt(tpy))


# ===================== KIVENARA =====================
def kivenara_match():
    tr = sorted(load_trades(Path("/workspace/mql5_hist/2229059.csv")), key=lambda t: t.t_open)
    d1 = load_nq_d1()
    h1 = load_nq_h1()
    d1 = d1.copy()
    d1["sma10"] = d1.close.rolling(10).mean()
    d1["sma20"] = d1.close.rolling(20).mean()
    d1["sma50"] = d1.close.rolling(50).mean()

    rows = []

    def add(rule, khung, ok, tot, extra=None):
        m = (ok / tot) if tot else 0.0
        rec = dict(he="2229059", rule=rule, khung=khung, match=round(m, 4), ok=ok, tot=tot, accept=m >= 0.60 and tot >= 100)
        if extra:
            rec.update(extra)
        rows.append(rec)
        print(f"KIV {rule}: {ok}/{tot}={m:.1%} accept={rec['accept']}")
        return rec

    # D1 rules (prior completed day)
    for name, fn in [
        ("d1_prior_bull", lambda h: 1 if h.iloc[-1].close > h.iloc[-1].open else -1),
        ("d1_close_gt_prior", lambda h: 1 if h.iloc[-1].close > h.iloc[-2].close else -1),
        ("d1_close_gt_sma10", lambda h: 1 if h.iloc[-1].close > h.iloc[-1].sma10 else -1),
        ("d1_close_gt_sma20", lambda h: 1 if h.iloc[-1].close > h.iloc[-1].sma20 else -1),
        ("d1_close_gt_sma50", lambda h: 1 if h.iloc[-1].close > h.iloc[-1].sma50 else -1),
        ("d1_sma10_gt_sma20", lambda h: 1 if h.iloc[-1].sma10 > h.iloc[-1].sma20 else -1),
    ]:
        ok = tot = 0
        for t in tr:
            day = pd.Timestamp(t.t_open.date())
            hist = d1.loc[: day - pd.Timedelta(days=1)]
            if len(hist) < 60:
                continue
            pred = fn(hist)
            if pred == 0:
                continue
            tot += 1
            if pred == t.chieu:
                ok += 1
        add(name, "D1", ok, tot)

    # H1: broker GMT+3 (off=3) best from scan; entry 18:30 broker = 15:30 UTC
    best_h1 = None
    for off in range(0, 8):
        for mode, win in [("sma50", 50), ("sma20", 20), ("bull", 0), ("vs_prev", 0)]:
            ok = tot = 0
            for t in tr:
                ts = (pd.Timestamp(t.t_open) - pd.Timedelta(hours=off)).tz_localize("UTC")
                if ts < h1.index.min() or ts > h1.index.max():
                    continue
                loc = h1.index.asof(ts - pd.Timedelta(minutes=1))
                if pd.isna(loc):
                    continue
                i = h1.index.get_loc(loc)
                if isinstance(i, slice) or i < 60:
                    continue
                row = h1.iloc[i]
                if mode == "bull":
                    pred = 1 if row.close > row.open else -1
                elif mode == "vs_prev":
                    pred = 1 if row.close > h1.iloc[i - 1].close else -1
                else:
                    sma = h1.close.iloc[i - win + 1 : i + 1].mean()
                    pred = 1 if row.close > sma else -1
                tot += 1
                if pred == t.chieu:
                    ok += 1
            if tot < 100:
                continue
            rec = add(f"h1_off{off}_{mode}", "H1", ok, tot, extra={"broker_utc_off_h": off})
            if best_h1 is None or rec["match"] > best_h1["match"]:
                best_h1 = rec

    meta = dict(
        n=len(tr),
        buy_pct=round(100 * sum(t.chieu > 0 for t in tr) / len(tr), 2),
        entry="18:30 luôn (664/664)",
        sl_med=100.0,
        tp_med=165.0,
        hold_med_h=round(float(np.median([(t.t_close - t.t_open).total_seconds() / 3600 for t in tr])), 3),
        exit_comment=dict(Counter((t.comment or "") for t in tr)),
        range=[str(tr[0].t_open), str(tr[-1].t_open)],
        best_h1=best_h1,
    )
    return rows, meta, tr, d1, h1


def simulate_path_h1(h1, entry_i, sig, sl_pts, tp_pts, hold_cap_bars, trail=False):
    entry = float(h1.iloc[entry_i].open)
    sl = entry - sig * sl_pts
    tp = entry + sig * tp_pts
    best = entry
    for j in range(entry_i, min(len(h1), entry_i + hold_cap_bars + 1)):
        bar = h1.iloc[j]
        if trail:
            if sig > 0:
                best = max(best, float(bar.high))
                # trail SL to lock if +0.5*sl moved
                if best - entry >= sl_pts * 0.5:
                    sl = max(sl, best - sl_pts)
            else:
                best = min(best, float(bar.low))
                if entry - best >= sl_pts * 0.5:
                    sl = min(sl, best + sl_pts)
        if sig > 0:
            if bar.low <= sl:
                return sl, j, "sl"
            if bar.high >= tp:
                return tp, j, "tp"
        else:
            if bar.high >= sl:
                return sl, j, "sl"
            if bar.low <= tp:
                return tp, j, "tp"
    j = min(len(h1) - 1, entry_i + hold_cap_bars)
    return float(h1.iloc[j].close), j, "time"


def v1_kivenara_h1(h1: pd.DataFrame, off_h=3, sma_win=50, sl_pts=100.0, tp_pts=165.0):
    """V1 trên H1 NQ (proxy US100): vào giờ 15:30 UTC (18:30 GMT+3), hướng = close_prev > SMA50.
    WF 12/3 tháng; tối ưu sl_mult/tp_mult/trail trên train; hold_cap 30 ngày (~720 H1 bars).
    """
    phi = load_phi("US100")
    hold_cap_bars = 30 * 24  # 30d of H1
    # candidate entry hours UTC: 15:30 → bar starting 15:00
    entry_hour = 15  # open of 15:00 bar ≈ 18:00-19:00 broker

    # Precompute signal on each bar (using prior close vs sma — signal at bar close for next open)
    close = h1["close"].values
    opens = h1["open"].values
    highs = h1["high"].values
    lows = h1["low"].values
    times = h1.index

    sma = pd.Series(close, index=h1.index).rolling(sma_win).mean().values

    def signal_at(i):
        if i < sma_win or np.isnan(sma[i]):
            return 0
        return 1 if close[i] > sma[i] else -1

    # indices of entry candidates: bars whose hour==entry_hour
    cand = [i for i in range(sma_win, len(h1) - 2) if times[i].hour == entry_hour]

    q_starts = pd.date_range(
        start=max(pd.Timestamp("2024-07-01", tz="UTC"), times[sma_win] + pd.DateOffset(months=3)),
        end=times[-1],
        freq="QS",
    )

    def train_score(i0, i1, slm, tpm, trail):
        e = 10000.0
        last = i0
        pnls = []
        for i in cand:
            if i < i0 or i >= i1 or i < last:
                continue
            # signal from prior bar (i-1 close)
            sig = signal_at(i - 1)
            if sig == 0:
                continue
            entry = float(opens[i])
            sl0 = entry - sig * sl_pts * slm
            tp0 = entry + sig * tp_pts * tpm
            exit_px, exit_i, _ = _sim(i, sig, sl0, tp0, trail, sl_pts * slm)
            if exit_i is None:
                continue
            hold_days = (times[exit_i] - times[i]).total_seconds() / 86400
            gross = sig * (exit_px - entry)
            if phi:
                sp, sw, _ = xm_cost_price(phi, max(hold_days, 0), sig, gia_tham=entry)
            else:
                sp = sw = 0.0
            net = gross - sp + sw
            risk = abs(entry - (entry - sig * sl_pts * slm))
            contract = phi.contract if phi else 10.0
            vol = (0.01 * e) / (risk * contract) if risk > 0 else 0
            pnl = net * contract * vol
            e = max(e + pnl, 0)
            pnls.append(pnl)
            last = exit_i + 1
        if not pnls:
            return -1e9
        years = max((times[min(i1, len(times) - 1)] - times[i0]).total_seconds() / (365.25 * 86400), 1e-9)
        return (e / 10000.0) ** (1 / years) - 1 if e > 0 else -1

    def _sim(entry_i, sig, sl, tp, trail, trail_dist):
        entry = float(opens[entry_i])
        best = entry
        sl_cur = sl
        for j in range(entry_i, min(len(h1), entry_i + hold_cap_bars + 1)):
            if trail:
                if sig > 0:
                    best = max(best, float(highs[j]))
                    if best - entry >= trail_dist * 0.5:
                        sl_cur = max(sl_cur, best - trail_dist)
                else:
                    best = min(best, float(lows[j]))
                    if entry - best >= trail_dist * 0.5:
                        sl_cur = min(sl_cur, best + trail_dist)
            if sig > 0:
                if lows[j] <= sl_cur:
                    return float(sl_cur), j, "sl"
                if highs[j] >= tp:
                    return float(tp), j, "tp"
            else:
                if highs[j] >= sl_cur:
                    return float(sl_cur), j, "sl"
                if lows[j] <= tp:
                    return float(tp), j, "tp"
        j = min(len(h1) - 1, entry_i + hold_cap_bars)
        return float(close[j]), j, "time"

    # OOS stitch
    equity = 10000.0
    oos_trades = []
    eq_pts = []
    param_hist = []
    last_exit_i = 0

    for qs in q_starts:
        train_start = qs - pd.DateOffset(months=12)
        train_end = qs
        test_end = qs + pd.DateOffset(months=3)
        i0 = int(h1.index.searchsorted(train_start))
        i1 = int(h1.index.searchsorted(train_end))
        j0 = int(h1.index.searchsorted(qs))
        j1 = int(h1.index.searchsorted(min(test_end, times[-1])))
        if i1 - i0 < 100 or j1 - j0 < 10:
            continue
        best = None
        for slm in (0.75, 1.0, 1.25):
            for tpm in (0.75, 1.0, 1.25, 1.5):
                for trail in (False, True):
                    sc = train_score(i0, i1, slm, tpm, trail)
                    if best is None or sc > best[0]:
                        best = (sc, slm, tpm, trail)
        _, slm, tpm, trail = best
        param_hist.append(dict(qs=str(qs.date()), slm=slm, tpm=tpm, trail=trail, train_cagr=round(best[0], 4)))

        for i in cand:
            if i < j0 or i >= j1 or i < last_exit_i:
                continue
            sig = signal_at(i - 1)
            if sig == 0:
                continue
            entry = float(opens[i])
            sl0 = entry - sig * sl_pts * slm
            tp0 = entry + sig * tp_pts * tpm
            exit_px, exit_i, why = _sim(i, sig, sl0, tp0, trail, sl_pts * slm)
            hold_days = (times[exit_i] - times[i]).total_seconds() / 86400
            gross = sig * (exit_px - entry)
            if phi:
                sp, sw, _ = xm_cost_price(phi, max(hold_days, 0), sig, gia_tham=entry)
            else:
                sp = sw = 0.0
            net = gross - sp + sw
            risk = abs(entry - (entry - sig * sl_pts * slm))
            contract = phi.contract if phi else 10.0
            vol = (0.01 * equity) / (risk * contract) if risk > 0 else 0
            pnl = net * contract * vol
            equity = max(equity + pnl, 0)
            oos_trades.append(dict(
                entry=str(times[i]), exit=str(times[exit_i]), sig=sig, pnl=round(pnl, 2),
                net_price=round(net, 4), hold_d=round(hold_days, 3), why=why, slm=slm, tpm=tpm, trail=trail,
            ))
            eq_pts.append((times[exit_i], equity))
            last_exit_i = exit_i + 1

    if not oos_trades:
        return dict(verdict="KHONG_OOS", rule="h1_sma50_off3", n=0)

    eq = pd.Series({t: e for t, e in eq_pts}).sort_index()
    # prepend start
    eq = pd.concat([pd.Series({eq.index[0] - pd.Timedelta(days=1): 10000.0}), eq])
    years = (eq.index[-1] - eq.index[0]).total_seconds() / (365.25 * 86400)
    cagr_v = cagr(eq, years)
    dd = max_dd(eq)
    pnls = np.array([t["pnl"] for t in oos_trades], dtype=float)
    sh = sharpe_from_trade_pnls(pnls, years)

    # bootstrap 500
    rng = np.random.default_rng(42)
    boot = []
    for _ in range(500):
        sample = rng.choice(pnls, size=len(pnls), replace=True)
        e = 10000.0
        for p in sample:
            e = max(e + p, 0)
        if e > 0 and years > 0:
            boot.append((e / 10000.0) ** (1 / years) - 1)

    # random-entry: same schedule hours, random direction
    rand_cagrs = []
    rng2 = np.random.default_rng(7)
    n_tr = len(oos_trades)
    for _ in range(200):
        e = 10000.0
        last = 0
        picked = 0
        order = list(cand)
        rng2.shuffle(order)
        for i in sorted(order):
            if i < last or picked >= n_tr:
                continue
            if times[i] < eq.index[0] or times[i] > eq.index[-1]:
                continue
            sig = int(rng2.choice([-1, 1]))
            entry = float(opens[i])
            sl0 = entry - sig * sl_pts
            tp0 = entry + sig * tp_pts
            exit_px, exit_i, _ = _sim(i, sig, sl0, tp0, False, sl_pts)
            hold_days = (times[exit_i] - times[i]).total_seconds() / 86400
            gross = sig * (exit_px - entry)
            if phi:
                sp, sw, _ = xm_cost_price(phi, max(hold_days, 0), sig, gia_tham=entry)
            else:
                sp = sw = 0.0
            net = gross - sp + sw
            risk = sl_pts
            contract = phi.contract if phi else 10.0
            vol = (0.01 * e) / (risk * contract) if risk > 0 else 0
            e = max(e + net * contract * vol, 0)
            last = exit_i + 1
            picked += 1
        if e > 0 and years > 0:
            rand_cagrs.append((e / 10000.0) ** (1 / years) - 1)

    verdict = "PASS" if (dd == dd and dd < 0.80 and cagr_v == cagr_v and cagr_v > 0.10) else "REJECT"
    return dict(
        rule="h1_close_gt_sma50 @18:30 broker(GMT+3)",
        match_rule="h1_off3_sma50",
        n_oos_trades=len(oos_trades),
        years=round(years, 3),
        trades_per_yr=round(len(oos_trades) / years, 2) if years else None,
        cagr_pct=round(cagr_v * 100, 3) if cagr_v == cagr_v else None,
        dd_pct=round(dd * 100, 3) if dd == dd else None,
        sharpe=round(sh, 3) if sh == sh else None,
        final_equity=round(equity, 2),
        boot_cagr_p50_pct=round(float(np.median(boot)) * 100, 3) if boot else None,
        boot_cagr_p05_pct=round(float(np.percentile(boot, 5)) * 100, 3) if boot else None,
        random_entry_cagr_p50_pct=round(float(np.median(rand_cagrs)) * 100, 3) if rand_cagrs else None,
        random_entry_cagr_p95_pct=round(float(np.percentile(rand_cagrs, 95)) * 100, 3) if rand_cagrs else None,
        beat_random=(cagr_v > float(np.median(rand_cagrs))) if rand_cagrs and cagr_v == cagr_v else None,
        verdict=verdict,
        phi_nguon=phi.nguon if phi else None,
        n_wf_windows=len(param_hist),
        param_hist=param_hist[:8],
        hold_cap_days=30,
        note="NQ=F H1 proxy US100; WF12/3; risk1%; XM cost từ chi_phi_do+spread_bar",
    )


def v1_kivenara_d1(d1: pd.DataFrame, rule="d1_prior_bull"):
    """V1 dài hạn D1 2008–2026 với luật D1 đã chấp nhận; vào open ngày sau tín hiệu."""
    phi = load_phi("US100")
    d1 = d1.copy()
    d1["sma20"] = d1.close.rolling(20).mean()
    hold_cap = 30
    sl_pts, tp_pts = 100.0, 165.0

    def signal(i):
        row = d1.iloc[i]
        if rule == "d1_prior_bull":
            return 1 if row.close > row.open else -1
        if rule == "d1_close_gt_prior":
            if i < 1:
                return 0
            return 1 if row.close > d1.iloc[i - 1].close else -1
        if rule == "d1_close_gt_sma20":
            if pd.isna(row.sma20):
                return 0
            return 1 if row.close > row.sma20 else -1
        return 0

    times = d1.index
    q_starts = pd.date_range(
        start=max(pd.Timestamp("2009-01-01"), times.min() + pd.DateOffset(years=1)),
        end=times.max(),
        freq="QS",
    )

    def run_window(i0, i1, slm, tpm, start_eq=10000.0, record=False):
        e = start_eq
        trades = []
        last = i0
        for i in range(max(i0, 60), i1 - 1):
            if i < last:
                continue
            sig = signal(i)
            if sig == 0:
                continue
            ei = i + 1
            if ei >= i1:
                break
            entry = float(d1.iloc[ei].open)
            sl = entry - sig * sl_pts * slm
            tp = entry + sig * tp_pts * tpm
            exit_px = exit_i = None
            for j in range(ei, min(len(d1), ei + hold_cap + 1)):
                bar = d1.iloc[j]
                hold = (times[j] - times[ei]).days
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
                if hold >= hold_cap:
                    exit_px, exit_i = float(bar.close), j
                    break
            if exit_px is None:
                continue
            hold = (times[exit_i] - times[ei]).days
            gross = sig * (exit_px - entry)
            if phi:
                sp, sw, _ = xm_cost_price(phi, max(hold, 0), sig, gia_tham=entry)
            else:
                sp = sw = 0.0
            net = gross - sp + sw
            risk = abs(entry - sl)
            contract = phi.contract if phi else 10.0
            vol = (0.01 * e) / (risk * contract) if risk > 0 else 0
            pnl = net * contract * vol
            e = max(e + pnl, 0)
            trades.append(dict(pnl=pnl, entry=times[ei], exit=times[exit_i], sig=sig, net=net, hold=hold))
            last = exit_i + 1
        return e, trades

    equity = 10000.0
    oos = []
    eq_pts = []
    params = []
    last_exit_time = times[0]

    for qs in q_starts:
        ts, te = qs - pd.DateOffset(months=12), qs
        i0 = int(d1.index.searchsorted(ts))
        i1 = int(d1.index.searchsorted(te))
        j0 = int(d1.index.searchsorted(qs))
        j1 = int(d1.index.searchsorted(min(qs + pd.DateOffset(months=3), times.max())))
        if i1 - i0 < 50 or j1 - j0 < 5:
            continue
        best = None
        for slm in (0.75, 1.0, 1.25):
            for tpm in (0.75, 1.0, 1.25, 1.5):
                e, trs = run_window(i0, i1, slm, tpm)
                years = max((te - ts).days / 365.25, 1e-9)
                sc = (e / 10000.0) ** (1 / years) - 1 if e > 0 else -1
                if best is None or sc > best[0]:
                    best = (sc, slm, tpm)
        _, slm, tpm = best
        params.append(dict(qs=str(qs.date()), slm=slm, tpm=tpm, train_cagr=round(best[0], 4)))
        # OOS with continuing equity, no overlap
        e, trs = run_window(j0, j1, slm, tpm, start_eq=equity)
        # filter overlap by time
        for t in trs:
            if t["entry"] < last_exit_time:
                continue
            # recompute from current equity path already in run_window starting equity
            oos.append(t)
            last_exit_time = t["exit"]
        # rebuild equity from accepted oos only at end — simpler: use sequential global
        # Instead re-sim OOS chronologically below
        pass

    # Clean sequential OOS with frozen per-window params
    equity = 10000.0
    oos = []
    eq_pts = []
    last_exit_i = 0
    # map qs -> params
    for p, qs in zip(params, [pd.Timestamp(x["qs"]) for x in params]):
        j0 = int(d1.index.searchsorted(qs))
        j1 = int(d1.index.searchsorted(min(qs + pd.DateOffset(months=3), times.max())))
        slm, tpm = p["slm"], p["tpm"]
        for i in range(max(j0, 60), j1 - 1):
            if i < last_exit_i:
                continue
            sig = signal(i)
            if sig == 0:
                continue
            ei = i + 1
            if ei >= j1:
                break
            entry = float(d1.iloc[ei].open)
            sl = entry - sig * sl_pts * slm
            tp = entry + sig * tp_pts * tpm
            exit_px = exit_i = None
            for j in range(ei, min(len(d1), ei + hold_cap + 1)):
                bar = d1.iloc[j]
                hold = (times[j] - times[ei]).days
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
                if hold >= hold_cap:
                    exit_px, exit_i = float(bar.close), j
                    break
            if exit_px is None:
                continue
            hold = (times[exit_i] - times[ei]).days
            gross = sig * (exit_px - entry)
            if phi:
                sp, sw, _ = xm_cost_price(phi, max(hold, 0), sig, gia_tham=entry)
            else:
                sp = sw = 0.0
            net = gross - sp + sw
            risk = abs(entry - sl)
            contract = phi.contract if phi else 10.0
            vol = (0.01 * equity) / (risk * contract) if risk > 0 else 0
            pnl = net * contract * vol
            equity = max(equity + pnl, 0)
            oos.append(dict(pnl=pnl, entry=str(times[ei].date()), hold=hold, sig=sig))
            eq_pts.append((times[exit_i], equity))
            last_exit_i = exit_i + 1

    if not oos:
        return dict(verdict="KHONG_OOS", rule=rule)

    eq = pd.Series({t: e for t, e in eq_pts}).sort_index()
    eq = pd.concat([pd.Series({eq.index[0] - pd.Timedelta(days=1): 10000.0}), eq])
    years = (eq.index[-1] - eq.index[0]).days / 365.25
    cagr_v = cagr(eq, years)
    dd = max_dd(eq)
    pnls = np.array([t["pnl"] for t in oos])
    sh = sharpe_from_trade_pnls(pnls, years)

    rng = np.random.default_rng(42)
    boot = []
    for _ in range(500):
        sample = rng.choice(pnls, size=len(pnls), replace=True)
        e = 10000.0
        for p in sample:
            e = max(e + p, 0)
        if e > 0 and years > 0:
            boot.append((e / 10000.0) ** (1 / years) - 1)

    # random entry D1
    rng2 = np.random.default_rng(7)
    rand = []
    n_tr = len(oos)
    for _ in range(200):
        e = 10000.0
        idxs = rng2.choice(range(60, len(d1) - 2), size=min(n_tr, 400), replace=False)
        for i in sorted(idxs):
            sig = int(rng2.choice([-1, 1]))
            entry = float(d1.iloc[i].open)
            sl = entry - sig * sl_pts
            tp = entry + sig * tp_pts
            exit_px = None
            hold = 0
            for j in range(i, min(len(d1), i + hold_cap + 1)):
                bar = d1.iloc[j]
                hold = (times[j] - times[i]).days
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
                if hold >= hold_cap:
                    exit_px = float(bar.close)
                    break
            if exit_px is None:
                continue
            gross = sig * (exit_px - entry)
            if phi:
                sp, sw, _ = xm_cost_price(phi, max(hold, 0), sig, gia_tham=entry)
            else:
                sp = sw = 0.0
            net = gross - sp + sw
            contract = phi.contract if phi else 10.0
            vol = (0.01 * e) / (sl_pts * contract)
            e = max(e + net * contract * vol, 0)
        if e > 0 and years > 0:
            rand.append((e / 10000.0) ** (1 / years) - 1)

    verdict = "PASS" if (dd == dd and dd < 0.80 and cagr_v == cagr_v and cagr_v > 0.10) else "REJECT"
    return dict(
        rule=rule,
        n_oos_trades=len(oos),
        years=round(years, 3),
        trades_per_yr=round(len(oos) / years, 2) if years else None,
        cagr_pct=round(cagr_v * 100, 3) if cagr_v == cagr_v else None,
        dd_pct=round(dd * 100, 3) if dd == dd else None,
        sharpe=round(sh, 3) if sh == sh else None,
        final_equity=round(equity, 2),
        boot_cagr_p50_pct=round(float(np.median(boot)) * 100, 3) if boot else None,
        boot_cagr_p05_pct=round(float(np.percentile(boot, 5)) * 100, 3) if boot else None,
        random_entry_cagr_p50_pct=round(float(np.median(rand)) * 100, 3) if rand else None,
        random_entry_cagr_p95_pct=round(float(np.percentile(rand, 95)) * 100, 3) if rand else None,
        beat_random=(cagr_v > float(np.median(rand))) if rand and cagr_v == cagr_v else None,
        verdict=verdict,
        phi_nguon=phi.nguon if phi else None,
        n_wf_windows=len(params),
        note="D1 NQ=F proxy US100 2008–2026; WF12/3; risk1%; hold_cap30d; XM cost",
    )


# ===================== MCA100 =====================
def mca100_match(xauh: pd.DataFrame):
    tr = sorted(load_trades(Path("/workspace/mql5_hist/2153920.csv")), key=lambda t: t.t_open)
    xau = [t for t in tr if t.symbol == "XAUUSD"]
    rows = []

    def add(rule, khung, ok, tot, **extra):
        m = ok / tot if tot else 0.0
        rec = dict(he="2153920", rule=rule, khung=khung, match=round(m, 4), ok=ok, tot=tot, accept=m >= 0.60 and tot >= 100)
        rec.update(extra)
        rows.append(rec)
        print(f"MCA {rule}: {ok}/{tot}={m:.1%} accept={rec['accept']}")
        return rec

    # Direction-only (no fill price) — prior bar features
    def dir_test(name, fn):
        ok = tot = 0
        for t in xau:
            hist = xauh.loc[: pd.Timestamp(t.t_open) - pd.Timedelta(seconds=1)]
            if len(hist) < 60:
                continue
            pred = fn(hist)
            if pred == 0:
                continue
            tot += 1
            if pred == t.chieu:
                ok += 1
        add(name, "H1", ok, tot)

    dir_test("h1_close_gt_sma20", lambda h: 1 if h.iloc[-1].close > h.close.iloc[-20:].mean() else -1)
    dir_test("h1_close_gt_sma50", lambda h: 1 if h.iloc[-1].close > h.close.iloc[-50:].mean() else -1)
    dir_test("h1_bull_bar", lambda h: 1 if h.iloc[-1].close > h.iloc[-1].open else -1)
    dir_test("h1_close_gt_prior", lambda h: 1 if h.iloc[-1].close > h.iloc[-2].close else -1)
    add("always_buy_baseline", "meta", sum(t.chieu > 0 for t in xau), len(xau), note="không phải luật vào lệnh 2 chiều")

    # Structure match: Buy entry ≈ prior D1 high (±tol); Sell ≈ prior D1 low
    # This tests pending-stop placement hypothesis without tautology on direction from fill
    for tol in (1.0, 2.0, 5.0, 10.0):
        ok = tot = 0
        for t in xau:
            hist = xauh.loc[: pd.Timestamp(t.t_open) - pd.Timedelta(seconds=1)]
            d1 = hist.resample("1D").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
            if len(d1) < 3:
                continue
            prev = d1.iloc[-2]  # last completed D1
            tot += 1
            if t.chieu > 0:
                if abs(t.price_open - float(prev.high)) <= tol:
                    ok += 1
            else:
                if abs(t.price_open - float(prev.low)) <= tol:
                    ok += 1
        add(f"entry_near_priorD1_extreme_tol{tol}", "D1", ok, tot, note="cấu trúc giá vào vs cực trị D1 trước")

    for tol in (0.5, 1.0, 2.0, 5.0):
        ok = tot = 0
        for t in xau:
            hist = xauh.loc[: pd.Timestamp(t.t_open) - pd.Timedelta(seconds=1)]
            if len(hist) < 5:
                continue
            prev = hist.iloc[-1]
            tot += 1
            if t.chieu > 0:
                if abs(t.price_open - float(prev.high)) <= tol:
                    ok += 1
            else:
                if abs(t.price_open - float(prev.low)) <= tol:
                    ok += 1
        add(f"entry_near_priorH1_extreme_tol{tol}", "H1", ok, tot)

    # Regenerative breakout rule match: each day place BS at D1.high+off, SS at D1.low-off;
    # first fill in next 5 days; compare to real trades that day-window (direction ±1 bar)
    # Measure: of real trades, what % have a simulated fill same direction within ±1 H1 bar
    for off in (0.0, 0.5, 1.0, 2.0, 5.0):
        ok = tot = 0
        for t in xau:
            t0 = pd.Timestamp(t.t_open)
            hist = xauh.loc[: t0 - pd.Timedelta(seconds=1)]
            d1 = hist.resample("1D").agg({"high": "max", "low": "min"}).dropna()
            if len(d1) < 3:
                continue
            prev = d1.iloc[-2]
            bs = float(prev.high) + off
            ss = float(prev.low) - off
            # walk forward H1 from start of decision day (day after prev) to t0+2h
            start = d1.index[-1]  # current incomplete or last
            fut = xauh.loc[start : t0 + pd.Timedelta(hours=2)]
            if len(fut) < 2:
                continue
            sim_dir = None
            sim_time = None
            for ts, bar in fut.iterrows():
                if bar.high >= bs:
                    sim_dir, sim_time = 1, ts
                    break
                if bar.low <= ss:
                    sim_dir, sim_time = -1, ts
                    break
            tot += 1
            if sim_dir == t.chieu and sim_time is not None:
                if abs((sim_time - t0).total_seconds()) <= 3600 * 2:  # within 2h ≈ ±1-2 H1 bars
                    ok += 1
                elif sim_dir == t.chieu:
                    # direction only match (looser)
                    pass
        add(f"regen_D1break_off{off}_dir+time±2h", "D1", ok, tot)

    # looser: direction-only regen
    for off in (0.0, 1.0, 5.0):
        ok = tot = 0
        for t in xau:
            t0 = pd.Timestamp(t.t_open)
            hist = xauh.loc[: t0 - pd.Timedelta(seconds=1)]
            d1 = hist.resample("1D").agg({"high": "max", "low": "min"}).dropna()
            if len(d1) < 3:
                continue
            prev = d1.iloc[-2]
            bs = float(prev.high) + off
            ss = float(prev.low) - off
            start = d1.index[-1]
            fut = xauh.loc[start : t0 + pd.Timedelta(days=5)]
            sim_dir = None
            for ts, bar in fut.iterrows():
                if bar.high >= bs:
                    sim_dir = 1
                    break
                if bar.low <= ss:
                    sim_dir = -1
                    break
            if sim_dir is None:
                continue
            tot += 1
            if sim_dir == t.chieu:
                ok += 1
        add(f"regen_D1break_off{off}_dir_only", "D1", ok, tot)

    sl = [abs(t.sl - t.price_open) for t in xau if t.sl]
    tp = [abs(t.tp - t.price_open) for t in xau if t.tp]
    meta = dict(
        n=len(xau),
        n_all=len(tr),
        buy_pct=round(100 * sum(t.chieu > 0 for t in xau) / len(xau), 2),
        sl_med=round(float(np.median(sl)), 4) if sl else None,
        tp_med=round(float(np.median(tp)), 4) if tp else None,
        hold_med_h=round(float(np.median([(t.t_close - t.t_open).total_seconds() / 3600 for t in xau])), 3),
        range=[str(xau[0].t_open), str(xau[-1].t_open)],
        pending_raw=dict(BuyStop=274, SellStop=104, BuyLimit=17),
    )
    return rows, meta, xau


def v1_mca_breakout(xauh, off=0.0, sl_pts=6.85, tp_pts=8.54):
    """V1 XAU: mỗi ngày đặt BuyStop=priorD1.high+off, SellStop=priorD1.low-off; SL/TP cố định; WF12/3."""
    phi = load_phi("XAUUSD")
    d1 = xauh.resample("1D").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    hold_cap_days = 30

    # Build list of daily signals (stop levels)
    days = d1.index

    def sim_from_day(di, slm, tpm, start_eq):
        """di = index into d1 for prior day used as reference; enter from di+1."""
        if di + 1 >= len(d1) - 1:
            return None
        prev = d1.iloc[di]
        bs = float(prev.high) + off
        ss = float(prev.low) - off
        # scan H1 from start of next day
        t_start = days[di + 1]
        t_end = t_start + pd.Timedelta(days=hold_cap_days)
        fut = xauh.loc[t_start:t_end]
        if len(fut) < 2:
            return None
        sig = entry = entry_t = None
        for ts, bar in fut.iterrows():
            if bar.high >= bs:
                sig, entry, entry_t = 1, bs, ts
                break
            if bar.low <= ss:
                sig, entry, entry_t = -1, ss, ts
                break
        if sig is None:
            return None
        sl = entry - sig * sl_pts * slm
        tp = entry + sig * tp_pts * tpm
        after = fut.loc[entry_t:]
        exit_px = None
        exit_t = None
        for ts, bar in after.iloc[1:].iterrows():
            hold = (ts - entry_t).total_seconds() / 86400
            if sig > 0:
                if bar.low <= sl:
                    exit_px, exit_t = sl, ts
                    break
                if bar.high >= tp:
                    exit_px, exit_t = tp, ts
                    break
            else:
                if bar.high >= sl:
                    exit_px, exit_t = sl, ts
                    break
                if bar.low <= tp:
                    exit_px, exit_t = tp, ts
                    break
            if hold >= hold_cap_days:
                exit_px, exit_t = float(bar.close), ts
                break
        if exit_px is None:
            return None
        hold = (exit_t - entry_t).total_seconds() / 86400
        gross = sig * (exit_px - entry)
        if phi:
            sp, sw, _ = xm_cost_price(phi, max(hold, 0), sig, gia_tham=entry)
        else:
            sp = sw = 0.0
        net = gross - sp + sw
        return dict(entry_t=entry_t, exit_t=exit_t, sig=sig, net=net, hold=hold, entry=entry, exit=exit_px)

    q_starts = pd.date_range(
        start=max(pd.Timestamp("2010-01-01"), d1.index.min() + pd.DateOffset(years=1)),
        end=d1.index.max(),
        freq="QS",
    )

    def train_best(t0, t1):
        best = None
        # sample every 2nd day for speed
        di0 = int(d1.index.searchsorted(t0))
        di1 = int(d1.index.searchsorted(t1))
        for slm in (0.75, 1.0, 1.25):
            for tpm in (0.75, 1.0, 1.25):
                e = 10000.0
                last_exit = t0
                n = 0
                for di in range(di0, di1 - 2, 1):
                    if days[di] < last_exit:
                        continue
                    r = sim_from_day(di, slm, tpm, e)
                    if r is None:
                        continue
                    if r["entry_t"] < pd.Timestamp(t0) or r["entry_t"] >= pd.Timestamp(t1):
                        continue
                    risk = sl_pts * slm
                    contract = phi.contract if phi else 1.0
                    vol = (0.01 * e) / (risk * contract) if risk > 0 else 0
                    pnl = r["net"] * contract * vol
                    e = max(e + pnl, 0)
                    last_exit = r["exit_t"]
                    n += 1
                years = max((t1 - t0).days / 365.25, 1e-9)
                sc = (e / 10000.0) ** (1 / years) - 1 if e > 0 else -1
                if best is None or sc > best[0]:
                    best = (sc, slm, tpm, n)
        return best

    equity = 10000.0
    oos = []
    eq_pts = []
    params = []
    last_exit = d1.index.min()

    for qs in q_starts:
        ts = qs - pd.DateOffset(months=12)
        if ts < d1.index.min():
            continue
        bp = train_best(ts, qs)
        if bp is None:
            continue
        _, slm, tpm, _ = bp
        params.append(dict(qs=str(qs.date()), slm=slm, tpm=tpm, train_cagr=round(bp[0], 4)))
        di0 = int(d1.index.searchsorted(qs))
        di1 = int(d1.index.searchsorted(min(qs + pd.DateOffset(months=3), d1.index.max())))
        for di in range(di0, di1 - 2):
            if days[di] < last_exit:
                continue
            r = sim_from_day(di, slm, tpm, equity)
            if r is None:
                continue
            if r["entry_t"] < qs or r["entry_t"] >= qs + pd.DateOffset(months=3):
                continue
            risk = sl_pts * slm
            contract = phi.contract if phi else 1.0
            vol = (0.01 * equity) / (risk * contract) if risk > 0 else 0
            pnl = r["net"] * contract * vol
            equity = max(equity + pnl, 0)
            oos.append(dict(pnl=pnl, entry=str(r["entry_t"]), sig=r["sig"], hold=r["hold"], net=r["net"]))
            eq_pts.append((r["exit_t"], equity))
            last_exit = r["exit_t"]

    if not oos:
        return dict(verdict="KHONG_OOS", rule=f"D1_breakout_off{off}")

    eq = pd.Series({t: e for t, e in eq_pts}).sort_index()
    eq = pd.concat([pd.Series({eq.index[0] - pd.Timedelta(days=1): 10000.0}), eq])
    years = (eq.index[-1] - eq.index[0]).total_seconds() / (365.25 * 86400)
    cagr_v = cagr(eq, years)
    dd = max_dd(eq)
    pnls = np.array([t["pnl"] for t in oos])
    sh = sharpe_from_trade_pnls(pnls, years)

    rng = np.random.default_rng(42)
    boot = []
    for _ in range(500):
        sample = rng.choice(pnls, size=len(pnls), replace=True)
        e = 10000.0
        for p in sample:
            e = max(e + p, 0)
        if e > 0 and years > 0:
            boot.append((e / 10000.0) ** (1 / years) - 1)

    rng2 = np.random.default_rng(7)
    rand = []
    n_tr = len(oos)
    for _ in range(100):  # fewer — MCA sim heavier
        e = 10000.0
        idxs = rng2.choice(range(60, len(d1) - 5), size=min(n_tr, 300), replace=False)
        for di in sorted(idxs):
            # random direction market entry at D1 open
            sig = int(rng2.choice([-1, 1]))
            entry = float(d1.iloc[di].open)
            sl = entry - sig * sl_pts
            tp = entry + sig * tp_pts
            fut = xauh.loc[days[di] : days[di] + pd.Timedelta(days=hold_cap_days)]
            exit_px = None
            exit_t = None
            entry_t = days[di]
            for ts, bar in fut.iloc[1:].iterrows():
                hold = (ts - entry_t).total_seconds() / 86400
                if sig > 0:
                    if bar.low <= sl:
                        exit_px, exit_t = sl, ts
                        break
                    if bar.high >= tp:
                        exit_px, exit_t = tp, ts
                        break
                else:
                    if bar.high >= sl:
                        exit_px, exit_t = sl, ts
                        break
                    if bar.low <= tp:
                        exit_px, exit_t = tp, ts
                        break
                if hold >= hold_cap_days:
                    exit_px, exit_t = float(bar.close), ts
                    break
            if exit_px is None:
                continue
            hold = (exit_t - entry_t).total_seconds() / 86400
            gross = sig * (exit_px - entry)
            if phi:
                sp, sw, _ = xm_cost_price(phi, max(hold, 0), sig, gia_tham=entry)
            else:
                sp = sw = 0.0
            net = gross - sp + sw
            contract = phi.contract if phi else 1.0
            vol = (0.01 * e) / (sl_pts * contract)
            e = max(e + net * contract * vol, 0)
        if e > 0 and years > 0:
            rand.append((e / 10000.0) ** (1 / years) - 1)

    verdict = "PASS" if (dd == dd and dd < 0.80 and cagr_v == cagr_v and cagr_v > 0.10) else "REJECT"
    return dict(
        rule=f"XAU_D1_breakout_off{off}_SL{sl_pts}_TP{tp_pts}",
        n_oos_trades=len(oos),
        years=round(years, 3),
        trades_per_yr=round(len(oos) / years, 2) if years else None,
        cagr_pct=round(cagr_v * 100, 3) if cagr_v == cagr_v else None,
        dd_pct=round(dd * 100, 3) if dd == dd else None,
        sharpe=round(sh, 3) if sh == sh else None,
        final_equity=round(equity, 2),
        boot_cagr_p50_pct=round(float(np.median(boot)) * 100, 3) if boot else None,
        boot_cagr_p05_pct=round(float(np.percentile(boot, 5)) * 100, 3) if boot else None,
        random_entry_cagr_p50_pct=round(float(np.median(rand)) * 100, 3) if rand else None,
        random_entry_cagr_p95_pct=round(float(np.percentile(rand, 95)) * 100, 3) if rand else None,
        beat_random=(cagr_v > float(np.median(rand))) if rand and cagr_v == cagr_v else None,
        verdict=verdict,
        phi_nguon=phi.nguon if phi else None,
        n_wf_windows=len(params),
        note="XAU H1 2009–2026; WF12/3; risk1%; hold_cap30d; XM phi_xm_micro",
    )


def friday_pro_vs_bh():
    tr = sorted(load_trades(Path("/workspace/mql5_hist/2344620.csv")), key=lambda t: t.t_open)
    out = {}
    for sym in ("GBPJPY", "USDJPY"):
        ts = [t for t in tr if t.symbol == sym]
        if len(ts) < 10:
            continue
        t0, t1 = ts[0].t_open, ts[-1].t_close
        px0, px1 = ts[0].price_open, ts[-1].price_close
        years = (t1 - t0).total_seconds() / (365.25 * 86400)
        ret = px1 / px0 - 1
        cagr_px = (1 + ret) ** (1 / years) - 1 if years > 0 and (1 + ret) > 0 else float("nan")
        buy_pct = 100 * sum(1 for t in ts if t.chieu > 0) / len(ts)
        sys_net = sum(t.profit + t.swap + t.commission for t in ts)
        # continuous long 1.0 lot swap drag over same period (price units)
        phi = load_phi(sym)
        swap_drag_pct = None
        if phi and years > 0:
            dem = years * 365 * 7 / 5
            # POINTS mode: swap_mua * point * nights → price
            sw_price = phi.swap_mua * phi.point * dem
            mid = (px0 + px1) / 2
            swap_drag_pct = 100 * sw_price / mid if mid else None
            # B&H after swap (long): price ret + swap drag (swap_mua can be + or -)
            bh_after_swap_ret = ret + sw_price / px0
            bh_as_cagr = (1 + bh_after_swap_ret) ** (1 / years) - 1 if (1 + bh_after_swap_ret) > 0 else float("nan")
        else:
            bh_as_cagr = float("nan")
        # system CAGR rough from sum profit — NOT account equity; report absolute + buy%
        out[sym] = dict(
            n=len(ts),
            years=round(years, 3),
            buy_pct=round(buy_pct, 2),
            bh_price_ret_pct=round(ret * 100, 3),
            bh_price_cagr_pct=round(cagr_px * 100, 3) if cagr_px == cagr_px else None,
            bh_after_swap_cagr_pct=round(bh_as_cagr * 100, 3) if bh_as_cagr == bh_as_cagr else None,
            swap_long_drag_pct_of_mid=round(swap_drag_pct, 4) if swap_drag_pct is not None else None,
            sys_net_broker_usd=round(sys_net, 2),
            px0=px0,
            px1=px1,
            note="B&H ĐO từ giá open lệnh đầu → close lệnh cuối CSV; swap liên tục 1 lot theo phi XM/chi_phi_do",
        )
    buy_all = 100 * sum(1 for t in tr if t.chieu > 0) / len(tr)
    out["ALL"] = dict(n=len(tr), buy_pct=round(buy_all, 2), hang="pyramid", max_cung=5,
                      ket_luan="buy%≈100% → gần buy-and-hold có chọn lọc; so với B&H sau swap xem sym")
    return out


def main():
    print("=== GRID recount (đã có) ===")
    grid = json.loads((OUT / "grid_recount.json").read_text())
    from collections import Counter
    if isinstance(grid, list):
        hang = Counter(x.get("hang") for x in grid)
        mart = sum(1 for x in grid if x.get("martingale"))
        grid_summary = dict(hang)
        grid_summary["martingale"] = mart
        grid_summary["n"] = len(grid)
        print(grid_summary)
        grid = grid_summary
    else:
        print(grid)

    print("\n=== KIVENARA match ===")
    kiv_rules, kiv_meta, kiv_tr, d1, h1 = kivenara_match()
    kiv_acc = [r for r in kiv_rules if r["accept"]]
    kiv_acc.sort(key=lambda x: -x["match"])
    print("accepted", len(kiv_acc), "best", kiv_acc[0] if kiv_acc else None)

    print("\n=== MCA100 match ===")
    xauh = load_xau_h1()
    mca_rules, mca_meta, mca_tr = mca100_match(xauh)
    mca_acc = [r for r in mca_rules if r["accept"] and r["rule"] != "always_buy_baseline"]
    mca_acc.sort(key=lambda x: -x["match"])
    print("accepted (excl baseline)", len(mca_acc), "best", mca_acc[0] if mca_acc else None)

    print("\n=== Friday B&H ===")
    fri = friday_pro_vs_bh()
    print(json.dumps(fri, ensure_ascii=False, indent=2))

    v1 = {}
    # Kivenara V1: H1 best + D1 accepted
    if any(r["rule"] == "h1_off3_sma50" and r["accept"] for r in kiv_rules):
        print("\n=== V1 Kivenara H1 ===")
        v1["kivenara_h1"] = v1_kivenara_h1(h1)
        print(json.dumps({k: v1["kivenara_h1"][k] for k in v1["kivenara_h1"] if k != "param_hist"}, ensure_ascii=False, indent=2))
    d1_acc = [r for r in kiv_acc if r["rule"].startswith("d1_")]
    if d1_acc:
        rule = d1_acc[0]["rule"]
        print(f"\n=== V1 Kivenara D1 {rule} ===")
        v1["kivenara_d1"] = v1_kivenara_d1(d1, rule)
        print(json.dumps(v1["kivenara_d1"], ensure_ascii=False, indent=2))

    # MCA V1 only if regenerative breakout direction match >= 60%
    regen_ok = [r for r in mca_acc if "regen_D1break" in r["rule"] and "dir" in r["rule"]]
    trend_ok = [r for r in mca_acc if r["rule"].startswith("h1_")]
    if regen_ok:
        # pick best off from rule name
        best = regen_ok[0]
        import re
        m = re.search(r"off([0-9.]+)", best["rule"])
        off = float(m.group(1)) if m else 0.0
        print(f"\n=== V1 MCA breakout off={off} ===")
        v1["mca100"] = v1_mca_breakout(xauh, off=off)
        print(json.dumps({k: v1["mca100"][k] for k in v1["mca100"]}, ensure_ascii=False, indent=2))
    elif trend_ok and trend_ok[0]["match"] >= 0.60:
        # trend filter alone is not entry — still try breakout off=0 as structural candidate if dir_only close
        print("\n=== V1 MCA thử D1 breakout off=0 (trend match cao nhưng breakout cấu trúc) ===")
        # Only run if we accept a directional rule; use off=0
        v1["mca100"] = v1_mca_breakout(xauh, off=0.0)
        v1["mca100"]["match_basis"] = trend_ok[0]
        print(json.dumps({k: v1["mca100"].get(k) for k in ("verdict", "cagr_pct", "dd_pct", "sharpe", "n_oos_trades", "trades_per_yr", "years", "beat_random", "boot_cagr_p50_pct", "random_entry_cagr_p50_pct")}, ensure_ascii=False, indent=2))
    else:
        v1["mca100"] = dict(verdict="KHONG_CO_LUAT", ly_do="không rule tái tạo đạt match>=60% (ngoài always_buy / trend-trong-bull)", top=mca_rules[:10])

    out = dict(
        grid_recount_summary=grid if isinstance(grid, dict) else {},
        kivenara_meta=kiv_meta,
        kivenara_rules=kiv_rules,
        kivenara_accepted=kiv_acc[:10],
        mca_meta=mca_meta,
        mca_rules=mca_rules,
        mca_accepted=mca_acc[:10],
        friday_bh=fri,
        v1=v1,
    )
    (OUT / "v1_dich_nguoc_ket_qua.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("\nWROTE v1_dich_nguoc_ket_qua.json")


if __name__ == "__main__":
    main()
