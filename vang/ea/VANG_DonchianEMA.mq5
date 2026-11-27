//+------------------------------------------------------------------+
//| VANG_DonchianEMA.mq5                                              |
//| H1 Donchian 20 + loc EMA 55, SL 2*ATR / TP 4*ATR, rui ro 2%.      |
//| Tin hieu luc dong nen (bar 1), vao luc mo nen moi. Chi 1 vi the.   |
//| Ban doi chieu voi mo phong Python vang/ma/mo_phong.py.             |
//+------------------------------------------------------------------+
#property copyright "brain2 vang"
#property version   "1.00"
#property strict
#include <Trade/Trade.mqh>

input int    InpDonchian = 20;
input int    InpEMA      = 55;
input int    InpATR      = 14;
input double InpSL_ATR   = 2.0;
input double InpTP_ATR   = 4.0;
input double InpRuiRo    = 0.02;
input double InpVonTham  = 0.0;   // 0 = dung AccountInfoDouble(ACCOUNT_EQUITY)
input long   InpMagic    = 2026112701;
input int    InpSlippage = 50;    // diem (point)

CTrade trade;
datetime g_bar = 0;
int      g_ema = INVALID_HANDLE;
int      g_atr = INVALID_HANDLE;

int OnInit()
{
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpSlippage);
   g_ema = iMA(_Symbol, PERIOD_H1, InpEMA, 0, MODE_EMA, PRICE_CLOSE);
   g_atr = iATR(_Symbol, PERIOD_H1, InpATR);
   if(g_ema == INVALID_HANDLE || g_atr == INVALID_HANDLE)
      return INIT_FAILED;
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   if(g_ema != INVALID_HANDLE) IndicatorRelease(g_ema);
   if(g_atr != INVALID_HANDLE) IndicatorRelease(g_atr);
}

bool DangGiu()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol &&
         PositionGetInteger(POSITION_MAGIC) == InpMagic)
         return true;
   }
   return false;
}

double LotTheoRuiRo(double sl_khoang)
{
   double von = (InpVonTham > 0 ? InpVonTham : AccountInfoDouble(ACCOUNT_EQUITY));
   double tick = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tv   = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   if(tick <= 0 || tv <= 0 || sl_khoang <= 0) return 0;
   double rui_1lot = sl_khoang / tick * tv;
   if(rui_1lot <= 0) return 0;
   double lot = MathFloor((von * InpRuiRo / rui_1lot) / 0.01 + 1e-12) * 0.01;
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   if(lot < vmin)
   {
      if(vmin * rui_1lot > von * 0.05) return 0;
      lot = vmin;
   }
   if(lot > vmax) lot = vmax;
   if(step > 0) lot = MathFloor(lot / step + 1e-12) * step;
   return lot;
}

void DatKieuKhop()
{
   long fm = 0;
   if(!SymbolInfoInteger(_Symbol, SYMBOL_FILLING_MODE, fm)) return;
   if((fm & SYMBOL_FILLING_IOC) == SYMBOL_FILLING_IOC)
      trade.SetTypeFilling(ORDER_FILLING_IOC);
   else if((fm & SYMBOL_FILLING_FOK) == SYMBOL_FILLING_FOK)
      trade.SetTypeFilling(ORDER_FILLING_FOK);
   else
      trade.SetTypeFilling(ORDER_FILLING_RETURN);
}

void OnTick()
{
   datetime t0 = iTime(_Symbol, PERIOD_H1, 0);
   if(t0 == 0 || t0 == g_bar) return;
   g_bar = t0;
   if(DangGiu()) return;
   if(Bars(_Symbol, PERIOD_H1) < InpDonchian + InpEMA + 5) return;

   // Tin hieu tai nến vừa đóng (shift 1). Kenh = 20 nến truoc do (shift 2..21).
   double c1 = iClose(_Symbol, PERIOD_H1, 1);
   int hh_shift = iHighest(_Symbol, PERIOD_H1, MODE_HIGH, InpDonchian, 2);
   int ll_shift = iLowest(_Symbol, PERIOD_H1, MODE_LOW, InpDonchian, 2);
   if(hh_shift < 0 || ll_shift < 0) return;
   double hh = iHigh(_Symbol, PERIOD_H1, hh_shift);
   double ll = iLow(_Symbol, PERIOD_H1, ll_shift);

   double ema[2], atr[2];
   if(CopyBuffer(g_ema, 0, 1, 1, ema) < 1) return;
   if(CopyBuffer(g_atr, 0, 1, 1, atr) < 1) return;
   if(atr[0] <= 0) return;

   int hu = 0;
   if(c1 > hh && c1 > ema[0]) hu = 1;
   else if(c1 < ll && c1 < ema[0]) hu = -1;
   if(hu == 0) return;

   double slk = InpSL_ATR * atr[0];
   double tpk = InpTP_ATR * atr[0];
   double lot = LotTheoRuiRo(slk);
   if(lot <= 0) return;

   DatKieuKhop();
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double diem = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   int    dig  = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   if(hu > 0)
   {
      double sl = NormalizeDouble(ask - slk, dig);
      double tp = NormalizeDouble(ask + tpk, dig);
      trade.Buy(lot, _Symbol, ask, sl, tp, "DC20_EMA55");
   }
   else
   {
      double sl = NormalizeDouble(bid + slk, dig);
      double tp = NormalizeDouble(bid - tpk, dig);
      trade.Sell(lot, _Symbol, bid, sl, tp, "DC20_EMA55");
   }
}
