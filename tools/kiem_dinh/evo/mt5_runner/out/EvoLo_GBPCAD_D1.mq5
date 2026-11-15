//+------------------------------------------------------------------+
//| EvoLo_GBPCAD_D1 - SINH TU DONG boi nhan/dich_mq5.py. KHONG SUA TAY.
//| 20 co che tu config/co_che_dsl.json, chon bang InpMaCoChe.
//|
//| Gop nhieu co che vao MOT EA co chu dich: mot luot tester ton ~138 giay
//| ma bai test that chi 0,5 giay - phan con lai la boot terminal. Chay
//| OPTIMIZATION tren InpMaCoChe thi N co che ton bang MOT lan boot.
//+------------------------------------------------------------------+
#property copyright "The Brain"
#include <Trade\Trade.mqh>

input int    InpMaCoChe = 0;      // ma co che (0..19)

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
int h_ma5 = INVALID_HANDLE;
int h_rsi0 = INVALID_HANDLE;
int h_rsi1 = INVALID_HANDLE;
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
   return(Chi(h_rsi0, s));
  }

double F6(int s)
  {
   return(10);
  }

double F7(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F8(int s)
  {
   return(Chi(h_ma0, s));
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
   return(0.85);
  }

double F12(int s)
  {
   return(Chi(h_rsi0, s));
  }

double F13(int s)
  {
   return(90);
  }

double F14(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F15(int s)
  {
   return(Chi(h_ma0, s));
  }

double F16(int s)
  {
   return(Chi(h_atr0, s));
  }

double F17(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F16(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F18(int s)
  {
   return(0.85);
  }

double F19(int s)
  {
   return(iHigh(_Symbol,KHUNG,s) - iLow(_Symbol,KHUNG,s));
  }

double F20(int s)
  {
   return(F19(s+1));
  }

double F21(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F20(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F22(int s)
  {
   return(0.15);
  }

double F23(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F24(int s)
  {
   return(iHigh(_Symbol, KHUNG, s+0));
  }

double F25(int s)
  {
   double v[]; ArrayResize(v, 5);
   for(int i = 0; i < 5; i++) v[i] = F24(s+i);
   double m = v[0]; for(int i=1;i<5;i++) if(v[i]>m) m=v[i];
   return(m);
  }

double F26(int s)
  {
   return(F25(s+1));
  }

double F27(int s)
  {
   return(Chi(h_atr0, s));
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
   return(0.5);
  }

double F30(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F31(int s)
  {
   return(iHigh(_Symbol, KHUNG, s+0));
  }

double F32(int s)
  {
   return(F31(s+2));
  }

double F33(int s)
  {
   return(Chi(h_atr0, s));
  }

double F34(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F33(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F35(int s)
  {
   return(0.5);
  }

double F36(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F37(int s)
  {
   double v[]; ArrayResize(v, 5);
   for(int i = 0; i < 5; i++) v[i] = F36(s+i);
   double t=0; for(int i=0;i<5;i++) t+=v[i]; double m=t/5.0;
   double q=0; for(int i=0;i<5;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/5.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F38(int s)
  {
   return(-1.2);
  }

double F39(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F40(int s)
  {
   return(Chi(h_ma1, s));
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
   return(0.5);
  }

double F44(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F45(int s)
  {
   return(0.25);
  }

double F46(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F47(int s)
  {
   return(F46(s+1));
  }

double F48(int s)
  {
   return(0.25);
  }

double F49(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F50(int s)
  {
   return(Chi(h_ma1, s));
  }

double F51(int s)
  {
   return(Chi(h_atr0, s));
  }

double F52(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F51(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F53(int s)
  {
   return(0.3);
  }

double F54(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F55(int s)
  {
   return(0.75);
  }

double F56(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F57(int s)
  {
   double a = F56(s+120);
   if(a == 0.0) return(0.0);
   return((F56(s) - a) / a);
  }

double F58(int s)
  {
   double v[]; ArrayResize(v, 500);
   for(int i = 0; i < 500; i++) v[i] = F57(s+i);
   int d = 0; for(int i=1;i<500;i++) if(v[i] <= v[0]) d++;
   return((double)d / 499.0);
  }

double F59(int s)
  {
   return(0.7);
  }

double F60(int s)
  {
   return(Chi(h_atr0, s));
  }

double F61(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F60(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F62(int s)
  {
   return(0.5);
  }

double F63(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F64(int s)
  {
   return(Chi(h_ma2, s));
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
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F68(int s)
  {
   double a = F67(s+120);
   if(a == 0.0) return(0.0);
   return((F67(s) - a) / a);
  }

double F69(int s)
  {
   double v[]; ArrayResize(v, 500);
   for(int i = 0; i < 500; i++) v[i] = F68(s+i);
   int d = 0; for(int i=1;i<500;i++) if(v[i] <= v[0]) d++;
   return((double)d / 499.0);
  }

double F70(int s)
  {
   return(0.3);
  }

double F71(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F72(int s)
  {
   return(0.8);
  }

double F73(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F74(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F73(s+i);
   double t=0; for(int i=0;i<20;i++) t+=v[i]; double m=t/20.0;
   double q=0; for(int i=0;i<20;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/20.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F75(int s)
  {
   return(1);
  }

double F76(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F77(int s)
  {
   return(0.2);
  }

double F78(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F79(int s)
  {
   double a = F78(s+60);
   if(a == 0.0) return(0.0);
   return((F78(s) - a) / a);
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
   return(0.75);
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
   return(0.4);
  }

double F85(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F86(int s)
  {
   return(Chi(h_ma3, s));
  }

double F87(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F88(int s)
  {
   return(Chi(h_ma3, s));
  }

double F89(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F90(int s)
  {
   return(Chi(h_ma4, s));
  }

double F91(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F92(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F93(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F92(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]<m) m=v[i];
   return(m);
  }

double F94(int s)
  {
   return(F93(s+1));
  }

double F95(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F96(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F97(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F96(s+i);
   double m = v[0]; for(int i=1;i<20;i++) if(v[i]<m) m=v[i];
   return(m);
  }

double F98(int s)
  {
   return(F97(s+1));
  }

double F99(int s)
  {
   return(Chi(h_atr0, s));
  }

double F100(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F99(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F101(int s)
  {
   return(0.7);
  }

double F102(int s)
  {
   return(Chi(h_rsi0, s));
  }

double F103(int s)
  {
   return(10);
  }

double F104(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F105(int s)
  {
   double a = F104(s+60);
   if(a == 0.0) return(0.0);
   return((F104(s) - a) / a);
  }

double F106(int s)
  {
   double v[]; ArrayResize(v, 500);
   for(int i = 0; i < 500; i++) v[i] = F105(s+i);
   int d = 0; for(int i=1;i<500;i++) if(v[i] <= v[0]) d++;
   return((double)d / 499.0);
  }

double F107(int s)
  {
   return(0.7);
  }

double F108(int s)
  {
   return(Chi(h_atr0, s));
  }

double F109(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F108(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F110(int s)
  {
   return(0.7);
  }

double F111(int s)
  {
   return(Chi(h_rsi0, s));
  }

double F112(int s)
  {
   return(70);
  }

double F113(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F114(int s)
  {
   return(0.2);
  }

double F115(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F116(int s)
  {
   double a = F115(s+120);
   if(a == 0.0) return(0.0);
   return((F115(s) - a) / a);
  }

double F117(int s)
  {
   double v[]; ArrayResize(v, 500);
   for(int i = 0; i < 500; i++) v[i] = F116(s+i);
   int d = 0; for(int i=1;i<500;i++) if(v[i] <= v[0]) d++;
   return((double)d / 499.0);
  }

double F118(int s)
  {
   return(0.75);
  }

double F119(int s)
  {
   return(Chi(h_atr0, s));
  }

double F120(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F119(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F121(int s)
  {
   return(0.5);
  }

double F122(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F123(int s)
  {
   return(0.8);
  }

double F124(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F125(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F124(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F126(int s)
  {
   return(0.3);
  }

double F127(int s)
  {
   return(Chi(h_rsi1, s));
  }

double F128(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F127(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F129(int s)
  {
   return(0.65);
  }

double F130(int s)
  {
   return(Chi(h_atr0, s));
  }

double F131(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F130(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F132(int s)
  {
   return(0.3);
  }

double F133(int s)
  {
   return(Chi(h_atr0, s));
  }

double F134(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F133(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F135(int s)
  {
   return(0.7);
  }

double F136(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F137(int s)
  {
   return(0.3);
  }

double F138(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F139(int s)
  {
   return(0.3);
  }

double F140(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F141(int s)
  {
   return(F140(s+1));
  }

double F142(int s)
  {
   return(0.3);
  }

double F143(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F144(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F143(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F145(int s)
  {
   return(0.5);
  }

double F146(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F147(int s)
  {
   return(Chi(h_ma1, s));
  }

double F148(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F149(int s)
  {
   return(0.7);
  }

double F150(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F151(int s)
  {
   return(0.25);
  }

double F152(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F153(int s)
  {
   double v[]; ArrayResize(v, 20);
   for(int i = 0; i < 20; i++) v[i] = F152(s+i);
   double t=0; for(int i=0;i<20;i++) t+=v[i]; double m=t/20.0;
   double q=0; for(int i=0;i<20;i++) q+=(v[i]-m)*(v[i]-m);
   double sd = MathSqrt(q/20.0);
   if(sd <= 0.0) return(0.0);
   return((v[0]-m)/sd);
  }

double F154(int s)
  {
   return(0);
  }

double F155(int s)
  {
   return(iHigh(_Symbol,KHUNG,s) - iLow(_Symbol,KHUNG,s));
  }

double F156(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F155(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F157(int s)
  {
   return(0.5);
  }

double F158(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F159(int s)
  {
   return(Chi(h_ma5, s));
  }

double F160(int s)
  {
   MqlDateTime d; TimeToStruct(iTime(_Symbol,KHUNG,s), d);
   return((double)d.day_of_week);
  }

double F161(int s)
  {
   return(4);
  }

double F162(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F163(int s)
  {
   return(0.75);
  }

double F164(int s)
  {
   return(Chi(h_atr0, s));
  }

double F165(int s)
  {
   double v[]; ArrayResize(v, 250);
   for(int i = 0; i < 250; i++) v[i] = F164(s+i);
   int d = 0; for(int i=1;i<250;i++) if(v[i] <= v[0]) d++;
   return((double)d / 249.0);
  }

double F166(int s)
  {
   return(0.7);
  }

double F167(int s)
  {
   return(iLow(_Symbol, KHUNG, s+0));
  }

double F168(int s)
  {
   return(Chi(h_ma3, s));
  }

double F169(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F170(int s)
  {
   return(Chi(h_ma3, s));
  }

double F171(int s)
  {
   return(Chi(h_ma5, s));
  }

double F172(int s)
  {
   double a = F171(s+10);
   if(a == 0.0) return(0.0);
   return((F171(s) - a) / a);
  }

double F173(int s)
  {
   return(0);
  }

double F174(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F175(int s)
  {
   double v[]; ArrayResize(v, 5);
   for(int i = 0; i < 5; i++) v[i] = F174(s+i);
   double t = 0; for(int i=0;i<5;i++) t += v[i];
   return(t / 5.0);
  }

double F176(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F175(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F177(int s)
  {
   return(0.4);
  }

double F178(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F179(int s)
  {
   return(Chi(h_ma3, s));
  }

double F180(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F181(int s)
  {
   return(0.3);
  }

double F182(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F183(int s)
  {
   return(F182(s+1));
  }

double F184(int s)
  {
   return(0.3);
  }

double F185(int s)
  {
   return((double)iTickVolume(_Symbol,KHUNG,s));
  }

double F186(int s)
  {
   double v[]; ArrayResize(v, 100);
   for(int i = 0; i < 100; i++) v[i] = F185(s+i);
   int d = 0; for(int i=1;i<100;i++) if(v[i] <= v[0]) d++;
   return((double)d / 99.0);
  }

double F187(int s)
  {
   return(0.4);
  }

double F188(int s)
  {
   return(iClose(_Symbol, KHUNG, s+0));
  }

double F189(int s)
  {
   double a = F188(s+120);
   if(a == 0.0) return(0.0);
   return((F188(s) - a) / a);
  }

double F190(int s)
  {
   return(0);
  }

double F191(int s)
  {
   double h=iHigh(_Symbol,KHUNG,s), l=iLow(_Symbol,KHUNG,s);
   if(h - l <= 0.0) return(0.5);
   return((iClose(_Symbol,KHUNG,s) - l) / (h - l));
  }

double F192(int s)
  {
   return(0.8);
  }


//--- vao/ra cua tung co che
bool VAO0(int s) { return((F1(s) >= F2(s))); }
bool RA0(int s)  { return(false); }
bool VAO1(int s) { return((F3(s) >= F4(s))); }
bool RA1(int s)  { return(false); }
bool VAO2(int s) { return((F5(s) < F6(s)) && (F7(s) > F8(s)) && (F10(s) < F11(s))); }
bool RA2(int s)  { return(false); }
bool VAO3(int s) { return((F12(s) > F13(s)) && (F14(s) < F15(s)) && (F17(s) < F18(s))); }
bool RA3(int s)  { return(false); }
bool VAO4(int s) { return((F21(s) < F22(s)) && (F23(s) > F26(s)) && (F28(s) < F29(s))); }
bool RA4(int s)  { return(false); }
bool VAO5(int s) { return((F30(s) > F32(s)) && (F34(s) < F35(s))); }
bool RA5(int s)  { return(false); }
bool VAO6(int s) { return((F37(s) < F38(s)) && (F39(s) > F40(s)) && (F42(s) < F43(s))); }
bool RA6(int s)  { return(false); }
bool VAO7(int s) { return((F44(s) < F45(s)) && (F47(s) < F48(s)) && (F49(s) > F50(s)) && (F52(s) > F53(s))); }
bool RA7(int s)  { return((F54(s) > F55(s))); }
bool VAO8(int s) { return((F58(s) > F59(s)) && (F61(s) < F62(s)) && (F63(s) > F64(s))); }
bool RA8(int s)  { return((F65(s) < F66(s) && F65(s+1) >= F66(s+1))); }
bool VAO9(int s) { return((F69(s) < F70(s)) && (F71(s) > F72(s)) && (F74(s) > F75(s))); }
bool RA9(int s)  { return((F76(s) < F77(s))); }
bool VAO10(int s) { return((F80(s) > F81(s)) && (F83(s) < F84(s)) && (F85(s) < F86(s)) && (F87(s) > F88(s))); }
bool RA10(int s)  { return((F89(s) < F90(s))); }
bool VAO11(int s) { return((F91(s) < F94(s)) && (F95(s) > F98(s)) && (F100(s) > F101(s))); }
bool RA11(int s)  { return(false); }
bool VAO12(int s) { return((F102(s) < F103(s)) && (F106(s) > F107(s)) && (F109(s) < F110(s))); }
bool RA12(int s)  { return((F111(s) > F112(s))); }
bool VAO13(int s) { return((F113(s) < F114(s)) && (F117(s) > F118(s)) && (F120(s) < F121(s))); }
bool RA13(int s)  { return(false); }
bool VAO14(int s) { return((F122(s) > F123(s)) && (F125(s) < F126(s)) && (F128(s) > F129(s)) && (F131(s) > F132(s)) && (F134(s) < F135(s))); }
bool RA14(int s)  { return((F136(s) < F137(s))); }
bool VAO15(int s) { return((F138(s) < F139(s)) && (F141(s) < F142(s)) && (F144(s) < F145(s)) && (F146(s) > F147(s))); }
bool RA15(int s)  { return((F148(s) > F149(s))); }
bool VAO16(int s) { return((F150(s) < F151(s)) && (F153(s) < F154(s)) && (F156(s) < F157(s)) && (F158(s) > F159(s))); }
bool RA16(int s)  { return(false); }
bool VAO17(int s) { return((F160(s) >= F161(s)) && (F162(s) > F163(s)) && (F165(s) > F166(s))); }
bool RA17(int s)  { return(false); }
bool VAO18(int s) { return((F167(s) < F168(s)) && (F169(s) > F170(s)) && (F172(s) > F173(s)) && (F176(s) < F177(s))); }
bool RA18(int s)  { return((F178(s) < F179(s))); }
bool VAO19(int s) { return((F180(s) < F181(s)) && (F183(s) < F184(s)) && (F186(s) < F187(s)) && (F189(s) > F190(s))); }
bool RA19(int s)  { return((F191(s) > F192(s))); }

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
     }
   return(false);
  }

int Chieu(int k) { switch(k) { case 0: return(1); case 1: return(-1); case 2: return(1); case 3: return(-1); case 4: return(1); case 5: return(1); case 6: return(1); case 7: return(1); case 8: return(1); case 9: return(-1); case 10: return(1); case 11: return(1); case 12: return(1); case 13: return(1); case 14: return(-1); case 15: return(1); case 16: return(1); case 17: return(-1); case 18: return(1); case 19: return(1); } return(1); }
int Giu(int k)   { switch(k) { case 0: return(500); case 1: return(500); case 2: return(3); case 3: return(3); case 4: return(5); case 5: return(6); case 6: return(3); case 7: return(3); case 8: return(30); case 9: return(4); case 10: return(15); case 11: return(5); case 12: return(4); case 13: return(12); case 14: return(4); case 15: return(4); case 16: return(4); case 17: return(2); case 18: return(5); case 19: return(4); } return(1); }
bool CoDieuKienRa(int k) { switch(k) { case 0: return(false); case 1: return(false); case 2: return(false); case 3: return(false); case 4: return(false); case 5: return(false); case 6: return(false); case 7: return(true); case 8: return(true); case 9: return(true); case 10: return(true); case 11: return(false); case 12: return(true); case 13: return(false); case 14: return(true); case 15: return(true); case 16: return(false); case 17: return(false); case 18: return(true); case 19: return(true); } return(false); }

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
   h_ma0 = iMA(_Symbol, KHUNG, 200, 0, MODE_EMA, PRICE_CLOSE);
   h_ma1 = iMA(_Symbol, KHUNG, 200, 0, MODE_SMA, PRICE_CLOSE);
   h_ma2 = iMA(_Symbol, KHUNG, 50, 0, MODE_EMA, PRICE_CLOSE);
   h_ma3 = iMA(_Symbol, KHUNG, 20, 0, MODE_EMA, PRICE_CLOSE);
   h_ma4 = iMA(_Symbol, KHUNG, 50, 0, MODE_SMA, PRICE_CLOSE);
   h_ma5 = iMA(_Symbol, KHUNG, 100, 0, MODE_EMA, PRICE_CLOSE);
   h_rsi0 = iRSI(_Symbol, KHUNG, 2, PRICE_CLOSE);
   h_rsi1 = iRSI(_Symbol, KHUNG, 14, PRICE_CLOSE);
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
