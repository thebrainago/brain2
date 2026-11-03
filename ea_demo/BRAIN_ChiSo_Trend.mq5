//+------------------------------------------------------------------+
//| BRAIN_ChiSo_Trend.mq5 - brain2 nhanh chi so (04/11/2026)           |
//| Theo xu huong thien MUA tren chi so CFD (US500/US30/US100/GER40).  |
//| Vao: gia > SMA(InpSmaCheDo) khung D1 (che do tang) + kich hoat:    |
//|   InpKichHoat=0 pha dinh Donchian N nen, 1 dong luc ROC N > 0,     |
//|   2 ca hai. Tuy chon loc ADX >= InpAdxMin (0 = tat).               |
//| Ra: SL ban dau InpSlATR*ATR, trailing InpTrailATR*ATR (chandelier),|
//|   thoat che do khi dong cua D1 < SMA che do (tuy chon them dem).   |
//| Lot: % rui ro theo khoang SL (ATR) hoac lot co dinh.               |
//| Swap: Tester tru swap that vao net; EA cong don swap/phi ra log va |
//|   OnTester tra net (da gom swap+phi) de bao cao rong.              |
//+------------------------------------------------------------------+
#property copyright "brain2"
#property version   "1.00"
#include <Trade/Trade.mqh>

input ENUM_TIMEFRAMES InpTF   = PERIOD_D1; // khung kich hoat/ATR (D1 hoac H4)
input int    InpSmaCheDo      = 200;   // SMA che do tren D1
input int    InpKichHoat      = 0;     // 0 Donchian, 1 ROC, 2 ca hai
input int    InpDonchianN     = 20;    // so nen pha dinh
input int    InpRocN          = 60;    // so nen dong luc
input double InpAdxMin        = 0.0;   // 0 = tat loc ADX
input int    InpAdxN          = 14;
input int    InpAtrN          = 20;
input double InpSlATR         = 3.0;   // SL ban dau = k*ATR
input double InpTrailATR      = 4.0;   // trailing = k*ATR tu dinh cao nhat; 0 = tat
input bool   InpThoatCheDo    = true;  // dong khi close D1 < SMA che do
input double InpDemCheDoPct   = 0.0;   // dem duoi SMA truoc khi thoat (% gia)
input bool   InpChoBan        = false; // cho phep ban khi gia < SMA (mac dinh chi mua)
input int    InpKieuLot       = 1;     // 0 lot co dinh, 1 % rui ro
input double InpLot0          = 0.1;   // lot co dinh (cung la tham so nhan k cua tho)
input double InpRuiRoPct      = 1.0;   // % von rui ro/lenh theo khoang SL
input double InpHeSoLot       = 1.0;   // nhan them lot (de quet k khi kieu % rui ro)
input double InpLotMax        = 50.0;
input long   InpMagic         = 2026110401;
input bool   InpLogChung      = true;
input string InpFileLog       = "brain2_chiso_log.csv";

CTrade trade;
int hSma=INVALID_HANDLE, hAtr=INVALID_HANDLE, hAdx=INVALID_HANDLE;
datetime g_nen=0;
double g_dinh=0;

double Buf(int h,int b,int i){ double a[]; if(CopyBuffer(h,b,i,1,a)!=1) return EMPTY_VALUE; return a[0]; }

void GhiLog(string s)
{
   int f = FileOpen(InpFileLog, FILE_READ|FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_SHARE_READ|(InpLogChung?FILE_COMMON:0), ';');
   if(f==INVALID_HANDLE) return;
   FileSeek(f,0,SEEK_END); FileWriteString(f,s+"\r\n"); FileClose(f);
}

int OnInit()
{
   hSma = iMA(_Symbol, PERIOD_D1, InpSmaCheDo, 0, MODE_SMA, PRICE_CLOSE);
   hAtr = iATR(_Symbol, InpTF, InpAtrN);
   if(InpAdxMin>0) hAdx = iADX(_Symbol, InpTF, InpAdxN);
   if(hSma==INVALID_HANDLE || hAtr==INVALID_HANDLE || (InpAdxMin>0 && hAdx==INVALID_HANDLE)) return INIT_FAILED;
   trade.SetExpertMagicNumber(InpMagic);
   return INIT_SUCCEEDED;
}

bool CoVithe(long &loai, ulong &ticket)
{
   for(int i=PositionsTotal()-1;i>=0;i--){
      ulong t=PositionGetTicket(i);
      if(PositionGetString(POSITION_SYMBOL)==_Symbol && PositionGetInteger(POSITION_MAGIC)==InpMagic){ loai=PositionGetInteger(POSITION_TYPE); ticket=t; return true; }
   }
   return false;
}

double TinhLot(double kc)
{
   double lot = InpLot0;
   if(InpKieuLot==1 && kc>0){
      double tv=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_VALUE), ts=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE);
      if(tv>0 && ts>0) lot = AccountInfoDouble(ACCOUNT_EQUITY)*InpRuiRoPct/100.0 / (kc/ts*tv);
   }
   lot *= InpHeSoLot;
   double st=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP), mn=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN), mx=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MAX);
   lot = MathFloor(lot/st)*st;
   lot = MathMin(MathMin(lot,mx),InpLotMax);
   return lot<mn ? 0 : lot;
}

void OnTick()
{
   datetime t0=iTime(_Symbol,InpTF,0);
   double atr=Buf(hAtr,0,1); if(atr==EMPTY_VALUE||atr<=0) return;
   long loai; ulong tk;
   bool co=CoVithe(loai,tk);
   // trailing moi tick theo dinh/day tu luc vao
   if(co && InpTrailATR>0){
      double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID), ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
      double sl=PositionGetDouble(POSITION_SL), tp=PositionGetDouble(POSITION_TP);
      if(loai==POSITION_TYPE_BUY){ g_dinh=MathMax(g_dinh,bid); double m=NormalizeDouble(g_dinh-InpTrailATR*atr,_Digits); if(m>sl+_Point && m<bid) trade.PositionModify(tk,m,tp); }
      else { if(g_dinh<=0) g_dinh=ask; g_dinh=MathMin(g_dinh,ask); double m=NormalizeDouble(g_dinh+InpTrailATR*atr,_Digits); if((sl==0||m<sl-_Point) && m>ask) trade.PositionModify(tk,m,tp); }
   }
   if(t0==g_nen) return; g_nen=t0;               // logic vao/ra theo nen dong
   double sma=Buf(hSma,0,1), cD1=iClose(_Symbol,PERIOD_D1,1);
   if(sma==EMPTY_VALUE||cD1<=0) return;
   bool tang = cD1 > sma, giam = cD1 < sma;
   co=CoVithe(loai,tk);
   if(co && InpThoatCheDo){
      if(loai==POSITION_TYPE_BUY && cD1 < sma*(1.0-InpDemCheDoPct/100.0)){ trade.PositionClose(tk); co=false; }
      else if(loai==POSITION_TYPE_SELL && cD1 > sma*(1.0+InpDemCheDoPct/100.0)){ trade.PositionClose(tk); co=false; }
   }
   if(co) return;
   double c1=iClose(_Symbol,InpTF,1);
   int ih=iHighest(_Symbol,InpTF,MODE_HIGH,InpDonchianN,2), il=iLowest(_Symbol,InpTF,MODE_LOW,InpDonchianN,2);
   bool phaLen = ih>=0 && c1 > iHigh(_Symbol,InpTF,ih);
   bool phaXuong = il>=0 && c1 < iLow(_Symbol,InpTF,il);
   double cRoc=iClose(_Symbol,InpTF,1+InpRocN);
   bool rocLen = cRoc>0 && c1>cRoc, rocXuong = cRoc>0 && c1<cRoc;
   bool kLen = InpKichHoat==0 ? phaLen : (InpKichHoat==1 ? rocLen : (phaLen&&rocLen));
   bool kXuong = InpKichHoat==0 ? phaXuong : (InpKichHoat==1 ? rocXuong : (phaXuong&&rocXuong));
   if(InpAdxMin>0){ double adx=Buf(hAdx,0,1); if(adx==EMPTY_VALUE||adx<InpAdxMin){ kLen=false; kXuong=false; } }
   double kc=InpSlATR*atr, lot=TinhLot(kc);
   if(lot<=0) return;
   if(tang && kLen){
      double a=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
      if(trade.Buy(lot,_Symbol,0,NormalizeDouble(a-kc,_Digits),0,"chiso_mua")) g_dinh=SymbolInfoDouble(_Symbol,SYMBOL_BID);
   } else if(InpChoBan && giam && kXuong){
      double b=SymbolInfoDouble(_Symbol,SYMBOL_BID);
      if(trade.Sell(lot,_Symbol,0,NormalizeDouble(b+kc,_Digits),0,"chiso_ban")) g_dinh=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
   }
}

void TongHop(double &loi,double &swp,double &phi,int &n)
{
   loi=0; swp=0; phi=0; n=0;
   if(!HistorySelect(0,TimeCurrent()+86400)) return;
   for(int i=0;i<HistoryDealsTotal();i++){
      ulong d=HistoryDealGetTicket(i);
      if(HistoryDealGetInteger(d,DEAL_MAGIC)!=InpMagic) continue;
      loi+=HistoryDealGetDouble(d,DEAL_PROFIT); swp+=HistoryDealGetDouble(d,DEAL_SWAP); phi+=HistoryDealGetDouble(d,DEAL_COMMISSION)+HistoryDealGetDouble(d,DEAL_FEE);
      if(HistoryDealGetInteger(d,DEAL_ENTRY)==DEAL_ENTRY_OUT) n++;
   }
}

double OnTester()
{
   double loi,swp,phi; int n; TongHop(loi,swp,phi,n);
   GhiLog(StringFormat("%s;%s;lenh=%d;loi_gop=%.2f;swap=%.2f;phi=%.2f;rong=%.2f",_Symbol,EnumToString(InpTF),n,loi,swp,phi,loi+swp+phi));
   return loi+swp+phi;   // net RONG (da tru swap + phi)
}

void OnDeinit(const int r)
{
   if(!MQLInfoInteger(MQL_TESTER)){ double loi,swp,phi; int n; TongHop(loi,swp,phi,n); GhiLog(StringFormat("deinit;%s;rong=%.2f;swap=%.2f",_Symbol,loi+swp+phi,swp)); }
}
