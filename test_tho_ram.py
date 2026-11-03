# -*- coding: utf-8 -*-
"""Thợ MT5 chỉ nhận việc mới khi RAM trống > ngưỡng; MaxBars; dọn Tester/cache."""
import os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "may_nha"))
import tho_mt5 as T


def test_chan_khi_ram_thap(monkeypatch):
    monkeypatch.setenv("BRAIN_RAM_TRONG_MIN_GB", "8")
    assert T.du_ram_nhan_viec(do=lambda: 5.0)[0] is False
    assert T.du_ram_nhan_viec(do=lambda: 9.0)[0] is True
    assert T.du_ram_nhan_viec(do=lambda: None)[0] is True


def test_cho_du_ram_doi_roi_nhan(monkeypatch):
    monkeypatch.setenv("BRAIN_RAM_TRONG_MIN_GB", "8")
    gt = iter([2.0, 7.9, 8.5]); ngu = []
    assert T.cho_du_ram(ngu=ngu.append, do=lambda: next(gt), buoc=60)
    assert ngu == [60, 60]
    assert not T.cho_du_ram(ngu=lambda s: None, do=lambda: 1.0, toi_da=120)


def test_ram_that_do_duoc():
    g = T.ram_trong_gb()
    assert g is None or g > 0


def test_maxbars(tmp_path):
    c = tmp_path / "config"; c.mkdir()
    f = c / "common.ini"
    f.write_text("[Common]\r\nLogin=1\r\n[Charts]\r\nMaxBars=100000000\r\nX=1\r\n", encoding="utf-16")
    assert T.gioi_han_maxbars(tmp_path, 50000)
    t = f.read_text(encoding="utf-16")
    assert "MaxBars=50000" in t and "100000000" not in t and "Login=1" in t
    assert not T.gioi_han_maxbars(tmp_path, 50000)
    f.write_text("[Common]\nLogin=1\n", encoding="utf-8")
    assert T.gioi_han_maxbars(tmp_path, 50000)
    assert "[Charts]" in f.read_text(encoding="utf-8")
    assert not T.gioi_han_maxbars(tmp_path / "khong", 1)


def test_don_cache(tmp_path):
    d = tmp_path / "Tester" / "cache"; d.mkdir(parents=True)
    cu, moi = d / "a.tst", d / "b.tst"
    cu.write_text("x"); moi.write_text("y")
    os.utime(cu, (time.time() - 5 * 86400,) * 2)
    assert T.don_cache_tester(tmp_path, 2) == 1
    assert not cu.exists() and moi.exists()
