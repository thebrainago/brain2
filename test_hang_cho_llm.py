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
    # Da tieu thu: chu ky sau (cung loai, prompt khac) phai xep CHO moi, khong
    # tra lai cung mot orphan.
    r3 = HCL.xep_hang("nghi_de_xuat", "sys", "prompt-B-vong-2", tru="NGHI", ep_json=True)
    assert r3["trang_thai"] == "CHO" and r3["pending"] is True
    # Id on dinh: prompt xoay van cung id
    assert r3["id"] == i


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


def test_suc_khoe_ok_khi_rong(hang):
    sk = HCL.suc_khoe(stale_giay=60)
    assert sk["ok"] is True
    assert sk["cho_n"] == 0 and sk["loi_n"] == 0 and sk["cho_stale_n"] == 0
    assert sk["provider"] == "hang_cho"


def test_suc_khoe_phat_stale_va_loi(hang, monkeypatch):
    import time
    r = HCL.xep_hang("nghi_de_xuat", "s", "prompt-stale", tru="NGHI")
    p = HCL.CHO / ("%s.json" % r["id"])
    # gia lap file cu
    cu = time.time() - 7200
    import os as _os
    _os.utime(p, (cu, cu))
    sk = HCL.suc_khoe(stale_giay=1800)
    assert sk["ok"] is False
    assert sk["cho_stale_n"] == 1
    # them loi/
    (HCL.LOI / "x.json").write_text("{}", encoding="utf-8")
    sk2 = HCL.suc_khoe(stale_giay=1800)
    assert sk2["loi_n"] == 1 and sk2["ok"] is False


def test_mach_c_duong_llm_hang_cho_khong_can_openai(hang, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from nhan import mach
    kq = mach.c_duong_llm()
    assert kq["gia_tri"] == "hang_cho"
    assert kq["trang_thai"] == mach.TOT
    assert "hang_cho" in (kq.get("mo_ta") or "")


def test_dieu_phoi_khong_fatal_openai_khi_hang_cho(hang, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    import dieu_phoi as DP
    # nhip_moi=True de khong them fatal nhip
    dg = DP.danh_gia_ket_qua(
        0, {"loi": "thieu OPENAI_API_KEY (va cc-switch khong co provider nao)"},
        {"trang_thai": "nghi", "luc": "2026-10-30 12:00:00", "chi_tiet_obj": {}},
        nhip_moi=True)
    assert dg["ok"] is True or dg["status"] == "degraded"
    assert not any("payload.loi" in f for f in dg["fatal"])



def test_nghi_prompt_xoay_tieu_thu_theo_loai(hang, tmp_path):
    """Bug 2: prompt NGHI xoay → bam lech; van nhat tra loi chua tieu thu cung loai."""
    # Gia lap orphan: worker tra loi id CU (bam theo prompt cu, khac id on dinh).
    orphan_id = "deadbeeforphan0000000001"
    (HCL.XONG / ("%s.json" % orphan_id)).write_text(json.dumps({
        "id": orphan_id, "ok": True, "loai_viec": "nghi_de_xuat", "tru": "NGHI",
        "van_ban": json.dumps({"de_xuat": [{"ten": "co_che_orphan", "ho": "xu_huong",
                                            "co_che": "ai tra tien khi A khi B",
                                            "vao": [], "nguon": ""}],
                               "ly_do_chon": "orphan"}, ensure_ascii=False),
        "json": {"de_xuat": [{"ten": "co_che_orphan"}], "ly_do_chon": "orphan"},
        "da_tieu_thu": False,
    }, ensure_ascii=False), encoding="utf-8")
    # Prompt MOI (id on dinh khac orphan_id) — phai nhat orphan theo loai
    r = HCL.xep_hang("nghi_de_xuat", "sys", "prompt-XOAY-tai-lieu-vong-99",
                     tru="NGHI", ep_json=True)
    assert r["trang_thai"] == "OK"
    assert r.get("tieu_thu_theo_loai") is True or "orphan" in (r.get("ghi_chu") or "")
    assert "co_che_orphan" in r["van_ban"]
    # Orphan da danh dau tieu thu
    d = json.loads((HCL.XONG / ("%s.json" % orphan_id)).read_text(encoding="utf-8"))
    assert d.get("da_tieu_thu") is True
    # Lan sau khong nhat lai
    r2 = HCL.xep_hang("nghi_de_xuat", "sys", "prompt-XOAY-tiep", tru="NGHI", ep_json=True)
    assert r2["trang_thai"] == "CHO"


def test_id_on_dinh_nghi_khong_phu_nhac(hang):
    a = HCL.bam_yeu_cau("nghi_de_xuat", "sys", "prompt-1", tru="NGHI")
    b = HCL.bam_yeu_cau("nghi_de_xuat", "sys-khac", "prompt-2-xoay", tru="NGHI")
    assert a == b
    c = HCL.bam_yeu_cau("dich_boc", "sys", "prompt-1")
    d = HCL.bam_yeu_cau("dich_boc", "sys", "prompt-2")
    assert c != d


