# -*- coding: utf-8 -*-
"""GOI HAM (lenh vao trong ham phu, dieu kien o cho goi) - them 11/10/2026.

`nhan/goi_ham_mql.py` nang lenh vao len cho goi CHI khi do thi goi nho va giai duoc
tron ven. Kiem: (1) ban ham phu doc RA DUNG dieu kien nhu ban viet thang trong
OnTick; (2) tu choi CO LY DO moi dang khong chung minh duoc (nhieu cho goi, else,
vong lap, OnChartEvent, phuong thuc lop, dieu kien o hai tang, bieu thuc ghep...);
(3) ham hoi vi the cua tac gia = quan tri; (4) `if(A or B) return;` tach dung.
"""
import unittest

import numpy as np
import pandas as pd

from nhan import doc_ma as DM
from nhan import goi_ham_mql as GH
from nhan import ngu_phap as NP

DAU = """#include <Trade/Trade.mqh>
input int InpRSI = 14;
input double InpLevel = 30;
input double Lots = 0.1;
CTrade trade;
MqlTick tk;
int hRsi;
double rsi[];
int OnInit(){ hRsi = iRSI(_Symbol,_Period,InpRSI,PRICE_CLOSE); ArraySetAsSeries(rsi,true); return(INIT_SUCCEEDED); }
"""
INLINE = DAU + """
void OnTick()
{
   if(CopyBuffer(hRsi,0,0,3,rsi) != 3) return;
   if(PositionsTotal() > 0) return;
   if(rsi[1] < InpLevel)
      trade.Buy(Lots,_Symbol);
}
"""
HAS_POS = """
bool HasPos()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
      if(PositionGetSymbol(i) == _Symbol) return(true);
   return(false);
}
"""
OPEN_BUY = """
void OpenBuy()
{
   if(!SymbolInfoTick(_Symbol, tk)) return;
   trade.Buy(Lots,_Symbol);
}
"""
HELPER = DAU + HAS_POS + OPEN_BUY + """
void OnTick()
{
   if(CopyBuffer(hRsi,0,0,3,rsi) != 3) return;
   if(HasPos()) return;
   if(rsi[1] < InpLevel)
      OpenBuy();
}
"""


def _doc(vb):
    return DM.doc_chien_luoc(vb, nguon="t")


def _ly_do(vb):
    d = _doc(vb)
    return d, " | ".join(d["chua_dien_dat_duoc"])


def _h1(n=1500, seed=5):
    r = np.random.default_rng(seed)
    p = 1.1 + np.cumsum(r.normal(0, 0.0007, n))
    idx = pd.date_range("2024-01-01", periods=n, freq="h")
    return pd.DataFrame({"open": p, "high": p + 4e-4, "low": p - 4e-4, "close": p,
                         "tick_volume": 100}, index=idx)


class DichDung(unittest.TestCase):
    def test_ham_phu_ra_dung_nhu_viet_thang(self):
        a, b = _doc(INLINE), _doc(HELPER)
        self.assertEqual(a["so_vao_lenh_co_co_che"], 1)
        self.assertEqual(b["so_vao_lenh_co_co_che"], 1)
        self.assertEqual([c["vao"] for c in a["co_che"]], [c["vao"] for c in b["co_che"]])
        self.assertEqual(b["co_che"][0]["chieu"], 1)
        self.assertIn("HasPos()", b["co_che"][0]["bo_qua_quan_tri"])

    def test_hai_tang_dieu_kien_o_tang_giua(self):
        vb = DAU + HAS_POS + OPEN_BUY + """
void CheckSignal()
{
   if(rsi[1] < InpLevel)
      OpenBuy();
}
void OnTick()
{
   if(CopyBuffer(hRsi,0,0,3,rsi) != 3) return;
   if(!HasPos())
      CheckSignal();
}
"""
        d = _doc(vb)
        self.assertEqual(d["so_vao_lenh_co_co_che"], 1, d["chua_dien_dat_duoc"])
        self.assertEqual(d["co_che"][0]["vao"], _doc(INLINE)["co_che"][0]["vao"])

    def test_dieu_kien_chi_o_thoat_som_cua_ham_phu(self):
        vb = DAU + """
ulong DoBuy()
{
   if(CopyBuffer(hRsi,0,0,3,rsi) != 3) return(0);
   if(rsi[1] >= InpLevel) return(0);
   if(!trade.Buy(Lots,_Symbol)) return(0);
   return(trade.ResultOrder());
}
void OnTick()
{
   if(PositionsTotal() > 0) return;
   DoBuy();
}
"""
        d = _doc(vb)
        self.assertEqual(d["so_vao_lenh_co_co_che"], 1, d["chua_dien_dat_duoc"])
        self.assertEqual(d["co_che"][0]["vao"], _doc(INLINE)["co_che"][0]["vao"])

    def test_co_che_qua_kiem_khong_nhin_truoc(self):
        df = _h1()
        for c in _doc(HELPER)["co_che"]:
            self.assertEqual(NP.kiem_khai_bao(c), [])
            ok, ly = NP.kiem_khong_nhin_truoc(c, df)
            self.assertTrue(ok, ly)

    def test_thoat_som_hoac_tach_dung(self):
        # `if(A or B) return;` == hai thoat som: ve vi the bo qua, ve RSI giu
        vb = DAU + HAS_POS + """
void OnTick()
{
   if(CopyBuffer(hRsi,0,0,3,rsi) != 3) return;
   if(rsi[1] >= InpLevel || HasPos()) return;
   trade.Buy(Lots,_Symbol);
}
"""
        d = _doc(vb)
        self.assertEqual(d["so_vao_lenh_co_co_che"], 1, d["chua_dien_dat_duoc"])
        self.assertEqual(d["co_che"][0]["vao"], _doc(INLINE)["co_che"][0]["vao"])


class TuChoi(unittest.TestCase):
    def _tu_choi(self, vb, mau):
        d, ly = _ly_do(vb)
        self.assertEqual(d["so_vao_lenh_co_co_che"], 0, d["co_che"])
        return mau, ly

    def test_goi_tu_hai_cho(self):
        self.assertIn(*self._tu_choi(DAU + OPEN_BUY + """
void OnTick()
{
   if(CopyBuffer(hRsi,0,0,3,rsi) != 3) return;
   if(rsi[1] < InpLevel) OpenBuy();
   if(rsi[2] < 20) OpenBuy();
}
""", "goi tu 2 cho"))

    def test_nhanh_else(self):
        self.assertIn(*self._tu_choi(DAU + OPEN_BUY + """
void OnTick()
{
   if(CopyBuffer(hRsi,0,0,3,rsi) != 3) return;
   if(rsi[1] > 70) Print("x");
   else OpenBuy();
}
""", "else"))

    def test_trong_vong_lap(self):
        self.assertIn(*self._tu_choi(DAU + OPEN_BUY + """
void OnTick()
{
   for(int i = 0; i < 3; i++)
   {
      if(rsi[1] < InpLevel) OpenBuy();
   }
}
""", "khoi for"))

    def test_chi_tu_onchartevent(self):
        self.assertIn(*self._tu_choi(DAU + OPEN_BUY + """
void OnChartEvent(const int id, const long &l, const double &d, const string &s)
{
   if(id == CHARTEVENT_OBJECT_CLICK) OpenBuy();
}
""", "khong toi OnTick"))

    def test_phuong_thuc_lop(self):
        self.assertIn(*self._tu_choi(DAU + """
class CBot
{
public:
   void Open() { trade.Buy(Lots,_Symbol); }
};
CBot bot;
void OnTick()
{
   if(rsi[1] < InpLevel) bot.Open();
}
""", "lop/struct"))

    def test_dieu_kien_o_hai_tang(self):
        self.assertIn(*self._tu_choi(DAU + """
void OpenBuy()
{
   if(rsi[2] > 50) return;
   trade.Buy(Lots,_Symbol);
}
void OnTick()
{
   if(rsi[1] < InpLevel) OpenBuy();
}
""", "HAI tang"))

    def test_goi_trong_dieu_kien_ghep(self):
        self.assertIn(*self._tu_choi(DAU + """
bool OpenBuy() { bool r = trade.Buy(Lots,_Symbol); return r; }
void OnTick()
{
   if(rsi[1] < InpLevel && OpenBuy()) Print("ok");
}
""", "loi goi OpenBuy nam trong"))

    def test_toan_tu_ba_ngoi(self):
        self.assertIn(*self._tu_choi(DAU + """
bool OpenBuy() { bool r = trade.Buy(Lots,_Symbol); return r; }
void OnTick()
{
   bool x = rsi[1] < InpLevel ? OpenBuy() : false;
}
""", "bieu thuc phuc tap"))

    def test_overload(self):
        self.assertIn(*self._tu_choi(DAU + """
void OpenBuy() { trade.Buy(Lots,_Symbol); }
void OpenBuy(double l) { Print(l); }
void OnTick()
{
   if(rsi[1] < InpLevel) OpenBuy();
}
""", "overload"))

    def test_de_quy(self):
        self.assertIn(*self._tu_choi(DAU + """
void OpenBuy(int k)
{
   if(k > 0) OpenBuy(k - 1);
   trade.Buy(Lots,_Symbol);
}
void OnTick()
{
   if(rsi[1] < InpLevel) OpenBuy(2);
}
""", "goi ham"))

    def test_khong_dieu_kien_vao(self):
        self.assertIn(*self._tu_choi(DAU + OPEN_BUY + """
void OnTick()
{
   if(PositionsTotal() > 0) return;
   OpenBuy();
}
""", "khong co dieu kien vao"))


class ThanHam(unittest.TestCase):
    def test_mat_na_giu_do_dai_va_bo_chuoi(self):
        vb = 'Print("{ OpenBuy(");  /* } */ x = 1;'
        mn = GH.mat_na(vb)
        self.assertEqual(len(mn), len(vb))
        self.assertNotIn("{", mn)
        self.assertNotIn("OpenBuy", mn)

    def test_ham_tu_do_bat_kieu_tra_ve_la(self):
        vb = "ulong Foo(int a)\n{\n return 1;\n}\nENUM_ORDER_TYPE Bar()\n{\n return 0;\n}\n" \
             "class C { void M() { } };\n"
        b = GH.ham_tu_do(GH.mat_na(vb))
        self.assertEqual(sorted(b), ["Bar", "Foo"])

    def test_ham_hoi_vi_the_khong_nhan_ham_doc_gia(self):
        vb = HAS_POS + """
bool Up()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--) {}
   return(iClose(_Symbol,_Period,1) > iOpen(_Symbol,_Period,1));
}
"""
        self.assertEqual(DM._ham_hoi_vi_the(vb), {"HasPos"})


if __name__ == "__main__":
    unittest.main()
