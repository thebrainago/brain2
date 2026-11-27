//+------------------------------------------------------------------+
//| VANG_LuoiEMA.mq5                                                  |
//| Luoi theo loc EMA 55: buoc 1.5 ATR, toi da 4 chan, TP 1.2 ATR     |
//| (gia TB), SL tong 5 ATR. Lot moi chan co dinh (InpLotChan).        |
//| Mo/them chan luc mo nến H1; chot TP/SL theo tick.                  |
//+------------------------------------------------------------------+
#property copyright "brain2 vang"
#property version   "1.00"
#property strict
#include <Trade/Trade.mqh>

input int    InpEMA        = 55;
input int    InpATR        = 14;
input double InpBuocATR    = 1.5;
input int    InpMaxChan    = 4;
input double InpTP_ATR     = 1.2;
input double InpSL_ATR     = 5.0;
input double InpLotChan    = 0.01;  // lot co dinh moi chan (do truoc tu ATR trung vi Python)
input long   InpMagic      = 2026112702;
input int    InpSlippage   = 50;

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

int DemChan(int &huong, double &tb, double &tong_lot)
{
   int n = 0;
   double ts = 0, tl = 0;
   huong = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      int typ = (int)PositionGetInteger(POSITION_TYPE);
      int h = (typ == POSITION_TYPE_BUY ? 1 : -1);
      if(huong == 0) huong = h;
      double v = PositionGetDouble(POSITION_VOLUME);
      double p = PositionGetDouble(POSITION_PRICE_OPEN);
      ts += p * v;
      tl += v;
      n++;
   }
   tong_lot = tl;
   tb = (tl > 0 ? ts / tl : 0);
   return n;
}

void DongHet(const string ly)
{
   DatKieuKhop();
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      trade.PositionClose(tk);
   }
}

void MoChan(int hu)
{
   DatKieuKhop();
   double lot = InpLotChan;
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(lot < vmin) lot = vmin;
   if(lot > vmax) lot = vmax;
   if(hu > 0)
      trade.Buy(lot, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_ASK), 0, 0, "LUOI_EMA55");
   else
      trade.Sell(lot, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_BID), 0, 0, "LUOI_EMA55");
}

void OnTick()
{
   if(Bars(_Symbol, PERIOD_H1) < InpEMA + 5) return;
   double atr[1];
   if(CopyBuffer(g_atr, 0, 1, 1, atr) < 1 || atr[0] <= 0) return;

   int hu = 0;
   double tb = 0, tl = 0;
   int nchan = DemChan(hu, tb, tl);

   // Chot theo tick: TP/SL quanh gia trung binh, ATR cua nến đã đóng.
   if(nchan > 0 && hu != 0)
   {
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      bool hit = false;
      if(hu > 0)
      {
         if(bid >= tb + InpTP_ATR * atr[0]) hit = true;
         else if(bid <= tb - InpSL_ATR * atr[0]) hit = true;
      }
      else
      {
         if(ask <= tb - InpTP_ATR * atr[0]) hit = true;
         else if(ask >= tb + InpSL_ATR * atr[0]) hit = true;
      }
      if(hit)
      {
         DongHet("tp_sl");
         nchan = 0;
         hu = 0;
      }
   }

   datetime t0 = iTime(_Symbol, PERIOD_H1, 0);
   if(t0 == 0 || t0 == g_bar) return;
   g_bar = t0;

   // Mo / them chan tai mo nến, loc EMA tai nến vừa đóng.
   nchan = DemChan(hu, tb, tl);
   double ema[1];
   if(CopyBuffer(g_ema, 0, 1, 1, ema) < 1) return;
   double c1 = iClose(_Symbol, PERIOD_H1, 1);
   int loc = 0;
   if(c1 > ema[0]) loc = 1;
   else if(c1 < ema[0]) loc = -1;
   if(loc == 0) return;

   double open0 = iOpen(_Symbol, PERIOD_H1, 0);
   if(nchan == 0)
      MoChan(loc);
   else if(nchan < InpMaxChan && hu == loc)
   {
      bool nguoc = (hu > 0) ? (open0 <= tb - InpBuocATR * atr[0])
                            : (open0 >= tb + InpBuocATR * atr[0]);
      if(nguoc) MoChan(hu);
   }
}
