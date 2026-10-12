#!/usr/bin/env python3
"""Tai nen H1 BID + ASK tu kho cong khai Dukascopy -> CSV co SPREAD THAT tung gio (vong 8).

    python tai_dukascopy_spread.py NZDUSD 2018 2023 /workspace/du_lieu_fx/nzdusd_h1_duka_ba.csv

Nguon (cung dang file voi `tai_dukascopy_h1.py`, them ben ASK):
  https://datafeed.dukascopy.com/datafeed/{MA}/{NAM}/{THANG-1:02d}/{BID|ASK}_candles_hour_1.bi5
Ban ghi 24 byte big-endian: giay tu dau thang (int32), open, close, low, high (int32, gia x 10^chu_so),
volume (float32); gio UTC. Bar volume BID = 0 (dong cua) bi bo.
Cot ra: time (gio server Europe/Helsinki - giong chuoi HistData), open/high/low/close (BID),
ask_open, ask_close, spread_open = ask_open - bid_open (spread o TICK DAU cua gio - dung luc
EA vao lenh o open bar), spread_close. Gia la gia THAT cua Dukascopy (ECN), KHONG phai XM.

Kho tra loi chap chon (TLS/timeout/429/503) -> goi `curl` tuan tu, lui dan (5..120 s), toi
da 10 lan / file; dem file vao `_bi5_ba/` de tai tiep. File van hong -> bao ten, khong lap lien.
"""
from __future__ import annotations

import lzma
import struct
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

CHU_SO = {"JPY": 3, "XAU": 3}
URL = "https://datafeed.dukascopy.com/datafeed/{ma}/{nam}/{thang:02d}/{ben}_candles_hour_1.bi5"
KHO = Path("/workspace/du_lieu_fx/_bi5_ba")


def _tai(ma: str, nam: int, thang0: int, ben: str) -> bytes | None:
    f = KHO / ma / f"{ben}_{nam}_{thang0:02d}.bi5"
    if f.exists():
        return f.read_bytes()
    f.parent.mkdir(parents=True, exist_ok=True)
    url = URL.format(ma=ma, nam=nam, thang=thang0, ben=ben)
    tam = f.with_suffix(".tam")
    for lan in range(10):
        r = subprocess.run(["curl", "-s", "-m", "40", "-A", "Mozilla/5.0", "-o", str(tam),
                            "-w", "%{http_code}", url], capture_output=True, text=True)
        if r.stdout.strip() == "200" and tam.exists():
            b = tam.read_bytes()
            try:
                if b:
                    lzma.decompress(b)
                tam.rename(f)
                return b
            except lzma.LZMAError:
                pass
        time.sleep(min(120, 5 * (lan + 1)))
    print(f"THIEU {ma} {nam}-{thang0 + 1:02d} {ben}", flush=True)
    return None


def _giai(raw: bytes, nam: int, thang0: int, cs: int) -> pd.DataFrame:
    if not raw:
        return pd.DataFrame()
    b = lzma.decompress(raw)
    n = len(b) // 24
    goc = pd.Timestamp(year=nam, month=thang0 + 1, day=1, tz="UTC")
    rows = [struct.unpack(">5if", b[k * 24:(k + 1) * 24]) for k in range(n)]
    df = pd.DataFrame(rows, columns=["s", "open", "close", "low", "high", "vol"])
    df.index = goc + pd.to_timedelta(df["s"], unit="s")
    for c in ("open", "close", "low", "high"):
        df[c] = df[c] / 10 ** cs
    return df


def tai(ma: str, nam_dau: int, nam_cuoi: int, den: pd.Timestamp | None = None) -> pd.DataFrame:
    cs = next((v for k, v in CHU_SO.items() if k in ma), 5)
    phan = []
    for nam in range(nam_dau, nam_cuoi + 1):
        for t0 in range(12):
            if den is not None and pd.Timestamp(year=nam, month=t0 + 1, day=1, tz="UTC") > den:
                break
            rb, ra = _tai(ma, nam, t0, "BID"), _tai(ma, nam, t0, "ASK")
            if rb is None or ra is None:
                continue
            b, a = _giai(rb, nam, t0, cs), _giai(ra, nam, t0, cs)
            if b.empty or a.empty:
                continue
            d = b[["open", "high", "low", "close", "vol"]].copy()
            d["ask_open"] = a["open"].reindex(d.index)
            d["ask_close"] = a["close"].reindex(d.index)
            phan.append(d)
    df = pd.concat(phan)
    df = df[(df["vol"] > 0) & ~((df["open"] == df["high"]) & (df["low"] == df["close"]) &
                                (df["open"] == df["close"]))]
    df["spread_open"] = df["ask_open"] - df["open"]
    df["spread_close"] = df["ask_close"] - df["close"]
    df.index = df.index.tz_convert("Europe/Helsinki").tz_localize(None)
    df.index.name = "time"
    return df.drop(columns=["vol"])


def main(argv=None) -> int:
    a = (argv or sys.argv[1:])
    ma, n0, n1, ra = a[0].upper(), int(a[1]), int(a[2]), a[3]
    df = tai(ma, n0, n1, pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=35))
    df.to_csv(ra)
    print(ma, len(df), df.index[0], df.index[-1], "spread_open trung vi",
          float(df["spread_open"].median()), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
