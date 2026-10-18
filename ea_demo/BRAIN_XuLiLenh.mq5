//+------------------------------------------------------------------+
//| BRAIN_XuLiLenh.mq5 - BO MAY XU LI LENH theo cach chu du an danh (17/10/2026)
//|
//| Chu du an: "phi giao dich, tinh diem gia chay, spread, cac cach entry, dca xu li lenh khi sai,
//| trailing vi the co loi, hedging can bang lenh" - day la phan quyet dinh tien, phai chay tren MT5
//| de CHINH SAN tinh diem / spread / swap / hoa hong (Python tung doan sai point o 214/407 ma XM).
//|
//| Mot RO lenh moi chieu (ro MUA, ro BAN), quan li bang GIA (don vi gia cua ma, vd US500 "5 gia")
//| hoac boi so ATR cua khung tin hieu:
//|   VAO       tin hieu nen DA DONG (MRZ z-score / RSI / Donchian) hoac KHONG tin hieu (PMG: luon co ro)
//|   DCA       nhoi NGHICH khi gia di nguoc 1 buoc (buoc gian dan x g), hoac nhoi THUAN theo chieu gia chay
//|   LOT       deu / tang tuyen tinh / nhan he so r theo tang
//|   TP RO     gia von binh quan +/- TP (gia hoac ATR)
//|   TRAILING  khi gia vuot gia von + kich hoat: bam dinh, tra lai 'khoang' thi dong ca ro
//|   HEDGE     ro lo tha noi >= X % so du: mo lenh NGUOC cung khoi luong x ti le (khoa) - mo khoa khi
//|             gia hoi tu cuc tri - GO: tong ro + hedge >= muc tien thi dong het
//|   BAO VE    khong nhoi/hedge khi margin level < muc; khong mo lenh trong gio cam (doi ngay spread gian)
//|             hoac khi spread > tran; cat lo ro tuy chon (0 = khong SL, dung cach chu du an danh)
//| Ghi log CSV (Common\Files) cung dinh dang BRAIN_V24 -> do_phi_xm.py doc duoc phi that.
//| 19/10/2026: VAO_CSV - lenh vao doc tu file CSV (MQL5\Files hoac Common\Files khi InpCsvChung, de chay Tester):
//|   dong dau la tieu de; moi dong `thoi_gian,ma,chieu,gia,nguon[,lot]` (thoi_gian gio SERVER "YYYY.MM.DD HH:MM:SS",
//|   chieu 1 mua / -1 ban, gia = gia BID tham khao, lot trong = InpLot0) - cung dinh dang LenhVao cua Python
//|   (nhan/ong_dan.xuat_csv_vao). Quan li (DCA / nhoi / trailing / hedge khoa-go / TP ro) giu nguyen; them tham so
//|   theo PHAN CUA GIA (InpTPPct, InpBuocPct, InpTrailKichPct, InpTrailKhoangPct, InpMoKhoaPct) de khop nhan/tai_khoan.
//|   Lenh vuot SYMBOL_VOLUME_MAX: TACH thanh nhieu lenh (toi da 50), nhu chay_tk Python. Moi lenh ro mang tag "#tang".
//|   VAO_CSV ghi them <InpFileCsv>_lenh_mt5.csv (tung deal, co position id) va <InpFileCsv>_gia.csv (nen InpTF) de
//|   ong_dan.py doc_mt5 doi chieu voi Python tren cung CSV va cung gia.
//| BACKTEST / DEMO. Khong phai loi khuyen dau tu.
//+------------------------------------------------------------------+
#property copyright "brain2"
#property version   "1.10"
#include <Trade/Trade.mqh>

enum ENUM_VAO   { VAO_KHONG = 0, VAO_MRZ = 1, VAO_RSI = 2, VAO_DONCHIAN = 3, VAO_CSV = 4 };
enum ENUM_NHOI  { NHOI_TAT = 0, NHOI_NGHICH = 1, NHOI_THUAN = 2 };
enum ENUM_LOT   { LOT_DEU = 0, LOT_TUYEN_TINH = 1, LOT_NHAN = 2 };

input group "VAO LENH"
input ENUM_VAO        InpVao          = VAO_MRZ;   // tin hieu vao (nen DA DONG cua InpTF)
input ENUM_TIMEFRAMES InpTF           = PERIOD_D1; // khung tin hieu + ATR
input int             InpN            = 50;        // chu ky MRZ / Donchian
input double          InpNguongZ      = 2.0;       // MRZ: |z| vao lenh
input double          InpRsiThap      = 30;        // RSI: mua khi <
input double          InpRsiCao       = 70;        // RSI: ban khi >
input int             InpChieuKhongTin = 1;        // VAO_KHONG: 1 chi mua, -1 chi ban, 0 ca hai
input int             InpChoNen       = 0;         // so nen InpTF cho sau khi dong ro moi mo ro moi
input double          InpLot0         = 0.01;      // lot tang dau
input string          InpFileCsv      = "";        // VAO_CSV: ten file lenh vao (vd brain2\\od_x_vao.csv)
input bool            InpCsvChung     = true;      // VAO_CSV: doc tu Common\Files (Tester) thay vi MQL5\Files
input string          InpCsvMa        = "";        // VAO_CSV: chi lay dong co cot ma = gia tri nay ("" = moi dong)
input int             InpCsvTreGiay   = 3600;      // VAO_CSV: bo lenh tre hon X giay so voi thoi_gian (vd nen dong cua)
input bool            InpXuatGia      = true;      // VAO_CSV: OnDeinit ghi nen InpTF + lenh MT5 de doi chieu

input group "DCA / NHOI"
input ENUM_NHOI       InpNhoi         = NHOI_NGHICH;
input double          InpBuocGia      = 0;         // buoc nhoi (don vi GIA); 0 -> dung InpBuocATR
input double          InpBuocATR      = 1.0;       // buoc nhoi (x ATR14 luc mo ro)
input double          InpGianBuoc     = 1.0;       // buoc tang k = buoc x g^k (1 = deu)
input ENUM_LOT        InpKieuLot      = LOT_DEU;
input double          InpHeSoLot      = 1.5;       // LOT_NHAN: lot_k = lot0 x r^k
input int             InpMaxTang      = 5;         // so lenh toi da moi ro (ke ca lenh dau)
input double          InpBuocPct      = 0;         // >0: muc nhoi k = gia lenh dau x (1 - chieu x pct x k) (nhu Python)

input group "CHOT RO"
input double          InpTPGia        = 0;         // TP tu gia von binh quan (GIA); 0 -> InpTPATR
input double          InpTPATR        = 0.5;       // TP (x ATR14 luc mo ro); 0 = tat (chi trailing/go)
input double          InpTrailKichGia = 0;         // trailing bat khi gia vuot gia von + X (GIA); 0 -> ATR
input double          InpTrailKichATR = 1.0;       // (x ATR); 0 = tat trailing
input double          InpTrailKhoangGia = 0;       // tra lai X tu dinh thi dong ro (GIA); 0 -> ATR
input double          InpTrailKhoangATR = 0.5;     // (x ATR)
input int             InpGiuToiDaNen  = 0;         // dong ro sau N nen InpTF (0 = gong vo han)
input double          InpTPPct        = 0;         // >0: TP = gia von x pct (thang InpTPGia/ATR)
input double          InpTrailKichPct = 0;         // >0: trailing bat khi lai >= gia von x pct
input double          InpTrailKhoangPct = 0;       // trailing: dong khi gia ve dinh x (1 -/+ pct)

input group "HEDGE / GO LENH"
input double          InpHedgeKhiLoPct = 0;        // ro lo tha noi >= X % so du -> khoa (0 = tat hedge)
input double          InpHedgeTiLe    = 1.0;       // khoi luong hedge = tong lot ro x ti le
input double          InpMoKhoaGia    = 0;         // mo khoa: dong hedge khi gia hoi X tu cuc tri (GIA); 0 -> ATR
input double          InpMoKhoaATR    = 1.0;       // (x ATR); 0 = khong tu mo khoa
input double          InpGoTien       = 0;         // GO: ro + hedge >= X (tien te tk) -> dong het
input int             InpHedgeMaxLan  = 3;         // so lan khoa toi da moi ro
input double          InpMoKhoaPct    = 0;         // >0: mo khoa khi gia hoi cuc tri x pct (thang InpMoKhoaGia/ATR)
input bool            InpKhoaLaiKhongMoc = false;  // true: khoa lai ngay khi lo du nguong (nhu Python, khong cho vuot moc)

input group "BAO VE TAI KHOAN"
input double          InpMarginMin    = 300;       // khong nhoi / hedge khi margin level < X % (0 = tat)
input double          InpCatLoPct     = 0;         // cat ca ro (+hedge) khi lo >= X % so du (0 = khong SL)
input int             InpGioCamTu     = 23;        // gio server bat dau cam MO lenh (doi ngay, spread gian)
input int             InpGioCamDen    = 2;         // ... den gio nay (cam tu <= gio < den, vong qua 0h)
input double          InpSpreadMaxGia = 0;         // khong mo lenh khi spread > X (GIA); 0 = tat
input long            InpMagic        = 2026101701;
input string          InpFileLog      = "brain2_xu_li_lenh_log.csv";
input bool            InpLogChung     = true;      // ghi vao Common\Files (lay duoc ca khi chay Tester)

CTrade   trade;
int      h_atr = INVALID_HANDLE, h_rsi = INVALID_HANDLE, h_ma = INVALID_HANDLE, h_sd = INVALID_HANDLE;
datetime g_nen = 0;
bool     g_hedging = false;
// thong ke cuoi ky (in ra log + Journal)
int      g_n_cu[2] = {0, 0};   // so lenh ro lan doc truoc (de biet ro vua dong het)
int      g_so_ro = 0, g_tang_max = 0, g_so_khoa = 0, g_so_go = 0, g_so_cat = 0, g_so_trail = 0, g_so_tp = 0, g_so_het_gio = 0;
// VAO_CSV
datetime g_csv_t[];
int      g_csv_c[];
double   g_csv_lot[];
int      g_csv_n = 0, g_csv_i = 0, g_csv_bo_tre = 0, g_csv_bo_co_ro = 0, g_so_tach = 0;
datetime g_t_dau = 0;
bool DocCsv();
void ChayCsv();
void GhiLenhMt5(string s, bool moi = false);
void XuatGia();

struct Ro
{
   int      n;          // so lenh ro
   double   lot;        // tong lot
   double   gia_tb;     // gia von binh quan (theo lot)
   double   loi;        // lai/lo tha noi (profit + swap)
   double   gia_cuoi;   // gia lenh moi nhat
   datetime t_dau;      // gio lenh dau
   int      n_hedge;    // so lenh hedge dang mo cua ro nay
   double   lot_hedge;
   double   loi_hedge;
   int      tang;       // so TANG (lenh tach vi SYMBOL_VOLUME_MAX cung tang = 1 tang)
   double   gia_dau;    // gia lenh dau ro (muc DCA theo phan cua gia)
};

string Tag(int chieu)   { return chieu > 0 ? "XL_B" : "XL_S"; }     // lenh ro
string TagH(int chieu)  { return chieu > 0 ? "XL_HB" : "XL_HS"; }   // lenh hedge CUA ro do (chieu nguoc)
string TagT(int chieu, int k) { return Tag(chieu) + "#" + IntegerToString(k); }   // lenh ro, tang k (0 = lenh dau)
int    TangCua(string c)                                              // "XL_B#3" -> 3; khong co '#' -> -1
{
   int i = StringFind(c, "#");
   if(i < 0) return -1;
   return (int)StringToInteger(StringSubstr(c, i + 1));
}
string GV(int chieu, string k) { return StringFormat("xl_%I64d_%s_%s_%s", InpMagic, _Symbol, chieu > 0 ? "B" : "S", k); }
double GVLay(string ten, double mac_dinh) { return GlobalVariableCheck(ten) ? GlobalVariableGet(ten) : mac_dinh; }

void GhiLog(string s)
{
   int co = FILE_READ | FILE_WRITE | FILE_CSV | FILE_ANSI | FILE_SHARE_READ | (InpLogChung ? FILE_COMMON : 0);
   int h = FileOpen(InpFileLog, co, ';');
   if(h == INVALID_HANDLE) return;
   FileSeek(h, 0, SEEK_END);
   FileWriteString(h, s + "\r\n");
   FileClose(h);
}

double ChuanLot(double v)
{
   double st = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP), mn = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), mx = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(st > 0) v = MathFloor(v / st + 1e-9) * st;
   return MathMax(mn, MathMin(mx, v));
}

double LamTronLot(double v)                     // nhu ChuanLot nhung KHONG chan tran (de tach lenh)
{
   double st = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP), mn = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   if(st > 0) v = MathFloor(v / st + 1e-9) * st;
   return MathMax(mn, v);
}

double Lay1(int h, int buf = 0)
{
   double b[];
   if(h == INVALID_HANDLE || CopyBuffer(h, buf, 1, 1, b) != 1) return EMPTY_VALUE;
   return b[0];
}

bool DocRo(int chieu, Ro &r)
{
   r.n = 0; r.lot = 0; r.gia_tb = 0; r.loi = 0; r.gia_cuoi = 0; r.t_dau = 0; r.n_hedge = 0; r.lot_hedge = 0; r.loi_hedge = 0;
   r.tang = 0; r.gia_dau = 0;
   datetime t_moi = 0; double tong = 0; int k_max = -1; bool co_cu = false;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol || PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      string c = PositionGetString(POSITION_COMMENT);
      double v = PositionGetDouble(POSITION_VOLUME), p = PositionGetDouble(POSITION_PRICE_OPEN);
      double l = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
      datetime tt = (datetime)PositionGetInteger(POSITION_TIME);
      if(StringFind(c, TagH(chieu)) == 0) { r.n_hedge++; r.lot_hedge += v; r.loi_hedge += l; continue; }
      if(StringFind(c, Tag(chieu)) != 0) continue;
      r.n++; r.lot += v; tong += v * p; r.loi += l;
      if(tt >= t_moi) { t_moi = tt; r.gia_cuoi = p; }
      if(r.t_dau == 0 || tt < r.t_dau) { r.t_dau = tt; r.gia_dau = p; }
      int k = TangCua(c);
      if(k < 0) co_cu = true; else if(k > k_max) k_max = k;
   }
   if(r.lot > 0) r.gia_tb = tong / r.lot;
   r.tang = co_cu ? r.n : k_max + 1;               // lenh cu khong tag tang -> dem lenh nhu truoc
   return r.n > 0;
}

void DongHet(int chieu, bool ca_hedge, string ly_do)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol || PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      string c = PositionGetString(POSITION_COMMENT);
      bool la_ro = StringFind(c, Tag(chieu)) == 0, la_h = StringFind(c, TagH(chieu)) == 0;
      if(la_ro || (ca_hedge && la_h)) trade.PositionClose(t);
   }
   GhiLog(StringFormat("%s;%s;dong_ro_%s;0;0;%.5f;%.5f;%d;0;0;0;%s", TimeToString(TimeCurrent()), _Symbol, chieu > 0 ? "mua" : "ban",
          SymbolInfoDouble(_Symbol, SYMBOL_BID), SymbolInfoDouble(_Symbol, SYMBOL_ASK), (int)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD), ly_do));
}

void DongHedge(int chieu)
{
   double tich = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol || PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      if(StringFind(PositionGetString(POSITION_COMMENT), TagH(chieu)) == 0)
      {
         tich += PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
         trade.PositionClose(t);
      }
   }
   // lai/lo DA CHOT cua lenh khoa thuoc ro nay (nhu r.tich cua Python) -> GO tinh ca phan nay
   string gt = GV(chieu, "tich");
   GlobalVariableSet(gt, GVLay(gt, 0) + tich);
}

bool GioCam()
{
   if(InpGioCamTu == InpGioCamDen) return false;
   MqlDateTime d; TimeToStruct(TimeCurrent(), d);
   if(InpGioCamTu < InpGioCamDen) return d.hour >= InpGioCamTu && d.hour < InpGioCamDen;
   return d.hour >= InpGioCamTu || d.hour < InpGioCamDen;       // vong qua 0h, vd 23 -> 2
}

bool DuocMo()
{
   if(GioCam()) return false;
   double sp = SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(InpSpreadMaxGia > 0 && sp > InpSpreadMaxGia) return false;
   return true;
}

bool MarginDu()
{
   if(InpMarginMin <= 0) return true;
   double ml = AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);
   return ml <= 0 || ml >= InpMarginMin;            // 0 = chua dung margin
}

bool Mo1(int chieu, double lot, string tag)
{
   bool ok = chieu > 0 ? trade.Buy(lot, _Symbol, 0, 0, 0, tag) : trade.Sell(lot, _Symbol, 0, 0, 0, tag);
   return ok && (trade.ResultRetcode() == TRADE_RETCODE_DONE || trade.ResultRetcode() == TRADE_RETCODE_PLACED);
}

// mo `lot`; vuot SYMBOL_VOLUME_MAX -> TACH thanh n lenh (n <= 50, nhu nhan/tai_khoan.chay_tk), cung tag
bool Mo(int chieu, double lot, string tag)
{
   double mx = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX), mn = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   lot = LamTronLot(lot);
   if(mx <= 0 || lot <= mx + 1e-9) return Mo1(chieu, ChuanLot(lot), tag);
   int n = (int)MathCeil(lot / mx - 1e-9);
   if(n > 50) { GhiLog(StringFormat("%s;%s;tu_choi_lot_max;%.2f;0;0;0;0;0;0;0;%s", TimeToString(TimeCurrent()), _Symbol, lot, tag)); return false; }
   double con = lot;
   g_so_tach++;
   for(int i = 0; i < n; i++)
   {
      double p = MathMin(con, mx);
      con = NormalizeDouble(con - p, 8);
      if(p < mn - 1e-9) break;
      if(!Mo1(chieu, ChuanLot(p), tag)) return false;
   }
   return true;
}

double Lot0Ro(int chieu) { return GVLay(GV(chieu, "lot0"), InpLot0); }   // lot dau RO (VAO_CSV co the khac InpLot0)

double LotTang(int k, int chieu = 0)          // k = 0 la lenh dau
{
   double l0 = chieu == 0 ? InpLot0 : Lot0Ro(chieu);
   if(InpKieuLot == LOT_TUYEN_TINH) return l0 * (k + 1);
   if(InpKieuLot == LOT_NHAN)       return l0 * MathPow(InpHeSoLot, k);
   return l0;
}

double KhoangGia(double gia, double atr_x, double atr) { return gia > 0 ? gia : atr_x * atr; }

int TinHieu()
{
   if(InpVao == VAO_KHONG) return 2;               // luon co ro (chieu theo InpChieuKhongTin)
   if(InpVao == VAO_RSI)
   {
      double r = Lay1(h_rsi);
      if(r == EMPTY_VALUE) return 0;
      return r < InpRsiThap ? 1 : (r > InpRsiCao ? -1 : 0);
   }
   if(InpVao == VAO_MRZ)
   {
      double m = Lay1(h_ma), s = Lay1(h_sd), c = iClose(_Symbol, InpTF, 1);
      if(m == EMPTY_VALUE || s == EMPTY_VALUE || s <= 0) return 0;
      double z = (c - m) / s;
      return z < -InpNguongZ ? 1 : (z > InpNguongZ ? -1 : 0);
   }
   // DONCHIAN: dong cua nen vua dong pha dinh/day N nen truoc do
   int ic = iHighest(_Symbol, InpTF, MODE_HIGH, InpN, 2), it = iLowest(_Symbol, InpTF, MODE_LOW, InpN, 2);
   if(ic < 0 || it < 0) return 0;
   double c1 = iClose(_Symbol, InpTF, 1);
   if(c1 > iHigh(_Symbol, InpTF, ic)) return 1;
   if(c1 < iLow(_Symbol, InpTF, it)) return -1;
   return 0;
}

// ---- quan li MOT ro, goi moi tick
void QuanLi(int chieu)
{
   Ro r;
   bool co = DocRo(chieu, r);
   if(!co)
   {
      if(r.n_hedge > 0) DongHedge(chieu);          // hedge mo coi (ro da dong) -> dong
      return;
   }
   string ga = GV(chieu, "atr");
   double atr = GlobalVariableCheck(ga) ? GlobalVariableGet(ga) : Lay1(h_atr);
   if((atr == EMPTY_VALUE || atr <= 0) && InpVao != VAO_CSV) return;
   if(atr == EMPTY_VALUE || atr < 0) atr = 0;      // VAO_CSV: tham so theo phan cua gia, khong can ATR
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double gia_thoat = chieu > 0 ? bid : ask, gia_vao = chieu > 0 ? ask : bid;
   double lai_gia = chieu * (gia_thoat - r.gia_tb);                     // gia da chay co loi tu gia von (don vi gia)
   double tich = GVLay(GV(chieu, "tich"), 0);              // lai/lo da chot cua lenh khoa
   double tong = r.loi + r.loi_hedge + tich, so_du = AccountInfoDouble(ACCOUNT_BALANCE);
   if(r.tang > g_tang_max) g_tang_max = r.tang;

   // 1) cat lo tuy chon
   if(InpCatLoPct > 0 && tong <= -InpCatLoPct / 100.0 * so_du) { DongHet(chieu, true, "cat_lo"); g_so_cat++; return; }
   // 2) giu toi da
   if(InpGiuToiDaNen > 0 && iBarShift(_Symbol, InpTF, r.t_dau, false) >= InpGiuToiDaNen) { DongHet(chieu, true, "het_gio"); g_so_het_gio++; return; }

   if(r.n_hedge > 0)
   {
      // 3) dang KHOA: go khi tong >= muc; mo khoa khi gia hoi tu cuc tri
      if(tong >= InpGoTien) { DongHet(chieu, true, "go"); g_so_go++; return; }
      string gx = GV(chieu, "cuc_tri");
      double ct = GVLay(gx, gia_thoat);
      ct = chieu > 0 ? MathMin(ct, gia_thoat) : MathMax(ct, gia_thoat);
      GlobalVariableSet(gx, ct);
      double mk = InpMoKhoaPct > 0 ? InpMoKhoaPct * ct : KhoangGia(InpMoKhoaGia, InpMoKhoaATR, atr);
      if(mk > 0 && chieu * (gia_thoat - ct) >= mk)
      {
         DongHedge(chieu); GlobalVariableDel(gx);
         GlobalVariableSet(GV(chieu, "moc_khoa"), ct);   // chi khoa lai khi gia VUOT cuc tri nay (chong khoa/mo lien tuc)
      }
      return;                                       // khi khoa: khong nhoi, khong TP rieng ro
   }

   // 4) TP ro tu gia von
   double tp = InpTPPct > 0 ? InpTPPct * r.gia_tb : KhoangGia(InpTPGia, InpTPATR, atr);
   if(tp > 0 && lai_gia >= tp) { DongHet(chieu, true, "tp"); g_so_tp++; return; }
   // 4b) GO sau khi da mo khoa: ro + lai/lo da chot cua lenh khoa >= muc (nhu Python: go_tien tinh ca r.tich)
   if(InpHedgeKhiLoPct > 0 && tich != 0 && tong >= InpGoTien) { DongHet(chieu, true, "go"); g_so_go++; return; }
   // 5) trailing ro
   double kich = InpTrailKichPct > 0 ? InpTrailKichPct * r.gia_tb : KhoangGia(InpTrailKichGia, InpTrailKichATR, atr);
   if(kich > 0)
   {
      string gd = GV(chieu, "dinh");
      if(lai_gia >= kich || GlobalVariableCheck(gd))
      {
         double dinh = GVLay(gd, gia_thoat);
         dinh = chieu > 0 ? MathMax(dinh, gia_thoat) : MathMin(dinh, gia_thoat);
         GlobalVariableSet(gd, dinh);
         double kh = InpTrailKhoangPct > 0 ? InpTrailKhoangPct * dinh : KhoangGia(InpTrailKhoangGia, InpTrailKhoangATR, atr);
         if(chieu * (dinh - gia_thoat) >= kh) { DongHet(chieu, true, "trailing"); g_so_trail++; return; }
      }
   }
   // 6) khoa (hedge) khi lo sau
   string gm = GV(chieu, "moc_khoa");
   bool vuot_moc = InpKhoaLaiKhongMoc || !GlobalVariableCheck(gm) || chieu * (gia_thoat - GlobalVariableGet(gm)) < 0;
   if(InpHedgeKhiLoPct > 0 && g_hedging && MarginDu() && GlobalVariableGet(GV(chieu, "so_khoa")) < InpHedgeMaxLan
      && r.loi <= -InpHedgeKhiLoPct / 100.0 * so_du && vuot_moc)
   {
      if(Mo(-chieu, r.lot * InpHedgeTiLe, TagH(chieu)))
      {
         GlobalVariableSet(GV(chieu, "so_khoa"), GlobalVariableGet(GV(chieu, "so_khoa")) + 1);
         GlobalVariableSet(GV(chieu, "cuc_tri"), gia_thoat);
         g_so_khoa++;
      }
      return;
   }
   // 7) nhoi (DCA nghich / nhoi thuan)
   if(InpNhoi == NHOI_TAT || r.tang >= InpMaxTang || !DuocMo() || !MarginDu()) return;
   if(InpBuocPct > 0)
   {
      // muc co dinh tu gia lenh dau: tang k o gia_dau x (1 - chieu x pct x k) (nhu chay_tk); NHOI_THUAN: dau nguoc lai
      double sg = InpNhoi == NHOI_NGHICH ? -1.0 : 1.0;
      double muc = r.gia_dau * (1.0 + sg * chieu * InpBuocPct * r.tang);
      bool cham = InpNhoi == NHOI_NGHICH ? chieu * (gia_vao - muc) <= 0 : chieu * (gia_vao - muc) >= 0;
      if(cham) Mo(chieu, LotTang(r.tang, chieu), TagT(chieu, r.tang));
      return;
   }
   double buoc = KhoangGia(InpBuocGia, InpBuocATR, atr) * MathPow(InpGianBuoc, r.tang - 1);
   if(buoc <= 0) return;
   bool can = InpNhoi == NHOI_NGHICH ? chieu * (r.gia_cuoi - gia_vao) >= buoc : chieu * (gia_vao - r.gia_cuoi) >= buoc;
   if(can) Mo(chieu, LotTang(r.tang, chieu), TagT(chieu, r.tang));
}

// tra true khi KHONG can thu lai trong nen nay (da mo, da co ro, dang cho InpChoNen); false = thu lai tick sau
bool MoRoMoi(int chieu, double lot0 = 0)
{
   Ro r;
   if(DocRo(chieu, r)) { if(InpVao == VAO_CSV) g_csv_bo_co_ro++; return true; }
   if(!DuocMo()) return false;
   if(InpChoNen > 0)
   {
      double t_dong = GVLay(GV(chieu, "t_dong"), 0);
      if(t_dong > 0 && iBarShift(_Symbol, InpTF, (datetime)(long)t_dong, false) < InpChoNen) return true;
   }
   double atr = Lay1(h_atr);
   if((atr == EMPTY_VALUE || atr <= 0) && InpVao != VAO_CSV) return true;
   double l0 = lot0 > 0 ? lot0 : InpLot0;
   if(!Mo(chieu, l0, TagT(chieu, 0))) return false;   // vd [Market closed] luc 00h -> thu lai
   GlobalVariableSet(GV(chieu, "lot0"), l0);
   if(atr != EMPTY_VALUE && atr > 0) GlobalVariableSet(GV(chieu, "atr"), atr);   // buoc / TP theo ATR LUC MO RO
   else GlobalVariableDel(GV(chieu, "atr"));
   GlobalVariableDel(GV(chieu, "dinh")); GlobalVariableDel(GV(chieu, "cuc_tri")); GlobalVariableDel(GV(chieu, "moc_khoa"));
   GlobalVariableDel(GV(chieu, "tich"));
   GlobalVariableSet(GV(chieu, "so_khoa"), 0);
   g_so_ro++;
   return true;
}

int OnInit()
{
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(50);
   g_hedging = AccountInfoInteger(ACCOUNT_MARGIN_MODE) == ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;
   if(InpHedgeKhiLoPct > 0 && !g_hedging) Print("CANH BAO: tai khoan NETTING -> khong hedge duoc, tat hedge");
   h_atr = iATR(_Symbol, InpTF, 14);
   if(InpVao == VAO_RSI) h_rsi = iRSI(_Symbol, InpTF, 14, PRICE_CLOSE);
   if(InpVao == VAO_MRZ) { h_ma = iMA(_Symbol, InpTF, InpN, 0, MODE_SMA, PRICE_CLOSE); h_sd = iStdDev(_Symbol, InpTF, InpN, 0, MODE_SMA, PRICE_CLOSE); }
   if(h_atr == INVALID_HANDLE) return INIT_FAILED;
   for(int c = -1; c <= 1; c += 2)
   {
      Ro r;
      if(!DocRo(c, r)) { GlobalVariableDel(GV(c, "atr")); GlobalVariableDel(GV(c, "dinh")); GlobalVariableDel(GV(c, "cuc_tri")); GlobalVariableDel(GV(c, "so_khoa")); GlobalVariableDel(GV(c, "moc_khoa")); GlobalVariableDel(GV(c, "tich")); GlobalVariableDel(GV(c, "lot0")); }
      g_n_cu[c > 0 ? 0 : 1] = r.n;
   }
   GhiLog("thoi_gian;ma;su_kien;khoi_luong;gia;bid;ask;spread_point;swap;hoa_hong;loi;phu");
   if(InpVao == VAO_CSV)
   {
      if(!DocCsv()) return INIT_FAILED;
      GhiLenhMt5("thoi_gian;deal;position;vao_ra;chieu;khoi_luong;gia;loi;swap;hoa_hong;phu", true);
   }
   return INIT_SUCCEEDED;
}

// ---- VAO_CSV: doc file lenh vao (thoi_gian,ma,chieu,gia,nguon[,lot]); dong sai dinh dang bo qua, dem
bool DocCsv()
{
   if(InpFileCsv == "") { Print("VAO_CSV: thieu InpFileCsv"); return false; }
   int h = FileOpen(InpFileCsv, FILE_READ | FILE_TXT | FILE_ANSI | FILE_SHARE_READ | (InpCsvChung ? FILE_COMMON : 0));
   if(h == INVALID_HANDLE) { Print("VAO_CSV: khong mo duoc ", InpFileCsv, " loi ", GetLastError()); return false; }
   ArrayResize(g_csv_t, 0); ArrayResize(g_csv_c, 0); ArrayResize(g_csv_lot, 0);
   g_csv_n = 0; g_csv_i = 0;
   int sai = 0; bool dau = true;
   while(!FileIsEnding(h))
   {
      string dong = FileReadString(h);
      StringTrimLeft(dong); StringTrimRight(dong);
      if(dong == "") continue;
      if(dau) { dau = false; if(StringFind(dong, "thoi_gian") == 0) continue; }   // tieu de
      string o[];
      int k = StringSplit(dong, ',', o);
      if(k < 5) { sai++; continue; }
      if(InpCsvMa != "" && o[1] != InpCsvMa) continue;
      datetime t = StringToTime(o[0]);
      int c = (int)StringToInteger(o[2]);
      if(t <= 0 || (c != 1 && c != -1)) { sai++; continue; }
      double l = (k >= 6 && o[5] != "") ? StringToDouble(o[5]) : 0;
      ArrayResize(g_csv_t, g_csv_n + 1, 4096); ArrayResize(g_csv_c, g_csv_n + 1, 4096); ArrayResize(g_csv_lot, g_csv_n + 1, 4096);
      g_csv_t[g_csv_n] = t; g_csv_c[g_csv_n] = c; g_csv_lot[g_csv_n] = l;
      g_csv_n++;
   }
   FileClose(h);
   for(int i = 1; i < g_csv_n; i++)                   // Python ghi da sap xep; o day chi kiem tra
      if(g_csv_t[i] < g_csv_t[i - 1]) { Print("VAO_CSV: file chua sap xep theo thoi_gian (dong ", i + 1, ")"); return false; }
   PrintFormat("VAO_CSV: %d lenh vao tu %s (bo %d dong sai)", g_csv_n, InpFileCsv, sai);
   return g_csv_n > 0;
}

// lenh vao CSV da den gio: mo ro (neu chua co ro cung chieu). false = can thu lai tick sau (gio cam / dong cua)
void ChayCsv()
{
   datetime now = TimeCurrent();
   while(g_csv_i < g_csv_n && g_csv_t[g_csv_i] <= now)
   {
      if(now - g_csv_t[g_csv_i] > InpCsvTreGiay) { g_csv_bo_tre++; g_csv_i++; continue; }
      if(!MoRoMoi(g_csv_c[g_csv_i], g_csv_lot[g_csv_i])) return;   // thu lai CUNG lenh o tick sau
      g_csv_i++;
   }
}

string TenPhu(string duoi)                          // od_x_vao.csv -> od_x_vao.csv_lenh_mt5.csv
{
   return InpFileCsv + duoi;
}

void GhiLenhMt5(string s, bool moi)
{
   int co = FILE_READ | FILE_WRITE | FILE_TXT | FILE_ANSI | FILE_SHARE_READ | (InpCsvChung ? FILE_COMMON : 0);
   if(moi) { int x = FileOpen(TenPhu("_lenh_mt5.csv"), FILE_WRITE | FILE_TXT | FILE_ANSI | (InpCsvChung ? FILE_COMMON : 0)); if(x != INVALID_HANDLE) FileClose(x); }
   int h = FileOpen(TenPhu("_lenh_mt5.csv"), co);
   if(h == INVALID_HANDLE) return;
   FileSeek(h, 0, SEEK_END);
   FileWriteString(h, s + "\r\n");
   FileClose(h);
}

void XuatGia()                                      // nen InpTF trong ky test -> doi chieu Python tren CUNG gia
{
   if(g_t_dau == 0) return;
   MqlRates rt[];
   int n = CopyRates(_Symbol, InpTF, g_t_dau, TimeCurrent(), rt);
   if(n <= 0) { Print("XuatGia: CopyRates loi ", GetLastError()); return; }
   int h = FileOpen(TenPhu("_gia.csv"), FILE_WRITE | FILE_TXT | FILE_ANSI | (InpCsvChung ? FILE_COMMON : 0));
   if(h == INVALID_HANDLE) return;
   FileWriteString(h, "time,open,high,low,close,spread_point\r\n");
   for(int i = 0; i < n; i++)
      FileWriteString(h, StringFormat("%s,%.6f,%.6f,%.6f,%.6f,%d\r\n", TimeToString(rt[i].time, TIME_DATE | TIME_SECONDS),
                      rt[i].open, rt[i].high, rt[i].low, rt[i].close, rt[i].spread));
   FileClose(h);
}

void OnDeinit(const int reason)
{
   string s = StringFormat("so_ro=%d tang_max=%d tp=%d trailing=%d khoa=%d go=%d cat_lo=%d het_gio=%d hedging=%s",
                           g_so_ro, g_tang_max, g_so_tp, g_so_trail, g_so_khoa, g_so_go, g_so_cat, g_so_het_gio, g_hedging ? "co" : "khong");
   if(InpVao == VAO_CSV)
   {
      s += StringFormat(" csv=%d/%d bo_tre=%d bo_co_ro=%d tach=%d", g_csv_i, g_csv_n, g_csv_bo_tre, g_csv_bo_co_ro, g_so_tach);
      if(InpXuatGia) XuatGia();
   }
   Print("BRAIN_XuLiLenh ", _Symbol, " ", s);
   GhiLog(StringFormat("%s;%s;tong_ket;0;0;0;0;0;0;0;0;%s", TimeToString(TimeCurrent()), _Symbol, s));
}

double OnTester()
{
   return (double)g_tang_max;                       // cot "OnTester result" trong bao cao = so tang sau nhat da dung
}

void OnTick()
{
   if(g_t_dau == 0) g_t_dau = TimeCurrent();
   QuanLi(1);
   QuanLi(-1);
   if(InpVao == VAO_CSV) { ChayCsv(); return; }
   datetime t0 = iTime(_Symbol, InpTF, 0);
   if(t0 == 0) return;
   bool nen_moi = t0 != g_nen;
   if(InpVao == VAO_KHONG)
   {
      if(InpChieuKhongTin >= 0) MoRoMoi(1);
      if(InpChieuKhongTin <= 0) MoRoMoi(-1);
      g_nen = t0;
      return;
   }
   if(!nen_moi) return;
   int tin = TinHieu();
   if((tin == 1 || tin == -1) && !MoRoMoi(tin)) return;   // gio cam / spread gian / dong cua: thu lai tick sau CUNG nen
   g_nen = t0;
}

void OnTradeTransaction(const MqlTradeTransaction &tr, const MqlTradeRequest &rq, const MqlTradeResult &rs)
{
   if(tr.type != TRADE_TRANSACTION_DEAL_ADD || !HistoryDealSelect(tr.deal)) return;
   if(HistoryDealGetInteger(tr.deal, DEAL_MAGIC) != InpMagic || HistoryDealGetString(tr.deal, DEAL_SYMBOL) != _Symbol) return;
   long vao = HistoryDealGetInteger(tr.deal, DEAL_ENTRY);
   if(InpVao == VAO_CSV && InpXuatGia)
      GhiLenhMt5(StringFormat("%s;%I64u;%I64d;%s;%d;%.2f;%.6f;%.2f;%.2f;%.2f;%s",
                 TimeToString((datetime)HistoryDealGetInteger(tr.deal, DEAL_TIME), TIME_DATE | TIME_SECONDS), tr.deal,
                 HistoryDealGetInteger(tr.deal, DEAL_POSITION_ID), vao == DEAL_ENTRY_IN ? "in" : (vao == DEAL_ENTRY_OUT ? "out" : "inout"),
                 HistoryDealGetInteger(tr.deal, DEAL_TYPE) == DEAL_TYPE_BUY ? 1 : -1, HistoryDealGetDouble(tr.deal, DEAL_VOLUME),
                 HistoryDealGetDouble(tr.deal, DEAL_PRICE), HistoryDealGetDouble(tr.deal, DEAL_PROFIT),
                 HistoryDealGetDouble(tr.deal, DEAL_SWAP), HistoryDealGetDouble(tr.deal, DEAL_COMMISSION),
                 HistoryDealGetString(tr.deal, DEAL_COMMENT)));
   for(int c = -1; c <= 1; c += 2)            // ro chieu c vua dong het -> ghi gio dong cho InpChoNen
   {
      Ro r; DocRo(c, r);
      int i = c > 0 ? 0 : 1;
      if(r.n == 0 && g_n_cu[i] > 0) GlobalVariableSet(GV(c, "t_dong"), (double)TimeCurrent());
      g_n_cu[i] = r.n;
   }
   GhiLog(StringFormat("%s;%s;%s;%.2f;%.5f;%.5f;%.5f;%d;%.2f;%.2f;%.2f;%s",
          TimeToString(TimeCurrent()), _Symbol, vao == DEAL_ENTRY_IN ? "vao" : "ra",
          HistoryDealGetDouble(tr.deal, DEAL_VOLUME), HistoryDealGetDouble(tr.deal, DEAL_PRICE),
          SymbolInfoDouble(_Symbol, SYMBOL_BID), SymbolInfoDouble(_Symbol, SYMBOL_ASK),
          (int)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD), HistoryDealGetDouble(tr.deal, DEAL_SWAP),
          HistoryDealGetDouble(tr.deal, DEAL_COMMISSION), HistoryDealGetDouble(tr.deal, DEAL_PROFIT),
          HistoryDealGetString(tr.deal, DEAL_COMMENT)));
}
//+------------------------------------------------------------------+
