# -*- coding: utf-8 -*-
"""Tối ưu tay_v2 vàng trên cửa sổ đầy 2025.09–2026.11, không delta15, walk-forward 3m/1m.

Không đặt lệnh thật.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from phong_cach_tay.ma.may_v2 import P_v2  # noqa: E402
from phong_cach_tay.ma.chay_v2 import (  # noqa: E402
    tai_m1_vn, dung_dac_trung, them_rej_dn, diem_S, diem_S_short,
    lap_tin, go, tom_tat, is_oos_row,
)
from phong_cach_tay.ma.chay_vang_11 import (  # noqa: E402
    gan_regime, stress_11, song, PACK_CACHE,
)
from vang.ma.chay_hyb_vang import sharpe_tu_eq  # noqa: E402

OUT = ROOT / "phong_cach_tay" / "ket_qua"
EQ0 = 10000.0
CSV = Path("/workspace/backtests/rapid_hedge/data/GOLD_i_M1_202508_202611.csv")
BASE = dict(L0=0.01, K=4, maxL=20, flcap=0.15, hfrac=1.0, hlot=0.01,
            dca_max_bars=0, loss_close=0.30, adx_th=30, h_boost=0.0, cooldown=240)


def nap_full():
    ath = pd.read_csv(CSV, parse_dates=["time"])
    raw = tai_m1_vn(CSV)
    mask = (ath.time >= "2025-09-01") & (ath.time < "2026-11-28")
    r = raw.loc[mask.values].reset_index(drop=True)
    d, _ = dung_dac_trung(r)
    raw_f = pd.DataFrame({"time": d["t"], "open": d.o, "high": d.h, "low": d.l, "close": d.c,
                          "tick_volume": 1.0})
    if "tick_volume" in r.columns and len(r) == len(d):
        raw_f["tick_volume"] = r["tick_volume"].to_numpy()
    rej = them_rej_dn(d, r)
    sig = lap_tin(d, diem_S(d, None), diem_S_short(d, rej), None, "chi_bao", "lu")
    atr, slope, adx, d1_ow = gan_regime(d, raw_f)
    t = pd.to_datetime(d["t"])
    return dict(
        d=d, raw_f=raw_f, sig=sig, atr=atr, slope=slope, adx=adx, d1_ow=d1_ow, t=t,
        o=d.o.to_numpy(np.float64), h=d.h.to_numpy(np.float64),
        l=d.l.to_numpy(np.float64), c=d.c.to_numpy(np.float64),
        roll=d.roll.to_numpy(),
        i0=400, i1=len(d),
    )


def folds_3m_1m():
    months = pd.period_range("2025-12", "2026-11", freq="M")
    out = []
    for tm in months:
        train0 = (tm - 3).to_timestamp()
        if train0 < pd.Timestamp("2025-09-01"):
            train0 = pd.Timestamp("2025-09-01")
        test0 = tm.to_timestamp()
        test1 = (tm + 1).to_timestamp() if tm < months[-1] else pd.Timestamp("2026-11-28")
        out.append((str(tm), train0, test0, test1))
    return out


def chay(ctx, P, i0=None, i1=None, sprx2=False):
    i0 = ctx["i0"] if i0 is None else i0
    i1 = ctx["i1"] if i1 is None else i1
    res, eq, *_ = go(ctx["o"], ctx["h"], ctx["l"], ctx["c"], ctx["roll"], ctx["sig"],
                     P, i0, i1, atr=ctx["atr"], slope=ctx["slope"], adx=ctx["adx"])
    row = tom_tat("x", res)
    row["sharpe"] = round(sharpe_tu_eq(eq, EQ0), 3)
    if sprx2:
        P2 = np.array(P, dtype=np.float64).copy()
        P2[10] = float(P2[10]) * 2
        r2, *_ = go(ctx["o"], ctx["h"], ctx["l"], ctx["c"], ctx["roll"], ctx["sig"],
                    P2, i0, i1, atr=ctx["atr"], slope=ctx["slope"], adx=ctx["adx"])
        row["net_sprx2"] = round(float(r2[0]), 2)
        row["dd_sprx2"] = round(float(r2[1]), 2)
        row["dd_pct_sprx2"] = round(float(r2[1]) / EQ0 * 100, 2)
        row["blown_sprx2"] = bool(r2[10] >= 0)
    return row, res, eq


def dat_cua(row, spr=False):
    ok = (not row.get("blown", True)) and row.get("net", -1) > 0 and row.get("dd_pct", 999) < 80
    if spr:
        ok = ok and (not row.get("blown_sprx2", True)) and row.get("net_sprx2", -1) > 0 and row.get("dd_pct_sprx2", 999) < 80
    return bool(ok)


def builder_raw(ctx):
    def builder(dw):
        raww = pd.DataFrame({"time": dw["t"], "open": dw.o, "high": dw.h,
                             "low": dw.l, "close": dw.c, "tick_volume": 1.0})
        try:
            rdn = them_rej_dn(dw, raww)
        except Exception:
            rdn = np.zeros(len(dw))
        return lap_tin(dw, diem_S(dw, None), diem_S_short(dw, rdn), None, "chi_bao", "lu")
    return builder


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    print("nap cua so day...", flush=True)
    ctx = nap_full()
    print("nen", ctx["i1"], ctx["t"].iloc[ctx["i0"]], "->", ctx["t"].iloc[-1], flush=True)
    Pwarm = P_v2("XAU", **BASE, short_cap=0.04, max_lc=2, lc_period=6900, lc_pause=6900,
                 day_loss=0.15, week_loss=0.30, eq_lot=1, dca_mode=2, flat_orphan=1)
    _ = go(ctx["o"], ctx["h"], ctx["l"], ctx["c"], ctx["roll"], ctx["sig"],
           Pwarm, ctx["i0"], min(ctx["i0"] + 3000, ctx["i1"]),
           atr=ctx["atr"], slope=ctx["slope"], adx=ctx["adx"])
    print("compiled", f"{time.time()-t0:.1f}s", flush=True)

    cfgs = []
    def add(ten, **kw):
        d = dict(BASE)
        d.update(kw)
        cfgs.append((ten, d))

    add("goc")
    add("orphan", flat_orphan=1)
    add("sc04", short_cap=0.04)
    add("sc04_cd20000", short_cap=0.04, cooldown=20000)
    add("sc04_orphan", short_cap=0.04, flat_orphan=1)
    add("sc04_cd20000_orphan", short_cap=0.04, cooldown=20000, flat_orphan=1)
    add("orphan_week20", flat_orphan=1, week_loss=0.20)
    add("orphan_week30", flat_orphan=1, week_loss=0.30)
    add("orphan_day15", flat_orphan=1, day_loss=0.15)
    add("orphan_day15_week30", flat_orphan=1, day_loss=0.15, week_loss=0.30)
    add("orphan_lc2w", flat_orphan=1, max_lc=2, lc_period=6900, lc_pause=6900)
    add("orphan_lc2w_sc04", flat_orphan=1, max_lc=2, lc_period=6900, lc_pause=6900, short_cap=0.04)
    add("orphan_eqlot", flat_orphan=1, eq_lot=1)
    add("orphan_dca1", flat_orphan=1, dca_mode=1)
    add("orphan_dca2", flat_orphan=1, dca_mode=2)
    add("lc2w", max_lc=2, lc_period=6900, lc_pause=6900)
    add("day15_week30", day_loss=0.15, week_loss=0.30)
    add("sc04_orphan_eqlot_week30", short_cap=0.04, flat_orphan=1, eq_lot=1, week_loss=0.30)
    add("sc04_orphan_day10_week20", short_cap=0.04, flat_orphan=1, day_loss=0.10, week_loss=0.20)
    add("sc04_orphan_lc2w_week25", short_cap=0.04, flat_orphan=1, max_lc=2, lc_period=6900, lc_pause=6900, week_loss=0.25)
    add("sc04_orphan_dca2_week30", short_cap=0.04, flat_orphan=1, dca_mode=2, week_loss=0.30)
    add("sc04_orphan_dca2_lc2w", short_cap=0.04, flat_orphan=1, dca_mode=2, max_lc=2, lc_period=6900, lc_pause=6900)
    add("kitchen_lite", short_cap=0.04, flat_orphan=1, week_loss=0.25, eq_lot=1, dca_mode=2)
    add("kitchen", short_cap=0.04, flat_orphan=1, max_lc=2, lc_period=6900, lc_pause=6900,
        day_loss=0.15, week_loss=0.30, eq_lot=1, dca_mode=2)
    add("orphan_cd20000", flat_orphan=1, cooldown=20000)
    add("sc04_orphan_day15", short_cap=0.04, flat_orphan=1, day_loss=0.15)

    fds = folds_3m_1m()
    t_idx = ctx["t"]
    print(f"quet {len(cfgs)} cfg, {len(fds)} fold WF...", flush=True)
    hang, fold_rows = [], []
    for j, (ten, kw) in enumerate(cfgs, 1):
        P = P_v2("XAU", **kw)
        row, res, eq = chay(ctx, P, sprx2=True)
        row["ten"] = ten
        for k in ("short_cap", "max_lc", "lc_period", "lc_pause", "day_loss", "week_loss",
                  "eq_lot", "dca_mode", "flat_orphan", "cooldown", "loss_close"):
            row[k] = kw.get(k, BASE.get(k, 0) if k in BASE else 0)
        row["dat_full"] = dat_cua(row, spr=False)
        row["dat_sprx2"] = dat_cua(row, spr=True)
        # WF folds
        n_ok = 0
        worst_net, worst_dd = 0.0, 0.0
        for fn, tr0, te0, te1 in fds:
            i0 = int(np.searchsorted(t_idx.values, np.datetime64(te0)))
            i1 = int(np.searchsorted(t_idx.values, np.datetime64(te1)))
            if i1 - i0 < 100:
                continue
            fr, *_ = chay(ctx, P, i0=max(i0, 1), i1=i1, sprx2=False)
            ok = dat_cua(fr, spr=False)
            n_ok += int(ok)
            worst_net = min(worst_net, fr["net"]) if n_ok + (not ok) else fr["net"]
            worst_dd = max(worst_dd, fr["dd_pct"])
            fold_rows.append(dict(cfg=ten, fold=fn, train0=str(tr0.date()),
                                  test0=str(te0.date()), test1=str(te1.date()),
                                  net=fr["net"], dd_pct=fr["dd_pct"], maxfl=fr["maxfl"],
                                  blown=fr["blown"], dat=ok, n_en=fr["n_en"]))
        n_fold = len([1 for r in fold_rows if r["cfg"] == ten])
        row["wf_ok"] = n_ok
        row["wf_all"] = n_fold
        row["wf_dat"] = n_ok == n_fold and n_fold > 0
        row["wf_worst_net"] = round(min((r["net"] for r in fold_rows if r["cfg"] == ten), default=0), 2)
        row["wf_worst_dd"] = round(max((r["dd_pct"] for r in fold_rows if r["cfg"] == ten), default=0), 2)
        hang.append((row, P, kw, eq, res))
        print(f"  {j}/{len(cfgs)} {ten} net={row['net']} dd={row['dd_pct']} sprx2={row['net_sprx2']}/{row['dd_pct_sprx2']} "
              f"full={row['dat_full']} spr={row['dat_sprx2']} WF {n_ok}/{n_fold} worst_f {row['wf_worst_net']}/{row['wf_worst_dd']}",
              flush=True)

    bang = pd.DataFrame([h[0] for h in hang])
    bang.to_csv(OUT / "vang_wf_full_quet.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(OUT / "vang_wf_folds.csv", index=False)

    # stress 15: all that pass full, plus goc, plus top by (dat_sprx2, wf_ok, net)
    pick = set(bang[bang.dat_full].ten)
    pick |= {"goc", "sc04_cd20000", "orphan", "kitchen", "kitchen_lite"}
    # also best 3 by wf_ok then net
    pick |= set(bang.sort_values(["wf_ok", "dat_sprx2", "net"], ascending=[False, False, False]).ten.head(6))

    print("stress 15 tren", sorted(pick), flush=True)
    bld = builder_raw(ctx)
    st_rows, tom = [], []
    t_np = ctx["t"].to_numpy()
    for row, P, kw, eq, res in hang:
        if row["ten"] not in pick:
            continue
        i_deep = ctx["i0"] + int(np.argmin(eq)) if not row["blown"] else int(np.searchsorted(t_np, np.datetime64("2026-01-21")))
        i_deep = min(max(i_deep, ctx["i0"] + 10), ctx["i1"] - 10)
        print(f"  {row['ten']} i_deep", i_deep, ctx["t"].iloc[i_deep], flush=True)
        rows = stress_11(
            ctx["d"], ctx["raw_f"], ctx["roll"], ctx["o"], ctx["h"], ctx["l"], ctx["c"],
            t_np, ctx["i0"], ctx["i1"], i_deep, P, bld,
            ctx["atr"], ctx["slope"], ctx["adx"], packs=PACK_CACHE, hai_chieu=True,
        )
        n_s = sum(1 for r in rows if song(r))
        te = min((r["net"] for r in rows if not np.isnan(r.get("net", np.nan))), default=float("nan"))
        td = max((r["dd_pct"] for r in rows if not np.isnan(r.get("dd_pct", np.nan))), default=float("nan"))
        print(f"    stress {n_s}/{len(rows)} worst_net={te} worst_dd={td}", flush=True)
        rec = dict(ten=row["ten"], net=row["net"], dd_pct=row["dd_pct"],
                   net_sprx2=row["net_sprx2"], dd_pct_sprx2=row["dd_pct_sprx2"],
                   dat_full=row["dat_full"], dat_sprx2=row["dat_sprx2"],
                   wf_ok=row["wf_ok"], wf_all=row["wf_all"], wf_dat=row["wf_dat"],
                   n_stress=n_s, n_st_all=len(rows), worst_net=te, worst_dd=td,
                   dat_15=n_s == len(rows),
                   dat_all=row["dat_sprx2"] and row["wf_dat"] and n_s == len(rows))
        for r in rows:
            rr = dict(r); rr["cfg"] = row["ten"]
            st_rows.append(rr)
        tom.append(rec)

    pd.DataFrame(st_rows).to_csv(OUT / "vang_wf_stress15.csv", index=False)
    pd.DataFrame(tom).to_csv(OUT / "vang_wf_tomtat.csv", index=False)
    print("tom tat dat_all:", [r["ten"] for r in tom if r["dat_all"]], flush=True)
    print("xong", f"{time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    sys.exit(main() or 0)
