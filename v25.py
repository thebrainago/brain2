# -*- coding: utf-8 -*-
"""Vong 25: mo phong co che bo doc + 4 EA dich tay, pooled M15/H1/H4 (8 chuoi) va D1 (54 tai san). Dang ky: reports/vong25_tien_dang_ky.md. MO PHONG."""
from __future__ import annotations

import hashlib
import json
import sys
from multiprocessing import Pool

import numpy as np
import pandas as pd

import mua_vu as MV
import v23
import v24
from nhan import ngu_phap as NP

NAN = np.nan
KK = "/workspace/v25_kiemke.json"
TACH_NHO = pd.Timestamp("2025-05-15")


def diem_of(ten):
    t = ten.lower()
    if "jpy" in t: return 1e-3
    if "xau" in t or t.startswith("gc_") or "vang" in t: return 0.01
    if t.startswith("si_"): return 1e-3
    if t.endswith("_x") or t.startswith("bo1_"): return 1e-5
    return 0.01


def co_che():
    d = json.load(open(KK)); seen = {}
    for k in d:
        for x in d[k]:
            for s in x["specs"]:
                key = hashlib.md5(json.dumps({a: s.get(a) for a in ("vao", "ra", "chieu", "giu", "sltp", "trong_bar")}, sort_keys=True, default=str).encode()).hexdigest()[:12]
                if key not in seen: seen[key] = {**s, "_ma": key, "_ea": x["file"].split("cau_kho/")[-1], "_bo": k}
    return list(seen.values())


def kiem_ke():
    d = json.load(open(KK)); vt = lambda f: hashlib.md5(open(f, errors="ignore").read().encode()).hexdigest()
    tat = {}; dich = set()
    for k in d:
        for x in d[k]:
            h = vt(x["file"]); tat.setdefault(h, x["file"])
            if x["so_spec"]: dich.add(h)
    return {"ea_duy_nhat": len(tat), "ea_bo_doc_dich_duoc": len(dich), "theo_bo": {k: [len(d[k]), sum(x["so_spec"] > 0 for x in d[k])] for k in d}}


def atr_sma(h, l, c, n):
    pc = np.r_[c[0], c[:-1]]; tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc))); return pd.Series(tr).rolling(n).mean().to_numpy()


def kc(x, h, l, c, diem):
    if x is None: return None
    if isinstance(x, (int, float)): return np.full(len(c), float(x) * diem)
    if isinstance(x, dict) and x.get("chi_bao") == "tuyen_tinh":
        tot = np.zeros(len(c))
        for th, hs in zip(x["toan_hang"], x["he_so"]):
            if th.get("chi_bao") != "atr": return "KHONG"
            tot += hs * (atr_sma(h, l, c, int(th.get("n", 14))) if th.get("kieu") == "sma" else v23.atr(h, l, c, int(th.get("n", 14))))
        return tot
    return "KHONG"


def S_bo_doc(spec, d, diem):
    h, l, c = (d[k].to_numpy() for k in ("high", "low", "close")); n = len(c)
    v = np.nan_to_num(np.asarray(NP.sinh_tu_spec(spec, d), float)); s = np.sign(v)
    sig = np.where((s != 0) & (np.r_[0, s[:-1]] != s), s, 0).astype(int)
    st = spec.get("sltp") or {}
    sl_d = st.get("sl_diem"); tp_d = st.get("tp_diem")
    sld = kc(sl_d if sl_d else st.get("sl_kc"), h, l, c, diem); tpd = kc(tp_d if tp_d else st.get("tp_kc"), h, l, c, diem)
    if isinstance(sld, str) or isinstance(tpd, str): return None
    sl = c - sig * sld if sld is not None else np.full(n, NAN); tp = c + sig * tpd if tpd is not None else np.full(n, NAN)
    S = {"sig": sig, "sl": sl, "tp": tp, "H": int(st.get("het_bar") or 500)}
    if spec.get("ra") or (sld is None and tpd is None): S["ex"] = np.where((s == 0) | (s != np.r_[s[0], s[:-1]]), 2, 0)  # chi dung thong tin den close i
    return S


def rsi_wilder(c, n): return v23.rsi(c, n)


def ea_asq(d, kh, diem):
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close")); n = len(c)
    eF, eS = v23.ema(c, 50), v23.ema(c, 200); A = v23.atr(h, l, c, 50); r = rsi_wilder(c, 14)
    lon = {"M5": "1h", "M15": "1h", "H1": "4h", "H4": "1D", "D1": "W-FRI"}[kh]
    hF = v23.htf_ffill(d, lon, lambda g: v23.ema(g["close"].to_numpy(), 20)); hS = v23.htf_ffill(d, lon, lambda g: v23.ema(g["close"].to_numpy(), 50))
    hh = pd.Series(h).shift(1).rolling(15).max().to_numpy(); ll = pd.Series(l).shift(1).rolling(15).min().to_numpy(); c2 = np.r_[NAN, c[:-1]]
    hr = (d.index - pd.Timedelta(hours=0)).hour.to_numpy(); wd = d.index.dayofweek.to_numpy()
    phien = ((hr >= 8) & (hr < 17) & ~((wd == 4) & (hr >= 14))) if kh != "D1" else np.ones(n, bool)
    sep = np.abs(eF - eS) >= 0.3 * A
    bu = (eF > eS) & sep & (c > eF) & (c > eS) & (c > hh - 0.3 * A) & (c2 <= hh) & (r >= 45) & (r <= 65) & (c > c2) & (hF > hS) & phien
    be = (eF < eS) & sep & (c < eF) & (c < eS) & (c < ll + 0.3 * A) & (c2 >= ll) & (r >= 35) & (r <= 55) & (c < c2) & (hF < hS) & phien
    sig = np.where(bu, 1, np.where(be, -1, 0)); return {"sig": sig, "sl": c - sig * 300 * diem, "tp": c + sig * 450 * diem, "be_r": 0.5, "tr": ("fix", 100 * diem, 200 * diem)}


def ea_rsi_earnforex(d, kh, diem):
    c = d["close"].to_numpy(); r = rsi_wilder(c, 14); rp = np.r_[NAN, r[:-1]]
    up = (r > 20) & (rp <= 20); dn = (r < 80) & (rp >= 80)
    sig = np.where(up, 1, np.where(dn, -1, 0)); ex = np.where(dn, -1, np.where(up, 1, 0))
    return {"sig": sig, "sl": np.full(len(c), NAN), "tp": np.full(len(c), NAN), "ex": ex}


def ea_ma_cross(d, kh, diem):
    c = d["close"].to_numpy(); f, s = v23.sma(c, 12), v23.sma(c, 40); x = (f > s) & (np.r_[NAN, f[:-1]] < np.r_[NAN, s[:-1]])
    sig = x.astype(int); return {"sig": sig, "sl": c - 30 * diem, "tp": c + 70 * diem}


def ea_macd_sample(d, kh, diem):
    c = d["close"].to_numpy(); m = v23.ema(c, 12) - v23.ema(c, 26); sg = v23.ema(m, 9); mp, sp = np.r_[NAN, m[:-1]], np.r_[NAN, sg[:-1]]
    ma = v23.ema(c, 26); map_ = np.r_[NAN, ma[:-1]]
    cu, cd = (m > sg) & (mp < sp), (m < sg) & (mp > sp)
    bu = (m < 0) & cu & (np.abs(m) > 3 * diem) & (ma > map_); be = (m > 0) & cd & (m > 3 * diem) & (ma < map_)
    sig = np.where(bu, 1, np.where(be, -1, 0))
    ex = np.where((m > 0) & cd & (m > 2 * diem), -1, np.where((m < 0) & cu & (np.abs(m) > 2 * diem), 1, 0))
    return {"sig": sig, "sl": np.full(len(c), NAN), "tp": c + sig * 50 * diem, "ex": ex, "tr": ("fix", 30 * diem, 30 * diem)}


TAY = {"TAY_ASQ_SafeScalping": (ea_asq, "breakout+xu_huong"), "TAY_EarnForex_RSI_EA": (ea_rsi_earnforex, "dao_chieu"),
       "TAY_MA_cross_mq4": (ea_ma_cross, "xu_huong"), "TAY_MACD_Sample_mq4": (ea_macd_sample, "dong_luong")}


def bo_du_lieu(kh):
    if kh == "D1": return v24.tai_d1()
    B = {}
    for t in v23.CHUOI_NHO:
        d, _, _ = v23.lay(t, kh); d["so_tick"] = 1; B[t] = d
    return B


def loc(d, ten):
    h, l, c = (d[k].to_numpy() for k in ("high", "low", "close"))
    if ten == "ST": return v23.supertrend(h, l, c, 10, 4.0)[0]
    e = v23.ema(c, 200); return np.sign(c - e)


def chay_mot(args):
    kh, ma, nguon_S, loc_ten = args
    B = bo_du_lieu(kh); tach = pd.Timestamp("2015-04-01") if kh == "D1" else TACH_NHO; kq = {}
    for che, hs, sl in (("truoc", 0, 0), ("sau", 1, 0.5), ("sau_x15_s1", 1.5, 1.0)):
        T = []; ok = 0
        for ten, d in B.items():
            if len(d) < 300: continue
            h, l, c = (d[k].to_numpy() for k in ("high", "low", "close")); A = v23.atr(h, l, c); diem = diem_of(ten)
            try: S = nguon_S(d, kh, diem)
            except Exception as e:                       # noqa: BLE001
                return {"ma": ma, "khung": kh, "loi": f"{type(e).__name__}: {str(e)[:120]}"}
            if S is None: return {"ma": ma, "khung": kh, "loi": "khoang SL/TP khong dien dat"}
            if loc_ten:
                f = loc(d, loc_ten); S = dict(S); S["sig"] = np.where(np.sign(S["sig"]) == f, S["sig"], 0)
                S["tp"] = np.full(len(c), NAN); S["tr"] = ("chand", 22, 3.0); S.pop("be_r", None); S.pop("ex", None); S["H"] = 500
                S["sl"] = c - np.sign(S["sig"]) * 3 * A
            drift = float(np.mean(np.diff(np.log(c[d.index < tach])))) if (d.index < tach).sum() > 50 else 0.0
            L = v23.sim(d, S, d["spread_open"].to_numpy() * hs, A); ok += 1
            T += v24.tra(L, drift, che != "truoc", sl)
        v24.TACH_DONG[0] = tach; q = v24.danh_gia(T, ok) if T else None
        if q: kq[che] = q
        kq["n_lenh_" + che] = len(T)
    print(ma, kh, loc_ten, "xong", flush=True)
    return {"ma": ma, "khung": kh, "loc": loc_ten, **kq}


class _BD:
    def __init__(self, spec): self.spec = spec
    def __call__(self, d, kh, diem): return S_bo_doc(self.spec, d, diem)


def main(ra=None):
    CC = co_che(); kk = kiem_ke(); print("kiem ke", kk, "co che", len(CC))
    jobs = []
    for kh in ("M15", "H1", "H4", "D1"):
        for s in CC: jobs.append((kh, s["_ma"], _BD(s), None))
        for t, (f, _) in TAY.items(): jobs.append((kh, t, f, None))
    with Pool(3, maxtasksperchild=4) as P: R = P.map(chay_mot, jobs, chunksize=1)
    meta = {s["_ma"]: {"ten": s.get("ten"), "ho": s.get("ho"), "ea": s["_ea"], "bo": s["_bo"], "trong_bar": bool(s.get("trong_bar"))} for s in CC}
    meta.update({t: {"ten": t, "ho": nh, "ea": t, "bo": "dich_tay", "trong_bar": False} for t, (_, nh) in TAY.items()})
    for r in R: r.update(meta[r["ma"]])
    # ghep: top 10 theo NUA PHAT HIEN sau phi (H1, D1)
    gj = []
    nguon = {s["_ma"]: _BD(s) for s in CC}; nguon.update({t: f for t, (f, _) in TAY.items()})
    for kh in ("H1", "D1"):
        xs = sorted([r for r in R if r["khung"] == kh and "sau" in r], key=lambda r: -r["sau"]["tb_ph_bps"])[:10]
        for r in xs:
            for lt in ("ST", "EMA200"): gj.append((kh, r["ma"], nguon[r["ma"]], lt))
    with Pool(3, maxtasksperchild=4) as P: G = P.map(chay_mot, gj, chunksize=1)
    for r in G: r.update(meta[r["ma"]]); r["ghep"] = True
    tat = R + G; v = [r for r in tat if "sau" in r]
    cu = v23.v22_ho() + [x["p"] for x in json.load(open("reports/vong23.json"))["o"] if "p" in x] + \
        [x["sau"]["p"] for x in json.load(open("reports/vong24.json"))["he"] if "sau" in x]
    assert len(cu) == json.load(open("reports/vong24.json"))["ho_holm"], len(cu)
    H = MV.holm(cu + [r["sau"]["p"] for r in v])
    for r, h in zip(v, H[len(cu):]):
        s = r["sau"]; x = r.get("sau_x15_s1")
        r["p_holm"] = h; r["song"] = bool(h < 0.05 and s["p_boot"] < 0.05 and s["tb_ph_bps"] > 0 and s["tb_kiem_bps"] > 0 and x and x["tb_kiem_bps"] > 0 and s["maxdd_pct"] < 80)
    print("ho", len(H), "o", len(tat), "do duoc", len(v), "song", sum(r["song"] for r in v))
    if ra: json.dump({"nhan": "MO PHONG", "kiem_ke": kk, "ho_holm": len(H), "o": tat}, open(ra, "w"), ensure_ascii=False, indent=0, default=float)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
