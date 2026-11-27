//+------------------------------------------------------------------+
//| VANG_HedgeEMA.mq5                                                 |
//| Loc EMA: vao 1 chieu. Neu nguoc InpHedgeATR thi mo lenh dao       |
//| InpHeSoHedge lan lot. Chot ca hai khi lai rong >= TP ATR hoac     |
//| lo rong <= SL ATR (moc = he so * ATR * lot goc * 100).            |
//| Khung = Period cua tester (H1 hoac M15). Vao luc mo nen moi.      |
//| Ban doi chieu voi vang/ma/mo_phong_mo_rong.py :: _dao_hedge.      |
//+------------------------------------------------------------------+
#property copyright "brain2 vang"
#property version   "1.00"
#property strict
#include <Trade/Trade.mqh>

input int    InpEMA        = 55;
input int    InpATR        = 14;
input double InpHedgeATR   = 2.0;
input double InpTP_ATR     = 1.2;
input double InpSL_ATR     = 4.0;
input double InpHeSoHedge  = 1.5;
input double InpLotGoc     = 0.08;
input long   InpMagic      = 2026112703;
input int    InpSlippage   = 50;

CTrade   trade;
datetime g_bar = 0;
int      g_ema = INVALID_HANDLE;
int      g_atr = INVALID_HANDLE;
ulong    g_tk1 = 0;
ulong    g_tk2 = 0;
int      g_hu  = 0;
double   g_gia1 = 0;

int OnInit()
{
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpSlippage);
   g_ema = iMA(_Symbol, _Period, InpEMA, 0, MODE_EMA, PRICE_CLOSE);
   g_atr = iATR(_Symbol, _Period, InpATR);
   if(g_ema == INVALID_HANDLE || g_atr == INVALID_HANDLE)
      return INIT_FAILED;
   g_tk1 = g_tk2 = 0;
   g_hu = 0;
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

double ChuanLot(double lot)
{
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   if(step <= 0) step = 0.01;
   lot = MathFloor(lot / step + 1e-12) * step;
   if(lot < vmin) lot = vmin;
   if(lot > vmax) lot = vmax;
   return lot;
}

bool LaLenhTa(ulong tk)
{
   if(tk == 0 || !PositionSelectByTicket(tk)) return false;
   return (PositionGetString(POSITION_SYMBOL) == _Symbol &&
           PositionGetInteger(POSITION_MAGIC) == InpMagic);
}

void QuetLaiVeThe()
{
   // neu ticket mat, tim lai theo magic
   bool c1 = LaLenhTa(g_tk1);
   bool c2 = LaLenhTa(g_tk2);
   if(c1 && (c2 || g_tk2 == 0)) return;
   g_tk1 = 0; g_tk2 = 0; g_hu = 0;
   ulong a = 0, b = 0;
   int na = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(!LaLenhTa(tk)) continue;
      na++;
      if(a == 0) a = tk;
      else b = tk;
   }
   if(na == 0) return;
   if(!PositionSelectByTicket(a)) return;
   int typ = (int)PositionGetInteger(POSITION_TYPE);
   g_tk1 = a;
   g_hu = (typ == POSITION_TYPE_BUY ? 1 : -1);
   g_gia1 = PositionGetDouble(POSITION_PRICE_OPEN);
   if(na >= 2) g_tk2 = b;
}

double LaiRong()
{
   double s = 0;
   if(LaLenhTa(g_tk1))
      s += PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
   if(g_tk2 != 0 && LaLenhTa(g_tk2))
      s += PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
   return s;
}

void DongHet()
{
   DatKieuKhop();
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(!LaLenhTa(tk)) continue;
      trade.PositionClose(tk);
   }
   g_tk1 = 0;
   g_tk2 = 0;
   g_hu = 0;
}

bool MoLenh(int hu, double lot, const string cmt, ulong &tk)
{
   DatKieuKhop();
   lot = ChuanLot(lot);
   if(lot <= 0) return false;
   bool ok = false;
   if(hu > 0)
      ok = trade.Buy(lot, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_ASK), 0, 0, cmt);
   else
      ok = trade.Sell(lot, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_BID), 0, 0, cmt);
   if(!ok) return false;
   ulong deal = trade.ResultDeal();
   if(deal > 0 && HistoryDealSelect(deal))
   {
      tk = (ulong)HistoryDealGetInteger(deal, DEAL_POSITION_ID);
      if(tk > 0) return true;
   }
   // fallback: vi the moi nhat cung magic
   datetime moi = 0;
   tk = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(!LaLenhTa(t)) continue;
      datetime tm = (datetime)PositionGetInteger(POSITION_TIME);
      if(tm >= moi) { moi = tm; tk = t; }
   }
   return (tk > 0);
}

void OnTick()
{
   if(Bars(_Symbol, _Period) < InpEMA + 5) return;
   double atr[1];
   if(CopyBuffer(g_atr, 0, 1, 1, atr) < 1 || atr[0] <= 0) return;

   QuetLaiVeThe();

   if(g_tk1 != 0 && g_hu != 0)
   {
      // mo hedge khi gia di nguoc InpHedgeATR tu gia vao
      if(g_tk2 == 0)
      {
         double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
         double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
         bool nguoc = (g_hu > 0) ? (bid <= g_gia1 - InpHedgeATR * atr[0])
                                 : (ask >= g_gia1 + InpHedgeATR * atr[0]);
         if(nguoc)
         {
            ulong tk2 = 0;
            if(MoLenh(-g_hu, InpLotGoc * InpHeSoHedge, "HEDGE_DAO", tk2))
               g_tk2 = tk2;
         }
      }

      double moc_tp = InpTP_ATR * atr[0] * InpLotGoc * 100.0;
      double moc_sl = -InpSL_ATR * atr[0] * InpLotGoc * 100.0;
      double lai = LaiRong();
      if(lai <= moc_sl || lai >= moc_tp)
         DongHet();
   }

   datetime t0 = iTime(_Symbol, _Period, 0);
   if(t0 == 0 || t0 == g_bar) return;
   g_bar = t0;

   QuetLaiVeThe();
   if(g_tk1 != 0) return;

   double ema[1];
   if(CopyBuffer(g_ema, 0, 1, 1, ema) < 1) return;
   double c1 = iClose(_Symbol, _Period, 1);
   int loc = 0;
   if(c1 > ema[0]) loc = 1;
   else if(c1 < ema[0]) loc = -1;
   if(loc == 0) return;

   ulong tk = 0;
   if(MoLenh(loc, InpLotGoc, "HEDGE_GOC", tk))
   {
      g_tk1 = tk;
      g_hu = loc;
      if(PositionSelectByTicket(tk))
         g_gia1 = PositionGetDouble(POSITION_PRICE_OPEN);
   }
}
