# -*- coding: utf-8 -*-
"""NHAN P4 (11/10/2026): luat loai som de xuat D1/D2 chi la NHAN, khong doi GIU/BO."""
import vong_thu_nghiem as V


def test_khong_ro_khong_nhan():
    assert V.nhan_p4(None, {"p": 0.01}) is None


def test_d2_placebo():
    assert V.nhan_p4("hedge", {"p": 0.03})["qua"] is True
    n = V.nhan_p4("hedge", {"p": 0.2})
    assert n["qua"] is False and n["ly_do"] == ["D2_thang_placebo"]
    n = V.nhan_p4("hedge", {"p": None, "placebo_bo_qua": "chan lenh dung trong bar"})
    assert n["qua"] is None and n["muc"]["D2_thang_placebo"]["dat"] is None
    assert "CHƯA ĐO ĐƯỢC" in V._chu_p4(n)


def test_d1_luoi_duong_xau_nhat():
    n = V.nhan_p4("luoi", {"p": 0.01})
    assert n["muc"]["D1_duong_xau_nhat_lai"]["dat"] is None and n["qua"] is None
    n = V.nhan_p4("luoi", {"p": 0.01}, [0.5, 0.2, -0.1, 0.3, 0.4, 0.1, 0.2, 0.3])
    assert n["qua"] is False and n["ly_do"] == ["D1_duong_xau_nhat_lai"]
    n = V.nhan_p4("luoi", {"p": 0.01}, [0.5, 0.2, 0.1, 0.3])
    assert n["qua"] is True
    assert "chỉ là NHÃN" in V._chu_p4(n)


def test_chi_la_nhan_khong_doi_giu():
    # cong_luoi khong doi theo nhan: dat chi phu thuoc p/chay nhu truoc
    import inspect
    src = inspect.getsource(V._chay_nhom)
    assert 'dong["giu_lai"] = bool(dat_cu and cl["dat"])' in src
