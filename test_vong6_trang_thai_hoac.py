# -*- coding: utf-8 -*-
"""Vong 6 (12/10/2026): ham bool F() cua tac gia, loc trang thai tai khoan / nhip lenh, HOAC
(else-if phu dinh VA), loc thoat mau thuan voi guard, kiem ha tang MQL4."""
from nhan import doc_ma as DM
from nhan import ham_bool_mql as HB
from nhan import mql4_chuan as MQ4

DAU = """#include <Trade/Trade.mqh>
input int InpStart = 8;
input int InpEnd = 17;
input bool InpUseSession = true;
input int InpMaxTradesPerDay = 3;
input double InpMaxDailyLossPct = 2.0;
CTrade trade;
int h;
double r[];
int g_tradesToday = 0;
double g_dayStartBal = 0;
int OnInit(){ h = iRSI(_Symbol,_Period,14,PRICE_CLOSE); ArraySetAsSeries(r,true); return 0; }
"""

PHIEN = """
bool InSession()
{
   if(!InpUseSession) return true;
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   return (dt.hour >= InpStart && dt.hour < InpEnd);
}
"""


def _doc(vb, set_ea=None):
    return DM.doc_chien_luoc(vb, nguon="t", set_ea=set_ea)


def _co_gio(vao, phep, n):
    return any(d["trai"].get("chi_bao") == "gio" and d["phep"] == phep and
               d["phai"].get("hang") == n for d in vao)


def test_ham_phien_thanh_dieu_kien_gio():
    r = _doc(DAU + PHIEN + """
void OnTick()
{
   if(CopyBuffer(h,0,1,1,r)!=1) return;
   if(!InSession()) return;
   if(r[0] < 30) trade.Buy(0.1,_Symbol);
}
""")
    assert r["so_vao_lenh_co_co_che"] == 1, r["chua_dien_dat_duoc"]
    vao = r["co_che"][0]["vao"]
    assert _co_gio(vao, ">=", 8.0) and _co_gio(vao, "<", 17.0), vao


def test_ham_phien_tat_bang_input_khong_them_dieu_kien():
    r = _doc(DAU.replace("InpUseSession = true", "InpUseSession = false") + PHIEN + """
void OnTick()
{
   if(CopyBuffer(h,0,1,1,r)!=1) return;
   if(!InSession()) return;
   if(r[0] < 30) trade.Buy(0.1,_Symbol);
}
""")
    assert r["so_vao_lenh_co_co_che"] == 1
    assert not any(d["trai"].get("chi_bao") == "gio" for d in r["co_che"][0]["vao"])


def test_gio_gmt_khong_dich():
    r = _doc(DAU + PHIEN.replace("TimeCurrent()", "TimeGMT()") + """
void OnTick()
{
   if(CopyBuffer(h,0,1,1,r)!=1) return;
   if(!InSession()) return;
   if(r[0] < 30) trade.Buy(0.1,_Symbol);
}
""")
    # gio GMT lech gio may chu cua du lieu mot khoang khong biet -> khong doan
    assert r["so_vao_lenh_co_co_che"] == 0


def test_ham_bool_tin_hieu_va_phu_dinh():
    r = _doc(DAU + """
bool BuyOk() { return (r[0] < 30); }
void OnTick()
{
   if(CopyBuffer(h,0,1,1,r)!=1) return;
   if(BuyOk()) trade.Buy(0.1,_Symbol);
   if(!BuyOk()) trade.Sell(0.1,_Symbol);
}
""")
    assert r["so_vao_lenh_co_co_che"] == 2, r["chua_dien_dat_duoc"]
    ph = {c["chieu"]: c["vao"][0]["phep"] for c in r["co_che"]}
    assert ph == {1: "<", -1: ">="}


def test_ham_bool_hai_ve_phu_dinh_tu_choi():
    r = _doc(DAU + """
bool Ok()
{
   if(r[0] > 70) return false;
   return (r[0] > 20);
}
void OnTick()
{
   if(CopyBuffer(h,0,1,1,r)!=1) return;
   if(!Ok()) trade.Sell(0.1,_Symbol);
}
""")
    # !(not a and b) = a OR not b -> khong dien dat bang VA
    assert r["so_vao_lenh_co_co_che"] == 0


def test_phan_tich_than_ham():
    HB.dat_van_ban("bool F(){ if(x > 1) return false; return (y < 2); }", {})
    assert [(k, x) for k, _, x in HB.phan_tich("F")] == [("neg", "x > 1"), ("pos", "(y < 2)")]
    HB.dat_van_ban("bool G(){ for(int i=0;i<3;i++){} return true; }", {})
    assert HB.phan_tich("G") is None
    HB.dat_van_ban("bool K(){ if(a) return true; if(b) return true; return false; }", {})
    assert HB.phan_tich("K") is None                   # a OR b


def test_gioi_han_lenh_ngay_va_lo_ngay_la_quan_tri():
    r = _doc(DAU + """
void OnTick()
{
   if(CopyBuffer(h,0,1,1,r)!=1) return;
   if(g_tradesToday >= InpMaxTradesPerDay) return;
   if((AccountInfoDouble(ACCOUNT_BALANCE) - g_dayStartBal) / g_dayStartBal * 100 < -InpMaxDailyLossPct) return;
   if(r[0] < 30)
   {
      if(trade.Buy(0.1,_Symbol)) g_tradesToday++;
   }
}
void OnNewDay(){ g_tradesToday = 0; g_dayStartBal = AccountInfoDouble(ACCOUNT_BALANCE); }
""")
    assert r["so_vao_lenh_co_co_che"] == 1, r["chua_dien_dat_duoc"]
    qt = " ".join(r["co_che"][0]["bo_qua_quan_tri"])
    assert "g_tradesToday" in qt and "g_dayStartBal" in qt


def test_bien_dem_khong_gan_lenh_khong_phai_trang_thai():
    # `n++` dem nen tang (tin hieu) - KHONG gan voi lenh dat -> khong duoc bo qua
    r = _doc(DAU + """
int n = 0;
void OnTick()
{
   if(CopyBuffer(h,0,1,1,r)!=1) return;
   if(iClose(_Symbol,_Period,1) > iOpen(_Symbol,_Period,1)) n++; else n = 0;
   if(n < 3) return;
   if(r[0] < 30) trade.Buy(0.1,_Symbol);
}
""")
    assert r["so_vao_lenh_co_co_che"] == 0


def test_else_if_phu_dinh_va_thanh_hoac():
    r = _doc(DAU + """
void OnTick()
{
   if(CopyBuffer(h,0,1,2,r)!=2) return;
   double c = iClose(_Symbol,_Period,1);
   double o = iOpen(_Symbol,_Period,1);
   if(r[0] < 30 && c > o) trade.Buy(0.1,_Symbol);
   else if(r[0] < 40) trade.Sell(0.1,_Symbol);
}
""")
    ban = [c for c in r["co_che"] if c["chieu"] == -1]
    # B and not(a and b) = (B and not a) OR (B and not b): B=r<40, a=r<30 -> nhanh 1 = 30<=r<40
    assert len(ban) == 2, r["chua_dien_dat_duoc"]
    assert len({c["nhom_he"] for c in ban}) == 1
    phep = sorted(tuple(sorted(d["phep"] for d in c["vao"])) for c in ban)
    assert phep == [("<", "<="), ("<", ">=")], phep


def test_else_if_guard_quan_tri_khong_lam_hong_chung_minh():
    r = _doc(DAU + """
void OnTick()
{
   if(CopyBuffer(h,0,1,1,r)!=1) return;
   if(r[0] < 30) trade.Buy(0.1,_Symbol);
   else if(PositionsTotal() == 0 && r[0] > 70) trade.Sell(0.1,_Symbol);
}
""")
    assert r["so_vao_lenh_co_co_che"] == 2, r["chua_dien_dat_duoc"]


def test_loc_thoat_mau_thuan_guard_bo_qua_mql4():
    src = """
extern int MovingPeriod = 12;
void CheckForOpen()
{
   double ma;
   int res;
   if(Volume[0]>1) return;
   ma=iMA(NULL,0,MovingPeriod,0,MODE_SMA,PRICE_CLOSE,0);
   if(Open[1]>ma && Close[1]<ma)
     {
      res=OrderSend(Symbol(),OP_SELL,0.1,Bid,3,0,0,"",1,0,Red);
      return;
     }
   if(Open[1]<ma && Close[1]>ma)
     {
      res=OrderSend(Symbol(),OP_BUY,0.1,Ask,3,0,0,"",1,0,Blue);
      return;
     }
}
void OnTick()
{
   if(Bars<100 || IsTradeAllowed()==false) return;
   CheckForOpen();
}
"""
    r = DM.doc_chien_luoc(MQ4.chuan_hoa(src), nguon="t")
    assert r["so_vao_lenh_co_co_che"] == 2, r["chua_dien_dat_duoc"]
    mua = [c for c in r["co_che"] if c["chieu"] == 1][0]
    assert any("loai tru voi dieu kien vao" in x for x in mua["bo_qua_quan_tri"])


def test_loc_thoat_khong_mau_thuan_van_tu_choi():
    r = _doc(DAU + """
void OnTick()
{
   if(CopyBuffer(h,0,1,1,r)!=1) return;
   if(r[0] > 50 && iClose(_Symbol,_Period,1) > iOpen(_Symbol,_Period,1)) return;
   if(r[0] < 60) trade.Buy(0.1,_Symbol);
}
""")
    assert r["so_vao_lenh_co_co_che"] == 0
