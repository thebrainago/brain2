import numpy as np, pandas as pd
from nhan.song_zigzag_atr import zigzag, atr, song


def _gia(n=3000, seed=1):
    r = np.random.default_rng(seed)
    c = 100 + np.cumsum(r.normal(0, 1, n))
    h = c + r.uniform(0, 1, n); l = c - r.uniform(0, 1, n)
    return h, l, c


def test_khong_nhin_truoc():
    h, l, c = _gia()
    a = atr(h, l, c)
    full = zigzag(h, l, a, 2.0)
    for t in (500, 1234, 2000, 2999):
        cut = zigzag(h[:t + 1], l[:t + 1], a[:t + 1], 2.0)
        assert cut == [p for p in full if p["xn"] <= t]


def test_xac_nhan_sau_du_nguong():
    h, l, c = _gia(seed=7)
    a = atr(h, l, c)
    for p in zigzag(h, l, a, 3.0):
        i = p["xn"]
        assert i > p["idx"]
        if p["loai"] == 1:
            assert p["gia"] - l[i] >= 3.0 * a[i] - 1e-9
            assert p["gia"] == h[p["idx"]:i + 1].max()
        else:
            assert h[i] - p["gia"] >= 3.0 * a[i] - 1e-9
            assert p["gia"] == l[p["idx"]:i + 1].min()


def test_xen_ke_dinh_day_va_song():
    h, l, c = _gia(seed=3)
    p = zigzag(h, l, atr(h, l, c), 1.0)
    assert all(p[j]["loai"] != p[j + 1]["loai"] for j in range(len(p) - 1))
    df = pd.DataFrame(dict(high=h, low=l, close=c), index=pd.RangeIndex(len(c)))
    w, _, _ = song(df, 2.0)
    assert len(w) > 10 and (w.diem > 0).all() and set(w.loai) <= {"day", "hoi"}
