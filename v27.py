# -*- coding: utf-8 -*-
"""Vong 27 (MO PHONG): MRZ near-miss ghep luat Seeker (EMA12/26, RSI can) + da tai san + khung nho H1/H4; loc theo tang.
Dang ky: reports/vong27_tien_dang_ky.md. Toc do: nho dem tin_hieu (khong tinh lai 3 lan/che do phi) + chay song song theo o."""
from __future__ import annotations
import json, os, sys, time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
import v19, v22, v24, v26
import phi_xm_that as PX

DU = v26.DU
MOI = {"EURJPY_X": "eurjpy", "GBPJPY_X": "gbpjpy", "EURGBP_X": "eurgbp", "XAG": "xagusd", "SPX": "spxusd", "NSX": "nsxusd", "DAX": "grxeur"}
PHI_MOI = {"EURJPY_X": 3e-4, "GBPJPY_X": 3e-4, "EURGBP_X": 3e-4, "XAG": PX.BANG["SI_F"][1] * 1e-4, 
           "SPX": PX.BANG["iGSPC"][1] * 1e-4, "NSX": PX.BANG["iNDX"][1] * 1e-4, "DAX": PX.BANG["iGDAXI"][1] * 1e-4}
_TH = {}


def tin_hieu(d):
    k = (id(d), len(d))
    if k not in _TH: _TH[k] = v19.tin_hieu(d)
    return _TH[k]


def rsi(c, n=14):
    dl = c.diff(); u = dl.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); v = (-dl.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + u / v)


def loc(d, sig, kieu):
    c = d["close"]; sig = sig.copy()
    if kieu in ("EMA_DONG", "EMA_NGUOC"):
        t = np.sign((c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()).to_numpy())
        sig[(sig != t) if kieu == "EMA_DONG" else (sig == t)] = 0
    elif kieu == "RSI_CAN":
        r = rsi(c).to_numpy(); sig[~(((sig == 1) & (r < 35)) | ((sig == -1) & (r > 65)))] = 0
    return sig


def m5(ten):
    f = DU + (f"hd27/{MOI[ten]}_m5.csv" if ten in MOI else f"{v26.M5[ten]}_m5_histdata_ny7.csv")
    return pd.read_csv(f, parse_dates=["time"]).set_index("time") if os.path.exists(f) else None


def khung(ten, k):
    d = m5(ten)
    if d is None: return None
    g = d.resample(k).agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    g["spread_open"] = 0.0; g["so_tick"] = 1; return g


def phi_bar(ten, d, gio_co_dinh=None):
    if ten in v26.M5:
        h = np.full(len(d), gio_co_dinh) if gio_co_dinh is not None else d.index.hour
        return np.array([v26.sp_gio(ten, int(x)) for x in h]), "spread_do_theo_gio"
    if ten in PHI_MOI: return np.full(len(d), PHI_MOI[ten]), "bang_phi_xm/v24"
    return np.full(len(d), PX.bps_of_xm(ten, luc_mo_nen=False)), "bang_phi_xm/v24"


def chay_o(o):
    B, kieu, tach, gio = o["B"], o["ghep"], o["tach"], o.get("gio")
    v24.TACH_DONG[0] = tach; kq = {"phi": None}
    for che, hs, sl in (("truoc", 0, 0), ("sau", 1, 0.5), ("sau_x15_s1", 1.5, 1.0)):
        if che != "truoc":   # tang 1: chi sang phi khi truoc phi duong ca hai nua
            t = kq.get("truoc")
            if not t or t["tb_ph_bps"] <= 0 or t["tb_kiem_bps"] <= 0: kq["dung_tang"] = 1; break
        T = []
        for ten, d in B.items():
            s, atr, _ = tin_hieu(d); c = d["close"].to_numpy()
            drift = float(np.mean(np.diff(np.log(c[d.index < tach])))) if (d.index < tach).sum() > 50 else 0.0
            pb, kq["phi"] = phi_bar(ten, d, gio)
            T += v24.tra(v22.chay(d, loc(d, s["MRZ"].astype(int), kieu), "TR2", atr, c * pb * hs), drift, che != "truoc", sl)
        q = v24.danh_gia(T, len(B)) if T else None
        if q: kq[che] = q
        else: kq["dung_tang"] = 0; break
    return {k: v for k, v in o.items() if k not in ("B",)} | kq


def o_list():
    D1 = v24.tai_d1(); O = []
    for t in ("AUDUSD_X", "GBPUSD_X"):
        for g in ("EMA_DONG", "EMA_NGUOC", "RSI_CAN"):
            O.append({"phan": "P1_D1", "nhom": t, "khung": "D1", "ghep": g, "B": {t: D1[t]}, "tach": v26.TACH_A, "gio": 2})
    O.append({"phan": "P1_D1", "nhom": "POOL_FX_CHEO", "khung": "D1", "ghep": "KHONG", "B": {k: v for k, v in D1.items() if k.endswith("_X") and k not in v26.FX7}, "tach": v26.TACH_A})
    O.append({"phan": "P1_D1", "nhom": "POOL_HANGHOA_CHISO", "khung": "D1", "ghep": "KHONG", "B": {k: v for k, v in D1.items() if not k.endswith("_X")}, "tach": v26.TACH_A})
    for k, kk in (("H1", "1h"), ("H4", "4h")):
        Bk = {t: khung(t, kk) for t in v26.FX7}
        for nh, ts in (("AUDUSD", ["AUDUSD_X"]), ("GBPUSD", ["GBPUSD_X"]), ("POOL_FX7", v26.FX7)):
            O.append({"phan": "P2_khung_nho", "nhom": nh, "khung": k, "ghep": "KHONG", "B": {t: Bk[t] for t in ts}, "tach": v26.TACH_B})
        Bm = {t: x for t in MOI if (x := khung(t, kk)) is not None}
        O.append({"phan": "P2_khung_nho", "nhom": "POOL_MOI", "khung": k, "ghep": "KHONG", "B": Bm, "tach": v26.TACH_B, "tai_san": sorted(Bm)})
    return O


def main(song_song=True):
    t0 = time.time(); O = o_list(); t1 = time.time()
    if song_song:
        with ProcessPoolExecutor(min(8, os.cpu_count() or 1)) as ex: R = list(ex.map(chay_o, O))
    else: R = [chay_o(o) for o in O]
    return R, {"nap_giay": t1 - t0, "chay_giay": time.time() - t1}


def holm_cu():
    cu = v26.holm_cu() + [x["sau"]["p"] if "sau" in x else 1.0 for x in json.load(open("reports/vong26.json"))["o"]] + \
        [x["sau"]["p"] if "sau" in x else 1.0 for x in json.load(open("reports/vong26_seeker.json"))["o"]]
    assert len(cu) == json.load(open("reports/vong26_seeker.json"))["ho_holm"], len(cu)
    return cu


if __name__ == "__main__":
    R, tg = main("--tuan-tu" not in sys.argv); n = v26.cham(R, holm_cu())
    for r in R: print(r["phan"], r["nhom"], r["khung"], r["ghep"], {k: (round(r[k]["tb_ph_bps"], 1), round(r[k]["tb_kiem_bps"], 1), r[k]["n_ph"], r[k]["n_kiem"], round(r[k]["p"], 3), round(r[k]["maxdd_pct"], 1)) for k in ("truoc", "sau", "sau_x15_s1") if k in r}, "holm", round(r["p_holm"], 3), r["song"])
    print("ho", n, "song", sum(r["song"] for r in R), tg)
    json.dump({"nhan": "MO PHONG", "ho_holm": n, "toc_do": tg, "o": R}, open("reports/vong27.json", "w"), ensure_ascii=False, indent=0, default=str)
