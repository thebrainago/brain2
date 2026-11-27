//+------------------------------------------------------------------+
//| VANG_LuoiPhuc.mq5                                                 |
//| Luoi + nhan lot trong ro (InpHeSoLot) + go lenh sau ro lo         |
//| (InpHeSoPhuc ^ bac, toi da InpMaxBac). TP/SL quanh gia TB.        |
//| Khung = Period tester. Doi chieu mo_phong_mo_rong._phuc_hoi.      |
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
input double InpLotChan    = 0.01;
input double InpHeSoLot    = 1.0;   // nhan lot trong ro: chan k *= he^so k
input double InpHeSoPhuc   = 1.0;   // nhan ca ro sau lo
input int    InpMaxBac     = 0;     // so lan tang bac go sau lo
input long   InpMagic      = 2026112705;
input int    InpSlippage   = 50;

CTrade   trade;
datetime g_bar = 0;
int      g_ema = INVALID_HANDLE;
int      g_atr = INVALID_HANDLE;
int      g_bac = 0;
double   g_no  = 0;

int OnInit()
{
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpSlippage);
   g_ema = iMA(_Symbol, _Period, InpEMA, 0, MODE_EMA, PRICE_CLOSE);
   g_atr = iATR(_Symbol, _Period, InpATR);
   if(g_ema == INVALID_HANDLE || g_atr == INVALID_HANDLE)
      return INIT_FAILED;
   g_bac = 0;
   g_no = 0;
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

bool LaLenhTaTicket(ulong tk)
{
   if(tk == 0 || !PositionSelectByTicket(tk)) return false;
   return (PositionGetString(POSITION_SYMBOL) == _Symbol &&
           PositionGetInteger(POSITION_MAGIC) == InpMagic);
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
      if(!LaLenhTaTicket(tk)) continue;
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

void DongHet()
{
   DatKieuKhop();
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(!LaLenhTaTicket(tk)) continue;
      trade.PositionClose(tk);
   }
}

void CapNhatBacSauChot(double pnl)
{
   g_no -= pnl;
   if(g_no <= 0.0 && pnl > 0.0)
   {
      g_no = 0.0;
      g_bac = 0;
   }
   else if(pnl < 0.0)
   {
      if(g_bac < InpMaxBac)
         g_bac++;
   }
}

double LotChanThu(int chi_so_chan)
{
   double scale = 1.0;
   if(InpHeSoPhuc > 1.0000001 && g_bac > 0)
      scale = MathPow(InpHeSoPhuc, g_bac);
   double hs = 1.0;
   if(InpHeSoLot > 1.0000001 && chi_so_chan > 0)
      hs = MathPow(InpHeSoLot, chi_so_chan);
   return ChuanLot(InpLotChan * scale * hs);
}

void MoChan(int hu, int chi_so_chan)
{
   DatKieuKhop();
   double lot = LotChanThu(chi_so_chan);
   if(lot <= 0) return;
   if(hu > 0)
      trade.Buy(lot, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_ASK), 0, 0, "LUOI_PHUC");
   else
      trade.Sell(lot, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_BID), 0, 0, "LUOI_PHUC");
}

void OnTick()
{
   if(Bars(_Symbol, _Period) < InpEMA + 5) return;
   double atr[1];
   if(CopyBuffer(g_atr, 0, 1, 1, atr) < 1 || atr[0] <= 0) return;

   int hu = 0;
   double tb = 0, tl = 0;
   int nchan = DemChan(hu, tb, tl);

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
         double eq0 = AccountInfoDouble(ACCOUNT_EQUITY);
         DongHet();
         double pnl = AccountInfoDouble(ACCOUNT_EQUITY) - eq0;
         CapNhatBacSauChot(pnl);
         nchan = 0;
         hu = 0;
      }
   }

   datetime t0 = iTime(_Symbol, _Period, 0);
   if(t0 == 0 || t0 == g_bar) return;
   g_bar = t0;

   nchan = DemChan(hu, tb, tl);
   double ema[1];
   if(CopyBuffer(g_ema, 0, 1, 1, ema) < 1) return;
   double c1 = iClose(_Symbol, _Period, 1);
   int loc = 0;
   if(c1 > ema[0]) loc = 1;
   else if(c1 < ema[0]) loc = -1;
   if(loc == 0) return;

   double open0 = iOpen(_Symbol, _Period, 0);
   if(nchan == 0)
      MoChan(loc, 0);
   else if(nchan < InpMaxChan && hu == loc)
   {
      bool nguoc = (hu > 0) ? (open0 <= tb - InpBuocATR * atr[0])
                            : (open0 >= tb + InpBuocATR * atr[0]);
      if(nguoc) MoChan(hu, nchan);
   }
}
