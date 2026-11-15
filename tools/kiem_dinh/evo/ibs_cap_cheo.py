#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiem dinh IBS mean-reversion tren cap cheo forex.

Quy tac: long khi IBS=(C-L)/(H-L)<0.2; short doi xung IBS>0.8.
Bien the: loc xu huong C>SMA200 (long) / C<SMA200 (short);
thoat sau 1 nen, hoac khi IBS nguoc chieu (long: IBS>0.8, short: IBS<0.2), toi da 4 nen.

Chuan:
  - Tin hieu tai close nen t, khop open that nen t+1, thoat tai open.
  - Phi: spread co dinh (pip) + swap uoc luong (pip/dem lich, luon tinh la chi phi).
  - IS/OOS tach theo ngay (mac dinh 2019-01-01; H4 AUD* tach 2022-01-01 vi H1 that chi tu 2018-04).
  - Doi chung: dich vong chuoi vi the trong tung giai doan (cung so lenh / thoi gian giu).
  - Sharpe va %/nam tinh tren chuoi loi nhuan lich (ke ca phien khong co lenh).
  - "passed" chi khi OOS don lap vuot baseline (p<=0.05, PF>1, Sharpe>0, >=30 lenh).

Khong mo tk, khong dat lenh that. Khong ghi du lieu gia.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

DATA_YAHOO = Path("/workspace/thong_ke_ma50")
DATA_H1 = Path("/workspace/brain2/data")

PAIRS = ("AUDCAD", "AUDNZD", "EURCAD", "CADJPY")
PIP = {"AUDCAD": 1e-4, "AUDNZD": 1e-4, "EURCAD": 1e-4, "CADJPY": 0.01}
# Spread typ. 1.5-3 pip (retail). AUDNZD rong hon.
SPREAD_PIPS = {"AUDCAD": 2.0, "AUDNZD": 3.0, "EURCAD": 2.5, "CADJPY": 2.0}
# Swap tho: luon tinh la chi phi, ~0.5 pip/dem (khong lay swap co loi).
SWAP_PIPS = {"AUDCAD": 0.5, "AUDNZD": 0.6, "EURCAD": 0.5, "CADJPY": 0.5}

# H1 that (khong phai daily dong moc 00:00) bat dau tu:
H1_TRUE_FROM = {
    "AUDCAD": "2018-04-14",
    "AUDNZD": "2018-04-14",
    "EURCAD": "2007-05-11",
}

N_RAND = 1000
RNG_SEED = 20261115

VARIANTS = [
    # name, side, trend, exit_mode
    ("L_ibs02_1bar", "long", False, "1bar"),
    ("L_ibs02_sma200_1bar", "long", True, "1bar"),
    ("L_ibs02_ex08_max4", "long", False, "ibs_max4"),
    ("L_ibs02_sma200_ex08_max4", "long", True, "ibs_max4"),
    ("S_ibs08_1bar", "short", False, "1bar"),
    ("S_ibs08_sma200_1bar", "short", True, "1bar"),
    ("S_ibs08_sma200_ex02_max4", "short", True, "ibs_max4"),
    ("LS_sma200_1bar", "both", True, "1bar"),
    ("LS_sma200_ex_max4", "both", True, "ibs_max4"),
]


def _clean_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in ("open", "high", "low", "close"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["open", "high", "low", "close"])
    df = df[(df["high"] >= df["low"]) & (df["high"] > 0) & (df["low"] > 0)]
    mx = df[["open", "close"]].max(axis=1)
    mn = df[["open", "close"]].min(axis=1)
    df = df[(df["high"] + 1e-12 >= mx) & (df["low"] - 1e-12 <= mn)]
    df = df[df["high"] > df["low"]]
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="last")]
    return df


def load_yahoo_daily(pair: str) -> pd.DataFrame:
    p = DATA_YAHOO / f"{pair.lower()}_yahoo_daily.csv"
    df = pd.read_csv(p, parse_dates=["date"])
    df = df.set_index("date")
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    df = _clean_ohlc(df)
    # Yahoo FX hay co nen Chu Nhat (mo tuan) va thieu Thu Sau. Bo thu 7 neu co.
    df = df[df.index.day_of_week != 5]
    return df[["open", "high", "low", "close"]]


def load_h4(pair: str) -> pd.DataFrame:
    src = DATA_H1 / f"{pair}_H1.parquet"
    raw = pd.read_parquet(src)
    raw["time"] = pd.to_datetime(raw["time"]).dt.tz_localize(None)
    start = pd.Timestamp(H1_TRUE_FROM[pair])
    raw = raw[raw["time"] >= start].copy()
    raw = raw.set_index("time").sort_index()
    raw = _clean_ohlc(raw)
    # Dem so nen H1 trong moi hop H4 de bo hop qua thua.
    tmp = raw[["open", "high", "low", "close"]].copy()
    tmp["_n"] = 1
    h4 = tmp.resample("4h", label="left", closed="left").agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        n=(" _n".strip(), "sum") if False else ("_n", "sum"),
    )
    h4 = h4.dropna(subset=["open", "high", "low", "close"])
    h4 = h4[h4["n"] >= 2]
    h4 = _clean_ohlc(h4)
    return h4[["open", "high", "low", "close"]]


def ibs_sma(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    hl = out["high"] - out["low"]
    out["ibs"] = np.where(hl > 0, (out["close"] - out["low"]) / hl, np.nan)
    out["sma200"] = out["close"].rolling(200, min_periods=200).mean()
    return out


def calendar_nights(t0, t1) -> int:
    d0 = pd.Timestamp(t0).normalize()
    d1 = pd.Timestamp(t1).normalize()
    return max(0, int((d1 - d0).days))


@dataclass
class Trade:
    side: int
    entry_i: int
    exit_i: int
    ret: float


def run_variant(df: pd.DataFrame, pair: str, side_mode: str, use_trend: bool, exit_mode: str):
    ibs = df["ibs"].values
    close = df["close"].values
    sma = df["sma200"].values
    opn = df["open"].values
    times = df.index
    n = len(df)
    pip = PIP[pair]
    spread = SPREAD_PIPS[pair] * pip
    swap = SWAP_PIPS[pair] * pip

    pos = np.zeros(n, dtype=float)  # pos[i] giu tu open[i] -> open[i+1]
    costs = np.zeros(n, dtype=float)
    trades: list[Trade] = []

    t = 199  # cho SMA200 kip am
    while t < n - 2:
        if not np.isfinite(ibs[t]):
            t += 1
            continue
        long_sig = ibs[t] < 0.2
        short_sig = ibs[t] > 0.8
        if use_trend:
            if not np.isfinite(sma[t]):
                t += 1
                continue
            long_sig = long_sig and (close[t] > sma[t])
            short_sig = short_sig and (close[t] < sma[t])
        side = 0
        if side_mode in ("long", "both") and long_sig:
            side = 1
        elif side_mode in ("short", "both") and short_sig:
            side = -1
        if side == 0:
            t += 1
            continue

        entry_i = t + 1
        if entry_i >= n - 1:
            break
        exit_i = None
        for k in range(entry_i, n - 1):
            held = k - entry_i + 1
            if exit_mode == "1bar":
                exit_i = k + 1
                break
            opp = (side == 1 and np.isfinite(ibs[k]) and ibs[k] > 0.8) or (
                side == -1 and np.isfinite(ibs[k]) and ibs[k] < 0.2
            )
            if opp or held >= 4:
                exit_i = k + 1
                break
        if exit_i is None or exit_i >= n:
            break

        entry_px = opn[entry_i]
        exit_px = opn[exit_i]
        if not np.isfinite(entry_px) or not np.isfinite(exit_px) or entry_px <= 0:
            t += 1
            continue
        nights = calendar_nights(times[entry_i], times[exit_i])
        ret = side * (exit_px - entry_px) / entry_px - spread / entry_px - (swap * nights) / entry_px
        trades.append(Trade(side, entry_i, exit_i, ret))
        pos[entry_i:exit_i] = side
        # phi tra tai nen vao (spread + swap se phan bo bang cash-drag tren ret cuoi)
        # de MTM dung: spread 1/2 vao + 1/2 ra; swap tren moi dem vuot qua moc 00:00
        costs[entry_i] += (spread / 2) / entry_px
        costs[exit_i - 1] += (spread / 2) / entry_px
        # swap: gan vao cac nen ma khoang open[i] -> open[i+1] di qua nua dem
        for i in range(entry_i, exit_i):
            if i + 1 < n and calendar_nights(times[i], times[i + 1]) > 0:
                nt = calendar_nights(times[i], times[i + 1])
                costs[i] += (swap * nt) / entry_px
        t = exit_i

    # MTM open-to-open
    r_open = np.zeros(n)
    r_open[:-1] = (opn[1:] / opn[:-1] - 1.0)
    # nen cuoi khong co open sau
    pnl = pos * r_open - costs
    pnl[-1] = 0.0
    return pos, pnl, trades


def metrics(pnl: np.ndarray, trades: list[Trade], times, ann_bars: float):
    pnl = np.asarray(pnl, float)
    if len(pnl) < 10 or np.nanstd(pnl) == 0:
        return dict(trades=0, win=np.nan, avg=np.nan, pf=np.nan, sharpe=0.0, cagr=0.0, maxdd=0.0, tot=0.0)
    rets = np.array([tr.ret for tr in trades], float)
    ntr = len(rets)
    win = 100.0 * np.mean(rets > 0) if ntr else np.nan
    avg = 100.0 * np.mean(rets) if ntr else np.nan
    gp = rets[rets > 0].sum()
    gl = -rets[rets < 0].sum()
    pf = (gp / gl) if gl > 1e-15 else (np.inf if gp > 0 else np.nan)
    sd = pnl.std(ddof=0)
    sharpe = float(pnl.mean() / sd * np.sqrt(ann_bars)) if sd > 0 else 0.0
    eq = np.cumprod(1.0 + pnl)
    tot = 100.0 * (eq[-1] - 1.0) if eq[-1] > 0 else -100.0
    if len(times) >= 2:
        years = max((times[-1] - times[0]).days / 365.25, 1e-6)
    else:
        years = len(pnl) / ann_bars
    if eq[-1] > 0 and years > 0:
        cagr = 100.0 * (eq[-1] ** (1.0 / years) - 1.0)
    else:
        cagr = -100.0
    peak = np.maximum.accumulate(eq)
    maxdd = 100.0 * np.max(1.0 - eq / np.maximum(peak, 1e-12))
    return dict(trades=ntr, win=win, avg=avg, pf=pf, sharpe=sharpe, cagr=cagr, maxdd=maxdd, tot=tot)


def nights_array(times):
    n = len(times)
    out = np.zeros(n, dtype=np.int16)
    d = pd.DatetimeIndex(times).normalize()
    out[:-1] = np.maximum((d[1:] - d[:-1]).days, 0)
    return out


def _costs_on_pos(pos, pnl_raw_open, pair, nights, opn):
    """Phi vector hoa: 1/2 spread khi mo/dong, swap moi dem lich dang giu."""
    pip = PIP[pair]
    spread = SPREAD_PIPS[pair] * pip
    swap = SWAP_PIPS[pair] * pip
    n = len(pos)
    pos = np.asarray(pos, float)
    px = np.where(opn > 0, opn, np.nan)
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
        add = (spread / 2.0) / src_px
        add = np.where(np.isfinite(add), add, 0.0)
        np.add.at(costs, dest, add)
    if open_new.any():
        add = (spread / 2.0) / px
        add = np.where(open_new & np.isfinite(add), add, 0.0)
        costs += add
    swap_add = np.zeros(n, dtype=float)
    m = (pos != 0) & (nights > 0) & np.isfinite(px) & (px > 0)
    swap_add[:-1] = np.where(m[:-1], (swap * nights[:-1]) / px[:-1], 0.0)
    costs += swap_add
    pnl = pos * pnl_raw_open - costs
    pnl[-1] = 0.0
    return pos, pnl


def rand_sharpe(pos, pnl_raw_open, pair, nights, opn, mask, sharpe0, ann, rng, n_rand=N_RAND):
    idx = np.flatnonzero(mask)
    m = len(idx)
    if m < 80 or np.all(pos[idx] == pos[idx][0]):
        return np.nan, np.nan
    null = np.empty(n_rand)
    pos_m = pos[idx]
    for j in range(n_rand):
        k = int(rng.integers(20, m - 20))
        pos_full = pos.copy()
        pos_full[idx] = np.roll(pos_m, k)
        _, pnl_s = _costs_on_pos(pos_full, pnl_raw_open, pair, nights, opn)
        q = pnl_s[idx]
        sd = q.std(ddof=0)
        null[j] = q.mean() / sd * np.sqrt(ann) if sd > 0 else 0.0
    p = (1.0 + np.sum(null >= sharpe0)) / (n_rand + 1.0)
    return float(p), float(null.mean())


def ann_factor(times, tf: str) -> float:
    if len(times) < 2:
        return 252.0 if tf == "D1" else 1512.0
    years = max((times[-1] - times[0]).days / 365.25, 1e-9)
    return len(times) / years


def split_mask(times, split):
    split = pd.Timestamp(split)
    is_m = times < split
    oos_m = times >= split
    return is_m, oos_m


def eval_one(df, pair, tf, variant, split, rng):
    name, side, trend, exit_mode = variant
    pos, pnl, trades = run_variant(df, pair, side, trend, exit_mode)
    times = df.index
    opn = df["open"].values
    r_open = np.zeros(len(df))
    r_open[:-1] = df["open"].values[1:] / df["open"].values[:-1] - 1.0
    nights = nights_array(times)
    ann = ann_factor(times, tf)
    is_m, oos_m = split_mask(times, split)
    row = dict(
        pair=pair,
        tf=tf,
        variant=name,
        side=side,
        trend=trend,
        exit=exit_mode,
        split=str(pd.Timestamp(split).date()),
        start=str(times[0].date()),
        end=str(times[-1].date()),
        n_bars=int(len(df)),
        spread_pips=SPREAD_PIPS[pair],
        swap_pips=SWAP_PIPS[pair],
    )
    for per, mask in (("IS", is_m), ("OOS", oos_m)):
        # trades theo thoi diem vao
        tr = [t for t in trades if mask[t.entry_i]]
        mt = metrics(pnl[mask], tr, times[mask], ann)
        for k, v in mt.items():
            row[f"{per}_{k}"] = v
        p, mu = rand_sharpe(pos, r_open, pair, nights, opn, mask, mt["sharpe"], ann, rng)
        row[f"{per}_p_rand"] = p
        row[f"{per}_rand_sharpe"] = mu
    row["OOS_verdict"] = verdict(row)
    return row


def verdict(row) -> str:
    """passed chi khi OOS tu dung ve KINH TE va vs baseline.
    Sharpe ~0 / PF ~1.01 khong du, vi do nhay voi uoc luong spread/swap.
    """
    tr = row.get("OOS_trades") or 0
    sh = row.get("OOS_sharpe")
    pf = row.get("OOS_pf")
    avg = row.get("OOS_avg")
    p = row.get("OOS_p_rand")
    rsh = row.get("OOS_rand_sharpe")

    def fin(x):
        return x is not None and np.isfinite(x)

    if tr < 15 or not fin(sh) or not fin(pf):
        return "khong edge"
    econ = fin(avg) and avg > 0 and pf >= 1.2 and sh >= 0.30
    vs_base = fin(p) and p <= 0.05 and (not fin(rsh) or sh > rsh)
    if tr >= 30 and econ and vs_base:
        return "passed"
    # ung vien: co lai nho, tot hon ngau nhien, nhung chua du manh / chua chac kinh te
    weak_plus = (
        tr >= 30
        and fin(avg)
        and avg > 0
        and pf > 1.0
        and sh > 0
        and fin(rsh)
        and sh > rsh
    )
    if weak_plus:
        return "ung vien yeu"
    return "khong edge"


def fmt(x, nd=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    if isinstance(x, float) and abs(x) >= 1000:
        return f"{x:.0f}"
    return f"{x:.{nd}f}"


def load_series():
    series = []
    # Daily Yahoo, 4 cap, tach 2019
    for pair in PAIRS:
        df = ibs_sma(load_yahoo_daily(pair))
        series.append((pair, "D1", df, "2019-01-01", "Yahoo Finance daily (FX=X), da loc nen OHLC loi / range=0 / thu 7"))
    # H4
    for pair, split in (("EURCAD", "2019-01-01"), ("AUDCAD", "2022-01-01"), ("AUDNZD", "2022-01-01")):
        df = ibs_sma(load_h4(pair))
        series.append((pair, "H4", df, split, f"Resample 4h tu H1 tren box (true H1 tu {H1_TRUE_FROM[pair]})"))
    return series


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="/tmp/ibs_out")
    ap.add_argument("--yahoo-dir", default="")
    ap.add_argument("--h1-dir", default="")
    ap.add_argument("--n-rand", type=int, default=0)
    args = ap.parse_args()
    # Gan duong dan / N_RAND qua thuoc tinh module, tranh "global" trong main.
    import sys
    mod = sys.modules[__name__]
    if args.yahoo_dir:
        mod.DATA_YAHOO = Path(args.yahoo_dir)
    if args.h1_dir:
        mod.DATA_H1 = Path(args.h1_dir)
    if args.n_rand and args.n_rand > 0:
        mod.N_RAND = int(args.n_rand)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    rng_master = np.random.default_rng(RNG_SEED)
    rows = []
    meta = []
    for pair, tf, df, split, note in load_series():
        print(f"== {pair} {tf} bars={len(df)} {df.index[0].date()}..{df.index[-1].date()} split={split}")
        meta.append(
            dict(
                pair=pair,
                tf=tf,
                start=str(df.index[0]),
                end=str(df.index[-1]),
                n=int(len(df)),
                split=split,
                note=note,
            )
        )
        for var in VARIANTS:
            rng = np.random.default_rng(rng_master.integers(0, 2**31 - 1))
            row = eval_one(df, pair, tf, var, split, rng)
            rows.append(row)
            print(
                f"  {var[0]:28} OOS n={row['OOS_trades']:4} win={fmt(row['OOS_win'])} "
                f"avg={fmt(row['OOS_avg'],3)} PF={fmt(row['OOS_pf'])} sh={fmt(row['OOS_sharpe'])} "
                f"p={fmt(row['OOS_p_rand'],3)} vsRand={fmt(row['OOS_rand_sharpe'])} {row['OOS_verdict']}"
            )

    res = pd.DataFrame(rows)
    res.to_csv(out / "ibs_cap_cheo_results.csv", index=False)
    (out / "ibs_cap_cheo_meta.json").write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")
    print("wrote", out / "ibs_cap_cheo_results.csv")
    return res, meta


if __name__ == "__main__":
    main()
