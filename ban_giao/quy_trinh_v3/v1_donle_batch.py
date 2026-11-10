#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RE + V1 batch cho don_le (trừ 2229059) + pyramid e/c>=1.2."""
from __future__ import annotations
import json, math
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, "/workspace/quy_trinh_v3")
from phan_tich_mql5_hist import load_trades, load_phi, xm_cost_price

OUT = Path("/workspace/quy_trinh_v3")
DATA = OUT / "data"

CANDS = [
    # don_le e/c>=1.2 (excl 2229059)
    dict(id="2244828", ten="Kivenara 815m52ff", hang="don_le", ec=3.573, ket0="REJECT_CAGR"),
    dict(id="2269966", ten="BreakZone Scalper HFM", hang="don_le", ec=1.285, ket0="REJECT_ec"),
    dict(id="2245675", ten="OnlyUJ", hang="don_le", ec=1.250, ket0="REJECT_ec"),
    dict(id="2250577", ten="Golden System 2", hang="don_le", ec=2.571, ket0="REJECT_CAGR"),
    # pyramid PASS or e/c>=1.2 (MCA/Friday already V1'd — still restate)
    dict(id="2392805", ten="UZUNAMI88", hang="pyramid", ec=4.175, ket0="REJECT_CAGR"),
    dict(id="2337217", ten="Top Cat S", hang="pyramid", ec=1.359, ket0="REJECT_ec"),
]


def load_nq_d1():
    df = pd.read_csv(DATA / "nq_f_d1.csv", skiprows=3, names=["dt", "close", "high", "low", "open", "volume"])
    df["dt"] = pd.to_datetime(df["dt"])
    return df.set_index("dt").sort_index().dropna(subset=["close"])


def load_nq_h1():
    df = pd.read_csv(DATA / "nq_f_h1.csv", skiprows=3, names=["dt", "close", "high", "low", "open", "volume"])
    df["dt"] = pd.to_datetime(df["dt"], utc=True)
    return df.set_index("dt").sort_index().dropna(subset=["close"])


def load_xau_h1():
    h1 = pd.read_csv("/workspace/du_lieu_fx/hd_dai/xauusd_h1_2008_2023_ny7.csv")
    h1["dt"] = pd.to_datetime(h1["time"])
    h1 = h1.set_index("dt")[["open", "high", "low", "close"]].astype(float)
    m5 = pd.read_csv("/workspace/du_lieu_fx/hd28/xauusd_m5_histdata_ny7_den202610.csv")
    m5["dt"] = pd.to_datetime(m5["time"])
    m5 = m5.set_index("dt")[["open", "high", "low", "close"]].astype(float)
    h1b = m5.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    out = pd.concat([h1, h1b]).sort_index()
    return out[~out.index.duplicated(keep="last")]


def load_fx_h1(sym: str) -> pd.DataFrame:
    """Try common paths for FX H1."""
    cands = [
        Path(f"/workspace/du_lieu_fx/{sym.lower()}_h1_tu_histdata_m5_ny7.csv"),
        Path(f"/workspace/du_lieu_fx/{sym.lower()}_h1_tick_ba_ny7.csv"),
        Path(f"/workspace/du_lieu_fx/{sym.lower()}_h1_duka_ba_2024_2026.csv"),
        Path(f"/workspace/du_lieu_fx/hd_dai/{sym.lower()}_h1_2009_2023_ny7.csv"),
        Path(f"/workspace/du_lieu_fx/hd_dai/{sym.lower()}_h1_2008_2023_ny7.csv"),
    ]
    # also build from m5 if present
    m5p = Path(f"/workspace/du_lieu_fx/{sym.lower()}_m5_histdata_ny7.csv")
    frames = []
    for p in cands:
        if p.exists():
            d = pd.read_csv(p)
            cols = {c.lower(): c for c in d.columns}
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
                d = d.set_index("dt")[["open", "high", "low", "close"]].astype(float)
                frames.append(d)
                print(f"  loaded {p.name} n={len(d)}")
    if m5p.exists():
        d = pd.read_csv(m5p)
        rename = {}
        for c in d.columns:
            cl = c.lower()
            if cl in ("time", "datetime", "date", "dt") or "time" in cl:
                rename[c] = "dt"
            elif cl in ("open", "high", "low", "close"):
                rename[c] = cl
        d = d.rename(columns=rename)
        d["dt"] = pd.to_datetime(d["dt"])
        d = d.set_index("dt")[["open", "high", "low", "close"]].astype(float)
        h = d.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
        frames.append(h)
        print(f"  m5→h1 {m5p.name} n={len(h)}")
    if not frames:
        raise FileNotFoundError(sym)
    out = pd.concat(frames).sort_index()
    return out[~out.index.duplicated(keep="last")]


def match_h1_sma(tr, h1, off_hours, win=50, entry_minute=None):
    ok = tot = 0
    for t in tr:
        ts = (pd.Timestamp(t.t_open) - pd.Timedelta(hours=off_hours))
        if ts.tzinfo is None:
            ts = ts.tz_localize("UTC")
        else:
            ts = ts.tz_convert("UTC")
        if h1.index.tz is None:
            # assume NY7 / naive as UTC-equivalent for HistData ny7 — treat naive
            ts_naive = pd.Timestamp(t.t_open) - pd.Timedelta(hours=off_hours)
            if ts_naive < h1.index.min() or ts_naive > h1.index.max():
                continue
            loc = h1.index.asof(ts_naive - pd.Timedelta(minutes=1))
        else:
            if ts < h1.index.min() or ts > h1.index.max():
                continue
            loc = h1.index.asof(ts - pd.Timedelta(minutes=1))
        if pd.isna(loc):
            continue
        i = h1.index.get_loc(loc)
        if isinstance(i, slice) or i < win:
            continue
        sma = h1.close.iloc[i - win + 1 : i + 1].mean()
        pred = 1 if h1.iloc[i].close > sma else -1
        tot += 1
        if pred == t.chieu:
            ok += 1
    return ok, tot, (ok / tot if tot else 0.0)


def match_d1_rule(tr, d1, rule):
    d1 = d1.copy()
    d1["sma20"] = d1.close.rolling(20).mean()
    d1["sma50"] = d1.close.rolling(50).mean()
    ok = tot = 0
    for t in tr:
        day = pd.Timestamp(t.t_open.date())
        hist = d1.loc[: day - pd.Timedelta(days=1)]
        if len(hist) < 60:
            continue
        row = hist.iloc[-1]
        if rule == "prior_bull":
            pred = 1 if row.close > row.open else -1
        elif rule == "close_gt_prior":
            pred = 1 if row.close > hist.iloc[-2].close else -1
        elif rule == "close_gt_sma20":
            pred = 1 if row.close > row.sma20 else -1
        elif rule == "close_gt_sma50":
            pred = 1 if row.close > row.sma50 else -1
        else:
            continue
        tot += 1
        if pred == t.chieu:
            ok += 1
    return ok, tot, (ok / tot if tot else 0.0)


def match_h1_rules_generic(tr, h1, naive=True):
    """Scan common H1 direction rules with TZ offsets 0..8."""
    results = []
    for off in range(0, 9):
        for mode, win in [("sma50", 50), ("sma20", 20), ("bull", 0), ("vs_prev", 0)]:
            ok = tot = 0
            for t in tr:
                if naive:
                    ts = pd.Timestamp(t.t_open) - pd.Timedelta(hours=off)
                    if h1.index.tz is not None:
                        ts = ts.tz_localize("UTC")
                else:
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
            if tot >= 80:
                results.append(dict(rule=f"h1_off{off}_{mode}", match=round(ok / tot, 4), ok=ok, tot=tot, off=off, mode=mode))
    results.sort(key=lambda x: -x["match"])
    return results


def cagr(eq, years):
    if years <= 0 or len(eq) < 2:
        return float("nan")
    v0, v1 = float(eq.iloc[0]), float(eq.iloc[-1])
    if v0 <= 0 or v1 <= 0:
        return float("nan")
    return (v1 / v0) ** (1 / years) - 1


def max_dd(eq):
    peak = eq.cummax()
    dd = (peak - eq) / peak.replace(0, np.nan)
    return float(dd.max()) if len(dd) else float("nan")


def sharpe_trades(pnls, years):
    if len(pnls) < 10 or years <= 0:
        return float("nan")
    a = np.array(pnls, dtype=float)
    if a.std() == 0:
        return float("nan")
    return float(a.mean() / a.std() * math.sqrt(len(a) / years))


def v1_h1_tod_sma(h1, phi_sym, entry_hour_utc, sma_win=50, sl_pts=100.0, tp_pts=165.0, trail_opt=True):
    """Generic V1: enter at entry_hour_utc each day, dir=close>SMA, WF12/3."""
    phi = load_phi(phi_sym)
    if phi is None:
        return dict(verdict="CHUA_DO", ly_do=f"no phi {phi_sym}")
    hold_cap_bars = 30 * 24
    close = h1["close"].values
    opens = h1["open"].values
    highs = h1["high"].values
    lows = h1["low"].values
    times = h1.index
    # ensure tz-aware UTC for NQ; for naive FX treat as-is
    sma = pd.Series(close).rolling(sma_win).mean().values

    def signal_at(i):
        if i < sma_win or np.isnan(sma[i]):
            return 0
        return 1 if close[i] > sma[i] else -1

    def hour_of(ts):
        return ts.hour

    cand = [i for i in range(sma_win, len(h1) - 2) if hour_of(times[i]) == entry_hour_utc]

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
                    return float(sl_cur), j
                if highs[j] >= tp:
                    return float(tp), j
            else:
                if highs[j] >= sl_cur:
                    return float(sl_cur), j
                if lows[j] <= tp:
                    return float(tp), j
        j = min(len(h1) - 1, entry_i + hold_cap_bars)
        return float(close[j]), j

    # WF windows
    tmin = times[sma_win]
    if getattr(tmin, "tzinfo", None) is not None:
        q_starts = pd.date_range(start=max(pd.Timestamp("2010-01-01", tz="UTC"), tmin + pd.DateOffset(months=12)), end=times[-1], freq="QS")
    else:
        q_starts = pd.date_range(start=max(pd.Timestamp("2010-01-01"), pd.Timestamp(tmin) + pd.DateOffset(months=12)), end=times[-1], freq="QS")

    def train_score(i0, i1, slm, tpm, trail):
        e = 10000.0
        last = i0
        for i in cand:
            if i < i0 or i >= i1 or i < last:
                continue
            sig = signal_at(i - 1)
            if sig == 0:
                continue
            entry = float(opens[i])
            sl0 = entry - sig * sl_pts * slm
            tp0 = entry + sig * tp_pts * tpm
            exit_px, exit_i = _sim(i, sig, sl0, tp0, trail, sl_pts * slm)
            hold_days = (times[exit_i] - times[i]).total_seconds() / 86400
            gross = sig * (exit_px - entry)
            sp, sw, _ = xm_cost_price(phi, max(hold_days, 0), sig, gia_tham=entry)
            net = gross - sp + sw
            risk = abs(entry - (entry - sig * sl_pts * slm))
            vol = (0.01 * e) / (risk * phi.contract) if risk > 0 else 0
            e = max(e + net * phi.contract * vol, 0)
            last = exit_i + 1
        years = max((times[min(i1, len(times) - 1)] - times[i0]).total_seconds() / (365.25 * 86400), 1e-9)
        return (e / 10000.0) ** (1 / years) - 1 if e > 0 else -1

    equity = 10000.0
    oos = []
    eq_pts = []
    params = []
    last_exit_i = 0
    trails = (False, True) if trail_opt else (False,)

    for qs in q_starts:
        train_start = qs - pd.DateOffset(months=12)
        i0 = int(h1.index.searchsorted(train_start))
        i1 = int(h1.index.searchsorted(qs))
        j0 = int(h1.index.searchsorted(qs))
        j1 = int(h1.index.searchsorted(min(qs + pd.DateOffset(months=3), times[-1])))
        if i1 - i0 < 100 or j1 - j0 < 5:
            continue
        best = None
        for slm in (0.75, 1.0, 1.25):
            for tpm in (0.75, 1.0, 1.25, 1.5):
                for trail in trails:
                    sc = train_score(i0, i1, slm, tpm, trail)
                    if best is None or sc > best[0]:
                        best = (sc, slm, tpm, trail)
        _, slm, tpm, trail = best
        params.append(dict(qs=str(qs.date()), slm=slm, tpm=tpm, trail=trail, train_cagr=round(best[0], 4)))
        for i in cand:
            if i < j0 or i >= j1 or i < last_exit_i:
                continue
            sig = signal_at(i - 1)
            if sig == 0:
                continue
            entry = float(opens[i])
            sl0 = entry - sig * sl_pts * slm
            tp0 = entry + sig * tp_pts * tpm
            exit_px, exit_i = _sim(i, sig, sl0, tp0, trail, sl_pts * slm)
            hold_days = (times[exit_i] - times[i]).total_seconds() / 86400
            gross = sig * (exit_px - entry)
            sp, sw, _ = xm_cost_price(phi, max(hold_days, 0), sig, gia_tham=entry)
            net = gross - sp + sw
            risk = abs(entry - (entry - sig * sl_pts * slm))
            vol = (0.01 * equity) / (risk * phi.contract) if risk > 0 else 0
            pnl = net * phi.contract * vol
            equity = max(equity + pnl, 0)
            oos.append(pnl)
            eq_pts.append((times[exit_i], equity))
            last_exit_i = exit_i + 1

    if not oos:
        return dict(verdict="KHONG_OOS", n=0)
    eq = pd.Series({t: e for t, e in eq_pts}).sort_index()
    eq = pd.concat([pd.Series({eq.index[0] - pd.Timedelta(days=1): 10000.0}), eq])
    years = (eq.index[-1] - eq.index[0]).total_seconds() / (365.25 * 86400)
    cagr_v = cagr(eq, years)
    dd = max_dd(eq)
    pnls = np.array(oos)
    sh = sharpe_trades(pnls, years)
    rng = np.random.default_rng(42)
    boot = []
    for _ in range(500):
        sample = rng.choice(pnls, size=len(pnls), replace=True)
        e = 10000.0
        for p in sample:
            e = max(e + p, 0)
        if e > 0 and years > 0:
            boot.append((e / 10000.0) ** (1 / years) - 1)
    # random entry
    rng2 = np.random.default_rng(7)
    rand = []
    for _ in range(200):
        e = 10000.0
        last = 0
        picked = 0
        order = list(cand)
        rng2.shuffle(order)
        for i in sorted(order):
            if i < last or picked >= len(oos):
                continue
            if times[i] < eq.index[0] or times[i] > eq.index[-1]:
                continue
            sig = int(rng2.choice([-1, 1]))
            entry = float(opens[i])
            sl0 = entry - sig * sl_pts
            tp0 = entry + sig * tp_pts
            exit_px, exit_i = _sim(i, sig, sl0, tp0, False, sl_pts)
            hold_days = (times[exit_i] - times[i]).total_seconds() / 86400
            gross = sig * (exit_px - entry)
            sp, sw, _ = xm_cost_price(phi, max(hold_days, 0), sig, gia_tham=entry)
            net = gross - sp + sw
            vol = (0.01 * e) / (sl_pts * phi.contract)
            e = max(e + net * phi.contract * vol, 0)
            last = exit_i + 1
            picked += 1
        if e > 0 and years > 0:
            rand.append((e / 10000.0) ** (1 / years) - 1)

    verdict = "PASS" if (dd == dd and dd < 0.80 and cagr_v == cagr_v and cagr_v > 0.10) else "REJECT"
    return dict(
        n_oos=len(oos),
        years=round(years, 3),
        trades_per_yr=round(len(oos) / years, 2) if years else None,
        cagr_pct=round(cagr_v * 100, 3) if cagr_v == cagr_v else None,
        dd_pct=round(dd * 100, 3) if dd == dd else None,
        sharpe=round(sh, 3) if sh == sh else None,
        final_equity=round(equity, 2),
        boot_p50=round(float(np.median(boot)) * 100, 3) if boot else None,
        boot_p05=round(float(np.percentile(boot, 5)) * 100, 3) if boot else None,
        random_p50=round(float(np.median(rand)) * 100, 3) if rand else None,
        beat_random=(cagr_v > float(np.median(rand))) if rand and cagr_v == cagr_v else None,
        verdict=verdict,
        phi=phi.nguon,
        n_wf=len(params),
        entry_hour_utc=entry_hour_utc,
        sma_win=sma_win,
        sl_pts=sl_pts,
        tp_pts=tp_pts,
    )


def v1_d1_rule(d1, phi_sym, rule, sl_pts, tp_pts):
    phi = load_phi(phi_sym)
    if phi is None:
        return dict(verdict="CHUA_DO")
    d1 = d1.copy()
    d1["sma20"] = d1.close.rolling(20).mean()
    d1["sma50"] = d1.close.rolling(50).mean()
    times = d1.index
    hold_cap = 30

    def signal(i):
        row = d1.iloc[i]
        if rule == "prior_bull":
            return 1 if row.close > row.open else -1
        if rule == "close_gt_sma20":
            return 0 if pd.isna(row.sma20) else (1 if row.close > row.sma20 else -1)
        if rule == "close_gt_sma50":
            return 0 if pd.isna(row.sma50) else (1 if row.close > row.sma50 else -1)
        if rule == "close_gt_prior":
            return 1 if i > 0 and row.close > d1.iloc[i - 1].close else (-1 if i > 0 else 0)
        return 0

    q_starts = pd.date_range(
        start=max(pd.Timestamp("2009-01-01"), times.min() + pd.DateOffset(years=1)),
        end=times.max(),
        freq="QS",
    )

    def run_train(i0, i1, slm, tpm):
        e = 10000.0
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
            sp, sw, _ = xm_cost_price(phi, max(hold, 0), sig, gia_tham=entry)
            net = gross - sp + sw
            risk = abs(entry - sl)
            vol = (0.01 * e) / (risk * phi.contract) if risk > 0 else 0
            e = max(e + net * phi.contract * vol, 0)
            last = exit_i + 1
        years = max((times[min(i1 - 1, len(times) - 1)] - times[i0]).days / 365.25, 1e-9)
        return (e / 10000.0) ** (1 / years) - 1 if e > 0 else -1

    equity = 10000.0
    oos = []
    eq_pts = []
    last_exit_i = 0
    n_wf = 0
    for qs in q_starts:
        i0 = int(d1.index.searchsorted(qs - pd.DateOffset(months=12)))
        i1 = int(d1.index.searchsorted(qs))
        j0 = int(d1.index.searchsorted(qs))
        j1 = int(d1.index.searchsorted(min(qs + pd.DateOffset(months=3), times.max())))
        if i1 - i0 < 40 or j1 - j0 < 3:
            continue
        best = None
        for slm in (0.75, 1.0, 1.25):
            for tpm in (0.75, 1.0, 1.25, 1.5):
                sc = run_train(i0, i1, slm, tpm)
                if best is None or sc > best[0]:
                    best = (sc, slm, tpm)
        _, slm, tpm = best
        n_wf += 1
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
            sp, sw, _ = xm_cost_price(phi, max(hold, 0), sig, gia_tham=entry)
            net = gross - sp + sw
            risk = abs(entry - sl)
            vol = (0.01 * equity) / (risk * phi.contract) if risk > 0 else 0
            pnl = net * phi.contract * vol
            equity = max(equity + pnl, 0)
            oos.append(pnl)
            eq_pts.append((times[exit_i], equity))
            last_exit_i = exit_i + 1

    if not oos:
        return dict(verdict="KHONG_OOS", rule=rule)
    eq = pd.Series({t: e for t, e in eq_pts}).sort_index()
    eq = pd.concat([pd.Series({eq.index[0] - pd.Timedelta(days=1): 10000.0}), eq])
    years = (eq.index[-1] - eq.index[0]).days / 365.25
    cagr_v = cagr(eq, years)
    dd = max_dd(eq)
    pnls = np.array(oos)
    sh = sharpe_trades(pnls, years)
    rng = np.random.default_rng(42)
    boot = [(lambda s: (max(10000 + sum(s), 0) / 10000) ** (1 / years) - 1)(rng.choice(pnls, size=len(pnls), replace=True)) for _ in range(500)]
    boot = [b for b in boot if b == b]
    rng2 = np.random.default_rng(7)
    rand = []
    for _ in range(200):
        e = 10000.0
        idxs = rng2.choice(range(60, len(d1) - 2), size=min(len(oos), 400), replace=False)
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
            sp, sw, _ = xm_cost_price(phi, max(hold, 0), sig, gia_tham=entry)
            net = gross - sp + sw
            vol = (0.01 * e) / (sl_pts * phi.contract)
            e = max(e + net * phi.contract * vol, 0)
        if e > 0 and years > 0:
            rand.append((e / 10000.0) ** (1 / years) - 1)
    verdict = "PASS" if (dd == dd and dd < 0.80 and cagr_v == cagr_v and cagr_v > 0.10) else "REJECT"
    return dict(
        rule=rule,
        n_oos=len(oos),
        years=round(years, 3),
        trades_per_yr=round(len(oos) / years, 2) if years else None,
        cagr_pct=round(cagr_v * 100, 3) if cagr_v == cagr_v else None,
        dd_pct=round(dd * 100, 3) if dd == dd else None,
        sharpe=round(sh, 3) if sh == sh else None,
        final_equity=round(equity, 2),
        boot_p50=round(float(np.median(boot)) * 100, 3) if boot else None,
        boot_p05=round(float(np.percentile(boot, 5)) * 100, 3) if boot else None,
        random_p50=round(float(np.median(rand)) * 100, 3) if rand else None,
        beat_random=(cagr_v > float(np.median(rand))) if rand and cagr_v == cagr_v else None,
        verdict=verdict,
        phi=phi.nguon,
        n_wf=n_wf,
        sl_pts=sl_pts,
        tp_pts=tp_pts,
    )


def main():
    results = []
    # preload
    nq_h1 = load_nq_h1()
    nq_d1 = load_nq_d1()
    xau = load_xau_h1()
    print("NQ H1", len(nq_h1), "D1", len(nq_d1), "XAU", len(xau))

    # --- 2244828 Kivenara 815: 18:00 broker, SL100 TP175 ---
    tr = sorted(load_trades(Path("/workspace/mql5_hist/2244828.csv")), key=lambda t: t.t_open)
    print("\n=== 2244828 Kivenara815 ===")
    h1rules = match_h1_rules_generic(tr, nq_h1, naive=False)
    d1rules = []
    for rule in ("prior_bull", "close_gt_prior", "close_gt_sma20", "close_gt_sma50"):
        ok, tot, m = match_d1_rule(tr, nq_d1, rule)
        d1rules.append(dict(rule=f"d1_{rule}", match=round(m, 4), ok=ok, tot=tot))
        print(f"  d1_{rule}: {ok}/{tot}={m:.1%}")
    print("  best H1", h1rules[:3])
    best = h1rules[0] if h1rules else None
    accepted = [r for r in h1rules + d1rules if r["match"] >= 0.60 and r.get("tot", 0) >= 100]
    v1 = None
    if best and best["match"] >= 0.60:
        # entry hour: broker 18:00 GMT+3 → 15:00 UTC
        v1 = v1_h1_tod_sma(nq_h1, "US100", entry_hour_utc=15, sma_win=50, sl_pts=100, tp_pts=175)
        print("  V1 H1", v1)
    d1_acc = [r for r in d1rules if r["match"] >= 0.60]
    v1d = None
    if d1_acc:
        v1d = v1_d1_rule(nq_d1, "US100", d1_acc[0]["rule"].replace("d1_", ""), 100, 175)
        print("  V1 D1", v1d)
    results.append(dict(id="2244828", ten="Kivenara 815m52ff", hang="don_le", match_h1=h1rules[:5], match_d1=d1rules, v1_h1=v1, v1_d1=v1d))

    # --- 2250577 Golden System 2 XAU ---
    tr = sorted(load_trades(Path("/workspace/mql5_hist/2250577.csv")), key=lambda t: t.t_open)
    print("\n=== 2250577 Golden System 2 ===")
    h1r = match_h1_rules_generic(tr, xau, naive=True)
    print("  best", h1r[:5])
    # SL/TP med from trades
    import statistics as st
    sl = st.median([abs(t.sl - t.price_open) for t in tr if t.sl])
    tp = st.median([abs(t.tp - t.price_open) for t in tr if t.tp])
    print("  SL/TP med", sl, tp)
    v1 = None
    if h1r and h1r[0]["match"] >= 0.60:
        # no fixed TOD — use D1 proxy with accepted rule
        # Build D1 from XAU for long V1
        xd1 = xau.resample("1D").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
        # map best mode to d1
        mode = h1r[0]["mode"]
        rule = "close_gt_sma50" if mode == "sma50" else ("close_gt_sma20" if mode == "sma20" else "prior_bull")
        ok, tot, m = match_d1_rule(tr, xd1, rule)
        print(f"  D1 proxy {rule}: {ok}/{tot}={m:.1%}")
        if m >= 0.60:
            v1 = v1_d1_rule(xd1, "XAUUSD", rule, float(sl), float(tp))
            print("  V1 D1", v1)
        else:
            # still try best H1-like via D1 sma50 even if match borderline
            v1 = dict(verdict="KHONG_CO_LUAT_D1", d1_match=round(m, 4), h1_best=h1r[0])
            # Try intraday V1 without fixed hour: signal every H1 bar close>sma — too many trades; skip
    results.append(dict(id="2250577", ten="Golden System 2", hang="don_le", match_h1=h1r[:5], sl=sl, tp=tp, v1=v1))

    # --- 2269966 BreakZone XAU ---
    tr = sorted(load_trades(Path("/workspace/mql5_hist/2269966.csv")), key=lambda t: t.t_open)
    print("\n=== 2269966 BreakZone ===")
    h1r = match_h1_rules_generic(tr, xau, naive=True)
    print("  best", h1r[:5])
    v1 = None
    if h1r and h1r[0]["match"] >= 0.60:
        xd1 = xau.resample("1D").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
        mode = h1r[0]["mode"]
        rule = "close_gt_sma50" if mode == "sma50" else ("close_gt_sma20" if mode == "sma20" else "prior_bull")
        ok, tot, m = match_d1_rule(tr, xd1, rule)
        print(f"  D1 {rule}: {m:.1%}")
        # ATR-based SL proxy: median |exit-entry|
        dist = st.median([abs(t.price_close - t.price_open) for t in tr])
        sl_p, tp_p = dist, dist * 1.5
        if m >= 0.60:
            v1 = v1_d1_rule(xd1, "XAUUSD", rule, float(sl_p), float(tp_p))
            print("  V1", v1)
        else:
            v1 = dict(verdict="KHONG_CO_LUAT_D1", d1_match=round(m, 4), h1_best=h1r[0], note="H1 match cao nhưng D1 proxy <60%; không SL cố định")
    results.append(dict(id="2269966", ten="BreakZone", hang="don_le", match_h1=h1r[:5], v1=v1))

    # --- 2245675 OnlyUJ USDJPY ---
    print("\n=== 2245675 OnlyUJ ===")
    try:
        uj = load_fx_h1("USDJPY")
        print("  USDJPY H1", len(uj), uj.index.min(), uj.index.max())
        tr = sorted(load_trades(Path("/workspace/mql5_hist/2245675.csv")), key=lambda t: t.t_open)
        h1r = match_h1_rules_generic(tr, uj, naive=True)
        print("  best", h1r[:5])
        v1 = None
        if h1r and h1r[0]["match"] >= 0.60:
            d1 = uj.resample("1D").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
            mode = h1r[0]["mode"]
            rule = "close_gt_sma50" if mode == "sma50" else ("close_gt_sma20" if mode == "sma20" else "prior_bull")
            ok, tot, m = match_d1_rule(tr, d1, rule)
            dist = st.median([abs(t.price_close - t.price_open) for t in tr])
            print(f"  D1 {rule}={m:.1%} dist_med={dist}")
            if m >= 0.55:  # slightly soft for V1 attempt if H1 strong
                v1 = v1_d1_rule(d1, "USDJPY", rule, float(dist), float(dist) * 1.5)
                v1["d1_match"] = round(m, 4)
                print("  V1", v1)
            else:
                v1 = dict(verdict="KHONG_CO_LUAT_D1", d1_match=round(m, 4), h1_best=h1r[0])
        results.append(dict(id="2245675", ten="OnlyUJ", hang="don_le", match_h1=h1r[:5], v1=v1))
    except Exception as e:
        print("  ERR", e)
        results.append(dict(id="2245675", ten="OnlyUJ", hang="don_le", error=str(e)))

    # --- 2337217 Top Cat S EURUSD ---
    print("\n=== 2337217 Top Cat S ===")
    try:
        eu = load_fx_h1("EURUSD")
        tr = sorted(load_trades(Path("/workspace/mql5_hist/2337217.csv")), key=lambda t: t.t_open)
        h1r = match_h1_rules_generic(tr, eu, naive=True)
        print("  best", h1r[:5], "buy%", round(100 * sum(t.chieu > 0 for t in tr) / len(tr), 1))
        v1 = None
        if h1r and h1r[0]["match"] >= 0.60:
            d1 = eu.resample("1D").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
            mode = h1r[0]["mode"]
            rule = "close_gt_sma50" if mode == "sma50" else ("close_gt_sma20" if mode == "sma20" else "prior_bull")
            ok, tot, m = match_d1_rule(tr, d1, rule)
            sl = st.median([abs(t.sl - t.price_open) for t in tr if t.sl] or [0.0002])
            tp = st.median([abs(t.tp - t.price_open) for t in tr if t.tp] or [0.0011])
            print(f"  D1 {rule}={m:.1%} SL={sl} TP={tp}")
            if m >= 0.55:
                v1 = v1_d1_rule(d1, "EURUSD", rule, float(sl), float(tp))
                v1["d1_match"] = round(m, 4)
                print("  V1", v1)
            else:
                v1 = dict(verdict="KHONG_CO_LUAT_D1", d1_match=round(m, 4), h1_best=h1r[0])
        results.append(dict(id="2337217", ten="Top Cat S", hang="pyramid", match_h1=h1r[:5], v1=v1))
    except Exception as e:
        print("  ERR", e)
        results.append(dict(id="2337217", ten="Top Cat S", hang="pyramid", error=str(e)))

    # --- 2392805 UZUNAMI88 XAU+GBPJPY ---
    print("\n=== 2392805 UZUNAMI88 ===")
    tr = sorted(load_trades(Path("/workspace/mql5_hist/2392805.csv")), key=lambda t: t.t_open)
    xtr = [t for t in tr if t.symbol == "XAUUSD"]
    jtr = [t for t in tr if t.symbol == "GBPJPY"]
    hx = match_h1_rules_generic(xtr, xau, naive=True) if xtr else []
    print("  XAU best", hx[:3] if hx else None, "n", len(xtr))
    v1x = v1j = None
    try:
        gj = load_fx_h1("GBPJPY")
        hj = match_h1_rules_generic(jtr, gj, naive=True) if jtr else []
        print("  GBPJPY best", hj[:3] if hj else None, "n", len(jtr))
    except Exception as e:
        hj = []
        print("  GBPJPY data ERR", e)
    if hx and hx[0]["match"] >= 0.60:
        xd1 = xau.resample("1D").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
        mode = hx[0]["mode"]
        rule = "close_gt_sma50" if mode == "sma50" else ("close_gt_sma20" if mode == "sma20" else "prior_bull")
        ok, tot, m = match_d1_rule(xtr, xd1, rule)
        sl = st.median([abs(t.sl - t.price_open) for t in xtr if t.sl])
        tp = st.median([abs(t.tp - t.price_open) for t in xtr if t.tp] or [sl * 1.5])
        print(f"  XAU D1 {rule}={m:.1%}")
        if m >= 0.55:
            v1x = v1_d1_rule(xd1, "XAUUSD", rule, float(sl), float(tp))
            v1x["d1_match"] = round(m, 4)
            print("  V1 XAU", v1x)
    if hj and hj[0]["match"] >= 0.60:
        d1 = gj.resample("1D").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
        mode = hj[0]["mode"]
        rule = "close_gt_sma50" if mode == "sma50" else ("close_gt_sma20" if mode == "sma20" else "prior_bull")
        ok, tot, m = match_d1_rule(jtr, d1, rule)
        sl = st.median([abs(t.sl - t.price_open) for t in jtr if t.sl])
        tp = st.median([abs(t.tp - t.price_open) for t in jtr if t.tp] or [sl * 1.5])
        print(f"  GBPJPY D1 {rule}={m:.1%}")
        if m >= 0.55:
            v1j = v1_d1_rule(d1, "GBPJPY", rule, float(sl), float(tp))
            v1j["d1_match"] = round(m, 4)
            print("  V1 GBPJPY", v1j)
    results.append(dict(id="2392805", ten="UZUNAMI88", hang="pyramid", match_xau=hx[:5], match_gbpjpy=hj[:5] if hj else [], v1_xau=v1x, v1_gbpjpy=v1j))

    # prior results shortcuts
    prior = json.loads((OUT / "v1_dich_nguoc_ket_qua.json").read_text())
    results.append(dict(
        id="2229059", ten="Kivenara 8315 (đã làm)", hang="don_le", skip=True,
        v1=prior.get("v1", {}).get("kivenara_h1") or prior.get("v1", {}).get("kivenara_d1"),
    ))
    results.append(dict(
        id="2153920", ten="MCA100 (đã làm)", hang="pyramid", skip=True,
        v1=prior.get("v1", {}).get("mca100"),
    ))
    results.append(dict(
        id="2344620", ten="Friday Pro (đã làm)", hang="pyramid", skip=True,
        note="buy≈100% ≈ B&H; B&H sau swap CAGR 3.8–5.8%",
    ))

    # Happy Gold e/c 1.094 — below 1.2 threshold: note only
    results.append(dict(id="1862128", ten="EA Happy Gold", hang="don_le", skip=True, note="e/c=1.094<1.2 — không chạy RE/V1 theo ngưỡng"))

    outp = OUT / "v1_donle_ket_qua.json"
    outp.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("\nWROTE", outp)


if __name__ == "__main__":
    main()
