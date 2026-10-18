# -*- coding: utf-8 -*-
"""LUOI MARTINGALE Breakout5 / Breakout5-2-2 (them 10/10/2026 toi).

(1) `ro_mql.doc_ro` doc khoi luoi bang trinh thong dich MQL nho (cong bar, them
lenh CUNG chieu, chuoi lot that), va KHONG doc khi ma doi dang (dot bien);
(2) `mo_phong.chay_he`: them lenh chi o lan goi dau moi bar, chot dinh <=, cong
mo lenh mot lan/bar, vao lai giua bar theo pivot (`muc_lai`), khong nhin truoc;
(3) `doc_chien_luoc` xep loai diem vao dung.
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
B5 = "EA Snippets_Breakout_Breakout5.mq5"
B522 = "EA Snippets_Breakout_Breakout5-2-2.mq5"
KHONG_PHI = CP.MoHinhChiPhi(ma="EURUSD")
LOT_DAU8 = [0.03, 0.04, 0.06, 0.09, 0.13, 0.19, 0.28, 0.41]


def _vb(ten):
    return (MAU / ten).read_text(errors="ignore")


def _ro(vb):
    v = DM._chuan_hoa_mql5(DM._chuan_hoa(vb))
    return RO.doc_ro(v, DM._hang_mql(v), DM.rut_input(v))


class DocLuoi(unittest.TestCase):
    def test_breakout5(self):
        r = _ro(_vb(B5))
        ro = r["ro"]
        self.assertIsNotNone(ro, r["ly_do"])
        self.assertEqual(ro["lot_dau"], 0.02)
        self.assertEqual(ro["dinh"], {"reset_am": False, "moc": 5.0, "ti_le": 0.7,
                                      "phep": "<=", "reset_vao": True})
        self.assertIsNone(ro["cat_lo"])
        self.assertEqual(ro["hedge"], [])
        lu = ro["luoi"]
        self.assertTrue(lu["cong_bar"] and lu["cung_chieu"] and lu["reset_dinh"])
        self.assertEqual(lu["muc_dau"], {"mua": ["BID", -30.0], "ban": ["BID", 30.0]})
        self.assertEqual(lu["buoc"], {"mua": ["BID", -30.0], "ban": ["BID", 30.0]})
        self.assertEqual(lu["lot"][:8], LOT_DAU8)
        self.assertTrue(ro["cong_mo_bar"])
        self.assertEqual([(k["dich"], k["toi_duoc"]) for k in r["khoi"]], [(True, True)])

    def test_breakout5_2_2_giong_breakout5_o_input_mac_dinh(self):
        r = _ro(_vb(B522))
        self.assertIsNotNone(r["ro"], r["ly_do"])
        self.assertEqual(r["ro"], _ro(_vb(B5))["ro"])
        # nhanh else (hedge vung) khong toi duoc voi hedgeatlevel=0
        self.assertEqual([(k["dich"], k["toi_duoc"]) for k in r["khoi"]],
                         [(True, True), (False, False)])
        self.assertTrue(any("expectation = 5" in g for g in r["ghi"]))

    def test_dot_bien_input(self):
        vb = _vb(B5).replace("volumefactor = 1.45;", "volumefactor = 2.0;")
        self.assertEqual(_ro(vb)["ro"]["luoi"]["lot"][:4], [0.04, 0.08, 0.16, 0.32])
        vb = _vb(B5).replace("HedgeRange = 30;", "HedgeRange = 50;")
        lu = _ro(vb)["ro"]["luoi"]
        self.assertEqual(lu["muc_dau"]["mua"], ["BID", -50.0])
        self.assertEqual(lu["buoc"]["ban"], ["BID", 50.0])
        vb = _vb(B522).replace("takeprofitamountperstartvolume = 250;",
                               "takeprofitamountperstartvolume = 500;")
        self.assertEqual(_ro(vb)["ro"]["dinh"]["moc"], 10.0)

    def test_dot_bien_khong_chac_thi_khong_dich(self):
        # bo cong bar trong ham dong -> them lenh moi tick: chua ho tro -> khong dich
        vb = _vb(B5)
        i = vb.find("void checkForClose()")
        j = vb.find("   if ( curTime == prevTime ) {\n      return;\n   }", i)
        self.assertGreater(j, i)
        vb2 = vb[:j] + vb[j:].replace("   if ( curTime == prevTime ) {\n      return;\n   }",
                                      "", 1)
        self.assertIsNone(_ro(vb2)["ro"])
        # ham la trong khoi them lenh
        vb2 = vb.replace("Tradesinfo.lastvolume=volume;\n         trade.PositionOpen",
                         "Tradesinfo.lastvolume=volume;\n         DoSomething();\n"
                         "         trade.PositionOpen")
        self.assertNotEqual(vb2, vb)
        self.assertIsNone(_ro(vb2)["ro"])
        # hedge vung bat (hedgeatlevel=3): dieu kien phu thuoc so lenh -> khong dich
        vb2 = _vb(B522).replace("hedgeatlevel = 0;", "hedgeatlevel = 3;")
        self.assertIsNone(_ro(vb2)["ro"])
        # phi hoa hong tru vao loi lo -> khong dich (chua mo hinh)
        vb2 = _vb(B522).replace("commissonperlot = 0;", "commissonperlot = 7;")
        self.assertIsNone(_ro(vb2)["ro"])
        # khoi luong dau theo von (AccountInfoDouble) -> khong ro -> khong dich
        vb2 = _vb(B522).replace("volumestartbyequitypercent = 0;",
                                "volumestartbyequitypercent = 1;")
        self.assertIsNone(_ro(vb2)["ro"])
        # them lenh NGUOC chieu dang khac (BUY khi gia len) -> hanh vi khac, van doc dung
        # chieu: cung_chieu phai False
        vb2 = vb.replace("if(hedgedown)\n         {\n            type=ORDER_TYPE_SELL;",
                         "if(hedgedown)\n         {\n            type=ORDER_TYPE_BUY;")
        r2 = _ro(vb2)
        self.assertTrue(r2["ro"] is None or r2["ro"]["luoi"]["cung_chieu"] is not True)


class DocChienLuoc(unittest.TestCase):
    def test_phan_loai(self):
        d = DM.doc_chien_luoc(_vb(B5), nguon=B5)
        self.assertEqual(d["phan_loai_vao_lenh"]["quan_ly_dich_duoc"], 1)
        self.assertEqual(d["phan_loai_vao_lenh"]["quan_ly_vi_the"], 0)
        d2 = DM.doc_chien_luoc(_vb(B522), nguon=B522)
        pl = d2["phan_loai_vao_lenh"]
        self.assertEqual((pl["dich_duoc"], pl["quan_ly_dich_duoc"], pl["ma_chet"]), (1, 1, 1))
        for sp in d["co_che"] + d2["co_che"]:
            self.assertIn("luoi", sp["ro"])
            self.assertEqual(NP.kiem_khai_bao(sp), [])
            self.assertTrue(sp["vao_lai_giua_bar"])

    def test_kiem_khai_bao_bat_luoi_hong(self):
        sp = DM.doc_chien_luoc(_vb(B5), nguon=B5)["co_che"][0]
        sp["ro"]["luoi"]["lot"] = [0.03, -1]
        self.assertTrue(NP.kiem_khai_bao(sp))

    def test_muc_lai_la_pivot_gio(self):
        sp = DM.doc_chien_luoc(_vb(B5), nguon=B5)["co_che"]
        df = _df([(1.1, 1.102, 1.098, 1.101), (1.101, 1.103, 1.1, 1.1)])
        ch = [NP.sinh_chan(s, df) for s in sp]
        p = (df["high"] + df["low"] + df["close"]).to_numpy() / 3
        for c in ch:
            self.assertTrue(np.allclose(c["muc_lai"], p))
        self.assertEqual(sorted(c["phep_lai"] for c in ch), ["<", ">="])


# ------------------------------------------------------------------ mo phong
RO_B5 = _ro(_vb(B5))["ro"]


def _df(bars, t0="2024-01-02 08:00"):
    idx = pd.date_range(t0, periods=len(bars), freq="h")
    return pd.DataFrame(bars, columns=["open", "high", "low", "close"], index=idx)


def _chan(n, chieu=1, ro=RO_B5, vao=(0,), muc_lai=None, phep_lai=None):
    cho = np.zeros(n, dtype=bool)
    for k in vao:
        cho[k] = True
    return {"chieu": chieu, "cho": cho, "muc": None, "huong": None, "co": None,
            "loc": None, "sl": None, "tp": None, "keo": None, "giu": 1,
            "chan_boi": [], "dat": [], "ro": ro, "muc_lai": muc_lai, "phep_lai": phep_lai}


def _chay(bars, chan_fn=None, cp=KHONG_PHI):
    df = _df(bars)
    nk = []
    ch = chan_fn(len(df)) if chan_fn else [_chan(len(df))]
    kq = MP.chay_he(df, ch, cp, ma="EURUSD", nhat_ky=nk, diem=1e-5)
    return kq, nk, df


class MoPhongLuoi(unittest.TestCase):
    def test_them_lenh_o_open_moi_bar_roi_chot_dinh(self):
        kq, nk, _ = _chay([(1.1, 1.1, 1.1, 1.1),
                           (1.1, 1.1, 1.099, 1.099),        # vao 1.1; muc 1.0997; KHONG them giua bar
                           (1.099, 1.099, 1.098, 1.098),    # open 1.099 <= 1.0997 -> them 0.03
                           (1.098, 1.1, 1.098, 1.1),        # open 1.098 <= 1.0987 -> them 0.04; dinh 11$
                           (1.1, 1.1, 1.0995, 1.0995),      # roi: dong khi loi <= 7.7
                           (1.0995, 1.0995, 1.0995, 1.0995)])
        x = nk[0]
        self.assertEqual([(t["bar"], t["lot"]) for t in x["them"]], [(2, 0.03), (3, 0.04)])
        self.assertAlmostEqual(x["them"][0]["gia"], 1.099, places=12)
        self.assertEqual(x["ly_do"], "chot_dinh")
        self.assertEqual(x["bar_ra"], 4)
        self.assertAlmostEqual(x["gia_ra"], (9889 + 7.7) / 9000, places=9)
        self.assertAlmostEqual(x["loi_tien"], 7.7, places=6)
        # loi suat theo von danh nghia lenh dau (0.02): trong so 1, 1.5, 2
        # 18/10/2026: SO HOC tung bar (tong trong so cac lenh dang mo x loi suat cua bar), roi moi lay log
        p = x["gia_ra"]
        ky_vong = (np.log(1 + (1.099 / 1.1 - 1)) + np.log(1 + 2.5 * (1.098 / 1.099 - 1))
                   + np.log(1 + 4.5 * (1.1 / 1.098 - 1)) + np.log(1 + 4.5 * (p / 1.1 - 1)))
        self.assertAlmostEqual(kq.loi.sum(), ky_vong, places=9)
        self.assertEqual(kq.chi_tiet["luoi"]["max_lenh"], 3)

    def test_chuoi_lot_moi_bar_mot_lenh(self):
        bars = [(1.1, 1.1, 1.1, 1.1)]
        g = 1.1
        for _ in range(6):
            bars.append((g, g, g - 0.001, g - 0.001))
            g -= 0.001
        kq, nk, _ = _chay(bars)
        self.assertEqual([t["lot"] for t in nk[0]["them"]], [0.03, 0.04, 0.06, 0.09, 0.13])
        self.assertEqual([t["bar"] for t in nk[0]["them"]], [2, 3, 4, 5, 6])

    def test_chua_toi_moc_5_khong_chot(self):
        # loi dinh 4$ (< 5) roi ve 0: khong dong
        kq, nk, _ = _chay([(1.1, 1.1, 1.1, 1.1),
                           (1.1, 1.1002, 1.1, 1.1002),
                           (1.1002, 1.1002, 1.1, 1.1),
                           (1.1, 1.1, 1.1, 1.1)])
        self.assertNotIn("ly_do", nk[0])

    def _hai_chan(self, ml, cong=True):
        ro = dict(RO_B5, cong_mo_bar=cong)

        def f(n):
            lv = np.full(n, ml)
            return [_chan(n, 1, ro, (0,), lv, "<"), _chan(n, -1, ro, (), lv, ">=")]
        return f

    def test_vao_lai_giua_bar_theo_pivot(self):
        bars = [(1.1, 1.1, 1.1, 1.1),
                (1.1, 1.1, 1.1, 1.1),             # vao mua o open bar 1
                (1.1, 1.103, 1.1, 1.102),         # 0.02 lot: dinh 6$ -> dong o 1.1021 (4.2$)
                (1.102, 1.102, 1.102, 1.102)]
        _, nk, _ = _chay(bars, self._hai_chan(1.1022))
        self.assertEqual(nk[0]["ly_do"], "chot_dinh")
        self.assertAlmostEqual(nk[0]["gia_ra"], 1.1021, places=9)
        self.assertAlmostEqual(nk[0]["loi_tien"], 4.2, places=6)
        self.assertEqual((nk[1]["bar_vao"], nk[1]["chieu"]), (2, 1))   # 1.1021 < 1.1022 -> MUA
        self.assertAlmostEqual(nk[1]["gia_vao"], 1.1021, places=9)
        _, nk, _ = _chay(bars, self._hai_chan(1.1020))
        self.assertEqual((nk[1]["bar_vao"], nk[1]["chieu"]), (2, -1))  # >= pivot -> BAN

    def test_cong_mo_lenh_mot_lan_moi_bar(self):
        bars = [(1.1, 1.1, 1.1, 1.1),
                (1.1, 1.103, 1.1, 1.102),         # vao o open bar 1 VA dong trong bar 1
                (1.102, 1.102, 1.102, 1.102)]
        _, nk, _ = _chay(bars, self._hai_chan(1.1022, cong=True))
        self.assertEqual(nk[0]["bar_ra"], 1)
        self.assertEqual(len(nk), 1)              # khong vao lai trong bar 1 (cho o bar 2 = False)
        _, nk, _ = _chay(bars, self._hai_chan(1.1022, cong=False))
        self.assertEqual(nk[1]["bar_vao"], 1)

    def test_khong_nhin_truoc_phep_cat(self):
        sp = DM.doc_chien_luoc(_vb(B5), nguon=B5)["co_che"]
        rng = np.random.default_rng(5)
        n = 700
        c = 1.1 + np.cumsum(rng.normal(0, 0.0012, n))
        o = np.r_[c[0], c[:-1]]
        h = np.maximum(o, c) + rng.uniform(0, 0.001, n)
        l = np.minimum(o, c) - rng.uniform(0, 0.001, n)
        df = _df(list(zip(o, h, l, c)))
        cp = CP.MoHinhChiPhi(ma="EURUSD", spread_frac_chung=1.5e-4, truot_gia_frac=4e-5)
        full = MP.chay_he(df, [NP.sinh_chan(s, df) for s in sp], cp, ma="EURUSD", diem=1e-5)
        self.assertGreater(full.chi_tiet["luoi"]["max_lenh"], 2)
        for m in (150, 333, 600):
            d = df.iloc[:m]
            cut = MP.chay_he(d, [NP.sinh_chan(s, d) for s in sp], cp, ma="EURUSD", diem=1e-5)
            self.assertTrue(np.allclose(cut.loi[:m - 1], full.loi[:m - 1], atol=1e-12), m)


if __name__ == "__main__":
    unittest.main()
