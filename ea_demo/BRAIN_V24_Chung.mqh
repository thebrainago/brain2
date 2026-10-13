//+------------------------------------------------------------------+
//| BRAIN_V24_Chung.mqh - brain2 vong 24/25 - logic chung 2 EA D1      |
//| Khop v24.py -> v22.chay(thoat="TR2") + v19.tin_hieu (RSI / MRZ):   |
//|  - Tin hieu tren nen D1 VUA DONG (shift 1), vao o open nen ke tiep |
//|  - SL ban dau = gia vao -/+ 1,5*ATR14(nen tin hieu)                |
//|  - Sau moi nen dong: best = max/min(best, close); SL = best -/+ 2*ATR14(nen do), chi keo theo huong co loi |
//|  - Giu toi da 72 nen: dong o open nen thu 73, nen do KHONG xet vao moi |
//|  - InpGioVao: lenh vao duoc hoan toi gio server nay (cung nen D1)  |
//|  - Mot vi the moi chart; MO PHONG -> chi backtest/demo.            |
//+------------------------------------------------------------------+
#include <Trade/Trade.mqh>

enum ENUM_CHE_DO_LOT { LOT_CO_DINH = 0, LOT_PHAN_TRAM_RUI_RO = 1 };

input ENUM_CHE_DO_LOT InpCheDoLot = LOT_CO_DINH; // lot co dinh hoac % rui ro
input double InpLots          = 0.01;   // lot co dinh
input double InpRuiRoPct      = 0.5;    // % von rui ro / lenh (khoang SL ban dau 1,5 ATR)
input int    InpSoNen         = 1500;   // so nen D1 de tinh chi bao (EWM hoi tu)
input long   InpMagic         = 2026102401;
input string InpFileLog       = "brain2_v24_log.csv";
input bool   InpLogChung      = true;   // ghi vao thu muc Common\Files (de lay log ca khi chay Tester)
#ifndef GIO_VAO_MAC_DINH
#define GIO_VAO_MAC_DINH 0
#endif
// 13/10/2026: spread XM luc 00h server gap 3-5 lan (GBPUSD ~5,2 pip, AUDUSD ~3,5 pip; tu 02h ~1 pip) -> cho toi gio nay moi vao lenh moi.
// Tin hieu van tinh tu nen D1 vua dong (khong nhin truoc). 0 = vao ngay tick dau nen (hanh vi v24 cu).
input int    InpGioVao        = GIO_VAO_MAC_DINH; // gio server (0-23) bat dau duoc vao lenh moi

// hang so CO DINH (khong toi uu) - khop Python
#define ATR_N      14
#define RSI_N      14
// 13/10/2026 toi (sinh_viec): tham so luoi cho tester; mac dinh = v24 (D1, z 2, RSI 30/70, SMA50, SL 1,5 ATR)
input ENUM_TIMEFRAMES InpTF   = PERIOD_D1; // khung tin hieu (D1/H4/H1)
input double InpNguongZ       = 2.0;    // MRZ: |z| vao lenh
input double InpRsiThap       = 30;     // RSI: mua khi < 
input double InpRsiCao        = 70;     // RSI: ban khi >
input int    InpMrzN          = 50;     // MRZ: so nen SMA/STD
input double InpSlATR         = 1.5;    // SL ban dau (x ATR14)
#define MRZ_N      InpMrzN
#define SL_ATR     InpSlATR
#define TF_TIN     InpTF
// 13/10/2026 vong 27 (VONG_LAP 3): bien the thoat chi de backtest; mac dinh = hang so v24 cu (2,0 ATR / 72 nen)
input double InpTrATR        = 2.0;    // khoang trailing (x ATR14)
input int    InpGiuToiDa     = 72;     // giu toi da N nen D1
#define TR_ATR     InpTrATR
#define GIU_TOI_DA InpGiuToiDa

CTrade trade;
datetime g_nen_cuoi = 0;
// 13/10/2026: CFD/vang XM dong cua luc 00:00 server -> lenh thi truong o tick dau nen D1 bi tu choi [Market closed].
// Giu lenh CHO (vao / dong het han) va thu lai o cac tick sau CUNG nen, tuc khop o gia mo phien dau tien
// (tuong duong 'open nen' cua du lieu ngay trong Python). Sang nen moi thi bo lenh cho, tinh lai binh thuong.
int    g_cho_tin = 0;      // +1/-1: con lenh vao dang cho
double g_cho_kc  = 0;      // khoang SL ban dau (1,5*ATR nen tin hieu)
ulong  g_cho_dong = 0;     // ve can dong (het 72 nen) dang cho
string   g_gv_best;

void GhiLog(string s)
{
   int co = FILE_READ|FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_SHARE_READ|(InpLogChung ? FILE_COMMON : 0);
   int h = FileOpen(InpFileLog, co, ';');
   if(h == INVALID_HANDLE) return;
   FileSeek(h, 0, SEEK_END);
   FileWriteString(h, s + "\r\n");
   FileClose(h);
}

// tinh chi bao tren cac nen DA DONG; r[] tu cu toi moi, phan tu cuoi = nen shift 1
bool ChiBao(double &atr1, double &gia_tri1, int &tin)
{
   MqlRates r[];
   ArraySetAsSeries(r, false);
   int n = CopyRates(_Symbol, TF_TIN, 1, InpSoNen, r);
   if(n < MRZ_N + 2) return false;
   double atr = r[0].high - r[0].low;
   double eu = 0, ed = 0; bool co_ewm = false;
   for(int i = 1; i < n; i++)
   {
      double pc = r[i-1].close;
      double tr = MathMax(r[i].high - r[i].low, MathMax(MathAbs(r[i].high - pc), MathAbs(r[i].low - pc)));
      atr = atr + (tr - atr) / ATR_N;
      double d = r[i].close - pc, u = MathMax(d, 0.0), v = MathMax(-d, 0.0);
      if(!co_ewm) { eu = u; ed = v; co_ewm = true; }
      else { eu = eu + (u - eu) / RSI_N; ed = ed + (v - ed) / RSI_N; }
   }
   atr1 = atr; tin = 0;
#ifdef CHE_DO_RSI
   if(eu == 0 && ed == 0) { gia_tri1 = EMPTY_VALUE; return true; }
   double rsi = (ed == 0) ? 100.0 : 100.0 - 100.0 / (1.0 + eu / ed);
   gia_tri1 = rsi;
   if(rsi < InpRsiThap) tin = 1; else if(rsi > InpRsiCao) tin = -1;
#else
   double m = 0, s2 = 0;
   for(int i = n - MRZ_N; i < n; i++) m += r[i].close;
   m /= MRZ_N;
   for(int i = n - MRZ_N; i < n; i++) s2 += (r[i].close - m) * (r[i].close - m);
   double sd = MathSqrt(s2 / (MRZ_N - 1));          // ddof=1 nhu pandas rolling.std()
   if(sd <= 0) { gia_tri1 = EMPTY_VALUE; return true; }
   double z = (r[n-1].close - m) / sd;
   gia_tri1 = z;
   if(z < -InpNguongZ) tin = 1; else if(z > InpNguongZ) tin = -1;
#endif
   return true;
}

bool ViThe(ulong &ticket, long &loai, double &sl, datetime &t_vao)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol || PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      ticket = t; loai = PositionGetInteger(POSITION_TYPE); sl = PositionGetDouble(POSITION_SL);
      t_vao = (datetime)PositionGetInteger(POSITION_TIME); return true;
   }
   return false;
}

double TinhLot(double kc_sl)
{
   double lot = InpLots;
   if(InpCheDoLot == LOT_PHAN_TRAM_RUI_RO)
   {
      double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
      if(tv > 0 && ts > 0 && kc_sl > 0) lot = AccountInfoDouble(ACCOUNT_EQUITY) * InpRuiRoPct / 100.0 / (kc_sl / ts * tv);
   }
   double st = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP), mn = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), mx = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(st > 0) lot = MathFloor(lot / st) * st;
   return MathMax(mn, MathMin(mx, lot));
}

int OnInit()
{
   trade.SetExpertMagicNumber(InpMagic);
   g_gv_best = "brain2_v24_best_" + _Symbol + "_" + IntegerToString(InpMagic);
   GhiLog("thoi_gian;ma;su_kien;khoi_luong;gia;bid;ask;spread_point;swap;hoa_hong;loi;chi_bao");
   return INIT_SUCCEEDED;
}

void OnTick()
{
   datetime t0 = iTime(_Symbol, TF_TIN, 0);
   if(t0 == 0) return;
   if(t0 == g_nen_cuoi) { ThuLaiLenhCho(); return; } // trong nen: chi thu lai lenh bi tu choi vi dong cua
   g_nen_cuoi = t0; g_cho_tin = 0; g_cho_dong = 0;
   double atr1, gt1; int tin;
   if(!ChiBao(atr1, gt1, tin)) return;
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   GhiLog(StringFormat("%s;%s;kiem;0;0;%.5f;%.5f;%d;0;0;0;%.4f", TimeToString(TimeCurrent()), _Symbol, bid, ask,
          (int)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD), gt1));
   int dg = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   ulong tk; long loai; double sl; datetime tv;
   if(ViThe(tk, loai, sl, tv))
   {
      int giu = iBarShift(_Symbol, TF_TIN, tv, false);   // so nen da dong tinh ca nen vao
      if(giu >= GIU_TOI_DA) { if(!trade.PositionClose(tk) && DongCua()) g_cho_dong = tk; GlobalVariableDel(g_gv_best); return; }  // nen nay khong vao moi
      double c1 = iClose(_Symbol, TF_TIN, 1);
      double best = GlobalVariableCheck(g_gv_best) ? GlobalVariableGet(g_gv_best) : c1;
      double moi;
      if(loai == POSITION_TYPE_BUY) { best = MathMax(best, c1); moi = best - TR_ATR * atr1; if(moi > sl) trade.PositionModify(tk, NormalizeDouble(moi, dg), 0); }
      else                          { best = MathMin(best, c1); moi = best + TR_ATR * atr1; if(moi < sl) trade.PositionModify(tk, NormalizeDouble(moi, dg), 0); }
      GlobalVariableSet(g_gv_best, best);
      return;
   }
   GlobalVariableDel(g_gv_best);
   if(tin == 0) return;
   double kc = SL_ATR * atr1;
   if(ChuaToiGio()) { g_cho_tin = tin; g_cho_kc = kc; return; }   // cho toi InpGioVao (ThuLaiLenhCho)
   if(!VaoLenh(tin, kc) && DongCua()) { g_cho_tin = tin; g_cho_kc = kc; }
}

bool ChuaToiGio()
{
   if(InpGioVao <= 0) return false;
   MqlDateTime dt; TimeToStruct(TimeCurrent(), dt);
   return dt.hour < MathMin(InpGioVao, 23);
}

bool DongCua() { uint rc = trade.ResultRetcode(); return rc == TRADE_RETCODE_MARKET_CLOSED || rc == TRADE_RETCODE_TRADE_DISABLED; }

bool VaoLenh(int tin, double kc)
{
   int dg = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS); double lot = TinhLot(kc);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(tin > 0) return trade.Buy(lot, _Symbol, 0, NormalizeDouble(ask - kc, dg), 0, "brain2 v24") && trade.ResultRetcode() == TRADE_RETCODE_DONE;
   return trade.Sell(lot, _Symbol, 0, NormalizeDouble(bid + kc, dg), 0, "brain2 v24") && trade.ResultRetcode() == TRADE_RETCODE_DONE;
}

void ThuLaiLenhCho()
{
   if(g_cho_dong != 0) { if(!PositionSelectByTicket(g_cho_dong) || trade.PositionClose(g_cho_dong)) g_cho_dong = 0; return; }  // nen nay khong vao moi
   if(g_cho_tin == 0) return;
   if(ChuaToiGio()) return;
   ulong tk; long loai; double sl; datetime tv;
   if(ViThe(tk, loai, sl, tv)) { g_cho_tin = 0; return; }
   if(VaoLenh(g_cho_tin, g_cho_kc) || !DongCua()) g_cho_tin = 0;
}

void OnTradeTransaction(const MqlTradeTransaction &tr, const MqlTradeRequest &rq, const MqlTradeResult &rs)
{
   if(tr.type != TRADE_TRANSACTION_DEAL_ADD) return;
   if(!HistoryDealSelect(tr.deal)) return;
   if(HistoryDealGetInteger(tr.deal, DEAL_MAGIC) != InpMagic || HistoryDealGetString(tr.deal, DEAL_SYMBOL) != _Symbol) return;
   GhiLog(StringFormat("%s;%s;%s;%.2f;%.5f;%.5f;%.5f;%d;%.2f;%.2f;%.2f;",
          TimeToString(TimeCurrent()), _Symbol,
          HistoryDealGetInteger(tr.deal, DEAL_ENTRY) == DEAL_ENTRY_IN ? "vao" : "ra",
          HistoryDealGetDouble(tr.deal, DEAL_VOLUME), HistoryDealGetDouble(tr.deal, DEAL_PRICE),
          SymbolInfoDouble(_Symbol, SYMBOL_BID), SymbolInfoDouble(_Symbol, SYMBOL_ASK),
          (int)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD), HistoryDealGetDouble(tr.deal, DEAL_SWAP),
          HistoryDealGetDouble(tr.deal, DEAL_COMMISSION), HistoryDealGetDouble(tr.deal, DEAL_PROFIT)));
}
