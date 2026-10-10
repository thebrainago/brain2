# -*- coding: utf-8 -*-
"""Lop doc MQL5 cua `nhan/doc_ma.py` (them 10/10/2026) tren bo `mau_thu/`.

Kiem NGHIA, khong chi dem: mot co che rut ra phai dung chieu, mang du bo loc
cua tac gia, va KHONG duoc rut tu lenh hedge phu thuoc gia vao lenh.
"""
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from nhan import doc_ma as DM
from nhan import ngu_phap as NP

MAU = Path(__file__).resolve().parent / "mau_thu"


def _doc(ten):
    return DM.doc_chien_luoc((MAU / ten).read_text(errors="ignore"), nguon=ten)


def _h1(n=24 * 60, seed=3):
    rng = np.random.default_rng(seed)
    p = 1.1 + np.cumsum(rng.normal(0, 0.0007, n))
    idx = pd.date_range("2022-01-03", periods=n, freq="h")
    return pd.DataFrame({"open": p, "high": p + 0.0004, "low": p - 0.0004,
                         "close": p, "tick_volume": 100}, index=idx)


class PhaVoPhien(unittest.TestCase):
    def test_tach_mua_ban_theo_nhanh(self):
        d = _doc("EA Snippets_Breakout_Breakout1.mq5")
        self.assertEqual(d["so_vao_lenh"], 1)
        self.assertEqual(sorted(c["chieu"] for c in d["co_che"]), [-1, 1])

    def test_giu_bo_loc_gio_va_ma_cua_tac_gia(self):
        mua = [c for c in _doc("EA Snippets_Breakout_Breakout1.mq5")["co_che"]
               if c["chieu"] == 1][0]
        vao = mua["vao"]
        self.assertEqual(vao[0]["phai"], {"chi_bao": "cao_trong_gio",
                                          "gio_tu": 5, "gio_den": 8})
        self.assertIn({"trai": {"chi_bao": "gio"}, "phep": ">=",
                       "phai": {"hang": 9.0}}, vao)
        # MaValues[0] sau CopyBuffer(...,0,10,...) KHONG dao chieu = bar cu nhat
        self.assertIn({"trai": {"chi_bao": "gia", "cot": "close"}, "phep": ">=",
                       "phai": {"chi_bao": "tre", "n": 9,
                                "cua": {"chi_bao": "sma", "n": 50}}}, vao)

    def test_khong_rut_lenh_hedge(self):
        d = _doc("EA Snippets_Breakout_Breakout2.mq5")
        self.assertEqual(d["so_vao_lenh"], 3)
        self.assertEqual(d["so_vao_lenh_co_co_che"], 1)

    def test_ham_tu_viet_khong_co_ma_thi_bo(self):
        self.assertEqual(_doc("EA Snippets_Pivots_Pivots1.mq5")["co_che"], [])

    def test_moi_co_che_qua_kiem_va_khong_nhin_truoc(self):
        df = _h1()
        for ten in ("EA Snippets_Breakout_Breakout1.mq5",
                    "EA Snippets_Breakout_Breakout2.mq5"):
            for c in _doc(ten)["co_che"]:
                self.assertEqual(NP.kiem_khai_bao(c), [])
                ok, ly = NP.kiem_khong_nhin_truoc(c, df)
                self.assertTrue(ok, ly)


class HamTinHieu(unittest.TestCase):
    def test_getsignal_tra_1_va_tru_1(self):
        d = _doc("mql5-pro_assets_EA_Template.mq5")
        mua = [c for c in d["co_che"] if c["chieu"] == 1][0]
        self.assertEqual(mua["vao"], [{
            "trai": {"chi_bao": "tre", "cua": {"chi_bao": "gia", "cot": "close"}, "n": 1},
            "phep": ">",
            "phai": {"chi_bao": "tre", "cua": {"chi_bao": "gia", "cot": "close"}, "n": 2}}])


class CaoTrongGio(unittest.TestCase):
    def test_nan_truoc_khi_khung_dong(self):
        df = _h1(48)
        s = NP.toan_hang(df, {"chi_bao": "cao_trong_gio", "gio_tu": 0, "gio_den": 7})
        self.assertTrue(s[df.index.hour <= 7].isna().all())
        ngay0 = df.index.normalize() == df.index[0].normalize()
        self.assertAlmostEqual(s[ngay0 & (df.index.hour == 8)].iloc[0],
                               df["high"][ngay0 & (df.index.hour <= 7)].max())



class VongThuNghiem(unittest.TestCase):
    def test_chay_het_va_toi_uu_khong_loi(self):
        import vong_thu_nghiem as V
        df = V.du_lieu_gia_lap(24 * 120, seed=7)
        ra = V.chay_mot_file(MAU / "EA Snippets_Breakout_Breakout1.mq5", df)
        self.assertEqual(len(ra), 2)
        for x in ra:
            self.assertNotIn("loi", x)
            self.assertIn("tham_so_tot", x)
            self.assertIn("t_kiem", x)


if __name__ == "__main__":
    unittest.main()
