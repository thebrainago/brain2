# -*- coding: utf-8 -*-
"""Bug 1: plan_hash lech (cua_so doi) khong duoc giet chu ky kham_pha."""
from __future__ import annotations

import pytest


def test_dang_ky_gia_thuyet_hoac_phien_ban(tmp_path, monkeypatch):
    import nhan.so as SO
    monkeypatch.setattr(SO, "DB", tmp_path / "t.db")
    SO.khoi_tao()

    ma = "EURCAD.H4.ma_cross_buy.vao0_test"
    gid1, ph1 = SO.dang_ky_gia_thuyet(
        ma=ma, co_che="c1", template="ma_cross_buy", tham_so={"n": 50},
        tai_san="EURCAD", khung="H4", cua_so="2011-01-01..2026-10-30",
        ho="xu_huong", nguon="test", tru_sinh="QUANTLAB")
    assert gid1 and len(ph1) == 16

    # cua_so doi — day la goc cua ValueError 30/10 (EURCAD.H4.ma_cross_buy...)
    gid2, ph2, ma2 = SO.dang_ky_gia_thuyet_hoac_phien_ban(
        ma=ma, co_che="c1", template="ma_cross_buy", tham_so={"n": 50},
        tai_san="EURCAD", khung="H4", cua_so="2007-05-07..2026-10-02",
        ho="xu_huong", nguon="test", tru_sinh="QUANTLAB")
    assert ph2 != ph1
    assert ma2 == f"{ma}.v{ph2}"
    assert gid2 is not None

    # Hanh vi cu van raise khi goi truc tiep
    with pytest.raises(ValueError, match="plan_hash"):
        SO.dang_ky_gia_thuyet(
            ma=ma, co_che="c1", template="ma_cross_buy", tham_so={"n": 50},
            tai_san="EURCAD", khung="H4", cua_so="2007-05-07..2026-10-02",
            ho="xu_huong", nguon="test", tru_sinh="QUANTLAB")

    # Cung plan moi goi lai → idempotent tren ma phien ban
    gid3, ph3, ma3 = SO.dang_ky_gia_thuyet_hoac_phien_ban(
        ma=ma, co_che="c1", template="ma_cross_buy", tham_so={"n": 50},
        tai_san="EURCAD", khung="H4", cua_so="2007-05-07..2026-10-02",
        ho="xu_huong", nguon="test", tru_sinh="QUANTLAB")
    assert ma3 == ma2 and ph3 == ph2 and gid3 == gid2


def test_dang_ky_sau_quet_bat_loi_tung_ung_vien(tmp_path, monkeypatch):
    """dang_ky_sau_quet khong de 1 ung vien plan_hash lech boom ca vong."""
    import nhan.so as SO
    monkeypatch.setattr(SO, "DB", tmp_path / "t2.db")
    SO.khoi_tao()

    ma_gt = "EURCAD.H4.ma_cross_buy.n50"
    SO.dang_ky_gia_thuyet(
        ma=ma_gt, co_che="c", template="ma_cross_buy", tham_so={"n": 50},
        tai_san="EURCAD", khung="H4", cua_so="2011-01-01..2026-10-30",
        ho="xu_huong", nguon="cu", tru_sinh="QUANTLAB")

    from tru import quantlab as QL
    ra = {
        "ma": "EURCAD", "khung": "H4",
        "cua_so": "2007-05-07..2026-10-02",
        "che_do": "test",
        "mua_giu_train": {"sharpe": 0.1},
        "_ung_vien": [{
            "mau": "ma_cross_buy", "co_che": "c", "ho": "xu_huong",
            "tham_so": {"n": 50}, "chi_so": {"sharpe": 0.5},
        }, {
            "mau": "ma_cross_buy", "co_che": "c2", "ho": "xu_huong",
            "tham_so": {"n": 99}, "chi_so": {"sharpe": 0.6},
        }],
        "_thieu_luc": [],
    }
    # Khong raise — ung vien 1 plan_hash lech → phien ban; ung vien 2 moi
    out = QL.dang_ky_sau_quet(ra)
    assert isinstance(out, dict)
    rows = SO.nhieu("SELECT ma FROM gia_thuyet WHERE ma LIKE ?", "EURCAD.H4.ma_cross_buy%")
    assert len(rows) >= 2
    # Phien ban cho ung vien lech cua_so
    assert any(".v" in r["ma"] for r in rows)
