# -*- coding: utf-8 -*-
"""ger_ea_tin_hieu.py - TIN HIEU cua cac EA ho geraked/metatrader5 cho `nhan/ger_ea.py` (12/10/2026).

DICH TAY tung ham `BuySignal()/SellSignal()` (doi chieu tung dong voi .mq5 cua tac gia, ghi o docstring
moi ham) - KHONG qua bo doc `doc_ma`, nen KHONG tinh vao so "diem vao dich duoc" cua bo doc. Chi bao
dung chi bao CHUAN cua MT5 (ma nguon Indicators/Examples): EMA, MACD (main), Stochastic, RSI, Bands,
Fractals. EA dung iCustom (CEZLSMA: HeikenAshi/ChandelierExit/ZLSMA; AFAOSMD: AverageForce/Andean)
-> CHUA DICH (`TIN_HIEU` khong co).

Quy uoc chi so: tin hieu cua bar j tinh o tick DAU bar j; `X[k]` cua EA (ArraySetAsSeries) = gia tri
tai bar j-k (k >= 1 = bar da dong). Tra {"huong", "sl", "tp"} (mang dai n; huong +1 = BuySignal
dung, -1 = SellSignal dung, 0 = khong). Gia ASK = BID + spread (tham so `s` theo bar).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

EMPTY = np.inf


# ------------------------------------------------------------------ chi bao chuan MT5
def ema(x: np.ndarray, n: int) -> np.ndarray:
    """Moving Average.mq5 CalculateEMA: buf[0] = price[0], buf[i] = p*a + buf[i-1]*(1-a), a = 2/(n+1)."""
    return pd.Series(x).ewm(alpha=2.0 / (n + 1), adjust=False).mean().to_numpy()


def macd_main(c: np.ndarray, nhanh: int, cham: int) -> np.ndarray:
    return ema(c, nhanh) - ema(c, cham)


def sma(x: np.ndarray, n: int) -> np.ndarray:
    return pd.Series(x).rolling(n).mean().to_numpy()


def stochastic(h, l, c, k: int, d: int, slowing: int):
    """Stochastic.mq5 (MODE_SMA, STO_LOWHIGH): main = 100*sum(c-LL, slowing)/sum(HH-LL, slowing)."""
    ll = pd.Series(l).rolling(k).min().to_numpy()
    hh = pd.Series(h).rolling(k).max().to_numpy()
    tu = pd.Series(c - ll).rolling(slowing).sum().to_numpy()
    mau = pd.Series(hh - ll).rolling(slowing).sum().to_numpy()
    main = np.where(mau == 0, 100.0, 100.0 * tu / np.where(mau == 0, 1, mau))
    return main, sma(main, d)


def rsi(c: np.ndarray, n: int) -> np.ndarray:
    """RSI.mq5: trung binh dau = SMA cua n chenh lech dau, sau do (cu*(n-1)+moi)/n."""
    dc = np.diff(c, prepend=c[0])
    up, dn = np.clip(dc, 0, None), np.clip(-dc, 0, None)
    ra = np.full(len(c), np.nan)
    if len(c) <= n:
        return ra
    ap, an = up[1:n + 1].mean(), dn[1:n + 1].mean()
    for i in range(n, len(c)):
        if i > n:
            ap = (ap * (n - 1) + up[i]) / n
            an = (an * (n - 1) + dn[i]) / n
        ra[i] = 100.0 - 100.0 / (1 + ap / an) if an != 0 else (100.0 if ap != 0 else 50.0)
    return ra


def bands(c: np.ndarray, n: int, dev: float):
    """BB.mq5: giua = SMA(n), do lech chuan TONG THE tren n gia."""
    s = pd.Series(c)
    m = s.rolling(n).mean().to_numpy()
    sd = s.rolling(n).std(ddof=0).to_numpy()
    return m, m + dev * sd, m - dev * sd


def _rong(n):
    return {"huong": np.zeros(n, dtype=int), "sl": np.zeros(n), "tp": np.zeros(n)}


def _lay(th, k, mac):
    v = str(th.get(k, mac)).strip()
    try:
        return float(v)
    except ValueError:
        return {"true": 1.0, "false": 0.0}.get(v.lower(), mac)


# ------------------------------------------------------------------ cac EA
def tin_hieu_3maf(df, th: dict, s: np.ndarray, diem: float) -> tuple[dict, list]:
    """3MAF.mq5 v1.5. Buy: MA1[1]>MA2[1]>MA3[1] && Low(1)>MA3[1] && Low(1)<MA1[1] && FR_D[2]!=EMPTY;
    in=Ask; sl = Low(1)>MA2[1] ? MA2[1] : MA3[1]; d=|in-sl| < MinSL*_Point -> false (roi thu Sell);
    tp = in + TPCoef*d. Sell doi xung (High, FR_U, Bid).
    GIA DINH Fractals: Fractals.mq5 chi tinh toi bar series 3 (`i<rates_total-3`), o series 2 khong
    bao gio duoc ghi -> gia tri phu thuoc bo nho moi cua buffer. Tac gia co backtest CO lenh nen
    gia tri do != EMPTY_VALUE -> dieu kien fractal LUON DUNG (ghi ro, khong kiem duoc khi chua co MT5)."""
    o, h, l = (df[k].to_numpy(float) for k in ("open", "high", "low"))
    c = df["close"].to_numpy(float)
    meth = int(_lay(th, "MaMethod", 1))
    if meth != 1 or int(_lay(th, "MaPrice", 1)) != 1:
        raise NotImplementedError("3MAF: chi dich MaMethod=EMA, MaPrice=CLOSE")
    m1, m2, m3 = (ema(c, int(_lay(th, k, v))) for k, v in (("MA1Len", 60), ("MA2Len", 350),
                                                           ("MA3Len", 600)))
    tpc, minsl = _lay(th, "TPCoef", 1.5), _lay(th, "MinSL", 100)
    n = len(df)
    r = _rong(n)
    cb = ["Fractals series 2: GIA DINH != EMPTY_VALUE (dieu kien fractal luon dung)"]
    for j in range(601, n):
        a1, a2, a3, lo1, hi1 = m1[j - 1], m2[j - 1], m3[j - 1], l[j - 1], h[j - 1]
        ask, bid = o[j] + s[j], o[j]
        if a1 > a2 > a3 and lo1 > a3 and lo1 < a1:
            sl = a2 if lo1 > a2 else a3
            d = abs(ask - sl)
            if d >= minsl * diem:
                r["huong"][j], r["sl"][j], r["tp"][j] = 1, sl, ask + tpc * d
                continue
        if a3 > a2 > a1 and hi1 < a3 and hi1 > a1:
            sl = a2 if hi1 < a2 else a3
            d = abs(bid - sl)
            if d >= minsl * diem:
                r["huong"][j], r["sl"][j], r["tp"][j] = -1, sl, bid - tpc * d
    return r, cb


def _sl_swing(l, h, j, lookback, dev, diem, mua):
    """BuySL/SellSL(SL_SWING, lookback, price, dev, start=1): iLowest(MODE_LOW, lookback, 1)."""
    if mua:
        return float(np.min(l[j - lookback:j])) - dev * diem
    return float(np.max(h[j - lookback:j])) + dev * diem


def tin_hieu_2macdsto(df, th: dict, s: np.ndarray, diem: float) -> tuple[dict, list]:
    """2MACDSTO.mq5. Buy: M2[2]>0 && M1[2]<0 && STO_M[2]<20 && STO_M[2]<=STO_S[2] && STO_M[1]>STO_S[1];
    sl = BuySL(SLType=SWING, SLLookback, Ask, SLDev, 1); tp = in + TPCoef*|in-sl|. Sell doi xung (>80)."""
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    if int(_lay(th, "SLType", 0)) != 0 or int(_lay(th, "StoMethod", 0)) != 0 \
            or int(_lay(th, "StoPrice", 0)) != 0:
        raise NotImplementedError("2MACDSTO: chi dich SL_SWING, STO MODE_SMA/STO_LOWHIGH")
    M1 = macd_main(c, int(_lay(th, "M1Fast", 13)), int(_lay(th, "M1Slow", 21)))
    M2 = macd_main(c, int(_lay(th, "M2Fast", 34)), int(_lay(th, "M2Slow", 144)))
    sm, ss = stochastic(h, l, c, int(_lay(th, "StoKPeriod", 7)), int(_lay(th, "StoDPeriod", 3)),
                        int(_lay(th, "StoSlowing", 3)))
    lb, dev, tpc = int(_lay(th, "SLLookback", 7)), _lay(th, "SLDev", 60), _lay(th, "TPCoef", 1.0)
    n = len(df)
    r = _rong(n)
    for j in range(200, n):
        if M2[j - 2] > 0 and M1[j - 2] < 0 and sm[j - 2] < 20 and sm[j - 2] <= ss[j - 2] \
                and sm[j - 1] > ss[j - 1]:
            ask = o[j] + s[j]
            sl = _sl_swing(l, h, j, lb, dev, diem, True)
            r["huong"][j], r["sl"][j], r["tp"][j] = 1, sl, ask + tpc * abs(ask - sl)
        elif M2[j - 2] < 0 and M1[j - 2] > 0 and sm[j - 2] > 80 and sm[j - 2] >= ss[j - 2] \
                and sm[j - 1] < ss[j - 1]:
            bid = o[j]
            sl = _sl_swing(l, h, j, lb, dev, diem, False)
            r["huong"][j], r["sl"][j], r["tp"][j] = -1, sl, bid - tpc * abs(bid - sl)
    return r, []


def tin_hieu_bbrsi(df, th: dict, s: np.ndarray, diem: float) -> tuple[dict, list]:
    """BBRSI.mq5. Buy: RSI[2]<30 && Close(2)<BB_L[2] && RSI[1]>30 && Close(1)>BB_L[1] && RSI[1]<50 &&
    Close(1)<BB_M[1]; sl = SLCoef==0 ? in-SLDev*_Point : BB_L[1]-SLCoef*(BB_M[1]-BB_L[1])-SLDev*_Point;
    tp = in + TPCoef*|in-sl|. Sell doi xung (70, BB_U). CloseOrders (CheckClose) chi dich khi =false."""
    o, c = df["open"].to_numpy(float), df["close"].to_numpy(float)
    if _lay(th, "CloseOrders", 0):
        raise NotImplementedError("BBRSI: CloseOrders=true chua dich")
    m, u, lw = bands(c, int(_lay(th, "BBLen", 500)), _lay(th, "BBDev", 2.0))
    R = rsi(c, int(_lay(th, "RSILen", 7)))
    slc, sld, tpc = _lay(th, "SLCoef", 0.9), _lay(th, "SLDev", 0), _lay(th, "TPCoef", 1.0)
    n = len(df)
    r = _rong(n)
    for j in range(3, n):
        a, b = j - 1, j - 2
        if np.isnan(m[b]) or np.isnan(R[b]):
            continue
        if R[b] < 30 and c[b] < lw[b] and R[a] > 30 and c[a] > lw[a] and R[a] < 50 and c[a] < m[a]:
            vao = o[j] + s[j]
            sl = vao - sld * diem if not slc else lw[a] - slc * (m[a] - lw[a]) - sld * diem
            r["huong"][j], r["sl"][j], r["tp"][j] = 1, sl, vao + tpc * abs(vao - sl)
        elif R[b] > 70 and c[b] > u[b] and R[a] < 70 and c[a] < u[a] and R[a] > 50 and c[a] > m[a]:
            vao = o[j]
            sl = vao + sld * diem if not slc else u[a] + slc * (u[a] - m[a]) + sld * diem
            r["huong"][j], r["sl"][j], r["tp"][j] = -1, sl, vao - tpc * abs(vao - sl)
    return r, []


def _3macd_mot_chieu(M1, M2, M3, j, B, dau):
    """Mot ham BuySignal (dau=+1) / SellSignal (dau=-1) cua 3MACD.mq5 tai bar j (X[k] = X[j-k])."""
    g = lambda M, k: dau * M[j - k]          # quy ve chieu mua: "> 0" cua Buy == "< 0" cua Sell
    if g(M3, 1) > 0 and g(M2, 1) > 0 and g(M2, 2) > 0 and g(M2, 3) > 0 and g(M2, 1) > g(M2, 2) \
            and g(M2, 2) < g(M2, 3):
        jj = 0
        for i in range(2, B - 1):
            if g(M3, i) <= 0 or g(M3, i + 1) <= 0:
                return False
            if g(M2, i) <= 0 or g(M2, i + 1) <= 0:
                return False
            if g(M1, i) < 0 and g(M1, i + 1) > 0:
                jj = i + 1
                break
        if jj == 0:
            return False
        kk = 0
        for i in range(jj, B - 2):
            if g(M3, i) <= 0 or g(M3, i + 1) <= 0 or g(M3, i + 2) <= 0:
                return False
            if g(M2, i) <= 0 or g(M2, i + 1) <= 0 or g(M2, i + 2) <= 0:
                return False
            if g(M2, i) < g(M2, i + 1) and g(M2, i + 1) > g(M2, i + 2):
                kk = i + 1
                break
        return kk != 0
    if g(M3, 1) > 0 and g(M3, 2) > 0 and g(M3, 3) > 0 and g(M3, 1) > g(M3, 2) and g(M3, 2) < g(M3, 3):
        jj = 0
        for i in range(2, B - 1):
            if g(M3, i) <= 0 or g(M3, i + 1) <= 0:
                return False
            if g(M2, i) < 0 and g(M2, i + 1) > 0:
                jj = i + 1
                break
        if jj == 0:
            return False
        kk = 0
        for i in range(jj, B - 1):
            if g(M3, i) <= 0 or g(M3, i + 1) <= 0:
                return False
            if g(M2, i) <= 0 or g(M2, i + 1) <= 0:
                return False
            if g(M1, i) < 0 and g(M1, i + 1) > 0:
                kk = i + 1
                break
        if kk == 0:
            return False
        mm = 0
        for i in range(kk, B - 2):
            if g(M3, i) <= 0 or g(M3, i + 1) <= 0 or g(M3, i + 2) <= 0:
                return False
            if g(M2, i) <= 0 or g(M2, i + 1) <= 0 or g(M2, i + 2) <= 0:
                return False
            if g(M2, i) < g(M2, i + 1) and g(M2, i + 1) > g(M2, i + 2):
                mm = i + 1
                break
        return mm != 0
    return False


def tin_hieu_3macd(df, th: dict, s: np.ndarray, diem: float) -> tuple[dict, list]:
    """3MACD.mq5: ba MACD main; BuySignal/SellSignal dich tung vong lap (xem `_3macd_mot_chieu` -
    Sell = Buy voi moi so sanh doi dau, doi chieu tung dong). SL_SWING, tp = in +- TPCoef*|in-sl|."""
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    if int(_lay(th, "SLType", 0)) != 0:
        raise NotImplementedError("3MACD: chi dich SL_SWING")
    M1 = macd_main(c, int(_lay(th, "M1Fast", 5)), int(_lay(th, "M1Slow", 8)))
    M2 = macd_main(c, int(_lay(th, "M2Fast", 13)), int(_lay(th, "M2Slow", 21)))
    M3 = macd_main(c, int(_lay(th, "M3Fast", 34)), int(_lay(th, "M3Slow", 144)))
    B = int(_lay(th, "BuffSize", 32))
    lb, dev, tpc = int(_lay(th, "SLLookback", 7)), _lay(th, "SLDev", 60), _lay(th, "TPCoef", 2.0)
    n = len(df)
    r = _rong(n)
    for j in range(max(200, B + 1), n):
        if _3macd_mot_chieu(M1, M2, M3, j, B, 1):
            ask = o[j] + s[j]
            sl = _sl_swing(l, h, j, lb, dev, diem, True)
            r["huong"][j], r["sl"][j], r["tp"][j] = 1, sl, ask + tpc * abs(ask - sl)
        elif _3macd_mot_chieu(M1, M2, M3, j, B, -1):
            bid = o[j]
            sl = _sl_swing(l, h, j, lb, dev, diem, False)
            r["huong"][j], r["sl"][j], r["tp"][j] = -1, sl, bid - tpc * abs(bid - sl)
    return r, []


TIN_HIEU = {"3MAF": tin_hieu_3maf, "2MACDSTO": tin_hieu_2macdsto, "BBRSI": tin_hieu_bbrsi,
            "3MACD": tin_hieu_3macd}
CHUA_DICH = {"CEZLSMA": "iCustom HeikenAshi + ChandelierExit + ZLSMA, CloseOrders=true",
             "AFAOSMD": "iCustom AverageForce + AndeanOscillator"}
