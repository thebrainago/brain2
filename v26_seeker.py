# -*- coding: utf-8 -*-
"""Vong 26 phan C: kiem nhanh luat Seeker moi (reports/seeker_v26/LUAT_TRICH.json) - truoc phi -> sau phi XM (spread do theo gio).
EMA12/26 cat (mql5 77653, D1, Yahoo 2004-2026, tach 2015-04-01); RSI_Exhaustion (mql5 77738: ban khi RSI14 cat len 65 trong 14-18h, H1
M5 HistData 2024-2026, tach 2025-05-15). Giu 1 nen (giu=1 theo bo doc; SL ATR cua EA BO QUA -> xap xi). Eliot_Waves: dieu kien
luon dung (low[1] < high) -> khong co tin hieu thuc, khong kiem. MO PHONG."""
import json
import numpy as np
import pandas as pd
import v24, v26

def lenh_ema(d):
    c = d["close"]; f, s = c.ewm(span=12, adjust=False).mean(), c.ewm(span=26, adjust=False).mean()
    up = (f > s) & (f.shift() <= s.shift()); dn = (f < s) & (f.shift() >= s.shift())
    return np.where(up, 1, np.where(dn, -1, 0))

def lenh_rsi(d):
    c = d["close"]; dl = c.diff(); u = dl.clip(lower=0).ewm(alpha=1/14, adjust=False).mean(); v = (-dl.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
    r = 100 - 100 / (1 + u / v); h = d.index.hour
    return np.where((r >= 65) & (r.shift() < 65) & (h >= 14) & (h < 18), -1, 0)

def tra(d, sig, sp_fn, phi, hs=1.0, sl=0.5):
    o = d["open"].to_numpy(); hr = d.index.hour; T = []
    for i in np.flatnonzero(sig[:-2]):
        j = i + 1; s = sig[i]; r = s * (o[j + 1] - o[j]) / o[j]
        if phi: r -= hs * sp_fn(hr[j]) + 2 * sl * 1e-4
        T.append((d.index[j], r, d.index[j + 1]))
    return T

def main():
    o = []
    D1 = {k: v for k, v in v24.tai_d1().items() if k in v26.FX7}
    H1 = {}
    for t in v26.FX7:
        m = pd.read_csv(v26.DU + f"{v26.M5[t]}_m5_histdata_ny7.csv", parse_dates=["time"]).set_index("time")
        H1[t] = m.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    for ten, B, f, tach, gio in (("EMA12_26_CAT_D1", D1, lenh_ema, v26.TACH_A, lambda t, h: v26.sp_gio(t, 2)),
                                 ("RSI_EXHAUSTION_H1", H1, lenh_rsi, v26.TACH_B, lambda t, h: v26.sp_gio(t, h))):
        for nh, ts in v26.NHOM.items():
            r = {"he": ten, "nhom": nh}
            for che, phi, hs, sl in (("truoc", False, 1, 0), ("sau", True, 1, 0.5), ("sau_x15_s1", True, 1.5, 1.0)):
                T = []
                for t in ts: T += tra(B[t], f(B[t]), lambda h, t=t: gio(t, h), phi, hs, sl)
                q = v26.danh_gia(T, len(ts), tach)
                if q: r[che] = q
            o.append(r); print(json.dumps(r, default=float)[:300], flush=True)
    cu = v26.holm_cu() + [x["sau"]["p"] if "sau" in x else 1.0 for x in json.load(open("reports/vong26.json"))["o"]]
    n = v26.cham(o, cu); print("ho", n, "song", sum(x["song"] for x in o))
    json.dump({"nhan": "MO PHONG", "ho_holm": n, "o": o}, open("reports/vong26_seeker.json", "w"), ensure_ascii=False, indent=0, default=float)

if __name__ == "__main__":
    main()
