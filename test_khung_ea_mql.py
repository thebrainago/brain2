# -*- coding: utf-8 -*-
"""KHUNG EA CO DINH + .set + ham boc buffer + het gio theo bar + vong thu M5 (them 11/10/2026).

Kiem: (1) `.set` ap dung input (khung so MT5 -> PERIOD_*), (2) khung co dinh chi nhan khi MOI doi
so khung cung mot PERIOD_X va khong dung khung bieu do o dau ca, (3) ham boc doc mot buffer ->
mang, tu choi dang khac, (4) gio cua iTime(..,1) = luc mo bar i, (5) het gio N bar, (6) EA mau
dang RSI_Exhaustion doc tron (vao + SL/TP ATR + het gio + khung M5), (7) vong thu: nhan khung CSV,
co che khung M5 KHONG chay tren H1, chon .set, (8) mo_phong dong o tick dau bar j+N.
"""
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from nhan import doc_ma as DM
from nhan import khung_ea_mql as K
from nhan import mo_phong as MP
from nhan import chi_phi as CP
import vong_thu_nghiem as V

EA = r'''
#include <Trade/Trade.mqh>
CTrade trade;
input ENUM_TIMEFRAMES InpTimeframe = PERIOD_H1;
input double InpLot = 1.0;
input ulong InpMagic = 1;
const int InpRSIPeriod = 14;
const double InpLevel = 65.0;
const int InpStartHour = 14;
const int InpEndHour = 18;
const int InpATRPeriod = 14;
const double InpStopATR = 4.0;
const double InpTakeATR = 4.0;
const int InpMaxBars = 96;
int g_rsi = INVALID_HANDLE;
int g_atr = INVALID_HANDLE;
datetime g_last = 0;
double ReadBufferValue(const int handle,const int buffer,const int shift)
{
   if(handle==INVALID_HANDLE)
      return EMPTY_VALUE;
   double values[];
   ArraySetAsSeries(values,true);
   if(CopyBuffer(handle,buffer,shift,1,values)!=1)
      return EMPTY_VALUE;
   return values[0];
}
double GetRSI(const int shift)
{
   return ReadBufferValue(g_rsi,0,shift);
}
double GetATR(const int shift)
{
   return ReadBufferValue(g_atr,0,shift);
}
bool HasPos()
{
   return PositionSelect(_Symbol);
}
bool IsOurPosition()
{
   if(!PositionSelect(_Symbol))
      return false;
   return ((ulong)PositionGetInteger(POSITION_MAGIC)==InpMagic);
}
int BarsSinceEntry()
{
   if(!IsOurPosition())
      return 0;
   datetime positionTime=(datetime)PositionGetInteger(POSITION_TIME);
   int shift=iBarShift(_Symbol,InpTimeframe,positionTime,false);
   if(shift<0)
      return 0;
   return shift;
}
bool OpenSell(const datetime t,const double atr)
{
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol,tick))
      return false;
   double entry=tick.bid;
   double sl=entry+InpStopATR*atr;
   double tp=entry-InpTakeATR*atr;
   int digits=(int)SymbolInfoInteger(_Symbol,SYMBOL_DIGITS);
   sl=NormalizeDouble(sl,digits);
   tp=NormalizeDouble(tp,digits);
   bool ok=trade.Sell(InpLot,_Symbol,0.0,sl,tp,"x");
   return ok;
}
void EvaluateEntry()
{
   if(HasPos())
      return;
   datetime signalTime=iTime(_Symbol,InpTimeframe,1);
   if(signalTime==0)
      return;
   MqlDateTime d;
   TimeToStruct(signalTime,d);
   if(d.hour<InpStartHour || d.hour>=InpEndHour)
      return;
   double rsiNow =GetRSI(1);
   double rsiPrev=GetRSI(2);
   if(rsiNow==EMPTY_VALUE || rsiPrev==EMPTY_VALUE)
      return;
   if(!(rsiPrev<InpLevel && rsiNow>=InpLevel))
      return;
   double atr=GetATR(1);
   if(atr==EMPTY_VALUE || atr<=0.0)
      return;
   OpenSell(signalTime,atr);
}
void ManageTimeout()
{
   if(!IsOurPosition())
      return;
   if(BarsSinceEntry()<InpMaxBars)
      return;
   trade.PositionClose(_Symbol);
}
int OnInit()
{
   if(InpTimeframe==PERIOD_CURRENT)
   {
      Print("PERIOD_CURRENT is not allowed");
      return INIT_PARAMETERS_INCORRECT;
   }
   g_rsi=iRSI(_Symbol,InpTimeframe,InpRSIPeriod,PRICE_CLOSE);
   g_atr=iATR(_Symbol,InpTimeframe,InpATRPeriod);
   return INIT_SUCCEEDED;
}
void OnTick()
{
   datetime cur=iTime(_Symbol,InpTimeframe,0);
   if(cur==0)
      return;
   if(cur!=g_last)
   {
      g_last=cur;
      ManageTimeout();
      if(!HasPos())
         EvaluateEntry();
   }
}
'''


class SetVaKhung(unittest.TestCase):
    def test_set_khung_so_thanh_period(self):
        vb, g = K.ap_set(EA, K.doc_set("InpTimeframe=5\nInpLot=0.5||0.1||0.1||1||N\n;x\nKhac=3"))
        self.assertIn("input ENUM_TIMEFRAMES InpTimeframe = PERIOD_M5;", vb)
        self.assertIn("input double InpLot = 0.5;", vb)
        self.assertEqual(g["khong_co"], ["Khac"])
        self.assertEqual(g["ap"]["InpTimeframe"], ("PERIOD_H1", "PERIOD_M5"))

    def test_set_enum_khac_khong_ap(self):
        vb = "input ENUM_MA_METHOD M = MODE_SMA;\n"
        vb2, g = K.ap_set(vb, {"M": "1"})
        self.assertEqual(vb2, vb)
        self.assertIn("M", g["bo_qua"])

    def test_set_gia_tri_bang_nhau_khong_ghi(self):
        _, g = K.ap_set("input double L = 1.00;\n", {"L": "1.0"})
        self.assertEqual(g["ap"], {})

    def test_khung_co_dinh_viet_lai(self):
        k, vb, _ = K.khung_co_dinh(EA)
        self.assertEqual(k, "H1")
        self.assertIn("iRSI(_Symbol,_Period,InpRSIPeriod,PRICE_CLOSE)", vb)
        self.assertIn("iBarShift(_Symbol,_Period,positionTime,false)", vb)
        self.assertIn("iTime(_Symbol,_Period,1)", vb)
        self.assertNotIn("InpTimeframe,", vb)
        # chuoi "PERIOD_CURRENT" trong Print va phep so sanh OnInit khong lam hong
        self.assertIn('InpTimeframe==PERIOD_CURRENT', vb)

    def test_khung_tron_khong_nhan(self):
        vb = EA.replace("iTime(_Symbol,InpTimeframe,0)", "iTime(_Symbol,PERIOD_CURRENT,0)")
        k, vb2, ly = K.khung_co_dinh(vb)
        self.assertIsNone(k)
        self.assertEqual(vb2, vb)
        self.assertIn("tron", ly)

    def test_hai_khung_co_dinh_khong_nhan(self):
        vb = EA.replace("iATR(_Symbol,InpTimeframe,", "iATR(_Symbol,PERIOD_D1,")
        self.assertIsNone(K.khung_co_dinh(vb)[0])

    def test_khung_bieu_do_ngoai_doi_so_khong_nhan(self):
        vb = EA.replace("int OnInit()\n{", "int OnInit()\n{\n   int p=PeriodSeconds();")
        self.assertIsNone(K.khung_co_dinh(vb)[0])

    def test_khung_bien_khong_giai_duoc(self):
        vb = EA.replace("iRSI(_Symbol,InpTimeframe,", "iRSI(_Symbol,g_tf,")
        self.assertIsNone(K.khung_co_dinh(vb)[0])


class BocBuffer(unittest.TestCase):
    def test_noi_ham_boc(self):
        vb, ghi = K.noi_ham_boc_buffer(DM._chuan_hoa(EA))
        self.assertIn("double rsiNow =__boc_g_rsi_0[1];", vb)
        self.assertIn("double rsiPrev=__boc_g_rsi_0[2];", vb)
        self.assertIn("CopyBuffer(g_rsi,0,0,3,__boc_g_rsi_0);", vb)
        self.assertIn("CopyBuffer(g_atr,0,0,2,__boc_g_atr_0);", vb)
        self.assertEqual(len(ghi), 2)

    def test_tu_choi_count_khac_1(self):
        vb = EA.replace("CopyBuffer(handle,buffer,shift,1,values)",
                        "CopyBuffer(handle,buffer,shift,2,values)")
        self.assertEqual(K.noi_ham_boc_buffer(vb)[1], [])

    def test_tu_choi_tham_chieu(self):
        vb = EA.replace("const int shift)\n{\n   if(handle", "int &shift)\n{\n   if(handle")
        self.assertEqual(K.noi_ham_boc_buffer(vb)[1], [])

    def test_tu_choi_tra_phan_tu_khac(self):
        vb = EA.replace("   return values[0];\n}", "   return values[0]+values[1];\n}")
        self.assertEqual(K.noi_ham_boc_buffer(vb)[1], [])


class HetGio(unittest.TestCase):
    def test_het_gio_96(self):
        # het_gio_bar doc van ban DA viet lai khung (iBarShift tren _Period = khung chay)
        self.assertEqual(K.het_gio_bar(EA, {"InpMaxBars": "96"}), (None, []))
        n, ghi = K.het_gio_bar(K.khung_co_dinh(EA)[1], {"InpMaxBars": "96"})
        self.assertEqual(n, 96)
        self.assertTrue(ghi)

    def test_het_gio_goi_ngoai_ontick_khong_nhan(self):
        vb = EA.replace("      ManageTimeout();\n", "").replace(
            "int OnInit()\n{", "void OnTimer()\n{\n   ManageTimeout();\n}\nint OnInit()\n{")
        n, ghi = K.het_gio_bar(K.khung_co_dinh(vb)[1], {"InpMaxBars": "96"})
        self.assertIsNone(n)
        self.assertTrue(any("OnTick" in x for x in ghi))

    def test_het_gio_thoat_som_la_khong_nhan(self):
        vb = EA.replace("   if(BarsSinceEntry()<InpMaxBars)",
                        "   if(Close[1]>1.0)\n      return;\n   if(BarsSinceEntry()<InpMaxBars)")
        n, _ = K.het_gio_bar(K.khung_co_dinh(vb)[1], {"InpMaxBars": "96"})
        self.assertIsNone(n)


class DocTron(unittest.TestCase):
    def test_ea_doc_voi_set_m5(self):
        r = DM.doc_chien_luoc(EA, nguon="t.mq5", set_ea="InpTimeframe=5\n")
        self.assertEqual(r["khung_ea"], "M5")
        (sp,) = r["co_che"]
        self.assertEqual(sp["khung_ea"], "M5")
        self.assertEqual(sp["chieu"], -1)
        vao = sp["vao"]
        # gio cua iTime(..,1) = luc MO bar i -> KHONG mang "luc dong"
        self.assertIn({"trai": {"chi_bao": "gio"}, "phep": ">=", "phai": {"hang": 14.0}}, vao)
        self.assertIn({"trai": {"chi_bao": "gio"}, "phep": "<", "phai": {"hang": 18.0}}, vao)
        self.assertIn({"trai": {"chi_bao": "rsi", "n": 14}, "phep": ">=",
                       "phai": {"hang": 65.0}}, vao)
        self.assertIn({"trai": {"chi_bao": "tre", "cua": {"chi_bao": "rsi", "n": 14}, "n": 1},
                       "phep": "<", "phai": {"hang": 65.0}}, vao)
        k = sp["sltp"]
        self.assertEqual(k["sl_kc"]["he_so"], [4.0])
        self.assertEqual(k["tp_kc"]["he_so"], [4.0])
        self.assertEqual(k["sl_kc"]["toan_hang"][0]["chi_bao"], "atr")
        self.assertEqual((k["ref_sl"], k["ref_tp"]), ("BID", "BID"))
        self.assertEqual(k["het_bar"], 96)

    def test_khong_set_dung_mac_dinh(self):
        r = DM.doc_chien_luoc(EA, nguon="t.mq5")
        self.assertEqual(r["khung_ea"], "H1")

    def test_gio_itime0_van_luc_dong(self):
        vb = EA.replace("datetime signalTime=iTime(_Symbol,InpTimeframe,1);",
                        "datetime signalTime=iTime(_Symbol,InpTimeframe,0);")
        (sp,) = DM.doc_chien_luoc(vb, nguon="t.mq5")["co_che"]
        self.assertIn({"trai": {"chi_bao": "gio", "luc": "dong"}, "phep": ">=",
                       "phai": {"hang": 14.0}}, sp["vao"])

    def test_gio_itime2_khong_dich(self):
        vb = EA.replace("datetime signalTime=iTime(_Symbol,InpTimeframe,1);",
                        "datetime signalTime=iTime(_Symbol,InpTimeframe,2);")
        self.assertEqual(DM.doc_chien_luoc(vb, nguon="t.mq5")["co_che"], [])


def _gia(khung, n=300):
    idx = pd.date_range("2024-01-01", periods=n, freq=V._tan_so(khung))
    c = 1.1 + np.cumsum(np.random.default_rng(1).normal(0, 1e-4, n))
    return pd.DataFrame({"open": c, "high": c + 1e-4, "low": c - 1e-4, "close": c}, index=idx)


class VongThuKhung(unittest.TestCase):
    def test_khung_tu_du_lieu(self):
        for k in ("M5", "M15", "H1", "D1"):
            self.assertEqual(V.khung_tu_du_lieu(_gia(k)), k)
        self.assertIn("M5", V.BAR_NAM)
        self.assertEqual(V.BAR_NAM["M5"], 12 * V.BAR_NAM["H1"])

    def test_gia_lap_m5(self):
        df = V.du_lieu_gia_lap(500, 1, "M5")
        self.assertEqual(V.khung_tu_du_lieu(df), "M5")

    def test_co_che_m5_khong_chay_tren_h1(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "ea.mq5"
            p.write_text(EA)
            (Path(d) / "ea_x.set").write_text("InpTimeframe=5\n")
            ra = V.chay_mot_file(p, _gia("H1", 400), "H1", toi_uu_bat=False,
                                 cp=CP.MoHinhChiPhi(ma="EURUSD"))
            self.assertEqual(len(ra), 1)
            self.assertIn("M5 != du lieu H1", ra[0]["khong_hop_khung"])
            self.assertFalse(ra[0]["giu_lai"])
            ra = V.chay_mot_file(p, _gia("M5", 600), "M5", toi_uu_bat=False,
                                 cp=CP.MoHinhChiPhi(ma="EURUSD"))
            self.assertNotIn("khong_hop_khung", ra[0])
            self.assertEqual(ra[0]["khung_ea"], "M5")
            self.assertEqual(ra[0]["set"]["tep"], "ea_x.set")

    def test_chon_set(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "ea.mq5"
            p.write_text(EA)
            self.assertEqual(V.set_cua_ea(p), (None, ""))
            (Path(d) / "ea_a.set").write_text("InpTimeframe=5\n")
            self.assertEqual(V.set_cua_ea(p)[0].name, "ea_a.set")
            (Path(d) / "ea_b.set").write_text("InpTimeframe=15\n")
            t, ghi = V.set_cua_ea(p)
            self.assertIsNone(t)
            self.assertIn("2 file .set", ghi)
            (Path(d) / "NGUON.json").write_text(json.dumps([{"file": "ea.mq5", "set": ["ea_b.set"]}]))
            self.assertEqual(V.set_cua_ea(p)[0].name, "ea_b.set")

    def test_main_csv_sai_khung_bao_loi(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "g.csv"
            _gia("M5", 50).rename_axis("time").to_csv(f)
            self.assertEqual(V.main(["--csv", str(f), "--khung", "H1", "--mau", d]), 2)


class MoPhongHetGio(unittest.TestCase):
    def test_dong_o_tick_dau_bar_j_cong_n(self):
        n = 12
        idx = pd.date_range("2024-01-01", periods=n, freq="5min")
        df = pd.DataFrame({"open": 1.0, "high": 1.0001, "low": 0.9999, "close": 1.0}, index=idx)
        cho = np.zeros(n, dtype=bool)
        cho[1] = True
        c = {"chieu": -1, "cho": cho, "muc": None, "muc_lai": None, "phep_lai": None,
             "huong": None, "co": None, "loc": None, "sl": None, "tp": None, "keo": None,
             "giu": 1, "chan_boi": [], "dat": [], "ro": None, "sl_kc": None, "tp_kc": None,
             "sl_kc_min_spread": None, "rui_ro": None, "spread_max_diem": None, "mt5": True,
             "sl_diem": 500, "tp_diem": 500, "ref_sl": "BID", "ref_tp": "BID", "dong_mo": None,
             "het_bar": 4}
        nk = []
        MP.chay_he(df, [c], CP.MoHinhChiPhi(ma="TEST", spread_frac_chung=1e-5), diem=1e-5,
                   nhat_ky=nk)
        self.assertEqual(nk[0]["bar_vao"], 2)
        self.assertEqual(nk[0]["bar_ra"], 6)
        self.assertEqual(nk[0]["ly_do"], "het_gio")


if __name__ == "__main__":
    unittest.main()
