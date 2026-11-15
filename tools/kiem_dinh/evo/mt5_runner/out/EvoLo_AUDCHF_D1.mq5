//+------------------------------------------------------------------+
//| EvoLo_AUDCHF_D1 - SINH TU DONG boi nhan/dich_mq5.py. KHONG SUA TAY.
//| 11 co che tu config/co_che_dsl.json, chon bang InpMaCoChe.
//|
//| Gop nhieu co che vao MOT EA co chu dich: mot luot tester ton ~138 giay
//| ma bai test that chi 0,5 giay - phan con lai la boot terminal. Chay
//| OPTIMIZATION tren InpMaCoChe thi N co che ton bang MOT lan boot.
//+------------------------------------------------------------------+
#property copyright "The Brain"
#include <Trade\Trade.mqh>

input int    InpMaCoChe = 0;      // ma co che (0..10)

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

#define KHUNG PERIOD_D1

int h_ma0 = INVALID_HANDLE;
int h_ma1 = INVALID_HANDLE;
int h_ma2 = INVALID_HANDLE;
int h_ma3 = INVALID_HANDLE;
int h_ma4 = INVALID_HANDLE;
int h_rsi0 = INVALID_HANDLE;
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
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F6(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F7(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F6(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]<m) m=v[i];
   return(m);
  }

double F8(int s)
  {
   return(F7(s+1));
  }

double F9(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F10(int s)
  {
   return(0.65);
  }

double F11(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F12(int s)
  {
   return(Chi(h_ma0, s));
  }

double F13(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F14(int s)
  {
   return(0.8);
  }

double F15(int s)
  {
   return(Chi(h_atr0, s));
  }

double F16(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F15(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F17(int s)
  {
   return(0.6);
  }

double F18(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F19(int s)
  {
   return(Chi(h_ma1, s));
  }

double F20(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F21(int s)
  {
   return(0.2);
  }

double F22(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F23(int s)
  {
   double a = F22(s+3);
   if(a == 0.0) return(0.0);
   return((F22(s) - a) / a);
  }

double F24(int s)
  {
   double v[]; ArrayResize(v, 500);
   for(int i = 0; i < 500; i++) v[i] = F23(s+i);
   int d = 0; for(int i=1;i<500;i++) if(v[i] <= v[0]) d++;
   return((double)d / 499.0);
  }

double F25(int s)
  {
   return(0.1);
  }

double F26(int s)
  {
   return(iHigh(_Symbol,KHUNG,s) - iLow(_Symbol,KHUNG,s));
  }

double F27(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F26(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F28(int s)
  {
   return(0.5);
  }

double F29(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F30(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F31(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F30(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]<m) m=v[i];
   return(m);
  }

double F32(int s)
  {
   return(F31(s+1));
  }

double F33(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F34(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F35(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F34(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]<m) m=v[i];
   return(m);
  }

double F36(int s)
  {
   return(F35(s+1));
  }

double F37(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F38(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F37(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F39(int s)
  {
   return(0.4);
  }

double F40(int s)
  {
   return(Chi(h_atr0, s));
  }

double F41(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F40(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F42(int s)
  {
   return(0.25);
  }

double F43(int s)
  {
   return(Chi(h_atr0, s));
  }

double F44(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F43(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F45(int s)
  {
   return(0.75);
  }

double F46(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F47(int s)
  {
   return(0.7);
  }

double F48(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F49(int s)
  {
   return(Chi(h_ma2, s));
  }

double F50(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F51(int s)
  {
   return(Chi(h_ma2, s));
  }

double F52(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F53(int s)
  {
   double a = F52(s+120);
   if(a == 0.0) return(0.0);
   return((F52(s) - a) / a);
  }

double F54(int s)
  {
   return(0);
  }

double F55(int s)
  {
   return(Chi(h_atr0, s));
  }

double F56(int s)
  {
   double v[]; ArrayResize(v, 200);
   for(int i = 0; i < 200; i++) v[i] = F55(s+i);
   int d = 0; for(int i=1;i<200;i++) if(v[i] <= v[0]) d++;
   return((double)d / 199.0);
  }

double F57(int s)
  {
   return(0.5);
  }

double F58(int s)
  {
   return(iHigh(_Symbol, KHUNG, s+0));
  }

double F59(int s)
  {
   return(iHigh(_Symbol, KHUNG, s+0));
  }

double F60(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F59(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]>m) m=v[i];
   return(m);
  }

double F61(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F62(int s)
  {
   return(0.35);
  }

double F63(int s)
  {
   return(Chi(h_rsi0, s));
  }

double F64(int s)
  {
   double v[]; ArrayResize(v, 200);
   for(int i = 0; i < 200; i++) v[i] = F63(s+i);
   int d = 0; for(int i=1;i<200;i++) if(v[i] <= v[0]) d++;
   return((double)d / 199.0);
  }

double F65(int s)
  {
   return(0.8);
  }

double F66(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F67(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F68(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F67(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]<m) m=v[i];
   return(m);
  }

double F69(int s)
  {
   return(F68(s+1));
  }

double F70(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F71(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F72(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F71(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]<m) m=v[i];
   return(m);
  }

double F73(int s)
  {
   return(F72(s+1));
  }

double F74(int s)
  {
   return(Chi(h_atr0, s));
  }

double F75(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F74(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F76(int s)
  {
   return(0.6);
  }

double F77(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F78(int s)
  {
   return(iHigh(_Symbol, KHUNG, s+0));
  }

double F79(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F78(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]>m) m=v[i];
   return(m);
  }

double F80(int s)
  {
   return(F79(s+1));
  }

double F81(int s)
  {
   return(Chi(h_atr0, s));
  }

double F82(int s)
  {
   double v[]; ArrayResize(v, 200);
   for(int i = 0; i < 200; i++) v[i] = F81(s+i);
   int d = 0; for(int i=1;i<200;i++) if(v[i] <= v[0]) d++;
   return((double)d / 199.0);
  }

double F83(int s)
  {
   return(0.35);
  }

double F84(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F85(int s)
  {
   double v[]; ArrayResize(v, 10);
   for(int i = 0; i < 10; i++) v[i] = F84(s+i);
   double t = 0; for(int i=0;i<10;i++) t += v[i];
   return(t / 10.0);
  }

double F86(int s)
  {
   double v[]; ArrayResize(v, 200);
   for(int i = 0; i < 200; i++) v[i] = F85(s+i);
   int d = 0; for(int i=1;i<200;i++) if(v[i] <= v[0]) d++;
   return((double)d / 199.0);
  }

double F87(int s)
  {
   return(0.5);
  }

double F88(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F89(int s)
  {
   return(Chi(h_ma3, s));
  }

double F90(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F91(int s)
  {
   return(Chi(h_ma4, s));
  }

double F92(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F93(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F92(s+i);
   double t=0; for(int i=0;i<20;i++) t+=v[i]; double m=t/20.0;
   double q=0; for(int i=0;i<20;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/20.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F94(int s)
  {
   return(F93(s+3));
  }

double F95(int s)
  {
   return(-1.2);
  }

double F96(int s)
  {
   return(Chi(h_atr0, s));
  }

double F97(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F96(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F98(int s)
  {
   return(0.4);
  }

double F99(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F100(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F99(s+i);
   double t=0; for(int i=0;i<20;i++) t+=v[i]; double m=t/20.0;
   double q=0; for(int i=0;i<20;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/20.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F101(int s)
  {
   return(1);
  }


//--- vao/ra cua tung co che
bool VAO0(int s) { return((F1(s) >= F2(s))); }
bool RA0(int s)  { return(false); }
bool VAO1(int s) { return((F3(s) >= F4(s))); }
bool RA1(int s)  { return(false); }
bool VAO2(int s) { return((F5(s) < F8(s)) && (F9(s) > F10(s)) && (F11(s) > F12(s))); }
bool RA2(int s)  { return(false); }
bool VAO3(int s) { return((F13(s) > F14(s)) && (F16(s) > F17(s)) && (F18(s) < F19(s))); }
bool RA3(int s)  { return((F20(s) < F21(s))); }
bool VAO4(int s) { return((F24(s) < F25(s)) && (F27(s) < F28(s))); }
bool RA4(int s)  { return(false); }
bool VAO5(int s) { return((F29(s) < F32(s)) && (F33(s) > F36(s)) && (F38(s) < F39(s)) && (F41(s) > F42(s)) && (F44(s) < F45(s))); }
bool RA5(int s)  { return((F46(s) > F47(s))); }
bool VAO6(int s) { return((F48(s) < F49(s)) && (F50(s) > F51(s)) && (F53(s) > F54(s)) && (F56(s) < F57(s))); }
bool RA6(int s)  { return(false); }
bool VAO7(int s) { return((F58(s) >= F60(s)) && (F61(s) < F62(s)) && (F64(s) > F65(s))); }
bool RA7(int s)  { return(false); }
bool VAO8(int s) { return((F66(s) < F69(s)) && (F70(s) > F73(s)) && (F75(s) < F76(s))); }
bool RA8(int s)  { return(false); }
bool VAO9(int s) { return((F77(s) > F80(s)) && (F82(s) < F83(s)) && (F86(s) < F87(s))); }
bool RA9(int s)  { return((F88(s) < F89(s))); }
bool VAO10(int s) { return((F90(s) > F91(s) && F90(s+1) <= F91(s+1)) && (F94(s) < F95(s)) && (F97(s) < F98(s))); }
bool RA10(int s)  { return((F100(s) > F101(s))); }

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
      case 9: return(VAO9(s));
      case 10: return(VAO10(s));
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
      case 9: return(RA9(s));
      case 10: return(RA10(s));
     }
   return(false);
  }

int Chieu(int k) { switch(k) { case 0: return(1); case 1: return(-1); case 2: return(1); case 3: return(-1); case 4: return(1); case 5: return(1); case 6: return(1); case 7: return(-1); case 8: return(1); case 9: return(1); case 10: return(1); } return(1); }
int Giu(int k)   { switch(k) { case 0: return(500); case 1: return(500); case 2: return(5); case 3: return(3); case 4: return(6); case 5: return(5); case 6: return(10); case 7: return(3); case 8: return(6); case 9: return(10); case 10: return(5); } return(1); }
bool CoDieuKienRa(int k) { switch(k) { case 0: return(false); case 1: return(false); case 2: return(false); case 3: return(true); case 4: return(false); case 5: return(true); case 6: return(false); case 7: return(false); case 8: return(false); case 9: return(true); case 10: return(true); } return(false); }

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
   h_ma1 = iMA(_Symbol, KHUNG, 100, 0, MODE_EMA, PRICE_CLOSE);
   h_ma2 = iMA(_Symbol, KHUNG, 50, 0, MODE_SMA, PRICE_CLOSE);
   h_ma3 = iMA(_Symbol, KHUNG, 20, 0, MODE_SMA, PRICE_CLOSE);
   h_ma4 = iMA(_Symbol, KHUNG, 10, 0, MODE_EMA, PRICE_CLOSE);
   h_rsi0 = iRSI(_Symbol, KHUNG, 14, PRICE_CLOSE);
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
