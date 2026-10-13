# -*- coding: utf-8 -*-
"""Vong 28 (MO PHONG), chu ky 4 vong lap: hang P1 viec 1-4 (+7 ap luc). MRZ z50 +-2 D1 vao 02h (proxy spread 02h).
P1-1 pool AUDUSD+NZDUSD+AUDCAD+GBPUSD; P1-2 loc che do ADX<20 hoac ATR% thap; P1-3 thoat TR1.5/TR2.5/GIO5; P1-4 loc xu huong W1 EMA20.
Dang ky: reports/vong28_tien_dang_ky.md. Holm cong don tu 12949."""
from __future__ import annotations
import json, os, sys, time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
import v22, v23, v24, v26, v27

POOL4 = ["AUDUSD_X", "NZDUSD_X", "AUDCAD_X", "GBPUSD_X"]
GIO = 2


def chay(d, sig, atr, sp, k_tr=2.0, giu_max=72, trail=True):
    """Tong quat hoa v22.chay(TR2): trailing k_tr*ATR (trail=False -> chi dung ban dau), giu toi da giu_max nen.
    k_tr=2, giu_max=72, trail=True trung khop v22.chay(..., 'TR2', ...) (co test)."""
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close"))
    ngay = d.index.normalize().asi8 // 86_400_000_000_000; n = len(c); out = []; i = 60
    while i < n - 2:
        s = sig[i]; a = atr[i]
        if s == 0 or not np.isfinite(a) or a <= 0: i += 1; continue
        j = i + 1; E = o[j] + sp[j] if s > 0 else o[j]
        st = E - 1.5 * a if s > 0 else E + 1.5 * a
        best = c[j]; k = j; X = None
        while k < n - 1:
            if s > 0:
                if l[k] <= st: X = st; break
            else:
                if h[k] + sp[k] >= st: X = st; break
            best = max(best, c[k]) if s > 0 else min(best, c[k])
            if trail: st = max(st, best - k_tr * atr[k]) if s > 0 else min(st, best + k_tr * atr[k])
            if k - j + 1 >= giu_max: X = o[k + 1] if s > 0 else o[k + 1] + sp[k + 1]; k += 1; break
            k += 1
        if X is None: break
        r = (X - E) / E if s > 0 else (E - X) / E
        out.append((d.index[j], r, s, k - j + 1, E, int(ngay[k] - ngay[j]))); i = max(k, i + 1)
    return out


THOAT = {"TR2": dict(k_tr=2.0), "TR1.5": dict(k_tr=1.5), "TR2.5": dict(k_tr=2.5), "GIO5": dict(trail=False, giu_max=5)}


def adx(d, n=14):
    h, l, c = d["high"], d["low"], d["close"]
    up, dn = h.diff(), -l.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=d.index)
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=d.index)
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    w = lambda x: x.ewm(alpha=1 / n, adjust=False).mean()
    at = w(tr); pdi = 100 * w(pdm) / at; mdi = 100 * w(mdm) / at
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    return w(dx.fillna(0))


def xu_huong_w1(d, n=20):
    """+1/-1: close W1 tuan da dong gan nhat (nhan W-FRI <= ngay) so EMA20 W1. Tuan dang do (nhan > ngay) khong dung."""
    w = d["close"].resample("W-FRI").last().dropna(); e = w.ewm(span=n, adjust=False).mean()
    t = pd.Series(np.sign((w - e).to_numpy()), index=w.index)
    # bo tuan cuoi neu chua dong (nhan > ngay cuoi du lieu)
    t = t[t.index <= d.index[-1]]
    return t.reindex(d.index, method="ffill").fillna(0).to_numpy()


def loc(d, sig, kieu):
    sig = np.asarray(sig).copy()
    if kieu == "CHE_DO":
        c = d["close"]; a = pd.Series(v23.atr(d["high"].to_numpy(), d["low"].to_numpy(), c.to_numpy()), index=d.index) / c
        ok = (adx(d) < 20).to_numpy() | (a < a.rolling(250).median().shift()).to_numpy()
        sig[~ok] = 0
    elif kieu == "W1_EMA20":
        sig[sig != xu_huong_w1(d)] = 0
    return sig


def chay_o(o):
    B, kieu, thoat, tach = o["B"], o["loc"], o["thoat"], o["tach"]
    v24.TACH_DONG[0] = tach; v24.RNG = np.random.default_rng(2800 + o["so"]); kq = {"phi": {}}
    for che, hs, sl in (("truoc", 0, 0), ("sau", 1, 0.5), ("sau_x15_s1", 1.5, 1.0)):
        if che != "truoc":
            t = kq.get("truoc")
            if not t or t["tb_ph_bps"] <= 0 or t["tb_kiem_bps"] <= 0: kq["dung_tang"] = 1; break
        T = []; theo = {}
        for ten, d in B.items():
            s, atr, _ = v27.tin_hieu(d); c = d["close"].to_numpy()
            drift = float(np.mean(np.diff(np.log(c[d.index < tach])))) if (d.index < tach).sum() > 50 else 0.0
            pb, kq["phi"][ten] = v27.phi_bar(ten, d, GIO)
            L = v24.tra(chay(d, loc(d, s["MRZ"].astype(int), kieu), atr, c * pb * hs, **THOAT[thoat]), drift, che != "truoc", sl)
            T += L; theo[ten] = L
        q = v24.danh_gia(T, len(B)) if T else None
        if q:
            if len(B) > 1:
                q["theo_tai_san_bps_ph_kiem_n"] = {t: [round(float(np.mean([x[1] for x in L if x[0] < tach] or [np.nan])) * 1e4, 1),
                                                     round(float(np.mean([x[1] for x in L if x[0] >= tach] or [np.nan])) * 1e4, 1), len(L)] for t, L in theo.items()}
            kq[che] = q
        else: kq["dung_tang"] = 0; break
    return {k: v for k, v in o.items() if k != "B"} | kq


def o_list(D1=None):
    D1 = D1 or v24.tai_d1(); P4 = {t: D1[t] for t in POOL4}; F7 = {t: D1[t] for t in v26.FX7}; T = v26.TACH_A; O = []
    O.append({"viec": "P1-1", "nhom": "POOL4", "loc": "KHONG", "thoat": "TR2", "B": P4})
    for t in ("AUDUSD_X", "GBPUSD_X"): O.append({"viec": "P1-2", "nhom": t, "loc": "CHE_DO", "thoat": "TR2", "B": {t: D1[t]}})
    for t in ("AUDUSD_X", "GBPUSD_X"):
        for th in ("TR1.5", "TR2.5", "GIO5"): O.append({"viec": "P1-3", "nhom": t, "loc": "KHONG", "thoat": th, "B": {t: D1[t]}})
    O.append({"viec": "P1-4", "nhom": "POOL4", "loc": "W1_EMA20", "thoat": "TR2", "B": P4})
    O.append({"viec": "P1-4", "nhom": "FX7", "loc": "W1_EMA20", "thoat": "TR2", "B": F7})
    for i, o in enumerate(O): o["so"] = i + 1; o["tach"] = T
    tham_chieu = [{"viec": "tham_chieu_v26", "nhom": t, "loc": "KHONG", "thoat": "TR2", "B": {t: D1[t]}, "tach": T, "so": 100 + i} for i, t in enumerate(("AUDUSD_X", "GBPUSD_X"))]
    return O, tham_chieu


SO_O_DANG_KY = 11


def holm_cu():
    cu = v27.holm_cu() + [x["sau"]["p"] if "sau" in x else 1.0 for x in json.load(open("reports/vong27.json"))["o"]]
    assert len(cu) == json.load(open("reports/vong27.json"))["ho_holm"] == 12949, len(cu)
    return cu


def main(song_song=True):
    t0 = time.time(); O, TC = o_list(); t1 = time.time()
    assert len(O) == SO_O_DANG_KY
    if song_song:
        with ProcessPoolExecutor(min(8, os.cpu_count() or 1)) as ex: R = list(ex.map(chay_o, O + TC))
    else: R = [chay_o(o) for o in O + TC]
    return R[:len(O)], R[len(O):], {"nap_giay": round(t1 - t0, 2), "chay_giay": round(time.time() - t1, 2), "so_o": len(O) + len(TC)}


def _tom(r):
    return {k: (round(r[k]["tb_ph_bps"], 1), round(r[k]["tb_kiem_bps"], 1), r[k]["n_ph"], r[k]["n_kiem"], round(r[k]["p"], 4), round(r[k]["p_boot"], 4), round(r[k]["maxdd_pct"], 1)) for k in ("truoc", "sau", "sau_x15_s1") if k in r}


if __name__ == "__main__":
    R, TC, tg = main("--tuan-tu" not in sys.argv); cu = holm_cu(); n = v26.cham(R, cu)
    for r in R + TC: print(r["so"], r["viec"], r["nhom"], r["loc"], r["thoat"], _tom(r), "dung_tang", r.get("dung_tang"), "holm", round(r.get("p_holm", float("nan")), 3), r.get("song"))
    print("ho", len(cu), "->", n, "song", sum(r["song"] for r in R), tg)
    json.dump({"nhan": "MO PHONG", "ho_holm_truoc": len(cu), "ho_holm": n, "so_song": int(sum(r["song"] for r in R)), "toc_do": tg, "o": R,
               "tham_chieu_khong_dem_holm": TC}, open("reports/vong28.json", "w"), ensure_ascii=False, indent=0, default=str)
