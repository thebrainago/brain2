# -*- coding: utf-8 -*-
"""Sai so mo phong lam dep ket qua (ra soat 18/10/2026). Moi test la mot loi THAT da do duoc:

1. Chay tai khoan bi ghi la thang (bar chay mang log 0).
2. Lenh BAN duoc tang ~ phuong sai moi bar (cong don log).
3. SL bi nhay qua (gap) van khop o gia SL.
4. Stress "chi phi x2" khong doi gi (sai ten khoa; spread theo nam triet tieu he so).
5. Spread gio rollover khong bao gio bi tinh.
6. Lenh trong ngay tra phi qua dem du khong qua nua dem; lenh H1 qua dem chi tra 2/24 dem.
"""
import numpy as np
import pandas as pd

from nhan import chi_phi as CP, do_luong as DO, mo_phong as MP, sang_loc as SL


def _df(gia, freq="D", bat_dau="2020-01-06"):
    gia = np.asarray(gia, float)
    idx = pd.date_range(bat_dau, periods=len(gia), freq=freq)
    return pd.DataFrame({"open": gia, "high": gia * 1.001, "low": gia * 0.999, "close": gia}, index=idx)


def _cp0(ma="US500CASH", **kw):
    return CP.MoHinhChiPhi(ma=ma, do_tin="DO", **kw)


def test_chay_tai_khoan_khong_duoc_ghi_la_thang():
    gia = np.r_[np.linspace(100, 160, 60), 96.0, np.linspace(96, 120, 40)]
    kq = MP.chay(_df(gia), np.ones(len(gia)), _cp0(), don_bay=3.0)
    assert kq.chay_tai_khoan
    cs = DO.chi_so(kq.loi, kq.index)
    assert cs["tong_lai_pct"] <= -99.0 and cs["max_dd_pct"] <= -99.0


def test_ban_khong_duoc_tang_phuong_sai():
    rng = np.random.default_rng(1)
    r = rng.normal(0, 0.011, 2000)
    gia = 100 * np.exp(np.cumsum(r))
    df = _df(gia)
    kq = MP.chay(df, -np.ones(len(gia)), _cp0())          # mac dinh "tu_dong"
    ra = np.expm1(MP._loi_suat_tien(df))
    ky_vong = np.sum(np.log1p(-ra[1:]))                   # ban ca von, can bang moi bar (so hoc)
    assert abs(np.sum(kq.loi) - ky_vong) < 1e-9
    kq_log = MP.chay(df, -np.ones(len(gia)), _cp0(), gop="log")
    assert np.sum(kq_log.loi) - ky_vong > 0.1              # ban cu: ~ sum r^2 lai "tu tren troi"


def test_sl_bi_gap_khop_o_open_khong_o_sl():
    gia = [100.0, 100.0, 100.0, 90.0, 90.0, 90.0]
    df = _df(gia)
    th = np.zeros(len(gia))
    th[0] = 1.0                                            # vao mua open bar 1 = 100
    kq = MP.chay_tpsl(df, th, tp_frac=0.10, sl_frac=0.02, cp=_cp0())
    assert abs(np.exp(np.sum(kq.loi)) - 0.90) < 1e-3       # lo ca gap (-10 %), khong phai -2 %


def test_stress_chi_phi_x2_that_su_nhan_doi():
    cp = _cp0(spread_frac_chung=1e-4, spread_frac_theo_gio={10: 1e-4, 0: 8e-4}, truot_gia_frac=2e-5,
              phi_nam_mua=0.05, phi_nam_ban=-0.01, spread_frac_theo_nam={2020: 1.5e-4})
    cp2 = SL._nhan_doi_chi_phi(cp)
    idx = pd.date_range("2020-03-02 10:00", periods=3, freq="h")
    assert np.allclose(cp2.spread_mang(idx), 2 * cp.spread_mang(idx))
    assert cp2.truot_gia_frac == 2 * cp.truot_gia_frac
    assert cp2.phi_nam_mua == 0.10 and cp2.phi_nam_ban == 0.0  # khoan nhan bi bo, khong nhan doi


def test_spread_gio_rollover_duoc_do_va_bar_ngay_lay_gio_khop():
    idx = pd.date_range("2024-01-01", periods=24 * 400, freq="h")
    idx = idx[idx.dayofweek < 5]
    gia = np.full(len(idx), 1.1)
    sp = np.where(np.isin(idx.hour, [23, 0]), 100.0, 10.0)    # point; rollover rong 10 lan
    df = pd.DataFrame({"open": gia, "high": gia, "low": gia, "close": gia, "spread": sp}, index=idx)
    theo_gio, chung, _ = CP.do_spread("EURUSD", df)
    assert abs(theo_gio[0] / chung - 10.0) < 1e-9 and abs(theo_gio[23] / chung - 10.0) < 1e-9
    cp = _cp0("EURUSD", spread_frac_theo_gio=theo_gio, spread_frac_chung=chung)
    h1 = pd.DatetimeIndex(["2024-03-04 00:00", "2024-03-04 01:00", "2024-03-04 10:00"])
    assert cp.spread_mang(h1)[0] > 9 * cp.spread_mang(h1)[2]         # bar H1 00:00 tra spread rollover
    d1 = pd.date_range("2024-03-04", periods=5, freq="D")
    assert np.allclose(cp.spread_mang(d1), theo_gio[CP.GIO_KHOP_NGAY])  # bar ngay: gio khop that


def test_phi_qua_dem_theo_nua_dem_nhu_mt5():
    cp = _cp0("US500CASH", phi_nam_mua=3.65)                 # 1 % moi dem cho de dem
    assert cp.kieu_qua_dem == "nua_dem"
    trong_ngay = pd.date_range("2024-03-05 10:00", periods=6, freq="h")   # thu 3, khong qua nua dem
    assert np.sum(cp.phi_giu_mang(trong_ngay, np.ones(6))) == 0.0
    qua_dem = pd.date_range("2024-03-05 22:00", periods=4, freq="h")      # 22h -> 01h: qua MOT nua dem
    assert abs(np.sum(cp.phi_giu_mang(qua_dem, np.ones(4))) - 0.01) < 1e-12
