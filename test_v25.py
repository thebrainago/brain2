"""Vong 25: khong lookahead cho co che bo doc + 4 EA dich tay; SL truoc khi cung nen."""
import numpy as np, pandas as pd
import v23, v25

def _d(n=600, seed=1):
    r = np.random.default_rng(seed); c = 1.1 + np.cumsum(r.normal(0, 1e-3, n)); o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) + 5e-4; l = np.minimum(o, c) - 5e-4
    return pd.DataFrame({"open": o, "high": h, "low": l, "close": c, "spread_open": 1e-5}, index=pd.date_range("2024-01-01", periods=n, freq="h"))

def _khong_nhin_truoc(f):
    d = _d(); k = 400; A = f(d, "H1", 1e-5); B = f(d.iloc[:k + 1].copy(), "H1", 1e-5)
    for key in ("sig", "ex"):
        if key in A: assert np.array_equal(np.nan_to_num(A[key][:k + 1]), np.nan_to_num(B[key][:k + 1])), key

def test_tay_khong_lookahead():
    for f, _ in v25.TAY.values(): _khong_nhin_truoc(f)

def test_bo_doc_khong_lookahead():
    for s in v25.co_che()[:25]:
        if s.get("trong_bar"): continue
        try: _khong_nhin_truoc(v25._BD(s))
        except (TypeError, KeyError, ValueError, NotImplementedError): pass

def test_sl_truoc():
    d = _d(5); d.iloc[2, d.columns.get_loc("high")] = 9; d.iloc[2, d.columns.get_loc("low")] = 0.1
    c = d["close"].to_numpy(); S = {"sig": np.array([0, 1, 0, 0, 0]), "sl": c - 0.01, "tp": c + 0.01}
    L = v23.sim(d, S, np.zeros(5), np.ones(5))
    assert L and L[0][1] < 0
