# -*- coding: utf-8 -*-
"""Vong 15: kiem da tru xu huong (hoan vi dich vong + vuot mua-giu khop phoi nhiem). Dang ky truoc reports/vong15_tien_dang_ky.md. MO PHONG."""
from __future__ import annotations

import json
import math
import sys

import numpy as np
import pandas as pd

import fx_vi_mo as FX
import lich_su_kien as LS
import mua_vu as MV
import v14

RNG = np.random.default_rng(15)
NHOAN = 2000


def _ohlc(t):
    d = pd.read_csv(f"/workspace/du_lieu_ngay/{t}_ohlc_yahoo.csv", index_col=0, parse_dates=True)
    return d[d.index >= "1990-01-01"]


def _ibs_e(d):
    x = ((d["close"] - d["low"]) / (d["high"] - d["low"])).to_numpy()
    return np.r_[0.0, (x[:-1] < 0.2).astype(float)]


def chan(ten):
    """-> list (trong so, chuoi gia, e, ham phi(e, hs) -> loi rong)."""
    if ten in ("DANH_MUC_4_SPX", "DAU_CUOI_THANG", "SANTA"):
        g = MV.doc("spx_d1_yahoo.csv", "1950-01-01")
        e = FX.quy_tac("DANH_MUC_4_SPX")[0][1] if ten == "DANH_MUC_4_SPX" else MV.phoi_nhiem(ten, g)
        return [(1.0, g, np.asarray(e, float), lambda e, hs, g=g: MV.chay(g, e, FX.SPREAD["spx"], hs))]
    if ten in ("IBS_SPX", "V6_IBS"):
        out = []
        for t, sp, w in (("gspc", 1e-4, 1.0 if ten == "IBS_SPX" else 0.5), ("ndx", 1.1e-4, 0.5)):
            if ten == "IBS_SPX" and t == "ndx": continue
            d = _ohlc(t); out.append((w, d["close"], _ibs_e(d), lambda e, hs, c=d["close"], sp=sp: MV.chay(c, e, sp, hs)))
        return out
    if ten == "NDX_SAU_USDCAD_GIAM":
        s = v14.gia("ndx"); idx = s.index; rA = v14.gia("usdcad").pct_change()
        mo = idx[:-1] - pd.Timedelta(days=1)
        sig = np.r_[np.nan, rA.reindex(rA.index.union(mo)).ffill().reindex(mo).to_numpy()]
        e = (np.nan_to_num(np.sign(sig)) == -1).astype(float)
        return [(1.0, s, e, lambda e, hs, s=s: MV.chay(s, e, 1.5e-4, hs))]
    if ten == "TNX_USDJPY":
        e = np.asarray(FX.quy_tac("TNX_USDJPY")[0][1], float); g = FX.gia("jpy")
        return [(1.0, g, np.nan_to_num(e), lambda e, hs: FX.loi_rong("jpy", e, hs)[0])]
    raise KeyError(ten)


def chuoi(cs, hs, k=0):
    ds = []
    for w, g, e, f in cs:
        ee = np.roll(e, k) if k else e
        ds.append(pd.Series(w * np.asarray(f(ee, hs)), index=g.index))
    return pd.concat(ds, axis=1).fillna(0).sum(axis=1)


def vuot(cs, hs, tu=0.0):
    L = chuoi(cs, hs); bh = chuoi([(w, g, np.ones(len(e)), f) for w, g, e, f in cs], hs)
    expo = np.mean([np.mean(np.abs(e)) for _, _, e, _ in cs])
    c = int(len(L) * tu)
    return float((L.iloc[c:].mean() - expo * bh.iloc[c:].mean()) * 252 * 100)   # %/nam


def kiem(ten):
    cs = chan(ten); n = min(len(e) for _, _, e, _ in cs)
    thuc = chuoi(cs, 1.0).mean()
    ks = RNG.integers(252, n - 252, NHOAN)
    hv = np.array([chuoi(cs, 1.0, int(k)).mean() for k in ks])
    z = (thuc - hv.mean()) / hv.std(ddof=1)
    L = chuoi(cs, 1.0)
    o = {"he": ten, "z": float(z), "p": MV.p1(z), "p_thuc_nghiem": float((np.sum(hv >= thuc) + 1) / (NHOAN + 1)),
         "maxdd_pct": MV.do(L.to_numpy(), L.index)["maxdd_pct"]}
    for hs in (1.0, 1.5):
        o[f"vuot_toan_x{hs:g}"] = vuot(cs, hs); o[f"vuot_30cuoi_x{hs:g}"] = vuot(cs, hs, 0.7)
    return o


def cpi_o():
    ev = set(LS.cpi()); out = []
    for t in v14.TS:
        s = v14.gia(t); idx = s.index; r = s.pct_change().fillna(0).to_numpy(); nua = np.asarray(idx < idx[len(idx) // 2])
        e = np.array([x.date() in ev for x in idx])
        for cs, m in (("truoc", np.r_[e[1:], False]), ("ngay", e), ("sau", np.r_[False, e[:-1]])):
            q = v14.p_o(r - r[nua].mean() * 0, m, nua)
            # tru xu huong: so voi trung binh moi ngay nua KIEM
            a, b = m & nua, m & ~nua
            if a.sum() < 20 or b.sum() < 20: continue
            sg = 1.0 if r[a].mean() - r[nua].mean() > 0 else -1.0
            x, y = sg * r[b], sg * r[~nua & ~m]
            t_ = (x.mean() - y.mean()) / math.sqrt(x.var(ddof=1) / len(x) + y.var(ddof=1) / len(y))
            out.append({"ts": t, "o": f"cpi_{cs}", "huong": sg, "p": MV.p1(t_), "n_kiem": int(b.sum())})
    return out


HE = ["DANH_MUC_4_SPX", "DAU_CUOI_THANG", "SANTA", "IBS_SPX", "V6_IBS", "NDX_SAU_USDCAD_GIAM", "TNX_USDJPY"]


def main(ra=None):
    v14j = json.load(open("reports/vong14.json"))
    cu = v14.p_cu() + [x["p"] for x in v14j["o"]]
    he = [kiem(t) for t in HE]; cp = cpi_o()
    ps = cu + [x["p"] for x in he] + [x["p"] for x in cp]
    H = MV.holm(ps); B = v14.bh(ps)
    for x, h, q in zip(he + cp, H[len(cu):], B[len(cu):]): x["p_holm"] = h; x["q_bh"] = q
    print("ho", len(ps))
    for o in he:
        o["song"] = o["p_holm"] < 0.05 and o["maxdd_pct"] < 80 and all(o[k] > 0 for k in o if k.startswith("vuot_"))
        print(o["he"], "z %.2f p %.2e pTN %.4f holm %.3f bh %.3f" % (o["z"], o["p"], o["p_thuc_nghiem"], o["p_holm"], o["q_bh"]),
              "vuot toan %.2f/%.2f 30cuoi %.2f/%.2f" % (o["vuot_toan_x1"], o["vuot_toan_x1.5"], o["vuot_30cuoi_x1"], o["vuot_30cuoi_x1.5"]),
              "DD", o["maxdd_pct"], "SONG" if o["song"] else "-")
    cp.sort(key=lambda x: x["p"]); print("CPI min", [(x["ts"], x["o"], round(x["p"], 4), round(x["p_holm"], 3)) for x in cp[:5]])
    if ra:
        json.dump({"nhan": "MO PHONG", "ho_holm": len(ps), "he": he, "cpi": cp}, open(ra, "w"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
