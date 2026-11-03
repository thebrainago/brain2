//+------------------------------------------------------------------+
//| BRAIN_DN_LuoiHedgeTP.mq5 — BẢN NHÁP từ dịch ngược tín hiệu MQL5   |
//| 2330430 (GBPUSD). Luật SUY LUẬN thống kê, KHÔNG phải mã gốc.      |
//| Lưới hai chiều: mỗi mức cách Buoc pip có 1 BUY và 1 SELL, mỗi lệnh |
//| TP = TP pip, không SL. Đóng hết khi lãi nổi tổng >= 0 và số lệnh   |
//| >= DongRoKhi. CHƯA chạy Strategy Tester — kết quả: CHƯA ĐO ĐƯỢC.   |
//+------------------------------------------------------------------+
#property strict
#include <Trade/Trade.mqh>
input double BuocPip    = 35;     // bước lưới (pip)
input double TPPip      = 35;     // TP từng lệnh (pip)
input double LotMoi1000 = 0.001;  // lot cho mỗi 1000 USD số dư
input int    MaxLenhMoiChieu = 60;
input int    DongRoKhi  = 6;
input long   Magic      = 2330430;
CTrade tr; double swap_cong = 0;

double Pip(){ return (_Digits==3||_Digits==5) ? 10*_Point : _Point; }
double LotMoi(){
   double l = LotMoi1000*AccountInfoDouble(ACCOUNT_BALANCE)/1000.0;
   double st = SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP), mn = SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN);
   return MathMax(mn, MathFloor(l/st)*st);
}
int OnInit(){ tr.SetExpertMagicNumber(Magic); EventSetTimer(60); return INIT_SUCCEEDED; }
void OnDeinit(const int r){ EventKillTimer(); }
void OnTimer(){ PrintFormat("swap cộng dồn %.2f", swap_cong); }
void OnTradeTransaction(const MqlTradeTransaction &t,const MqlTradeRequest &rq,const MqlTradeResult &rs){
   if(t.type==TRADE_TRANSACTION_DEAL_ADD && HistoryDealSelect(t.deal))
      swap_cong += HistoryDealGetDouble(t.deal, DEAL_SWAP);
}
void OnTick(){
   double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID), ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK), p=Pip();
   int nb=0, ns=0; double noi=0; bool gan_b=false, gan_s=false;
   for(int i=PositionsTotal()-1;i>=0;i--){
      ulong tk=PositionGetTicket(i); if(!PositionSelectByTicket(tk)) continue;
      if(PositionGetInteger(POSITION_MAGIC)!=Magic || PositionGetString(POSITION_SYMBOL)!=_Symbol) continue;
      double gm=PositionGetDouble(POSITION_PRICE_OPEN); noi += PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP);
      if(PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_BUY){ nb++; if(MathAbs(gm-ask)<BuocPip*p*0.999) gan_b=true; }
      else { ns++; if(MathAbs(gm-bid)<BuocPip*p*0.999) gan_s=true; }
   }
   if(nb+ns>=DongRoKhi && noi>=0){
      for(int i=PositionsTotal()-1;i>=0;i--){ ulong tk=PositionGetTicket(i);
         if(PositionSelectByTicket(tk) && PositionGetInteger(POSITION_MAGIC)==Magic && PositionGetString(POSITION_SYMBOL)==_Symbol) tr.PositionClose(tk); }
      return;
   }
   if(!gan_b && nb<MaxLenhMoiChieu) tr.Buy(LotMoi(),_Symbol,ask,0,ask+TPPip*p,"DN2330430");
   if(!gan_s && ns<MaxLenhMoiChieu) tr.Sell(LotMoi(),_Symbol,bid,0,bid-TPPip*p,"DN2330430");
}
