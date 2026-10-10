# -*- coding: utf-8 -*-
"""SL/TP DAT TRUC TIEP o lenh vao + dong lenh o tick dau bar (them 11/10/2026).

Ba lop: (1) `doc_ma._sltp_truc_tiep` / `_dong_mo_bar_mql` doc dung SL/TP cua 5 EA
mo rong (`_Point` x input, ATR x he so, muc MA + TP theo R) va KHONG doc khi khong
chac; (2) `mo_phong.chay_he` (chan `mt5`) dat muc dung goc ASK/BID, lenh ban dong o
ASK, tu choi khi sai phia, dong o tick dau khong vao lai cung tick, khong nhin
truoc (phep cat); (3) DSL: kiem cu phap, phoi/ap tham so, buoc chu ky cung handle.
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

SC = Path(__file__).resolve().parent / "mau_thu" / "mo_rong" / "santiago-cruzlopez"


def _doc(ten, thay=None):
    vb = (SC / ten).read_text(errors="ignore")
    for a, b in (thay or []):
        assert a in vb, a
        vb = vb.replace(a, b)
    return DM.doc_chien_luoc(vb, nguon=ten)["co_che"]


class DocSLTPTrucTiep(unittest.TestCase):
    def test_011_diem_goc_bid_mua_ask_ban(self):
        mua, ban = _doc("011_RSI_V2_EA.mq5")
        for sp, ref in ((mua, "BID"), (ban, "ASK")):
            k = sp["sltp"]
            self.assertTrue(k["mt5"])
            self.assertEqual((k["sl_diem"], k["tp_diem"]), (200.0, 100.0))
            self.assertEqual((k["ref_sl"], k["ref_tp"]), (ref, ref))
            self.assertTrue(sp["gia_dinh_diem"])
            self.assertEqual(NP.kiem_khai_bao(sp), [])
            self.assertIn("trong_bar", sp)              # lenh dung trong bar giu nguyen
            self.assertNotIn("dong_mo_bar", sp)         # Close_Signal=false: khong dong
            self.assertTrue(any("_Point" in x for x in sp["gia_dinh"]))

    def test_011_input_stop_loss_0_thi_khong_sl(self):
        mua, _ = _doc("011_RSI_V2_EA.mq5", [("Stop_Loss     = 200;", "Stop_Loss     = 0;")])
        self.assertIsNone(mua["sltp"]["sl_diem"])
        self.assertEqual(mua["sltp"]["tp_diem"], 100.0)

    def test_011_ca_hai_0_thi_khong_sltp(self):
        mua, _ = _doc("011_RSI_V2_EA.mq5", [("Stop_Loss     = 200;", "Stop_Loss     = 0;"),
                                            ("Take_Profit   = 100;", "Take_Profit   = 0;")])
        self.assertNotIn("sltp", mua)

    def test_012_symbol_point_goc_ask_mua_bid_ban(self):
        mua, ban = _doc("012_MA_V1_EA.mq5")
        self.assertEqual((mua["sltp"]["sl_diem"], mua["sltp"]["tp_diem"]), (150.0, 250.0))
        self.assertEqual(mua["sltp"]["ref_sl"], "ASK")
        self.assertEqual(ban["sltp"]["ref_sl"], "BID")
        # EA khong dem vi the -> ghi xap xi mot vi the moi chan
        self.assertTrue(any("KHONG gioi han so vi the" in x for x in mua["gia_dinh"]))

    def test_013_dong_theo_dai_giua_va_shift_dung_bar(self):
        mua, ban = _doc("013_Bollinger_Bands_EA.mq5")
        # bands_shift=1: buffer bar 0 = bollinger TINH TAI bar 1 = bar i (khong tre)
        self.assertEqual(mua["vao"][0]["phai"]["chi_bao"], "bollinger")
        self.assertEqual(mua["dong_mo_bar"]["phep"], ">=")
        self.assertEqual(mua["dong_mo_bar"]["gia"], "BID")
        self.assertEqual(ban["dong_mo_bar"]["phep"], "<=")
        self.assertEqual(ban["dong_mo_bar"]["gia"], "ASK")
        for sp in (mua, ban):
            self.assertEqual(sp["dong_mo_bar"]["muc"]["lay"], "giua")
            self.assertEqual(sp["dong_mo_bar"]["muc"]["n"], 21)
            self.assertEqual(NP.kiem_khai_bao(sp), [])

    def test_013_dong_khong_doc_khi_kiem_moi_tick(self):
        mua, _ = _doc("013_Bollinger_Bands_EA.mq5",
                      [("   if(!IsNewBar())\n     {\n      return;\n     }", "")])
        self.assertNotIn("dong_mo_bar", mua)

    def test_015_sl_muc_ema_tp_theo_R(self):
        mua, ban = _doc("015_Triple_MA_EA.mq5")
        for sp in (mua, ban):
            k = sp["sltp"]
            self.assertEqual(k["sl"], {"chi_bao": "ema", "n": 30})   # MAVG2[1] = bar i
            self.assertEqual(k["tp"], 1.0)
            self.assertEqual(NP.kiem_khai_bao(sp), [])
        mua2, _ = _doc("015_Triple_MA_EA.mq5", [("TP_Ratio       = 1.0;", "TP_Ratio       = 2.5;")])
        self.assertEqual(mua2["sltp"]["tp"], 2.5)

    def test_017_atr_he_so_goc_ask_bid(self):
        mua, ban = _doc("017_Ichi_ATR_EA.mq5")
        for sp, ref in ((mua, "ASK"), (ban, "BID")):
            k = sp["sltp"]
            self.assertEqual(k["sl_kc"]["toan_hang"][0], {"chi_bao": "atr", "n": 14, "kieu": "sma"})
            self.assertEqual(k["sl_kc"]["he_so"], [1.0])
            self.assertEqual(k["ref_sl"], ref)
        self.assertTrue(any("market execution" in x for x in ban["gia_dinh"]))

    def test_khoang_khong_phai_diem_hay_atr_thi_khong_doan(self):
        mua, _ = _doc("012_MA_V1_EA.mq5", [(
            "double SL = ask - Stop_Loss*SymbolInfoDouble(_Symbol,SYMBOL_POINT);",
            "double SL = ask - MathAbs(MA_fastBuffer[1]-MA_slowBuffer[1]);")])
        self.assertNotIn("sltp", mua)
        self.assertTrue(any("chua dich" in x for x in mua["gia_dinh"]))

    def test_sai_phia_thi_khong_dich(self):
        mua, _ = _doc("012_MA_V1_EA.mq5", [(
            "double SL = ask - Stop_Loss*", "double SL = ask + Stop_Loss*")])
        self.assertNotIn("sltp", mua)


# ------------------------------------------------------------- MO PHONG
def _df(rows):
    idx = pd.date_range("2024-01-01", periods=len(rows), freq="h")
    return pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx)


def _chan(n, ch, cho_bar=(0,), **kw):
    cho = np.zeros(n, dtype=bool)
    for b in cho_bar:
        cho[b] = True
    c = {"chieu": ch, "cho": cho, "muc": None, "muc_lai": None, "phep_lai": None,
         "huong": None, "co": None, "loc": None, "sl": None, "tp": None, "keo": None,
         "giu": 1, "chan_boi": [], "dat": [], "ro": None, "sl_kc": None, "tp_kc": None,
         "sl_kc_min_spread": None, "rui_ro": None, "spread_max_diem": None, "mt5": True,
         "sl_diem": None, "tp_diem": None, "ref_sl": None, "ref_tp": None, "dong_mo": None}
    c.update(kw)
    return c


CP_S = CP.MoHinhChiPhi(ma="TEST", spread_frac_chung=0.001)   # s = 0.001 o gia 1.0
PHANG = [(1.0, 1.0, 1.0, 1.0)] * 2 + [(1.0, 1.0, 1.0, 1.0)] * 4


def _chay(rows, chan, cp=CP_S):
    nk = []
    MP.chay_he(_df(rows), chan, cp, diem=1e-4, nhat_ky=nk)
    return nk


class MoPhongMT5(unittest.TestCase):
    def test_muc_diem_theo_goc_va_ban_dong_o_ask(self):
        n = len(PHANG)
        # mua goc BID: SL = 1 - 0.01, TP = 1 + 0.02
        nk = _chay(PHANG, [_chan(n, 1, sl_diem=100, tp_diem=200, ref_sl="BID", ref_tp="BID")])
        self.assertAlmostEqual(nk[0]["sl"], 0.99)
        self.assertAlmostEqual(nk[0]["tp"], 1.02)
        # mua goc ASK (= 1.001)
        nk = _chay(PHANG, [_chan(n, 1, sl_diem=100, tp_diem=200, ref_sl="ASK", ref_tp="ASK")])
        self.assertAlmostEqual(nk[0]["sl"], 0.991)
        self.assertAlmostEqual(nk[0]["tp"], 1.021)
        # ban goc ASK: SL that 1.011 -> cham khi BID 1.010; TP that 0.981 -> BID 0.980
        nk = _chay(PHANG, [_chan(n, -1, sl_diem=100, tp_diem=200, ref_sl="ASK", ref_tp="ASK")])
        self.assertAlmostEqual(nk[0]["sl"], 1.010)
        self.assertAlmostEqual(nk[0]["tp"], 0.980)
        # ban goc BID: SL that 1.01 -> BID 1.009
        nk = _chay(PHANG, [_chan(n, -1, sl_diem=100, tp_diem=200, ref_sl="BID", ref_tp="BID")])
        self.assertAlmostEqual(nk[0]["sl"], 1.009)
        self.assertAlmostEqual(nk[0]["tp"], 0.979)

    def test_sl_muc_tp_R_tu_gia_khop(self):
        n = len(PHANG)
        nk = _chay(PHANG, [_chan(n, 1, sl=np.full(n, 0.99), tp=1.0)])
        self.assertAlmostEqual(nk[0]["sl"], 0.99)
        self.assertAlmostEqual(nk[0]["tp"], 1.001 + (1.001 - 0.99))     # vao o ASK
        nk = _chay(PHANG, [_chan(n, -1, sl=np.full(n, 1.01), tp=1.0)])
        self.assertAlmostEqual(nk[0]["sl"], 1.01 - 0.001)
        self.assertAlmostEqual(nk[0]["tp"], (1.0 + (1.0 - 1.01)) - 0.001)

    def test_sl_sai_phia_mt5_tu_choi(self):
        n = len(PHANG)
        nk = _chay(PHANG, [_chan(n, 1, sl=np.full(n, 1.0005), tp=1.0)])
        self.assertEqual(nk, [])

    def test_cham_sl_dong_dung_muc(self):
        rows = [(1.0, 1.0, 1.0, 1.0), (1.0, 1.005, 0.995, 1.0), (1.0, 1.0, 0.985, 0.99),
                (0.99, 0.99, 0.99, 0.99)]
        nk = _chay(rows, [_chan(4, 1, sl_diem=100, tp_diem=200, ref_sl="BID", ref_tp="BID")],
                   cp=CP.MoHinhChiPhi(ma="TEST"))
        self.assertEqual((nk[0]["bar_vao"], nk[0]["bar_ra"], nk[0]["ly_do"]), (1, 2, "sl"))
        self.assertAlmostEqual(nk[0]["gia_ra"], 0.99)

    def test_dong_mo_bar_khong_vao_lai_cung_tick(self):
        rows = [(1.0, 1.0, 1.0, 1.0), (1.0, 1.001, 0.999, 1.0), (1.003, 1.003, 1.003, 1.003),
                (1.003, 1.003, 1.003, 1.003), (1.003, 1.003, 1.003, 1.003)]
        n = len(rows)
        muc = np.full(n, 1.002)
        nk = _chay(rows, [_chan(n, 1, cho_bar=(0, 1, 2), sl_diem=500, ref_sl="BID",
                                dong_mo=(">=", muc, "BID"))], cp=CP.MoHinhChiPhi(ma="TEST"))
        self.assertEqual((nk[0]["bar_vao"], nk[0]["bar_ra"], nk[0]["ly_do"]),
                         (1, 2, "dong_mo_bar"))
        # bar 2: da dong o tick dau -> KHONG vao lai cung tick; vao lai o bar 3 (cho[2])
        self.assertEqual(nk[1]["bar_vao"], 3)
        # vao o bar 3 roi dong NGAY cung tick (EA kiem dong sau lenh vao)
        self.assertEqual((nk[1]["bar_ra"], nk[1]["ly_do"]), (3, "dong_mo_bar"))

    def test_dong_mo_ban_so_ask(self):
        rows = [(1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0), (0.9985, 0.9985, 0.9985, 0.9985),
                (0.9985, 0.9985, 0.9985, 0.9985)]
        n = len(rows)
        # ASK o bar 2 = 0.9985 + 0.001*0.9985 > 0.999 -> chua dong; khong spread thi dong
        nk = _chay(rows, [_chan(n, -1, sl_diem=500, ref_sl="ASK",
                                dong_mo=("<=", np.full(n, 0.999), "ASK"))])
        self.assertNotEqual(nk[0].get("ly_do"), "dong_mo_bar")
        nk = _chay(rows, [_chan(n, -1, sl_diem=500, ref_sl="ASK",
                                dong_mo=("<=", np.full(n, 0.999), "ASK"))],
                   cp=CP.MoHinhChiPhi(ma="TEST"))
        self.assertEqual((nk[0]["bar_ra"], nk[0]["ly_do"]), (2, "dong_mo_bar"))

    def test_khong_nhin_truoc_phep_cat(self):
        rng = np.random.default_rng(3)
        n = 1500
        c = 1.1 * np.exp(np.cumsum(rng.normal(0, 0.0015, n)))
        o = np.r_[1.1, c[:-1]]
        h = np.maximum(o, c) * (1 + rng.uniform(0, 0.001, n))
        l = np.minimum(o, c) * (1 - rng.uniform(0, 0.001, n))
        df = pd.DataFrame({"open": o, "high": h, "low": l, "close": c},
                          index=pd.date_range("2024-01-01", periods=n, freq="h"))
        cp = CP.MoHinhChiPhi(ma="TEST", spread_frac_chung=1e-4)
        for ten in ("013_Bollinger_Bands_EA.mq5", "015_Triple_MA_EA.mq5",
                    "017_Ichi_ATR_EA.mq5", "011_RSI_V2_EA.mq5"):
            for sp in _doc(ten):
                cat = 1000
                a = MP.chay_he(df, [NP.sinh_chan(sp, df)], cp, diem=1e-5)
                d2 = df.copy()
                d2.iloc[cat:, :] = d2.iloc[cat:, :] * 1.05      # doi tuong lai
                b = MP.chay_he(d2, [NP.sinh_chan(sp, d2)], cp, diem=1e-5)
                np.testing.assert_allclose(a.loi[:cat - 1], b.loi[:cat - 1], atol=1e-12,
                                           err_msg=f"{ten} {sp['chieu']}")
                self.assertGreater(a.so_lenh, 5, ten)


class DSL(unittest.TestCase):
    def test_kiem_cu_phap_mt5(self):
        sp = _doc("011_RSI_V2_EA.mq5")[0]
        sp2 = dict(sp, sltp=dict(sp["sltp"], sl_kc={"chi_bao": "atr", "n": 14}))
        self.assertTrue(any("nhieu kieu SL" in e for e in NP.kiem_khai_bao(sp2)))
        sp3 = dict(sp, sltp=dict(sp["sltp"], ref_sl=None))
        self.assertTrue(any("ref_sl" in e for e in NP.kiem_khai_bao(sp3)))

    def test_phoi_va_ap_tham_so(self):
        sp = _doc("013_Bollinger_Bands_EA.mq5")[0]
        ts = NP.tham_so_cua(sp)
        self.assertEqual(ts["sltp_sl_diem"], 100.0)
        self.assertEqual(ts["sltp_tp_diem"], 200.0)
        self.assertEqual(ts["dong_mo_bar_muc_n"], 21)
        moi = NP.ap_tham_so(sp, {"sltp_sl_diem": 150.0, "dong_mo_bar_muc_n": 30})
        self.assertEqual(moi["sltp"]["sl_diem"], 150.0)
        self.assertEqual(moi["dong_mo_bar"]["muc"]["n"], 30)
        self.assertEqual(sp["dong_mo_bar"]["muc"]["n"], 21)            # ban goc khong doi

    def test_buoc_chu_ky_cung_handle_bands(self):
        sp = _doc("013_Bollinger_Bands_EA.mq5")[0]
        g = V.buoc_tham_so(sp)
        self.assertTrue(any({"vao0_phai_n", "dong_mo_bar_muc_n"} <= set(x) for x in g), g)
        ts, ax = V.tham_so_nhom([sp])
        # mot khoa chu ky chung cho vao va dong
        self.assertEqual(sum(1 for k in ts if k.endswith("_n")), 1, ts)

    def test_vong_chay_sltp_bang_chay_he(self):
        rng = np.random.default_rng(5)
        n = 3000
        c = 1.1 * np.exp(np.cumsum(rng.normal(0, 0.0015, n)))
        o = np.r_[1.1, c[:-1]]
        df = pd.DataFrame({"open": o, "high": np.maximum(o, c) * 1.0005,
                           "low": np.minimum(o, c) * 0.9995, "close": c},
                          index=pd.date_range("2024-01-01", periods=n, freq="h"))
        r = V.chay_mot_file(SC / "012_MA_V1_EA.mq5", df, "H1", False, 20, cp=CP_S)
        self.assertEqual(len(r), 2)
        for x in r:
            self.assertIn("nhom", x)                  # qua chay_he, khong qua `danh_gia`
            self.assertEqual(x["diem_gia_dinh"], V.DIEM)
            self.assertNotIn("loi", x)


if __name__ == "__main__":
    unittest.main()
