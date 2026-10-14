# -*- coding: utf-8 -*-
"""Mo hinh phi Exness (chi de SO SANH / KIEM CHEO; san chinh la XM Ultra Low).
Spread lay tu kho tick cong khai https://ticks.ex2archive.com/ticks/{MA}/{NAM}/{THANG}/Exness_{MA}_{NAM}_{THANG}.zip
(cot Exness,Symbol,Timestamp UTC,Bid,Ask). Tai gon theo mau thang (THANG_MAU), tinh spread bps theo
gio UTC x thu trong tuan (trung vi, p90), xoa zip/csv tho ngay, chi giu bang tong hop
/workspace/du_lieu_fx/exness/spread_exness.csv.
Hoa hong: Raw_Spread 3,5 USD/lot/chieu (theo trang cong khai, "toi da"); Standard 0.
Swap: 2 kich ban - mien swap (mac dinh Exness) va swap day du (Exness khong cong bo lich su swap tren
kho; dung muc swap XM trong reports/phi_xm_micro_that.csv lam xap xi - ghi ro trong bao cao).
Truot gia: 0,5 x spread moi chieu.
    python phi_exness.py   # tai + tong hop
"""
from __future__ import annotations
import io, os, subprocess, sys, zipfile
import pandas as pd

URL = "https://ticks.ex2archive.com/ticks/{m}/{y}/{mo:02d}/Exness_{m}_{y}_{mo:02d}.zip"
RA = "/workspace/du_lieu_fx/exness/spread_exness.csv"
MA = {"EURUSD": "EURUSD", "GBPUSD": "GBPUSD", "AUDUSD": "AUDUSD", "USDCAD": "USDCAD", "USDJPY": "USDJPY",
      "USDCHF": "USDCHF", "NZDUSD": "NZDUSD", "EURGBP": "EURGBP", "EURJPY": "EURJPY", "XAUUSD": "XAUUSD",
      "US500": "US500", "US100": "USTEC", "GER40": "DE30"}
LOAI = {"Standard": "", "Raw": "_Raw_Spread"}
THANG_MAU = [(2025, 2), (2025, 6), (2025, 10)]
HOA_HONG_USD_LOT_CHIEU = {"Standard": 0.0, "Raw": 3.5}
TRUOT_X_SPREAD = 0.5


def tai_mot(ma, y, mo):
    u = URL.format(m=ma, y=y, mo=mo)
    for _ in range(4):
        r = subprocess.run(["curl", "-s", "-f", "-m", "300", u], capture_output=True)
        if r.returncode == 0 and r.stdout[:2] == b"PK": break
    else:
        return None
    z = zipfile.ZipFile(io.BytesIO(r.stdout)); f = z.namelist()[0]
    d = pd.read_csv(z.open(f), usecols=[2, 3, 4]); d.columns = ["t", "b", "a"]
    d["t"] = pd.to_datetime(d["t"], format="%Y-%m-%d %H:%M:%S.%fZ", errors="coerce"); d["s"] = (d.a - d.b) / ((d.a + d.b) / 2) * 1e4
    return d[["t", "s"]]


def tong_hop():
    rows = []
    for ten, ma in MA.items():
        for loai, hau in LOAI.items():
            P = [x for x in (tai_mot(ma + hau, y, mo) for y, mo in THANG_MAU) if x is not None]
            if not P: print("KHONG TAI DUOC", ten, loai, flush=True); continue
            d = pd.concat(P); d = d[d.t.dt.dayofweek < 5]
            g = d.groupby([d.t.dt.dayofweek.rename("thu"), d.t.dt.hour.rename("gio_utc")])["s"]
            q = pd.DataFrame({"med": g.median(), "p90": g.quantile(0.9), "n": g.size()}).reset_index()
            q.insert(0, "loai", loai); q.insert(0, "ma", ten); q["so_thang"] = len(P); rows.append(q)
            print(ten, loai, len(d), round(d.s.median(), 3), flush=True)
    out = pd.concat(rows); out.to_csv(RA, index=False); return out


_B = None


def bang():
    global _B
    if _B is None: _B = pd.read_csv(RA)
    return _B


def spread_bps(ten, loai, gio_utc, p90=False):
    """Spread bps Exness tai gio UTC (gop moi ngay trong tuan, trung vi cua trung vi). None neu khong co."""
    b = bang(); x = b[(b.ma == ten) & (b.loai == loai) & (b.gio_utc == gio_utc)]
    return None if x.empty else float(x["p90" if p90 else "med"].median())


if __name__ == "__main__":
    tong_hop()
