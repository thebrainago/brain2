//+------------------------------------------------------------------+
//| BRAIN_DN_RoDCAHedge.mq5 — BẢN NHÁP từ dịch ngược tín hiệu MQL5    |
//| 2262642 (AUDCAD). Luật SUY LUẬN thống kê, KHÔNG phải mã gốc.      |
//| Hai rổ BUY/SELL độc lập (hedge), lot đều; thêm lệnh khi giá đi    |
//| ngược BuocPip từ lệnh cuối; đóng cả rổ khi giá về giá trung bình  |
//| ± TPPip. Không SL. CHƯA chạy Strategy Tester — CHƯA ĐO ĐƯỢC.      |
//+------------------------------------------------------------------+
#property strict
#include <Trade/Trade.mqh>
input double BuocPip    = 15;
input double TPPip      = 11;
input double LotMoi1000 = 0.002;
input int    MaxLenhMoiRo = 140;
input long   Magic      = 2262642;
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
void XuLyRo(int chieu){   // +1 BUY, -1 SELL
   double p=Pip(), gia = chieu>0 ? SymbolInfoDouble(_Symbol,SYMBOL_BID) : SymbolInfoDouble(_Symbol,SYMBOL_ASK);
   int n=0; double sl=0, sw=0, cuoi=0; datetime tcuoi=0;
   for(int i=PositionsTotal()-1;i>=0;i--){
      ulong tk=PositionGetTicket(i); if(!PositionSelectByTicket(tk)) continue;
      if(PositionGetInteger(POSITION_MAGIC)!=Magic || PositionGetString(POSITION_SYMBOL)!=_Symbol) continue;
      int c = PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_BUY ? 1 : -1; if(c!=chieu) continue;
      double v=PositionGetDouble(POSITION_VOLUME), gm=PositionGetDouble(POSITION_PRICE_OPEN);
      n++; sl+=v; sw+=v*gm; if((datetime)PositionGetInteger(POSITION_TIME)>=tcuoi){ tcuoi=(datetime)PositionGetInteger(POSITION_TIME); cuoi=gm; }
   }
   if(n==0){ if(chieu>0) tr.Buy(LotMoi(),_Symbol); else tr.Sell(LotMoi(),_Symbol); return; }
   double tb=sw/sl;
   if(chieu*(gia-tb)>=TPPip*p){
      for(int i=PositionsTotal()-1;i>=0;i--){ ulong tk=PositionGetTicket(i);
         if(!PositionSelectByTicket(tk) || PositionGetInteger(POSITION_MAGIC)!=Magic || PositionGetString(POSITION_SYMBOL)!=_Symbol) continue;
         int c = PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_BUY ? 1 : -1; if(c==chieu) tr.PositionClose(tk); }
      return;
   }
   if(n<MaxLenhMoiRo && chieu*(cuoi-gia)>=BuocPip*p){ if(chieu>0) tr.Buy(LotMoi(),_Symbol); else tr.Sell(LotMoi(),_Symbol); }
}
void OnTick(){ XuLyRo(1); XuLyRo(-1); }
