# -*- coding: utf-8 -*-
"""Bo sinh tin hieu du lieu Fxaurum dung chung (XAU <- GCZ6, US500 <- ESZ6). Viet boi worker SP500 (Phan 1), 27/11/2026.

CHI TINH TIN HIEU, KHONG DAT LENH. Dinh nghia giong sp500/ma/p1_quy_tac.py (da do trong sp500/P1_QUY_TAC_DATA.md).

Dau vao: bang phut futures (UTC ms) co cot o,h,l,c,vol,vol_mua,vol_ban,lon_mua,lon_ban (+ ho so KL theo phien neu co).
  - ES: sp500/ma/keo_tick_esz6.py -> phut_YYYYMMDD.csv / hoso_YYYYMMDD.csv (RTH 08:00-16:15 NY)
  - GC: sp500/ma/gom_tick_gc.py -> gc_phut.csv / gc_hoso.csv (phien Globex 18:00-17:00 NY)
Dau ra: DataFrame theo phut + ham chieu len truc nen M1 XM (gio may chu XM = gio New York + 7h).

Tin hieu (chieu +1 mua / -1 ban, chot o CUOI phut m, chi dung tu nen bat dau >= m + tre):
  big30      tong (mua lon - ban lon) 30' vuot nguong (phan vi 95%)
  delta15    delta 15' vuot nguong (phan vi 90%)
  cvd_pk     gia dinh/day 30' moi nhung CVD khong xac nhan -> nguoc lai
  vah_val_pha   dong vuot VAH/VAL phien truoc -> theo
  muc_fade   cham VAH/VAL/POC phien truoc roi dong vao trong -> nguoc (chi tinh khi big30, delta15 khong nguoc)
Luat uu tien (do o P1): big30 > delta15 > muc gia.
  uu_tien = 2*big30_giu + 1*delta15_giu  (giu 15')
  cong_dca_mua = 0 khi big30_giu < 0 (big trade ban dang ngược DCA mua), nguoc lai 1; cong_dca_ban tuong tu.
  sig_<ma>   tin hieu vao cum ngan da DAT o P1 (ES: vah_val_pha | cvd_pk+delta15; GC: big30 | big30+delta15 | delta15+muc_fade)
"""
from __future__ import annotations
import glob, os
import numpy as np
import pandas as pd

ES_DIR = "/workspace/sp500_2711/tick_esz6"
GC_DIR = "/workspace/sp500_2711/gc_tick"
NGUONG_MAC_DINH = {"ES": {"b30": 460.0, "d15": 910.4}, "GC": {"b30": 199.0, "d15": 227.0}}  # nua dau so phien, P1


def doc_phut(ma: str, thu_muc: str | None = None) -> tuple[pd.DataFrame, dict]:
    """Tra (bang phut, {phien: ho so KL})."""
    if ma == "ES":
        d = thu_muc or ES_DIR; fr = []; pro = {}
        for f in sorted(glob.glob(os.path.join(d, "phut_*.csv"))):
            x = pd.read_csv(f); ten = os.path.basename(f)[5:13]
            if len(x) < 300: continue
            x["phien"] = ten; fr.append(x)
            h = os.path.join(d, f"hoso_{ten}.csv")
            if os.path.exists(h): pro[ten] = pd.read_csv(h)
        F = pd.concat(fr).drop_duplicates("phut_ms").sort_values("phut_ms").reset_index(drop=True)
    else:
        d = thu_muc or GC_DIR
        F = pd.read_csv(os.path.join(d, "gc_phut.csv")).sort_values("phut_ms").reset_index(drop=True)
        ny = pd.to_datetime(F.phut_ms, unit="ms", utc=True).dt.tz_convert("America/New_York")
        F["phien"] = (ny + pd.Timedelta(hours=6)).dt.strftime("%Y%m%d").values
        hs = pd.read_csv(os.path.join(d, "gc_hoso.csv"), dtype={"ngay": str})
        pro = {k: v for k, v in hs.groupby("ngay")}
    return F, pro


def _va(hs: pd.DataFrame):
    hs = hs.sort_values("gia"); v = (hs.vol_mua + hs.vol_ban).values; g = hs.gia.values
    if len(v) < 5: return None
    i = int(np.argmax(v)); tot = v.sum(); lo = hi = i; acc = v[i]
    while acc < 0.7 * tot:
        a = v[lo - 1] if lo > 0 else -1; b = v[hi + 1] if hi < len(v) - 1 else -1
        if b >= a: hi += 1; acc += v[hi]
        else: lo -= 1; acc += v[lo]
    return g[i], g[hi], g[lo]


def tin_hieu(F: pd.DataFrame, pro: dict, nguong: dict, giu: int = 15) -> pd.DataFrame:
    """Them cot tin hieu vao bang phut (khong nhin truoc trong phut: dung du lieu den het phut m)."""
    F = F.copy(); g = F.groupby("phien")
    F["d"] = F.vol_mua - F.vol_ban; F["bd"] = F.lon_mua - F.lon_ban
    F["cvd"] = g["d"].cumsum()
    F["d15"] = g["d"].transform(lambda s: s.rolling(15, min_periods=15).sum())
    F["b30"] = g["bd"].transform(lambda s: s.rolling(30, min_periods=30).sum())
    F["hh30"] = g["h"].transform(lambda s: s.shift(1).rolling(30, min_periods=30).max())
    F["ll30"] = g["l"].transform(lambda s: s.shift(1).rolling(30, min_periods=30).min())
    g = F.groupby("phien")
    F["cmax30"] = g["cvd"].transform(lambda s: s.shift(1).rolling(30, min_periods=30).max())
    F["cmin30"] = g["cvd"].transform(lambda s: s.shift(1).rolling(30, min_periods=30).min())
    PH = sorted(F.phien.unique()); VA = {}
    for a, b in zip(PH[:-1], PH[1:]):
        if a in pro:
            r = _va(pro[a])
            if r: VA[b] = r
    for k, j in (("poc", 0), ("vah", 1), ("val", 2)):
        F[k] = F.phien.map(lambda p: VA.get(p, (np.nan,) * 3)[j])
    c = F.c.values; h = F.h.values; l = F.l.values; pc = np.r_[np.nan, c[:-1]]
    def z(): return np.zeros(len(F))
    x = z(); x[F.b30.values > nguong["b30"]] = 1; x[F.b30.values < -nguong["b30"]] = -1; F["big30"] = x
    x = z(); x[F.d15.values > nguong["d15"]] = 1; x[F.d15.values < -nguong["d15"]] = -1; F["delta15"] = x
    x = z(); x[(c >= F.hh30.values) & (F.cvd.values < F.cmax30.values)] = -1
    x[(c <= F.ll30.values) & (F.cvd.values > F.cmin30.values)] = 1; F["cvd_pk"] = x
    vah = F.vah.values; val = F.val.values; poc = F.poc.values
    x = z(); x[(pc <= vah) & (c > vah)] = 1; x[(pc >= val) & (c < val)] = -1; F["vah_val_pha"] = x
    x = z(); x[(h >= vah) & (c < vah)] = -1; x[(l <= val) & (c > val)] = 1
    t = (l <= poc) & (h >= poc); x[t & (pc > poc)] = 1; x[t & (pc < poc)] = -1; F["muc_fade"] = x
    def hold(col):
        s = pd.Series(np.where(F[col].values != 0, F[col].values, np.nan))
        return s.groupby(F.phien.values).transform(lambda q: q.ffill(limit=giu)).fillna(0).values
    gb = hold("big30"); gd = hold("delta15")
    F["big30_giu"] = gb; F["delta15_giu"] = gd
    F["uu_tien"] = 2 * gb + gd
    F["muc_hop_le"] = np.where((F.muc_fade.values != 0) & (gb * F.muc_fade.values >= 0) & (gd * F.muc_fade.values >= 0), F.muc_fade.values, 0)
    F["cong_dca_mua"] = (gb >= 0).astype(int); F["cong_dca_ban"] = (gb <= 0).astype(int)
    big = F.big30.values; d15 = F.delta15.values; cv = F.cvd_pk.values; mf = F.muc_fade.values
    F["sig_ES"] = np.where(F.vah_val_pha.values != 0, F.vah_val_pha.values, np.where((cv != 0) & (gd == cv), cv, 0))
    F["sig_GC"] = np.where(big != 0, big, np.where((d15 != 0) & (gb == d15), d15, np.where((mf != 0) & (gd == mf), mf, 0)))
    return F


def ms_tu_gio_may_chu(t: pd.Series) -> np.ndarray:
    """Gio may chu XM (naive) -> UTC ms. May chu XM = gio New York + 7h (kiem bang tuong quan 0,995-0,997)."""
    ny = (pd.to_datetime(t) - pd.Timedelta(hours=7)).dt.tz_localize("America/New_York", ambiguous="NaT", nonexistent="NaT")
    return ny.dt.tz_convert("UTC").dt.tz_localize(None).values.astype("datetime64[ms]").astype("int64")


def len_m1(F: pd.DataFrame, ms_m1: np.ndarray, cot: list[str], tre_ms: int = 120000, giu_phut: int = 1) -> dict:
    """Chieu cot tin hieu (theo phut futures) len truc nen M1 XM (ms_m1 = gio mo nen, UTC ms).
    Gia tri cua phut futures m dung cho nen M1 bat dau trong [m+tre, m+tre+giu_phut phut). Ngoai du lieu = 0 (trung tinh)."""
    out = {k: np.zeros(len(ms_m1)) for k in cot}
    o = np.argsort(ms_m1); srt = ms_m1[o]
    st = F.phut_ms.values + tre_ms
    j0 = np.searchsorted(srt, st); j1 = np.searchsorted(srt, st + giu_phut * 60000)
    for k in cot:
        v = F[k].values; nz = np.nonzero(v)[0]
        for i in nz:
            if j1[i] > j0[i]: out[k][o[j0[i]:j1[i]]] = v[i]
    return out


def tao(ma: str, ms_m1: np.ndarray | None = None, thu_muc: str | None = None, nguong: dict | None = None) -> tuple[pd.DataFrame, dict | None]:
    """Tien ich: doc + tinh tin hieu (+ chieu len M1 neu co ms_m1). Cot giu-15' (big30_giu, delta15_giu, uu_tien, cong_dca_*) chieu 1 phut/1 phut."""
    F, pro = doc_phut(ma, thu_muc)
    F = tin_hieu(F, pro, nguong or NGUONG_MAC_DINH[ma])
    if ms_m1 is None: return F, None
    cot = ["big30", "delta15", "cvd_pk", "vah_val_pha", "muc_fade", "muc_hop_le", "big30_giu", "delta15_giu", "uu_tien", f"sig_{ma}"]
    M = len_m1(F, ms_m1, cot)
    # cong DCA: 1 mac dinh (ngoai du lieu khong chan)
    M["cong_dca_mua"] = (M["big30_giu"] >= 0).astype(float); M["cong_dca_ban"] = (M["big30_giu"] <= 0).astype(float)
    return F, M
