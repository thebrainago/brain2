# -*- coding: utf-8 -*-
"""Mô phỏng lệnh: tín hiệu đóng nến i, vào mở nến i+1, SL/TP theo high/low nến sau. Nếu SL và TP cùng nến thì tính SL (thận trọng)."""
from __future__ import annotations
import numpy as np
from numba import njit
from . import phi_xm as phi

VON_DAU = 10_000.0
RUI_RO = 0.02  # 2% vốn / lệnh theo khoảng SL


@njit
def _mo_phong(
    open_, high, low, close, spread_pts,
    gio, thu,
    tin, loc,
    atr,
    sl_atr, tp_atr, trail_atr, max_nen, chot_trong_ngay,
    von_dau, rui_ro, tinh_swap, khung_nho,
):
    n = len(close)
    von = von_dau
    dinh = von_dau
    dd_max = 0.0
    huong = 0
    gia_vao = 0.0
    sl = 0.0
    tp = 0.0
    lot = 0.0
    nen_vao = -1
    gio_vao = -1
    thu_vao = -1
    phi_vao = 0.0
    n_lenh = 0
    n_thang = 0
    tong_pnl = 0.0
    tong_thang = 0.0
    tong_thua = 0.0
    # equity sampled each bar
    # we don't store full curve to save memory; only metrics

    fallback_pts = 20.0 if khung_nho else 16.0

    for i in range(1, n):
        # quản trị vị thế đang mở trên nến i (dùng OHLC nến i)
        if huong != 0:
            # swap nếu qua ngày (giờ giảm — qua nửa đêm máy chủ)
            if tinh_swap and gio[i] < gio[i - 1]:
                sw = lot * (phi_SWAP_LONG if huong > 0 else phi_SWAP_SHORT)
                # Wednesday 3-day: thu_vao is entry weekday; charge 3x when holding into Wed->Thu? 
                # XM swap3=Wed: charged on Wednesday night. Server: if previous hour was ... simpler: if thu[i]==3 and gio[i]==0 or gio crossed 0 on Wednesday
                if thu[i] == 3 and gio[i] < gio[i - 1]:
                    sw *= 3.0
                von += sw
                tong_pnl += sw

            hit_sl = False
            hit_tp = False
            if huong > 0:
                if sl > 0 and low[i] <= sl:
                    hit_sl = True
                if tp > 0 and high[i] >= tp:
                    hit_tp = True
            else:
                if sl > 0 and high[i] >= sl:
                    hit_sl = True
                if tp > 0 and low[i] <= tp:
                    hit_tp = True

            ra = 0.0
            ly_do = 0
            if hit_sl and hit_tp:
                ra = sl
                ly_do = 1
            elif hit_sl:
                ra = sl
                ly_do = 1
            elif hit_tp:
                ra = tp
                ly_do = 2
            else:
                # trailing
                if trail_atr > 0.0 and atr[i] == atr[i]:  # not nan
                    buoc = trail_atr * atr[i]
                    if huong > 0:
                        moi = close[i] - buoc
                        if moi > sl:
                            sl = moi
                    else:
                        moi = close[i] + buoc
                        if sl == 0.0 or moi < sl:
                            sl = moi
                # hết giờ / hết nến
                if max_nen > 0 and (i - nen_vao) >= max_nen:
                    ra = close[i]
                    ly_do = 3
                elif chot_trong_ngay == 1 and (gio[i] < gio[i - 1] or (gio[i] >= 23)):
                    # đóng trước khi qua ngày, hoặc nến 23h
                    ra = close[i]
                    ly_do = 4

            if ra != 0.0:
                pts = spread_pts[i] if spread_pts[i] > 0 else fallback_pts
                phi_ra = (0.5 * pts + 0.5 * pts) * 0.01  # nửa spread + trượt 0.5*spread = 1.0*spread giá
                # chi_phi_mot_chieu = 0.5*sg + 0.5*sg = sg, sg=pts*0.01
                if huong > 0:
                    gia_thuc = ra - phi_ra
                else:
                    gia_thuc = ra + phi_ra
                pnl = lot * 100.0 * huong * (gia_thuc - gia_vao)
                von += pnl
                tong_pnl += pnl
                n_lenh += 1
                if pnl > 0:
                    n_thang += 1
                    tong_thang += pnl
                else:
                    tong_thua += pnl
                huong = 0
                lot = 0.0

        if von > dinh:
            dinh = von
        if dinh > 0:
            dd = (dinh - von) / dinh
            if dd > dd_max:
                dd_max = dd
        if von <= von_dau * 0.01:
            # sập tài khoản
            von = max(von, 0.0)
            break

        # vào lệnh tại MỞ nến i, tín hiệu nến i-1
        if huong == 0:
            s = tin[i - 1]
            f = loc[i - 1]
            ok = False
            if s == 1 and (f == 1 or f == 2):
                ok = True
            elif s == -1 and (f == -1 or f == 2):
                ok = True
            if ok and atr[i - 1] == atr[i - 1] and atr[i - 1] > 0:
                hu = 1 if s == 1 else -1
                pts = spread_pts[i] if spread_pts[i] > 0 else fallback_pts
                phi_c = (pts * 0.01)  # một chiều = spread giá (nửa + trượt 0.5)
                gia = open_[i] + hu * phi_c
                sl_k = sl_atr * atr[i - 1]
                tp_k = tp_atr * atr[i - 1]
                if sl_k <= 0:
                    sl_k = 2.0 * atr[i - 1]
                sl_g = gia - hu * sl_k
                tp_g = gia + hu * tp_k if tp_atr > 0 else 0.0
                rui = sl_k * 100.0  # USD / 1 lot
                if rui <= 0:
                    continue
                lot0 = (von * rui_ro) / rui
                # làm tròn lot
                if lot0 < 0.01:
                    # bỏ lệnh quá nhỏ? vẫn vào lot min nếu rủi ro không vượt 5%
                    if 0.01 * rui > von * 0.05:
                        continue
                    lot0 = 0.01
                if lot0 > 50.0:
                    lot0 = 50.0
                lot0 = np.floor(lot0 / 0.01 + 1e-12) * 0.01
                if lot0 < 0.01:
                    continue
                huong = hu
                gia_vao = gia
                sl = sl_g
                tp = tp_g
                lot = lot0
                nen_vao = i
                gio_vao = gio[i]
                thu_vao = thu[i]

    # đóng vị thế còn lại ở close cuối
    if huong != 0:
        pts = spread_pts[n - 1] if spread_pts[n - 1] > 0 else fallback_pts
        phi_ra = pts * 0.01
        gia_thuc = close[n - 1] - huong * phi_ra
        pnl = lot * 100.0 * huong * (gia_thuc - gia_vao)
        von += pnl
        tong_pnl += pnl
        n_lenh += 1
        if pnl > 0:
            n_thang += 1
            tong_thang += pnl
        else:
            tong_thua += pnl
        if von > dinh:
            dinh = von
        if dinh > 0:
            dd = (dinh - von) / dinh
            if dd > dd_max:
                dd_max = dd

    return von, dd_max, n_lenh, n_thang, tong_pnl, tong_thang, tong_thua


# numba cannot read Python module constants easily inside njit if imported as objects;
# inlined 100.0, 0.01, swap numbers:
phi_SWAP_LONG = -83.83
phi_SWAP_SHORT = 20.64


def mo_phong_df(df, tin, loc, qt, von_dau=VON_DAU, rui_ro=RUI_RO, tinh_swap=False, khung="H1"):
    ten, sl_atr, tp_atr, trail_atr, max_nen, eod = qt
    o = df["open"].to_numpy(np.float64)
    h = df["high"].to_numpy(np.float64)
    l = df["low"].to_numpy(np.float64)
    c = df["close"].to_numpy(np.float64)
    sp = df["spread"].to_numpy(np.float64)
    gio = df["gio"].to_numpy(np.int32)
    thu = df["thu"].to_numpy(np.int32)
    from .tin_hieu import atr as tinh_atr
    a = tinh_atr(h, l, c, 14)
    khung_nho = 1 if khung.upper() in {"M1", "M5"} else 0
    von, dd, n_lenh, n_thang, tong, tt, tth = _mo_phong(
        o, h, l, c, sp, gio, thu,
        tin.astype(np.int8), loc.astype(np.int8), a,
        float(sl_atr), float(tp_atr), float(trail_atr), int(max_nen), int(eod),
        float(von_dau), float(rui_ro), 1 if tinh_swap else 0, khung_nho,
    )
    t0, t1 = df["time"].iloc[0], df["time"].iloc[-1]
    nam = (pd_to_years(t0, t1))
    cagr = (von / von_dau) ** (1.0 / nam) - 1.0 if von > 0 and nam > 0 else -1.0
    wr = (n_thang / n_lenh) if n_lenh else 0.0
    pf = (tt / abs(tth)) if tth < 0 else (99.0 if tt > 0 else 0.0)
    dat = (cagr > 0.10) and (dd < 0.80) and (n_lenh >= 20) and (von > 0)
    return {
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
        "swap": bool(tinh_swap),
        "von_dau": float(von_dau),
        "rui_ro": float(rui_ro),
        "dat": bool(dat),
        "loi_nhuan_lai": float(von / von_dau - 1.0) if von_dau else 0.0,
    }


def pd_to_years(t0, t1):
    return max((pd_ts(t1) - pd_ts(t0)).days / 365.25, 1e-6)


def pd_ts(x):
    import pandas as pd
    return pd.Timestamp(x)


def mua_giu(df, von_dau=VON_DAU, dung_don_bay=False):
    """Mua-giữ không đòn bẩy: 1 ounce cố định? Ở đây: dùng toàn bộ vốn mua vàng (không đòn bẩy), cộng phí vào/ra một lần."""
    import pandas as pd
    c = df["close"].to_numpy(np.float64)
    sp = df["spread"].to_numpy(np.float64)
    t0, t1 = df["time"].iloc[0], df["time"].iloc[-1]
    pts0 = sp[0] if sp[0] > 0 else 16.0
    pts1 = sp[-1] if sp[-1] > 0 else 16.0
    vao = c[0] + pts0 * 0.01
    ra = c[-1] - pts1 * 0.01
    ret = ra / vao - 1.0
    # max dd trên close (không đòn bẩy)
    eq = c / c[0]
    peak = np.maximum.accumulate(eq)
    dd = float(np.max((peak - eq) / peak))
    nam = pd_to_years(t0, t1)
    cagr = (1.0 + ret) ** (1.0 / nam) - 1.0 if (1.0 + ret) > 0 else -1.0
    return {
        "quan_tri": "mua_giu_khong_don_bay",
        "von_cuoi": von_dau * (1.0 + ret),
        "cagr": float(cagr),
        "dd": dd,
        "n_lenh": 1,
        "thang": 1 if ret > 0 else 0,
        "winrate": 1.0 if ret > 0 else 0.0,
        "pf": 99.0 if ret > 0 else 0.0,
        "tong_pnl": von_dau * ret,
        "nam": float(nam),
        "tu": str(t0),
        "den": str(t1),
        "swap": False,
        "von_dau": float(von_dau),
        "rui_ro": 0.0,
        "dat": bool(cagr > 0.10 and dd < 0.80),
        "loi_nhuan_lai": float(ret),
    }


@njit
def _luoi(
    open_, high, low, close, spread_pts, gio,
    atr, huong_loc,
    buoc_atr, max_chan, tp_atr_tb, sl_tong_atr,
    von_dau, lot_nen, tinh_swap, khung_nho,
    he_so_lot,
):
    """Lưới/DCA: theo bộ lọc hướng. he_so_lot=1 chân đều; >1 nhân lot kiểu martingale (chân k lot = lot_nen * he_so_lot**k)."""
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
    # tối đa 12 chân
    MAXC = 12
    gia = np.zeros(MAXC)
    lots = np.zeros(MAXC)
    hu = 0
    nchan = 0

    def _phi(i):
        pts = spread_pts[i] if spread_pts[i] > 0 else fallback
        return pts * 0.01

    for i in range(1, n):
        if nchan > 0:
            if tinh_swap and gio[i] < gio[i - 1]:
                sw = 0.0
                for k in range(nchan):
                    sw += lots[k] * (phi_SWAP_LONG if hu > 0 else phi_SWAP_SHORT)
                von += sw
                tong += sw
            # giá trung bình
            ts = 0.0
            tl = 0.0
            for k in range(nchan):
                ts += gia[k] * lots[k]
                tl += lots[k]
            tb = ts / tl
            # TP / SL tổng
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
                ph = _phi(i)
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

        # mở / thêm chân tại open i
        loc = huong_loc[i - 1]
        if loc == 0 or atr[i - 1] != atr[i - 1] or atr[i - 1] <= 0:
            continue
        ph = _phi(i)
        if nchan == 0:
            hu = 1 if loc == 1 or loc == 2 else -1
            # nếu loc==2: chiều theo donchian? dùng close vs open nến tín hiệu
            if loc == 2:
                hu = 1 if close[i - 1] >= open_[i - 1] else -1
            g = open_[i] + hu * ph
            gia[0] = g
            lots[0] = lot_nen
            nchan = 1
        elif nchan < max_chan and nchan < MAXC:
            # thêm khi đi ngược buoc_atr
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
                lots[nchan] = lot_nen * (he_so_lot ** nchan)
                nchan += 1

    if nchan > 0:
        ph = _phi(n - 1)
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


def mo_phong_luoi(df, loc, buoc_atr=1.0, max_chan=5, tp_atr_tb=1.0, sl_tong_atr=4.0,
                  von_dau=VON_DAU, tinh_swap=False, khung="H1", he_so_lot=1.0,
                  rui_ro_gio=0.02):
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
    # quy lot để cả rổ (tổng lot tối đa nếu đầy chân) ~ rui_ro_gio vốn khi chạm SL tổng
    hs = float(he_so_lot)
    mc = int(max_chan)
    if hs <= 1.0000001:
        tong_he = float(mc)
    else:
        tong_he = (hs ** mc - 1.0) / (hs - 1.0)
    lot_nen = max(0.01, min(50.0, np.floor((von_dau * rui_ro_gio / (rui_1lot * tong_he)) / 0.01) * 0.01))
    von, dd, n_lenh, n_thang, tong, tt, tth = _luoi(
        o, h, l, c, sp, gio, a, loc.astype(np.int8),
        float(buoc_atr), int(max_chan), float(tp_atr_tb), float(sl_tong_atr),
        float(von_dau), float(lot_nen), 1 if tinh_swap else 0,
        1 if khung.upper() in {"M1", "M5"} else 0,
        float(hs),
    )
    t0, t1 = df["time"].iloc[0], df["time"].iloc[-1]
    nam = pd_to_years(t0, t1)
    cagr = (von / von_dau) ** (1.0 / nam) - 1.0 if von > 0 and nam > 0 else -1.0
    wr = (n_thang / n_lenh) if n_lenh else 0.0
    pf = (tt / abs(tth)) if tth < 0 else (99.0 if tt > 0 else 0.0)
    tag = f"luoi_b{buoc_atr}_c{max_chan}_tp{tp_atr_tb}_sl{sl_tong_atr}"
    if abs(hs - 1.0) > 1e-9:
        tag += f"_x{hs}"
    return {
        "quan_tri": tag,
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
        "swap": bool(tinh_swap),
        "von_dau": float(von_dau),
        "rui_ro": float(rui_ro_gio),
        "dat": bool(cagr > 0.10 and dd < 0.80 and n_lenh >= 20 and von > 0),
        "dat_moi": bool(von > von_dau and dd < 0.80),
        "loi_nhuan_lai": float(von / von_dau - 1.0) if von_dau else 0.0,
        "lot_chan": float(lot_nen),
        "he_so_lot": float(hs),
    }
