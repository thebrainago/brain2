# -*- coding: utf-8 -*-
"""CONG GIU CHO LUOI/MARTINGALE (them 10/10/2026, sau 57657761).

Placebo random walk cho luoi Breakout5 Sharpe kiem DUONG 10/10 seed -> Sharpe/t
khong phai phep thu hop le cho he luoi. Cong moi (`vong_thu_nghiem.cong_luoi`):
song sot voi tai khoan KHAI BAO (ky quy + stop-out trong `mo_phong.chay_he`),
loi rong kiem > 0, va THANG gia duoc cung cau truc (chieu ngau nhien, cung ro).
"""
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

import vong_thu_nghiem as V
from nhan import doc_ma as DM
from nhan import ngu_phap as NP
from nhan import mo_phong as MP
from nhan import chi_phi as CP

MAU = Path(__file__).resolve().parent / "mau_thu"
B1 = MAU / "EA Snippets_Breakout_Breakout1.mq5"
B5 = MAU / "EA Snippets_Breakout_Breakout5.mq5"
KHONG_PHI = CP.MoHinhChiPhi(ma="EURUSD")
RO_DON = {"lot_dau": 1.0, "hop_dong": 100000.0, "dinh": None, "cat_lo": None, "hedge": []}


def _specs(p):
    return DM.doc_chien_luoc(p.read_text(errors="ignore"), nguon=p.name)["co_che"]


def _df(bars, t0="2024-01-02 08:00"):
    idx = pd.date_range(t0, periods=len(bars), freq="h")
    return pd.DataFrame(bars, columns=["open", "high", "low", "close"], index=idx)


def _chan(n, chieu=1, ro=RO_DON, vao=(0,)):
    cho = np.zeros(n, dtype=bool)
    for k in vao:
        cho[k] = True
    return {"chieu": chieu, "cho": cho, "muc": None, "huong": None, "co": None,
            "loc": None, "sl": None, "tp": None, "keo": None, "giu": 1,
            "chan_boi": [], "dat": [], "ro": ro, "muc_lai": None, "phep_lai": None}


class TaiKhoan(unittest.TestCase):
    def test_stop_out_chinh_xac_trong_bar(self):
        # mua 1 lot o 1.1 (ky quy 1100$); von 2000, 1:100, stop-out 50%:
        # 2000 + 1e5 (p - 1.1) = 0.5 * 1000 p  ->  p = 108000 / 99500
        df = _df([(1.1, 1.1, 1.1, 1.1), (1.1, 1.1, 1.08, 1.08), (1.08, 1.08, 1.08, 1.08)])
        nk = []
        kq = MP.chay_he(df, [_chan(3)], KHONG_PHI, ma="EURUSD", nhat_ky=nk, diem=1e-5,
                        tai_khoan={"von": 2000, "don_bay": 100, "stop_out": 0.5})
        p = 108000 / 99500
        self.assertEqual(nk[0]["ly_do"], "stop_out")
        self.assertAlmostEqual(nk[0]["gia_ra"], p, places=9)
        tk = kq.chi_tiet["tai_khoan"]
        self.assertEqual(tk["so_stop_out"], 1)
        self.assertAlmostEqual(tk["von"], 0.5 * 1000 * p, places=3)
        self.assertAlmostEqual(tk["muc_ky_quy_min"], 0.5, places=6)

    def test_stop_out_khi_gap_o_open(self):
        df = _df([(1.1, 1.1, 1.1, 1.1), (1.1, 1.1, 1.1, 1.1), (1.07, 1.07, 1.07, 1.07),
                  (1.07, 1.07, 1.07, 1.07)])
        nk = []
        kq = MP.chay_he(df, [_chan(4)], KHONG_PHI, ma="EURUSD", nhat_ky=nk, diem=1e-5,
                        tai_khoan={"von": 2000, "don_bay": 100, "stop_out": 0.5})
        self.assertEqual((nk[0]["ly_do"], nk[0]["bar_ra"]), ("stop_out", 2))
        self.assertAlmostEqual(nk[0]["gia_ra"], 1.07, places=12)
        self.assertEqual(kq.chi_tiet["tai_khoan"]["so_stop_out"], 1)

    def test_thieu_ky_quy_khong_vao(self):
        df = _df([(1.1, 1.1, 1.1, 1.1)] * 3)
        kq = MP.chay_he(df, [_chan(3)], KHONG_PHI, ma="EURUSD", diem=1e-5,
                        tai_khoan={"von": 500, "don_bay": 100, "stop_out": 0.5})
        self.assertEqual(kq.so_lenh, 0)
        self.assertGreaterEqual(kq.chi_tiet["tai_khoan"]["tu_choi_ky_quy"], 1)

    def test_lenh_luoi_bi_tu_choi_khi_thieu_ky_quy(self):
        ro = DM.doc_chien_luoc(B5.read_text(errors="ignore"), nguon="b5")["co_che"][0]["ro"]
        bars = [(1.1, 1.1, 1.1, 1.1), (1.1, 1.1, 1.099, 1.099),
                (1.099, 1.099, 1.098, 1.098), (1.098, 1.098, 1.098, 1.098)]
        df = _df(bars)
        nk = []
        # 0.02 lot can 22$ ky quy; them 0.03 -> 55$ > von 40 -> tu choi
        kq = MP.chay_he(df, [_chan(4, ro=ro)], KHONG_PHI, ma="EURUSD", nhat_ky=nk,
                        diem=1e-5, tai_khoan={"von": 40, "don_bay": 100, "stop_out": 0.2})
        self.assertNotIn("them", nk[0])
        self.assertGreaterEqual(kq.chi_tiet["tai_khoan"]["tu_choi_ky_quy"], 1)
        nk2 = []
        MP.chay_he(df, [_chan(4, ro=ro)], KHONG_PHI, ma="EURUSD", nhat_ky=nk2, diem=1e-5)
        self.assertIn("them", nk2[0])

    def test_khong_tai_khoan_va_tai_khoan_vo_han_giong_nhau(self):
        df = V.du_lieu_gia_lap_duong(1500, seed=3)
        sp = _specs(B5)
        cp = V.mo_hinh_chi_phi(df)
        a = MP.chay_he(df, [NP.sinh_chan(s, df) for s in sp], cp, ma="EURUSD")
        b = MP.chay_he(df, [NP.sinh_chan(s, df) for s in sp], cp, ma="EURUSD",
                       tai_khoan={"von": 1e12, "don_bay": 100, "stop_out": 0.5})
        self.assertNotIn("tai_khoan", a.chi_tiet)
        self.assertTrue(np.array_equal(a.loi, b.loi))
        self.assertEqual(b.chi_tiet["tai_khoan"]["so_stop_out"], 0)


class Placebo(unittest.TestCase):
    def setUp(self):
        self.df = V.du_lieu_gia_lap_duong(1200, seed=7)
        self.sp = _specs(B5)

    def test_chan_placebo_giu_cau_truc_doi_chieu(self):
        goc = [NP.sinh_chan(s, self.df) for s in self.sp]
        pl = V.chan_placebo(self.sp, self.df, np.random.default_rng(1))
        pl2 = V.chan_placebo(self.sp, self.df, np.random.default_rng(1))
        self.assertEqual(len(pl), len(goc))
        hop_goc = np.logical_or.reduce([c["cho"] for c in goc])
        hop_pl = np.logical_or.reduce([c["cho"] for c in pl])
        self.assertTrue(np.array_equal(hop_goc, hop_pl))       # cung thoi diem duoc vao
        self.assertTrue(np.all(sum(c["cho"].astype(int) for c in pl) <= 1))
        for g, c, c2 in zip(goc, pl, pl2):
            self.assertIs(c["ro"], g["ro"])                      # cung ro / luoi
            self.assertEqual(c["chieu"], g["chieu"])
            self.assertTrue(np.array_equal(c["cho"], c2["cho"]))  # tai lap theo seed
            lai = c["muc_lai"]
            dung = (self.df["close"].to_numpy() * 0 + 1.1)
            ok = np.array([MP_so(x, c["phep_lai"], m) for x, m in zip(dung, lai)])
            self.assertTrue(np.array_equal(ok, c["cho"]))         # vao lai = chieu dong xu
        frac = np.mean(pl[0]["cho"][hop_goc])
        self.assertTrue(0.4 < frac < 0.6)

    def test_chan_lenh_dung_trong_bar_chua_ho_tro(self):
        sp = _specs(B1)
        with self.assertRaises(NotImplementedError):
            V.chan_placebo(sp, self.df, np.random.default_rng(0))


def MP_so(a, phep, b):
    return {">": a > b, ">=": a >= b, "<": a < b, "<=": a <= b}[phep]


class CongLuoi(unittest.TestCase):
    def _r(self, x, so=0):
        return {"loi_log": x, "tai_khoan": {"so_stop_out": so, "chay": False}}

    def test_p_mot_phia(self):
        pl = [self._r(v) for v in np.linspace(-1, 1, 99)]
        c = V.cong_luoi(self._r(0), self._r(5.0), pl)
        self.assertTrue(c["dat"])
        self.assertAlmostEqual(c["p"], 0.01)
        c = V.cong_luoi(self._r(0), self._r(0.5), pl)
        self.assertFalse(c["dat"])
        self.assertAlmostEqual(c["p"], (1 + np.sum(np.linspace(-1, 1, 99) >= 0.5)) / 100)

    def test_stop_out_va_lo_rong_bi_loai(self):
        pl = [self._r(-1.0)] * 99
        self.assertIn("stop_out_kiem", V.cong_luoi(self._r(0), self._r(2, so=1), pl)["ly_do"])
        self.assertIn("stop_out_toi_uu", V.cong_luoi(self._r(0, so=2), self._r(2), pl)["ly_do"])
        c = V.cong_luoi(self._r(0), self._r(-0.5), pl)
        self.assertEqual(c["ly_do"], ["lo_rong_kiem"])

    def test_toi_uu_loai_tham_so_stop_out(self):
        self.assertEqual(V._diem({"sharpe": 9.0, "so_lenh": 999,
                                  "tai_khoan": {"so_stop_out": 1, "chay": False}}, 10), -1e9)
        self.assertEqual(V._diem({"sharpe": 1.0, "so_lenh": 999}, 10), 1.0)


class VongLap(unittest.TestCase):
    def test_luoi_qua_cong_luoi_he_khac_khong_doi(self):
        df = V.du_lieu_gia_lap_duong(2400, seed=11)
        r5 = V.chay_mot_file(B5, df, toi_uu_bat=False, n_placebo=9,
                             t_tu=-1e9, t_kiem=-1e9, lenh_min=1)
        he = [x for x in r5 if x.get("nhom")][0]
        self.assertTrue(he["luoi"])
        cl = he["cong_luoi"]
        self.assertEqual(cl["n_placebo"], 9)
        self.assertTrue(cl["dat_nguong_t_cu"])               # nguong cu tat -> cong luoi quyet
        self.assertEqual(he["giu_lai"], cl["dat"])
        self.assertIn("tai_khoan", he["tot_kiem"])
        r1 = V.chay_mot_file(B1, df, toi_uu_bat=False)
        for x in r1:
            self.assertNotIn("cong_luoi", x)
            self.assertNotIn("tai_khoan", x.get("tot_kiem", {}))

    def test_nguong_t_cu_van_ap_cho_luoi(self):
        df = V.du_lieu_gia_lap_duong(2400, seed=11)
        r5 = V.chay_mot_file(B5, df, toi_uu_bat=False, n_placebo=3, t_tu=1e9, t_kiem=1e9)
        he = [x for x in r5 if x.get("nhom")][0]
        self.assertFalse(he["cong_luoi"]["dat_nguong_t_cu"])
        self.assertFalse(he["giu_lai"])


if __name__ == "__main__":
    unittest.main()
