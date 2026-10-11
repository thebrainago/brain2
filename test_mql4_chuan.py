# -*- coding: utf-8 -*-
"""Lan MQL4 mong (`nhan/mql4_chuan.py`, 11/10/2026): chi doi CU PHAP co tuong duong 1-1.

Cac ca PHAI giu nguyen (bo doc tu choi): lenh CHO, khung co dinh khac, dich bar la bien,
chuoi tu tinh (Heikin-Ashi) - chi them ly do cau truc, khong dich.
"""
from nhan import doc_ma as DM
from nhan import mql4_chuan as M4

_EA4 = """
extern int MAPeriod = 20;
extern double Lots = 0.1;
int start()
{
   if(OrdersTotal() > 0) return(0);
   double ma1 = iMA(NULL,0,MAPeriod,0,MODE_EMA,PRICE_CLOSE,1);
   if(Close[1] > ma1 && Close[2] <= iMA(NULL,0,MAPeriod,0,MODE_EMA,PRICE_CLOSE,2))
      OrderSend(Symbol(), OP_BUY, Lots, Ask, 3, 0, 0, "x", 1, 0, clrBlue);
   return(0);
}
"""


def test_chuan_hoa_cu_phap():
    vb = M4.chuan_hoa(_EA4)
    assert "input int MAPeriod = 20;" in vb
    assert "void OnTick()" in vb
    assert "ORDER_TYPE_BUY" in vb and "OP_BUY" not in vb
    assert "iClose(_Symbol,_Period,1)" in vb
    assert "SymbolInfoDouble(_Symbol,SYMBOL_ASK)" in vb
    # cung ky hieu ma `_chuan_hoa_mql5` sinh tu handle+CopyBuffer: bar1 = khong hau to, bar2 = [1]
    assert "iMA(_Symbol,_Period,20,0,MODE_EMA,PRICE_CLOSE)" in vb
    assert "iMA(_Symbol,_Period,20,0,MODE_EMA,PRICE_CLOSE)[1]" in vb


def test_mql4_doc_duoc_qua_bo_doc_chung():
    r = DM.doc_chien_luoc(M4.chuan_hoa(_EA4), nguon="t4")
    assert r["so_vao_lenh_co_co_che"] == 1, r["chua_dien_dat_duoc"]
    s = str(r["co_che"][0]["vao"])
    assert "'ema'" in s and "'n': 20" in s


def test_lenh_cho_giu_nguyen_tu_choi():
    vb = _EA4.replace("OP_BUY,", "OP_BUYSTOP,")
    out = M4.chuan_hoa(vb)
    assert "OP_BUYSTOP" in out
    assert DM.doc_chien_luoc(out, nguon="t")["so_vao_lenh_co_co_che"] == 0
    assert any("lenh CHO" in x for x in M4.dau_hieu_chan(vb))


def test_khung_co_dinh_va_dich_bien_giu_nguyen():
    vb = _EA4.replace("iMA(NULL,0,MAPeriod,0,MODE_EMA,PRICE_CLOSE,1)",
                      "iMA(NULL,PERIOD_H4,MAPeriod,0,MODE_EMA,PRICE_CLOSE,1)")
    assert "PERIOD_H4" in M4.chuan_hoa(vb)
    vb2 = _EA4.replace("PRICE_CLOSE,1)", "PRICE_CLOSE,i)")
    assert "PRICE_CLOSE,i)" in M4.chuan_hoa(vb2)


def test_bands_doi_thu_tu_doi_so():
    vb = "x = iBands(NULL,0,20,2.0,0,PRICE_CLOSE,MODE_UPPER,1);"
    assert "iBands_tren(_Symbol,_Period,20,0,2.0,PRICE_CLOSE)" in M4.chuan_hoa(vb)


def test_ly_do_cau_truc():
    ha = """
int start(){
   for(int idx=n; idx>=0; idx--) {
      haOpen[idx] = (Open[idx]+Close[idx])/2.0;
   }
   OrderSend(Symbol(), OP_BUY, 0.1, Ask, 3, 0, 0);
   return(0);
}"""
    assert any("haOpen" in x for x in M4.dau_hieu_chan(ha))
    assert M4.dau_hieu_chan("int start(){ return(0); }") == \
        ["khong co OrderSend (khung/khuon mau, khong dat lenh)"]
