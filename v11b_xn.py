# -*- coding: utf-8 -*-
"""Vong 11b - XAC NHAN cac o song quet (reports/vong11b.json) voi phi XM + swap, x1 / x1,5, tren nua giu lai.
Them kiem GIAO DICH DUOC (sua nhin truoc, chi lam GIAM so song): o cheo ma gio dong cua cua A >= gio dong cua
cua B (UTC) -> dung r_A(t-2) (r_A(t-1) chua biet luc B dong cua). O gio: gia khop THAT tu tick bid/ask
(mua o ask, ban o bid, spread XM = spread that + markup co dinh). MO PHONG."""
from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd

import mua_vu as MV
import v11b as VB

SPREAD = {"eurusd": 1.4e-4, "gbpusd": 1.6e-4, "jpy": 1.46e-4, "chf": 1.8e-4, "cad": 1.6e-4, "audusd": 2.6e-4,
          "nzdusd": 2.9e-4, "xauusd_gcf": 2.0e-4, "bz": 4.0e-4, "gspc": 1.0e-4, "ndx": 1.1e-4, "gdaxi": 1.0e-4,
          "n225": 2.6e-4}
TIEN = {"eurusd": ("XM", "US"), "jpy": ("US", "JP"), "audusd": ("AU", "US"), "nzdusd": ("US", "US"),
        "gbpusd": ("US", "US"), "chf": ("US", "US"), "cad": ("US", "US")}      # thieu GB/CH/CA/NZ -> chenh 0 (gia dinh)
HANG_DONG = {"n225": 1, "gdaxi": 2, "gspc": 3, "ndx": 3, "xauusd_gcf": 4, "bz": 4}
#: FX = 3: kiem bang HistData (dong 17:00 NY) - nen ngay FX cua Yahoo KHONG dong sau My/vang (cheo vang->AUDUSD:
#: dong thoi t=9,7, giao dich duoc t=-1,6) -> coi nhu dong cung luc, phai tre them mot ngay.
HANG_FX = 3


def loi(ts, e, hs):
    g = VB._close_ngay(ts); idx = g.index
    r = g.pct_change().fillna(0).to_numpy(); e = np.nan_to_num(np.asarray(e, float))
    doi = np.abs(np.diff(np.r_[0.0, e]))
    ngay = np.r_[1.0, np.diff(idx.values).astype("timedelta64[D]").astype(float)]
    if ts in TIEN:
        import fx_vi_mo as FX
        b = FX.bis(idx); x, y = TIEN[ts]
        fin = e * (b[x] - b[y]).fillna(0).to_numpy() - np.abs(e) * 0.01
    else:
        fin = -e * MV.lai_suat(idx) - np.abs(e) * 0.025
    return pd.Series(e * r - doi * (SPREAD[ts] * hs / 2 + 0.5e-4) + fin * ngay / 365, index=idx)


def o_ngay(ten, hs):
    ts, kieu, k = ten.split("|")
    g = VB._close_ngay(ts); idx = g.index
    if kieu == "cheo":
        a = VB._close_ngay(k).pct_change()
        tre = 2 if HANG_DONG.get(k, HANG_FX) >= HANG_DONG.get(ts, HANG_FX) else 1
        s = np.sign(a.shift(tre - 1).reindex(idx, method="ffill").shift(1)).to_numpy()
        return idx, s
    k = int(k)
    m = {"thu": idx.dayofweek == k, "ngay": idx.day == k, "thang": idx.month == k}[kieu]
    return idx, m.astype(float)


def o_gio(ten, hs, huong):
    ts, _, k = ten.split("|"); k = int(k)
    d = pd.read_csv(f"/workspace/du_lieu_fx/{ts}_h1_tick_ba_ny7.csv", index_col=0, parse_dates=True)
    import vong_thu_nghiem as VT
    cp = VT.mo_hinh_chi_phi(d[["open", "high", "low", "close"]], ma=ts.upper())
    raw = (d["spread_open"] / d["open"]).shift(-1)       # spread tick dau bar SAU ~ luc dong bar nay
    markup = float(np.mean(cp.spread_mang(d.index))) - float(raw.mean())
    ra = []
    t = d.index
    for i in range(1, len(d) - 1):
        if t[i].hour == k and (t[i] - t[i - 1]) == pd.Timedelta(hours=1):
            vao_bid, ra_bid = d["close"].iloc[i - 1], d["close"].iloc[i]
            sp_vao = (raw.iloc[i - 1] + markup) * hs * vao_bid
            sp_ra = (raw.iloc[i] + markup) * hs * ra_bid
            if huong > 0:
                r = ra_bid / (vao_bid + sp_vao) - 1
            else:
                r = vao_bid / (ra_bid + sp_ra) - 1
            if np.isfinite(r):
                ra.append((t[i], r - 1e-4))
    return pd.Series([x[1] for x in ra], index=pd.DatetimeIndex([x[0] for x in ra]))


def main():
    q = json.load(open("reports/vong11b.json"))["quet"]["song_holm"]
    out = []
    for x in q:
        ten, h = x["o"], x["huong"]
        rec = {"o": ten, "huong": h}
        for hs in (1.0, 1.5):
            if "|gio|" in ten:
                if not __import__("os").path.exists(f"/workspace/du_lieu_fx/{ten.split('|')[0]}_h1_tick_ba_ny7.csv"):
                    rec["loi"] = "khong co tick"; break
                L = o_gio(ten, hs, h)
                c = L.index[0] + (L.index[-1] - L.index[0]) / 2
                v = L[L.index >= c].to_numpy()
                eq = np.cumprod(1 + v)
                rec[f"x{hs:g}"] = {"n": len(v), "loi_pct": round((eq[-1] - 1) * 100, 2),
                                   "maxdd_pct": round(float(np.max(1 - eq / np.maximum.accumulate(eq))) * 100, 2),
                                   "tb_bps": round(v.mean() * 1e4, 2)}
            else:
                idx, e = o_ngay(ten, hs)
                L = loi(ten.split("|")[0], h * e, hs)
                c = idx[0] + (idx[-1] - idx[0]) / 2
                v = L[L.index >= c]
                rec[f"x{hs:g}"] = MV.do(v.to_numpy(), v.index)
        if "x1.5" in rec:
            rec["song"] = all(rec[k]["loi_pct"] > 0 and rec[k]["maxdd_pct"] < 80 for k in ("x1", "x1.5"))
        out.append(rec)
        print(ten, h, rec.get("x1"), rec.get("x1.5", {}).get("loi_pct"), rec.get("song"))
    json.dump({"nhan": "MO PHONG", "o": out, "song": [r["o"] for r in out if r.get("song")]},
              open("reports/vong11b_xac_nhan.json", "w"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    main()
