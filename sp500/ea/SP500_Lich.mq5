//+------------------------------------------------------------------+
//| SP500_Lich.mq5 - he theo lich cho US500Cash XM (27/11/2026)       |
//| CheDo bit1: cuoi thang (TOM) mua 15:50 NY ngay GD cuoi thang,     |
//|   ban 15:50 NY ngay GD thu NgayDau cua thang moi.                 |
//| CheDo bit2: qua dem thu Hai - mua 15:50 NY thu Hai, ban 09:35 T3.  |
//| CheDo bit4: IBS - mua 15:50 NY khi IBS phien < IbsNguong, giu IbsGiu ngay.
//| Loc: 0 khong; 1 SMA100 (gia dong RTH) doc len so voi 21 ngay truoc|
//+------------------------------------------------------------------+
#property strict
#include <Trade/Trade.mqh>
input int    CheDo     = 1;     // 1=TOM, 2=thu Hai qua dem, 3=ca hai
input int    NgayDau   = 3;     // TOM: ban o ngay GD thu may cua thang moi
input int    Loc       = 0;
input double IbsNguong = 0.1;   // CheDo bit4: IBS phien RTH < nguong -> mua dong cua
input int    IbsGiu    = 3;     // so ngay giu lenh IBS
input int    IbsLoc    = 1;     // 1 = chi mua khi gia > SMA200 (D1)
input double DonBay    = 5.0;
input long   Magic     = 2711600;
CTrade tr;
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


double SoLot(double gia){ double tv=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_VALUE), ts=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE);
   double lot=DonBay*AccountInfoDouble(ACCOUNT_EQUITY)/(gia*tv/ts);
   double st=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP), mn=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN), mx=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MAX);
   lot=MathFloor(lot/st)*st; if(lot<mn) lot=0; if(lot>mx) lot=mx; return lot; }
bool CoVithe(long mg){ for(int i=PositionsTotal()-1;i>=0;i--){ ulong t=PositionGetTicket(i); if(PositionGetInteger(POSITION_MAGIC)==mg) return true;} return false; }
void Dong(long mg){ for(int i=PositionsTotal()-1;i>=0;i--){ ulong t=PositionGetTicket(i); if(PositionGetInteger(POSITION_MAGIC)==mg){ tr.SetExpertMagicNumber(mg); tr.PositionClose(t);} } }
void Mua(long mg){ double a=SymbolInfoDouble(_Symbol,SYMBOL_ASK); double l=SoLot(a); if(l<=0) return; tr.SetExpertMagicNumber(mg); tr.Buy(l,_Symbol,0,0,0,"lich"); }
bool LocOK(){ if(Loc==0) return true; MqlRates r[]; int n=CopyRates(_Symbol,PERIOD_D1,0,140,r); if(n<130) return false;
   double a=0,b=0; for(int i=n-100;i<n;i++) a+=r[i].close; for(int i=n-121;i<n-21;i++) b+=r[i].close; return a>b; }
int ibs_con=0;
bool Sma200OK(){ if(IbsLoc==0) return true; MqlRates r[]; int n=CopyRates(_Symbol,PERIOD_D1,0,205,r); if(n<201) return false; double m=0; for(int i=n-201;i<n-1;i++) m+=r[i].close; m/=200; return r[n-1].close>m; }
double IbsHomNay(datetime d){ MqlRates r[]; int n=CopyRates(_Symbol,PERIOD_M5,d,TimeCurrent(),r); double h=-1e18,l=1e18,c=0; int k=0;
   for(int i=0;i<n;i++){ int p=PhutNY(r[i].time); if(p<570||p>=960) continue; h=MathMax(h,r[i].high); l=MathMin(l,r[i].low); c=r[i].close; k++; }
   if(k<10||h<=l) return 0.5; return (c-l)/(h-l); }
int so_ngay_gd_thang=0; int thang_hien=-1; datetime ngay_dem=0, ngay_xu_ly_dong=0, ngay_xu_ly_mo=0;
int OnInit(){ return INIT_SUCCEEDED; }
void OnTick(){
   datetime now=TimeCurrent(); int p=PhutNY(now); datetime d=now-(now%86400); MqlDateTime t; TimeToStruct(now,t);
   if(p>=570 && d!=ngay_dem){ ngay_dem=d; if(t.mon!=thang_hien){thang_hien=t.mon; so_ngay_gd_thang=0;} so_ngay_gd_thang++; }
   // 09:35 NY: dong lenh qua dem thu Hai
   if(p>=575 && p<600 && d!=ngay_xu_ly_mo){ ngay_xu_ly_mo=d; if(CoVithe(Magic+2)) Dong(Magic+2); }
   if(p>=950 && p<958 && d!=ngay_xu_ly_dong){ ngay_xu_ly_dong=d;
      // TOM: ban o ngay GD thu NgayDau
      if((CheDo&1)!=0 && CoVithe(Magic+1) && so_ngay_gd_thang==NgayDau) Dong(Magic+1);
      // ngay GD cuoi thang: ngay lam viec ke tiep thuoc thang khac
      datetime nx=d+86400; MqlDateTime u; TimeToStruct(nx,u); while(u.day_of_week==0||u.day_of_week==6){ nx+=86400; TimeToStruct(nx,u);} 
      if((CheDo&1)!=0 && u.mon!=t.mon && !CoVithe(Magic+1) && LocOK()) Mua(Magic+1);
      if((CheDo&2)!=0 && t.day_of_week==1 && !CoVithe(Magic+2)) Mua(Magic+2);
      if((CheDo&4)!=0){ if(CoVithe(Magic+4)){ ibs_con--; if(ibs_con<=0) Dong(Magic+4); }
         else if(IbsHomNay(d)<IbsNguong && Sma200OK()){ Mua(Magic+4); ibs_con=IbsGiu; } }
   }
}
double OnTester(){
   HistorySelect(0,TimeCurrent()); string fn=StringFormat("sp500_lich_m%d_n%d_loc%d_ibs%.2f_%d_%d_L%.0f.csv",CheDo,NgayDau,Loc,IbsNguong,IbsGiu,IbsLoc,DonBay);
   int h=FileOpen(fn,FILE_WRITE|FILE_CSV|FILE_COMMON|FILE_ANSI,',');
   if(h!=INVALID_HANDLE){ FileWrite(h,"time","type","entry","volume","price","profit","swap","commission","balance_after");
      double bal=TesterStatistics(STAT_INITIAL_DEPOSIT);
      for(int i=0;i<HistoryDealsTotal();i++){ ulong k=HistoryDealGetTicket(i); long ty=HistoryDealGetInteger(k,DEAL_TYPE); if(ty>1) continue;
         double pr=HistoryDealGetDouble(k,DEAL_PROFIT),sw=HistoryDealGetDouble(k,DEAL_SWAP),cm=HistoryDealGetDouble(k,DEAL_COMMISSION); bal+=pr+sw+cm;
         FileWrite(h,TimeToString((datetime)HistoryDealGetInteger(k,DEAL_TIME)),ty,HistoryDealGetInteger(k,DEAL_ENTRY),HistoryDealGetDouble(k,DEAL_VOLUME),HistoryDealGetDouble(k,DEAL_PRICE),pr,sw,cm,bal);}
      FileClose(h);}
   return TesterStatistics(STAT_PROFIT); }
