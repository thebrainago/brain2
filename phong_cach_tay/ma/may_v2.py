# -*- coding: utf-8 -*-
"""Máy tay_v2: cụm vào, TP giá nhanh, DCA lot cố định, hedge nhỏ, đóng rổ khi lãi tổng.

Mô phỏng nến M1 (hoặc M5) với thứ tự trong nến thận trọng: giá bất lợi trước, TP sau.
Không đặt lệnh thật.
"""
from __future__ import annotations

import numpy as np
from numba import njit

MAXT = 128

# P indices
# 0 L0  1 K  2 tp  3 gap  4 hgap  5 hlot  6 hN  7 maxL  8 maxH
# 9 basket_min  10 spr  11 pv  12 swl  13 sws  14 EQ0  15 lev  16 ddb
# 17 htp  18 allow_new  19 flcap (tỷ lệ equity, 0=tắt; dừng DCA mới, không cắt SL)
# 20 hfrac (0=dùng hN*hlot; >0 = hedge = hfrac * lot chính)
# 21 dca_max_bars (0=tắt; hết số nến này thì không DCA thêm)


def P_v2(sym="XAU", **kw):
    if sym == "XAU":
        d = dict(L0=0.10, K=4, tp=4.00, gap=5.47, hgap=21.37, hlot=0.10, hN=5,
                 maxL=20, maxH=10, basket_min=0.0, spr=0.20, pv=100.0,
                 swl=-83.83, sws=20.64, EQ0=10000.0, lev=1000.0, ddb=3000.0,
                 htp=4.00, allow_new=0.0, flcap=0.0, hfrac=0.0, dca_max_bars=0.0)
    else:
        d = dict(L0=0.10, K=5, tp=6.53, gap=8.32, hgap=80.0, hlot=0.10, hN=5,
                 maxL=20, maxH=10, basket_min=0.0, spr=0.65, pv=1.0,
                 swl=-1.24, sws=0.17, EQ0=10000.0, lev=1000.0, ddb=3000.0,
                 htp=6.53, allow_new=0.0, flcap=0.0, hfrac=0.0, dca_max_bars=0.0)
    d.update(kw)
    return np.array([
        d["L0"], d["K"], d["tp"], d["gap"], d["hgap"], d["hlot"], d["hN"],
        d["maxL"], d["maxH"], d["basket_min"], d["spr"], d["pv"], d["swl"], d["sws"],
        d["EQ0"], d["lev"], d["ddb"], d["htp"], d["allow_new"],
        d["flcap"], d["hfrac"], d["dca_max_bars"],
    ], dtype=np.float64)


@njit(cache=True)
def _add(px, lots, side, hg, n, p, v, s, is_h):
    if n >= MAXT or v <= 0:
        return n
    px[n] = p
    lots[n] = v
    side[n] = s
    hg[n] = is_h
    return n + 1


@njit(cache=True)
def _close_one(px, lots, side, hg, n, k, fill, pv):
    pnl = (fill - px[k]) * side[k] * lots[k] * pv
    # swap remove
    last = n - 1
    if k != last:
        px[k] = px[last]
        lots[k] = lots[last]
        side[k] = side[last]
        hg[k] = hg[last]
    return n - 1, pnl


@njit(cache=True)
def _float_pnl(px, lots, side, n, mid, pv):
    s = 0.0
    for k in range(n):
        s += (mid - px[k]) * side[k] * lots[k] * pv
    return s


@njit(cache=True)
def run(o, h, l, c, roll, sig, P, i0, i1):
    """sig: +1 mua, -1 bán, 0 đứng. Conservative intrabar."""
    L0, K, tp, gap, hgap, hlot, hN, maxL, maxH, bmin, spr, pv, swl, sws, EQ0, lev, ddb, htp, allow_new = P[:19]
    flcap = P[19] if len(P) > 19 else 0.0
    hfrac = P[20] if len(P) > 20 else 0.0
    dca_max_bars = P[21] if len(P) > 21 else 0.0
    nbar = len(c)
    px = np.empty(MAXT)
    lots = np.empty(MAXT)
    side = np.empty(MAXT)
    hg = np.empty(MAXT)
    nt = 0
    cash = EQ0
    peak = EQ0
    maxdd = 0.0
    maxfl = 0.0  # most negative floating
    blown = -1.0
    n_en = 0
    n_tp = 0
    n_dca = 0
    n_hd = 0
    n_bk = 0  # basket flatten
    max_tix = 0
    max_lots = 0.0

    # shadow (up to 8000 baskets)
    MAXB = 8000
    bo = np.full(MAXB, -1)
    bc = np.full(MAXB, -1)
    bpnl = np.zeros(MAXB)
    bworst = np.zeros(MAXB)
    blots = np.zeros(MAXB)
    bnt = np.zeros(MAXB)
    nb = 0
    cur_open = -1
    cur_pnl = 0.0
    cur_worst = 0.0
    cur_lots = 0.0

    hs = spr * 0.5
    i0 = max(i0, 1)
    i1 = min(i1, nbar)

    eq_len = i1 - i0
    eq = np.empty(eq_len)

    for i in range(i0, i1):
        # swap
        if roll[i] and nt > 0:
            for k in range(nt):
                if side[k] > 0:
                    cash += swl * lots[k]
                else:
                    cash += sws * lots[k]

        # Vào cụm tại giá mở (tín hiệu đã shift, không nhìn trước), rồi xử lý trong nến.
        if blown < 0:
            s = sig[i]
            if s != 0 and nt == 0:
                fill = o[i] + s * hs
                kk = int(K)
                if kk < 1:
                    kk = 1
                for _j in range(kk):
                    if nt >= MAXT:
                        break
                    nt = _add(px, lots, side, hg, nt, fill, L0, s, 0.0)
                n_en += 1
                if cur_open < 0:
                    cur_open = i
                    cur_pnl = 0.0
                    cur_worst = 0.0
                    cur_lots = L0 * kk
                    if nb < MAXB:
                        bo[nb] = i
                        bnt[nb] = nt

        # --- sổ hiện có, bất lợi trước rồi TP ---
        if nt > 0:
            # determine main side = sign of non-hedge lots (or first ticket)
            main_s = 0.0
            last_main = np.nan
            n_main = 0
            v_main = 0.0
            v_h = 0.0
            n_h = 0
            for k in range(nt):
                if hg[k] == 0:
                    main_s = side[k]
                    last_main = px[k]
                    n_main += 1
                    v_main += lots[k]
                else:
                    v_h += lots[k]
                    n_h += 1
            # if only hedges left, they are the book
            if n_main == 0 and nt > 0:
                main_s = -side[0]

            # adverse extreme
            adv = l[i] if main_s > 0 else h[i]
            fav = h[i] if main_s > 0 else l[i]

            n_dca_before = n_dca
            n_hd_before = n_hd
            # DCA: step from last_main while adverse reaches next level
            # Dừng DCA mới nếu quá thời gian / lỗ thả nổi chạm trần % equity (không cắt SL).
            hold_ok = True
            if dca_max_bars > 0 and cur_open >= 0 and (i - cur_open) >= int(dca_max_bars):
                hold_ok = False
            fl_adv = _float_pnl(px, lots, side, nt, adv, pv)
            eq_ref = cash + _float_pnl(px, lots, side, nt, o[i], pv)
            cap_ok = True
            if flcap > 0 and fl_adv < 0 and (-fl_adv) >= flcap * max(eq_ref, 1.0):
                cap_ok = False
            if n_main > 0 and gap > 0 and hold_ok and cap_ok:
                guard = 0
                while n_main < int(maxL) and nt < MAXT and guard < 40:
                    guard += 1
                    nxt = last_main - main_s * gap
                    hit = (adv <= nxt) if main_s > 0 else (adv >= nxt)
                    if not hit:
                        break
                    fill = nxt + main_s * hs
                    extra = (adv - fill) * main_s * L0 * pv
                    if flcap > 0 and (fl_adv + extra) < 0 and (-(fl_adv + extra)) >= flcap * max(eq_ref, 1.0):
                        break
                    nt = _add(px, lots, side, hg, nt, fill, L0, main_s, 0.0)
                    last_main = fill
                    n_main += 1
                    v_main += L0
                    n_dca += 1
                    fl_adv += extra

            # Hedge when adverse from last_main (or basket mid) >= hgap
            if n_main > 0 and hgap > 0 and n_h < int(maxH) and nt < MAXT:
                # mid of mains
                midm = 0.0
                vm = 0.0
                for k in range(nt):
                    if hg[k] == 0:
                        midm += px[k] * lots[k]
                        vm += lots[k]
                if vm > 0:
                    midm /= vm
                    far = (midm - adv) * main_s  # positive if adverse
                    if far >= hgap:
                        hsides = -main_s
                        lv = midm - main_s * hgap
                        hfill = lv + hsides * hs
                        ok = (adv <= lv) if main_s > 0 else (adv >= lv)
                        if hfrac > 0:
                            htot = hfrac * vm
                            lot_h = L0 if L0 > 0 else hlot
                            if lot_h <= 0:
                                lot_h = 0.01
                            batch = int(max(1, round(htot / lot_h)))
                            h_each = htot / batch
                        else:
                            batch = int(hN)
                            h_each = hlot
                        left = int(maxH) - n_h
                        if batch > left:
                            batch = left
                        if ok and batch > 0 and h_each > 0:
                            for _b in range(batch):
                                if nt >= MAXT:
                                    break
                                nt = _add(px, lots, side, hg, nt, hfill, h_each, hsides, 1.0)
                                n_h += 1
                            n_hd += 1

            # Không lấy TP trong cùng nến đã DCA/hedge (tránh thiên lệch chữ V trên OHLC).
            added_adverse = (n_dca > n_dca_before) or (n_hd > n_hd_before)
            # Close TP: mains at +tp, hedges at +htp.
            guard = 0
            while (not added_adverse) and nt > 0 and guard < MAXT + 5:
                guard += 1
                closed_any = False
                k = 0
                while k < nt:
                    need = htp if hg[k] == 1 else tp
                    tgt = px[k] + side[k] * need
                    hit = (h[i] >= tgt) if side[k] > 0 else (l[i] <= tgt)
                    if hit:
                        fill = tgt
                        nt, pnl = _close_one(px, lots, side, hg, nt, k, fill, pv)
                        cash += pnl
                        cur_pnl += pnl
                        n_tp += 1
                        closed_any = True
                        # k stays, swapped
                    else:
                        k += 1
                if not closed_any:
                    break

            # flatten if total floating + already realized this basket >= bmin
            if nt > 0:
                mid = c[i]
                fl = _float_pnl(px, lots, side, nt, mid, pv)
                # realized this basket is cur_pnl; close if fl+?  Use mark-to-close at mid - side*hs
                close_pnl = 0.0
                for k in range(nt):
                    fill = mid - side[k] * hs
                    close_pnl += (fill - px[k]) * side[k] * lots[k] * pv
                if (cur_pnl + close_pnl) >= bmin and (cur_pnl + close_pnl) > 0:
                    cash += close_pnl
                    cur_pnl += close_pnl
                    nt = 0
                    n_bk += 1

        # mark equity
        mid = c[i]
        fl = _float_pnl(px, lots, side, nt, mid, pv) if nt > 0 else 0.0
        eqi = cash + fl
        if fl < maxfl:
            maxfl = fl
        if eqi > peak:
            peak = eqi
        dd = peak - eqi
        if dd > maxdd:
            maxdd = dd
        if eqi <= 0 and blown < 0:
            blown = float(i)
            # dump remaining
            if nt > 0:
                cash += fl
                nt = 0
            eqi = cash

        # end basket if flattened
        if nt == 0 and cur_open >= 0:
            if nb < MAXB:
                bc[nb] = i
                bpnl[nb] = cur_pnl
                bworst[nb] = cur_worst
                blots[nb] = cur_lots
                # bnt already
                nb += 1
            cur_open = -1
            cur_pnl = 0.0
            cur_worst = 0.0
            cur_lots = 0.0

        if nt > 0:
            if fl < cur_worst:
                cur_worst = fl
            vl = 0.0
            for k in range(nt):
                vl += lots[k]
            if vl > cur_lots:
                cur_lots = vl
            if nt > max_tix:
                max_tix = nt
            if vl > max_lots:
                max_lots = vl

        eq[i - i0] = eqi
        if blown >= 0 and i > int(blown):
            eq[i - i0] = cash

    # close leftover at last close (mark)
    if nt > 0:
        mid = c[i1 - 1]
        fl = 0.0
        for k in range(nt):
            fill = mid - side[k] * hs
            fl += (fill - px[k]) * side[k] * lots[k] * pv
        cash += fl
        cur_pnl += fl
        nt = 0
        if cur_open >= 0 and nb < MAXB:
            bc[nb] = i1 - 1
            bpnl[nb] = cur_pnl
            bworst[nb] = cur_worst
            blots[nb] = cur_lots
            nb += 1
        eq[-1] = cash

    net = cash - EQ0
    res = np.array([
        net, maxdd, maxfl, float(n_en), float(n_tp), float(n_dca), float(n_hd),
        float(n_bk), float(max_tix), max_lots, blown, float(nb), cash,
    ])
    return res, eq, bo[:nb].copy(), bc[:nb].copy(), bpnl[:nb].copy(), bworst[:nb].copy(), blots[:nb].copy()
