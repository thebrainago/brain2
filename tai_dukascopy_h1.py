#!/usr/bin/env python3
"""Tai nen H1 (gia BID) tu kho cong khai Dukascopy -> CSV gio server uoc luong.

    python tai_dukascopy_h1.py EURUSD 2010 2026 /workspace/du_lieu_fx/eurusd_h1_duka.csv

Nguon: https://datafeed.dukascopy.com/datafeed/{MA}/{NAM}/{THANG-1:02d}/BID_candles_hour_1.bi5
(moi file = mot thang nen H1, nen LZMA, ban ghi 24 byte big-endian:
giay_tu_dau_thang:int32, open, close, low, high: int32 (gia * 10^chu_so), volume: float32;
thoi gian UTC). Bo bar volume = 0 (cuoi tuan / khong giao dich) va bar phang O=H=L=C.
Doi sang `Europe/Helsinki` (UTC+2/+3) nhu chuoi Yahoo cu - bo loc gio cua EA viet theo
gio server (gia dinh, ghi trong GHI_CHU). Chi dung cho NGHIEN CUU; du lieu ngoai repo.
File thang loi mang -> thu lai 4 lan; van loi -> bao ten thang thieu (khong lap lien).
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
URL = "https://datafeed.dukascopy.com/datafeed/{ma}/{nam}/{thang:02d}/BID_candles_hour_1.bi5"


KHO = Path("/workspace/du_lieu_fx/_bi5")       # dem tung thang (tai tiep khi bi ngat)


def _tai_thang(ma: str, nam: int, thang0: int) -> tuple[tuple, bytes | None]:
    """Mot thang; dem ra dia. Kho tra 429 khi goi day -> tai TUAN TU, nghi giua cac
    lan, lui lai lau dan khi 429/loi mang."""
    f = KHO / ma / f"{nam}_{thang0:02d}.bi5"
    if f.exists():
        return (nam, thang0), f.read_bytes()
    url = URL.format(ma=ma, nam=nam, thang=thang0)
    for lan in range(8):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                raw = r.read()
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(raw)
            time.sleep(0.7)
            return (nam, thang0), raw
        except Exception:                                  # noqa: BLE001
            time.sleep(min(60.0, 3.0 * 2 ** lan))
    return (nam, thang0), None


def giai_ma(nam: int, thang0: int, raw: bytes, chu_so: int) -> pd.DataFrame:
    if not raw:
        return pd.DataFrame()
    d = lzma.decompress(raw)
    n = len(d) // 24
    rec = [struct.unpack(">iiiiif", d[k * 24:(k + 1) * 24]) for k in range(n)]
    goc = pd.Timestamp(year=nam, month=thang0 + 1, day=1, tz="UTC")
    s = 10.0 ** chu_so
    df = pd.DataFrame(rec, columns=["t", "open", "close", "low", "high", "volume"])
    df.index = goc + pd.to_timedelta(df["t"], unit="s")
    for c in ("open", "close", "low", "high"):
        df[c] = df[c] / s
    return df[["open", "high", "low", "close", "volume"]]


def tai(ma: str, nam_dau: int, nam_cuoi: int, den: pd.Timestamp | None = None) -> tuple:
    viec = [(y, m) for y in range(nam_dau, nam_cuoi + 1) for m in range(12)]
    den = den or pd.Timestamp.now(tz="UTC")
    viec = [(y, m) for y, m in viec if pd.Timestamp(year=y, month=m + 1, day=1, tz="UTC") < den]
    chu_so = CHU_SO.get(ma[-3:], 5)
    kq = [_tai_thang(ma, *v) for v in viec]
    thieu = [k for k, raw in kq if raw is None]
    phan = [giai_ma(y, m, raw, chu_so) for (y, m), raw in kq if raw]
    df = pd.concat([p for p in phan if len(p)]).sort_index()
    df = df[~df.index.duplicated()]
    phang = (df["high"] == df["low"])
    df = df[(df["volume"] > 0) & ~phang]
    df.index = df.index.tz_convert("Europe/Helsinki").tz_localize(None)
    df.index.name = "time"
    return df, thieu


def main(argv=None) -> int:
    a = argv or sys.argv[1:]
    ma, nd, nc, ra = a[0].upper(), int(a[1]), int(a[2]), Path(a[3])
    df, thieu = tai(ma, nd, nc)
    ra.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ra, float_format="%.6f")
    print(f"{ma}: {len(df)} bar H1 {df.index[0]} -> {df.index[-1]} (gio Helsinki); "
          f"thang thieu: {thieu or 'khong'} -> {ra}")
    return 1 if thieu else 0


if __name__ == "__main__":
    raise SystemExit(main())
