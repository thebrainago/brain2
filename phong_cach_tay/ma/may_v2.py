# -*- coding: utf-8 -*-
"""Máy tay_v2: cụm vào, TP giá nhanh, DCA lot cố định, hedge nhỏ, đóng rổ khi lãi tổng.

Mô phỏng nến M1 (hoặc M5) với thứ tự trong nến thận trọng: giá bất lợi trước, TP sau.
Không đặt lệnh thật.

P thêm (22+): lot_decay, gap_atr, loss_close, max_age, adx_th, h_boost, cooldown.
loss_close: đóng cả rổ khi lỗ tổng (đã thực hiện + thả nổi) chạm X% equity lúc mở rổ — không phải SL từng lệnh.
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
# 22 lot_decay (0 hoặc 1=tắt; 0<d<1: lot tầng = L0*d^depth, làm tròn bước 0,01)
# 23 gap_atr (0=khe cố định; >0 khe = max(gap*0.5, gap_atr*ATR))
# 24 loss_close (0=tắt; đóng rổ khi lỗ tổng >= X * equity lúc mở)
# 25 max_age (0=tắt; đóng rổ sau N nến)
# 26 adx_th (0=tắt; ADX>=ngưỡng và slope ngược rổ thì dừng DCA mới)
# 27 h_boost (0=tắt; khi drift ngược, hfrac *= 1+h_boost)
# 28 cooldown (0=tắt; số nến không vào mới sau khi đóng lỗ tổng)
# 29 max_lc (0=tắt; sau N lần đóng lỗ tổng thì không mở rổ mới đến hết cửa sổ)
# 30 short_cap (0=tắt; trần tổng lot chiều ngắn, gồm cụm vào và DCA)


def P_v2(sym="XAU", **kw):
    if sym == "XAU":
        d = dict(L0=0.10, K=4, tp=4.00, gap=5.47, hgap=21.37, hlot=0.10, hN=5,
                 maxL=20, maxH=10, basket_min=0.0, spr=0.20, pv=100.0,
                 swl=-83.83, sws=20.64, EQ0=10000.0, lev=1000.0, ddb=3000.0,
                 htp=4.00, allow_new=0.0, flcap=0.0, hfrac=0.0, dca_max_bars=0.0,
                 lot_decay=0.0, gap_atr=0.0, loss_close=0.0, max_age=0.0,
                 adx_th=0.0, h_boost=0.0, cooldown=0.0, max_lc=0.0, short_cap=0.0)
    else:
        d = dict(L0=0.10, K=5, tp=6.53, gap=8.32, hgap=80.0, hlot=0.10, hN=5,
                 maxL=20, maxH=10, basket_min=0.0, spr=0.65, pv=1.0,
                 swl=-1.24, sws=0.17, EQ0=10000.0, lev=1000.0, ddb=3000.0,
                 htp=6.53, allow_new=0.0, flcap=0.0, hfrac=0.0, dca_max_bars=0.0,
                 lot_decay=0.0, gap_atr=0.0, loss_close=0.0, max_age=0.0,
                 adx_th=0.0, h_boost=0.0, cooldown=0.0, max_lc=0.0, short_cap=0.0)
    d.update(kw)
    return np.array([
        d["L0"], d["K"], d["tp"], d["gap"], d["hgap"], d["hlot"], d["hN"],
        d["maxL"], d["maxH"], d["basket_min"], d["spr"], d["pv"], d["swl"], d["sws"],
        d["EQ0"], d["lev"], d["ddb"], d["htp"], d["allow_new"],
        d["flcap"], d["hfrac"], d["dca_max_bars"],
        d["lot_decay"], d["gap_atr"], d["loss_close"], d["max_age"],
        d["adx_th"], d["h_boost"], d["cooldown"],
        d["max_lc"], d["short_cap"],
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
def _flatten(px, lots, side, n, mid, hs, pv):
    pnl = 0.0
    for k in range(n):
        fill = mid - side[k] * hs
        pnl += (fill - px[k]) * side[k] * lots[k] * pv
    return pnl


@njit(cache=True)
def _layer_lot(L0, decay, depth, step):
    if decay <= 0.0 or decay >= 1.0 or depth <= 0:
        v = L0
    else:
        v = L0
        d = 0
        while d < depth:
            v *= decay
            d += 1
    if step <= 0:
        step = 0.01
    v = np.floor(v / step + 0.5) * step
    if v < step * 0.5:
        return 0.0
    return v


def run(o, h, l, c, roll, sig, P, i0, i1, atr=None, slope=None, adx=None):
    n = len(c)
    z = np.zeros(n, dtype=np.float64)
    if atr is None:
        atr = z
    if slope is None:
        slope = z
    if adx is None:
        adx = z
    return _run(o, h, l, c, roll, sig, P, i0, i1,
                np.asarray(atr, dtype=np.float64),
                np.asarray(slope, dtype=np.float64),
                np.asarray(adx, dtype=np.float64))


@njit(cache=True)
def _run(o, h, l, c, roll, sig, P, i0, i1, atr, slope, adx):
    """sig: +1 mua, -1 bán, 0 đứng. Conservative intrabar."""
    L0, K, tp, gap, hgap, hlot, hN, maxL, maxH, bmin, spr, pv, swl, sws, EQ0, lev, ddb, htp, allow_new = P[:19]
    flcap = P[19] if len(P) > 19 else 0.0
    hfrac = P[20] if len(P) > 20 else 0.0
    dca_max_bars = P[21] if len(P) > 21 else 0.0
    lot_decay = P[22] if len(P) > 22 else 0.0
    gap_atr = P[23] if len(P) > 23 else 0.0
    loss_close = P[24] if len(P) > 24 else 0.0
    max_age = P[25] if len(P) > 25 else 0.0
    adx_th = P[26] if len(P) > 26 else 0.0
    h_boost = P[27] if len(P) > 27 else 0.0
    cooldown = P[28] if len(P) > 28 else 0.0
    max_lc = P[29] if len(P) > 29 else 0.0
    short_cap = P[30] if len(P) > 30 else 0.0
    step = 0.01
    if L0 >= 0.1:
        step = 0.01
    nbar = len(c)
    px = np.empty(MAXT)
    lots = np.empty(MAXT)
    side = np.empty(MAXT)
    hg = np.empty(MAXT)
    nt = 0
    cash = EQ0
    peak = EQ0
    maxdd = 0.0
    maxfl = 0.0
    blown = -1.0
    n_en = 0
    n_tp = 0
    n_dca = 0
    n_hd = 0
    n_bk = 0
    max_tix = 0
    max_lots = 0.0

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
    eq_open = EQ0
    k_init = 0
    cool_until = -1
    n_lc = 0

    hs = spr * 0.5
    i0 = max(i0, 1)
    i1 = min(i1, nbar)

    eq_len = i1 - i0
    eq = np.empty(eq_len)

    for i in range(i0, i1):
        if roll[i] and nt > 0:
            for k in range(nt):
                if side[k] > 0:
                    cash += swl * lots[k]
                else:
                    cash += sws * lots[k]

        if blown < 0:
            s = sig[i]
            if s != 0 and nt == 0 and i >= cool_until:
                fill = o[i] + s * hs
                kk = int(K)
                if kk < 1:
                    kk = 1
                if short_cap > 0.0 and s < 0:
                    capn = int(short_cap / L0 + 1e-12) if L0 > 0 else 0
                    if capn < 1:
                        kk = 0
                    elif kk > capn:
                        kk = capn
                if kk >= 1:
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
                    eq_open = cash
                    if eq_open < 1.0:
                        eq_open = 1.0
                    k_init = kk
                    if nb < MAXB:
                        bo[nb] = i
                        bnt[nb] = nt

        if nt > 0:
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
            if n_main == 0 and nt > 0:
                main_s = -side[0]

            adv = l[i] if main_s > 0 else h[i]
            fav = h[i] if main_s > 0 else l[i]

            n_dca_before = n_dca
            n_hd_before = n_hd

            # khe động theo ATR (ATR đã shift, không nhìn trước)
            gap_i = gap
            if gap_atr > 0.0 and atr[i] > 0.0:
                g2 = gap_atr * atr[i]
                if gap > 0.0:
                    if g2 < 0.5 * gap:
                        g2 = 0.5 * gap
                gap_i = g2

            # lỗ tổng tại cực bất lợi: đóng rổ trước khi DCA thêm
            fl_adv = _float_pnl(px, lots, side, nt, adv, pv)
            hit_loss = False
            if loss_close > 0.0 and (cur_pnl + fl_adv) <= -loss_close * eq_open:
                hit_loss = True
                close_pnl = _flatten(px, lots, side, nt, adv, hs, pv)
                cash += close_pnl
                cur_pnl += close_pnl
                nt = 0
                n_bk += 1
                n_lc += 1
                if cooldown > 0:
                    cool_until = i + int(cooldown)
                if max_lc > 0 and n_lc >= int(max_lc):
                    cool_until = nbar + 1

            hold_ok = True
            if dca_max_bars > 0 and cur_open >= 0 and (i - cur_open) >= int(dca_max_bars):
                hold_ok = False
            eq_ref = cash + _float_pnl(px, lots, side, nt, o[i], pv) if nt > 0 else cash
            cap_ok = True
            if (not hit_loss) and flcap > 0 and fl_adv < 0 and (-fl_adv) >= flcap * max(eq_ref, 1.0):
                cap_ok = False
            # regime: dừng DCA khi xu hướng ngược rổ
            regime_ok = True
            if adx_th > 0.0 and adx[i] >= adx_th and slope[i] * main_s < 0:
                regime_ok = False

            if (not hit_loss) and n_main > 0 and gap_i > 0 and hold_ok and cap_ok and regime_ok:
                guard = 0
                while n_main < int(maxL) and nt < MAXT and guard < 40:
                    guard += 1
                    nxt = last_main - main_s * gap_i
                    hit = (adv <= nxt) if main_s > 0 else (adv >= nxt)
                    if not hit:
                        break
                    depth = n_main - k_init
                    if depth < 1:
                        depth = 1
                    vadd = _layer_lot(L0, lot_decay, depth, step)
                    if vadd <= 0:
                        break
                    if short_cap > 0.0 and main_s < 0 and (v_main + vadd) > short_cap + 1e-12:
                        break
                    fill = nxt + main_s * hs
                    extra = (adv - fill) * main_s * vadd * pv
                    if flcap > 0 and (fl_adv + extra) < 0 and (-(fl_adv + extra)) >= flcap * max(eq_ref, 1.0):
                        break
                    if loss_close > 0.0 and (cur_pnl + fl_adv + extra) <= -loss_close * eq_open:
                        break
                    nt = _add(px, lots, side, hg, nt, fill, vadd, main_s, 0.0)
                    last_main = fill
                    n_main += 1
                    v_main += vadd
                    n_dca += 1
                    fl_adv += extra

            # Hedge
            if (not hit_loss) and n_main > 0 and hgap > 0 and n_h < int(maxH) and nt < MAXT:
                midm = 0.0
                vm = 0.0
                for k in range(nt):
                    if hg[k] == 0:
                        midm += px[k] * lots[k]
                        vm += lots[k]
                if vm > 0:
                    midm /= vm
                    far = (midm - adv) * main_s
                    if far >= hgap:
                        hsides = -main_s
                        lv = midm - main_s * hgap
                        hfill = lv + hsides * hs
                        ok = (adv <= lv) if main_s > 0 else (adv >= lv)
                        hf = hfrac
                        if h_boost > 0.0 and slope[i] * main_s < 0:
                            hf = hfrac * (1.0 + h_boost)
                        if hf > 0:
                            htot = hf * vm
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

            if not hit_loss:
                added_adverse = (n_dca > n_dca_before) or (n_hd > n_hd_before)
                # kiểm lỗ tổng lần nữa sau DCA/hedge, tại cực bất lợi
                if nt > 0 and loss_close > 0.0:
                    fl_adv2 = _float_pnl(px, lots, side, nt, adv, pv)
                    if (cur_pnl + fl_adv2) <= -loss_close * eq_open:
                        close_pnl = _flatten(px, lots, side, nt, adv, hs, pv)
                        cash += close_pnl
                        cur_pnl += close_pnl
                        nt = 0
                        n_bk += 1
                        hit_loss = True
                        added_adverse = True
                        n_lc += 1
                        if cooldown > 0:
                            cool_until = i + int(cooldown)
                        if max_lc > 0 and n_lc >= int(max_lc):
                            cool_until = nbar + 1

                guard = 0
                while (not hit_loss) and (not added_adverse) and nt > 0 and guard < MAXT + 5:
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
                        else:
                            k += 1
                    if not closed_any:
                        break

                if (not hit_loss) and nt > 0:
                    mid = c[i]
                    close_pnl = 0.0
                    for k in range(nt):
                        fill = mid - side[k] * hs
                        close_pnl += (fill - px[k]) * side[k] * lots[k] * pv
                    tot = cur_pnl + close_pnl
                    do_flat = False
                    is_loss_flat = False
                    if tot >= bmin and tot > 0:
                        do_flat = True
                    if (not do_flat) and loss_close > 0.0 and tot <= -loss_close * eq_open:
                        do_flat = True
                        is_loss_flat = True
                    if (not do_flat) and max_age > 0 and cur_open >= 0 and (i - cur_open) >= int(max_age):
                        do_flat = True
                    if do_flat:
                        cash += close_pnl
                        cur_pnl += close_pnl
                        nt = 0
                        n_bk += 1
                        if is_loss_flat:
                            n_lc += 1
                            if cooldown > 0:
                                cool_until = i + int(cooldown)
                            if max_lc > 0 and n_lc >= int(max_lc):
                                cool_until = nbar + 1

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
            if nt > 0:
                cash += fl
                nt = 0
            eqi = cash

        if nt == 0 and cur_open >= 0:
            if nb < MAXB:
                bc[nb] = i
                bpnl[nb] = cur_pnl
                bworst[nb] = cur_worst
                blots[nb] = cur_lots
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
