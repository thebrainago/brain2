//+------------------------------------------------------------------+
//| EvoLo_AUDCHF_H4 - SINH TU DONG boi nhan/dich_mq5.py. KHONG SUA TAY.
//| 21 co che tu config/co_che_dsl.json, chon bang InpMaCoChe.
//|
//| Gop nhieu co che vao MOT EA co chu dich: mot luot tester ton ~138 giay
//| ma bai test that chi 0,5 giay - phan con lai la boot terminal. Chay
//| OPTIMIZATION tren InpMaCoChe thi N co che ton bang MOT lan boot.
//+------------------------------------------------------------------+
#property copyright "The Brain"
#include <Trade\Trade.mqh>

input int    InpMaCoChe = 0;      // ma co che (0..20)

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
   MqlDateTime d; TimeToStruct(iTime(_Symbol,KHUNG,s), d);
   return((double)d.hour);
  }

double F6(int s)
  {
   return(16);
  }

double F7(int s)
  {
   MqlDateTime d; TimeToStruct(iTime(_Symbol,KHUNG,s), d);
   return((double)d.hour);
  }

double F8(int s)
  {
   return(20);
  }

double F9(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F10(int s)
  {
   double a = F9(s+1);
   if(a == 0.0) return(0.0);
   return((F9(s) - a) / a);
  }

double F11(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F10(s+i);
   double t=0; for(int i=0;i<100;i++) t+=v[i]; double m=t/100.0;
   double q=0; for(int i=0;i<100;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/100.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F12(int s)
  {
   return(2.5);
  }

double F13(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F14(int s)
  {
   return(Chi(h_ma0, s));
  }

double F15(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F16(int s)
  {
   double v[]; ArrayResize(v, 40);
   for(int i = 0; i < 40; i++) v[i] = F15(s+i);
   double t=0; for(int i=0;i<40;i++) t+=v[i]; double m=t/40.0;
   double q=0; for(int i=0;i<40;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/40.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F17(int s)
  {
   return(1.5);
  }

double F18(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F19(int s)
  {
   double a = F18(s+40);
   if(a == 0.0) return(0.0);
   return((F18(s) - a) / a);
  }

double F20(int s)
  {
   return(MathAbs(F19(s)));
  }

double F21(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F20(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F22(int s)
  {
   return(0.4);
  }

double F23(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F24(int s)
  {
   double v[]; ArrayResize(v, 40);
   for(int i = 0; i < 40; i++) v[i] = F23(s+i);
   double t=0; for(int i=0;i<40;i++) t+=v[i]; double m=t/40.0;
   double q=0; for(int i=0;i<40;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/40.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F25(int s)
  {
   return(-0.5);
  }

double F26(int s)
  {
   return(iHigh(_Symbol,KHUNG,s) - iLow(_Symbol,KHUNG,s));
  }

double F27(int s)
  {
   double v[]; ArrayResize(v, 5);
   for(int i = 0; i < 5; i++) v[i] = F26(s+i);
   double t = 0; for(int i=0;i<5;i++) t += v[i];
   return(t / 5.0);
  }

double F28(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F27(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F29(int s)
  {
   return(0.2);
  }

double F30(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F31(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F32(int s)
  {
   return(F31(s+1));
  }

double F33(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F32(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]<m) m=v[i];
   return(m);
  }

double F34(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F35(int s)
  {
   double a = F34(s+120);
   if(a == 0.0) return(0.0);
   return((F34(s) - a) / a);
  }

double F36(int s)
  {
   return(0);
  }

double F37(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F38(int s)
  {
   double a = F37(s+120);
   if(a == 0.0) return(0.0);
   return((F37(s) - a) / a);
  }

double F39(int s)
  {
   double v[]; ArrayResize(v, 500);
   for(int i = 0; i < 500; i++) v[i] = F38(s+i);
   int d = 0; for(int i=1;i<500;i++) if(v[i] <= v[0]) d++;
   return((double)d / 499.0);
  }

double F40(int s)
  {
   return(0.8);
  }

double F41(int s)
  {
   return(Chi(h_atr0, s));
  }

double F42(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F41(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F43(int s)
  {
   return(0.4);
  }

double F44(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F45(int s)
  {
   double v[]; ArrayResize(v, 50);
   for(int i = 0; i < 50; i++) v[i] = F44(s+i);
   double t=0; for(int i=0;i<50;i++) t+=v[i]; double m=t/50.0;
   double q=0; for(int i=0;i<50;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/50.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F46(int s)
  {
   return(1);
  }

double F47(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F48(int s)
  {
   return(0.55);
  }

double F49(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F50(int s)
  {
   double a = F49(s+5);
   if(a == 0.0) return(0.0);
   return((F49(s) - a) / a);
  }

double F51(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F50(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F52(int s)
  {
   return(0.2);
  }

double F53(int s)
  {
   return(Chi(h_atr0, s));
  }

double F54(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F53(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F55(int s)
  {
   return(F54(s+10));
  }

double F56(int s)
  {
   return(0.85);
  }

double F57(int s)
  {
   return(iHigh(_Symbol,KHUNG,s) - iLow(_Symbol,KHUNG,s));
  }

double F58(int s)
  {
   double v[]; ArrayResize(v, 60);
   for(int i = 0; i < 60; i++) v[i] = F57(s+i);
   int d = 0; for(int i=1;i<60;i++) if(v[i] <= v[0]) d++;
   return((double)d / 59.0);
  }

double F59(int s)
  {
   return(0.5);
  }

double F60(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F61(int s)
  {
   return(Chi(h_ma1, s));
  }

double F62(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F63(int s)
  {
   return(Chi(h_ma1, s));
  }

double F64(int s)
  {
   return(iHigh(_Symbol, KHUNG, s+0));
  }

double F65(int s)
  {
   return(iHigh(_Symbol, KHUNG, s+0));
  }

double F66(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F65(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]>m) m=v[i];
   return(m);
  }

double F67(int s)
  {
   return(F66(s+1));
  }

double F68(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F69(int s)
  {
   return(iHigh(_Symbol, KHUNG, s+0));
  }

double F70(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F69(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]>m) m=v[i];
   return(m);
  }

double F71(int s)
  {
   return(F70(s+1));
  }

double F72(int s)
  {
   return(Chi(h_atr0, s));
  }

double F73(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F72(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F74(int s)
  {
   return(0.7);
  }

double F75(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F76(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F75(s+i);
   double t=0; for(int i=0;i<20;i++) t+=v[i]; double m=t/20.0;
   double q=0; for(int i=0;i<20;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/20.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F77(int s)
  {
   return(-2);
  }

double F78(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F79(int s)
  {
   double a = F78(s+50);
   if(a == 0.0) return(0.0);
   return((F78(s) - a) / a);
  }

double F80(int s)
  {
   return(MathAbs(F79(s)));
  }

double F81(int s)
  {
   double v[]; ArrayResize(v, 500);
   for(int i = 0; i < 500; i++) v[i] = F80(s+i);
   int d = 0; for(int i=1;i<500;i++) if(v[i] <= v[0]) d++;
   return((double)d / 499.0);
  }

double F82(int s)
  {
   return(0.3);
  }

double F83(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F84(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F83(s+i);
   double t=0; for(int i=0;i<20;i++) t+=v[i]; double m=t/20.0;
   double q=0; for(int i=0;i<20;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/20.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F85(int s)
  {
   return(2);
  }

double F86(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F87(int s)
  {
   double a = F86(s+50);
   if(a == 0.0) return(0.0);
   return((F86(s) - a) / a);
  }

double F88(int s)
  {
   return(MathAbs(F87(s)));
  }

double F89(int s)
  {
   double v[]; ArrayResize(v, 500);
   for(int i = 0; i < 500; i++) v[i] = F88(s+i);
   int d = 0; for(int i=1;i<500;i++) if(v[i] <= v[0]) d++;
   return((double)d / 499.0);
  }

double F90(int s)
  {
   return(0.3);
  }

double F91(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F92(int s)
  {
   return(0.2);
  }

double F93(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F94(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F93(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F95(int s)
  {
   return(0.15);
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
   return(0.5);
  }

double F99(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F100(int s)
  {
   double a = F99(s+3);
   if(a == 0.0) return(0.0);
   return((F99(s) - a) / a);
  }

double F101(int s)
  {
   double v[]; ArrayResize(v, 500);
   for(int i = 0; i < 500; i++) v[i] = F100(s+i);
   int d = 0; for(int i=1;i<500;i++) if(v[i] <= v[0]) d++;
   return((double)d / 499.0);
  }

double F102(int s)
  {
   return(0.08);
  }

double F103(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F104(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F103(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F105(int s)
  {
   return(0.8);
  }

double F106(int s)
  {
   return(iClose(_Symbol,KHUNG,s) - iOpen(_Symbol,KHUNG,s));
  }

double F107(int s)
  {
   return(MathAbs(F106(s)));
  }

double F108(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F107(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F109(int s)
  {
   return(0.5);
  }

double F110(int s)
  {
   return(iClose(_Symbol,KHUNG,s) - iOpen(_Symbol,KHUNG,s));
  }

double F111(int s)
  {
   return(MathAbs(F110(s)));
  }

double F112(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F111(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F113(int s)
  {
   return(0.9);
  }

double F114(int s)
  {
   return(iClose(_Symbol,KHUNG,s) - iOpen(_Symbol,KHUNG,s));
  }

double F115(int s)
  {
   return(0);
  }

double F116(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F117(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F116(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F118(int s)
  {
   return(0.6);
  }

double F119(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F120(int s)
  {
   return(Chi(h_ma2, s));
  }

double F121(int s)
  {
   return(iHigh(_Symbol, KHUNG, s+0));
  }

double F122(int s)
  {
   return(iHigh(_Symbol, KHUNG, s+0));
  }

double F123(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F122(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]>m) m=v[i];
   return(m);
  }

double F124(int s)
  {
   return(F123(s+1));
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
   return(0.4);
  }

double F128(int s)
  {
   return(Chi(h_atr0, s));
  }

double F129(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F128(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F130(int s)
  {
   return(0.4);
  }

double F131(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F132(int s)
  {
   return(0.3);
  }

double F133(int s)
  {
   return(iHigh(_Symbol,KHUNG,s) - iLow(_Symbol,KHUNG,s));
  }

double F134(int s)
  {
   double v[]; ArrayResize(v, 7);
   for(int i = 0; i < 7; i++) v[i] = F133(s+i);
   int d = 0; for(int i=1;i<7;i++) if(v[i] <= v[0]) d++;
   return((double)d / 6.0);
  }

double F135(int s)
  {
   return(0.15);
  }

double F136(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F137(int s)
  {
   return(0.35);
  }

double F138(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F139(int s)
  {
   return(Chi(h_ma0, s));
  }

double F140(int s)
  {
   return(iHigh(_Symbol, KHUNG, s+0));
  }

double F141(int s)
  {
   return(iHigh(_Symbol, KHUNG, s+0));
  }

double F142(int s)
  {
   return(F141(s+1));
  }

double F143(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F144(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F145(int s)
  {
   return(F144(s+1));
  }

double F146(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F147(int s)
  {
   return(0.3);
  }

double F148(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F149(int s)
  {
   return(Chi(h_ma2, s));
  }

double F150(int s)
  {
   return(Chi(h_atr0, s));
  }

double F151(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F150(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F152(int s)
  {
   return(0.3);
  }

double F153(int s)
  {
   return(Chi(h_atr0, s));
  }

double F154(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F153(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F155(int s)
  {
   return(0.8);
  }

double F156(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F157(int s)
  {
   return(0.8);
  }

double F158(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F159(int s)
  {
   return(F158(s+1));
  }

double F160(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F161(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F160(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]<m) m=v[i];
   return(m);
  }

double F162(int s)
  {
   return(F161(s+1));
  }

double F163(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F164(int s)
  {
   return(0.7);
  }

double F165(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F166(int s)
  {
   double v[]; ArrayResize(v, 50);
   for(int i = 0; i < 50; i++) v[i] = F165(s+i);
   double t=0; for(int i=0;i<50;i++) t+=v[i]; double m=t/50.0;
   double q=0; for(int i=0;i<50;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/50.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F167(int s)
  {
   return(0.5);
  }

double F168(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F169(int s)
  {
   return(Chi(h_ma0, s));
  }

double F170(int s)
  {
   MqlDateTime d; TimeToStruct(iTime(_Symbol,KHUNG,s), d);
   return((double)d.day);
  }

double F171(int s)
  {
   return(3);
  }

double F172(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F173(int s)
  {
   double a = F172(s+120);
   if(a == 0.0) return(0.0);
   return((F172(s) - a) / a);
  }

double F174(int s)
  {
   return(0);
  }

double F175(int s)
  {
   return(Chi(h_atr0, s));
  }

double F176(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F175(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F177(int s)
  {
   return(0.5);
  }

double F178(int s)
  {
   return(Chi(h_ma3, s));
  }

double F179(int s)
  {
   double a = F178(s+20);
   if(a == 0.0) return(0.0);
   return((F178(s) - a) / a);
  }

double F180(int s)
  {
   return(0);
  }

double F181(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F182(int s)
  {
   return(Chi(h_ma4, s));
  }

double F183(int s)
  {
   return(iHigh(_Symbol,KHUNG,s) - iLow(_Symbol,KHUNG,s));
  }

double F184(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F183(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F185(int s)
  {
   return(0.35);
  }

double F186(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F187(int s)
  {
   double v[]; ArrayResize(v, 50);
   for(int i = 0; i < 50; i++) v[i] = F186(s+i);
   double t=0; for(int i=0;i<50;i++) t+=v[i]; double m=t/50.0;
   double q=0; for(int i=0;i<50;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/50.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F188(int s)
  {
   return(1.5);
  }

double F189(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F190(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F189(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F191(int s)
  {
   return(0.45);
  }

double F192(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F193(int s)
  {
   double a = F192(s+120);
   if(a == 0.0) return(0.0);
   return((F192(s) - a) / a);
  }

double F194(int s)
  {
   return(0);
  }

double F195(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F196(int s)
  {
   return(Chi(h_ma5, s));
  }


//--- vao/ra cua tung co che
bool VAO0(int s) { return((F1(s) >= F2(s))); }
bool RA0(int s)  { return(false); }
bool VAO1(int s) { return((F3(s) >= F4(s))); }
bool RA1(int s)  { return(false); }
bool VAO2(int s) { return((F5(s) >= F6(s)) && (F7(s) <= F8(s)) && (F11(s) > F12(s)) && (F13(s) < F14(s))); }
bool RA2(int s)  { return(false); }
bool VAO3(int s) { return((F16(s) > F17(s)) && (F21(s) < F22(s))); }
bool RA3(int s)  { return((F24(s) < F25(s))); }
bool VAO4(int s) { return((F28(s) < F29(s)) && (F30(s) < F33(s) && F30(s+1) >= F33(s+1))); }
bool RA4(int s)  { return(false); }
bool VAO5(int s) { return((F35(s) > F36(s)) && (F39(s) > F40(s)) && (F42(s) < F43(s))); }
bool RA5(int s)  { return(false); }
bool VAO6(int s) { return((F45(s) > F46(s)) && (F47(s) > F48(s)) && (F51(s) < F52(s))); }
bool RA6(int s)  { return(false); }
bool VAO7(int s) { return((F55(s) > F56(s)) && (F58(s) < F59(s)) && (F60(s) > F61(s))); }
bool RA7(int s)  { return((F62(s) < F63(s) && F62(s+1) >= F63(s+1))); }
bool VAO8(int s) { return((F64(s) > F67(s)) && (F68(s) < F71(s)) && (F73(s) > F74(s))); }
bool RA8(int s)  { return(false); }
bool VAO9(int s) { return((F76(s) < F77(s)) && (F81(s) < F82(s))); }
bool RA9(int s)  { return(false); }
bool VAO10(int s) { return((F84(s) > F85(s)) && (F89(s) < F90(s))); }
bool RA10(int s)  { return(false); }
bool VAO11(int s) { return((F91(s) < F92(s)) && (F94(s) < F95(s)) && (F97(s) < F98(s))); }
bool RA11(int s)  { return(false); }
bool VAO12(int s) { return((F101(s) < F102(s)) && (F104(s) > F105(s)) && (F108(s) < F109(s))); }
bool RA12(int s)  { return(false); }
bool VAO13(int s) { return((F112(s) > F113(s)) && (F114(s) < F115(s)) && (F117(s) < F118(s)) && (F119(s) > F120(s))); }
bool RA13(int s)  { return(false); }
bool VAO14(int s) { return((F121(s) >= F124(s)) && (F126(s) < F127(s)) && (F129(s) < F130(s))); }
bool RA14(int s)  { return((F131(s) < F132(s))); }
bool VAO15(int s) { return((F134(s) <= F135(s)) && (F136(s) < F137(s)) && (F138(s) > F139(s))); }
bool RA15(int s)  { return(false); }
bool VAO16(int s) { return((F140(s) < F142(s)) && (F143(s) > F145(s)) && (F146(s) < F147(s)) && (F148(s) > F149(s)) && (F151(s) > F152(s)) && (F154(s) < F155(s))); }
bool RA16(int s)  { return((F156(s) > F157(s))); }
bool VAO17(int s) { return((F159(s) <= F162(s)) && (F163(s) > F164(s)) && (F166(s) > F167(s)) && (F168(s) > F169(s))); }
bool RA17(int s)  { return(false); }
bool VAO18(int s) { return((F170(s) <= F171(s)) && (F173(s) < F174(s)) && (F176(s) < F177(s))); }
bool RA18(int s)  { return(false); }
bool VAO19(int s) { return((F179(s) > F180(s)) && (F181(s) < F182(s)) && (F184(s) < F185(s))); }
bool RA19(int s)  { return(false); }
bool VAO20(int s) { return((F187(s) > F188(s)) && (F190(s) < F191(s)) && (F193(s) < F194(s))); }
bool RA20(int s)  { return((F195(s) < F196(s))); }

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
     }
   return(false);
  }

int Chieu(int k) { switch(k) { case 0: return(1); case 1: return(-1); case 2: return(-1); case 3: return(-1); case 4: return(-1); case 5: return(1); case 6: return(1); case 7: return(1); case 8: return(-1); case 9: return(1); case 10: return(-1); case 11: return(1); case 12: return(1); case 13: return(1); case 14: return(-1); case 15: return(1); case 16: return(1); case 17: return(1); case 18: return(1); case 19: return(1); case 20: return(-1); } return(1); }
int Giu(int k)   { switch(k) { case 0: return(500); case 1: return(500); case 2: return(3); case 3: return(8); case 4: return(10); case 5: return(20); case 6: return(5); case 7: return(10); case 8: return(5); case 9: return(12); case 10: return(12); case 11: return(8); case 12: return(6); case 13: return(3); case 14: return(4); case 15: return(5); case 16: return(4); case 17: return(5); case 18: return(6); case 19: return(10); case 20: return(6); } return(1); }
bool CoDieuKienRa(int k) { switch(k) { case 0: return(false); case 1: return(false); case 2: return(false); case 3: return(true); case 4: return(false); case 5: return(false); case 6: return(false); case 7: return(true); case 8: return(false); case 9: return(false); case 10: return(false); case 11: return(false); case 12: return(false); case 13: return(false); case 14: return(true); case 15: return(false); case 16: return(true); case 17: return(false); case 18: return(false); case 19: return(false); case 20: return(true); } return(false); }

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
   h_ma1 = iMA(_Symbol, KHUNG, 50, 0, MODE_SMA, PRICE_CLOSE);
   h_ma2 = iMA(_Symbol, KHUNG, 100, 0, MODE_SMA, PRICE_CLOSE);
   h_ma3 = iMA(_Symbol, KHUNG, 100, 0, MODE_EMA, PRICE_CLOSE);
   h_ma4 = iMA(_Symbol, KHUNG, 20, 0, MODE_EMA, PRICE_CLOSE);
   h_ma5 = iMA(_Symbol, KHUNG, 20, 0, MODE_SMA, PRICE_CLOSE);
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
