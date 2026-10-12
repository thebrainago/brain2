import numpy as np, pandas as pd, v22


def _d(n=200, f="5min"):
    idx = pd.date_range("2024-01-02", periods=n, freq=f); c = np.full(n, 1.0)
    return pd.DataFrame({"open": c, "high": c + 1e-4, "low": c - 1e-4, "close": c, "spread_open": 0.0}, index=idx)


def test_sl_truoc_khi_cung_nen():
    d = _d(); d.iloc[101, 1] = 1.02; d.iloc[101, 2] = 0.98
    sig = np.zeros(200, int); sig[99] = 1; atr = np.full(200, 0.01)
    L = v22.chay(d, sig, "TP", atr, np.zeros(200))
    assert L[0][1] < 0  # SL va TP cung nen -> tinh SL


def test_mtf_khong_nhin_truoc():
    d = _d(600, "5min"); d["close"] = np.r_[np.full(300, 1.0), np.linspace(1, 2, 300)]
    h = v22.mtf_huong(d, "M5")
    # nen M30 bat dau tang tu 300 (25h00) -> huong chi xuat hien tu nen M30 ke tiep tro di
    assert (h[:306] <= 0).all()


def test_phi_truoc_sau():
    L = [(pd.Timestamp("2024-01-01") + pd.Timedelta(days=i), 0.001, 1, 3, 1.0, 1) for i in range(40)]
    g = v22.ket_qua(L, pd.Timestamp("2024-01-21"), 0, 1e-4, False, 0)
    m = v22.ket_qua(L, pd.Timestamp("2024-01-21"), 0, 1e-4, True, 1.0)
    assert g["tb_bps"] > m["tb_bps"] and abs(g["tb_bps"] - m["tb_bps"] - (2 + 0.025 / 365 * 1e4)) < 1e-6
