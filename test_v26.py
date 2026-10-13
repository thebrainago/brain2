import numpy as np
import pandas as pd
import v26


def _d(n=900, seed=1):
    r = np.random.default_rng(seed); c = 1 + np.cumsum(r.normal(0, 0.005, n)); o = np.r_[c[0], c[:-1]]
    return pd.DataFrame({"open": o, "high": np.maximum(o, c) + 0.002, "low": np.minimum(o, c) - 0.002, "close": c,
                         "spread_open": 0.0, "so_tick": 1}, index=pd.bdate_range("2010-01-01", periods=n))


def test_khong_nhin_truoc():
    d = _d(); sp = np.zeros(len(d))
    for kieu in ("KHONG", "XU_HUONG", "VOL_THAP", "DANH_MUC"):
        A = v26.lenh(d, "MRZ", kieu, sp); B = v26.lenh(d.iloc[:600], "MRZ", kieu, sp[:600])
        a = [x[:3] for x in A if x[0] < d.index[500]]; b = [x[:3] for x in B if x[0] < d.index[500]]
        assert a == b


def test_spread_00h_dat_hon_02h():
    for t in ("GBPUSD_X", "AUDUSD_X"):
        assert v26.sp_gio(t, 0) > 2 * v26.sp_gio(t, 2)
