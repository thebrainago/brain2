import numpy as np, pandas as pd, v19

def _d(n=600):
    idx = pd.date_range("2024-01-01", periods=n, freq="h")
    return pd.DataFrame({"open": 1.1, "high": 1.1005, "low": 1.0995, "close": 1.1, "spread_open": 1e-4, "so_tick": 1}, index=idx)

def test_sl_truoc_khi_cung_nen():
    d = _d(); atr = np.full(len(d), 1e-3); tin = np.zeros(len(d)); tin[100] = 1
    d.iloc[102, d.columns.get_loc("high")] = 1.2; d.iloc[102, d.columns.get_loc("low")] = 1.0   # cham ca SL va TP
    L = v19.chay(d, tin, "TP", atr)
    assert L[0][1] < 0

def test_moi_thoat_chay_duoc():
    d = _d(); atr = np.full(len(d), 1e-3); tin = np.zeros(len(d)); tin[100] = -1
    for th in v19.THOAT: assert v19.chay(d, tin, th, atr)
