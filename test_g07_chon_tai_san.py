"""G07 (G-b chon tai san): ke hoach dong bang + swap gia dinh + nhan gia giu % bien dong."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent / "hieu_chuan"))
import g07_chon_tai_san as g  # noqa: E402


def test_ke_hoach_khop_ban_dong_bang():
    assert g.bam_ke_hoach() == json.loads(g.KE_HOACH_FILE.read_text())["sha256_16"] == "eddb7e748b7924e9"


def test_swap_khop_so_do_thang_8_2026():
    t = pd.Period("2026-08", freq="M")
    mua, ban = g.bang_swap("XAUUSD")
    assert abs(mua[t] + 0.04477) < 1e-9 and abs(ban[t] - 0.03709) < 1e-9
    mua, ban = g.bang_swap("EURGBP")
    assert abs(mua[t] + 0.0305) < 1e-9 and abs(ban[t] - 0.00439) < 1e-9


def test_swap_chi_so_ca_hai_chieu_mat_markup():
    mua, ban = g.bang_swap("NSXUSD")
    assert np.allclose((mua + ban).dropna(), -0.05)


def test_bien_do_ngay_bo_ngay_it_nen():
    idx = pd.date_range("2020-01-06", periods=1440 * 2, freq="1min")
    df = pd.DataFrame({"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0}, index=idx)
    df.loc[idx[:1440], "high"] = 1.01
    df = pd.concat([df, pd.DataFrame({"open": 1, "high": 9, "low": 0, "close": 1},
                                     index=pd.date_range("2020-01-08", periods=10, freq="1min"))])
    r = g.bien_do_ngay(df)
    assert abs(r[2020] - 0.005) < 1e-12        # trung vi (0,01; 0) - ngay 10 nen bi bo
