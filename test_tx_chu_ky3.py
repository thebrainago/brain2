# -*- coding: utf-8 -*-
"""Vong 27 chu ky 3: tien xu ly chieu lenh qua hang cuc bo, else->if(!A), sua goi_ham `if(A and B) F();`."""
from nhan import tien_xu_ly_ea as TX
from nhan import doc_ma as DM

_DAU = """
#include <Trade/Trade.mqh>
CTrade trade;
input int InpFast = 10;
input int InpSlow = 30;
int hF, hS;
int OnInit(){ hF=iMA(_Symbol,_Period,InpFast,0,MODE_SMA,PRICE_CLOSE);
 hS=iMA(_Symbol,_Period,InpSlow,0,MODE_SMA,PRICE_CLOSE); return 0; }
"""
_TICK = """
void OnTick()
{
   if(PositionsTotal() > 0) return;
   double f[], s[];
   ArraySetAsSeries(f, true); ArraySetAsSeries(s, true);
   if(CopyBuffer(hF, 0, 1, 2, f) != 2) return;
   if(CopyBuffer(hS, 0, 1, 2, s) != 2) return;
   if(f[1] <= s[1] && f[0] > s[0])
      OpenPosition(ORDER_TYPE_BUY);
   if(f[1] >= s[1] && f[0] < s[0])
      OpenPosition(ORDER_TYPE_SELL);
}
"""


def _doc(vb):
    v2, log = TX.bien_doi(vb)
    return DM.doc_chien_luoc(v2, nguon="t"), log


def test_ba_ngoi_hang_khong_sinh_chieu_sai():
    mo = """
void OpenPosition(ENUM_ORDER_TYPE type)
{
   bool ok = (type == ORDER_TYPE_BUY) ? trade.Buy(0.1, _Symbol) : trade.Sell(0.1, _Symbol);
   if(!ok) Print("fail");
}
"""
    d, log = _doc(_DAU + mo + _TICK)
    assert any("gap_ba_ngoi_hang" in x for x in log)
    cc = d["co_che"]
    assert len(cc) == 2                              # ban cu: 4 luat (2 luat chieu SAI)
    assert sorted(c["chieu"] for c in cc) == [-1, 1]
    mua = [c for c in cc if c["chieu"] == 1][0]["ten"]
    assert "duoi" in mua.split("_va_")[0] and "tren" in mua.split("_va_")[1]   # mua khi cat LEN


def test_request_type_hang_danh_dau_chieu():
    vb = """void Mo(){ MqlTradeRequest rq={}; MqlTradeResult rs={}; rq.type = ORDER_TYPE_SELL; rq.volume=0.1;
 if(!OrderSend(rq, rs)) Print(1); }"""
    v2, log = TX._chieu_hang(vb)
    assert "OrderSend(rq, rs /*ORDER_TYPE_SELL*/)" in v2 and log
    # gan .type hai lan -> khong danh dau
    vb2 = vb.replace("rq.volume=0.1;", "rq.volume=0.1; if(x) rq.type = ORDER_TYPE_BUY;")
    assert "/*ORDER_TYPE" not in TX._chieu_hang(vb2)[0]


def test_bien_hang_cuc_bo_va_gan_lai():
    vb = "void Mo(){ ENUM_ORDER_TYPE t = ORDER_TYPE_BUY; trade.PositionOpen(_Symbol, t, 0.1, Ask, 0, 0); }"
    assert "PositionOpen(_Symbol, ORDER_TYPE_BUY," in TX._chieu_hang(vb)[0]
    vb2 = vb.replace("trade.", "if(z) t = ORDER_TYPE_SELL; trade.")
    assert "PositionOpen(_Symbol, t," in TX._chieu_hang(vb2)[0]


def test_else_thanh_if_chi_khi_nhanh_co_lenh():
    vb = ("void OnTick(){ if(OrdersTotal()>=1){ x(); } else { if(a>b) OrderSend(Symbol(),OP_BUY,1,Ask,3,0,0); }"
          " if(c) y(); else z(); }")
    v2, log = TX._else_thanh_if(vb)
    assert "if(!(OrdersTotal()>=1))" in v2 and "else z();" in v2 and log
    # dieu kien co gan -> giu nguyen
    vb3 = vb.replace("OrdersTotal()>=1", "(n=OrdersTotal())>=1")
    assert TX._else_thanh_if(vb3)[0] == vb3
    # else-if khong dung
    vb4 = "void OnTick(){ if(a) x(); else if(b) OrderSend(Symbol(),OP_BUY,1,Ask,3,0,0); }"
    assert TX._else_thanh_if(vb4)[0] == vb4
    # else treo (if long khong ngoac) -> khong dung
    vb5 = "void OnTick(){ if(a) if(b) x(); else OrderSend(Symbol(),OP_BUY,1,Ask,3,0,0); }"
    assert TX._else_thanh_if(vb5)[0] == vb5
    # chu thich truoc if khong chan
    vb6 = "void OnTick(){ x=1;\n // kiem vi the\n if(PositionSelect(_Symbol)) { y(); } else { if(a>b) trade.Buy(0.1); } }"
    assert "if(!(PositionSelect(_Symbol)))" in TX._else_thanh_if(vb6)[0]
