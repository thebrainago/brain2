#!/usr/bin/env python3
"""HistData TICK (GENERIC_ASCII, `YYYYMMDD HHMMSSmmm,bid,ask,vol`, gio New York) -> nen
H1 (hoac khung khac) gio server NY+7, co SPREAD THAT (vong 8, 12/10/2026).

    python gop_histdata_tick.py DIR EURUSD /workspace/du_lieu_fx/eurusd_h1_tick_ba.csv [--khung 1h]

Cot ra: open/high/low/close (BID), spread_open = ask - bid o TICK DAU cua bar (luc EA vao lenh
o open bar), spread_tb (trung binh moi tick trong bar), spread_max, so_tick.
Nguon: https://www.histdata.com (Tick Data, mien phi). Spread la cua NGUON DU LIEU HistData (gan
ECN), KHONG phai spread tai khoan XM - dung de do HINH DANG thoi gian cua spread (gian luc mo
cua / tin / qua dem). Du lieu ngoai repo. Chi NGHIEN CUU (mo phong).
"""
from __future__ import annotations

import argparse
import io
import zipfile
from pathlib import Path

import pandas as pd


def _mot_thang(p: Path, khung: str) -> pd.DataFrame:
    with zipfile.ZipFile(p) as z:
        ten = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
        with z.open(ten) as f:
            df = pd.read_csv(io.TextIOWrapper(f), header=None, names=["t", "bid", "ask", "v"],
                             dtype={"t": str, "bid": float, "ask": float})
    tg = pd.to_datetime(df["t"].str[:15], format="%Y%m%d %H%M%S") + \
        pd.to_timedelta(df["t"].str[15:18].astype(int), unit="ms")
    # gio HistData = gio New York (co DST) -> server MT5 'NY close' = NY + 7 h (xem gop_histdata_m5)
    df.index = tg + pd.Timedelta(hours=7)
    df = df[(df["ask"] >= df["bid"]) & (df["bid"] > 0)]
    sp = df["ask"] - df["bid"]
    g = df["bid"].resample(khung, label="left", closed="left")
    ra = pd.DataFrame({"open": g.first(), "high": g.max(), "low": g.min(), "close": g.last()})
    gs = sp.resample(khung, label="left", closed="left")
    ra["spread_open"] = gs.first()
    ra["spread_tb"] = gs.mean()
    ra["spread_max"] = gs.max()
    ra["so_tick"] = gs.count()
    return ra.dropna(subset=["open"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("ma")
    ap.add_argument("ra")
    ap.add_argument("--khung", default="1h")
    a = ap.parse_args(argv)
    tep = sorted(Path(a.dir).glob(f"DAT_ASCII_{a.ma.upper()}_T_*.zip"))
    phan = [_mot_thang(p, a.khung) for p in tep]
    df = pd.concat(phan).sort_index()
    df = df[~df.index.duplicated(keep="first")]
    df.index.name = "time"
    df.to_csv(a.ra)
    print(a.ma, len(tep), "thang ->", len(df), "bar", df.index[0], df.index[-1],
          "spread_open trung vi", float(df["spread_open"].median()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
