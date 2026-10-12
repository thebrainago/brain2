# -*- coding: utf-8 -*-
"""Vong 12: tai hien he cu cua the-brain (CHI THAM KHAO, khong copy ma/bi mat) trong khung brain2.
Dang ky truoc: reports/vong12_tien_dang_ky.md (commit 3c6b75ae). MO PHONG.   python v12.py --ra reports/vong12.json"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd

import mua_vu as MV

SP_AUDCAD, TRUOT = 2.8e-4, 0.5e-4


def ibs_mot(ten, sp, hs):
    d = pd.read_csv(f"/workspace/du_lieu_ngay/{ten}_ohlc_yahoo.csv", index_col=0, parse_dates=True)
    d = d[d.index >= "1990-01-01"]
    x = ((d["close"] - d["low"]) / (d["high"] - d["low"])).to_numpy()
    e = np.r_[0.0, (x[:-1] < 0.2).astype(float)]
    return pd.Series(MV.chay(d["close"], e, sp, hs), index=d.index)


def v6(hs):
    a, b = ibs_mot("gspc", 1.0e-4, hs), ibs_mot("ndx", 1.1e-4, hs)
    idx = a.index.intersection(b.index)
    idx = idx[idx >= b.index[b.ne(0).argmax()] if False else idx >= "1990-01-01"]
    return 0.5 * a.reindex(idx).fillna(0) + 0.5 * b.reindex(idx).fillna(0)


def _rsi(c, n=14):
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def audcad(quy_tac, hs):
    m5 = pd.read_csv("/workspace/du_lieu_fx/audcad_m5_histdata_ny7.csv", index_col=0, parse_dates=True)
    h4 = m5.resample("4h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    c = h4["close"]
    v = pd.Series(np.nan, index=h4.index)
    if quy_tac == "AUDCAD_RSI_DAO_CHIEU":
        r = _rsi(c); v[r < 30] = 1.0; v[r > 55] = 0.0
    else:
        z = (c - c.rolling(50).mean()) / c.rolling(50).std()
        v[z < -2.5] = 1.0; v[z.abs() < 0.3] = 0.0
    tin = v.ffill().fillna(0.0).to_numpy()
    e = np.r_[0.0, tin[:-1]]                                    # vao o bar sau
    ret = c.pct_change().fillna(0).to_numpy()
    doi = np.abs(np.diff(np.r_[0.0, e]))
    b = pd.read_csv("/workspace/du_lieu_ngay/bis_lai_suat_chinh_sach.csv", index_col=0, parse_dates=True)
    b = b.reindex(b.index.union(h4.index)).ffill().reindex(h4.index) / 100
    dif = (b["AU"] - b["CA"]).fillna(0).to_numpy()
    dt = np.r_[4 / 24, np.diff(h4.index.values).astype("timedelta64[m]").astype(float) / 1440]
    L = e * ret - doi * (SP_AUDCAD * hs / 2 + TRUOT) + (e * dif - np.abs(e) * 0.01) * dt / 365
    s = pd.Series(L, index=h4.index)
    ngay = (1 + s).groupby(s.index.normalize()).prod() - 1
    return ngay, int(np.sum(np.diff(np.r_[0.0, e]) > 0))


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--ra"); a = ap.parse_args(argv)
    ra = []
    for ten in ("V6_IBS_DANH_MUC", "AUDCAD_RSI_DAO_CHIEU", "AUDCAD_OU_N50_Z25_MUA"):
        o = {"quy_tac": ten}
        for hs in (1.0, 1.5):
            if ten.startswith("V6"):
                L = v6(hs); lenh = None
            else:
                L, lenh = audcad(ten, hs)
            v, idx = L.to_numpy(), L.index; c = int(len(v) * 0.7)
            m = np.asarray(idx.year >= 2010)
            o[f"x{hs:g}"] = {"toan": MV.do(v, idx), "nm": MV.do(v[c:], idx[c:]),
                             "sau_cong_bo": MV.do(v[m], idx[m]) if ten.startswith("V6") else None}
        o.update(tu=str(idx[0].date()), den=str(idx[-1].date()), so_lenh=lenh, p=MV.p1(o["x1"]["toan"]["t"]))
        ra.append(o)
    cu = json.load(open("reports/vong11_tong_hop.json"))
    v10 = json.load(open("reports/vong10_mua_vu.json"))["quy_tac"]; v11 = json.load(open("reports/vong11_fx_vi_mo.json"))["quy_tac"]
    b = json.load(open("reports/vong11b.json"))
    ps = [x["p"] for x in v11] + [x["p"] for x in v10] + [b["vang_m30"][k]["x1"]["p"] for k in ("vn", "server", "gmt")] + [b["ibs"]["p"]]
    ph = MV.holm(ps + [o["p"] for o in ra])
    for o, q in zip(ra, ph[len(ps):]):
        o["p_holm_29"] = q
        x1, x15 = o["x1"], o["x1.5"]
        tc = {"lai_toan": x1["toan"]["loi_pct"] > 0, "dd_lt_80": x1["toan"]["maxdd_pct"] < 80,
              "nm_lai_x1": x1["nm"]["loi_pct"] > 0, "nm_lai_x1_5": x15["nm"]["loi_pct"] > 0, "p_holm_lt_005": q < 0.05}
        if x1["sau_cong_bo"]:
            tc["sau_cong_bo"] = x1["sau_cong_bo"]["sharpe"] > 0
        o["tieu_chi"] = tc; o["song"] = all(tc.values())
        print(o["quy_tac"], o["tu"], o["so_lenh"], x1["toan"], "NM", x1["nm"]["loi_pct"], x15["nm"]["loi_pct"],
              "p %.4f holm %.4f" % (o["p"], q), "SONG" if o["song"] else "-")
    names = list(cu["p_holm"]) + [o["quy_tac"] for o in ra]
    out = {"nhan": "MO PHONG", "ho_holm": len(ph), "quy_tac": ra, "p_holm_29": dict(zip(names, ph))}
    print({k: round(v, 4) for k, v in out["p_holm_29"].items() if v < 0.1})
    if a.ra:
        json.dump(out, open(a.ra, "w"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    main()
