#!/usr/bin/env python3
"""Gop nen M5 (HistData da gop tu M1, gio server NY+7) -> H1 / H4.

    python gop_m5_len_h1_h4.py /workspace/du_lieu_fx/hd28/eurgbp_m5_den202610.csv \
        /workspace/du_lieu_fx/hd_ck7/eurgbp_h1_tu_histdata_m5_ny7.csv \
        /workspace/du_lieu_fx/hd_ck7/eurgbp_h4_tu_histdata_m5_ny7.csv

Nhan trai, closed left; OHLC = open dau / high max / low min / close cuoi;
tick_volume = tong (neu co) hoac dem bar M5. Bo bar rong. Du lieu NGOAI repo.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


def gop(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    g = df.resample(rule, label="left", closed="left")
    tv = g["tick_volume"].sum() if "tick_volume" in df.columns else g["close"].count()
    out = pd.DataFrame({
        "open": g["open"].first(),
        "high": g["high"].max(),
        "low": g["low"].min(),
        "close": g["close"].last(),
        "tick_volume": tv,
    }).dropna(subset=["open"])
    return out


def doc_m5(p: Path) -> pd.DataFrame:
    df = pd.read_csv(p, parse_dates=["time"], index_col="time")
    if "tick_volume" not in df.columns:
        df["tick_volume"] = 1
    return df


def main(argv=None) -> int:
    a = list(argv or sys.argv[1:])
    if len(a) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    src, ra_h1, ra_h4 = Path(a[0]), Path(a[1]), Path(a[2])
    df = doc_m5(src)
    h1, h4 = gop(df, "1h"), gop(df, "4h")
    for p, d in ((ra_h1, h1), (ra_h4, h4)):
        p.parent.mkdir(parents=True, exist_ok=True)
        d.to_csv(p, float_format="%.6f")
    print(f"{src.name}: M5 {len(df)} -> H1 {len(h1)} ({h1.index[0]}..{h1.index[-1]}) "
          f"| H4 {len(h4)} ({h4.index[0]}..{h4.index[-1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
