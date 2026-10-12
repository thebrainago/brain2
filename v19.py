# -*- coding: utf-8 -*-
"""Vong 19: nhom chien luoc + trailing + ghep. Dang ky truoc reports/vong19_tien_dang_ky.md. MO PHONG."""
from __future__ import annotations

import glob
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

import numpy as np
import pandas as pd

import mua_vu as MV
import v17_fx as F

XM = 1.2
VAO_NHOM = {"ENGULF": "NEN", "PINBAR": "NEN", "ROC24": "DONG_LUONG", "MACD0": "DONG_LUONG", "RSI": "DAO_CHIEU",
            "DINH20": "BREAKOUT", "MRZ": "MR", "PHIEN_A": "PHIEN_GIO"}
THOAT = ["TP", "GIO6", "TR1", "TR2", "TR3", "CHAND", "BE_TR2", "H4"]


def tin_hieu(d):
    o, h, l, c = (d[k] for k in ("open", "high", "low", "close"))
    x, b, atr, _ = F.chi_bao(d)
    s = {}
    bull = (c > o) & (c.shift() < o.shift()) & (c >= o.shift()) & (o <= c.shift())
    bear = (c < o) & (c.shift() > o.shift()) & (c <= o.shift()) & (o >= c.shift())
    s["ENGULF"] = np.where(bull, 1, np.where(bear, -1, 0))
    rg = (h - l).replace(0, np.nan); lo_w = (np.minimum(o, c) - l) / rg; up_w = (h - np.maximum(o, c)) / rg
    s["PINBAR"] = np.where(lo_w >= 2 / 3, 1, np.where(up_w >= 2 / 3, -1, 0))
    r24 = np.sign(c - c.shift(24)); s["ROC24"] = np.where((r24 != r24.shift()) & (r24 != 0), r24, 0)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean(); m = np.sign(macd)
    s["MACD0"] = np.where((m != m.shift()) & (m != 0), m, 0)
    s["RSI"] = x["RSI"]; s["DINH20"] = b["DINH20"]; s["PHIEN_A"] = b["PHIEN_A"]
    z = (c - c.rolling(50).mean()) / c.rolling(50).std(); s["MRZ"] = np.where(z < -2, 1, np.where(z > 2, -1, 0))
    s = {k: np.nan_to_num(np.asarray(v, float)) for k, v in s.items()}
    return s, atr, r24.fillna(0).to_numpy()


def chay(d, tin, thoat, atr, hs=1.0):
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close"))
    sp = d["spread_open"].to_numpy() * XM * hs; hr = d.index.hour.to_numpy()
    blk = d.index.normalize().asi8 // 3_600_000_000_000 + hr // 4
    n = len(c); out = []; i = 60
    while i < n - 2:
        s = tin[i]; a = atr[i]
        if s == 0 or not np.isfinite(a) or a <= 0: i += 1; continue
        j = i + 1; E = o[j] + sp[j] if s > 0 else o[j]
        st = E - 1.5 * a if s > 0 else E + 1.5 * a           # muc stop theo gia bid (mua) / ask (ban)
        tp = (E + a if s > 0 else E - a) if thoat == "TP" else None
        best = c[j]; be = False; k = j; X = None; h4_lo = h4_hi = None; cur_blk = blk[j]; blk_lo, blk_hi = l[j], h[j]
        while k < n - 1:
            if s > 0:
                if l[k] <= st: X = st; break
                if tp is not None and h[k] >= tp and k > j: X = tp; break
            else:
                if h[k] + sp[k] >= st: X = st; break
                if tp is not None and l[k] + sp[k] <= tp and k > j: X = tp; break
            # cap nhat stop sau khi bar k dong (ap dung tu bar k+1)
            best = max(best, c[k]) if s > 0 else min(best, c[k])
            ak = atr[k]
            def keo(m):
                nonlocal st
                st = max(st, m) if s > 0 else min(st, m)
            if thoat in ("TR1", "TR2", "TR3"):
                kk = int(thoat[2]); keo(best - kk * ak if s > 0 else best + kk * ak)
            elif thoat == "CHAND":
                w = slice(max(j, k - 21), k + 1); keo(h[w].max() - 3 * ak if s > 0 else l[w].min() + 3 * ak)
            elif thoat == "BE_TR2":
                if not be and ((s > 0 and c[k] >= E + ak) or (s < 0 and c[k] <= E - ak)): be = True
                if be: keo(E); keo(best - 2 * ak if s > 0 else best + 2 * ak)
            elif thoat == "H4":
                if blk[k + 1] != cur_blk:
                    keo(blk_lo if s > 0 else blk_hi); cur_blk = blk[k + 1]; blk_lo, blk_hi = l[k + 1], h[k + 1]
                else:
                    blk_lo, blk_hi = min(blk_lo, l[k + 1]), max(blk_hi, h[k + 1])
            if (thoat == "GIO6" and k - j + 1 >= 6) or k - j + 1 >= 72:
                X = o[k + 1] if s > 0 else o[k + 1] + sp[k + 1]; k += 1; break
            k += 1
        if X is None: break
        r = (X - E) / E if s > 0 else (E - X) / E
        dem = int(np.sum(np.diff(hr[j:k + 1]) < 0)); out.append((d.index[j], r - dem * F.QD)); i = max(k, i + 1)
    return out


def tk(lenh, giua):
    a = np.array([x for t, x in lenh if t < giua]); b = np.array([x for t, x in lenh if t >= giua])
    if len(a) < 15 or len(b) < 15 or b.std(ddof=1) == 0: return None
    eq = np.cumprod(1 + np.array([x for _, x in lenh]))
    return {"n_ph": len(a), "n_kiem": len(b), "ph_pct": float(a.sum() * 100), "kiem_pct": float(b.sum() * 100),
            "p": MV.p1(b.mean() / b.std(ddof=1) * math.sqrt(len(b))), "maxdd_pct": float(np.max(1 - eq / np.maximum.accumulate(eq))) * 100}


def loc_ab(sa, sb, nhom_b, r24):
    if nhom_b == "DONG_LUONG": return np.where(np.sign(r24) == np.sign(sa), sa, 0)
    gan = pd.Series(sb).replace(0, np.nan).ffill(limit=24).fillna(0).to_numpy()
    return np.where(np.sign(gan) == np.sign(sa), sa, 0)


def ho_cu():
    import v14
    J = lambda f: json.load(open(f))
    return v14.p_cu() + [x["p"] for x in J("reports/vong14.json")["o"]] + [x["p"] for x in J("reports/vong15.json")["he"]] + \
        [x["p"] for x in J("reports/vong15.json")["cpi"]] + [x["p"] for x in J("reports/vong16.json")["o"]] + \
        [x["p"] for x in J("reports/vong17_don_bay.json")["loc"]] + [x["p"] for x in J("reports/vong17_fx.json")["o"] if "p" in x] + \
        [x["p"] for x in J("reports/vong17_hang_hoa.json")["o"]] + [x["p"] for x in J("reports/vong18.json")["o"] if "p" in x]


def thi_nghiem():
    o1 = []; D = {}
    for cap in F.CAP:
        d = F.tai(cap); s, atr, r24 = tin_hieu(d); giua = d.index[len(d) // 2]; D[cap] = (d, s, atr, r24, giua)
        for v in s:
            for th in THOAT:
                r = {"cap": cap, "vao": v, "nhom": VAO_NHOM[v], "thoat": th}
                q = tk(chay(d, s[v], th, atr), giua)
                if q:
                    r.update(q); q2 = tk(chay(d, s[v], th, atr, 1.5), giua); r["kiem_x1_5_pct"] = q2["kiem_pct"] if q2 else None
                o1.append(r)
        print(cap, "xong", flush=True)
    v1 = [r for r in o1 if "p" in r]
    tv = {g: np.median([r["ph_pct"] for r in v1 if r["nhom"] == g]) for g in set(VAO_NHOM.values())}
    top = sorted(tv, key=lambda g: -tv[g])[:3]
    best_exit = {}
    for v in VAO_NHOM:
        if VAO_NHOM[v] in top:
            best_exit[v] = max(THOAT, key=lambda th: np.median([r["ph_pct"] for r in v1 if r["vao"] == v and r["thoat"] == th] or [-1e9]))
    # moi nhom: tin hieu dai dien = vao co trung vi nua phat hien cao nhat trong nhom
    dai_dien = {g: max([v for v in VAO_NHOM if VAO_NHOM[v] == g], key=lambda v: np.median([r["ph_pct"] for r in v1 if r["vao"] == v])) for g in top}
    o2 = []
    for A in top:
        for B in top:
            if A == B: continue
            va, vb = dai_dien[A], dai_dien[B]
            for th in sorted({best_exit[va], "GIO6", "TR2"}) + ([] if len({best_exit[va], "GIO6", "TR2"}) == 3 else ["TR3"]):
                for cap in F.CAP:
                    d, s, atr, r24, giua = D[cap]
                    tin = loc_ab(s[va], s[vb], B, r24)
                    r = {"cap": cap, "A": f"{A}:{va}", "B": f"{B}:{vb}", "thoat": th}
                    q = tk(chay(d, tin, th, atr), giua)
                    if q:
                        r.update(q); q2 = tk(chay(d, tin, th, atr, 1.5), giua); r["kiem_x1_5_pct"] = q2["kiem_pct"] if q2 else None
                    o2.append(r)
    return o1, o2, {"tv_ph_nhom": tv, "top3": top, "dai_dien": dai_dien, "thoat_tot_ph": best_exit}


# ---------- gan nhan + bang xep hang theo nhom (ket qua cu + moi)
def xep_hang(o1, o2):
    J = lambda f: json.load(open(f)); rows = []
    def add(nhom, nguon, kiem, kiem15, p, net=True): rows.append({"nhom": nhom, "nguon": nguon, "kiem": kiem, "kiem15": kiem15, "p": p, "net": net})
    for x in J("reports/vong17_fx.json")["o"]:
        if "p" not in x: continue
        g = "DAO_CHIEU" if x["loai"] == "dao_chieu" else ("PHIEN_GIO" if x["vao"] == "PHIEN_A" else "BREAKOUT")
        add(g, "v17_fx", x["tong_kiem_pct"], None, x["p"])
    for x in J("reports/vong18.json")["o"]:
        if "p" not in x: continue
        g = {"B1": "PHIEN_GIO", "B2": "VI_MO", "B3": "BREAKOUT", "B4": "DAO_CHIEU"}[x["he"]]
        add(g, "v18", x["kiem_pct"], x.get("kiem_x1_5_truot05_pct"), x["p"])
    for x in J("reports/vong18.json")["hedge"]: add("HEDGE_GRID", "v18_hedge", x["lai_pct"], x["lai_x1_5_truot05_pct"], None)
    for x in J("reports/vong17_hang_hoa.json")["o"]: add("LICH_MUA_VU", "v17_hang_hoa", x["kiem_x1_pct"], x["kiem_x1.5_pct"], x["p"])
    for x in J("reports/vong14.json")["o"]:
        add("LICH_MUA_VU" if x["loai"] == "lich" else "VI_MO", "v14 (truoc phi)", None, None, x["p"], False)
    for x in J("reports/vong15.json")["he"]:
        g = "MR" if "IBS" in x["he"] else ("VI_MO" if x["he"] in ("TNX_USDJPY", "NDX_SAU_USDCAD_GIAM") else "LICH_MUA_VU")
        add(g, "v15", x["vuot_30cuoi_x1"], x["vuot_30cuoi_x1.5"], x["p"])
    for x in J("reports/vong17_don_bay.json")["loc"]: add("DON_BAY", "v17_don_bay", x["vuot_30cuoi"], None, x["p"])
    for x in o1 + o2:
        if "p" in x: add(x.get("nhom") or x["A"].split(":")[0], "v19" if "nhom" in x else "v19_ghep", x["kiem_pct"], x.get("kiem_x1_5_pct"), x["p"])
    bang = {}
    for g in sorted({r["nhom"] for r in rows}):
        xs = [r for r in rows if r["nhom"] == g]; k = [r["kiem"] for r in xs if r["kiem"] is not None]
        k15 = [(r["kiem15"] - r["kiem"]) for r in xs if r["kiem15"] is not None and r["kiem"] is not None]
        ps = [r["p"] for r in xs if r["p"] is not None]
        bang[g] = {"so_co_che": len(xs), "ty_le_lai_kiem_pct": round(100 * np.mean([v > 0 for v in k]), 1) if k else None,
                   "trung_vi_kiem": round(float(np.median(k)), 2) if k else None, "p_tot_nhat": float(min(ps)) if ps else None,
                   "do_nhay_phi_x1_5_trung_vi": round(float(np.median(k15)), 2) if k15 else None}
    return bang


TU_KHOA = [("HEDGE_GRID", r"hedg|grid|martingale|recovery|averag"), ("BREAKOUT", r"breakout|break_out|straddle|\borb\b|donchian|channel"),
           ("PHIEN_GIO", r"session|london|asian|time_?filter|newyork|tokyo"), ("NEN", r"engulf|pinbar|pin_bar|candle|doji|hammer|harami"),
           ("DAO_CHIEU", r"reversal|revers|exhaust|rsi|stoch"), ("MR", r"mean.?revers|bollinger|zscore|z_score|\bbb\b"),
           ("DONG_LUONG", r"momentum|macd|trend|\bma\b|moving.?average|ema|adx|ichimoku|supertrend"),
           ("VI_MO", r"news|calendar|nfp"), ("LICH_MUA_VU", r"season|day_?of_?week|month")]


def nhan_kho():
    dem = Counter(); n = 0
    for f in glob.glob("data/cau_kho/*/**/*.mq[45]", recursive=True):
        n += 1; ten = os.path.basename(f).lower()
        try: vb = open(f, errors="ignore").read(20000).lower()
        except Exception: vb = ""
        g = next((g for g, rx in TU_KHOA if re.search(rx, ten)), None) or next((g for g, rx in TU_KHOA if re.search(rx, vb)), "KHAC")
        dem[g] += 1
    return n, dict(dem)


def main(ra=None):
    o1, o2, chon = thi_nghiem()
    cu = ho_cu(); v = [r for r in o1 + o2 if "p" in r]
    H = MV.holm(cu + [r["p"] for r in v])
    for r, q in zip(v, H[len(cu):]):
        r["p_holm"] = q; r["song"] = q < 0.05 and r["ph_pct"] > 0 and r["kiem_pct"] > 0 and (r.get("kiem_x1_5_pct") or -1) > 0 and r["maxdd_pct"] < 80
    print("ho", len(H), "o moi", len(o1), len(o2), "du lenh", len(v), "song", sum(r["song"] for r in v)); print("chon", chon)
    for r in sorted(v, key=lambda r: r["p"])[:10]:
        print({k: (round(x, 4) if isinstance(x, float) else x) for k, x in r.items()})
    # trailing vs TP/time theo nhom (trung vi nua kiem)
    tr = {}
    for g in sorted(set(VAO_NHOM.values())):
        tr[g] = {th: round(float(np.median([r["kiem_pct"] for r in o1 if "p" in r and r["nhom"] == g and r["thoat"] == th] or [np.nan])), 2) for th in THOAT}
        print("THOAT", g, tr[g])
    bang = xep_hang(o1, o2)
    for g, x in sorted(bang.items(), key=lambda kv: -(kv[1]["trung_vi_kiem"] if kv[1]["trung_vi_kiem"] is not None else -1e9)): print("NHOM", g, x)
    nk = nhan_kho(); print("KHO", nk)
    if ra: json.dump({"nhan": "MO PHONG", "ho_holm": len(H), "o": o1, "ghep": o2, "chon": chon, "thoat_theo_nhom": tr, "bang_nhom": bang, "kho_theo_nhom": nk},
                     open(ra, "w"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
