# -*- coding: utf-8 -*-
"""Bay cua MT5 tester trong launcher mt5tools (ra soat 18/10/2026)."""
import os
import sys
import time

sys.path.insert(0, "mt5tools")
import an_toan_tester as AT  # noqa: E402
import sinh_viec as SV  # noqa: E402


def test_don_bay_dung_dinh_dang_mt5():
    assert AT.dong_don_bay(30) == "Leverage=1:30\n"
    assert AT.kiem_don_bay("1:30", 30) == ""
    assert "1:100" in AT.kiem_don_bay("1:100", 30)          # 58/58 bao cao that: dat 30, tester chay 1:100


def test_bao_cao_cu_khong_duoc_doc_lai(tmp_path):
    f = tmp_path / "xl_a.htm"
    f.write_text("cu")
    os.utime(f, (time.time() - 600, time.time() - 600))
    assert not AT.bao_cao_moi(f, time.time())
    AT.xoa_bao_cao_cu(tmp_path, "xl_a")
    assert not f.exists()


def test_0_lenh_trong_vai_giay_la_chua_do_duoc():
    assert AT.phan_xu_ket_qua({"net": 0.0, "lenh": 0}, 20).startswith("chua_do_duoc")
    assert AT.phan_xu_ket_qua({"net": None, "lenh": None}, 300) == "khong_doc_duoc_bao_cao"
    assert AT.phan_xu_ket_qua({"net": 0.0, "lenh": 0}, 300) == ""          # chay du lau, that su khong co lenh
    assert AT.phan_xu_ket_qua({"net": 5.0, "lenh": 12}, 20) == ""


def _r(**k):
    r = {"ea": "MRZ", "ma": "GBPUSD#", "tf": "D1", "ts": SV._ts("MRZ", {}), "pha": "IS"}
    r.update(k)
    return r


def test_lan_chay_hong_duoc_thu_lai_toi_da_hai_lan():
    v = SV.lay_viec(1, so_cai=[])[0]
    hong = dict(v, loi="khong_bao_cao")
    assert SV.khoa(v) in {SV.khoa(x) for x in SV.lay_viec(4000, so_cai=[hong])}
    assert SV.khoa(v) not in {SV.khoa(x) for x in SV.lay_viec(4000, so_cai=[hong, hong])}


def test_oos_hong_khong_bi_tinh_la_truot_oos():
    is_ = _r(pf=1.5, lenh=50, net=100.0, p=0.01, dd="10.0 (1.0%)")
    oos_tot = dict(is_, pha="OOS", pf=1.3, lenh=20, net=50.0)
    oos_hong = dict(is_, pha="OOS", loi="qua_gio")
    t = SV.tong_ket([is_, oos_tot, oos_hong])                # dong hong den SAU khong duoc de len dong tot
    assert len(t["ung_vien_ca_hai"]) == 1
