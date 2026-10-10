# -*- coding: utf-8 -*-
"""SYMBOL_VOLUME_MAX / SYMBOL_VOLUME_LIMIT + ro hedge qua cong tai khoan (10/10/2026 dem).

- `tai_khoan["lot_max"]`: san TU CHOI lenh co lot > lot_max (MT5 INVALID_VOLUME; EA
  khong chia lenh) - khong cat bot lot. Lenh luoi bi tu choi: chuoi lot khong tien.
- `tai_khoan["lot_tong_max"]`: tong lot CUNG chieu + lenh moi > muc -> tu choi.
- Ro hedge Breakout2/2-2/3 nay chay voi tai khoan + cong giu (placebo cung cau truc).
So tinh tay trong tung test.
"""
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd

import vong_thu_nghiem as V
from nhan import doc_ma as DM
from nhan import mo_phong as MP
from nhan import chi_phi as CP

MAU = Path(__file__).resolve().parent / "mau_thu"
B5 = MAU / "EA Snippets_Breakout_Breakout5.mq5"
B2 = MAU / "EA Snippets_Breakout_Breakout2.mq5"
KHONG_PHI = CP.MoHinhChiPhi(ma="EURUSD")
TK = {"von": 10000, "don_bay": 100, "stop_out": 0.5}


def _df(bars, t0="2024-01-02 08:00"):
    idx = pd.date_range(t0, periods=len(bars), freq="h")
    return pd.DataFrame(bars, columns=["open", "high", "low", "close"], index=idx)


def _ro(p):
    return DM.doc_chien_luoc(p.read_text(errors="ignore"), nguon=p.name)["co_che"][0]["ro"]


def _chan(n, ro, chieu=1, vao=(0,)):
    cho = np.zeros(n, dtype=bool)
    for k in vao:
        cho[k] = True
    return {"chieu": chieu, "cho": cho, "muc": None, "huong": None, "co": None,
            "loc": None, "sl": None, "tp": None, "keo": None, "giu": 1,
            "chan_boi": [], "dat": [], "ro": ro, "muc_lai": None, "phep_lai": None}


def _luoi_phang():
    # mua 0.02 @1.1000 (open bar 1); open bar 2 = 1.0995 <= 1.0997 -> them 0.03,
    # muc moi 1.0992; open bar 3,4,5 = 1.0990 <= 1.0992 -> buoc 0.04 (thu moi bar)
    return _df([(1.1, 1.1, 1.1, 1.1), (1.1, 1.1, 1.1, 1.1), (1.0995, 1.0995, 1.0995, 1.0995),
                (1.099, 1.099, 1.099, 1.099), (1.099, 1.099, 1.099, 1.099),
                (1.099, 1.099, 1.099, 1.099)])


def _chay(df, ro, tk, chieu=1):
    nk = []
    kq = MP.chay_he(df, [_chan(len(df), ro, chieu)], KHONG_PHI, ma="EURUSD", nhat_ky=nk,
                    diem=1e-5, tai_khoan=tk)
    return kq, nk


class LotMax(unittest.TestCase):
    def test_khong_gioi_han_nhu_cu(self):
        ro = _ro(B5)
        self.assertEqual(list(ro["luoi"]["lot"][:2]), [0.03, 0.04])
        kq0, nk0 = _chay(_luoi_phang(), ro, dict(TK))
        kq1, nk1 = _chay(_luoi_phang(), ro, dict(TK, lot_max=None, lot_tong_max=0))
        self.assertEqual([x["lot"] for x in nk0[0]["them"]], [0.03, 0.04])
        self.assertEqual(nk0, nk1)
        np.testing.assert_array_equal(kq0.loi, kq1.loi)
        self.assertEqual(kq0.chi_tiet["tai_khoan"]["tu_choi_lot_max"], 0)

    def test_lot_max_tu_choi_buoc_luoi_va_ket(self):
        # lot_max 0.035: 0.02 va 0.03 qua; 0.04 bi tu choi o bar 3, 4, 5 (thu lai moi bar,
        # chuoi lot khong tien) -> 3 lan tu choi, ro giu 2 lenh
        kq, nk = _chay(_luoi_phang(), _ro(B5), dict(TK, lot_max=0.035))
        tk = kq.chi_tiet["tai_khoan"]
        self.assertEqual([x["lot"] for x in nk[0]["them"]], [0.03])
        self.assertEqual(tk["tu_choi_lot_max"], 3)
        self.assertEqual(tk["tu_choi_ky_quy"], 0)
        self.assertEqual(kq.chi_tiet["luoi"]["max_lot"], 0.03)

    def test_lot_max_tu_choi_lenh_dau(self):
        kq, nk = _chay(_luoi_phang(), _ro(B5), dict(TK, lot_max=0.01))
        self.assertEqual(kq.so_lenh, 0)
        self.assertEqual(nk, [])
        self.assertEqual(kq.chi_tiet["tai_khoan"]["tu_choi_lot_max"], 1)   # cho chi bar 0
        self.assertEqual(float(np.abs(kq.loi).sum()), 0.0)

    def test_lot_tong_max_cung_chieu(self):
        # 0.02 + 0.03 = 0.05 <= 0.05 qua; + 0.04 = 0.09 > 0.05 -> tu choi (3 bar)
        kq, nk = _chay(_luoi_phang(), _ro(B5), dict(TK, lot_tong_max=0.05))
        self.assertEqual([x["lot"] for x in nk[0]["them"]], [0.03])
        self.assertEqual(kq.chi_tiet["tai_khoan"]["tu_choi_lot_max"], 3)
        # muc 0.0499 -> ca 0.03 cung bi tu choi (0.05 > 0.0499): 4 lan (bar 2..5)
        kq, nk = _chay(_luoi_phang(), _ro(B5), dict(TK, lot_tong_max=0.0499))
        self.assertNotIn("them", nk[0])
        self.assertEqual(kq.chi_tiet["tai_khoan"]["tu_choi_lot_max"], 4)

    def test_hedge_b2_bi_tu_choi_khi_vuot_lot_max(self):
        ro = _ro(B2)
        h = ro["hedge"][0]
        self.assertEqual((h["kich"], h["khoang_diem"], h["lot"]), ("diem", 300.0, 0.4))
        # mua 0.1 @1.1000 (khong phi, spread 0) -> hedge ban 0.4 khi BID <= 1.0970.
        # Bar 2 xuong 1.0965: lo 35 USD > cat_lo -120 -> chua cat.
        df = _df([(1.1, 1.1, 1.1, 1.1), (1.1, 1.1, 1.1, 1.1),
                  (1.1, 1.1, 1.0965, 1.0965), (1.0965, 1.0965, 1.0965, 1.0965)])
        kq, nk = _chay(df, ro, dict(TK))
        self.assertEqual(len(nk[0]["hedge"]), 1)
        self.assertAlmostEqual(nk[0]["hedge"][0]["gia"], 1.097, places=9)
        kq, nk = _chay(df, ro, dict(TK, lot_max=0.3))
        self.assertNotIn("hedge", nk[0])
        self.assertGreaterEqual(kq.chi_tiet["tai_khoan"]["tu_choi_lot_max"], 1)
        # khong co hedge: ro 1 lenh 0.1 lot; lo tha noi cuoi = 0.1*1e5*0.0035 = 35 USD
        self.assertAlmostEqual(kq.chi_tiet["tai_khoan"]["von_rong_min"], 10000 - 35.0, places=6)


class CongRoHedge(unittest.TestCase):
    def test_la_ro(self):
        r = DM.doc_chien_luoc(B2.read_text(errors="ignore"), nguon=B2.name)
        sp = r["co_che"]
        self.assertTrue(V.la_ro(sp))
        self.assertFalse(V.la_luoi(sp))
        self.assertFalse(V.la_ro([{"ten": "x"}]))

    def test_b2_qua_cong_tai_khoan_va_placebo(self):
        df = V.du_lieu_gia_lap_duong(24 * 120, seed=3)
        ra = V.chay_mot_file(B2, df, toi_uu_bat=False, n_placebo=5)
        he = [x for x in ra if x.get("nhom")]
        self.assertEqual(len(he), 1)
        x = he[0]
        self.assertNotIn("loi", x)
        self.assertEqual(x["loai_ro"], "hedge")
        self.assertIn("tai_khoan", x["tot_kiem"])
        self.assertEqual(x["tai_khoan_khai_bao"]["lot_max"], 100.0)
        cl = x["cong_luoi"]
        self.assertEqual(cl["n_placebo"], 5)
        self.assertIsNone(cl["placebo_bo_qua"])
        self.assertIsNotNone(cl["p"])
        # cong chi SIET: giu => dat nguong t cu VA dat cong
        self.assertEqual(x["giu_lai"], bool(cl["dat_nguong_t_cu"] and cl["dat"]))

    def test_placebo_khong_lam_duoc_thi_bo_qua_co_ly_do(self):
        df = V.du_lieu_gia_lap_duong(24 * 120, seed=3)
        with mock.patch.object(V, "placebo_cung_cau_truc",
                               side_effect=NotImplementedError("chan lenh dung trong bar")):
            ra = V.chay_mot_file(B2, df, toi_uu_bat=False, n_placebo=5)
        x = [x for x in ra if x.get("nhom")][0]
        cl = x["cong_luoi"]
        self.assertEqual(cl["placebo_bo_qua"], "chan lenh dung trong bar")
        self.assertIsNone(cl["p"])
        self.assertFalse(any(l.startswith("khong_thang_placebo") for l in cl["ly_do"]))
        self.assertEqual(x["giu_lai"], bool(cl["dat_nguong_t_cu"] and cl["dat"]))

    def test_bo_qua_placebo_khong_noi_cac_dieu_kien_khac(self):
        tu = {"loi_log": 0.1, "tai_khoan": {"so_stop_out": 1, "chay": False}}
        kiem = {"loi_log": -0.2, "tai_khoan": {"so_stop_out": 0, "chay": False,
                                               "bar_stop_out_dau": None, "so_bar": 100}}
        cl = V.cong_luoi(tu, kiem, [], nam_kiem=1.0, placebo_bo_qua="x")
        self.assertFalse(cl["dat"])
        self.assertEqual(cl["ly_do"], ["stop_out_toi_uu", "lo_rong_kiem"])
        # khong bo qua + khong placebo -> p = 1 -> van loai
        cl = V.cong_luoi({"loi_log": 1}, {"loi_log": 1}, [], nam_kiem=1.0)
        self.assertIn("khong_thang_placebo p=1.000>0.05", cl["ly_do"])


if __name__ == "__main__":
    unittest.main()
