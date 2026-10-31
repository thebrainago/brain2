# -*- coding: utf-8 -*-
"""MT5 kha dung tren may nay — dieu_toc bo qua tester treo, Evo bao ro."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from nhan import dieu_toc as DT
from nhan import mt5_kha_dung as MKD


@pytest.fixture()
def tmp_mt5(tmp_path, monkeypatch):
    kq = tmp_path / "ket_qua_mt5"
    kq.mkdir()
    hang = tmp_path / "hang_cho_mt5.jsonl"
    hoan = tmp_path / "hang_cho_mt5_hoan_may_nha.jsonl"
    tt = tmp_path / "MT5_KHA_DUNG.json"
    monkeypatch.setattr(MKD, "KQ_ONG_DAN", kq)
    monkeypatch.setattr(MKD, "HANG_ONG_DAN", hang)
    monkeypatch.setattr(MKD, "HANG_HOAN", hoan)
    monkeypatch.setattr(MKD, "TRANG_THAI", tt)
    monkeypatch.setattr(MKD, "GIO_KHONG_KET_QUA", 6.0)
    monkeypatch.delenv("BRAIN_MT5_KHA_DUNG", raising=False)
    return {"kq": kq, "hang": hang, "hoan": hoan, "tt": tt}


def test_env_ep_tat(tmp_mt5, monkeypatch):
    monkeypatch.setenv("BRAIN_MT5_KHA_DUNG", "0")
    r = MKD.trang_thai(tien_trinh=[])
    assert r["ok"] is False and r["ep_boi_env"] is True


def test_env_ep_bat(tmp_mt5, monkeypatch):
    monkeypatch.setenv("BRAIN_MT5_KHA_DUNG", "1")
    r = MKD.trang_thai(tien_trinh=[(1, "terminal64.exe")])
    assert r["ok"] is True and r["ep_boi_env"] is True


def test_auto_kq_moi_ok(tmp_mt5):
    f = tmp_mt5["kq"] / "od_x_XM_CSV_vao.csv_lenh_mt5.csv"
    f.write_text("a", encoding="utf-8")
    r = MKD.trang_thai(tien_trinh=[(9, "C:\\\\x\\\\terminal64.exe")], bay_gio=time.time())
    assert r["ok"] is True
    assert r["gio_tu_kq_moi"] is not None and r["gio_tu_kq_moi"] < 1


def test_auto_tester_treo_khong_kq(tmp_mt5):
    f = tmp_mt5["kq"] / "od_cu.csv"
    f.write_text("a", encoding="utf-8")
    cu = time.time() - 10 * 3600
    os.utime(f, (cu, cu))
    r = MKD.trang_thai(
        tien_trinh=[(145380, "C:\\\\Program Files\\\\MetaTrader 5\\\\terminal64.exe")],
        bay_gio=time.time())
    assert r["ok"] is False
    assert "tester song" in r["ly_do"] or "TLS" in r["ly_do"]


def test_bo_qua_tin_hieu_tester(tmp_mt5, monkeypatch):
    monkeypatch.setenv("BRAIN_MT5_KHA_DUNG", "0")
    ly = ["tester_mt5:145380", "cpu_90", "tester_mt5:1"]
    ra = MKD.bo_qua_tin_hieu_tester(ly)
    assert ra == ["cpu_90"]


def test_dieu_toc_khong_dung_khi_mt5_treo(tmp_mt5, monkeypatch):
    """terminal64 song + ket qua cu -> muc binh_thuong (khong dung SEEKER)."""
    f = tmp_mt5["kq"] / "od_cu.csv"
    f.write_text("a", encoding="utf-8")
    cu = time.time() - 10 * 3600
    os.utime(f, (cu, cu))
    monkeypatch.delenv("BRAIN_DIEU_TOC", raising=False)
    r = DT.trang_thai(
        cpu=10.0,
        tien_trinh=[(145380, "C:\\\\MT5\\\\terminal64.exe /config:x.ini")],
        khoa=[])
    assert r["muc"] == "binh_thuong"
    assert any(x.startswith("mt5_khong_kha_dung") for x in r["ly_do"])
    assert not any(x.startswith("tester_mt5:") for x in r["ly_do"])


def test_dieu_toc_van_dung_khi_mt5_khoe(tmp_mt5, monkeypatch):
    f = tmp_mt5["kq"] / "od_moi.csv"
    f.write_text("a", encoding="utf-8")
    monkeypatch.delenv("BRAIN_DIEU_TOC", raising=False)
    r = DT.trang_thai(
        cpu=10.0,
        tien_trinh=[(1, "terminal64.exe")],
        khoa=[])
    assert r["muc"] == "dung"
    assert any(x.startswith("tester_mt5:") for x in r["ly_do"])


def test_danh_dau_hoan_giu_hang(tmp_mt5, monkeypatch):
    monkeypatch.setenv("BRAIN_MT5_KHA_DUNG", "0")
    hang = tmp_mt5["hang"]
    hang.write_text(
        json.dumps({"ten": "od_a_XM_CSV", "ma": "EURUSD", "ea": "XL"}, ensure_ascii=False) + "\n"
        + json.dumps({"ten": "od_b_XM_CSV", "ma": "GBPUSD", "ea": "XL"}, ensure_ascii=False) + "\n",
        encoding="utf-8")
    r = MKD.danh_dau_hoan_may_nha()
    assert r["them"] == 2 and r["tong_dich"] == 2
    # nguon khong bi xoa
    assert hang.exists() and hang.read_text(encoding="utf-8").count("\n") == 2
    lines = tmp_mt5["hoan"].read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    d = json.loads(lines[0])
    assert d["hoan_may_nha"] is True and d["ten"].startswith("od_")
    # goi lai khong nhan ban
    r2 = MKD.danh_dau_hoan_may_nha()
    assert r2["them"] == 0 and r2["tong_dich"] == 2


def test_phat_hien_mt5_va_suppress_seeker_stall(tmp_mt5, monkeypatch):
    monkeypatch.setenv("BRAIN_MT5_KHA_DUNG", "0")
    from tru import evolution as EVO
    vh = {
        "luc": "2026-10-30 10:00:00",
        "tru": {
            "SEEKER": {"dung_im": True, "tre_giay": 200 * 60, "trang_thai": "nghi",
                       "lan_cuoi": "2026-10-30 06:00:00"},
            "QUANTLAB": {"dung_im": False, "tre_giay": 10, "trang_thai": "nghi"},
            "CAUKHO": {"dung_im": True, "tre_giay": 200 * 60, "trang_thai": "nghi"},
            "NGHI": {"dung_im": False, "tre_giay": 10, "trang_thai": "nghi"},
        },
        "so_toan_ven": {"lanh": True, "mo_ta": "ok"},
        "dia_trong_gb": 50,
        "mt5_tick_test": "GO",
        "seeker_ty_le_vong_rong": 0.0,
        "thanh_phan": {},
        "do_sau_nguon": {},
        "viec_loi": 0, "viec_cho": 0, "viec_treo": 0, "viec": {},
        "nguon": {},
        "tai_lieu": 0, "gia_thuyet": {},
        "tai_nguyen": {}, "watchdog": {},
        "seeker_da_boc": 0, "seeker_nang_suat_100": None,
        "seeker_gia_thuyet_tu_tai_lieu": 0, "seeker_ung_vien": 0,
        "seeker_tai_lieu_artifact": 0, "nghi_co_che_noi_sinh": 0,
        "nang_suat_nguon": {},
    }
    sk = {"fdr_trung_trong_epoch_song": 0, "fdr_mo_coi_moi": 0, "fdr_tong": 0,
          "so_gt_da_ket": 0, "khop_ba_tang": True, "pass_hom_nay": [],
          "pass_hom_nay_so": 0}
    # sk may need more — if KeyError, fill from real do_suc_khoe
    try:
        vd = EVO.phat_hien(vh, sk)
    except KeyError as e:
        sk_full = EVO.do_suc_khoe_day_chuyen()
        sk_full.update(sk)
        vd = EVO.phat_hien(vh, sk_full)
    mas = [v["ma"] for v in vd]
    assert "mt5_khong_kha_dung" in mas
    assert "tru_dung_im_SEEKER" not in mas
    assert "tru_dung_im_CAUKHO" not in mas


def test_quet_telegram_follow_degraded_khong_telethon(monkeypatch):
    """Khong telethon -> bo_qua/degraded ngay, khong treo ngan sach."""
    import tru.seeker as SK
    monkeypatch.setattr(SK, "TG", None)
    ra = SK.quet_telegram_follow(toi_da_kenh=1, so_bai_moi_kenh=1, ngan_sach_giay=5)
    assert ra.get("bo_qua") is True and ra.get("degraded") is True
    assert "telethon" in (ra.get("loi") or "").lower()
