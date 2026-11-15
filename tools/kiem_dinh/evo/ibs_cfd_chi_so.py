#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiem dinh IBS mean-reversion tren CFD chi so My (US500, US100), khung ngay.

Tai su dung khung tu ibs_cap_cheo.py (tin hieu close t, khop open t+1, SMA200,
dich vong vi the, tieu chi passed). Doi phi sang mo hinh CFD:
  - Spread diem chi so (US500 0.6 pt, US100 1.5 pt; chay them 2x).
  - Phi qua dem: long 7.5%/nam, short 2.5%/nam (luon la chi phi), /365 moi dem;
    Thu Sau -> Thu Hai = 3 dem lich.
SPY/QQQ dung OHLC gia (khong dieu chinh co tuc) de gan voi CFD chi so gia;
spread ETF = spread chi so / ty le quy mo trung vi (GSPC/SPY, NDX/QQQ).

Khong mo tk, khong dat lenh that. Khong ghi du lieu gia len git.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from ibs_cap_cheo import (  # noqa: E402
    N_RAND,
    RNG_SEED,
    Trade,
    _clean_ohlc,
    calendar_nights,
    ibs_sma,
    metrics,
    nights_array,
)

YAHOO_DIR = Path("/workspace/thong_ke_ma50/ibs_work/yahoo")
SPLIT_OOS = "2015-01-01"
SPLIT_2020 = "2020-01-01"
FIN_LONG = 0.075
FIN_SHORT = 0.025

# name, file, cfd, spread_pts (on the index), index_key for scale
SERIES = [
    dict(name="US500_GSPC", file="gspc_yahoo_daily.csv", yahoo="^GSPC", cfd="US500", spread=0.6, scale_vs=None),
    dict(name="US500_SPY", file="spy_yahoo_daily.csv", yahoo="SPY", cfd="US500", spread=0.6, scale_vs="US500_GSPC"),
    dict(name="US100_NDX", file="ndx_yahoo_daily.csv", yahoo="^NDX", cfd="US100", spread=1.5, scale_vs=None),
    dict(name="US100_QQQ", file="qqq_yahoo_daily.csv", yahoo="QQQ", cfd="US100", spread=1.5, scale_vs="US100_NDX"),
]

VARIANTS = [
    ("L_ibs02_1bar", "long", False, "1bar"),
    ("L_ibs02_sma200_1bar", "long", True, "1bar"),
    ("L_ibs02_ex08_max4", "long", False, "ibs_max4"),
    ("L_ibs02_sma200_ex08_max4", "long", True, "ibs_max4"),
    ("S_ibs08_sma200_1bar", "short", True, "1bar"),
    ("S_ibs08_sma200_ex02_max4", "short", True, "ibs_max4"),
]

def load_daily(fname: str) -> pd.DataFrame:
    p = YAHOO_DIR / fname
    df = pd.read_csv(p, parse_dates=["date"])
    df = df.set_index("date")
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    df = _clean_ohlc(df)
    return df[["open", "high", "low", "close"]]


def scale_factor(etf: pd.DataFrame, idx: pd.DataFrame) -> float:
    both = pd.concat([etf["close"].rename("e"), idx["close"].rename("i")], axis=1, join="inner").dropna()
    ratio = (both["i"] / both["e"]).replace([np.inf, -np.inf], np.nan).dropna()
    return float(ratio.median())


def run_variant_cfd(df, spread_pts, use_fin, side_mode, use_trend, exit_mode):
    ibs = df["ibs"].values
    close = df["close"].values
    sma = df["sma200"].values
    opn = df["open"].values
    times = df.index
    n = len(df)
    nights = nights_array(times)

    pos = np.zeros(n, dtype=float)
    costs = np.zeros(n, dtype=float)
    trades: list[Trade] = []

    t = 199
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
            long_sig = bool(long_sig and (close[t] > sma[t]))
            short_sig = bool(short_sig and (close[t] < sma[t]))
        side = 0
        if side_mode == "long" and long_sig:
            side = 1
        elif side_mode == "short" and short_sig:
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
        nt = calendar_nights(times[entry_i], times[exit_i])
        spread_frac = spread_pts / entry_px
        fin_rate = FIN_LONG if side == 1 else FIN_SHORT
        fin = (fin_rate * nt / 365.0) if use_fin else 0.0
        ret = side * (exit_px - entry_px) / entry_px - spread_frac - fin
        trades.append(Trade(side, entry_i, exit_i, ret))
        pos[entry_i:exit_i] = side
        costs[entry_i] += spread_frac / 2.0
        costs[exit_i - 1] += spread_frac / 2.0
        if use_fin:
            for i in range(entry_i, exit_i):
                if nights[i] > 0:
                    costs[i] += fin_rate * float(nights[i]) / 365.0
        t = exit_i

    r_open = np.zeros(n)
    r_open[:-1] = opn[1:] / opn[:-1] - 1.0
    pnl = pos * r_open - costs
    pnl[-1] = 0.0
    return pos, pnl, trades, nights, r_open


def costs_on_pos_cfd(pos, r_open, nights, opn, spread_pts, use_fin):
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
        add = (spread_pts / 2.0) / src_px
        add = np.where(np.isfinite(add), add, 0.0)
        np.add.at(costs, dest, add)
    if open_new.any():
        add = (spread_pts / 2.0) / px
        add = np.where(open_new & np.isfinite(add), add, 0.0)
        costs += add
    if use_fin:
        rate = np.where(pos > 0, FIN_LONG, np.where(pos < 0, FIN_SHORT, 0.0))
        fin = np.zeros(n, dtype=float)
        m = (pos != 0) & (nights > 0)
        fin[:-1] = np.where(m[:-1], rate[:-1] * nights[:-1] / 365.0, 0.0)
        costs += fin
    pnl = pos * r_open - costs
    pnl[-1] = 0.0
    return pnl


def rand_sharpe(pos, r_open, nights, opn, spread_pts, use_fin, mask, sharpe0, ann, rng, n_rand=N_RAND):
    idx = np.flatnonzero(mask)
    m = len(idx)
    if m < 80 or np.all(pos[idx] == pos[idx][0]):
        return np.nan, np.nan
    pos_m = pos[idx]
    null = np.empty(n_rand)
    for j in range(n_rand):
        k = int(rng.integers(20, m - 20))
        pos_full = pos.copy()
        pos_full[idx] = np.roll(pos_m, k)
        pnl_s = costs_on_pos_cfd(pos_full, r_open, nights, opn, spread_pts, use_fin)
        q = pnl_s[idx]
        sd = q.std(ddof=0)
        null[j] = q.mean() / sd * np.sqrt(ann) if sd > 0 else 0.0
    p = (1.0 + np.sum(null >= sharpe0)) / (n_rand + 1.0)
    return float(p), float(null.mean())


def ann_factor(times) -> float:
    if len(times) < 2:
        return 252.0
    years = max((times[-1] - times[0]).days / 365.25, 1e-9)
    return len(times) / years


def verdict_period(row, prefix: str) -> str:
    tr = row.get(f"{prefix}_trades") or 0
    sh = row.get(f"{prefix}_sharpe")
    pf = row.get(f"{prefix}_pf")
    avg = row.get(f"{prefix}_avg")
    p = row.get(f"{prefix}_p_rand")
    rsh = row.get(f"{prefix}_rand_sharpe")

    def fin(x):
        return x is not None and np.isfinite(x)

    if tr < 15 or not fin(sh) or not fin(pf):
        return "khong edge"
    econ = fin(avg) and avg > 0 and pf >= 1.20 and sh >= 0.30
    vs_base = fin(p) and p <= 0.05 and (not fin(rsh) or sh > rsh)
    if tr >= 30 and econ and vs_base:
        return "passed"
    weak_plus = (
        tr >= 30 and fin(avg) and avg > 0 and pf > 1.0 and sh > 0 and fin(rsh) and sh > rsh
    )
    if weak_plus:
        return "ung vien yeu"
    return "khong edge"


def eval_one(df, meta, variant, spread_pts, use_fin, cost_name, rng):
    name, side, trend, exit_mode = variant
    pos, pnl, trades, nights, r_open = run_variant_cfd(
        df, spread_pts, use_fin, side, trend, exit_mode
    )
    times = df.index
    opn = df["open"].values
    ann = ann_factor(times)
    masks = {
        "IS": times < pd.Timestamp(SPLIT_OOS),
        "OOS": times >= pd.Timestamp(SPLIT_OOS),
        "Y2020": times >= pd.Timestamp(SPLIT_2020),
    }
    row = dict(
        series=meta["name"],
        yahoo=meta["yahoo"],
        cfd=meta["cfd"],
        variant=name,
        side=side,
        trend=trend,
        exit=exit_mode,
        cost=cost_name,
        spread_pts=float(spread_pts),
        use_fin=bool(use_fin),
        scale=float(meta["scale"]),
        start=str(times[0].date()),
        end=str(times[-1].date()),
        n_bars=int(len(df)),
    )
    for per, mask in masks.items():
        tr = [t for t in trades if mask[t.entry_i]]
        mt = metrics(pnl[mask], tr, times[mask], ann)
        for k, v in mt.items():
            row[f"{per}_{k}"] = v
        p, mu = rand_sharpe(
            pos, r_open, nights, opn, spread_pts, use_fin, mask, mt["sharpe"], ann, rng
        )
        row[f"{per}_p_rand"] = p
        row[f"{per}_rand_sharpe"] = mu
        row[f"{per}_verdict"] = verdict_period(row, per)
    return row


def load_all():
    raw = {}
    for s in SERIES:
        raw[s["name"]] = ibs_sma(load_daily(s["file"]))
    out = []
    for s in SERIES:
        meta = dict(s)
        if s["scale_vs"]:
            sc = scale_factor(raw[s["name"]], raw[s["scale_vs"]])
            meta["scale"] = sc
            meta["spread_used_base"] = s["spread"] / sc
        else:
            meta["scale"] = 1.0
            meta["spread_used_base"] = s["spread"]
        out.append((meta, raw[s["name"]]))
        print(f"loaded {meta['name']} {meta['yahoo']} n={len(raw[s['name']])} "
              f"{raw[s['name']].index[0].date()}..{raw[s['name']].index[-1].date()} "
              f"scale={meta['scale']:.3f} spread_base={meta['spread_used_base']:.4f}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="/tmp/ibs_cfd_out")
    ap.add_argument("--yahoo-dir", default="")
    args = ap.parse_args()
    if args.yahoo_dir:
        import sys as _s
        _s.modules[__name__].YAHOO_DIR = Path(args.yahoo_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    series = load_all()
    rng_master = np.random.default_rng(RNG_SEED)
    rows = []
    for meta, df in series:
        for cname, mult, use_fin in [
            ("spread1x_fin", 1.0, True),
            ("spread2x_fin", 2.0, True),
            ("spread1x_nofin", 1.0, False),
        ]:
            spread_pts = meta["spread_used_base"] * mult
            for var in VARIANTS:
                rng = np.random.default_rng(rng_master.integers(0, 2**31 - 1))
                row = eval_one(df, meta, var, spread_pts, use_fin, cname, rng)
                rows.append(row)
                if cname == "spread1x_fin":
                    print(
                        f"  {meta['name']:12} {var[0]:28} {cname:16} "
                        f"OOS n={row['OOS_trades']:4} win={row['OOS_win'] if row['OOS_win']==row['OOS_win'] else float('nan'):.2f} "
                        f"avg={row['OOS_avg']:.3f} PF={row['OOS_pf']:.2f} sh={row['OOS_sharpe']:.2f} "
                        f"cagr={row['OOS_cagr']:.2f} p={row['OOS_p_rand']:.3f} {row['OOS_verdict']}"
                    )
    res = pd.DataFrame(rows)
    res.to_csv(out / "ibs_cfd_chi_so_results.csv", index=False)
    (out / "ibs_cfd_meta.json").write_text(
        json.dumps([m for m, _ in series], indent=2, default=str), encoding="utf-8"
    )
    print("wrote", out / "ibs_cfd_chi_so_results.csv", "rows", len(res))
    return res


if __name__ == "__main__":
    main()
