//+------------------------------------------------------------------+
//| BRAIN_V24_MRZ_Trail_D1.mq5 - brain2 vong 24: z50 < -2 mua / > 2 ban |
//| z = (close - SMA50)/STD50 (ddof 1) nen D1 vua dong; SL 1,5 ATR, trailing 2 ATR, toi da 72 nen. |
//| MO PHONG - vong 24 KHONG SONG (Holm 1,0). Chi de backtest/so sanh. |
//+------------------------------------------------------------------+
#property copyright "brain2"
#property version   "1.00"
#include "BRAIN_V24_Chung.mqh"
