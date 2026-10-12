import numpy as np, pandas as pd, v20

def test_c1_khong_nhin_truoc():
    idx = pd.date_range("2024-01-01", periods=800, freq="h"); r = np.random.default_rng(0)
    c = 1 + np.cumsum(r.normal(0, 1e-3, 800)); d = pd.DataFrame({"open": c, "high": c + 1e-3, "low": c - 1e-3, "close": c}, index=idx)
    atr = np.full(800, 2e-3)
    a = v20.c1(*v20.dac_trung(d, atr)[:4])
    d2 = d.copy(); d2.iloc[700:] *= 1.5          # doi tuong lai -> qua khu khong doi
    b = v20.c1(*v20.dac_trung(d2, atr)[:4])
    assert np.array_equal(np.nan_to_num(a[:700], nan=-1), np.nan_to_num(b[:700], nan=-1))
