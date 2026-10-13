# -*- coding: utf-8 -*-
"""Vong 26: MRZ/RSI trailing D1 tren GBPUSD/AUDUSD (+pool FX), vao lech khoi 00:00, ghep phong cach. Phi XM that.
Dang ky: reports/vong26_tien_dang_ky.md. MO PHONG."""
from __future__ import annotations
import json, sys
import numpy as np
import pandas as pd
import mua_vu as MV
import v19, v22, v23, v24
import phi_xm_that as PX

FX7 = ["EURUSD_X", "GBPUSD_X", "JPY_X", "AUDUSD_X", "NZDUSD_X", "USDCAD_X", "USDCHF_X"]
NHOM = {"GBPUSD": ["GBPUSD_X"], "AUDUSD": ["AUDUSD_X"], "POOL_FX": FX7}
M5 = {"EURUSD_X": "eurusd", "GBPUSD_X": "gbpusd", "JPY_X": "usdjpy", "AUDUSD_X": "audusd", "NZDUSD_X": "nzdusd", "USDCAD_X": "usdcad", "USDCHF_X": "usdchf"}
DU = "/workspace/du_lieu_fx/"
_SP = {}


def sp_gio(ten, gio):
    """Trung vi spread mo nen H1 (bps) do tu XM-like bid/ask tick 2024-2026 (du_lieu_fx/*_h1_tick_ba_ny7.csv), gio server."""
    if ten not in _SP:
        d = pd.read_csv(DU + f"{M5[ten]}_h1_tick_ba_ny7.csv", parse_dates=["time"])
        _SP[ten] = (d.spread_open / d.open).groupby(d.time.dt.hour).median().to_dict()
    return _SP[ten][gio]


TACH_A = pd.Timestamp("2015-04-01"); TACH_B = pd.Timestamp("2025-05-15")


def loc(d, sig, kieu):
    c = d["close"]; sig = sig.copy()
    if kieu == "XU_HUONG":
        e = c.ewm(span=200, adjust=False).mean(); sl = np.sign(e.diff()).fillna(0).to_numpy(); sig[sig != sl] = 0
    elif kieu == "VOL_THAP":
        a = pd.Series(v23.atr(d["high"].to_numpy(), d["low"].to_numpy(), c.to_numpy()), index=d.index)
        sig[~(a < a.rolling(250).median().shift()).to_numpy()] = 0
    return sig


def lenh(d, he, kieu, sp):
    s, atr, _ = v19.tin_hieu(d)
    if kieu == "DANH_MUC":
        return v22.chay(d, s[he].astype(int), "TR2", atr, sp) + v22.chay(d, s["DINH20"].astype(int), "TR2", atr, sp)
    return v22.chay(d, loc(d, s[he].astype(int), kieu), "TR2", atr, sp)


def danh_gia(T, n_ts, tach):
    v24.TACH_DONG[0] = tach; return v24.danh_gia(T, n_ts)


def chay_o(B, ten_ts, he, kieu, tach, spread_fn):
    kq = {}
    for che, hs, sl in (("truoc", 0, 0), ("sau", 1, 0.5), ("sau_x15_s1", 1.5, 1.0)):
        T = []
        for ten in ten_ts:
            d = B[ten]; c = d["close"].to_numpy()
            drift = float(np.mean(np.diff(np.log(c[d.index < tach])))) if (d.index < tach).sum() > 50 else 0.0
            sp = d["close"].to_numpy() * spread_fn(ten) * hs
            T += v24.tra(lenh(d, he, kieu, sp), drift, che != "truoc", sl)
        q = danh_gia(T, len(ten_ts), tach)
        if q: kq[che] = q
    return kq


def d1_dich(ten, k):
    d = pd.read_csv(DU + f"{M5[ten]}_m5_histdata_ny7.csv", parse_dates=["time"]).set_index("time")
    d.index = d.index - pd.Timedelta(hours=k)
    g = d.resample("1D").agg({"open": "first", "high": "max", "low": "min", "close": "last", "tick_volume": "count"}).dropna()
    g = g[g["tick_volume"] >= 144].drop(columns="tick_volume")   # >= 12h du lieu M5
    g["spread_open"] = 0.0; g["so_tick"] = 1; return g


def main(ra=None):
    out = []
    D1 = {k: v for k, v in v24.tai_d1().items() if k in FX7}
    for nh, ts in NHOM.items():
        for he in ("MRZ", "RSI"):
            for kieu in ("KHONG", "XU_HUONG", "VOL_THAP", "DANH_MUC"):
                r = {"phan": "A_proxy_D1", "nhom": nh, "he": he + "_TR2_D1", "ghep": kieu, "phi": "spread_do_02h", **chay_o(D1, ts, he, kieu, TACH_A, lambda t: sp_gio(t, 2))}
                out.append(r); print(json.dumps(r, default=float)[:400], flush=True)
            r = {"phan": "A_doi_chieu_00h", "nhom": nh, "he": he + "_TR2_D1", "ghep": "KHONG", "phi": "spread_do_00h", **chay_o(D1, ts, he, "KHONG", TACH_A, lambda t: sp_gio(t, 0))}
            out.append(r); print(json.dumps(r, default=float)[:400], flush=True)
    for k in (0, 1, 2, 3):
        B = {t: d1_dich(t, k) for t in FX7}
        for nh, ts in NHOM.items():
            for he in ("MRZ", "RSI"):
                r = {"phan": "B_dich_gio", "k_gio": k, "nhom": nh, "he": he + "_TR2_D1", "ghep": "KHONG", "phi": f"spread_do_{k:02d}h",
                     **chay_o(B, ts, he, "KHONG", TACH_B, lambda t, k=k: sp_gio(t, k))}
                out.append(r); print(json.dumps(r, default=float)[:400], flush=True)
    return out


def holm_cu():
    cu = v23.v22_ho() + [x["p"] for x in json.load(open("reports/vong23.json"))["o"] if "p" in x] + \
        [x["sau"]["p"] for x in json.load(open("reports/vong24.json"))["he"] if "sau" in x] + \
        [x["sau"]["p"] for x in json.load(open("reports/vong25.json"))["o"] if "sau" in x]
    assert len(cu) == json.load(open("reports/vong25.json"))["ho_holm"], len(cu)
    # lan chay so bo cung vong (phi bang XM cu) van dem vao ho
    return cu + [x["sau"]["p"] if "sau" in x else 1.0 for x in json.load(open("reports/vong26_so_bo_phi_bang.json"))["o"]]


def cham(o, cu):
    """o: list ket qua; ghi p_holm/song. Ca o khong do duoc (thieu lenh) van dem 1 phep thu voi p=1."""
    H = MV.holm(cu + [r["sau"]["p"] if "sau" in r else 1.0 for r in o])
    for r, h in zip(o, H[len(cu):]):
        s = r.get("sau"); x = r.get("sau_x15_s1"); r["p_holm"] = h
        r["song"] = bool(s and h < 0.05 and s["p_boot"] < 0.05 and s["tb_ph_bps"] > 0 and s["tb_kiem_bps"] > 0 and x and x["tb_kiem_bps"] > 0 and s["maxdd_pct"] < 80)
    return len(H)


if __name__ == "__main__":
    o = main(); cu = holm_cu(); n = cham(o, cu)
    print("ho", n, "song", sum(r["song"] for r in o))
    json.dump({"nhan": "MO PHONG", "ho_holm": n, "o": o}, open(sys.argv[1] if len(sys.argv) > 1 else "reports/vong26.json", "w"), ensure_ascii=False, indent=0, default=float)
