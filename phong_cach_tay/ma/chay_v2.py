# -*- coding: utf-8 -*-
"""tay_v2: ngữ cảnh vào lệnh của Anh + kiểm 7 bước XAU rồi US500. Không đặt lệnh thật."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from vang.ma.chay_hyb_vang import (  # noqa: E402
    dung_dac_trung, diem_S, bonus_data, tai_xm_m1_vn, dsr, sharpe_tu_eq,
)
from phong_cach_tay.ma.may import S_xac_nhan, SPEC  # noqa: E402
from phong_cach_tay.ma.may_v2 import P_v2, run as run_v2  # noqa: E402
from vang.ma.chay_hyb_vang import XM_M1  # noqa: E402

OUT_BAO = ROOT / "phong_cach_tay" / "bao_cao"
OUT_KQ = ROOT / "phong_cach_tay" / "ket_qua"
DU = ROOT / "phong_cach_tay" / "du_lieu"
POS_F = OUT_KQ / "vi_the_dong.csv"
EQ0 = 10000.0
WIN = {
    "Q4-2018": ("2018-09-25", "2019-02-28"),
    "Covid 02-04/2020": ("2020-02-10", "2020-07-31"),
    "2022 H1": ("2021-12-28", "2022-07-31"),
    "2022 08-10": ("2022-08-12", "2022-12-15"),
    "08-10/2023": ("2023-07-25", "2023-12-15"),
    "07-08/2024": ("2024-07-10", "2024-09-30"),
    "02-04/2025": ("2025-02-15", "2025-07-15"),
}


def rsi(c, n=14):
    d = np.diff(c, prepend=c[0])
    up = pd.Series(np.maximum(d, 0)).ewm(alpha=1 / n, adjust=False).mean()
    dn = pd.Series(np.maximum(-d, 0)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn.replace(0, 1e-9))).to_numpy()


def them_rej_dn(d: pd.DataFrame, raw: pd.DataFrame) -> np.ndarray:
    g = raw.set_index("time")
    x5 = g.resample("5min").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    rng = (x5.high - x5.low).replace(0, np.nan)
    rej = (((x5.high - np.maximum(x5.open, x5.close)) / rng >= 0.5) & (x5.close <= x5.high - 0.6 * rng)).astype(float)
    # known() from prep
    from importlib.util import spec_from_file_location, module_from_spec
    spec = spec_from_file_location("rh_prep_v2", "/workspace/backtests/rapid_hedge/prep.py")
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    arr = mod.known(d["t"], x5.index, rej.to_numpy(), "5min")
    return pd.Series(arr).shift(1).bfill().fillna(0).to_numpy()


def diem_S_short(d: pd.DataFrame, rej_dn: np.ndarray) -> np.ndarray:
    s = ((d["bbz"].to_numpy() > 2).astype(np.int16)
         + (rej_dn > 0).astype(np.int16)
         + (d["usopen"].to_numpy() > 0).astype(np.int16)
         + (d["reg"].to_numpy() < 0.8).astype(np.int16)
         - (d["vwz"].to_numpy() > 2).astype(np.int16))
    return s.astype(np.float64)


def tai_m1_vn(path: Path) -> pd.DataFrame:
    m = pd.read_csv(path, parse_dates=["time"])
    t = m["time"].dt.tz_localize("Europe/Athens", ambiguous="infer", nonexistent="shift_forward")
    m = m.copy()
    m["time"] = t.dt.tz_convert("Asia/Saigon").dt.tz_localize(None)
    return m


def gio_phien(h):
    if 7 <= h < 14:
        return "chau_a_7-14"
    if 14 <= h < 20:
        return "london_14-20"
    return "my_20-07"


def lap_tin(d, sl, ss, bonus, che_do="chi_bao", phien="lu"):
    """che_do: chi_bao | xac_nhan | chi_phien (vào khi có phiên, S>=0 không chặn). phien: all|lu|us."""
    hr = d["t"].dt.hour.to_numpy()
    if phien == "us":
        mask = (hr >= 20) | (hr < 7)
    elif phien == "lu":
        mask = (hr >= 14) | (hr < 7)
    else:
        mask = np.ones(len(d), dtype=bool)
    sig = np.zeros(len(d), dtype=np.float64)
    if che_do == "chi_phien":
        # không dùng: quá dày. Dùng S>=1 hoặc short.
        pass
    if bonus is None:
        bl, bs = sl, ss
    else:
        bl = S_xac_nhan(sl, bonus)
        bs = S_xac_nhan(ss, np.where(bonus != 0, -bonus, 0))  # data âm = thuận short
    if che_do == "xac_nhan":
        long_ok, short_ok = bl, bs
    else:
        long_ok, short_ok = sl, ss
    long = (long_ok >= 1) & mask
    short = (short_ok >= 1) & mask
    sig[long] = 1
    sig[short & ~long] = -1
    return sig


def tom_tat(ten, res, eq0=EQ0):
    net, maxdd, maxfl, n_en, n_tp, n_dca, n_hd, n_bk, max_tix, max_lots, blown, nb, cash = res
    dd_pct = maxdd / eq0 if eq0 else 0
    dat = (net > 0) and (dd_pct < 0.80) and (blown < 0)
    return dict(
        ten=ten, net=round(float(net), 2), maxdd=round(float(maxdd), 2),
        dd_pct=round(float(dd_pct) * 100, 2), maxfl=round(float(maxfl), 2),
        n_en=int(n_en), n_tp=int(n_tp), n_dca=int(n_dca), n_hd=int(n_hd),
        n_bk=int(n_bk), n_ro=int(nb), max_tix=int(max_tix),
        maxlots=round(float(max_lots), 2), blown=bool(blown >= 0), dat=bool(dat),
    )


def md_table(df, cols):
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(lines)


def ngu_canh(d, sl, ss, bonus, rej_dn):
    """Gắn điều kiện chỉ báo/Fxaurum vào từng vị thế vàng của Anh."""
    if not POS_F.exists():
        return pd.DataFrame(), {}
    pos = pd.read_csv(POS_F)
    pos["t0"] = pd.to_datetime(pos["t0"], utc=True).dt.tz_convert("Asia/Saigon").dt.tz_localize(None)
    g = pos[pos["symbol"] == "GOLD.i#"].copy()
    tt = d["t"].to_numpy()
    idx = np.searchsorted(tt, g["t0"].to_numpy(), side="right") - 1
    idx = np.clip(idx, 0, len(d) - 1)
    g["bar"] = idx
    g["S_long"] = sl[idx]
    g["S_short"] = ss[idx]
    g["bbz"] = d["bbz"].to_numpy()[idx]
    g["vwz"] = d["vwz"].to_numpy()[idx]
    g["rej"] = d["rej"].to_numpy()[idx]
    g["rej_dn"] = rej_dn[idx]
    g["usopen"] = d["usopen"].to_numpy()[idx]
    g["us"] = d["us"].to_numpy()[idx]
    g["reg"] = d["reg"].to_numpy()[idx]
    g["bonus"] = bonus[idx] if bonus is not None else 0
    g["gio"] = g["t0"].dt.hour
    g["phien"] = g["gio"].map(gio_phien)
    g["ngay"] = g["t0"].dt.strftime("%Y-%m-%d")
    g["lot01"] = g["vol"] <= 0.11
    g["nhanh"] = g["hold_min"] < 5
    g["lai"] = g["pnl"] > 0
    # cùng chiều với S?
    g["S_cung"] = np.where(g["side"] == "buy", g["S_long"] >= 1, g["S_short"] >= 1)
    g["S_diem"] = np.where(g["side"] == "buy", g["S_long"], g["S_short"])
    g["data_cung"] = np.where(g["side"] == "buy", g["bonus"] > 0, g["bonus"] < 0)
    g["data_nguoc"] = np.where(g["side"] == "buy", g["bonus"] < 0, g["bonus"] > 0)

    def rate(h, col):
        if len(h) == 0:
            return None
        return round(float(h[col].mean() * 100), 1)

    slices = {
        "tat_ca": g,
        "thang": g[g.lai],
        "thua": g[~g.lai],
        "nhanh_lai": g[g.nhanh & g.lai],
        "30p_4h": g[(g.hold_min >= 30) & (g.hold_min < 240)],
        "lot_le_0.1": g[g.lot01],
        "lot_le_0.1_nhanh": g[g.lot01 & g.nhanh],
        "tru_25-11": g[g.ngay != "2026-11-25"],
        "my_20-07": g[g.phien == "my_20-07"],
        "london_14-20": g[g.phien == "london_14-20"],
    }
    rows = []
    for name, h in slices.items():
        rows.append(dict(
            nhom=name, n=int(len(h)), pnl=round(float(h.pnl.sum()), 2) if len(h) else 0,
            wr=round(float(h.lai.mean() * 100), 1) if len(h) else None,
            S_cung=rate(h, "S_cung"),
            S_med=round(float(h.S_diem.median()), 2) if len(h) else None,
            usopen=rate(h, "usopen"),
            us=rate(h, "us"),
            rej_thuan=round(float(np.where(h.side == "buy", h.rej > 0, h.rej_dn > 0).mean() * 100), 1) if len(h) else None,
            bb_2sig=round(float(np.where(h.side == "buy", h.bbz < -2, h.bbz > 2).mean() * 100), 1) if len(h) else None,
            data_cung=rate(h, "data_cung"),
            data_nguoc=rate(h, "data_nguoc"),
            data_khac0=round(float((h.bonus != 0).mean() * 100), 1) if len(h) else None,
        ))
    bang = pd.DataFrame(rows)

    # theo giờ: điều kiện
    gio = []
    for hr, h in g.groupby("gio"):
        gio.append(dict(
            gio=int(hr), n=int(len(h)), pnl=round(float(h.pnl.sum()), 1),
            wr=round(float(h.lai.mean() * 100), 1),
            S_cung=rate(h, "S_cung"), usopen=rate(h, "usopen"),
            data_cung=rate(h, "data_cung"),
        ))
    return bang, dict(gio=gio, n=len(g), S_cung_all=rate(g, "S_cung"),
                      S_cung_nhanh=rate(g[g.nhanh & g.lai], "S_cung") if (g.nhanh & g.lai).any() else None)


def go(o, h, l, c, roll, sig, P, i0, i1, atr=None, slope=None, adx=None):
    return run_v2(o, h, l, c, roll, sig, P, i0, i1, atr=atr, slope=slope, adx=adx)


def is_oos_row(row, res, eq, i0, i_oos, P):
    j = i_oos - i0
    eq0 = float(P[14])
    if 0 < j < len(eq):
        is_net = float(eq[j - 1] - eq0)
        oos_net = float(eq[-1] - eq[j - 1])
        peak = eq0
        is_dd = 0.0
        for v in eq[:j]:
            if v > peak:
                peak = v
            is_dd = max(is_dd, peak - v)
        peak = eq[j - 1]
        oos_dd = 0.0
        for v in eq[j:]:
            if v > peak:
                peak = v
            oos_dd = max(oos_dd, peak - v)
    else:
        is_net, oos_net, is_dd, oos_dd = row["net"], 0.0, row["maxdd"], 0.0
    row["is_net"] = round(is_net, 2)
    row["oos_net"] = round(oos_net, 2)
    row["is_dd"] = round(float(is_dd), 2)
    row["oos_dd"] = round(float(oos_dd), 2)
    return row


def chay_sym(sym, raw, d, sl, ss, bonus, t0_wall):
    sp = SPEC[sym]
    i0 = 400
    i1 = len(d)
    t = d["t"].to_numpy()
    i_oos = int(np.searchsorted(t, np.datetime64("2026-10-01")))
    o = d["o"].to_numpy(np.float64)
    h = d["h"].to_numpy(np.float64)
    l = d["l"].to_numpy(np.float64)
    c = d["c"].to_numpy(np.float64)
    roll = d["roll"].to_numpy()

    # tín hiệu
    sig0 = lap_tin(d, sl, ss, None, "chi_bao", "lu")
    sig1 = lap_tin(d, sl, ss, bonus, "xac_nhan", "lu")
    sig_us = lap_tin(d, sl, ss, None, "chi_bao", "us")
    # Vào theo phiên + nến trước giảm/tăng (Anh ít có S>=1 ở lệnh lãi nhanh: 14,6%)
    hr = d["t"].dt.hour.to_numpy()
    mask_lu = (hr >= 14) | (hr < 7)
    prev_dn = d["c"].shift(1) < d["o"].shift(1)
    prev_up = d["c"].shift(1) > d["o"].shift(1)
    sig_ph = np.zeros(len(d), dtype=np.float64)
    sig_ph[(mask_lu & prev_dn.fillna(False)).to_numpy()] = 1
    sig_ph[(mask_lu & prev_up.fillna(False) & ~prev_dn.fillna(False)).to_numpy()] = -1
    print(f"[{sym}] sig chi_bao lu {(sig0!=0).sum()} xac_nhan {(sig1!=0).sum()} us {(sig_us!=0).sum()} phien_dip {(sig_ph!=0).sum()} IS {i_oos-i0} OOS {i1-i_oos}", flush=True)

    cfgs = {
        "tay_v2": (P_v2(sym), sig0),
        "tay_v2_xac_nhan": (P_v2(sym), sig1),
        "tay_v2_usonly": (P_v2(sym), sig_us),
        "tay_v2_phien_dip": (P_v2(sym), sig_ph),
        "lan_tp312": (P_v2(sym, tp=3.12, htp=3.12), sig0),
        "lan_tp522": (P_v2(sym, tp=5.22, htp=5.22), sig0),
        "lan_gap4": (P_v2(sym, gap=4.0), sig0),
        "lan_gap8": (P_v2(sym, gap=8.0), sig0),
        "lan_hgap15": (P_v2(sym, hgap=15.0 if sym == "XAU" else 60.0), sig0),
        "lan_hgap30": (P_v2(sym, hgap=30.0 if sym == "XAU" else 120.0), sig0),
        "lan_maxL10": (P_v2(sym, maxL=10), sig0),
        "lan_maxL40": (P_v2(sym, maxL=40), sig0),
        "lan_maxL80": (P_v2(sym, maxL=80), sig0),
    }
    if sym == "XAU":
        cfgs["lan_tp159"] = (P_v2(sym, tp=1.59, htp=1.59), sig0)

    print(f"[{sym}] compile...", flush=True)
    _ = go(o, h, l, c, roll, sig0, P_v2(sym), i0, min(i0 + 3000, i1))
    print(f"[{sym}] compiled {time.time()-t0_wall:.1f}s", flush=True)

    hang, eq_luu, shadow = [], {}, []
    for ten, (P, sig) in cfgs.items():
        print(f"[{sym}] chay {ten}", flush=True)
        res, eq, bo, bc, bpnl, bworst, blots = go(o, h, l, c, roll, sig, P, i0, i1)
        row = tom_tat(ten, res)
        row = is_oos_row(row, res, eq, i0, i_oos, P)
        P2 = P.copy()
        P2[10] = float(P[10]) * 2  # spr
        res2, eq2, *_ = go(o, h, l, c, roll, sig, P2, i0, i1)
        row["net_sprx2"] = round(float(res2[0]), 2)
        row["dd_sprx2"] = round(float(res2[1]), 2)
        row["dat_sprx2"] = bool(res2[0] > 0 and res2[1] / EQ0 < 0.80 and res2[10] < 0)
        sr = sharpe_tu_eq(eq, EQ0)
        row["sharpe"] = round(sr, 3)
        row["dsr"] = round(dsr(sr, len(eq), n_trials=len(cfgs) + 11), 3)
        row["sym"] = sym
        hang.append(row)
        eq_luu[ten] = eq
        if ten in ("tay_v2", "tay_v2_xac_nhan"):
            for k in range(len(bo)):
                shadow.append(dict(
                    sym=sym, he=ten,
                    mo=str(d["t"].iloc[int(bo[k])]) if bo[k] >= 0 else "",
                    dong="" if bc[k] < 0 else str(d["t"].iloc[int(bc[k])]),
                    pnl=float(bpnl[k]), worst=float(bworst[k]), lots=float(blots[k]),
                    ghi_chu="chi log, khong dat lenh",
                ))
        print(" ", row, flush=True)

    bang = pd.DataFrame(hang)

    # 11 stress on tay_v2 and tay_v2_xac_nhan (and best if different)
    print(f"[{sym}] stress...", flush=True)
    stress_rows = []
    i_deep = i0 + int(np.argmin(eq_luu["tay_v2"]))

    def gap_fn(g, i):
        def f(oo, hh, ll, cc):
            oo, hh, ll, cc = oo.copy(), hh.copy(), ll.copy(), cc.copy()
            oo[i:] *= (1 - g)
            hh[i:] *= (1 - g)
            ll[i:] *= (1 - g)
            cc[i:] *= (1 - g)
            return oo, hh, ll, cc
        return f

    def grind_fn(tot, days, start="2026-06-01"):
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

    mains = ["tay_v2", "tay_v2_xac_nhan", "tay_v2_phien_dip"]
    synth = [
        ("gap-10% tai day von", gap_fn(0.10, i_deep)),
        ("gap-20% tai day von", gap_fn(0.20, i_deep)),
        ("grind-20%/60ngay", grind_fn(0.20, 60)),
        ("grind-35%/120ngay", grind_fn(0.35, 120)),
    ]
    for sn, fn in synth:
        o2, h2, l2, c2 = fn(o, h, l, c)
        for cn in mains:
            P, sig = cfgs[cn]
            res, *_ = go(o2, h2, l2, c2, roll, sig, P, i0, i1)
            row = tom_tat(f"{cn}|{sn}", res)
            row["scenario"] = sn
            row["cfg"] = cn
            row["sym"] = sym
            stress_rows.append(row)
            print(f"  stress {cn} {sn} net={row['net']} dd={row['maxdd']} blown={row['blown']}", flush=True)

    # 7 crash: M5 parquet (mịn hơn M15 vì cạnh <5 phút)
    pq = sp["pq"]
    if pq.exists():
        m5 = pd.read_parquet(pq).reset_index()
        if "time" not in m5.columns:
            m5 = m5.rename(columns={m5.columns[0]: "time"})
        m5["time"] = pd.to_datetime(m5["time"])
        m5 = m5.set_index("time").sort_index()
        m5 = m5.reset_index()
        m5["tick_volume"] = 1.0
        for wn, (a, b) in WIN.items():
            w = m5[(m5.time >= a) & (m5.time < b)].copy()
            if len(w) < 200:
                stress_rows.append(dict(ten=f"thieu|{wn}", scenario=wn, cfg="—", net=np.nan, ghi="nến không đủ", sym=sym))
                continue
            fsc = float(sp["scale_crash"]) / float(w.close.iloc[0])
            for k in ["open", "high", "low", "close"]:
                w[k] = w[k] * fsc
            dw, _vp = dung_dac_trung(w)
            rej_dn = them_rej_dn(dw, w)
            slw = diem_S(dw, None)
            ssw = diem_S_short(dw, rej_dn)
            sigw = lap_tin(dw, slw, ssw, None, "chi_bao", "lu")
            i0w = 50
            Pw = P_v2(sym)
            res, *_ = go(
                dw.o.to_numpy(np.float64), dw.h.to_numpy(np.float64),
                dw.l.to_numpy(np.float64), dw.c.to_numpy(np.float64),
                dw.roll.to_numpy(), sigw, Pw, i0w, len(dw),
            )
            row = tom_tat(f"tay_v2|{wn}", res)
            row["scenario"] = wn
            row["cfg"] = "tay_v2"
            row["scale"] = round(fsc, 3)
            row["n_nen"] = len(dw)
            row["sym"] = sym
            stress_rows.append(row)
            # xac_nhan trùng vì không có Fxaurum lịch sử
            row2 = dict(row)
            row2["ten"] = f"tay_v2_xac_nhan|{wn}"
            row2["cfg"] = "tay_v2_xac_nhan"
            stress_rows.append(row2)
            # phien_dip có tín hiệu khác
            sigp = np.zeros(len(dw), dtype=np.float64)
            hrw = dw["t"].dt.hour.to_numpy()
            mask = (hrw >= 14) | (hrw < 7)
            prev_dn = (dw["c"].shift(1) < dw["o"].shift(1)).fillna(False).to_numpy()
            prev_up = (dw["c"].shift(1) > dw["o"].shift(1)).fillna(False).to_numpy()
            sigp[mask & prev_dn] = 1
            sigp[mask & prev_up & ~prev_dn] = -1
            resp, *_ = go(
                dw.o.to_numpy(np.float64), dw.h.to_numpy(np.float64),
                dw.l.to_numpy(np.float64), dw.c.to_numpy(np.float64),
                dw.roll.to_numpy(), sigp, Pw, i0w, len(dw),
            )
            rowp = tom_tat(f"tay_v2_phien_dip|{wn}", resp)
            rowp["scenario"] = wn
            rowp["cfg"] = "tay_v2_phien_dip"
            rowp["scale"] = round(fsc, 3)
            rowp["n_nen"] = len(dw)
            rowp["sym"] = sym
            stress_rows.append(rowp)
            print(f"  crash tay_v2 {wn} net={row['net']} dd={row['maxdd']} blown={row['blown']}; phien {rowp['net']}/{rowp['maxdd']}", flush=True)

    st = pd.DataFrame(stress_rows)
    meta = dict(
        n=len(raw), t0=str(raw.time.iloc[0]), t1=str(raw.time.iloc[-1]),
        is_bars=int(i_oos - i0), oos_bars=int(i1 - i_oos),
        spr=float(P_v2(sym)[10]), pv=float(P_v2(sym)[11]),
        n_sig=int((sig0 != 0).sum()),
        scale_crash=sp["scale_crash"],
        kieu_nen_crash="M5 parquet (trong nến thận trọng), không phải tick XM",
    )
    return bang, st, shadow, meta


def main():
    t0 = time.time()
    OUT_BAO.mkdir(parents=True, exist_ok=True)
    OUT_KQ.mkdir(parents=True, exist_ok=True)

    print("nap GOLD M1 + dac trung...", flush=True)
    raw_x = tai_m1_vn(SPEC["XAU"]["m1"])
    dx, _vpx = dung_dac_trung(raw_x)
    rej_dn_x = them_rej_dn(dx, raw_x)
    slx = diem_S(dx, None)
    ssx = diem_S_short(dx, rej_dn_x)
    bonus, _opt = bonus_data(dx)
    print("XAU n", len(dx), "bonus!=0", int((bonus != 0).sum()), flush=True)

    # ngữ cảnh
    print("ngu canh vao lenh vang...", flush=True)
    bang_nc, meta_nc = ngu_canh(dx, slx, ssx, bonus, rej_dn_x)
    bang_nc.to_csv(OUT_KQ / "v2_ngu_canh.csv", index=False)
    (OUT_KQ / "v2_ngu_canh_meta.json").write_text(json.dumps(meta_nc, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    bx, stx, shx, mx = chay_sym("XAU", raw_x, dx, slx, ssx, bonus, t0)

    print("nap US500 M1...", flush=True)
    raw_s = tai_m1_vn(SPEC["US500"]["m1"])
    ds, _vps = dung_dac_trung(raw_s)
    rej_dn_s = them_rej_dn(ds, raw_s)
    sls = diem_S(ds, None)
    sss = diem_S_short(ds, rej_dn_s)
    bs, sts, shs, ms = chay_sym("US500", raw_s, ds, sls, sss, None, t0)

    bang = pd.concat([bx, bs], ignore_index=True)
    st = pd.concat([stx, sts], ignore_index=True)
    bang.to_csv(OUT_KQ / "v2_is_oos.csv", index=False)
    st.to_csv(OUT_KQ / "v2_stress.csv", index=False)
    if shx or shs:
        pd.DataFrame(shx + shs).to_csv(OUT_KQ / "shadow_tay_v2.csv", index=False)
    (OUT_KQ / "v2_meta.json").write_text(json.dumps({"XAU": mx, "US500": ms}, ensure_ascii=False, indent=2), encoding="utf-8")

    # báo cáo ngữ cảnh + 7 bước
    lines = [
        "# tay_v2 — ngữ cảnh lệnh tay và kiểm 7 bước",
        "",
        f"Xuất: {pd.Timestamp.now(tz='Asia/Saigon')} (giờ Việt Nam, UTC+7).",
        "",
        "## 0. Lưu ý quan trọng về “cạnh <5 phút”",
        "",
        "Lãi vàng giữ <5 phút (+40.950, WR 97,4%) **tập trung rất mạnh**: 38.523 đến từ 25/11/2026 với lot 1,00 sau khi nạp thêm 900.000 demo. "
        "Ba ngày 20, 21, 25/11 chiếm 98,7% lãi vàng. Trừ 25/11, lệnh <5 phút chỉ còn +2.427 (61 lệnh, WR 100%). "
        "Lệnh lot ≤ 0,10 và giữ <5 phút: n=155, **tất cả lãi**, +5.260,5, khe TP trung vị **4,00 USD**, giữ trung vị 1,40 phút — đây là số dùng để khớp máy (không lấy 3,12 vì đó là hòa trộn với lot 1,00, TP trung vị 1,59).",
        "",
        "Khe DCA 5,47 / 14,5 phút và hedge 21,37 vẫn lấy từ toàn bộ lịch sử (thêm cùng chiều sau >2 giây / vào ngược).",
        "",
        "## 1. Ngữ cảnh vào lệnh (vàng, gắn nến M1 + chỉ báo + Fxaurum)",
        "",
    ]
    if not bang_nc.empty:
        lines += [
            md_table(bang_nc, list(bang_nc.columns)),
            "",
            f"- Tỷ lệ vị thế vàng có điểm S cùng chiều ≥ 1: {meta_nc.get('S_cung_all')}%. Nhóm nhanh-lãi: {meta_nc.get('S_cung_nhanh')}%.",
            "- Nếu tỷ lệ S cùng chiều thấp: Anh vào tay theo quan sát, không đợi đủ điều kiện chỉ báo; máy dùng S≥1 sẽ **bỏ lỡ** nhiều lệnh của Anh, nhưng đó là bộ lọc 'tín hiệu' theo yêu cầu.",
            "",
        ]
    lines += [
        "## 2. Máy tay_v2",
        "",
        "- Vào cụm K lệnh lot cố định khi S (mua) hoặc S_short (bán) ≥ 1, phiên London+Mỹ (14h–07h VN) mặc định.",
        "- TP từng lệnh theo khe giá đã khớp (vàng 4,00; US500 6,53 từ lot ≤0,10 giữ <5 phút lãi).",
        "- DCA lot cố định (hệ số 1,0) mỗi khi giá đi ngược đúng khe (5,47 / 8,32).",
        "- Hedge cụm 5×0,10 khi rổ đi ngược khe hedge (21,37 / 80).",
        "- Đóng cả rổ khi lãi tổng (sau spread) > 0. Không SL cứng.",
        "- Nến M1, trong nến **thận trọng** (nhánh bất lợi/DCA/hedge trước, TP sau). Không có tick XM trên box.",
        "- Vốn 10.000 USD = 1.000.000 USC. Tiêu chí: lãi > 0, DD < 80%, không cháy.",
        "- IS trước 2026-10-01, OOS từ 2026-10-01. Tham số khớp từ lịch sử deal (chủ yếu tháng 11, nằm trong OOS) — có rò thông tin hành vi, không phải tối ưu IS thuần.",
        "",
    ]
    for sym, m in [("XAU", mx), ("US500", ms)]:
        sub = bang[bang["sym"] == sym]
        sts = st[st["sym"] == sym]
        lines += [
            f"## 3. Kết quả {sym}",
            "",
            f"- M1 XM {m['t0']} → {m['t1']}, {m['n']} nến, tín hiệu {m['n_sig']}. IS {m['is_bars']}, OOS {m['oos_bars']}.",
            "",
            md_table(sub, [c for c in ["ten", "net", "maxdd", "dd_pct", "maxfl", "is_net", "oos_net", "net_sprx2", "dd_sprx2", "sharpe", "dsr", "n_en", "n_tp", "n_dca", "n_hd", "n_ro", "max_tix", "maxlots", "blown", "dat", "dat_sprx2"] if c in sub.columns]),
            "",
        ]
        if not sts.empty:
            cols = [c for c in ["cfg", "scenario", "net", "maxdd", "dd_pct", "maxfl", "blown", "dat", "n_nen"] if c in sts.columns]
            lines += ["### Stress", "", md_table(sts, cols), ""]
            for cn in ["tay_v2", "tay_v2_xac_nhan"]:
                ss = sts[sts["cfg"] == cn]
                nsc = len(ss)
                n_ok = int((~ss["blown"].astype(bool) & (ss["dd_pct"] < 80)).sum()) if nsc else 0
                te = float(ss["net"].min()) if nsc else float("nan")
                lines.append(f"- {cn}: sống {n_ok}/{nsc} kịch bản (không cháy và DD<80%). Tệ nhất {te:.0f} USD ({te*100:.0f} USC).")
            lines.append("")

    lines += [
        f"Nhật ký bóng: `phong_cach_tay/ket_qua/shadow_tay_v2.csv`. Chạy {time.time()-t0:.1f} giây. Không đặt lệnh thật.",
        "",
        "Cửa sổ sập dùng nến M5 parquet (mốc giờ parquet, scale 4000/7000), vẫn thô hơn cạnh <5 phút trên M1.",
    ]
    text = "\n".join(lines) + "\n"
    (OUT_BAO / "BAO_CAO_V2.md").write_text(text, encoding="utf-8")
    (OUT_BAO / "NGU_CANH.md").write_text(
        "# Ngữ cảnh vào lệnh (rút từ BAO_CAO_V2)\n\n" + "\n".join(lines[lines.index("## 1. Ngữ cảnh vào lệnh (vàng, gắn nến M1 + chỉ báo + Fxaurum)"):lines.index("## 2. Máy tay_v2")]),
        encoding="utf-8",
    )
    print("XONG V2", bang.to_string(index=False), flush=True)
    print("dt", time.time() - t0, flush=True)


if __name__ == "__main__":
    main()
