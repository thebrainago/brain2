#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Do ben IBS long tren US100 (^NDX, QQQ) va US500 (^GSPC), khung ngay, phi CFD nhu ibs_cfd_chi_so.py.

1) Walk-forward rolling 5 nam train / 1 nam test
2) Luoi nguong IBS va thoat, Sharpe OOS 2015+
3) Tre khop: close / next open / mo cua +1 nen
4) Che do: VIX><20, tren/duoi SMA200, truoc/sau 2010
5) BH-FDR va deflated Sharpe

Khong mo tk, khong dat lenh that. Khong ghi chuoi gia len git.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

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
from ibs_cfd_chi_so import (  # noqa: E402
    FIN_LONG,
    YAHOO_DIR,
    costs_on_pos_cfd,
    load_daily,
    scale_factor,
)

def as_bool(x):
    return np.asarray(x, dtype=bool)

SPLIT_OOS = pd.Timestamp("2015-01-01")
SPLIT_2010 = pd.Timestamp("2010-01-01")
IBS_INS = (0.10, 0.15, 0.20, 0.25, 0.30)
# 1bar + IBS-exit x max_bars
EXITS = [("1bar", None, 1)] + [(f"ex{int(e*10):02d}_max{m}", e, m) for e in (0.7, 0.8, 0.9) for m in (2, 4, 6)]
# 10 exits * 5 ins = 50

CANDIDATES = [
    # name, ibs_in, exit_ibs, max_bars  (exit_ibs None => 1 bar)
    ("L_ibs02_1bar", 0.20, None, 1),
    ("L_ibs02_ex08_max4", 0.20, 0.80, 4),
]


def load_series():
    gspc = ibs_sma(load_daily("gspc_yahoo_daily.csv"))
    ndx = ibs_sma(load_daily("ndx_yahoo_daily.csv"))
    qqq = ibs_sma(load_daily("qqq_yahoo_daily.csv"))
    sc = scale_factor(qqq, ndx)
    out = [
        dict(name="US500_GSPC", yahoo="^GSPC", cfd="US500", df=gspc, spread=0.6),
        dict(name="US100_NDX", yahoo="^NDX", cfd="US100", df=ndx, spread=1.5),
        dict(name="US100_QQQ", yahoo="QQQ", cfd="US100", df=qqq, spread=1.5 / sc, scale=sc),
    ]
    vix = pd.read_csv(Path("/workspace/thong_ke_ma50/ibs_work/yahoo/vix_yahoo_daily.csv"), parse_dates=["date"])
    vix = vix.set_index("date")
    vix.index = pd.to_datetime(vix.index).tz_localize(None).normalize()
    vix = vix.rename(columns={"close": "vix"})[["vix"]]
    for s in out:
        s["df"] = s["df"].join(vix, how="left")
        print(f"loaded {s['name']} n={len(s['df'])} {s['df'].index[0].date()}..{s['df'].index[-1].date()} "
              f"spread={s['spread']:.4f} vix_ok={int(s['df']['vix'].notna().sum())}")
    return out


def run_long(df, spread_pts, ibs_in, exit_ibs, max_bars, entry_mode="next_open", use_trend=False, use_fin=True):
    """entry_mode: next_open | delay1 | close (tham chieu). Long only."""
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

    # px series used for MTM
    if entry_mode == "close":
        px = close.copy()
    else:
        px = opn.copy()

    t = 199
    while t < n - 3:
        if not np.isfinite(ibs[t]) or not (ibs[t] < ibs_in):
            t += 1
            continue
        if use_trend and (not np.isfinite(sma[t]) or not (close[t] > sma[t])):
            t += 1
            continue

        if entry_mode == "close":
            entry_i = t  # khop close nen tin hieu
            if entry_i >= n - 1:
                break
        elif entry_mode == "delay1":
            entry_i = t + 2
            if entry_i >= n - 1:
                break
        else:
            entry_i = t + 1
            if entry_i >= n - 1:
                break

        entry_px = px[entry_i]
        if not np.isfinite(entry_px) or entry_px <= 0:
            t += 1
            continue

        exit_i = None
        if entry_mode == "close":
            # 1bar: thoat close t+1; ibs-exit: kiem tra tu close entry (cung nen?) — chi sau 1 nen
            start_k = entry_i  # se tang held o close ke tiep
            # quy uoc: sau khi vao close t, nen dau tien de thoat la t+1
            for k in range(entry_i, n - 1):
                held = k - entry_i  # 0 tai ngay vao, chua thoat ngay
                if held <= 0:
                    continue
                if exit_ibs is None:
                    exit_i = k  # close k, held=1
                    break
                opp = np.isfinite(ibs[k]) and ibs[k] > exit_ibs
                if opp or held >= max_bars:
                    exit_i = k
                    break
        else:
            for k in range(entry_i, n - 1):
                held = k - entry_i + 1
                if exit_ibs is None:
                    exit_i = k + 1  # mo cua sau 1 nen
                    break
                opp = np.isfinite(ibs[k]) and ibs[k] > exit_ibs
                if opp or held >= max_bars:
                    exit_i = k + 1
                    break
        if exit_i is None or exit_i >= n:
            break
        exit_px = px[exit_i]
        if not np.isfinite(exit_px) or exit_px <= 0:
            t += 1
            continue
        nt = calendar_nights(times[entry_i], times[exit_i])
        spread_frac = spread_pts / entry_px
        fin = (FIN_LONG * nt / 365.0) if use_fin else 0.0
        ret = (exit_px - entry_px) / entry_px - spread_frac - fin
        trades.append(Trade(1, entry_i, exit_i, ret))
        # vi the: next_open/delay1 tu open entry -> open exit; close tu bar entry -> exit (dong)
        pos[entry_i:exit_i] = 1.0
        costs[entry_i] += spread_frac / 2.0
        if exit_i - 1 >= 0:
            costs[exit_i - 1] += spread_frac / 2.0
        if use_fin:
            for i in range(entry_i, exit_i):
                if nights[i] > 0:
                    costs[i] += FIN_LONG * float(nights[i]) / 365.0
        t = exit_i if entry_mode == "close" else exit_i

    r = np.zeros(n)
    r[:-1] = px[1:] / px[:-1] - 1.0
    pnl = pos * r - costs
    pnl[-1] = 0.0
    return pos, pnl, trades, nights, r, px


def ann_factor(times) -> float:
    if len(times) < 2:
        return 252.0
    years = max((times[-1] - times[0]).days / 365.25, 1e-9)
    return len(times) / years


def period_metrics(pnl, trades, times, mask, ann):
    mask = np.asarray(mask, dtype=bool)
    tr = [t for t in trades if mask[t.entry_i]]
    return metrics(pnl[mask], tr, times[mask], ann)


def rand_p(pos, r, nights, px, spread_pts, mask, sharpe0, ann, rng, n_rand=N_RAND, use_fin=True):
    idx = np.flatnonzero(mask)
    m = len(idx)
    if m < 80 or np.all(pos[idx] == pos[idx][0]):
        return np.nan, np.nan
    pos_m = pos[idx]
    null = np.empty(n_rand)
    for j in range(n_rand):
        k = int(rng.integers(20, m - 20))
        pf = pos.copy()
        pf[idx] = np.roll(pos_m, k)
        pnl_s = costs_on_pos_cfd(pf, r, nights, px, spread_pts, use_fin)
        q = pnl_s[idx]
        sd = q.std(ddof=0)
        null[j] = q.mean() / sd * np.sqrt(ann) if sd > 0 else 0.0
    p = (1.0 + np.sum(null >= sharpe0)) / (n_rand + 1.0)
    return float(p), float(null.mean())


def verdict(mt, p=np.nan, rsh=np.nan):
    tr, sh, pf, avg = mt["trades"], mt["sharpe"], mt["pf"], mt["avg"]
    def fin(x):
        return x is not None and np.isfinite(x)
    if tr < 15 or not fin(sh) or not fin(pf):
        return "khong edge"
    econ = fin(avg) and avg > 0 and pf >= 1.20 and sh >= 0.30
    vs = (not fin(p)) or (p <= 0.05 and (not fin(rsh) or sh > rsh))
    if tr >= 30 and econ and (not fin(p) or vs):
        # neu khong co p, khong cho passed
        if fin(p) and p <= 0.05:
            return "passed"
    if tr >= 30 and fin(avg) and avg > 0 and pf > 1.0 and sh > 0 and (not fin(rsh) or sh > rsh):
        return "ung vien yeu"
    return "khong edge"


def bh_fdr(pvals, q=0.05):
    p = np.asarray(pvals, float)
    ok = np.isfinite(p)
    m = int(ok.sum())
    if m == 0:
        return np.zeros(len(p), dtype=bool), np.nan
    order = np.argsort(np.where(ok, p, np.inf))
    thresh = np.nan
    passed = np.zeros(len(p), dtype=bool)
    for rank, i in enumerate(order, 1):
        if not ok[i]:
            break
        if p[i] <= q * rank / m:
            thresh = p[i]
        else:
            # still continue to find max k with p(k)<=q*k/m (BH is max such k)
            pass
    # standard BH: find largest k such that p(k) <= q*k/m
    ps = p[ok]
    ps_sorted = np.sort(ps)
    kmax = 0
    for k, pv in enumerate(ps_sorted, 1):
        if pv <= q * k / m:
            kmax = k
            thresh = pv
    if kmax:
        passed = ok & (p <= thresh)
    return passed, (float(thresh) if kmax else np.nan)


def deflated_sharpe(sr, t_obs, n_trials, skew=0.0, kurt=3.0):
    """Bailey & Lopez de Prado (2014). Tra ve DSR = PSR(E[max SR]), va SR0."""
    if not np.isfinite(sr) or t_obs <= 2 or n_trials < 1:
        return np.nan, np.nan
    g = 0.5772156649015329
    v = (1.0 - skew * sr + ((kurt - 1.0) / 4.0) * sr ** 2) / (t_obs - 1)
    sr_std = float(np.sqrt(max(v, 1e-18)))
    if n_trials <= 1:
        sr0 = 0.0
    else:
        z1 = norm.ppf(1.0 - 1.0 / n_trials)
        z2 = norm.ppf(1.0 - 1.0 / (n_trials * np.e))
        sr0 = sr_std * ((1 - g) * z1 + g * z2)
    dsr = float(norm.cdf((sr - sr0) / sr_std))
    return dsr, float(sr0)


def year_return(pnl, times, year):
    m = (times.year == year)
    if m.sum() < 5:
        return np.nan
    r = pnl[m]
    return float(np.prod(1.0 + r) - 1.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="/tmp/ibs_robust_out")
    ap.add_argument("--n-rand", type=int, default=500)
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    n_rand = args.n_rand
    rng_master = np.random.default_rng(RNG_SEED)

    series = load_series()

    # ---------- 2) parameter grid OOS 2015+ ----------
    grid_rows = []
    print("== GRID OOS 2015+ ==")
    for s in series:
        df, spread = s["df"], s["spread"]
        times = df.index
        oos = times >= SPLIT_OOS
        ann = ann_factor(times)
        for ibs_in in IBS_INS:
            for ex_name, ex_ibs, mx in EXITS:
                pos, pnl, tr, nights, r, px = run_long(df, spread, ibs_in, ex_ibs, mx)
                mt = period_metrics(pnl, tr, times, oos, ann)
                rng = np.random.default_rng(rng_master.integers(0, 2**31 - 1))
                # r_open for costs_on_pos must be open-to-open; we used open px
                p, mu = rand_p(pos, r, nights, px, spread, oos, mt["sharpe"], ann, rng, n_rand)
                row = dict(series=s["name"], ibs_in=ibs_in, exit=ex_name, exit_ibs=ex_ibs if ex_ibs is not None else np.nan,
                           max_bars=mx, **{f"OOS_{k}": v for k, v in mt.items()}, OOS_p_rand=p, OOS_rand_sharpe=mu)
                row["OOS_verdict"] = verdict(mt, p, mu)
                grid_rows.append(row)
        sub = [r for r in grid_rows if r["series"] == s["name"]]
        best = max(sub, key=lambda x: (x["OOS_sharpe"] if np.isfinite(x["OOS_sharpe"]) else -9))
        print(f"  {s['name']} best {best['ibs_in']} {best['exit']} sh={best['OOS_sharpe']:.2f} "
              f"PF={best['OOS_pf']:.2f} p={best['OOS_p_rand']:.3f} {best['OOS_verdict']}")

    grid = pd.DataFrame(grid_rows)
    grid.to_csv(out / "grid_oos2015.csv", index=False)

    # ---------- 3) entry delay on candidates, OOS 2015+ ----------
    delay_rows = []
    print("== ENTRY DELAY ==")
    for s in series:
        df, spread = s["df"], s["spread"]
        times, ann = df.index, ann_factor(df.index)
        oos = (times >= SPLIT_OOS)
        for cname, ibs_in, ex_ibs, mx in CANDIDATES:
            base_sh = None
            for mode in ("next_open", "delay1", "close"):
                pos, pnl, tr, nights, r, px = run_long(df, spread, ibs_in, ex_ibs, mx, entry_mode=mode)
                mt = period_metrics(pnl, tr, times, oos, ann)
                if mode == "next_open":
                    base_sh = mt["sharpe"]
                delay_rows.append(dict(series=s["name"], variant=cname, mode=mode, **{f"OOS_{k}": v for k, v in mt.items()}))
                print(f"  {s['name']:12} {cname:20} {mode:10} n={mt['trades']} avg={mt['avg']:.3f} "
                      f"PF={mt['pf']:.2f} sh={mt['sharpe']:.2f} cagr={mt['cagr']:.2f}")
    delay = pd.DataFrame(delay_rows)
    delay.to_csv(out / "entry_delay.csv", index=False)

    # ---------- 4) regime splits on candidates (next_open, full & by period) ----------
    regime_rows = []
    print("== REGIME ==")
    for s in series:
        df, spread = s["df"], s["spread"]
        times, ann = df.index, ann_factor(df.index)
        vix = df["vix"].values
        close, sma = df["close"].values, df["sma200"].values
        for cname, ibs_in, ex_ibs, mx in CANDIDATES:
            pos, pnl, tr, nights, r, px = run_long(df, spread, ibs_in, ex_ibs, mx)
            # trade-level tags at signal: entry_i-1 for next_open is signal bar
            def trade_mask_from(pred):
                m = np.zeros(len(df), dtype=bool)
                # metrics uses trade.entry_i; we filter trades then rebuild via period_metrics
                return pred

            splits = {
                "all": np.ones(len(df), dtype=bool),
                "pre2010": times < SPLIT_2010,
                "2010_2014": (times >= SPLIT_2010) & (times < SPLIT_OOS),
                "post2015": times >= SPLIT_OOS,
                "vix_lt20": np.isfinite(vix) & (vix < 20),
                "vix_ge20": np.isfinite(vix) & (vix >= 20),
                "above_sma200": np.isfinite(sma) & (close > sma),
                "below_sma200": np.isfinite(sma) & (close <= sma),
            }
            # VIX/SMA: gan nhan theo nen tin hieu (entry_i-1)
            sig_i = np.clip(np.array([t.entry_i - 1 for t in tr]), 0, len(df) - 1)
            for t, si in zip(tr, sig_i):
                t.signal_i = si  # type: ignore
            for name, bar_mask in splits.items():
                if name.startswith("vix") or name.endswith("sma200"):
                    # loc theo tin hieu, khong theo moi thanh pnl
                    if name == "vix_lt20":
                        keep = {t.entry_i for t in tr if np.isfinite(vix[t.signal_i]) and vix[t.signal_i] < 20}
                    elif name == "vix_ge20":
                        keep = {t.entry_i for t in tr if np.isfinite(vix[t.signal_i]) and vix[t.signal_i] >= 20}
                    elif name == "above_sma200":
                        keep = {t.entry_i for t in tr if np.isfinite(sma[t.signal_i]) and close[t.signal_i] > sma[t.signal_i]}
                    else:
                        keep = {t.entry_i for t in tr if np.isfinite(sma[t.signal_i]) and close[t.signal_i] <= sma[t.signal_i]}
                    trs = [t for t in tr if t.entry_i in keep]
                    # pnl chi nhung doan nam giu cua cac lenh do
                    mpos = np.zeros(len(df), dtype=bool)
                    for t in trs:
                        mpos[t.entry_i:t.exit_i] = True
                    mt = metrics(np.where(mpos, pnl, 0.0), trs, times, ann)
                    # Sharpe o day bi loang vi gan 0 nhieu ngay; dung trade-stats chinh, Sharpe thong bao kem
                else:
                    mt = period_metrics(pnl, tr, times, bar_mask, ann)
                regime_rows.append(dict(series=s["name"], variant=cname, regime=name, **mt))
                print(f"  {s['name']:12} {cname:20} {name:12} n={mt['trades']:4} win={mt['win'] if np.isfinite(mt['win']) else np.nan:5.1f} "
                      f"avg={mt['avg'] if np.isfinite(mt['avg']) else np.nan:6.3f} PF={mt['pf'] if np.isfinite(mt['pf']) else np.nan:5.2f} "
                      f"sh={mt['sharpe']:.2f} cagr={mt['cagr']:.2f}")
    regime = pd.DataFrame(regime_rows)
    regime.to_csv(out / "regime.csv", index=False)

    # ---------- 1) walk-forward ----------
    print("== WALK-FORWARD 5y/1y ==")
    wf_rows = []
    # precompute all grid variants on each series once (full pnl/trades)
    cached = {}
    for s in series:
        df, spread = s["df"], s["spread"]
        for ibs_in in IBS_INS:
            for ex_name, ex_ibs, mx in EXITS:
                pos, pnl, tr, nights, r, px = run_long(df, spread, ibs_in, ex_ibs, mx)
                cached[(s["name"], ibs_in, ex_name)] = (pnl, tr, df.index, ann_factor(df.index))

        years = list(range(1990, 2027))
        # first test year: need 5y train after data start + sma warmup
        start = df.index[200] if len(df) > 200 else df.index[0]
        first_test = max(start.year + 5, 1995)
        for y in years:
            if y < first_test or y > df.index[-1].year:
                continue
            train_mask = (df.index >= pd.Timestamp(f"{y-5}-01-01")) & (df.index < pd.Timestamp(f"{y}-01-01"))
            test_mask = (df.index.year == y)
            if train_mask.sum() < 200 or test_mask.sum() < 20:
                continue
            # pick best train Sharpe among grid (min 20 trades)
            best_key, best_sh = None, -9e9
            for ibs_in in IBS_INS:
                for ex_name, ex_ibs, mx in EXITS:
                    pnl, tr, times, ann = cached[(s["name"], ibs_in, ex_name)]
                    mt = period_metrics(pnl, tr, times, train_mask, ann)
                    if mt["trades"] >= 20 and np.isfinite(mt["sharpe"]) and mt["sharpe"] > best_sh:
                        best_sh = mt["sharpe"]
                        best_key = (ibs_in, ex_name)
            # test year returns: optimized + two fixed candidates
            def yr(ibs_in, ex_name):
                pnl, tr, times, ann = cached[(s["name"], ibs_in, ex_name)]
                ret = year_return(pnl, times, y)
                ntr = sum(1 for t in tr if times[t.entry_i].year == y)
                return ret, ntr
            rec = dict(series=s["name"], year=y)
            if best_key:
                ret, ntr = yr(*best_key)
                rec.update(opt_ibs=best_key[0], opt_exit=best_key[1], opt_train_sh=best_sh,
                           opt_ret=ret, opt_trades=ntr)
            for cname, ibs_in, ex_ibs, mx in CANDIDATES:
                ex_name = "1bar" if ex_ibs is None else f"ex{int(ex_ibs*10):02d}_max{mx}"
                ret, ntr = yr(ibs_in, ex_name)
                rec[f"{cname}_ret"] = ret
                rec[f"{cname}_trades"] = ntr
            wf_rows.append(rec)
            if best_key:
                print(f"  {s['name']:12} {y} opt={best_key[0]}/{best_key[1]} trainSh={best_sh:.2f} "
                      f"test={rec.get('opt_ret', np.nan)*100 if rec.get('opt_ret')==rec.get('opt_ret') else np.nan:6.2f}%  "
                      f"1bar={rec.get('L_ibs02_1bar_ret', np.nan)*100:6.2f}%  "
                      f"ex08={rec.get('L_ibs02_ex08_max4_ret', np.nan)*100:6.2f}%")
    wf = pd.DataFrame(wf_rows)
    wf.to_csv(out / "walkforward.csv", index=False)

    # WF summary
    print("== WF SUMMARY % positive years ==")
    wf_sum = []
    for name, g in wf.groupby("series"):
        for col, label in [("opt_ret", "wf_opt"), ("L_ibs02_1bar_ret", "fixed_1bar"),
                           ("L_ibs02_ex08_max4_ret", "fixed_ex08_max4")]:
            r = g[col].dropna()
            if len(r) == 0:
                continue
            post = g.loc[g.year >= 2015, col].dropna()
            pre = g.loc[g.year < 2015, col].dropna()
            rec = dict(series=name, rule=label, n_years=len(r),
                       pct_pos=100.0 * (r > 0).mean(), mean_ret=100.0 * r.mean(),
                       med_ret=100.0 * r.median(), cum=100.0 * (np.prod(1 + r) - 1),
                       n_pre=len(pre), pct_pos_pre=100.0 * (pre > 0).mean() if len(pre) else np.nan,
                       mean_pre=100.0 * pre.mean() if len(pre) else np.nan,
                       n_post=len(post), pct_pos_post=100.0 * (post > 0).mean() if len(post) else np.nan,
                       mean_post=100.0 * post.mean() if len(post) else np.nan)
            wf_sum.append(rec)
            print(f"  {name:12} {label:18} yrs={rec['n_years']} pos={rec['pct_pos']:.1f}% mean={rec['mean_ret']:.2f}% "
                  f"pre {rec['pct_pos_pre']:.1f}%/{rec['mean_pre']:.2f}%  post {rec['pct_pos_post']:.1f}%/{rec['mean_post']:.2f}%")
    pd.DataFrame(wf_sum).to_csv(out / "walkforward_summary.csv", index=False)

    # ---------- 5) multiple testing ----------
    print("== FDR / DSR ==")
    fdr_info = {}
    for q in (0.05, 0.10):
        for sname, g in grid.groupby("series"):
            ok, thr = bh_fdr(g["OOS_p_rand"].values, q=q)
            fdr_info[f"{sname}_q{q}"] = dict(m=int(g["OOS_p_rand"].notna().sum()), n_pass=int(ok.sum()), thresh=thr)
            print(f"  BH {sname} q={q} m={g['OOS_p_rand'].notna().sum()} pass={ok.sum()} thr={thr}")
        ok, thr = bh_fdr(grid["OOS_p_rand"].values, q=q)
        fdr_info[f"pooled_q{q}"] = dict(m=int(grid["OOS_p_rand"].notna().sum()), n_pass=int(ok.sum()), thresh=thr)
        print(f"  BH pooled q={q} m={grid['OOS_p_rand'].notna().sum()} pass={ok.sum()} thr={thr}")

    # DSR for best cell per series and for prior 'passed' candidates
    # T ~ number of OOS daily obs (~ 2015-2026 = 11.8*252)
    dsr_rows = []
    N_GRID = 50 * 3  # this study
    N_FAMILY = 63 + 24 + 150  # forex all + cfd official + this grid
    for s in series:
        g = grid[grid.series == s["name"]]
        best = g.loc[g["OOS_sharpe"].idxmax()]
        # approx T from oos length
        # Sharpe da nien hoa: T phai la so nam, khong phai so nen.
        t_obs = max((s["df"].index[-1] - SPLIT_OOS).days / 365.25, 1.0)
        for N, tag in ((50, "per_series_grid50"), (N_GRID, "this_study_150"), (N_FAMILY, "all_ibs_project")):
            dsr, sr0 = deflated_sharpe(float(best["OOS_sharpe"]), t_obs, N)
            dsr_rows.append(dict(series=s["name"], sel=f"best_grid/{best['ibs_in']}/{best['exit']}",
                                 sharpe=float(best["OOS_sharpe"]), T=t_obs, N=N, tag=tag, DSR=dsr, SR0=sr0))
            print(f"  DSR {s['name']} best sh={best['OOS_sharpe']:.2f} N={N} SR0={sr0:.2f} DSR={dsr:.3f}")
        # candidates
        for cname, ibs_in, ex_ibs, mx in CANDIDATES:
            ex_name = "1bar" if ex_ibs is None else f"ex{int(ex_ibs*10):02d}_max{mx}"
            row = g[(g.ibs_in == ibs_in) & (g.exit == ex_name)]
            if len(row) == 0:
                continue
            sh = float(row.iloc[0]["OOS_sharpe"])
            for N, tag in ((N_GRID, "this_study_150"), (N_FAMILY, "all_ibs_project")):
                dsr, sr0 = deflated_sharpe(sh, t_obs, N)
                dsr_rows.append(dict(series=s["name"], sel=cname, sharpe=sh, T=t_obs, N=N, tag=tag, DSR=dsr, SR0=sr0))
    pd.DataFrame(dsr_rows).to_csv(out / "dsr.csv", index=False)
    (out / "fdr.json").write_text(json.dumps(fdr_info, indent=2, default=str), encoding="utf-8")
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
