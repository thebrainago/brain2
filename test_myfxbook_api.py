# -*- coding: utf-8 -*-
"""Myfxbook: không gọi host bị chặn; JSON tài liệu không thành ĐẠT và không thành việc MT5."""
import json
from pathlib import Path

import pytest

from seeker.cong_khai import myfxbook_api as A
from seeker.cong_khai import chay

pytestmark = pytest.mark.timeout(30)
FX = Path(__file__).resolve().parent / "seeker" / "fixtures"


def _js(ten):
    return json.loads((FX / ten).read_text(encoding="utf-8"))


def test_khong_ket_noi_va_khong_goi_host():
    st = A.trang_thai_ket_noi()
    assert st["ket_noi"] is False and st["loai"] == "challenge" and A.host_bi_chan()
    assert "personal information only" in st["api_pham_vi_tai_lieu"]


def test_tai_khoan_minh_la_khai_bao():
    d = A.doc_phan_hoi(_js("myfxbook_get_my_accounts.json"))
    assert d["pham_vi"] == "tai_khoan_cua_minh" and d["so_lenh"] is None
    assert d["ho_so"][0]["dat"] is False and d["ho_so"][0]["gain_pct_khai_bao"] == 8.92
    assert d["ho_so"][0]["co_lich_su_lenh"] is False


def test_watched_khong_co_lich_su():
    d = A.doc_phan_hoi(_js("myfxbook_get_watched.json"))
    assert d["pham_vi"] == "tom_tat_tai_khoan_dang_theo_doi"
    assert d["so_lenh"] is None and d["ho_so"][0]["id"] is None
    assert "không" in d["ly_do"].lower() or "Không" in d["ly_do"]


def test_history_50_khong_phai_ben_thu_ba():
    d = A.doc_phan_hoi(_js("myfxbook_get_history.json"))
    assert d["so_lenh"] == 1 and d["day_du"] is False and d["dat"] is False
    assert "trader khác" in d["ly_do"] or "không ghi" in d["ly_do"]
    assert A.doc_phan_hoi(_js("myfxbook_login_error.json"))["loai"] == "auth"


def test_nhap_ra_viec_nghien_cuu_khong_trung_mt5(tmp_path):
    r = A.nhap(FX / "myfxbook_get_history.json", tmp_path)
    assert r["quyet_dinh"] == "nhan"
    v = r["viec"]
    assert v["loai"] == "nghien_cuu_track_record" and v["khong_phai_viec_mt5"] is True
    assert v["dat"] is False and v["chien_luoc_giai_ma"] is False
    assert (tmp_path / (v["id"] + ".json")).is_file()
    assert not (tmp_path / "can_test").exists()
    assert A.nhap(FX / "myfxbook_get_history.json", tmp_path)["quyet_dinh"] == "trung"


def test_quet_cong_khai_khong_cham_myfxbook():
    class TT:
        def __init__(self):
            self.goi = []
        def tai_ro(self, url):
            self.goi.append(url)
            return {"loai": "ok", "text": "<html>ok</html>", "stale": False, "ly_do": "", "http": 200, "url_cuoi": url}
    tt = TT()
    d = chay.dem_myfxbook(tt)
    assert d["khong_goi"] is True and d["loai"] == "challenge" and tt.goi == []
