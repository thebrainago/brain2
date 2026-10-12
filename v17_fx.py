# -*- coding: utf-8 -*-
"""Vong 17 (3)+(4): dao chieu ghep + pha vo tren FX H1 bid/ask that (HistData tick). Dang ky truoc reports/vong17_tien_dang_ky.md. MO PHONG."""
from __future__ import annotations

import itertools as it
import json
import math
import sys

import numpy as np
import pandas as pd

import mua_vu as MV

CAP = ["eurusd", "gbpusd", "usdjpy", "audusd", "nzdusd", "usdcad", "usdchf"]
XM = 1.2; QD = 0.025 / 365


def tai(cap):
    d = pd.read_csv(f"/workspace/du_lieu_fx/{cap}_h1_tick_ba_ny7.csv", parse_dates=["time"]).set_index("time")
    return d[d["so_tick"] > 0]


def chi_bao(d):
    c, h, l = d["close"], d["high"], d["low"]
    dl = c.diff(); up = dl.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean(); dn = (-dl.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    ma = c.rolling(20).mean(); sd = c.rolling(20).std(ddof=0)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean(); sig = macd.ewm(span=9, adjust=False).mean()
    k = (100 * (c - l.rolling(14).min()) / (h.rolling(14).max() - l.rolling(14).min())).rolling(3).mean()
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / 14, adjust=False).mean(); atr100 = tr.rolling(100).mean()
    ngay = d.index.normalize()
    hd = h.groupby(ngay).max(); ld = l.groupby(ngay).min()
    dinh_hq = pd.Series(hd.shift().reindex(ngay).to_numpy(), index=d.index); day_hq = pd.Series(ld.shift().reindex(ngay).to_numpy(), index=d.index)
    sang = d.index.hour < 8
    ha = h.where(sang).groupby(ngay).transform("max"); la = l.where(sang).groupby(ngay).transform("min")
    x = {}
    x["RSI"] = np.where(rsi < 30, 1, np.where(rsi > 70, -1, 0))
    x["BB"] = np.where(c < ma - 2 * sd, 1, np.where(c > ma + 2 * sd, -1, 0))
    up_ = (macd > sig) & (macd.shift() <= sig.shift()); dn_ = (macd < sig) & (macd.shift() >= sig.shift())
    x["MACD"] = np.where(up_ & (macd < 0), 1, np.where(dn_ & (macd > 0), -1, 0))
    x["STO"] = np.where(k < 20, 1, np.where(k > 80, -1, 0))
    b = {}
    b["DINH20"] = np.where(c > h.shift().rolling(20).max(), 1, np.where(c < l.shift().rolling(20).min(), -1, 0))
    b["NGAY_TRUOC"] = np.where((c > dinh_hq) & (c.shift() <= dinh_hq), 1, np.where((c < day_hq) & (c.shift() >= day_hq), -1, 0))
    sau = d.index.hour >= 8
    b["PHIEN_A"] = np.where(sau & (c > ha) & (c.shift() <= ha), 1, np.where(sau & (c < la) & (c.shift() >= la), -1, 0))
    b["NEN_LON"] = np.where((h - l) > 2 * atr.shift(), np.sign(c - d["open"]), 0)
    return x, b, atr.to_numpy(), (atr / atr100).to_numpy()


def chay(d, tin, quan_ly, atr, tl, hs=1.0):
    o = d["open"].to_numpy(); c = d["close"].to_numpy(); sp = d["spread_open"].to_numpy() * XM * hs
    hr = d.index.hour.to_numpy(); h4 = (d.index.normalize().asi8 // 3_600_000_000_000 + hr // 4)
    n = len(c); lenh = []; i = 0
    while i < n - 2:
        s = tin[i]
        if s == 0 or not np.isfinite(atr[i]): i += 1; continue
        j0 = i + 1; vao = o[j0] + (sp[j0] if s > 0 else 0)
        dinh = c[j0]; j = j0; ra_ = None
        while j < n - 1:
            ma = None
            if quan_ly == "GIU6" and j - j0 + 1 >= 6: ma = True
            elif quan_ly == "GIU3" and j - j0 + 1 >= 3: ma = True
            elif quan_ly in ("TRAIL2", "TRAIL1.5"):
                k = 2.0 if quan_ly == "TRAIL2" else 1.5
                dinh = max(dinh, c[j]) if s > 0 else min(dinh, c[j])
                if (s > 0 and c[j] < dinh - k * atr[j]) or (s < 0 and c[j] > dinh + k * atr[j]) or j - j0 + 1 >= (48 if k == 2 else 24): ma = True
            elif quan_ly == "HET_H4" and h4[j + 1] != h4[j0]: ma = True
            elif quan_ly == "VOL" and ((np.isfinite(tl[j]) and tl[j] > 1.5) or j - j0 + 1 >= 48): ma = True
            elif quan_ly == "SOM" and ((j - j0 + 1 == 2 and (c[j] - vao) * s <= 0) or j - j0 + 1 >= 24): ma = True
            if ma: ra_ = j + 1; break
            j += 1
        if ra_ is None: break
        ra = o[ra_] + (sp[ra_] if s < 0 else 0)
        dem = int(np.sum(np.diff(hr[j0:ra_ + 1]) < 0))
        lenh.append((d.index[j0], s * (ra - vao) / vao - dem * QD))
        i = ra_
    return lenh


def thong_ke(lenh, giua):
    a = np.array([x for t, x in lenh if t < giua]); b = np.array([x for t, x in lenh if t >= giua])
    if len(a) < 20 or len(b) < 20 or b.std(ddof=1) == 0: return None
    eq = np.cumprod(1 + np.array([x for _, x in lenh])); dd = float(np.max(1 - eq / np.maximum.accumulate(eq))) * 100
    return {"n_ph": len(a), "n_kiem": len(b), "tong_ph_pct": float(a.sum() * 100), "tong_kiem_pct": float(b.sum() * 100),
            "p": MV.p1(b.mean() / b.std(ddof=1) * math.sqrt(len(b))), "maxdd_pct": dd}


def main(ra=None):
    out = []
    for cap in CAP:
        d = tai(cap); x, b, atr, tl = chi_bao(d); giua = d.index[len(d) // 2]
        o_ = []
        for k in (1, 2, 3):
            for to in it.combinations(x, k):
                m = np.stack([x[t] for t in to]); tin = np.where((m == 1).all(0), 1, np.where((m == -1).all(0), -1, 0))
                for q in ("GIU6", "TRAIL2", "HET_H4", "VOL"): o_.append(("dao_chieu", "+".join(to), q, tin))
        for t, tin in b.items():
            for q in ("GIU3", "TRAIL1.5", "SOM"): o_.append(("pha_vo", t, q, np.asarray(tin)))
        for loai, ten, q, tin in o_:
            s = thong_ke(chay(d, tin, q, atr, tl), giua)
            r = {"cap": cap, "loai": loai, "vao": ten, "quan_ly": q}
            if s: r.update(s)
            out.append(r)
        print(cap, "xong", flush=True)
    v = [r for r in out if "p" in r]
    ps0 = json.load(open("reports/vong16.json"))["ho_holm"]
    print("o co du lenh", len(v), "/", len(out))
    import v14, v17_don_bay  # noqa
    cu = v14.p_cu() + [x["p"] for x in json.load(open("reports/vong14.json"))["o"]] + [x["p"] for x in json.load(open("reports/vong15.json"))["he"]] + \
        [x["p"] for x in json.load(open("reports/vong15.json"))["cpi"]] + [x["p"] for x in json.load(open("reports/vong16.json"))["o"]] + \
        [x["p"] for x in json.load(open("reports/vong17_don_bay.json"))["loc"]]
    assert len(cu) == ps0 + 12
    H = MV.holm(cu + [r["p"] for r in v])
    for r, h in zip(v, H[len(cu):]): r["p_holm"] = h
    v.sort(key=lambda r: r["p"])
    for r in v[:12]:
        print(r["cap"], r["loai"], r["vao"], r["quan_ly"], "n", r["n_ph"], r["n_kiem"], "ph %.1f kiem %.1f" % (r["tong_ph_pct"], r["tong_kiem_pct"]), "p %.4f holm %.3f DD %.1f" % (r["p"], r["p_holm"], r["maxdd_pct"]))
    print("lai ca 2 nua:", sum(r["tong_ph_pct"] > 0 and r["tong_kiem_pct"] > 0 for r in v), "kiem lai:", sum(r["tong_kiem_pct"] > 0 for r in v),
          "trung vi kiem %.1f" % np.median([r["tong_kiem_pct"] for r in v]))
    if ra: json.dump({"nhan": "MO PHONG", "ho_holm": len(H), "o": out}, open(ra, "w"), ensure_ascii=False, default=float)
    return v


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
