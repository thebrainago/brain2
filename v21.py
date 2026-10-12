# -*- coding: utf-8 -*-
"""Vong 21: luan diem 'gia luon gap lai EMA' + luoi EMA/ATR/do doc. Dang ky truoc reports/vong21_tien_dang_ky.md. MO PHONG."""
from __future__ import annotations

import itertools as it
import json
import math
import sys

import numpy as np
import pandas as pd

import mua_vu as MV
import v17_fx as F
import v19
import v19b

EMA = [20, 50, 100, 200]; K = [1.5, 2.0, 3.0, 4.0]; MODE = ["MR", "PB"]; LOC = ["KHONG", "ATR_THAP", "ATR_CAO"]; THEM = ["KHONG", "RSI", "BB"]
RNG = np.random.default_rng(21)
DN = "/workspace/du_lieu_ngay/"


def d1(f, bps, tu, qd_mua):
    d = pd.read_csv(DN + f, index_col=0, parse_dates=True)[["open", "high", "low", "close"]].dropna()
    d = d[(d.index >= tu) & (d["high"] > d["low"])]; d["spread_open"] = d["close"] * bps; d["so_tick"] = 1; d.attrs["qd_mua"] = qd_mua; return d


def bo_du_lieu():
    B = {f"bo1_{c}": (F.tai(c), "H1") for c in F.CAP}
    for t, (d, c) in v19b.bo2().items(): B[f"bo2_{t}"] = (d, "H1")
    B["d1_eurusd"] = (d1("eurusd=x_dai_yahoo.csv", 1.4e-4, "2004-01-01", False), "D1")
    B["d1_usdjpy"] = (d1("jpy=x_dai_yahoo.csv", 1.5e-4, "2004-01-01", False), "D1")
    B["d1_audusd"] = (d1("audusd=x_dai_yahoo.csv", 2.6e-4, "2006-06-01", False), "D1")
    B["d1_gbpusd"] = (d1("gbpusd_ohlc_yahoo.csv", 1.6e-4, "2004-01-01", False), "D1")
    B["d1_spx"] = (d1("gspc_dai_yahoo.csv", 1e-4, "1990-01-01", True), "D1")
    B["d1_vang"] = (d1("gcf_ohlc_yahoo.csv", 2e-4, "2001-01-01", True), "D1")
    return B


def atr_of(d):
    h, l, c = d["high"], d["low"], d["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / 14, adjust=False).mean().to_numpy()


def cham_lai(h, l, c, ema, atr, k, N):
    dist = (c - ema) / atr; xa = np.abs(dist) >= k; ev = np.where(xa & ~np.r_[False, xa[:-1]])[0]
    ok = []; tg = []
    for i in ev:
        j = np.where((l[i + 1:i + 1 + N] <= ema[i + 1:i + 1 + N]) & (h[i + 1:i + 1 + N] >= ema[i + 1:i + 1 + N]))[0]
        if i + N >= len(c): continue
        ok.append(len(j) > 0); tg.append(j[0] + 1 if len(j) else np.nan)
    return (float(np.mean(ok)) if ok else np.nan, float(np.nanmedian(tg)) if ok and np.isfinite(tg).any() else np.nan, len(ok))


def luan_diem(B):
    out = []
    for ten, (d, kh) in B.items():
        if ten.startswith("bo1_") and ten not in ("bo1_eurusd", "bo1_usdjpy", "bo1_audusd"): continue
        N = 48 if kh == "H1" else 20
        c0 = d["close"].to_numpy(); r = np.diff(np.log(c0)); hl = (d["high"] - d["low"]).to_numpy() / c0
        for n in EMA:
            for k in K:
                def tinh(c):
                    s = pd.Series(c); ema = s.ewm(span=n, adjust=False).mean().to_numpy()
                    h = c * (1 + hl / 2); l = c * (1 - hl / 2)
                    tr = np.maximum(h - l, np.maximum(np.abs(h - np.r_[c[0], c[:-1]]), np.abs(l - np.r_[c[0], c[:-1]])))
                    atr = pd.Series(tr).ewm(alpha=1 / 14, adjust=False).mean().to_numpy()
                    return cham_lai(h, l, c, ema, atr, k, N)
                thuc = tinh(c0)
                tr_ = [tinh(np.exp(np.r_[np.log(c0[0]), np.log(c0[0]) + np.cumsum(RNG.permutation(r))])) for _ in range(40)]
                m = np.array([x[0] for x in tr_]); z = (thuc[0] - np.nanmean(m)) / (np.nanstd(m) + 1e-12)
                out.append({"chuoi": ten, "ema": n, "k": k, "ty_le_cham": thuc[0], "tg_tv": thuc[1], "n_su_kien": thuc[2],
                            "ty_le_cham_tron": float(np.nanmean(m)), "z": float(z)})
    return out


def chay(d, ema, atr, sig, mode, k, hs=1.0, H=48):
    o, h, l, c = (d[x].to_numpy() for x in ("open", "high", "low", "close")); sp = d["spread_open"].to_numpy() * v19.XM * hs
    hr = d.index.hour.to_numpy(); ngay = np.r_[0, np.diff(d.index.normalize().asi8) > 0].astype(bool)
    qd = 0.025 / 365; n = len(c); out = []; i = 210
    while i < n - 2:
        s = sig[i]
        if s == 0: i += 1; continue
        j = i + 1; a = atr[i]; E = o[j] + sp[j] if s > 0 else o[j]
        sl = E - (k if mode == "MR" else 1.5) * a if s > 0 else E + (k if mode == "MR" else 1.5) * a
        X = None; kk = j
        while kk < n - 1:
            tp = ema[kk - 1] if mode == "MR" else (E + k * a if s > 0 else E - k * a)
            if s > 0:
                if l[kk] <= sl: X = sl; break
                if h[kk] >= tp and kk > j: X = max(tp, o[kk]) if mode == "MR" else tp; break
            else:
                if h[kk] + sp[kk] >= sl: X = sl; break
                if l[kk] + sp[kk] <= tp and kk > j: X = min(tp, o[kk] + sp[kk]) if mode == "MR" else tp; break
            if kk - j + 1 >= H: X = o[kk + 1] if s > 0 else o[kk + 1] + sp[kk + 1]; kk += 1; break
            kk += 1
        if X is None: break
        r = (X - E) / E * (1 if s > 0 else -1)
        dem = int(np.sum(ngay[j + 1:kk + 1])) if len(ngay) else 0
        if hr.max() > 0: dem = int(np.sum(np.diff(hr[j:kk + 1]) < 0))
        out.append((d.index[j], r - dem * qd, s, kk - j + 1)); i = max(kk, i + 1)
    return out


def tin(d, ema, atr, mode, k, loc, them, rsi, bbu, bbl, atrp):
    c = d["close"].to_numpy(); s = (ema - np.r_[np.full(10, np.nan), ema[:-10]]) / atr; dist = (c - ema) / atr
    if mode == "MR":
        sig = np.where((np.abs(s) < 0.5) & (dist >= k), -1, np.where((np.abs(s) < 0.5) & (dist <= -k), 1, 0))
        if them == "RSI": sig = np.where(((sig == 1) & (rsi < 30)) | ((sig == -1) & (rsi > 70)), sig, 0)
        if them == "BB": sig = np.where(((sig == 1) & (c < bbl)) | ((sig == -1) & (c > bbu)), sig, 0)
    else:
        xa_len = pd.Series(dist >= k).rolling(24, min_periods=1).max().shift().fillna(0).to_numpy() > 0
        xa_xuong = pd.Series(dist <= -k).rolling(24, min_periods=1).max().shift().fillna(0).to_numpy() > 0
        gan = np.abs(dist) <= 0.25
        sig = np.where((s >= 0.5) & xa_len & gan, 1, np.where((s <= -0.5) & xa_xuong & gan, -1, 0))
        if them == "RSI": sig = np.where(((sig == 1) & (rsi > 50)) | ((sig == -1) & (rsi < 50)), sig, 0)
        if them == "BB": sig = np.where((c < bbu) & (c > bbl), sig, 0)
    if loc == "ATR_THAP": sig = np.where(atrp < 0.5, sig, 0)
    if loc == "ATR_CAO": sig = np.where(atrp > 0.5, sig, 0)
    return np.nan_to_num(sig).astype(int)


def tk(L, giua, drift):
    tru = lambda t, r, s, nb: r - s * drift * nb
    a = np.array([tru(*x) for x in L if x[0] < giua]); b = np.array([tru(*x) for x in L if x[0] >= giua])
    if len(a) < 15 or len(b) < 15 or b.std(ddof=1) == 0: return None
    eq = np.cumprod(1 + np.array([x[1] for x in L]))
    return {"n_ph": len(a), "n_kiem": len(b), "ph_pct": float(a.sum() * 100), "kiem_pct": float(b.sum() * 100),
            "p": MV.p1(b.mean() / b.std(ddof=1) * math.sqrt(len(b))), "maxdd_pct": float(np.max(1 - eq / np.maximum.accumulate(eq)) * 100)}


def main(ra=None):
    B = bo_du_lieu(); kq = {"luan_diem": luan_diem(B)}
    print("LUAN DIEM (ty le cham thuc vs tron, z):")
    for x in kq["luan_diem"]:
        if x["k"] in (2.0, 4.0): print(" ", x["chuoi"], x["ema"], x["k"], "%.2f vs %.2f z %.1f tg %.0f n %d" % (x["ty_le_cham"], x["ty_le_cham_tron"], x["z"], x["tg_tv"], x["n_su_kien"]))
    o = []
    for ten, (d, kh) in B.items():
        c = d["close"]; atr = atr_of(d); giua = d.index[len(d) // 2]
        drift = float(np.mean(np.diff(np.log(c.to_numpy()))[: len(c) // 2]))
        dl = c.diff(); up = dl.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean(); dn = (-dl.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
        rsi = (100 - 100 / (1 + up / dn)).to_numpy(); m20 = c.rolling(20).mean(); sd = c.rolling(20).std(ddof=0)
        bbu, bbl = (m20 + 2 * sd).to_numpy(), (m20 - 2 * sd).to_numpy()
        A = pd.Series(atr); atrp = A.rolling(500, min_periods=100).rank(pct=True).shift().to_numpy()
        for n in EMA:
            ema = c.ewm(span=n, adjust=False).mean().to_numpy()
            for mode, k, loc, them in it.product(MODE, K, LOC, THEM):
                sig = tin(d, ema, atr, mode, k, loc, them, rsi, bbu, bbl, atrp)
                H = 48 if kh == "H1" else 20
                r = {"chuoi": ten, "ema": n, "che_do": mode, "k": k, "loc": loc, "them": them}
                q = tk(chay(d, ema, atr, sig, mode, k, 1.0, H), giua, drift)
                if q:
                    r.update(q); q2 = tk(chay(d, ema, atr, sig, mode, k, 1.5, H), giua, drift); r["kiem_x1_5_pct"] = q2["kiem_pct"] if q2 else None
                o.append(r)
        print(ten, "xong", flush=True)
    v = [r for r in o if "p" in r]
    cu = v19.ho_cu(); J = json.load(open("reports/vong19.json")); Jb = json.load(open("reports/vong19b.json")); J20 = json.load(open("reports/vong20.json"))
    cu += [r["p"] for r in J["o"] + J["ghep"] if "p" in r] + [r["p"] for r in Jb["o"] if "p" in r] + [r["p"] for r in J20["o"] if "p" in r]
    assert len(cu) == J20["ho_holm"]
    H = MV.holm(cu + [r["p"] for r in v])
    for r, h in zip(v, H[len(cu):]):
        r["p_holm"] = h; r["song"] = h < 0.05 and r["ph_pct"] > 0 and r["kiem_pct"] > 0 and (r.get("kiem_x1_5_pct") or -1) > 0 and r["maxdd_pct"] < 80
    print("ho", len(H), "o", len(o), "du lenh", len(v), "song", sum(r["song"] for r in v),
          "lai ca 2 nua", sum(r["ph_pct"] > 0 and r["kiem_pct"] > 0 for r in v), "trung vi kiem %.2f" % np.median([r["kiem_pct"] for r in v]))
    idx = {(r["chuoi"], r["ema"], r["che_do"], r["k"], r["loc"], r["them"]): r for r in v}
    nh = []
    for r in sorted(v, key=lambda r: r["p"])[:10]:
        ei, ki = EMA.index(r["ema"]), K.index(r["k"]); lc = []
        for de, dk in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if 0 <= ei + de < 4 and 0 <= ki + dk < 4:
                x = idx.get((r["chuoi"], EMA[ei + de], r["che_do"], K[ki + dk], r["loc"], r["them"]))
                if x: lc.append(x["kiem_pct"] > 0)
        r["lan_can_duong_pct"] = round(100 * np.mean(lc), 0) if lc else None; nh.append(r)
        print(r["chuoi"], r["ema"], r["che_do"], r["k"], r["loc"], r["them"], "n", r["n_ph"], r["n_kiem"], "ph %.1f kiem %.1f x1.5 %s p %.4f holm %.3f DD %.1f lan can+ %s%%" % (
            r["ph_pct"], r["kiem_pct"], r.get("kiem_x1_5_pct") and round(r["kiem_x1_5_pct"], 1), r["p"], r["p_holm"], r["maxdd_pct"], r["lan_can_duong_pct"]))
    bd = {}
    for mode in MODE:
        for n in EMA:
            bd[f"{mode}|{n}"] = [round(float(np.median([r["kiem_pct"] for r in v if r["che_do"] == mode and r["ema"] == n and r["k"] == k] or [np.nan])), 2) for k in K]
            print("BAN DO", mode, n, dict(zip(K, bd[f"{mode}|{n}"])), "ty le kiem>0 %.0f%%" % (100 * np.mean([r["kiem_pct"] > 0 for r in v if r["che_do"] == mode and r["ema"] == n])))
    for g in ("bo1", "bo2", "d1"):
        xs = [r for r in v if r["chuoi"].startswith(g)]
        print("BO", g, "o", len(xs), "ty le kiem>0 %.0f%%" % (100 * np.mean([r["kiem_pct"] > 0 for r in xs])), "tv %.2f" % np.median([r["kiem_pct"] for r in xs]))
    kq.update(ho_holm=len(H), o=o, ban_do=bd)
    if ra: json.dump(kq, open(ra, "w"), ensure_ascii=False, default=float)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
