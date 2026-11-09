// V3 09/11/2026: tao custom symbol GBPCAD_HD = HistData M1 (gio EST+7, nhu Python) 2008-2018 + XM GBPCAD# M1 tu 2019. Chi o slot g12.
input string InpTen   = "GBPCAD_HD";
input string InpGoc   = "GBPCAD#";
input string InpFile  = "GBPCAD_HD_M1_2008_2018_est7.csv";
input int    InpSpread = 58;                    // diem; = spread p90 XM micro GBPCAD do 10/2026
input datetime InpNoi  = D'2030.01.01 00:00';
input datetime InpDen  = D'2026.10.11 00:00';
input bool   InpXoa   = true;
input bool   InpDungXM = false;
void Ghi(string s){ Print(s); int h=FileOpen("v3_nap_hd_log.txt",FILE_READ|FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON); if(h!=INVALID_HANDLE){FileSeek(h,0,SEEK_END);FileWriteString(h,TimeToString(TimeLocal(),TIME_DATE|TIME_SECONDS)+" "+s+"\r\n");FileClose(h);} }
void OnStart()
{
   bool custom=false;
   if(!SymbolExist(InpTen,custom))
   { if(!CustomSymbolCreate(InpTen,"v3",InpGoc)) { Ghi("CustomSymbolCreate loi "+(string)GetLastError()); TerminalClose(1); return; } Ghi("tao "+InpTen); }
   else Ghi("da co "+InpTen+" custom="+(string)custom);
   if(InpXoa) CustomRatesDelete(InpTen,0,D'2030.01.01');
   string F[]={"GBPCAD_HD_M1_2008_2018_est7.csv","GBPCAD_HD_M1_2019_2026_est7.csv"}; long tong=0;
   for(int f=0;f<ArraySize(F);f++){
   int h=FileOpen(F[f],FILE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON|FILE_SHARE_READ);
   if(h==INVALID_HANDLE){ Ghi("khong mo "+F[f]+" "+(string)GetLastError()); TerminalClose(2); return; }
   MqlRates r[]; ArrayResize(r,200000); int n=0;
   while(!FileIsEnding(h))
   {
      string d=FileReadString(h); string o[];
      if(StringSplit(d,',',o)<5) continue;
      MqlRates x; x.time=StringToTime(o[0]); x.open=StringToDouble(o[1]); x.high=StringToDouble(o[2]); x.low=StringToDouble(o[3]); x.close=StringToDouble(o[4]);
      x.tick_volume=4; x.real_volume=0; x.spread=InpSpread;
      r[n++]=x;
      if(n==200000){ if(CustomRatesUpdate(InpTen,r)<0) Ghi("update loi "+(string)GetLastError()); tong+=n; n=0; }
   }
   FileClose(h);
   if(n>0){ ArrayResize(r,n); CustomRatesUpdate(InpTen,r); tong+=n; }
   Ghi(F[f]+" xong, tong "+(string)tong); }
   Ghi("HistData nap "+(string)tong+" nen M1");
   // XM tu InpNoi, theo thang
   long tong2=0; datetime a=InpNoi;
   while(InpDungXM && a<InpDen)
   {
      MqlDateTime m; TimeToStruct(a,m); m.mon++; if(m.mon>12){m.mon=1;m.year++;} datetime b=StructToTime(m);
      MqlRates q[]; int k=-1;
      for(int t=0;t<30 && k<=0;t++){ k=CopyRates(InpGoc,PERIOD_M1,a,b-1,q); if(k<=0) Sleep(1000); }
      if(k>0){ CustomRatesUpdate(InpTen,q); tong2+=k; }
      else Ghi("XM thang "+TimeToString(a,TIME_DATE)+" khong co nen, loi "+(string)GetLastError());
      a=b;
   }
   Ghi("XM nap "+(string)tong2+" nen M1");
   MqlRates z[]; int c=CopyRates(InpTen,PERIOD_M1,D'2009.01.01',InpDen,z);
   Ghi("kiem: "+InpTen+" M1 2009->den = "+(string)c);
   Ghi("XONG");
   TerminalClose(0);
}
