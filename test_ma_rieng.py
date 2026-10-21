# -*- coding: utf-8 -*-
"""20/10/2026: the python_llm (ma nguon o tin_hieu["ma"]) khong duoc bi hieu la danh sach symbol."""
import random

from nhan import ong_dan as OD


def test_python_llm_khong_phai_symbol():
    t = {"id": "x", "tin_hieu": {"kieu": "python_llm", "ma": "def tin_hieu(df):\n    return df['close']*0\n"}}
    assert OD._ma_rieng(t) == []
    cfg = {"khung": ["H1"]}
    OD_ma = OD.ma_co_du_lieu
    OD.ma_co_du_lieu = lambda _c: ["EURUSD"]
    try:
        r = OD.mau_thu(t, random.Random(1), cfg)
    finally:
        OD.ma_co_du_lieu = OD_ma
    assert r is not None and r["ma"] == "EURUSD"


def test_symbol_rieng_van_giu():
    assert OD._ma_rieng({"tin_hieu": {"kieu": "lenh_ngoai", "ma": ["XAUUSD"]}}) == ["XAUUSD"]
