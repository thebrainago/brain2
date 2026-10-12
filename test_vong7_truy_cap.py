# -*- coding: utf-8 -*-
"""Vong 7: mang handle + ham boc theo chi so `Val(i,b,s)`, loc ngay bang switch,
ham gia mot dong `Price(k)`, VA long ngoac trong ham bool, `dir > 0 ? Buy : Sell`."""
import unittest

from nhan import doc_ma as DM
from nhan import khung_ea_mql as KEA

MAU = r'''
#include <Trade/Trade.mqh>
CTrade trade;
input int In0_Period = 9;
input int In1_Period = 21;
input bool InpMon = true; input bool InpTue = true; input bool InpWed = true;
input bool InpThu = true; input bool InpFri = true; input bool InpSat = false; input bool InpSun = %(sun)s;
input int InpSLPoints = 250;
int gHandle[2];
int OnInit()
{
   gHandle[0] = iMA(_Symbol, PERIOD_M15, In0_Period, 0, MODE_EMA, PRICE_CLOSE);
   gHandle[1] = iMA(_Symbol, PERIOD_M15, In1_Period, 0, MODE_EMA, PRICE_CLOSE);
   return INIT_SUCCEEDED;
}
void OnDeinit(const int r){ for(int i=0;i<2;i++) if(gHandle[i]!=INVALID_HANDLE) IndicatorRelease(gHandle[i]); }
double Val(int idx, int buffer, int shift)
{
   double b[];
   ArraySetAsSeries(b, true);
   if(CopyBuffer(gHandle[idx], buffer, shift, 1, b) <= 0) return(EMPTY_VALUE);
   return(b[0]);
}
double Price(int shift) { return iClose(_Symbol, PERIOD_M15, shift); }
bool BuySignal()  { return( (Val(0, 0, 2) <= Val(1, 0, 2) && Val(0, 0, 1) > Val(1, 0, 1)) && (Val(1, 0, 1) < Price(1)) ); }
bool SellSignal() { return( (Val(0, 0, 2) >= Val(1, 0, 2) && Val(0, 0, 1) < Val(1, 0, 1)) && (Val(1, 0, 1) > Price(1)) ); }
bool DayFilter()
{
   MqlDateTime t; TimeToStruct(TimeCurrent(), t);
   switch(t.day_of_week){
      case 1: return(InpMon); case 2: return(InpTue); case 3: return(InpWed);
      case 4: return(InpThu); case 5: return(InpFri); case 6: return(InpSat);
      default: return(InpSun);
   }
}
void OpenTrade(int dir)
{
   double price = (dir > 0) ? SymbolInfoDouble(_Symbol, SYMBOL_ASK)
                            : SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double sl = (dir > 0) ? price - InpSLPoints*_Point : price + InpSLPoints*_Point;
   bool ok = (dir > 0) ? trade.Buy(0.1, _Symbol, 0, sl, 0)
                       : trade.Sell(0.1, _Symbol, 0, sl, 0);
}
void OnTick()
{
   static datetime last = 0;
   datetime bt = iTime(_Symbol, PERIOD_M15, 0);
   if(bt == last) return;
   last = bt;
   if(!DayFilter()) return;
   if(BuySignal())  { OpenTrade(1);  return; }
   if(SellSignal()) { OpenTrade(-1); return; }
}
'''


def _doc(sun="false"):
    return DM.doc_chien_luoc(MAU % {"sun": sun}, nguon="mau_val.mq5")


class Vong7(unittest.TestCase):
    def test_mang_handle_thanh_bien_don(self):
        vb, ghi = KEA.mang_handle(MAU % {"sun": "false"})
        self.assertIn("gHandle__0 = iMA(", vb)
        self.assertIn("Val(gHandle__1, 0, 2)", vb)
        self.assertIn("CopyBuffer(idx, buffer", vb)
        self.assertTrue(ghi)

    def test_mang_handle_chi_so_khong_ro_khong_doi(self):
        vb0 = (MAU % {"sun": "false"}).replace("void OnTick()\n{",
                                              "void OnTick()\n{\n   int j=1; double x = gHandle[j];")
        vb, ghi = KEA.mang_handle(vb0)
        self.assertEqual(vb, vb0)
        self.assertEqual(ghi, [])

    def test_doc_hai_chieu_dung_huong_va_sl(self):
        r = _doc()
        cc = r["co_che"]
        self.assertEqual(r["so_vao_lenh_co_co_che"], 2)
        mua = [c for c in cc if c["chieu"] == 1]
        ban = [c for c in cc if c["chieu"] == -1]
        self.assertEqual(len(mua), 1)
        self.assertEqual(len(ban), 1)
        # mua: ema9 cat len ema21 (khong lan nhanh ban vao - truoc vong 7 HOAC tron hai cho goi)
        txt = str(mua[0]["vao"])
        self.assertIn("'phep': '>'", txt)
        self.assertEqual(mua[0]["sltp"]["sl_diem"], 250.0)
        self.assertEqual(mua[0]["sltp"]["ref_sl"], "ASK")
        self.assertEqual(ban[0]["sltp"]["ref_sl"], "BID")
        self.assertEqual(mua[0].get("khung_ea"), "M15")

    def test_loc_ngay_switch(self):
        r = _doc("false")
        thu = [v for v in r["co_che"][0]["vao"] if v["trai"].get("chi_bao") == "ngay_trong_tuan"]
        self.assertEqual(sorted(v["phai"]["hang"] for v in thu), [0.0, 6.0])
        r2 = _doc("true")
        thu2 = [v for v in r2["co_che"][0]["vao"] if v["trai"].get("chi_bao") == "ngay_trong_tuan"]
        self.assertEqual([v["phai"]["hang"] for v in thu2], [6.0])

    def test_ternary_tham_so_khong_giai_thi_tu_choi(self):
        # `dir` khong phai so sanh hang ma la bien ngoai -> khong duoc lot thanh HOAC hai chieu
        vb = (MAU % {"sun": "false"}).replace("(dir > 0) ? trade.Buy", "(dir > gX) ? trade.Buy")
        vb = vb.replace("CTrade trade;", "CTrade trade; int gX = 0;")
        r = DM.doc_chien_luoc(vb, nguon="mau_val2.mq5")
        for c in r.get("co_che", []):
            self.assertNotIn("_hoac", c)


if __name__ == "__main__":
    unittest.main()
