# -*- coding: utf-8 -*-
"""CHOT CAP (hai co `static int` tieu thu khi vao lenh) - them 11/10/2026.

(1) `doc_ma` + `nhan/chot_mql.py` doc 016_CCI_2MAVG thanh toan tu `chot_cap` + `ra`;
(2) tin hieu/lenh dong KHOP TUNG BAR voi ban chep tay OnTick cua EA (ke ca loi
`fastMA2 = MAVG2_Buffer[2]`) tren du lieu gia lap; (3) khong nhin truoc (phep cat);
(4) tu choi CO LY DO khi may trang thai khong chung minh duoc; (5) DSL: kiem cu
phap, hang so cung khong phoi cho toi uu, `giu` khong phoi khi co `ra`.
"""
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from nhan import doc_ma as DM
from nhan import ngu_phap as NP
import vong_thu_nghiem as V

F016 = (Path(__file__).resolve().parent / "mau_thu" / "mo_rong" / "santiago-cruzlopez"
        / "016_CCI_2MAVG_EA.mq5")


def _vb(thay=None):
    vb = F016.read_text(errors="ignore")
    for a, b in (thay or []):
        assert a in vb, a
        vb = vb.replace(a, b)
    return vb


def _doc(thay=None):
    return DM.doc_chien_luoc(_vb(thay), nguon="016")


def _df(n=3000, seed=7):
    r = np.random.default_rng(seed)
    c = 1.1 * np.exp(np.cumsum(r.normal(0, 0.0015, n)))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) * (1 + np.abs(r.normal(0, 0.0005, n)))
    l = np.minimum(o, c) * (1 - np.abs(r.normal(0, 0.0005, n)))
    idx = pd.date_range("2024-01-01", periods=n, freq="h")
    return pd.DataFrame({"open": o, "high": h, "low": l, "close": c}, index=idx)


def _tham_chieu(df):
    """Chep tay OnTick cua 016 (tick dau bar j: buffer[1] = bar j-1, [2] = j-2)."""
    cci = NP.toan_hang(df, {"chi_bao": "cci", "n": 14, "cot": "close"}).to_numpy()
    f = NP.toan_hang(df, {"chi_bao": "ema", "n": 10}).to_numpy()
    s = NP.toan_hang(df, {"chi_bao": "ema", "n": 60}).to_numpy()
    n = len(df)
    MA = CC = 0
    vao = {1: np.zeros(n, bool), -1: np.zeros(n, bool)}
    dong = {1: np.zeros(n, bool), -1: np.zeros(n, bool)}   # dong lenh MUA / BAN
    for j in range(2, n):
        c1, c2 = cci[j - 1], cci[j - 2]
        if c1 > 0 and c2 <= 0:
            CC = 1
        if c1 < 0 and c2 >= 0:
            CC = -1
        fa1, fa2, sl1, sl2 = f[j - 1], s[j - 2], s[j - 1], s[j - 2]   # loi EA giu nguyen
        if fa1 > sl1 and fa2 <= sl2:
            MA = 1
            dong[-1][j] = True
        if fa1 < sl1 and fa2 >= sl2:
            MA = -1
            dong[1][j] = True
        if MA != 0 and MA == CC:
            vao[MA][j] = True
            MA = CC = 0
    return vao, dong


class DocChot016(unittest.TestCase):
    def test_hai_co_che_chot_cap_va_ra(self):
        d = _doc()
        self.assertEqual(d["so_vao_lenh"], 2)
        self.assertEqual(d["so_vao_lenh_co_co_che"], 2)
        cc = {sp["chieu"]: sp for sp in d["co_che"]}
        self.assertEqual(set(cc), {1, -1})
        for ch, sp in cc.items():
            self.assertEqual(NP.kiem_khai_bao(sp), [])
            t = sp["vao"][0]["trai"]
            self.assertEqual(t["chi_bao"], "chot_cap")
            self.assertEqual(sp["vao"][0]["phai"], {"hang_co_dinh": float(ch)})
            self.assertEqual([(x["bien"], x["gt"]) for x in t["dat"]],
                             [("b", 1), ("b", -1), ("a", 1), ("a", -1)])
            # ve luon dung `s2 <= s2` (loi EA) da bo -> su kien MA con mot ve
            self.assertEqual(len(t["dat"][2]["khi"]), 1)
            self.assertEqual(sp["ra"], [{"trai": {"chi_bao": "ema", "n": 10},
                                         "phep": "<" if ch == 1 else ">",
                                         "phai": {"chi_bao": "ema", "n": 60}}])
            self.assertTrue(any("LUON DUNG" in g for g in sp["gia_dinh"]))
            self.assertNotIn("sltp", sp)

    def test_khop_tung_bar_voi_ban_chep_tay(self):
        df = _df()
        vao, dong = _tham_chieu(df)
        cc = {sp["chieu"]: sp for sp in _doc()["co_che"]}
        for ch in (1, -1):
            v = NP._dieu_kien(df, cc[ch]["vao"], mac_dinh=False).to_numpy()
            r = NP._dieu_kien(df, cc[ch]["ra"], mac_dinh=False).to_numpy()
            e = np.r_[False, v[:-1]]            # tin hieu close i -> tick dau bar i+1
            x = np.r_[False, r[:-1]]
            self.assertGreater(vao[ch].sum(), 10)
            np.testing.assert_array_equal(e[61:], vao[ch][61:])
            np.testing.assert_array_equal(x[61:], dong[ch][61:])

    def test_khong_nhin_truoc(self):
        df = _df(1500)
        sp = _doc()["co_che"][0]
        ok, _ = NP.kiem_khong_nhin_truoc(sp, df)
        self.assertTrue(ok)
        t = sp["vao"][0]["trai"]
        full = NP.toan_hang(df, t).to_numpy()
        cut = NP.toan_hang(df.iloc[:900].copy(), t).to_numpy()
        np.testing.assert_array_equal(full[:900], cut)


class TuChoiChot(unittest.TestCase):
    def _kiem_tu_choi(self, thay, chu):
        d = _doc(thay)
        self.assertEqual(d["co_che"], [], d["chua_dien_dat_duoc"])
        self.assertTrue(any(x.startswith("chot:") and chu in x
                            for x in d["chua_dien_dat_duoc"]), d["chua_dien_dat_duoc"])

    def test_khong_cong_bar_moi(self):
        self._kiem_tu_choi([("bool newBar = NewBar();", "bool newBar = true;")], "cong bar moi")

    def test_co_dung_ngoai_mau(self):
        self._kiem_tu_choi([("bool newBar = NewBar();",
                        "bool newBar = NewBar();\n   if(MACross>0) Print(1);")], "ngoai mau")

    def test_khoi_reset_co_lenh_khac(self):
        self._kiem_tu_choi([("            CCICross = 0;\n",
                        "            CCICross = 0;\n            Print(2);\n")], "reset")

    def test_khong_static(self):
        self._kiem_tu_choi([("static int MACross  = 0;", "int MACross  = 0;")], "static int")

    def test_gan_gia_tri_khac(self):
        self._kiem_tu_choi([("if(CCI1>0 && CCI2<=0) CCICross =  1;",
                        "if(CCI1>0 && CCI2<=0) CCICross =  2;")], "ngoai mau")

    def test_ham_bar_moi_khac_mau(self):
        self._kiem_tu_choi([("if(now == current) return(false);", "if(now == current) return(true);")],
                      "cong bar moi")


class DSLChot(unittest.TestCase):
    def test_kiem_cu_phap(self):
        t = {"chi_bao": "chot_cap", "kiem": ["a", "b"],
             "dat": [{"bien": "a", "gt": 2, "khi": [{"trai": {"chi_bao": "ema", "n": 3},
                                                      "phep": ">", "phai": {"hang": 0}}]}]}
        loi = NP._kiem_toan_hang(t)
        self.assertTrue(any("gt" in x for x in loi))
        self.assertTrue(any("'b'" in x for x in loi))

    def test_hang_co_dinh_va_giu_khong_phoi(self):
        sp = _doc()["co_che"][0]
        ts = NP.tham_so_cua(sp)
        self.assertFalse(any("hang" in k for k in ts))
        # chu ky cung handle buoc chung ca o `vao` lan `ra`
        nhom = [sorted(g) for g in V.buoc_tham_so(sp)]
        self.assertTrue(any("ra0_trai_n" in g and len(g) == 3 for g in nhom))
        k = next(k for k in ts if k.endswith("dat2_khi0_trai_n"))
        moi = NP.ap_tham_so(sp, {k: 20})
        self.assertEqual(moi["vao"][0]["trai"]["dat"][2]["khi"][0]["trai"]["n"], 20)

    def test_mau_thu_khong_doi(self):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent / "mau_thu"))
        import do_moc
        r = do_moc.do()
        self.assertEqual((r["vao_co"], r["vao_lenh"]), (13, 22))


if __name__ == "__main__":
    unittest.main()
