# -*- coding: utf-8 -*-
"""Gắn quy tắc data P1 (qua phong_cach_tay.tin_hieu_data, không sửa file đó) vào cụm tay_v2.

- Đo sự khớp với cụm lịch sử lãi/lỗ của Anh.
- Dùng 4 luật vàng ĐẠT + luật ưu tiên big30>delta15>mức làm lọc vào/xác nhận.
- Kiểm 7 bước. Không đặt lệnh thật.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import phong_cach_tay.tin_hieu_data as td  # noqa: E402  # KHÔNG sửa file này
from phong_cach_tay.ma.may import SPEC  # noqa: E402
from phong_cach_tay.ma.may_v2 import P_v2  # noqa: E402
from phong_cach_tay.ma.chay_v2 import (  # noqa: E402
    tai_m1_vn, dung_dac_trung, them_rej_dn, diem_S, diem_S_short, bonus_data,
    lap_tin, go, tom_tat, is_oos_row, md_table, gio_phien,
)
from vang.ma.chay_hyb_vang import dsr, sharpe_tu_eq  # noqa: E402

OUT_BAO = ROOT / "phong_cach_tay" / "bao_cao"
OUT_KQ = ROOT / "phong_cach_tay" / "ket_qua"
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

# 4 luật vàng ĐẠT (P1, TB 60′, sau phí) — dựng từ cột generator + VWAP/POC/VA trên F
LUAT_VANG = [
    ("big30_poc_win", "big30_theo NGUOC poc_cham_bat", 7.908, 34),
    ("big30_vwap", "big30_theo + vwap_cat_theo", 6.929, 58),
    ("d15_vahfade", "delta15_theo + vah_val_fade", 2.972, 125),
    ("big30_d15", "big30_theo + delta15_theo", 2.007, 387),
]


def _hold(phien, x, H=15):
    s = pd.Series(np.where(x != 0, x, np.nan))
    return s.groupby(phien).transform(lambda q: q.ffill(limit=H)).fillna(0).values


def them_to_hop_vang(F: pd.DataFrame) -> pd.DataFrame:
    """Thêm tổ hợp ĐẠT P1 (không sửa generator). Cần o,h,l,c,vol,phien,big30,delta15,big30_giu,delta15_giu,poc,vah,val."""
    F = F.copy()
    c = F.c.values
    h = F.h.values
    l = F.l.values
    pc = np.r_[np.nan, c[:-1]]
    poc, vah, val = F.poc.values, F.vah.values, F.val.values
    poc_b = np.zeros(len(F))
    t = (l <= poc) & (h >= poc)
    poc_b[t & (pc > poc)] = 1
    poc_b[t & (pc < poc)] = -1
    vah_f = np.zeros(len(F))
    vah_f[(h >= vah) & (c < vah)] = -1
    vah_f[(l <= val) & (c > val)] = 1
    # VWAP phiên (cùng công thức P1)
    tp = (F.h + F.l + F.c) / 3
    F["_tpv"] = tp * F.vol
    cv = F.groupby("phien")["vol"].cumsum()
    vwap = F.groupby("phien")["_tpv"].cumsum() / cv.replace(0, np.nan)
    vw = vwap.to_numpy()
    vwap_cat = np.zeros(len(F))
    vwap_cat[(pc < vw) & (c > vw)] = 1
    vwap_cat[(pc > vw) & (c < vw)] = -1
    F.drop(columns=["_tpv"], inplace=True)
    F["poc_cham_bat"] = poc_b
    F["vah_val_fade"] = vah_f
    F["vwap_cat"] = vwap_cat
    hp, hv, hvah = _hold(F.phien.values, poc_b), _hold(F.phien.values, vwap_cat), _hold(F.phien.values, vah_f)
    big, d15 = F.big30.values, F.delta15.values
    gd = F.delta15_giu.values
    F["big30_poc_win"] = np.where((big != 0) & (hp == -big), big, 0.0)
    F["big30_vwap"] = np.where((big != 0) & (hv == big), big, 0.0)
    F["d15_vahfade"] = np.where((d15 != 0) & (hvah == d15), d15, 0.0)
    F["big30_d15"] = np.where((big != 0) & (gd == big), big, 0.0)
    # ưu tiên khi gán union: d15_vah < big_d15 < vwap < poc_win (big thắng)
    uni = F["d15_vahfade"].to_numpy().copy()
    uni = np.where(F["big30_d15"].values != 0, F["big30_d15"].values, uni)
    uni = np.where(F["big30_vwap"].values != 0, F["big30_vwap"].values, uni)
    uni = np.where(F["big30_poc_win"].values != 0, F["big30_poc_win"].values, uni)
    F["union4"] = uni
    # mức bị big30 ngược: cấm
    F["muc_bi_cam"] = ((vah_f != 0) & (F.big30_giu.values == -vah_f)) | ((poc_b != 0) & (F.big30_giu.values == -poc_b))
    return F


def ms_m1_tu_t_vn(t_vn: pd.Series) -> np.ndarray:
    t = pd.to_datetime(t_vn).dt.tz_localize("Asia/Saigon", ambiguous="infer", nonexistent="shift_forward")
    return t.dt.tz_convert("UTC").dt.tz_localize(None).values.astype("datetime64[ms]").astype("int64")


def chieu(F, ms, cot, tre_ms=60_000, giu_phut=15):
    return td.len_m1(F, ms, cot, tre_ms=tre_ms, giu_phut=giu_phut)


def gan_cum_lich_su(d, M, sym_xm, extra_flags=None):
    if not POS_F.exists():
        return pd.DataFrame()
    pos = pd.read_csv(POS_F)
    pos["t0"] = pd.to_datetime(pos["t0"], utc=True).dt.tz_convert("Asia/Saigon").dt.tz_localize(None)
    g = pos[pos["symbol"] == sym_xm].copy()
    if g.empty:
        return g
    tt = d["t"].to_numpy()
    idx = np.clip(np.searchsorted(tt, g["t0"].to_numpy(), side="right") - 1, 0, len(d) - 1)
    g["bar"] = idx
    for k, arr in M.items():
        g[k] = np.asarray(arr)[idx]
    if extra_flags:
        for k, arr in extra_flags.items():
            g[k] = np.asarray(arr)[idx]
    g["gio"] = g["t0"].dt.hour
    g["phien"] = g["gio"].map(gio_phien)
    g["ngay"] = g["t0"].dt.strftime("%Y-%m-%d")
    g["lot01"] = g["vol"] <= 0.11
    g["nhanh"] = g["hold_min"] < 5
    g["lai"] = g["pnl"] > 0
    side = np.where(g["side"] == "buy", 1.0, -1.0)
    for k in [c for c in g.columns if c in list(M) + list(extra_flags or {})]:
        g[k + "_cung"] = np.sign(g[k]) == side
        g[k + "_nguoc"] = (np.sign(g[k]) == -side) & (g[k] != 0)
        g[k + "_co"] = g[k] != 0
    return g


def bang_khop(g: pd.DataFrame, cots: list[str]) -> pd.DataFrame:
    slices = {
        "tat_ca": g,
        "thang": g[g.lai],
        "thua": g[~g.lai],
        "nhanh_lai": g[g.nhanh & g.lai],
        "30p_4h": g[(g.hold_min >= 30) & (g.hold_min < 240)],
        "lot_le_0.1": g[g.lot01],
        "lot_le_0.1_nhanh": g[g.lot01 & g.nhanh],
        "tru_25-11": g[g.ngay != "2026-11-25"] if "ngay" in g.columns else g,
    }
    rows = []
    for name, h in slices.items():
        row = dict(nhom=name, n=int(len(h)), pnl=round(float(h.pnl.sum()), 2) if len(h) else 0,
                   wr=round(float(h.lai.mean() * 100), 1) if len(h) else None)
        for c in cots:
            if not len(h):
                row[f"{c}_co"] = row[f"{c}_cung"] = row[f"{c}_nguoc"] = None
                continue
            row[f"{c}_co"] = round(float(h[c + "_co"].mean() * 100), 1) if (c + "_co") in h else None
            row[f"{c}_cung"] = round(float(h[c + "_cung"].mean() * 100), 1) if (c + "_cung") in h else None
            row[f"{c}_nguoc"] = round(float(h[c + "_nguoc"].mean() * 100), 1) if (c + "_nguoc") in h else None
        rows.append(row)
    return pd.DataFrame(rows)


def chay_stress(sym, d, roll, o, h, l, c, t, i0, i1, i_deep, cfgs, mains):
    rows = []

    def gap_fn(g, i):
        def f(oo, hh, ll, cc):
            oo, hh, ll, cc = oo.copy(), hh.copy(), ll.copy(), cc.copy()
            fac = np.ones(len(cc)); fac[i:] = 1 - g
            return oo * fac, hh * fac, ll * fac, cc * fac
        return f

    def grind_fn(tot, days, start="2026-06-01"):
        def f(oo, hh, ll, cc):
            oo, hh, ll, cc = oo.copy(), hh.copy(), ll.copy(), cc.copy()
            i_s = int(np.searchsorted(t, np.datetime64(start)))
            n = len(cc); k = np.zeros(n); span = days * 1380
            k[i_s:] = np.minimum(np.arange(n - i_s) / max(span, 1), 1.0)
            fac = np.exp(np.log(1 - tot) * k)
            return oo * fac, hh * fac, ll * fac, cc * fac
        return f

    for sn, fn in [
        ("gap-10% tai day von", gap_fn(0.10, i_deep)),
        ("gap-20% tai day von", gap_fn(0.20, i_deep)),
        ("grind-20%/60ngay", grind_fn(0.20, 60)),
        ("grind-35%/120ngay", grind_fn(0.35, 120)),
    ]:
        o2, h2, l2, c2 = fn(o, h, l, c)
        for cn in mains:
            P, sig = cfgs[cn]
            res, *_ = go(o2, h2, l2, c2, roll, sig, P, i0, i1)
            row = tom_tat(f"{cn}|{sn}", res)
            row.update(scenario=sn, cfg=cn, sym=sym)
            rows.append(row)
            print(f"  stress {cn} {sn} net={row['net']} dd={row['maxdd']} blown={row['blown']}", flush=True)
    return rows


def main():
    t0 = time.time()
    OUT_BAO.mkdir(parents=True, exist_ok=True)
    OUT_KQ.mkdir(parents=True, exist_ok=True)
    print("dung generator", td.__file__, flush=True)

    # ----- XAU đặc trưng + tín hiệu P1 -----
    print("nap GOLD M1...", flush=True)
    raw_x = tai_m1_vn(SPEC["XAU"]["m1"])
    dx, _ = dung_dac_trung(raw_x)
    rej_dn_x = them_rej_dn(dx, raw_x)
    slx, ssx = diem_S(dx, None), diem_S_short(dx, rej_dn_x)
    bonus, _ = bonus_data(dx)
    sig_chi = lap_tin(dx, slx, ssx, None, "chi_bao", "lu")
    ms_x = ms_m1_tu_t_vn(dx["t"])
    print("tao tin hieu GC (generator P1)...", flush=True)
    Fg, Mx_off = td.tao("GC", ms_x)  # mặc định tre=120s, giu=1'
    Fg = them_to_hop_vang(Fg)
    cot_gc = ["big30", "delta15", "big30_giu", "delta15_giu", "uu_tien", "sig_GC",
              "poc_cham_bat", "vah_val_fade", "vwap_cat",
              "big30_poc_win", "big30_vwap", "d15_vahfade", "big30_d15", "union4"]
    Mx = chieu(Fg, ms_x, cot_gc, tre_ms=60_000, giu_phut=15)
    # tín hiệu vào
    def s_from(arr):
        return np.asarray(arr, dtype=np.float64)

    sigs_x = {
        "tay_v2": sig_chi,
        "p1_sig_GC_mac_dinh": s_from(Mx_off["sig_GC"]),
        "p1_union4": s_from(Mx["union4"]),
        "p1_big30_d15": s_from(Mx["big30_d15"]),
        "p1_d15_vahfade": s_from(Mx["d15_vahfade"]),
        "p1_big30_vwap": s_from(Mx["big30_vwap"]),
        "p1_big30_poc_win": s_from(Mx["big30_poc_win"]),
        "p1_uu_tien": np.sign(s_from(Mx["uu_tien"])),
        "tay_v2_xac_nhan_p1": np.where((sig_chi != 0) & (s_from(Mx["union4"]) == sig_chi), sig_chi, 0.0),
        "tay_v2_chan_big_nguoc": np.where(
            (sig_chi != 0) & (s_from(Mx["big30_giu"]) == -sig_chi), 0.0, sig_chi),
    }
    print("XAU n_sig", {k: int((v != 0).sum()) for k, v in sigs_x.items()},
          "F", Fg.phut_ms.min(), Fg.phut_ms.max(), flush=True)

    kh_x = gan_cum_lich_su(dx, Mx, "GOLD.i#")
    cots_kh = ["big30_giu", "delta15_giu", "union4", "big30_d15", "d15_vahfade",
               "big30_vwap", "big30_poc_win", "uu_tien", "sig_GC"]
    # sig_GC 15' from Mx (not official 1')
    bang_x = bang_khop(kh_x, cots_kh)
    bang_x.to_csv(OUT_KQ / "v2_p1_khop_XAU.csv", index=False)
    print("KHOP XAU\n", bang_x.to_string(index=False), flush=True)

    # ----- US500 -----
    print("nap US500 M1...", flush=True)
    raw_s = tai_m1_vn(SPEC["US500"]["m1"])
    ds, _ = dung_dac_trung(raw_s)
    rej_dn_s = them_rej_dn(ds, raw_s)
    sls, sss = diem_S(ds, None), diem_S_short(ds, rej_dn_s)
    sig_chi_s = lap_tin(ds, sls, sss, None, "chi_bao", "lu")
    ms_s = ms_m1_tu_t_vn(ds["t"])
    print("tao tin hieu ES...", flush=True)
    Fe, Me_off = td.tao("ES", ms_s)
    cot_es = ["big30", "delta15", "big30_giu", "delta15_giu", "uu_tien", "sig_ES",
              "vah_val_pha", "cvd_pk", "muc_fade", "muc_hop_le"]
    Me = chieu(Fe, ms_s, cot_es, tre_ms=60_000, giu_phut=15)
    # tổ hợp ĐẠT ES: vah_val_pha; cvd_pk + delta15 cùng chiều
    cvd, d15g = Fe.cvd_pk.values, Fe.delta15_giu.values
    Fe = Fe.copy()
    Fe["cvd_d15"] = np.where((cvd != 0) & (d15g == cvd), cvd, 0.0)
    Me.update(chieu(Fe, ms_s, ["cvd_d15"], tre_ms=60_000, giu_phut=15))
    sigs_s = {
        "tay_v2": sig_chi_s,
        "p1_sig_ES_mac_dinh": s_from(Me_off["sig_ES"]),
        "p1_vah_pha": s_from(Me["vah_val_pha"]),
        "p1_cvd_d15": s_from(Me["cvd_d15"]),
        "p1_uu_tien": np.sign(s_from(Me["uu_tien"])),
        "tay_v2_xac_nhan_p1": np.where(
            (sig_chi_s != 0) & (s_from(Me_off.get("sig_ES", Me["sig_ES"])) == sig_chi_s)
            | ((sig_chi_s != 0) & (s_from(Me["vah_val_pha"]) == sig_chi_s))
            | ((sig_chi_s != 0) & (s_from(Me["cvd_d15"]) == sig_chi_s)),
            sig_chi_s, 0.0),
        "tay_v2_chan_big_nguoc": np.where(
            (sig_chi_s != 0) & (s_from(Me["big30_giu"]) == -sig_chi_s), 0.0, sig_chi_s),
    }
    # fix xac_nhan precedence: write clearly
    u_es = np.where(s_from(Me["vah_val_pha"]) != 0, s_from(Me["vah_val_pha"]), s_from(Me["cvd_d15"]))
    sigs_s["p1_union_es"] = u_es
    sigs_s["tay_v2_xac_nhan_p1"] = np.where((sig_chi_s != 0) & (u_es == sig_chi_s), sig_chi_s, 0.0)
    print("US500 n_sig", {k: int((v != 0).sum()) for k, v in sigs_s.items()}, flush=True)

    kh_s = gan_cum_lich_su(ds, Me, "US500Cash#")
    bang_s = bang_khop(kh_s, ["big30_giu", "delta15_giu", "uu_tien", "sig_ES", "vah_val_pha", "cvd_d15"])
    bang_s.to_csv(OUT_KQ / "v2_p1_khop_US500.csv", index=False)
    print("KHOP US500\n", bang_s.to_string(index=False), flush=True)

    # ----- 7 bước -----
    all_bang, all_st, shadow, meta = [], [], [], {}
    jobs = [
        ("XAU", dx, raw_x, sigs_x, ["tay_v2", "p1_union4", "p1_big30_d15", "p1_sig_GC_mac_dinh",
                                     "tay_v2_xac_nhan_p1", "tay_v2_chan_big_nguoc", "p1_uu_tien"]),
        ("US500", ds, raw_s, sigs_s, ["tay_v2", "p1_union_es", "p1_vah_pha", "p1_sig_ES_mac_dinh",
                                       "tay_v2_xac_nhan_p1", "tay_v2_chan_big_nguoc", "p1_uu_tien"]),
    ]
    # also run remaining gold filters (no full stress except mains)
    gold_extra = ["p1_d15_vahfade", "p1_big30_vwap", "p1_big30_poc_win"]
    us_extra = ["p1_cvd_d15"]

    for sym, d, raw, sigs, mains_run in jobs:
        i0, i1 = 400, len(d)
        t = d["t"].to_numpy()
        i_oos = int(np.searchsorted(t, np.datetime64("2026-10-01")))
        o, h, l, c = d.o.to_numpy(np.float64), d.h.to_numpy(np.float64), d.l.to_numpy(np.float64), d.c.to_numpy(np.float64)
        roll = d.roll.to_numpy()
        P = P_v2(sym)
        print(f"[{sym}] compile...", flush=True)
        _ = go(o, h, l, c, roll, sigs["tay_v2"], P, i0, min(i0 + 2000, i1))
        cfgs = {ten: (P, sigs[ten]) for ten in sigs}
        hang, eq_luu = [], {}
        run_list = list(dict.fromkeys(mains_run + (gold_extra if sym == "XAU" else us_extra)))
        for ten in run_list:
            print(f"[{sym}] chay {ten} n={(sigs[ten]!=0).sum()}", flush=True)
            res, eq, bo, bc, bpnl, bworst, blots = go(o, h, l, c, roll, sigs[ten], P, i0, i1)
            row = tom_tat(ten, res)
            row = is_oos_row(row, res, eq, i0, i_oos, P)
            P2 = P.copy(); P2[10] = float(P[10]) * 2
            res2, *_ = go(o, h, l, c, roll, sigs[ten], P2, i0, i1)
            row["net_sprx2"] = round(float(res2[0]), 2)
            row["dd_sprx2"] = round(float(res2[1]), 2)
            row["dat_sprx2"] = bool(res2[0] > 0 and res2[1] / EQ0 < 0.80 and res2[10] < 0)
            sr = sharpe_tu_eq(eq, EQ0)
            row["sharpe"] = round(sr, 3)
            row["dsr"] = round(dsr(sr, len(eq), n_trials=len(run_list) + 11), 3)
            row["sym"] = sym
            hang.append(row)
            eq_luu[ten] = eq
            if ten in mains_run[:4]:
                for k in range(len(bo)):
                    shadow.append(dict(sym=sym, he=ten,
                                       mo=str(d.t.iloc[int(bo[k])]) if bo[k] >= 0 else "",
                                       dong="" if bc[k] < 0 else str(d.t.iloc[int(bc[k])]),
                                       pnl=float(bpnl[k]), worst=float(bworst[k]), lots=float(blots[k]),
                                       ghi_chu="chi log, khong dat lenh"))
            print(" ", row, flush=True)
        bang = pd.DataFrame(hang)
        # stress on key filters
        key = [x for x in (["p1_union4", "tay_v2_xac_nhan_p1", "tay_v2_chan_big_nguoc"] if sym == "XAU"
                           else ["p1_union_es", "tay_v2_xac_nhan_p1", "tay_v2_chan_big_nguoc"]) if x in eq_luu]
        if "tay_v2" in eq_luu:
            key = ["tay_v2"] + key
        i_deep = i0 + int(np.argmin(eq_luu.get(key[0], eq_luu["tay_v2"])))
        print(f"[{sym}] stress {key}...", flush=True)
        st_rows = chay_stress(sym, d, roll, o, h, l, c, t, i0, i1, i_deep, cfgs, key)
        # crash M5: no historical Fxaurum — P1 filters are 0, tay_v2_chan_big stays, p1 entries silent
        pq = SPEC[sym]["pq"]
        if pq.exists():
            m5 = pd.read_parquet(pq).reset_index()
            if "time" not in m5.columns:
                m5 = m5.rename(columns={m5.columns[0]: "time"})
            m5["time"] = pd.to_datetime(m5["time"])
            m5["tick_volume"] = 1.0
            for wn, (a, b) in WIN.items():
                w = m5[(m5.time >= a) & (m5.time < b)].copy()
                if len(w) < 200:
                    st_rows.append(dict(ten=f"thieu|{wn}", scenario=wn, cfg="—", net=np.nan, sym=sym))
                    continue
                fsc = float(SPEC[sym]["scale_crash"]) / float(w.close.iloc[0])
                for k in ["open", "high", "low", "close"]:
                    w[k] *= fsc
                dw, _ = dung_dac_trung(w)
                rdn = them_rej_dn(dw, w)
                sigw = lap_tin(dw, diem_S(dw, None), diem_S_short(dw, rdn), None, "chi_bao", "lu")
                # p1 = 0 (không có tick lịch sử)
                zero = np.zeros(len(dw))
                Pw = P_v2(sym); i0w = 50
                for cn, sigw_ in [("tay_v2", sigw), ("tay_v2_chan_big_nguoc", sigw),
                                  ("p1_union4" if sym == "XAU" else "p1_union_es", zero),
                                  ("tay_v2_xac_nhan_p1", zero)]:
                    if cn not in key:
                        continue
                    rw, *_ = go(dw.o.to_numpy(np.float64), dw.h.to_numpy(np.float64),
                                dw.l.to_numpy(np.float64), dw.c.to_numpy(np.float64),
                                dw.roll.to_numpy(), sigw_, Pw, i0w, len(dw))
                    row = tom_tat(f"{cn}|{wn}", rw)
                    row.update(scenario=wn, cfg=cn, scale=round(fsc, 3), n_nen=len(dw), sym=sym)
                    st_rows.append(row)
                    print(f"  crash {cn} {wn} net={row['net']} dd={row['maxdd']} blown={row['blown']}", flush=True)
        all_bang.append(bang)
        all_st.append(pd.DataFrame(st_rows))
        meta[sym] = dict(n=len(raw), t0=str(raw.time.iloc[0]), t1=str(raw.time.iloc[-1]),
                         is_bars=int(i_oos - i0), oos_bars=int(i1 - i_oos),
                         n_sig={k: int((sigs[k] != 0).sum()) for k in sigs})

    bang = pd.concat(all_bang, ignore_index=True)
    st = pd.concat(all_st, ignore_index=True)
    bang.to_csv(OUT_KQ / "v2_p1_is_oos.csv", index=False)
    st.to_csv(OUT_KQ / "v2_p1_stress.csv", index=False)
    if shadow:
        pd.DataFrame(shadow).to_csv(OUT_KQ / "shadow_tay_v2_p1.csv", index=False)
    (OUT_KQ / "v2_p1_meta.json").write_text(json.dumps(dict(meta=meta, generator=td.__file__), ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    lines = [
        "# tay_v2 + lọc tín hiệu data Phần 1",
        "",
        f"Xuất: {pd.Timestamp.now(tz='Asia/Saigon')} (giờ Việt Nam, UTC+7).",
        "",
        "Dùng `phong_cach_tay/tin_hieu_data.py` (không sửa). Tổ hợp vàng ĐẠT thêm từ cột generator + VWAP/POC/VA trên cùng bảng phút (đúng định nghĩa `p1_quy_tac.py`).",
        "Chiều lên M1: trễ 60 giây (vào mở nến m+1 như P1), giữ 15 phút. `p1_sig_*_mac_dinh` dùng `tao()` mặc định (trễ 120 giây, giữ 1 phút).",
        "Vốn 10.000 USD = 1.000.000 USC. Không đặt lệnh thật. Cửa sổ sập M5 không có tick Fxaurum — lọc P1 = 0.",
        "",
        "## Khớp với cụm lịch sử của Anh",
        "",
        "### Vàng (GOLD.i#)",
        "",
        md_table(bang_x, list(bang_x.columns)),
        "",
        "Cột `_co` = % vị thế có tín hiệu ≠ 0 tại lúc vào (giữ 15′). `_cung` / `_nguoc` so với chiều lệnh.",
        "",
        "### US500",
        "",
        md_table(bang_s, list(bang_s.columns)),
        "",
        "## Kiểm 7 bước",
        "",
    ]
    for sym in ["XAU", "US500"]:
        sub = bang[bang["sym"] == sym]
        sts = st[st["sym"] == sym] if "sym" in st.columns else st
        m = meta[sym]
        lines += [
            f"### {sym}",
            "",
            f"- M1 {m['t0']} → {m['t1']}. Số bar có tín hiệu: {m['n_sig']}.",
            "",
            md_table(sub, [c for c in ["ten", "net", "maxdd", "dd_pct", "maxfl", "is_net", "oos_net",
                                       "net_sprx2", "dd_sprx2", "sharpe", "dsr", "n_en", "n_tp", "blown", "dat", "dat_sprx2"] if c in sub.columns]),
            "",
        ]
        if not sts.empty:
            cols = [c for c in ["cfg", "scenario", "net", "maxdd", "dd_pct", "blown", "dat", "n_nen"] if c in sts.columns]
            lines += [md_table(sts, cols), ""]
            for cn in sts["cfg"].dropna().unique():
                if cn == "—":
                    continue
                ss = sts[sts.cfg == cn]
                n_ok = int((~ss.blown.astype(bool) & (ss.dd_pct < 80)).sum())
                te = float(ss.net.min())
                lines.append(f"- {cn}: sống {n_ok}/{len(ss)} (không cháy, DD<80%). Tệ nhất {te:.0f} USD.")
            lines.append("")
    lines += [f"Chạy {time.time()-t0:.1f} giây. Nhật ký bóng: `ket_qua/shadow_tay_v2_p1.csv`."]
    (OUT_BAO / "BAO_CAO_V2_P1.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("XONG P1", bang.to_string(index=False), flush=True)
    print("dt", time.time() - t0, flush=True)


if __name__ == "__main__":
    main()
