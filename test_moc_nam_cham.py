import numpy as np, pandas as pd
from nhan.moc_nam_cham import moc


def _h1(n=24 * 120, seed=2):
    r = np.random.default_rng(seed)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h")
    idx = idx[idx.dayofweek < 5]
    c = 100 + np.cumsum(r.normal(0, 0.2, len(idx)))
    o = np.r_[c[0], c[:-1]]
    return pd.DataFrame(dict(open=o, high=np.maximum(o, c) + r.uniform(0, .1, len(c)),
                             low=np.minimum(o, c) - r.uniform(0, .1, len(c)), close=c), index=idx)


def test_khong_nhin_truoc():
    df = _h1()
    full = moc(df)
    for T in (500, 1111, 1600):
        cut = moc(df.iloc[:T + 1])
        a = full[full.kb <= T].set_index(["ngay", "ten"]).sort_index()
        b = cut[cut.kb <= T].set_index(["ngay", "ten"]).sort_index()
        common = a.index.intersection(b.index)
        assert len(common) == len(a) == len(b)
        assert np.allclose(a.loc[common, "gia"], b.loc[common, "gia"])


def test_du_80_moc():
    assert moc(_h1()).ten.nunique() >= 75
