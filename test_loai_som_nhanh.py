# -*- coding: utf-8 -*-
"""Nhan LOAI SOM NHANH (11/10/2026): DD > 65 % hoac lai < 10 %/nam - chi NHAN, khong doi GIU/BO."""
import inspect
import math

import vong_thu_nghiem as V


def _tk(von_dau, von_cuoi, von_min):
    return {"tai_khoan": {"von_dau": von_dau, "von_cuoi": von_cuoi, "von_rong_min": von_min}}


def test_tai_khoan_lai_cao_dd_thap_khong_loai():
    n = V.nhan_loai_som_nhanh(_tk(10000, 12100, 9000), 2.0)   # +10 %/nam, DD 10 %
    assert n["loai"] is False and abs(n["lai_nam_pct"] - 10.0) < 1e-6 and n["maxdd_pct"] == 10.0


def test_lai_thap_bi_loai():
    n = V.nhan_loai_som_nhanh(_tk(10000, 10500, 9500), 1.0)
    assert n["loai"] is True and any("lãi" in x for x in n["ly_do"])


def test_dd_cao_bi_loai():
    n = V.nhan_loai_som_nhanh(_tk(10000, 20000, 3000), 1.0)   # lai 100 % nhung DD 70 %
    assert n["loai"] is True and any("maxDD" in x for x in n["ly_do"])


def test_chay_tai_khoan_khong_loi():
    n = V.nhan_loai_som_nhanh(_tk(10000, 0, 0), 1.0)
    assert n["loai"] is True and n["lai_nam_pct"] == -100.0


def test_lenh_don_va_chua_do():
    n = V.nhan_loai_som_nhanh({"loi_log": math.log(1.21), "maxdd_pct": 5.0}, 2.0)
    assert n["loai"] is False and abs(n["lai_nam_pct"] - 10.0) < 1e-6
    n = V.nhan_loai_som_nhanh({"loi_log": 0.1, "maxdd_pct": 5.0}, 0)
    assert n["loai"] is None and "CHƯA ĐO ĐƯỢC" in V._chu_loai_som(n)


def test_chu_ghi_uoc_luong_va_chi_nhan():
    t = V._chu_loai_som(V.nhan_loai_som_nhanh(_tk(10000, 10100, 9900), 1.0))
    assert "ƯỚC LƯỢNG" in t and "không đổi GIỮ/BỎ" in t and "LOẠI SỚM" in t


def test_khong_doi_giu():
    src = inspect.getsource(V._chay_nhom)
    assert 'dong["giu_lai"] = bool(dat_cu and cl["dat"])' in src
    assert "loai_som_nhanh" in src and "giu_lai" not in src.split("loai_som_nhanh")[1].split("\n")[0]
