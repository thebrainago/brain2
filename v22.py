# -*- coding: utf-8 -*-
"""Vong 22: nhom chien luoc v19 + EMA v21 tren M5..W1, truoc/sau phi. Dang ky: reports/vong22_tien_dang_ky.md. MO PHONG."""
from __future__ import annotations

import json
import math
import sys
from multiprocessing import Pool

import numpy as np
import pandas as pd

import mua_vu as MV
import v17_fx as F
import v19
import v19b
import v21

DU = "/workspace/du_lieu_fx/"
KHUNG = ["M5", "M15", "M30", "H1", "H4"]
QUY = {"M5": "5min", "M15": "15min", "M30": "30min", "H1": "1h", "H4": "4h", "D1": "1D", "W1": "W-FRI"}
LON = {"M5": "M30", "M15": "H1", "M30": "H4", "H1": "H4", "H4": "D1", "D1": "W1"}
TIN = {"ROC24": "DONG_LUONG", "MACD0": "DONG_LUONG", "DINH20": "BREAKOUT", "RSI": "DAO_CHIEU", "MRZ": "MR",
       "DONCHIAN55": "XU_HUONG_DAI", "MA50_200": "XU_HUONG_DAI", "MTF": "DA_KHUNG", "GAP_FILL": "GAP", "NEWS_FADE": "NEWS_FADE",
       "SWEEP": "SMC", "FVG": "SMC", "ENGULF": "NEN", "PINBAR": "NEN", "PHIEN_A": "PHIEN", "OPENING_RANGE": "PHIEN"}
EMAO = [("MR", 20, 2.0, False), ("MR", 50, 3.0, False), ("PB", 20, 2.0, False), ("PB", 50, 2.0, False), ("MR", 20, 2.0, True), ("PB", 50, 2.0, True)]
THOAT = ["TP", "TR2"]
QD = 0.025 / 365


def pip_of(ten):
    if "jpy" in ten: return 0.01
    if "xau" in ten or "vang" in ten: return 0.1
    if "us500" in ten or "uk100" in ten or "spx" in ten: return 1.0
    return 1e-4


def gop(d, kh):
    if kh == "M5": return d
    g = d.resample(QUY[kh], label="left", closed="left").agg({"open": "first", "high": "max", "low": "min", "close": "last", "spread_open": "first"})
    return g.dropna(subset=["open"])


def m5(f, sp=None, sp_h1=None, col="spread_tb", tu=None, den=None, bps=None):
    d = pd.read_csv(DU + f, parse_dates=["time"]).set_index("time")[["open", "high", "low", "close"]]
    if tu: d = d[d.index >= tu]
    if den: d = d[d.index < den]
    if sp_h1:
        s = pd.read_csv(DU + sp_h1, parse_dates=["time"]).set_index("time")[col]
        d["spread_open"] = s.reindex(d.index.floor("h")).ffill().bfill().to_numpy()
    elif bps: d["spread_open"] = d["close"] * bps
    else: d["spread_open"] = sp
    return d


def nguon(ten):
    """Tra ve (df goc, loai_spread, co_drift)."""
    if ten.startswith("bo1_"):
        c = ten[4:]; return m5(f"{c}_m5_histdata_ny7.csv", sp_h1=f"{c}_h1_tick_ba_ny7.csv"), "that", False
    if ten == "bo2_eurusd18": return m5("eurusd_cu_m5_histdata_server.csv", sp=1.4e-4), "co_dinh", False
    if ten == "bo2_nzdusd18": return m5("nzdusd_m5_histdata_2018_2023_ny7.csv", sp_h1="nzdusd_h1_duka_ba_2018_2023.csv", col="spread_open"), "that", False
    if ten == "bo2_audcad08": return m5("audcad_m5_histdata_ny7.csv", sp=2.5e-4, den="2024-01-01"), "co_dinh", False
    if ten == "bo2_xauusd24": return m5("xauusd_m5_histdata_ny7.csv", bps=2e-4), "co_dinh", True
    if ten in ("us500_h1", "uk100_h1"):
        d = pd.read_csv(DU + f"{ten.split('_')[0]}_h1_yahoo_ny7.csv", parse_dates=["time"]).set_index("time")[["open", "high", "low", "close"]]
        d["spread_open"] = d["close"] * (1e-4 if "us500" in ten else 1.5e-4); return d, "co_dinh", True
    B = {"d1_eurusd": ("eurusd=x_dai_yahoo.csv", 1.4e-4, "2004-01-01"), "d1_usdjpy": ("jpy=x_dai_yahoo.csv", 1.5e-4, "2004-01-01"),
         "d1_audusd": ("audusd=x_dai_yahoo.csv", 2.6e-4, "2006-06-01"), "d1_gbpusd": ("gbpusd_ohlc_yahoo.csv", 1.6e-4, "2004-01-01"),
         "d1_spx": ("gspc_dai_yahoo.csv", 1e-4, "1990-01-01"), "d1_vang": ("gcf_ohlc_yahoo.csv", 2e-4, "2001-01-01")}
    f, bps, tu = B[ten]; d = v21.d1(f, bps, tu, False)[["open", "high", "low", "close", "spread_open"]]
    return d, "co_dinh", ten in ("d1_spx", "d1_vang")


def chay(d, sig, thoat, atr, sp):
    """Nhu v19.chay (TP / TR2) nhung swap theo so ngay lich giu lenh, tra ve (t, r, huong, so_nen, E, ngay)."""
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close"))
    ngay = d.index.normalize().asi8 // 86_400_000_000_000; n = len(c); out = []; i = 60
    while i < n - 2:
        s = sig[i]; a = atr[i]
        if s == 0 or not np.isfinite(a) or a <= 0: i += 1; continue
        j = i + 1; E = o[j] + sp[j] if s > 0 else o[j]
        st = E - 1.5 * a if s > 0 else E + 1.5 * a; tp = (E + a if s > 0 else E - a) if thoat == "TP" else None
        best = c[j]; k = j; X = None
        while k < n - 1:
            if s > 0:
                if l[k] <= st: X = st; break
                if tp is not None and h[k] >= tp and k > j: X = tp; break
            else:
                if h[k] + sp[k] >= st: X = st; break
                if tp is not None and l[k] + sp[k] <= tp and k > j: X = tp; break
            best = max(best, c[k]) if s > 0 else min(best, c[k])
            if thoat == "TR2": st = max(st, best - 2 * atr[k]) if s > 0 else min(st, best + 2 * atr[k])
            if k - j + 1 >= 72: X = o[k + 1] if s > 0 else o[k + 1] + sp[k + 1]; k += 1; break
            k += 1
        if X is None: break
        r = (X - E) / E if s > 0 else (E - X) / E
        out.append((d.index[j], r, s, k - j + 1, E, int(ngay[k] - ngay[j]))); i = max(k, i + 1)
    return out


def ema_chay(d, ema, atr, sig, mode, k, sp):
    dd = d.copy(); dd["spread_open"] = sp / v19.XM
    L = v21.chay(dd, ema, atr, sig, mode, k, 1.0, 72)
    ngay = d.index.normalize().asi8 // 86_400_000_000_000; pos = {t: i for i, t in enumerate(d.index)}; o = d["open"].to_numpy()
    hr = d.index.hour.to_numpy(); nd = np.r_[0, np.diff(d.index.normalize().asi8) > 0].astype(bool)
    out = []
    for t, r, s, nb in L:
        j = pos[t]; kk = min(j + nb - 1, len(o) - 1)
        # v21.chay da tru swap theo so lan qua ngay; cong lai de tinh swap thong nhat theo ngay lich o ket_qua()
        dem = int(np.sum(np.diff(hr[j:kk + 1]) < 0)) if hr.max() > 0 else int(np.sum(nd[j + 1:kk + 1]))
        out.append((t, r + dem * 0.025 / 365, s, nb, o[j], int(ngay[kk] - ngay[j])))
    return out


def ket_qua(L, giua, drift, pip, phi, slip_pip):
    """phi=False: truoc phi. phi=True: tru swap + truot slip_pip moi chieu."""
    if not L: return None
    r = np.array([x[1] - (x[5] * QD + 2 * slip_pip * pip / x[4] if phi else 0) - x[2] * drift * x[3] for x in L])
    t = np.array([x[0] for x in L]); a, b = r[t < giua], r[t >= giua]
    if len(a) < 15 or len(b) < 15 or b.std(ddof=1) == 0: return None
    eq = np.cumprod(1 + np.clip(r, -0.99, None))
    return {"n_ph": len(a), "n_kiem": len(b), "ph_pct": float(a.sum() * 100), "kiem_pct": float(b.sum() * 100),
            "p": MV.p1(b.mean() / b.std(ddof=1) * math.sqrt(len(b))), "maxdd_pct": float(np.max(1 - eq / np.maximum.accumulate(eq)) * 100),
            "tb_bps": float(r.mean() * 1e4)}


def mtf_huong(d, kh):
    if kh not in LON: return None
    lon = d["close"].resample(QUY[LON[kh]], label="left", closed="left").last().dropna()
    e = lon.ewm(span=50, adjust=False).mean(); sl = np.sign(e.diff())
    # gia tri cua nen lon chi dung SAU khi nen lon dong: dich nhan sang dau nen lon ke tiep
    sl.index = list(sl.index[1:]) + [sl.index[-1] + (sl.index[-1] - sl.index[-2])]
    return sl.reindex(d.index, method="ffill").fillna(0).to_numpy()


def lam(job):
    ten, kh = job
    g, loai, co_drift = nguon(ten)
    d = gop(g, "D1" if False else kh) if kh in KHUNG else (g if kh == "D1" else g.resample("W-FRI").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "spread_open": "first"}).dropna())
    d = d[d["high"] >= d["low"]].copy(); d["so_tick"] = 1
    if len(d) < 400: return []
    pip = pip_of(ten); giua = d.index[len(d) // 2]; c = d["close"]
    drift = float(np.mean(np.diff(np.log(c.to_numpy()))[: len(c) // 2])) if co_drift else 0.0
    s1, atr, _ = v19.tin_hieu(d); s2 = v19b.tin_moi(d, atr, giua); S = {**s1, **s2}
    sp0 = np.zeros(len(d)); sp1 = d["spread_open"].to_numpy() * v19.XM
    out = []; base = {"chuoi": ten, "khung": kh, "spread": loai, "n_nen": len(d)}

    def ghi(nhom, ten_o, f):
        Lg, L1, L15 = f(sp0), f(sp1), f(sp1 * 1.5)
        r = {**base, "nhom": nhom, "o": ten_o}
        g0 = ket_qua(Lg, giua, drift, pip, False, 0); m = ket_qua(L1, giua, drift, pip, True, 0.5)
        if g0: r["truoc_phi"] = g0
        if m:
            r.update(m); r["kiem_slip0_pct"] = ket_qua(L1, giua, drift, pip, True, 0)["kiem_pct"]
            r["kiem_slip1_pct"] = ket_qua(L1, giua, drift, pip, True, 1.0)["kiem_pct"]
            q = ket_qua(L15, giua, drift, pip, True, 1.0); r["kiem_x1_5_slip1_pct"] = q["kiem_pct"] if q else None
            phi = [(x[5] * QD + (sp1[d.index.get_loc(x[0])] + 1.0 * pip) / x[4]) * 1e4 for x in L1[:3000]]
            r["phi_lenh_bps"] = float(np.mean(phi)); r["bien_do_tho_bps"] = float(np.mean([abs(x[1]) for x in Lg]) * 1e4) if Lg else None
        out.append(r)

    for sname, nhom in TIN.items():
        sig = S[sname].astype(int)
        for th in THOAT: ghi(nhom, f"{sname}_{th}", lambda sp, sig=sig, th=th: chay(d, sig, th, atr, sp))
    a21 = v21.atr_of(d); hm = mtf_huong(d, kh)
    for mode, n, k, mt in EMAO:
        if mt and hm is None: continue
        ema = c.ewm(span=n, adjust=False).mean().to_numpy(); z = np.zeros(len(d))
        sig = v21.tin(d, ema, a21, mode, k, "KHONG", "KHONG", z, z, z, z)
        if mt: sig = np.where(np.sign(sig) == hm, sig, 0) if mode == "PB" else np.where(np.sign(sig) == hm, sig, 0)
        ghi("EMA_DA_KHUNG" if mt else "EMA", f"EMA{mode}{n}_k{k}{'_MTF' if mt else ''}", lambda sp, sig=sig, ema=ema, mode=mode, k=k: ema_chay(d, ema, a21, sig, mode, k, sp))
    print(ten, kh, len(d), "xong", flush=True)
    return out


def jobs():
    J = [(f"bo1_{c}", k) for c in F.CAP for k in KHUNG] + [(t, k) for t in ("bo2_eurusd18", "bo2_nzdusd18", "bo2_audcad08", "bo2_xauusd24") for k in KHUNG]
    J += [(t, k) for t in ("us500_h1", "uk100_h1") for k in ("H1", "H4")]
    J += [(t, k) for t in ("d1_eurusd", "d1_usdjpy", "d1_audusd", "d1_gbpusd", "d1_spx", "d1_vang") for k in ("D1", "W1")]
    return J


def main(ra=None):
    with Pool(3, maxtasksperchild=1) as P: R = P.map(lam, sorted(jobs(), key=lambda j: j[1] != "M5"), chunksize=1)
    o = [r for x in R for r in x]
    v = [r for r in o if "p" in r]
    J21 = json.load(open("reports/vong21.json"))
    cu = v19.ho_cu(); J = json.load(open("reports/vong19.json")); Jb = json.load(open("reports/vong19b.json")); J20 = json.load(open("reports/vong20.json"))
    cu += [r["p"] for r in J["o"] + J["ghep"] if "p" in r] + [r["p"] for r in Jb["o"] if "p" in r] + [r["p"] for r in J20["o"] if "p" in r] + [r["p"] for r in J21["o"] if "p" in r]
    assert len(cu) == J21["ho_holm"], len(cu)
    H = MV.holm(cu + [r["p"] for r in v])
    for r, h in zip(v, H[len(cu):]):
        r["p_holm"] = h; x15 = r.get("kiem_x1_5_slip1_pct")
        r["song"] = bool(h < 0.05 and r["ph_pct"] > 0 and r["kiem_pct"] > 0 and r["kiem_slip1_pct"] > 0 and x15 is not None and x15 > 0 and r["maxdd_pct"] < 80)
    g = [r for r in o if "truoc_phi" in r]; Hg = MV.holm([r["truoc_phi"]["p"] for r in g])
    for r, h in zip(g, Hg): r["truoc_phi"]["p_holm_rieng"] = h
    bang = {}
    for nh in sorted(set(r["nhom"] for r in o)):
        for kh in ["M5", "M15", "M30", "H1", "H4", "D1", "W1"]:
            xs = [r for r in o if r["nhom"] == nh and r["khung"] == kh]
            if not xs: continue
            tg = [r["truoc_phi"] for r in xs if "truoc_phi" in r]; ts = [r for r in xs if "p" in r]
            bang[f"{nh}|{kh}"] = {"o": len(xs), "o_do_duoc_truoc": len(tg), "o_do_duoc_sau": len(ts),
                "tv_kiem_truoc_pct": round(float(np.median([x["kiem_pct"] for x in tg])), 2) if tg else None,
                "lai_ca2_truoc_pct": round(100 * np.mean([x["ph_pct"] > 0 and x["kiem_pct"] > 0 for x in tg]), 0) if tg else None,
                "tv_lenh_truoc_bps": round(float(np.median([x["tb_bps"] for x in tg])), 2) if tg else None,
                "song_truoc_rieng": sum(x["p_holm_rieng"] < 0.05 and x["ph_pct"] > 0 and x["kiem_pct"] > 0 for x in tg),
                "tv_kiem_sau_pct": round(float(np.median([x["kiem_pct"] for x in ts])), 2) if ts else None,
                "lai_ca2_sau_pct": round(100 * np.mean([x["ph_pct"] > 0 and x["kiem_pct"] > 0 for x in ts]), 0) if ts else None,
                "tv_phi_bps": round(float(np.median([x["phi_lenh_bps"] for x in ts])), 2) if ts else None,
                "tv_bien_do_bps": round(float(np.median([x["bien_do_tho_bps"] for x in ts if x["bien_do_tho_bps"]])), 2) if ts else None,
                "song": sum(x["song"] for x in ts)}
    for k, x in bang.items(): print(k, x)
    print("ho", len(H), "o", len(o), "do duoc", len(v), "song", sum(r["song"] for r in v))
    for r in sorted(v, key=lambda r: r["p"])[:12]:
        print(r["chuoi"], r["khung"], r["o"], r["n_ph"], r["n_kiem"], "ph %.1f kiem %.1f s1 %.1f x15 %s p %.4g holm %.3f" % (r["ph_pct"], r["kiem_pct"], r["kiem_slip1_pct"], r["kiem_x1_5_slip1_pct"], r["p"], r["p_holm"]))
    print("TRUOC PHI tot nhat:")
    for r in sorted(g, key=lambda r: r["truoc_phi"]["p"])[:12]:
        t = r["truoc_phi"]; print(r["chuoi"], r["khung"], r["o"], t["n_kiem"], "ph %.1f kiem %.1f tb %.2fbps p %.3g holm_rieng %.3f" % (t["ph_pct"], t["kiem_pct"], t["tb_bps"], t["p"], t["p_holm_rieng"]), "sau", r.get("kiem_pct"))
    if ra: json.dump({"nhan": "MO PHONG", "ho_holm": len(H), "o": o, "bang": bang}, open(ra, "w"), ensure_ascii=False, indent=0, default=float)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
