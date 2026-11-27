# -*- coding: utf-8 -*-
"""Mô phỏng mở rộng: lưới nhân lot, gỡ lệnh (tăng lot sau lỗ), hedge đảo chiều."""
from __future__ import annotations
import numpy as np
from numba import njit
from .mo_phong import VON_DAU, pd_to_years, phi_SWAP_LONG, phi_SWAP_SHORT

phi_SWAP_LONG_ = -83.83
phi_SWAP_SHORT_ = 20.64


def _dong_goi(von, dd, n_lenh, n_thang, tong, tt, tth, t0, t1, von_dau, ten, swap, lot, **extra):
    nam = pd_to_years(t0, t1)
    cagr = (von / von_dau) ** (1.0 / nam) - 1.0 if von > 0 and nam > 0 else -1.0
    wr = (n_thang / n_lenh) if n_lenh else 0.0
    pf = (tt / abs(tth)) if tth < 0 else (99.0 if tt > 0 else 0.0)
    d = {
        "quan_tri": ten,
        "von_cuoi": float(von),
        "cagr": float(cagr),
        "dd": float(dd),
        "n_lenh": int(n_lenh),
        "thang": int(n_thang),
        "winrate": float(wr),
        "pf": float(pf),
        "tong_pnl": float(tong),
        "nam": float(nam),
        "tu": str(t0),
        "den": str(t1),
        "swap": bool(swap),
        "von_dau": float(von_dau),
        "rui_ro": float(extra.pop("rui_ro", 0.02)),
        "dat": bool(cagr > 0.10 and dd < 0.80 and n_lenh >= 20 and von > 0),
        "dat_moi": bool(von > von_dau and dd < 0.80),
        "loi_nhuan_lai": float(von / von_dau - 1.0) if von_dau else 0.0,
        "lot_chan": float(lot),
    }
    d.update(extra)
    return d


@njit
def _phuc_hoi(
    open_, high, low, close, spread_pts, gio,
    atr, huong_loc,
    buoc_atr, max_chan, tp_atr_tb, sl_tong_atr,
    von_dau, lot_nen, tinh_swap, khung_nho,
    he_so_lot, he_so_phuc, max_bac,
):
    """Lưới + gỡ lệnh: sau rổ lỗ, nhân lot cả rổ kế tiếp cho đến khi hoàn lỗ hoặc đạt max_bac."""
    n = len(close)
    von = von_dau
    dinh = von_dau
    dd_max = 0.0
    n_lenh = 0
    n_thang = 0
    tong = 0.0
    tt = 0.0
    tth = 0.0
    fallback = 20.0 if khung_nho else 16.0
    MAXC = 12
    gia = np.zeros(MAXC)
    lots = np.zeros(MAXC)
    hu = 0
    nchan = 0
    bac = 0
    no = 0.0

    for i in range(1, n):
        if nchan > 0:
            if tinh_swap and gio[i] < gio[i - 1]:
                sw = 0.0
                for k in range(nchan):
                    sw += lots[k] * (phi_SWAP_LONG_ if hu > 0 else phi_SWAP_SHORT_)
                von += sw
                tong += sw
            ts = 0.0
            tl = 0.0
            for k in range(nchan):
                ts += gia[k] * lots[k]
                tl += lots[k]
            tb = ts / tl
            hit = 0
            ra = 0.0
            if hu > 0:
                if tp_atr_tb > 0 and high[i] >= tb + tp_atr_tb * atr[i - 1]:
                    hit = 2
                    ra = tb + tp_atr_tb * atr[i - 1]
                elif sl_tong_atr > 0 and low[i] <= tb - sl_tong_atr * atr[i - 1]:
                    hit = 1
                    ra = tb - sl_tong_atr * atr[i - 1]
            else:
                if tp_atr_tb > 0 and low[i] <= tb - tp_atr_tb * atr[i - 1]:
                    hit = 2
                    ra = tb - tp_atr_tb * atr[i - 1]
                elif sl_tong_atr > 0 and high[i] >= tb + sl_tong_atr * atr[i - 1]:
                    hit = 1
                    ra = tb + sl_tong_atr * atr[i - 1]
            if hit:
                pts = spread_pts[i] if spread_pts[i] > 0 else fallback
                ph = pts * 0.01
                pnl = 0.0
                for k in range(nchan):
                    gt = ra - hu * ph
                    pnl += lots[k] * 100.0 * hu * (gt - gia[k])
                von += pnl
                tong += pnl
                n_lenh += 1
                if pnl > 0:
                    n_thang += 1
                    tt += pnl
                else:
                    tth += pnl
                no -= pnl
                if no <= 0.0 and pnl > 0:
                    no = 0.0
                    bac = 0
                elif pnl < 0:
                    if bac < max_bac:
                        bac += 1
                nchan = 0
                hu = 0

        if von > dinh:
            dinh = von
        if dinh > 0:
            dd = (dinh - von) / dinh
            if dd > dd_max:
                dd_max = dd
        if von <= von_dau * 0.01:
            von = max(von, 0.0)
            break

        loc = huong_loc[i - 1]
        if loc == 0 or atr[i - 1] != atr[i - 1] or atr[i - 1] <= 0:
            continue
        pts = spread_pts[i] if spread_pts[i] > 0 else fallback
        ph = pts * 0.01
        scale = he_so_phuc ** bac
        if nchan == 0:
            hu = 1 if loc == 1 or loc == 2 else -1
            if loc == 2:
                hu = 1 if close[i - 1] >= open_[i - 1] else -1
            g = open_[i] + hu * ph
            gia[0] = g
            lots[0] = lot_nen * scale
            nchan = 1
        elif nchan < max_chan and nchan < MAXC:
            ts = 0.0
            tl = 0.0
            for k in range(nchan):
                ts += gia[k] * lots[k]
                tl += lots[k]
            tb = ts / tl
            nguoc = (open_[i] <= tb - buoc_atr * atr[i - 1]) if hu > 0 else (open_[i] >= tb + buoc_atr * atr[i - 1])
            if nguoc:
                g = open_[i] + hu * ph
                gia[nchan] = g
                lots[nchan] = lot_nen * scale * (he_so_lot ** nchan)
                nchan += 1

    if nchan > 0:
        pts = spread_pts[n - 1] if spread_pts[n - 1] > 0 else fallback
        ph = pts * 0.01
        pnl = 0.0
        for k in range(nchan):
            gt = close[n - 1] - hu * ph
            pnl += lots[k] * 100.0 * hu * (gt - gia[k])
        von += pnl
        tong += pnl
        n_lenh += 1
        if pnl > 0:
            n_thang += 1
            tt += pnl
        else:
            tth += pnl
        if von > dinh:
            dinh = von
        if dinh > 0:
            dd = (dinh - von) / dinh
            if dd > dd_max:
                dd_max = dd
    return von, dd_max, n_lenh, n_thang, tong, tt, tth


@njit
def _dao_hedge(
    open_, high, low, close, spread_pts, gio,
    atr, huong_loc,
    hedge_atr, tp_atr, sl_atr, he_so_hedge,
    von_dau, lot_nen, tinh_swap, khung_nho,
):
    """Vào 1 chiều theo lọc. Nếu ngược hedge_atr thì mở lệnh đảo he_so_hedge lần lot.
    Đóng cả hai khi lãi ròng >= tp_atr hoặc lỗ ròng <= sl_atr (theo ATR * lot gốc).
    he_so_hedge=1 khóa lỗ; >1 lệch theo chiều đảo để gỡ."""
    n = len(close)
    von = von_dau
    dinh = von_dau
    dd_max = 0.0
    n_lenh = 0
    n_thang = 0
    tong = 0.0
    tt = 0.0
    tth = 0.0
    fallback = 20.0 if khung_nho else 16.0
    hu = 0
    gia1 = 0.0
    lot1 = 0.0
    gia2 = 0.0
    lot2 = 0.0
    co_hedge = 0

    for i in range(1, n):
        pts = spread_pts[i] if spread_pts[i] > 0 else fallback
        ph = pts * 0.01
        if hu != 0:
            if tinh_swap and gio[i] < gio[i - 1]:
                sw = lot1 * (phi_SWAP_LONG_ if hu > 0 else phi_SWAP_SHORT_)
                if co_hedge == 1:
                    sw += lot2 * (phi_SWAP_LONG_ if (-hu) > 0 else phi_SWAP_SHORT_)
                von += sw
                tong += sw

            a = atr[i - 1] if atr[i - 1] == atr[i - 1] and atr[i - 1] > 0 else 0.0
            # mở hedge khi chưa có và giá đi ngược
            if co_hedge == 0 and a > 0:
                nguoc = (low[i] <= gia1 - hedge_atr * a) if hu > 0 else (high[i] >= gia1 + hedge_atr * a)
                if nguoc:
                    pxh = gia1 - hu * hedge_atr * a
                    gia2 = pxh + (-hu) * ph
                    lot2 = lot_nen * he_so_hedge
                    co_hedge = 1

            hit = 0
            ra = 0.0
            if a > 0:
                moc_tp = tp_atr * a * lot_nen * 100.0
                moc_sl = -sl_atr * a * lot_nen * 100.0
                # P&L tại high / low / close; SL ưu tiên nếu cùng nến; khớp close (thận trọng)
                p_h = lot1 * 100.0 * hu * ((high[i] - hu * ph) - gia1)
                p_l = lot1 * 100.0 * hu * ((low[i] - hu * ph) - gia1)
                p_c = lot1 * 100.0 * hu * ((close[i] - hu * ph) - gia1)
                if co_hedge == 1:
                    p_h += lot2 * 100.0 * (-hu) * ((high[i] - (-hu) * ph) - gia2)
                    p_l += lot2 * 100.0 * (-hu) * ((low[i] - (-hu) * ph) - gia2)
                    p_c += lot2 * 100.0 * (-hu) * ((close[i] - (-hu) * ph) - gia2)
                sl_hit = (p_h <= moc_sl) or (p_l <= moc_sl) or (p_c <= moc_sl)
                tp_hit = (p_h >= moc_tp) or (p_l >= moc_tp) or (p_c >= moc_tp)
                if sl_hit:
                    hit = 1
                    ra = close[i]
                elif tp_hit:
                    hit = 2
                    ra = close[i]
            if hit:
                pnl = lot1 * 100.0 * hu * ((ra - hu * ph) - gia1)
                if co_hedge == 1:
                    pnl += lot2 * 100.0 * (-hu) * ((ra - (-hu) * ph) - gia2)
                von += pnl
                tong += pnl
                n_lenh += 1
                if pnl > 0:
                    n_thang += 1
                    tt += pnl
                else:
                    tth += pnl
                hu = 0
                lot1 = 0.0
                lot2 = 0.0
                co_hedge = 0

        if von > dinh:
            dinh = von
        if dinh > 0:
            dd = (dinh - von) / dinh
            if dd > dd_max:
                dd_max = dd
        if von <= von_dau * 0.01:
            von = max(von, 0.0)
            break

        loc = huong_loc[i - 1]
        if hu != 0 or loc == 0 or atr[i - 1] != atr[i - 1] or atr[i - 1] <= 0:
            continue
        pts = spread_pts[i] if spread_pts[i] > 0 else fallback
        ph = pts * 0.01
        hu = 1 if loc == 1 or loc == 2 else -1
        if loc == 2:
            hu = 1 if close[i - 1] >= open_[i - 1] else -1
        gia1 = open_[i] + hu * ph
        lot1 = lot_nen
        gia2 = 0.0
        lot2 = 0.0
        co_hedge = 0

    if hu != 0:
        pts = spread_pts[n - 1] if spread_pts[n - 1] > 0 else fallback
        ph = pts * 0.01
        px = close[n - 1]
        pnl = lot1 * 100.0 * hu * ((px - hu * ph) - gia1)
        if co_hedge == 1:
            pnl += lot2 * 100.0 * (-hu) * ((px - (-hu) * ph) - gia2)
        von += pnl
        tong += pnl
        n_lenh += 1
        if pnl > 0:
            n_thang += 1
            tt += pnl
        else:
            tth += pnl
        if von > dinh:
            dinh = von
        if dinh > 0:
            dd = (dinh - von) / dinh
            if dd > dd_max:
                dd_max = dd
    return von, dd_max, n_lenh, n_thang, tong, tt, tth


def mo_phong_phuc_hoi(df, loc, buoc_atr=1.5, max_chan=4, tp_atr_tb=1.2, sl_tong_atr=5.0,
                      he_so_lot=1.0, he_so_phuc=1.5, max_bac=3,
                      von_dau=VON_DAU, tinh_swap=False, khung="H1", rui_ro_gio=0.02):
    from .tin_hieu import atr as tinh_atr
    o = df["open"].to_numpy(np.float64)
    h = df["high"].to_numpy(np.float64)
    l = df["low"].to_numpy(np.float64)
    c = df["close"].to_numpy(np.float64)
    sp = df["spread"].to_numpy(np.float64)
    gio = df["gio"].to_numpy(np.int32)
    a = tinh_atr(h, l, c, 14)
    atr_med = float(np.nanmedian(a))
    rui_1lot = max(sl_tong_atr * atr_med * 100.0, 1.0)
    hs = float(he_so_lot)
    hp = float(he_so_phuc)
    mc = int(max_chan)
    if hs <= 1.0000001:
        tong_he = float(mc)
    else:
        tong_he = (hs ** mc - 1.0) / (hs - 1.0)
    # tính cả bậc gỡ tối đa
    tong_he *= (hp ** int(max_bac))
    lot_nen = max(0.01, min(50.0, np.floor((von_dau * rui_ro_gio / (rui_1lot * tong_he)) / 0.01) * 0.01))
    von, dd, n_lenh, n_thang, tong, tt, tth = _phuc_hoi(
        o, h, l, c, sp, gio, a, loc.astype(np.int8),
        float(buoc_atr), int(max_chan), float(tp_atr_tb), float(sl_tong_atr),
        float(von_dau), float(lot_nen), 1 if tinh_swap else 0,
        1 if khung.upper() in {"M1", "M5"} else 0,
        float(hs), float(hp), int(max_bac),
    )
    t0, t1 = df["time"].iloc[0], df["time"].iloc[-1]
    ten = f"phuc_b{buoc_atr}_c{max_chan}_tp{tp_atr_tb}_sl{sl_tong_atr}_x{hs}_g{hp}_bac{max_bac}"
    return _dong_goi(von, dd, n_lenh, n_thang, tong, tt, tth, t0, t1, von_dau, ten, tinh_swap, lot_nen,
                     he_so_lot=hs, he_so_phuc=hp, max_bac=int(max_bac), rui_ro=rui_ro_gio)


def mo_phong_hedge(df, loc, hedge_atr=2.0, tp_atr=1.2, sl_atr=4.0, he_so_hedge=1.5,
                   von_dau=VON_DAU, tinh_swap=False, khung="H1", rui_ro_gio=0.02):
    from .tin_hieu import atr as tinh_atr
    o = df["open"].to_numpy(np.float64)
    h = df["high"].to_numpy(np.float64)
    l = df["low"].to_numpy(np.float64)
    c = df["close"].to_numpy(np.float64)
    sp = df["spread"].to_numpy(np.float64)
    gio = df["gio"].to_numpy(np.int32)
    a = tinh_atr(h, l, c, 14)
    atr_med = float(np.nanmedian(a))
    # rủi ro theo SL ròng * he_so (xấp xỉ)
    rui_1lot = max(sl_atr * atr_med * 100.0 * max(he_so_hedge, 1.0), 1.0)
    lot_nen = max(0.01, min(50.0, np.floor((von_dau * rui_ro_gio / rui_1lot) / 0.01) * 0.01))
    von, dd, n_lenh, n_thang, tong, tt, tth = _dao_hedge(
        o, h, l, c, sp, gio, a, loc.astype(np.int8),
        float(hedge_atr), float(tp_atr), float(sl_atr), float(he_so_hedge),
        float(von_dau), float(lot_nen), 1 if tinh_swap else 0,
        1 if khung.upper() in {"M1", "M5"} else 0,
    )
    t0, t1 = df["time"].iloc[0], df["time"].iloc[-1]
    ten = f"hedge_h{hedge_atr}_tp{tp_atr}_sl{sl_atr}_x{he_so_hedge}"
    return _dong_goi(von, dd, n_lenh, n_thang, tong, tt, tth, t0, t1, von_dau, ten, tinh_swap, lot_nen,
                     he_so_hedge=float(he_so_hedge), rui_ro=rui_ro_gio)
