//+------------------------------------------------------------------+
//| IBS_US100.mq5                                                    |
//| ỨNG VIÊN – CHƯA PASS – CHỈ DÙNG TRÊN TÀI KHOẢN DEMO              |
//|                                                                  |
//| Long D1 theo đặc tả docs/kien-thuc-thong-ke/ibs_us100_spec.md    |
//| Tín hiệu lúc đóng cửa nến t, khớp mở cửa nến t+1.                |
//| CHƯA COMPILE trên máy soạn mã này (không có MetaEditor).         |
//| Không mở tài khoản thật, không copy lệnh, không chạy live.       |
//+------------------------------------------------------------------+
#property copyright "brain2/EVO – ứng viên chưa pass"
#property link      "https://github.com/thebrainago/brain2/blob/evo/thong-ke-kien-thuc/docs/kien-thuc-thong-ke/ibs_us100_spec.md"
#property version   "1.00"
#property description "IBS US100 D1. ỨNG VIÊN – CHƯA PASS. CHỈ DEMO. Chưa compile trên máy soạn mã."
#property description "Vào IBS<0.20 tại mở nến sau; ra IBS>0.80 hoặc tối đa 4 nến."

#include <Trade/Trade.mqh>

input group "=== Cảnh báo ==="
input bool   InpAckDemoOnly = false;          // Xác nhận: chỉ chạy trên tài khoản DEMO

input group "=== Lệnh ==="
input string InpSymbol      = "";             // Mã cần giao dịch (trống = mã của đồ thị)
input double InpLots        = 0.10;           // Khối lượng cố định (nếu không dùng rủi ro %)
input bool   InpUseRiskPct  = false;          // true = tính lot theo % vốn (ước lượng qua ATR, không phải SL thật)
input double InpRiskPercent = 0.50;           // % vốn ước lượng rủi ro mỗi lệnh (khi InpUseRiskPct)
input double InpRiskAtrMult = 2.0;            // Hệ số ATR(14) D1 dùng để ước lượng khoảng rủi ro khi tính lot

input group "=== Quy tắc IBS ==="
input double InpIbsBuy      = 0.20;           // Vào long khi IBS nến vừa đóng < ngưỡng này
input double InpIbsExit     = 0.80;           // Ra khi IBS nến vừa đóng > ngưỡng này
input int    InpMaxBars     = 4;              // Số nến D1 tối đa được giữ (đếm nến đã đóng sau khi vào)

input group "=== Lọc / an toàn ==="
input int    InpMaxSpreadPoints = 0;          // Bỏ qua vào lệnh nếu spread (điểm SYMBOL_POINT) vượt ngưỡng; 0 = không lọc. Lệnh ra vẫn được phép.
input int    InpMagic       = 20261115;       // Magic number
input int    InpSlippagePts = 10;             // Độ trượt tối đa khi gửi lệnh (điểm)
input bool   InpUseVixFilter= false;          // Lọc VIX (TẮT mặc định; chưa kiểm OOS độc lập – chỉ thử nghiệm)
input string InpVixSymbol   = "VIX";          // Mã VIX trên sàn (nếu lọc bật)
input double InpVixMin      = 20.0;           // Chỉ vào lệnh khi VIX nến D1 vừa đóng >= ngưỡng này

//---
CTrade         g_trade;
string         g_symbol;
datetime       g_last_d1 = 0;      // mốc nến D1 hiện tại (để nhận nến mới)
datetime       g_entry_bar = 0;    // thời điểm mở nến D1 lúc vào lệnh
bool           g_exited_this_bar = false;
bool           g_pending_exit = false;  // retry thoát nếu tick đầu gặp market closed
bool           g_pending_entry = false; // retry vào tại phiên mở cửa của nến D1 mới


//+------------------------------------------------------------------+
int OnInit()
  {
   g_symbol = (InpSymbol == "" ? _Symbol : InpSymbol);
   if(!SymbolSelect(g_symbol, true))
     {
      Print("IBS_US100: không chọn được mã ", g_symbol);
      return(INIT_FAILED);
     }
   if(InpMaxBars < 1 || InpIbsBuy <= 0.0 || InpIbsBuy >= 1.0 || InpIbsExit <= InpIbsBuy)
     {
      Print("IBS_US100: tham số IBS/MaxBars không hợp lệ.");
      return(INIT_PARAMETERS_INCORRECT);
     }
   if(!InpAckDemoOnly)
     {
      Print("IBS_US100: hãy bật InpAckDemoOnly (xác nhận chỉ DEMO). Khởi tạo bị từ chối.");
      return(INIT_PARAMETERS_INCORRECT);
     }
   if(!MQLInfoInteger(MQL_TESTER) &&
      (ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE) != ACCOUNT_TRADE_MODE_DEMO)
     {
      Print("IBS_US100: từ chối – tài khoản không phải DEMO. Ứng viên – chưa pass.");
      return(INIT_FAILED);
     }

   g_trade.SetExpertMagicNumber((ulong)InpMagic);
   g_trade.SetDeviationInPoints((ulong)MathMax(InpSlippagePts, 0));
   // Kiểu khớp lệnh theo sàn
   const int fill = (int)SymbolInfoInteger(g_symbol, SYMBOL_FILLING_MODE);
   if((fill & SYMBOL_FILLING_IOC) == SYMBOL_FILLING_IOC)
      g_trade.SetTypeFilling(ORDER_FILLING_IOC);
   else if((fill & SYMBOL_FILLING_FOK) == SYMBOL_FILLING_FOK)
      g_trade.SetTypeFilling(ORDER_FILLING_FOK);
   else
      g_trade.SetTypeFilling(ORDER_FILLING_RETURN);

   // Ghi nhận nến D1 hiện tại để KHÔNG vào lệnh giữa ngày lúc gắn EA / lúc tester vừa start.
   g_last_d1 = iTime(g_symbol, PERIOD_D1, 0);
   g_entry_bar = 0;
   // 15/11/2026 forward demo: khởi động lại terminal giữa chừng thì khôi phục nến vào
   // từ giờ mở lệnh, nếu không lệnh sẽ không bao giờ thoát theo 4 nến.
   for(int i = PositionsTotal() - 1; i >= 0; --i)
     {
      const ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != g_symbol) continue;
      if((long)PositionGetInteger(POSITION_MAGIC) != (long)InpMagic) continue;
      const int sh = iBarShift(g_symbol, PERIOD_D1, (datetime)PositionGetInteger(POSITION_TIME), false);
      if(sh >= 0) g_entry_bar = iTime(g_symbol, PERIOD_D1, sh);
     }
   Print("IBS_US100: DEMO only, ứng viên chưa pass, chưa compile trên máy soạn mã. Symbol=", g_symbol);
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
  }

//+------------------------------------------------------------------+
void OnTick()
  {
   if(!InpAckDemoOnly)
      return;
   if((ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_REAL)
      return;

   // Xử lý khi có nến D1 mới (nến trước vừa đóng). Nếu tick đầu gặp market closed
   // (CFD chỉ số thường đóng lúc 00:00), giữ lệnh chờ và khớp lại ở tick mở phiên — đúng "vào tại mở nến sau".
   const datetime t0 = iTime(g_symbol, PERIOD_D1, 0);
   if(t0 == 0)
      return;

   if(t0 != g_last_d1)
     {
      g_last_d1 = t0;
      g_exited_this_bar = false;
      g_pending_exit = false;
      g_pending_entry = false;

      if(iBars(g_symbol, PERIOD_D1) < 6)
         return;

      const double h = iHigh(g_symbol, PERIOD_D1, 1);
      const double l = iLow(g_symbol, PERIOD_D1, 1);
      const double c = iClose(g_symbol, PERIOD_D1, 1);
      if(h <= 0.0 || l <= 0.0 || c <= 0.0 || h < l)
         return;

      double ibs = EMPTY_VALUE;
      if(h > l)
         ibs = (c - l) / (h - l);

      // 1) Nếu đang giữ lệnh của EA này: xét thoát trước.
      if(HasOurPosition())
        {
         const int held = BarsHeld(); // số nến D1 đã đóng kể từ nến vào
         const bool exit_ibs = (ibs != EMPTY_VALUE && ibs > InpIbsExit);
         const bool exit_time = (held >= InpMaxBars);
         if(exit_ibs || exit_time)
            g_pending_exit = true;
        }

      // 2) Không vào lại ngay trên cùng nến vừa thoát (khớp đặc tả Python: tín hiệu sau là đóng cửa nến thoát).
      if(!g_pending_exit && !HasOurPosition() && ibs != EMPTY_VALUE && ibs < InpIbsBuy)
        {
         if(SpreadOk() && VixOk())
            g_pending_entry = true;
        }
     }

   if(g_pending_exit)
     {
      if(CloseOurPosition())
        {
         g_exited_this_bar = true;
         g_entry_bar = 0;
         g_pending_exit = false;
         g_pending_entry = false;
        }
      return;
     }

   if(!g_pending_entry)
      return;
   if(g_exited_this_bar || HasOurPosition())
     {
      g_pending_entry = false;
      return;
     }
   if(!SpreadOk() || !VixOk())
      return;

   const double lots = ComputeLots();
   if(lots <= 0.0)
     {
      g_pending_entry = false;
      return;
     }
   if(g_trade.Buy(lots, g_symbol, 0.0, 0.0, 0.0, "IBS_US100 demo ung vien"))
     {
      g_entry_bar = t0; // vào tại mở phiên của nến D1 hiện tại
      g_pending_entry = false;
      Print("IBS_US100: BUY lots=", lots, " bar=", TimeToString(t0));
     }
   else
     {
      const uint rc = g_trade.ResultRetcode();
      Print("IBS_US100: Buy thất bại, retcode=", rc, " ", g_trade.ResultRetcodeDescription());
      // Giữ pending chỉ khi thị trường đóng; lỗi khác thì bỏ tín hiệu nến này.
      if(rc != TRADE_RETCODE_MARKET_CLOSED)
         g_pending_entry = false;
     }
  }

//+------------------------------------------------------------------+
bool HasOurPosition()
  {
   for(int i = PositionsTotal() - 1; i >= 0; --i)
     {
      const ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != g_symbol)
         continue;
      if((long)PositionGetInteger(POSITION_MAGIC) != (long)InpMagic)
         continue;
      if((ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE) != POSITION_TYPE_BUY)
         continue;
      return(true);
     }
   return(false);
  }

//+------------------------------------------------------------------+
int BarsHeld()
  {
   if(g_entry_bar == 0)
      return(0);
   const int shift = iBarShift(g_symbol, PERIOD_D1, g_entry_bar, true);
   if(shift < 0)
      return(0);
   // shift=0: vẫn đang ở nến vào (không xảy ra ở bước nến mới).
   // shift=1: nến vào vừa đóng → đã giữ 1 nến; shift=4 → đủ 4 nến, thoát.
   return(shift);
  }

//+------------------------------------------------------------------+
bool CloseOurPosition()
  {
   bool any = false;
   for(int i = PositionsTotal() - 1; i >= 0; --i)
     {
      const ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != g_symbol)
         continue;
      if((long)PositionGetInteger(POSITION_MAGIC) != (long)InpMagic)
         continue;
      if(!g_trade.PositionClose(ticket))
        {
         Print("IBS_US100: đóng lệnh thất bại, retcode=", g_trade.ResultRetcode());
         return(false);
        }
      any = true;
     }
   return(any);
  }

//+------------------------------------------------------------------+
bool SpreadOk()
  {
   if(InpMaxSpreadPoints <= 0)
      return(true);
   const long spread = SymbolInfoInteger(g_symbol, SYMBOL_SPREAD);
   return(spread <= (long)InpMaxSpreadPoints);
  }

//+------------------------------------------------------------------+
bool VixOk()
  {
   if(!InpUseVixFilter)
      return(true);
   if(InpVixSymbol == "")
      return(false);
   if(!SymbolSelect(InpVixSymbol, true))
     {
      Print("IBS_US100: không có mã VIX ", InpVixSymbol, " – bỏ qua vào lệnh.");
      return(false);
     }
   const double v = iClose(InpVixSymbol, PERIOD_D1, 1);
   if(v <= 0.0)
      return(false);
   return(v >= InpVixMin);
  }

//+------------------------------------------------------------------+
double ComputeLots()
  {
   const double vmin  = SymbolInfoDouble(g_symbol, SYMBOL_VOLUME_MIN);
   const double vmax  = SymbolInfoDouble(g_symbol, SYMBOL_VOLUME_MAX);
   const double vstep = SymbolInfoDouble(g_symbol, SYMBOL_VOLUME_STEP);
   double lots = InpLots;

   if(InpUseRiskPct && InpRiskPercent > 0.0)
     {
      // Không có SL thật; ATR chỉ để ước lượng lot, không đặt stoploss.
      const int atr_handle = iATR(g_symbol, PERIOD_D1, 14);
      double atr_buf[];
      double atr = 0.0;
      if(atr_handle != INVALID_HANDLE)
        {
         ArraySetAsSeries(atr_buf, true);
         if(CopyBuffer(atr_handle, 0, 1, 1, atr_buf) == 1)
            atr = atr_buf[0];
         IndicatorRelease(atr_handle);
        }
      const double price = SymbolInfoDouble(g_symbol, SYMBOL_ASK);
      const double sl_dist = (atr > 0.0 ? atr * InpRiskAtrMult : price * 0.02);
      const double tick_sz = SymbolInfoDouble(g_symbol, SYMBOL_TRADE_TICK_SIZE);
      const double tick_vl = SymbolInfoDouble(g_symbol, SYMBOL_TRADE_TICK_VALUE);
      const double equity  = AccountInfoDouble(ACCOUNT_EQUITY);
      if(sl_dist > 0.0 && tick_sz > 0.0 && tick_vl > 0.0 && equity > 0.0)
        {
         const double money = equity * InpRiskPercent / 100.0;
         lots = money / (sl_dist / tick_sz * tick_vl);
        }
     }

   if(vstep > 0.0)
      lots = MathFloor(lots / vstep + 1e-8) * vstep;
   if(lots < vmin)
      lots = vmin;
   if(lots > vmax)
      lots = vmax;
   const int digits_vol = (vstep >= 1.0 ? 0 : (vstep >= 0.1 ? 1 : 2));
   return(NormalizeDouble(lots, digits_vol));
  }

//+------------------------------------------------------------------+
