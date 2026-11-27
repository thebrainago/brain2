# -*- coding: utf-8 -*-
"""Họ tín hiệu vàng: xu hướng, hồi quy, phá vỡ, phiên, mùa vụ. Tín hiệu tại đóng nến i, vào lệnh ở mở nến i+1."""
from __future__ import annotations
import numpy as np
import pandas as pd

EPS = 1e-12


def ema(x, n):
    s = pd.Series(x)
    return s.ewm(span=n, adjust=False).mean().to_numpy()


def sma(x, n):
    return pd.Series(x).rolling(n, min_periods=n).mean().to_numpy()


def stdev(x, n):
    return pd.Series(x).rolling(n, min_periods=n).std(ddof=0).to_numpy()


def rsi(c, n=14):
    d = np.diff(c, prepend=c[0])
    up = np.where(d > 0, d, 0.0)
    dn = np.where(d < 0, -d, 0.0)
    au = pd.Series(up).ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    ad = pd.Series(dn).ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    rs = au / (ad + EPS)
    return 100.0 - 100.0 / (1.0 + rs)


def atr(h, l, c, n=14):
    prev = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - prev), np.abs(l - prev)))
    return pd.Series(tr).ewm(alpha=1 / n, adjust=False).mean().to_numpy()


def macd(c, f=12, s=26, sig=9):
    m = ema(c, f) - ema(c, s)
    sg = ema(m, sig)
    return m, sg, m - sg


def di_adx(h, l, c, n=14):
    up = h - np.r_[h[0], h[:-1]]
    dn = np.r_[l[0], l[:-1]] - l
    plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
    minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)
    prev = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - prev), np.abs(l - prev)))
    atrn = pd.Series(tr).ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    pdi = 100 * pd.Series(plus_dm).ewm(alpha=1 / n, adjust=False).mean().to_numpy() / (atrn + EPS)
    mdi = 100 * pd.Series(minus_dm).ewm(alpha=1 / n, adjust=False).mean().to_numpy() / (atrn + EPS)
    dx = 100 * np.abs(pdi - mdi) / (pdi + mdi + EPS)
    adx = pd.Series(dx).ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    return pdi, mdi, adx


def donchian(h, l, n):
    hh = pd.Series(h).rolling(n, min_periods=n).max().to_numpy()
    ll = pd.Series(l).rolling(n, min_periods=n).min().to_numpy()
    # breakout so với cửa sổ KHÔNG gồm nến hiện tại
    hh_prev = np.r_[np.nan, hh[:-1]]
    ll_prev = np.r_[np.nan, ll[:-1]]
    return hh_prev, ll_prev


def ibs(o, h, l, c):
    return (c - l) / (h - l + EPS)


def _cross_up(a, b):
    prev_a = np.r_[a[0], a[:-1]]
    prev_b = np.r_[b[0], b[:-1]]
    return (prev_a <= prev_b) & (a > b)


def _cross_dn(a, b):
    prev_a = np.r_[a[0], a[:-1]]
    prev_b = np.r_[b[0], b[:-1]]
    return (prev_a >= prev_b) & (a < b)


def tin_vao(df: pd.DataFrame, ten: str) -> np.ndarray:
    """Mảng int8: +1 mua, -1 bán, 0 đứng. Quyết định lúc đóng nến."""
    o, h, l, c = (df[k].to_numpy(dtype=np.float64) for k in ("open", "high", "low", "close"))
    n = len(c)
    z = np.zeros(n, dtype=np.int8)
    gio = df["gio"].to_numpy() if "gio" in df.columns else np.zeros(n, dtype=int)
    gio_vn = df["gio_vn"].to_numpy() if "gio_vn" in df.columns else gio
    thu = df["thu"].to_numpy() if "thu" in df.columns else np.zeros(n, dtype=int)

    if ten == "ema_9_21":
        a, b = ema(c, 9), ema(c, 21)
        z[_cross_up(a, b)] = 1
        z[_cross_dn(a, b)] = -1
    elif ten == "ema_21_55":
        a, b = ema(c, 21), ema(c, 55)
        z[_cross_up(a, b)] = 1
        z[_cross_dn(a, b)] = -1
    elif ten == "sma_50_200":
        a, b = sma(c, 50), sma(c, 200)
        z[_cross_up(a, b)] = 1
        z[_cross_dn(a, b)] = -1
    elif ten == "gia_cat_sma50":
        b = sma(c, 50)
        z[_cross_up(c, b)] = 1
        z[_cross_dn(c, b)] = -1
    elif ten == "macd":
        m, sg, _ = macd(c)
        z[_cross_up(m, sg)] = 1
        z[_cross_dn(m, sg)] = -1
    elif ten == "adx_di":
        pdi, mdi, adx = di_adx(h, l, c)
        z[_cross_up(pdi, mdi) & (adx > 20)] = 1
        z[_cross_dn(pdi, mdi) & (adx > 20)] = -1
    elif ten == "ichimoku_tk":
        tenkan = (pd.Series(h).rolling(9).max() + pd.Series(l).rolling(9).min()).to_numpy() / 2
        kijun = (pd.Series(h).rolling(26).max() + pd.Series(l).rolling(26).min()).to_numpy() / 2
        z[_cross_up(tenkan, kijun)] = 1
        z[_cross_dn(tenkan, kijun)] = -1
    elif ten == "rsi_30_70":
        r = rsi(c, 14)
        pr = np.r_[r[0], r[:-1]]
        z[(pr <= 30) & (r > 30)] = 1
        z[(pr >= 70) & (r < 70)] = -1
    elif ten == "rsi_20_80":
        r = rsi(c, 14)
        pr = np.r_[r[0], r[:-1]]
        z[(pr <= 20) & (r > 20)] = 1
        z[(pr >= 80) & (r < 80)] = -1
    elif ten == "bb_fade":
        mid, sd = sma(c, 20), stdev(c, 20)
        up, dn = mid + 2 * sd, mid - 2 * sd
        pc, pu, pdn = np.r_[c[0], c[:-1]], np.r_[up[0], up[:-1]], np.r_[dn[0], dn[:-1]]
        z[(pc <= pdn) & (c > dn)] = 1
        z[(pc >= pu) & (c < up)] = -1
    elif ten == "ibs":
        v = ibs(o, h, l, c)
        z[v <= 0.2] = 1
        z[v >= 0.8] = -1
    elif ten == "zscore_20_2":
        mid, sd = sma(c, 20), stdev(c, 20)
        zs = (c - mid) / (sd + EPS)
        pz = np.r_[zs[0], zs[:-1]]
        z[(pz <= -2) & (zs > -2)] = 1
        z[(pz >= 2) & (zs < 2)] = -1
    elif ten == "donchian_20":
        hh, ll = donchian(h, l, 20)
        z[c > hh] = 1
        z[c < ll] = -1
    elif ten == "donchian_55":
        hh, ll = donchian(h, l, 55)
        z[c > hh] = 1
        z[c < ll] = -1
    elif ten == "fractal":
        # Williams 5 nến: đỉnh/đáy tại i-2, phá lúc đóng sau đó
        if n > 6:
            fr_hi = (h[2:-2] > h[0:-4]) & (h[2:-2] > h[1:-3]) & (h[2:-2] > h[3:-1]) & (h[2:-2] > h[4:])
            fr_lo = (l[2:-2] < l[0:-4]) & (l[2:-2] < l[1:-3]) & (l[2:-2] < l[3:-1]) & (l[2:-2] < l[4:])
            # fr_hi[k] là fractal tại nến k+2, cần nến k+4 mới xác nhận. Không nhìn trước.
            last_hi = np.full(n, np.nan)
            last_lo = np.full(n, np.nan)
            lh = np.nan
            llv = np.nan
            for i in range(n):
                k = i - 4
                if 0 <= k < n - 4:
                    if fr_hi[k]:
                        lh = h[k + 2]
                    if fr_lo[k]:
                        llv = l[k + 2]
                last_hi[i] = lh
                last_lo[i] = llv
            z[c > last_hi] = 1
            z[c < last_lo] = -1
    elif ten.startswith("orb_"):
        # Phá range N nến đầu phiên. Server: Á 02-08, London 10-16, NY 15-21.
        # Anh: London 14-20 VN = 09-15 máy chủ.
        cua = {
            "orb_a": (2, 4, 8),          # (gio_mo, n_nen_range_neu_H1, gio_het)
            "orb_london": (10, 2, 18),
            "orb_london_anh": (9, 2, 15),
            "orb_ny": (15, 2, 22),
        }.get(ten)
        if cua is None:
            return z
        g0, _, g1 = cua
        # range = high/low các nến cùng ngày có giờ < mốc vào lệnh, lấy 1-2 giờ đầu
        ngay = df["time"].dt.floor("D").to_numpy() if hasattr(df["time"].dt, "floor") else df["time"].to_numpy()
        # dùng ngày dương lịch của time
        day = pd.to_datetime(df["time"]).dt.normalize().to_numpy()
        rh = np.full(n, np.nan)
        rl = np.full(n, np.nan)
        cur_d = None
        mh = ml = None
        started = False
        for i in range(n):
            d = day[i]
            gi = int(gio[i])
            if cur_d != d:
                cur_d, mh, ml, started = d, None, None, False
            if gi >= g0 and not started:
                # tích lũy range đến hết giờ mở + 1
                if mh is None:
                    mh, ml = h[i], l[i]
                else:
                    mh = max(mh, h[i])
                    ml = min(ml, l[i])
                # khóa range sau giờ g0 (nến đầu phiên); nến sau đó mới break
                if gi > g0:
                    started = True
            rh[i], rl[i] = (mh if mh is not None else np.nan), (ml if ml is not None else np.nan)
            if started and gi < g1:
                if c[i] > mh:
                    z[i] = 1
                elif c[i] < ml:
                    z[i] = -1
    elif ten == "mua_giu":
        z[0] = 1  # tín hiệu một lần; mô phỏng sẽ giữ
    else:
        raise ValueError(f"Không biết tín hiệu vào: {ten}")
    # nến chưa đủ chỉ báo → 0
    z[np.isnan(c)] = 0
    return z


def bo_loc(df: pd.DataFrame, ten: str) -> np.ndarray:
    """Mảng int8: +1 chỉ cho long, -1 chỉ short, 2 cho cả hai, 0 cấm vào."""
    o, h, l, c = (df[k].to_numpy(dtype=np.float64) for k in ("open", "high", "low", "close"))
    n = len(c)
    if ten == "khong":
        return np.full(n, 2, dtype=np.int8)
    gio = df["gio"].to_numpy() if "gio" in df.columns else np.zeros(n, dtype=int)
    gio_vn = df["gio_vn"].to_numpy() if "gio_vn" in df.columns else gio
    thu = df["thu"].to_numpy() if "thu" in df.columns else np.zeros(n, dtype=int)
    thang = df["thang"].to_numpy() if "thang" in df.columns else np.zeros(n, dtype=int)
    ngay = df["ngay"].to_numpy() if "ngay" in df.columns else np.zeros(n, dtype=int)
    out = np.zeros(n, dtype=np.int8)

    if ten == "ema_trend_55":
        e = ema(c, 55)
        out[c > e] = 1
        out[c < e] = -1
    elif ten == "ema_trend_200":
        e = ema(c, 200)
        out[c > e] = 1
        out[c < e] = -1
    elif ten == "adx_25":
        pdi, mdi, adx = di_adx(h, l, c)
        ok = adx >= 25
        out[ok & (pdi > mdi)] = 1
        out[ok & (mdi > pdi)] = -1
    elif ten == "phien_london":
        out[(gio >= 10) & (gio < 18)] = 2
    elif ten == "phien_london_anh":
        # 14:00-20:00 VN = 09-15 máy chủ
        out[(gio >= 9) & (gio < 15)] = 2
    elif ten == "phien_ny":
        out[(gio >= 15) & (gio < 22)] = 2
    elif ten == "phien_a":
        out[(gio >= 2) & (gio < 10)] = 2
    elif ten == "mua_vu_8_2":
        # tháng 8 đến hết tháng 2
        out[(thang >= 8) | (thang <= 2)] = 2
    elif ten == "dow_tru_thu6":
        out[thu != 4] = 2
    elif ten == "cuoi_thang":
        out[(ngay <= 5) | (ngay >= 25)] = 2
    elif ten == "chi_mua":
        out[:] = 1
    elif ten == "santa":
        # 15/12-15/1
        out[((thang == 12) & (ngay >= 15)) | ((thang == 1) & (ngay <= 15))] = 2
    else:
        raise ValueError(f"Không biết bộ lọc: {ten}")
    return out


# Danh sách dùng khi quét
HO_VAO = [
    "ema_9_21", "ema_21_55", "sma_50_200", "gia_cat_sma50", "macd", "adx_di", "ichimoku_tk",
    "rsi_30_70", "rsi_20_80", "bb_fade", "ibs", "zscore_20_2",
    "donchian_20", "donchian_55", "fractal",
    "orb_london", "orb_london_anh", "orb_ny", "orb_a",
]
HO_VAO_NHO = [  # khung M5 (nhiều nến): bỏ bớt để kịp thời gian
    "ema_9_21", "ema_21_55", "macd", "rsi_30_70", "bb_fade", "ibs",
    "donchian_20", "orb_london_anh", "orb_ny", "adx_di",
]
HO_LOC = [
    "khong", "ema_trend_55", "ema_trend_200", "adx_25",
    "phien_london", "phien_london_anh", "phien_ny", "phien_a",
    "mua_vu_8_2", "dow_tru_thu6", "cuoi_thang", "chi_mua", "santa",
]
HO_LOC_NHO = ["khong", "ema_trend_55", "adx_25", "phien_london_anh", "phien_ny", "chi_mua", "mua_vu_8_2"]

# Quản trị: (tên, sl_atr, tp_atr, trail_atr, max_nen, chot_trong_ngay)
HO_QT = [
    ("atr_sl15_tp30", 1.5, 3.0, 0.0, 0, 0),
    ("atr_sl20_tp40", 2.0, 4.0, 0.0, 0, 0),
    ("atr_sl20_tp20", 2.0, 2.0, 0.0, 0, 0),
    ("atr_sl20_trail15", 2.0, 0.0, 1.5, 0, 0),
    ("atr_sl20_time24", 2.0, 4.0, 0.0, 24, 0),
    ("atr_sl20_eod", 2.0, 4.0, 0.0, 0, 1),
]
HO_QT_NHO = [
    ("atr_sl20_tp40", 2.0, 4.0, 0.0, 0, 0),
    ("atr_sl20_trail15", 2.0, 0.0, 1.5, 0, 0),
    ("atr_sl20_eod", 2.0, 4.0, 0.0, 0, 1),
]
