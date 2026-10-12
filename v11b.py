# -*- coding: utf-8 -*-
"""Vong 11b: vang M30 (quy tac nguoi dung), S&P IBS, quet kham pha/giu lai.
Dang ky truoc: reports/vong11b_tien_dang_ky.md. MO PHONG.   python v11b.py --ra reports/vong11b.json"""
from __future__ import annotations

import argparse
import json
import math

import numpy as np
import pandas as pd

import fx_vi_mo as FX
import mua_vu as MV

DF = "/workspace/du_lieu_fx"


def _sang_utc(idx_server):
    ny = idx_server - pd.Timedelta(hours=7)
    return ny.tz_localize("America/New_York", ambiguous="NaT", nonexistent="NaT").tz_convert("UTC")


def vang_m30(bien_the: str, he_so=1.0):
    m5 = pd.read_csv(f"{DF}/xauusd_m5_histdata_ny7.csv", index_col=0, parse_dates=True)
    utc = _sang_utc(m5.index)
    m5 = m5[utc.notna()]; utc = utc[utc.notna()]
    if bien_the == "vn":
        t = utc.tz_convert(None) + pd.Timedelta(hours=7)
    elif bien_the == "gmt":
        t = utc.tz_convert(None)
    else:
        t = m5.index
    m5 = m5.copy(); m5.index = t
    m30 = m5.resample("30min").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    loi = []; ngay = []
    for d, g in m30.groupby(m30.index.date):
        if pd.Timestamp(d).dayofweek > 4:
            continue
        def bar(hh, mm):
            k = pd.Timestamp(d) + pd.Timedelta(hours=hh, minutes=mm)
            return g.loc[k] if k in g.index else None
        b8, b12, b1230, b1630 = bar(8, 0), bar(12, 0), bar(12, 30), bar(16, 30)
        if any(x is None for x in (b8, b12, b1230, b1630)):
            continue
        dhuong = np.sign(b12["open"] - b8["open"])
        if dhuong == 0:
            continue
        if np.sign(b12["close"] - b12["open"]) == -dhuong and np.sign(b1230["close"] - b1230["open"]) == dhuong:
            r = dhuong * (b1630["close"] / b1230["close"] - 1)
            loi.append(r - (2e-4 * he_so / 2 + 0.5e-4) * 2); ngay.append(pd.Timestamp(d))
    return pd.Series(loi, index=pd.DatetimeIndex(ngay))


def ibs(he_so=1.0):
    d = pd.read_csv("/workspace/du_lieu_ngay/gspc_ohlc_yahoo.csv", index_col=0, parse_dates=True)
    d = d[d.index >= "1990-01-01"]
    x = ((d["close"] - d["low"]) / (d["high"] - d["low"])).to_numpy()
    e = np.r_[0.0, (x[:-1] < 0.2).astype(float)]
    return pd.Series(MV.chay(d["close"], e, 1e-4, he_so), index=d.index)


def do_lenh(L: pd.Series, nam_cb=None):
    """Thong ke tren chuoi loi theo lenh/ngay (L), p mot phia t-test TB."""
    v = L.to_numpy(); n = len(v)
    if n < 10:
        return {"n": n}
    t = v.mean() / (v.std(ddof=1) / math.sqrt(n))
    eq = np.cumprod(1 + v)
    c = int(n * 0.7)
    return {"n": n, "loi_pct": round((eq[-1] - 1) * 100, 2), "maxdd_pct": round(float(np.max(1 - eq / np.maximum.accumulate(eq))) * 100, 2),
            "tb_bps": round(v.mean() * 1e4, 2), "t": round(float(t), 3), "p": MV.p1(t),
            "nm_loi_pct": round((np.prod(1 + v[c:]) - 1) * 100, 2)}


# ---------------------------------------------------------------- quet
NGAY = ["eurusd", "gbpusd", "jpy", "chf", "cad", "audusd", "nzdusd", "xauusd_gcf", "bz", "gspc", "ndx", "gdaxi", "n225"]
GIO = ["eurusd", "gbpusd", "usdjpy", "usdchf", "audusd", "nzdusd", "usdcad", "xauusd"]


def _close_ngay(t):
    import os
    p = f"/workspace/du_lieu_ngay/{t}_ohlc_yahoo.csv"
    if not os.path.exists(p):
        p = f"/workspace/du_lieu_ngay/{t}_d1_yahoo.csv"
    s = pd.read_csv(p, index_col=0, parse_dates=True)["close"]
    return s[s.index >= "1990-01-01"]


def _o(r_kp, r_xn, nhan):
    """Mot o: kham pha (hai phia) -> huong; xac nhan mot phia."""
    def tt(v):
        v = v[np.isfinite(v)]
        return (v.mean() / (v.std(ddof=1) / math.sqrt(len(v))), len(v)) if len(v) > 10 and v.std() > 0 else (0.0, len(v))
    tk, nk = tt(r_kp); tx, nx = tt(r_xn)
    huong = 1.0 if tk >= 0 else -1.0
    return {"o": nhan, "t_kp": round(float(tk), 3), "n_kp": nk, "huong": huong, "t_xn": round(float(huong * tx), 3),
            "n_xn": nx, "p_xn": MV.p1(huong * tx) if nx > 10 else 1.0}


def quet():
    o = []
    for t in NGAY:
        s = _close_ngay(t); r = s.pct_change()
        c = s.index[0] + (s.index[-1] - s.index[0]) / 2
        kp, xn = r[r.index < c], r[r.index >= c]
        for k in range(5):
            o.append(_o(kp[kp.index.dayofweek == k].values, xn[xn.index.dayofweek == k].values, f"{t}|thu|{k}"))
        for k in range(1, 32):
            o.append(_o(kp[kp.index.day == k].values, xn[xn.index.day == k].values, f"{t}|ngay|{k}"))
        for k in range(1, 13):
            o.append(_o(kp[kp.index.month == k].values, xn[xn.index.month == k].values, f"{t}|thang|{k}"))
    cl = {t: _close_ngay(t).pct_change() for t in NGAY}
    for a in NGAY:
        for b in NGAY:
            if a == b:
                continue
            ra = cl[a].shift(1).reindex(cl[b].index)
            x = (np.sign(ra) * cl[b]).dropna()
            c = x.index[0] + (x.index[-1] - x.index[0]) / 2
            o.append(_o(x[x.index < c].values, x[x.index >= c].values, f"{b}|cheo|{a}"))
    for t in GIO:
        m5 = pd.read_csv(f"{DF}/{t}_m5_histdata_ny7.csv", index_col=0, parse_dates=True)
        h = m5["close"].resample("1h").last().dropna(); r = h.pct_change().dropna()
        c = r.index[0] + (r.index[-1] - r.index[0]) / 2
        kp, xn = r[r.index < c], r[r.index >= c]
        for k in range(24):
            o.append(_o(kp[kp.index.hour == k].values, xn[xn.index.hour == k].values, f"{t}|gio|{k}"))
    ps = [x["p_xn"] for x in o]
    ph = MV.holm(ps)
    m = len(ps); od = np.argsort(ps); bh = np.ones(m); prev = 1.0
    for rank in range(m - 1, -1, -1):
        i = od[rank]; prev = min(prev, ps[i] * m / (rank + 1)); bh[i] = prev
    for x, q, f in zip(o, ph, bh):
        x["p_holm"] = q; x["q_bh"] = float(f)
    return o


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--ra"); a = ap.parse_args(argv)
    out = {"nhan": "MO PHONG"}
    a1 = {}
    for bt in ("vn", "server", "gmt"):
        a1[bt] = {"x1": do_lenh(vang_m30(bt, 1.0)), "x1.5": do_lenh(vang_m30(bt, 1.5))}
    L1, L15 = ibs(1.0), ibs(1.5)
    idx = L1.index; v = L1.to_numpy(); c = int(len(v) * 0.7)
    ib = {"x1": {"toan": MV.do(v, idx), "nm": MV.do(v[c:], idx[c:]),
                 "sau_cong_bo": MV.do(v[idx.year >= 2010], idx[idx.year >= 2010])},
          "x1.5": {"nm": MV.do(L15.to_numpy()[c:], idx[c:])}}
    ib["p"] = MV.p1(ib["x1"]["toan"]["t"])
    v11 = json.load(open("reports/vong11_fx_vi_mo.json"))
    ps = [x["p"] for x in v11["quy_tac"]] + list(json.load(open("reports/vong10_mua_vu.json")) and
                                                 [x["p"] for x in json.load(open("reports/vong10_mua_vu.json"))["quy_tac"]])
    ps_moi = [a1[b]["x1"].get("p", 1.0) for b in ("vn", "server", "gmt")] + [ib["p"]]
    ph = MV.holm(ps + ps_moi)
    for b, q in zip(("vn", "server", "gmt"), ph[len(ps):len(ps) + 3]):
        a1[b]["p_holm_26"] = q
    ib["p_holm_26"] = ph[-1]
    out.update(vang_m30=a1, ibs=ib, ho_holm=len(ps) + 4,
               holm_26_cac_quy_tac_cu={x["quy_tac"]: q for x, q in zip(v11["quy_tac"], ph)})
    q = quet()
    out["quet"] = {"so_o": len(q), "song_holm": [x for x in q if x["p_holm"] < 0.05],
                   "fdr10": [x for x in q if x["q_bh"] < 0.10], "tot_nhat": sorted(q, key=lambda x: x["p_xn"])[:15]}
    print(json.dumps({k: out[k] for k in ("vang_m30", "ibs", "ho_holm")}, ensure_ascii=False, indent=0, default=float)[:3000])
    print("quet", len(q), "song holm", len(out["quet"]["song_holm"]), "fdr10", len(out["quet"]["fdr10"]))
    for x in out["quet"]["tot_nhat"][:10]:
        print(x)
    if a.ra:
        json.dump(out, open(a.ra, "w"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    main()
