# -*- coding: utf-8 -*-
"""Thu vien co che nho (vong 7): to hop <= 3 manh, moi manh doi dung truong chan."""
import unittest

import numpy as np
import pandas as pd

from nhan import mo_phong as MP
from nhan import chi_phi as CP
from nhan import thu_vien_co_che as TV


def _df(n=400, seed=1):
    rng = np.random.default_rng(seed)
    c = 1.1 + np.cumsum(rng.normal(0, 5e-4, n))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) + 2e-4
    l = np.minimum(o, c) - 2e-4
    idx = pd.date_range("2025-01-06", periods=n, freq="1h")
    return pd.DataFrame({"open": o, "high": h, "low": l, "close": c}, index=idx)


def _chan(df, chieu=1):
    n = len(df)
    cho = np.zeros(n, dtype=bool)
    cho[::7] = True
    return {"chieu": chieu, "cho": cho, "muc": None, "muc_lai": None, "phep_lai": None,
            "huong": None, "co": None, "loc": None, "sl": None, "tp": None, "keo": None,
            "giu": 3, "chan_boi": [], "dat": [], "ro": None, "sl_kc": None, "tp_kc": None,
            "sl_kc_min_spread": None, "rui_ro": None, "spread_max_diem": None, "mt5": False,
            "sl_diem": None, "tp_diem": None, "ref_sl": None, "ref_tp": None, "dong_mo": None,
            "het_bar": None, "dong_pip": None, "dao_khi_nguoc": False}


class ThuVien(unittest.TestCase):
    def test_so_to_hop(self):
        th = TV.to_hop()
        self.assertEqual(len(th), 26)
        self.assertEqual(th[0], ())
        self.assertTrue(all(len(x) <= 3 for x in th))
        self.assertEqual(len(set(th)), 26)

    def test_manh_doi_dung_truong_va_khong_sua_goc(self):
        df = _df()
        c = _chan(df)
        ra = TV.ap_manh([c], df, ("A", "S", "D"))[0]
        self.assertIsNone(c["sl_kc"])                       # ban goc khong doi
        a = TV.atr(df)
        np.testing.assert_allclose(ra["sl_kc"][20:], 1.5 * a[20:])
        np.testing.assert_allclose(ra["tp_kc"][20:], 3.0 * a[20:])
        self.assertEqual(ra["spread_max_diem"], 30.0)
        self.assertIn(TV.BIEN_NGAY, ra["chan_boi"])
        self.assertIn(TV.BIEN_NGAY, ra["dat"])

    def test_phien_dung_gio_bar_vao(self):
        df = _df()
        ra = TV.ap_manh([_chan(df)], df, ("P",))[0]
        gio = df.index.hour
        for i in np.flatnonzero(ra["cho"]):
            self.assertTrue(7 <= gio[i + 1] < 22)

    def test_keo_them_sl_khi_chua_co(self):
        df = _df()
        ra = TV.ap_manh([_chan(df, -1)], df, ("T",))[0]
        self.assertIsNotNone(ra["sl_kc"])
        a = TV.atr(df)
        np.testing.assert_allclose(ra["keo"][20:], df["close"].to_numpy()[20:] + a[20:])

    def test_gioi_han_ngay_chan_lenh_thu_hai(self):
        df = _df()
        cp = CP.MoHinhChiPhi(ma="EURUSD")
        c = _chan(df)
        k0 = MP.chay_he(df, [c], cp, khung="H1", diem=1e-5)
        k1 = MP.chay_he(df, TV.ap_manh([c], df, ("D",)), cp, khung="H1", diem=1e-5)
        nk: list = []
        MP.chay_he(df, TV.ap_manh([c], df, ("D",)), cp, khung="H1", diem=1e-5, nhat_ky=nk)
        ngay = [df.index[x["bar_vao"]].date() for x in nk]
        self.assertEqual(len(ngay), len(set(ngay)))         # toi da 1 lenh / ngay
        self.assertLess(k1.so_lenh, k0.so_lenh)

    def test_ro_khong_ap(self):
        df = _df()
        c = _chan(df)
        c["ro"] = {"x": 1}
        with self.assertRaises(ValueError):
            TV.ap_manh([c], df, ("A",))
        self.assertEqual(len(TV.ap_manh([c], df, ())), 1)


if __name__ == "__main__":
    unittest.main()
