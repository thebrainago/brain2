# -*- coding: utf-8 -*-
"""So sanh phi XM Ultra Low (san chinh) va Exness (doi chieu) tren cac he dan dau. MO PHONG, KHONG PHAI TIEN THAT.
Gia: D1 Yahoo dang co (/workspace/du_lieu_ngay/v24, tu 2004). Moi lenh danh nghia co dinh 10.000 USD (khong lai kep).
Phi moi lenh (ty le danh nghia): spread (vao+ra)/2 + truot 0,5 x spread moi chieu + hoa hong + swap theo dem.
Gio khop: he vao/ra o MO NEN D1 = 00h server XM (~21-22h UTC -> Exness lay TB gio 21 va 22 UTC);
IBS vao/ra o DONG CUA = 23h server XM (~20h UTC Exness).
Dinh nghia he (lan chay nay, ghi ro vi chua co tham so chuan duy nhat trong repo):
  IBS: IBS=(C-L)/(H-L)<0,2 -> mua o dong cua, ban dong cua hom sau.
  MRZ(n,z=2): z=(C-SMA_n)/STD_n; z<-2 mua, z>2 ban, vao mo nen sau; dung 1,5xATR14; thoat khi z cat 0
    (dong cua -> mo nen sau), hoac trail kxATR theo dong cua tot nhat, hoac het H nen.
  RSI: RSI14<30 mua, >70 ban; thoat RSI cat 50; trail 2xATR; H=72.
"""
from __future__ import annotations
import json, math
import numpy as np, pandas as pd
import phi_xm_that as X
import phi_exness as E

DV = "/workspace/du_lieu_ngay/v24/"; VON = 10_000.0
HE = [  # ten, file, kieu, tham so, ma XM, ma Exness, lop
    ("IBS<0.2 US500", "iGSPC", "IBS", {}, "US500Cash#", "US500", "CS"),
    ("IBS<0.2 US100", "iNDX", "IBS", {}, "US100Cash#", "US100", "CS"),
    ("MRZ AUDUSD z2 SMA50 trail3", "AUDUSD_X", "MRZ", {"n": 50, "trail": 3, "H": 72}, "AUDUSD#", "AUDUSD", "FX"),
    ("MRZ GBPUSD SMA20 hold72", "GBPUSD_X", "MRZ", {"n": 20, "trail": None, "H": 72}, "GBPUSD#", "GBPUSD", "FX"),
    ("RSI EURJPY", "EURJPY_X", "RSI", {"trail": 2, "H": 72}, None, "EURJPY", "FX"),
    ("MRZ GER40", "iGDAXI", "MRZ", {"n": 20, "trail": 2, "H": 72}, "GER40Cash#", "GER40", "CS"),
    ("MRZ EURGBP", "EURGBP_X", "MRZ", {"n": 20, "trail": 2, "H": 72}, None, "EURGBP", "FX"),
    ("MRZ USDCAD", "USDCAD_X", "MRZ", {"n": 20, "trail": 2, "H": 72}, "USDCAD#", "USDCAD", "FX"),
]


def doc(f):
    d = pd.read_csv(DV + f + ".csv", index_col=0, parse_dates=True)
    d = d[(d.index >= "2004-01-01") & (d.high >= d.low) & (d.close > 0)]
    return d[(d.high > d.low) | (d.open != d.close)]


def atr(d, n=14):
    pc = d.close.shift(); tr = pd.concat([d.high - d.low, (d.high - pc).abs(), (d.low - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean().to_numpy()


def lenh(d, kieu, p):
    """Tra ve list (i_vao, i_ra, huong, gia_vao, gia_ra). Gia tho, chua phi."""
    o, h, l, c = (d[k].to_numpy() for k in ("open", "high", "low", "close")); n = len(c); out = []
    if kieu == "IBS":
        ibs = (c - l) / np.where(h > l, h - l, np.nan)
        for i in range(60, n - 1):
            if ibs[i] < 0.2: out.append((i, i + 1, 1, c[i], c[i + 1]))
        return out
    A = atr(d)
    if kieu == "MRZ":
        m = d.close.rolling(p["n"]).mean(); s = d.close.rolling(p["n"]).std(); z = ((d.close - m) / s).to_numpy()
        sig = np.where(z < -2, 1, np.where(z > 2, -1, 0)); thoat = lambda k, hu: (z[k] >= 0) if hu > 0 else (z[k] <= 0)
    else:
        dl = d.close.diff(); up = dl.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean(); dn = (-dl.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
        r = (100 - 100 / (1 + up / dn)).to_numpy(); sig = np.where(r < 30, 1, np.where(r > 70, -1, 0))
        thoat = lambda k, hu: (r[k] >= 50) if hu > 0 else (r[k] <= 50)
    i = 60
    while i < n - 2:
        hu = sig[i]; a = A[i]
        if hu == 0 or not np.isfinite(a) or a <= 0: i += 1; continue
        j = i + 1; Ev = o[j]; st = Ev - 1.5 * a * hu; best = c[j]; k = j; Xr = None; kr = None
        while k < n - 1:
            if (hu > 0 and l[k] <= st) or (hu < 0 and h[k] >= st): Xr, kr = (min(st, o[k]) if hu > 0 else max(st, o[k])) if k > j else st, k; break
            if thoat(k, hu) or k - j + 1 >= p["H"]: Xr, kr = o[k + 1], k + 1; break
            best = max(best, c[k]) if hu > 0 else min(best, c[k])
            if p.get("trail"): st = max(st, best - p["trail"] * A[k]) if hu > 0 else min(st, best + p["trail"] * A[k])
            k += 1
        if Xr is None: break
        out.append((j, kr, hu, Ev, Xr)); i = max(kr, i + 1)
    return out


def so_dem(t0, t1, ngay3):
    """So dem tinh swap tu ngay t0 den truoc t1 (ngay lam viec), ngay3 (0=Thu Hai) tinh 3."""
    tong = 0
    for dd in pd.bdate_range(t0.normalize(), t1.normalize() - pd.Timedelta(days=1)):
        tong += 3 if dd.dayofweek == ngay3 else 1
    return tong


THU = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4}
_EURUSD = None
UOC = set()


def danh_nghia_usd_1lot(ten_f, gia, t):
    global _EURUSD
    if ten_f.startswith("USD"): return 100000.0
    if ten_f in ("AUDUSD_X", "GBPUSD_X", "EURUSD_X", "NZDUSD_X"): return 100000.0 * gia
    if ten_f.startswith("EUR"):
        if _EURUSD is None: _EURUSD = doc("EURUSD_X").close
        return 100000.0 * float(_EURUSD.asof(t))
    return None


def chi_phi(san, kb, he, d, L):
    ten, f, kieu, p, ma_xm, ma_ex, lop = he
    gio_xm = 23 if kieu == "IBS" else 0; gio_ex = [20] if kieu == "IBS" else [21, 22]
    if san.startswith("XM"):
        tk = "UltraLow" if san == "XM_UltraLow" else "Standard"
        if ma_xm is None: return None, "spread/swap XM cho ma nay CHUA DO DUOC (khong co trong phi_xm_micro_that.csv)"
        v, uoc = X.spread_gio_bps_tk(ma_xm, gio_xm, tk); sp = v * 1e-4; hh = 0.0
        if uoc: UOC.add(f"{ma_xm}->{tk}")
        ngay3 = THU[X.spec_xm()[X.ho_so_xm(ma_xm, tk)[0]]["swap3"]]
        sw = lambda hu, g: X.swap_dem_tk(ma_xm, hu, g, "nhu_tester" if kb == "mien_swap" else "day_du", tk)
    else:
        loai = "Standard" if san == "Exness_Standard" else "Raw"
        v = [E.spread_bps(ma_ex, loai, g) for g in gio_ex]
        if any(x is None for x in v): return None, f"khong co du lieu tick Exness {ma_ex} {loai}"
        sp = float(np.mean(v)) * 1e-4; hh = E.HOA_HONG_USD_LOT_CHIEU[loai] if lop == "FX" else 0.0
        if kb == "mien_swap": sw = lambda hu, g: 0.0; ngay3 = 2
        else:
            if ma_xm is None: return None, "swap day du Exness CHUA DO DUOC (khong co muc swap proxy)"
            ngay3 = THU[X.spec_xm()[ma_xm]["swap3"]]; sw = lambda hu, g: X.swap_dem_ty_le(ma_xm, hu, g, "day_du")
    idx = d.index; R = []
    for (i, k, hu, Ev, Xr) in L:
        r = (Xr - Ev) / Ev * hu
        c = sp + 2 * X.TRUOT_X_SPREAD * sp  # spread (vao+ra)/2 = 1 spread; truot 0,5 spread moi chieu
        if hh:
            dn = danh_nghia_usd_1lot(f, Ev, idx[i]); c += 2 * hh / dn
        dem = so_dem(idx[i], idx[k], ngay3) if kieu != "IBS" else (3 if idx[i].dayofweek == ngay3 else 1)
        R.append((idx[i], r - c + sw(hu, Ev) * dem))
    return R, None


def thong_ke(R):
    if not R: return {"so_lenh": 0}
    r = np.array([x[1] for x in R]); usd = r * VON; eq = np.cumsum(usd); dd = np.max(np.maximum.accumulate(np.r_[0, eq])[1:] - eq)
    w, lo = usd[usd > 0].sum(), -usd[usd < 0].sum()
    return {"so_lenh": int(len(r)), "lai_rong_usd": round(float(usd.sum()), 2), "pf": round(float(w / lo), 3) if lo > 0 else None,
            "maxdd_usd": round(float(dd), 2), "maxdd_pct_von": round(float(dd / VON * 100), 2), "tb_bps": round(float(r.mean() * 1e4), 2)}


def main():
    SAN = ["XM_Standard", "XM_UltraLow", "Exness_Standard", "Exness_Raw"]; KB = ["mien_swap", "swap_day_du"]; out = []
    for he in HE:
        d = doc(he[1]); L = lenh(d, he[2], he[3]); mid = d.index[0] + (d.index[-1] - d.index[0]) / 2
        r0 = {"he": he[0], "du_lieu": f"{d.index[0].date()}..{d.index[-1].date()}", "moc_chia": str(mid.date()),
              "gia_tho": {"nua1": thong_ke([(d.index[i], (x - e) / e * hu) for i, k, hu, e, x in L if d.index[i] < mid]),
                          "nua2": thong_ke([(d.index[i], (x - e) / e * hu) for i, k, hu, e, x in L if d.index[i] >= mid])}, "ket_qua": {}}
        for s in SAN:
            for kb in KB:
                R, ly_do = chi_phi(s, kb, he, d, L); key = f"{s}|{kb}"
                r0["ket_qua"][key] = {"ghi_chu": ly_do} if R is None else {"nua1": thong_ke([x for x in R if x[0] < mid]), "nua2": thong_ke([x for x in R if x[0] >= mid])}
        out.append(r0); print(he[0], "xong", flush=True)
    out.append({"ma_spread_uoc": sorted(UOC)}); json.dump(out, open("reports/so_sanh_san.json", "w"), ensure_ascii=False, indent=1, default=str)
    return out


if __name__ == "__main__":
    main()
