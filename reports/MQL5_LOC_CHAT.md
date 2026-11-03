# Lọc CHẶT tín hiệu MQL5 công khai (03/11/2026)

Nguồn: `data/cong_khai/tin_hieu.jsonl` (đã quét). Số liệu đo trên trang tín hiệu MQL5; Growth MQL5 đã khử nạp/rút.
Tiêu chí: tuổi >= 24 tháng, tài khoản thật, <= 3 mã, DD < 80 %, CAGR > 10 %/năm, đường growth không cháy; lưới/martingale/DCA phải sống qua 03/2020 hoặc 2022.

- Tổng tín hiệu (sau gộp trùng): **1578**
- ĐẠT lọc chặt: **83**

## Lý do loại (một tín hiệu có thể nhiều lý do)

- tuổi < 24 tháng: 1122
- > 3 mã: 760
- CAGR <= 10 %/năm hoặc chưa đo: 408
- lưới/martingale nhưng không có dữ liệu phủ 03/2020 hay 2022: 244
- DD >= 80 % hoặc chưa đo: 244
- tháng tệ nhất <= -50 %: 156
- đường growth sụt >= 80 % (cháy): 104
- không rõ mã: 27
- không chắc tài khoản thật: 19
- không có đường growth: 17
- không phải MQL5: 16

## Xếp hạng tín hiệu đạt

| # | ID | Tên | Mã | Tuổi (tháng) | CAGR %/năm | DD % | Sụt growth % | Lưới? | Biến động | Máy chủ |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [1862128](https://www.mql5.com/en/signals/1862128) | EA Happy Gold Eightcap | XAUUSD | 44,6 | 237,91 | 11,70 | 6,69 | không | không áp dụng | EightcapInternational-Real-4 |
| 2 | [2394758](https://www.mql5.com/en/signals/2394758) | Harmonizer High Risk | AUDCAD NZDCAD | 24,8 | 482,14 | 14,93 | 0,00 | không | không áp dụng | Alpari-MT5 |
| 3 | [2378478](https://www.mql5.com/en/signals/2378478) | LazyProV2 AUDCAD | AUDCAD | 45,8 | 48,73 | 7,03 | 0,00 | không | không áp dụng | XMGlobal-Real 22 |
| 4 | [2360068](https://www.mql5.com/en/signals/2360068) | Harmonizer Extreme | AUDCAD NZDCAD | 26,7 | 350,43 | 22,42 | 0,00 | không | không áp dụng | Alpari-MT5 |
| 5 | [2391347](https://www.mql5.com/en/signals/2391347) | Aurum Titan | BTCUSD DOW XAUUSD | 30,1 | 221,59 | 29,34 | 21,57 | không | không áp dụng | KVBPrimeLimited-Real |
| 6 | [2363323](https://www.mql5.com/en/signals/2363323) | UpEverest MT4 | AUDCAD | 34,0 | 95,98 | 15,18 | 0,00 | không | không áp dụng | FPMarketsSC-Live4 |
| 7 | [2231030](https://www.mql5.com/en/signals/2231030) | MSC Gold Stable Pro | XAUUSD | 30,4 | 202,64 | 33,70 | 10,22 | không | không áp dụng | NeotechFinancialServices-Live |
| 8 | [2153920](https://www.mql5.com/en/signals/2153920) | MCA100 | EURUSD GBPUSD XAUUSD | 35,6 | 171,15 | 35,37 | 19,14 | không | không áp dụng | ICMarketsSC-Live09 |
| 9 | [2330430](https://www.mql5.com/en/signals/2330430) | JINNIUFX7 | GBPUSD | 121,0 | 22,67 | 8,31 | 0,57 | không | không áp dụng | BlackwellGlobal2-Live3 |
| 10 | [2343251](https://www.mql5.com/en/signals/2343251) | HJM1 | EURNOK EURUSD XAUUSD | 28,8 | 690,52 | 41,01 | 0,00 | không | không áp dụng | CribMarket-Live |
| 11 | [2342395](https://www.mql5.com/en/signals/2342395) | KUHN | XAUUSD | 38,6 | 199,08 | 48,22 | 32,66 | không | không áp dụng | ECMarkets-Live01 |
| 12 | [2393522](https://www.mql5.com/en/signals/2393522) | Xingli 5108 | ETHUSD XAUUSD | 24,4 | 177,90 | 35,33 | 26,06 | không | không áp dụng | TradeMaxGlobal-Live8 |
| 13 | [2244828](https://www.mql5.com/en/signals/2244828) | Kivenara 815m52ff | NAS100 | 31,3 | 136,55 | 36,81 | 31,98 | không | không áp dụng | Elev8-Real9 |
| 14 | [2265943](https://www.mql5.com/en/signals/2265943) | The Gold Miner | GOLDM | 24,6 | 190,25 | 44,95 | 41,45 | không | không áp dụng | XMGlobal-MT5 12 |
| 15 | [2269966](https://www.mql5.com/en/signals/2269966) | BreakZone Scalper HFM | XAUUSD | 24,4 | 247,23 | 47,16 | 35,87 | không | không áp dụng | HFMarketsGlobal-Live1 |
| 16 | [2378480](https://www.mql5.com/en/signals/2378480) | EansPRO V3 XAUUSD | AUDUSD GOLDMI | 59,8 | 26,61 | 10,25 | 0,00 | không | không áp dụng | XMGlobal-Real 16 |
| 17 | [2351061](https://www.mql5.com/en/signals/2351061) | Gold Minion | XAUUSD | 35,9 | 98,92 | 29,66 | 25,98 | không | không áp dụng | ICMarketsSC-MT5-4 |
| 18 | [2245675](https://www.mql5.com/en/signals/2245675) | OnlyUJ | USDJPY | 27,6 | 119,57 | 35,54 | 23,67 | không | không áp dụng | Exness-MT5Real15 |
| 19 | [2344620](https://www.mql5.com/en/signals/2344620) | Friday Pro | GBPJPY NOKJPY USDJPY | 39,1 | 90,41 | 33,16 | 24,92 | không | không áp dụng | ICMarketsSC-Live05 |
| 20 | [2387289](https://www.mql5.com/en/signals/2387289) | Nasdaq manual | EURUSD NQCASH | 26,4 | 124,75 | 38,27 | 1,16 | không | không áp dụng | ForexClub-MT4 Market Real 2 Server |
| 21 | [2380604](https://www.mql5.com/en/signals/2380604) | MSC Gold Fund Pro | XAUUSD | 40,0 | 12,74 | 4,04 | 3,10 | không | không áp dụng | NeotechFinancialServices-Live |
| 22 | [2172246](https://www.mql5.com/en/signals/2172246) | TwoHundredPercentAnnually | AUDCAD AUDNZD NZDCAD | 45,1 | 65,03 | 28,95 | 1,65 | không | không áp dụng | ICMarketsSC-Live26 |
| 23 | [2196457](https://www.mql5.com/en/signals/2196457) | X117 Taoist nature | GOLD USDCHF | 33,1 | 134,19 | 50,99 | 40,08 | không | không áp dụng | XMGlobal-MT5 2 |
| 24 | [2392805](https://www.mql5.com/en/signals/2392805) | UZUNAMI88 | GBPJPY XAUUSD | 44,9 | 39,57 | 18,35 | 16,84 | không | không áp dụng | MaxrichGroup-Real |
| 25 | [2308093](https://www.mql5.com/en/signals/2308093) | UpFuji MT4 | AUDCAD | 37,3 | 58,54 | 27,15 | 0,68 | không | không áp dụng | RoboForex-Pro-5 |
| 26 | [2242498](https://www.mql5.com/en/signals/2242498) | Goldtrade Pro High Risk | XAUUSD | 27,8 | 150,39 | 60,45 | 56,66 | không | không áp dụng | CapitalPointTrading-MT5-4 |
| 27 | [1725090](https://www.mql5.com/en/signals/1725090) | My Son Trading Account | US500 | 49,0 | 53,88 | 30,29 | 0,11 | không | không áp dụng | ICMarkets-MT5-2 |
| 28 | [2378484](https://www.mql5.com/en/signals/2378484) | LazyPro v23 EURUSD | EURUSD | 44,4 | 77,47 | 41,61 | 4,81 | không | không áp dụng | XMGlobal-Real 5 |
| 29 | [1887017](https://www.mql5.com/en/signals/1887017) | MAPLEROO | AUDCAD | 44,4 | 125,60 | 70,63 | 17,21 | không | không áp dụng | ICMarketsSC-Live23 |
| 30 | [1758568](https://www.mql5.com/en/signals/1758568) | EA Happy Power FM | EURCHF | 60,3 | 81,68 | 55,75 | 11,16 | không | không áp dụng | ForexMart-RealServer |
| 31 | [2049326](https://www.mql5.com/en/signals/2049326) | SFE Impulse | BTCUSD ETHUSD | 38,2 | 50,54 | 27,95 | 24,17 | không | không áp dụng | ICMarketsSC-MT5-4 |
| 32 | [2274644](https://www.mql5.com/en/signals/2274644) | Pinnacle Alpha | AUDCAD AUDNZD NZDCAD | 57,3 | 34,07 | 23,56 | 0,00 | không | không áp dụng | FortunePrimeGlobal-Live |
| 33 | [2330426](https://www.mql5.com/en/signals/2330426) | JINNIUFX3 | GBPUSD XAUUSD | 85,5 | 43,63 | 36,44 | 18,63 | không | không áp dụng | BlackwellGlobal2-Live3 |
| 34 | [2250577](https://www.mql5.com/en/signals/2250577) | Golden System 2 | XAUUSD | 52,2 | 59,25 | 40,17 | 28,96 | không | không áp dụng | ICMarketsSC-Live27 |
| 35 | [2042164](https://www.mql5.com/en/signals/2042164) | PrismaForex | AUDCAD CADCHF EURGBP | 50,6 | 53,27 | 37,61 | 0,39 | không | không áp dụng | RoboMarketsCY-ECN |
| 36 | [2375487](https://www.mql5.com/en/signals/2375487) | Different gold strategies 1 | XAUUSD | 25,8 | 64,39 | 31,69 | 29,16 | không | không áp dụng | ICMarketsSC-MT5-2 |
| 37 | [2378485](https://www.mql5.com/en/signals/2378485) | MetaPro v22 EURUSD | EURUSD | 45,8 | 77,84 | 52,78 | 0,00 | không | không áp dụng | XMGlobal-Real 22 |
| 38 | [2100250](https://www.mql5.com/en/signals/2100250) | Gld Trde Pro | XAUUSD | 36,6 | 117,49 | 71,82 | 50,89 | không | không áp dụng | EightcapInternational-Real-4 |
| 39 | [2234719](https://www.mql5.com/en/signals/2234719) | Navi | BTCUSD | 28,8 | 74,99 | 40,10 | 38,33 | không | không áp dụng | Exness-MT5Real8 |
| 40 | [1566312](https://www.mql5.com/en/signals/1566312) | SteadyRock Growth IFL XAUUSD ICMarkets | XAUUSD | 52,9 | 40,75 | 31,28 | 22,69 | không | không áp dụng | ICMarketsSC-Live32 |
| 41 | [2051827](https://www.mql5.com/en/signals/2051827) | TYLWK | AUDCAD AUDNZD NZDCAD | 40,7 | 91,35 | 64,17 | 0,00 | không | không áp dụng | RadexMarkets-Real 6 |
| 42 | [2051881](https://www.mql5.com/en/signals/2051881) | HPCWK | AUDCAD AUDNZD NZDCAD | 40,0 | 91,34 | 64,12 | 0,00 | không | không áp dụng | RadexMarkets-Real 6 |
| 43 | [2378489](https://www.mql5.com/en/signals/2378489) | EansPRO V3 EURUSD | EURUSD | 46,0 | 48,51 | 37,73 | 0,00 | không | không áp dụng | XMGlobal-Real 22 |
| 44 | [2232206](https://www.mql5.com/en/signals/2232206) | AlgoMind DayTrading | XAUUSD | 32,2 | 72,91 | 47,56 | 39,33 | không | không áp dụng | Headway-Real |
| 45 | [1309107](https://www.mql5.com/en/signals/1309107) | SteadyRock Growth IFL XAUUSD Tickmill | XAUUSD | 58,9 | 53,64 | 48,11 | 42,14 | không | không áp dụng | TickmillUK-Live03 |
| 46 | [2229059](https://www.mql5.com/en/signals/2229059) | Kivenara 8315m01f | NAS100 | 32,4 | 51,71 | 34,62 | 28,74 | không | không áp dụng | Elev8-Real10 |
| 47 | [2023750](https://www.mql5.com/en/signals/2023750) | NoStress MT4 | AUDCAD | 39,1 | 51,75 | 39,40 | 0,00 | không | không áp dụng | CapitalPointTrading-Live05 |
| 48 | [1798961](https://www.mql5.com/en/signals/1798961) | AutoScalping V9C | EURUSD | 49,9 | 65,86 | 61,65 | 0,00 | không | không áp dụng | XMGlobal-Real 36 |
| 49 | [2023752](https://www.mql5.com/en/signals/2023752) | NoStress MT5 | AUDCAD | 39,1 | 50,11 | 41,57 | 0,00 | không | không áp dụng | CapitalPointTrading-MT5 |
| 50 | [1018646](https://www.mql5.com/en/signals/1018646) | RetireNow MT5 | AUDCAD EURUSD | 65,1 | 54,56 | 59,48 | 4,45 | không | không áp dụng | ActivTradesCorp-Server |
| 51 | [1612976](https://www.mql5.com/en/signals/1612976) | XPulse EA | AUDCAD AUDNZD NZDCAD | 51,8 | 57,29 | 56,86 | 8,61 | không | không áp dụng | ICMarketsSC-Live32 |
| 52 | [2261205](https://www.mql5.com/en/signals/2261205) | EA 3 CurrencyPair MediumRisk | AUDCAD AUDNZD NZDCAD | 35,9 | 52,79 | 43,98 | 43,13 | không | không áp dụng | ICMarketsSC-Live23 |
| 53 | [2331134](https://www.mql5.com/en/signals/2331134) | Sputnik SI Auto | ETHUSD EURUSD GBPUSD | 64,9 | 32,53 | 37,20 | 0,00 | không | không áp dụng | ForexClub-MT4 Market Real 2 Server |
| 54 | [2195619](https://www.mql5.com/en/signals/2195619) | The Gold Reaper Live default settings | XAUUSD | 32,9 | 56,15 | 45,64 | 37,29 | không | không áp dụng | PepperstoneUK-Live |
| 55 | [2272380](https://www.mql5.com/en/signals/2272380) | NANO M0NEY CORP from FXGP WMC | AUDCAD EURUSD GBPUSD | 30,1 | 97,55 | 77,95 | 0,00 | không | không áp dụng | Weltrade-Live |
| 56 | [2303521](https://www.mql5.com/en/signals/2303521) | Interstellar | AUDCAD | 53,4 | 49,02 | 53,02 | 49,53 | không | không áp dụng | LiteFinanceVC-Live-05 |
| 57 | [2183815](https://www.mql5.com/en/signals/2183815) | Jaya bersama XM 1 | BTCUSD EURUSD | 33,8 | 82,30 | 79,84 | 0,12 | không | không áp dụng | XMGlobal-Real 8 |
| 58 | [1708760](https://www.mql5.com/en/signals/1708760) | NS lazyPRO 24155959 | AUDUSD EURUSD | 52,2 | 60,03 | 73,67 | 0,00 | không | không áp dụng | XMGlobal-Real 23 |
| 59 | [2320603](https://www.mql5.com/en/signals/2320603) | IC Trading Signla MT5 | AUDCAD AUDNZD NZDCAD | 30,6 | 19,11 | 18,89 | 1,89 | không | không áp dụng | ICMarketsSC-MT5-4 |
| 60 | [2126101](https://www.mql5.com/en/signals/2126101) | TriForce MT5 | AUDCAD AUDUSD EURUSD | 35,2 | 41,53 | 44,62 | 0,67 | không | không áp dụng | CapitalPointTrading-MT5-4 |
| 61 | [1412455](https://www.mql5.com/en/signals/1412455) | NS eP v3 49109488 | AUDUSD EURUSD | 56,6 | 24,14 | 34,77 | 4,01 | không | không áp dụng | XMGlobal-Real 39 |
| 62 | [1750952](https://www.mql5.com/en/signals/1750952) | Cradle by SecureFX Trader | AUDCAD AUDNZD NZDCAD | 53,6 | 21,64 | 31,33 | 0,00 | không | không áp dụng | ICMarketsAU-MT4-Live |
| 63 | [1436120](https://www.mql5.com/en/signals/1436120) | NS eP V3 49120344 | AUDUSD EURUSD NZDCAD | 55,9 | 51,31 | 78,21 | 0,00 | không | không áp dụng | XMGlobal-Real 39 |
| 64 | [1810556](https://www.mql5.com/en/signals/1810556) | NS lazyPRO 66097110 | AUDCAD AUDUSD | 48,5 | 38,67 | 55,35 | 0,00 | không | không áp dụng | HFMarketsSV-Live Server 7 |
| 65 | [854817](https://www.mql5.com/en/signals/854817) | Mars5 | EURUSD GBPUSD PROFIT | 85,3 | 24,46 | 45,53 | 0,00 | không | không áp dụng | Weltrade-Live |
| 66 | [1051498](https://www.mql5.com/en/signals/1051498) | EA HFM FM | AUDUSD EURCHF USDCHF | 64,4 | 39,00 | 52,17 | 0,00 | có (từ khoá trang/phong cách) | sống qua 2022 (+110.8 %) | ForexMart-RealServer |
| 67 | [2000089](https://www.mql5.com/en/signals/2000089) | ForxeShootClassMT5 | EURUSD GBPUSD USDCHF | 41,6 | 42,84 | 59,32 | 34,14 | không | không áp dụng | Swissquote-Server |
| 68 | [1939809](https://www.mql5.com/en/signals/1939809) | C120 JPY_GOLD | USDJPY XAUUSD | 42,1 | 25,65 | 37,18 | 21,29 | không | không áp dụng | ICMarkets-Live20 |
| 69 | [2201396](https://www.mql5.com/en/signals/2201396) | Pullenback Stability Growth | AUDCAD AUDNZD NZDCAD | 49,0 | 35,41 | 57,06 | 0,00 | không | không áp dụng | Exness-Real18 |
| 70 | [2236796](https://www.mql5.com/en/signals/2236796) | UnicornFx GSS 60 | EURUSD | 35,0 | 28,02 | 41,25 | 4,03 | không | không áp dụng | LiteFinanceVC-Live-08 |
| 71 | [2337217](https://www.mql5.com/en/signals/2337217) | Top Cat S | EURUSD | 32,7 | 24,52 | 36,38 | 1,54 | không | không áp dụng | AdmiralsGroup-Live3 |
| 72 | [2193151](https://www.mql5.com/en/signals/2193151) | MinorForce MT5 | AUDCAD AUDNZD NZDCAD | 33,1 | 46,78 | 73,57 | 2,23 | không | không áp dụng | XMGlobal-MT5 10 |
| 73 | [984972](https://www.mql5.com/en/signals/984972) | ManagmentM | EURUSD | 66,9 | 17,18 | 38,50 | 32,27 | không | không áp dụng | RoboMarketsCY-Prime |
| 74 | [2273171](https://www.mql5.com/en/signals/2273171) | EA Happy Algorithm PRO FM | EURUSD USDCHF | 31,7 | 25,18 | 41,61 | 7,57 | không | không áp dụng | ForexMart-RealServer |
| 75 | [1047527](https://www.mql5.com/en/signals/1047527) | Happy MartiGrid EA | AUDUSD | 64,6 | 21,07 | 42,10 | 0,00 | có (từ khoá trang/phong cách) | sống qua 2022 (+50.2 %) | ForexMart-RealServer |
| 76 | [2323713](https://www.mql5.com/en/signals/2323713) | Advanced Scalper Live | EURUSD GBPUSD USDJPY | 80,5 | 12,24 | 38,02 | 31,06 | không | không áp dụng | TickmillUK-Live03 |
| 77 | [2198360](https://www.mql5.com/en/signals/2198360) | XXX OIL | BRENTE CLECN UKOILE | 52,9 | 24,22 | 66,98 | 46,61 | không | không áp dụng | PurpleTrading-03Live |
| 78 | [2135908](https://www.mql5.com/en/signals/2135908) | GBP Daily Trade V1 | EURGBP GBPUSD | 35,4 | 11,81 | 26,62 | 23,75 | không | không áp dụng | XM.COM-MT5 |
| 79 | [2354516](https://www.mql5.com/en/signals/2354516) | Sydney MT5 | GBPUSD USDJPY | 39,3 | 25,77 | 63,92 | 58,53 | không | không áp dụng | ICMarketsSC-MT5-4 |
| 80 | [2270515](https://www.mql5.com/en/signals/2270515) | MC RB | AUDCAD AUDNZD NZDCAD | 42,3 | 22,05 | 68,79 | 0,00 | không | không áp dụng | RoboForex-ECN |
| 81 | [2227935](https://www.mql5.com/en/signals/2227935) | JM | AUDCAD AUDNZD NZDCAD | 42,3 | 14,46 | 52,56 | 49,51 | không | không áp dụng | ICMarketsSC-MT5-4 |
| 82 | [2103795](https://www.mql5.com/en/signals/2103795) | Bitcoin Scalp Pro | BTCUSD | 36,6 | 16,73 | 71,38 | 56,56 | không | không áp dụng | ICMarketsSC-MT5-4 |
| 83 | [2356275](https://www.mql5.com/en/signals/2356275) | LANCER | COFFEE KCZ6CFD USDJPY | 30,1 | 10,90 | 42,90 | 35,66 | không | không áp dụng | ICMarketsSC-Live08 |

## EA trên MQL5 Market của tác giả (top 30, quét 03/11/2026 bằng curl công khai)

| ID tín hiệu | Tên | Tác giả | EA Market | Free Demo | Giá USD | Nền tảng |
|---|---|---|---|---|---|---|
| 1862128 | EA Happy Gold Eightcap | happyforex | không thấy | — | — | — |
| 2394758 | Harmonizer High Risk | mnimoos | [Night Swimmer / Free Download Trading Robot (Expert Advisor)](https://www.mql5.com/en/market/product/108979) | không thấy | 0.00 | MT5 |
| 2394758 | Harmonizer High Risk | mnimoos | [Night Swimmer MT4 / Free Download Trading Robot (Expert Advi](https://www.mql5.com/en/market/product/113684) | không thấy | 0.00 | MT4 |
| 2394758 | Harmonizer High Risk | mnimoos | [Harmonizer EA MT5 / Buy Trading Robot (Expert Advisor) for M](https://www.mql5.com/en/market/product/96759) | có | 870.00 | MT5 |
| 2394758 | Harmonizer High Risk | mnimoos | [Harmonizer EA / Buy Trading Robot (Expert Advisor) for MetaT](https://www.mql5.com/en/market/product/98560) | có | 870.00 | MT4 |
| 2378478 | LazyProV2 AUDCAD | 38177933 | không thấy | — | — | — |
| 2360068 | Harmonizer Extreme | mnimoos | [Night Swimmer / Free Download Trading Robot (Expert Advisor)](https://www.mql5.com/en/market/product/108979) | không thấy | 0.00 | MT5 |
| 2360068 | Harmonizer Extreme | mnimoos | [Night Swimmer MT4 / Free Download Trading Robot (Expert Advi](https://www.mql5.com/en/market/product/113684) | không thấy | 0.00 | MT4 |
| 2360068 | Harmonizer Extreme | mnimoos | [Harmonizer EA MT5 / Buy Trading Robot (Expert Advisor) for M](https://www.mql5.com/en/market/product/96759) | có | 870.00 | MT5 |
| 2360068 | Harmonizer Extreme | mnimoos | [Harmonizer EA / Buy Trading Robot (Expert Advisor) for MetaT](https://www.mql5.com/en/market/product/98560) | có | 870.00 | MT4 |
| 2391347 | Aurum Titan | serenao | không thấy | — | — | — |
| 2363323 | UpEverest MT4 | tec_daniel | [ToTheMoon MT5 / Buy Trading Robot (Expert Advisor) for MetaT](https://www.mql5.com/en/market/product/97962) | có | 600.00 | MT5 |
| 2363323 | UpEverest MT4 | tec_daniel | [ToTheMoon MT4 / Buy Trading Robot (Expert Advisor) for MetaT](https://www.mql5.com/en/market/product/97963) | có | 600.00 | MT4 |
| 2231030 | MSC Gold Stable Pro | datbh | [MSC SuperGold Pro EA / Buy Trading Robot (Expert Advisor) fo](https://www.mql5.com/en/market/product/204099) | có | 1099.00 | MT5 |
| 2231030 | MSC Gold Stable Pro | datbh | [MSC Line EA / Buy Trading Robot (Expert Advisor) for MetaTra](https://www.mql5.com/en/market/product/93601) | có | 299.00 | MT4 |
| 2231030 | MSC Gold Stable Pro | datbh | [MSC Line EA MT5 / Buy Trading Robot (Expert Advisor) for Met](https://www.mql5.com/en/market/product/93979) | có | 390.00 | MT5 |
| 2231030 | MSC Gold Stable Pro | datbh | [MSC ProMax EA MT5 / Buy Trading Robot (Expert Advisor) for M](https://www.mql5.com/en/market/product/94028) | có | 499.00 | MT5 |
| 2231030 | MSC Gold Stable Pro | datbh | [MSC ProMax EA / Buy Trading Robot (Expert Advisor) for MetaT](https://www.mql5.com/en/market/product/94064) | có | 499.00 | MT4 |
| 2153920 | MCA100 | liehtw | không thấy | — | — | — |
| 2330430 | JINNIUFX7 | wangfuchao | không thấy | — | — | — |
| 2343251 | HJM1 | traderswayyyyyn22 | không thấy | — | — | — |
| 2342395 | KUHN | jcw2018 | [Smart Trend and Range EA / Buy Trading Robot (Expert Advisor](https://www.mql5.com/en/market/product/153994) | có | 120.00 | MT4 |
| 2342395 | KUHN | jcw2018 | [Gold Terminator EA / Buy Trading Robot (Expert Advisor) for ](https://www.mql5.com/en/market/product/154080) | có | 120.00 | MT4 |
| 2342395 | KUHN | jcw2018 | [Poseidon X4 / Buy Trading Robot (Expert Advisor) for MetaTra](https://www.mql5.com/en/market/product/154108) | có | 120.00 | MT4 |
| 2342395 | KUHN | jcw2018 | [Ares Hunter / Buy Trading Robot (Expert Advisor) for MetaTra](https://www.mql5.com/en/market/product/154343) | có | 120.00 | MT4 |
| 2342395 | KUHN | jcw2018 | [Valkyrie Gold / Buy Trading Robot (Expert Advisor) for MetaT](https://www.mql5.com/en/market/product/154646) | có | 120.00 | MT4 |
| 2342395 | KUHN | jcw2018 | [Zeus Hedge AI / Buy Trading Robot (Expert Advisor) for MetaT](https://www.mql5.com/en/market/product/154802) | có | 120.00 | MT4 |
| 2342395 | KUHN | jcw2018 | [Ares Quantum / Buy Trading Robot (Expert Advisor) for MetaTr](https://www.mql5.com/en/market/product/154808) | có | 120.00 | MT4 |
| 2342395 | KUHN | jcw2018 | [Thunder Breaker / Buy Trading Robot (Expert Advisor) for Met](https://www.mql5.com/en/market/product/155279) | có | 120.00 | MT4 |
| 2342395 | KUHN | jcw2018 | [Neural Hedge AI / Buy Trading Robot (Expert Advisor) for Met](https://www.mql5.com/en/market/product/155793) | có | 120.00 | MT4 |
| 2342395 | KUHN | jcw2018 | [Vector AI / Buy Trading Robot (Expert Advisor) for MetaTrade](https://www.mql5.com/en/market/product/155977) | có | 200.00 | MT4 |
| 2342395 | KUHN | jcw2018 | [Gold Overlord / Buy Trading Robot (Expert Advisor) for MetaT](https://www.mql5.com/en/market/product/158160) | có | 200.00 | MT4 |
| 2393522 | Xingli 5108 | z0922638424 | không thấy | — | — | — |
| 2244828 | Kivenara 815m52ff | jurnaltrading | không thấy | — | — | — |
| 2265943 | The Gold Miner | lucaslucci | không thấy | — | — | — |
| 2269966 | BreakZone Scalper HFM | tomosie | [Candle Strike / Buy Trading Robot (Expert Advisor) for MetaT](https://www.mql5.com/en/market/product/118108) | có | 50.00 | MT4 |
| 2269966 | BreakZone Scalper HFM | tomosie | [InfinityPro / Buy Trading Robot (Expert Advisor) for MetaTra](https://www.mql5.com/en/market/product/119470) | có | 30.00 | MT4 |
| 2269966 | BreakZone Scalper HFM | tomosie | [Dark Eagle MT4 / Buy Trading Robot (Expert Advisor) for Meta](https://www.mql5.com/en/market/product/121472) | có | 30.00 | MT4 |
| 2269966 | BreakZone Scalper HFM | tomosie | [Angel Eyes / Free Download Trading Robot (Expert Advisor) fo](https://www.mql5.com/en/market/product/122948) | không thấy | 0.00 | MT4 |
| 2269966 | BreakZone Scalper HFM | tomosie | [Neuro Edge / Free Download Trading Robot (Expert Advisor) fo](https://www.mql5.com/en/market/product/154414) | không thấy | 0.00 | MT5 |
| 2269966 | BreakZone Scalper HFM | tomosie | [Zone Breakout / Buy Trading Robot (Expert Advisor) for MetaT](https://www.mql5.com/en/market/product/163777) | có | 455.00 | MT5 |
| 2269966 | BreakZone Scalper HFM | tomosie | [Gold Nexus Prime / Buy Trading Robot (Expert Advisor) for Me](https://www.mql5.com/en/market/product/180323) | có | 75.00 | MT5 |
| 2269966 | BreakZone Scalper HFM | tomosie | [Gold Dominion / Buy Trading Robot (Expert Advisor) for MetaT](https://www.mql5.com/en/market/product/181267) | có | 75.00 | MT5 |
| 2269966 | BreakZone Scalper HFM | tomosie | [GoldSession / Buy Trading Robot (Expert Advisor) for MetaTra](https://www.mql5.com/en/market/product/193341) | có | 150.00 | MT4 |
| 2269966 | BreakZone Scalper HFM | tomosie | [Zone Breakout Limited / Free Download Trading Robot (Expert ](https://www.mql5.com/en/market/product/202470) | không thấy | 0.00 | MT5 |
| 2269966 | BreakZone Scalper HFM | tomosie | [EA Mata Elang Pro / Buy Trading Robot (Expert Advisor) for M](https://www.mql5.com/en/market/product/49608) | có | 50.00 | MT4 |
| 2269966 | BreakZone Scalper HFM | tomosie | [EA AutoGreen / Buy Trading Robot (Expert Advisor) for MetaTr](https://www.mql5.com/en/market/product/68514) | có | 50.00 | MT4 |
| 2269966 | BreakZone Scalper HFM | tomosie | [ScalperGhost / Free Download Trading Robot (Expert Advisor) ](https://www.mql5.com/en/market/product/78275) | không thấy | 0.00 | MT4 |
| 2269966 | BreakZone Scalper HFM | tomosie | [ScalperGhost Pro / Buy Trading Robot (Expert Advisor) for Me](https://www.mql5.com/en/market/product/79675) | có | 55.00 | MT4 |
| 2269966 | BreakZone Scalper HFM | tomosie | [Super MataELang Pro / Buy Trading Robot (Expert Advisor) for](https://www.mql5.com/en/market/product/87076) | có | 50.00 | MT4 |
| 2269966 | BreakZone Scalper HFM | tomosie | [Super MataELang Limited / Free Download Trading Robot (Exper](https://www.mql5.com/en/market/product/87200) | không thấy | 0.00 | MT4 |
| 2378480 | EansPRO V3 XAUUSD | 38177933 | không thấy | — | — | — |
| 2351061 | Gold Minion | riyo | không thấy | — | — | — |
| 2245675 | OnlyUJ | jamesnguyen230215 | [OnlyTime / Buy Trading Robot (Expert Advisor) for MetaTrader](https://www.mql5.com/en/market/product/156366) | có | 1000.00 | MT5 |
| 2344620 | Friday Pro | mingtrader | [Universal Tradebot MT5 / Buy Trading Robot (Expert Advisor) ](https://www.mql5.com/en/market/product/101424) | có | 199.00 | MT5 |
| 2344620 | Friday Pro | mingtrader | [Universal Tradebot MT4 / Buy Trading Robot (Expert Advisor) ](https://www.mql5.com/en/market/product/101425) | có | 199.00 | MT4 |
| 2344620 | Friday Pro | mingtrader | [Friday Pro / Buy Trading Robot (Expert Advisor) for MetaTrad](https://www.mql5.com/en/market/product/102817) | có | 399.00 | MT4 |
| 2344620 | Friday Pro | mingtrader | [Friday Pro MT5 / Buy Trading Robot (Expert Advisor) for Meta](https://www.mql5.com/en/market/product/102893) | có | 399.00 | MT5 |
| 2344620 | Friday Pro | mingtrader | [AI Momentum Scalper MT5 / Buy Trading Robot (Expert Advisor)](https://www.mql5.com/en/market/product/111154) | có | 699.00 | MT5 |
| 2344620 | Friday Pro | mingtrader | [MA Momentum Scalper / Buy Trading Robot (Expert Advisor) for](https://www.mql5.com/en/market/product/135576) | có | 499.00 | MT5 |
| 2344620 | Friday Pro | mingtrader | [RSI Momentum Scalper / Buy Trading Robot (Expert Advisor) fo](https://www.mql5.com/en/market/product/138801) | có | 199.00 | MT5 |
| 2344620 | Friday Pro | mingtrader | [Extreme Reversion Trader / Buy Trading Robot (Expert Advisor](https://www.mql5.com/en/market/product/149373) | có | 499.00 | MT5 |
| 2344620 | Friday Pro | mingtrader | [Trade Strike / Buy Trading Robot (Expert Advisor) for MetaTr](https://www.mql5.com/en/market/product/152688) | có | 399.00 | MT5 |
| 2344620 | Friday Pro | mingtrader | [GridIron / Buy Trading Robot (Expert Advisor) for MetaTrader](https://www.mql5.com/en/market/product/181969) | có | 299.00 | MT5 |
| 2344620 | Friday Pro | mingtrader | [MingTraderAUDCAD for MT4 / Buy Trading Robot (Expert Advisor](https://www.mql5.com/en/market/product/73946) | có | 299.00 | MT4 |
| 2344620 | Friday Pro | mingtrader | [MingTraderAUDCAD for MT5 / Buy Trading Robot (Expert Advisor](https://www.mql5.com/en/market/product/73947) | có | 299.00 | MT5 |
| 2387289 | Nasdaq manual | rubicon2016 | không thấy | — | — | — |
| 2380604 | MSC Gold Fund Pro | datbh | [MSC SuperGold Pro EA / Buy Trading Robot (Expert Advisor) fo](https://www.mql5.com/en/market/product/204099) | có | 1099.00 | MT5 |
| 2380604 | MSC Gold Fund Pro | datbh | [MSC Line EA / Buy Trading Robot (Expert Advisor) for MetaTra](https://www.mql5.com/en/market/product/93601) | có | 299.00 | MT4 |
| 2380604 | MSC Gold Fund Pro | datbh | [MSC Line EA MT5 / Buy Trading Robot (Expert Advisor) for Met](https://www.mql5.com/en/market/product/93979) | có | 390.00 | MT5 |
| 2380604 | MSC Gold Fund Pro | datbh | [MSC ProMax EA MT5 / Buy Trading Robot (Expert Advisor) for M](https://www.mql5.com/en/market/product/94028) | có | 499.00 | MT5 |
| 2380604 | MSC Gold Fund Pro | datbh | [MSC ProMax EA / Buy Trading Robot (Expert Advisor) for MetaT](https://www.mql5.com/en/market/product/94064) | có | 499.00 | MT4 |
| 2172246 | TwoHundredPercentAnnually | vladenka | không thấy | — | — | — |
| 2196457 | X117 Taoist nature | easonleung | không thấy | — | — | — |
| 2392805 | UZUNAMI88 | uzunami88 | không thấy | — | — | — |
| 2308093 | UpFuji MT4 | tec_daniel | [ToTheMoon MT5 / Buy Trading Robot (Expert Advisor) for MetaT](https://www.mql5.com/en/market/product/97962) | có | 600.00 | MT5 |
| 2308093 | UpFuji MT4 | tec_daniel | [ToTheMoon MT4 / Buy Trading Robot (Expert Advisor) for MetaT](https://www.mql5.com/en/market/product/97963) | có | 600.00 | MT4 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Luna AI PRO / Buy Trading Robot (Expert Advisor) for MetaTra](https://www.mql5.com/en/market/product/101970) | có | 399.00 | MT4 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Luna AI Pro MT5 / Buy Trading Robot (Expert Advisor) for Met](https://www.mql5.com/en/market/product/101974) | có | 399.00 | MT5 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Gold Trade Pro MT5 / Buy Trading Robot (Expert Advisor) for ](https://www.mql5.com/en/market/product/102737) | có | 649.00 | MT5 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Gold Trade Pro / Buy Trading Robot (Expert Advisor) for Meta](https://www.mql5.com/en/market/product/102746) | có | 649.00 | MT4 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Stability Pro MT4 / Buy Trading Robot (Expert Advisor) for M](https://www.mql5.com/en/market/product/105029) | có | 499.00 | MT4 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Stability Pro MT5 / Buy Trading Robot (Expert Advisor) for M](https://www.mql5.com/en/market/product/105030) | có | 499.00 | MT5 |
| 2242498 | Goldtrade Pro High Risk | strueli | [The Gold Reaper MT5 / Buy Trading Robot (Expert Advisor) for](https://www.mql5.com/en/market/product/111357) | có | 949.00 | MT5 |
| 2242498 | Goldtrade Pro High Risk | strueli | [The Gold Reaper MT4 / Buy Trading Robot (Expert Advisor) for](https://www.mql5.com/en/market/product/111467) | có | 949.00 | MT4 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Indicement MT5 / Buy Trading Robot (Expert Advisor) for Meta](https://www.mql5.com/en/market/product/122529) | có | 549.00 | MT5 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Indicement MT4 / Buy Trading Robot (Expert Advisor) for Meta](https://www.mql5.com/en/market/product/122651) | có | 549.00 | MT4 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Goldbot One MT5 / Buy Trading Robot (Expert Advisor) for Met](https://www.mql5.com/en/market/product/127379) | có | 649.00 | MT5 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Goldbot One MT4 / Buy Trading Robot (Expert Advisor) for Met](https://www.mql5.com/en/market/product/127380) | có | 649.00 | MT4 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Ultimate Breakout System / Buy Trading Robot (Expert Advisor](https://www.mql5.com/en/market/product/133653) | có | 1699.00 | MT5 |
| 2242498 | Goldtrade Pro High Risk | strueli | [The Bitcoin Reaper / Buy Trading Robot (Expert Advisor) for ](https://www.mql5.com/en/market/product/142178) | có | 549.00 | MT5 |
| 2242498 | Goldtrade Pro High Risk | strueli | [The ORB Master / Buy Trading Robot (Expert Advisor) for Meta](https://www.mql5.com/en/market/product/150079) | có | 499.00 | MT5 |
| 2242498 | Goldtrade Pro High Risk | strueli | [The Gold Phantom / Buy Trading Robot (Expert Advisor) for Me](https://www.mql5.com/en/market/product/161561) | có | 649.00 | MT5 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Advanced Scalper / Buy Trading Robot (Expert Advisor) for Me](https://www.mql5.com/en/market/product/24254) | có | 549.00 | MT4 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Advanced Scalper MT5 / Buy Trading Robot (Expert Advisor) fo](https://www.mql5.com/en/market/product/31243) | có | 599.00 | MT5 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Gecko / Buy Trading Robot (Expert Advisor) for MetaTrader 4](https://www.mql5.com/en/market/product/49052) | có | 149.00 | MT4 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Gecko EA MT5 / Buy Trading Robot (Expert Advisor) for MetaTr](https://www.mql5.com/en/market/product/68347) | có | 149.00 | MT5 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Bitcoin Scalp Pro / Buy Trading Robot (Expert Advisor) for M](https://www.mql5.com/en/market/product/87947) | có | 399.00 | MT4 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Bitcoin Scalp Pro MT5 / Buy Trading Robot (Expert Advisor) f](https://www.mql5.com/en/market/product/87972) | có | 399.00 | MT5 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Apex Trader MT5 / Buy Trading Robot (Expert Advisor) for Met](https://www.mql5.com/en/market/product/92659) | có | 499.00 | MT5 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Apex Trader MT4 / Buy Trading Robot (Expert Advisor) for Met](https://www.mql5.com/en/market/product/92662) | có | 499.00 | MT4 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Daytrade Pro Algo / Buy Trading Robot (Expert Advisor) for M](https://www.mql5.com/en/market/product/97854) | có | 599.00 | MT4 |
| 2242498 | Goldtrade Pro High Risk | strueli | [Daytrade Pro Algo MT5 / Buy Trading Robot (Expert Advisor) f](https://www.mql5.com/en/market/product/97855) | có | 599.00 | MT5 |
| 1725090 | My Son Trading Account | tkhg | không thấy | — | — | — |
| 2378484 | LazyPro v23 EURUSD | 38177933 | không thấy | — | — | — |
| 1887017 | MAPLEROO | rfsoftware | [Shogun RX / Buy Trading Robot (Expert Advisor) for MetaTrade](https://www.mql5.com/en/market/product/94000) | có | 99.00 | MT4 |
| 1887017 | MAPLEROO | rfsoftware | [Barbarian / Buy Trading Robot (Expert Advisor) for MetaTrade](https://www.mql5.com/en/market/product/94100) | có | 99.00 | MT4 |
| 1887017 | MAPLEROO | rfsoftware | [Dark Knight RX / Buy Trading Robot (Expert Advisor) for Meta](https://www.mql5.com/en/market/product/94244) | có | 129.99 | MT4 |
| 1887017 | MAPLEROO | rfsoftware | [Mapleroo / Buy Trading Robot (Expert Advisor) for MetaTrader](https://www.mql5.com/en/market/product/95630) | có | 99.00 | MT4 |
| 1758568 | EA Happy Power FM | happyforex | không thấy | — | — | — |

Ghi chú 03/11/2026 (bản lọc lại): chỉ giữ sản phẩm có tiêu đề MQL5 "Trading Robot (Expert Advisor)" và tên không phải công cụ (tool/manager/copier/panel/utility/indicator/library…). Tác giả EA Happy Gold (happyforex): trang seller công khai chỉ hiện 3 sản phẩm miễn phí đều là tiện ích → không có EA giao dịch đọc được từ box; sản phẩm trả phí (nếu có) nạp bằng JS — CHƯA ĐO ĐƯỢC. 12/30 tác giả có EA giao dịch, 10/30 có EA MT5 kèm Free Demo; 33 sản phẩm demo MT5 đã xếp hàng.
