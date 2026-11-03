# -*- coding: utf-8 -*-
"""MÔ PHỎNG Python 5 EA vàng (Telegram vutruea EA1..EA5) + CLMCA chế độ C_V1, dịch từ mã nguồn .mq5.
Mô hình: tín hiệu tại nến đã đóng -> vào ở giá mở nến kế (BUY tại ask = bid + spread); SL/TP kiểm bằng high/low BID
(SELL đóng ở ask); nến chạm cả SL và TP -> tính SL trước (bảo thủ); trailing/breakeven cập nhật bằng giá ĐÓNG nến
(tick thật sẽ khác). Giờ dữ liệu NY+7 (≈ giờ server XM) -> dùng thẳng cho bộ lọc giờ “GMT” của EA (EA dùng TimeCurrent()
= giờ server). Phí: spread 0,55 USD (p50 GOLDmicro XM đo), hoa hồng 0, swap XM đo (điểm/lot/ngày, x3 đêm thứ Tư) +
kịch bản BẢO THỦ (cả hai chiều = −83,83 điểm) và LẠC QUAN swap 0 (swap XM hiện tại áp cho 2009–2021 lúc lãi suất ~0 là quá nặng; swap lịch sử CHƯA ĐO ĐƯỢC). Margin 1:500, stop-out 20%. Lô chuẩn (100 oz), bước 0,01, tối thiểu 0,01.
    python -m nhan.dich_nguoc.backtest_vang
"""
from __future__ import annotations
import json
import numpy as np
import pandas as pd

FX = "/workspace/du_lieu_fx/"; HD = FX + "hd_dai/"
PT = 0.01; CS = 100.0; SPREAD = 0.55


# ---------------- dữ liệu ----------------
def doc_xau(khung: str) -> pd.DataFrame:
    """XAUUSD: histdata M1 2009–2023 (gộp) + hd28 M5 2024–2026, giờ NY+7."""
    phan = []
    p = HD + f"xauusd_{khung.lower()}_2009_2023_ny7.csv"
    try:
        phan.append(pd.read_csv(p, parse_dates=["time"]).set_index("time"))
    except FileNotFoundError:
        pass
    m5 = pd.read_csv(FX + "hd28/xauusd_m5_histdata_ny7_den202610.csv", parse_dates=["time"]).set_index("time")
    g = m5[["open", "high", "low", "close"]].resample({"M15": "15min", "H1": "1h", "H4": "4h"}[khung]).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    if phan: g = g[g.index > phan[-1].index[-1]]
    phan.append(g)
    g = pd.concat(phan).sort_index()
    return g[~g.index.duplicated()][["open", "high", "low", "close"]].astype(float)


# ---------------- chỉ báo kiểu MT5 ----------------
def ema(x, n): return pd.Series(x).ewm(span=n, adjust=False).mean().values
def atr_mt5(h, l, c, n=14):
    tr = np.maximum(h - l, np.maximum(abs(h - np.r_[c[0], c[:-1]]), abs(l - np.r_[c[0], c[:-1]])))
    return pd.Series(tr).rolling(n).mean().values          # iATR MT5 = SMA của TR
def rsi_mt5(c, n=14):
    d = np.diff(c, prepend=c[0]); u = pd.Series(np.clip(d, 0, None)).ewm(alpha=1 / n, adjust=False).mean()
    v = pd.Series(np.clip(-d, 0, None)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + u / v.replace(0, np.nan))).values


# ---------------- động cơ ----------------
def lot_theo_rui_ro(bal, pct, sl_gia):
    if sl_gia <= 0: return 0.01
    l = bal * pct / 100 / (sl_gia * CS)
    return max(0.01, np.floor(l / 0.01) * 0.01)


def mo_phong(g, tin_hieu, ten, von=10000.0, swap_mua=-83.83, swap_ban=20.64, don_bay=500.0):
    """tin_hieu(i, ctx) -> list lệnh mới {chieu, sl, tp, lot_pct|lot, quan_ly:{...}} vào tại open[i+1]; ctx có bal, so_mo."""
    O, H, L, C = (g[k].values for k in ("open", "high", "low", "close")); idx = g.index
    ngay = idx.normalize(); thu = idx.dayofweek
    bal = von; mo = []; dinh = von; dd = 0.0; so_lenh = 0; chet = False; so_so = 0; tong_swap = 0.0; cho = []
    def dong(p, gia, lot=None):
        nonlocal bal
        lot = p["lot"] if lot is None else lot
        ra = gia if p["c"] == 1 else gia + SPREAD          # SELL đóng ở ask
        bal += p["c"] * (ra - p["gia"]) * lot * CS
    for i in range(1, len(g)):
        # swap qua ngày
        if ngay[i] != ngay[i - 1] and mo:
            k3 = 3 if thu[i - 1] == 2 else 1
            sw = sum((swap_mua if p["c"] == 1 else swap_ban) * PT * CS * p["lot"] for p in mo) * k3; bal += sw; tong_swap += sw
        # lệnh chờ (EA3)
        con = []
        for q in cho:
            if idx[i] >= q["het"]: continue
            khop = (H[i] + SPREAD >= q["gia"]) if q["c"] == 1 else (L[i] <= q["gia"])
            if khop:
                gia = max(q["gia"], O[i] + SPREAD) if q["c"] == 1 else min(q["gia"], O[i])
                mo.append(dict(c=q["c"], gia=gia, sl=q["sl"], tp=q["tp"], lot=q["lot"], ql=q["ql"], best=gia)); so_lenh += 1
            else: con.append(q)
        cho = con
        # quản lý lệnh mở trên nến i
        giu = []
        for p in mo:
            c = p["c"]; lo = L[i] if c == 1 else L[i] + SPREAD; hi = H[i] if c == 1 else H[i] + SPREAD
            cham_sl = p["sl"] is not None and ((lo <= p["sl"]) if c == 1 else (hi >= p["sl"]))
            if cham_sl:
                gia_sl = min(p["sl"], O[i]) if c == 1 else max(p["sl"], O[i] + SPREAD)
                dong(p, gia_sl if c == 1 else gia_sl - SPREAD); continue
            ql = p["ql"]
            if ql.get("tp1") and not p.get("tp1_xong") and ((hi >= p["gia"] + ql["tp1"]) if c == 1 else (lo <= p["gia"] - ql["tp1"])):
                nua = max(0.01, np.floor(p["lot"] * 0.5 / 0.01) * 0.01)
                if nua < p["lot"]:
                    gia1 = p["gia"] + c * ql["tp1"]; dong(p, gia1 if c == 1 else gia1 - SPREAD, nua); p["lot"] = round(p["lot"] - nua, 2)
                p["sl"] = p["gia"] + c * ql["be_buf"]; p["tp1_xong"] = True
            if p["tp"] is not None and ((hi >= p["tp"]) if c == 1 else (lo <= p["tp"])):
                dong(p, p["tp"] if c == 1 else p["tp"] - SPREAD); continue
            # trailing / BE theo giá đóng
            cb = C[i] if c == 1 else C[i] + SPREAD
            if ql.get("trail_atr") is not None:
                moi = cb - c * ql["trail_atr"][i]
                if np.isfinite(moi) and (p["sl"] is None or c * (moi - p["sl"]) > PT): p["sl"] = moi
            if ql.get("trail_pt"):
                moi = cb - c * ql["trail_pt"]
                if p["sl"] is None or c * (moi - p["sl"]) > ql["trail_step"]: p["sl"] = moi
            if ql.get("be"):
                if c * (cb - p["gia"]) >= ql["be"] and (p["sl"] is None or c * (p["sl"] - p["gia"]) < 0): p["sl"] = p["gia"] + c * 10 * PT
            if ql.get("ladder_r"):
                p["best"] = max(p["best"], H[i]); f = int(np.floor((p["best"] - p["gia"]) / ql["ladder_r"] + 1e-9))
                if f >= 2:
                    tg = p["gia"] + (f - 2) * ql["ladder_r"]
                    if tg > p["sl"]:
                        if tg >= C[i]: dong(p, C[i]); continue
                        p["sl"] = tg
            giu.append(p)
        mo = giu
        noi = sum(p["c"] * (((C[i]) if p["c"] == 1 else C[i] + SPREAD) - p["gia"]) * p["lot"] * CS for p in mo)
        xau = sum(p["c"] * (((L[i] if p["c"] == 1 else H[i] + SPREAD)) - p["gia"]) * p["lot"] * CS for p in mo)
        e = bal + xau; marg = sum(p["lot"] for p in mo) * CS * C[i] / don_bay
        if mo and marg > 0 and e < 0.2 * marg:
            for p in mo: dong(p, L[i] if p["c"] == 1 else H[i])
            mo = []; so_so += 1; e = bal
        dinh = max(dinh, bal + noi); dd = max(dd, 1 - e / dinh)
        if bal <= 0.01 * von:
            chet = True; break
        if i + 1 < len(g):
            for q in tin_hieu(i, dict(bal=bal, so_mo=len(mo), mo=mo)):
                if q.get("cho"):
                    cho.append(q); continue
                gia = O[i + 1] + (SPREAD if q["c"] == 1 else 0.0)
                sl = q["sl_fn"](gia) if "sl_fn" in q else q["sl"]; tp = q["tp_fn"](gia) if "tp_fn" in q else q["tp"]
                if sl is not None and q["c"] * (gia - sl) <= 0: continue
                lot = lot_theo_rui_ro(bal, q["pct"], abs(gia - sl)) if "pct" in q else q["lot"]
                if lot <= 0: continue
                ql = dict(q.get("ql", {}))
                if q.get("r_tu_sl"): ql["ladder_r"] = gia - sl
                mo.append(dict(c=q["c"], gia=gia, sl=sl, tp=tp, lot=lot, ql=ql, best=gia)); so_lenh += 1
    eq = 0.0 if chet else bal + sum(p["c"] * (((C[-1]) if p["c"] == 1 else C[-1] + SPREAD) - p["gia"]) * p["lot"] * CS for p in mo)
    nam = max((idx[-1] - idx[0]).days, 1) / 365.25; cagr = (eq / von) ** (1 / nam) - 1 if eq > 0 else -1.0
    return {"ea": ten, "tu": str(idx[0]), "den": str(idx[-1]), "so_nam": round(nam, 2), "von": von, "equity_cuoi": round(float(eq), 2),
            "cagr": round(float(cagr), 4), "dd_max_equity": round(float(min(dd, 1)), 4), "so_lenh": so_lenh, "so_stop_out": so_so,
            "tong_swap": round(tong_swap, 2), "chay_tai_khoan": bool(chet), "dat": bool((not chet) and dd < 0.8 and cagr > 0.10)}


# ---------------- 5 EA + CLMCA ----------------
def ea1(g, rui_ro=1.5):
    c = g.close.values; f, m, s = ema(c, 21), ema(c, 55), ema(c, 200); a = atr_mt5(g.high.values, g.low.values, c)
    h = g.index.hour; d = g.index.dayofweek
    def th(i, ctx):
        # EA kiểm ở nến mới (i+1) với nến 1 = i, nến 2 = i-1; giờ/thứ của thời điểm kiểm = nến i+1
        if i < 201 or ctx["so_mo"] >= 1: return []
        t = g.index[i + 1]
        if t.dayofweek == 4 or t.hour < 7 or t.hour >= 21: return []
        bull = f[i] > m[i] > s[i]; bear = f[i] < m[i] < s[i]
        q = dict(pct=rui_ro, tp=None, ql=dict(trail_atr=a))
        if bull and c[i - 1] < f[i - 1] and c[i] > f[i]:
            return [dict(q, c=1, sl_fn=lambda p, x=a[i]: p - 1.5 * x, tp_fn=lambda p, x=a[i]: p + 3 * x)]
        if bear and c[i - 1] > f[i - 1] and c[i] < f[i]:
            return [dict(q, c=-1, sl_fn=lambda p, x=a[i]: p + 1.5 * x, tp_fn=lambda p, x=a[i]: p - 3 * x)]
        return []
    return th


def ea2(g, rui_ro=1.5):
    c = g.close.values; lo = g.low.values; hi = g.high.values
    mid = pd.Series(c).rolling(20).mean().values; sd = pd.Series(c).rolling(20).std(ddof=0).values
    up, dn = mid + 2 * sd, mid - 2 * sd; r = rsi_mt5(c)
    def th(i, ctx):
        if i < 21 or ctx["so_mo"] >= 1: return []
        t = g.index[i + 1]
        if t.dayofweek == 4 or t.hour < 8 or t.hour >= 20: return []
        ql = dict(be=200 * PT)
        if lo[i] <= dn[i] and c[i] > dn[i] and r[i] < 35:
            return [dict(c=1, pct=rui_ro, ql=ql, sl_fn=lambda p: p - 300 * PT, tp_fn=lambda p, m=mid[i]: m if m > p else p + 500 * PT)]
        if hi[i] >= up[i] and c[i] < up[i] and r[i] > 65:
            return [dict(c=-1, pct=rui_ro, ql=ql, sl_fn=lambda p: p + 300 * PT, tp_fn=lambda p, m=mid[i]: m if m < p else p - 500 * PT)]
        return []
    return th


def ea3(g, rui_ro=2.0):
    """London breakout (M15): range phiên Á 0–7h, đặt Buy/Sell Stop ±10 điểm lúc ≥7h, hủy lúc 12h; SL đối diện ±50 điểm; RR 2;
    trailing 200 điểm bước 50. Không thứ Sáu. Cả hai lệnh chờ có thể khớp (EA gốc không OCO)."""
    hi = g.high.values; lo = g.low.values; idx = g.index; da = {}
    def th(i, ctx):
        t = idx[i]; n = t.normalize()
        st = da.setdefault(n, {"h": -1e9, "l": 1e9, "xong": False})
        if t.dayofweek == 4: return []
        if t.hour < 7:
            st["h"] = max(st["h"], hi[i]); st["l"] = min(st["l"], lo[i]); return []
        t1 = idx[i + 1]
        if st["xong"] or t1.normalize() != n or t1.hour >= 12 or st["h"] < 0: return []
        st["xong"] = True
        if (st["h"] - st["l"]) / PT < 150: return []
        bp, sp = st["h"] + 10 * PT, st["l"] - 10 * PT; bsl, ssl = st["l"] - 50 * PT, st["h"] + 50 * PT
        het = n + pd.Timedelta(hours=12); ql = dict(trail_pt=200 * PT, trail_step=50 * PT)
        bl = lot_theo_rui_ro(ctx["bal"], rui_ro, bp - bsl); sl_ = lot_theo_rui_ro(ctx["bal"], rui_ro, ssl - sp)
        return [dict(cho=True, c=1, gia=bp, sl=bsl, tp=bp + 2 * (bp - bsl), lot=bl, het=het, ql=ql),
                dict(cho=True, c=-1, gia=sp, sl=ssl, tp=sp - 2 * (ssl - sp), lot=sl_, het=het, ql=ql)]
    return th


def ea4(g, rui_ro=1.5):
    c = g.close.values; e50, e200 = ema(c, 50), ema(c, 200); a = atr_mt5(g.high.values, g.low.values, c)
    macd = ema(c, 12) - ema(c, 26); sig = pd.Series(macd).rolling(9).mean().values; hist = macd - sig   # MT5 iMACD: signal = SMA
    def th(i, ctx):
        if i < 201 or ctx["so_mo"] >= 1: return []
        t = g.index[i + 1]
        if t.dayofweek == 4 or t.hour < 7 or t.hour >= 20: return []
        tr = 1.5 * a
        if c[i] > e200[i] and e50[i] > e200[i] and macd[i - 1] < sig[i - 1] and macd[i] > sig[i] and hist[i] > 0 and hist[i] > hist[i - 1]:
            return [dict(c=1, pct=rui_ro, ql=dict(trail_atr=tr), sl_fn=lambda p, x=a[i]: p - 2 * x, tp_fn=lambda p, x=a[i]: p + 4 * x)]
        if c[i] < e200[i] and e50[i] < e200[i] and macd[i - 1] > sig[i - 1] and macd[i] < sig[i] and hist[i] < 0 and hist[i] < hist[i - 1]:
            return [dict(c=-1, pct=rui_ro, ql=dict(trail_atr=tr), sl_fn=lambda p, x=a[i]: p + 2 * x, tp_fn=lambda p, x=a[i]: p - 4 * x)]
        return []
    return th


def ea5(g, rui_ro=1.0):
    c = g.close.values; hi = g.high.values; lo = g.low.values; e21 = ema(c, 21); O = g.open.values
    ll = pd.Series(lo).rolling(5).min(); hh = pd.Series(hi).rolling(5).max()
    k = (100 * (pd.Series(c) - ll).rolling(3).sum() / (hh - ll).rolling(3).sum()).values; dd_ = pd.Series(k).rolling(3).mean().values
    d1 = g.resample("1D").agg({"high": "max", "low": "min", "close": "last"}).dropna()
    pv = pd.DataFrame({"P": (d1.high + d1.low + d1.close) / 3}); pv["R1"] = 2 * pv.P - d1.low; pv["S1"] = 2 * pv.P - d1.high
    pv["R2"] = pv.P + d1.high - d1.low; pv["S2"] = pv.P - (d1.high - d1.low); pv = pv.shift(1)   # pivot của ngày hôm trước
    piv = pv.reindex(g.index.normalize()).values
    def th(i, ctx):
        if i < 30 or ctx["so_mo"] >= 2: return []
        t = g.index[i + 1]
        if t.dayofweek == 4 or t.hour < 7 or t.hour >= 20: return []
        P, R1, S1, R2, S2 = piv[i + 1]
        if not np.isfinite(P): return []
        bid = O[i + 1]; ask = bid + SPREAD; z = 150 * PT
        ql = dict(tp1=100 * PT, be_buf=10 * PT)
        if (abs(bid - S1) <= z or abs(bid - S2) <= z) and k[i - 1] < dd_[i - 1] and k[i] > dd_[i] and k[i] < 25 and c[i] > e21[i]:
            return [dict(c=1, pct=rui_ro, ql=ql, sl_fn=lambda p: p - 150 * PT, tp_fn=lambda p: p + 200 * PT)]
        if (abs(ask - R1) <= z or abs(ask - R2) <= z) and k[i - 1] > dd_[i - 1] and k[i] < dd_[i] and k[i] > 75 and c[i] < e21[i]:
            return [dict(c=-1, pct=rui_ro, ql=ql, sl_fn=lambda p: p + 150 * PT, tp_fn=lambda p: p - 200 * PT)]
        return []
    return th


def clmca_c_v1(g, rui_ro=1.0):
    """CLMCA C_V1 (M15, chỉ LONG): ADX-EMA14 ≥ 22; dragon (EMA34 high − EMA34 low) ≥ 0,7646·ATR; slope EMA34 close (lag 3)
    ≥ 0,1593·ATR; H4 & H1 close > EMA34 & EMA89 (nến khung lớn đã đóng); pullback: low(c2) ≤ EMA34h(c2) hoặc ≤ EMA89(c2);
    nến c1 xanh, close > EMA34h & EMA89; giờ UTC 7..19; SL = EMA89 − 0,9558·ATR; không TP; thang SL C (f≥2 -> entry+(f−2)R);
    tối đa 3 lệnh, tối đa 2 lệnh lỗ/ngày UTC. Rủi ro % số dư (bộ .set mặc định dùng $50/lệnh; ở đây % để lãi kép)."""
    o, h, l, c = (g[k].values for k in ("open", "high", "low", "close"))
    e34h, e34l, e34c, e89 = ema(h, 34), ema(l, 34), ema(c, 34), ema(c, 89)
    tr = np.maximum(h - l, np.maximum(abs(h - np.r_[c[0], c[:-1]]), abs(l - np.r_[c[0], c[:-1]])))
    atr = np.zeros(len(c)); atr[0] = h[0] - l[0]
    for i in range(1, len(c)): atr[i] = atr[i - 1] + (tr[i] - atr[i - 1]) / 14
    up = np.diff(h, prepend=h[0]); dn = -np.diff(l, prepend=l[0])
    pdm = np.where((up > dn) & (up > 0), up, 0.0); mdm = np.where((dn > up) & (dn > 0), dn, 0.0); pdm[0] = mdm[0] = 0
    tr2 = tr.copy(); tr2[0] = h[0] - l[0]
    str_, sp, sm = ema(tr2, 14), ema(pdm, 14), ema(mdm, 14)
    pdi, mdi = 100 * sp / (str_ + 1e-9), 100 * sm / (str_ + 1e-9); adx = ema(100 * abs(pdi - mdi) / (pdi + mdi + 1e-9), 14)
    def khung(r):
        k = g.resample(r, label="left").agg({"close": "last"}).dropna().close
        return pd.DataFrame({"c": k, "e34": ema(k.values, 34), "e89": ema(k.values, 89), "n": np.arange(1, len(k) + 1)}, index=k.index)
    H1, H4 = khung("1h"), khung("4h")
    # giờ UTC: dữ liệu NY+7 -> UTC theo lịch DST New York
    ny = (g.index - pd.Timedelta(hours=7)).tz_localize("America/New_York", ambiguous="NaT", nonexistent="shift_forward")
    gio_utc = ny.tz_convert("UTC").hour.values
    def asof(df, t, dur):
        j = df.index.searchsorted(t - dur, side="right") - 1
        return df.iloc[j] if j >= 0 else None
    lo_ngay = {}
    def th(i, ctx):
        if i < 200 or ctx["so_mo"] >= 3: return []
        if not (7 <= gio_utc[i] <= 19): return []
        dec = g.index[i] + pd.Timedelta(minutes=15)
        a1, a4 = asof(H1, dec, pd.Timedelta(hours=1)), asof(H4, dec, pd.Timedelta(hours=4))
        if a1 is None or a4 is None or a1.n < 89 or a4.n < 89: return []
        if not (a4.c > a4.e34 and a4.c > a4.e89 and a1.c > a1.e34 and a1.c > a1.e89): return []
        A = atr[i]
        if not (A > 0 and adx[i] >= 22 and e34h[i] - e34l[i] >= 0.7646233157450126 * A and e34c[i] - e34c[i - 3] >= 0.1592965241135443 * A): return []
        if not (l[i - 1] <= e34h[i - 1] or l[i - 1] <= e89[i - 1]): return []
        if not (c[i] > o[i] and c[i] > e34h[i] and c[i] > e89[i]): return []
        sl = e89[i] - 0.9557791446812658 * A
        return [dict(c=1, pct=min(rui_ro, 2.0), tp=None, sl_fn=lambda p, s=sl: s, ql=dict(ladder_r=None), r_tu_sl=True)]
    return th


EA = {"EA1_MultiEMA_ATR_H1": ("H1", ea1), "EA2_RSI_BB_H1": ("H1", ea2), "EA3_London_Breakout_M15": ("M15", ea3),
      "EA4_MACD_200EMA_H1": ("H1", ea4), "EA4_MACD_200EMA_H4": ("H4", ea4), "EA5_Stoch_Pivot_M15": ("M15", ea5),
      "CLMCA_C_V1_M15": ("M15", clmca_c_v1)}

if __name__ == "__main__":
    import sys
    chon = sys.argv[1:] or list(EA)
    ra = []; du = {}
    for ten in chon:
        kh, f = EA[ten]
        if kh not in du: du[kh] = doc_xau(kh)
        g = du[kh]
        for kb, (sm, sb) in {"swap_do_XM": (-83.83, 20.64), "swap_bao_thu": (-83.83, -83.83), "swap_0_lac_quan": (0.0, 0.0)}.items():
            k = mo_phong(g, f(g), ten, swap_mua=sm, swap_ban=sb); k.update(khung=kh, kich_ban_swap=kb); ra.append(k)
            print(json.dumps(k, ensure_ascii=False), flush=True)
    json.dump(ra, open("data/dich_nguoc/backtest_vang.json", "w"), ensure_ascii=False, indent=1)
