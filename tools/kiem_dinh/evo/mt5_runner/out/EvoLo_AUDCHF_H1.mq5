//+------------------------------------------------------------------+
//| EvoLo_AUDCHF_H1 - SINH TU DONG boi nhan/dich_mq5.py. KHONG SUA TAY.
//| 9 co che tu config/co_che_dsl.json, chon bang InpMaCoChe.
//|
//| Gop nhieu co che vao MOT EA co chu dich: mot luot tester ton ~138 giay
//| ma bai test that chi 0,5 giay - phan con lai la boot terminal. Chay
//| OPTIMIZATION tren InpMaCoChe thi N co che ton bang MOT lan boot.
//+------------------------------------------------------------------+
#property copyright "The Brain"
#include <Trade\Trade.mqh>

input int    InpMaCoChe = 0;      // ma co che (0..8)

//--- DICH TIN HIEU o RUNTIME, khong phai luc sinh ma.
//---
//--- Do 06/09: mot luot tester ton ~130 giay BOOT + gan nhu 0 giay tinh (20 nhan
//--- chay song song; 393 pass ton dung bang 1 pass). Nen them pass la MIEN PHI,
//--- con them LAN CHAY thi dat. Sinh 101 ban dich thanh 101 co che rieng lam ma
//--- nguon phinh 10 lan va bien dich cham; de `InpDich` thanh THAM SO TOI UU HOA
//--- thi EA giu nguyen kich thuoc va ta quet duoc co_che x do_dich trong MOT
//--- luot. 40 co che x 26 do dich = 1.040 pass, van la mot lan boot.
input int    InpDich    = 0;      // dich dieu kien di N nen (placebo)
input double InpLot     = 0.10;
input long   InpMagic   = 26090601;
//--- 15/11/2026 (Evo): gio server KHONG khop lenh. Gio 0 = dao ngay (rollover),
//--- spread XM vot 4-8 pip; truoc day EA D1/H4 vao/ra dung 00:00. -1 = tat.
input int    InpGioTranh = 0;
//--- Ngoai tester: tu choi chay neu tai khoan KHONG phai DEMO.
input bool   InpChiDemo  = true;

#define KHUNG PERIOD_H1

int h_ma0 = INVALID_HANDLE;
int h_ma1 = INVALID_HANDLE;
int h_ma2 = INVALID_HANDLE;
int h_ma3 = INVALID_HANDLE;
int h_atr0 = INVALID_HANDLE;

CTrade   trade;
datetime g_nen_cuoi = 0;
int      g_bar_vao  = 0;
int      g_y_dinh   = 0;          // 0 khong, 1 mo, -1 dong

double Chi(int h, int s)
  {
   return(ChiB(h, 0, s));
  }

// Doc mot BUFFER bat ky. ADX co ba duong (0 = ADX, 1 = +DI, 2 = -DI); truoc
// 15/09/2026 chi co ban doc buffer 0, nen moi chi bao NHIEU DUONG deu khong
// dich duoc va 34 co che dung ADX chua bao gio ra toi tester.
double ChiB(int h, int buf, int s)
  {
   if(h == INVALID_HANDLE) return(0.0);
   double b[];
   if(CopyBuffer(h, buf, s, 1, b) != 1) return(0.0);
   return(b[0]);
  }

double F1(int s)
  {
   return(iHigh(_Symbol, KHUNG, s+0));
  }

double F2(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F3(int s)
  {
   return(iHigh(_Symbol, KHUNG, s+0));
  }

double F4(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F5(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F6(int s)
  {
   return(Chi(h_ma0, s));
  }

double F7(int s)
  {
   return(Chi(h_atr0, s));
  }

double F8(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F7(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F9(int s)
  {
   return(0.3);
  }

double F10(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F11(int s)
  {
   double a = F10(s+20);
   if(a == 0.0) return(0.0);
   return((F10(s) - a) / a);
  }

double F12(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F11(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F13(int s)
  {
   return(0.7);
  }

double F14(int s)
  {
   return(Chi(h_atr0, s));
  }

double F15(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F14(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F16(int s)
  {
   return(0.7);
  }

double F17(int s)
  {
   MqlDateTime d; TimeToStruct(iTime(_Symbol,KHUNG,s), d);
   return((double)d.day);
  }

double F18(int s)
  {
   return(27);
  }

double F19(int s)
  {
   return(Chi(h_atr0, s));
  }

double F20(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F19(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F21(int s)
  {
   return(0.6);
  }

double F22(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F23(int s)
  {
   double v[]; ArrayResize(v, 50);
   for(int i = 0; i < 50; i++) v[i] = F22(s+i);
   double t=0; for(int i=0;i<50;i++) t+=v[i]; double m=t/50.0;
   double q=0; for(int i=0;i<50;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/50.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F24(int s)
  {
   return(1);
  }

double F25(int s)
  {
   return(iHigh(_Symbol,KHUNG,s) - iLow(_Symbol,KHUNG,s));
  }

double F26(int s)
  {
   double v[]; ArrayResize(v, 50);
   for(int i = 0; i < 50; i++) v[i] = F25(s+i);
   int d = 0; for(int i=1;i<50;i++) if(v[i] <= v[0]) d++;
   return((double)d / 49.0);
  }

double F27(int s)
  {
   return(0.4);
  }

double F28(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F29(int s)
  {
   return(Chi(h_ma1, s));
  }

double F30(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F31(int s)
  {
   return(Chi(h_ma0, s));
  }

double F32(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F33(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F34(int s)
  {
   return(F33(s+1));
  }

double F35(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F36(int s)
  {
   return(F35(s+1));
  }

double F37(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F38(int s)
  {
   return(F37(s+2));
  }

double F39(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F40(int s)
  {
   return(F39(s+2));
  }

double F41(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F42(int s)
  {
   return(F41(s+3));
  }

double F43(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F44(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F43(s+i);
   int d = 0; for(int i=1;i<20;i++) if(v[i] <= v[0]) d++;
   return((double)d / 19.0);
  }

double F45(int s)
  {
   return(0.15);
  }

double F46(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F47(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F46(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F48(int s)
  {
   return(0.35);
  }

double F49(int s)
  {
   return(Chi(h_ma2, s));
  }

double F50(int s)
  {
   double a = F49(s+10);
   if(a == 0.0) return(0.0);
   return((F49(s) - a) / a);
  }

double F51(int s)
  {
   return(MathAbs(F50(s)));
  }

double F52(int s)
  {
   double v[]; ArrayResize(v, 500);
   for(int i = 0; i < 500; i++) v[i] = F51(s+i);
   int d = 0; for(int i=1;i<500;i++) if(v[i] <= v[0]) d++;
   return((double)d / 499.0);
  }

double F53(int s)
  {
   return(0.3);
  }

double F54(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F55(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F54(s+i);
   int d = 0; for(int i=1;i<20;i++) if(v[i] <= v[0]) d++;
   return((double)d / 19.0);
  }

double F56(int s)
  {
   return(0.5);
  }

double F57(int s)
  {
   return(Chi(h_atr0, s));
  }

double F58(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F57(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F59(int s)
  {
   return(F58(s+5));
  }

double F60(int s)
  {
   return(0.85);
  }

double F61(int s)
  {
   return(Chi(h_atr0, s));
  }

double F62(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F61(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F63(int s)
  {
   return(0.6);
  }

double F64(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F65(int s)
  {
   return(0.4);
  }

double F66(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F67(int s)
  {
   return(Chi(h_ma3, s));
  }

double F68(int s)
  {
   MqlDateTime d; TimeToStruct(iTime(_Symbol,KHUNG,s), d);
   return((double)d.day_of_week);
  }

double F69(int s)
  {
   return(0);
  }

double F70(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F71(int s)
  {
   double a = F70(s+30);
   if(a == 0.0) return(0.0);
   return((F70(s) - a) / a);
  }

double F72(int s)
  {
   return(0);
  }

double F73(int s)
  {
   return(Chi(h_atr0, s));
  }

double F74(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F73(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F75(int s)
  {
   return(0.5);
  }

double F76(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F77(int s)
  {
   double v[]; ArrayResize(v, 50);
   for(int i = 0; i < 50; i++) v[i] = F76(s+i);
   double t=0; for(int i=0;i<50;i++) t+=v[i]; double m=t/50.0;
   double q=0; for(int i=0;i<50;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/50.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F78(int s)
  {
   return(-1.5);
  }

double F79(int s)
  {
   return(Chi(h_atr0, s));
  }

double F80(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F79(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F81(int s)
  {
   return(0.5);
  }

double F82(int s)
  {
   return(Chi(h_atr0, s));
  }

double F83(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F82(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F84(int s)
  {
   return(F83(s+15));
  }

double F85(int s)
  {
   return(0.8);
  }

double F86(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F87(int s)
  {
   return(Chi(h_ma2, s));
  }


//--- vao/ra cua tung co che
bool VAO0(int s) { return((F1(s) >= F2(s))); }
bool RA0(int s)  { return(false); }
bool VAO1(int s) { return((F3(s) >= F4(s))); }
bool RA1(int s)  { return(false); }
bool VAO2(int s) { return((F5(s) > F6(s)) && (F8(s) < F9(s)) && (F12(s) > F13(s))); }
bool RA2(int s)  { return((F15(s) > F16(s))); }
bool VAO3(int s) { return((F17(s) >= F18(s)) && (F20(s) < F21(s))); }
bool RA3(int s)  { return(false); }
bool VAO4(int s) { return((F23(s) > F24(s)) && (F26(s) < F27(s)) && (F28(s) > F29(s)) && (F30(s) < F31(s))); }
bool RA4(int s)  { return(false); }
bool VAO5(int s) { return((F32(s) < F34(s)) && (F36(s) < F38(s)) && (F40(s) < F42(s)) && (F44(s) < F45(s)) && (F47(s) < F48(s)) && (F52(s) < F53(s))); }
bool RA5(int s)  { return((F55(s) > F56(s))); }
bool VAO6(int s) { return((F59(s) > F60(s)) && (F62(s) < F63(s)) && (F64(s) < F65(s)) && (F66(s) > F67(s))); }
bool RA6(int s)  { return(false); }
bool VAO7(int s) { return((F68(s) <= F69(s)) && (F71(s) < F72(s)) && (F74(s) < F75(s))); }
bool RA7(int s)  { return(false); }
bool VAO8(int s) { return((F77(s) < F78(s)) && (F80(s) < F81(s)) && (F84(s) > F85(s))); }
bool RA8(int s)  { return((F86(s) > F87(s))); }

bool CoVao(int k, int s)
  {
   switch(k)
     {
      case 0: return(VAO0(s));
      case 1: return(VAO1(s));
      case 2: return(VAO2(s));
      case 3: return(VAO3(s));
      case 4: return(VAO4(s));
      case 5: return(VAO5(s));
      case 6: return(VAO6(s));
      case 7: return(VAO7(s));
      case 8: return(VAO8(s));
     }
   return(false);
  }

bool CoRa(int k, int s)
  {
   switch(k)
     {
      case 0: return(RA0(s));
      case 1: return(RA1(s));
      case 2: return(RA2(s));
      case 3: return(RA3(s));
      case 4: return(RA4(s));
      case 5: return(RA5(s));
      case 6: return(RA6(s));
      case 7: return(RA7(s));
      case 8: return(RA8(s));
     }
   return(false);
  }

int Chieu(int k) { switch(k) { case 0: return(1); case 1: return(-1); case 2: return(1); case 3: return(1); case 4: return(-1); case 5: return(1); case 6: return(1); case 7: return(1); case 8: return(1); } return(1); }
int Giu(int k)   { switch(k) { case 0: return(500); case 1: return(500); case 2: return(10); case 3: return(5); case 4: return(5); case 5: return(5); case 6: return(10); case 7: return(6); case 8: return(8); } return(1); }
bool CoDieuKienRa(int k) { switch(k) { case 0: return(false); case 1: return(false); case 2: return(true); case 3: return(false); case 4: return(false); case 5: return(true); case 6: return(false); case 7: return(false); case 8: return(true); } return(false); }

//+------------------------------------------------------------------+
int OnInit()
  {
   if(InpChiDemo && !MQLInfoInteger(MQL_TESTER) &&
      (ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE) != ACCOUNT_TRADE_MODE_DEMO)
     {
      Print("Tu choi: tai khoan khong phai DEMO");
      return(INIT_FAILED);
     }
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetTypeFillingBySymbol(_Symbol);
   // Khoi dong lai terminal giua chung: dem lai so nen da giu tu gio mo lenh,
   // neu khong lenh giu-N-nen se khong bao gio dong theo thoi gian.
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol &&
         PositionGetInteger(POSITION_MAGIC) == InpMagic)
        {
         int sh = iBarShift(_Symbol, KHUNG, (datetime)PositionGetInteger(POSITION_TIME), false);
         if(sh > 0) g_bar_vao = sh;
        }
     }
   // Khong hanh dong giua nen luc vua gan EA / khoi dong lai.
   g_nen_cuoi = (datetime)SeriesInfoInteger(_Symbol, KHUNG, SERIES_LASTBAR_DATE);
   h_ma0 = iMA(_Symbol, KHUNG, 200, 0, MODE_SMA, PRICE_CLOSE);
   h_ma1 = iMA(_Symbol, KHUNG, 20, 0, MODE_SMA, PRICE_CLOSE);
   h_ma2 = iMA(_Symbol, KHUNG, 50, 0, MODE_SMA, PRICE_CLOSE);
   h_ma3 = iMA(_Symbol, KHUNG, 100, 0, MODE_SMA, PRICE_CLOSE);
   h_atr0 = iATR(_Symbol, KHUNG, 14);
   return(INIT_SUCCEEDED);
  }

bool DangMo()
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol &&
         PositionGetInteger(POSITION_MAGIC) == InpMagic) return(true);
     }
   return(false);
  }

void DongHet()
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol &&
         PositionGetInteger(POSITION_MAGIC) == InpMagic) trade.PositionClose(tk);
     }
  }

//--- Khop y dinh o nen dau tien CO THE giao dich.
//--- Nen cua khung tin hieu doi luc 00:00, ma 00:00 nam NGOAI phien cua CFD chi
//--- so -> hanh dong ngay tai do thi moi lenh tra "Market closed" va bao cao ghi
//--- 0 lenh, doc y het mot he khong bao gio vao lenh.
void KhopYDinh()
  {
   if(g_y_dinh == 0) return;
   if(InpGioTranh >= 0)
     {
      MqlDateTime dt; TimeToStruct(TimeCurrent(), dt);
      if(dt.hour == InpGioTranh) return;
     }
   if((ENUM_SYMBOL_TRADE_MODE)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE)
      != SYMBOL_TRADE_MODE_FULL) return;
   if(g_y_dinh < 0)
     {
      if(!DangMo()) { g_y_dinh = 0; return; }
      DongHet();
      if(!DangMo()) { g_bar_vao = 0; g_y_dinh = 0; }
      return;
     }
   if(DangMo()) { g_y_dinh = 0; return; }
   bool ok = (Chieu(InpMaCoChe) > 0) ? trade.Buy(InpLot, _Symbol)
                                     : trade.Sell(InpLot, _Symbol);
   if(ok) { g_bar_vao = 0; g_y_dinh = 0; }
  }

void OnTick()
  {
   KhopYDinh();

   datetime t = (datetime)SeriesInfoInteger(_Symbol, KHUNG, SERIES_LASTBAR_DATE);
   if(t == g_nen_cuoi) return;
   g_nen_cuoi = t;

   int k = InpMaCoChe;
   if(DangMo())
     {
      g_bar_vao++;
      bool ra = CoDieuKienRa(k) ? CoRa(k, 1 + InpDich) : (g_bar_vao >= Giu(k));
      g_y_dinh = (ra || g_bar_vao >= 500) ? -1 : 0;
     }
   else
      g_y_dinh = CoVao(k, 1 + InpDich) ? 1 : 0;
  }
//+------------------------------------------------------------------+
