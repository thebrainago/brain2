# -*- coding: utf-8 -*-
"""Bộ mốc nam châm (magnetic levels) trên dữ liệu H1 giờ server NY+7. KHÔNG nhìn trước:
mỗi mốc có `kb` = chỉ số nến H1 đầu tiên mà mốc đã biết (mọi dữ liệu dùng để tính đều < kb).
Phiên (giờ server): Á 1–9h, Âu 9–16h, Mỹ 16–23h; London mở 10h, NY mở 16h, nửa đêm NY 07h.
VWAP: dữ liệu không có volume thật → dùng TWAP (trung bình giá đóng H1) và ghi rõ."""
import numpy as np
import pandas as pd
from nhan.song_zigzag_atr import atr, zigzag

PHIEN = {"A": (1, 9), "AU": (9, 16), "MY": (16, 23)}


def _luoi(p):
    g = 10 ** (np.floor(np.log10(p)) - 1)
    return g, g / 4


def moc(df):
    """df: H1 index thời gian, cột open/high/low/close. Trả DataFrame: ngay, ten, gia, kb."""
    o, h, l, c = (df[x].values for x in ("open", "high", "low", "close"))
    idx = df.index
    ngay = idx.normalize()
    a1 = atr(h, l, c)
    zz = {k: zigzag(h, l, a1, k) for k in (1.0, 2.0, 3.0)}
    d = df.groupby(ngay).agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"))
    d["twap"] = df.close.groupby(ngay).mean()
    for p, (g0, g1) in PHIEN.items():
        m = (idx.hour >= g0) & (idx.hour < g1)
        d[p + "_H"] = df.high[m].groupby(ngay[m]).max(); d[p + "_L"] = df.low[m].groupby(ngay[m]).min()
    d["or_H"] = df.high.groupby(ngay).first(); d["or_L"] = df.low.groupby(ngay).first()
    tr = np.maximum.reduce([d.high - d.low, (d.high - d.close.shift()).abs(), (d.low - d.close.shift()).abs()])
    d["adr"] = pd.Series(tr, index=d.index).rolling(20).mean()
    wk = d.index.to_period("W-SUN"); mo = d.index.to_period("M"); qu = d.index.to_period("Q"); yr = d.index.to_period("Y")
    def per(key):
        g = d.groupby(key).agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"))
        prev = g.shift(1)
        return g, prev
    W, Wp = per(wk); M, Mp = per(mo); Q, Qp = per(qu); Y, Yp = per(yr)
    Wpp = W.shift(2)
    dn = list(d.index); first_bar = pd.Series(np.arange(len(idx)), index=idx).groupby(ngay).first()
    first_hour = {}
    for hh in (1, 7, 9, 10, 16):
        m = idx.hour == hh
        first_hour[hh] = pd.Series(np.arange(len(idx))[m], index=ngay[m]).groupby(level=0).first()
    rows = []
    gap_chua = []  # (gia muc, ngay tao) gap ngày chưa lấp
    gap_tuan = None
    for i in range(1, len(dn)):
        t, pd_ = dn[i], d.iloc[i - 1]
        kb = int(first_bar[t]); P = (pd_.high + pd_.low + pd_.close) / 3; R = pd_.high - pd_.low
        w, m_, q, y = wk[i], mo[i], qu[i], yr[i]
        def add(ten, gia, k=kb):
            if gia is not None and np.isfinite(gia): rows.append((t, ten, float(gia), int(k)))
        cur = d.iloc[i]
        add("DO", cur.open); add("WO", W.loc[w, "open"] if wk[i - 1] != w else W.loc[w, "open"])
        add("MO", M.loc[m_, "open"]); add("QO", Q.loc[q, "open"]); add("YO", Y.loc[y, "open"])
        # chỉ dùng giá mở của kỳ (đã biết từ nến đầu kỳ ≤ kb)
        add("PDH", pd_.high); add("PDL", pd_.low); add("PDC", pd_.close); add("PD50", (pd_.high + pd_.low) / 2)
        add("PDO", pd_.open); add("PD_TWAP", pd_.twap); add("PD_F382", pd_.low + 0.382 * R); add("PD_F618", pd_.low + 0.618 * R)
        if i >= 2:
            p2 = d.iloc[i - 2]; add("P2DH", p2.high); add("P2DL", p2.low)
        for nm, (G, Gp) in (("W", (W, Wp)), ("M", (M, Mp)), ("Q", (Q, Qp)), ("Y", (Y, Yp))):
            key = {"W": w, "M": m_, "Q": q, "Y": y}[nm]
            if key in Gp.index and np.isfinite(Gp.loc[key, "high"]):
                g = Gp.loc[key]
                add(f"P{nm}H", g.high); add(f"P{nm}L", g.low)
                if nm in ("W", "M"):
                    add(f"P{nm}C", g.close); add(f"P{nm}50", (g.high + g.low) / 2)
                    Pp = (g.high + g.low + g.close) / 3
                    add(f"{nm}P", Pp); add(f"{nm}R1", 2 * Pp - g.low); add(f"{nm}S1", 2 * Pp - g.high)
                    if nm == "W":
                        add("WR2", Pp + g.high - g.low); add("WS2", Pp - (g.high - g.low)); add("PWO", g.open)
        add("P", P); add("R1", 2 * P - pd_.low); add("S1", 2 * P - pd_.high); add("R2", P + R); add("S2", P - R)
        add("R3", pd_.high + 2 * (P - pd_.low)); add("S3", pd_.low - 2 * (pd_.high - P))
        add("CAM_H3", pd_.close + R * 1.1 / 4); add("CAM_L3", pd_.close - R * 1.1 / 4)
        add("CAM_H4", pd_.close + R * 1.1 / 2); add("CAM_L4", pd_.close - R * 1.1 / 2)
        for p in PHIEN:
            add("PD_" + p + "_H", pd_[p + "_H"]); add("PD_" + p + "_L", pd_[p + "_L"])
        if np.isfinite(pd_.adr):
            add("DO+ADR/2", cur.open + pd_.adr / 2); add("DO-ADR/2", cur.open - pd_.adr / 2)
        G0, G1 = _luoi(cur.open)
        add("TRON_LON_TREN", np.ceil(cur.open / G0) * G0); add("TRON_LON_DUOI", np.floor(cur.open / G0) * G0)
        add("TRON_NHO_TREN", np.ceil(cur.open / G1) * G1); add("TRON_NHO_DUOI", np.floor(cur.open / G1) * G1)
        for k, pv in zz.items():
            ok = [p for p in pv if p["xn"] < kb]
            hi = [p for p in ok if p["loai"] == 1]; lo = [p for p in ok if p["loai"] == -1]
            if hi: add(f"ZZ{int(k)}_DINH", hi[-1]["gia"])
            if lo: add(f"ZZ{int(k)}_DAY", lo[-1]["gia"])
        # gap ngày chưa lấp (cập nhật bằng dữ liệu ngày trước, đã đóng)
        gap_chua = [(g, t0) for g, t0 in gap_chua if not (pd_.low <= g <= pd_.high)]
        if i >= 2:
            pp = d.iloc[i - 2]
            if abs(pd_.open - pp.close) > 0.25 * (d.adr.iloc[i - 2] if np.isfinite(d.adr.iloc[i - 2]) else np.inf) \
                    and not (pd_.low <= pp.close <= pd_.high):
                gap_chua.append((pp.close, dn[i - 1]))
        if gap_chua: add("GAP_CHUA_LAP", gap_chua[-1][0])
        if wk[i - 1] != w:  # ngày đầu tuần: gap tuần = đóng tuần trước
            gap_tuan = Wp.loc[w, "close"] if w in Wp.index else None
        if gap_tuan is not None:
            if pd_.low <= gap_tuan <= pd_.high and wk[i - 1] == w: gap_tuan = None
            else: add("GAP_TUAN", gap_tuan)
        # mốc trong ngày: biết sau khi phiên/nến xác định
        if kb + 1 < len(idx) and ngay[kb + 1] == t: add("OR_H", cur.or_H, kb + 1); add("OR_L", cur.or_L, kb + 1)
        if t in first_hour[7].index: add("MIDNIGHT_NY", o[first_hour[7][t]], int(first_hour[7][t]))
        if t in first_hour[10].index: add("LONDON_MO", o[first_hour[10][t]], int(first_hour[10][t]))
        if t in first_hour[16].index:
            k16 = int(first_hour[16][t]); add("NY_MO", o[k16], k16)
            add("AU_H", cur["AU_H"], k16); add("AU_L", cur["AU_L"], k16)
        if t in first_hour[9].index:
            k9 = int(first_hour[9][t])
            add("A_H", cur["A_H"], k9); add("A_L", cur["A_L"], k9); add("A_MID", (cur["A_H"] + cur["A_L"]) / 2, k9)
            add("A_H+100%", cur["A_H"] + (cur["A_H"] - cur["A_L"]), k9); add("A_L-100%", cur["A_L"] - (cur["A_H"] - cur["A_L"]), k9)
    return pd.DataFrame(rows, columns=["ngay", "ten", "gia", "kb"])
