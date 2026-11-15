//+------------------------------------------------------------------+
//| EvoXuatCSV - xuat lich su deal forward demo ra CSV (Evo 15/11/2026)
//| Gan vao 1 chart bat ky. Moi gio ghi lai toan bo deal cua cac magic
//| trong InpMagics vao MQL5\Files\evo_forward_deals.csv va vi the dang mo
//| vao evo_forward_open.csv. Khong dat lenh. Chi doc tai khoan.
//+------------------------------------------------------------------+
#property copyright "brain2/EVO"
input string InpMagics = "26111501,26111502,26111503";
input int    InpPhut   = 60;

long g_m[];

bool CoMagic(long m)
  {
   for(int i = 0; i < ArraySize(g_m); i++) if(g_m[i] == m) return(true);
   return(false);
  }

int OnInit()
  {
   string p[]; int n = StringSplit(InpMagics, ',', p);
   ArrayResize(g_m, n);
   for(int i = 0; i < n; i++) g_m[i] = StringToInteger(p[i]);
   EventSetTimer(MathMax(InpPhut, 1) * 60);
   Xuat();
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int r) { EventKillTimer(); }
void OnTimer() { Xuat(); }
void OnTick() {}

void Xuat()
  {
   long mode = AccountInfoInteger(ACCOUNT_TRADE_MODE);
   if(!HistorySelect(0, TimeCurrent() + 86400)) return;
   int f = FileOpen("evo_forward_deals.csv", FILE_WRITE | FILE_CSV | FILE_ANSI, ',');
   if(f == INVALID_HANDLE) return;
   FileWrite(f, "login", "demo", "ticket", "position", "time", "symbol", "magic", "type", "entry",
             "volume", "price", "profit", "swap", "commission", "comment");
   int n = HistoryDealsTotal();
   for(int i = 0; i < n; i++)
     {
      ulong t = HistoryDealGetTicket(i);
      long mg = HistoryDealGetInteger(t, DEAL_MAGIC);
      if(!CoMagic(mg)) continue;
      FileWrite(f, AccountInfoInteger(ACCOUNT_LOGIN), (mode == ACCOUNT_TRADE_MODE_DEMO ? 1 : 0), t,
                HistoryDealGetInteger(t, DEAL_POSITION_ID),
                TimeToString((datetime)HistoryDealGetInteger(t, DEAL_TIME), TIME_DATE | TIME_SECONDS),
                HistoryDealGetString(t, DEAL_SYMBOL), mg, HistoryDealGetInteger(t, DEAL_TYPE),
                HistoryDealGetInteger(t, DEAL_ENTRY), HistoryDealGetDouble(t, DEAL_VOLUME),
                HistoryDealGetDouble(t, DEAL_PRICE), HistoryDealGetDouble(t, DEAL_PROFIT),
                HistoryDealGetDouble(t, DEAL_SWAP), HistoryDealGetDouble(t, DEAL_COMMISSION),
                HistoryDealGetString(t, DEAL_COMMENT));
     }
   FileClose(f);
   f = FileOpen("evo_forward_status.txt", FILE_WRITE | FILE_TXT | FILE_ANSI);
   if(f != INVALID_HANDLE)
     {
      FileWrite(f, "luc_server=" + TimeToString(TimeCurrent(), TIME_DATE | TIME_SECONDS));
      FileWrite(f, "login=" + IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN)) + " server=" + AccountInfoString(ACCOUNT_SERVER));
      FileWrite(f, "trade_mode=" + (mode == ACCOUNT_TRADE_MODE_DEMO ? "DEMO" : (mode == ACCOUNT_TRADE_MODE_REAL ? "REAL" : "CONTEST")));
      FileWrite(f, "terminal_trade_allowed=" + IntegerToString(TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)));
      FileWrite(f, "balance=" + DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2) + " equity=" + DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2));
      FileClose(f);
     }
   f = FileOpen("evo_forward_open.csv", FILE_WRITE | FILE_CSV | FILE_ANSI, ',');
   if(f == INVALID_HANDLE) return;
   FileWrite(f, "snapshot", "ticket", "time", "symbol", "magic", "type", "volume", "price_open", "profit", "swap");
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0 || !CoMagic(PositionGetInteger(POSITION_MAGIC))) continue;
      FileWrite(f, TimeToString(TimeCurrent(), TIME_DATE | TIME_SECONDS), t,
                TimeToString((datetime)PositionGetInteger(POSITION_TIME), TIME_DATE | TIME_SECONDS),
                PositionGetString(POSITION_SYMBOL), PositionGetInteger(POSITION_MAGIC),
                PositionGetInteger(POSITION_TYPE), PositionGetDouble(POSITION_VOLUME),
                PositionGetDouble(POSITION_PRICE_OPEN), PositionGetDouble(POSITION_PROFIT),
                PositionGetDouble(POSITION_SWAP));
     }
   FileClose(f);
  }
