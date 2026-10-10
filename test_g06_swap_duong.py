# -*- coding: utf-8 -*-
"""G06 (11/10/2026): swap tuy chon trong `luoi_duong.chay_duong`."""
import pandas as pd
import pytest

from nhan.luoi import ThamSo
from nhan.luoi_duong import chay_duong


def _df(times, p=1.0):
    idx = pd.DatetimeIndex(pd.to_datetime(times))
    return pd.DataFrame({"open": p, "high": p, "low": p, "close": p}, index=idx)


TS = ThamSo(buoc=50, tp=50, tran_tang=3, che_do="mua", lot=0.01)


def test_mac_dinh_khong_swap_giong_het():
    df = _df(["2026-10-07 23:00", "2026-10-08 01:00", "2026-10-08 02:00"])
    a = chay_duong(df, TS, 10_000, spread_pip=0.0)
    b = chay_duong(df, TS, 10_000, spread_pip=0.0, swap_nam=None)
    assert a == b and a["swap_tk"] == 0.0


def test_qua_dem_thu_tu_x3():
    # 2026-10-07 la thu Tu -> rollover sang thu Nam = 3 dem; 0,01 lot x 100.000 x gia 1 x 3,65 %/365 = 0,1/dem
    df = _df(["2026-10-07 23:00", "2026-10-08 01:00", "2026-10-08 02:00"])
    kq = chay_duong(df, TS, 10_000, spread_pip=0.0, swap_nam=(0.0365, -9.0))
    assert kq["swap_tk"] == pytest.approx(0.3)
    assert kq["lai_tk"] == pytest.approx(0.3)
    assert kq["lot_dem_mua"] == pytest.approx(0.03) and kq["lot_dem_ban"] == 0.0


def test_trong_ngay_va_cuoi_tuan():
    trong_ngay = _df(["2026-10-06 10:00", "2026-10-06 11:00"])
    assert chay_duong(trong_ngay, TS, 10_000, spread_pip=0.0, swap_nam=(0.0365, 0))["swap_tk"] == 0.0
    # thu Sau 23:00 -> thu Hai 01:00: rollover thu Sau (1) + T7/CN (0) = 1 dem
    cuoi_tuan = _df(["2026-10-09 23:00", "2026-10-12 01:00"])
    kq = chay_duong(cuoi_tuan, TS, 10_000, spread_pip=0.0, swap_nam=(-0.0365, 0), quy_doi=2.0)
    assert kq["swap_tk"] == pytest.approx(-0.05)          # doi sang tien tai khoan: / 2
