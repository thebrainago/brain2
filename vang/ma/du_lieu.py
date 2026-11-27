# -*- coding: utf-8 -*-
"""Nạp và ghép chuỗi giá vàng. Ưu tiên nến XM GOLD.i (CFD thật, có spread)."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

GOC_REPO = Path(__file__).resolve().parents[2]
H1_XM = GOC_REPO / "reports/mt5_v27/gia_xm/GOLD_i_H1.csv.gz"
D1_XM = GOC_REPO / "reports/mt5_v27/gia_xm/GOLD_i_D1.csv"
M5_PQ = Path("/workspace/quet_intraday/m5/xauusd.parquet")
M1_PQ = Path("/workspace/quet_intraday/dot3/m1/xauusd.parquet")
# Đồng hồ nến XM: mở tuần Thứ Hai 01:00 = Chủ nhật 23:00 GMT → máy chủ GMT+2 (không DST).
LECH_MAY_CHU_UTC = 2
# M5/M1 parquet dùng mốc giờ riêng (không phải máy chủ XM). Dùng cho tín hiệu giá; phiên giao dịch ghi rõ nguồn.

H1_DU_GIO_TU = pd.Timestamp("2014-01-02")  # 2010-2012 chỉ D1; 2013 thiếu nến


def _chuan(df: pd.DataFrame, ts=None) -> pd.DataFrame:
    if ts is not None:
        df = df.copy()
        df["time"] = pd.to_datetime(ts)
    elif "time" in df.columns:
        df = df.copy()
        df["time"] = pd.to_datetime(df["time"])
    else:
        df = df.reset_index()
        df = df.rename(columns={df.columns[0]: "time"})
        df["time"] = pd.to_datetime(df["time"])
    for c in ("open", "high", "low", "close"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if "spread" not in df.columns:
        df["spread"] = 0.0
    else:
        df["spread"] = pd.to_numeric(df["spread"], errors="coerce").fillna(0.0)
    df = df.dropna(subset=["open", "high", "low", "close"]).sort_values("time")
    df = df[df["high"] >= df["low"]]
    df = df.drop_duplicates("time", keep="last")
    return df[["time", "open", "high", "low", "close", "spread"]].reset_index(drop=True)


def _gop(rules):
    """Gộp nến: rules là list (offset, freq) pandas."""
    pass


def tai_h1_xm(tu=None, den=None) -> pd.DataFrame:
    df = _chuan(pd.read_csv(H1_XM, parse_dates=["time"]))
    df = df[df["time"] >= H1_DU_GIO_TU]
    if tu is not None:
        df = df[df["time"] >= pd.Timestamp(tu)]
    if den is not None:
        df = df[df["time"] <= pd.Timestamp(den)]
    return df.reset_index(drop=True)


def tai_d1_xm(tu=None, den=None) -> pd.DataFrame:
    df = _chuan(pd.read_csv(D1_XM, parse_dates=["time"]))
    if tu is not None:
        df = df[df["time"] >= pd.Timestamp(tu)]
    if den is not None:
        df = df[df["time"] <= pd.Timestamp(den)]
    return df.reset_index(drop=True)


def gop_khung(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    x = df.set_index("time")
    g = x.resample(rule, label="left", closed="left").agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        spread=("spread", "median"),
    ).dropna(subset=["open", "close"])
    return g.reset_index()


def tai_m5():
    if not M5_PQ.exists():
        raise FileNotFoundError(M5_PQ)
    df = pd.read_parquet(M5_PQ)
    return _chuan(df)


def tai_m1():
    if not M1_PQ.exists():
        raise FileNotFoundError(M1_PQ)
    df = pd.read_parquet(M1_PQ)
    return _chuan(df)


def tai_khung(ten: str) -> tuple[pd.DataFrame, str, str]:
    """Trả (df, nguon, ghi_chu_timezone)."""
    ten = ten.upper()
    if ten == "D1":
        return tai_d1_xm(), "XM GOLD.i D1 2010-01-04..2026-10-12", "máy chủ XM GMT+2"
    if ten == "H1":
        return tai_h1_xm(), "XM GOLD.i H1 đủ giờ 2014-01-02..2026-10-12", "máy chủ XM GMT+2"
    if ten == "H4":
        df = gop_khung(tai_h1_xm(), "4h")
        return df, "Gộp H4 từ XM GOLD.i H1 2014-01-02..2026-10-12", "máy chủ XM GMT+2"
    if ten == "M15":
        df = gop_khung(tai_m5(), "15min")
        return df, "Gộp M15 từ parquet M5 2017-01-02..2026-10-09", "mốc giờ parquet (không phải máy chủ XM)"
    if ten == "M5":
        return tai_m5(), "parquet M5 2017-01-02..2026-10-09", "mốc giờ parquet (không phải máy chủ XM)"
    if ten == "M1":
        return tai_m1(), "parquet M1 2017-01-02..2026-10-09", "mốc giờ parquet (không phải máy chủ XM)"
    raise ValueError(ten)


def them_cot_thoi_gian(df: pd.DataFrame, tz_may_chu=True) -> pd.DataFrame:
    """Thêm giờ máy chủ và giờ VN (UTC+7). Nếu tz_may_chu=False, coi time đã là mốc raw, vẫn tính VN = time + (7-2) khi giả định cùng GMT+2; với parquet không giả định."""
    out = df.copy()
    t = pd.to_datetime(out["time"])
    out["gio"] = t.dt.hour.to_numpy()
    out["thu"] = t.dt.dayofweek.to_numpy()  # 0=T2
    out["thang"] = t.dt.month.to_numpy()
    out["ngay"] = t.dt.day.to_numpy()
    if tz_may_chu:
        # VN = máy chủ + 5 giờ
        vn = t + pd.Timedelta(hours=5)
        out["gio_vn"] = vn.dt.hour.to_numpy()
    else:
        out["gio_vn"] = t.dt.hour.to_numpy()  # không chắc, đánh dấu riêng
    return out
