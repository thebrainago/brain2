# -*- coding: utf-8 -*-
"""Chi bao SONG o bar 0 -> muc gia trong bar (them 11/10/2026).

EA kiem MOI tick doc `rsi[0]`/`ma[0]`: gia tri tinh voi close = gia tick, doi
trong bar. `X[1] >= 30 && X[0] < 30` khong mau thuan - no la giao cat GIUA bar.
RSI/MA tren close tang don dieu theo gia tick nen dieu kien quy ve `gia ? P*`
voi P* biet o close bar truoc (`ngu_phap.muc_song`) -> lenh dung (`trong_bar`).
Test kiem: P* dung tung so (noi them P* vao chuoi roi tinh lai chi bao), khong
nhin truoc (cat chuoi), bo doc tao dung khoi, EA chi chay tick dau van bi tu
choi, mo phong khop dung nhu duyet gia tick (low/high) bang vet can.
"""
import unittest

import numpy as np
import pandas as pd

from nhan import chi_phi as CP
from nhan import doc_ma as DM
from nhan import mau as M
from nhan import mo_phong as MP
from nhan import ngu_phap as NP


def _df(n=600, seed=3, buoc=0.0012):
    rng = np.random.default_rng(seed)
    c = 1.1 + np.cumsum(rng.normal(0, buoc, n))
    o = np.r_[c[0], c[:-1]] + rng.normal(0, buoc / 10, n)
    hi = np.maximum(o, c) + np.abs(rng.normal(0, buoc / 2, n))
    lo = np.minimum(o, c) - np.abs(rng.normal(0, buoc / 2, n))
    idx = pd.date_range("2022-01-03", periods=n, freq="h")
    return pd.DataFrame({"open": o, "high": hi, "low": lo, "close": c,
                         "tick_volume": 100}, index=idx)


def _noi(df, i, p):
    """Chuoi close den bar i roi THEM mot bar co close = p (gia tick bar i+1)."""
    c = np.append(df["close"].to_numpy()[:i + 1], p)
    return pd.DataFrame({"open": c, "high": c, "low": c, "close": c})


class TestMucSong(unittest.TestCase):
    def setUp(self):
        self.df = _df()

    def test_rsi_dung_tung_so(self):
        for L in (30.0, 70.0, 50.0):
            lv = NP.toan_hang(self.df, {"chi_bao": "muc_song", "cua": {"chi_bao": "rsi", "n": 21},
                                        "nguong": {"hang": L}})
            for i in (60, 300, 598):
                r = M.rsi(_noi(self.df, i, lv.iloc[i])["close"], 21).iloc[-1]
                self.assertAlmostEqual(r, L, places=6)

    def test_rsi_nguong_ngoai_khoang_la_nan(self):
        lv = NP.toan_hang(self.df, {"chi_bao": "muc_song", "cua": {"chi_bao": "rsi", "n": 14},
                                    "nguong": {"hang": 100.0}})
        self.assertTrue(lv.isna().all())

    def test_giao_cat_ma_dung_tung_so(self):
        for F, S in (({"chi_bao": "sma", "n": 14}, {"chi_bao": "sma", "n": 21}),
                     ({"chi_bao": "ema", "n": 10}, {"chi_bao": "wma", "n": 30}),
                     ({"chi_bao": "smma", "n": 5}, {"chi_bao": "gia", "cot": "close"}),
                     ({"chi_bao": "wma", "n": 7}, {"chi_bao": "ema", "n": 40})):
            lv = NP.toan_hang(self.df, {"chi_bao": "muc_song", "cua": F, "cat": S})
            for i in (100, 598):
                d2 = _noi(self.df, i, lv.iloc[i])
                self.assertAlmostEqual(NP.toan_hang(d2, F).iloc[-1],
                                       NP.toan_hang(d2, S).iloc[-1], places=9, msg=str(F))

    def test_nguong_ma_la_chuoi(self):
        F = {"chi_bao": "ema", "n": 20}
        X = {"chi_bao": "sma", "n": 50}
        lv = NP.toan_hang(self.df, {"chi_bao": "muc_song", "cua": F, "nguong": X})
        i = 400
        d2 = _noi(self.df, i, lv.iloc[i])
        self.assertAlmostEqual(NP.toan_hang(d2, F).iloc[-1],
                               NP.toan_hang(self.df, X).iloc[i], places=9)

    def test_khong_nhin_truoc_cat_chuoi(self):
        for t in ({"chi_bao": "muc_song", "cua": {"chi_bao": "rsi", "n": 21},
                   "nguong": {"hang": 30.0}},
                  {"chi_bao": "muc_song", "cua": {"chi_bao": "sma", "n": 14},
                   "cat": {"chi_bao": "sma", "n": 21}},
                  {"chi_bao": "muc_song", "cua": {"chi_bao": "wma", "n": 9},
                   "cat": {"chi_bao": "gia", "cot": "close"}}):
            full = NP.toan_hang(self.df, t).to_numpy()
            for k in (80, 250, 599):
                cat = NP.toan_hang(self.df.iloc[:k + 1].copy(), t).to_numpy()
                np.testing.assert_allclose(cat, full[:k + 1], rtol=0, atol=1e-12,
                                           equal_nan=True)

    def test_kiem_cu_phap(self):
        ok = {"chi_bao": "muc_song", "cua": {"chi_bao": "sma", "n": 14},
              "cat": {"chi_bao": "sma", "n": 21}}
        self.assertEqual(NP._kiem_toan_hang(ok), [])
        cung_w = {"chi_bao": "muc_song", "cua": {"chi_bao": "sma", "n": 14},
                  "cat": {"chi_bao": "smma", "n": 14}}
        self.assertTrue(NP._kiem_toan_hang(cung_w))
        self.assertTrue(NP._kiem_toan_hang({"chi_bao": "muc_song",
                                            "cua": {"chi_bao": "cci", "n": 14},
                                            "nguong": {"hang": 0.0}}))
        self.assertTrue(NP._kiem_toan_hang({"chi_bao": "muc_song",
                                            "cua": {"chi_bao": "rsi", "n": 14, "cot": "open"},
                                            "nguong": {"hang": 30.0}}))
        self.assertEqual(NP.huong_song(ok), 1)
        self.assertEqual(NP.huong_song(dict(ok, cua={"chi_bao": "sma", "n": 30})), -1)


DAU = """#property copyright "t"
#include <Trade\\Trade.mqh>
CTrade trade;
input int RSI_Period = 21;
input int RSI_Level = 70;
int h, hf, hs; double r[], f[], s[];
datetime t0 = 0;
int OnInit(){ h = iRSI(_Symbol,PERIOD_CURRENT,RSI_Period,%s);
   hf = iMA(_Symbol,PERIOD_CURRENT,14,0,MODE_SMA,PRICE_CLOSE);
   hs = iMA(_Symbol,PERIOD_CURRENT,21,0,%s,PRICE_CLOSE); return 0; }
bool IsNewBar(){ static datetime p=0; datetime c=iTime(_Symbol,PERIOD_CURRENT,0);
   if(p!=c){p=c; return true;} return false; }
void OnTick(){
%s
   int v = CopyBuffer(h,0,0,2,r);
   if(v != 2){ Print("thieu"); return; }
   CopyBuffer(hf,0,0,2,f); CopyBuffer(hs,0,0,2,s);
   ArraySetAsSeries(r,true); ArraySetAsSeries(f,true); ArraySetAsSeries(s,true);
   if(%s && t0 != iTime(_Symbol,PERIOD_CURRENT,0)){
      t0 = iTime(_Symbol,PERIOD_CURRENT,0);
      trade.Buy(0.1);
   }
}
"""

RSI_CAT = "r[1]>=(100-RSI_Level) && r[0]<(100-RSI_Level)"


def _doc(dk, cong="", gia="PRICE_CLOSE", pp="MODE_SMA"):
    return DM.doc_chien_luoc(DAU % (gia, pp, cong, dk), nguon="t.mq5")


class TestDocChiBaoSong(unittest.TestCase):
    def test_rsi_cat_xuong_moi_tick_thanh_lenh_dung(self):
        d = _doc(RSI_CAT)
        self.assertEqual(d["so_vao_lenh_co_co_che"], 1, d["chua_dien_dat_duoc"])
        sp = d["co_che"][0]
        self.assertIn({"trai": {"chi_bao": "rsi", "n": 21}, "phep": ">=",
                       "phai": {"hang": 30.0}}, sp["vao"])
        self.assertIn({"trai": {"chi_bao": "gia", "cot": "close"}, "phep": "<",
                       "phai": {"chi_bao": "muc_song", "cua": {"chi_bao": "rsi", "n": 21},
                                "nguong": {"hang": 30.0}}}, sp["vao"])
        self.assertEqual(sp["trong_bar"]["huong"], "<")
        self.assertEqual(NP.kiem_khai_bao(sp), [])
        ok, ly_do = NP.kiem_khong_nhin_truoc(sp, _df(400))
        self.assertTrue(ok, ly_do)
        self.assertIn("v != 2", sp["bo_qua_quan_tri"])

    def test_tick_dau_van_la_mau_thuan(self):
        d = _doc(RSI_CAT, cong="   if(!IsNewBar()) return;")
        self.assertEqual(d["so_vao_lenh_co_co_che"], 0)
        self.assertTrue(any("mau thuan" in x for x in d["chua_dien_dat_duoc"]))

    def test_rsi_gia_open_khong_dao(self):
        d = _doc(RSI_CAT, gia="PRICE_OPEN")
        self.assertEqual(d["so_vao_lenh_co_co_che"], 0)
        self.assertTrue(any("chua dao duoc" in x for x in d["chua_dien_dat_duoc"]))

    def test_giao_cat_hai_ma(self):
        d = _doc("f[1]<=s[1] && f[0]>s[0]")
        sp = d["co_che"][0]
        self.assertEqual(sp["trong_bar"]["huong"], ">")
        self.assertIn({"trai": {"chi_bao": "gia", "cot": "close"}, "phep": ">",
                       "phai": {"chi_bao": "muc_song", "cua": {"chi_bao": "sma", "n": 14},
                                "cat": {"chi_bao": "sma", "n": 21}}}, sp["vao"])
        self.assertEqual(NP.kiem_khai_bao(sp), [])

    def test_ma_cung_trong_so_tu_choi(self):
        # sma14 vs smma21: trong so khac -> dich duoc
        self.assertEqual(_doc("f[1]<=s[1] && f[0]>s[0]", pp="MODE_SMMA")
                         ["so_vao_lenh_co_co_che"], 1)
        # sma14 vs smma14: cung w = 1/14 -> hieu khong phu thuoc gia tick -> tu choi
        vb = (DAU % ("PRICE_CLOSE", "MODE_SMMA", "", "f[1]<=s[1] && f[0]>s[0]")).replace(
            "hs = iMA(_Symbol,PERIOD_CURRENT,21", "hs = iMA(_Symbol,PERIOD_CURRENT,14")
        d2 = DM.doc_chien_luoc(vb, nguon="t.mq5")
        self.assertEqual(d2["so_vao_lenh_co_co_che"], 0)
        self.assertTrue(any("khong quy ve" in x for x in d2["chua_dien_dat_duoc"]))

    def test_gia_song_tren_ma_song(self):
        than = DAU.replace(
            "void OnTick(){", "MqlTick tk;\nvoid OnTick(){\n   SymbolInfoTick(_Symbol,tk);")
        d = DM.doc_chien_luoc(than % ("PRICE_CLOSE", "MODE_SMA", "", "tk.ask>s[0]"),
                              nguon="t.mq5")
        sp = d["co_che"][0]
        self.assertEqual(sp["trong_bar"]["huong"], ">")
        self.assertIn({"trai": {"chi_bao": "gia", "cot": "close"}, "phep": ">",
                       "phai": {"chi_bao": "muc_song", "cua": {"chi_bao": "sma", "n": 21},
                                "cat": {"chi_bao": "gia", "cot": "close"}}}, sp["vao"])


class TestMoPhongVetCan(unittest.TestCase):
    def test_khop_trong_bar_bang_duyet_gia(self):
        """Vet can: bar j kich hoat khi CO gia p trong [low_j, high_j] (va open)
        lam rsi_song(p) < 30 voi rsi bar j-1 >= 30. RSI tang theo p nen chi can
        thu p = low_j (va p = open_j cho gia khop)."""
        df = _df(1500, seed=11, buoc=0.004)
        sp = _doc(RSI_CAT)["co_che"][0]
        cho, muc, huong = NP.sinh_trong_bar(sp, df)
        kq = MP.chay_dung_trong_bar(df, cho, muc, huong, 1, 1, CP.MoHinhChiPhi(ma="TEST"))
        rsi = M.rsi(df["close"], 21).to_numpy()
        o, lo = df["open"].to_numpy(), df["low"].to_numpy()
        vao_vc, vao_mp = [], []
        for j in range(60, len(df)):
            if cho[j - 1] and np.isfinite(muc[j - 1]) and \
                    (o[j] < muc[j - 1] or lo[j] < muc[j - 1]):
                vao_mp.append(j)
            if rsi[j - 1] >= 30 and \
                    M.rsi(_noi(df, j - 1, lo[j])["close"], 21).iloc[-1] < 30:
                vao_vc.append(j)
        self.assertGreater(len(vao_vc), 5)
        self.assertEqual(vao_mp, vao_vc)
        # gia khop = P* (khong gap) hoac open (gap qua muc)
        j = vao_mp[0]
        self.assertEqual(kq.vi_the[j - 1], 0)
        P = o[j + 1] / np.exp(kq.loi_tho[j])
        self.assertAlmostEqual(P, o[j] if o[j] < muc[j - 1] else muc[j - 1], places=10)
        rp = M.rsi(_noi(df, j - 1, P)["close"], 21).iloc[-1]
        self.assertLessEqual(rp, 30 + 1e-6)


if __name__ == "__main__":
    unittest.main()
