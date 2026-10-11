# -*- coding: utf-8 -*-
"""Loc nhanh B1/B2/B3 (11/10/2026, goi the-brain C11/B2/B9) - CHI NHAN, khong doi GIU/BO."""
import inspect

import numpy as np
import pandas as pd

import vong_thu_nghiem as V
from nhan import chi_phi as CP


def _df(n=200, bien_do=0.0010, gia=1.1):
    idx = pd.date_range("2024-01-01", periods=n, freq="h")
    c = np.full(n, gia)
    return pd.DataFrame({"open": c, "high": c + bien_do / 2, "low": c - bien_do / 2,
                         "close": c}, index=idx)


def test_loc_phi_tran_8_bps():
    df = _df()
    n = V.nhan_loc_phi(CP.MoHinhChiPhi(ma="X", spread_frac_chung=9e-4), df)
    assert n["loai_truoc_xep_hang"] is True and abs(n["spread_bps"] - 9.0) < 1e-9
    assert "BỎ TRƯỚC XẾP HẠNG" in V._chu_loc_phi(n) and "không đổi GIỮ/BỎ" in V._chu_loc_phi(n)
    n = V.nhan_loc_phi(CP.MoHinhChiPhi(ma="X", spread_frac_chung=1.6e-4), df)
    assert n["loai_truoc_xep_hang"] is False
    assert abs(n["spread_tren_bien_do"] - 1.6 / (0.001 / 1.1 * 1e4)) < 1e-3


def test_loc_phi_khong_phi_chua_do():
    n = V.nhan_loc_phi(CP.MoHinhChiPhi(ma="X"), _df(), khong_phi=True)
    assert n["loai_truoc_xep_hang"] is None and "CHƯA ĐO ĐƯỢC" in V._chu_loc_phi(n)


def _luoi(buoc_diem):
    return [{"ro": {"luoi": {"lot": [0.01], "buoc": {"mua": ["BID", buoc_diem],
                                                     "ban": ["ASK", buoc_diem]}}}}]


def test_phan_giai_buoc_nho_chua_do():
    df = _df(bien_do=0.0010)                                # 100 diem 5 so
    n = V.nhan_phan_giai(_luoi(150), df, diem=1e-5)         # 1,5x < 2
    assert n["do_duoc"] is False and abs(n["ty_le"] - 1.5) < 1e-9
    assert "CHƯA ĐO ĐƯỢC" in V._chu_phan_giai(n)
    assert V.nhan_phan_giai(_luoi(250), df, diem=1e-5)["do_duoc"] is True


def test_phan_giai_hedge_va_khong_co_khoang():
    sp = [{"ro": {"hedge": [{"kich": "diem", "khoang_diem": 50, "lot": 0.1, "khi_so_lenh": 1}]}}]
    assert V.nhan_phan_giai(sp, _df(), diem=1e-5)["do_duoc"] is False
    assert V.nhan_phan_giai([{"ro": {"hedge": [{"kich": "loi", "nguong": -5}]}}], _df()) is None


def test_lo_treo_va_phi_an():
    k = {"lo_treo_max_usd": 2965.0, "tai_khoan": {"von_dau": 10000.0},
         "loi_log": 0.05, "loi_log_gop": 0.2}
    n = V.nhan_lo_treo(k)
    assert n == {"usd": 2965.0, "pct_von": 29.65}
    assert "29.6% vốn" in V._chu_lo_treo(n) or "29.7% vốn" in V._chu_lo_treo(n)
    assert "phí ăn 75% lãi gộp" in V._chu_phi_an(k)
    assert "lãi gộp ≤ 0" in V._chu_phi_an({"loi_log": -0.1, "loi_log_gop": -0.05})
    assert V.nhan_lo_treo({"loi_log": 0.1}) is None


def test_danh_gia_nhom_co_lo_treo_khi_co_ro():
    """Engine that: luoi Breakout5 tren gia gia lap -> co lo_treo_max_usd > 0, gop/rong; buoc
    30 diem < 2x bien do nen -> nhan phan giai CHUA DO DUOC."""
    from pathlib import Path
    from nhan import doc_ma as DM
    f = Path(V.LAB) / "mau_thu" / "EA Snippets_Breakout_Breakout5.mq5"
    cc = DM.doc_chien_luoc(f.read_text(encoding="utf-8", errors="ignore"), nguon=f.name)
    specs = [sp for sp in cc["co_che"] if sp.get("ro")]
    assert specs
    df = V.du_lieu_gia_lap(24 * 60, 3, "H1")
    r = V.danh_gia_nhom(specs, df, "H1", tai_khoan=dict(V.TAI_KHOAN_MAC_DINH))
    assert r["lo_treo_max_usd"] > 0 and "loi_log_gop" in r
    assert r["lo_treo_max_usd"] >= r["luoi"]["lo_tha_noi_max_usd"] - 1.0
    assert V.nhan_phan_giai(specs, df)["do_duoc"] is False


def test_chi_nhan_khong_doi_giu():
    src = inspect.getsource(V._chay_nhom)
    assert 'dong["giu_lai"] = bool(dat_cu and cl["dat"])' in src
    for k in ("lo_treo", "phan_giai"):
        dong_k = [ln for ln in src.splitlines() if f'dong["{k}"]' in ln]
        assert dong_k and all("giu_lai" not in ln for ln in dong_k)
