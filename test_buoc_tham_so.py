# -*- coding: utf-8 -*-
"""Bo toi uu BUOC cac khoa cung mot input EA (them 11/10/2026).

Giao cat trong bar `rsi[1]>=30 && rsi[0]<30` dung MOT handle iRSI va MOT muc
`100-RSI_Level`. Toi uu tach roi chu ky / nguong hai ve thanh chien luoc khac
(them bac tu do = de qua khop). Buoc chi SIET, khong noi.
"""
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

import vong_thu_nghiem as V
from nhan import doc_ma as DM

LAB = Path(__file__).resolve().parent
RSI_V2 = LAB / "mau_thu" / "mo_rong" / "santiago-cruzlopez" / "011_RSI_V2_EA.mq5"


def _sp(i=0):
    return DM.doc_chien_luoc(RSI_V2.read_text(encoding="utf-8", errors="ignore"),
                             nguon=RSI_V2.name)["co_che"][i]


class TestBuoc(unittest.TestCase):
    def test_nhom_rsi_va_nguong(self):
        self.assertEqual(V.buoc_tham_so(_sp()),
                         [["vao0_trai_n", "vao1_phai_cua_n"],
                          ["vao0_phai_hang", "vao1_phai_nguong_hang"]])

    def test_khong_buoc_khi_khac(self):
        sp = {"vao": [{"trai": {"chi_bao": "rsi", "n": 14}, "phep": ">", "phai": {"hang": 30.0}},
                      {"trai": {"chi_bao": "rsi", "n": 21}, "phep": "<", "phai": {"hang": 70.0}},
                      {"trai": {"chi_bao": "tre", "cua": {"chi_bao": "sma", "n": 5}, "n": 1},
                       "phep": ">", "phai": {"chi_bao": "tre", "cua": {"chi_bao": "sma", "n": 5},
                                             "n": 2}}],
              "giu": 1}
        # hai sma5 (khac do tre) buoc chu ky; do tre (n cua `tre`) KHONG buoc
        self.assertEqual(V.buoc_tham_so(sp), [["vao2_phai_cua_n", "vao2_trai_cua_n"]])

    def test_toi_uu_giu_nhom_bang_nhau(self):
        rng = np.random.default_rng(4)
        n = 3000
        c = 1.1 + np.cumsum(rng.normal(0, 0.002, n))
        df = pd.DataFrame({"open": c, "high": c + 0.0015, "low": c - 0.0015, "close": c},
                          index=pd.date_range("2021-01-04", periods=n, freq="h"))
        sp = _sp()
        tot, _, so = V.toi_uu(sp, df, "H1", 5, luot=1, cp=V.mo_hinh_chi_phi(df, "EURUSD", True))
        self.assertGreater(so, 1)
        for g in V.buoc_tham_so(sp):
            self.assertEqual(len({tot[k] for k in g}), 1, g)
        self.assertEqual(set(tot), set(V.NP.tham_so_cua(sp)))

    def test_nhom_he_gop_khoa(self):
        sp0, sp1 = _sp(0), _sp(1)
        ts, ax = V.tham_so_nhom([sp0, sp1])
        for k, ds in ax.items():
            for c, m in ds:
                self.assertIn(m, V.NP.tham_so_cua([sp0, sp1][c]))
        # rsi chu ky chung ca hai chan + buoc trong chan -> mot khoa duy nhat
        k_rsi = [k for k, ds in ax.items() if (0, "vao0_trai_n") in ds]
        self.assertEqual(len(k_rsi), 1)
        self.assertIn((1, "vao1_phai_cua_n"), ax[k_rsi[0]])


if __name__ == "__main__":
    unittest.main()
