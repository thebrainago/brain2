# -*- coding: utf-8 -*-
"""SL/TP THEO KHOANG CACH ATR cua EA Template (them 10/10/2026, vong "ro hedge").

(1) `ro_mql.doc_sltp_kc` doc dung SL = gia -+ max(InpSlAtrMult*ATR, 3*spread),
TP = gia +- InpTpAtrMult*ATR, khoi luong theo rui ro InpRiskPct, loc spread
InpMaxSpreadPts - va KHONG doc khi mau doi; (2) `mo_phong.chay_he` khop dung gia,
trong so = rui_ro*gia/khoang_SL, khong vao lai giua bar (EA chi vao o bar moi),
mot vi the mot luc; (3) ATR kieu MT5 (trung binh cong TR), khong nhin truoc.
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
TPL = "mql5-pro_assets_EA_Template.mq5"


def _vb():
    return (MAU / TPL).read_text(errors="ignore")


def _kc(vb):
    v = DM._chuan_hoa(vb)
    return RO.doc_sltp_kc(v, "OpenTrade", DM._hang_mql(DM._chuan_hoa_mql5(v)))


class DocATR(unittest.TestCase):
    def test_doc_dung(self):
        k, ghi, sm = _kc(_vb())
        self.assertEqual(k["sl_kc"]["he_so"], [2.0])
        self.assertEqual(k["tp_kc"]["he_so"], [3.0])
        self.assertEqual(k["sl_kc"]["toan_hang"][0], {"chi_bao": "atr", "n": 14, "kieu": "sma"})
        self.assertEqual(k["sl_kc_min_spread"], 3.0)
        self.assertEqual(k["rui_ro"], 0.01)
        self.assertEqual(sm, 30.0)

    def test_dot_bien_input(self):
        vb = _vb().replace("InpSlAtrMult    = 2;", "InpSlAtrMult    = 4;") \
                  .replace("InpAtrPeriod    = 14;", "InpAtrPeriod    = 21;") \
                  .replace("InpRiskPct      = 1.0;", "InpRiskPct      = 2.5;")
        k, _, _ = _kc(vb)
        self.assertEqual(k["sl_kc"]["he_so"], [4.0])
        self.assertEqual(k["sl_kc"]["toan_hang"][0]["n"], 21)
        self.assertEqual(k["rui_ro"], 0.025)

    def test_dot_bien_khong_chac_thi_khong_doc(self):
        # ATR o bar 0 (dang chay) thay vi bar 1 -> khong dung mau
        k, _, _ = _kc(_vb().replace("CopyBuffer(g_st.hATR, 0, 1, 1, v)",
                                    "CopyBuffer(g_st.hATR, 0, 0, 1, v)"))
        self.assertIsNone(k)
        # SL tinh khac dang (khong phai price - dir*slDist)
        k, _, _ = _kc(_vb().replace("NormalizePrice(price - dir * slDist)",
                                    "NormalizePrice(price - dir * slDist * 0.5)"))
        self.assertIsNone(k)

    def test_spec_template(self):
        d = DM.doc_chien_luoc(_vb(), nguon=TPL)
        self.assertEqual(len(d["co_che"]), 2)
        for sp in d["co_che"]:
            self.assertEqual(NP.kiem_khai_bao(sp), [])
            self.assertEqual(sp["nhom_he"], TPL)
            self.assertEqual(sp["loc_spread_diem"], 30.0)
            ts = NP.tham_so_cua(sp)
            self.assertNotIn("giu", ts)
            self.assertEqual((ts["sltp_sl_he"], ts["sltp_tp_he"], ts["sltp_atr_n"]),
                             (2.0, 3.0, 14))
            self.assertFalse(any("CountMyPositions" in x for x in sp["bo_qua_quan_tri"]))


def _df(bars, t0="2024-01-02 08:00"):
    idx = pd.date_range(t0, periods=len(bars), freq="h")
    return pd.DataFrame(bars, columns=["open", "high", "low", "close"], index=idx)


def _chan(n, chieu=1, sl_kc=0.002, tp_kc=0.003, vao=(0,), rui_ro=None, min_sp=None,
          sm=None):
    cho = np.zeros(n, dtype=bool)
    for k in vao:
        cho[k] = True
    return {"chieu": chieu, "cho": cho, "muc": None, "huong": None, "co": None,
            "loc": None, "sl": None, "tp": None, "keo": None, "giu": 1,
            "chan_boi": [], "dat": [], "ro": None,
            "sl_kc": np.full(n, sl_kc), "tp_kc": np.full(n, tp_kc),
            "sl_kc_min_spread": min_sp, "rui_ro": rui_ro, "spread_max_diem": sm}


class MoPhongATR(unittest.TestCase):
    def test_tp_va_trong_so(self):
        bars = [(1.1, 1.1, 1.1, 1.1), (1.1, 1.104, 1.1, 1.104), (1.104,) * 4]
        df = _df(bars)
        nk = []
        kq = MP.chay_he(df, [_chan(3, rui_ro=0.01)], CP.MoHinhChiPhi(ma="EURUSD"),
                        nhat_ky=nk, diem=1e-5)
        self.assertEqual(nk[0]["ly_do"], "tp")
        self.assertAlmostEqual(nk[0]["gia_ra"], 1.103, places=9)
        w = 0.01 * 1.1 / 0.002
        self.assertAlmostEqual(nk[0]["trong_so"], w, places=9)
        # 18/10/2026: SO HOC tung bar - log(1 + w * loi suat), khong phai w * log(gia ra / gia vao)
        self.assertAlmostEqual(kq.loi.sum(), np.log(1 + w * (1.103 / 1.1 - 1)), places=9)

    def test_sl_ban_va_khoang_toi_thieu_spread(self):
        # spread 1e-3 (frac) -> 3*spread*gia = 0.0033 > 0.002 -> SL ban = 1.1033
        cp = CP.MoHinhChiPhi(ma="EURUSD", spread_frac_chung=1e-3)
        bars = [(1.1, 1.1, 1.1, 1.1), (1.1, 1.104, 1.1, 1.104), (1.104,) * 4]
        nk = []
        MP.chay_he(_df(bars), [_chan(3, chieu=-1, min_sp=3.0)], cp, nhat_ky=nk, diem=1e-5)
        self.assertAlmostEqual(nk[0]["sl"], 1.1 + 0.0033, places=9)
        self.assertEqual(nk[0]["ly_do"], "sl")

    def test_loc_spread(self):
        cp = CP.MoHinhChiPhi(ma="EURUSD", spread_frac_chung=3e-4)   # ~33 point @1.1
        bars = [(1.1,) * 4] * 4
        nk = []
        MP.chay_he(_df(bars), [_chan(4, sm=30.0, vao=(0, 1, 2))], cp, nhat_ky=nk, diem=1e-5)
        self.assertEqual(nk, [])
        MP.chay_he(_df(bars), [_chan(4, sm=40.0, vao=(0, 1, 2))], cp, nhat_ky=nk, diem=1e-5)
        self.assertEqual(len(nk), 1)

    def test_khong_vao_lai_giua_bar_va_mot_vi_the(self):
        # SL cham o bar 1 -> khong vao lai trong bar 1 du cho[0] dung; bar 2 vao lai
        bars = [(1.1, 1.1, 1.1, 1.1), (1.1, 1.1, 1.097, 1.099), (1.099,) * 4, (1.099,) * 4]
        nk = []
        MP.chay_he(_df(bars), [_chan(4, vao=(0, 1)), _chan(4, chieu=-1, vao=(0, 1))],
                   CP.MoHinhChiPhi(ma="EURUSD"), nhat_ky=nk, diem=1e-5)
        self.assertEqual([x["bar_vao"] for x in nk], [1, 2])
        self.assertEqual(nk[0]["ly_do"], "sl")

    def test_atr_mt5_trung_binh_cong(self):
        rng = np.random.default_rng(1)
        n = 100
        c = 1.1 + np.cumsum(rng.normal(0, 1e-3, n))
        o = np.r_[c[0], c[:-1]]
        df = _df(list(zip(o, np.maximum(o, c) + 5e-4, np.minimum(o, c) - 5e-4, c)))
        a = NP.toan_hang(df, {"chi_bao": "atr", "n": 14, "kieu": "sma"}).to_numpy()
        tr = np.maximum(df.high - df.low, np.maximum((df.high - df.close.shift()).abs(),
                                                     (df.low - df.close.shift()).abs()))
        self.assertAlmostEqual(a[50], tr.iloc[37:51].mean(), places=12)
        # khong nhin truoc: cat du lieu khong doi gia tri qua khu
        b = NP.toan_hang(df.iloc[:60], {"chi_bao": "atr", "n": 14, "kieu": "sma"}).to_numpy()
        self.assertTrue(np.allclose(a[:60], b, equal_nan=True))

    def test_he_template_that_chay_va_khong_nhin_truoc(self):
        d = DM.doc_chien_luoc(_vb(), nguon=TPL)["co_che"]
        rng = np.random.default_rng(5)
        n = 800
        c = 1.1 + np.cumsum(rng.normal(0, 1e-3, n))
        o = np.r_[c[0], c[:-1]]
        df = _df(list(zip(o, np.maximum(o, c) + rng.uniform(0, 8e-4, n),
                          np.minimum(o, c) - rng.uniform(0, 8e-4, n), c)))
        cp = CP.MoHinhChiPhi(ma="EURUSD", spread_frac_chung=1.5e-4, truot_gia_frac=4e-5)
        full = MP.chay_he(df, [NP.sinh_chan(sp, df) for sp in d], cp, ma="EURUSD", diem=1e-5)
        self.assertGreater(full.so_lenh, 20)
        for m in (300, 555):
            dc = df.iloc[:m]
            cut = MP.chay_he(dc, [NP.sinh_chan(sp, dc) for sp in d], cp, ma="EURUSD",
                             diem=1e-5)
            self.assertTrue(np.allclose(cut.loi[:m - 1], full.loi[:m - 1], atol=1e-12), m)


if __name__ == "__main__":
    unittest.main()
