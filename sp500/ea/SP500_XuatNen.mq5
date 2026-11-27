//+------------------------------------------------------------------+
//| SP500_XuatNen.mq5 - xuat nen M5 cua XM (time server, OHLC, spread)|
//| Chay trong tester (model 2) de lay lich su gia XM cho Python.     |
//+------------------------------------------------------------------+
#property strict
int h=INVALID_HANDLE; datetime last=0;
int OnInit(){ h=FileOpen("sp500_xm_m5_"+_Symbol+".csv",FILE_WRITE|FILE_CSV|FILE_COMMON|FILE_ANSI,','); 
   if(h!=INVALID_HANDLE) FileWrite(h,"time","open","high","low","close","tick_volume","spread"); return INIT_SUCCEEDED; }
void OnTick(){ MqlRates r[]; if(CopyRates(_Symbol,PERIOD_M5,1,1,r)!=1) return; if(r[0].time==last) return; last=r[0].time;
   FileWrite(h,TimeToString(r[0].time,TIME_DATE|TIME_MINUTES),DoubleToString(r[0].open,2),DoubleToString(r[0].high,2),DoubleToString(r[0].low,2),DoubleToString(r[0].close,2),(long)r[0].tick_volume,r[0].spread); }
void OnDeinit(const int reason){ if(h!=INVALID_HANDLE) FileClose(h); }
