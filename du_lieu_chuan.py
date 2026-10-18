"""Đọc kho dữ liệu giá chuẩn (Dukascopy tick -> M1 Bid/Ask) ở /workspace/du_lieu_chuan.

    from du_lieu_chuan import doc
    df = doc("EURUSD", "H1", "2024-01-01", "2024-06-30")            # mid OHLC + spread + so_tick
    df = doc("XAUUSD", "M5", "2025-01-01", gia="bid")               # bid OHLC
    df = doc("USA500.IDX", "D1", gia="tat_ca")                       # mọi cột bid_*/ask_*/mid_*

Giờ UTC, nhãn trái. Phút không có tick không có dòng (không bịa nến). Khung lớn gộp từ M1:
open=first, high=max, low=min, close=last, spread_tb bình quân theo số tick, so_tick=tổng.
D1/H4 cắt theo UTC (00:00, 04:00, ...).
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

GOC = Path(os.environ.get("DU_LIEU_CHUAN", "/workspace/du_lieu_chuan"))
KHUNG = {"M1": "1min", "M5": "5min", "M15": "15min", "M30": "30min", "H1": "1h", "H4": "4h", "D1": "1D"}
_BIET_DANH = {"USA500": "USA500.IDX", "US500": "USA500.IDX", "USATECH": "USATECH.IDX", "US100": "USATECH.IDX",
              "DEU": "DEU.IDX", "GER40": "DEU.IDX", "GBR": "GBR.IDX", "UK100": "GBR.IDX", "JPN": "JPN.IDX",
              "JP225": "JPN.IDX", "LIGHT": "LIGHT.CMD", "WTI": "LIGHT.CMD", "USOIL": "LIGHT.CMD",
              "BRENT": "BRENT.CMD", "UKOIL": "BRENT.CMD", "GOLD": "XAUUSD", "SILVER": "XAGUSD"}


def ten_chuan(ma: str) -> str:
    m = ma.upper().replace("/", "")
    return _BIET_DANH.get(m, m)


def ds_ma() -> list[str]:
    s = set()
    for d in ("m1", "_ngay"):
        if (GOC / d).exists():
            s |= {p.name for p in (GOC / d).iterdir() if p.is_dir() and any(p.iterdir())}
    return sorted(s)


def _doc_m1(ma: str, tu: pd.Timestamp | None, den: pd.Timestamp | None) -> pd.DataFrame:
    phan = []
    for f in sorted((GOC / "m1" / ma).glob(f"{ma}_*.parquet")):
        nam = int(f.stem.rsplit("_", 1)[1])
        if (tu is not None and nam < tu.year) or (den is not None and nam > den.year):
            continue
        phan.append(pd.read_parquet(f))
    for f in sorted((GOC / "_ngay" / ma).glob("*.parquet")):           # ngày chưa gộp năm
        d = pd.Timestamp(f.stem, tz="UTC")
        if (tu is not None and d < tu.normalize()) or (den is not None and d > den):
            continue
        phan.append(pd.read_parquet(f))
    if not phan:
        raise FileNotFoundError(f"Chưa có dữ liệu chuẩn cho {ma} trong {GOC}")
    df = pd.concat(phan)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    if tu is not None:
        df = df[df.index >= tu]
    if den is not None:
        df = df[df.index <= den]
    return df


def gop_khung(m1: pd.DataFrame, khung: str) -> pd.DataFrame:
    if khung == "M1":
        return m1
    g = m1.assign(_w=m1["spread_tb"] * m1["so_tick"]).resample(KHUNG[khung], label="left", closed="left")
    df = pd.DataFrame({
        "bid_o": g["bid_o"].first(), "bid_h": g["bid_h"].max(), "bid_l": g["bid_l"].min(), "bid_c": g["bid_c"].last(),
        "ask_o": g["ask_o"].first(), "ask_h": g["ask_h"].max(), "ask_l": g["ask_l"].min(), "ask_c": g["ask_c"].last(),
        "spread_min": g["spread_min"].min(), "spread_max": g["spread_max"].max(),
        "so_tick": g["so_tick"].sum(), "_w": g["_w"].sum(),
    })
    df = df[df["so_tick"] > 0].copy()
    df["spread_tb"] = df.pop("_w") / df["so_tick"]
    df["so_tick"] = df["so_tick"].astype("int64")
    return df[list(m1.columns)]


def _ts(x):
    if x is None:
        return None
    t = pd.Timestamp(x)
    return t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")


def doc(ma: str, khung: str = "M1", tu=None, den=None, gia: str = "mid") -> pd.DataFrame:
    """gia: 'mid' | 'bid' | 'ask' | 'tat_ca'. Trả cột open/high/low/close (+spread_tb/min/max, so_tick).

    'den' dạng ngày ('2024-06-30') được hiểu là hết ngày đó."""
    khung = khung.upper()
    if khung not in KHUNG:
        raise ValueError(f"Khung {khung} không hỗ trợ; chọn {list(KHUNG)}")
    ma = ten_chuan(ma)
    tu_, den_ = _ts(tu), _ts(den)
    if den_ is not None and den is not None and len(str(den)) <= 10:
        den_ = den_ + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    m1 = _doc_m1(ma, tu_, den_)
    df = gop_khung(m1, khung)
    phu = df[["spread_tb", "spread_min", "spread_max", "so_tick"]]
    if gia == "tat_ca":
        out = df.copy()
        for k in "ohlc":
            out[f"mid_{k}"] = (df[f"bid_{k}"] + df[f"ask_{k}"]) / 2
        return out
    if gia in ("bid", "ask"):
        o = df[[f"{gia}_{k}" for k in "ohlc"]].copy()
    elif gia == "mid":
        o = pd.DataFrame({f"mid_{k}": (df[f"bid_{k}"] + df[f"ask_{k}"]) / 2 for k in "ohlc"}, index=df.index)
    else:
        raise ValueError("gia phải là mid/bid/ask/tat_ca")
    o.columns = ["open", "high", "low", "close"]
    return pd.concat([o, phu], axis=1)


def sinh_khung(ma: str, khung_ds=("M5", "M15", "H1", "H4", "D1")) -> dict:
    """Ghi sẵn khung lớn ra /workspace/du_lieu_chuan/{KHUNG}/{ma}.parquet (để tra cứu nhanh)."""
    ma = ten_chuan(ma)
    m1 = _doc_m1(ma, None, None)
    ra = {}
    for k in khung_ds:
        f = GOC / k / f"{ma}.parquet"
        f.parent.mkdir(parents=True, exist_ok=True)
        df = gop_khung(m1, k)
        df.to_parquet(f, compression="zstd")
        ra[k] = len(df)
    return ra


if __name__ == "__main__":
    import sys
    for m in (sys.argv[1:] or ds_ma()):
        print(m, sinh_khung(m))
