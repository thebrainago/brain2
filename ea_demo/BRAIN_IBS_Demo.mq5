//+------------------------------------------------------------------+
//| BRAIN_IBS_Demo.mq5  - brain2 vong 13 - CHI DE CHAY DEMO XM          |
//| Quy tac (mo phong song, Holm 34 p=0,048): IBS < 0,2 cua PHIEN Mỹ  |
//| -> mua gan cuoi phien, giu toi lan kiem tiep theo (1 ngay).        |
//| IBS = (gia - thap phien)/(cao phien - thap phien), phien tinh tu   |
//| InpGioMoPhien:InpPhutMoPhien (gio server) toi luc kiem.            |
//| KHONG phai tien that. Ghi nhat ky khop lenh/spread/swap ra CSV.    |
//+------------------------------------------------------------------+
#property copyright "brain2"
#property version   "1.00"
#include <Trade/Trade.mqh>

input string InpSymbols        = "US500Cash,US100Cash"; // ma XM (tach bang dau phay)
input double InpIbsMax         = 0.2;    // nguong IBS
input double InpLots           = 0.10;   // khoi luong CO DINH moi ma (nho)
input int    InpGioMoPhien     = 16;     // gio server mo phien cash My (16:30 server = 09:30 NY)
input int    InpPhutMoPhien    = 30;
input int    InpGioKiem        = 22;     // gio server kiem/vao lenh (truoc dong phien 23:00 server)
input int    InpPhutKiem       = 55;
input long   InpMagic          = 2026101301;
input string InpFileLog        = "brain2_ibs_log.csv";

CTrade trade;
string g_sym[];
datetime g_ngay_da_kiem[];

void GhiLog(string s)
{
   int h = FileOpen(InpFileLog, FILE_READ|FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_SHARE_READ, ';');
   if(h == INVALID_HANDLE) return;
   FileSeek(h, 0, SEEK_END);
   FileWriteString(h, s + "\r\n");
   FileClose(h);
}

int OnInit()
{
   int n = StringSplit(InpSymbols, ',', g_sym);
   if(n <= 0) return INIT_PARAMETERS_INCORRECT;
   ArrayResize(g_ngay_da_kiem, n);
   for(int i = 0; i < n; i++) { StringTrimLeft(g_sym[i]); StringTrimRight(g_sym[i]); SymbolSelect(g_sym[i], true); g_ngay_da_kiem[i] = 0; }
   trade.SetExpertMagicNumber(InpMagic);
   GhiLog("thoi_gian;ma;su_kien;khoi_luong;gia;bid;ask;spread_point;swap;hoa_hong;loi;ibs");
   EventSetTimer(20);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) { EventKillTimer(); }

// cao/thap/gia hien tai cua phien tu gio mo phien toi bay gio (bar M5)
bool IbsPhien(string sym, double &ibs)
{
   MqlDateTime t; TimeToStruct(TimeCurrent(), t);
   t.hour = InpGioMoPhien; t.min = InpPhutMoPhien; t.sec = 0;
   datetime mo = StructToTime(t);
   MqlRates r[];
   int n = CopyRates(sym, PERIOD_M5, mo, TimeCurrent(), r);
   if(n < 6) return false;
   double hi = r[0].high, lo = r[0].low;
   for(int i = 1; i < n; i++) { hi = MathMax(hi, r[i].high); lo = MathMin(lo, r[i].low); }
   double c = SymbolInfoDouble(sym, SYMBOL_BID);
   if(hi - lo <= 0) return false;
   ibs = (c - lo) / (hi - lo);
   return true;
}

double KhoiLuongDangGiu(string sym)
{
   double v = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == sym && PositionGetInteger(POSITION_MAGIC) == InpMagic)
         v += PositionGetDouble(POSITION_VOLUME);
   }
   return v;
}

void DongHet(string sym)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == sym && PositionGetInteger(POSITION_MAGIC) == InpMagic)
         trade.PositionClose(tk);
   }
}

void OnTimer()
{
   MqlDateTime t; TimeToStruct(TimeCurrent(), t);
   if(t.day_of_week == 0 || t.day_of_week == 6) return;
   if(t.hour * 60 + t.min < InpGioKiem * 60 + InpPhutKiem) return;
   datetime hom_nay = StringToTime(StringFormat("%04d.%02d.%02d", t.year, t.mon, t.day));
   for(int i = 0; i < ArraySize(g_sym); i++)
   {
      if(g_ngay_da_kiem[i] == hom_nay) continue;
      string sym = g_sym[i];
      double ibs;
      if(!IbsPhien(sym, ibs)) continue;          // chua co du bar phien (ngay nghi) -> khong lam gi
      g_ngay_da_kiem[i] = hom_nay;
      bool tin = ibs < InpIbsMax;
      double dang = KhoiLuongDangGiu(sym);
      GhiLog(StringFormat("%s;%s;kiem;%.2f;0;%.5f;%.5f;%d;0;0;0;%.4f", TimeToString(TimeCurrent()), sym, dang,
             SymbolInfoDouble(sym, SYMBOL_BID), SymbolInfoDouble(sym, SYMBOL_ASK),
             (int)SymbolInfoInteger(sym, SYMBOL_SPREAD), ibs));
      if(tin && dang <= 0) trade.Buy(InpLots, sym, 0, 0, 0, "brain2 IBS");
      else if(!tin && dang > 0) DongHet(sym);
      // tin && dang > 0: GIU (mo phong khong tra phi khi tin hieu lien tiep)
   }
}

void OnTradeTransaction(const MqlTradeTransaction &tr, const MqlTradeRequest &rq, const MqlTradeResult &rs)
{
   if(tr.type != TRADE_TRANSACTION_DEAL_ADD) return;
   if(!HistoryDealSelect(tr.deal)) return;
   if(HistoryDealGetInteger(tr.deal, DEAL_MAGIC) != InpMagic) return;
   string sym = HistoryDealGetString(tr.deal, DEAL_SYMBOL);
   GhiLog(StringFormat("%s;%s;%s;%.2f;%.5f;%.5f;%.5f;%d;%.2f;%.2f;%.2f;",
          TimeToString(TimeCurrent()), sym,
          HistoryDealGetInteger(tr.deal, DEAL_ENTRY) == DEAL_ENTRY_IN ? "vao" : "ra",
          HistoryDealGetDouble(tr.deal, DEAL_VOLUME), HistoryDealGetDouble(tr.deal, DEAL_PRICE),
          SymbolInfoDouble(sym, SYMBOL_BID), SymbolInfoDouble(sym, SYMBOL_ASK),
          (int)SymbolInfoInteger(sym, SYMBOL_SPREAD), HistoryDealGetDouble(tr.deal, DEAL_SWAP),
          HistoryDealGetDouble(tr.deal, DEAL_COMMISSION), HistoryDealGetDouble(tr.deal, DEAL_PROFIT)));
}
