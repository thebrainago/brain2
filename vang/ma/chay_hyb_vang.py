# -*- coding: utf-8 -*-
"""Giai đoạn B: cổng HYB+AG sang vàng, so baseline với tín hiệu Fxaurum.
Quy trình: IS/OOS, spread x2, 11 stress, lân cận, cháy/lỗ thả nổi vs 80%, DSR, nhật ký bóng.
Không đặt lệnh thật.
"""
from __future__ import annotations

import json, sys, time, math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vang" / "nguon_hyb"))

import importlib.util
def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
_rh = _load("/workspace/backtests/rapid_hedge/prep.py", "rh_prep_vang")
atr_df, known = _rh.atr, _rh.known
_zz = _load(str(ROOT / "vang" / "nguon_hyb" / "song_zigzag_atr.py"), "zz_vang")
zigzag = _zz.zigzag
from vang.ma import may_hyb  # noqa: E402
from vang.ma.tin_hieu_data import (  # noqa: E402
    tai_nen_cfd_va_basis, cum_big_trade, su_kien_flow, tin_vwap_poc,
)

XM_M1 = Path("/workspace/backtests/rapid_hedge/data/GOLD_i_M1.csv")
GC_DIR = Path("/workspace/brain2/vang/du_lieu/fxaurum")
M5_PQ = Path("/workspace/quet_intraday/m5/xauusd.parquet")
OUT_BAO = ROOT / "vang" / "bao_cao"
OUT_KQ = ROOT / "vang" / "ket_qua"
SHADOW = OUT_KQ / "shadow_hyb_vang.csv"

# 7 cửa sổ sập (cùng lịch US500), + 2 grind + 2 gap = 11
WIN = {
    "Q4-2018": ("2018-09-25", "2019-02-28"),
    "Covid 02-04/2020": ("2020-02-10", "2020-07-31"),
    "2022 H1": ("2021-12-28", "2022-07-31"),
    "2022 08-10": ("2022-08-12", "2022-12-15"),
    "08-10/2023": ("2023-07-25", "2023-12-15"),
    "07-08/2024": ("2024-07-10", "2024-09-30"),
    "02-04/2025": ("2025-02-15", "2025-07-15"),
}

# HYB+AG mặc định (cổng ATR, lot bước 0.01, pv=100)
def P_mac_dinh(spr=0.20, K=3, coef=1.3, G=3.0, th=1.5, EQ0=10000.0, ddb=3000.0):
    # (xem may_hyb.run / sim_ag)
    zmode=0; maxL=10; tp1=1.0; sfrac=0.5; bx=0.0; bxu=0
    hmode=1; hN=5; hr=1.0; hcap=2.0; htp=0.8; hrecl=1; hexp=960; brk=0.0
    mlf=200.0; lev=500.0; swl=-83.83; sws=20.64; emode=0; refill=1; dmin=0.5; mg=3.0
    lmode=1; ks=1.5; gmin=1.5; gmax=4.8
    wP=0.5; wF=1.0; wV=1.5; wO=1.5
    se=1.0; sd=1.0; shi=99.0; chi=99.0; mhi=1.0; sfd=0.5; flipx=0; oppx=0; deadw=960
    tf=0; tmode=1; tnl=5; tnd=5*1380; trel=1; hstop=0; bpd=1380
    pv=100.0; step=0.01
    return np.array([
        zmode,K,coef,maxL,tp1,sfrac,bx,bxu,hmode,hN,hr,hcap,htp,hrecl,hexp,brk,spr,EQ0,ddb,mlf,lev,swl,sws,emode,refill,dmin,mg,
        lmode,G,ks,gmin,gmax,wP,wF,wV,wO,se,sd,shi,chi,mhi,sfd,flipx,oppx,deadw,
        tf,th,tmode,tnl,tnd,trel,hstop,bpd,pv,step,
    ], dtype=np.float64)


def us_session_vn(t_vn: pd.Series):
    """t_vn: giờ Việt Nam (UTC+7). Phiên Mỹ 09:30-16:00 ET."""
    # DST Mỹ 2026: 8/3-1/11. UTC+7 = ET+11 (DST) hoặc ET+12 (chuẩn)
    t = pd.to_datetime(t_vn)
    dst = (t >= pd.Timestamp("2026-03-08")) & (t < pd.Timestamp("2026-11-01"))
    # ngoài 2026: xấp xỉ tháng 3-10
    dst = dst | ((t.dt.year != 2026) & t.dt.month.between(4, 10))
    mo = t.dt.hour * 60 + t.dt.minute
    mo_open = np.where(dst, 20 * 60 + 30, 21 * 60 + 30)
    rel = (mo - mo_open) % 1440
    us = (rel < 390).astype(np.int8)
    usopen = (rel < 120).astype(np.int8)
    return us, usopen


def rsi(c, n=14):
    d = np.diff(c, prepend=c[0])
    up = pd.Series(np.maximum(d, 0)).ewm(alpha=1 / n, adjust=False).mean()
    dn = pd.Series(np.maximum(-d, 0)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn.replace(0, 1e-9))).to_numpy()


def dung_dac_trung(m: pd.DataFrame) -> pd.DataFrame:
    """m: time naive UTC+7 (để resample giống gốc), OHLC CFD, tick_volume, spread."""
    m = m.copy().drop_duplicates("time").reset_index(drop=True)
    g = m.set_index("time")
    r = {}
    for fr in ["5min", "15min", "60min"]:
        x = g.resample(fr).agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
        x["atr"] = atr_df(x)
        r[fr] = x
    t = m["time"]
    d = pd.DataFrame(dict(t=t, o=m.open.to_numpy(), h=m.high.to_numpy(), l=m.low.to_numpy(), c=m.close.to_numpy()))
    d["a5"] = known(t, r["5min"].index, r["5min"].atr.to_numpy(), "5min")
    d["a15"] = known(t, r["15min"].index, r["15min"].atr.to_numpy(), "15min")
    d["ah1"] = known(t, r["60min"].index, r["60min"].atr.to_numpy(), "60min")
    d["m5end"] = (t.dt.floor("5min") != t.dt.floor("5min").shift(-1)).to_numpy()
    d["c5p"] = known(t, r["5min"].index, r["5min"].close.shift(1).to_numpy(), "5min")
    d = d.bfill()
    # ngày lịch máy chủ Athens ≈ t_vn - 4h (DST) / 5h (chuẩn). Dùng date của t (UTC+7) cho roll gần đúng.
    sd = t.dt.date
    d["roll"] = (pd.Series(sd) != pd.Series(sd).shift(1)).to_numpy()
    d.loc[0, "roll"] = False
    # zigzag M15
    x = r["15min"]
    piv = zigzag(x.high.to_numpy(), x.low.to_numpy(), x.atr.to_numpy(), 2.0)
    tt = d.t.to_numpy()
    n = len(d)
    lo = np.full(n, np.nan)
    ex = np.full(n, np.nan)
    for q in piv:
        if q["loai"] != -1:
            continue
        a = np.searchsorted(tt, np.datetime64(x.index[q["xn"]] + pd.Timedelta("15min")))
        e = np.searchsorted(tt, np.datetime64(x.index[q["idx"]]))
        if a < n:
            lo[a] = q["gia"]
            ex[a] = e
    d["zz_lo"] = pd.Series(lo).ffill().to_numpy()
    d["zz_ext"] = pd.Series(ex).ffill().fillna(0).astype(np.int64).to_numpy()
    # VP daily: POC/VAL/VAH 3 phiên trước (bin 0.5)
    tp = (m.high + m.low + m.close) / 3
    vol = m["tick_volume"].clip(lower=1).astype(float) if "tick_volume" in m.columns else pd.Series(1.0, index=m.index)
    day = pd.Series(sd, index=m.index)
    poc_list = []
    days = list(dict.fromkeys(sd))
    vp_by_day = {}
    tmp = pd.DataFrame({"day": day, "bin": (m.close / 0.5).round() * 0.5, "vol": vol})
    for dd, g2 in tmp.groupby("day"):
        s = g2.groupby("bin")["vol"].sum().sort_values(ascending=False)
        if s.empty:
            vp_by_day[dd] = [np.nan, np.nan, np.nan]
        else:
            poc = float(s.index[0])
            # VAL/VAH thô: biên 70% volume quanh POC
            tot = s.sum()
            acc = 0.0
            used = set()
            for b, v in s.items():
                used.add(b)
                acc += v
                if acc >= 0.7 * tot:
                    break
            vp_by_day[dd] = [min(used) if used else poc, poc, max(used) if used else poc]
    arr = np.full((len(days), 12), np.nan)
    di = {dd: i for i, dd in enumerate(days)}
    for i, dd in enumerate(days):
        prev = [vp_by_day[x] for x in days[:i][-3:]]
        vals = [z for v in prev for z in v]
        arr[i, :len(vals)] = vals
    d["didx"] = pd.Series(sd).map(di).astype(np.int64).to_numpy()
    # chỉ báo, shift 1
    I = pd.DataFrame(index=d.index)
    x5 = r["5min"]
    I["rsi5"] = known(t, x5.index, rsi(x5.close.to_numpy()), "5min")
    day_s = pd.Series(sd.values)
    cv = (tp.to_numpy() * vol.to_numpy())
    # session VWAP z theo ngày VN
    vw = pd.Series(cv, index=m.index).groupby(day).cumsum() / vol.groupby(day).cumsum()
    var = (pd.Series(vol.to_numpy() * tp.to_numpy() ** 2, index=m.index).groupby(day).cumsum() / vol.groupby(day).cumsum() - vw * vw).clip(lower=0)
    sdv = np.sqrt(var)
    I["vwz"] = ((m.close.to_numpy() - vw.to_numpy()) / sdv.replace(0, np.nan).to_numpy())
    I["vwz"] = pd.Series(I["vwz"]).clip(-6, 6).fillna(0).to_numpy()
    x15 = r["15min"]
    mid = x15.close.rolling(20).mean()
    sd15 = x15.close.rolling(20).std()
    midk = known(t, x15.index, mid.to_numpy(), "15min")
    sdk = known(t, x15.index, sd15.to_numpy(), "15min")
    I["bbz"] = pd.Series((d.c.to_numpy() - midk) / sdk).clip(-6, 6).fillna(0).to_numpy()
    rng = (x5.high - x5.low).replace(0, np.nan)
    rej = (((np.minimum(x5.open, x5.close) - x5.low) / rng >= 0.5) & (x5.close >= x5.low + 0.6 * rng)).astype(float).to_numpy()
    I["rej"] = known(t, x5.index, rej, "5min")
    I["us"], I["usopen"] = us_session_vn(t)
    w = int(5 * 1440)
    I["reg"] = (d.a15 / d.a15.rolling(w, min_periods=50).median()).fillna(1).to_numpy()
    I = I.shift(1).bfill()
    for k in I:
        d[k] = I[k].to_numpy()
    # D1 EMA200 / EMA50 / slope 10
    d1 = g.resample("1D").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    ema200 = d1.close.ewm(span=200, adjust=False).mean()
    ema50 = d1.close.ewm(span=50, adjust=False).mean()
    slp = ema200.diff(10)
    d["d1c"] = known(t, d1.index, d1.close.to_numpy(), "1D")
    d["e200"] = known(t, d1.index, ema200.to_numpy(), "1D")
    d["e50"] = known(t, d1.index, ema50.to_numpy(), "1D")
    d["slp"] = known(t, d1.index, slp.to_numpy(), "1D")
    d[["d1c", "e200", "e50", "slp"]] = d[["d1c", "e200", "e50", "slp"]].ffill().bfill()
    return d, arr


def diem_S(d: pd.DataFrame, bonus=None) -> np.ndarray:
    s = ((d["bbz"].to_numpy() < -2).astype(np.int16)
         + (d["rej"].to_numpy() > 0).astype(np.int16)
         + (d["usopen"].to_numpy() > 0).astype(np.int16)
         + (d["reg"].to_numpy() < 0.8).astype(np.int16)
         - (d["vwz"].to_numpy() < -2).astype(np.int16))
    if bonus is not None:
        s = s + bonus.astype(np.int16)
    return s.astype(np.float64)


def tai_xm_m1_vn() -> pd.DataFrame:
    m = pd.read_csv(XM_M1, parse_dates=["time"])
    # máy chủ Athens → UTC+7
    t = m["time"].dt.tz_localize("Europe/Athens", ambiguous="infer", nonexistent="shift_forward")
    m = m.copy()
    m["time"] = t.dt.tz_convert("Asia/Saigon").dt.tz_localize(None)
    m = m.rename(columns={"tick_volume": "tick_volume"})
    return m


def bonus_data(d: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """+1 nếu tín hiệu data cùng chiều mua (HYB chỉ mua đáy); -1 nếu ngược. Trả (bonus, opt_levels)."""
    n = len(d)
    bonus = np.zeros(n, dtype=np.int16)
    opt = np.full((n, 6), np.nan)
    if not GC_DIR.exists():
        return bonus, opt
    try:
        gc_cfd = tai_nen_cfd_va_basis(GC_DIR, XM_M1)
        ev_v, gc2 = tin_vwap_poc(gc_cfd)
        big = pd.read_csv(GC_DIR / "gcz6_bigtrades.csv") if (GC_DIR / "gcz6_bigtrades.csv").exists() else pd.DataFrame()
        flow = json.loads((GC_DIR / "gcz6_flow.json").read_text()) if (GC_DIR / "gcz6_flow.json").exists() else {}
        evs = {
            "cum50": cum_big_trade(big, min_vol=50, cua_so_ms=60_000, n_min=2, band=0.8),
            "vwap_tc": ev_v.get("vwap_tu_choi"),
            "sw": su_kien_flow(flow, "sw", min_vol=5),
        }
        # d.t là UTC+7 naive; ev.time là UTC aware
        t_utc = pd.to_datetime(d["t"]).dt.tz_localize("Asia/Saigon").dt.tz_convert("UTC")
        # map
        def gan(ev):
            loc = np.zeros(n, dtype=np.int16)
            if ev is None or ev.empty:
                return loc
            idx = np.searchsorted(t_utc.to_numpy(), ev["time"].to_numpy(), side="right") - 1
            for i, h in zip(idx, ev["huong"].to_numpy()):
                if 0 <= i < n and loc[i] == 0:
                    loc[i] = np.int16(h)
            return loc
        tot = np.zeros(n, dtype=np.int16)
        for ev in evs.values():
            tot = tot + gan(ev)
        bonus = np.where(tot > 0, 1, np.where(tot < 0, -1, 0)).astype(np.int16)
        # mức vùng: VWAP/POC phiên (quy CFD) của GC, gắn vào opt
        if "vwap" in gc2.columns:
            t2 = gc2["time"]
            # cùng trục d.t UTC+7
            t2_vn = t2.dt.tz_convert("Asia/Saigon").dt.tz_localize(None)
            # reindex gần nhất
            g = gc2.assign(tvn=t2_vn).drop_duplicates("tvn").set_index("tvn")
            vwap = g["vwap"].reindex(d["t"], method="ffill")
            poc = g["poc_truoc"].reindex(d["t"], method="ffill") if "poc_truoc" in g.columns else None
            # GC vwap là giá future — quy CFD = GC - basis
            if "basis" in g.columns:
                basis = g["basis"].reindex(d["t"], method="ffill")
                opt[:, 0] = (vwap - basis).to_numpy()
                if poc is not None:
                    opt[:, 1] = (poc - basis).to_numpy()
            else:
                opt[:, 0] = vwap.to_numpy()
                if poc is not None:
                    opt[:, 1] = poc.to_numpy()
    except Exception as e:
        print("bonus_data loi", type(e).__name__, e, flush=True)
    return bonus, opt


def go(d, vp, opt, S, P, i0, i1):
    flip = np.zeros(len(d), dtype=np.float64)
    arrays = [d[k].to_numpy(dtype=np.float64) for k in ["o", "h", "l", "c", "a5", "a15", "ah1"]]
    m5end = d["m5end"].to_numpy()
    c5p = d["c5p"].to_numpy(dtype=np.float64)
    roll = d["roll"].to_numpy()
    zzlo = d["zz_lo"].to_numpy(dtype=np.float64)
    zzext = d["zz_ext"].to_numpy(dtype=np.int64)
    didx = d["didx"].to_numpy(dtype=np.int64)
    d1c = d["d1c"].to_numpy(dtype=np.float64)
    e200 = d["e200"].to_numpy(dtype=np.float64)
    e50 = d["e50"].to_numpy(dtype=np.float64)
    slp = d["slp"].to_numpy(dtype=np.float64)
    res, eqc, bo, bc, blay, bworst, bpnl, blots = may_hyb.run(
        arrays[0], arrays[1], arrays[2], arrays[3], arrays[4], arrays[5], arrays[6],
        m5end, c5p, roll, zzlo, zzext, didx, vp, opt, S, flip, d1c, e200, e50, slp, P, i0, i1,
    )
    names = ["net","real","hreal","sreal","maxdd","minml","minml100","ntick","nhtick","nstp",
             "ndcablk","nddblk","nmlwarn","maxlots","maxhl","blown","nb","ne","maxfl","maxlay",
             "blown100","nth","threal","nhalt"]
    r = {k: float(res[i]) for i, k in enumerate(names)}
    return r, dict(eq=eqc, bo=bo, bc=bc, blay=blay, bworst=bworst, bpnl=bpnl, blots=blots)


def tom_tat(ten, r, eq0=10000.0):
    dd_pct = r["maxdd"] / eq0 if eq0 else 0
    loi = r["net"]
    dat = (loi > 0) and (dd_pct < 0.80) and (r["blown"] < 0)
    return dict(ten=ten, net=round(loi, 2), maxdd=round(r["maxdd"], 2), dd_pct=round(dd_pct * 100, 2),
                maxfl=round(r["maxfl"], 2), minml=round(r["minml"], 1), minml100=round(r["minml100"], 1),
                n_ro=int(r["nb"]), maxlay=int(r["maxlay"]), maxlots=round(r["maxlots"], 2),
                blown=bool(r["blown"] >= 0), stopout100=bool(r["blown100"] >= 0),
                nth=int(r["nth"]), nhalt=int(r["nhalt"]), dat=bool(dat))


def dsr(sr, n_obs, n_trials, sr0=0.0):
    """Deflated Sharpe xấp xỉ Bailey & López de Prado."""
    if n_obs <= 2:
        return 0.0
    # E[max SR] ≈ sr0 + sqrt(var) * ((1-gamma)*norm.ppf(1-1/N)+gamma*norm.ppf(1-1/N*e^-1))
    from math import log, sqrt, erfc, exp
    # dùng CDF chuẩn ngược thô
    def ppf(p):
        # Acklam approx
        a = [ -3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
              1.383577509590605e+02, -3.066479806614716e+01, 2.506628277459239e+00 ]
        b = [ -5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
              6.680131188771972e+01, -1.328068071678348e+01 ]
        c = [ -7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
              -2.549732539343734e+00, 4.374664141464858e+00, 2.938163982698783e+00 ]
        d = [ 7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
              3.754408661907416e+00 ]
        plow, phigh = 0.02425, 1-0.02425
        if p < plow:
            q = sqrt(-2*log(p))
            return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
        if p > phigh:
            q = sqrt(-2*log(1-p))
            return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
        q = p - 0.5; r = q*q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    N = max(int(n_trials), 1)
    eul = 0.5772156649
    z1 = ppf(1 - 1.0 / N) if N > 1 else 0.0
    z2 = ppf(1 - 1.0 / (N * math.e)) if N > 1 else 0.0
    emax = sr0 + (1 - eul) * z1 + eul * z2
    # se of SR ~ sqrt((1+0.5 sr^2)/(n-1))
    se = math.sqrt((1 + 0.5 * sr * sr) / (n_obs - 1))
    z = (sr - emax) / se if se > 0 else 0
    # Phi(z)
    return 0.5 * math.erfc(-z / math.sqrt(2))


def sharpe_tu_eq(eq, eq0, n_year_bars=1380 * 252):
    ret = np.diff(eq, prepend=eq0)
    if ret.std() == 0:
        return 0.0
    # Sharpe năm hóa theo số nến/ngày ~1380
    mu = ret.mean()
    sd = ret.std()
    return float(mu / sd * math.sqrt(n_year_bars))


def main():
    t0 = time.time()
    OUT_BAO.mkdir(parents=True, exist_ok=True)
    OUT_KQ.mkdir(parents=True, exist_ok=True)
    print("nap GOLD M1...", flush=True)
    raw = tai_xm_m1_vn()
    print("n", len(raw), raw.time.iloc[0], raw.time.iloc[-1], flush=True)
    d, vp = dung_dac_trung(raw)
    print("dac trung xong", len(d), "a15 med", float(np.nanmedian(d.a15)), flush=True)
    bonus, opt_data = bonus_data(d)
    print("bonus !=0", int((bonus != 0).sum()), "opt finite", int(np.isfinite(opt_data).any(1).sum()), flush=True)
    S0 = diem_S(d, None)
    S1 = diem_S(d, bonus)
    opt0 = np.full((len(d), 6), np.nan)
    # warmup
    i0 = 400
    i1 = len(d)
    t = d["t"].to_numpy()
    i_oos = int(np.searchsorted(t, np.datetime64("2026-10-01")))
    print("IS bars", i_oos - i0, "OOS", i1 - i_oos, flush=True)

    cfgs = {
        "baseline_HYB_AG": (P_mac_dinh(), S0, opt0),
        "data_S_plus": (P_mac_dinh(), S1, opt_data),
        # bài học sweep: lot 0.5=K5, coef 1.15, G=3, AG 2x
        "bai_hoc_K5_c115_AG2": (P_mac_dinh(K=5, coef=1.15, th=2.0), S1, opt_data),
    }
    # lân cận quanh baseline+data
    for ten, kwargs in [
        ("lan_coef115", dict(coef=1.15)),
        ("lan_G2", dict(G=2.0)),
        ("lan_th2", dict(th=2.0)),
        ("lan_K5", dict(K=5)),
    ]:
        cfgs[ten] = (P_mac_dinh(**kwargs), S1, opt_data)

    hang = []
    eq_luu = {}
    shadow_rows = []
    # warmup numba lần đầu
    print("compile numba...", flush=True)
    _ = go(d, vp, opt0, S0, P_mac_dinh(), i0, min(i0 + 2000, i1))
    print("compiled", f"{time.time()-t0:.1f}s", flush=True)

    for ten, (P, S, opt) in cfgs.items():
        print("chay", ten, flush=True)
        r, x = go(d, vp, opt, S, P, i0, i1)
        row = tom_tat(ten, r)
        # IS/OOS từ đường vốn
        eq = x["eq"]
        eq0 = 10000.0
        # eq indexed from i0
        j_oos = i_oos - i0
        if 0 < j_oos < len(eq):
            is_net = float(eq[j_oos - 1] - eq0)
            oos_net = float(eq[-1] - eq[j_oos - 1])
            peak = eq0
            is_dd = 0.0
            for v in eq[:j_oos]:
                if v > peak: peak = v
                is_dd = max(is_dd, peak - v)
            peak = eq[j_oos - 1]
            oos_dd = 0.0
            for v in eq[j_oos:]:
                if v > peak: peak = v
                oos_dd = max(oos_dd, peak - v)
        else:
            is_net = row["net"]; oos_net = 0; is_dd = row["maxdd"]; oos_dd = 0
        row["is_net"] = round(is_net, 2)
        row["oos_net"] = round(oos_net, 2)
        row["is_dd"] = round(is_dd, 2)
        row["oos_dd"] = round(oos_dd, 2)
        # spread x2
        P2 = P.copy(); P2[16] = float(P[16]) * 2  # spr index
        r2, x2 = go(d, vp, opt, S, P2, i0, i1)
        row["net_sprx2"] = round(r2["net"], 2)
        row["dd_sprx2"] = round(r2["maxdd"], 2)
        row["dat_sprx2"] = bool(r2["net"] > 0 and r2["maxdd"] / 10000 < 0.80 and r2["blown"] < 0)
        sr = sharpe_tu_eq(eq, eq0)
        row["sharpe"] = round(sr, 3)
        row["dsr"] = round(dsr(sr, len(eq), n_trials=len(cfgs) + 11), 3)
        hang.append(row)
        eq_luu[ten] = eq
        # nhật ký bóng (baseline + data)
        if ten in ("baseline_HYB_AG", "data_S_plus"):
            for k in range(len(x["bo"])):
                t_mo = str(d["t"].iloc[int(x["bo"][k])]) if x["bo"][k] >= 0 else ""
                t_dong = "" if x["bc"][k] < 0 else str(d["t"].iloc[int(x["bc"][k])])
                shadow_rows.append(dict(he=ten, mo=t_mo, dong=t_dong or "con_mo",
                                        tang=int(x["blay"][k]), pnl=float(x["bpnl"][k]),
                                        worst=float(x["bworst"][k]), lots=float(x["blots"][k]),
                                        ghi_chu="chi log, khong dat lenh"))
        print(" ", row, flush=True)

    bang = pd.DataFrame(hang)
    bang.to_csv(OUT_KQ / "hyb_vang_is_oos.csv", index=False)
    if shadow_rows:
        pd.DataFrame(shadow_rows).to_csv(SHADOW, index=False)

    # 11 stress trên cấu hình baseline và data_S_plus
    print("stress...", flush=True)
    stress_rows = []
    # 2 grind + 2 gap trên M1 Jun-Nov
    def bien_doi(fn):
        d2 = d.copy()
        fn(d2)
        return d2

    # điểm sâu của baseline
    eq_b = eq_luu["baseline_HYB_AG"]
    i_deep = i0 + int(np.argmin(eq_b))
    def gap(g, i):
        def f(dx):
            for k in ["o", "h", "l", "c", "c5p", "zz_lo"]:
                dx.loc[i:, k] = dx.loc[i:, k] * (1 - g)
        return f
    def grind(tot, days, start="2026-06-01"):
        def f(dx):
            i_s = int(np.searchsorted(t, np.datetime64(start)))
            n = len(dx)
            k = np.zeros(n)
            span = days * 1380
            k[i_s:] = np.minimum(np.arange(n - i_s) / span, 1.0)
            fac = np.exp(np.log(1 - tot) * k)
            for kk in ["o", "h", "l", "c", "c5p", "zz_lo"]:
                dx[kk] = dx[kk] * fac
            for kk in ["a5", "a15", "ah1"]:
                dx[kk] = dx[kk] * fac
        return f

    synth = [
        ("gap-10% tai day von", gap(0.10, i_deep)),
        ("gap-20% tai day von", gap(0.20, i_deep)),
        ("grind-20%/60ngay", grind(0.20, 60)),
        ("grind-35%/120ngay", grind(0.35, 120)),
    ]
    for sn, fn in synth:
        d2 = bien_doi(fn)
        for cn, (P, S, opt) in [("baseline_HYB_AG", cfgs["baseline_HYB_AG"]),
                                ("data_S_plus", cfgs["data_S_plus"])]:
            r, _ = go(d2, vp, opt, S, P, i0, i1)
            row = tom_tat(f"{cn}|{sn}", r)
            row["scenario"] = sn
            row["cfg"] = cn
            stress_rows.append(row)
            print(" stress", cn, sn, row["net"], "dd", row["maxdd"], "blown", row["blown"], flush=True)

    # 7 crash M15 từ parquet (mốc giờ parquet, ghi rõ)
    if M5_PQ.exists():
        m5 = pd.read_parquet(M5_PQ)
        m5 = m5.reset_index()
        if "time" not in m5.columns:
            m5 = m5.rename(columns={m5.columns[0]: "time"})
        m5["time"] = pd.to_datetime(m5["time"])
        m15 = (m5.set_index("time").resample("15min")
               .agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna())
        m15["tick_volume"] = 1.0
        m15 = m15.reset_index()
        for wn, (a, b) in WIN.items():
            w = m15[(m15.time >= a) & (m15.time < b)].copy()
            if len(w) < 200:
                stress_rows.append(dict(ten=f"thieu|{wn}", scenario=wn, cfg="—", net=np.nan, ghi="nến không đủ"))
                continue
            # scale về 4000
            f = 4000.0 / float(w.close.iloc[0])
            for k in ["open", "high", "low", "close"]:
                w[k] = w[k] * f
            dw, vpw = dung_dac_trung(w.rename(columns={"open": "open", "high": "high", "low": "low", "close": "close"}))
            # S chỉ HYB, không có data (lịch sử không có Fxaurum)
            Sw = diem_S(dw, None)
            optw = np.full((len(dw), 6), np.nan)
            i0w = 50
            # M15: ~92 nến/ngày vàng; chỉnh tnd/hexp/deadw/bpd theo nến (P[14]=hexp, 44=deadw, 49=tnd, 52=bpd)
            for cn, Pbase in [("baseline_HYB_AG", P_mac_dinh()), ("data_S_plus", P_mac_dinh())]:
                P = Pbase.copy()
                P[14] = 64     # hexp ~16 giờ
                P[44] = 64     # deadw
                P[49] = 5 * 92 # tnd 5 ngày
                P[52] = 92     # bpd 1 ngày
                r, _ = go(dw, vpw, optw, Sw, P, i0w, len(dw))
                row = tom_tat(f"{cn}|{wn}", r)
                row["scenario"] = wn
                row["cfg"] = cn
                row["scale"] = round(f, 3)
                row["n_nen"] = len(dw)
                stress_rows.append(row)
                print(" crash", cn, wn, "net", row["net"], "dd", row["maxdd"], "blown", row["blown"], flush=True)

    st = pd.DataFrame(stress_rows)
    st.to_csv(OUT_KQ / "hyb_vang_stress.csv", index=False)

    # viết báo cáo
    def md_table(df, cols):
        lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
        for _, r in df.iterrows():
            lines.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
        return "\n".join(lines)

    # sống sót 11 kịch bản
    song = []
    for cn in ["baseline_HYB_AG", "data_S_plus"]:
        sub = st[st["cfg"] == cn] if "cfg" in st.columns else st
        nsc = len(sub)
        n_ok = int((~sub["blown"].astype(bool) & (sub["dd_pct"] < 80)).sum()) if nsc else 0
        te_nhat = float(sub["net"].min()) if nsc else float("nan")
        song.append((cn, n_ok, nsc, te_nhat))

    lines = [
        "# Giai đoạn B — cổng HYB+AG sang vàng XM (đo lường)",
        "",
        "Máy xử lý lệnh: HYB + AG 1,5x (thiết kế 26/11, `E:\\\\backtests\\\\sp500_sys\\\\`). "
        "Cổng vàng: ATR M15, pv=100 USD / 1,00 giá / 1,00 lot, bước lot 0,01 (K=3 → vào 0,03 lot, tương đương ATR-scaled với 3×0,1 lot US500 pv=1). "
        "Spread mặc định 0,20 giá (20 pts M1). Vốn 10.000. Không SL cứng. **Không đặt lệnh thật** (chỉ nhật ký bóng).",
        "",
        f"- Dữ liệu: XM GOLD.i# M1 {raw.time.iloc[0]} → {raw.time.iloc[-1]}, đổi Europe/Athens → UTC+7.",
        "- IS: trước 2026-10-01; OOS: từ 2026-10-01.",
        "- Tín hiệu data (cải thiện điểm S và mức VWAP/POC quy CFD): cụm big-trade ≥50, từ chối VWAP, đảo sweep (kho flow 18–27/11).",
        "",
        "## Kết quả Jun–Nov (và IS/OOS, spread ×2)",
        "",
        md_table(bang, ["ten", "net", "maxdd", "dd_pct", "maxfl", "is_net", "oos_net", "net_sprx2", "dd_sprx2", "sharpe", "dsr", "n_ro", "blown", "dat"]),
        "",
        "Tiêu chí pass: lãi ròng > 0 và max DD < 80% vốn 10.000, không cháy (equity ≤ 0).",
        "",
        "## 11 kịch bản stress",
        "",
        "7 cửa sổ sập theo lịch US500, nến M15 từ parquet XAUUSD (mốc giờ parquet, **không phải** máy chủ XM), scale về 4000. "
        "2 gap và 2 grind trên M1 GOLD.i# Jun–Nov.",
        "",
    ]
    if not st.empty:
        cols = [c for c in ["cfg", "scenario", "net", "maxdd", "dd_pct", "maxfl", "blown", "dat", "n_nen"] if c in st.columns]
        lines.append(md_table(st, cols))
        lines.append("")
        for cn, ok, nsc, tn in song:
            lines.append(f"- {cn}: sống {ok}/{nsc} kịch bản (không cháy và DD<80%). Lãi/lỗ tệ nhất {tn:.0f} USD.")
    lines += [
        "",
        f"Nhật ký bóng: `{SHADOW}` (chỉ ghi, không đặt lệnh).",
        f"Chạy trong {time.time()-t0:.1f} giây.",
        "",
        "Lưu ý: OptionsDb GCZ6 chỉ 19–20/11 và chưa đọc được GEX/max pain qua API trong phiên này, nên trọng số quyền chọn (1,5) gần như không có mức thật.",
    ]
    (OUT_BAO / "GIAI_DOAN_B_HYB.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("XONG B", bang.to_string(index=False), flush=True)
    print("stress n", len(st), "bao", OUT_BAO / "GIAI_DOAN_B_HYB.md", "dt", time.time()-t0, flush=True)


if __name__ == "__main__":
    main()
