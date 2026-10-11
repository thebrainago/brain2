#!/usr/bin/env python3
"""Tai nen M1 (gia BID, tuy chon ASK) tu kho cong khai Dukascopy -> gop M5 gio server uoc luong.

    python tai_dukascopy_m5.py EURUSD 2023-12-26 2026-10-10 /workspace/du_lieu_fx/eurusd_m5_duka_server.csv
    python tai_dukascopy_m5.py EURUSD 2023-12-26 2026-10-10 out.csv --ask   # them cot spread (ASK-BID open)

Nguon (cung kho `tai_dukascopy_h1.py`, $0, khong dang nhap):
https://datafeed.dukascopy.com/datafeed/{MA}/{NAM}/{THANG-1:02d}/{NGAY:02d}/{BID|ASK}_candles_min_1.bi5
(moi file = mot ngay nen M1 UTC, LZMA, ban ghi 24 byte big-endian: giay_tu_dau_ngay:int32,
open, close, low, high: int32 (gia * 10^chu_so), volume: float32).
Bo phut volume = 0 (khong giao dich). Gop M5 (nhan trai: bar 14:05 = 14:05..14:09:59), doi sang
`Europe/Helsinki` (UTC+2/+3) NHU chuoi H1 cua du an (gio server XM/MT5 pho bien - GIA DINH, ghi
trong GHI_CHU). KHONG bia nen: ngay loi mang -> thu lai, van loi -> liet ke ngay thieu, exit 1.
Du lieu ngoai repo (`/workspace/du_lieu_fx`). Chi dung cho NGHIEN CUU (mo phong).
"""
from __future__ import annotations

import lzma
import struct
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

CHU_SO = {"JPY": 3}
URL = ("https://datafeed.dukascopy.com/datafeed/{ma}/{nam}/{thang0:02d}/{ngay:02d}/"
       "{phia}_candles_min_1.bi5")
KHO = Path("/workspace/du_lieu_fx/_bi5")
NGHI = 1.0


def _tai_ngay(ma: str, d: pd.Timestamp, phia: str = "BID") -> bytes | None:
    f = KHO / f"{ma}_M1_{phia}" / f"{d:%Y_%m_%d}.bi5"
    if f.exists():
        return f.read_bytes()
    url = URL.format(ma=ma, nam=d.year, thang0=d.month - 1, ngay=d.day, phia=phia)
    for lan in range(8):
        try:
            rq = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(rq, timeout=30) as r:
                raw = r.read()
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(raw)
            time.sleep(NGHI)
            return raw
        except Exception:                                  # noqa: BLE001 - 429/mang: lui lai
            time.sleep(min(90.0, 5.0 * 2 ** lan))
    return None


def giai_ma(d: pd.Timestamp, raw: bytes, chu_so: int) -> pd.DataFrame:
    if not raw:
        return pd.DataFrame()
    b = lzma.decompress(raw)
    n = len(b) // 24
    rec = [struct.unpack(">iiiiif", b[k * 24:(k + 1) * 24]) for k in range(n)]
    goc = pd.Timestamp(year=d.year, month=d.month, day=d.day, tz="UTC")
    s = 10.0 ** chu_so
    df = pd.DataFrame(rec, columns=["t", "open", "close", "low", "high", "volume"])
    df.index = goc + pd.to_timedelta(df["t"], unit="s")
    for c in ("open", "close", "low", "high"):
        df[c] = df[c] / s
    return df[["open", "high", "low", "close", "volume"]]


def gop_m5(m1: pd.DataFrame) -> pd.DataFrame:
    """M1 (UTC, da bo phut volume 0) -> M5 nhan trai; bar khong co phut nao -> bo (khong bia)."""
    g = m1.resample("5min", label="left", closed="left")
    df = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(),
                       "low": g["low"].min(), "close": g["close"].last(),
                       "tick_volume": g["volume"].sum()})
    return df.dropna(subset=["open"])


def tai(ma: str, tu: str, den: str, ask: bool = False) -> tuple[pd.DataFrame, list]:
    ngay = [d for d in pd.date_range(tu, den, freq="D") if d.weekday() != 5]   # thu 7 dong cua
    chu_so = CHU_SO.get(ma[-3:], 5)
    phan, phan_ask, thieu = [], [], []
    for i, d in enumerate(ngay):
        raw = _tai_ngay(ma, d)
        if raw is None:
            thieu.append(f"{d:%Y-%m-%d}")
            continue
        phan.append(giai_ma(d, raw, chu_so))
        if ask:
            ra = _tai_ngay(ma, d, "ASK")
            if ra is None:
                thieu.append(f"{d:%Y-%m-%d} ASK")
            else:
                phan_ask.append(giai_ma(d, ra, chu_so))
        if i % 50 == 0:
            print(f"  {d:%Y-%m-%d} ({i + 1}/{len(ngay)}) thieu {len(thieu)}", flush=True)
    m1 = pd.concat([p for p in phan if len(p)]).sort_index()
    m1 = m1[~m1.index.duplicated()]
    m1 = m1[(m1["volume"] > 0)]
    df = gop_m5(m1)
    if ask and phan_ask:
        a1 = pd.concat([p for p in phan_ask if len(p)]).sort_index()
        a1 = a1[~a1.index.duplicated()]
        a1 = a1[a1["volume"] > 0]
        ao = a1["open"].resample("5min", label="left", closed="left").first()
        sp = (ao.reindex(df.index) - df["open"])
        df["spread"] = (sp * 10 ** chu_so).round()        # diem (_Point), nhu cot spread MT5
    df.index = df.index.tz_convert("Europe/Helsinki").tz_localize(None)
    df.index.name = "time"
    return df, thieu


def main(argv=None) -> int:
    a = list(argv or sys.argv[1:])
    ask = "--ask" in a
    a = [x for x in a if x != "--ask"]
    ma, tu, den, ra = a[0].upper(), a[1], a[2], Path(a[3])
    df, thieu = tai(ma, tu, den, ask)
    ra.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ra, float_format="%.6f")
    print(f"{ma}: {len(df)} bar M5 {df.index[0]} -> {df.index[-1]} (gio Helsinki); "
          f"ngay thieu: {thieu or 'khong'} -> {ra}")
    return 1 if thieu else 0


if __name__ == "__main__":
    raise SystemExit(main())
