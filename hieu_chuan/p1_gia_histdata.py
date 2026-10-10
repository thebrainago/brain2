#!/usr/bin/env python3
"""Doi nen M1 HistData.com (cong khai, mien phi; gia BID; gio EST CO DINH UTC-5, khong DST)
sang M1 + H1 gio may chu Europe/Helsinki (UTC+2/+3, kieu XM) cho P1.

    python hieu_chuan/p1_gia_histdata.py /workspace/du_lieu_fx/histdata /workspace/du_lieu_fx

Tai: goi `histdata` (pip) -> download_hist_data(year='2019', month=None, pair='audcad',
platform=GENERIC_ASCII, time_frame=ONE_MINUTE). Du lieu KHONG vao git (ngoai repo).
Vi sao HistData ma khong phai Dukascopy: 10/10/2026 datafeed.dukascopy.com het thoi gian
ket noi TLS tu may nay (2 viec tai dai khac dang chay song song) - tai 1 thang/10 phut.
"""
import sys
from pathlib import Path

import pandas as pd


def doc_m1(f: Path) -> pd.DataFrame:
    df = pd.read_csv(f, sep=";", header=None, names=["t", "open", "high", "low", "close", "v"])
    t = pd.to_datetime(df["t"], format="%Y%m%d %H%M%S") + pd.Timedelta(hours=5)   # EST co dinh -> UTC
    df.index = t.dt.tz_localize("UTC").dt.tz_convert("Europe/Helsinki").dt.tz_localize(None)
    df.index.name = "time"
    return df[["open", "high", "low", "close"]]


def main(a):
    vao, ra = Path(a[0]), Path(a[1])
    for ma in ("AUDCAD", "NZDCAD", "USDCAD"):
        m1 = doc_m1(vao / f"DAT_ASCII_{ma}_M1_2019.csv")
        m1 = m1[(m1.index >= "2019-02-01") & (m1.index < "2019-09-02")]
        h1 = m1.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
        m1.to_csv(ra / f"{ma.lower()}_m1_histdata_2019.csv", float_format="%.6f")
        h1.to_csv(ra / f"{ma.lower()}_h1_duka_2019.csv".replace("duka", "histdata"), float_format="%.6f")
        print(ma, "M1", len(m1), "H1", len(h1), h1.index[0], h1.index[-1])


if __name__ == "__main__":
    main(sys.argv[1:])
