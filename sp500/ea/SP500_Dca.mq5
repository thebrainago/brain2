//+------------------------------------------------------------------+
//| SP500_Dca.mq5 - DCA / go lenh trong phien My cho US500Cash XM     |
//| (27/11/2026) Ban MT5 cua sp500/ma/dca.py (k_dca, k_go).           |
//| He 1 = DCA ro: vao theo che do tai 09:30+Bar0*5 NY, gia nguoc     |
//|   Buoc*ATR -> them lenh klg*Nhan (toi NMax), chot ca ro khi gia   |
//|   vuot gia TB TP*ATR; Lap=1 vao lai sau khi chot; SL>0 cat sau day.|
//| He 2 = go lenh (zone recovery): vung Vung*ATR, dao chieu klg*Nhan,|
//|   dong het khi tong lai >= TP*ATR*1 don vi.                       |
//| Dong tat ca 15:59 NY (12:59 ngay dong som). Khong giu qua dem.    |
//| ATR14, SMA tinh tren nen ngay RTH (09:30-16:00 NY) ghep tu M5.    |
//+------------------------------------------------------------------+
#property strict
#include <Trade/Trade.mqh>
input int    He      = 1;     // 1 DCA, 2 go lenh
input int    LocXH   = 2;     // 0 none, 1 sma200, 2 slope200, 3 sma50&slope200
input bool   ChoBan  = false; // DCA: cho phep ban khi che do giam
input double Buoc    = 0.5;
input double Nhan    = 2.0;
input int    NMax    = 5;
input double TP      = 0.5;
input double SL      = 0.0;
input bool   Lap     = true;
input int    Bar0    = 6;
input double Vung    = 0.5;
input double DonBay  = 0.5;
input long   Magic   = 2711700;
input string TuNhan  = "x";
CTrade tr;
#include "LichNYSE.mqh"
double dO[],dH[],dL[],dC[]; int nd=0;
datetime ngay=0; int g=0; double atr=0, lot0=0, kl_cuoi=0, gia_cuoi=0, tren=0, duoi=0; int n=0, huong_cuoi=0; bool xong=true, da_vao=false;
void NenNgay(datetime d){ MqlRates r[]; int k=CopyRates(_Symbol,PERIOD_M5,d-400*86400,d,r); nd=0;
   ArrayResize(dO,0); ArrayResize(dH,0); ArrayResize(dL,0); ArrayResize(dC,0); datetime cur=0;
   for(int i=0;i<k;i++){ if(r[i].time>=d) break; int p=PhutNY(r[i].time); if(p<570||p>=960) continue; datetime dd=r[i].time-(r[i].time%86400);
      if(dd!=cur){ cur=dd; nd++; ArrayResize(dO,nd); ArrayResize(dH,nd); ArrayResize(dL,nd); ArrayResize(dC,nd); dO[nd-1]=r[i].open; dH[nd-1]=r[i].high; dL[nd-1]=r[i].low; }
      dH[nd-1]=MathMax(dH[nd-1],r[i].high); dL[nd-1]=MathMin(dL[nd-1],r[i].low); dC[nd-1]=r[i].close; } }
double Sma(int len,int lui){ int e=nd-lui; if(e-len<0) return -1; double s=0; for(int i=e-len;i<e;i++) s+=dC[i]; return s/len; }
int CheDo(){ if(nd<230) return 0; double pc=dC[nd-1];
   int a1=pc>Sma(200,0)?1:-1; int sl=Sma(200,0)>Sma(200,21)?1:-1; int s50=pc>Sma(50,0)?1:-1;
   if(LocXH==0) return 1; if(LocXH==1) return a1; if(LocXH==2) return sl; return (s50==sl)?s50:0; }
double Atr(){ if(nd<16) return 0; double s=0; for(int i=nd-14;i<nd;i++){ double t=MathMax(dH[i]-dL[i],MathMax(MathAbs(dH[i]-dC[i-1]),MathAbs(dL[i]-dC[i-1]))); s+=t;} return s/14; }
double LotChuan(double v){ double st=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP), mn=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN), mx=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MAX);
   v=MathFloor(v/st+1e-9)*st; if(v<mn) v=mn; if(v>mx) v=mx; return v; }
void Mo(int h,double kl){ tr.SetExpertMagicNumber(Magic); if(h>0) tr.Buy(LotChuan(kl),_Symbol,0,0,0,"dca"); else tr.Sell(LotChuan(kl),_Symbol,0,0,0,"dca"); }
void DongHet(){ tr.SetExpertMagicNumber(Magic); for(int i=PositionsTotal()-1;i>=0;i--){ ulong t=PositionGetTicket(i); if(PositionGetInteger(POSITION_MAGIC)==Magic) tr.PositionClose(t);} n=0; }
double LaiRo(){ double s=0; for(int i=PositionsTotal()-1;i>=0;i--){ ulong t=PositionGetTicket(i); if(PositionGetInteger(POSITION_MAGIC)==Magic) s+=PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP);} return s; }
double GiaTB(){ double s=0,v=0; for(int i=PositionsTotal()-1;i>=0;i--){ ulong t=PositionGetTicket(i); if(PositionGetInteger(POSITION_MAGIC)==Magic){ double q=PositionGetDouble(POSITION_VOLUME); s+=q*PositionGetDouble(POSITION_PRICE_OPEN); v+=q;} } return v>0?s/v:0; }
int OnInit(){ return INIT_SUCCEEDED; }
void OnTick(){
   datetime now=TimeCurrent(); int p=PhutNY(now); datetime d=now-(now%86400);
   if(NgayNghiNYSE(d)) return;
   int dong=PhutDongNY(d)-1;
   if(p>=dong){ if(n>0 || PositionsTotal()>0) DongHet(); xong=true; return; }
   if(p<570+Bar0*5) return;
   double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID), ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
   if(d!=ngay){ ngay=d; NenNgay(d); g=CheDo(); atr=Atr(); xong=(g==0||atr<=0); da_vao=false; n=0;
      if(He==1 && g<0 && !ChoBan) xong=true;
      double tv=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_VALUE), ts=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE);
      lot0=DonBay*AccountInfoDouble(ACCOUNT_EQUITY)/(bid*tv/ts); }
   if(xong) return;
   double tv=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_VALUE), ts=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE);
   if(He==1){
      double x=(g>0)?bid:ask;
      if(n==0){ if(da_vao && !Lap){ xong=true; return; } Mo(g,lot0); n=1; kl_cuoi=lot0; gia_cuoi=(g>0)?ask:bid; da_vao=true; return; }
      if(g*(x-GiaTB())>=TP*atr){ DongHet(); if(!Lap) xong=true; return; }
      if(n<NMax && g*(x-gia_cuoi)<=-Buoc*atr){ kl_cuoi*=Nhan; Mo(g,kl_cuoi); gia_cuoi-=g*Buoc*atr; n++; return; }
      if(SL>0 && n>=NMax && g*(x-gia_cuoi)<=-SL*atr){ DongHet(); xong=true; return; }
   } else {
      if(n==0){ if(da_vao){ xong=true; return; } Mo(g,lot0); n=1; kl_cuoi=lot0; huong_cuoi=g; da_vao=true;
         double p0=(g>0)?ask:bid; tren=(g>0)?p0:p0+Vung*atr; duoi=(g>0)?p0-Vung*atr:p0; return; }
      if(LaiRo()>=TP*atr*lot0*tv/ts){ DongHet(); xong=true; return; }
      if(n<NMax){ if(huong_cuoi>0 && bid<=duoi){ kl_cuoi*=Nhan; Mo(-1,kl_cuoi); huong_cuoi=-1; n++; }
         else if(huong_cuoi<0 && ask>=tren){ kl_cuoi*=Nhan; Mo(1,kl_cuoi); huong_cuoi=1; n++; } }
   }
}
double OnTester(){
   HistorySelect(0,TimeCurrent()); string fn=StringFormat("sp500_dca_%s_he%d_loc%d_b%.2f_n%.1f_m%d_tp%.2f_v%.2f_L%.2f.csv",TuNhan,He,LocXH,Buoc,Nhan,NMax,TP,Vung,DonBay);
   int h=FileOpen(fn,FILE_WRITE|FILE_CSV|FILE_COMMON|FILE_ANSI,',');
   if(h!=INVALID_HANDLE){ FileWrite(h,"time","type","entry","volume","price","profit","swap","commission","balance_after");
      double bal=TesterStatistics(STAT_INITIAL_DEPOSIT);
      for(int i=0;i<HistoryDealsTotal();i++){ ulong k=HistoryDealGetTicket(i); long ty=HistoryDealGetInteger(k,DEAL_TYPE); if(ty>1) continue;
         double pr=HistoryDealGetDouble(k,DEAL_PROFIT),sw=HistoryDealGetDouble(k,DEAL_SWAP),cm=HistoryDealGetDouble(k,DEAL_COMMISSION); bal+=pr+sw+cm;
         FileWrite(h,TimeToString((datetime)HistoryDealGetInteger(k,DEAL_TIME)),ty,HistoryDealGetInteger(k,DEAL_ENTRY),HistoryDealGetDouble(k,DEAL_VOLUME),HistoryDealGetDouble(k,DEAL_PRICE),pr,sw,cm,bal);}
      FileClose(h);}
   int q=FileOpen("sp500_tomtat.csv",FILE_READ|FILE_WRITE|FILE_CSV|FILE_COMMON|FILE_ANSI,','); if(q!=INVALID_HANDLE){ FileSeek(q,0,SEEK_END);
      FileWrite(q,fn,TimeToString(TimeCurrent()),TesterStatistics(STAT_INITIAL_DEPOSIT),TesterStatistics(STAT_PROFIT),TesterStatistics(STAT_TRADES),
        TesterStatistics(STAT_BALANCE_DDREL_PERCENT),TesterStatistics(STAT_EQUITY_DDREL_PERCENT),TesterStatistics(STAT_EQUITY_DD),TesterStatistics(STAT_MIN_MARGINLEVEL)); FileClose(q);}
   return TesterStatistics(STAT_PROFIT); }
