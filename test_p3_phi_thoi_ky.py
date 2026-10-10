# -*- coding: utf-8 -*-
"""P3 (11/10/2026): swap THEO LENH (rollover nua dem, x3 thu Tu) + phi DUNG THOI KY
(swap theo thang tu chenh lai suat, spread theo nam khi bar co cot spread)."""
import unittest

import numpy as np
import pandas as pd

import vong_thu_nghiem as V
from nhan import chi_phi as CP
from nhan import lai_suat_fx as LS
from nhan import mo_phong as MP


def _df(bars, t0):
    idx = pd.date_range(t0, periods=len(bars), freq="h")
    return pd.DataFrame(bars, columns=["open", "high", "low", "close"], index=idx)


def _chan(n, ro, chieu=1, vao=(0,)):
    cho = np.zeros(n, dtype=bool)
    for k in vao:
        cho[k] = True
    return {"chieu": chieu, "cho": cho, "muc": None, "huong": None, "co": None,
            "loc": None, "sl": None, "tp": None, "keo": None, "giu": 1,
            "chan_boi": [], "dat": [], "ro": ro, "muc_lai": None, "phep_lai": None}


RO1 = {"lot_dau": 1.0, "hop_dong": 100000.0, "dinh": None, "cat_lo": None, "hedge": []}


class DemQuaDem(unittest.TestCase):
    def test_tuan_7_dem_thu_tu_x3_cuoi_tuan_0(self):
        idx = pd.date_range("2026-10-05 00:00", "2026-10-12 00:00", freq="h")  # T2 -> T2
        d = CP.dem_qua_dem(idx)
        self.assertEqual(d.sum(), 7.0)
        theo = {str(idx[i].date()): d[i] for i in np.nonzero(d)[0]}
        self.assertEqual(theo, {"2026-10-05": 1, "2026-10-06": 1, "2026-10-07": 3,
                                "2026-10-08": 1, "2026-10-09": 1})

    def test_khoang_trong_cuoi_tuan_va_trong_ngay(self):
        idx = pd.DatetimeIndex(["2026-10-09 22:00", "2026-10-09 23:00", "2026-10-12 00:00",
                                "2026-10-12 05:00"])
        self.assertEqual(list(CP.dem_qua_dem(idx)), [0.0, 1.0, 0.0, 0.0])

    def test_cfd_x3_thu_sau(self):
        idx = pd.date_range("2026-10-05 00:00", "2026-10-12 00:00", freq="h")
        d = CP.dem_qua_dem(idx, ngay_ba=4)
        self.assertEqual(d.sum(), 7.0)
        self.assertEqual(d[idx.get_loc(pd.Timestamp("2026-10-09 23:00"))], 3.0)


class PhiGiuNuaDem(unittest.TestCase):
    def test_lenh_trong_ngay_khong_tra_swap(self):
        idx = pd.date_range("2026-10-06 00:00", periods=48, freq="h")
        h = np.zeros(48)
        h[10:16] = 1.0                       # mo 10:00, dong 16:00 cung ngay
        cu = CP.MoHinhChiPhi(ma="EURUSD", phi_nam_mua=0.0365)
        moi = cu.bien_the()
        moi.kieu_qua_dem = "nua_dem"
        self.assertGreater(cu.phi_giu_mang(idx, h).sum(), 0)
        self.assertEqual(moi.phi_giu_mang(idx, h).sum(), 0.0)
        h2 = np.zeros(48)
        h2[20:30] = 1.0                      # qua nua dem thu Ba -> 1 dem
        self.assertAlmostEqual(moi.phi_giu_mang(idx, h2).sum(), 0.0365 / 365, places=12)

    def test_giu_dai_bang_lien_tuc(self):
        idx = pd.date_range("2026-01-05 00:00", "2026-03-30 00:00", freq="h")  # 12 tuan
        h = np.ones(len(idx))
        cu = CP.MoHinhChiPhi(ma="EURUSD", phi_nam_mua=0.02)
        moi = cu.bien_the()
        moi.kieu_qua_dem = "nua_dem"
        self.assertAlmostEqual(moi.phi_giu_mang(idx, h).sum(), cu.phi_giu_mang(idx, h).sum(),
                               places=10)


class SwapTheoThang(unittest.TestCase):
    def test_bang_lai_suat_co_eurusd(self):
        ch = LS.chenh_thang("EURUSD")
        self.assertIsNotNone(ch)
        self.assertIn("2003-06", ch)
        self.assertLess(ch["2003-06"], 0)            # 2003: EUR > USD -> MUA duoc nhan
        self.assertGreater(ch["2018-12"], 0.02)      # 2018: USD >> EUR
        self.assertIsNone(LS.chenh_thang("XAUUSD"))

    def test_ap_thoi_ky_giu_dung_phi_thang_do(self):
        idx = pd.date_range("2003-06-02", "2026-09-30", freq="D")
        df = pd.DataFrame({"open": 1.1, "high": 1.1, "low": 1.1, "close": 1.1}, index=idx)
        cp = CP.MoHinhChiPhi(ma="EURUSD", phi_nam_mua=0.02477, phi_nam_ban=-0.0045)
        m = CP.ap_thoi_ky(cp, df, ngay_do="2026-09")
        pm, pb = m.phi_nam_theo_bar(idx)
        k = idx.get_loc(pd.Timestamp("2026-09-15"))
        self.assertAlmostEqual(pm[k], 0.02477, places=10)
        self.assertAlmostEqual(pb[k], -0.0045, places=10)
        k3 = idx.get_loc(pd.Timestamp("2003-06-15"))
        self.assertLess(pm[k3], pb[k3])              # 2003 mua re hon ban
        self.assertAlmostEqual(pm[k3] + pb[k3], pm[k] + pb[k], places=10)  # markup giu nguyen
        self.assertEqual(m.kieu_qua_dem, "nua_dem")
        self.assertIn("p3", m.phien_ban())
        self.assertTrue(any("CHUA DO DUOC" in x for x in m.canh_bao))   # khong cot spread
        self.assertEqual(cp.kieu_qua_dem, "lien_tuc")                    # ban goc khong doi

    def test_ngay_do_doc_tu_canh_bao(self):
        cp = CP.MoHinhChiPhi(ma="EURUSD", phi_nam_mua=0.02, phi_nam_ban=0.0,
                             canh_bao=["phi qua dem do tu XM:EURUSD (2018-12-03 09:00:00), x"])
        df = pd.DataFrame({"close": [1.1]}, index=pd.DatetimeIndex(["2018-12-03"]))
        m = CP.ap_thoi_ky(cp, df)
        self.assertAlmostEqual(m.markup_mua, 0.02 - LS.chenh_thang("EURUSD")["2018-12"],
                               places=12)

    def test_cap_khong_co_lai_suat_khong_doan(self):
        cp = CP.MoHinhChiPhi(ma="XAUUSD", phi_nam_mua=0.075, phi_nam_ban=-0.02)
        df = pd.DataFrame({"close": [2000.0]}, index=pd.DatetimeIndex(["2020-01-01"]))
        m = CP.ap_thoi_ky(cp, df)
        self.assertEqual(m.chenh_lai_suat, {})
        pm, _ = m.phi_nam_theo_bar(df.index)
        self.assertEqual(pm[0], 0.075)

    def test_bien_the_phi_day_markup(self):
        cp = CP.MoHinhChiPhi(ma="EURUSD", phi_nam_mua=0.02, phi_nam_ban=0.0)
        idx = pd.date_range("2010-01-01", periods=5, freq="D")
        m = CP.ap_thoi_ky(cp, pd.DataFrame({"close": 1.3}, index=idx), ngay_do="2026-09")
        m2 = m.bien_the(phi_mua=0.03)
        self.assertAlmostEqual(m2.phi_nam_theo_bar(idx)[0][0] - m.phi_nam_theo_bar(idx)[0][0],
                               0.01, places=12)


class SpreadTheoNam(unittest.TestCase):
    def test_do_va_ap_spread_theo_nam(self):
        idx = pd.date_range("2019-01-01", "2020-12-31 23:00", freq="h")
        idx = idx[idx.dayofweek < 5]
        sp = np.where(idx.year == 2019, 20.0, 10.0)     # point
        df = pd.DataFrame({"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "spread": sp},
                          index=idx)
        cp = CP.MoHinhChiPhi(ma="EURUSD", spread_frac_chung=1.5e-4)
        m = CP.ap_thoi_ky(cp, df)
        self.assertEqual(m.spread_frac_theo_nam, {2019: 2e-4, 2020: 1e-4})
        s = m.spread_mang(idx)
        self.assertAlmostEqual(s[0], 2e-4, places=12)
        self.assertAlmostEqual(s[-1], 1e-4, places=12)
        np.testing.assert_allclose(cp.spread_mang(idx), 1.5e-4)        # goc khong doi


class SwapTheoLenhTrongTaiKhoan(unittest.TestCase):
    CP_ = CP.MoHinhChiPhi(ma="EURUSD", truot_gia_frac=1e-5, phi_nam_mua=0.0365,
                          kieu_qua_dem="nua_dem")

    def test_qua_dem_thu_tu_x3_tinh_tay(self):
        # mo thu Tu 2026-10-07 20:00, 10 bar -> qua nua dem thu Tu (x3) mot lan
        df = _df([(1.1, 1.1, 1.1, 1.1)] * 10, "2026-10-07 20:00")
        kq = MP.chay_he(df, [_chan(10, RO1)], self.CP_, ma="EURUSD", diem=1e-5,
                        tai_khoan={"von": 10000, "don_bay": 100, "stop_out": 0.5})
        tk = kq.chi_tiet["tai_khoan"]
        ky_vong = 1e5 * 1.1 * 0.0365 * 3 / 365
        self.assertAlmostEqual(tk["phi_qua_dem_usd"], ky_vong, places=9)
        self.assertAlmostEqual(tk["swap_lenh_mo_usd"], ky_vong, places=9)  # lenh con mo
        self.assertAlmostEqual(tk["von"], 10000 - tk["phi_truot_usd"] - ky_vong, places=9)

    def test_swap_vao_so_du_khi_dong_va_nhat_ky(self):
        # mua 1 lot, giu qua 2 dem (thu Hai, thu Ba), cat lo khi gia rot
        ro = dict(RO1, cat_lo=-500.0)
        bars = [(1.1, 1.1, 1.1, 1.1)] * 40 + [(1.094, 1.094, 1.094, 1.094)] * 3
        df = _df(bars, "2026-10-05 12:00")
        nk = []
        kq = MP.chay_he(df, [_chan(len(df), ro)], self.CP_, ma="EURUSD", diem=1e-5,
                        nhat_ky=nk, tai_khoan={"von": 10000, "don_bay": 100, "stop_out": 0.5})
        tk = kq.chi_tiet["tai_khoan"]
        self.assertEqual(nk[0]["ly_do"], "cat_lo")
        sw = 1e5 * 1.1 * 0.0365 * 2 / 365
        self.assertAlmostEqual(nk[0]["swap_usd"], sw, places=9)
        self.assertAlmostEqual(tk["phi_qua_dem_usd"], sw, places=9)
        self.assertNotIn("swap_lenh_mo_usd", tk)
        self.assertAlmostEqual(tk["von"], 10000 + nk[0]["loi_tien"] - sw - tk["phi_truot_usd"],
                               places=9)

    def test_stop_out_tinh_ca_swap_cua_lenh(self):
        # 1 lot, von 600: ky quy 1100, stop-out 50% = 550. Khong swap: gia 1.1 -> von rong
        # 600 - spread(0) = 600 > 550 -> khong stop-out. Swap rat lon (365 %/nam -> 1 %
        # notional/dem = 1100 USD/dem) -> qua 1 dem: von rong 600 - 1100 < 550 -> stop-out.
        cp = CP.MoHinhChiPhi(ma="EURUSD", phi_nam_mua=3.65, kieu_qua_dem="nua_dem")
        df = _df([(1.1, 1.1, 1.1, 1.1)] * 10, "2026-10-06 20:00")
        nk = []
        kq = MP.chay_he(df, [_chan(10, RO1)], cp, ma="EURUSD", diem=1e-5, nhat_ky=nk,
                        tai_khoan={"von": 1200, "don_bay": 100, "stop_out": 0.5})
        tk = kq.chi_tiet["tai_khoan"]
        self.assertEqual(tk["so_stop_out"], 1)
        self.assertEqual(nk[0]["ly_do"], "stop_out")
        self.assertAlmostEqual(tk["von"], 1200 - 1100.0, places=6)   # swap tru khi dong

    def test_khong_tai_khoan_loi_giong_tai_khoan_lon(self):
        df = V.du_lieu_gia_lap_duong(1500, seed=5)
        cp = V.mo_hinh_chi_phi(df)
        self.assertIn("p3", cp.phien_ban())
        ro = dict(RO1, cat_lo=-300.0, dinh={"moc": 200.0, "ti_le": 0.7})
        ch = [_chan(len(df), ro, vao=range(0, len(df), 50))]
        a = MP.chay_he(df, ch, cp, ma="EURUSD", diem=1e-5)
        b = MP.chay_he(df, ch, cp, ma="EURUSD", diem=1e-5,
                       tai_khoan={"von": 1e12, "don_bay": 100, "stop_out": 0.5})
        np.testing.assert_array_equal(a.loi, b.loi)

    def test_phi_cu_van_chay_duoc(self):
        df = V.du_lieu_gia_lap(300)
        cu = V.mo_hinh_chi_phi(df, phi_cu=True)
        self.assertEqual(cu.phien_ban(), f"cp{CP.THE_HE}")
        self.assertEqual(cu.kieu_qua_dem, "lien_tuc")


if __name__ == "__main__":
    unittest.main()
