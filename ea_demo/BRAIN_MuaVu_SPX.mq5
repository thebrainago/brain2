//+------------------------------------------------------------------+
//| BRAIN_MuaVu_SPX.mq5 - brain2 vong 13 - CHI DE CHAY DEMO XM          |
//| Danh muc 4 quy tac mua vu tren US500 (mo phong song, Holm p~0):    |
//|  dau/cuoi thang (phien cuoi + 3 phien dau), Santa (5 phien cuoi    |
//|  thang 12 + 2 phien dau thang 1), Halloween (thang 11 -> 4),       |
//|  nam 3 chu ky bau cu (nam % 4 == 3). Moi quy tac bat = InpLotMoiQT.|
//| Kiem moi ngay gan cuoi phien: dat khoi luong cho PHIEN KE TIEP.    |
//| Lich phien = thu 2-6 (KHONG tinh ngay le My - xem INSTALL_DEMO).   |
//| KHONG phai tien that. Ghi nhat ky khop lenh/spread/swap ra CSV.    |
//+------------------------------------------------------------------+
#property copyright "brain2"
#property version   "1.00"
#include <Trade/Trade.mqh>

input string InpSymbol      = "US500Cash"; // ma XM
input bool   InpDauCuoiThang = true;
input bool   InpSanta        = true;
input bool   InpHalloween    = true;
input bool   InpNam3         = true;
input double InpLotMoiQT     = 0.05;   // khoi luong moi quy tac dang bat (nho)
input int    InpGioKiem      = 22;     // gio server kiem (truoc dong phien)
input int    InpPhutKiem     = 55;
input long   InpMagic        = 2026101302;
input string InpFileLog      = "brain2_muavu_log.csv";

CTrade trade;
datetime g_da_kiem = 0;

void GhiLog(string s)
{
   int h = FileOpen(InpFileLog, FILE_READ|FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_SHARE_READ, ';');
   if(h == INVALID_HANDLE) return;
   FileSeek(h, 0, SEEK_END);
   FileWriteString(h, s + "\r\n");
   FileClose(h);
}

bool LaNgayThuong(datetime d) { MqlDateTime t; TimeToStruct(d, t); return t.day_of_week >= 1 && t.day_of_week <= 5; }

datetime NgayThuongKe(datetime d)
{
   datetime x = d + 86400;
   while(!LaNgayThuong(x)) x += 86400;
   return x;
}

// so thu tu ngay thuong trong thang (1 = phien dau) va so ngay thuong con lai sau no
void ViTriTrongThang(datetime d, int &thu_tu, int &con_lai)
{
   MqlDateTime t; TimeToStruct(d, t);
   thu_tu = 0; con_lai = 0;
   MqlDateTime u = t; u.day = 1; u.hour = 0; u.min = 0; u.sec = 0;
   datetime x = StructToTime(u);
   while(true)
   {
      MqlDateTime v; TimeToStruct(x, v);
      if(v.mon != t.mon) break;
      if(LaNgayThuong(x)) { if(x <= d) thu_tu++; else con_lai++; }
      x += 86400;
   }
}

int SoQuyTacBat(datetime d)   // d = ngay cua PHIEN se giu
{
   MqlDateTime t; TimeToStruct(d, t);
   int tt, cl; ViTriTrongThang(d, tt, cl);
   int n = 0;
   if(InpNam3 && t.year % 4 == 3) n++;
   if(InpHalloween && (t.mon >= 11 || t.mon <= 4)) n++;
   if(InpDauCuoiThang && (cl == 0 || tt <= 3)) n++;
   if(InpSanta && ((t.mon == 12 && cl <= 4) || (t.mon == 1 && tt <= 2))) n++;
   return n;
}

double KhoiLuongDangGiu()
{
   double v = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == InpSymbol && PositionGetInteger(POSITION_MAGIC) == InpMagic)
         v += PositionGetDouble(POSITION_VOLUME);
   }
   return v;
}

void GiamToi(double muc)
{
   for(int i = PositionsTotal() - 1; i >= 0 && KhoiLuongDangGiu() > muc + 1e-8; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != InpSymbol || PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      double vol = PositionGetDouble(POSITION_VOLUME);
      double thua = KhoiLuongDangGiu() - muc;
      if(vol <= thua + 1e-8) trade.PositionClose(tk);
      else trade.PositionClosePartial(tk, NormalizeDouble(thua, 2));
   }
}

int OnInit()
{
   SymbolSelect(InpSymbol, true);
   trade.SetExpertMagicNumber(InpMagic);
   GhiLog("thoi_gian;ma;su_kien;khoi_luong;gia;bid;ask;spread_point;swap;hoa_hong;loi;so_quy_tac");
   EventSetTimer(20);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) { EventKillTimer(); }

void OnTimer()
{
   datetime now = TimeCurrent();
   MqlDateTime t; TimeToStruct(now, t);
   if(!LaNgayThuong(now)) return;
   if(t.hour * 60 + t.min < InpGioKiem * 60 + InpPhutKiem) return;
   datetime hom_nay = StringToTime(StringFormat("%04d.%02d.%02d", t.year, t.mon, t.day));
   if(g_da_kiem == hom_nay) return;
   g_da_kiem = hom_nay;
   int n = SoQuyTacBat(NgayThuongKe(hom_nay));
   double muc = NormalizeDouble(n * InpLotMoiQT, 2);
   double dang = KhoiLuongDangGiu();
   GhiLog(StringFormat("%s;%s;kiem;%.2f;0;%.5f;%.5f;%d;0;0;0;%d", TimeToString(now), InpSymbol, dang,
          SymbolInfoDouble(InpSymbol, SYMBOL_BID), SymbolInfoDouble(InpSymbol, SYMBOL_ASK),
          (int)SymbolInfoInteger(InpSymbol, SYMBOL_SPREAD), n));
   if(muc > dang + 1e-8) trade.Buy(NormalizeDouble(muc - dang, 2), InpSymbol, 0, 0, 0, "brain2 mua vu");
   else if(muc < dang - 1e-8) GiamToi(muc);
}

void OnTradeTransaction(const MqlTradeTransaction &tr, const MqlTradeRequest &rq, const MqlTradeResult &rs)
{
   if(tr.type != TRADE_TRANSACTION_DEAL_ADD) return;
   if(!HistoryDealSelect(tr.deal)) return;
   if(HistoryDealGetInteger(tr.deal, DEAL_MAGIC) != InpMagic) return;
   GhiLog(StringFormat("%s;%s;%s;%.2f;%.5f;%.5f;%.5f;%d;%.2f;%.2f;%.2f;",
          TimeToString(TimeCurrent()), InpSymbol,
          HistoryDealGetInteger(tr.deal, DEAL_ENTRY) == DEAL_ENTRY_IN ? "vao" : "ra",
          HistoryDealGetDouble(tr.deal, DEAL_VOLUME), HistoryDealGetDouble(tr.deal, DEAL_PRICE),
          SymbolInfoDouble(InpSymbol, SYMBOL_BID), SymbolInfoDouble(InpSymbol, SYMBOL_ASK),
          (int)SymbolInfoInteger(InpSymbol, SYMBOL_SPREAD), HistoryDealGetDouble(tr.deal, DEAL_SWAP),
          HistoryDealGetDouble(tr.deal, DEAL_COMMISSION), HistoryDealGetDouble(tr.deal, DEAL_PROFIT)));
}
