# -*- coding: utf-8 -*-
"""ZigZag theo bội số ATR (KHÔNG nhìn trước) + đo tính chất sóng.

Đỉnh/đáy chỉ được XÁC NHẬN ở nến i khi giá đã đảo chiều từ cực trị ≥ k·ATR14(i).
Mọi hàm chỉ dùng dữ liệu ≤ nến đang xét. Dựng lại công trình ZigZag (14/10/2026).
"""
import numpy as np
import pandas as pd

# Phí XM Ultra Low (hậu tố #): spread trung vị H1, bps — chép từ phi_xm_that.BANG ở commit HEAD (không import bản WIP).
PHI_UL = {"US500": 1.00, "US100": 0.97, "GER40": 0.95, "XAUUSD": 0.65, "DAU": 3.99,
          "EURUSD": 0.72, "GBPUSD": 0.60, "USDJPY": 0.52, "USDCHF": 1.33, "AUDUSD": 1.83,
          "NZDUSD": 3.10, "USDCAD": 1.16}
TRUOT_BPS = 1.0  # trượt khứ hồi


def atr(h, l, c, n=14):
    h, l, c = map(np.asarray, (h, l, c))
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum.reduce([h - l, np.abs(h - pc), np.abs(l - pc)])
    return pd.Series(tr).ewm(alpha=1 / n, adjust=False).mean().values


def zigzag(h, l, a, k):
    """Trả list dict pivot: idx (nến cực trị), xn (nến xác nhận), gia, loai (+1 đỉnh, -1 đáy).
    Chỉ dùng h[:i+1], l[:i+1], a[i] tại nến i."""
    h, l, a = map(np.asarray, (h, l, a))
    piv = []
    d = 0
    mx, mxi, mn, mni = h[0], 0, l[0], 0
    for i in range(1, len(h)):
        if not np.isfinite(a[i]) or a[i] <= 0:
            continue
        thr = k * a[i]
        if d == 0:
            if h[i] > mx: mx, mxi = h[i], i
            if l[i] < mn: mn, mni = l[i], i
            if h[i] - mn >= thr and mni < i:
                piv.append(dict(idx=mni, xn=i, gia=mn, loai=-1)); d = 1; mx, mxi = h[i], i
            elif mx - l[i] >= thr and mxi < i:
                piv.append(dict(idx=mxi, xn=i, gia=mx, loai=1)); d = -1; mn, mni = l[i], i
        elif d == 1:  # chân đang đi lên, tìm đỉnh
            if h[i] > mx: mx, mxi = h[i], i
            elif mx - l[i] >= thr:
                piv.append(dict(idx=mxi, xn=i, gia=mx, loai=1)); d = -1; mn, mni = l[i], i
        else:
            if l[i] < mn: mn, mni = l[i], i
            elif h[i] - mn >= thr:
                piv.append(dict(idx=mni, xn=i, gia=mn, loai=-1)); d = 1; mx, mxi = h[i], i
    return piv


def song(df, k, ma=200):
    """Bảng sóng giữa các pivot liên tiếp. Phân loại đẩy/hồi theo MA200 tại nến bắt đầu sóng."""
    h, l, c = df.high.values, df.low.values, df.close.values
    a = atr(h, l, c)
    m = pd.Series(c).rolling(ma).mean().values
    p = zigzag(h, l, a, k)
    rows = []
    for j in range(len(p) - 1):
        s, e = p[j], p[j + 1]
        if not np.isfinite(m[s["idx"]]):
            continue
        huong = 1 if e["gia"] > s["gia"] else -1
        xu = 1 if c[s["idx"]] > m[s["idx"]] else -1
        bd = abs(e["gia"] - s["gia"])
        rows.append(dict(i0=s["idx"], i1=e["idx"], xn=e["xn"], t0=df.index[s["idx"]], huong=huong, xu=xu,
                         loai="day" if huong == xu else "hoi", diem=bd, pct=100 * bd / s["gia"],
                         atr=bd / a[s["idx"]], nen=e["idx"] - s["idx"]))
    w = pd.DataFrame(rows)
    if len(w):
        tl = [np.nan]
        for j in range(1, len(w)):
            tl.append(w.diem[j] / w.diem[j - 1] if (w.loai[j] == "hoi" and w.loai[j - 1] == "day") else np.nan)
        w["ti_le_hoi"] = tl
    return w, p, a


def phan_vi(x, q=(50, 70, 90)):
    x = np.asarray(pd.Series(x).dropna())
    return {f"p{v}": (round(float(np.percentile(x, v)), 4) if len(x) else None) for v in q} | {"n": int(len(x))}


def tom_tat(w):
    out = {}
    for loai in ("day", "hoi"):
        s = w[w.loai == loai]
        out[loai] = {c: phan_vi(s[c]) for c in ("diem", "pct", "atr", "nen")}
    out["ti_le_hoi"] = phan_vi(w.ti_le_hoi)
    return out
