# -*- coding: utf-8 -*-
"""Bổ sung stress gap/grind vàng tăng, tìm guard sống cả hai chiều.

Không đặt lệnh thật. Dùng lại pack/cửa sổ sập của chay_vang_11.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import phong_cach_tay.tin_hieu_data as td  # noqa: E402
from phong_cach_tay.ma.may import SPEC  # noqa: E402
from phong_cach_tay.ma.may_v2 import P_v2  # noqa: E402
from phong_cach_tay.ma.chay_v2 import (  # noqa: E402
    tai_m1_vn, dung_dac_trung, them_rej_dn, diem_S, diem_S_short,
    lap_tin, go, tom_tat, is_oos_row,
)
from phong_cach_tay.ma.chay_v2_p1 import them_to_hop_vang, ms_m1_tu_t_vn, chieu  # noqa: E402
from phong_cach_tay.ma.chay_vang_an_toan import loc_delta15  # noqa: E402
from phong_cach_tay.ma.chay_vang_11 import (  # noqa: E402
    gan_regime, loc_vao, stress_11, song, PACK_CACHE,
)
from vang.ma.chay_hyb_vang import sharpe_tu_eq  # noqa: E402

OUT_KQ = ROOT / "phong_cach_tay" / "ket_qua"
EQ0 = 10000.0
BASE = dict(L0=0.01, K=4, maxL=20, flcap=0.15, hfrac=1.0, hlot=0.01,
            dca_max_bars=0, loss_close=0.30, adx_th=30, h_boost=0.0, cooldown=240)


def nap_jun_nov():
    raw = tai_m1_vn(SPEC["XAU"]["m1"])
    d, _ = dung_dac_trung(raw)
    raw_f = pd.DataFrame({"time": d["t"], "open": d.o, "high": d.h, "low": d.l, "close": d.c,
                          "tick_volume": 1.0})
    if "tick_volume" in raw.columns and len(raw) == len(d):
        raw_f["tick_volume"] = raw["tick_volume"].to_numpy()
    rej = them_rej_dn(d, raw)
    sig0 = lap_tin(d, diem_S(d, None), diem_S_short(d, rej), None, "chi_bao", "lu")
    ms = ms_m1_tu_t_vn(d["t"])
    Fg, _ = td.tao("GC", ms)
    Fg = them_to_hop_vang(Fg)
    Mx = chieu(Fg, ms, ["delta15_giu"], tre_ms=60_000, giu_phut=15)
    sig_d15 = loc_delta15(sig0, Mx["delta15_giu"])
    atr, slope, adx, d1_ow = gan_regime(d, raw_f)
    i0, i1 = 400, len(d)
    t = d["t"].to_numpy()
    i_oos = int(np.searchsorted(t, np.datetime64("2026-10-01")))
    pack = dict(
        raw=raw, d=d, raw_f=raw_f, sig0=sig0, sig_d15=sig_d15, Mx=Mx,
        atr=atr, slope=slope, adx=adx, d1_ow=d1_ow,
        i0=i0, i1=i1, t=t, i_oos=i_oos,
        o=d.o.to_numpy(np.float64), h=d.h.to_numpy(np.float64),
        l=d.l.to_numpy(np.float64), c=d.c.to_numpy(np.float64),
        roll=d.roll.to_numpy(),
    )
    return pack


def builder_d15(ctx):
    d, Mx = ctx["d"], ctx["Mx"]

    def builder(dw):
        raww = pd.DataFrame({"time": dw["t"], "open": dw.o, "high": dw.h,
                             "low": dw.l, "close": dw.c, "tick_volume": 1.0})
        try:
            rdn = them_rej_dn(dw, raww)
        except Exception:
            rdn = np.zeros(len(dw))
        sigw = lap_tin(dw, diem_S(dw, None), diem_S_short(dw, rdn), None, "chi_bao", "lu")
        if len(sigw) == len(Mx["delta15_giu"]):
            return loc_delta15(sigw, Mx["delta15_giu"])
        return sigw
    return builder


def builder_trend(ctx):
    """delta15 + không vào ngược slope khi ADX>=20."""
    base = builder_d15(ctx)

    def builder(dw):
        sigw = base(dw)
        raww = pd.DataFrame({"time": dw["t"], "open": dw.o, "high": dw.h,
                             "low": dw.l, "close": dw.c, "tick_volume": 1.0})
        atrw, slw, adxw, ow = gan_regime(dw, raww)
        return loc_vao(sigw, dw, slw, adxw, ow, "khong_nguoc_trend")
    return builder


def builder_long_only(ctx):
    base = builder_d15(ctx)

    def builder(dw):
        s = base(dw)
        return np.where(s > 0, s, 0.0)
    return builder


def tom_cua(ten, res, eq, i0, i_oos, P):
    row = is_oos_row(tom_tat(ten, res), res, eq, i0, i_oos, P)
    P2 = np.array(P, dtype=np.float64).copy()
    P2[10] = float(P2[10]) * 2
    r2, *_ = go(
        # filled by caller if needed
        *([None] * 0),
    )
    return row


def chay_goc(ctx, sig, P):
    o, h, l, c, roll = ctx["o"], ctx["h"], ctx["l"], ctx["c"], ctx["roll"]
    i0, i1 = ctx["i0"], ctx["i1"]
    res, eq, *_ = go(o, h, l, c, roll, sig, P, i0, i1,
                     atr=ctx["atr"], slope=ctx["slope"], adx=ctx["adx"])
    row = is_oos_row(tom_tat("jun_nov", res), res, eq, i0, ctx["i_oos"], P)
    P2 = np.array(P, dtype=np.float64).copy()
    P2[10] = float(P2[10]) * 2
    r2, *_ = go(o, h, l, c, roll, sig, P2, i0, i1,
                atr=ctx["atr"], slope=ctx["slope"], adx=ctx["adx"])
    row["net_sprx2"] = round(float(r2[0]), 2)
    row["dd_sprx2"] = round(float(r2[1]), 2)
    row["sharpe"] = round(sharpe_tu_eq(eq, EQ0), 3)
    return row, res, eq


def main():
    t0 = time.time()
    OUT_KQ.mkdir(parents=True, exist_ok=True)
    print("nap Jun-Nov...", flush=True)
    ctx = nap_jun_nov()
    P0 = P_v2("XAU", **BASE)
    # warmup compile including new fields
    _ = go(ctx["o"], ctx["h"], ctx["l"], ctx["c"], ctx["roll"], ctx["sig_d15"],
           P_v2("XAU", **BASE, max_lc=2, short_cap=0.08),
           ctx["i0"], min(ctx["i0"] + 2000, ctx["i1"]),
           atr=ctx["atr"], slope=ctx["slope"], adx=ctx["adx"])
    print("compiled", f"{time.time()-t0:.1f}s", flush=True)

    row0, res0, eq0 = chay_goc(ctx, ctx["sig_d15"], P0)
    i_deep = ctx["i0"] + int(np.argmin(eq0))
    print("goc", row0, "i_deep", i_deep, ctx["d"].t.iloc[i_deep], flush=True)

    sig_trend = loc_vao(ctx["sig_d15"], ctx["d"], ctx["slope"], ctx["adx"],
                        ctx["d1_ow"], "khong_nguoc_trend")
    sig_long = np.where(ctx["sig_d15"] > 0, ctx["sig_d15"], 0.0)
    print("sig d15", int((ctx["sig_d15"] != 0).sum()),
          "trend", int((sig_trend != 0).sum()),
          "long", int((sig_long != 0).sum()), flush=True)

    cfgs = []

    def add(ten, kw, sig_name="d15"):
        cfgs.append((ten, dict(kw), sig_name))

    add("goc_59672872", dict(BASE))
    add("goc_khong_d15", dict(BASE), "raw")
    for cd in (1380, 2760, 6900, 20000):
        add(f"cd{cd}", dict(BASE, cooldown=cd))
    for n in (1, 2, 3):
        add(f"maxlc{n}", dict(BASE, max_lc=n))
        add(f"maxlc{n}_cd1380", dict(BASE, max_lc=n, cooldown=1380))
    for cap in (0.04, 0.08, 0.12):
        add(f"sc{cap}", dict(BASE, short_cap=cap))
        add(f"sc{cap}_maxlc2", dict(BASE, short_cap=cap, max_lc=2))
    add("khong_short", dict(BASE), "long")
    add("khong_nguoc_trend", dict(BASE), "trend")
    add("trend_maxlc2", dict(BASE, max_lc=2), "trend")
    add("trend_cd1380", dict(BASE, cooldown=1380), "trend")
    add("lc20_maxlc2", dict(BASE, loss_close=0.20, max_lc=2))
    add("lc20_cd1380", dict(BASE, loss_close=0.20, cooldown=1380))

    sigs = {"d15": ctx["sig_d15"], "raw": ctx["sig0"], "trend": sig_trend, "long": sig_long}
    builders = {
        "d15": builder_d15(ctx),
        "raw": builder_d15(ctx),  # replaced below
        "trend": builder_trend(ctx),
        "long": builder_long_only(ctx),
    }

    def builder_raw(dw):
        raww = pd.DataFrame({"time": dw["t"], "open": dw.o, "high": dw.h,
                             "low": dw.l, "close": dw.c, "tick_volume": 1.0})
        try:
            rdn = them_rej_dn(dw, raww)
        except Exception:
            rdn = np.zeros(len(dw))
        return lap_tin(dw, diem_S(dw, None), diem_S_short(dw, rdn), None, "chi_bao", "lu")
    builders["raw"] = builder_raw

    hang = []
    print(f"quet {len(cfgs)} cau hinh Jun-Nov...", flush=True)
    for j, (ten, kw, sn) in enumerate(cfgs, 1):
        P = P_v2("XAU", **kw)
        row, res, eq = chay_goc(ctx, sigs[sn], P)
        row["ten"] = ten
        row["sig"] = sn
        for k in ("loss_close", "cooldown", "adx_th", "max_lc", "short_cap"):
            row[k] = kw.get(k, BASE.get(k, 0))
        hang.append((row, P, sn, kw, eq, res))
        print(f"  {j}/{len(cfgs)} {ten} net={row['net']} dd={row['dd_pct']} dat={row['dat']} sprx2={row['net_sprx2']}",
              flush=True)

    bang = pd.DataFrame([h[0] for h in hang])
    bang.to_csv(OUT_KQ / "vang_2chieu_jun_nov.csv", index=False)

    # stress 15 for all that pass Jun-Nov, plus goc always
    print("stress 15 (4 giam + 4 tang + 7 sap)...", flush=True)
    st_rows = []
    tom = []
    for row, P, sn, kw, eq, res in hang:
        if (not row["dat"]) and row["ten"] not in ("goc_59672872", "goc_khong_d15"):
            continue
        rows = stress_11(
            ctx["d"], ctx["raw_f"], ctx["roll"], ctx["o"], ctx["h"], ctx["l"], ctx["c"],
            ctx["t"], ctx["i0"], ctx["i1"], i_deep, P, builders[sn],
            ctx["atr"], ctx["slope"], ctx["adx"], packs=PACK_CACHE, hai_chieu=True,
        )
        n_ok = sum(1 for r in rows if song(r))
        n_all = len(rows)
        te = min((r["net"] for r in rows if not np.isnan(r.get("net", np.nan))), default=float("nan"))
        te_dd = max((r["dd_pct"] for r in rows if not np.isnan(r.get("dd_pct", np.nan))), default=float("nan"))
        print(f"  {row['ten']}: {n_ok}/{n_all} worst_net={te} worst_dd={te_dd} JunNov {row['net']} dd={row['dd_pct']}",
              flush=True)
        rec = dict(ten=row["ten"], sig=sn, net=row["net"], dd_pct=row["dd_pct"],
                   is_net=row.get("is_net"), oos_net=row.get("oos_net"),
                   net_sprx2=row["net_sprx2"], dd_sprx2=row["dd_sprx2"],
                   sharpe=row["sharpe"], n_ok=n_ok, n_all=n_all,
                   worst_net=te, worst_dd=te_dd, dat_jn=row["dat"])
        for r in rows:
            rr = dict(r)
            rr["cfg"] = row["ten"]
            st_rows.append(rr)
            rec[r.get("scenario") or r.get("ten")] = r.get("dd_pct")
        tom.append(rec)

    pd.DataFrame(st_rows).to_csv(OUT_KQ / "vang_2chieu_stress15.csv", index=False)
    pd.DataFrame(tom).to_csv(OUT_KQ / "vang_2chieu_tomtat.csv", index=False)

    # long window 2025.09-2026.11 unfiltered, on promising cfgs
    long_csv = Path("/workspace/backtests/rapid_hedge/data/GOLD_i_M1_202508_202611.csv")
    if long_csv.exists():
        print("cua so dai 2025.09-2026.11 khong delta15...", flush=True)
        ath = pd.read_csv(long_csv, parse_dates=["time"])
        raw = tai_m1_vn(long_csv)
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
        i0, i1 = 400, len(d)
        t = d["t"].to_numpy()
        i_oos = int(np.searchsorted(t, np.datetime64("2026-10-01")))
        o, h, l, c = d.o.to_numpy(np.float64), d.h.to_numpy(np.float64), d.l.to_numpy(np.float64), d.c.to_numpy(np.float64)
        roll = d.roll.to_numpy()
        sig_tr = loc_vao(sig, d, slope, adx, d1_ow, "khong_nguoc_trend")
        sig_lo = np.where(sig > 0, sig, 0.0)
        long_sigs = {"d15": sig, "raw": sig, "trend": sig_tr, "long": sig_lo}
        long_rows = []
        # only goc + those with 15/15 or best n_ok
        pick = {r["ten"] for r in tom if r["n_ok"] >= 13} | {"goc_59672872", "goc_khong_d15"}
        for row, P, sn, kw, eq, res in hang:
            if row["ten"] not in pick:
                continue
            sg = long_sigs[sn]
            rr, eq2, *_ = go(o, h, l, c, roll, sg, P, i0, i1, atr=atr, slope=slope, adx=adx)
            rec = is_oos_row(tom_tat(row["ten"], rr), rr, eq2, i0, i_oos, P)
            j = int(np.argmin(eq2))
            rec["t_eq_min"] = str(d.t.iloc[i0 + j])
            rec["eq_min"] = round(float(eq2[j]), 2)
            long_rows.append(rec)
            print(f"  long {rec['ten']} net={rec['net']} dd={rec['dd_pct']} blown={rec['blown']} tmin={rec['t_eq_min']} eqmin={rec['eq_min']}",
                  flush=True)
        pd.DataFrame(long_rows).to_csv(OUT_KQ / "vang_2chieu_cua_so_dai.csv", index=False)

    print("xong", f"{time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    sys.exit(main() or 0)
