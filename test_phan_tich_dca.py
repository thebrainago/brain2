# -*- coding: utf-8 -*-
"""Test phan_tich_dca + dual-track dich (khong can mang)."""
from __future__ import annotations

import json
from pathlib import Path

from nhan import phan_tich_dca as DCA
from nhan import dich_nguoc_tin_hieu as DN


def _trade(sym, ch, lot, gia, luc, loi, luc_ra=None, sl=None):
    return {
        "symbol": sym, "chieu": ch, "lot": lot, "gia_vao": gia, "gia_ra": gia + (0.001 if ch > 0 else -0.001),
        "luc_vao": luc, "luc_ra": luc_ra or luc.replace("T10:", "T18:"),
        "loi": loi, "sl": sl, "commission": 0, "swap": 0,
    }


def test_gom_basket_va_he_so():
    trades = [
        _trade("EURUSD", 1, 0.01, 1.1000, "2024-01-01T10:00:00Z", -5),
        _trade("EURUSD", 1, 0.02, 1.0950, "2024-01-01T12:00:00Z", -8),
        _trade("EURUSD", 1, 0.04, 1.0900, "2024-01-01T14:00:00Z", 20, luc_ra="2024-01-01T20:00:00Z"),
    ]
    b = DCA.gom_basket(trades)
    assert len(b) == 1
    assert b[0]["so_lop"] == 3
    assert b[0]["he_so_lot_tb"] == 2.0
    assert b[0]["co_recovery"] is True
    ho = DCA.thong_ke_dca(trades)
    assert ho["so_multi"] == 1
    assert ho["module"]["he_so_lot_med"] == 2.0
    assert "khoang_pip_med" in ho["module"]
    nhac = DCA.tao_nhac_dca(ho, nguon="test", he_id="demo")
    assert "dca_go_lenh" in nhac
    assert "toi_da_lop" in nhac or "toi_da_lop_p90" in nhac


def test_xep_hang_he():
    trades = [_trade("EURUSD", 1, 0.01, 1.1, "2024-01-01T10:00:00Z", 1) for _ in range(5)]
    x = DN.xep_hang_he(trades)
    assert x["ok"] is False  # <30 lenh, tuoi thieu


def test_track_auto_dca_flag():
    trades = [
        _trade("EURUSD", 1, 0.01, 1.1, "2024-01-01T10:00:00Z", -5, sl=None),
        _trade("EURUSD", 1, 0.02, 1.095, "2024-01-01T11:00:00Z", -5, sl=None),
        _trade("EURUSD", 1, 0.04, 1.09, "2024-01-01T12:00:00Z", 15, sl=None),
    ] * 15  # đủ số + martingale pattern
    # stamp unique times
    out = []
    for i, t in enumerate(trades):
        t = dict(t)
        t["luc_vao"] = "2024-01-%02dT%02d:00:00Z" % (1 + (i // 24) % 28, i % 24)
        t["luc_ra"] = "2024-01-%02dT%02d:30:00Z" % (1 + (i // 24) % 28, i % 24)
        out.append(t)
    loc = DN.loc_he(out, tu_choi_nguy_hiem=False)
    assert loc["martingale"] or loc["grid"] or loc["khong_sl"]


if __name__ == "__main__":
    test_gom_basket_va_he_so()
    test_xep_hang_he()
    test_track_auto_dca_flag()
    print("OK test_phan_tich_dca")
