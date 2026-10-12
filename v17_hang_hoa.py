# -*- coding: utf-8 -*-
"""Vong 17 (5): mua vu hang hoa futures lien tuc Yahoo + xep hang loai tai san. Dang ky truoc reports/vong17_hang_hoa_tien_dang_ky.md. MO PHONG."""
from __future__ import annotations

import json
import math
import sys

import numpy as np
import pandas as pd

import mua_vu as MV
import v14

HH = {"ng": 10e-4, "cl": 4e-4, "bz": 4e-4, "gc": 2e-4, "si": 4e-4, "hg": 5e-4, "zc": 8e-4, "zw": 8e-4, "zs": 8e-4, "kc": 8e-4, "sb": 8e-4, "cc": 8e-4, "ct": 8e-4}


def loi(t):
    s = pd.read_csv(f"/workspace/du_lieu_ngay/hh_{t}_yahoo.csv", index_col=0, parse_dates=True)["close"]
    s = s[s > 0]; r = s.pct_change()
    r[r.abs() > 0.08] = 0.0            # xap xi bo khoang trong roll (va ca ngay bien dong that > 8 %)
    return r.fillna(0.0)


def don(F):
    return {k: v for k, v in F.items() if not k.startswith("chuky")}


def main(ra=None):
    out = []
    for t in HH:
        r = loi(t); idx = r.index; x = r.to_numpy(); nua = np.asarray(idx < idx[len(idx) // 2])
        for o, m in don(v14.dac_trung(idx)).items():
            a, b = m & nua, m & ~nua
            if a.sum() < 20 or b.sum() < 20: continue
            sg = 1.0 if x[a].mean() - x[nua].mean() > 0 else -1.0
            u, w = sg * x[b], sg * x[~nua & ~m]
            z = (u.mean() - w.mean()) / math.sqrt(u.var(ddof=1) / len(u) + w.var(ddof=1) / len(w))
            # sau phi: giu o (huong sg) nhung ngay trong o; khong qua dem rieng (futures)
            e = sg * m.astype(float); doi = np.abs(np.diff(np.r_[0.0, e]))
            res = {}
            for hs in (1.0, 1.5):
                L = e * x - doi * (HH[t] * hs / 2 + MV.TRUOT)
                k = len(L) // 2
                res[f"kiem_x{hs:g}_pct"] = float((np.prod(1 + L[k:]) - 1) * 100)
                res[f"vuot_kiem_x{hs:g}_pct_nam"] = float((L[k:].mean() - np.mean(np.abs(e[k:])) * sg * x[k:].mean()) * 252 * 100)
                if hs == 1.0: res["maxdd_pct"] = MV.do(L, idx)["maxdd_pct"]
            out.append({"ts": t, "o": o, "huong": sg, "z": float(z), "p": MV.p1(z), "n_kiem": int(b.sum()), **res})
    cu = v14.p_cu() + [x["p"] for x in json.load(open("reports/vong14.json"))["o"]] + [x["p"] for x in json.load(open("reports/vong15.json"))["he"]] + \
        [x["p"] for x in json.load(open("reports/vong15.json"))["cpi"]] + [x["p"] for x in json.load(open("reports/vong16.json"))["o"]] + \
        [x["p"] for x in json.load(open("reports/vong17_don_bay.json"))["loc"]] + \
        [x["p"] for x in json.load(open("reports/vong17_fx.json"))["o"] if "p" in x]
    H = MV.holm(cu + [o["p"] for o in out]); B = v14.bh(cu + [o["p"] for o in out])
    for o, h, q in zip(out, H[len(cu):], B[len(cu):]):
        o["p_holm"] = h; o["q_bh"] = q
        o["song"] = h < 0.05 and o["kiem_x1_pct"] > 0 and o["kiem_x1.5_pct"] > 0 and o["vuot_kiem_x1_pct_nam"] > 0 and o["maxdd_pct"] < 80
    out.sort(key=lambda o: o["p"])
    print("ho", len(H), "o", len(out), "song", sum(o["song"] for o in out))
    for o in out[:10]:
        print(o["ts"], o["o"], o["huong"], "z %.2f p %.5f holm %.3f bh %.3f" % (o["z"], o["p"], o["p_holm"], o["q_bh"]),
              "kiem %.1f/%.1f vuot %.2f DD %.1f" % (o["kiem_x1_pct"], o["kiem_x1.5_pct"], o["vuot_kiem_x1_pct_nam"], o["maxdd_pct"]))
    # xep hang loai tai san: |z| nua kiem (da tru xu huong) - hang hoa (vong nay) vs chi so/FX (o lich vong 14, chi so z tu p)
    loai = {"chi_so": {"spx", "ndx", "gdaxi", "ftse", "n225", "hsi"}, "fx": {"eurusd", "gbpusd", "usdjpy", "audusd", "nzdusd", "usdchf", "usdcad", "audjpy"}}
    v14o = [x for x in json.load(open("reports/vong14.json"))["o"] if x["loai"] == "lich" and "+" not in x["o"]]
    def zp(p): from statistics import NormalDist; return NormalDist().inv_cdf(1 - min(max(p, 1e-12), 1 - 1e-12))
    xh = {}
    for ten, tap in loai.items():
        zs = [zp(x["p"]) for x in v14o if x["ts"] in tap]; xh[ten + " (vong14, so voi 0)"] = (len(zs), round(float(np.median(zs)), 2), round(max(zs), 2))
    zs = [zp(x["p"]) for x in v14o if x["ts"] in ("vang", "dau")]; xh["vang+dau (vong14, so voi 0)"] = (len(zs), round(float(np.median(zs)), 2), round(max(zs), 2))
    zs = [o["z"] for o in out]; xh["hang_hoa (vong17, tru xu huong)"] = (len(zs), round(float(np.median(zs)), 2), round(max(zs), 2))
    for t in HH:
        zs = [o["z"] for o in out if o["ts"] == t]; xh[f"  {t}"] = (len(zs), round(float(np.median(zs)), 2), round(max(zs), 2))
    print("xep hang (so o, trung vi z, z max):"); [print(" ", k, v) for k, v in xh.items()]
    if ra: json.dump({"nhan": "MO PHONG", "ho_holm": len(H), "o": out, "xep_hang": xh}, open(ra, "w"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
