# -*- coding: utf-8 -*-
"""P1: nhan/luoi_duong.py - mo phong luoi theo duong gia (khop tai nguong, spread mot lan)."""
import numpy as np
import pandas as pd
import pytest

from nhan.luoi import ThamSo
from nhan.luoi_duong import _Ro, chay_duong, duong


def _df(bars):
    idx = pd.date_range("2019-03-01", periods=len(bars), freq="h")
    return pd.DataFrame(bars, columns=["open", "high", "low", "close"], index=idx)


def test_thu_tu_duong():
    assert duong(1.0, 1.3, 0.9, 1.1, "thap_truoc") == (1.0, 0.9, 1.3, 1.1)
    assert duong(1.0, 1.3, 0.9, 1.1, "cao_truoc") == (1.0, 1.3, 0.9, 1.1)
    assert duong(1.0, 1.3, 0.9, 0.95, "mau_nen") == (1.0, 1.3, 0.9, 0.95)
    assert duong(1.0, 1.05, 0.8, 0.9, "gan_open") == (1.0, 1.05, 0.8, 0.9)


def test_tang_va_tp_khop_tai_nguong():
    # mua, buoc 10, tp 5, lot phang 0.01, khong spread: mo 1.0000, xuong 0.9990 (tang 2), len 1.0010
    ts = ThamSo(buoc=10, tp=5, tran_tang=5, che_do="mua", lot=0.01, kieu_lot="phang")
    df = _df([(1.0000, 1.0000, 1.0000, 1.0000), (1.0000, 1.0010, 0.9990, 1.0010)])
    kq = chay_duong(df, ts, 10_000, "thap_truoc", spread_pip=0.0)
    # TP tai TB 0.9995 + 5 pip = 1.0000: lai = 0 + 10 pip * 0.01 lot = 1.0; mo L1 moi tai 1.0000,
    # TP moi 1.0005 -> +0.5; L1 1.0005 -> TP 1.0010 cham dung close -> +0.5; L1 1.0010 dong cuoi = 0
    assert kq["lai_tk"] == pytest.approx(2.0)
    assert kq["so_ro"] == 3


def test_tia_dong_tai_nguong_khong_tai_cuc_tri():
    ts = ThamSo(buoc=10, tp=100, tran_tang=5, che_do="mua", lot=0.01, kieu_lot="phang",
                tia_lenh=True, bien_cap=4)
    r = _Ro(1, ts, True, 0.0)
    lai = [0.0]
    r.mo(1.0000, 1.0, lai)
    r.toi(1.0000, 0.9990, 1.0, lai, nhay=False)      # them tang 2 tai 0.9990
    assert len(r.vao) == 2
    r.toi(0.9990, 1.0050, 1.0, lai, nhay=False)      # cap dong tai TB 0.9995 + 4 pip = 0.9999
    assert r.so_cap == 1
    # lai cap = (0.9999-1.0)+(0.9999-0.9990) = 8 pip * 0.01 lot = 0.8; L1 moi tai 0.9999
    assert r.chot == pytest.approx(0.8)
    assert r.vao[0][0] == pytest.approx(0.9999)


def test_lot_lam_tron_nhu_ea():
    ts = ThamSo(lot=0.02, kieu_lot="nhan", he_so_lot=0.4)
    r = _Ro(1, ts, True, 0.0)
    assert [r.lot(k) for k in range(4)] == pytest.approx([0.02, 0.01, 0.01, 0.01])
    r2 = _Ro(1, ts, False, 0.0)
    assert r2.lot(2) == pytest.approx(0.0032)


def test_spread_mot_lan_moi_lenh():
    ts = ThamSo(buoc=10, tp=5, tran_tang=5, che_do="ban", lot=0.1, kieu_lot="phang")
    df = _df([(1.0, 1.0, 1.0, 1.0)] * 3)
    kq = chay_duong(df, ts, 10_000, "gan_open", spread_pip=2.0)
    assert kq["lai_tk"] == pytest.approx(-2 * 1e-4 * 0.1 * 100_000)
    assert kq["so_lenh"] == 1


def test_tham_so_chua_ho_tro_bao_loi():
    with pytest.raises(ValueError):
        chay_duong(_df([(1, 1, 1, 1)]), ThamSo(cho_lui=5), 10_000)


def test_nhan_25_09_chi_la_nhan():
    import vong_thu_nghiem as V
    assert V.nhan_25_09({"loi_log": 0.1, "maxdd_pct": 30.0})["dat"] is True
    n = V.nhan_25_09({"loi_log": 0.1, "maxdd_pct": 85.0})
    assert n["dat"] is False and "maxDD" in n["ly_do"][0]
    tk = {"von_dau": 10_000, "von_cuoi": 12_000, "von_rong_min": 4_000, "so_stop_out": 1, "chay": False}
    n = V.nhan_25_09({"loi_log": 0.2, "tai_khoan": tk})
    assert n["dat"] is False and n["maxdd_pct"] == 60.0 and "stop-out/cháy" in n["ly_do"]
