import numpy as np, pandas as pd, v18

def _d(n=400, seed=0):
    idx = pd.date_range("2024-01-01", periods=n, freq="h"); r = np.random.default_rng(seed)
    c = 1.1 + np.cumsum(r.normal(0, 5e-4, n)); o = np.r_[c[0], c[:-1]]
    return pd.DataFrame({"open": o, "high": np.maximum(o, c) + 2e-4, "low": np.minimum(o, c) - 2e-4, "close": c,
                         "spread_open": 1e-4, "so_tick": 1}, index=idx)

def test_lenh_co_phi_spread_khi_gia_dung_yen():
    d = _d(); d[["open", "high", "low", "close"]] = 1.1; atr = np.full(len(d), 1e-3)
    d.loc[d.index[100], "close"] = 1.2; d.loc[d.index[100], "high"] = 1.2   # pha vo gia
    L = v18.mo_phong(d, atr, "B3", "GIO3", cap="eurusd")
    assert L and L[0][1] < 0          # mua dinh roi gia ve 1.1 + tra spread -> lo

def test_hedge_khong_vuot_von_khi_chay():
    d = _d(3000, 1); atr = np.full(len(d), 1e-3)
    ck, eq = v18.hedge(d, atr, "eurusd")
    assert len(eq) == len(d) and np.isfinite(eq).all()
