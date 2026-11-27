//+------------------------------------------------------------------+
//| LichNYSE.mqh - ngay nghi va ngay dong cua som cua NYSE (27/11/2026)|
//| Dung chung cho EA SP500_*. Gio NY tinh tu gio server XM (EET/EEST).|
//+------------------------------------------------------------------+
int ChuNhatThu(int y,int m,int k){ MqlDateTime t; t.year=y; t.mon=m; t.day=1; t.hour=0; t.min=0; t.sec=0;
   datetime d=StructToTime(t); TimeToStruct(d,t); int first=1+((7-t.day_of_week)%7);
   if(k>0) return first+7*(k-1); int dim=(m==2)?((y%4==0)?29:28):((m==4||m==6||m==9||m==11)?30:31);
   int last=first; while(last+7<=dim) last+=7; return last; }
int ThuTrongThang(int y,int m,int wd,int k){ // wd: 0=CN..6=T7; k>0 thu k, k=-1 cuoi
   MqlDateTime t; t.year=y; t.mon=m; t.day=1; t.hour=0;t.min=0;t.sec=0; datetime d=StructToTime(t); TimeToStruct(d,t);
   int first=1+((wd-t.day_of_week+7)%7); if(k>0) return first+7*(k-1);
   int dim=(m==2)?((y%4==0)?29:28):((m==4||m==6||m==9||m==11)?30:31); int last=first; while(last+7<=dim) last+=7; return last; }
bool MyDST(MqlDateTime &t){ int a=ChuNhatThu(t.year,3,2), b=ChuNhatThu(t.year,11,1);
   if(t.mon>3&&t.mon<11) return true; if(t.mon==3) return t.day>=a; if(t.mon==11) return t.day<b; return false; }
bool EuDST(MqlDateTime &t){ int a=ChuNhatThu(t.year,3,-1), b=ChuNhatThu(t.year,10,-1);
   if(t.mon>3&&t.mon<10) return true; if(t.mon==3) return t.day>=a; if(t.mon==10) return t.day<b; return false; }
int LechGio(MqlDateTime &t){ return (MyDST(t)==EuDST(t))?0:-60; }
int PhutNY(datetime s){ MqlDateTime t; TimeToStruct(s,t); return t.hour*60+t.min - 7*60 - LechGio(t); }
datetime NgayTao(int y,int m,int d){ MqlDateTime t; t.year=y;t.mon=m;t.day=d;t.hour=0;t.min=0;t.sec=0; return StructToTime(t); }
datetime PhucSinh(int y){ int a=y%19,b=y/100,c=y%100,d=b/4,e=b%4,f=(b+8)/25,g=(b-f+1)/3,h=(19*a+b-d-g+15)%30,i=c/4,k=c%4,l=(32+2*e+2*i-h-k)%7,m=(a+11*h+22*l)/451;
   int mon=(h+l-7*m+114)/31, day=((h+l-7*m+114)%31)+1; return NgayTao(y,mon,day); }
datetime QuanSat(datetime d){ MqlDateTime t; TimeToStruct(d,t); if(t.day_of_week==6) return d-86400; if(t.day_of_week==0) return d+86400; return d; }
bool NgayNghiNYSE(datetime x){
   MqlDateTime t; TimeToStruct(x,t); if(t.day_of_week==0||t.day_of_week==6) return true;
   datetime d=NgayTao(t.year,t.mon,t.day); int y=t.year;
   // Tet duong: 1/1, CN -> T2 2/1; T7 -> khong nghi bu
   datetime nd=NgayTao(y,1,1); MqlDateTime u; TimeToStruct(nd,u); if(u.day_of_week==0) nd+=86400; if(u.day_of_week!=6 && d==nd) return true;
   if(d==NgayTao(y,1,ThuTrongThang(y,1,1,3))) return true;          // MLK
   if(d==NgayTao(y,2,ThuTrongThang(y,2,1,3))) return true;          // Presidents
   if(d==PhucSinh(y)-2*86400) return true;                           // Good Friday
   if(d==NgayTao(y,5,ThuTrongThang(y,5,1,-1))) return true;         // Memorial
   if(y>=2022 && d==QuanSat(NgayTao(y,6,19))) return true;           // Juneteenth
   if(d==QuanSat(NgayTao(y,7,4))) return true;                       // Doc lap
   if(d==NgayTao(y,9,ThuTrongThang(y,9,1,1))) return true;          // Labor
   if(d==NgayTao(y,11,ThuTrongThang(y,11,4,4))) return true;        // Thanksgiving
   if(d==QuanSat(NgayTao(y,12,25))) return true;                     // Giang sinh
   if(d==NgayTao(2018,12,5) || d==NgayTao(2025,1,9)) return true;    // tang le TT Bush, Carter
   return false; }
// Phut NY dong cua: 960 binh thuong, 780 (13:00) ngay dong som
int PhutDongNY(datetime x){ MqlDateTime t; TimeToStruct(x,t); int y=t.year; datetime d=NgayTao(y,t.mon,t.day);
   if(d==NgayTao(y,11,ThuTrongThang(y,11,4,4))+86400) return 780;   // sau Thanksgiving
   if(t.mon==12 && t.day==24 && !NgayNghiNYSE(d)) return 780;
   if(t.mon==7 && t.day==3 && !NgayNghiNYSE(d)) return 780;
   return 960; }
datetime NgayGDKeTiep(datetime d){ datetime x=d+86400; while(NgayNghiNYSE(x)) x+=86400; return x; }
