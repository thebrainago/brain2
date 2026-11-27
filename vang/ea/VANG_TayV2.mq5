//+------------------------------------------------------------------+
//| VANG_TayV2.mq5                                                    |
//| Phong mach tay_v2 mac dinh vang (commit 59672872), khong delta15. |
//| Cum L0*K, TP gia, DCA khe, hedge hfrac, flcap (chi dung DCA),     |
//| dong ro lo tong X% equity luc mo, ADX+D1 EMA200 dung DCA,         |
//| FlatOrphan=1 (khong lat hedge). Them: dca_mode, lc_period/pause,  |
//| day/week_loss, eq_lot. Input moi mac dinh 0 = tat (hanh vi cu).   |
//| MT5 p4 tick that 2025.09-2026.11: maxL=8+orphan VAN pha (~-9994). |
//| Khong dat lenh that. Tester only.                                 |
//+------------------------------------------------------------------+
#property copyright "brain2 vang tay_v2"
#property version   "1.02"
#property strict
#include <Trade/Trade.mqh>

input double InpL0         = 0.01;
input int    InpK          = 4;
input int    InpMaxL       = 8;
input int    InpMaxH       = 10;
input double InpTP         = 4.00;
input double InpGap        = 5.47;
input double InpHGap       = 21.37;
input double InpHFrac      = 1.0;
input double InpFlCap      = 0.15;
input double InpLossClose  = 0.30;
input int    InpADXLen     = 14;
input double InpADXTh      = 30.0;
input int    InpEMA200     = 200;
input int    InpSlopeBars  = 10;
input int    InpCooldown   = 240;
input int    InpMaxLc      = 0;      // 0=tat; sau N lan dong lo tong thi dung mo ro moi
input double InpShortCap   = 0.0;    // 0=tat; tran tong lot chieu ngan (cum+DCA)
input int    InpFlatOrphan = 1;      // 1=dong hedge mo coi khi het lenh chinh, khong lat ro
input int    InpLcPeriod   = 0;      // 0=max_lc vinh vien; >0 dem max_lc trong N nen M1 roi pause
input int    InpLcPause    = 0;      // 0=pause = lc_period; so nen dung sau khi dat max_lc trong cua so
input double InpDayLoss    = 0.0;    // 0=tat; dung vao/DCA moi khi lo ngay >= X * equity dau ngay
input double InpWeekLoss   = 0.0;    // 0=tat; tuong tu theo 5 ngay roll (VN)
input int    InpEqLot      = 0;      // 0=tat; 1=giam K va maxL theo min(1, balance/von ban dau), khong tang
input int    InpDcaMode    = 0;      // 0=ADX dung DCA nguoc; 1=DCA chi cung slope; 2=ca tin hieu chi cung slope
input double InpD1OneWay   = 0.60;
input int    InpBBLen      = 20;
input long   InpMagic      = 2026112791;
input int    InpSlippage   = 50;
input int    InpMaxSpreadPts = 500;

CTrade   trade;
datetime g_bar = 0;
int      g_adx = INVALID_HANDLE;
int      g_ema = INVALID_HANDLE;
int      g_bb_mid = INVALID_HANDLE;
int      g_bb_sd  = INVALID_HANDLE;
int      g_atr15  = INVALID_HANDLE;

int      g_cool_left = 0;
int      g_n_lc      = 0;
int      g_n_lc_win  = 0;
int      g_lc_win_i0 = -1;
int      g_bar_i     = 0;
int      g_day_key   = 0;
int      g_n_day     = 0;
double   g_eq0       = 0;
double   g_day_eq0   = 0;
double   g_week_eq0  = 0;
bool     g_day_stop  = false;
bool     g_week_stop = false;
bool     g_halt      = false;
double   g_eq_open   = 0;
double   g_eq_bar    = 0;
double   g_realized  = 0;
datetime g_open_bar  = 0;
int      g_k_init    = 0;
bool     g_hedged    = false;
double   g_last_main = 0;
int      g_main_s    = 0;
ulong    g_mains[64];
ulong    g_hedges[32];
int      g_nm = 0;
int      g_nh = 0;

int OnInit()
{
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpSlippage);
   long mm = AccountInfoInteger(ACCOUNT_MARGIN_MODE);
   if(mm != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
      Print("CANH BAO: tai khoan khong phai hedging, cum ve the co the gop netting.");
   g_adx = iADX(_Symbol, PERIOD_M15, InpADXLen);
   g_ema = iMA(_Symbol, PERIOD_D1, InpEMA200, 0, MODE_EMA, PRICE_CLOSE);
   g_bb_mid = iMA(_Symbol, PERIOD_M15, InpBBLen, 0, MODE_SMA, PRICE_CLOSE);
   g_bb_sd  = iStdDev(_Symbol, PERIOD_M15, InpBBLen, 0, MODE_SMA, PRICE_CLOSE);
   g_atr15  = iATR(_Symbol, PERIOD_M15, 14);
   if(g_adx==INVALID_HANDLE || g_ema==INVALID_HANDLE || g_bb_mid==INVALID_HANDLE ||
      g_bb_sd==INVALID_HANDLE || g_atr15==INVALID_HANDLE)
      return INIT_FAILED;
   DatKieuKhop();
   g_eq0 = AccountInfoDouble(ACCOUNT_BALANCE);
   if(g_eq0<1) g_eq0=10000;
   g_day_eq0 = g_eq0;
   g_week_eq0 = g_eq0;
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   if(g_adx!=INVALID_HANDLE) IndicatorRelease(g_adx);
   if(g_ema!=INVALID_HANDLE) IndicatorRelease(g_ema);
   if(g_bb_mid!=INVALID_HANDLE) IndicatorRelease(g_bb_mid);
   if(g_bb_sd!=INVALID_HANDLE) IndicatorRelease(g_bb_sd);
   if(g_atr15!=INVALID_HANDLE) IndicatorRelease(g_atr15);
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
   if(step<=0) step=0.01;
   lot = MathFloor(lot/step+1e-12)*step;
   if(lot<vmin) lot=0;
   if(lot>vmax) lot=vmax;
   return lot;
}

datetime TimeVN(const datetime t)
{
   // May chu XM = Europe/Athens. VN = UTC+7.
   // EU DST: chu nhat cuoi Thang 3 -> chu nhat cuoi Thang 10.
   int y = TimeYear(t);
   datetime start = LastSunday(y, 3);
   datetime stop  = LastSunday(y, 10);
   bool eust = (t>=start && t<stop);
   int add = eust ? 4*3600 : 5*3600;
   return t + add;
}

datetime LastSunday(const int year, const int month)
{
   // 01:00 server (gan 00:00 UTC+0/+1) — dung ngay chu nhat cuoi
   MqlDateTime dt;
   dt.year=year; dt.mon=month; dt.day=1; dt.hour=1; dt.min=0; dt.sec=0;
   int nextm = (month==12?1:month+1);
   int nexty = (month==12?year+1:year);
   MqlDateTime nx; nx.year=nexty; nx.mon=nextm; nx.day=1; nx.hour=1; nx.min=0; nx.sec=0;
   datetime t = StructToTime(nx) - 86400;
   TimeToStruct(t, dt);
   while(dt.day_of_week!=0)
   {
      t -= 86400;
      TimeToStruct(t, dt);
   }
   return t;
}

int TimeYear(const datetime t)
{
   MqlDateTime dt; TimeToStruct(t, dt); return dt.year;
}

int HourVN(const datetime t)
{
   MqlDateTime dt; TimeToStruct(TimeVN(t), dt); return dt.hour;
}

int MinuteVN(const datetime t)
{
   MqlDateTime dt; TimeToStruct(TimeVN(t), dt); return dt.min;
}

int DayKeyVN(const datetime t)
{
   MqlDateTime dt; TimeToStruct(TimeVN(t), dt);
   return dt.year*10000 + dt.mon*100 + dt.day;
}

bool UsOpenBar(const datetime t)
{
   datetime vn = TimeVN(t);
   MqlDateTime dt; TimeToStruct(vn, dt);
   int y=dt.year, mo=dt.mon, d=dt.day, h=dt.hour, mi=dt.min;
   bool usdst=false;
   if(y==2026)
      usdst = ( (mo>3 || (mo==3 && d>=8)) && (mo<11) );
   else
      usdst = (mo>=4 && mo<=10);
   int mo_open = usdst ? (20*60+30) : (21*60+30);
   int cur = h*60+mi;
   int rel = cur - mo_open;
   if(rel<0) rel += 1440;
   return (rel < 120);
}

bool PhienLU(const datetime t)
{
   int h = HourVN(t);
   return (h>=14 || h<7);
}

double Median(double &a[], int n)
{
   if(n<=0) return 0;
   double b[];
   ArrayResize(b,n);
   for(int i=0;i<n;i++) b[i]=a[i];
   ArraySort(b);
   if((n%2)==1) return b[n/2];
   return 0.5*(b[n/2-1]+b[n/2]);
}

bool RejM5(const int hu)
{
   // bar M5 da dong (shift 1)
   double o=iOpen(_Symbol,PERIOD_M5,1);
   double h=iHigh(_Symbol,PERIOD_M5,1);
   double l=iLow(_Symbol,PERIOD_M5,1);
   double c=iClose(_Symbol,PERIOD_M5,1);
   double rng=h-l;
   if(rng<=0) return false;
   if(hu>0)
      return ((MathMin(o,c)-l)/rng>=0.50 && c>=l+0.6*rng);
   return ((h-MathMax(o,c))/rng>=0.50 && c<=h-0.6*rng);
}

double VwapZ()
{
   // VWAP ngay VN, tinh den nen M1 shift 1. z = (c1-vwap)/sd.
   datetime t1 = iTime(_Symbol, PERIOD_M1, 1);
   if(t1==0) return 0;
   int key = DayKeyVN(t1);
   int nb = Bars(_Symbol, PERIOD_M1);
   double s=0, sv=0, sq=0;
   int used=0;
   int lim = MathMin(nb, 2000);
   for(int i=1;i<lim;i++)
   {
      datetime ti=iTime(_Symbol,PERIOD_M1,i);
      if(ti==0) break;
      if(DayKeyVN(ti)!=key) break;
      double tp=(iHigh(_Symbol,PERIOD_M1,i)+iLow(_Symbol,PERIOD_M1,i)+iClose(_Symbol,PERIOD_M1,i))/3.0;
      double v=(double)iTickVolume(_Symbol,PERIOD_M1,i);
      if(v<=0) v=1;
      s  += tp*v;
      sq += v*tp*tp;
      sv += v;
      used++;
   }
   if(sv<=0 || used<2) return 0;
   double vw=s/sv;
   double var=sq/sv - vw*vw;
   if(var<0) var=0;
   double sd=MathSqrt(var);
   if(sd<=1e-8) return 0;
   double z=(iClose(_Symbol,PERIOD_M1,1)-vw)/sd;
   if(z>6) z=6;
   if(z<-6) z=-6;
   return z;
}

double BBz()
{
   double mid[2], sd[2];
   if(CopyBuffer(g_bb_mid,0,1,1,mid)<1) return 0;
   if(CopyBuffer(g_bb_sd,0,1,1,sd)<1) return 0;
   if(sd[0]<=1e-8) return 0;
   double c1=iClose(_Symbol,PERIOD_M1,1);
   double z=(c1-mid[0])/sd[0];
   if(z>6) z=6;
   if(z<-6) z=-6;
   return z;
}

double RegATR()
{
   // a15 / trung vi a15 5 ngay (~480 nen M15)
   double a[];
   int n=480;
   ArraySetAsSeries(a,true);
   if(CopyBuffer(g_atr15,0,1,n,a)<n) return 1;
   double med=Median(a,n);
   if(med<=0) return 1;
   return a[0]/med;
}

int DiemS(const int hu)
{
   double bb=BBz();
   double vw=VwapZ();
   double rg=RegATR();
   datetime t1=iTime(_Symbol,PERIOD_M1,1);
   bool uso=UsOpenBar(t1);
   int s=0;
   if(hu>0)
   {
      if(bb<-2) s++;
      if(RejM5(1)) s++;
      if(uso) s++;
      if(rg<0.8) s++;
      if(vw<-2) s--;
   }
   else
   {
      if(bb>2) s++;
      if(RejM5(-1)) s++;
      if(uso) s++;
      if(rg<0.8) s++;
      if(vw>2) s--;
   }
   return s;
}

int TinHieu()
{
   datetime t0=iTime(_Symbol,PERIOD_M1,0);
   if(!PhienLU(t0)) return 0;
   int sl=DiemS(1);
   int ss=DiemS(-1);
   if(sl>=1) return 1;
   if(ss>=1) return -1;
   return 0;
}

bool LaLenhTa(const ulong tk)
{
   if(tk==0 || !PositionSelectByTicket(tk)) return false;
   return (PositionGetString(POSITION_SYMBOL)==_Symbol &&
           PositionGetInteger(POSITION_MAGIC)==InpMagic);
}

void DongBoVe()
{
   // loai ticket da dong; neu mat het, quet lai theo magic
   int nm=0, nh=0;
   for(int i=0;i<g_nm;i++)
      if(LaLenhTa(g_mains[i])) g_mains[nm++]=g_mains[i];
   g_nm=nm;
   for(int i=0;i<g_nh;i++)
      if(LaLenhTa(g_hedges[i])) g_hedges[nh++]=g_hedges[i];
   g_nh=nh;
   if(g_nm+g_nh>0) return;
   // quet toan bo (phuc hoi)
   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong tk=PositionGetTicket(i);
      if(!LaLenhTa(tk)) continue;
      string cmt=PositionGetString(POSITION_COMMENT);
      int typ=(int)PositionGetInteger(POSITION_TYPE);
      if(StringFind(cmt,"T2_H")>=0)
      {
         if(g_nh<32) g_hedges[g_nh++]=tk;
      }
      else
      {
         if(g_nm<64) g_mains[g_nm++]=tk;
         g_main_s = (typ==POSITION_TYPE_BUY ? 1 : -1);
         g_last_main = PositionGetDouble(POSITION_PRICE_OPEN);
      }
   }
}

double TongLoiThe()
{
   double s=0;
   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong tk=PositionGetTicket(i);
      if(!LaLenhTa(tk)) continue;
      s += PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP);
   }
   return s;
}

double TongLotMain()
{
   double v=0;
   for(int i=0;i<g_nm;i++)
   {
      if(!LaLenhTa(g_mains[i])) continue;
      v += PositionGetDouble(POSITION_VOLUME);
   }
   return v;
}

double MidMain()
{
   double s=0,v=0;
   for(int i=0;i<g_nm;i++)
   {
      if(!LaLenhTa(g_mains[i])) continue;
      double vi=PositionGetDouble(POSITION_VOLUME);
      s += PositionGetDouble(POSITION_PRICE_OPEN)*vi;
      v += vi;
   }
   if(v<=0) return 0;
   return s/v;
}

void DongHet()
{
   DatKieuKhop();
   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong tk=PositionGetTicket(i);
      if(!LaLenhTa(tk)) continue;
      trade.PositionClose(tk);
   }
   g_nm=0; g_nh=0;
   g_hedged=false;
   g_last_main=0;
   g_main_s=0;
   g_open_bar=0;
   g_realized=0;
}

bool MoLenh(const int hu, const double lot, const string cmt, const double tp_gia, ulong &tk)
{
   DatKieuKhop();
   double lots=ChuanLot(lot);
   if(lots<=0) return false;
   double ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
   double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID);
   double sl=0, tp=0;
   if(hu>0) tp=tp_gia;
   else     tp=tp_gia;
   // chuan tp theo dung
   int dig=(int)SymbolInfoInteger(_Symbol,SYMBOL_DIGITS);
   tp=NormalizeDouble(tp,dig);
   bool ok=false;
   if(hu>0) ok=trade.Buy(lots,_Symbol,ask,sl,tp,cmt);
   else     ok=trade.Sell(lots,_Symbol,bid,sl,tp,cmt);
   if(!ok) return false;
   ulong deal=trade.ResultDeal();
   if(deal>0 && HistoryDealSelect(deal))
   {
      tk=(ulong)HistoryDealGetInteger(deal,DEAL_POSITION_ID);
      if(tk>0) return true;
   }
   datetime moi=0; tk=0;
   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong t=PositionGetTicket(i);
      if(!LaLenhTa(t)) continue;
      datetime tm=(datetime)PositionGetInteger(POSITION_TIME);
      if(tm>=moi){ moi=tm; tk=t; }
   }
   return (tk>0);
}

int SlopeHienTai()
{
   int slope=0;
   double e[];
   ArraySetAsSeries(e,true);
   int need=InpSlopeBars+2;
   if(CopyBuffer(g_ema,0,1,need,e)>=need)
   {
      double slp=e[0]-e[InpSlopeBars];
      if(slp>0) slope=1;
      else if(slp<0) slope=-1;
   }
   double o=iOpen(_Symbol,PERIOD_D1,1);
   double h=iHigh(_Symbol,PERIOD_D1,1);
   double l=iLow(_Symbol,PERIOD_D1,1);
   double c=iClose(_Symbol,PERIOD_D1,1);
   double rng=h-l;
   if(rng>0)
   {
      double ow=(c-o)/rng;
      if(MathAbs(ow)>=InpD1OneWay)
         slope = (ow>0 ? 1 : -1);
   }
   return slope;
}

double AdxDong()
{
   double adx[];
   ArraySetAsSeries(adx,true);
   if(CopyBuffer(g_adx,0,1,1,adx)<1) return 0;
   return adx[0];
}

bool RegimeNguoc()
{
   int slope=SlopeHienTai();
   if(InpDcaMode>=1)
   {
      if(slope==0 || g_main_s==0) return true; // khong DCA khi khong ro slope
      return (slope*g_main_s <= 0);
   }
   if(InpADXTh<=0) return false;
   if(AdxDong()<InpADXTh) return false;
   if(slope==0 || g_main_s==0) return false;
   return (slope*g_main_s < 0);
}

void SauLossClose()
{
   g_n_lc++;
   if(InpCooldown>g_cool_left) g_cool_left=InpCooldown;
   if(InpMaxLc<=0) return;
   if(InpLcPeriod>0)
   {
      if(g_lc_win_i0<0 || (g_bar_i-g_lc_win_i0)>=InpLcPeriod)
      {
         g_lc_win_i0=g_bar_i;
         g_n_lc_win=0;
      }
      g_n_lc_win++;
      if(g_n_lc_win>=InpMaxLc)
      {
         int pause=(InpLcPause>0 ? InpLcPause : InpLcPeriod);
         if(pause>g_cool_left) g_cool_left=pause;
         g_n_lc_win=0;
         g_lc_win_i0=g_bar_i;
      }
   }
   else if(g_n_lc>=InpMaxLc)
      g_halt=true;
}

void CapNhatNgayTuan(const datetime t0)
{
   int key=DayKeyVN(t0);
   double eq=AccountInfoDouble(ACCOUNT_EQUITY);
   if(eq<1) eq=1;
   if(g_day_key==0)
   {
      g_day_key=key;
      g_day_eq0=eq;
      g_week_eq0=eq;
      g_n_day=0;
   }
   else if(key!=g_day_key)
   {
      g_day_key=key;
      g_day_eq0=eq;
      g_day_stop=false;
      g_n_day++;
      if(g_n_day>=5)
      {
         g_n_day=0;
         g_week_eq0=eq;
         g_week_stop=false;
      }
   }
   if(InpDayLoss>0 && (eq-g_day_eq0) <= -InpDayLoss*g_day_eq0)
      g_day_stop=true;
   if(InpWeekLoss>0 && (eq-g_week_eq0) <= -InpWeekLoss*g_week_eq0)
      g_week_stop=true;
}

double TyLeVon()
{
   if(InpEqLot<=0 || g_eq0<=0) return 1.0;
   double sc=AccountInfoDouble(ACCOUNT_BALANCE)/g_eq0;
   if(sc<0) sc=0;
   if(sc>1) sc=1;
   return sc;
}

int MaxLHienTai()
{
   int ml=InpMaxL;
   if(InpEqLot<=0) return ml;
   ml=(int)MathRound(InpMaxL*TyLeVon());
   if(ml<1) ml=1;
   return ml;
}

void XuLyGioRo()
{
   if(g_nm+g_nh<=0) return;
   double fl=TongLoiThe();
   double tong=g_realized+fl;
   // lo tong: dong ca ro, khong SL tung lenh
   if(InpLossClose>0 && tong <= -InpLossClose*g_eq_open)
   {
      DongHet();
      SauLossClose();
      return;
   }
   // dong ro khi lai tong > 0
   if(tong>0)
   {
      DongHet();
      return;
   }

   if(g_nm<=0)
   {
      if(InpFlatOrphan!=0 && g_nh>0)
         DongHet();
      return;
   }

   double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID);
   double ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
   double px  = (g_main_s>0 ? bid : ask);

   // flcap: dung DCA moi (equity luc mo nen hoac hien tai)
   bool cap_ok=true;
   if(InpFlCap>0 && fl<0)
   {
      double eqref=MathMax(g_eq_bar, 1.0);
      if((-fl) >= InpFlCap*eqref) cap_ok=false;
   }
   bool regime_ok = !RegimeNguoc();
   if(g_day_stop || g_week_stop) regime_ok=false;
   int maxL_i=MaxLHienTai();

   if(cap_ok && regime_ok && InpGap>0 && g_nm<maxL_i)
   {
      int guard=0;
      while(g_nm<maxL_i && guard<40)
      {
         guard++;
         if(InpShortCap>0 && g_main_s<0 && (TongLotMain()+InpL0)>InpShortCap+1e-12)
            break;
         double nxt = g_last_main - g_main_s*InpGap;
         bool hit = (g_main_s>0) ? (bid<=nxt) : (ask>=nxt);
         if(!hit) break;
         double fill_ref = nxt; // TP tinh tu gia vao thuc te
         ulong tk=0;
         double tp = (g_main_s>0 ? fill_ref+InpTP : fill_ref-InpTP);
         if(!MoLenh(g_main_s, InpL0, "T2_DCA", tp, tk))
            break;
         if(LaLenhTa(tk))
            g_last_main=PositionGetDouble(POSITION_PRICE_OPEN);
         else
            g_last_main=nxt;
         if(g_nm<64) g_mains[g_nm++]=tk;
      }
   }

   // hedge mot lan khi lech >= hgap tu trung binh gia main
   if(!g_hedged && InpHGap>0 && InpHFrac>0 && g_nh==0)
   {
      double midm=MidMain();
      double far = (midm-px)*g_main_s;
      if(far>=InpHGap)
      {
         double vm=TongLotMain();
         double htot=InpHFrac*vm;
         double lot0=InpL0;
         if(lot0<=0) lot0=0.01;
         int batch=(int)MathRound(htot/lot0);
         if(batch<1) batch=1;
         if(batch>InpMaxH) batch=InpMaxH;
         double h_each=htot/batch;
         int hsides=-g_main_s;
         double lv=midm-g_main_s*InpHGap;
         for(int b=0;b<batch;b++)
         {
            ulong tk=0;
            double tp=(hsides>0 ? lv+InpTP : lv-InpTP);
            if(!MoLenh(hsides, h_each, "T2_HEDGE", tp, tk))
               break;
            if(g_nh<32) g_hedges[g_nh++]=tk;
         }
         g_hedged=true;
      }
   }
}

void OnTick()
{
   DatKieuKhop();
   long spread_pts=SymbolInfoInteger(_Symbol,SYMBOL_SPREAD);
   if(spread_pts>InpMaxSpreadPts) return;

   DongBoVe();
   if(InpFlatOrphan!=0 && g_nm==0 && g_nh>0)
      DongHet();
   if(g_nm+g_nh>0)
      XuLyGioRo();

   datetime t0=iTime(_Symbol,PERIOD_M1,0);
   if(t0==0 || t0==g_bar) return;
   g_bar=t0;
   g_bar_i++;
   g_eq_bar=AccountInfoDouble(ACCOUNT_EQUITY);
   if(g_cool_left>0) g_cool_left--;
   CapNhatNgayTuan(t0);

   DongBoVe();
   if(InpFlatOrphan!=0 && g_nm==0 && g_nh>0)
      DongHet();
   if(g_nm+g_nh>0) return;
   if(g_halt) return;
   if(g_cool_left>0) return;
   if(g_day_stop || g_week_stop) return;
   if(Bars(_Symbol,PERIOD_M1)<300) return;

   int sig=TinHieu();
   if(sig==0) return;
   if(InpDcaMode>=2)
   {
      int slp=SlopeHienTai();
      if(slp==0 || slp*sig<0) return;
   }

   double ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
   double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID);
   double px=(sig>0?ask:bid);
   g_eq_open=AccountInfoDouble(ACCOUNT_EQUITY);
   if(g_eq_open<1) g_eq_open=1;
   g_realized=0;
   g_nm=0; g_nh=0;
   g_hedged=false;
   g_main_s=sig;
   g_open_bar=t0;
   double sc=TyLeVon();
   int kk=InpK;
   if(InpEqLot>0)
   {
      kk=(int)MathRound(InpK*sc);
      if(kk<1) kk=(sc>=0.25 ? 1 : 0);
   }
   if(kk<1) return;
   g_k_init=kk;
   if(InpShortCap>0 && sig<0)
   {
      int capn = (InpL0>0 ? (int)MathFloor(InpShortCap/InpL0+1e-12) : 0);
      if(capn<1) return;
      if(kk>capn) kk=capn;
   }
   for(int j=0;j<kk;j++)
   {
      ulong tk=0;
      double tp=(sig>0?px+InpTP:px-InpTP);
      if(!MoLenh(sig, InpL0, "T2_MAIN", tp, tk))
         break;
      if(g_nm<64) g_mains[g_nm++]=tk;
      if(LaLenhTa(tk))
         g_last_main=PositionGetDouble(POSITION_PRICE_OPEN);
      else
         g_last_main=px;
   }
}
//+------------------------------------------------------------------+
