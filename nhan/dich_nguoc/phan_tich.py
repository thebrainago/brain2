# -*- coding: utf-8 -*-
"""Thống kê hành vi: symbol, giờ/thứ, thời gian giữ, chuỗi lot (cố định/martingale/DCA), bước lưới (pip, ATR),
hedge, phân bố khoảng TP/SL."""
from __future__ import annotations
import numpy as np
import pandas as pd


# 03/11/2026: pip theo từng mã, port bảng PIP_THEO_SYMBOL từ seeker/tin-hieu-cong-khai (41052c33).
# Trước đây dầu, UK100/FRA40/JP225/AUS200/HK50/US500/USTEC/DE40… rơi về 0.0001 và ETH = 1.0 → khoảng lưới sai.
_PIP_CHI_SO = ("GER", "DE40", "DAX", "US30", "DJ30", "WALLSTREET", "US500", "SPX", "SP500", "US100", "NAS",
               "USTEC", "UK100", "FTSE", "FRA40", "CAC", "JP225", "JPN225", "NI225", "AUS200", "HK50", "EU50",
               "STOXX50", "IT40", "SPAIN35", "BTC", "XBT")
_PIP_DAU = ("USOIL", "UKOIL", "WTI", "BRENT", "OIL", "XTI", "XBR", "CRUD")


def pip(symbol: str) -> float:
    s = symbol.upper().replace(".I", "").rstrip("#").replace("MICRO", "")
    if s.startswith(("XAU", "GOLD")): return 0.1
    if s.startswith(("XAG", "SILVER")): return 0.01
    if s.startswith(("ETH",)): return 0.1
    if s.startswith(("NGAS", "NATGAS")): return 0.001
    if s.startswith(_PIP_DAU): return 0.01
    if s.startswith(_PIP_CHI_SO): return 1.0
    if "JPY" in s: return 0.01
    return 0.0001


def gio(df) -> dict:
    h = df["mo_luc"].dt.hour.value_counts(normalize=True).sort_index()
    return {int(k): round(float(v), 3) for k, v in h.items()}


def ro(df: pd.DataFrame) -> pd.DataFrame:
    """Gom lệnh thành 'rổ': cùng symbol + chiều, lệnh mới mở khi lệnh trước của rổ còn mở."""
    df = df.copy(); df["ro"] = -1; rid = 0
    for (sym, ch), g in df.groupby(["symbol", "chieu"]):
        dong_max = None
        for i, r in g.iterrows():
            if dong_max is None or (pd.notna(r["mo_luc"]) and r["mo_luc"] >= dong_max):
                rid += 1; dong_max = r["dong_luc"] if pd.notna(r["dong_luc"]) else r["mo_luc"]
            else:
                dong_max = max(dong_max, r["dong_luc"]) if pd.notna(r["dong_luc"]) else dong_max
            df.at[i, "ro"] = rid
    return df


def chuoi_lot(df: pd.DataFrame) -> dict:
    d = ro(df); ty_le, buoc = [], []
    for _, g in d.groupby("ro"):
        if len(g) < 2: continue
        g = g.sort_values("mo_luc"); p = pip(g["symbol"].iloc[0])
        ty_le += list((g["lot"].values[1:] / g["lot"].values[:-1]))
        buoc += list(np.abs(np.diff(g["gia_mo"].values)) / p)
    so_ro = d["ro"].nunique(); nhieu = int((d.groupby("ro").size() > 1).sum())
    tl = float(np.median(ty_le)) if ty_le else None
    kieu = "co_dinh_don_le" if not ty_le else ("co_dinh_dca" if abs(tl - 1) < 0.05 else ("martingale" if tl > 1.05 else "giam_dan"))
    return {"so_ro": int(so_ro), "ro_nhieu_lenh": nhieu, "ty_le_ro_nhieu_lenh": round(nhieu / max(1, so_ro), 3),
            "he_so_lot_trung_vi": None if tl is None else round(tl, 3), "kieu_lot": kieu,
            "buoc_luoi_pip_trung_vi": round(float(np.median(buoc)), 1) if buoc else None,
            "buoc_luoi_pip_p25_p75": [round(float(x), 1) for x in np.percentile(buoc, [25, 75])] if buoc else None,
            "so_lenh_toi_da_trong_ro": int(d.groupby("ro").size().max()) if len(d) else 0,
            "lot_dau_trung_vi": float(d.sort_values("mo_luc").groupby("ro")["lot"].first().median()) if len(d) else None}


def hedge(df) -> dict:
    n = 0
    for sym, g in df.groupby("symbol"):
        b = g[g.chieu == "buy"]; s = g[g.chieu == "sell"]
        for _, r in b.iterrows():
            n += int(((s.mo_luc < r.dong_luc) & (s.dong_luc > r.mo_luc)).any())
    return {"lenh_buy_chong_sell_cung_luc": n, "co_hedge": n > 0.05 * max(1, len(df))}


def tp_sl(df) -> dict:
    ra = {}
    for c in ("tp", "sl"):
        d = df[df[c].fillna(0) > 0]
        if len(d):
            k = (d[c] - d["gia_mo"]).abs() / d["symbol"].map(pip)
            ra[c + "_pip_trung_vi"] = round(float(k.median()), 1); ra[c + "_ty_le_co"] = round(len(d) / len(df), 3)
        else:
            ra[c + "_pip_trung_vi"] = None; ra[c + "_ty_le_co"] = 0.0
    kc = (df["gia_dong"] - df["gia_mo"]).abs() / df["symbol"].map(pip)
    ra["bien_do_dong_pip_trung_vi"] = round(float(kc.median()), 1) if kc.notna().any() else None
    return ra


def tong_quat(df) -> dict:
    giu = (df["dong_luc"] - df["mo_luc"]).dt.total_seconds() / 60
    return {"so_lenh": int(len(df)), "tu": str(df["mo_luc"].min()), "den": str(df["mo_luc"].max()),
            "symbol": {k: int(v) for k, v in df["symbol"].value_counts().items()},
            "ty_le_buy": round(float((df.chieu == "buy").mean()), 3),
            "gio_mo": gio(df), "thu_mo": {int(k): int(v) for k, v in df["mo_luc"].dt.dayofweek.value_counts().sort_index().items()},
            "giu_phut_trung_vi": round(float(giu.median()), 1) if giu.notna().any() else None,
            "giu_phut_p90": round(float(giu.quantile(0.9)), 1) if giu.notna().any() else None,
            "lot": chuoi_lot(df), "hedge": hedge(df), "tp_sl": tp_sl(df)}
