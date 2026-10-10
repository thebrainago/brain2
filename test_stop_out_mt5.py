# -*- coding: utf-8 -*-
"""STOP-OUT KIEU MT5 + phi trong so du (10/10/2026 toi).

Truoc: cham stop-out -> dong CA ro mot luc. MT5 dong lenh LO NHAT truoc, tung lenh,
den khi muc ky quy > stop_out; lenh con lai van chay. Truot gia + qua dem nay tru
thang vao von (truoc chi nam trong chuoi `loi`). `tai_khoan=None` khong doi.
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
B5 = MAU / "EA Snippets_Breakout_Breakout5.mq5"
KHONG_PHI = CP.MoHinhChiPhi(ma="EURUSD")


def _df(bars, t0="2024-01-02 08:00"):
    idx = pd.date_range(t0, periods=len(bars), freq="h")
    return pd.DataFrame(bars, columns=["open", "high", "low", "close"], index=idx)


def _ro_b5():
    return DM.doc_chien_luoc(B5.read_text(errors="ignore"), nguon="b5")["co_che"][0]["ro"]


def _chan(n, ro, chieu=1, vao=(0,)):
    cho = np.zeros(n, dtype=bool)
    for k in vao:
        cho[k] = True
    return {"chieu": chieu, "cho": cho, "muc": None, "huong": None, "co": None,
            "loc": None, "sl": None, "tp": None, "keo": None, "giu": 1,
            "chan_boi": [], "dat": [], "ro": ro, "muc_lai": None, "phep_lai": None}


def _luoi_3_lenh(gap):
    # vao mua 0.02 @1.1000; open bar 2 = 1.0995 <= 1.0997 -> them 0.03; open bar 3 =
    # 1.0990 <= 1.0992 -> them 0.04; bar 4 gap xuong `gap`.
    return _df([(1.1, 1.1, 1.1, 1.1), (1.1, 1.1, 1.0995, 1.0995),
                (1.0995, 1.0995, 1.099, 1.099), (1.099, 1.099, 1.099, 1.099),
                (gap, gap, gap, gap), (gap, gap, gap, gap)])


class StopOutTungLenh(unittest.TestCase):
    def test_dong_lenh_lo_nhat_truoc_ro_con_lai_tiep_tuc(self):
        ro = _ro_b5()
        self.assertEqual(list(ro["luoi"]["lot"][:2]), [0.03, 0.04])
        df = _luoi_3_lenh(1.088)
        nk = []
        kq = MP.chay_he(df, [_chan(len(df), ro)], KHONG_PHI, ma="EURUSD", nhat_ky=nk,
                        diem=1e-5, tai_khoan={"von": 150, "don_bay": 100, "stop_out": 0.5})
        tk = kq.chi_tiet["tai_khoan"]
        self.assertEqual([x["lot"] for x in nk[0]["them"]], [0.03, 0.04])
        # tai 1.088: lo -24 / -34.5 / -44 -> von rong 47.5 <= 0.5*90*1.088 = 48.96
        # MT5 dong 0.04 (lo nhat): von 106, ky quy 0.05 lot -> 47.5 > 27.2 -> dung
        self.assertEqual(len(nk[0]["stop_out_le"]), 1)
        le = nk[0]["stop_out_le"][0]
        self.assertEqual((le["lot"], le["bar"]), (0.04, 4))
        self.assertAlmostEqual(le["loi_tien"], -44.0, places=6)
        self.assertNotIn("ly_do", nk[0])               # ro van mo
        self.assertEqual((tk["so_stop_out"], tk["so_lenh_stop_out"]), (1, 1))
        self.assertAlmostEqual(tk["von"], 106.0, places=6)
        self.assertFalse(tk["chay"])
        self.assertGreaterEqual(tk["tu_choi_ky_quy"], 1)   # lenh luoi 0.06 thieu ky quy

    def test_dong_lien_tiep_den_het_ro(self):
        ro = _ro_b5()
        df = _luoi_3_lenh(1.075)
        nk = []
        kq = MP.chay_he(df, [_chan(len(df), ro)], KHONG_PHI, ma="EURUSD", nhat_ky=nk,
                        diem=1e-5, tai_khoan={"von": 150, "don_bay": 100, "stop_out": 0.5})
        tk = kq.chi_tiet["tai_khoan"]
        self.assertEqual([x["lot"] for x in nk[0]["stop_out_le"]], [0.04, 0.03])
        self.assertEqual(nk[0]["ly_do"], "stop_out")
        self.assertEqual((tk["so_stop_out"], tk["so_lenh_stop_out"]), (1, 3))
        self.assertAlmostEqual(tk["von"], 150 - 50 - 73.5 - 96, places=6)
        self.assertTrue(tk["chay"])

    def test_tong_loi_tien_khop_so_du(self):
        """Bao toan: von cuoi = von dau + loi tien moi lenh da dong (khong phi)."""
        ro = _ro_b5()
        df = _luoi_3_lenh(1.088)
        nk = []
        kq = MP.chay_he(df, [_chan(len(df), ro)], KHONG_PHI, ma="EURUSD", nhat_ky=nk,
                        diem=1e-5, tai_khoan={"von": 150, "don_bay": 100, "stop_out": 0.5})
        da_dong = sum(x["loi_tien"] for x in nk[0]["stop_out_le"])
        self.assertAlmostEqual(kq.chi_tiet["tai_khoan"]["von"], 150 + da_dong, places=9)


class PhiTrongSoDu(unittest.TestCase):
    def test_truot_va_qua_dem_tru_vao_von(self):
        cp = CP.MoHinhChiPhi(ma="EURUSD", truot_gia_frac=1e-5, phi_nam_mua=0.0365)
        ro = {"lot_dau": 1.0, "hop_dong": 100000.0, "dinh": None, "cat_lo": None,
              "hedge": []}
        df = _df([(1.1, 1.1, 1.1, 1.1)] * 30)
        kq = MP.chay_he(df, [_chan(30, ro)], cp, ma="EURUSD", diem=1e-5,
                        tai_khoan={"von": 10000, "don_bay": 100, "stop_out": 0.5})
        tk = kq.chi_tiet["tai_khoan"]
        self.assertAlmostEqual(tk["phi_truot_usd"], 1e5 * 1.1 * 1e-5, places=9)  # chi luc mo
        sw = cp.phi_giu_mang(df.index, np.ones(30), None)
        ky_vong = sum(1e5 * 1.1 * sw[j] for j in range(1, 29))
        self.assertGreater(ky_vong, 0)
        self.assertAlmostEqual(tk["phi_qua_dem_usd"], ky_vong, places=9)
        self.assertAlmostEqual(tk["von"], 10000 - tk["phi_truot_usd"] - ky_vong, places=9)

    def test_khong_tai_khoan_khong_doi_va_loi_khong_doi(self):
        df = V.du_lieu_gia_lap_duong(2000, seed=11)
        sp = DM.doc_chien_luoc(B5.read_text(errors="ignore"), nguon="b5")["co_che"]
        cp = V.mo_hinh_chi_phi(df)
        a = MP.chay_he(df, [NP.sinh_chan(s, df) for s in sp], cp, ma="EURUSD")
        b = MP.chay_he(df, [NP.sinh_chan(s, df) for s in sp], cp, ma="EURUSD",
                       tai_khoan={"von": 1e12, "don_bay": 100, "stop_out": 0.5})
        self.assertNotIn("tai_khoan", a.chi_tiet)
        self.assertTrue(np.array_equal(a.loi, b.loi))
        self.assertGreater(b.chi_tiet["tai_khoan"]["phi_truot_usd"], 0)


class XacSuatChayNam(unittest.TestCase):
    @staticmethod
    def _r(x, so=0):
        return {"loi_log": x, "tai_khoan": {"so_stop_out": so, "chay": False}}

    def test_ti_le_poisson(self):
        c = V.ti_le_chay_nam([self._r(0, 1), self._r(0, 0), self._r(0, 1), self._r(0)], 2.5)
        self.assertEqual((c["so_stop_out"], c["nam_phoi_nhiem"]), (2, 10.0))
        self.assertAlmostEqual(c["p_nam"], 1 - np.exp(-0.2), places=5)
        self.assertGreater(c["p_tren95"], c["p_nam"])
        # chi tinh stop-out DAU moi lan chay; phoi nhiem dung o bar stop-out dau
        r = {"loi_log": 0, "tai_khoan": {"so_stop_out": 7, "chay": True,
                                         "bar_stop_out_dau": 250, "so_bar": 1000}}
        c2 = V.ti_le_chay_nam([r, self._r(0)], 4.0)
        self.assertEqual((c2["so_stop_out"], c2["nam_phoi_nhiem"]), (1, 5.0))

    def test_cong_chi_siet_them(self):
        pl = [self._r(-1.0)] * 99
        # khong co nam_kiem: hanh vi cu
        self.assertTrue(V.cong_luoi(self._r(1), self._r(1), pl)["dat"])
        # placebo khong stop-out -> van dat
        cl = V.cong_luoi(self._r(1), self._r(1), pl, nam_kiem=5.0)
        self.assertTrue(cl["dat"])
        self.assertEqual(cl["chay_nam"]["p_nam"], 0.0)
        # cau truc chay: 30 stop-out / (99 x 5 nam) -> 5,9%/nam > 5% -> loai, du that song
        pl2 = [self._r(-1.0, 1)] * 30 + [self._r(-1.0)] * 69
        cl2 = V.cong_luoi(self._r(1), self._r(1), pl2, nam_kiem=5.0)
        self.assertFalse(cl2["dat"])
        self.assertTrue(any(x.startswith("xac_suat_chay_nam") for x in cl2["ly_do"]))
        # nguong 1 = tat (chi de do nhay)
        self.assertTrue(V.cong_luoi(self._r(1), self._r(1), pl2, nam_kiem=5.0,
                                    p_chay_nam=1.0)["dat"])


if __name__ == "__main__":
    unittest.main()
