# -*- coding: utf-8 -*-
"""Test cho nhan/tai_khoan.py bang nen TONG HOP nho (tinh tay duoc)."""
import numpy as np
import pandas as pd

from nhan import tai_khoan as TK


def bars(rows):
    return pd.DataFrame(rows, columns=["open", "high", "low", "close"])


def test_mot_ro_cham_tp_tru_spread_khong_xet_tp_o_nen_vao():
    # nen0: vao 100 (high 120 nhung KHONG xet TP o nen vao); nen1 high 106 -> TP 105,5 cham
    b = bars([[100, 120, 99, 100], [100, 106, 99, 104], [104, 104, 103, 104]])
    kq = TK.chay(b, [TK.LenhVao("a", 0, 100.0)], TK.QuanLi(tp_diem=5.5, spread_diem=1.0, swap_nam=0.0))
    nk = kq["nhat_ky"]
    assert len(nk) == 1 and nk.boi[0] == "tp" and nk.dong[0] == 1
    assert abs(nk.lai_diem[0] - (5.5 - 1.0)) < 1e-9
    assert abs(kq["tong_diem"] - 4.5) < 1e-9


def test_dca_ha_gia_von_va_tp_tinh_tu_gia_tb():
    # vao 100, DCA moi -1% (99) lot 1 -> gia TB 99,5 ; TP = 105 ; nen2 high 105 -> dong
    b = bars([[100, 100, 100, 100], [100, 100, 98.9, 99.2], [99.2, 105.2, 99.0, 105.0]])
    ql = TK.QuanLi(tp_diem=5.5, dca_buoc_pct=0.01, dca_toi_da=1, spread_diem=0.0, swap_nam=0.0)
    kq = TK.chay(b, [TK.LenhVao("a", 0, 100.0)], ql)
    nk = kq["nhat_ky"].iloc[0]
    assert nk.so_tang == 2 and nk.boi == "tp"
    # lai: (105 - 100) + (105 - 99) = 11 diem tren 2 lot ; chia lot dau (1.0) = 11
    assert abs(nk.lai_diem - 11.0) < 1e-9


def test_go_cheo_dong_ro_ket_bang_lai_noi_cua_ro_khac():
    # ro A vao 100 va ket; ro B vao 90 (qua thap) -> sau do gia ve 100: B lai noi +10 chua cham TP(+55), A hoa. dung TP rat lon de khong tu dong
    b = bars([[100, 100, 100, 100], [100, 100, 90, 90], [90, 100.5, 90, 100.0], [100, 100, 100, 100]])
    luong = [TK.LenhVao("a", 0, 110.0), TK.LenhVao("b", 1, 90.0)]
    ql = TK.QuanLi(tp_diem=50.0, go_cheo=True, go_nguong_diem=0.0, spread_diem=0.0, swap_nam=0.0)
    # A vao 110, o nen 2 close 100 -> -10 ; B vao 90, close 100 -> +10  => tong 0 >= 0 -> dong cap
    kq = TK.chay(b, luong, ql)
    nk = kq["nhat_ky"]
    assert set(nk.boi) == {"go_cheo"} and len(nk) == 2
    assert abs(kq["tong_diem"]) < 1e-9


def test_khong_go_cheo_khi_tong_van_am():
    b = bars([[100, 100, 100, 100], [100, 100, 90, 90], [90, 100.5, 90, 95.0]])
    luong = [TK.LenhVao("a", 0, 110.0), TK.LenhVao("b", 1, 90.0)]
    ql = TK.QuanLi(tp_diem=50.0, go_cheo=True, go_nguong_diem=0.0, spread_diem=0.0, swap_nam=0.0)
    kq = TK.chay(b, luong, ql)
    assert (kq["nhat_ky"].boi == "mo").all()          # A -15, B +5 -> khong du -> van mo


def test_swap_tinh_tu_moc_17h_ny_va_thu_sau_x3():
    idx = pd.date_range("2025-03-06 15:00", periods=4, freq="h", tz="America/New_York")   # thu Nam 15,16,17,18
    r = TK.rollover_tu_ny(idx)
    assert list(r) == [0.0, 0.0, 1.0, 0.0]
    fri = pd.DatetimeIndex([pd.Timestamp("2025-03-07 16:00", tz="America/New_York"),
                            pd.Timestamp("2025-03-09 18:00", tz="America/New_York")])          # thu Sau 16h roi CN 18h
    assert list(TK.rollover_tu_ny(fri)) == [0.0, 3.0]
    b = bars([[100, 100, 100, 100]] * 4)
    kq = TK.chay(b, [TK.LenhVao("a", 0, 100.0)], TK.QuanLi(tp_diem=999, spread_diem=0.0, swap_nam=0.365), rollover=r)
    # 1 lot * gia 100 * 0,365/365 * 1 = 0,1 diem
    assert abs(kq["so_du"] + 0.1) < 1e-9
