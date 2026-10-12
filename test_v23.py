import numpy as np, pandas as pd, v23


def _d(c, f="1h"):
    c = np.asarray(c, float); idx = pd.date_range("2024-01-02", periods=len(c), freq=f)
    return pd.DataFrame({"open": c, "high": c + 1e-4, "low": c - 1e-4, "close": c, "spread_open": 0.0}, index=idx)


def test_sl_truoc_cung_nen():
    d = _d(np.ones(50)); d.iloc[11, 1] = 1.05; d.iloc[11, 2] = 0.95
    S = {"sig": np.r_[np.zeros(9), 1, np.zeros(40)].astype(int), "sl": np.full(50, 0.99), "tp": np.full(50, 1.01)}
    L = v23.sim(d, S, np.zeros(50), np.full(50, 0.01))
    assert L[0][1] < 0


def test_pivot_khong_nhin_truoc():
    h = np.r_[np.arange(10), 20, np.arange(10)[::-1]].astype(float)
    ph, _ = v23.pivots(h, h, 5)
    assert not ph[:15].any() and ph[15]          # pivot o 10 chi biet tai 15


def test_htf_chi_dung_nen_da_dong():
    d = _d(np.arange(48) + 1.0, "1h")
    v = v23.htf_ffill(d, "1D", lambda g: g["high"].to_numpy())
    assert np.isnan(v[:24]).all() and v[24] == d["high"].iloc[:24].max()


def test_supertrend_lat():
    c = np.r_[np.linspace(2, 1, 60), np.linspace(1, 2, 60)]
    dr, _ = v23.supertrend(c + 0.01, c - 0.01, c, 10, 2.0)
    assert dr[50] < 0 and dr[-1] > 0
