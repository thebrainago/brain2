# URL bị chặn, phần máy tự gom (tự sinh bởi `python tru/seeker.py url-bi-chan`)

Danh sách chọn tay theo nguồn nằm ở `reports/URL_BI_CHAN.md` (tác vụ Seeker đa nguồn, lưu vào `data/seeker_da_nguon/nhap_tay/<nguồn>/<id>.<đuôi>`). File này bổ sung phần máy tự gom. Cả hai thư mục đều được ống dẫn đọc.

Máy **không** vượt Cloudflare, captcha hay chặn bot, và không dùng Browser MCP hay CDP để lách. Anh mở các trang dưới đây bằng Chrome của mình (đăng nhập nếu cần), rồi lưu vào **thư mục nhập tay** (mặc định `E:\brain2_nhap\`, đổi bằng biến `BRAIN_NHAP_TAY` hoặc `thu_muc_nhap_tay` trong `config/ong_dan.json`). Nhận: `.mq4` `.mq5` `.ex4` `.ex5` `.set` `.htm` `.csv` (xuất lịch sử lệnh) `.pine` `.py` `.zip`:

- EA / chỉ báo: file `.mq4` / `.mq5` (hoặc `.ex4` / `.ex5` nếu chỉ có bản biên dịch), kèm `.set` cùng tên nếu có;
- statement hoặc báo cáo tester: lưu trang `.htm`;
- trang có mã hiển thị trên web: Ctrl+S, chọn "Webpage, HTML only".

Đặt tên file **bắt đầu bằng mã ở cột Mã** (ví dụ `U1a2b3c_ten_ea.mq5`) để danh sách tự đánh dấu ĐÃ NHẬP. Sau đó `python3 ong_dan.py chay` tự đọc, phân loại và đưa vào chuỗi. Trang trả phí đã bị loại (không mua gì).

## 1. Máy bị chặn khi đọc (8)

| Mã | URL | Nguồn | Lý do | Trạng thái |
|---|---|---|---|---|
| U9c83a0 | https://traderviet.com/forums/robot-ea-indicator.44/ | doc_nhieu_trang:traderviet_ea#0 | chuyen_huong_la 200 | chờ mở tay |
| - | mql5_signals | nguon_can_trinh_duyet | trang render bang JS - HTML tho khong co link signal nao | chờ mở tay |
| - | reddit | nguon_can_trinh_duyet | 403 voi ca www.reddit.com lan old.reddit.com | chờ mở tay |
| - | myfxbook | nguon_can_trinh_duyet | SSLError khi bat tay | chờ mở tay |
| - | ssrn | nguon_can_trinh_duyet | SSLError khi bat tay | chờ mở tay |
| - | cftc_cot | nguon_can_trinh_duyet | 403 tu publicreporting.cftc.gov | chờ mở tay |
| - | darwinex | nguon_can_trinh_duyet | can dang nhap | chờ mở tay |
| - | fred | nguon_can_trinh_duyet | ConnectionReset - Banker da chuyen sang Yahoo/ECB/WorldBank | chờ mở tay |

## 2. Ứng viên chỉ có URL, cần mở tay để lấy mã / lệnh (200, điểm ưu tiên cao trước)

| Mã | Tên | Nguồn | Loại | Phong cách | URL | Trạng thái |
|---|---|---|---|---|---|---|
| U3e41d7 | MT5-CoupleHedgeEA | mql5_codebase | ea_hoan_thien | grid,hedge,news,recovery | https://www.mql5.com/en/code/29115 | ĐÃ NHẬP |
| U823cd1 | VR Smart Grid Lite MT5 | mql5_codebase | ea_hoan_thien | grid,martingale,news,trend | https://www.mql5.com/en/code/27440 | chờ mở tay |
| U2f9602 | Range BreakOut EA | mql5_codebase | ea_hoan_thien | breakout,grid,news,trailing | https://www.mql5.com/en/code/26451 | chờ mở tay |
| U2b17a5 | Reversing Grid on Limit orders | mql5_codebase | ea_hoan_thien | breakout,grid,news,trailing | https://www.mql5.com/en/code/26418 | chờ mở tay |
| Ua862d5 | RSI Levels Expert Advisor | mql5_codebase | ea_hoan_thien | martingale,mean_reversion,trailing,trend | https://www.mql5.com/en/code/26317 | chờ mở tay |
| U5e46f7 | EMA LWMA RSI | mql5_codebase | ea_hoan_thien | dca,hedge,mean_reversion,news | https://www.mql5.com/en/code/23239 | chờ mở tay |
| U5705fa | Dynamic averaging | mql5_codebase | ea_hoan_thien | dca,mean_reversion,news | https://www.mql5.com/en/code/23319 | chờ mở tay |
| U5191eb | Smoothing Average | mql5_codebase | ea_hoan_thien | grid,martingale,mean_reversion,news | https://www.mql5.com/en/code/22653 | chờ mở tay |
| Uc83b9c | ScalpWiz 9001 | mql5_codebase | ea_hoan_thien | hedge,mean_reversion,news,scalp | https://www.mql5.com/en/code/22678 | chờ mở tay |
| U9c9782 | Hedge any positions | mql5_codebase | ea_hoan_thien | hedge,news,session | https://www.mql5.com/en/code/22823 | chờ mở tay |
| U6a41c6 | Basket Closer Profit/Loss | mql5_codebase | ea_hoan_thien | basket,news | https://www.mql5.com/en/code/29607 | chờ mở tay |
| Ua4726a | MultiMartin | mql5_codebase | ea_hoan_thien | martingale,session,trailing | https://www.mql5.com/en/code/27286 | chờ mở tay |
| Uc37a0d | Exp_ColorMaRsi-Trigger_MMRec_Duplex | mql5_codebase | ea_hoan_thien | martingale,news,trend | https://www.mql5.com/en/code/23292 | chờ mở tay |
| U8e0453 | RSI RFTL EA | mql5_codebase | ea_hoan_thien | grid,hedge,martingale,mean_reversion | https://www.mql5.com/en/code/22662 | chờ mở tay |
| U210390 | RoNz Simple Scalper Rapid-Fire Strategy EA v1.03 | mql5_codebase | ea_hoan_thien | ml_ai,news,scalp,trailing | https://www.mql5.com/en/code/12177 | chờ mở tay |
| U2ba2be | Turtle Trader | mql5_codebase | ea_hoan_thien | news,trend | https://www.mql5.com/en/code/11122 | chờ mở tay |
| U85b2c9 | Take-profit Eur/Usd | mql5_codebase | ea_hoan_thien | mean_reversion,news | https://www.mql5.com/en/code/9845 | chờ mở tay |
| U19a051 | Dodgy Backtest Example | mql5_codebase | ea_hoan_thien | news,trend | https://www.mql5.com/en/code/9500 | chờ mở tay |
| Ue4889e | SilverTrend v3 | mql5_codebase | ea_hoan_thien | news,trend | https://www.mql5.com/en/code/7876 | chờ mở tay |
| Ubd23bf | Aegis Quantum Lite | mql5_codebase | ea_hoan_thien | dca,grid,martingale,mean_reversion | https://www.mql5.com/en/code/75002 | chờ mở tay |
| U418c99 | Higher period Bollinger Band breakout and retrace  | mql5_codebase | ea_hoan_thien | breakout,mean_reversion,news,trailing | https://www.mql5.com/en/code/24620 | chờ mở tay |
| Ua0963a | Market Miner | mql5_codebase | ea_hoan_thien | basket,breakout,mean_reversion,trend | https://www.mql5.com/en/code/74818 | chờ mở tay |
| U8b0e3b | Ichimoku | mql5_codebase | ea_hoan_thien | grid,hedge,martingale,trailing | https://www.mql5.com/en/code/23469 | chờ mở tay |
| U14c17e | Macd 1 Min Scalper | mql5_codebase | ea_hoan_thien | grid,hedge,scalp,trailing | https://www.mql5.com/en/code/23247 | chờ mở tay |
| U93feeb | 1 Minute Scalper | mql5_codebase | ea_hoan_thien | grid,hedge,scalp,trailing | https://www.mql5.com/en/code/22843 | chờ mở tay |
| U1588b9 | 5 Minutes Scalper | mql5_codebase | ea_hoan_thien | grid,hedge,scalp,trailing | https://www.mql5.com/en/code/22828 | chờ mở tay |
| U3b1dbc | Ichimoku Rretracement | mql5_codebase | ea_hoan_thien | grid,hedge,news,trailing | https://www.mql5.com/en/code/22321 | chờ mở tay |
| U83a430 | Hedging_Zone_Recovery_Area | mql5_codebase | ea_hoan_thien | basket,hedge,martingale,mean_reversion | https://www.mql5.com/en/code/20266 | chờ mở tay |
| U123494 | Self Optimizing RSI or MFI Trader | mql5_codebase | ea_hoan_thien | dca,mean_reversion | https://www.mql5.com/en/code/19392 | chờ mở tay |
| Uaa213d | Pending order grid | mql5_codebase | ea_hoan_thien | grid,mean_reversion,news,trailing | https://www.mql5.com/en/code/17984 | chờ mở tay |
| U5a68bd | Proper Bot | mql5_codebase | ea_hoan_thien | grid,martingale,mean_reversion,news | https://www.mql5.com/en/code/17373 | chờ mở tay |
| Ucc512f | Ichimoku Kinko Hyo System | mql5_codebase | ea_hoan_thien | breakout,martingale,news,trend | https://www.mql5.com/en/code/16972 | chờ mở tay |
| U1331d3 | News EA Template without DLL | mql5_codebase | ea_hoan_thien | basket,news | https://www.mql5.com/en/code/16308 | chờ mở tay |
| U296cc6 | Grid assistant | mql5_codebase | ea_hoan_thien | grid,mean_reversion,trailing | https://www.mql5.com/en/code/16093 | chờ mở tay |
| U2044d1 | The simplest RSI-based EA | mql5_codebase | ea_hoan_thien | grid,martingale,mean_reversion,news | https://www.mql5.com/en/code/16069 | chờ mở tay |
| U8269dd | Limits Martin | mql5_codebase | ea_hoan_thien | martingale,mean_reversion,trailing | https://www.mql5.com/en/code/16031 | chờ mở tay |
| U5d99cf | MartingailExpert | mql5_codebase | ea_hoan_thien | martingale,news,trailing | https://www.mql5.com/en/code/7613 | chờ mở tay |
| Ubf996b | EA Hedge Average | mql5_codebase | ea_hoan_thien | hedge,mean_reversion,news,trailing | https://www.mql5.com/en/code/15004 | chờ mở tay |
| Uc7c726 | RSI_Expert_v2.0 | mql5_codebase | ea_hoan_thien | martingale,news | https://www.mql5.com/en/code/14476 | chờ mở tay |
| U3ad7d0 | Grid | mql5_codebase | ea_hoan_thien | grid,news | https://www.mql5.com/en/code/12947 | chờ mở tay |
| U65178a | Expert_RSI_Stochastic_MA | mql5_codebase | ea_hoan_thien | martingale,mean_reversion,trailing | https://www.mql5.com/en/code/13960 | chờ mở tay |
| Uf51d66 | Simple News | mql5_codebase | ea_hoan_thien | grid,news,scalp,trailing | https://www.mql5.com/en/code/14200 | chờ mở tay |
| U63cf24 | Trend_Catcher | mql5_codebase | ea_hoan_thien | martingale,trailing,trend | https://www.mql5.com/en/code/13661 | chờ mở tay |
| U4f21d2 | ExpMartin | mql5_codebase | ea_hoan_thien | martingale,news | https://www.mql5.com/en/code/13532 | chờ mở tay |
| U5697fe | Close by Equity Percent | mql5_codebase | ea_hoan_thien | hedge,news | https://www.mql5.com/en/code/12430 | chờ mở tay |
| U6bc217 | Profit Counter | mql5_codebase | ea_hoan_thien | hedge,news,trailing | https://www.mql5.com/en/code/12207 | chờ mở tay |
| Ua6e2a7 | Close@Profit | mql5_codebase | ea_hoan_thien | grid,mean_reversion,news,trend | https://www.mql5.com/en/code/11473 | chờ mở tay |
| U736204 | STRADDLE NEWS | mql5_codebase | ea_hoan_thien | hedge,news,trailing | https://www.mql5.com/en/code/11003 | chờ mở tay |
| Uaa7569 | Order-Tool "Hedger" | mql5_codebase | ea_hoan_thien | hedge,trailing | https://www.mql5.com/en/code/10968 | chờ mở tay |
| U23f66f | Martini | mql5_codebase | ea_hoan_thien | martingale,news | https://www.mql5.com/en/code/10561 | chờ mở tay |
| U45be16 | RampokScalp | mql5_codebase | ea_hoan_thien | martingale,scalp,trend | https://www.mql5.com/en/code/10657 | chờ mở tay |
| U17ec8b | X bug free version v3.0 | mql5_codebase | ea_hoan_thien | grid,news | https://www.mql5.com/en/code/10479 | chờ mở tay |
| Ub5f2a6 | 204060 Program AIGrid System | mql5_codebase | ea_hoan_thien | grid,news,trailing,trend | https://www.mql5.com/en/code/10398 | chờ mở tay |
| Ub0952b | Simple Adviser EMA WMA RSI | mql5_codebase | ea_hoan_thien | hedge,mean_reversion,news,trailing | https://www.mql5.com/en/code/9619 | chờ mở tay |
| Ud9fc76 | EnvelopeMA version 0.0.1.beta | mql5_codebase | ea_hoan_thien | martingale,prop_risk,trend | https://www.mql5.com/en/code/9533 | chờ mở tay |
| U56000a | 20 pips a day opposite "yesterday's trend" | mql5_codebase | ea_hoan_thien | martingale,mean_reversion,news,scalp | https://www.mql5.com/en/code/8518 | chờ mở tay |
| Ua0e713 | 10 pips a day opposite "yesterday's trend" | mql5_codebase | ea_hoan_thien | martingale,trailing,trend | https://www.mql5.com/en/code/8468 | chờ mở tay |
| U80904d | EES Hedger - Take the other side of the trade - bu | mql5_codebase | ea_hoan_thien | hedge,mean_reversion,news,trailing | https://www.mql5.com/en/code/8320 | chờ mở tay |
| Uab5da7 | EMA Cross Contest Hedged | mql5_codebase | ea_hoan_thien | hedge,news,trend | https://www.mql5.com/en/code/7700 | chờ mở tay |
| U88d37b | OverHedgeV2 | mql5_codebase | ea_hoan_thien | hedge,news | https://www.mql5.com/en/code/7623 | chờ mở tay |
| U45cd77 | CoupleHedgeEA | mql5_codebase | ea_hoan_thien | grid,hedge,ml_ai,news | https://www.mql5.com/en/code/27369 | chờ mở tay |
| Ufb2a39 | TokyoSessionEA | mql5_codebase | ea_hoan_thien | hedge,ml_ai,news,scalp | https://www.mql5.com/en/code/27281 | chờ mở tay |
| U4696fa | Backtesting 3commas DCA Bot v2 | tradingview | ea_hoan_thien | dca | https://www.tradingview.com/script/8d6Auyst-Backtesting-3commas-DCA-Bot-v2/ | chờ mở tay |
| U075e43 | CycleMarketOrder(GRID TRADE CODE) | mql5_codebase | ea_hoan_thien | grid,news,trailing | https://www.mql5.com/en/code/23272 | chờ mở tay |
| Ua47e27 | Trendline Breaks with Multi Fibonacci Supertrend S | tradingview | ea_hoan_thien | grid,trend,breakout | https://www.tradingview.com/script/aVzNdTMg-Trendline-Breaks-with-Multi-Fibonacci-Supertrend-Strategy/ | chờ mở tay |
| U2083a6 | AUTOMATIC GRID BOT STRATEGY [ilovealgotrading] | tradingview | ea_hoan_thien | grid,trend | https://www.tradingview.com/script/6qZpzElZ-AUTOMATIC-GRID-BOT-STRATEGY-ilovealgotrading/ | chờ mở tay |
| U3ffe8f | DCA Bot Long/Short | tradingview | ea_hoan_thien | dca | https://www.tradingview.com/script/LTcMeU50-DCA-Bot-Long-Short/ | chờ mở tay |
| Ua58a76 | Grid Like Strategy | tradingview | ea_hoan_thien | grid,martingale,recovery | https://www.tradingview.com/script/oxvR5vMy-Grid-Like-Strategy/ | chờ mở tay |
| U6d60f2 | Bounce Number for Grid/Martingale strategies Lot S | mql5_codebase | ea_hoan_thien | grid,martingale | https://www.mql5.com/en/code/47874 | chờ mở tay |
| U76b9d3 | FreedX Grid Backtest | tradingview | ea_hoan_thien | grid | https://www.tradingview.com/script/4J80gPhd-FreedX-Grid-Backtest/ | chờ mở tay |
| U3e1f48 | GRID SPOT TRADING ALGORITHM - GRID BOT TRADING STR | tradingview | ea_hoan_thien | grid,hedge | https://www.tradingview.com/script/LK1zL4D8-GRID-SPOT-TRADING-ALGORITHM-GRID-BOT-TRADING-STRATEGY/ | chờ mở tay |
| U37975b | DCA Bot Emulator | tradingview | ea_hoan_thien | dca | https://www.tradingview.com/script/vyStpg6g-DCA-Bot-Emulator/ | chờ mở tay |
| U83074a | Rocket Grid Algorithm - The Quant Science | tradingview | ea_hoan_thien | grid,trend,mean_reversion | https://www.tradingview.com/script/lm2BJL4V-Rocket-Grid-Algorithm-The-Quant-Science/ | chờ mở tay |
| Ua312b7 | Zendog V2 backtest DCA bot 3commas | tradingview | ea_hoan_thien | dca | https://www.tradingview.com/script/9NXf1Bqb-Zendog-V2-backtest-DCA-bot-3commas/ | chờ mở tay |
| U219cb5 | (IK) Grid Script | tradingview | ea_hoan_thien | grid,trend | https://www.tradingview.com/script/IIchZZ2m-IK-Grid-Script/ | chờ mở tay |
| Uac6468 | Classic 2 Moving Averages crossover EA | mql5_codebase | ea_hoan_thien | mean_reversion,news,trend | https://www.mql5.com/en/code/26315 | chờ mở tay |
| Uf73d50 | Daily range | mql5_codebase | ea_hoan_thien | ml_ai,news | https://www.mql5.com/en/code/23334 | chờ mở tay |
| U606a6e | MA Trend | mql5_codebase | ea_hoan_thien | trailing,trend | https://www.mql5.com/en/code/23589 | chờ mở tay |
| Ua6dbcf | Orion Algo Strategy v2.0 | tradingview | ea_hoan_thien | dca | https://www.tradingview.com/script/1QOQnMVn-Orion-Algo-Strategy-v2-0/ | chờ mở tay |
| Uaea668 | Smart Grid Scalping (Pullback) Strategy[BullByte] | tradingview | ea_hoan_thien | grid,scalp,mean_reversion | https://www.tradingview.com/script/B3Ey5I4g-Smart-Grid-Scalping-Pullback-Strategy-BullByte/ | chờ mở tay |
| U3993f4 | CoGrid Management | tradingview | ea_hoan_thien | grid | https://www.tradingview.com/script/3kMUl7fJ/ | chờ mở tay |
| U181bd0 | 3Commas Bot DCA Backtester & Signals FREE | tradingview | ea_hoan_thien | dca | https://www.tradingview.com/script/Txo3OEBa-3Commas-Bot-DCA-Backtester-Signals-FREE/ | chờ mở tay |
| U7827b0 | Grid Spot Trading Algorithm V2 - The Quant Science | tradingview | ea_hoan_thien | grid | https://www.tradingview.com/script/ZJseWDie-Grid-Spot-Trading-Algorithm-V2-The-Quant-Science/ | chờ mở tay |
| U5920ac | LB & SB using RSI & Momentum | mql5_codebase | ea_hoan_thien | mean_reversion,news,trend | https://www.mql5.com/en/code/16575 | chờ mở tay |
| U08dfab | EMA - Expert Advisor based on intersections of two | mql5_codebase | ea_hoan_thien | breakout,news,trend | https://www.mql5.com/en/code/7675 | chờ mở tay |
| U7421d1 | Simple Multiple Timeframe Moving Average | mql5_codebase | ea_hoan_thien | news,prop_risk,trend | https://www.mql5.com/en/code/14752 | chờ mở tay |
| Ue0de8e | Example of RSI Automated | mql5_codebase | ea_hoan_thien | mean_reversion,news,trailing | https://www.mql5.com/en/code/14804 | chờ mở tay |
| U84752b | The Fraktrak xonax Expert Advisor based on the fra | mql5_codebase | ea_hoan_thien | breakout,news,trailing | https://www.mql5.com/en/code/14613 | chờ mở tay |
| U65c528 | Trend Expert Advisor based on the Escort strategy | mql5_codebase | ea_hoan_thien | news,trailing,trend | https://www.mql5.com/en/code/13419 | chờ mở tay |
| Uea0efc | Calc Profit Loss on LinePrice | mql5_codebase | ea_hoan_thien | news | https://www.mql5.com/en/code/13330 | chờ mở tay |
| U35ebe0 | ScalpWiz 9001 | mql5_codebase | ea_hoan_thien | mean_reversion,news,scalp | https://www.mql5.com/en/code/14502 | chờ mở tay |
| Uaa392a | RSI_Expert | mql5_codebase | ea_hoan_thien | mean_reversion,news,trailing,trend | https://www.mql5.com/en/code/13809 | chờ mở tay |
| U297dfc | The Expert Advisor on Traffic Light trend strategy | mql5_codebase | ea_hoan_thien | trailing,trend | https://www.mql5.com/en/code/13802 | chờ mở tay |
| Ubfea39 | News Hour Trade | mql5_codebase | ea_hoan_thien | news,trailing,trend | https://www.mql5.com/en/code/13509 | chờ mở tay |
| Uaeef75 | Angry Bird (Scalping) | mql5_codebase | ea_hoan_thien | news,prop_risk,scalp | https://www.mql5.com/en/code/12872 | chờ mở tay |
| U2f5b99 | Smoothing Average | mql5_codebase | ea_hoan_thien | news,scalp,trailing,trend | https://www.mql5.com/en/code/12789 | chờ mở tay |
| Ua14981 | Multi-Trendlines Breakout | mql5_codebase | ea_hoan_thien | breakout,news,trend | https://www.mql5.com/en/code/12598 | chờ mở tay |
| U1c436c | Hybrid Scalper | mql5_codebase | ea_hoan_thien | mean_reversion,news,scalp,session | https://www.mql5.com/en/code/12298 | chờ mở tay |
| U4fdee5 | THREE MOVING AVERAGE EA (X3MA EA) | mql5_codebase | ea_hoan_thien | news,trailing,trend | https://www.mql5.com/en/code/11057 | chờ mở tay |
| U22361c | PZ Reversal Trend Following EA | mql5_codebase | ea_hoan_thien | breakout,news,trend | https://www.mql5.com/en/code/10956 | chờ mở tay |
| U241740 | BreakOut | mql5_codebase | ea_hoan_thien | breakout,news,trailing,trend | https://www.mql5.com/en/code/10925 | chờ mở tay |
| U378422 | MMA_Breakout_strategy_Volume I - coded by WhooDoo2 | mql5_codebase | ea_hoan_thien | breakout,trend | https://www.mql5.com/en/code/10848 | chờ mở tay |
| U67d06d | Automatic stoploss and takeprofit | mql5_codebase | ea_hoan_thien | news,trend | https://www.mql5.com/en/code/10810 | chờ mở tay |
| Ud3965f | Auto news trader | mql5_codebase | ea_hoan_thien | news | https://www.mql5.com/en/code/10017 | chờ mở tay |
| U48db2a | earlyOpenTrend | mql5_codebase | ea_hoan_thien | trend | https://www.mql5.com/en/code/9826 | chờ mở tay |
| Ua3dcec | ORDER MANAGEMENT FOR EA DEVELOPMENT - LAST VERSION | mql5_codebase | ea_hoan_thien | news,trend | https://www.mql5.com/en/code/9718 | chờ mở tay |
| U888117 | Trend RDS | mql5_codebase | ea_hoan_thien | mean_reversion,news,trailing,trend | https://www.mql5.com/en/code/8322 | chờ mở tay |
| Uc62151 | moving average position system | mql5_codebase | ea_hoan_thien | news | https://www.mql5.com/en/code/8313 | chờ mở tay |
| Uc6cc0a | The implementation of the MACD pattern Trend conti | mql5_codebase | ea_hoan_thien | trend | https://www.mql5.com/en/code/8249 | chờ mở tay |
| U666af2 | TrendCapture | mql5_codebase | ea_hoan_thien | news,prop_risk,trend | https://www.mql5.com/en/code/8146 | chờ mở tay |
| U8710c3 | Moving Average Trade System | mql5_codebase | ea_hoan_thien | trailing | https://www.mql5.com/en/code/8040 | chờ mở tay |
| U607c65 | Short-Term Trends | mql5_codebase | ea_hoan_thien | news,trailing,trend | https://www.mql5.com/en/code/8031 | chờ mở tay |
| U6fade5 | "Forex Profit" System | mql5_codebase | ea_hoan_thien | news,trend | https://www.mql5.com/en/code/8117 | chờ mở tay |
| Uca7adc | BreakOut15 | mql5_codebase | ea_hoan_thien | breakout,news | https://www.mql5.com/en/code/7660 | chờ mở tay |
| Ub655d1 | Volatility Trader and Breakout EA (X-liquidex) | mql5_codebase | ea_hoan_thien | breakout,mean_reversion,news,scalp | https://www.mql5.com/en/code/11449 | chờ mở tay |
| U8a9779 | Ultimate Strategy Template | tradingview | ea_hoan_thien |  | https://www.tradingview.com/script/2lGyzYkC-Ultimate-Strategy-Template/ | chờ mở tay |
| U67af57 | Backtest Adapter | tradingview | ea_hoan_thien | ml_ai | https://www.tradingview.com/script/Pu38F2pB-Backtest-Adapter/ | chờ mở tay |
| U3a5cfd | Lorentzian Classification Strategy  | tradingview | ea_hoan_thien | trend,ml_ai | https://www.tradingview.com/script/SfyBCHIJ/ | chờ mở tay |
| U971e61 | AI SuperTrend x Pivot Percentile - Strategy [Prese | tradingview | ea_hoan_thien | trend | https://www.tradingview.com/script/eC3qAYNQ-AI-SuperTrend-x-Pivot-Percentile-Strategy-PresentTrading/ | chờ mở tay |
| Ue3d619 | Price and Volume Breakout Buy Strategy [TradeDots] | tradingview | ea_hoan_thien | trend,breakout | https://www.tradingview.com/script/jc2hs2qK-Price-and-Volume-Breakout-Buy-Strategy-TradeDots/ | chờ mở tay |
| U472180 | Relative Moving Average EA | mql5_codebase | ea_hoan_thien | trailing,trend | https://www.mql5.com/en/code/75473 | chờ mở tay |
| U432560 | Hammers & Stars Strategy | tradingview | ea_hoan_thien |  | https://www.tradingview.com/script/t776tkZv-Hammers-Stars-Strategy/ | chờ mở tay |
| U9dc9d8 | Scalping Support Resistance Strategy | tradingview | ea_hoan_thien | scalp | https://www.tradingview.com/script/gp332Dao-Scalping-Support-Resistance-Strategy/ | chờ mở tay |
| U9fb84b | 2 Days Breakout | mql5_codebase | ea_hoan_thien | breakout,trailing,trend | https://www.mql5.com/en/code/24135 | chờ mở tay |
| U7b7ade | Captain Backtest Model [TFO] | tradingview | ea_hoan_thien |  | https://www.tradingview.com/script/tOQ8gnxj-Captain-Backtest-Model-TFO/ | chờ mở tay |
| U95aa3e | Strategy for UT Bot Alerts indicator  | tradingview | ea_hoan_thien |  | https://www.tradingview.com/script/R9nsvSZR/ | chờ mở tay |
| U6e8d94 | Unseasonalised Average Trading Range and Forecast  | mql5_codebase | ea_hoan_thien | breakout,news | https://www.mql5.com/en/code/11055 | chờ mở tay |
| U0b681f | Scalping with Williams %R, MACD, and SMA (1m) | tradingview | ea_hoan_thien | trend,scalp,mean_reversion | https://www.tradingview.com/script/975ByLQ5-Scalping-with-Williams-R-MACD-and-SMA-1m/ | chờ mở tay |
| U3d5374 | Template Trailing Strategy (Backtester) | tradingview | ea_hoan_thien | trailing | https://www.tradingview.com/script/n8bgynWl-Template-Trailing-Strategy-Backtester/ | chờ mở tay |
| Uf96eea | Scalping Trading System bot Crypto and Stocks | tradingview | ea_hoan_thien | trend,scalp | https://www.tradingview.com/script/YotdMm0M-Scalping-Trading-System-bot-Crypto-and-Stocks/ | chờ mở tay |
| U1e642d | EDMA Scalping Strategy (Exponentially Deviating Mo | tradingview | ea_hoan_thien | trend,scalp | https://www.tradingview.com/script/CJesxF5m-EDMA-Scalping-Strategy-Exponentially-Deviating-Moving-Average/ | chờ mở tay |
| U220e5f | Trade Adjustment Panel | mql5_codebase | ea_hoan_thien | news,session,trailing,trend | https://www.mql5.com/en/code/75818 | chờ mở tay |
| U7f726c | Dynamic Swing Anchored VWAP STRAT (Zeiierman/PineI | tradingview | ea_hoan_thien |  | https://www.tradingview.com/script/gjFSGRCo-Dynamic-Swing-Anchored-VWAP-STRAT-Zeiierman-PineIndicators/ | chờ mở tay |
| Ub796de | UT Bot v2 - ATR Trailing Stop | tradingview | ea_hoan_thien | trailing | https://www.tradingview.com/script/lDGmh7ou-UT-Bot-v2-ATR-Trailing-Stop/ | chờ mở tay |
| U9d4d06 | 3C QFL Mean reversal | tradingview | ea_hoan_thien | mean_reversion | https://www.tradingview.com/script/SDRM0bBY-3C-QFL-Mean-reversal/ | chờ mở tay |
| U1ae21e | RSI-VWAP Indicator % | tradingview | ea_hoan_thien | trend,mean_reversion | https://www.tradingview.com/script/d0FZtMLp/ | chờ mở tay |
| U47ce37 | ORB Heikin Ashi SPY 5min Correlation Strategy | tradingview | ea_hoan_thien | breakout | https://www.tradingview.com/script/QpJvYDzb-ORB-Heikin-Ashi-SPY-5min-Correlation-Strategy/ | chờ mở tay |
| Uc66ba1 | Bitcoin Scalping Strategy (Sampled with: PMARP+MAD | tradingview | ea_hoan_thien | scalp | https://www.tradingview.com/script/T4rBZCvC-Bitcoin-Scalping-Strategy-Sampled-with-PMARP-MADRID-MA-RIBBON/ | chờ mở tay |
| U180696 | Squeeze Momentum Strategy [LazyBear] Buy Sell TP S | tradingview | ea_hoan_thien | trend | https://www.tradingview.com/script/lEQZl0vE-Squeeze-Momentum-Strategy-LazyBear-Buy-Sell-TP-SL-Alerts/ | chờ mở tay |
| U17e0c9 | Gold/Silver 30m Only Strategy Buy/Sell Signals | tradingview | ea_hoan_thien | mean_reversion | https://www.tradingview.com/script/lx4O1PPu-Gold-Silver-30m-Only-Strategy-Buy-Sell-Signals/ | chờ mở tay |
| U183588 | Bollinger Bands - Breakout Strategy | tradingview | ea_hoan_thien | trend,breakout,mean_reversion | https://www.tradingview.com/script/sTFw2fOj/ | chờ mở tay |
| Uc4f2b4 | 5min MACD scalp by Joel | tradingview | ea_hoan_thien | trend,scalp | https://www.tradingview.com/script/qN11DuKy-5min-MACD-scalp-by-Joel/ | chờ mở tay |
| U2e33c8 | Forex Scalping 1min Bollinger Bands, RSI and ADX T | tradingview | ea_hoan_thien | scalp,mean_reversion | https://www.tradingview.com/script/sR1hePBi-Forex-Scalping-1min-Bollinger-Bands-RSI-and-ADX-Trading-System/ | chờ mở tay |
| Uc8dd4b | EWO,RSI advanced Signals Strategy - Exhaustion Fil | tradingview | ea_hoan_thien | trend,mean_reversion | https://www.tradingview.com/script/B7MQqWes-EWO-RSI-advanced-Signals-Strategy-Exhaustion-Filter/ | chờ mở tay |
| U7df77b | TICK Scalping strategy, SPY 1 min | tradingview | ea_hoan_thien | scalp | https://www.tradingview.com/script/yiBwexdm-TICK-Scalping-strategy-SPY-1-min/ | chờ mở tay |
| U25db96 | Machine Learning: SuperTrend Strategy TP/SL [YinYa | tradingview | ea_hoan_thien | trend,ml_ai | https://www.tradingview.com/script/9Mm3qKME-Machine-Learning-SuperTrend-Strategy-TP-SL-YinYangAlgorithms/ | chờ mở tay |
| U0ad02b | Gold Breakout 15M Strategy [WillyAlgoTrader] | tradingview | ea_hoan_thien | breakout | https://www.tradingview.com/script/HnelYN0A-Gold-Breakout-15M-Strategy-WillyAlgoTrader/ | chờ mở tay |
| Uadc998 | *Backtesting System | tradingview | ea_hoan_thien | prop_risk | https://www.tradingview.com/script/GRTkk75x-Backtesting-System/ | chờ mở tay |
| Uaccfc1 | BBTrend w SuperTrend decision - Strategy [presentT | tradingview | ea_hoan_thien | trend,mean_reversion,prop_risk | https://www.tradingview.com/script/7C1kIEOn-BBTrend-w-SuperTrend-decision-Strategy-presentTrading/ | chờ mở tay |
| Ufbe3b8 | Simple and Profitable Scalping Strategy (ForexSign | tradingview | ea_hoan_thien | scalp,prop_risk | https://www.tradingview.com/script/x4za4NFZ-Simple-and-Profitable-Scalping-Strategy-ForexSignals-TV/ | chờ mở tay |
| U269b2e | RSI Divergence Strategy | tradingview | ea_hoan_thien | mean_reversion,trailing | https://www.tradingview.com/script/ASVRhqFM/ | chờ mở tay |
| U2e1346 | SUPPORT RESISTANCE STRATEGY [5MIN TF] | tradingview | ea_hoan_thien | breakout | https://www.tradingview.com/script/KOfsPM9h-SUPPORT-RESISTANCE-STRATEGY-5MIN-TF/ | chờ mở tay |
| Ud199f8 | Strategy: HMA 50 + Supertrend Sniper | tradingview | ea_hoan_thien | trend | https://www.tradingview.com/script/3SHJZytF/ | chờ mở tay |
| U99f968 | Fractal Breakout Strategy [KL] | tradingview | ea_hoan_thien | breakout,trailing | https://www.tradingview.com/script/agyP7x3R-Fractal-Breakout-Strategy-KL/ | chờ mở tay |
| U1bd051 | How to use Leverage and Margin in PineScript | tradingview | ea_hoan_thien |  | https://www.tradingview.com/script/9Iwinz7I-How-to-use-Leverage-and-Margin-in-PineScript/ | chờ mở tay |
| Uda944a | Bollinger Bands Enhanced Strategy | tradingview | ea_hoan_thien | trend,mean_reversion,trailing | https://www.tradingview.com/script/V4B5nKIx-Bollinger-Bands-Enhanced-Strategy/ | chờ mở tay |
| Ud6e7b2 | FlexiSuperTrend - Strategy [presentTrading] | tradingview | ea_hoan_thien | trend | https://www.tradingview.com/script/y9noW915-FlexiSuperTrend-Strategy-presentTrading/ | chờ mở tay |
| Uddff44 | Buy - Take Profit OR Stop Loss % Based | tradingview | ea_hoan_thien |  | https://www.tradingview.com/script/WD09HFwm-Buy-Take-Profit-OR-Stop-Loss-Based/ | chờ mở tay |
| U30849d | ORB Strategy [LuciTech] | tradingview | ea_hoan_thien | breakout,session | https://www.tradingview.com/script/10yYqaY7-ORB-Strategy-LuciTech/ | chờ mở tay |
| Ua88ab1 | Backtesting Module | tradingview | ea_hoan_thien |  | https://www.tradingview.com/script/uLY2TQdm/ | chờ mở tay |
| U147cb2 | 3 Candle Strike Stretegy | tradingview | ea_hoan_thien | trend | https://www.tradingview.com/script/zqbs2shU-3-Candle-Strike-Stretegy/ | chờ mở tay |
| U5cc7be | Universal Breakout Strategy [KedArc Quant] | tradingview | ea_hoan_thien | trend,breakout,mean_reversion,prop_risk | https://www.tradingview.com/script/tSoUhlM9-Universal-Breakout-Strategy-KedArc-Quant/ | chờ mở tay |
| U0a74de | TradingView Alerts to MT4 MT5 - Forex, indices, co | tradingview | ea_hoan_thien |  | https://www.tradingview.com/script/BTSkg8IP-TradingView-Alerts-to-MT4-MT5-Forex-indices-commodities/ | chờ mở tay |
| U375c0d | Forex Fractal EMA Scalper | tradingview | ea_hoan_thien | scalp | https://www.tradingview.com/script/pgsJGhIg-Forex-Fractal-EMA-Scalper/ | chờ mở tay |
| U8a9fab | Ichimoku with MACD/ CMF/ TSI  | tradingview | ea_hoan_thien | trend | https://www.tradingview.com/script/Pjsgs9JO-Ichimoku-with-MACD-CMF-TSI/ | chờ mở tay |
| U33d730 | Multi-Step FlexiSuperTrend - Strategy [presentTrad | tradingview | ea_hoan_thien | trend | https://www.tradingview.com/script/FxxdXitn-Multi-Step-FlexiSuperTrend-Strategy-presentTrading/ | chờ mở tay |
| Uba8d87 | Coral Trend Pullback Strategy (TradeIQ) | tradingview | ea_hoan_thien | trend | https://www.tradingview.com/script/kc6Itas8-Coral-Trend-Pullback-Strategy-TradeIQ/ | chờ mở tay |
| Ucb06ff | Momentum Sequence Strategy+ [Herman] | tradingview | ea_hoan_thien | trend | https://www.tradingview.com/script/mmrInMTp-Momentum-Sequence-Strategy-Herman/ | chờ mở tay |
| U4abd84 | X48 - Strategy / MA Type Cross + TPSL / Future&Spo | tradingview | ea_hoan_thien | trend | https://www.tradingview.com/script/DAD06s8m-X48-Strategy-MA-Type-Cross-TPSL-Future-Spot-V-2/ | chờ mở tay |
| Ubfa8be | ATR Trend Strategy with Moving Average / Fixed TP/ | tradingview | ea_hoan_thien | trend,breakout,prop_risk | https://www.tradingview.com/script/fM3YQz8i-ATR-Trend-Strategy-with-Moving-Average-Fixed-TP-SL-version/ | chờ mở tay |
| U0b65ff | Scalping The Bull - Two EMA Strategy | tradingview | ea_hoan_thien | trend,scalp | https://www.tradingview.com/script/M7e4uwLN/ | chờ mở tay |
| Ub6ec37 | Yesterday’s High Breakout - Trend Following Strate | tradingview | ea_hoan_thien | trend,breakout,trailing | https://www.tradingview.com/script/JoYgHVFj-Yesterday-s-High-Breakout-Trend-Following-Strategy/ | chờ mở tay |
| U0c9c08 | Reversal Trading Bot Strategy[BullByte] | tradingview | ea_hoan_thien | trend,mean_reversion | https://www.tradingview.com/script/cXVnf1WH-Reversal-Trading-Bot-Strategy-BullByte/ | chờ mở tay |
| U921738 | 5 ema strategy | tradingview | ea_hoan_thien |  | https://www.tradingview.com/script/EaZHR7q6-5-ema-strategy/ | chờ mở tay |
| Udcde4f | Boom Hunter + Hull Suite + Volatility Oscillator S | tradingview | ea_hoan_thien | trend | https://www.tradingview.com/script/McuqT8px-Boom-Hunter-Hull-Suite-Volatility-Oscillator-Strategy/ | chờ mở tay |
| U099f42 | Vegas SuperTrend Enhanced - Strategy [presentTradi | tradingview | ea_hoan_thien | trend | https://www.tradingview.com/script/ec57c7xL-Vegas-SuperTrend-Enhanced-Strategy-presentTrading/ | chờ mở tay |
| U5cc3fa | Extremely high win rate FOREX swing strategy | tradingview | ea_hoan_thien | prop_risk | https://www.tradingview.com/script/8hZoUlTI-Extremely-high-win-rate-FOREX-swing-strategy/ | chờ mở tay |
| Uc706fb | Pivot Point SuperTrend Strategy +TrendFilter | tradingview | ea_hoan_thien | trend | https://www.tradingview.com/script/WpJ5ym7u-Pivot-Point-SuperTrend-Strategy-TrendFilter/ | chờ mở tay |
| Ueb0620 | Top 40 High Low Strategy for SPY, 5min | tradingview | ea_hoan_thien |  | https://www.tradingview.com/script/3BFuBf4F-Top-40-High-Low-Strategy-for-SPY-5min/ | chờ mở tay |
| U49809a | 3Commas Bollinger Strategy | tradingview | ea_hoan_thien | mean_reversion | https://www.tradingview.com/script/zaMgoLFt-3Commas-Bollinger-Strategy/ | chờ mở tay |
| U87b426 | BollingerBands Strat + pending order alerts via Tr | tradingview | ea_hoan_thien | mean_reversion | https://www.tradingview.com/script/a5CmxEJq-BollingerBands-Strat-pending-order-alerts-via-TradingConnector/ | chờ mở tay |
| Ud76a8a | London BreakOut Classic | tradingview | ea_hoan_thien | trend,breakout,session | https://www.tradingview.com/script/Fh42LHOM-London-BreakOut-Classic/ | chờ mở tay |
| U503b36 | RSI Strategy with alerts via TradingConnector to F | tradingview | ea_hoan_thien | mean_reversion | https://www.tradingview.com/script/kQY2gaLx-RSI-Strategy-with-alerts-via-TradingConnector-to-Forex/ | chờ mở tay |
| U627a67 | THE only Pattern | forexfactory | chi_bao | grid,news | https://www.forexfactory.com/thread/607008-the-only-pattern | chờ mở tay |
| U1e7199 | On Point | forexfactory | chi_bao | dca,news | https://www.forexfactory.com/thread/1047434-on-point | chờ mở tay |
| U68786c | trend catching with NonLagDot indicator | forexfactory | chi_bao | martingale,hedge,basket,trend | https://www.forexfactory.com/thread/571026-trend-catching-with-nonlagdot-indicator | chờ mở tay |
| U67f2ef | Nb 10.0 trend trading system | forexfactory | chi_bao | grid,trend,news | https://www.forexfactory.com/thread/308304-nb-100-trend-trading-system | chờ mở tay |
| Ub513d1 | Institutional ICT Killzones and Asian Range | mql5_codebase | chi_bao | mean_reversion,news,prop_risk,session | https://www.mql5.com/en/code/71073 | chờ mở tay |
| U5834df | Session Scalping Zones | mql5_codebase | chi_bao | breakout,news,scalp,session | https://www.mql5.com/en/code/75530 | chờ mở tay |
| U4efd0a | Trading Made Simple | forexfactory | chi_bao | news | https://www.forexfactory.com/thread/291622-trading-made-simple | chờ mở tay |
| U356677 | Pivot Trading | forexfactory | chi_bao | news | https://www.forexfactory.com/thread/588764-pivot-trading | chờ mở tay |
| U63d2d9 | Another simple system - Time-Frame 15 | forexfactory | chi_bao | news | https://www.forexfactory.com/thread/345586-another-simple-system-time-frame-15 | chờ mở tay |
| U73cc36 | Genesis Matrix Trading | forexfactory | chi_bao | news | https://www.forexfactory.com/thread/373796-genesis-matrix-trading | chờ mở tay |
| U847f5e | Highest Open / Lowest Open Trade | forexfactory | chi_bao | breakout,news,trailing | https://www.forexfactory.com/thread/590623-highest-open-lowest-open-trade | chờ mở tay |
| U916a5b | digger | forexfactory | chi_bao | trend,news | https://www.forexfactory.com/thread/1155290-digger | chờ mở tay |
| U3c7d10 | Symphonie Trader System | forexfactory | chi_bao | trend,news | https://www.forexfactory.com/thread/315572-symphonie-trader-system | chờ mở tay |
| Uac3194 | Extreme TMA System | forexfactory | chi_bao | news | https://www.forexfactory.com/thread/343533-extreme-tma-system | chờ mở tay |
| Udafbc3 | Psych Levels, Pivots, and Trendlines - Resurrected | forexfactory | chi_bao | trend,news,session | https://www.forexfactory.com/thread/98028-psych-levels-pivots-and-trendlines-resurrected | chờ mở tay |
| U56c3fc | Trading is as simple as 1-2-3 | forexfactory | chi_bao | news | https://www.forexfactory.com/thread/549745-trading-is-as-simple-as-1-2-3 | chờ mở tay |
| Uba28cc | The DIBS Method... No Free Lunch continues | forexfactory | chi_bao | news,session | https://www.forexfactory.com/thread/86766-the-dibs-method-no-free-lunch-continues | chờ mở tay |
