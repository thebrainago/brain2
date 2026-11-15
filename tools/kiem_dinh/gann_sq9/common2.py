# -*- coding: utf-8 -*-
"""Hàm dùng chung cho Test A (giá) và Test B (thời gian) – Gann Sq9 từ đỉnh/đáy lớn."""
import numpy as np, pandas as pd

INSTR = {  # mã: (file, ngày bắt đầu). Vàng GC=F trước 2008 có ~35% nến daily H=L (dữ liệu hỏng) -> dùng từ 2008
    "GC=F": ("data_GCF_1d.pkl", "2008-01-01"),
    "ES=F": ("data_ESF_1d.pkl", "2000-01-01"),
    "^GSPC": ("data_GSPC_1d.pkl", "2000-01-01"),
}
SPLIT = pd.Timestamp("2016-01-01")   # trong mẫu < 2016 <= ngoài mẫu


def load(tk, base="."):
    f, start = INSTR[tk]
    d = pd.read_pickle(f"{base}/{f}").dropna(subset=["Open", "High", "Low", "Close"])
    d = d[d.index >= start]
    d.index = pd.to_datetime(d.index).tz_localize(None).normalize()
    return d


def atr_rma(h, l, c, n=14):
    pc = np.r_[np.nan, c[:-1]]
    tr = np.nanmax(np.vstack([h - l, np.abs(h - pc), np.abs(l - pc)]), axis=0)
    out = np.full(len(c), np.nan); out[n - 1] = tr[:n].mean()
    for i in range(n, len(c)): out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def pivots(src, left, right, high=True):
    """Chỉ số pivot (đỉnh nếu high) – cần left nến trái, right nến phải. Xác nhận tại p+right."""
    n = len(src); out = []
    for p in range(left, n - right):
        w = src[p - left:p + right + 1]; v = src[p]
        if high:
            if v >= w.max() and v > src[p - left:p].max(): out.append(p)
        else:
            if v <= w.min() and v < src[p - left:p].min(): out.append(p)
    return np.array(out, dtype=int)


def major_anchors(d):
    """Danh sách neo lớn: dict(type, kind H/L, p = nến pivot, conf = nến xác nhận, price)."""
    h, l = d.High.values, d.Low.values; n = len(d); A = []
    for L in (20, 60):
        for kind, src in (("H", h), ("L", l)):
            for p in pivots(src, L, L, kind == "H"):
                A.append(dict(type=f"piv{L}{kind}", kind=kind, p=p, conf=p + L, price=src[p]))
    # ATH: pivot 20/20 là đỉnh cao nhất kể từ đầu dữ liệu tại thời điểm đó
    runmax = np.maximum.accumulate(h)
    for p in pivots(h, 20, 20, True):
        if h[p] >= runmax[p] and p >= 250:
            A.append(dict(type="ATH", kind="H", p=p, conf=p + 20, price=h[p]))
    # Đỉnh/đáy năm: biết vào nến đầu năm sau
    yr = d.index.year.values
    for y in np.unique(yr)[:-1]:
        ix = np.flatnonzero(yr == y); nxt = np.flatnonzero(yr == y + 1)
        if len(ix) < 200 or not len(nxt): continue
        ph = ix[np.argmax(h[ix])]; pl = ix[np.argmin(l[ix])]
        A.append(dict(type="yearH", kind="H", p=ph, conf=nxt[0], price=h[ph]))
        A.append(dict(type="yearL", kind="L", p=pl, conf=nxt[0], price=l[pl]))
    return [a for a in A if a["conf"] < n - 1]


def sq9(anchor, ang, side):
    r = np.sqrt(anchor) + side * ang / 180.0
    return np.where(r > 0, r * r, np.nan)


def bh_fdr(p):
    """Benjamini–Hochberg q-values."""
    p = np.asarray(p, float); m = len(p); o = np.argsort(p)
    q = np.empty(m); prev = 1.0
    for rank, i in reversed(list(enumerate(o, 1))):
        prev = min(prev, p[i] * m / rank); q[i] = prev
    return q
