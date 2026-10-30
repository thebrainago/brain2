# -*- coding: utf-8 -*-
"""Test hang cho LLM (file queue) — khong can API key."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from nhan import hang_cho_llm as HCL


@pytest.fixture()
def hang(tmp_path, monkeypatch):
    monkeypatch.setattr(HCL, "GOC", tmp_path)
    monkeypatch.setattr(HCL, "CHO", tmp_path / "cho")
    monkeypatch.setattr(HCL, "XONG", tmp_path / "xong")
    monkeypatch.setattr(HCL, "LOI", tmp_path / "loi")
    HCL.dam_bao_thu_muc()
    monkeypatch.setenv("BRAIN_LLM_PROVIDER", "hang_cho")
    return tmp_path


def test_dang_bat(monkeypatch):
    monkeypatch.delenv("BRAIN_LLM_PROVIDER", raising=False)
    assert HCL.dang_bat() is False
    monkeypatch.setenv("BRAIN_LLM_PROVIDER", "hang_cho")
    assert HCL.dang_bat() is True
    monkeypatch.setenv("BRAIN_LLM_PROVIDER", "FILE")
    assert HCL.dang_bat() is True


def test_xep_hang_ghi_cho_va_idempotent(hang):
    r1 = HCL.xep_hang("nghi_de_xuat", "sys", "prompt-A", tru="NGHI", ep_json=True)
    assert r1["trang_thai"] == "CHO" and r1["pending"] is True
    assert (HCL.CHO / ("%s.json" % r1["id"])).exists()
    r2 = HCL.xep_hang("nghi_de_xuat", "sys", "prompt-A", tru="NGHI", ep_json=True)
    assert r2["id"] == r1["id"] and r2["trang_thai"] == "CHO"
    # Khong tao file thu 2
    assert len(list(HCL.CHO.glob("*.json"))) == 1


def test_tra_loi_va_doc_lai(hang, tmp_path):
    r = HCL.xep_hang("nghi_de_xuat", "sys", "prompt-B", tru="NGHI", ep_json=True)
    i = r["id"]
    tl = tmp_path / "tl.json"
    tl.write_text(json.dumps({"de_xuat": [{"ten": "a"}], "ly_do_chon": "x"}, ensure_ascii=False), encoding="utf-8")
    assert HCL.tra_loi(i, str(tl)) == 0
    assert not (HCL.CHO / ("%s.json" % i)).exists()
    assert (HCL.XONG / ("%s.json" % i)).exists()
    r2 = HCL.xep_hang("nghi_de_xuat", "sys", "prompt-B", tru="NGHI", ep_json=True)
    assert r2["trang_thai"] == "OK" and "de_xuat" in r2["van_ban"]
    assert r2.get("pending") is False


def test_tra_loi_invalid_vao_loi(hang, tmp_path):
    r = HCL.xep_hang("nghi_de_xuat", "", "prompt-C", ep_json=True)
    i = r["id"]
    tl = tmp_path / "bad.txt"
    tl.write_text("not json at all {{{", encoding="utf-8")
    assert HCL.tra_loi(i, str(tl)) == 2
    assert (HCL.LOI / ("%s.json" % i)).exists()
    assert (HCL.CHO / ("%s.json" % i)).exists()  # van cho (chua xong)


def test_cau_llm_goi_hang_cho(hang, monkeypatch):
    from nhan import cau_llm as LLM
    monkeypatch.setenv("BRAIN_LLM_PROVIDER", "hang_cho")
    assert LLM.co_khoa() is True
    r = LLM.goi("hay dich cai nay", he_thong="sys", loai_viec="dich_boc")
    assert r["trang_thai"] == "CHO" and r["pending"] is True
    # goi lai cung prompt -> CHO, khong storm
    r2 = LLM.goi("hay dich cai nay", he_thong="sys", loai_viec="dich_boc")
    assert r2["id"] == r["id"]


def test_tri_tue_hoi_hang_cho(hang, monkeypatch):
    from nhan import tri_tue as TT
    monkeypatch.setenv("BRAIN_LLM_PROVIDER", "hang_cho")
    # tranh doc cache/so that — dung dung_cache=False, bo_qua_han_muc
    kq = TT.hoi("prompt-nghi-1", "he", dung_cache=False, bo_qua_han_muc=True,
                ep_json=True, loai_viec="nghi_de_xuat", tru="NGHI")
    assert kq.get("pending") or kq.get("trang_thai") == "CHO"
    i = kq["id"]
    # gia lap worker
    (HCL.XONG / ("%s.json" % i)).write_text(json.dumps({
        "id": i, "van_ban": json.dumps({"de_xuat": [], "ly_do_chon": "khong"}, ensure_ascii=False),
        "ok": True,
    }), encoding="utf-8")
    (HCL.CHO / ("%s.json" % i)).unlink(missing_ok=True)
    kq2 = TT.hoi("prompt-nghi-1", "he", dung_cache=False, bo_qua_han_muc=True,
                 ep_json=True, loai_viec="nghi_de_xuat", tru="NGHI")
    assert kq2.get("trang_thai") == "OK" and kq2.get("van_ban")


def test_cli_liet_ke_thong_ke(hang, capsys):
    HCL.xep_hang("khac", "", "aaa")
    HCL.xep_hang("dich_boc", "s", "bbb")
    assert HCL.liet_ke() == 0
    out = capsys.readouterr().out
    assert '"cho": 2' in out or '"cho":2' in out.replace(" ", "")
    assert HCL.thong_ke() == 0
