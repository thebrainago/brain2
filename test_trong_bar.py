# -*- coding: utf-8 -*-
"""EA kiem lai MOI tick -> lenh dung khop TRONG bar (them 10/10/2026 khuya).

Kiem ba lop: (1) `doc_ma` phat hien dung EA nao kiem moi tick va dieu kien nao
la kich hoat; (2) `mo_phong.chay_dung_trong_bar` khop dung gia, khong nhin
truoc; (3) `vong_thu_nghiem` doi du lenh o CA HAI phan va tinh phi that.
"""
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from nhan import doc_ma as DM
from nhan import ngu_phap as NP
from nhan import mo_phong as MP
from nhan import chi_phi as CP
import vong_thu_nghiem as V

MAU = Path(__file__).resolve().parent / "mau_thu"
KHONG_PHI = CP.MoHinhChiPhi(ma="TEST")


def _doc(ten):
    return DM.doc_chien_luoc((MAU / ten).read_text(errors="ignore"), nguon=ten)


EA_KHUNG = """#property version "1.00"
#include <Trade\\Trade.mqh>
CTrade trade;
%s
void checkForOpen() {
   datetime curTime = iTime(_Symbol,_Period,0);
   static datetime prevTime;
   %s
   MqlRates current[];
   if(CopyRates(_Symbol,_Period,0,1,current)==-1)
      return;
   double lv = iHigh(_Symbol,_Period,1);
   bool up = current[0].high > lv;
   if(up)
   {
      trade.PositionOpen(_Symbol, ORDER_TYPE_BUY, 0.1, 0, 0, 0);
   }
   else
      return;
   prevTime = curTime;
}
void OnTick() {
   %s
   checkForOpen();
}
"""


class PhatHien(unittest.TestCase):
    def test_breakout1_la_lenh_dung_trong_bar(self):
        cc = _doc("EA Snippets_Breakout_Breakout1.mq5")["co_che"]
        self.assertEqual(len(cc), 2)
        for sp in cc:
            self.assertIs(sp.get("kiem_moi_tick"), True)
            tb = sp["trong_bar"]
            self.assertEqual(tb["huong"], ">" if sp["chieu"] == 1 else "<")
            # kich = pha vo bien phien + loc MA (gia song so voi MA); gio la cho phep
            kich = [sp["vao"][k] for k in tb["kich"]]
            self.assertEqual(sorted(d["phai"].get("chi_bao") for d in kich),
                             sorted(["cao_trong_gio" if sp["chieu"] == 1 else "thap_trong_gio",
                                     "tre"]))
            self.assertFalse(NP.kiem_khai_bao(sp))

    def test_breakout2_cap_bu_nhau_tick_dau_la_dung(self):
        for f in ("EA Snippets_Breakout_Breakout2.mq5", "EA Snippets_Breakout_Breakout2-2.mq5",
                  "EA Snippets_Breakout_Breakout3.mq5"):
            for sp in _doc(f)["co_che"]:
                self.assertEqual(sp.get("kiem_moi_tick"), "cap_bu_nhau", f)
                self.assertNotIn("trong_bar", sp)

    def test_co_cong_bar_moi_thi_khong_doi(self):
        for f in ("EA Snippets_Breakout_Breakout5.mq5", "EA Snippets_Breakout_Breakout5-2-2.mq5",
                  "mql5-pro_assets_EA_Template.mq5"):
            for sp in _doc(f)["co_che"]:
                self.assertNotIn("kiem_moi_tick", sp, f)
                self.assertNotIn("trong_bar", sp, f)

    def test_cong_prevTime_chi_hieu_luc_khi_gan_ngay(self):
        cong = "if ( curTime == prevTime ) {\n      return;\n   }"
        # gan prevTime o CUOI (sau lenh vao) -> moi tick chua co lenh deu di qua
        sp = DM.doc_chien_luoc(EA_KHUNG % ("", cong, ""))["co_che"]
        self.assertEqual(len(sp), 1)
        self.assertIn("trong_bar", sp[0])
        # gan NGAY sau cong -> cong bar moi that
        cong2 = cong + "\n   prevTime = curTime;"
        sp = DM.doc_chien_luoc(EA_KHUNG % ("", cong2, ""))["co_che"]
        self.assertNotIn("trong_bar", sp[0])

    def test_isnewbar_o_ham_goi(self):
        ham = "bool IsNewBar() { return true; }"
        sp = DM.doc_chien_luoc(EA_KHUNG % (ham, "", "if(!IsNewBar()) return;"))["co_che"]
        self.assertNotIn("trong_bar", sp[0])
        sp = DM.doc_chien_luoc(EA_KHUNG % (ham, "", ""))["co_che"]
        self.assertIn("trong_bar", sp[0])

    def test_khong_ro_ri_token_noi_bo(self):
        for f in sorted(MAU.glob("*.mq5")):
            r = DM.doc_chien_luoc(f.read_text(errors="ignore"), nguon=f.name)
            s = repr(r)
            self.assertNotIn(DM._GIA0, s, f.name)
            self.assertNotIn("_bar0", s, f.name)
            self.assertNotIn("_loai_b0", s, f.name)

    def test_kiem_khai_bao_bat_trong_bar_hong(self):
        sp = dict(_doc("EA Snippets_Breakout_Breakout1.mq5")["co_che"][0])
        sp["trong_bar"] = {"huong": ">", "kich": [9]}
        self.assertTrue(NP.kiem_khai_bao(sp))
        sp["trong_bar"] = {"huong": "<", "kich": [0]}         # phep '>' nguoc huong
        self.assertTrue(NP.kiem_khai_bao(sp))


def _df(o, h, l, c):
    idx = pd.date_range("2024-01-01", periods=len(o), freq="h")
    return pd.DataFrame({"open": o, "high": h, "low": l, "close": c}, index=idx)


class KhopLenh(unittest.TestCase):
    def test_khop_tai_muc_va_tai_open_khi_gap(self):
        df = _df([1.00, 1.00, 1.03, 1.05, 1.04],
                 [1.01, 1.025, 1.06, 1.06, 1.05],
                 [0.99, 0.99, 1.02, 1.03, 1.03],
                 [1.00, 1.02, 1.05, 1.04, 1.04])
        cho = np.array([1, 1, 0, 0, 0], bool)
        muc = np.array([1.02, 1.02, 9, 9, 9])
        kq = MP.chay_dung_trong_bar(df, cho, muc, ">", 1, 1, KHONG_PHI)
        # bar 1: open 1.00 < 1.02 < high 1.025 -> khop o 1.02, giu toi open bar 2
        self.assertAlmostEqual(kq.loi_tho[1], np.log(1.03 / 1.02))
        # bar 2: open 1.03 > 1.02 (gap) -> dang giu tu bar 1 nen keo dai, vao lai o open
        self.assertAlmostEqual(kq.loi_tho[2], np.log(1.05 / 1.03))
        self.assertEqual(kq.so_lenh, 1)
        self.assertEqual(list(kq.vi_the), [0, 1, 1, 0, 0])

    def test_khong_cham_muc_thi_khong_vao(self):
        df = _df([1.0] * 4, [1.01] * 4, [0.99] * 4, [1.0] * 4)
        kq = MP.chay_dung_trong_bar(df, np.ones(4, bool), np.full(4, 1.01), ">", 1, 1,
                                    KHONG_PHI)
        self.assertEqual(kq.so_lenh, 0)            # high == muc: chua VUOT
        kq = MP.chay_dung_trong_bar(df, np.ones(4, bool), np.full(4, 0.995), "<", -1, 1,
                                    KHONG_PHI)
        # giu=1: dong o open bar sau, roi khop LAI o muc giua bar -> 3 lenh (bar 1..3)
        self.assertEqual(kq.so_lenh, 3)
        self.assertAlmostEqual(kq.loi_tho[1], -np.log(1.0 / 0.995))

    def test_khong_nhin_truoc_phep_cat(self):
        sp = _doc("EA Snippets_Breakout_Breakout1.mq5")["co_che"][0]
        df = V.du_lieu_gia_lap_duong(24 * 40, seed=5)
        cho, muc, h = NP.sinh_trong_bar(sp, df)
        day = MP.chay_dung_trong_bar(df, cho, muc, h, 1, 2, KHONG_PHI)
        self.assertGreater(day.so_lenh, 5)
        for t in (300, 457, 611, 800, len(df) - 2):
            c2, m2, _ = NP.sinh_trong_bar(sp, df.iloc[:t + 1])
            np.testing.assert_array_equal(c2, cho[:t + 1])
            np.testing.assert_allclose(m2, muc[:t + 1], equal_nan=True)
            cat = MP.chay_dung_trong_bar(df.iloc[:t + 1], c2, m2, h, 1, 2, KHONG_PHI)
            np.testing.assert_array_equal(cat.vi_the, day.vi_the[:t + 1])
            np.testing.assert_allclose(cat.loi_tho[:t], day.loi_tho[:t])

    def test_placebo_buoc_ngau_nhien_lai_tho_xap_xi_0(self):
        # Dinh ly dung tuy chon: khop o muc roi giu toi open sau -> ky vong 0.
        df = V.du_lieu_gia_lap_duong(24 * 300, seed=11, buoc=240)
        c = df["close"].to_numpy()
        muc = c * 1.0005
        kq = MP.chay_dung_trong_bar(df, np.ones(len(df), bool), muc, ">", 1, 1, KHONG_PHI)
        x = kq.loi_tho[kq.vi_the != 0]
        self.assertGreater(len(x), 500)
        self.assertLess(abs(x.mean()), 3 * x.std() / np.sqrt(len(x)))


class VongLap(unittest.TestCase):
    def test_lenh_min_phan_tu(self):
        self.assertEqual(V.lenh_min_phan_tu(20, 70, 30), 47)
        self.assertEqual(V.lenh_min_phan_tu(20, 10, 90), 20)

    def test_chi_phi_that_khong_bang_0(self):
        cp = V.mo_hinh_chi_phi(V.du_lieu_gia_lap(200))
        self.assertGreater(cp.spread_frac_chung, 0)
        self.assertGreater(cp.truot_gia_frac, 0)

    def test_giu_lai_doi_du_lenh_ca_hai_phan(self):
        df = V.du_lieu_gia_lap_duong(24 * 200, seed=2)
        cp = V.mo_hinh_chi_phi(df, khong_phi=True)
        ra = []
        for f in ("EA Snippets_Breakout_Breakout1.mq5", "EA Snippets_Breakout_Breakout5-2-2.mq5"):
            ra += V.chay_mot_file(MAU / f, df, cp=cp)
        cat = int(len(df) * 0.7)
        can_tu = V.lenh_min_phan_tu(20, cat, len(df) - cat)
        co_tb = False
        for x in ra:
            if "loi" in x:
                self.fail(x["loi"])
            co_tb |= bool(x.get("trong_bar")) or any(
                c.get("trong_bar") for c in x.get("chan", []))   # dong nhom (10/10 dem)
            tu = x.get("tot_tu", x["goc_tu"])
            thieu = tu["so_lenh"] < can_tu or x["tot_kiem"]["so_lenh"] < 20
            self.assertEqual(bool(x.get("it_lenh")), thieu)
            if thieu:
                self.assertFalse(x["giu_lai"])
        self.assertTrue(co_tb)


if __name__ == "__main__":
    unittest.main()
