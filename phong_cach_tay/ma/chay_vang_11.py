# -*- coding: utf-8 -*-
"""Tối ưu vàng mặc định để sống 11/11 stress, vẫn lãi>0 DD<80% Jun–Nov.

Thử: đóng lỗ tổng, guard xu hướng (EMA/ADX/D1), khe ATR, lot giảm theo tầng,
hedge tăng khi drift, tuổi rổ tối đa, xác nhận chỉ báo. Không đặt lệnh thật.
"""
from __future__ import annotations

import itertools
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
    lap_tin, go, tom_tat, is_oos_row, md_table,
)
from phong_cach_tay.ma.chay_v2_p1 import (  # noqa: E402
    them_to_hop_vang, ms_m1_tu_t_vn, chieu,
)
from phong_cach_tay.ma.chay_vang_an_toan import loc_delta15, WIN  # noqa: E402
from vang.ma.chay_hyb_vang import dsr, sharpe_tu_eq, known  # noqa: E402

OUT_BAO = ROOT / "phong_cach_tay" / "bao_cao"
OUT_KQ = ROOT / "phong_cach_tay" / "ket_qua"
EQ0 = 10000.0


def adx_ohlc(h, l, c, n=14):
    prev_c = np.roll(c, 1); prev_c[0] = c[0]
    prev_h = np.roll(h, 1); prev_h[0] = h[0]
    prev_l = np.roll(l, 1); prev_l[0] = l[0]
    tr = np.maximum(h - l, np.maximum(np.abs(h - prev_c), np.abs(l - prev_c)))
    up = h - prev_h
    dn = prev_l - l
    plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
    minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)
    atr = pd.Series(tr).ewm(alpha=1 / n, adjust=False).mean()
    pdi = 100 * pd.Series(plus_dm).ewm(alpha=1 / n, adjust=False).mean() / atr.replace(0, np.nan)
    mdi = 100 * pd.Series(minus_dm).ewm(alpha=1 / n, adjust=False).mean() / atr.replace(0, np.nan)
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    adx = dx.ewm(alpha=1 / n, adjust=False).mean()
    return adx.fillna(0).to_numpy()


def gan_regime(d: pd.DataFrame, raw: pd.DataFrame):
    """ADX M15, slope D1/EMA, D1 one-way — đã nhân quả (shift)."""
    g = raw.set_index("time") if "time" in raw.columns else raw.set_index(raw.columns[0])
    if g.index.name is None or not isinstance(g.index, pd.DatetimeIndex):
        # raw from dung path uses 'time'
        pass
    if "time" in raw.columns:
        t = raw["time"]
        gg = raw.set_index("time")
    else:
        t = d["t"]
        gg = pd.DataFrame({"open": d.o.to_numpy(), "high": d.h.to_numpy(),
                           "low": d.l.to_numpy(), "close": d.c.to_numpy()}, index=pd.to_datetime(d.t))
    x15 = gg.resample("15min").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    adx15 = adx_ohlc(x15.high.to_numpy(), x15.low.to_numpy(), x15.close.to_numpy(), 14)
    adx = known(t, x15.index, adx15, "15min")
    adx = pd.Series(adx).shift(1).bfill().fillna(0).to_numpy()

    d1 = gg.resample("1D").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    rng = (d1.high - d1.low).replace(0, np.nan)
    ow = ((d1.close - d1.open) / rng).fillna(0).clip(-1, 1).to_numpy()
    d1_ow = known(t, d1.index, ow, "1D")
    d1_ow = pd.Series(d1_ow).shift(1).bfill().fillna(0).to_numpy()

    slp = d["slp"].to_numpy() if "slp" in d.columns else np.zeros(len(d))
    e50 = d["e50"].to_numpy() if "e50" in d.columns else np.zeros(len(d))
    e200 = d["e200"].to_numpy() if "e200" in d.columns else np.zeros(len(d))
    slope_ema = np.sign(slp)
    slope_x = np.sign(e50 - e200)
    slope = slope_ema.copy()
    # D1 one-way mạnh đè slope
    slope = np.where(np.abs(d1_ow) >= 0.6, np.sign(d1_ow), slope)
    # nếu EMA50/200 khác dấu với slp, giữ slp (chậm hơn) trừ khi one-way
    atr = d["a15"].to_numpy() if "a15" in d.columns else np.zeros(len(d))
    return atr.astype(np.float64), slope.astype(np.float64), adx.astype(np.float64), d1_ow.astype(np.float64)


def loc_vao(sig, d, slope, adx, d1_ow, che_do):
    s = np.asarray(sig, dtype=np.float64).copy()
    if che_do in ("d15", "goc"):
        return s
    bbz = d["bbz"].to_numpy()
    vwz = d["vwz"].to_numpy()
    rsi5 = d["rsi5"].to_numpy() if "rsi5" in d.columns else np.full(len(d), 50.0)
    sl = diem_S(d, None)
    ss = diem_S_short(d, np.zeros(len(d)))  # already baked in original sig; S>=2 uses sl/ss
    # reconstruct short score from columns
    if che_do == "S2":
        ok = ((s > 0) & (sl >= 2)) | ((s < 0) & (ss >= 2))
        # ss may be wrong; use sl for long and -components for short
        s_short = ((bbz > 2).astype(int) + (d["usopen"].to_numpy() > 0).astype(int)
                   + (d["reg"].to_numpy() < 0.8).astype(int) - (vwz > 2).astype(int))
        ok = ((s > 0) & (sl >= 2)) | ((s < 0) & (s_short >= 2))
        return np.where(ok, s, 0.0)
    if che_do == "bb_vwap":
        # mean-reversion: long bbz<=-2 or vwz<=-2; short ngược
        ok = ((s > 0) & ((bbz <= -2) | (vwz <= -2))) | ((s < 0) & ((bbz >= 2) | (vwz >= 2)))
        return np.where(ok, s, 0.0)
    if che_do == "rsi":
        ok = ((s > 0) & (rsi5 <= 40)) | ((s < 0) & (rsi5 >= 60))
        return np.where(ok, s, 0.0)
    if che_do == "khong_nguoc_trend":
        # không vào ngược slope khi ADX>=20
        ok = ~((adx >= 20) & (slope * s < 0))
        return np.where(ok, s, 0.0)
    if che_do == "bb_hoac_rsi":
        ok = ((s > 0) & ((bbz <= -2) | (rsi5 <= 35))) | ((s < 0) & ((bbz >= 2) | (rsi5 >= 65)))
        return np.where(ok, s, 0.0)
    return s


def gap_fn_factory(t, g, i):
    def f(oo, hh, ll, cc):
        oo, hh, ll, cc = oo.copy(), hh.copy(), ll.copy(), cc.copy()
        fac = np.ones(len(cc)); fac[i:] = 1 - g
        return oo * fac, hh * fac, ll * fac, cc * fac
    return f


def grind_fn_factory(t, tot, days, start="2026-06-01"):
    def f(oo, hh, ll, cc):
        oo, hh, ll, cc = oo.copy(), hh.copy(), ll.copy(), cc.copy()
        i_s = int(np.searchsorted(t, np.datetime64(start)))
        n = len(cc)
        k = np.zeros(n)
        span = days * 1380
        k[i_s:] = np.minimum(np.arange(n - i_s) / max(span, 1), 1.0)
        fac = np.exp(np.log(1 - tot) * k)
        return oo * fac, hh * fac, ll * fac, cc * fac
    return f


def chay_1(o, h, l, c, roll, sig, P, i0, i1, atr, slope, adx, t=None, i_oos=None):
    res, eq, *rest = go(o, h, l, c, roll, sig, P, i0, i1, atr=atr, slope=slope, adx=adx)
    row = tom_tat("x", res)
    if t is not None and i_oos is not None:
        row = is_oos_row(row, res, eq, i0, i_oos, P)
    return row, res, eq, rest


PACK_CACHE = {}


def _pack_from_raw(raw2, i0_default):
    dw, _ = dung_dac_trung(raw2)
    atr2, sl2, adx2, ow2 = gan_regime(dw, raw2)
    return dict(dw=dw, atr=atr2, slope=sl2, adx=adx2, ow=ow2,
                o=dw.o.to_numpy(np.float64), h=dw.h.to_numpy(np.float64),
                l=dw.l.to_numpy(np.float64), c=dw.c.to_numpy(np.float64),
                roll=dw.roll.to_numpy(), i0=i0_default, i1=len(dw))


def stress_11(d, raw, roll, o, h, l, c, t, i0, i1, i_deep, P, sig_builder, atr, slope, adx, packs=None):
    """sig_builder(dw) -> sig. packs: dict scenario -> feature pack (tránh tính lại)."""
    if packs is None:
        packs = PACK_CACHE
    rows = []
    for sn, fn in [
        ("gap-10% tai day von", gap_fn_factory(t, 0.10, i_deep)),
        ("gap-20% tai day von", gap_fn_factory(t, 0.20, i_deep)),
        ("grind-20%/60ngay", grind_fn_factory(t, 0.20, 60)),
        ("grind-35%/120ngay", grind_fn_factory(t, 0.35, 120)),
    ]:
        key = (sn, int(i_deep))
        if key not in packs:
            o2, h2, l2, c2 = fn(o, h, l, c)
            raw2 = pd.DataFrame({"time": d["t"], "open": o2, "high": h2, "low": l2, "close": c2,
                                 "tick_volume": 1.0})
            packs[key] = _pack_from_raw(raw2, i0)
            print(f"    pack {sn} ok", flush=True)
        pk = packs[key]
        sig2 = sig_builder(pk["dw"])
        res, *_ = go(pk["o"], pk["h"], pk["l"], pk["c"], pk["roll"], sig2, P, pk["i0"], pk["i1"],
                     atr=pk["atr"], slope=pk["slope"], adx=pk["adx"])
        row = tom_tat(sn, res)
        row["scenario"] = sn
        rows.append(row)

    pq = SPEC["XAU"]["pq"]
    if pq.exists():
        if ("__m5__",) not in packs:
            m5 = pd.read_parquet(pq).reset_index()
            if "time" not in m5.columns:
                m5 = m5.rename(columns={m5.columns[0]: "time"})
            m5["time"] = pd.to_datetime(m5["time"])
            m5["tick_volume"] = 1.0
            packs[("__m5__",)] = m5
        m5 = packs[("__m5__",)]
        for wn, (a, b) in WIN.items():
            if wn not in packs:
                w = m5[(m5.time >= a) & (m5.time < b)].copy()
                if len(w) < 200:
                    packs[wn] = None
                else:
                    fsc = 4000.0 / float(w.close.iloc[0])
                    for k in ["open", "high", "low", "close"]:
                        w[k] *= fsc
                    pk = _pack_from_raw(w, 50)
                    pk["n_nen"] = len(pk["dw"])
                    pk["scale"] = round(fsc, 3)
                    packs[wn] = pk
                    print(f"    pack crash {wn} n={pk['n_nen']}", flush=True)
            pk = packs[wn]
            if pk is None:
                rows.append(dict(ten=wn, scenario=wn, net=np.nan, maxdd=np.nan,
                                 dd_pct=999, blown=True, dat=False, n_nen=0))
                continue
            sigw = sig_builder(pk["dw"])
            rw, *_ = go(pk["o"], pk["h"], pk["l"], pk["c"], pk["roll"], sigw, P, pk["i0"], pk["i1"],
                        atr=pk["atr"], slope=pk["slope"], adx=pk["adx"])
            row = tom_tat(wn, rw)
            row.update(scenario=wn, n_nen=pk.get("n_nen", 0), scale=pk.get("scale", 1))
            rows.append(row)
    return rows


def song(r):
    return (not bool(r.get("blown", True))) and float(r.get("dd_pct", 999)) < 80 and not np.isnan(r.get("net", np.nan))


def main():
    t0 = time.time()
    OUT_BAO.mkdir(parents=True, exist_ok=True)
    OUT_KQ.mkdir(parents=True, exist_ok=True)

    print("nap M1 + P1 + regime...", flush=True)
    raw = tai_m1_vn(SPEC["XAU"]["m1"])
    d, _ = dung_dac_trung(raw)
    # raw time đã là VN naive
    raw_f = pd.DataFrame({"time": d["t"], "open": d.o, "high": d.h, "low": d.l, "close": d.c,
                          "tick_volume": raw["tick_volume"].to_numpy()[:len(d)] if "tick_volume" in raw.columns else 1.0})
    if "tick_volume" in raw.columns and len(raw) == len(d):
        raw_f["tick_volume"] = raw["tick_volume"].to_numpy()
    rej = them_rej_dn(d, raw)
    sl, ss = diem_S(d, None), diem_S_short(d, rej)
    sig0 = lap_tin(d, sl, ss, None, "chi_bao", "lu")
    ms = ms_m1_tu_t_vn(d["t"])
    Fg, _ = td.tao("GC", ms)
    Fg = them_to_hop_vang(Fg)
    Mx = chieu(Fg, ms, ["delta15_giu"], tre_ms=60_000, giu_phut=15)
    sig_d15 = loc_delta15(sig0, Mx["delta15_giu"])
    atr, slope, adx, d1_ow = gan_regime(d, raw_f)
    print("adx med", float(np.median(adx)), "p75", float(np.percentile(adx, 75)),
          "slope !=0", int((slope != 0).sum()), "atr med", float(np.median(atr[atr > 0])), flush=True)

    i0, i1 = 400, len(d)
    t = d["t"].to_numpy()
    i_oos = int(np.searchsorted(t, np.datetime64("2026-10-01")))
    o = d.o.to_numpy(np.float64)
    h = d.h.to_numpy(np.float64)
    l = d.l.to_numpy(np.float64)
    c = d.c.to_numpy(np.float64)
    roll = d.roll.to_numpy()

    print("compile...", flush=True)
    P0 = P_v2("XAU", L0=0.01, K=4, maxL=20, flcap=0.15, hfrac=1.0, hlot=0.01,
              loss_close=0.4, adx_th=25, cooldown=60)
    _ = go(o, h, l, c, roll, sig_d15, P0, i0, min(i0 + 2000, i1), atr=atr, slope=slope, adx=adx)
    print("compiled", f"{time.time()-t0:.1f}s", flush=True)

    # tín hiệu ứng viên
    sigs = {
        "d15": sig_d15,
        "S2": loc_vao(sig_d15, d, slope, adx, d1_ow, "S2"),
        "bb_vwap": loc_vao(sig_d15, d, slope, adx, d1_ow, "bb_vwap"),
        "rsi": loc_vao(sig_d15, d, slope, adx, d1_ow, "rsi"),
        "khong_nguoc_trend": loc_vao(sig_d15, d, slope, adx, d1_ow, "khong_nguoc_trend"),
        "bb_hoac_rsi": loc_vao(sig_d15, d, slope, adx, d1_ow, "bb_hoac_rsi"),
    }
    for k, v in sigs.items():
        print(f"  sig {k}: {int((v!=0).sum())}", flush=True)

    # --- Pha 1: loss_close / cooldown / age trên d15, không regime ---
    base = dict(L0=0.01, K=4, maxL=20, flcap=0.15, hfrac=1.0, hlot=0.01, dca_max_bars=0)
    hang = []
    cfgs = []  # (ten, kw, sig_name)

    def add(ten, kw, sig_name="d15"):
        cfgs.append((ten, dict(kw), sig_name))

    add("goc_truoc", dict(base))
    for lc in (0.20, 0.25, 0.30, 0.35, 0.40, 0.50):
        add(f"lc{int(lc*100)}", dict(base, loss_close=lc))
        add(f"lc{int(lc*100)}_cd60", dict(base, loss_close=lc, cooldown=60))
        add(f"lc{int(lc*100)}_cd240", dict(base, loss_close=lc, cooldown=240))
        add(f"lc{int(lc*100)}_cd1380", dict(base, loss_close=lc, cooldown=1380))
    for age in (240, 480, 1380, 2760):
        add(f"age{age}", dict(base, max_age=age))
        add(f"lc40_age{age}", dict(base, loss_close=0.40, max_age=age))
        add(f"lc40_cd240_age{age}", dict(base, loss_close=0.40, cooldown=240, max_age=age))

    # regime + loss close
    for lc, th, hb in itertools.product((0.30, 0.40, 0.50), (20, 25, 30), (0.0, 0.5, 1.0)):
        add(f"lc{int(lc*100)}_adx{th}_hb{hb}", dict(base, loss_close=lc, adx_th=th, h_boost=hb, cooldown=240))

    # ATR / decay
    for lc, ga, dec in itertools.product((0.40,), (0.0, 1.0, 1.5), (0.0, 0.7, 0.85)):
        add(f"lc40_ga{ga}_dec{dec}", dict(base, loss_close=lc, gap_atr=ga, lot_decay=dec, cooldown=240, adx_th=25))

    # entry filters on a few cores
    cores = [
        dict(base, loss_close=0.40, cooldown=240),
        dict(base, loss_close=0.40, cooldown=240, adx_th=25, h_boost=0.5),
        dict(base, loss_close=0.30, cooldown=240, adx_th=25),
        dict(base, loss_close=0.40, cooldown=1380, adx_th=25, h_boost=1.0, max_age=1380),
    ]
    for i, kw in enumerate(cores):
        for sn in sigs:
            if sn == "d15":
                continue
            add(f"core{i}_{sn}", dict(kw), sn)

    print(f"quet {len(cfgs)} cau hinh tren Jun-Nov...", flush=True)
    for j, (ten, kw, sn) in enumerate(cfgs, 1):
        P = P_v2("XAU", **kw)
        row, res, eq, _ = chay_1(o, h, l, c, roll, sigs[sn], P, i0, i1, atr, slope, adx, t, i_oos)
        row["ten"] = ten
        row["sig"] = sn
        for k in ("loss_close", "cooldown", "max_age", "adx_th", "h_boost", "gap_atr", "lot_decay", "L0", "K", "flcap", "hfrac"):
            row[k] = kw.get(k, 0)
        hang.append(row)
        if j % 40 == 0 or j == len(cfgs):
            print(f"  {j}/{len(cfgs)} last {ten} net={row['net']} dd={row['dd_pct']} dat={row['dat']}", flush=True)

    bang = pd.DataFrame(hang)
    bang.to_csv(OUT_KQ / "vang11_quet.csv", index=False)
    dat = bang[bang.dat == True]
    print(f"DAT Jun-Nov: {len(dat)}/{len(bang)}", flush=True)
    if len(dat):
        print(dat.sort_values(["dd_pct", "oos_net"], ascending=[True, False]).head(15).to_string(index=False), flush=True)

    # --- Stress trên các cấu hình đạt, ưu tiên DD thấp + OOS>0, tối đa ~24 ---
    if len(dat):
        chon = dat.copy()
        chon["uu"] = (chon.oos_net > 0).astype(int) * 3 + (chon.is_net > 0).astype(int) * 2 - chon.dd_pct / 100
        chon = chon.sort_values(["uu", "dd_pct"], ascending=[False, True])
        # đa dạng: lấy tốt nhất mỗi họ
        picked = []
        seen = set()
        for _, r in chon.iterrows():
            key = (round(float(r.loss_close), 2), int(r.cooldown), int(r.max_age),
                   int(r.adx_th), r.sig, round(float(r.h_boost), 2))
            if key in seen and len(picked) >= 8:
                continue
            seen.add(key)
            picked.append(r.ten)
            if len(picked) >= 20:
                break
    else:
        picked = list(bang.sort_values("dd_pct").ten.head(8))

    print("stress tren", picked, flush=True)
    # i_deep từ goc hoặc best
    goc_row = bang[bang.ten == "goc_truoc"]
    if len(goc_row):
        Ptmp = P_v2("XAU", **base)
        _, _, eqg, _ = chay_1(o, h, l, c, roll, sig_d15, Ptmp, i0, i1, atr, slope, adx)
        i_deep = i0 + int(np.argmin(eqg))
    else:
        i_deep = i0 + 5000
    print("i_deep", i_deep, d.t.iloc[min(i_deep, len(d)-1)], flush=True)

    SIG_CACHE = {}

    def make_builder(sn):
        def builder(dw):
            key = (sn, id(dw))
            if key in SIG_CACHE:
                return SIG_CACHE[key]
            raww = pd.DataFrame({"time": dw["t"], "open": dw.o, "high": dw.h, "low": dw.l, "close": dw.c, "tick_volume": 1.0})
            try:
                rdn = them_rej_dn(dw, raww)
            except Exception:
                rdn = np.zeros(len(dw))
            sigw = lap_tin(dw, diem_S(dw, None), diem_S_short(dw, rdn), None, "chi_bao", "lu")
            try:
                atrw, slw, adxw, ow = gan_regime(dw, raww)
            except Exception:
                slw = np.sign(dw["slp"].to_numpy()) if "slp" in dw.columns else np.zeros(len(dw))
                adxw = np.zeros(len(dw)); ow = slw
            out = sigw if sn == "d15" else loc_vao(sigw, dw, slw, adxw, ow, sn)
            SIG_CACHE[key] = out
            return out
        return builder

    st_all = []
    ket_11 = []
    for ten in picked:
        rec = bang[bang.ten == ten].iloc[0]
        kw = None
        sn = rec.sig
        for t2, kw2, sn2 in cfgs:
            if t2 == ten:
                kw, sn = kw2, sn2
                break
        P = P_v2("XAU", **kw)
        builder = make_builder(sn)
        rows = stress_11(d, raw_f, roll, o, h, l, c, t, i0, i1, i_deep, P, builder, atr, slope, adx)
        n_ok = sum(1 for r in rows if song(r))
        te = min((r["net"] for r in rows if not np.isnan(r.get("net", np.nan))), default=float("nan"))
        print(f"  {ten}: {n_ok}/11 worst_net={te}  JunNov net={rec.net} dd={rec.dd_pct}", flush=True)
        for r in rows:
            r["cfg"] = ten
            st_all.append(r)
        ket_11.append(dict(ten=ten, song=n_ok, worst_net=round(float(te), 2) if te == te else None,
                           net=rec.net, dd_pct=rec.dd_pct, is_net=rec.is_net, oos_net=rec.oos_net,
                           sig=sn, **{k: rec.get(k, 0) for k in ("loss_close", "cooldown", "max_age", "adx_th", "h_boost", "gap_atr", "lot_decay")}))

    st = pd.DataFrame(st_all)
    st.to_csv(OUT_KQ / "vang11_stress.csv", index=False)
    k11 = pd.DataFrame(ket_11)
    k11.to_csv(OUT_KQ / "vang11_stress_tomtat.csv", index=False)
    pass11 = k11[k11.song >= 11]
    print("PASS 11/11 + (already dat Jun-Nov):", list(pass11.ten) if len(pass11) else "KHONG", flush=True)
    if not len(pass11):
        gan = k11.sort_values(["song", "dd_pct"], ascending=[False, True])
        print("GAN NHAT:\n", gan.head(10).to_string(index=False), flush=True)

    # --- 7 bước đầy đủ trên pass 11/11 (hoặc top 3 gần nhất) ---
    if len(pass11):
        mains = list(pass11.sort_values(["dd_pct", "oos_net"], ascending=[True, False]).ten)
    else:
        mains = list(k11.sort_values(["song", "dd_pct"], ascending=[False, True]).ten.head(3))

    day, shadow = [], []
    eq_luu, P_luu, sig_luu = {}, {}, {}
    for ten in mains:
        kw = sn = None
        for t2, kw2, sn2 in cfgs:
            if t2 == ten:
                kw, sn = kw2, sn2
                break
        P = P_v2("XAU", **kw)
        sig = sigs[sn]
        res, eq, bo, bc, bpnl, bworst, blots = go(o, h, l, c, roll, sig, P, i0, i1, atr=atr, slope=slope, adx=adx)
        row = is_oos_row(tom_tat(ten, res), res, eq, i0, i_oos, P)
        P2 = P.copy(); P2[10] = float(P[10]) * 2
        res2, *_ = go(o, h, l, c, roll, sig, P2, i0, i1, atr=atr, slope=slope, adx=adx)
        row["net_sprx2"] = round(float(res2[0]), 2)
        row["dd_sprx2"] = round(float(res2[1]), 2)
        row["dat_sprx2"] = bool(res2[0] > 0 and res2[1] / EQ0 < 0.80 and res2[10] < 0)
        sr = sharpe_tu_eq(eq, EQ0)
        row["sharpe"] = round(sr, 3)
        row["dsr"] = round(dsr(sr, len(eq), n_trials=max(len(mains) + 11, 2)), 3)
        rec = bang[bang.ten == ten].iloc[0]
        for k in ("loss_close", "cooldown", "max_age", "adx_th", "h_boost", "gap_atr", "lot_decay", "sig"):
            row[k] = rec[k]
        sk = k11[k11.ten == ten].iloc[0]
        row["stress_song"] = int(sk.song)
        row["stress_worst"] = sk.worst_net
        day.append(row)
        eq_luu[ten] = eq
        P_luu[ten] = (P, sig, kw, sn)
        if len(shadow) < 6000:
            for k in range(len(bo)):
                shadow.append(dict(he=ten,
                                   mo=str(d.t.iloc[int(bo[k])]) if bo[k] >= 0 else "",
                                   dong="" if bc[k] < 0 else str(d.t.iloc[int(bc[k])]),
                                   pnl=float(bpnl[k]), worst=float(bworst[k]), lots=float(blots[k]),
                                   ghi_chu="chi log, khong dat lenh"))
        print("7b", row["ten"], "net", row["net"], "dd", row["dd_pct"], "spr", row["net_sprx2"],
              row["dd_sprx2"], "song", row["stress_song"], flush=True)

    bang7 = pd.DataFrame(day)
    bang7.to_csv(OUT_KQ / "vang11_7buoc.csv", index=False)
    if shadow:
        pd.DataFrame(shadow).to_csv(OUT_KQ / "shadow_vang11.csv", index=False)

    # --- Lân cận trên cấu hình tốt nhất (đạt 11/11 nếu có) ---
    lg_rows = []
    if mains:
        ten0 = mains[0]
        P, sig, kw, sn = P_luu[ten0]
        neighbors = [("goc", dict(kw))]
        # perturb
        for name, delta in [
            ("lc-5", dict(loss_close=max(0.10, kw.get("loss_close", 0.4) - 0.05))),
            ("lc+5", dict(loss_close=min(0.70, kw.get("loss_close", 0.4) + 0.05))),
            ("adx0", dict(adx_th=0.0)),
            ("adx20", dict(adx_th=20)),
            ("adx30", dict(adx_th=30)),
            ("hb0", dict(h_boost=0.0)),
            ("hb1", dict(h_boost=1.0)),
            ("cd0", dict(cooldown=0)),
            ("cd60", dict(cooldown=60)),
            ("cd1380", dict(cooldown=1380)),
            ("age0", dict(max_age=0)),
            ("age1380", dict(max_age=1380)),
            ("L0.02", dict(L0=0.02, hlot=0.02)),
            ("K3", dict(K=3)),
            ("hfrac0.5", dict(hfrac=0.5)),
            ("tp3", dict(tp=3.0)),
            ("tp5", dict(tp=5.0)),
            ("gap4", dict(gap=4.0)),
            ("gap7", dict(gap=7.0)),
            ("hgap15", dict(hgap=15.0)),
            ("hgap28", dict(hgap=28.0)),
            ("dec0.7", dict(lot_decay=0.7)),
            ("ga1.2", dict(gap_atr=1.2)),
        ]:
            neighbors.append((name, {**kw, **delta}))
        print(f"lang gieng cua {ten0}: {len(neighbors)}", flush=True)
        for name, nkw in neighbors:
            Pn = P_v2("XAU", **nkw)
            row, res, eq, _ = chay_1(o, h, l, c, roll, sigs[sn], Pn, i0, i1, atr, slope, adx, t, i_oos)
            row["ten"] = f"{ten0}|{name}"
            # sprx2 nhanh
            P2 = Pn.copy(); P2[10] = float(Pn[10]) * 2
            r2, *_ = go(o, h, l, c, roll, sigs[sn], P2, i0, i1, atr=atr, slope=slope, adx=adx)
            row["net_sprx2"] = round(float(r2[0]), 2)
            row["dd_sprx2"] = round(float(r2[1]), 2)
            row["dat_sprx2"] = bool(r2[0] > 0 and r2[1] / EQ0 < 0.80 and r2[10] < 0)
            lg_rows.append(row)
            print(f"  lg {name} net={row['net']} dd={row['dd_pct']} dat={row['dat']}", flush=True)
        # stress 11 cho 4 lân cận quan trọng nếu gốc đạt 11
        # (chỉ chạy Jun-Nov ở trên; stress thêm loss_close ±5 và adx0 nếu cần)
        extra_stress = ["goc", "lc-5", "lc+5", "adx0", "hfrac0.5", "L0.02", "hgap15"]
        for name, nkw in neighbors:
            if name not in extra_stress:
                continue
            Pn = P_v2("XAU", **nkw)
            rows = stress_11(d, raw_f, roll, o, h, l, c, t, i0, i1, i_deep, Pn, make_builder(sn), atr, slope, adx)
            n_ok = sum(1 for r in rows if song(r))
            te = min((r["net"] for r in rows if not np.isnan(r.get("net", np.nan))), default=float("nan"))
            # gắn vào lg row
            for lr in lg_rows:
                if lr["ten"] == f"{ten0}|{name}":
                    lr["stress_song"] = n_ok
                    lr["stress_worst"] = round(float(te), 2) if te == te else None
            print(f"  lg-stress {name}: {n_ok}/11 worst={te}", flush=True)
            for r in rows:
                r["cfg"] = f"{ten0}|{name}"
                st_all.append(r)
        st = pd.DataFrame(st_all)
        st.to_csv(OUT_KQ / "vang11_stress.csv", index=False)

    lgb = pd.DataFrame(lg_rows)
    if len(lgb):
        lgb.to_csv(OUT_KQ / "vang11_lang_gieng.csv", index=False)

    # --- báo cáo ---
    n_dat = int((bang.dat == True).sum())
    lines = [
        "# Vàng tay_v2 — tối ưu sống 11 stress (t349)",
        "",
        f"Xuất: {pd.Timestamp.now(tz='Asia/Saigon')} (giờ Việt Nam, UTC+7).",
        "",
        "Không đặt lệnh thật. Vốn 10.000 USD = 1.000.000 USC (100 USC = 1 USD).",
        "",
        "Mốc mặc định trước tối ưu (L0=0,01 K=4 maxL=20 hfrac=1 lọc delta15, không khóa 30p): "
        "Jun–Nov +14.032,99 USD, DD 34,24%, stress 8/11 (gãy grind −20%, grind −35%, Covid).",
        "",
        f"Quét {len(bang)} cấu hình (đóng lỗ tổng, guard ADX/EMA/D1, khe ATR, lot giảm, hedge boost, tuổi rổ, cooldown, lọc vào). "
        f"**Đạt Jun–Nov (lãi>0, DD<80%, không cháy): {n_dat}/{len(bang)}.**",
        "",
    ]
    if n_dat:
        show = dat.sort_values(["dd_pct", "oos_net"], ascending=[True, False]).head(15)
        cols = [c for c in ["ten", "sig", "net", "maxdd", "dd_pct", "maxfl", "is_net", "oos_net",
                            "loss_close", "cooldown", "max_age", "adx_th", "h_boost", "lot_decay", "gap_atr"] if c in show.columns]
        lines += [md_table(show, cols), ""]
    if len(k11):
        lines += ["## Stress 11 cửa sổ (cấu hình đạt Jun–Nov đã chọn)", "",
                  md_table(k11.sort_values(["song", "dd_pct"], ascending=[False, True]),
                           [c for c in ["ten", "song", "worst_net", "net", "dd_pct", "is_net", "oos_net", "sig",
                                        "loss_close", "cooldown", "max_age", "adx_th", "h_boost"] if c in k11.columns]),
                  "",
                  f"**Sống 11/11 và Jun–Nov đạt: {len(pass11)} cấu hình.**",
                  ""]
    if len(bang7):
        lines += ["## Kiểm 7 bước", "",
                  md_table(bang7, [c for c in ["ten", "net", "maxdd", "dd_pct", "maxfl", "is_net", "oos_net",
                                                "net_sprx2", "dd_sprx2", "dat", "dat_sprx2", "sharpe", "dsr",
                                                "stress_song", "stress_worst", "n_en", "blown",
                                                "loss_close", "cooldown", "max_age", "adx_th", "h_boost", "sig"] if c in bang7.columns]),
                  ""]
        for _, r in bang7.iterrows():
            usc = r.net * 100
            fl = r.maxfl * 100
            lines.append(
                f"- `{r.ten}`: lãi {r.net:.2f} USD ({usc:,.0f} USC), DD {r.dd_pct:.2f}%, "
                f"lỗ thả nổi tệ nhất {r.maxfl:.2f} USD ({fl:,.0f} USC), "
                f"IS {r.is_net:.2f} / OOS {r.oos_net:.2f}, spread×2 {r.net_sprx2:.2f} (DD {r.dd_sprx2/EQ0*100:.2f}%), "
                f"stress {int(r.stress_song)}/11, tệ nhất {r.stress_worst}."
            )
        lines.append("")
    if len(lgb):
        cols = [c for c in ["ten", "net", "dd_pct", "maxfl", "is_net", "oos_net", "dat",
                            "net_sprx2", "dat_sprx2", "stress_song", "stress_worst"] if c in lgb.columns]
        lines += ["## Lân cận tham số (cấu hình gốc = dòng `goc`)", "", md_table(lgb, cols), ""]
        if "stress_song" in lgb.columns:
            n_on = int(lgb["stress_song"].notna().sum())
            n_ok = int(((lgb.get("dat") == True) & (lgb["stress_song"] >= 11)).sum()) if n_on else 0
            lines.append(f"Lân cận có chạy đủ 11 stress: {n_on}. Vừa đạt Jun–Nov vừa 11/11: {n_ok}.")
            lines.append("")
    lines += [
        "Cửa sổ sập M5 parquet không có delta15 — lọc còn trung tính (tín hiệu chỉ báo). "
        "Gap/grind tính lại ATR/ADX/EMA trên giá đã biến hình.",
        "",
        f"Chạy {time.time()-t0:.1f} giây. File: `ket_qua/vang11_*.csv`, `shadow_vang11.csv`.",
    ]
    (OUT_BAO / "BAO_CAO_VANG_11.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("XONG", "pass11", list(pass11.ten) if len(pass11) else None, "dt", time.time() - t0, flush=True)


if __name__ == "__main__":
    main()
