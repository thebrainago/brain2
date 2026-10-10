# -*- coding: utf-8 -*-
"""iMACD / iStochastic cua MT5 -> DSL (them 11/10/2026).

Truoc do hai ham roi vao bang chung: n = doi so 2, BO QUA khung, chu ky cham/
tin hieu, lam muot - sai nghia. Gio chi dich khi khop dung cong thuc MT5:
MACD tin hieu = SMA (khong phai EMA), Stochastic %K co lam muot (slowing).
"""
import unittest

import numpy as np
import pandas as pd

from nhan import doc_ma as DM
from nhan import ngu_phap as NP

DAU = """#property copyright "t"
#include <Trade\\Trade.mqh>
CTrade trade;
int h; double a[], b[];
int OnInit(){ h = %s; return 0; }
bool IsNewBar(){ static datetime p=0; datetime c=iTime(_Symbol,PERIOD_CURRENT,0);
   if(p!=c){p=c; return true;} return false; }
void OnTick(){
   if(!IsNewBar()) return;
   ArraySetAsSeries(a,true); ArraySetAsSeries(b,true);
   CopyBuffer(h,MAIN_LINE,0,3,a);
   CopyBuffer(h,SIGNAL_LINE,0,3,b);
   if(a[1]>b[1] && a[2]<=b[2]) trade.Buy(0.1);
}
"""


def _doc(goi):
    return DM.doc_chien_luoc(DAU % goi, nguon="t.mq5")


def _df(n=500, seed=2):
    rng = np.random.default_rng(seed)
    c = 1.1 + np.cumsum(rng.normal(0, 0.001, n))
    hi = c + np.abs(rng.normal(0, 0.0005, n))
    lo = c - np.abs(rng.normal(0, 0.0005, n))
    return pd.DataFrame({"open": c, "high": hi, "low": lo, "close": c},
                        index=pd.date_range("2022-01-03", periods=n, freq="h"))


class TestMacd(unittest.TestCase):
    def test_doc_macd_chinh_va_tin_hieu_sma(self):
        d = _doc("iMACD(_Symbol,PERIOD_CURRENT,12,26,9,PRICE_CLOSE)")
        self.assertEqual(d["so_vao_lenh_co_co_che"], 1, d["chua_dien_dat_duoc"])
        v = d["co_che"][0]["vao"][0]
        self.assertEqual(v["trai"], {"chi_bao": "macd", "nhanh": 12, "cham": 26,
                                     "tin_hieu": 9, "lay": "macd"})
        self.assertEqual(v["phai"], {"chi_bao": "macd", "nhanh": 12, "cham": 26,
                                     "tin_hieu": 9, "lay": "tin_hieu",
                                     "kieu_tin_hieu": "sma"})
        self.assertEqual(NP.kiem_khai_bao(d["co_che"][0]), [])

    def test_tin_hieu_sma_tinh_tay(self):
        df = _df()
        c = df["close"]
        m = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
        t = NP.toan_hang(df, {"chi_bao": "macd", "nhanh": 12, "cham": 26, "tin_hieu": 9,
                              "lay": "tin_hieu", "kieu_tin_hieu": "sma"})
        np.testing.assert_allclose(t.to_numpy(), m.rolling(9).mean().to_numpy(),
                                   equal_nan=True)
        # khong co kieu_tin_hieu -> EMA nhu cu
        t2 = NP.toan_hang(df, {"chi_bao": "macd", "nhanh": 12, "cham": 26, "tin_hieu": 9,
                               "lay": "tin_hieu"})
        np.testing.assert_allclose(t2.to_numpy(), m.ewm(span=9, adjust=False).mean())

    def test_khung_khac_tu_choi(self):
        d = _doc("iMACD(_Symbol,PERIOD_D1,12,26,9,PRICE_CLOSE)")
        self.assertEqual(d["so_vao_lenh_co_co_che"], 0)


class TestStochastic(unittest.TestCase):
    def test_doc_stoch(self):
        d = _doc("iStochastic(_Symbol,_Period,5,3,3,MODE_SMA,STO_LOWHIGH)")
        self.assertEqual(d["so_vao_lenh_co_co_che"], 1, d["chua_dien_dat_duoc"])
        v = d["co_che"][0]["vao"][0]
        self.assertEqual(v["trai"], {"chi_bao": "stochastic", "n": 5, "lam_muot": 3})
        self.assertEqual(v["phai"], {"chi_bao": "stochastic", "n": 5, "lam_muot": 3,
                                     "lay": "tin_hieu", "d": 3})

    def test_lam_muot_tinh_tay(self):
        df = _df()
        k = NP.toan_hang(df, {"chi_bao": "stochastic", "n": 5, "lam_muot": 3}).to_numpy()
        s = NP.toan_hang(df, {"chi_bao": "stochastic", "n": 5, "lam_muot": 3,
                              "lay": "tin_hieu", "d": 3}).to_numpy()
        h, l, c = (df[x].to_numpy() for x in ("high", "low", "close"))
        i = 200
        tu = mau = 0.0
        for j in range(i - 2, i + 1):
            ll, hh = l[j - 4:j + 1].min(), h[j - 4:j + 1].max()
            tu += c[j] - ll
            mau += hh - ll
        self.assertAlmostEqual(k[i], 100 * tu / mau, places=9)
        self.assertAlmostEqual(s[i], np.mean(k[i - 2:i + 1]), places=9)
        # lam_muot 1 = %K tho nhu cu
        k1 = NP.toan_hang(df, {"chi_bao": "stochastic", "n": 5})
        k1b = NP.toan_hang(df, {"chi_bao": "stochastic", "n": 5, "lam_muot": 1})
        np.testing.assert_allclose(k1.to_numpy(), k1b.to_numpy(), equal_nan=True)

    def test_tu_choi_khi_khong_khop(self):
        for goi in ("iStochastic(_Symbol,_Period,5,3,3,MODE_EMA,STO_LOWHIGH)",
                    "iStochastic(_Symbol,_Period,5,3,3,MODE_SMA,STO_CLOSECLOSE)",
                    "iStochastic(_Symbol,PERIOD_H4,5,3,3,MODE_SMA,STO_LOWHIGH)"):
            self.assertEqual(_doc(goi)["so_vao_lenh_co_co_che"], 0, goi)

    def test_iadx_truc_tiep_khong_dich(self):
        self.assertIsNone(DM._tu_ham_mql5("iADX(_Symbol,_Period,14)"))


if __name__ == "__main__":
    unittest.main()
