# -*- coding: utf-8 -*-
"""G08 (G-a): quan tri ro tuy chon trong nhan/luoi_duong - chot theo USD, duoi dinh, dung theo gio."""
import pandas as pd
import pytest

from nhan.luoi import ThamSo
from nhan.luoi_duong import chay_duong


def _df(bars):
    idx = pd.date_range("2019-03-01", periods=len(bars), freq="h")
    return pd.DataFrame(bars, columns=["open", "high", "low", "close"], index=idx)


TS = dict(buoc=10, tp=5, tran_tang=5, che_do="mua", lot=0.01, kieu_lot="phang")


def test_chot_usd_thay_tp_pip():
    df = _df([(1.0, 1.0, 1.0, 1.0), (1.0, 1.0006, 1.0, 1.0006)])
    # 0,5 USD / (0,01 lot x 100000) = 5 pip tren TB -> dong 1.0005 (+0,5), mo lai 1.0005, het cua so 1.0006 (+0,1)
    kq = chay_duong(df, ThamSo(**TS), 10_000, "thap_truoc", spread_pip=0.0, chot_usd=0.5)
    assert kq["lai_tk"] == pytest.approx(0.6)
    assert kq["so_ro"] == 1
    # 2 USD -> 20 pip: khong cham, chi dong cuoi
    kq = chay_duong(df, ThamSo(**TS), 10_000, "thap_truoc", spread_pip=0.0, chot_usd=2.0)
    assert kq["lai_tk"] == pytest.approx(0.6) and kq["so_ro"] == 0


def test_duoi_dinh_dong_khi_lui():
    df = _df([(1.0, 1.0, 1.0, 1.0), (1.0, 1.0010, 1.0, 1.0007)])
    # kich hoat 1.0005, dinh 1.0010, lui 2 pip -> dong 1.0008 (+0,8); mo lai 1.0008, dong cuoi 1.0007 (-0,1)
    kq = chay_duong(df, ThamSo(**TS), 10_000, "thap_truoc", spread_pip=0.0, duoi=(5, 2))
    assert kq["lai_tk"] == pytest.approx(0.7)
    assert kq["so_duoi"] == 1 and kq["so_ro"] == 1
    # khong duoi: TP 5 pip -> khac
    kq0 = chay_duong(df, ThamSo(**TS), 10_000, "thap_truoc", spread_pip=0.0)
    assert kq0["so_duoi"] == 0 and kq0["so_ro"] == 2          # TP 1.0005 va 1.0010


def test_duoi_chua_kich_hoat_khong_dong():
    df = _df([(1.0, 1.0, 1.0, 1.0), (1.0, 1.0004, 1.0, 1.0001)])
    kq = chay_duong(df, ThamSo(**TS), 10_000, "thap_truoc", spread_pip=0.0, duoi=(5, 2))
    assert kq["so_duoi"] == 0 and kq["lai_tk"] == pytest.approx(0.1)


def test_dung_theo_gio():
    ts = ThamSo(buoc=100, tp=100, tran_tang=5, che_do="mua", lot=0.01, kieu_lot="phang")
    df = _df([(1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0),
              (0.9995, 0.9995, 0.9995, 0.9995), (0.9995, 0.9995, 0.9995, 0.9995)])
    kq = chay_duong(df, ts, 10_000, "gan_open", spread_pip=0.0, dung_gio=2)
    assert kq["so_dung_gio"] == 1
    assert kq["lai_tk"] == pytest.approx(-0.5)
    kq = chay_duong(df, ts, 10_000, "gan_open", spread_pip=0.0)
    assert kq["so_dung_gio"] == 0 and kq["lai_tk"] == pytest.approx(-0.5)


def test_ke_hoach_g08_dong_bang_va_goc_trung_g07():
    import json
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent / "hieu_chuan"))
    import g07_chon_tai_san as g07
    import g08_quan_tri_ro as g
    assert g.bam_ke_hoach() == json.loads(g.KE_HOACH_FILE.read_text())["sha256_16"]
    ts, kw = g.ts_bien_the("V0_goc")
    assert ts == ThamSo(**g07.KE_HOACH["tham_so"]) and kw == {}
    assert len(g.KE_HOACH["bien_the"]) == 6
