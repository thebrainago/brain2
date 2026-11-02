# Nguồn công khai ĐẠT — lịch sử xác minh công khai

Đo lúc 2026-11-03 00:53 (giờ Việt Nam, UTC+7). Sinh bởi `python3 -m seeker.cong_khai.chay`.

**Tiêu chí ĐẠT duy nhất:** max DD < 80% VÀ CAGR > 10%/năm. Không có tiêu chí nào khác.

- CAGR = (1 + tăng trưởng)^(12 / tuổi tháng) − 1. MQL5: tăng trưởng (Growth) **bỏ qua nạp/rút**, tuổi = số tuần lịch sử (Weeks).
- DD MQL5 = max(DD tương đối theo số dư, theo vốn).
- Thật/demo MQL5 suy từ tên máy chủ (có 'Demo'/'Contest' → demo).
- **Điểm xếp hạng chỉ để sắp thứ tự** giữa các tín hiệu đã ĐẠT (tuổi 40%, tài khoản thật 25%, DD thấp 20%, CAGR chặn trần 200% 15%). Không phải cổng.
- Tuổi ngắn (< 12 tháng) cho CAGR phóng đại; đây là lịch sử công khai, chưa phải kiểm chứng dữ liệu dài nhiều năm.
- **Thiên lệch sống sót:** danh sách mặc định của MQL5 (`/en/signals/mt5/list`, `/mt4/list`) chỉ hiện tín hiệu thật xếp hạng cao, nên tỉ lệ ĐẠT trên mẫu này KHÔNG đại diện cho toàn bộ tín hiệu. Tín hiệu đã cháy/ẩn không có trong mẫu.

## Số lượng quét

| Nền tảng | Kết quả |
|---|---|
| MQL5 | id_tim_thay=292, doc_duoc=292, khong_doc=0 |
| Myfxbook | doc_duoc=0, khong_doc=1 |
| LiteFinance | doc_duoc=16, khong_doc=0, chi_tiet_khong_cong_khai=3 |
| Exness | doc_duoc=0, khong_doc=1 |

Trạng thái: MQL5: {'DAT': 292}; LiteFinance: {'CHUA_DO': 16}

## Tín hiệu ĐẠT (292), sắp theo điểm xếp hạng

| # | Tên | Nền tảng | Link | CAGR %/năm | Max DD % | Tuổi (tháng) | Thật/demo | Tăng trưởng % | Số lệnh | Symbol | Kiểu (từ trong trang) | Lệnh cuối | Điểm xếp hạng |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | EA Happy News Eightcap | MQL5 | [1864588](https://www.mql5.com/en/signals/1864588) | 249.18 | 9.14 | 44.39 | that | 10105.66 | 1688 | GBPUSD.i USDJPY.i EURUSD.i AUDUSD.i | — | 6 days ago | 87.31 |
| 2 | Deux ex machina | MQL5 | [2271402](https://www.mql5.com/en/signals/2271402) | 114.70 | 25.99 | 65.78 | that | 6492.03 | 1914 | AUDCAD AUDNZD NZDCAD US30 XAUUSD DE40 EU | — | 4 hours ago | 87.11 |
| 3 | NoPain MT5 | MQL5 | [2262642](https://www.mql5.com/en/signals/2262642) | 86.97 | 20.63 | 60.03 | that | 2188.59 | 5917 | AUDCAD | — | 4 hours ago | 86.37 |
| 4 | ATong | MQL5 | [2327790](https://www.mql5.com/en/signals/2327790) | 136.35 | 38.55 | 66.47 | that | 11627.12 | 8342 | GBPUSD AUDUSD GBPAUD EURUSD USDCAD AUDCA | — | 5 hours ago | 85.59 |
| 5 | TP TRADER | MQL5 | [1932739](https://www.mql5.com/en/signals/1932739) | 63.55 | 19.06 | 82.56 | that | 2850.77 | 14751 | EURUSD XAUUSD GBPUSD USDJPY AUDUSD EURJP | — | 9 hours ago | 85.0 |
| 6 | JINNIUFX7 | MQL5 | [2330430](https://www.mql5.com/en/signals/2330430) | 22.67 | 8.31 | 120.97 | that | 684.52 | 12592 | GBPUSD | — | 10 hours ago | 84.62 |
| 7 | EansPRO V3 XAUUSD | MQL5 | [2378480](https://www.mql5.com/en/signals/2378480) | 26.61 | 10.25 | 59.80 | that | 224.12 | 1226 | GOLDmicro AUDUSDmicro | — | 3 hours ago | 84.3 |
| 8 | RFactor Portfolio JM | MQL5 | [743742](https://www.mql5.com/en/signals/743742) | 52.81 | 20.09 | 78.19 | that | 1484.51 | 10202 | GBPUSD EURUSD EURAUD EURCAD USDCAD EURGB | grid | 19 hours ago | 83.94 |
| 9 | SCR EURAUD | MQL5 | [2358336](https://www.mql5.com/en/signals/2358336) | 21.29 | 12.21 | 93.37 | that | 349.09 | 1843 | EURAUD AUDCAD EURUSD AUDJPY GER30Cash US | — | 4 days ago | 83.54 |
| 10 | ICTrading Signal 2 | MQL5 | [926651](https://www.mql5.com/en/signals/926651) | 21.53 | 18.91 | 109.93 | that | 496.62 | 5650 | NZDCAD AUDCAD NZDCHF AUDCHF USDCAD AUDUS | — | 5 days ago | 81.89 |
| 11 | Scalp IC Markets ECN | MQL5 | [683917](https://www.mql5.com/en/signals/683917) | 85.68 | 38.42 | 86.47 | that | 8542.65 | 2689 | GBPCAD EURAUD EURSGD EURCAD GBPUSD CHFJP | martingale | 4 days ago | 81.82 |
| 12 | NightVisionEA ICM | MQL5 | [731021](https://www.mql5.com/en/signals/731021) | 24.55 | 20.80 | 81.41 | that | 343.34 | 8214 | USDJPY EURCHF USDCHF GBPUSD EURCAD EURGB | — | 12 hours ago | 81.64 |
| 13 | Anson Account 3 | MQL5 | [2382360](https://www.mql5.com/en/signals/2382360) | 55.51 | 30.98 | 67.85 | that | 1113.85 | 1171 | EURUSD.s USDJPY.s | grid, martingale | 18 hours ago | 81.42 |
| 14 | Commodity Accumulation Plan | MQL5 | [2270674](https://www.mql5.com/en/signals/2270674) | 17.53 | 19.56 | 116.83 | that | 381.74 | 8512 | WHEAT PLATINUM COPPER COTTON#2 CrudeOIL  | — | 2 hours ago | 81.42 |
| 15 | SFE Portfolio1 | MQL5 | [138420](https://www.mql5.com/en/signals/138420) | 31.60 | 24.33 | 132.01 | that | 1951.55 | 3344 | LNKUSD BTCUSD ETHUSD EURUSD UNIUSD XAUUS | — | 3 days ago | 81.29 |
| 16 | FX Fun | MQL5 | [2355082](https://www.mql5.com/en/signals/2355082) | 63.86 | 14.57 | 52.44 | that | 765.57 | 6761 | AUDCADf NZDCADf AUDNZDf XAUUSDf | — | 7 hours ago | 81.11 |
| 17 | TT ic 001 | MQL5 | [1270954](https://www.mql5.com/en/signals/1270954) | 30.32 | 22.36 | 59.11 | that | 268.59 | 8012 | AUDCAD NZDCAD EURUSD EURGBP AUDNZD USDCA | — | 7 hours ago | 81.09 |
| 18 | Trade | MQL5 | [2204034](https://www.mql5.com/en/signals/2204034) | 135.59 | 57.48 | 60.03 | that | 7172.98 | 2679 | XAUUSD GBPUSD EURUSD BTCUSD AUDNZD NZDCA | — | 4 days ago | 80.8 |
| 19 | RAZOR EA | MQL5 | [2300694](https://www.mql5.com/en/signals/2300694) | 125.48 | 22.09 | 47.15 | that | 2340.33 | 1947 | NZDCAD AUDCAD AUDNZD XAGUSD XAUUSD EURUS | grid | 4 hours ago | 80.32 |
| 20 | Scalp IC Markets MT5 | MQL5 | [1560883](https://www.mql5.com/en/signals/1560883) | 55.76 | 32.86 | 58.88 | that | 779.61 | 2611 | GBPCAD GBPAUD EURSGD EURAUD GBPUSD EURCA | martingale | 4 days ago | 80.22 |
| 21 | Relax EA | MQL5 | [884935](https://www.mql5.com/en/signals/884935) | 45.90 | 33.30 | 71.76 | that | 857.22 | 2084 | CADJPY EURCAD EURCHF USDCAD GBPUSD EURGB | — | 18 hours ago | 80.12 |
| 22 | R Factor Broker FPMarkets | MQL5 | [973927](https://www.mql5.com/en/signals/973927) | 24.01 | 26.94 | 67.62 | that | 236.17 | 6225 | AUDCAD.r EURCAD.r EURUSD.r USDCAD.r EURA | — | 5 days ago | 80.07 |
| 23 | MySingalStart 3 | MQL5 | [1760039](https://www.mql5.com/en/signals/1760039) | 21.96 | 26.42 | 112.23 | that | 540.05 | 12326 | NZDCAD USDCAD NZDCHF AUDUSD AUDCAD AUDNZ | — | 4 hours ago | 80.04 |
| 24 | R Factor Mean Reversal | MQL5 | [734515](https://www.mql5.com/en/signals/734515) | 69.23 | 40.66 | 81.18 | that | 3413.40 | 34600 | GBPUSD EURGBP EURUSD EURAUD GBPAUD EURCA | — | 2 hours ago | 80.03 |
| 25 | MySingalStart 2 | MQL5 | [840474](https://www.mql5.com/en/signals/840474) | 30.49 | 29.47 | 80.03 | that | 489.88 | 9285 | NZDCAD AUDCAD AUDNZD NZDCHF AUDCHF SUMMA | — | 6 hours ago | 79.92 |
| 26 | Pinnacle Alpha | MQL5 | [2274644](https://www.mql5.com/en/signals/2274644) | 34.07 | 23.56 | 57.27 | that | 305.17 | 3156 | AUDCAD-E NZDCAD-E AUDNZD-E | — | 3 days ago | 79.85 |
| 27 | JINNIUFX3 | MQL5 | [2330426](https://www.mql5.com/en/signals/2330426) | 43.63 | 36.44 | 85.55 | that | 1221.51 | 1447 | XAUUSD GBPUSD | — | 3 days ago | 79.16 |
| 28 | Multi EA combo | MQL5 | [2376950](https://www.mql5.com/en/signals/2376950) | 36.60 | 35.48 | 62.33 | that | 405.32 | 12835 | NZDCADq AUDCADq EURUSDq USDJPYq GBPAUDq  | — | 7 hours ago | 78.88 |
| 29 | WolvesVN EU | MQL5 | [2385213](https://www.mql5.com/en/signals/2385213) | 20.79 | 30.87 | 73.36 | that | 217.26 | 2372 | EURUSD.fx AUDCAD.fx USDCAD.fx GBPUSD.fx  | — | 2 hours ago | 78.84 |
| 30 | Trading Hero 20k | MQL5 | [544163](https://www.mql5.com/en/signals/544163) | 27.39 | 33.82 | 93.60 | that | 560.74 | 18451 | NZDCAD AUDCAD AUDUSD GBPUSD AUDNZD EURUS | — | 4 hours ago | 78.6 |
| 31 | Trading Hero 10k Conservative | MQL5 | [1042318](https://www.mql5.com/en/signals/1042318) | 19.21 | 31.91 | 81.87 | that | 231.70 | 10603 | AUDUSD NZDCAD AUDCAD AUDNZD GBPUSD GBPCA | — | 6 hours ago | 78.46 |
| 32 | Sputnik SI Auto | MQL5 | [2331134](https://www.mql5.com/en/signals/2331134) | 32.53 | 37.20 | 64.86 | that | 358.31 | 9882 | EURUSD ETHUSD GBPUSD | — | 9 hours ago | 78.14 |
| 33 | Disco FIBO Pamm | MQL5 | [2077624](https://www.mql5.com/en/signals/2077624) | 48.69 | 41.61 | 59.57 | that | 616.54 | 2896 | XAUUSD.I GBPCAD.I GBPAUD.I EURAUD.I GBPU | — | 4 hours ago | 77.96 |
| 34 | Tharos II | MQL5 | [1059619](https://www.mql5.com/en/signals/1059619) | 61.52 | 46.67 | 65.09 | that | 1247.43 | 5725 | NZDCAD AUDCAD AUDNZD NZDUSD AUDUSD USDCA | — | 3 days ago | 77.95 |
| 35 | Calm Waters Signal | MQL5 | [2339857](https://www.mql5.com/en/signals/2339857) | 32.81 | 38.05 | 76.12 | that | 504.84 | 6664 | AUDNZD NZDCAD AUDCAD GBPUSD EURCAD EURAU | grid, martingale, dca | 4 hours ago | 77.95 |
| 36 | MySingalStart 4 | MQL5 | [1671156](https://www.mql5.com/en/signals/1671156) | 26.49 | 37.14 | 70.38 | that | 296.88 | 7062 | NZDCAD AUDCAD AUDNZD AUDUSD NZDUSD SUMMA | grid | 4 days ago | 77.7 |
| 37 | Sputnik2019 | MQL5 | [1922647](https://www.mql5.com/en/signals/1922647) | 50.64 | 45.24 | 87.62 | that | 1891.54 | 15730 | EURUSD XAUUSD USDJPY USDCAD | — | 9 hours ago | 77.49 |
| 38 | Niguru GBP | MQL5 | [1887334](https://www.mql5.com/en/signals/1887334) | 349.99 | 47.95 | 44.16 | that | 25239.70 | 2294 | GBPUSD XAUUSD | dca | 2 hours ago | 77.45 |
| 39 | LazyProV2 AUDCAD | MQL5 | [2378478](https://www.mql5.com/en/signals/2378478) | 48.73 | 7.03 | 45.77 | that | 354.50 | 985 | AUDCADmicro | — | 4 hours ago | 77.41 |
| 40 | OLD SCHOOL | MQL5 | [762818](https://www.mql5.com/en/signals/762818) | 15.94 | 35.66 | 77.27 | that | 159.13 | 2963 | USDJPY BTCUSD XAUUSD EURUSD GBPUSD USTEC | — | 4 hours ago | 77.28 |
| 41 | Crypto Trading Pepper | MQL5 | [1521998](https://www.mql5.com/en/signals/1521998) | 100.70 | 46.97 | 54.05 | that | 2205.11 | 2111 | BTCUSD ETHUSD GBPUSD XAUUSD AUDNZD NZDCA | — | 9 hours ago | 76.84 |
| 42 | SteadyRock Growth IFL XAUUSD Tickmill | MQL5 | [1309107](https://www.mql5.com/en/signals/1309107) | 53.64 | 48.11 | 58.88 | that | 722.52 | 2643 | XAUUSD | — | 3 hours ago | 76.25 |
| 43 | Dudu Whale | MQL5 | [2351032](https://www.mql5.com/en/signals/2351032) | 34.45 | 19.31 | 50.14 | that | 244.53 | 1922 | XAUUSD USDJPY GBPJPY XAUJPY GBPCAD EURJP | — | 4 hours ago | 76.18 |
| 44 | Gold Reaper Goldtrade Pro Daytrade Pro | MQL5 | [2204998](https://www.mql5.com/en/signals/2204998) | 75.00 | 32.59 | 50.14 | that | 936.39 | 8366 | XAUUSD USTEC US500 US30 BTCUSD GBPAUD EU | — | 2 hours ago | 75.9 |
| 45 | SteadyRock Growth IFL XAUUSD ICMarkets | MQL5 | [1566312](https://www.mql5.com/en/signals/1566312) | 40.75 | 31.28 | 52.90 | that | 351.30 | 2336 | XAUUSD | — | 3 hours ago | 75.5 |
| 46 | QImpulse_ValuT | MQL5 | [1857208](https://www.mql5.com/en/signals/1857208) | 39.17 | 22.39 | 48.99 | that | 285.45 | 1316 | XAUUSD USDJPY EURUSD GBPUSD AUDUSD USDCA | grid, martingale | 5 days ago | 75.0 |
| 47 | MonkeyKing | MQL5 | [1498254](https://www.mql5.com/en/signals/1498254) | 79.67 | 49.56 | 54.28 | that | 1316.04 | 2114 | EURUSD AUDCAD AUDUSD NZDCAD AUDNZD GBPCA | — | 3 days ago | 74.77 |
| 48 | NightVision Expert Advisor MT5 | MQL5 | [956328](https://www.mql5.com/en/signals/956328) | 23.14 | 48.38 | 71.53 | that | 245.84 | 7288 | USDJPY EURCHF USDCHF EURCAD GBPUSD EURGB | — | 14 hours ago | 74.64 |
| 49 | Fish n Grid | MQL5 | [1590997](https://www.mql5.com/en/signals/1590997) | 42.82 | 34.87 | 52.21 | that | 371.46 | 5642 | EURJPY GBPUSD NZDCAD AUDCAD AUDCHF EURCA | grid | 43 minutes ago | 74.3 |
| 50 | Golden System 2 | MQL5 | [2250577](https://www.mql5.com/en/signals/2250577) | 59.25 | 40.17 | 52.21 | that | 657.24 | 456 | XAUUSD | — | 3 days ago | 74.21 |
| 51 | My Son Trading Account | MQL5 | [1725090](https://www.mql5.com/en/signals/1725090) | 53.88 | 30.29 | 48.99 | that | 481.00 | 1720 | US500 | — | 2 hours ago | 74.13 |
| 52 | Stable growth pro | MQL5 | [1737977](https://www.mql5.com/en/signals/1737977) | 34.42 | 29.42 | 49.91 | that | 242.22 | 9423 | AUDCAD NZDCAD AUDNZD USDJPY GBPAUD EURAU | — | 7 hours ago | 73.5 |
| 53 | Steady Yeti | MQL5 | [2294298](https://www.mql5.com/en/signals/2294298) | 35.16 | 40.81 | 54.05 | that | 288.50 | 2950 | AUDCAD.p NZDCAD.p AUDNZD.p EURCAD.p EURA | — | 5 days ago | 73.47 |
| 54 | PrismaForex | MQL5 | [2042164](https://www.mql5.com/en/signals/2042164) | 53.27 | 37.61 | 50.60 | that | 505.42 | 2203 | AUDCAD EURGBP CADCHF | — | 4 hours ago | 73.33 |
| 55 | UZUNAMI88 | MQL5 | [2392805](https://www.mql5.com/en/signals/2392805) | 39.57 | 18.35 | 44.85 | that | 247.68 | 623 | XAUUSD GBPJPY | — | 3 hours ago | 73.28 |
| 56 | DKT007 | MQL5 | [2362458](https://www.mql5.com/en/signals/2362458) | 29.64 | 35.99 | 52.44 | that | 210.94 | 2361 | BTCUSD ETHUSD GBPUSD JP225 GBPJPY XAUUSD | — | 9 hours ago | 73.19 |
| 57 | MSC Gold Invest Pro | MQL5 | [1988269](https://www.mql5.com/en/signals/1988269) | 99.75 | 26.23 | 40.71 | that | 945.69 | 1791 | XAUUSD AUDCAD | grid | 2 minutes ago | 73.06 |
| 58 | Harmonizer High Risk | MQL5 | [2394758](https://www.mql5.com/en/signals/2394758) | 482.14 | 14.93 | 24.84 | that | 3733.62 | 1150 | AUDCAD NZDCAD | — | 9 hours ago | 72.83 |
| 59 | MCA100 | MQL5 | [2153920](https://www.mql5.com/en/signals/2153920) | 171.15 | 35.37 | 35.65 | that | 1836.36 | 432 | XAUUSD EURUSD GBPUSD | — | 3 days ago | 72.76 |
| 60 | TwoHundredPercentAnnually | MQL5 | [2172246](https://www.mql5.com/en/signals/2172246) | 65.03 | 28.95 | 45.08 | that | 556.63 | 3260 | NZDCAD AUDCAD AUDNZD | — | 4 days ago | 72.69 |
| 61 | BAS 2 11 | MQL5 | [2325779](https://www.mql5.com/en/signals/2325779) | 116.54 | 21.37 | 36.34 | that | 937.81 | 19665 | S1U6 SVZ5 SVM6 S1H6 SVH6 CRZ4 CRM4 SVU6  | — | 47 minutes ago | 72.62 |
| 62 | Smart trading | MQL5 | [2329267](https://www.mql5.com/en/signals/2329267) | 168.92 | 30.74 | 33.58 | that | 1493.00 | 2627 | EURUSD AUDUSD XAUUSD GBPCHF NZDUSD AUDNZ | — | 3 hours ago | 72.37 |
| 63 | Tick Multiprod | MQL5 | [2222743](https://www.mql5.com/en/signals/2222743) | 262.93 | 37.02 | 32.43 | that | 3157.88 | 5927 | XAUUSD US30 USTEC BTCUSD XAUEUR EURUSD D | martingale | 2 hours ago | 72.36 |
| 64 | Harmonizer Extreme | MQL5 | [2360068](https://www.mql5.com/en/signals/2360068) | 350.43 | 22.42 | 26.68 | that | 2739.46 | 1268 | AUDCAD NZDCAD | — | 9 hours ago | 72.18 |
| 65 | MSC Gold Stable Pro | MQL5 | [2231030](https://www.mql5.com/en/signals/2231030) | 202.64 | 33.70 | 30.36 | that | 1547.23 | 1192 | XAUUSD | — | 6 days ago | 71.82 |
| 66 | UpEverest MT4 | MQL5 | [2363323](https://www.mql5.com/en/signals/2363323) | 95.98 | 15.18 | 34.04 | that | 574.36 | 1607 | AUDCAD | — | 4 hours ago | 71.1 |
| 67 | GenX Multistrategies | MQL5 | [1719023](https://www.mql5.com/en/signals/1719023) | 66.60 | 50.41 | 49.22 | that | 711.49 | 5028 | USDJPY AUDCAD BTCUSD EURUSD ETHUSD EURGB | martingale | 2 hours ago | 70.21 |
| 68 | LazyPro v23 EURUSD | MQL5 | [2378484](https://www.mql5.com/en/signals/2378484) | 77.47 | 41.61 | 44.39 | that | 734.83 | 1613 | EURUSDmicro | — | 9 hours ago | 70.0 |
| 69 | EansPRO V3 EURUSD | MQL5 | [2378489](https://www.mql5.com/en/signals/2378489) | 48.51 | 37.73 | 46.00 | that | 355.42 | 1531 | EURUSDmicro | — | 44 minutes ago | 69.87 |
| 70 | SEA South East EA | MQL5 | [1496203](https://www.mql5.com/en/signals/1496203) | 17.90 | 53.87 | 55.43 | that | 113.94 | 2548 | EURUSD AUDCAD USDCAD USDCHF GBPUSD AUDUS | grid, martingale | 4 hours ago | 69.83 |
| 71 | Golden Swai | MQL5 | [2389881](https://www.mql5.com/en/signals/2389881) | 518.68 | 19.87 | 21.85 | that | 2661.40 | 996 | XAUUSD | — | 1 hour ago | 69.6 |
| 72 | Friday Pro | MQL5 | [2344620](https://www.mql5.com/en/signals/2344620) | 90.41 | 33.16 | 39.10 | that | 715.24 | 320 | GBPJPY USDJPY NOKJPY | — | 16 hours ago | 69.56 |
| 73 | Lenochkin | MQL5 | [2367841](https://www.mql5.com/en/signals/2367841) | 197.24 | 18.78 | 21.62 | that | 611.85 | 497 | EURUSD AUDCAD GBPUSD | — | 4 hours ago | 69.51 |
| 74 | Tem9 2 | MQL5 | [1905285](https://www.mql5.com/en/signals/1905285) | 42.23 | 46.69 | 49.45 | that | 327.03 | 14440 | EURUSD GBPUSD USDJPY XAUUSD EURJPY USDCH | — | 42 minutes ago | 69.46 |
| 75 | QImpulse_FPT | MQL5 | [2393631](https://www.mql5.com/en/signals/2393631) | 53.93 | 36.13 | 44.16 | that | 389.10 | 700 | XAUUSD USDJPY EURUSD GBPUSD USDCHF USDCA | — | 4 days ago | 69.45 |
| 76 | Goldtrade Pro ICM | MQL5 | [2084890](https://www.mql5.com/en/signals/2084890) | 102.36 | 31.95 | 37.03 | that | 780.33 | 792 | XAUUSD | grid, martingale | 12 hours ago | 69.38 |
| 77 | Rbb robo 4 | MQL5 | [2298455](https://www.mql5.com/en/signals/2298455) | 91.52 | 44.37 | 42.32 | that | 889.13 | 1684 | AUDCAD | grid, martingale | 4 hours ago | 68.98 |
| 78 | Gold Minion | MQL5 | [2351061](https://www.mql5.com/en/signals/2351061) | 98.92 | 29.66 | 35.88 | that | 681.74 | 766 | XAUUSD | — | 12 hours ago | 68.92 |
| 79 | HJM1 | MQL5 | [2343251](https://www.mql5.com/en/signals/2343251) | 690.52 | 41.01 | 28.75 | that | 14066.29 | 22838 | XAUUSDc EURNOKc EURUSDc | hedge | 6 hours ago | 68.91 |
| 80 | Soma PureGold Indexes and Oil | MQL5 | [2268766](https://www.mql5.com/en/signals/2268766) | 219.08 | 28.60 | 23.92 | that | 910.26 | 7224 | USTEC XAUUSD BTCUSD US30 US500 DE40 XTIU | — | 39 minutes ago | 68.8 |
| 81 | HAN INVEST SISTEM | MQL5 | [2393802](https://www.mql5.com/en/signals/2393802) | 212.98 | 13.91 | 18.40 | that | 475.16 | 179 | GBPUSD EURUSD EURAUD EURCAD AUDUSD USDCA | hedge | 13 days ago | 68.79 |
| 82 | SolarFlare | MQL5 | [2332166](https://www.mql5.com/en/signals/2332166) | 207.51 | 13.46 | 17.94 | that | 436.24 | 741 | XAUUSD GBPUSD BTCUSD | — | 3 days ago | 68.59 |
| 83 | ORDER FLOW System | MQL5 | [2348377](https://www.mql5.com/en/signals/2348377) | 178.99 | 9.96 | 18.86 | that | 401.54 | 803 | GBPUSD EURUSD USDJPY GBPAUD EURJPY XAUUS | martingale, dca | 5 days ago | 68.51 |
| 84 | MetaPro v22 EURUSD | MQL5 | [2378485](https://www.mql5.com/en/signals/2378485) | 77.84 | 52.78 | 45.77 | that | 798.69 | 729 | EURUSDmicro | — | 2 hours ago | 68.16 |
| 85 | FXtrading | MQL5 | [2356441](https://www.mql5.com/en/signals/2356441) | 535.08 | 14.09 | 17.48 | that | 1377.26 | 395 | NZDCAD USDCAD GBPUSD AUDUSD XAUUSD NZDUS | hedge | 8 hours ago | 68.13 |
| 86 | Fx Swing | MQL5 | [2384807](https://www.mql5.com/en/signals/2384807) | 143.82 | 35.50 | 31.74 | that | 956.27 | 10433 | EURUSD-P GBPUSD-P GBPCAD-P GBPCHF-P NZDU | — | 6 hours ago | 68.07 |
| 87 | KaKa 2 | MQL5 | [2379008](https://www.mql5.com/en/signals/2379008) | 71.55 | 23.26 | 35.19 | that | 386.79 | 706 | GBPUSD USDCAD EURNZD NZDUSD AUDUSD EURAU | — | 17 hours ago | 68.01 |
| 88 | GoldBot1 | MQL5 | [2282234](https://www.mql5.com/en/signals/2282234) | 212.62 | 27.79 | 21.62 | that | 679.59 | 442 | XAUUSD | — | 3 days ago | 67.47 |
| 89 | EUR Trader | MQL5 | [2367606](https://www.mql5.com/en/signals/2367606) | 690.04 | 21.73 | 19.32 | that | 2687.49 | 295 | EURUSD.a XAUUSD.a GBPUSD.a AUDUSD.a BTCU | — | 3 days ago | 67.45 |
| 90 | UpFuji MT4 | MQL5 | [2308093](https://www.mql5.com/en/signals/2308093) | 58.54 | 27.15 | 37.26 | that | 318.27 | 1732 | AUDCAD | — | 4 hours ago | 67.44 |
| 91 | Mon Scalper MT5 | MQL5 | [2361936](https://www.mql5.com/en/signals/2361936) | 284.13 | 28.71 | 21.85 | that | 1059.39 | 566 | XAUUSD | — | 4 hours ago | 67.39 |
| 92 | SFE Impulse | MQL5 | [2049326](https://www.mql5.com/en/signals/2049326) | 50.54 | 27.95 | 38.18 | that | 267.47 | 971 | ETHUSD BTCUSD | — | 11 hours ago | 67.26 |
| 93 | GoldWave signal | MQL5 | [2339082](https://www.mql5.com/en/signals/2339082) | 361.87 | 17.52 | 17.25 | that | 802.08 | 309 | XAUUSD CHINA50 | grid, martingale, dca | 4 days ago | 67.12 |
| 94 | GOLD BR | MQL5 | [2320903](https://www.mql5.com/en/signals/2320903) | 351.47 | 23.14 | 19.09 | that | 1000.02 | 201 | XAUUSD USDJPY | — | 3 days ago | 66.94 |
| 95 | Kivenara 815m52ff | MQL5 | [2244828](https://www.mql5.com/en/signals/2244828) | 136.55 | 36.81 | 31.28 | that | 843.42 | 616 | NAS100 | — | 2 hours ago | 66.89 |
| 96 | EA Happy Bitcoin M30 VM | MQL5 | [2317138](https://www.mql5.com/en/signals/2317138) | 557.14 | 16.41 | 16.33 | that | 1196.27 | 372 | BTCUSD | — | 4 hours ago | 66.78 |
| 97 | NebulaEA | MQL5 | [2332163](https://www.mql5.com/en/signals/2332163) | 181.87 | 8.54 | 15.41 | that | 278.39 | 977 | GBPUSD XAUUSD | — | 3 days ago | 66.78 |
| 98 | Signalium | MQL5 | [2385151](https://www.mql5.com/en/signals/2385151) | 339.01 | 31.07 | 21.16 | that | 1258.00 | 382 | GBPUSD_o EURUSD_o XAUUSD_o | — | 7 days ago | 66.34 |
| 99 | Gold Spike | MQL5 | [2349227](https://www.mql5.com/en/signals/2349227) | 297.50 | 8.56 | 11.96 | that | 295.68 | 434 | XAUUSD | — | 3 days ago | 65.83 |
| 100 | BIGFISH ENT | MQL5 | [2312950](https://www.mql5.com/en/signals/2312950) | 234.86 | 25.75 | 18.17 | that | 523.36 | 627 | AUDCAD GBPUSD EURUSD XAUUSD | — | 7 hours ago | 65.68 |
| 101 | EA Safe 1 | MQL5 | [1927666](https://www.mql5.com/en/signals/1927666) | 39.43 | 44.11 | 42.78 | that | 227.10 | 12446 | EURUSD GBPUSD USDJPY XAUUSD AUDNZD GBPAU | — | 4 hours ago | 65.45 |
| 102 | Multi currency Trade | MQL5 | [2317676](https://www.mql5.com/en/signals/2317676) | 37.85 | 43.97 | 42.78 | that | 214.07 | 9860 | EURJPY AUDUSD USDJPY NZDUSD EURUSD | — | 4 hours ago | 65.37 |
| 103 | Gold Trend X Signal | MQL5 | [2362085](https://www.mql5.com/en/signals/2362085) | 146.44 | 34.29 | 26.91 | that | 655.78 | 1083 | XAUUSD | grid, martingale | 4 hours ago | 65.35 |
| 104 | Techno Long Term | MQL5 | [2307342](https://www.mql5.com/en/signals/2307342) | 168.83 | 38.63 | 25.76 | that | 735.49 | 4824 | XAUUSD US30 USTEC BTCUSD US500 | grid, martingale, dca | 1 hour ago | 65.18 |
| 105 | Kenni Trades Gold Breakout | MQL5 | [2306053](https://www.mql5.com/en/signals/2306053) | 1085.11 | 27.88 | 18.17 | that | 4125.21 | 903 | XAUUSD NASUSD | grid, martingale, hedge | 3 days ago | 65.14 |
| 106 | NoStress MT4 | MQL5 | [2023750](https://www.mql5.com/en/signals/2023750) | 51.75 | 39.40 | 39.10 | that | 289.17 | 2371 | AUDCAD | — | 4 hours ago | 65.1 |
| 107 | VSA | MQL5 | [2393860](https://www.mql5.com/en/signals/2393860) | 1109.89 | 12.17 | 12.19 | that | 1158.60 | 158 | GBPUSD NZDUSD AUDUSD USDCAD EURUSD XAUUS | hedge | 3 days ago | 65.08 |
| 108 | DCA Large Cap Stocks | MQL5 | [2236750](https://www.mql5.com/en/signals/2236750) | 34.85 | 33.15 | 38.41 | that | 160.37 | 1717 | NVDA TSLA META WFC AAPL GOOGL AMZN RIO G | dca | 2 hours ago | 64.93 |
| 109 | Nobu Trap | MQL5 | [2319444](https://www.mql5.com/en/signals/2319444) | 270.23 | 22.96 | 15.87 | that | 464.69 | 711 | XAUUSD XAUJPY USDJPY GBPJPY EURJPY | grid, martingale | 4 hours ago | 64.84 |
| 110 | Gold Reaper New V2 2 | MQL5 | [2265877](https://www.mql5.com/en/signals/2265877) | 106.91 | 16.89 | 23.92 | that | 326.06 | 905 | XAUUSD | — | 7 days ago | 64.74 |
| 111 | GOLD HUAT EA | MQL5 | [2376856](https://www.mql5.com/en/signals/2376856) | 63.38 | 44.19 | 38.87 | that | 390.43 | 723 | XAUUSD USDJPY NAS100 GER40 US30 EURUSD A | grid, martingale, dca | 2 hours ago | 64.62 |
| 112 | GrattMarMic | MQL5 | [2393538](https://www.mql5.com/en/signals/2393538) | 169.55 | 12.56 | 14.95 | that | 243.96 | 3156 | EURUSD EURCHF CADCHF EURNZD XTIUSD USDSG | grid | 2 hours ago | 64.54 |
| 113 | EA18 | MQL5 | [2299080](https://www.mql5.com/en/signals/2299080) | 216.81 | 36.48 | 20.47 | that | 614.96 | 426 | NAS100 | — | 3 minutes ago | 64.53 |
| 114 | QuantumStar | MQL5 | [2332164](https://www.mql5.com/en/signals/2332164) | 130.58 | 9.08 | 17.94 | that | 248.68 | 755 | XAUUSD GBPUSD USDJPY | — | 3 days ago | 64.48 |
| 115 | BreakZone Scalper HFM | MQL5 | [2269966](https://www.mql5.com/en/signals/2269966) | 247.23 | 47.16 | 24.38 | that | 1154.13 | 448 | XAUUSDb | — | 3 days ago | 64.46 |
| 116 | Dudu 001 MT5 | MQL5 | [2361784](https://www.mql5.com/en/signals/2361784) | 90.67 | 24.81 | 28.29 | that | 357.89 | 1740 | XAUUSD USDJPY GBPJPY XAUJPY EURJPY | — | 4 hours ago | 64.46 |
| 117 | The Gold Miner | MQL5 | [2265943](https://www.mql5.com/en/signals/2265943) | 190.25 | 44.95 | 24.61 | that | 789.36 | 1203 | GOLDm# | — | 3 hours ago | 64.44 |
| 118 | NoStress MT5 | MQL5 | [2023752](https://www.mql5.com/en/signals/2023752) | 50.11 | 41.57 | 39.10 | that | 275.66 | 2362 | AUDCAD | — | 4 hours ago | 64.43 |
| 119 | BTC ICMarkets 50 high risk | MQL5 | [2225567](https://www.mql5.com/en/signals/2225567) | 122.76 | 48.65 | 33.58 | that | 840.52 | 1504 | BTCUSD XAUUSD GBPUSD EURUSD GBPCAD USDJP | grid, martingale | 10 minutes ago | 64.43 |
| 120 | X117 Taoist nature | MQL5 | [2196457](https://www.mql5.com/en/signals/2196457) | 134.19 | 50.99 | 33.12 | that | 947.17 | 1584 | GOLD# USDCHF# | — | 3 days ago | 64.4 |
| 121 | GB Trading | MQL5 | [2386818](https://www.mql5.com/en/signals/2386818) | 176.13 | 20.91 | 17.02 | that | 322.32 | 1495 | XAUUSD EURUSD USDJPY US30 BTCUSD AUDUSD  | — | 3 hours ago | 64.33 |
| 122 | Expert EURUSD Sys02 | MQL5 | [2181186](https://www.mql5.com/en/signals/2181186) | 90.45 | 40.08 | 33.81 | that | 514.13 | 1908 | EURUSD XAUUSD XTIUSD | martingale, hedge | 10 hours ago | 64.3 |
| 123 | Aether | MQL5 | [2324198](https://www.mql5.com/en/signals/2324198) | 344.28 | 23.93 | 15.18 | that | 559.61 | 1555 | XAUUSD.vip NZDCAD.vip EURUSD.vip AUDCAD. | — | 2 hours ago | 64.14 |
| 124 | Meaw | MQL5 | [2393078](https://www.mql5.com/en/signals/2393078) | 58.30 | 27.51 | 32.20 | that | 243.00 | 1503 | XAUUSD+ USOUSD XAGUSD UKOUSD EURUSD+ VIX | — | 3 hours ago | 63.96 |
| 125 | Expert EURUSD Sys01 | MQL5 | [2142461](https://www.mql5.com/en/signals/2142461) | 84.36 | 43.91 | 35.19 | that | 501.31 | 1977 | EURUSDp XAUUSDp BRENT | martingale, hedge | 10 hours ago | 63.81 |
| 126 | XAU Super Safe Mode Fusion 50501 | MQL5 | [2321576](https://www.mql5.com/en/signals/2321576) | 138.79 | 22.20 | 20.70 | that | 348.81 | 276 | XAUUSD | grid, martingale, dca | 5 days ago | 63.66 |
| 127 | Gold Important Sniper Level MT4 | MQL5 | [2290292](https://www.mql5.com/en/signals/2290292) | 128.31 | 26.64 | 23.46 | that | 402.25 | 218 | XAUUSD Gold | — | 5 days ago | 63.6 |
| 128 | Meridian Extreme Risk Mode | MQL5 | [2385675](https://www.mql5.com/en/signals/2385675) | 406.10 | 10.45 | 9.20 | that | 246.67 | 413 | AUDCAD | — | 6 hours ago | 63.52 |
| 129 | OnlyUJ | MQL5 | [2245675](https://www.mql5.com/en/signals/2245675) | 119.57 | 35.54 | 27.60 | that | 510.40 | 745 | USDJPY | — | 34 minutes ago | 63.48 |
| 130 | Hari Ke 7 | MQL5 | [2371938](https://www.mql5.com/en/signals/2371938) | 174.81 | 15.38 | 13.80 | that | 219.80 | 367 | AUDNZDr AUDCADr NZDCADr | martingale, dca | 5 days ago | 63.47 |
| 131 | Ekalaya | MQL5 | [2364632](https://www.mql5.com/en/signals/2364632) | 190.29 | 34.75 | 19.32 | that | 456.10 | 889 | GBPUSD_i EURUSD_i | — | 8 hours ago | 63.46 |
| 132 | Precise Pair Trading Pro | MQL5 | [2329290](https://www.mql5.com/en/signals/2329290) | 404.51 | 23.84 | 14.03 | that | 563.39 | 948 | EURUSD XAUUSD XAUEUR AUDUSD | grid, martingale | 18 hours ago | 63.39 |
| 133 | Eightcap 491 | MQL5 | [2294461](https://www.mql5.com/en/signals/2294461) | 209.23 | 42.88 | 21.16 | that | 632.04 | 423 | XAUUSD NDX100 | — | 3 days ago | 63.39 |
| 134 | GUNS FX V2 | MQL5 | [2376393](https://www.mql5.com/en/signals/2376393) | 1986.05 | 11.63 | 9.43 | that | 988.35 | 294 | XAUUSD | — | 3 days ago | 63.38 |
| 135 | Asterysc Hunter 3 | MQL5 | [2288774](https://www.mql5.com/en/signals/2288774) | 66.68 | 42.91 | 36.11 | that | 365.22 | 6611 | AUDCAD.. EURUSD.. GBPUSD.. UT100 XAUUSD. | — | 44 minutes ago | 63.35 |
| 136 | Kefren Portfolio 1 | MQL5 | [2369741](https://www.mql5.com/en/signals/2369741) | 265.20 | 18.55 | 11.96 | that | 263.63 | 2780 | XAUUSD+ BTCUSD DJ30 NAS100 GER40 USDJPY+ | — | 8 hours ago | 63.34 |
| 137 | AI Aurum Pivot LIVE | MQL5 | [2361796](https://www.mql5.com/en/signals/2361796) | 233.22 | 12.61 | 9.66 | that | 163.51 | 110 | XAUUSD | — | 3 days ago | 63.29 |
| 138 | Guns FX | MQL5 | [2362532](https://www.mql5.com/en/signals/2362532) | 263.51 | 12.29 | 9.43 | that | 175.72 | 309 | XAUUSD EURUSD GBPUSD | — | 3 days ago | 63.21 |
| 139 | Solnce | MQL5 | [2288975](https://www.mql5.com/en/signals/2288975) | 81.89 | 13.09 | 23.00 | that | 214.76 | 1145 | XAUUSD GBPUSD USDJPY EURUSD | — | 3 days ago | 63.2 |
| 140 | Myfx Multiprod | MQL5 | [2343740](https://www.mql5.com/en/signals/2343740) | 398.02 | 27.24 | 14.49 | that | 594.91 | 1283 | XAUUSD | — | 2 hours ago | 62.85 |
| 141 | Multi EA Trading | MQL5 | [2375343](https://www.mql5.com/en/signals/2375343) | 1350.12 | 33.14 | 16.10 | that | 3515.91 | 589 | XAUUSD GBPUSD EURUSD USDCAD AUDJPY NZDCA | — | 3 days ago | 62.45 |
| 142 | Nasdaq manual | MQL5 | [2387289](https://www.mql5.com/en/signals/2387289) | 124.75 | 38.27 | 26.45 | that | 495.94 | 3580 | EURUSD NQCash | — | 3 days ago | 62.42 |
| 143 | FXKINGPIN | MQL5 | [2386148](https://www.mql5.com/en/signals/2386148) | 752.08 | 22.32 | 11.96 | that | 746.02 | 493 | BTCUSDm XAUUSDm | — | 4 hours ago | 62.39 |
| 144 | MSC SuperGold Pro | MQL5 | [2304847](https://www.mql5.com/en/signals/2304847) | 1354.69 | 53.03 | 23.46 | that | 18659.17 | 3054 | XAUUSD.f AUDCAD.f | dca | 3 days ago | 62.38 |
| 145 | P820 Climb high and look far | MQL5 | [2204755](https://www.mql5.com/en/signals/2204755) | 86.73 | 43.62 | 32.66 | that | 447.25 | 1871 | GBPUSD USDJPY XAUUSD BTCUSD USDCHF EURUS | — | 3 days ago | 62.37 |
| 146 | Captain Snail Gold | MQL5 | [2201409](https://www.mql5.com/en/signals/2201409) | 309.62 | 33.45 | 16.10 | that | 563.16 | 601 | XAUUSD | grid | 12 hours ago | 62.37 |
| 147 | Long Gold 1102 | MQL5 | [2366314](https://www.mql5.com/en/signals/2366314) | 259.29 | 25.53 | 12.88 | that | 294.62 | 986 | XAUUSD GBPUSD BTCUSD USOIL UKOIL ETHUSD  | — | 4 hours ago | 62.2 |
| 148 | Range Breakout EA Live | MQL5 | [2271995](https://www.mql5.com/en/signals/2271995) | 112.79 | 28.29 | 23.46 | that | 337.67 | 2089 | USDJPY US30 DE40 BTCUSD XAUUSD | grid, martingale | 1 hour ago | 62.03 |
| 149 | Lunar Express Mission 11M | MQL5 | [2332746](https://www.mql5.com/en/signals/2332746) | 423.54 | 29.02 | 13.80 | that | 571.11 | 4092 | XAUUSD AUDCAD GBPCAD AUDUSD AUDJPY EURUS | — | 18 hours ago | 61.95 |
| 150 | Fast Turtle | MQL5 | [2344859](https://www.mql5.com/en/signals/2344859) | 317.85 | 22.42 | 11.27 | that | 283.04 | 2010 | GOLDm# GBPUSDm# AUDCADm# AUDNZDm# EURUSD | — | 3 days ago | 61.91 |
| 151 | EA 3 CurrencyPair MediumRisk | MQL5 | [2261205](https://www.mql5.com/en/signals/2261205) | 52.79 | 43.98 | 35.88 | that | 255.18 | 1303 | NZDCAD AUDNZD AUDCAD | — | 4 days ago | 61.88 |
| 152 | Kivenara 8315m01f | MQL5 | [2229059](https://www.mql5.com/en/signals/2229059) | 51.71 | 34.62 | 32.43 | that | 208.45 | 659 | NAS100 | — | 1 hour ago | 61.84 |
| 153 | Combo Profile 2026 | MQL5 | [2362349](https://www.mql5.com/en/signals/2362349) | 1346.94 | 19.34 | 9.89 | that | 804.49 | 861 | GBPUSD+ USDCHF+ USDCAD+ AUDUSD+ GBPAUD+  | — | 12 hours ago | 61.76 |
| 154 | Mohammed Qandeel | MQL5 | [2359368](https://www.mql5.com/en/signals/2359368) | 60.80 | 34.49 | 31.05 | that | 241.81 | 2894 | WTICASH US100CASH GER30CASH US30CASH STO | — | 3 hours ago | 61.64 |
| 155 | Hunting Cat Scalper Set C | MQL5 | [2231094](https://www.mql5.com/en/signals/2231094) | 65.00 | 30.92 | 29.21 | that | 238.39 | 1123 | USDJPY | grid | 4 days ago | 61.62 |
| 156 | World PEACE Multi FX Algo | MQL5 | [2379208](https://www.mql5.com/en/signals/2379208) | 973.81 | 47.44 | 20.01 | that | 5136.84 | 4500 | AUDCADr AUDNZDr GBPUSDr EURJPYr EURUSDr  | grid, hedge | 48 minutes ago | 61.48 |
| 157 | Xauusd H1 | MQL5 | [2376983](https://www.mql5.com/en/signals/2376983) | 131.85 | 32.60 | 22.08 | that | 369.87 | 1029 | XAUUSD US30 BTCUSD | — | 3 days ago | 61.46 |
| 158 | XAUUSD AI trade | MQL5 | [2337663](https://www.mql5.com/en/signals/2337663) | 717.85 | 31.67 | 14.03 | that | 1066.99 | 2966 | XAUUSD GBPUSD AUDUSD BTCUSD USDCAD EURAU | — | 4 hours ago | 61.44 |
| 159 | Eldorium Risk 5 | MQL5 | [2371082](https://www.mql5.com/en/signals/2371082) | 655.60 | 20.34 | 9.66 | that | 409.36 | 278 | XAUUSD | martingale | 3 days ago | 61.36 |
| 160 | Nano Sentinel | MQL5 | [2388152](https://www.mql5.com/en/signals/2388152) | 456.13 | 19.62 | 9.20 | that | 272.65 | 443 | XAUUSD | — | 4 days ago | 61.23 |
| 161 | Giaphat GOLD Vantage | MQL5 | [2372538](https://www.mql5.com/en/signals/2372538) | 395.51 | 19.31 | 8.97 | that | 230.79 | 1291 | XAUUSD+ EURUSD+ AUDCAD+ NZDCAD+ AUDNZD+  | — | 1 hour ago | 61.15 |
| 162 | Algoverse Portfolio | MQL5 | [2377503](https://www.mql5.com/en/signals/2377503) | 875.61 | 25.46 | 11.27 | that | 749.37 | 1405 | XAUUSD GBPUSD EURUSD NZDCAD USDJPY USDCH | martingale | 4 hours ago | 61.15 |
| 163 | Foxsov Sniper Pro | MQL5 | [2329641](https://www.mql5.com/en/signals/2329641) | 300.15 | 33.84 | 14.26 | that | 419.57 | 821 | XAUUSD+ BTCUSD NAS100.r DJ30.r | — | 4 days ago | 61.05 |
| 164 | IVOMAS | MQL5 | [2320008](https://www.mql5.com/en/signals/2320008) | 300.69 | 38.61 | 15.87 | that | 526.92 | 818 | XAUUSD EURUSD NZDJPY AUDUSD GBPUSD NZDUS | martingale | 4 hours ago | 60.93 |
| 165 | IC 026 | MQL5 | [2342068](https://www.mql5.com/en/signals/2342068) | 327.12 | 28.32 | 11.96 | that | 325.06 | 1768 | EURUSD GBPUSD AUDCAD AUDNZD XAUUSD NZDCA | — | 14 hours ago | 60.89 |
| 166 | MegaGold | MQL5 | [2337490](https://www.mql5.com/en/signals/2337490) | 153.79 | 30.70 | 17.94 | that | 302.43 | 364 | XAUUSD | grid, martingale | 2 hours ago | 60.82 |
| 167 | A18F52N | MQL5 | [2357382](https://www.mql5.com/en/signals/2357382) | 298.06 | 23.09 | 9.89 | that | 212.22 | 205 | NAS100 | — | 2 hours ago | 60.82 |
| 168 | XZflow 3 | MQL5 | [2244502](https://www.mql5.com/en/signals/2244502) | 79.74 | 41.99 | 30.36 | that | 340.84 | 873 | BTCUSD ETHUSD USDJPY GBPJPY JP225 USTEC  | — | 9 hours ago | 60.72 |
| 169 | Autopilot Vibranium Akun Ke 3062 | MQL5 | [2382840](https://www.mql5.com/en/signals/2382840) | 136.48 | 37.61 | 22.31 | that | 395.39 | 369 | GBPUSD | — | 4 days ago | 60.71 |
| 170 | Live Account Breakout EA | MQL5 | [2283078](https://www.mql5.com/en/signals/2283078) | 79.15 | 19.66 | 21.85 | that | 189.10 | 749 | USDJPY XAUUSD | — | 51 minutes ago | 60.59 |
| 171 | BIGFISH PREMIUM DOLLARS | MQL5 | [2305053](https://www.mql5.com/en/signals/2305053) | 210.87 | 47.29 | 18.40 | that | 469.23 | 709 | AUDCAD EURUSD GBPUSD US30 XAUUSD | — | 2 hours ago | 60.44 |
| 172 | TriForce MT5 | MQL5 | [2126101](https://www.mql5.com/en/signals/2126101) | 41.53 | 44.62 | 35.19 | that | 176.95 | 4798 | EURUSD AUDCAD AUDUSD | — | 2 hours ago | 60.42 |
| 173 | Steady Growth | MQL5 | [2298652](https://www.mql5.com/en/signals/2298652) | 292.96 | 50.30 | 19.32 | that | 805.54 | 850 | GBPJPY_SB USDJPY_SB GBPCHF_SB USDCHF_SB  | — | 1 hour ago | 60.31 |
| 174 | PeacockFeather GBPUSD | MQL5 | [2286356](https://www.mql5.com/en/signals/2286356) | 104.52 | 27.83 | 21.39 | that | 257.99 | 462 | GBPUSD | hedge | 10 hours ago | 60.14 |
| 175 | IC 016 | MQL5 | [2350007](https://www.mql5.com/en/signals/2350007) | 213.41 | 30.09 | 11.50 | that | 198.84 | 1495 | EURUSD GBPUSD AUDCAD AUDNZD XAUUSD NZDCA | — | 14 hours ago | 60.14 |
| 176 | GoldZILLA AI Medium Risk | MQL5 | [2362448](https://www.mql5.com/en/signals/2362448) | 191.07 | 23.28 | 9.89 | that | 141.22 | 419 | XAUUSD | — | 4 hours ago | 60.1 |
| 177 | AlgoMind DayTrading | MQL5 | [2232206](https://www.mql5.com/en/signals/2232206) | 72.91 | 47.56 | 32.20 | that | 334.69 | 2635 | XAUUSD | — | 3 days ago | 60.04 |
| 178 | Derek | MQL5 | [2379723](https://www.mql5.com/en/signals/2379723) | 377.58 | 20.22 | 7.59 | that | 168.84 | 203 | BTCUSD XAUUSD | — | 4 days ago | 60.0 |
| 179 | GARYPRO2500 | MQL5 | [2350542](https://www.mql5.com/en/signals/2350542) | 110.84 | 21.73 | 18.17 | that | 209.39 | 195 | XAUUSD USDJPY | — | 3 days ago | 59.99 |
| 180 | EA Miracolo et Amazing Brain | MQL5 | [2394150](https://www.mql5.com/en/signals/2394150) | 3794.17 | 19.97 | 7.36 | that | 845.05 | 786 | XAUUSD.r AUDUSD.r EURUSD.r | — | 1 hour ago | 59.91 |
| 181 | VFCaput Vitual | MQL5 | [2377661](https://www.mql5.com/en/signals/2377661) | 66.79 | 21.89 | 23.00 | that | 166.57 | 2363 | NZDCAD AUDCAD AUDNZD GBPJPY EURAUD CADCH | — | 4 hours ago | 59.87 |
| 182 | Three whales2 | MQL5 | [2294877](https://www.mql5.com/en/signals/2294877) | 507.94 | 43.45 | 16.10 | that | 1026.37 | 863 | XAUUSD | — | 12 hours ago | 59.87 |
| 183 | SixtyNine EA | MQL5 | [2361673](https://www.mql5.com/en/signals/2361673) | 5279.92 | 23.29 | 8.51 | that | 1588.14 | 568 | XAUUSD+ | — | 3 days ago | 59.85 |
| 184 | AUDCAD Smart | MQL5 | [2356497](https://www.mql5.com/en/signals/2356497) | 406.00 | 24.74 | 8.97 | that | 236.01 | 137 | AUDCAD | — | 6 hours ago | 59.8 |
| 185 | Navi | MQL5 | [2234719](https://www.mql5.com/en/signals/2234719) | 74.99 | 40.10 | 28.75 | that | 282.16 | 1382 | BTCUSD | — | 3 hours ago | 59.77 |
| 186 | JFX 1 | MQL5 | [2354958](https://www.mql5.com/en/signals/2354958) | 489.90 | 26.12 | 9.43 | that | 303.37 | 948 | EURUSD XAUUSD | martingale | 2 hours ago | 59.76 |
| 187 | The Gold Reaper Live default settings | MQL5 | [2195619](https://www.mql5.com/en/signals/2195619) | 56.15 | 45.64 | 32.89 | that | 239.19 | 1368 | XAUUSD.p | — | 3 days ago | 59.73 |
| 188 | Golden Key Classic | MQL5 | [2304448](https://www.mql5.com/en/signals/2304448) | 198.26 | 49.79 | 18.17 | that | 423.15 | 204 | GOLD# | — | 3 days ago | 59.54 |
| 189 | ConnectGain BR Agressivo | MQL5 | [2376654](https://www.mql5.com/en/signals/2376654) | 172.27 | 28.87 | 13.11 | that | 198.70 | 1366 | NZDCADxx AUDCADxx AUDNZDxx GBPJPYxx GBPN | — | 15 hours ago | 59.44 |
| 190 | GGSetka | MQL5 | [2366387](https://www.mql5.com/en/signals/2366387) | 112.97 | 20.71 | 16.56 | that | 183.85 | 399 | AUDCAD EURCHF | — | 50 minutes ago | 59.34 |
| 191 | Guardian FX Pro | MQL5 | [2385674](https://www.mql5.com/en/signals/2385674) | 1527.20 | 15.03 | 4.60 | that | 191.33 | 560 | GBPUSD USDJPY EURJPY BTCUSD.futu EURUSD  | martingale, hedge, dca | 6 hours ago | 59.31 |
| 192 | EA RDIP HPro 5P | MQL5 | [2336904](https://www.mql5.com/en/signals/2336904) | 406.01 | 38.18 | 13.11 | that | 487.89 | 2272 | GBPJPY USDJPY GBPUSD EURJPY EURUSD XAUUS | hedge, dca | 12 hours ago | 59.2 |
| 193 | Aura Gold Pro Edition Rbfx | MQL5 | [2366593](https://www.mql5.com/en/signals/2366593) | 985.08 | 24.83 | 8.05 | that | 395.02 | 436 | XAUUSD | — | 47 minutes ago | 59.16 |
| 194 | Different gold strategies 1 | MQL5 | [2375487](https://www.mql5.com/en/signals/2375487) | 64.39 | 31.69 | 25.76 | that | 190.66 | 267 | XAUUSD | — | 3 days ago | 59.08 |
| 195 | Vasa Trading Sistem 22 | MQL5 | [2346593](https://www.mql5.com/en/signals/2346593) | 176.50 | 25.87 | 10.81 | that | 149.97 | 799 | XAUUSD | grid, martingale | 3 days ago | 58.98 |
| 196 | Portifolio IA XP | MQL5 | [2283635](https://www.mql5.com/en/signals/2283635) | 131.56 | 47.42 | 23.92 | that | 433.19 | 1764 | WINJ26 WINM26 WINV26 WINQ26 WINM25 WINV2 | — | 3 days ago | 58.96 |
| 197 | Metal | MQL5 | [2389070](https://www.mql5.com/en/signals/2389070) | 94513.21 | 12.97 | 3.22 | that | 528.85 | 191 | XAUUSD BTCUSD | — | 4 minutes ago | 58.9 |
| 198 | Oilman T | MQL5 | [2325346](https://www.mql5.com/en/signals/2325346) | 194.19 | 43.31 | 15.18 | that | 291.57 | 1051 | XAUUSD.min USOIL | grid | 3 hours ago | 58.86 |
| 199 | Expert EURUSD Sys03 | MQL5 | [2265440](https://www.mql5.com/en/signals/2265440) | 64.10 | 42.15 | 29.21 | that | 233.89 | 1763 | EURUSD+ XAUUSD+ | martingale, hedge | 10 hours ago | 58.74 |
| 200 | XAUUSD AND XAUEUR | MQL5 | [2340704](https://www.mql5.com/en/signals/2340704) | 214.49 | 42.73 | 14.03 | that | 281.76 | 292 | XAUUSD XAUEUR | — | 19 hours ago | 58.67 |
| 201 | KiraCat | MQL5 | [2342895](https://www.mql5.com/en/signals/2342895) | 377.23 | 36.70 | 11.73 | that | 360.74 | 604 | US30 NZDCAD US100 XAUUSD USDCAD | grid, dca | 4 days ago | 58.65 |
| 202 | Jayanthi EA MT5 | MQL5 | [2251746](https://www.mql5.com/en/signals/2251746) | 55.74 | 32.25 | 26.22 | that | 163.27 | 285 | XAUUSD | grid, martingale, hedge | 16 hours ago | 58.6 |
| 203 | TTS Joyful | MQL5 | [2385587](https://www.mql5.com/en/signals/2385587) | 7738.58 | 14.15 | 2.99 | that | 196.47 | 66 | XAUUSD | — | 2 hours ago | 58.46 |
| 204 | SNJ | MQL5 | [2317789](https://www.mql5.com/en/signals/2317789) | 154.46 | 37.92 | 17.02 | that | 276.10 | 344 | XAUUSD GBPUSD | — | 3 hours ago | 58.45 |
| 205 | LONG TERM TRADING | MQL5 | [2311926](https://www.mql5.com/en/signals/2311926) | 106.25 | 32.13 | 20.24 | that | 239.07 | 1038 | XAUUSD AUDCAD EURUSD USDJPY USDCHF EURAU | — | 7 hours ago | 58.43 |
| 206 | Gold Reaper 100 DD Challenge | MQL5 | [2363636](https://www.mql5.com/en/signals/2363636) | 410.45 | 28.98 | 8.51 | that | 217.73 | 290 | XAUUSD | — | 3 days ago | 58.43 |
| 207 | Invictus X VANTAGE | MQL5 | [2354834](https://www.mql5.com/en/signals/2354834) | 1302.54 | 31.86 | 9.43 | that | 696.68 | 3515 | BTCUSD XAUUSD+ ETHUSD | — | 2 minutes ago | 58.32 |
| 208 | ANTS Gold And Crypto | MQL5 | [2356592](https://www.mql5.com/en/signals/2356592) | 265.20 | 39.99 | 12.42 | that | 282.14 | 2851 | XAUUSDp SOLUSD BTCUSD EURUSDp GBPUSDp CH | — | 10 minutes ago | 58.28 |
| 209 | TOOP1 Swing Live | MQL5 | [2376664](https://www.mql5.com/en/signals/2376664) | 1007.52 | 20.05 | 4.83 | that | 163.24 | 62 | XAUUSD+ | — | 4 hours ago | 58.21 |
| 210 | ALGO VISION | MQL5 | [2341570](https://www.mql5.com/en/signals/2341570) | 1321.69 | 39.73 | 12.19 | that | 1382.72 | 353 | XAUUSD | grid, martingale | 3 days ago | 58.19 |
| 211 | Fortune | MQL5 | [2363526](https://www.mql5.com/en/signals/2363526) | 1783.22 | 33.03 | 9.66 | that | 962.42 | 171 | XAUUSD-ECN | grid, martingale, hedge | 3 days ago | 58.18 |
| 212 | Ultimate Portfolio 2000 | MQL5 | [2324441](https://www.mql5.com/en/signals/2324441) | 210.31 | 47.39 | 14.95 | that | 309.92 | 2705 | XAUUSD DE40 USTEC US30 US500 | — | 3 hours ago | 58.12 |
| 213 | Zenith Alpha USD | MQL5 | [2374284](https://www.mql5.com/en/signals/2374284) | 623.15 | 28.97 | 8.05 | that | 277.05 | 214 | USDCADb NZDCHFb EURCHFb EURUSDb CADCHFb  | grid | 2 hours ago | 58.12 |
| 214 | VTS You Only Live Once 7 | MQL5 | [2361280](https://www.mql5.com/en/signals/2361280) | 920.57 | 29.68 | 8.28 | that | 396.71 | 420 | XAUUSD | — | 3 days ago | 58.1 |
| 215 | MT4 8800983 | MQL5 | [2377259](https://www.mql5.com/en/signals/2377259) | 12067.27 | 21.69 | 5.06 | that | 657.28 | 1265 | XAUUSD.p | — | 4 hours ago | 57.95 |
| 216 | Survival Gold | MQL5 | [2368076](https://www.mql5.com/en/signals/2368076) | 1996.37 | 33.96 | 9.43 | that | 992.58 | 269 | XAUUSD | — | 3 days ago | 57.8 |
| 217 | Gold Breakout PRO All Star | MQL5 | [2351091](https://www.mql5.com/en/signals/2351091) | 2948.50 | 35.31 | 9.89 | that | 1571.61 | 122 | XAUUSD BTCUSD | grid, martingale | 3 days ago | 57.77 |
| 218 | GOLD ARROW | MQL5 | [2380453](https://www.mql5.com/en/signals/2380453) | 219.32 | 41.20 | 11.96 | that | 218.09 | 471 | XAUUSD archived XAGUSD | — | 5 days ago | 57.67 |
| 219 | ATG EA 31 | MQL5 | [2356340](https://www.mql5.com/en/signals/2356340) | 458.08 | 34.14 | 9.20 | that | 273.65 | 117 | XAUUSD | — | 4 hours ago | 57.6 |
| 220 | MoonDog EA | MQL5 | [2381309](https://www.mql5.com/en/signals/2381309) | 16622.23 | 20.14 | 3.91 | that | 430.18 | 263 | XAUUSD | — | 3 days ago | 57.57 |
| 221 | Aura Gold Pro Edition FPMarkets | MQL5 | [2358523](https://www.mql5.com/en/signals/2358523) | 1030.62 | 34.97 | 9.43 | that | 572.56 | 516 | XAUUSD | — | 4 hours ago | 57.54 |
| 222 | GoldHunterPro | MQL5 | [2365208](https://www.mql5.com/en/signals/2365208) | 1372.90 | 29.95 | 7.36 | that | 420.57 | 255 | GOLD# | — | 3 days ago | 57.42 |
| 223 | THE CHOSEN ONE from FXGP WMC | MQL5 | [2377696](https://www.mql5.com/en/signals/2377696) | 1316.28 | 24.68 | 5.29 | that | 221.71 | 349 | XAUUSD AUDNZD NZDCAD EURUSD | — | 3 days ago | 57.36 |
| 224 | WIND PRO | MQL5 | [2342791](https://www.mql5.com/en/signals/2342791) | 261.31 | 43.17 | 12.19 | that | 268.73 | 319 | XAUUSD BTCUSD archived | — | 2 hours ago | 57.33 |
| 225 | ABGsignals | MQL5 | [2369981](https://www.mql5.com/en/signals/2369981) | 553.45 | 32.85 | 8.28 | that | 265.17 | 992 | XAUUSD.pro GBPJPY.pro EURNZD.pro AUDJPY. | — | 7 hours ago | 57.31 |
| 226 | The Golden Rocket | MQL5 | [2385842](https://www.mql5.com/en/signals/2385842) | 995.65 | 25.49 | 5.52 | that | 200.78 | 112 | XAUUSD.ecn | grid, martingale | 43 minutes ago | 57.31 |
| 227 | BalanceDynamic | MQL5 | [2353706](https://www.mql5.com/en/signals/2353706) | 332.58 | 37.27 | 9.89 | that | 234.37 | 2533 | GBPUSD EURUSD USDCHF USDJPY | — | 4 hours ago | 57.28 |
| 228 | TRG Gold | MQL5 | [2387489](https://www.mql5.com/en/signals/2387489) | 245.94 | 34.41 | 8.74 | that | 146.93 | 183 | AUDNZD.pro XAUUSD.pro NZDCAD.pro AUDCAD. | — | 3 days ago | 57.22 |
| 229 | EURUSD Algo Trading | MQL5 | [2379670](https://www.mql5.com/en/signals/2379670) | 646.63 | 35.85 | 9.20 | that | 367.07 | 2395 | EURUSD AUDUSD | hedge | 42 minutes ago | 57.17 |
| 230 | CARRO CAPITAL TRADER GRID 1 | MQL5 | [2373260](https://www.mql5.com/en/signals/2373260) | 506.71 | 41.46 | 11.27 | that | 443.69 | 4463 | GBPNZD EURCAD AUDNZD AUDCAD EURJPY USDCH | grid, martingale | 23 minutes ago | 57.15 |
| 231 | Experimental Code | MQL5 | [2346983](https://www.mql5.com/en/signals/2346983) | 751.47 | 40.92 | 11.04 | that | 617.39 | 292 | XAUUSD | — | 3 days ago | 57.13 |
| 232 | AI 6CCY Account 261 | MQL5 | [2386895](https://www.mql5.com/en/signals/2386895) | 185.96 | 44.11 | 13.80 | that | 234.77 | 521 | AUDCAD# GBPCHF# NZDCAD# NZDUSD# USDCAD#  | — | 4 days ago | 57.12 |
| 233 | GoldExtractor1 | MQL5 | [2381685](https://www.mql5.com/en/signals/2381685) | 854.98 | 42.99 | 11.73 | that | 807.70 | 914 | XAUUSD+ | — | 4 hours ago | 57.07 |
| 234 | Janus Zone | MQL5 | [2386128](https://www.mql5.com/en/signals/2386128) | 13477.53 | 20.23 | 2.99 | that | 239.96 | 162 | XAUUSD | — | 6 hours ago | 56.94 |
| 235 | Dynamic Liquidity Intelligence XM100 | MQL5 | [2370969](https://www.mql5.com/en/signals/2370969) | 4906.50 | 29.18 | 6.21 | that | 657.72 | 229 | GOLD# | — | 4 hours ago | 56.84 |
| 236 | Predator50U | MQL5 | [2381799](https://www.mql5.com/en/signals/2381799) | 25372.18 | 22.56 | 3.68 | that | 446.84 | 261 | XAUUSD | — | 4 hours ago | 56.81 |
| 237 | IC 327 | MQL5 | [2342579](https://www.mql5.com/en/signals/2342579) | 226.70 | 45.33 | 12.19 | that | 232.88 | 2081 | EURUSD AUDCAD GBPUSD XAUUSD BTCUSD USDJP | — | 14 hours ago | 56.79 |
| 238 | Quant stategy | MQL5 | [2387834](https://www.mql5.com/en/signals/2387834) | 2198.65 | 29.43 | 6.21 | that | 406.48 | 270 | XAUUSD EURUSD GBPUSD | — | 2 hours ago | 56.78 |
| 239 | UpEverest MT5 | MQL5 | [2308091](https://www.mql5.com/en/signals/2308091) | 60.50 | 18.92 | 17.94 | that | 102.86 | 559 | AUDCAD | — | 4 hours ago | 56.77 |
| 240 | Ellita Master | MQL5 | [2349087](https://www.mql5.com/en/signals/2349087) | 143.49 | 35.82 | 14.95 | that | 203.03 | 769 | XAUUSDm USOILm BTCUSDm XAGUSDm USDJPYm E | — | 3 days ago | 56.77 |
| 241 | Precision BTC AI 2 | MQL5 | [2376777](https://www.mql5.com/en/signals/2376777) | 64395.88 | 27.41 | 5.29 | that | 1631.95 | 883 | BTCUSD XAUUSD-ECN | — | 2 minutes ago | 56.67 |
| 242 | Complete Portfolio 1 | MQL5 | [2340546](https://www.mql5.com/en/signals/2340546) | 62.32 | 40.69 | 25.76 | that | 182.88 | 5143 | USDJPY XAUUSD WS30 SP500 GDAXI EURUSD ND | grid, martingale | 1 hour ago | 56.67 |
| 243 | GANN LUNAR | MQL5 | [2358821](https://www.mql5.com/en/signals/2358821) | 212.50 | 47.81 | 12.65 | that | 232.39 | 296 | XAUUSD.pkn GBPJPY.pkn USDJPY.pkn GBPUSD. | — | 4 hours ago | 56.48 |
| 244 | Vantage Precision BTC AI | MQL5 | [2376778](https://www.mql5.com/en/signals/2376778) | 2235.17 | 27.74 | 5.06 | that | 277.55 | 708 | BTCUSD XAUUSD+ | — | 2 minutes ago | 56.44 |
| 245 | TradeSentinel Apex | MQL5 | [2363322](https://www.mql5.com/en/signals/2363322) | 778.02 | 43.42 | 10.81 | that | 607.85 | 214 | XAUUSD+ USDJPY+ | — | 3 days ago | 56.35 |
| 246 | Vatikan | MQL5 | [2385060](https://www.mql5.com/en/signals/2385060) | 450.99 | 34.84 | 7.59 | that | 194.29 | 366 | EURUSD# GBPUSD# USDJPY# GOLD# BRENTCash# | — | 8 hours ago | 56.35 |
| 247 | VS P4 Portfolio Lmax 1134 | MQL5 | [2360005](https://www.mql5.com/en/signals/2360005) | 446.63 | 37.70 | 8.51 | that | 233.54 | 430 | XAUUSD.lmx CHFJPY.lmx EURUSD.lmx | grid, martingale | 18 hours ago | 56.25 |
| 248 | Cuan Club Agresif 7575 | MQL5 | [2364335](https://www.mql5.com/en/signals/2364335) | 326.99 | 36.15 | 7.59 | that | 150.46 | 345 | AUDCAD-STD | — | 4 hours ago | 56.02 |
| 249 | Lucky Cat MT5 | MQL5 | [2359404](https://www.mql5.com/en/signals/2359404) | 421.94 | 41.30 | 9.43 | that | 266.38 | 748 | XAUUSD | grid, martingale | 3 days ago | 55.96 |
| 250 | RICH ULTIMA OMNI CORE | MQL5 | [2362617](https://www.mql5.com/en/signals/2362617) | 438.63 | 37.63 | 8.05 | that | 209.44 | 491 | USDJPY.s EURJPY.s GBPJPY.s XAUUSD.s | martingale, dca | 3 hours ago | 55.96 |
| 251 | ECN_Portafolio_46_Aggresive | MQL5 | [2378963](https://www.mql5.com/en/signals/2378963) | 1414.52 | 27.95 | 4.37 | that | 169.04 | 463 | USDJPY XAUUSD EURUSD XAGUSD AUDUSD AMZN  | — | 4 hours ago | 55.93 |
| 252 | TriForce Engine | MQL5 | [2353870](https://www.mql5.com/en/signals/2353870) | 282.09 | 41.59 | 9.43 | that | 186.74 | 123 | GBPJPY.r EURJPY.r EURUSD.r NZDCAD.r AUDU | — | 4 days ago | 55.89 |
| 253 | A171 Soar to great heights | MQL5 | [2349987](https://www.mql5.com/en/signals/2349987) | 747.11 | 44.92 | 10.58 | that | 557.86 | 264 | GOLD | — | 3 days ago | 55.82 |
| 254 | Solo levelling | MQL5 | [2356978](https://www.mql5.com/en/signals/2356978) | 341.72 | 40.86 | 8.97 | that | 203.56 | 2017 | XAUUSD | — | 4 days ago | 55.77 |
| 255 | Farmed Hedge Yield Zcopy | MQL5 | [2361272](https://www.mql5.com/en/signals/2361272) | 507.85 | 39.47 | 8.28 | that | 247.39 | 1755 | EURAUD GBPAUD USDCHF EURUSD AUDCAD AUDNZ | hedge | 4 hours ago | 55.65 |
| 256 | Farmed Hedge Yield Copy I | MQL5 | [2356376](https://www.mql5.com/en/signals/2356376) | 1039.17 | 42.20 | 9.20 | that | 545.73 | 2378 | EURAUD.p GBPAUD.p EURUSD.p AUDCAD.p GBPC | hedge | 4 hours ago | 55.58 |
| 257 | Titan Gravity Strategy | MQL5 | [2362566](https://www.mql5.com/en/signals/2362566) | 1117.17 | 39.92 | 8.28 | that | 460.91 | 656 | AUDCAD NZDCAD AUDNZD XAUUSD | — | 6 hours ago | 55.54 |
| 258 | Trade With Dre Challenge 500usd | MQL5 | [2363457](https://www.mql5.com/en/signals/2363457) | 3829.13 | 38.77 | 7.82 | that | 993.83 | 1548 | XAUUSD.ecn | — | 3 days ago | 55.52 |
| 259 | AlfaVova | MQL5 | [2292103](https://www.mql5.com/en/signals/2292103) | 97.99 | 47.42 | 22.54 | that | 260.74 | 851 | GBPUSDrfd EURUSDrfd EURGBPrfd AUDCADrfd  | — | 7 minutes ago | 55.52 |
| 260 | Pattern Recognition Portfolio | MQL5 | [2340550](https://www.mql5.com/en/signals/2340550) | 101.85 | 27.72 | 14.72 | that | 136.68 | 1410 | USDJPY XAUUSD EURUSD WS30 GDAXI SP500 ND | grid, martingale | 1 hour ago | 55.52 |
| 261 | Dynamic Liquidity Intelligence HFM50 | MQL5 | [2373900](https://www.mql5.com/en/signals/2373900) | 72294.45 | 32.69 | 5.52 | that | 1967.59 | 201 | XAUUSDr | — | 4 hours ago | 55.51 |
| 262 | HedGinG GUCJ B | MQL5 | [2365401](https://www.mql5.com/en/signals/2365401) | 1090.37 | 45.00 | 10.12 | that | 707.53 | 1062 | GBPUSD CADJPY | hedge | 9 hours ago | 55.5 |
| 263 | Basket | MQL5 | [2386274](https://www.mql5.com/en/signals/2386274) | 1430.40 | 35.47 | 6.44 | that | 332.36 | 239 | USDJPY AUDJPY EURJPY GBPJPY JP225 BTCUSD | — | 15 minutes ago | 55.43 |
| 264 | HedGinG AUAC B | MQL5 | [2365512](https://www.mql5.com/en/signals/2365512) | 354.76 | 35.50 | 6.44 | that | 125.43 | 310 | AUDCAD AUDUSD | hedge | 6 hours ago | 55.42 |
| 265 | Onyx MT5 | MQL5 | [2369976](https://www.mql5.com/en/signals/2369976) | 6057.25 | 36.58 | 6.44 | that | 812.65 | 80 | XAUUSD+ | — | 4 days ago | 55.15 |
| 266 | Farmed Hedge Yield VCopy | MQL5 | [2357156](https://www.mql5.com/en/signals/2357156) | 987.31 | 44.36 | 9.20 | that | 523.07 | 2276 | EURAUD+ GBPAUD+ EURUSD+ AUDCAD+ AUDNZD+  | hedge | 4 hours ago | 55.04 |
| 267 | SynerTrend | MQL5 | [2283124](https://www.mql5.com/en/signals/2283124) | 84.11 | 43.84 | 21.85 | that | 203.86 | 2288 | EURUSD | grid, dca | 2 hours ago | 54.91 |
| 268 | SMART AI SIGNAL PRIME | MQL5 | [2379924](https://www.mql5.com/en/signals/2379924) | 875.60 | 35.86 | 5.75 | that | 197.87 | 985 | EURUSD | martingale | 7 hours ago | 54.87 |
| 269 | BV Trader | MQL5 | [2364493](https://www.mql5.com/en/signals/2364493) | 142.58 | 45.03 | 15.64 | that | 217.39 | 1230 | XAUUSD USDJPY CHFJPY GBPJPY GBPUSD EURUS | hedge | 37 minutes ago | 54.86 |
| 270 | Market Cycles Order Flow Signal | MQL5 | [2362087](https://www.mql5.com/en/signals/2362087) | 123.83 | 44.48 | 17.48 | that | 223.39 | 1960 | USDJPY GBPJPY XAUUSD EURJPY XAUJPY XBRUS | grid, martingale | 51 minutes ago | 54.82 |
| 271 | Farmed Hedge Showcase II | MQL5 | [2364302](https://www.mql5.com/en/signals/2364302) | 805.09 | 43.53 | 8.51 | that | 376.93 | 1613 | EURAUD GBPAUD AUDNZD USDCHF NZDCAD AUDCA | hedge | 4 hours ago | 54.79 |
| 272 | XYZ Goldscalper | MQL5 | [2393167](https://www.mql5.com/en/signals/2393167) | 5387.83 | 31.73 | 3.68 | that | 241.52 | 437 | XAUUSD | — | 3 days ago | 54.52 |
| 273 | UpFuji MT5 | MQL5 | [2308095](https://www.mql5.com/en/signals/2308095) | 70.00 | 31.53 | 17.94 | that | 121.07 | 639 | AUDCAD | grid | 4 hours ago | 54.33 |
| 274 | GGAccel | MQL5 | [2386131](https://www.mql5.com/en/signals/2386131) | 4101.66 | 47.61 | 8.97 | that | 1534.96 | 182 | AUDCAD EURCHF | — | 49 minutes ago | 54.08 |
| 275 | GoldCyle I | MQL5 | [2388353](https://www.mql5.com/en/signals/2388353) | 1353.70 | 38.92 | 5.29 | that | 225.43 | 118 | XAUUSD | — | 4 hours ago | 53.8 |
| 276 | Rudy74 | MQL5 | [2360608](https://www.mql5.com/en/signals/2360608) | 143.94 | 41.08 | 12.19 | that | 147.41 | 3213 | XAUUSD NAS100 US500 US30 GER40 GBPAUD EU | grid, martingale, dca | 12 hours ago | 53.65 |
| 277 | Gold Biscuits | MQL5 | [2364006](https://www.mql5.com/en/signals/2364006) | 2799.55 | 46.81 | 7.82 | that | 797.33 | 415 | XAUUSD.. | — | 3 days ago | 53.51 |
| 278 | KS Fx 2 | MQL5 | [2379378](https://www.mql5.com/en/signals/2379378) | 2462.33 | 37.85 | 4.37 | that | 225.82 | 2590 | GBPUSD EURUSD AUDCAD USDCHF AUDUSD CADCH | — | 36 minutes ago | 53.45 |
| 279 | Gold and GBPUSD | MQL5 | [2383311](https://www.mql5.com/en/signals/2383311) | 1203.37 | 39.17 | 4.83 | that | 181.07 | 1012 | XAUUSD+ GBPUSD+ | — | 4 hours ago | 53.43 |
| 280 | AurumTrade | MQL5 | [2362353](https://www.mql5.com/en/signals/2362353) | 1211.14 | 50.40 | 8.97 | that | 584.61 | 2024 | EURJPY GOLD USDJPY GBPUSD USDCAD AUDUSD  | — | 8 hours ago | 53.38 |
| 281 | Gold M1 Pro | MQL5 | [2381033](https://www.mql5.com/en/signals/2381033) | 7407.57 | 36.92 | 3.68 | that | 275.97 | 78 | XAUUSD.r | — | 7 days ago | 53.22 |
| 282 | GoldenCrown | MQL5 | [2381896](https://www.mql5.com/en/signals/2381896) | 2753.97 | 54.41 | 10.12 | that | 1588.22 | 679 | XAUUSD+ | — | 4 hours ago | 53.14 |
| 283 | JS Horizon MG | MQL5 | [2378783](https://www.mql5.com/en/signals/2378783) | 2084.48 | 39.23 | 4.37 | that | 207.43 | 871 | BTCUSD XAUUSD | grid, martingale | 1 hour ago | 53.11 |
| 284 | Dynamic Liquidity Intelligence R300 | MQL5 | [2365514](https://www.mql5.com/en/signals/2365514) | 3585.30 | 47.34 | 7.36 | that | 813.63 | 267 | XAUUSD | — | 4 hours ago | 53.07 |
| 285 | My AI Gold EA High Risk | MQL5 | [2389616](https://www.mql5.com/en/signals/2389616) | 67445.29 | 43.59 | 5.52 | that | 1902.69 | 117 | XAUUSD | — | 4 days ago | 52.78 |
| 286 | Farmed Hedge Yield X | MQL5 | [2378337](https://www.mql5.com/en/signals/2378337) | 3880.29 | 42.38 | 4.83 | that | 340.52 | 878 | EURUSD USDCHF NZDCAD EURNZD USDCAD AUDNZ | hedge | 4 hours ago | 52.62 |
| 287 | Farmed Hedge Yield II | MQL5 | [2356404](https://www.mql5.com/en/signals/2356404) | 2921.67 | 55.49 | 9.20 | that | 1264.13 | 2330 | GBPAUDm EURAUDm EURUSDm AUDCADm NZDCADm  | hedge | 4 hours ago | 52.26 |
| 288 | Yoni Gold Signal | MQL5 | [2381882](https://www.mql5.com/en/signals/2381882) | 3617.19 | 46.60 | 4.83 | that | 328.56 | 207 | XAUUSD+ | — | 4 hours ago | 51.57 |
| 289 | Mahmoudsarhan | MQL5 | [2392033](https://www.mql5.com/en/signals/2392033) | 3641.75 | 41.81 | 2.99 | that | 146.58 | 298 | XAUUSD | — | 3 hours ago | 51.54 |
| 290 | Dynamic Liquidity Intelligence PUP50 | MQL5 | [2373901](https://www.mql5.com/en/signals/2373901) | 15802.06 | 50.22 | 5.52 | that | 929.60 | 199 | XAUUSD.s | — | 4 hours ago | 51.12 |
| 291 | Dynamic Liquidity Intelligence pep50 | MQL5 | [2384429](https://www.mql5.com/en/signals/2384429) | 133114.00 | 44.66 | 3.22 | that | 589.32 | 116 | XAUUSD | — | 4 hours ago | 50.98 |
| 292 | Hum reaper | MQL5 | [2385216](https://www.mql5.com/en/signals/2385216) | 7480.78 | 44.59 | 2.99 | that | 194.01 | 377 | XAUUSD | — | 3 days ago | 50.85 |

## Chặn / không đọc được

- `https://www.myfxbook.com/systems` — bi_chan 403
- `https://social-trading.exness.com/strategy/110170778` — loi 

## Dịch ngược (`nhan/dich_nguoc`)

Lịch sử lệnh CSV của MQL5 (`/export/history`) chuyển hướng sang đăng nhập → **không có CSV công khai** cho tín hiệu ĐẠT nào; chưa đưa được vào dịch ngược từ box. Cách làm tiếp: Anh đăng nhập MQL5 trên máy nhà, tải CSV vào `data/cong_khai/csv/<id>.csv`, rồi `python -m nhan.dich_nguoc --lich-su data/cong_khai/csv/<id>.csv --ten mql5_<id> --url <link>`.
