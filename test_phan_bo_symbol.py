# -*- coding: utf-8 -*-
"""A3 (the-brain 02 D5, 11/10/2026): nhan ma tin hieu MQL5 doc tu bang Distribution.

Fixture viet tay theo DUNG cau truc trang that (do 11/10/2026 tren /en/signals/2196457):
tai khoan vang `GOLD#` 1563 lenh + `USDCHF#` 2 lenh, va chu "USDCHF EURUSD" rai rac trong
trang. Regex cu (`_RX_SYM`) bo sot GOLD# va gan USDCHF/EURUSD - day la loi can bat.
"""
import _quet_signal_mql5 as Q
from nhan import tin_hieu_mql5 as TH

TRANG = """<html><head><title>Gold Scalper - MQL5 signal</title></head><body>
<p>Recommended: EURUSD EURUSD EURUSD, USDCHF, GBPUSD. Broker suffix .pro</p>
<h3 class="tab__content__title">Distribution</h3>
<table class="signals-chart-dist signalsChart">
 <thead><tr><th class="col-symbol">Symbol</th><th class="col-buy-sell"></th><th>Deals</th>
 <th style="text-align:right;">Sell</th><th>Buy</th></tr></thead>
 <tbody>
  <tr title="Trades on GOLD#"><td class="col-symbol">GOLD#</td>
   <td class="col-buy-sell col-right">1.5K</td>
   <td class="bar col-30" title="Trades on GOLD#: 1563"><div style="width: 78%;"></div></td>
   <td class="bar col-right col-30" title="Sell trades on GOLD#: 604"></td>
   <td class="bar col-30" title="Buy trades on GOLD#: 959"></td></tr>
  <tr title="Trades on XAUUSDm"><td class="col-symbol">XAUUSDm</td>
   <td class="col-buy-sell col-right">40</td><td class="bar col-30"></td></tr>
  <tr title="Trades on USDCHF#"><td class="col-symbol">USDCHF#</td>
   <td class="col-buy-sell col-right">2</td>
   <td class="bar col-30" title="Trades on USDCHF#: 2"></td></tr>
  <tr class="nohl"><td></td><td></td><td class="scale"><i>250</i></td></tr>
 </tbody></table>
<table class="signals-chart-dist signalsChart">
 <thead><tr><th class="col-symbol">Symbol</th><th></th><th>Gross Profit, USD</th>
 <th>Loss, USD</th><th>Profit, USD</th></tr></thead>
 <tbody><tr><td class="col-symbol">EURUSD</td><td class="col-buy-sell">99K</td></tr></tbody>
</table></body></html>"""


def test_chuan_symbol():
    assert TH.chuan_symbol("GOLD#") == "XAUUSD"
    assert TH.chuan_symbol("XAUUSDm") == "XAUUSD"
    assert TH.chuan_symbol("EURUSD.pro") == "EURUSD"
    assert TH.chuan_symbol("EURUSD_i") == "EURUSD"
    assert TH.chuan_symbol("USDCHF#") == "USDCHF"
    assert TH.chuan_symbol("US30m") == "US30"
    assert TH.chuan_symbol("SILVER") == "XAGUSD"


def test_phan_bo_doc_bang_deals_khong_doc_bang_usd():
    pb = TH.phan_bo_symbol(TRANG)
    assert pb["symbol_chinh"] == "XAUUSD"
    assert pb["top"] == ["XAUUSD", "USDCHF"]                 # EURUSD chi o bang USD/chu trang
    assert {x["tho"]: x["lenh"] for x in pb["symbol"]} == {"GOLD#": 1563, "XAUUSDm": 40,
                                                           "USDCHF#": 2}
    assert abs(pb["ty_le_lenh"] - 1603 / 1605) < 1e-3


def test_regex_cu_sai_dung_loi_can_bat():
    cu = set(Q._RX_SYM.findall(TRANG))
    assert "EURUSD" in cu and "XAUUSD" not in cu              # loi the-brain D5 tai hien


def test_nhan_symbol_khong_doan_khi_khong_co_bang():
    n = Q.nhan_symbol("<html>EURUSD EURUSD USDCHF</html>")
    assert n["symbol"] == [] and n["symbol_chinh"] is None
    assert "CHƯA ĐO ĐƯỢC" in n["symbol_nguon"]
    n = Q.nhan_symbol(TRANG)
    assert n["symbol"][0] == "XAUUSD" and n["symbol_nguon"] == "distribution"


def test_mot_khong_con_goi_regex_cu():
    import inspect
    src = inspect.getsource(Q.mot)
    assert "_RX_SYM" not in src and "nhan_symbol" in src
