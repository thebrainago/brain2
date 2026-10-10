# -*- coding: utf-8 -*-
"""Lop doc MQL5 tren EA NGOAI (`mau_thu/mo_rong`, them 10/10/2026 khuya).

Moi test kiem NGHIA cua mot sua loi tong quat, tren doan ma nho viet tay theo
dung mau trong bo mo rong - va hai chieu: sua loi phai vua mo khoa ban dich
dung, vua TU CHOI cho khong dich duoc (handle bi che, giao cat trong bar...).
"""
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from nhan import doc_ma as DM
from nhan import ngu_phap as NP

LAB = Path(__file__).resolve().parent

DAU = """#property copyright "t"
#include <Trade\\Trade.mqh>
CTrade trade;
"""


def _doc(than: str) -> dict:
    return DM.doc_chien_luoc(DAU + than, nguon="t.mq5")


def _df(n=400, seed=5):
    rng = np.random.default_rng(seed)
    p = 1.1 + np.cumsum(rng.normal(0, 0.0007, n))
    idx = pd.date_range("2022-01-03", periods=n, freq="h")
    return pd.DataFrame({"open": p, "high": p + 0.0004, "low": p - 0.0004,
                         "close": p, "tick_volume": 100}, index=idx)


BB = """input int BB_Period = 20;
input int BB_Shift = %s;
input double BB_Dev = 2.0;
int h; double up[], lo[]; MqlTick tk;
int OnInit(){ h = iBands(_Symbol,PERIOD_CURRENT,BB_Period,BB_Shift,BB_Dev,PRICE_CLOSE); return 0; }
bool IsNewBar(){ static datetime p=0; datetime c=iTime(_Symbol,PERIOD_CURRENT,0);
   if(p!=c){p=c; return true;} return false; }
void OnTick(){
   if(!IsNewBar()) return;
   if(!SymbolInfoTick(_Symbol,tk)) return;
   CopyBuffer(h,UPPER_BAND,0,1,up);
   CopyBuffer(h,2,0,1,lo);
   if(tk.ask<=lo[0]) trade.PositionOpen(_Symbol,ORDER_TYPE_BUY,0.1,tk.ask,0,0);
}
"""


class TestChiBaoNhieuBuffer(unittest.TestCase):
    def test_bands_duoi_input_va_dich_la_tre(self):
        # Sua 11/10/2026: bands_shift = s -> buffer bar 0 = gia tri TINH TAI bar MQL5 s
        # (bar 1 = bar i) -> tre s-1, co dinh trong bar. Truoc day test nay khoa
        # `tre 1` cho s = 1 (lech MOT bar: bollinger(i-1) thay vi bollinger(i)).
        d = _doc(BB % "1")
        self.assertEqual(d["so_vao_lenh_co_co_che"], 1)
        v = d["co_che"][0]["vao"][0]
        self.assertEqual(v["trai"], {"chi_bao": "gia", "cot": "close"})
        self.assertEqual(v["phep"], "<=")
        self.assertEqual(v["phai"], {"chi_bao": "bollinger", "n": 20, "k": 2.0,
                                     "lay": "duoi", "ddof": 0})
        v2 = _doc(BB % "3")["co_che"][0]["vao"][0]
        self.assertEqual(v2["phai"]["chi_bao"], "tre")
        self.assertEqual(v2["phai"]["n"], 2)
        self.assertEqual(v2["phai"]["cua"]["lay"], "duoi")
        # buffer bar 1 (CopyBuffer start 1) voi shift 1 = tinh tai bar 2 = tre 1
        v3 = _doc((BB % "1").replace("CopyBuffer(h,2,0,1,lo)", "CopyBuffer(h,2,1,1,lo)")
                  )["co_che"][0]["vao"][0]
        self.assertEqual(v3["phai"]["chi_bao"], "tre")
        self.assertEqual(v3["phai"]["n"], 1)
        self.assertEqual(d["co_che"][0]["ho"], "quay_ve_trung_binh")
        self.assertEqual(NP.kiem_khai_bao(d["co_che"][0]), [])

    def test_bands_khong_dich(self):
        v = _doc(BB % "0")["co_che"][0]["vao"][0]
        self.assertEqual(v["phai"]["chi_bao"], "bollinger")

    def test_ddof0_la_do_lech_dan_so(self):
        df = _df()
        a = NP.toan_hang(df, {"chi_bao": "bollinger", "n": 20, "k": 2.0, "lay": "tren", "ddof": 0})
        b = NP.toan_hang(df, {"chi_bao": "bollinger", "n": 20, "k": 2.0, "lay": "tren"})
        x = df["close"].iloc[-20:]
        self.assertAlmostEqual(a.iloc[-1], x.mean() + 2 * x.std(ddof=0), places=12)
        self.assertAlmostEqual(b.iloc[-1], x.mean() + 2 * x.std(ddof=1), places=12)


class TestHamChiBao(unittest.TestCase):
    def test_gia_ap_dung_phuong_phap_khung(self):
        f = DM._tu_ham_mql5
        self.assertEqual(f("iRSI(_Symbol,PERIOD_CURRENT,14,PRICE_OPEN)"),
                         {"chi_bao": "rsi", "n": 14, "cot": "open"})
        self.assertEqual(f("iMA(_Symbol,_Period,8,0,MODE_SMMA,PRICE_CLOSE)"),
                         {"chi_bao": "smma", "n": 8})
        self.assertEqual(f("iMA(_Symbol,0,8,0,MODE_LWMA,PRICE_MEDIAN)"),
                         {"chi_bao": "wma", "n": 8, "cot": "hl2"})
        self.assertEqual(f("iATR(_Symbol,PERIOD_CURRENT,14)"),
                         {"chi_bao": "atr", "n": 14, "kieu": "sma"})
        self.assertEqual(f("iCCI(_Symbol,PERIOD_CURRENT,14,PRICE_TYPICAL)"),
                         {"chi_bao": "cci", "n": 14})
        self.assertEqual(f("iCCI(_Symbol,PERIOD_CURRENT,14,PRICE_CLOSE)"),
                         {"chi_bao": "cci", "n": 14, "cot": "close"})
        # khung co dinh khac khung bieu do / gia WEIGHTED / chu ky la bien -> khong dich
        self.assertIsNone(f("iMA(_Symbol,PERIOD_D1,8,0,MODE_SMA,PRICE_CLOSE)"))
        self.assertIsNone(f("iRSI(_Symbol,MA_Timeframe,14,PRICE_CLOSE)"))
        self.assertIsNone(f("iRSI(_Symbol,0,14,PRICE_WEIGHTED)"))
        self.assertIsNone(f("iRSI(_Symbol,0,RSI_Period,PRICE_CLOSE)"))
        self.assertEqual(f("iMA(NULL,0,50,2,MODE_SMA,PRICE_CLOSE)"),
                         {"chi_bao": "tre", "cua": {"chi_bao": "sma", "n": 50}, "n": 2})

    def test_so_hoc_hang(self):
        self.assertEqual(DM._so_hoc_hang("(100-70)"), 30.0)
        self.assertIsNone(DM._so_hoc_hang("100-RSI_Level"))
        self.assertIsNone(DM._so_hoc_hang("__import__('os')"))


RSI = """input int RSI_Period = 14;
input int RSI_Level = 70;
int h; double r[]; datetime openTimeBuy = 0;
int OnInit(){ %s = iRSI(_Symbol,PERIOD_CURRENT,RSI_Period,PRICE_CLOSE); ArraySetAsSeries(r,true); return 0; }
bool CountOpenPositions(int &cntBuy){ cntBuy=0;
   for(int i=PositionsTotal()-1;i>=0;i--){ if(PositionGetTicket(i)>0) cntBuy++; } return true; }
bool IsNewBar(){ static datetime p=0; datetime c=iTime(_Symbol,PERIOD_CURRENT,0);
   if(p!=c){p=c; return true;} return false; }
void OnTick(){
   if(!IsNewBar()) return;
   CopyBuffer(h,0,0,%s,r);
   int nb; if(!CountOpenPositions(nb)) return;
   if(nb<1 && %s && openTimeBuy!=iTime(_Symbol,PERIOD_CURRENT,0)){
      openTimeBuy=iTime(_Symbol,PERIOD_CURRENT,0);
      trade.PositionOpen(_Symbol,ORDER_TYPE_BUY,0.1,0,0,0);
   }
}
"""


class TestQuanTriVaTuChoi(unittest.TestCase):
    def test_bo_ve_quan_tri_giu_ve_tin_hieu_input_hang(self):
        d = _doc(RSI % ("h", "3", "r[2]>=(100-RSI_Level)"))
        self.assertEqual(d["so_vao_lenh_co_co_che"], 1)
        c = d["co_che"][0]
        self.assertEqual(c["vao"], [{"trai": {"chi_bao": "tre", "cua": {"chi_bao": "rsi", "n": 14},
                                              "n": 1}, "phep": ">=", "phai": {"hang": 30.0}}])
        self.assertIn("nb<1", c["bo_qua_quan_tri"])
        self.assertTrue(any("iTime" in x for x in c["bo_qua_quan_tri"]))

    def test_handle_bi_che_boi_bien_cuc_bo(self):
        d = _doc(RSI % ("int h", "3", "r[2]>=(100-RSI_Level)"))
        self.assertEqual(d["so_vao_lenh_co_co_che"], 0)

    def test_giao_cat_bar0_bar1_la_mau_thuan(self):
        d = _doc(RSI % ("h", "2", "r[1]>=(100-RSI_Level) && r[0]<(100-RSI_Level)"))
        self.assertEqual(d["so_vao_lenh_co_co_che"], 0)
        self.assertTrue(any("mau thuan" in x for x in d["chua_dien_dat_duoc"]))

    def test_so_voi_chinh_no(self):
        d = _doc(RSI % ("h", "2", "r[0]>r[1]"))
        self.assertEqual(d["so_vao_lenh_co_co_che"], 0)
        self.assertTrue(any("chinh no" in x for x in d["chua_dien_dat_duoc"]))

    def test_bien_dem_khong_phai_vi_the_khong_bo(self):
        # `nb` khong dem vi the (ham khong duyet PositionsTotal) -> KHONG duoc bo qua
        than = (RSI % ("h", "3", "r[2]>=(100-RSI_Level)")).replace(
            "for(int i=PositionsTotal()-1;i>=0;i--){ if(PositionGetTicket(i)>0) cntBuy++; }",
            "cntBuy++;")
        self.assertEqual(_doc(than)["so_vao_lenh_co_co_che"], 0)


CHUOI = """int h1, h2, h3;
int OnInit(){ h1=iMA(Symbol(),Period(),10,0,MODE_EMA,PRICE_CLOSE);
   h2=iMA(Symbol(),Period(),30,0,MODE_EMA,PRICE_CLOSE);
   h3=iMA(Symbol(),Period(),60,0,MODE_EMA,PRICE_CLOSE); return 0; }
void OnTick(){
   datetime cur = iTime(Symbol(),Period(),0);
   static datetime prev = cur;
   if(prev == cur) return;
   prev = cur;
   double a[], b[], c[];
   if(CopyBuffer(h1,0,0,3,a)<3) return;
   if(CopyBuffer(h2,0,0,3,b)<3) return;
   if(CopyBuffer(h3,0,0,3,c)<3) return;
   ArraySetAsSeries(a,true); ArraySetAsSeries(b,true); ArraySetAsSeries(c,true);
   ENUM_ORDER_TYPE t;
   if(b[1]>c[1] && a[2]<b[2] && a[1]>=b[1]) { t = ORDER_TYPE_BUY; }
   else if(%s) { t = ORDER_TYPE_SELL; }
   else return;
   trade.PositionOpen(Symbol(), t, 0.1, 0, 0, 0);
}
"""


class TestChuoiIfElse(unittest.TestCase):
    def test_hai_nhanh_loai_tru(self):
        d = _doc(CHUOI % "b[1]<c[1] && a[2]>b[2] && a[1]<=b[1]")
        self.assertEqual(d["so_vao_lenh"], 1)
        self.assertEqual(d["so_vao_lenh_co_co_che"], 1)
        self.assertEqual(sorted(c["chieu"] for c in d["co_che"]), [-1, 1])
        mua = next(c for c in d["co_che"] if c["chieu"] == 1)
        self.assertIn({"trai": {"chi_bao": "ema", "n": 30}, "phep": ">",
                       "phai": {"chi_bao": "ema", "n": 60}}, mua["vao"])
        self.assertEqual(mua["ho"], "xu_huong")

    def test_nhanh_hai_khong_loai_tru_thi_khong_dich(self):
        d = _doc(CHUOI % "b[2]<c[2] && a[1]<=b[1]")
        self.assertEqual(d["so_vao_lenh_co_co_che"], 0)
        self.assertTrue(any("loai tru" in x for x in d["chua_dien_dat_duoc"]))


class TestBoMoRong(unittest.TestCase):
    def test_do_moc_rong_va_mau_thu_khong_doi(self):
        import sys
        sys.path.insert(0, str(LAB / "mau_thu"))
        import do_moc as DMOC
        import do_moc_rong as DMR
        r = DMR.DMOC.do(DMR.tep_rong())
        self.assertEqual(r["file"], 15)
        self.assertEqual(r["vao_lenh"], 34)
        self.assertGreaterEqual(r["vao_co"], 5)
        g = DMOC.do()
        self.assertEqual((g["vao_co"], g["vao_lenh"]), (13, 22))


if __name__ == "__main__":
    unittest.main()
