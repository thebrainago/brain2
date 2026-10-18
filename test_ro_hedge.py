# -*- coding: utf-8 -*-
"""RO LENH: hedge / chot dinh / cat lo theo TONG loi lo (them 10/10/2026, vong "ro hedge").

Ba lop: (1) `ro_mql.doc_ro` doc DUNG logic `checkForClose` cua Breakout2/2-2/3
(va KHONG doc khi ma doi dang - dot bien); (2) `mo_phong.chay_he` khop dung gia
tren cac ca dung tay (chot dinh 45 -> dong o 0.9*dinh, hedge 300 point, cat lo
-120 sau hedge, hedge theo loi -30, gap), khong nhin truoc (phep cat); (3)
`doc_chien_luoc` gan `ro` vao lenh dau va xep lenh hedge dung loai.
"""
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from nhan import doc_ma as DM
from nhan import ngu_phap as NP
from nhan import mo_phong as MP
from nhan import chi_phi as CP
from nhan import ro_mql as RO

MAU = Path(__file__).resolve().parent / "mau_thu"
B2 = "EA Snippets_Breakout_Breakout2.mq5"
B22 = "EA Snippets_Breakout_Breakout2-2.mq5"
B3 = "EA Snippets_Breakout_Breakout3.mq5"
KHONG_PHI = CP.MoHinhChiPhi(ma="EURUSD")


def _vb(ten):
    return (MAU / ten).read_text(errors="ignore")


def _ro(vb):
    v = DM._chuan_hoa_mql5(DM._chuan_hoa(vb))
    return RO.doc_ro(v, DM._hang_mql(v), DM.rut_input(v))


RO_B2 = {"lot_dau": 0.1, "hop_dong": 100000.0,
         "dinh": {"moc": 45.0, "ti_le": 0.9, "reset_am": True, "reset_vao": False},
         "cat_lo": -120.0,
         "hedge": [{"kich": "diem", "khoang_diem": 300.0, "lot": 0.4, "reset_dinh": False,
                    "khi_so_lenh": 1}]}


class DocRo(unittest.TestCase):
    def test_breakout2(self):
        r = _ro(_vb(B2))
        self.assertEqual(r["ro"], RO_B2)
        self.assertEqual([(k["khi_so_lenh"], k["toi_duoc"]) for k in r["khoi"]],
                         [(22, False), (1, True)])

    def test_breakout2_2_hedge_theo_loi(self):
        r = _ro(_vb(B22))["ro"]
        self.assertEqual(r["hedge"], [{"kich": "loi", "nguong": -30.0, "lot": 0.3,
                                       "reset_dinh": False, "khi_so_lenh": 1}])
        self.assertTrue(r["dinh"]["reset_am"])

    def test_breakout3_input_hedgerange_va_reset(self):
        r = _ro(_vb(B3))["ro"]
        self.assertFalse(r["dinh"]["reset_am"])
        self.assertTrue(r["dinh"]["reset_vao"])
        self.assertTrue(r["hedge"][0]["reset_dinh"])
        self.assertEqual(r["hedge"][0]["khoang_diem"], 300.0)
        vb = _vb(B3).replace("input int            HedgeRange = 300;",
                             "input int            HedgeRange = 150;")
        self.assertEqual(_ro(vb)["ro"]["hedge"][0]["khoang_diem"], 150.0)

    def test_dot_bien_doi_so(self):
        vb = _vb(B2).replace("profits<(peakwin*0.9)", "profits<(peakwin*0.7)")
        self.assertEqual(_ro(vb)["ro"]["dinh"]["ti_le"], 0.7)
        vb = _vb(B2).replace("if(profits<=-120)", "if(profits<=-200)")
        self.assertEqual(_ro(vb)["ro"]["cat_lo"], -200.0)
        vb = _vb(B2).replace("volume = 0.4;", "volume = 0.2;")
        self.assertEqual(_ro(vb)["ro"]["hedge"][0]["lot"], 0.2)

    def test_dot_bien_khong_chac_thi_khong_dich(self):
        # them mot cau lenh la vao ham dong -> khong doan
        vb = _vb(B2).replace("   if(profits<=-120)\n",
                             "   if(dt.hour==22 && profits>=0)\n      CloseAll();\n"
                             "   if(profits<=-120)\n")
        r = _ro(vb)
        self.assertIsNone(r["ro"])
        self.assertTrue(r["ly_do"])
        # hedge CUNG chieu (khong phai hedge) -> khong dich
        vb = _vb(B2)
        i = vb.find("if(postotal==1)")
        doan = vb[i:].replace("type=ORDER_TYPE_SELL;", "type=ORDER_TYPE_BUY;", 1)
        r = _ro(vb[:i] + doan)
        self.assertIsNone(r["ro"])
        # dieu kien hedge postotal==2 -> khong toi duoc, ro van doc (chi khong hedge)
        vb = _vb(B2).replace("if(postotal==1)", "if(postotal==2)")
        r = _ro(vb)
        self.assertEqual(r["ro"]["hedge"], [])

    def test_breakout1_khong_co_ro(self):
        self.assertIsNone(_ro(_vb("EA Snippets_Breakout_Breakout1.mq5"))["ro"])


class DocChienLuoc(unittest.TestCase):
    def test_gan_ro_va_phan_loai(self):
        for ten in (B2, B22, B3):
            d = DM.doc_chien_luoc(_vb(ten), nguon=ten)
            self.assertEqual(len(d["co_che"]), 2)
            for sp in d["co_che"]:
                self.assertIn("ro", sp)
                self.assertEqual(sp["nhom_he"], ten)
                self.assertEqual(NP.kiem_khai_bao(sp), [])
                self.assertNotIn("giu", NP.tham_so_cua(sp))
            pl = d["phan_loai_vao_lenh"]
            self.assertEqual(pl["quan_ly_dich_duoc"], 1, ten)
            self.assertEqual(pl["quan_ly_vi_the"], 0, ten)

    def test_kiem_khai_bao_bat_ro_hong(self):
        sp = DM.doc_chien_luoc(_vb(B2), nguon=B2)["co_che"][0]
        sp["ro"] = dict(sp["ro"], cat_lo=50)
        self.assertTrue(NP.kiem_khai_bao(sp))


# ------------------------------------------------------------------ mo phong
def _df(bars, t0="2024-01-02 08:00"):
    idx = pd.date_range(t0, periods=len(bars), freq="h")
    return pd.DataFrame(bars, columns=["open", "high", "low", "close"], index=idx)


def _chan(n, chieu=1, ro=RO_B2, vao=(0,)):
    cho = np.zeros(n, dtype=bool)
    for k in vao:
        cho[k] = True
    return {"chieu": chieu, "cho": cho, "muc": None, "huong": None, "co": None,
            "loc": None, "sl": None, "tp": None, "keo": None, "giu": 1,
            "chan_boi": [], "dat": [], "ro": ro}


def _chay(bars, chieu=1, ro=RO_B2, cp=KHONG_PHI, vao=(0,)):
    df = _df(bars)
    nk = []
    kq = MP.chay_he(df, [_chan(len(df), chieu, ro, vao)], cp, ma="EURUSD", nhat_ky=nk,
                    diem=1e-5)
    return kq, nk, df


class MoPhongRo(unittest.TestCase):
    def test_chot_dinh(self):
        # vao 1.1000 -> len 1.1050 (loi 50$) -> rot: dong khi loi < 0.9*50 = 45 -> 1.1045
        kq, nk, _ = _chay([(1.1, 1.1, 1.1, 1.1),
                           (1.1, 1.105, 1.1, 1.105),
                           (1.105, 1.105, 1.103, 1.103),
                           (1.103, 1.103, 1.103, 1.103)])
        self.assertEqual(len(nk), 1)
        self.assertEqual(nk[0]["ly_do"], "chot_dinh")
        self.assertAlmostEqual(nk[0]["gia_ra"], 1.1045, places=9)
        self.assertAlmostEqual(nk[0]["loi_tien"], 45.0, places=4)
        self.assertAlmostEqual(kq.loi.sum(), np.log(1.1045 / 1.1), places=9)

    def test_chua_toi_moc_45_khong_chot(self):
        # dinh 44$ < 45 -> khong chot, rot ve -10$ van giu
        kq, nk, _ = _chay([(1.1, 1.1, 1.1, 1.1),
                           (1.1, 1.1044, 1.1, 1.1044),
                           (1.1044, 1.1044, 1.0990, 1.0990),
                           (1.0990, 1.0990, 1.0990, 1.0990)])
        self.assertNotIn("ly_do", nk[0])

    def test_hedge_300_point_roi_chot_dinh(self):
        # mua 0.1 o 1.1000; 1.0970 -> ban 0.4 (rong -0.3); 1.0930: loi =
        # 1e4*(1.093-1.1) + 4e4*(1.097-1.093) = -70 + 160 = 90 -> dinh 90;
        # hoi len: dong khi loi = 81 -> -3e4*p + 32880 = 81 -> p = 1.0933
        kq, nk, _ = _chay([(1.1, 1.1, 1.1, 1.1),
                           (1.1, 1.1, 1.093, 1.093),
                           (1.093, 1.0945, 1.093, 1.0945),
                           (1.0945, 1.0945, 1.0945, 1.0945)])
        self.assertEqual(len(nk[0]["hedge"]), 1)
        self.assertAlmostEqual(nk[0]["hedge"][0]["gia"], 1.097, places=9)
        self.assertEqual(nk[0]["hedge"][0]["lot"], 0.4)
        self.assertEqual(nk[0]["ly_do"], "chot_dinh")
        self.assertAlmostEqual(nk[0]["gia_ra"], 1.0933, places=9)
        self.assertAlmostEqual(nk[0]["loi_tien"], 81.0, places=4)
        # loi suat theo von danh nghia lenh dau, SO HOC tung bar (18/10/2026 - cong log cho chan BAN lai ao):
        # bar 1: mua 1.1 -> 1.093, ban x4 tu 1.097 -> 1.093; bar 2: ca hai tu 1.093 -> dong 1.0933
        ky_vong = (np.log(1 + (1.093 / 1.1 - 1) - 4 * (1.093 / 1.097 - 1))
                   + np.log(1 + (1.0933 / 1.093 - 1) - 4 * (1.0933 / 1.093 - 1)))
        self.assertAlmostEqual(kq.loi.sum(), ky_vong, places=9)
        self.assertEqual(kq.chi_tiet["chan"][0]["so_hedge"], 1)

    def test_cat_lo_sau_hedge(self):
        # sau hedge o 1.0970 (rong ban 0.3), gia quay ve 1.1000: loi = -120 -> cat lo
        kq, nk, _ = _chay([(1.1, 1.1, 1.1, 1.1),
                           (1.1, 1.1, 1.0965, 1.0965),
                           (1.0965, 1.1010, 1.0965, 1.1010),
                           (1.101, 1.101, 1.101, 1.101)])
        self.assertEqual(nk[0]["ly_do"], "cat_lo")
        self.assertAlmostEqual(nk[0]["gia_ra"], 1.1, places=9)
        self.assertAlmostEqual(nk[0]["loi_tien"], -120.0, places=4)

    def test_lenh_ban_hedge_mua(self):
        ro = dict(RO_B2)
        kq, nk, _ = _chay([(1.1, 1.1, 1.1, 1.1),
                           (1.1, 1.1035, 1.1, 1.1035),
                           (1.1035, 1.1035, 1.1035, 1.1035)], chieu=-1, ro=ro)
        # ban o BID 1.1000 -> hedgeprice = 1.1030 (BID >= 1.1030)
        self.assertAlmostEqual(nk[0]["hedge"][0]["gia"], 1.103, places=9)

    def test_spread_doi_muc_hedge_va_loi(self):
        cp = CP.MoHinhChiPhi(ma="EURUSD", spread_frac_chung=1e-4)
        kq, nk, _ = _chay([(1.1, 1.1, 1.1, 1.1),
                           (1.1, 1.1, 1.0960, 1.0960),
                           (1.096, 1.096, 1.096, 1.096)], cp=cp)
        # hedgeprice = ASK luc vao (1.1 + 1.1e-4) - 0.003
        self.assertAlmostEqual(nk[0]["hedge"][0]["gia"], 1.1 + 1.1e-4 - 0.003, places=9)

    def test_hedge_theo_loi(self):
        ro = dict(RO_B2, hedge=[{"kich": "loi", "nguong": -30.0, "lot": 0.3,
                                 "reset_dinh": False, "khi_so_lenh": 1}])
        kq, nk, _ = _chay([(1.1, 1.1, 1.1, 1.1),
                           (1.1, 1.1, 1.0960, 1.0960),
                           (1.096, 1.096, 1.096, 1.096)], ro=ro)
        self.assertAlmostEqual(nk[0]["hedge"][0]["gia"], 1.097, places=9)
        self.assertEqual(nk[0]["hedge"][0]["lot"], 0.3)

    def test_gap_qua_hedge_khop_o_open(self):
        kq, nk, _ = _chay([(1.1, 1.1, 1.1, 1.1),
                           (1.1, 1.1, 1.1, 1.1),
                           (1.0950, 1.0950, 1.0950, 1.0950),
                           (1.0950, 1.0950, 1.0950, 1.0950)])
        self.assertAlmostEqual(nk[0]["hedge"][0]["gia"], 1.095, places=9)
        self.assertEqual(nk[0]["hedge"][0]["bar"], 2)

    def test_mot_hedge_toi_da(self):
        # hedge xong (2 lenh) khong hedge them du gia di tiep
        kq, nk, _ = _chay([(1.1, 1.1, 1.1, 1.1),
                           (1.1, 1.1, 1.0968, 1.0968),
                           (1.0968, 1.1, 1.0968, 1.0995),
                           (1.0995, 1.0995, 1.0995, 1.0995)])
        self.assertEqual(len(nk[0]["hedge"]), 1)

    def test_phi_qua_dem_hai_chieu_tai_khoan_hedging(self):
        cp = CP.MoHinhChiPhi(ma="EURUSD", phi_nam_mua=0.0365, phi_nam_ban=0.0365)
        bars = [(1.1, 1.1, 1.1, 1.1), (1.1, 1.1, 1.0968, 1.0968)] + \
            [(1.0968, 1.0968, 1.0968, 1.0968)] * 48
        kq, nk, df = _chay(bars, cp=cp)
        # mua 1 + ban 4 (trong so) cung tra phi: ~ 5 x 0.0365/365 moi ngay
        self.assertGreater(kq.chi_phi_giu, 5 * 0.0365 / 365 * 1.5)

    def test_khong_nhin_truoc_phep_cat(self):
        rng = np.random.default_rng(3)
        n = 600
        c = 1.1 + np.cumsum(rng.normal(0, 0.0012, n))
        o = np.r_[c[0], c[:-1]]
        h = np.maximum(o, c) + rng.uniform(0, 0.001, n)
        l = np.minimum(o, c) - rng.uniform(0, 0.001, n)
        df = _df(list(zip(o, h, l, c)))
        cho = rng.uniform(size=n) < 0.05
        mk = lambda d, ch: dict(_chan(len(d), ch), cho=cho[:len(d)].copy())
        cp = CP.MoHinhChiPhi(ma="EURUSD", spread_frac_chung=1.5e-4, truot_gia_frac=4e-5)
        full = MP.chay_he(df, [mk(df, 1), mk(df, -1)], cp, ma="EURUSD", diem=1e-5)
        for m in (200, 377, 512):
            cut = MP.chay_he(df.iloc[:m], [mk(df.iloc[:m], 1), mk(df.iloc[:m], -1)], cp,
                             ma="EURUSD", diem=1e-5)
            # moi bar tru bar cuoi (bar cuoi cua phan cat chua biet open ke tiep)
            self.assertTrue(np.allclose(cut.loi[:m - 1], full.loi[:m - 1], atol=1e-12), m)

    def test_ro_that_tren_he_breakout2(self):
        """Ca he Breakout2 (2 chan + luat ngay + ro) chay duoc, co hedge, khong loi."""
        d = DM.doc_chien_luoc(_vb(B2), nguon=B2)["co_che"]
        rng = np.random.default_rng(7)
        n = 24 * 60
        c = 1.1 + np.cumsum(rng.normal(0, 0.0015, n))
        o = np.r_[c[0], c[:-1]]
        h = np.maximum(o, c) + rng.uniform(0, 0.001, n)
        l = np.minimum(o, c) - rng.uniform(0, 0.001, n)
        df = _df(list(zip(o, h, l, c)), t0="2024-01-01 00:00")
        nk = []
        kq = MP.chay_he(df, [NP.sinh_chan(sp, df) for sp in d], KHONG_PHI, ma="EURUSD",
                        nhat_ky=nk, diem=1e-5)
        self.assertGreater(kq.so_lenh, 20)
        self.assertTrue(any(x.get("hedge") for x in nk))
        # moi lenh vao luc 8h (gio dong bar truoc == 8) va toi da 1 lenh/ngay
        self.assertTrue(all(df.index[x["bar_vao"]].hour == 8 for x in nk))
        ngay = [df.index[x["bar_vao"]].date() for x in nk]
        self.assertEqual(len(ngay), len(set(ngay)))
        # ro dong theo tien: lenh dong co loi_tien >= 40.5 (chot) hoac <= -120 (cat)
        for x in nk:
            if x.get("ly_do") == "chot_dinh":
                self.assertGreaterEqual(x["loi_tien"], 40.5 - 1e-6)
            elif x.get("ly_do") == "cat_lo":
                self.assertLessEqual(x["loi_tien"], -120 + 1e-6)


if __name__ == "__main__":
    unittest.main()
