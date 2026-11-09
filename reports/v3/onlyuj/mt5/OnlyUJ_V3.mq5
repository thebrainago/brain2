// OnlyUJ_V3 - V3 09/11/2026 (CHI slot g12). Luat tai tao OnlyUJ (MQL5 2245675): range Asia H1 gio 0-7 cung ngay (gio server),
// tu gio 8: gia vuot dinh -> MUA, thung day -> BAN (cai nao truoc), 1 lenh/ngay, 1 vi the 1 luc. SL = 1.00*slm, TP = 1.50*tpm (JPY).
// Lot theo rui ro: InpRisk % equity tai SL. Giu toi da 30 ngay. Lich slm/tpm theo nam = v1_onlyuj_by_year.json (train nam truoc).
#include <Trade/Trade.mqh>
input double InpSL      = 1.00;
input double InpTP      = 1.50;
input double InpRisk    = 1.0;
input int    InpAsiaTu  = 0;
input int    InpAsiaDen = 7;
input int    InpGioVao  = 8;
input int    InpGioHet  = 23;
input int    InpGiuNgay = 30;
input bool   InpDungLich = true;
input double InpSlm     = 0.75;
input double InpTpm     = 1.0;
input long   InpMagic   = 2026110901;
CTrade tr;
int    NAM[]  = {2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025,2026};
double SLM[]  = {0.75,0.75,0.75,0.75,0.75,0.75,0.75,0.75,0.75,0.75,0.75,1.25,0.75,1.25,0.75,0.75,0.75,0.75};
double TPM[]  = {1.0 ,1.5 ,0.75,0.75,0.75,1.25,0.75,0.75,1.25,0.75,0.75,1.0 ,0.75,0.75,0.75,0.75,1.25,0.75};
datetime g_ngay=0, g_da_vao=0; double g_hi=0, g_lo=0; bool g_ok=false;
int g_n=0, g_het=0, g_bo_lot=0;
void LayLich(int y,double &slm,double &tpm){ slm=InpSlm; tpm=InpTpm; if(!InpDungLich) return; for(int i=0;i<ArraySize(NAM);i++) if(NAM[i]==y){slm=SLM[i];tpm=TPM[i];return;} }
bool CoViThe(ulong &tk, datetime &t0){ for(int i=PositionsTotal()-1;i>=0;i--){ ulong t=PositionGetTicket(i); if(PositionGetString(POSITION_SYMBOL)==_Symbol && PositionGetInteger(POSITION_MAGIC)==InpMagic){tk=t;t0=(datetime)PositionGetInteger(POSITION_TIME);return true;} } return false; }
double Lot(int chieu,double gia,double sl)
{
   double eq=AccountInfoDouble(ACCOUNT_EQUITY), rui=eq*InpRisk/100.0, lo1=0;
   if(!OrderCalcProfit(chieu>0?ORDER_TYPE_BUY:ORDER_TYPE_SELL,_Symbol,1.0,gia,sl,lo1) || lo1>=0) return 0;
   double v=rui/(-lo1), st=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP), mn=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN), mx=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MAX);
   v=MathFloor(v/st+1e-9)*st; if(v<mn) { g_bo_lot++; return 0; } if(v>mx) v=mx; return v;
}
int OnInit(){ tr.SetExpertMagicNumber(InpMagic); tr.SetDeviationInPoints(50); return INIT_SUCCEEDED; }
void OnTick()
{
   datetime now=TimeCurrent(); MqlDateTime m; TimeToStruct(now,m);
   datetime ngay=now-(now%86400);
   ulong tk; datetime t0;
   if(CoViThe(tk,t0)) { if(now-t0>=(long)InpGiuNgay*86400) { if(tr.PositionClose(tk)) g_het++; } return; }
   if(ngay!=g_ngay) { g_ngay=ngay; g_ok=false; }
   if(m.hour<InpGioVao || m.hour>InpGioHet || g_da_vao==ngay) return;
   if(!g_ok)
   {
      MqlRates r[]; int k=CopyRates(_Symbol,PERIOD_H1,ngay+InpAsiaTu*3600,ngay+InpAsiaDen*3600,r);
      if(k<=0) return;
      g_hi=-1; g_lo=1e18; int c=0;
      for(int i=0;i<k;i++){ MqlDateTime b; TimeToStruct(r[i].time,b); if(r[i].time<ngay || b.hour<InpAsiaTu || b.hour>InpAsiaDen) continue; g_hi=MathMax(g_hi,r[i].high); g_lo=MathMin(g_lo,r[i].low); c++; }
      if(c<4) { g_da_vao=ngay; return; }    // thieu nen Asia (dau tuan / nghi le) -> bo ngay
      g_ok=true;
   }
   double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID), ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
   double slm,tpm; LayLich(m.year,slm,tpm);
   int chieu=0; if(ask>g_hi) chieu=1; else if(bid<g_lo) chieu=-1;
   if(chieu==0) return;
   double gia=chieu>0?ask:bid, sl=gia-chieu*InpSL*slm, tp=gia+chieu*InpTP*tpm;
   double v=Lot(chieu,gia,sl); g_da_vao=ngay;
   if(v<=0) return;
   bool ok=chieu>0?tr.Buy(v,_Symbol,0,sl,tp,"UJ"):tr.Sell(v,_Symbol,0,sl,tp,"UJ");
   if(ok) g_n++;
}
void OnDeinit(const int r){ PrintFormat("OnlyUJ_V3 %s so_lenh=%d het_gio=%d bo_lot=%d",_Symbol,g_n,g_het,g_bo_lot); }
