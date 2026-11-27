# -*- coding: utf-8 -*-
"""Quét mở rộng lưới nhân lot, gỡ lệnh, hedge — đặc biệt M5/M15/H1. Tiêu chí mới: lãi ròng > 0 và DD < 80%."""
from __future__ import annotations
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pandas as pd
from vang.ma import du_lieu, tin_hieu, mo_phong
from vang.ma import mo_phong_mo_rong as mr

OUT = ROOT / "vang" / "ket_qua"
VON = 10_000.0

# bộ tham số lưới mở rộng (buoc, chan, tp, sl, he_so)
LUOI = [
    (1.0, 4, 1.0, 5.0, 1.0),
    (1.5, 4, 1.2, 5.0, 1.0),
    (1.0, 6, 0.8, 6.0, 1.0),
    (0.6, 6, 0.6, 5.0, 1.0),
    (0.8, 5, 0.8, 4.0, 1.0),
    (1.0, 8, 1.0, 6.0, 1.0),
    (2.0, 4, 1.5, 6.0, 1.0),
    (1.5, 4, 1.2, 5.0, 1.3),
    (1.5, 4, 1.2, 5.0, 1.5),
    (1.0, 5, 1.0, 5.0, 1.5),
    (1.0, 4, 0.8, 5.0, 2.0),
    (0.5, 8, 0.5, 4.0, 1.3),
    (0.8, 6, 0.6, 5.0, 1.5),
]

# (buoc, chan, tp, sl, he_so_lot, he_so_phuc, max_bac)
PHUC = [
    (1.5, 4, 1.2, 5.0, 1.0, 1.5, 3),
    (1.5, 4, 1.2, 5.0, 1.0, 2.0, 3),
    (1.0, 4, 1.0, 5.0, 1.0, 1.5, 3),
    (1.0, 5, 0.8, 5.0, 1.3, 1.5, 3),
    (0.8, 6, 0.6, 5.0, 1.0, 1.5, 4),
    (1.5, 4, 1.2, 5.0, 1.0, 1.3, 2),
]

# (hedge_atr, tp, sl, he_so_hedge)
HEDGE = [
    (2.0, 1.2, 4.0, 1.5),
    (2.0, 1.0, 5.0, 1.5),
    (1.5, 1.0, 4.0, 1.5),
    (2.5, 1.2, 5.0, 2.0),
    (2.0, 1.2, 4.0, 1.2),
    (3.0, 1.5, 6.0, 1.5),
    (2.0, 1.2, 4.0, 1.0),  # khóa lỗ đều lot
]

LOC_H1 = ["khong", "ema_trend_55", "ema_trend_200", "chi_mua", "adx_25", "mua_vu_8_2"]
LOC_NHO = ["khong", "ema_trend_55", "chi_mua", "adx_25", "phien_london_anh", "phien_ny"]


def tai_khung(ten):
    df, nguon, tz = du_lieu.tai_khung(ten)
    if "gio" not in df.columns:
        df = du_lieu.them_cot_thoi_gian(df, tz_may_chu=("máy chủ XM" in (tz or "")))
    return df, (nguon, tz)


def quet(ten_khung, df, meta, loc_ds):
    nguon, tz = meta
    rows = []
    cache = {}
    for ten_l in loc_ds:
        cache[ten_l] = tin_hieu.bo_loc(df, ten_l)
    t0 = time.time()
    k = 0
    for ten_l, loc in cache.items():
        for buoc, chan, tp, sl, hs in LUOI:
            r = mo_phong.mo_phong_luoi(
                df, loc, buoc_atr=buoc, max_chan=chan, tp_atr_tb=tp, sl_tong_atr=sl,
                tinh_swap=False, khung=ten_khung, he_so_lot=hs,
            )
            r.update(khung=ten_khung, vao="luoi_dca", loc=ten_l, nguon=nguon, tz=tz, ho="luoi")
            rows.append(r)
            k += 1
        for buoc, chan, tp, sl, hs, hp, bac in PHUC:
            r = mr.mo_phong_phuc_hoi(
                df, loc, buoc_atr=buoc, max_chan=chan, tp_atr_tb=tp, sl_tong_atr=sl,
                he_so_lot=hs, he_so_phuc=hp, max_bac=bac,
                tinh_swap=False, khung=ten_khung,
            )
            r.update(khung=ten_khung, vao="luoi_phuc_hoi", loc=ten_l, nguon=nguon, tz=tz, ho="phuc_hoi")
            rows.append(r)
            k += 1
        for ha, tp, sl, hx in HEDGE:
            r = mr.mo_phong_hedge(
                df, loc, hedge_atr=ha, tp_atr=tp, sl_atr=sl, he_so_hedge=hx,
                tinh_swap=False, khung=ten_khung,
            )
            r.update(khung=ten_khung, vao="hedge_dao", loc=ten_l, nguon=nguon, tz=tz, ho="hedge")
            rows.append(r)
            k += 1
    print(f"  {ten_khung}: {k} tổ hợp, {len(rows)} dòng, {time.time()-t0:.1f}s", flush=True)
    return rows


def cua_so_doi_chieu(h1):
    """Số Python cùng cửa sổ tick thật 2025-08-01..2026-10-12 cho 2 ứng viên MT5."""
    import pandas as pd
    tu, den = pd.Timestamp("2025-08-01"), pd.Timestamp("2026-10-12 23:59:59")
    d = h1[(h1["time"] >= tu) & (h1["time"] <= den)].copy()
    rows = []
    loc55 = tin_hieu.bo_loc(d, "ema_trend_55")
    sig = tin_hieu.tin_vao(d, "donchian_20")
    # qt tuple: ten, sl_atr, tp_atr, trail, max_nen, eod
    qt = ("atr_sl20_tp40", 2.0, 4.0, 0.0, 0, 0)
    for swap in (False, True):
        r = mo_phong.mo_phong_df(d, sig, loc55, qt, tinh_swap=swap, khung="H1")
        r.update(chien="donchian", cua="2025-08-01..2026-10-12", ho="nen")
        rows.append(r)
        r2 = mo_phong.mo_phong_luoi(
            d, loc55, buoc_atr=1.5, max_chan=4, tp_atr_tb=1.2, sl_tong_atr=5.0,
            tinh_swap=swap, khung="H1", he_so_lot=1.0,
        )
        r2.update(chien="luoi", cua="2025-08-01..2026-10-12", ho="luoi")
        rows.append(r2)
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    all_rows = []
    print("tải H1...", flush=True)
    h1 = du_lieu.tai_h1_xm()
    if "gio" not in h1.columns:
        h1 = du_lieu.them_cot_thoi_gian(h1)
    all_rows += quet("H1", h1, ("XM GOLD.i H1", "máy chủ XM GMT+2"), LOC_H1)

    print("tải H4...", flush=True)
    try:
        h4 = du_lieu.gop_khung(h1, "4h")
        if "gio" not in h4.columns:
            h4 = du_lieu.them_cot_thoi_gian(h4)
        all_rows += quet("H4", h4, ("XM GOLD.i H4 (gop H1)", "máy chủ XM GMT+2"), LOC_H1)
    except Exception as e:
        print("H4 lỗi", e, flush=True)

    for ten in ("M15", "M5"):
        print(f"tải {ten}...", flush=True)
        try:
            df, meta = tai_khung(ten)
            print(f"  {ten} bars={len(df)} {df['time'].iloc[0]}..{df['time'].iloc[-1]}", flush=True)
            all_rows += quet(ten, df, meta, LOC_NHO)
        except Exception as e:
            print(ten, "lỗi", e, flush=True)

    df = pd.DataFrame(all_rows)
    if "dat_moi" not in df.columns:
        df["dat_moi"] = (df["loi_nhuan_lai"] > 0) & (df["dd"] < 0.80)
    path = OUT / "quet_mo_rong_luoi_hedge_phuc_hoi.csv"
    df.to_csv(path, index=False)
    print("ghi", path, "n=", len(df), "dat_moi=", int(df["dat_moi"].sum()), flush=True)

    # cửa sổ tick
    print("cửa sổ tick 2025-08..2026-10...", flush=True)
    win = pd.DataFrame(cua_so_doi_chieu(h1))
    win.to_csv(OUT / "python_cua_so_tick_202508_202610.csv", index=False)
    cols = ["chien","swap","von_cuoi","cagr","dd","n_lenh","winrate","pf","loi_nhuan_lai","lot_chan"]
    print(win[cols].to_string(index=False), flush=True)

    # tóm tắt
    print("\n=== dat_moi theo khung/họ ===", flush=True)
    print(df.groupby(["khung","ho"])["dat_moi"].agg(["sum","count"]).to_string(), flush=True)
    sub = df[df["dat_moi"]].sort_values(["cagr","loi_nhuan_lai"], ascending=False)
    print("\n=== TOP 25 dat_moi ===", flush=True)
    cols2 = ["khung","ho","vao","loc","quan_tri","von_cuoi","cagr","dd","n_lenh","pf","loi_nhuan_lai","lot_chan"]
    print(sub[cols2].head(25).to_string(index=False), flush=True)
    print("\n=== TOP M5/M15 dat_moi ===", flush=True)
    m = sub[sub["khung"].isin(["M5","M15"])]
    print(m[cols2].head(25).to_string(index=False) if len(m) else "không có", flush=True)
    # top hedge / phuc
    for ho in ("hedge","phuc_hoi","luoi"):
        h = sub[sub["ho"]==ho].head(8)
        print(f"\n=== TOP {ho} ===", flush=True)
        print(h[cols2].to_string(index=False) if len(h) else "không có", flush=True)


if __name__ == "__main__":
    main()
