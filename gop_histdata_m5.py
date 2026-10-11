#!/usr/bin/env python3
"""HistData M1 (ASCII, gio EST co dinh UTC-5, khong DST) -> nen M5 gio server uoc luong (Helsinki).

    # tai (mien phi, $0): pip install histdata; trong thu muc DIR:
    #   python -c "from histdata import download_hist_data as d; from histdata.api import Platform as P, TimeFrame as T; d(year='2024',month=None,pair='eurusd',platform=P.GENERIC_ASCII,time_frame=T.ONE_MINUTE)"
    #   (nam hien tai: month='1'..'12')
    python gop_histdata_m5.py DIR EURUSD 2023-12-25 2026-10-10 /workspace/du_lieu_fx/eurusd_m5_histdata_server.csv

Nguon: https://www.histdata.com (GENERIC_ASCII M1, gia BID). Doi gio: EST (UTC-5 co dinh) -> UTC ->
`Europe/Helsinki` (UTC+2/+3) NHU chuoi H1 cua du an (gio server XM/MT5 pho bien - GIA DINH).
M5 = gop phut nhan trai (bar 14:05 = 14:05..14:09:59); bar khong co phut nao -> BO (khong bia nen).
In do day du theo thang (phut co / phut ky vong ngay thuong) de biet lo hong - KHONG lap.
Du lieu ngoai repo. Chi dung cho NGHIEN CUU (mo phong).
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import pandas as pd


def doc_zip(p: Path) -> pd.DataFrame:
    with zipfile.ZipFile(p) as z:
        ten = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if not ten:
            return pd.DataFrame()
        raw = z.read(ten[0]).decode("utf-8", "ignore")
    df = pd.read_csv(io.StringIO(raw), sep=";", header=None,
                     names=["t", "open", "high", "low", "close", "v"])
    df.index = (pd.to_datetime(df["t"], format="%Y%m%d %H%M%S")
                .dt.tz_localize("Etc/GMT+5").dt.tz_convert("UTC"))     # EST co dinh = UTC-5
    return df[["open", "high", "low", "close"]].astype(float)


def gop_m5(m1: pd.DataFrame) -> pd.DataFrame:
    g = m1.resample("5min", label="left", closed="left")
    df = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(),
                       "low": g["low"].min(), "close": g["close"].last(),
                       "tick_volume": g["close"].count()})      # so PHUT co nen (khong phai tick)
    return df.dropna(subset=["open"])


def do_day_du(m1_utc: pd.DataFrame) -> pd.DataFrame:
    """Phut co / phut ky vong (Thu 2 00:00 -> Thu 6 21:00 UTC xap xi) theo thang."""
    idx = m1_utc.index
    ngay_thuong = idx[(idx.dayofweek < 4) | ((idx.dayofweek == 4) & (idx.hour < 21))]
    co = pd.Series(1, index=ngay_thuong).resample("MS").sum()
    ky = pd.Series(1, index=pd.date_range(idx[0].floor("D"), idx[-1], freq="1min", tz="UTC"))
    ky = ky[(ky.index.dayofweek < 4) | ((ky.index.dayofweek == 4) & (ky.index.hour < 21))]
    ky = ky.resample("MS").sum()
    return pd.DataFrame({"co": co, "ky_vong": ky, "ty_le": (co / ky).round(4)})


def main(argv=None) -> int:
    a = list(argv or sys.argv[1:])
    thu_muc, ma, tu, den, ra = Path(a[0]), a[1].upper(), a[2], a[3], Path(a[4])
    phan = [doc_zip(p) for p in sorted(thu_muc.glob(f"DAT_ASCII_{ma}_M1_*.zip"))]
    m1 = pd.concat([p for p in phan if len(p)]).sort_index()
    m1 = m1[~m1.index.duplicated()]
    m1 = m1[(m1.index >= pd.Timestamp(tu, tz="Europe/Helsinki").tz_convert("UTC"))
            & (m1.index < pd.Timestamp(den, tz="Europe/Helsinki").tz_convert("UTC"))]
    dd = do_day_du(m1)
    df = gop_m5(m1)
    df.index = df.index.tz_convert("Europe/Helsinki").tz_localize(None)
    df.index.name = "time"
    ra.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ra, float_format="%.6f")
    print(dd.to_string())
    print(f"{ma}: {len(m1)} phut M1 -> {len(df)} bar M5 {df.index[0]} -> {df.index[-1]} "
          f"(gio Helsinki) -> {ra}; thang day du < 97%: "
          f"{[str(k.date())[:7] for k, v in dd['ty_le'].items() if v < 0.97] or 'khong'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
