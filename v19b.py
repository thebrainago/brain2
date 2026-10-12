# -*- coding: utf-8 -*-
"""Vong 19 bo sung: 13 phong cach moi + bo du lieu 2. Dang ky: reports/vong19_tien_dang_ky.md (BO SUNG). MO PHONG."""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

import lich_su_kien as LS
import mua_vu as MV
import v17_fx as F
import v19

NHOM2 = {"DONCHIAN55": "XU_HUONG_DAI", "MA50_200": "XU_HUONG_DAI", "SQUEEZE": "BIEN_DONG", "SWEEP": "SMC", "FVG": "SMC", "PIVOT": "SR_PIVOT",
         "ICHIMOKU": "ICHIMOKU", "FIB": "FIB", "OPENING_RANGE": "PHIEN_GIO", "GAP_FILL": "GAP", "MTF": "DA_KHUNG", "NEWS_FADE": "VI_MO", "ML_LOGIT": "ML"}
THOAT2 = ["TR2", "GIO6", "TP"]
DU = "/workspace/du_lieu_fx/"


def _m5_h1(f, sp):
    d = pd.read_csv(DU + f, parse_dates=["time"]).set_index("time")
    h = d.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    h["spread_open"] = sp; h["so_tick"] = 1; return h


def bo2():
    B = {}
    B["eurusd18"] = (_m5_h1("eurusd_cu_m5_histdata_server.csv", 1.4e-4), "eurusd")
    n = pd.read_csv(DU + "nzdusd_h1_duka_ba_2018_2023.csv", parse_dates=["time"]).set_index("time"); n["so_tick"] = 1
    B["nzdusd18_duka"] = (n[["open", "high", "low", "close", "spread_open", "so_tick"]], "nzdusd")
    a = _m5_h1("audcad_m5_histdata_ny7.csv", 2.5e-4); B["audcad08"] = (a[a.index < "2024-01-01"], "audcad")
    for t, bps in (("vang", 2e-4), ("us500", 1e-4), ("uk100", 1.5e-4)):
        d = pd.read_csv(DU + f"{t}_h1_yahoo_ny7.csv", parse_dates=["time"]).set_index("time")
        d["spread_open"] = d["close"] * bps; d["so_tick"] = 1; B[t + "_h1"] = (d, t)
    return B


def tin_moi(d, atr, giua):
    o, h, l, c = (d[k] for k in ("open", "high", "low", "close")); s = {}
    A = pd.Series(atr, index=d.index)
    s["DONCHIAN55"] = np.where(c > h.shift().rolling(55).max(), 1, np.where(c < l.shift().rolling(55).min(), -1, 0))
    m50, m200 = c.rolling(50).mean(), c.rolling(200).mean(); x = np.sign(m50 - m200)
    s["MA50_200"] = np.where((x != x.shift()) & (x != 0), x, 0)
    ma, sd = c.rolling(20).mean(), c.rolling(20).std(ddof=0); kel = 1.5 * A.rolling(20).mean()
    sq = ((ma + 2 * sd) < (ma + kel)) & ((ma - 2 * sd) > (ma - kel))
    s["SQUEEZE"] = np.where(sq.shift().fillna(False) & (c > ma + 2 * sd), 1, np.where(sq.shift().fillna(False) & (c < ma - 2 * sd), -1, 0))
    hh, ll = h.shift().rolling(20).max(), l.shift().rolling(20).min()
    s["SWEEP"] = np.where((h > hh) & (c < hh), -1, np.where((l < ll) & (c > ll), 1, 0))
    s["FVG"] = np.where(l > h.shift(2), 1, np.where(h < l.shift(2), -1, 0))
    ng = d.index.normalize(); hd, ld, cd = h.groupby(ng).max().shift(), l.groupby(ng).min().shift(), c.groupby(ng).last().shift()
    P = (hd + ld + cd) / 3; S1 = (2 * P - hd).reindex(ng).to_numpy(); R1 = (2 * P - ld).reindex(ng).to_numpy()
    s["PIVOT"] = np.where((l <= S1) & (c > S1), 1, np.where((h >= R1) & (c < R1), -1, 0))
    ten = (h.rolling(9).max() + l.rolling(9).min()) / 2; kij = (h.rolling(26).max() + l.rolling(26).min()) / 2
    sa = ((ten + kij) / 2).shift(26); sb = ((h.rolling(52).max() + l.rolling(52).min()) / 2).shift(26)
    top, bot = np.maximum(sa, sb), np.minimum(sa, sb)
    s["ICHIMOKU"] = np.where((c > top) & (c.shift() <= top.shift()), 1, np.where((c < bot) & (c.shift() >= bot.shift()), -1, 0))
    H48, L48 = h.rolling(48).max(), l.rolling(48).min(); up = c > m200
    lv_up = H48 - 0.5 * (H48 - L48); lv_up2 = H48 - 0.618 * (H48 - L48)
    lv_dn = L48 + 0.5 * (H48 - L48); lv_dn2 = L48 + 0.618 * (H48 - L48)
    s["FIB"] = np.where(up & (l <= lv_up) & (l >= lv_up2) & (c > o), 1, np.where(~up & (h >= lv_dn) & (h <= lv_dn2) & (c < o), -1, 0))
    hr = d.index.hour; orh = h.where(hr == 10).groupby(ng).transform("max"); orl = l.where(hr == 10).groupby(ng).transform("min")
    s["OPENING_RANGE"] = np.where((hr > 10) & (c > orh) & (c.shift() <= orh), 1, np.where((hr > 10) & (c < orl) & (c.shift() >= orl), -1, 0))
    gap = o - c.shift(); thu2 = (d.index.dayofweek == 0) & (pd.Series(d.index, index=d.index).diff() > pd.Timedelta(hours=24))
    s["GAP_FILL"] = np.where(thu2 & (gap > 0.3 * A.shift()), -1, np.where(thu2 & (gap < -0.3 * A.shift()), 1, 0))
    x, _, _, _ = F.chi_bao(d); r = x["RSI"]
    s["MTF"] = np.where((r == 1) & up, 1, np.where((r == -1) & ~up, -1, 0))
    ev = set(LS.nfp(2008, 2026)) | set(LS.cpi())
    nb = np.array([t.date() in ev for t in d.index]) & (hr == 15)
    s["NEWS_FADE"] = np.where(nb, -np.sign(c - o), 0)
    # ML: logistic tren nua phat hien
    R = c.pct_change(); X = pd.concat([R.shift(k) for k in range(5)] + [(pd.Series(np.nan_to_num(r.astype(float)), index=d.index))], axis=1).fillna(0).to_numpy()
    y = (c.shift(-6) > c).astype(float).to_numpy(); tr = np.asarray(d.index < giua) & np.isfinite(y)
    mu, sg = X[tr].mean(0), X[tr].std(0) + 1e-12; Z = (X - mu) / sg; w = np.zeros(Z.shape[1]); b = 0.0
    for _ in range(300):
        p = 1 / (1 + np.exp(-(Z[tr] @ w + b))); g = p - y[tr]; w -= 0.1 * Z[tr].T @ g / tr.sum(); b -= 0.1 * g.mean()
    p = 1 / (1 + np.exp(-(Z @ w + b))); s["ML_LOGIT"] = np.where(p > 0.55, 1, np.where(p < 0.45, -1, 0))
    return {k: np.nan_to_num(np.asarray(v, float)) for k, v in s.items()}


def lam(d, ten, cap, cu=False):
    giua = d.index[len(d) // 2]; s_cu, atr, _ = v19.tin_hieu(d); s = tin_moi(d, atr, giua)
    if cu: s.update(s_cu)
    out = []
    for v, tin in s.items():
        for th in THOAT2:
            r = {"bo": ten, "cap": cap, "vao": v, "nhom": NHOM2.get(v) or v19.VAO_NHOM[v], "thoat": th}
            q = v19.tk(v19.chay(d, tin, th, atr), giua)
            if q:
                r.update(q); q2 = v19.tk(v19.chay(d, tin, th, atr, 1.5), giua); r["kiem_x1_5_pct"] = q2["kiem_pct"] if q2 else None
            out.append(r)
    return out


def main(ra=None):
    o = []
    for cap in F.CAP:
        o += lam(F.tai(cap), "bo1_2024", cap); print(cap, flush=True)
    for ten, (d, cap) in bo2().items():
        o += lam(d, ten, cap, cu=True); print(ten, len(d), flush=True)
    J = json.load(open("reports/vong19.json")); cu = v19.ho_cu() + [r["p"] for r in J["o"] + J["ghep"] if "p" in r]
    assert len(cu) == J["ho_holm"]
    v = [r for r in o if "p" in r]; H = MV.holm(cu + [r["p"] for r in v])
    for r, q in zip(v, H[len(cu):]):
        r["p_holm"] = q; r["song"] = q < 0.05 and r["ph_pct"] > 0 and r["kiem_pct"] > 0 and (r.get("kiem_x1_5_pct") or -1) > 0 and r["maxdd_pct"] < 80
    print("ho", len(H), "o", len(o), "du lenh", len(v), "song", sum(r["song"] for r in v))
    for r in sorted(v, key=lambda r: r["p"])[:10]:
        print(r["bo"], r["cap"], r["vao"], r["thoat"], "n", r["n_ph"], r["n_kiem"], "ph %.1f kiem %.1f x1.5 %s p %.4f holm %.3f DD %.1f" % (r["ph_pct"], r["kiem_pct"], r.get("kiem_x1_5_pct"), r["p"], r["p_holm"], r["maxdd_pct"]))
    # bang nhom (bo1 2024 + bo2) va do ben
    bang = {}
    for g in sorted({r["nhom"] for r in v}):
        row = {}
        for bo, f in (("bo1", lambda r: r["bo"] == "bo1_2024"), ("bo2", lambda r: r["bo"] != "bo1_2024")):
            xs = [r for r in v if r["nhom"] == g and f(r)]
            if xs:
                row[bo] = {"so": len(xs), "ty_le_lai_kiem_pct": round(100 * np.mean([r["kiem_pct"] > 0 for r in xs]), 1), "tv_kiem": round(float(np.median([r["kiem_pct"] for r in xs])), 2),
                           "p_tot": round(min(r["p"] for r in xs), 4), "nhay_phi": round(float(np.median([r["kiem_x1_5_pct"] - r["kiem_pct"] for r in xs if r.get("kiem_x1_5_pct") is not None])), 2)}
        bang[g] = row; print("NHOM", g, row)
    from scipy.stats import spearmanr
    k1 = {}; k2 = {}
    for r in v:
        key = (r["vao"], r["thoat"]); (k1 if r["bo"] == "bo1_2024" else k2).setdefault(key, []).append(r["kiem_pct"])
    ks = [k for k in k1 if k in k2]
    rho = spearmanr([np.median(k1[k]) for k in ks], [np.median(k2[k]) for k in ks]) if len(ks) > 3 else None
    print("do ben Spearman bo1 vs bo2:", len(ks), rho)
    v11 = json.load(open("reports/vong11_fx_vi_mo.json"))["quy_tac"]
    cs = [{k: x.get(k) for k in ("quy_tac", "p")} for x in v11 if x["quy_tac"] in ("CARRY_AUDJPY", "AUD_NZD_HOI_QUY")]
    print("CARRY/STAT_ARB (vong 11):", cs)
    if ra: json.dump({"nhan": "MO PHONG", "ho_holm": len(H), "o": o, "bang_nhom": bang, "spearman": [len(ks), float(rho.statistic) if rho else None, float(rho.pvalue) if rho else None],
                      "carry_stat_arb_v11": cs}, open(ra, "w"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
