//+------------------------------------------------------------------+
//| SP500_BatDay.mq5 - mua bat day trong phien My (US500Cash XM)       |
//| Luat (do Python 27/11/2026 chon): mo phien NY 09:30, dat BUY LIMIT |
//| tai Open - KAtr*ATR14(phien RTH), TP = gia Open, khong qua dem:    |
//| dong het 15:55 NY. Tuy chon loc SMA200 (gia dong RTH).             |
//| Gio server XM = EET/EEST; NY 09:30 = 16:30 server, tru cac tuan    |
//| lech DST My/Au thi 15:30.                                          |
//+------------------------------------------------------------------+
#property strict
#include <Trade/Trade.mqh>
input double KAtr      = 0.75;  // khoang cach limit (x ATR14 RTH)
input double StopAtr   = 0.0;   // 0 = khong SL; >0 = SL = gia vao - StopAtr*ATR
input bool   TpVeOpen  = true;  // TP tai gia mo phien
input double DonBay    = 10.0;  // phoi nhiem = DonBay x equity
input int    LocXuHuong= 0;     // 0 khong loc; 1 chi mua khi dong RTH truoc > SMA200 RTH
input int    AtrN      = 14;
input long   Magic     = 2711500;
input bool   InNhatKy  = true;
CTrade tr;
datetime ngay_xu_ly = 0; double gia_open = 0; double atr_rth = 0; bool cho_phep = false;

int ChuNhatThu(int y,int m,int k){ // ngay cua Chu Nhat thu k (k=-1: cuoi thang)
   MqlDateTime t; t.year=y; t.mon=m; t.day=1; t.hour=0; t.min=0; t.sec=0;
   datetime d=StructToTime(t); TimeToStruct(d,t);
   int first=1+((7-t.day_of_week)%7);
   if(k>0) return first+7*(k-1);
   int dim=(m==2)?28:((m==4||m==6||m==9||m==11)?30:31);
   int last=first; while(last+7<=dim) last+=7; return last;
}
bool MyDST(MqlDateTime &t){ int a=ChuNhatThu(t.year,3,2), b=ChuNhatThu(t.year,11,1);
   if(t.mon>3&&t.mon<11) return true; if(t.mon==3) return t.day>=a; if(t.mon==11) return t.day<b; return false; }
bool EuDST(MqlDateTime &t){ int a=ChuNhatThu(t.year,3,-1), b=ChuNhatThu(t.year,10,-1);
   if(t.mon>3&&t.mon<10) return true; if(t.mon==3) return t.day>=a; if(t.mon==10) return t.day<b; return false; }
int LechGio(MqlDateTime &t){ return (MyDST(t)==EuDST(t))?0:-60; } // phut
int PhutNY(datetime s){ MqlDateTime t; TimeToStruct(s,t); return t.hour*60+t.min - 7*60 - LechGio(t); } // phut tu 00:00 NY

// Tinh ATR & SMA tren nen phien RTH tu M5 lich su (truoc ngay hien tai)
bool TinhRTH(datetime hom_nay){
   MqlRates r[]; int can=(LocXuHuong==1?215:AtrN+3)*300;
   int n=CopyRates(_Symbol,PERIOD_M5,hom_nay-1,can,r); if(n<1000) return false;
   double hi[],lo[],cl[]; ArrayResize(hi,0);ArrayResize(lo,0);ArrayResize(cl,0);
   datetime cur=0; double h=0,l=0,c=0; int k=0;
   for(int i=0;i<n;i++){ int p=PhutNY(r[i].time); if(p<570||p>=960) continue;
      datetime d=r[i].time-(r[i].time%86400);
      if(d!=cur){ if(cur!=0){k++;ArrayResize(hi,k);ArrayResize(lo,k);ArrayResize(cl,k);hi[k-1]=h;lo[k-1]=l;cl[k-1]=c;}
         cur=d;h=r[i].high;l=r[i].low; }
      h=MathMax(h,r[i].high); l=MathMin(l,r[i].low); c=r[i].close; }
   if(cur!=0){k++;ArrayResize(hi,k);ArrayResize(lo,k);ArrayResize(cl,k);hi[k-1]=h;lo[k-1]=l;cl[k-1]=c;}
   if(k<AtrN+2) return false;
   double s=0; for(int i=k-AtrN;i<k;i++){ double trr=MathMax(hi[i]-lo[i],MathMax(MathAbs(hi[i]-cl[i-1]),MathAbs(lo[i]-cl[i-1]))); s+=trr; }
   atr_rth=s/AtrN; cho_phep=true;
   if(LocXuHuong==1){ if(k<200){cho_phep=false;return true;} double m=0; for(int i=k-200;i<k;i++) m+=cl[i]; m/=200; cho_phep=cl[k-1]>m; }
   return true;
}
double SoLot(double gia){ double tv=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_VALUE), ts=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE);
   double notional_1lot=gia*tv/ts; double lot=DonBay*AccountInfoDouble(ACCOUNT_EQUITY)/notional_1lot;
   double st=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP), mn=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN), mx=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MAX);
   lot=MathFloor(lot/st)*st; if(lot<mn) lot=0; if(lot>mx) lot=mx; return lot; }
void DongHet(){ for(int i=PositionsTotal()-1;i>=0;i--){ ulong t=PositionGetTicket(i); if(PositionGetString(POSITION_SYMBOL)==_Symbol&&PositionGetInteger(POSITION_MAGIC)==Magic) tr.PositionClose(t);} 
   for(int i=OrdersTotal()-1;i>=0;i--){ ulong t=OrderGetTicket(i); if(OrderGetString(ORDER_SYMBOL)==_Symbol&&OrderGetInteger(ORDER_MAGIC)==Magic) tr.OrderDelete(t);} }
int OnInit(){ tr.SetExpertMagicNumber(Magic); return INIT_SUCCEEDED; }
void OnTick(){
   datetime now=TimeCurrent(); int p=PhutNY(now); datetime d=now-(now%86400);
   if(p>=950 || p<570){ if(PositionsTotal()+OrdersTotal()>0) DongHet(); return; }
   if(d!=ngay_xu_ly && p>=570 && p<575){
      ngay_xu_ly=d; DongHet();
      if(!TinhRTH(d)) return; if(!cho_phep) return;
      gia_open=SymbolInfoDouble(_Symbol,SYMBOL_BID);
      double e=NormalizeDouble(gia_open-KAtr*atr_rth,_Digits);
      double lot=SoLot(e); if(lot<=0) return;
      double sl=StopAtr>0?NormalizeDouble(e-StopAtr*atr_rth,_Digits):0, tp=TpVeOpen?NormalizeDouble(gia_open,_Digits):0;
      bool ok=tr.BuyLimit(lot,e,_Symbol,sl,tp,ORDER_TIME_GTC,0,"batday");
      if(InNhatKy) PrintFormat("NGAY %s open=%.2f atr=%.2f limit=%.2f lot=%.2f ok=%d",TimeToString(now),gia_open,atr_rth,e,lot,ok);
   }
}
double OnTester(){
   HistorySelect(0,TimeCurrent()); string fn=StringFormat("sp500_batday_%s_k%.2f_s%.1f_L%.0f_f%d.csv",_Symbol,KAtr,StopAtr,DonBay,LocXuHuong);
   int h=FileOpen(fn,FILE_WRITE|FILE_CSV|FILE_COMMON|FILE_ANSI,',');
   if(h!=INVALID_HANDLE){ FileWrite(h,"time","type","entry","volume","price","profit","swap","commission","balance_after");
      double bal=TesterStatistics(STAT_INITIAL_DEPOSIT);
      for(int i=0;i<HistoryDealsTotal();i++){ ulong t=HistoryDealGetTicket(i); long ty=HistoryDealGetInteger(t,DEAL_TYPE); if(ty>1) continue;
         double pr=HistoryDealGetDouble(t,DEAL_PROFIT),sw=HistoryDealGetDouble(t,DEAL_SWAP),cm=HistoryDealGetDouble(t,DEAL_COMMISSION); bal+=pr+sw+cm;
         FileWrite(h,TimeToString((datetime)HistoryDealGetInteger(t,DEAL_TIME)),ty,HistoryDealGetInteger(t,DEAL_ENTRY),HistoryDealGetDouble(t,DEAL_VOLUME),HistoryDealGetDouble(t,DEAL_PRICE),pr,sw,cm,bal);}
      FileClose(h);}
   return TesterStatistics(STAT_PROFIT); }
