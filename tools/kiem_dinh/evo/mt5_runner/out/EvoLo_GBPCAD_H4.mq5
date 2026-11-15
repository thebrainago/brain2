//+------------------------------------------------------------------+
//| EvoLo_GBPCAD_H4 - SINH TU DONG boi nhan/dich_mq5.py. KHONG SUA TAY.
//| 32 co che tu config/co_che_dsl.json, chon bang InpMaCoChe.
//|
//| Gop nhieu co che vao MOT EA co chu dich: mot luot tester ton ~138 giay
//| ma bai test that chi 0,5 giay - phan con lai la boot terminal. Chay
//| OPTIMIZATION tren InpMaCoChe thi N co che ton bang MOT lan boot.
//+------------------------------------------------------------------+
#property copyright "The Brain"
#include <Trade\Trade.mqh>

input int    InpMaCoChe = 0;      // ma co che (0..31)

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

#define KHUNG PERIOD_H4

int h_ma0 = INVALID_HANDLE;
int h_ma1 = INVALID_HANDLE;
int h_ma2 = INVALID_HANDLE;
int h_ma3 = INVALID_HANDLE;
int h_ma4 = INVALID_HANDLE;
int h_ma5 = INVALID_HANDLE;
int h_ma6 = INVALID_HANDLE;
int h_ma7 = INVALID_HANDLE;
int h_rsi0 = INVALID_HANDLE;
int h_rsi1 = INVALID_HANDLE;
int h_rsi2 = INVALID_HANDLE;
int h_atr0 = INVALID_HANDLE;
int h_atr1 = INVALID_HANDLE;
int h_atr2 = INVALID_HANDLE;

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
   MqlDateTime d; TimeToStruct(iTime(_Symbol,KHUNG,s), d);
   return((double)d.hour);
  }

double F6(int s)
  {
   return(0);
  }

double F7(int s)
  {
   MqlDateTime d; TimeToStruct(iTime(_Symbol,KHUNG,s), d);
   return((double)d.hour);
  }

double F8(int s)
  {
   return(4);
  }

double F9(int s)
  {
   return(Chi(h_atr0, s));
  }

double F10(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F9(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F11(int s)
  {
   return(0.3);
  }

double F12(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F13(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F12(s+i);
   double t=0; for(int i=0;i<20;i++) t+=v[i]; double m=t/20.0;
   double q=0; for(int i=0;i<20;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/20.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F14(int s)
  {
   return(1.5);
  }

double F15(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F16(int s)
  {
   return(0.15);
  }

double F17(int s)
  {
   return(Chi(h_atr0, s));
  }

double F18(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F17(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F19(int s)
  {
   return(0.7);
  }

double F20(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F21(int s)
  {
   return(0.7);
  }

double F22(int s)
  {
   return(Chi(h_rsi0, s));
  }

double F23(int s)
  {
   return(95);
  }

double F24(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F25(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F24(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F26(int s)
  {
   return(0.3);
  }

double F27(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F28(int s)
  {
   return(Chi(h_ma0, s));
  }

double F29(int s)
  {
   return(Chi(h_rsi0, s));
  }

double F30(int s)
  {
   return(40);
  }

double F31(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F32(int s)
  {
   return(Chi(h_ma0, s));
  }

double F33(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F34(int s)
  {
   double a = F33(s+3);
   if(a == 0.0) return(0.0);
   return((F33(s) - a) / a);
  }

double F35(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F34(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F36(int s)
  {
   return(0.85);
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
   return(0.3);
  }

double F40(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F41(int s)
  {
   return(Chi(h_ma1, s));
  }

double F42(int s)
  {
   return(iClose(_Symbol,KHUNG,s) - iOpen(_Symbol,KHUNG,s));
  }

double F43(int s)
  {
   return(0);
  }

double F44(int s)
  {
   return(iClose(_Symbol,KHUNG,s) - iOpen(_Symbol,KHUNG,s));
  }

double F45(int s)
  {
   return(F44(s+1));
  }

double F46(int s)
  {
   return(0);
  }

double F47(int s)
  {
   return(iClose(_Symbol,KHUNG,s) - iOpen(_Symbol,KHUNG,s));
  }

double F48(int s)
  {
   return(F47(s+2));
  }

double F49(int s)
  {
   return(0);
  }

double F50(int s)
  {
   return(iClose(_Symbol,KHUNG,s) - iOpen(_Symbol,KHUNG,s));
  }

double F51(int s)
  {
   return(MathAbs(F50(s)));
  }

double F52(int s)
  {
   return(iClose(_Symbol,KHUNG,s) - iOpen(_Symbol,KHUNG,s));
  }

double F53(int s)
  {
   return(MathAbs(F52(s)));
  }

double F54(int s)
  {
   return(F53(s+1));
  }

double F55(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F56(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F55(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F57(int s)
  {
   return(0.5);
  }

double F58(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F59(int s)
  {
   return(Chi(h_ma2, s));
  }

double F60(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F61(int s)
  {
   return(0.25);
  }

double F62(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F63(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F62(s+i);
   double t=0; for(int i=0;i<20;i++) t+=v[i]; double m=t/20.0;
   double q=0; for(int i=0;i<20;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/20.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F64(int s)
  {
   return(-1.5);
  }

double F65(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F66(int s)
  {
   return(Chi(h_ma2, s));
  }

double F67(int s)
  {
   return(Chi(h_atr0, s));
  }

double F68(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F67(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F69(int s)
  {
   return(0.5);
  }

double F70(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F71(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F70(s+i);
   double t=0; for(int i=0;i<20;i++) t+=v[i]; double m=t/20.0;
   double q=0; for(int i=0;i<20;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/20.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F72(int s)
  {
   return(0);
  }

double F73(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F74(int s)
  {
   return(Chi(h_ma3, s));
  }

double F75(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F76(int s)
  {
   return(Chi(h_ma3, s));
  }

double F77(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F78(int s)
  {
   double a = F77(s+120);
   if(a == 0.0) return(0.0);
   return((F77(s) - a) / a);
  }

double F79(int s)
  {
   double v[]; ArrayResize(v, 500);
   for(int i = 0; i < 500; i++) v[i] = F78(s+i);
   int d = 0; for(int i=1;i<500;i++) if(v[i] <= v[0]) d++;
   return((double)d / 499.0);
  }

double F80(int s)
  {
   return(0.7);
  }

double F81(int s)
  {
   return(Chi(h_atr1, s));
  }

double F82(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F81(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F83(int s)
  {
   return(0.9);
  }

double F84(int s)
  {
   return(Chi(h_atr2, s));
  }

double F85(int s)
  {
   double v[]; ArrayResize(v, 500);
   for(int i = 0; i < 500; i++) v[i] = F84(s+i);
   int d = 0; for(int i=1;i<500;i++) if(v[i] <= v[0]) d++;
   return((double)d / 499.0);
  }

double F86(int s)
  {
   return(0.5);
  }

double F87(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F88(int s)
  {
   double v[]; ArrayResize(v, 10);
   for(int i = 0; i < 10; i++) v[i] = F87(s+i);
   double t=0; for(int i=0;i<10;i++) t+=v[i]; double m=t/10.0;
   double q=0; for(int i=0;i<10;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/10.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F89(int s)
  {
   return(-1.5);
  }

double F90(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F91(int s)
  {
   return(Chi(h_ma2, s));
  }

double F92(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F93(int s)
  {
   double v[]; ArrayResize(v, 50);
   for(int i = 0; i < 50; i++) v[i] = F92(s+i);
   int d = 0; for(int i=1;i<50;i++) if(v[i] <= v[0]) d++;
   return((double)d / 49.0);
  }

double F94(int s)
  {
   return(0.9);
  }

double F95(int s)
  {
   return(Chi(h_ma4, s));
  }

double F96(int s)
  {
   return(F95(s) - F95(s+20));
  }

double F97(int s)
  {
   return(MathAbs(F96(s)));
  }

double F98(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F97(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F99(int s)
  {
   return(0.3);
  }

double F100(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F101(int s)
  {
   double v[]; ArrayResize(v, 50);
   for(int i = 0; i < 50; i++) v[i] = F100(s+i);
   int d = 0; for(int i=1;i<50;i++) if(v[i] <= v[0]) d++;
   return((double)d / 49.0);
  }

double F102(int s)
  {
   return(0.4);
  }

double F103(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F104(int s)
  {
   double v[]; ArrayResize(v, 30);
   for(int i = 0; i < 30; i++) v[i] = F103(s+i);
   double t=0; for(int i=0;i<30;i++) t+=v[i]; double m=t/30.0;
   double q=0; for(int i=0;i<30;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/30.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F105(int s)
  {
   return(-1.8);
  }

double F106(int s)
  {
   return(Chi(h_ma4, s));
  }

double F107(int s)
  {
   double a = F106(s+10);
   if(a == 0.0) return(0.0);
   return((F106(s) - a) / a);
  }

double F108(int s)
  {
   return(MathAbs(F107(s)));
  }

double F109(int s)
  {
   double v[]; ArrayResize(v, 500);
   for(int i = 0; i < 500; i++) v[i] = F108(s+i);
   int d = 0; for(int i=1;i<500;i++) if(v[i] <= v[0]) d++;
   return((double)d / 499.0);
  }

double F110(int s)
  {
   return(0.3);
  }

double F111(int s)
  {
   return(Chi(h_atr0, s));
  }

double F112(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F111(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F113(int s)
  {
   return(0.5);
  }

double F114(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F115(int s)
  {
   return(Chi(h_ma5, s));
  }

double F116(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F117(int s)
  {
   double a = F116(s+3);
   if(a == 0.0) return(0.0);
   return((F116(s) - a) / a);
  }

double F118(int s)
  {
   double v[]; ArrayResize(v, 500);
   for(int i = 0; i < 500; i++) v[i] = F117(s+i);
   int d = 0; for(int i=1;i<500;i++) if(v[i] <= v[0]) d++;
   return((double)d / 499.0);
  }

double F119(int s)
  {
   return(0.1);
  }

double F120(int s)
  {
   return(Chi(h_atr0, s));
  }

double F121(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F120(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F122(int s)
  {
   return(0.5);
  }

double F123(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F124(int s)
  {
   return(0.8);
  }

double F125(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F126(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F125(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F127(int s)
  {
   return(0.3);
  }

double F128(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F129(int s)
  {
   double a = F128(s+60);
   if(a == 0.0) return(0.0);
   return((F128(s) - a) / a);
  }

double F130(int s)
  {
   double v[]; ArrayResize(v, 500);
   for(int i = 0; i < 500; i++) v[i] = F129(s+i);
   int d = 0; for(int i=1;i<500;i++) if(v[i] <= v[0]) d++;
   return((double)d / 499.0);
  }

double F131(int s)
  {
   return(0.5);
  }

double F132(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F133(int s)
  {
   return(0.3);
  }

double F134(int s)
  {
   return(iClose(_Symbol,KHUNG,s) - iOpen(_Symbol,KHUNG,s));
  }

double F135(int s)
  {
   return(MathAbs(F134(s)));
  }

double F136(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F135(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F137(int s)
  {
   return(0.8);
  }

double F138(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F139(int s)
  {
   return(0.75);
  }

double F140(int s)
  {
   return(Chi(h_atr0, s));
  }

double F141(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F140(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F142(int s)
  {
   return(0.7);
  }

double F143(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F144(int s)
  {
   return(Chi(h_ma2, s));
  }

double F145(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F146(int s)
  {
   return(0.3);
  }

double F147(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F148(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F147(s+i);
   double t=0; for(int i=0;i<20;i++) t+=v[i]; double m=t/20.0;
   double q=0; for(int i=0;i<20;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/20.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F149(int s)
  {
   return(-1.5);
  }

double F150(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F151(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F150(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F152(int s)
  {
   return(0.9);
  }

double F153(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F154(int s)
  {
   return(0.5);
  }

double F155(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F156(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F155(s+i);
   double t=0; for(int i=0;i<20;i++) t+=v[i]; double m=t/20.0;
   double q=0; for(int i=0;i<20;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/20.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F157(int s)
  {
   return(0);
  }

double F158(int s)
  {
   return(iHigh(_Symbol,KHUNG,s) - iLow(_Symbol,KHUNG,s));
  }

double F159(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F158(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F160(int s)
  {
   return(0.85);
  }

double F161(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F162(int s)
  {
   return(0.75);
  }

double F163(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F164(int s)
  {
   double v[]; ArrayResize(v, 50);
   for(int i = 0; i < 50; i++) v[i] = F163(s+i);
   double t=0; for(int i=0;i<50;i++) t+=v[i]; double m=t/50.0;
   double q=0; for(int i=0;i<50;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/50.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F165(int s)
  {
   return(1);
  }

double F166(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F167(int s)
  {
   double v[]; ArrayResize(v, 3);
   for(int i = 0; i < 3; i++) v[i] = F166(s+i);
   double t = 0; for(int i=0;i<3;i++) t += v[i];
   return(t / 3.0);
  }

double F168(int s)
  {
   return(0.7);
  }

double F169(int s)
  {
   return(Chi(h_atr0, s));
  }

double F170(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F169(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F171(int s)
  {
   return(0.4);
  }

double F172(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F173(int s)
  {
   return(Chi(h_ma3, s));
  }

double F174(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F175(int s)
  {
   return(0.2);
  }

double F176(int s)
  {
   return(Chi(h_rsi1, s));
  }

double F177(int s)
  {
   return(38);
  }

double F178(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F179(int s)
  {
   double a = F178(s+250);
   if(a == 0.0) return(0.0);
   return((F178(s) - a) / a);
  }

double F180(int s)
  {
   return(0);
  }

double F181(int s)
  {
   return(Chi(h_atr0, s));
  }

double F182(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F181(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F183(int s)
  {
   return(0.8);
  }

double F184(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F185(int s)
  {
   double a = F184(s+10);
   if(a == 0.0) return(0.0);
   return((F184(s) - a) / a);
  }

double F186(int s)
  {
   double v[]; ArrayResize(v, 200);
   for(int i = 0; i < 200; i++) v[i] = F185(s+i);
   int d = 0; for(int i=1;i<200;i++) if(v[i] <= v[0]) d++;
   return((double)d / 199.0);
  }

double F187(int s)
  {
   return(0.85);
  }

double F188(int s)
  {
   return(Chi(h_atr0, s));
  }

double F189(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F188(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F190(int s)
  {
   return(0.4);
  }

double F191(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F192(int s)
  {
   return(Chi(h_ma6, s));
  }

double F193(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F194(int s)
  {
   return(0.2);
  }

double F195(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F196(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F195(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F197(int s)
  {
   return(0.4);
  }

double F198(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F199(int s)
  {
   double v[]; ArrayResize(v, 50);
   for(int i = 0; i < 50; i++) v[i] = F198(s+i);
   double t=0; for(int i=0;i<50;i++) t+=v[i]; double m=t/50.0;
   double q=0; for(int i=0;i<50;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/50.0);
   return(sd);
  }

double F200(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F199(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F201(int s)
  {
   return(0.4);
  }

double F202(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F203(int s)
  {
   return(Chi(h_ma0, s));
  }

double F204(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F205(int s)
  {
   return(0.8);
  }

double F206(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F207(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F208(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F207(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]<m) m=v[i];
   return(m);
  }

double F209(int s)
  {
   return(F208(s+1));
  }

double F210(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F211(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F212(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F211(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]<m) m=v[i];
   return(m);
  }

double F213(int s)
  {
   return(F212(s+1));
  }

double F214(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F215(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F214(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F216(int s)
  {
   return(0.5);
  }

double F217(int s)
  {
   return(Chi(h_ma7, s));
  }

double F218(int s)
  {
   double a = F217(s+20);
   if(a == 0.0) return(0.0);
   return((F217(s) - a) / a);
  }

double F219(int s)
  {
   return(0);
  }

double F220(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F221(int s)
  {
   return(0.8);
  }

double F222(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F223(int s)
  {
   return(0.8);
  }

double F224(int s)
  {
   return(Chi(h_atr0, s));
  }

double F225(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F224(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F226(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F225(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]>m) m=v[i];
   return(m);
  }

double F227(int s)
  {
   return(0.8);
  }

double F228(int s)
  {
   return(Chi(h_atr0, s));
  }

double F229(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F228(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F230(int s)
  {
   return(0.5);
  }

double F231(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F232(int s)
  {
   return(Chi(h_ma2, s));
  }

double F233(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F234(int s)
  {
   return(0.2);
  }

double F235(int s)
  {
   return(Chi(h_rsi2, s));
  }

double F236(int s)
  {
   return(15);
  }

double F237(int s)
  {
   return(Chi(h_atr0, s));
  }

double F238(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F237(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F239(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F238(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]>m) m=v[i];
   return(m);
  }

double F240(int s)
  {
   return(0.8);
  }

double F241(int s)
  {
   return(Chi(h_atr0, s));
  }

double F242(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F241(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F243(int s)
  {
   return(0.5);
  }

double F244(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F245(int s)
  {
   return(Chi(h_ma2, s));
  }

double F246(int s)
  {
   return(Chi(h_rsi2, s));
  }

double F247(int s)
  {
   return(60);
  }

double F248(int s)
  {
   return(Chi(h_rsi2, s));
  }

double F249(int s)
  {
   return(20);
  }

double F250(int s)
  {
   return(Chi(h_atr0, s));
  }

double F251(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F250(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F252(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F251(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]>m) m=v[i];
   return(m);
  }

double F253(int s)
  {
   return(0.8);
  }

double F254(int s)
  {
   return(Chi(h_atr0, s));
  }

double F255(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F254(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F256(int s)
  {
   return(0.5);
  }

double F257(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F258(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F257(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F259(int s)
  {
   return(0.6);
  }

double F260(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F261(int s)
  {
   return(Chi(h_ma2, s));
  }

double F262(int s)
  {
   return(Chi(h_rsi2, s));
  }

double F263(int s)
  {
   return(60);
  }

double F264(int s)
  {
   return(Chi(h_rsi2, s));
  }

double F265(int s)
  {
   return(25);
  }

double F266(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F267(int s)
  {
   return(0.3);
  }

double F268(int s)
  {
   return(Chi(h_atr0, s));
  }

double F269(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F268(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F270(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F269(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]>m) m=v[i];
   return(m);
  }

double F271(int s)
  {
   return(0.8);
  }

double F272(int s)
  {
   return(Chi(h_atr0, s));
  }

double F273(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F272(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F274(int s)
  {
   return(0.5);
  }

double F275(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F276(int s)
  {
   return(Chi(h_ma5, s));
  }

double F277(int s)
  {
   return(Chi(h_rsi2, s));
  }

double F278(int s)
  {
   return(60);
  }

double F279(int s)
  {
   return(Chi(h_rsi2, s));
  }

double F280(int s)
  {
   return(20);
  }

double F281(int s)
  {
   return(Chi(h_rsi2, s));
  }

double F282(int s)
  {
   return(F281(s+1));
  }

double F283(int s)
  {
   return(30);
  }

double F284(int s)
  {
   return(Chi(h_atr0, s));
  }

double F285(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F284(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F286(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F285(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]>m) m=v[i];
   return(m);
  }

double F287(int s)
  {
   return(0.8);
  }

double F288(int s)
  {
   return(Chi(h_atr0, s));
  }

double F289(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F288(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F290(int s)
  {
   return(0.5);
  }

double F291(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F292(int s)
  {
   return(Chi(h_ma2, s));
  }

double F293(int s)
  {
   return(Chi(h_rsi2, s));
  }

double F294(int s)
  {
   return(60);
  }

double F295(int s)
  {
   return(Chi(h_rsi2, s));
  }

double F296(int s)
  {
   return(80);
  }

double F297(int s)
  {
   return(Chi(h_atr0, s));
  }

double F298(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F297(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F299(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F298(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]>m) m=v[i];
   return(m);
  }

double F300(int s)
  {
   return(0.8);
  }

double F301(int s)
  {
   return(Chi(h_atr0, s));
  }

double F302(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F301(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F303(int s)
  {
   return(0.5);
  }

double F304(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F305(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F304(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F306(int s)
  {
   return(0.6);
  }

double F307(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F308(int s)
  {
   return(Chi(h_ma5, s));
  }

double F309(int s)
  {
   return(Chi(h_rsi2, s));
  }

double F310(int s)
  {
   return(40);
  }

double F311(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F312(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F313(int s)
  {
   double v[]; ArrayResize(v, 10);
   for(int i = 0; i < 10; i++) v[i] = F312(s+i);
   double m = v[0]; for(int i=1;i<10;i++) if(v[i]<m) m=v[i];
   return(m);
  }

double F314(int s)
  {
   return(F313(s+1));
  }

double F315(int s)
  {
   return(iClose(_Symbol,KHUNG,s) - iOpen(_Symbol,KHUNG,s));
  }

double F316(int s)
  {
   return(0);
  }

double F317(int s)
  {
   return(Chi(h_atr0, s));
  }

double F318(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F317(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F319(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F318(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]>m) m=v[i];
   return(m);
  }

double F320(int s)
  {
   return(0.8);
  }

double F321(int s)
  {
   return(Chi(h_atr0, s));
  }

double F322(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F321(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F323(int s)
  {
   return(0.6);
  }

double F324(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F325(int s)
  {
   return(Chi(h_ma2, s));
  }

double F326(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F327(int s)
  {
   return(0.85);
  }

double F328(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F329(int s)
  {
   return(0.7);
  }

double F330(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F331(int s)
  {
   return(F330(s+1));
  }

double F332(int s)
  {
   return(0.7);
  }

double F333(int s)
  {
   return(Chi(h_atr0, s));
  }

double F334(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F333(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F335(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F334(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]>m) m=v[i];
   return(m);
  }

double F336(int s)
  {
   return(0.8);
  }

double F337(int s)
  {
   return(Chi(h_atr0, s));
  }

double F338(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F337(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F339(int s)
  {
   return(0.5);
  }

double F340(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F341(int s)
  {
   double a = F340(s+120);
   if(a == 0.0) return(0.0);
   return((F340(s) - a) / a);
  }

double F342(int s)
  {
   return(0);
  }

double F343(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F344(int s)
  {
   return(0.2);
  }

double F345(int s)
  {
   return(iClose(_Symbol,KHUNG,s) - iOpen(_Symbol,KHUNG,s));
  }

double F346(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F345(s+i);
   double t=0; for(int i=0;i<100;i++) t+=v[i]; double m=t/100.0;
   double q=0; for(int i=0;i<100;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/100.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F347(int s)
  {
   return(-1.2);
  }

double F348(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F349(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F348(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F350(int s)
  {
   return(0.6);
  }

double F351(int s)
  {
   return(iHigh(_Symbol,KHUNG,s) - iLow(_Symbol,KHUNG,s));
  }

double F352(int s)
  {
   double v[]; ArrayResize(v, 10);
   for(int i = 0; i < 10; i++) v[i] = F351(s+i);
   double t = 0; for(int i=0;i<10;i++) t += v[i];
   return(t / 10.0);
  }

double F353(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F352(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F354(int s)
  {
   return(0.35);
  }

double F355(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F356(int s)
  {
   return(Chi(h_ma2, s));
  }

double F357(int s)
  {
   return(Chi(h_rsi2, s));
  }

double F358(int s)
  {
   return(60);
  }

double F359(int s)
  {
   return(Chi(h_rsi2, s));
  }

double F360(int s)
  {
   return(15);
  }

double F361(int s)
  {
   return(iHigh(_Symbol,KHUNG,s) - iLow(_Symbol,KHUNG,s));
  }

double F362(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F361(s+i);
   double t = 0; for(int i=0;i<20;i++) t += v[i];
   return(t / 20.0);
  }

double F363(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F362(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F364(int s)
  {
   return(0.35);
  }

double F365(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F366(int s)
  {
   return(Chi(h_ma0, s));
  }

double F367(int s)
  {
   return(Chi(h_rsi2, s));
  }

double F368(int s)
  {
   return(60);
  }


//--- vao/ra cua tung co che
bool VAO0(int s) { return((F1(s) >= F2(s))); }
bool RA0(int s)  { return(false); }
bool VAO1(int s) { return((F3(s) >= F4(s))); }
bool RA1(int s)  { return(false); }
bool VAO2(int s) { return((F5(s) >= F6(s)) && (F7(s) <= F8(s)) && (F10(s) < F11(s)) && (F13(s) > F14(s))); }
bool RA2(int s)  { return(false); }
bool VAO3(int s) { return((F15(s) < F16(s)) && (F18(s) > F19(s))); }
bool RA3(int s)  { return((F20(s) > F21(s))); }
bool VAO4(int s) { return((F22(s) > F23(s)) && (F25(s) < F26(s)) && (F27(s) < F28(s))); }
bool RA4(int s)  { return((F29(s) < F30(s))); }
bool VAO5(int s) { return((F31(s) < F32(s)) && (F35(s) > F36(s)) && (F38(s) < F39(s))); }
bool RA5(int s)  { return((F40(s) < F41(s))); }
bool VAO6(int s) { return((F42(s) > F43(s)) && (F45(s) > F46(s)) && (F48(s) > F49(s)) && (F51(s) < F54(s)) && (F56(s) < F57(s)) && (F58(s) < F59(s))); }
bool RA6(int s)  { return((F60(s) < F61(s))); }
bool VAO7(int s) { return((F63(s) < F64(s)) && (F65(s) > F66(s)) && (F68(s) < F69(s))); }
bool RA7(int s)  { return((F71(s) > F72(s))); }
bool VAO8(int s) { return((F73(s) < F74(s)) && (F75(s) > F76(s)) && (F79(s) > F80(s))); }
bool RA8(int s)  { return(false); }
bool VAO9(int s) { return((F82(s) > F83(s)) && (F85(s) < F86(s)) && (F88(s) < F89(s)) && (F90(s) > F91(s))); }
bool RA9(int s)  { return(false); }
bool VAO10(int s) { return((F93(s) > F94(s)) && (F98(s) < F99(s))); }
bool RA10(int s)  { return((F101(s) < F102(s))); }
bool VAO11(int s) { return((F104(s) < F105(s)) && (F109(s) < F110(s)) && (F112(s) < F113(s))); }
bool RA11(int s)  { return(false); }
bool VAO12(int s) { return((F114(s) > F115(s)) && (F118(s) < F119(s)) && (F121(s) < F122(s))); }
bool RA12(int s)  { return(false); }
bool VAO13(int s) { return((F123(s) > F124(s)) && (F126(s) < F127(s)) && (F130(s) < F131(s))); }
bool RA13(int s)  { return((F132(s) < F133(s))); }
bool VAO14(int s) { return((F136(s) > F137(s)) && (F138(s) > F139(s)) && (F141(s) > F142(s)) && (F143(s) < F144(s))); }
bool RA14(int s)  { return((F145(s) < F146(s))); }
bool VAO15(int s) { return((F148(s) < F149(s)) && (F151(s) > F152(s)) && (F153(s) > F154(s))); }
bool RA15(int s)  { return((F156(s) > F157(s))); }
bool VAO16(int s) { return((F159(s) > F160(s)) && (F161(s) > F162(s)) && (F164(s) > F165(s))); }
bool RA16(int s)  { return(false); }
bool VAO17(int s) { return((F167(s) > F168(s)) && (F170(s) < F171(s)) && (F172(s) < F173(s))); }
bool RA17(int s)  { return(false); }
bool VAO18(int s) { return((F174(s) < F175(s)) && (F176(s) < F177(s)) && (F179(s) > F180(s)) && (F182(s) < F183(s))); }
bool RA18(int s)  { return(false); }
bool VAO19(int s) { return((F186(s) > F187(s)) && (F189(s) < F190(s)) && (F191(s) < F192(s))); }
bool RA19(int s)  { return(false); }
bool VAO20(int s) { return((F193(s) < F194(s)) && (F196(s) < F197(s)) && (F200(s) < F201(s)) && (F202(s) > F203(s))); }
bool RA20(int s)  { return((F204(s) > F205(s))); }
bool VAO21(int s) { return((F206(s) < F209(s)) && (F210(s) > F213(s)) && (F215(s) < F216(s)) && (F218(s) > F219(s))); }
bool RA21(int s)  { return((F220(s) > F221(s))); }
bool VAO22(int s) { return((F222(s) > F223(s)) && (F226(s) > F227(s)) && (F229(s) < F230(s)) && (F231(s) < F232(s))); }
bool RA22(int s)  { return((F233(s) < F234(s))); }
bool VAO23(int s) { return((F235(s) < F236(s)) && (F239(s) > F240(s)) && (F242(s) < F243(s)) && (F244(s) > F245(s))); }
bool RA23(int s)  { return((F246(s) > F247(s))); }
bool VAO24(int s) { return((F248(s) < F249(s)) && (F252(s) > F253(s)) && (F255(s) < F256(s)) && (F258(s) < F259(s)) && (F260(s) > F261(s))); }
bool RA24(int s)  { return((F262(s) > F263(s))); }
bool VAO25(int s) { return((F264(s) < F265(s)) && (F266(s) < F267(s)) && (F270(s) > F271(s)) && (F273(s) < F274(s)) && (F275(s) > F276(s))); }
bool RA25(int s)  { return((F277(s) > F278(s))); }
bool VAO26(int s) { return((F279(s) < F280(s)) && (F282(s) < F283(s)) && (F286(s) > F287(s)) && (F289(s) < F290(s)) && (F291(s) > F292(s))); }
bool RA26(int s)  { return((F293(s) > F294(s))); }
bool VAO27(int s) { return((F295(s) > F296(s)) && (F299(s) > F300(s)) && (F302(s) < F303(s)) && (F305(s) < F306(s)) && (F307(s) < F308(s))); }
bool RA27(int s)  { return((F309(s) < F310(s))); }
bool VAO28(int s) { return((F311(s) < F314(s)) && (F315(s) > F316(s)) && (F319(s) > F320(s)) && (F322(s) < F323(s)) && (F324(s) > F325(s))); }
bool RA28(int s)  { return((F326(s) > F327(s))); }
bool VAO29(int s) { return((F328(s) > F329(s)) && (F331(s) > F332(s)) && (F335(s) > F336(s)) && (F338(s) < F339(s)) && (F341(s) < F342(s))); }
bool RA29(int s)  { return((F343(s) < F344(s))); }
bool VAO30(int s) { return((F346(s) < F347(s)) && (F349(s) < F350(s)) && (F353(s) < F354(s)) && (F355(s) > F356(s))); }
bool RA30(int s)  { return((F357(s) > F358(s))); }
bool VAO31(int s) { return((F359(s) < F360(s)) && (F363(s) < F364(s)) && (F365(s) > F366(s))); }
bool RA31(int s)  { return((F367(s) > F368(s))); }

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
      case 11: return(VAO11(s));
      case 12: return(VAO12(s));
      case 13: return(VAO13(s));
      case 14: return(VAO14(s));
      case 15: return(VAO15(s));
      case 16: return(VAO16(s));
      case 17: return(VAO17(s));
      case 18: return(VAO18(s));
      case 19: return(VAO19(s));
      case 20: return(VAO20(s));
      case 21: return(VAO21(s));
      case 22: return(VAO22(s));
      case 23: return(VAO23(s));
      case 24: return(VAO24(s));
      case 25: return(VAO25(s));
      case 26: return(VAO26(s));
      case 27: return(VAO27(s));
      case 28: return(VAO28(s));
      case 29: return(VAO29(s));
      case 30: return(VAO30(s));
      case 31: return(VAO31(s));
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
      case 11: return(RA11(s));
      case 12: return(RA12(s));
      case 13: return(RA13(s));
      case 14: return(RA14(s));
      case 15: return(RA15(s));
      case 16: return(RA16(s));
      case 17: return(RA17(s));
      case 18: return(RA18(s));
      case 19: return(RA19(s));
      case 20: return(RA20(s));
      case 21: return(RA21(s));
      case 22: return(RA22(s));
      case 23: return(RA23(s));
      case 24: return(RA24(s));
      case 25: return(RA25(s));
      case 26: return(RA26(s));
      case 27: return(RA27(s));
      case 28: return(RA28(s));
      case 29: return(RA29(s));
      case 30: return(RA30(s));
      case 31: return(RA31(s));
     }
   return(false);
  }

int Chieu(int k) { switch(k) { case 0: return(1); case 1: return(-1); case 2: return(-1); case 3: return(1); case 4: return(-1); case 5: return(-1); case 6: return(-1); case 7: return(1); case 8: return(1); case 9: return(1); case 10: return(-1); case 11: return(1); case 12: return(1); case 13: return(-1); case 14: return(-1); case 15: return(1); case 16: return(1); case 17: return(-1); case 18: return(1); case 19: return(-1); case 20: return(1); case 21: return(1); case 22: return(-1); case 23: return(1); case 24: return(1); case 25: return(1); case 26: return(1); case 27: return(-1); case 28: return(1); case 29: return(-1); case 30: return(1); case 31: return(1); } return(1); }
int Giu(int k)   { switch(k) { case 0: return(500); case 1: return(500); case 2: return(2); case 3: return(3); case 4: return(3); case 5: return(5); case 6: return(4); case 7: return(6); case 8: return(8); case 9: return(6); case 10: return(8); case 11: return(10); case 12: return(8); case 13: return(4); case 14: return(4); case 15: return(5); case 16: return(6); case 17: return(3); case 18: return(3); case 19: return(8); case 20: return(4); case 21: return(5); case 22: return(4); case 23: return(4); case 24: return(4); case 25: return(4); case 26: return(4); case 27: return(4); case 28: return(5); case 29: return(4); case 30: return(4); case 31: return(4); } return(1); }
bool CoDieuKienRa(int k) { switch(k) { case 0: return(false); case 1: return(false); case 2: return(false); case 3: return(true); case 4: return(true); case 5: return(true); case 6: return(true); case 7: return(true); case 8: return(false); case 9: return(false); case 10: return(true); case 11: return(false); case 12: return(false); case 13: return(true); case 14: return(true); case 15: return(true); case 16: return(false); case 17: return(false); case 18: return(false); case 19: return(false); case 20: return(true); case 21: return(true); case 22: return(true); case 23: return(true); case 24: return(true); case 25: return(true); case 26: return(true); case 27: return(true); case 28: return(true); case 29: return(true); case 30: return(true); case 31: return(true); } return(false); }

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
   h_ma0 = iMA(_Symbol, KHUNG, 100, 0, MODE_SMA, PRICE_CLOSE);
   h_ma1 = iMA(_Symbol, KHUNG, 10, 0, MODE_SMA, PRICE_CLOSE);
   h_ma2 = iMA(_Symbol, KHUNG, 200, 0, MODE_SMA, PRICE_CLOSE);
   h_ma3 = iMA(_Symbol, KHUNG, 50, 0, MODE_EMA, PRICE_CLOSE);
   h_ma4 = iMA(_Symbol, KHUNG, 50, 0, MODE_SMA, PRICE_CLOSE);
   h_ma5 = iMA(_Symbol, KHUNG, 100, 0, MODE_EMA, PRICE_CLOSE);
   h_ma6 = iMA(_Symbol, KHUNG, 150, 0, MODE_SMA, PRICE_CLOSE);
   h_ma7 = iMA(_Symbol, KHUNG, 200, 0, MODE_EMA, PRICE_CLOSE);
   h_rsi0 = iRSI(_Symbol, KHUNG, 2, PRICE_CLOSE);
   h_rsi1 = iRSI(_Symbol, KHUNG, 14, PRICE_CLOSE);
   h_rsi2 = iRSI(_Symbol, KHUNG, 3, PRICE_CLOSE);
   h_atr0 = iATR(_Symbol, KHUNG, 14);
   h_atr1 = iATR(_Symbol, KHUNG, 5);
   h_atr2 = iATR(_Symbol, KHUNG, 100);
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
