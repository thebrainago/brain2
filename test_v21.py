import numpy as np, pandas as pd, v21

def test_cham_lai_dem_dung():
    c = np.r_[np.full(50, 1.0), 1.1, 1.05, 1.0, np.full(60, 1.0)]; h = c + 0.001; l = c - 0.001
    ema = np.full(len(c), 1.0); atr = np.full(len(c), 0.02)
    ty, tg, n = v21.cham_lai(h, l, c, ema, atr, 4.0, 10)
    assert n == 1 and ty == 1.0 and tg == 2

def test_mr_tp_tai_ema():
    idx = pd.date_range("2024-01-01", periods=300, freq="h")
    c = np.full(300, 1.0); c[250] = 1.05
    d = pd.DataFrame({"open": c, "high": c + 1e-4, "low": c - 1e-4, "close": c, "spread_open": 0.0}, index=idx)
    d.iloc[251, 0] = 1.05; d.iloc[251, 1] = 1.0501; d.iloc[251, 2] = 1.0499; d.iloc[251, 3] = 1.05
    ema = np.full(300, 1.0); atr = np.full(300, 0.01); sig = np.zeros(300, int); sig[250] = -1
    L = v21.chay(d, ema, atr, sig, "MR", 4.0)
    assert L and L[0][1] > 0.04
