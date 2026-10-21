# -*- coding: utf-8 -*-
"""20/10/2026: che do LUOI (EA luoi / martingale hai chieu / luon vao khong co tin hieu chieu)."""
import random

import numpy as np
import pandas as pd

from nhan import dich_llm as DL
from nhan import luoi_hai_chieu as LH
from nhan import ong_dan as OD
from nhan import tai_khoan as TK


def _gia(n=3000, hat=7):
    r = np.random.default_rng(hat)
    x = 1.0 + np.cumsum(r.normal(0, 0.0012, n))
    i = pd.date_range("2024-01-01", periods=n, freq="h")
    o = np.r_[x[0], x[:-1]]
    h = np.maximum(o, x) + np.abs(r.normal(0, 0.0006, n))
    lo = np.minimum(o, x) - np.abs(r.normal(0, 0.0006, n))
    return pd.DataFrame({"open": o, "high": h, "low": lo, "close": x}, index=i)


LUOI = {"che_do": "luoi_hai_chieu", "chieu": "hai", "lot0": 0.01, "buoc_diem": 200, "toi_da": 10, "he_so_lot": 1.0,
        "tp_diem": 200}


def test_chuan_hoa_bat_loi():
    _, loi = LH.chuan_hoa({"che_do": "luoi_hai_chieu", "toi_da": 3})
    assert any("TP" in x for x in loi) and any("buoc" in x for x in loi)
    x, loi = LH.chuan_hoa(dict(LUOI, chieu="both"))
    assert not loi and x["chieu"] == "hai"


def test_quy_doi_tham_so_tac_gia():
    q = LH.ql_tu_tac_gia(dict(LUOI, tp_diem=None, tp_tien=1.0, cat_lo_tien=100), 1.0, 1e-5, 1000.0, 1.0, 1000.0)
    assert abs(q["dca_buoc_pct"] - 0.002) < 1e-12           # 200 diem x 1e-5 / gia 1.0
    assert abs(q["tp_pct"] - 0.001) < 1e-12                 # 1 USD / (0.01 lot x 100000) = 0.001 gia
    assert abs(q["cat_lo_pct"] - 0.1) < 1e-9                # 100 USD lot chuan -> 0.1 USD bo may (hop dong 1000) / 1000
    assert q["dca_toi_da"] == 10 and q["lot_tren_1000"] == 0.01
    assert OD.quan_li_tu(dict(q, cat_lo_pct=5.0), 1000.0).cat_lo_pct == 5.0


def test_kiem_dem_lenh_that_khong_dem_doi_tin_hieu():
    df = _gia()
    r = DL.kiem_tra({"luoi": LUOI, "spec": [], "python": ""}, df)
    assert r["dat"] and r["kieu"] == "luoi" and r["so_lenh"] >= 3 and r["so_tp"] >= 1
    # TP qua xa -> it ro that -> IT_LENH (dem ro cua bo may, khong dem lan doi)
    r2 = DL.kiem_tra({"luoi": dict(LUOI, tp_diem=10 ** 7, toi_da=0)}, df)
    assert not r2["dat"] and DL.nhom_ly_do(r2["ly_do"]) == "IT_LENH"
    r3 = DL.kiem_tra({"luoi": {"che_do": "luoi_hai_chieu"}}, df)
    assert not r3["dat"] and DL.nhom_ly_do(r3["ly_do"]) == "LUOI_SAI"


def test_bo_loc_chieu_nhin_truoc_bi_bat():
    df = _gia()
    gian = "def tin_hieu(df):\n    c = df['close']\n    m = c.rolling(48, center=True, min_periods=1).mean()\n" \
           "    return np.where(c > m, 1, -1).astype(int)\n"
    r = DL.kiem_tra({"luoi": dict(LUOI, loc_python=gian)}, df)
    assert not r["dat"] and any("NHIN TRUOC" in x or x.startswith("python:") for x in r["ly_do"])
    sach = "def tin_hieu(df):\n    c = df['close']\n    e = c.ewm(span=50, adjust=False).mean()\n" \
           "    return np.where(c > e, 1, -1).astype(int)\n"
    assert DL.kiem_tra({"luoi": dict(LUOI, loc_python=sach)}, df)["dat"]


def test_lenh_vao_hai_chieu_va_rut_gon_csv():
    df = _gia(600)
    l, _ = LH.chuan_hoa(LUOI)
    m, b = LH.cho_phep(l, df)
    ev = LH.lenh_vao(df, m, b, "x")
    assert len(ev) == 2 * (len(df) - 1) and {e.chieu for e in ev} == {1, -1}
    assert all(e.gia == df["open"].iloc[e.chi_so] for e in ev[:10])          # vao o OPEN nen sau
    q = OD.quan_li_tu(LH.ql_tu_tac_gia(l, 1.0, 1e-5, 1000.0, 1.0, 1000.0), 1000.0)
    kq = TK.chay_tk({"": df}, ev, q, TK.ho_so_tai_khoan("XM_MICRO_TAM", 1000.0), {"": TK.ho_so_phi("AUDCAD")},
                    ghi_von=False, ghi_lenh=True)
    gon = LH.rut_gon_csv(ev, kq["lenh"])
    assert 0 < len(gon) < len(ev)
    kq2 = TK.chay_tk({"": df}, gon, q, TK.ho_so_tai_khoan("XM_MICRO_TAM", 1000.0), {"": TK.ho_so_phi("AUDCAD")},
                     ghi_von=False)
    assert kq2["so_ro"] == kq["so_ro"]                                       # CSV rut gon cho cung so ro


def test_ong_dan_the_luoi_ql_tac_gia_co_dinh(monkeypatch):
    df = _gia(2000)
    monkeypatch.setattr(OD, "gia", lambda ma, khung="H1", cfg=None: df)
    monkeypatch.setattr(OD, "ma_co_du_lieu", lambda cfg=None: ["AUDCAD"])
    t = {"id": "t_luoi", "duong_dich": "luoi", "tin_hieu": {"kieu": "luoi", "luoi": LUOI, "khoang": {}}}
    cfg = dict(OD.cau_hinh(), khung=["H1"])
    a = OD.mau_thu(t, random.Random(1), cfg)
    b = OD.mau_thu(t, random.Random(2), cfg)
    assert a["ql"] == b["ql"] and a["ql"]["dca_toi_da"] == 10               # khong lay ngau nhien KHONG_GIAN_QL
    cb = OD.chuan_bi(t, a, cfg)
    assert {e.chieu for e in cb["ev"]} == {1, -1}
    assert OD._ma_rieng(t) == []


def test_lot_tuyen_tinh_va_cat_lo_diem_va_ca_hai():
    q = LH.ql_tu_tac_gia(dict(LUOI, kieu_lot="tuyen_tinh", cat_lo_diem=200), 1.0, 1e-5, 1000.0, 1.0, 1000.0)
    assert q["dca_lot_tuyen_tinh"] is True
    assert abs(q["cat_lo_pct"] - 0.002) < 1e-9          # 200 diem x 0.01 lot chuan = 2 USD -> 0.02 USD bo may / 1000
    ql = OD.quan_li_tu(q, 1000.0)
    assert ql.dca_lot_tuyen_tinh
    v = OD.set_csv(q, 1000.0, "XM", "H1", "x.csv")
    assert v["InpKieuLot"] == 1                          # EA LOT_TUYEN_TINH
    df = _gia(300)
    l, _ = LH.chuan_hoa(LUOI)
    s = np.zeros(len(df), int); s[10] = 2; s[20] = 1; s[30] = -1
    m, b = LH.cho_phep(l, df, s)
    assert m[10] and b[10] and m[20] and not b[20] and b[30] and not m[30] and not (m[5] or b[5])


def test_tin_hieu_the_luoi_khong_nem_ValueError_va_sinh_duoc_viec_csv(monkeypatch, tmp_path):
    """21/10/2026: `ong_dan.tin_hieu` nem ValueError('luoi') lam sap buoc_sinh_mt5 -> khong sinh viec MT5 cho ca hang."""
    df = _gia(2000)
    monkeypatch.setattr(OD, "gia", lambda ma, khung="H1", cfg=None: df)
    t = {"id": "t_luoi2", "duong_dich": "luoi", "tin_hieu": {"kieu": "luoi", "luoi": LUOI, "khoang": {}}}
    s = OD.tin_hieu(t, df, {}, "AUDCAD")
    assert len(s) == len(df) and set(np.unique(s)) <= {0, 1}
    loc = dict(LUOI, loc_python="def tin_hieu(df):\n    c = df['close']\n    e = c.ewm(span=50, adjust=False).mean()\n"
                                 "    return np.where(c > e, 1, -1).astype(int)\n")
    s2 = OD.tin_hieu({"tin_hieu": {"kieu": "luoi", "luoi": loc}}, df, {}, "AUDCAD")
    assert set(np.unique(s2)) == {1, -1}
    cfg = dict(OD.cau_hinh(), khung=["H1"])
    thu = OD.mau_thu(t, random.Random(1), cfg)
    ra = OD.viec_csv(t, thu, {"lai_pct_nam": 20.0, "sut_giam_pct": 30.0, "so_stop_out": 0, "lot0": 0.01}, cfg, tmp_path)
    assert isinstance(ra, list)
