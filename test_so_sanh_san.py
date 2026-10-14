import pandas as pd
import phi_xm_that as X
import so_sanh_san as S


def test_swap_tester_vs_day_du():
    assert X.swap_dem_ty_le("EURUSD#", 1, 1.1, "nhu_tester") == 0.0
    assert X.swap_dem_ty_le("EURUSD#", 1, 1.1, "day_du") < 0
    assert X.swap_dem_ty_le("US500Cash#", 1, 5000, "nhu_tester") == X.swap_dem_ty_le("US500Cash#", 1, 5000, "day_du") < 0


def test_spread_gio_00h_dat_hon():
    assert X.spread_gio_bps_xm("GER40Cash#", 0) > X.spread_gio_bps_xm("GER40Cash#", 12)


def test_so_dem_thu_tu_x3():
    assert S.so_dem(pd.Timestamp("2026-10-12"), pd.Timestamp("2026-10-15"), 2) == 1 + 1 + 3


def test_thong_ke():
    q = S.thong_ke([(pd.Timestamp("2020-01-01"), 0.01), (pd.Timestamp("2020-01-02"), -0.005)])
    assert q["so_lenh"] == 2 and q["pf"] == 2.0 and q["maxdd_usd"] == 50.0


def test_mac_dinh_standard():
    assert X.TAI_KHOAN_MAC_DINH == "Standard"
    assert X.ho_so_xm("EURUSD#") == ("EURUSD", False)
    assert X.ho_so_xm("US500Cash#")[1] is True
    v, uoc = X.spread_gio_bps_tk("EURUSD#", 10)
    assert not uoc and v > X.spread_gio_bps_xm("EURUSD#", 10)
    assert X.swap_dem_tk("EURUSD#", 1, 1.1, "mien_swap") < 0
