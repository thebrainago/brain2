# -*- coding: utf-8 -*-
"""SL/TP + keo SL + "mot lenh mot ngay" + mo phong CA HE (them 10/10/2026 dem).

Ba lop: (1) `doc_ma` doc dung SL/TP/keo SL/luat ngay tu MA THAT cua Breakout1
(va KHONG doc khi mau khong chac chan); (2) `mo_phong.chay_he` khop dung gia
tren cac ca dung tay, khong nhin truoc (phep cat), placebo ~ 0; (3)
`vong_thu_nghiem` chay nhom chung, tham so chung duoc buoc lai.
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
B1 = "EA Snippets_Breakout_Breakout1.mq5"
KHONG_PHI = CP.MoHinhChiPhi(ma="TEST")


def _vb():
    return (MAU / B1).read_text(errors="ignore")


def _doc(vb):
    return DM.doc_chien_luoc(vb, nguon=B1)["co_che"]


class DocSLTP(unittest.TestCase):
    def test_breakout1_sl_tp_keo_luat_ngay(self):
        cc = _doc(_vb())
        self.assertEqual([sp["chieu"] for sp in cc], [1, -1])
        mua, ban = cc
        self.assertEqual(mua["sltp"]["sl"]["chi_bao"], "thap_trong_gio")
        self.assertEqual(ban["sltp"]["sl"]["chi_bao"], "cao_trong_gio")
        for sp in cc:
            self.assertEqual((sp["sltp"]["sl"]["gio_tu"], sp["sltp"]["sl"]["gio_den"]), (5, 8))
            self.assertEqual(sp["sltp"]["tp"], 1.0)
            self.assertEqual(sp["sltp"]["keo"]["n"], 3)        # lows 1..3 da dong
            self.assertNotIn("_bar0", str(sp["sltp"]))
            self.assertEqual(sp["mot_lenh_ngay"]["chan_boi"], ["lastupday", "lastdownday"])
            self.assertEqual(NP.kiem_khai_bao(sp), [])
            self.assertFalse(any("lastupday" in x for x in sp["bo_qua_quan_tri"]))
        self.assertEqual(mua["sltp"]["keo"]["chi_bao"], "thap_nhat")
        self.assertEqual(ban["sltp"]["keo"]["chi_bao"], "cao_nhat")
        self.assertEqual(mua["mot_lenh_ngay"]["dat"], ["lastupday"])
        self.assertEqual(ban["mot_lenh_ngay"]["dat"], ["lastdownday"])
        self.assertEqual(mua["mot_lenh_ngay"]["nhom"], ban["mot_lenh_ngay"]["nhom"])

    def test_tpfactor_doi_theo_input(self):
        vb = _vb().replace("input double         TPFactor = 1;",
                           "input double         TPFactor = 2.5;")
        self.assertEqual([sp["sltp"]["tp"] for sp in _doc(vb)], [2.5, 2.5])

    def test_khong_keo_sl_khi_khong_co_positionmodify(self):
        vb = _vb().replace("trade.PositionModify(_Symbol,sl,PositionGetDouble(POSITION_TP));",
                           "")
        for sp in _doc(vb):
            self.assertIsNone(sp["sltp"]["keo"])

    def test_null_sl_tp_thi_khong_co_sltp(self):
        vb = _vb().replace("trade.PositionOpen(_Symbol, type, volume, price, sl, tp)",
                           "trade.PositionOpen(_Symbol, type, volume, price, NULL, NULL)")
        for sp in _doc(vb):
            self.assertNotIn("sltp", sp)
            self.assertIn("mot_lenh_ngay", sp)       # luat ngay van con

    def test_tp_la_hang_so_thi_khong_doan(self):
        vb = _vb().replace("tp = price+((price-lowrange)*TPFactor);",
                           "tp = price+calculateDistance(price, 300);")
        mua = _doc(vb)[0]
        self.assertNotIn("sltp", mua)
        self.assertTrue(any("TP" in x for x in mua.get("gia_dinh", [])))

    def test_luat_ngay_mot_chieu(self):
        vb = _vb().replace("if(lastupday==dt.day || lastdownday==dt.day)",
                           "if(lastupday==dt.day)")
        mua, ban = _doc(vb)
        for sp in (mua, ban):
            self.assertEqual(sp["mot_lenh_ngay"]["chan_boi"], ["lastupday"])
            self.assertEqual(NP.kiem_khai_bao(sp), [])
        self.assertEqual(mua["mot_lenh_ngay"]["dat"], ["lastupday"])
        self.assertEqual(ban["mot_lenh_ngay"]["dat"], [])     # ban khong chan ai

    def test_copy_cung_ten_mang_lay_lan_gan_nhat(self):
        # checkForClose: lows = 3 bar da dong; checkForOpen: lows = khung phien
        vb = DM._chuan_hoa(_vb())
        DM._CHE_DO_MQL, cu = True, DM._CHE_DO_MQL
        try:
            v = DM._chuan_hoa_mql5(vb)
            bang = sorted(DM._bang_ky_hieu(v) + DM._bang_mql(v), key=lambda x: x[0])
            i_dong = v.find("sl = MathMax(sl,lowrange)")
            i_mo = v.find("sl = lowrange")
            self.assertEqual(DM._toan_hang("lowrange", i_dong, bang, [])["chi_bao"],
                             "thap_nhat")
            self.assertEqual(DM._toan_hang("lowrange", i_mo, bang, [])["chi_bao"],
                             "thap_trong_gio")
        finally:
            DM._CHE_DO_MQL = cu


def _df(bars, bat_dau="2024-01-02 09:00"):
    idx = pd.date_range(bat_dau, periods=len(bars), freq="h")
    return pd.DataFrame(bars, columns=["open", "high", "low", "close"], index=idx)


def _chan(n, chieu, muc, sl, tp=1.0, keo=None, huong=None, cho=None, chan_boi=(),
          dat=()):
    return {"chieu": chieu, "cho": np.ones(n, bool) if cho is None else np.asarray(cho),
            "muc": None if muc is None else np.full(n, muc, float),
            "huong": huong or (">" if chieu > 0 else "<"),
            "sl": None if sl is None else np.full(n, sl, float), "tp": tp,
            "keo": None if keo is None else np.asarray(keo, float), "giu": 1,
            "chan_boi": list(chan_boi), "dat": list(dat)}


class MoPhongHe(unittest.TestCase):
    def test_vao_trong_bar_ra_o_tp(self):
        df = _df([[1.0990, 1.0995, 1.0985, 1.0990],
                  [1.0950, 1.1050, 1.0940, 1.1000],   # thap truoc (gan open) roi len qua 1.10
                  [1.1040, 1.1120, 1.1030, 1.1100],   # cham TP 1.11
                  [1.1100, 1.1110, 1.1090, 1.1100]])
        c = _chan(4, 1, 1.10, 1.09, cho=[True, False, False, False])
        kq = MP.chay_he(df, [c], KHONG_PHI)
        self.assertEqual(kq.so_lenh, 1)
        self.assertAlmostEqual(float(kq.loi_tho.sum()), np.log(1.11 / 1.10), places=12)
        self.assertEqual(kq.vi_the[2], 0)                 # da dong trong bar 2

    def test_gap_qua_sl_dong_o_open(self):
        df = _df([[1.0990, 1.0995, 1.0985, 1.0990],
                  [1.0995, 1.1010, 1.0994, 1.1005],   # vao o 1.10
                  [1.0850, 1.0860, 1.0840, 1.0850],   # gap duoi SL 1.09 -> ra o open
                  [1.0850, 1.0860, 1.0840, 1.0850]])
        kq = MP.chay_he(df, [_chan(4, 1, 1.10, 1.09)], KHONG_PHI)
        self.assertAlmostEqual(float(kq.loi_tho.sum()), np.log(1.0850 / 1.10), places=12)

    def test_keo_sl_chi_siet_va_khong_vuot_gia(self):
        n = 4
        df = _df([[1.0990, 1.0995, 1.0985, 1.0990],
                  [1.0995, 1.1010, 1.0994, 1.1005],   # vao 1.10
                  [1.1020, 1.1030, 1.1000, 1.1010],   # keo SL len 1.1005 (< open 1.102) -> cham
                  [1.1010, 1.1010, 1.1000, 1.1000]])
        keo = [np.nan, 1.0950, 1.1005, 1.1005]       # keo[1] ap o bar 2
        kq = MP.chay_he(df, [_chan(n, 1, 1.10, 1.09, tp=None, keo=keo)], KHONG_PHI)
        self.assertAlmostEqual(float(kq.loi_tho.sum()), np.log(1.1005 / 1.10), places=12)
        # muc keo VUOT gia hien tai -> MT5 tu choi, SL giu nguyen
        keo2 = [np.nan, 1.0950, 1.1050, 1.1050]
        kq2 = MP.chay_he(df, [_chan(n, 1, 1.10, 1.09, tp=None, keo=keo2)], KHONG_PHI)
        self.assertEqual(float(kq2.vi_the[2]), 1.0)        # van giu qua bar 2

    def test_mot_lenh_ngay_ban_truoc_chan_mua(self):
        # bar 1: ban khop o 1.095 roi cham TP (1.09); bar 2: gia vot qua muc mua 1.105
        # nhung CUNG NGAY -> khong mua. Bar 3 sang ngay moi -> mua duoc.
        df = _df([[1.1000, 1.1005, 1.0995, 1.1000],
                  [1.0990, 1.0992, 1.0890, 1.0900],
                  [1.0990, 1.1100, 1.0985, 1.1080],
                  [1.1080, 1.1200, 1.1075, 1.1150],
                  [1.1150, 1.1160, 1.1140, 1.1150]],
                 bat_dau="2024-01-02 21:00")           # bar 3 = 00:00 ngay 3
        cb = ["lastupday", "lastdownday"]
        mua = _chan(5, 1, 1.105, 1.095, chan_boi=cb, dat=["lastupday"])
        ban = _chan(5, -1, 1.095, 1.105, chan_boi=cb, dat=["lastdownday"])
        kq = MP.chay_he(df, [mua, ban], KHONG_PHI)
        lenh = [c["so_lenh"] for c in kq.chi_tiet["chan"]]
        self.assertEqual(lenh, [1, 1])
        self.assertEqual(float(kq.vi_the[2]), 0.0)         # bar 2 khong mua
        self.assertEqual(float(kq.vi_the[3]), 1.0)         # bar 3 (ngay moi) mua o open
        # khong luat ngay: bar 2 mua duoc
        mua2, ban2 = dict(mua, chan_boi=[]), dict(ban, chan_boi=[])
        kq2 = MP.chay_he(df, [mua2, ban2], KHONG_PHI)
        self.assertGreaterEqual(kq2.chi_tiet["chan"][0]["so_lenh"], 1)
        self.assertEqual(float(kq2.vi_the[2]), 1.0)

    def test_mot_vi_the_mot_luc(self):
        df = _df([[1.1000, 1.1005, 1.0995, 1.1000],
                  [1.1000, 1.1060, 1.0999, 1.1050],   # mua o 1.105
                  [1.1050, 1.1055, 1.0930, 1.0950],   # SL mua 1.10 cham; ban 1.095 sau do
                  [1.0950, 1.0960, 1.0940, 1.0950]])
        mua = _chan(4, 1, 1.105, 1.100, tp=None)
        ban = _chan(4, -1, 1.095, 1.100, tp=None)
        kq = MP.chay_he(df, [mua, ban], KHONG_PHI)
        # khong luat ngay: SL mua roi van vao ban trong CUNG bar (EA chay moi tick)
        self.assertEqual([c["so_lenh"] for c in kq.chi_tiet["chan"]], [1, 1])
        self.assertAlmostEqual(float(kq.chi_tiet["chan"][0]["loi"].sum()),
                               np.log(1.100 / 1.105), places=12)

    def test_chan_cheo_hai_co_cung_bar(self):
        # Bien phien H=1.10, L=1.09, MA=1.105 (tren H). Bar 2: gia len qua 1.10
        # TRUOC (co mua bat, nhung gia < MA nen chua mua) roi xuong qua 1.09: co
        # ban bat, loc ban (gia <= MA) dat - NHUNG `if(up && gia<MA) return;` cua
        # co mua dang bat chan luon lenh ban suot bar. EA: 0 lenh.
        n = 4
        df = _df([[1.0950, 1.0955, 1.0945, 1.0950],
                  [1.0950, 1.0960, 1.0880, 1.0890],
                  [1.0960, 1.1010, 1.0870, 1.0880],
                  [1.0880, 1.0890, 1.0870, 1.0880]])
        ma = np.full(n, 1.105)

        def chan(chieu, cho):
            c = _chan(n, chieu, 1.10 if chieu > 0 else 1.09, 1.09 if chieu > 0 else 1.10,
                      tp=None, cho=cho)
            c["muc"] = np.maximum(c["muc"], ma) if chieu > 0 else np.minimum(c["muc"], ma)
            c["co"] = (c["huong"], np.full(n, 1.10 if chieu > 0 else 1.09))
            c["loc"] = [(">=" if chieu > 0 else "<=", ma)]
            return c
        # chi cho phep o bar 2 (cho[1])
        mua, ban = chan(1, [False, True, False, False]), chan(-1, [False, True, False, False])
        kq = MP.chay_he(df, [mua, ban], KHONG_PHI)
        self.assertEqual(kq.so_lenh, 0)                    # EA: khong lenh nao bar 2
        # bo co/loc (hai chan doc lap) -> ban o 1.09: mo hinh SAI ma ta tranh
        for c in (mua, ban):
            c["co"] = c["loc"] = None
        kq2 = MP.chay_he(df, [mua, ban], KHONG_PHI)
        self.assertEqual([c["so_lenh"] for c in kq2.chi_tiet["chan"]], [0, 1])

    def test_breakout1_co_loc(self):
        for sp in _doc(_vb()):
            self.assertEqual(sp["trong_bar"]["kich"], [0, 3])
            self.assertEqual(sp["trong_bar"]["loc"], [3])      # loc MA
            df = V.du_lieu_gia_lap_duong(24 * 30, seed=1)
            c = NP.sinh_chan(sp, df)
            self.assertEqual(c["co"][0], sp["trong_bar"]["huong"])
            self.assertEqual(len(c["loc"]), 1)

    def test_khong_nhin_truoc_phep_cat(self):
        df = V.du_lieu_gia_lap_duong(24 * 80, seed=3)
        specs = _doc(_vb())
        day = MP.chay_he(df, [NP.sinh_chan(sp, df) for sp in specs], KHONG_PHI)
        for t in (600, 911, 1500):
            cat = df.iloc[:t]
            kq = MP.chay_he(cat, [NP.sinh_chan(sp, cat) for sp in specs], KHONG_PHI)
            np.testing.assert_allclose(kq.loi_tho[:t - 1], day.loi_tho[:t - 1], atol=1e-15)
            np.testing.assert_array_equal(kq.vi_the[:t - 1], day.vi_the[:t - 1])

    def test_placebo_duong_gia_ngau_nhien(self):
        # Duong gia ngau nhien that (rau la cuc tri that): SL/TP + luat ngay khong
        # tao ra edge. Trung binh Sharpe khong phi qua 8 seed phai gan 0.
        specs = _doc(_vb())
        sh = []
        for seed in range(8):
            df = V.du_lieu_gia_lap_duong(24 * 200, seed=seed)
            sh.append(V.danh_gia_nhom(specs, df, "H1", cp=KHONG_PHI)["sharpe"])
        self.assertLess(abs(float(np.mean(sh))), 0.6, sh)


class VongNhom(unittest.TestCase):
    def test_tham_so_chung_buoc_lai(self):
        specs = _doc(_vb())
        ts, ax = V.tham_so_nhom(specs)
        for k in ("vao1_phai_hang", "vao2_phai_hang", "vao3_phai_cua_n", "sltp_tp",
                  "sltp_keo_n"):
            self.assertIn(k, ts)
            self.assertEqual(len(ax[k]), 2)
        self.assertNotIn("giu", ts)                      # co SL/TP: khong dong theo gio
        moi = V.ap_tham_so_nhom(specs, ax, dict(ts, sltp_tp=2.0))
        self.assertEqual([sp["sltp"]["tp"] for sp in moi], [2.0, 2.0])

    def test_chay_mot_file_ra_mot_dong_nhom(self):
        df = V.du_lieu_gia_lap_duong(24 * 150, seed=5)
        ra = V.chay_mot_file(MAU / B1, df, "H1", True, 20, 2.0, 1.5, set(),
                             cp=V.mo_hinh_chi_phi(df))
        self.assertEqual(len(ra), 1)
        d = ra[0]
        self.assertEqual(d["chieu"], 0)
        self.assertEqual(len(d["tot_kiem"]["chan"]), 2)
        self.assertEqual(sum(c["so_lenh"] for c in d["tot_kiem"]["chan"]),
                         d["tot_kiem"]["so_lenh"])
        self.assertNotIn("loi", d)


if __name__ == "__main__":
    unittest.main()
