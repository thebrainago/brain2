# SEEKER đa nguồn — EA, chiến lược, chỉ báo, lịch sử giao dịch

Cập nhật: 2026-10-19 01:27 (giờ Bangkok, UTC+7). Chỉ mục máy đọc: `reports/SEEKER_DA_NGUON.json` (lược đồ `seeker_da_nguon/1`). Bản đầy đủ từng ứng viên: `data/seeker_da_nguon/ung_vien.jsonl` (git bỏ qua). Mã của người khác chỉ nằm trong `data/seeker_da_nguon/tai_ve/`, không vào repo.

**Mọi số lãi/DD dưới đây là theo tác giả hoặc công khai tại nguồn, CHƯA đo lại.** Chưa chạy bất kì mã tải về nào.

## Tổng quan

- Tổng ứng viên: **2580**; có mã: 1919; đã tải file: 1497; lịch sử có từng lệnh: 26.
- Trạng thái đọc: da_tai_doc_ky_hieu 950, da_tai 547, chi_url 1083.

### Theo loại

| Nhóm | Số |
|---|---|
| ea_hoan_thien | 1815 |
| lich_su_giao_dich | 514 |
| tien_ich | 126 |
| mo_ta_phuong_phap | 63 |
| chi_bao | 62 |

### Theo nguồn

| Nhóm | Số |
|---|---|
| github (qua chỉ mục ForexR, chỉ URL) | 858 |
| mql5_codebase | 483 |
| mql5_signals | 465 |
| github | 301 |
| forexfactory | 300 |
| tradingview | 80 |
| gogojungle | 43 |
| forex_station | 40 |
| web_blog_ja | 3 |
| web_blog_zh | 1 |
| mql5_forum | 1 |
| web_codebase_en | 1 |
| web_blog_vi | 1 |
| fxblue | 1 |
| myfxbook | 1 |
| gitee | 1 |

### Theo ngôn ngữ

| Nhóm | Số |
|---|---|
| en | 2291 |
| ru | 138 |
| ja | 63 |
| zh | 55 |
| pt | 20 |
| es | 10 |
| vi | 3 |

### Theo nền tảng

| Nhóm | Số |
|---|---|
| mt4 | 1150 |
| mt5 | 1092 |
| mt4_mt5 | 119 |
| pine | 106 |
| thu_cong | 53 |
| freqtrade | 39 |
| python | 17 |
| khac | 2 |
| backtrader | 1 |
| jesse | 1 |

### Theo phong cách (một ứng viên có thể nhiều nhãn)

| Nhóm | Số |
|---|---|
| trend | 1431 |
| trailing | 865 |
| mean_reversion | 852 |
| news | 747 |
| prop_risk | 700 |
| martingale | 625 |
| grid | 604 |
| hedge | 445 |
| scalp | 399 |
| breakout | 396 |
| session | 396 |
| basket | 265 |
| dca | 229 |
| recovery | 217 |
| smc_ict | 145 |
| ml_ai | 99 |

### Loại × nguồn

| Nguồn | Loại | Số |
|---|---|---|
| github | ea_hoan_thien | 1121 |
| mql5_signals | lich_su_giao_dich | 465 |
| mql5_codebase | ea_hoan_thien | 427 |
| forexfactory | ea_hoan_thien | 180 |
| tradingview | ea_hoan_thien | 80 |
| mql5_codebase | tien_ich | 54 |
| forexfactory | tien_ich | 50 |
| gogojungle | lich_su_giao_dich | 43 |
| forexfactory | chi_bao | 35 |
| forexfactory | mo_ta_phuong_phap | 31 |
| github | tien_ich | 22 |
| forex_station | mo_ta_phuong_phap | 22 |
| forex_station | chi_bao | 18 |
| github | mo_ta_phuong_phap | 9 |
| github | chi_bao | 7 |
| forexfactory | lich_su_giao_dich | 4 |
| web_blog_ja | ea_hoan_thien | 3 |
| mql5_codebase | chi_bao | 2 |
| web_blog_zh | ea_hoan_thien | 1 |
| mql5_forum | ea_hoan_thien | 1 |
| web_codebase_en | ea_hoan_thien | 1 |
| web_blog_vi | ea_hoan_thien | 1 |
| fxblue | lich_su_giao_dich | 1 |
| myfxbook | lich_su_giao_dich | 1 |
| gitee | mo_ta_phuong_phap | 1 |

## Xếp hạng ứng viên hoàn thiện đáng test nhất

Chọn tay từ điểm `diem_uu_tien` và đọc mô tả nguồn. "MT5 thẳng" = có .mq5/.ex5 hoặc mã MQL5 để chạy Strategy Tester; "Python" = cần dịch/chạy bằng khung Python; "Chỉ lịch sử" = signal không có mã, dùng làm chuẩn đối chiếu.

| # | Tên | Nguồn | URL | Chạy | Vì sao |
|---|---|---|---|---|---|
| 1 | 370 Percent from 2022 to 2026 at 10 Percent MaxDD. The GER40 | mql5_codebase | https://www.mql5.com/en/code/78380 | MT5 thẳng | EA phá vỡ phiên GER40 H1 có lưới gỡ; tác giả đăng backtest 2022–2026 +376,5% (≈78,7%/năm, lot cố định), DD 10,5%, PF 2,07 — theo tác giả, chưa đo |
| 2 | 87.8 Percent from 2021 to YTD at 8.5 Percent MaxDD. The Nikk | mql5_codebase | https://www.mql5.com/en/code/78027 | MT5 thẳng | EA phiên JP225 M15; tác giả ghi +18,5%/năm không gộp, DD 8,5%, PF 1,68 — theo tác giả, chưa đo |
| 3 | Gold Breakout EA for XAUUSD H4 +90 Percent in a 2020 to 2026 | mql5_codebase | https://www.mql5.com/en/code/77691 | MT5 thẳng | Breakout kiểu Turtle trên XAUUSD H4; tác giả ghi +90% 2020–2026, DD 11,38%, PF 1,77 — theo tác giả |
| 4 | ExMachina SafeScalping | mql5_codebase | https://www.mql5.com/en/code/70052 | MT5 thẳng | Scalp có lưới/DCA, tự dừng khi DD vượt ngưỡng, lọc phiên; tác giả ghi DD 0,86%, PF 1,24 |
| 5 | GridPro Panel — open-source grid trading EA with on-chart co | mql5_codebase | https://www.mql5.com/en/code/78206 | MT5 thẳng | GridPro Panel: lưới mã mở đủ lớp quản lí rủi ro (SL rổ theo tiền, giới hạn từng lớp) — mẫu tốt cho xử lí lệnh |
| 6 | XANDER Grid XAUUSD | mql5_codebase | https://www.mql5.com/en/code/71776 | MT5 thẳng | XANDER Grid XAUUSD: lưới + martingale + gỡ lệnh cho vàng, đúng trọng tâm xử lí lệnh |
| 7 | BlueMoon | mql5_codebase | https://www.mql5.com/en/code/75264 | MT5 thẳng | BlueMoon: lưới rổ có hedge và recovery, nhiều kí hiệu vận hành |
| 8 | Free Grid EA Ikarus - From zero to hero | forexfactory | https://www.forexfactory.com/thread/1070898-free-grid-ea-ikarus-from-zero-to | MT4/MT5 thẳng | Ikarus: EA lưới miễn phí, thread FF dài có người dùng đăng kết quả; đã tải 4 file |
| 9 | Most Famous Blessing 3.9.6 EA and Setfiles | forexfactory | https://www.forexfactory.com/thread/792598-most-famous-blessing-396-ea-and-setfiles | MT4 thẳng | Blessing 3.9.6: lưới/martingale kinh điển, nhiều bộ .set; đã tải file đính kèm từ thread FF |
| 10 | MT5 Grid and Recovery EA | forexfactory | https://www.forexfactory.com/thread/1408891-mt5-grid-and-recovery-ea | MT5 thẳng | MT5 Grid and Recovery EA: lưới + gỡ lệnh, tác giả đăng statement live trong thread |
| 11 | Trio Orchestra EA: A free - no expiry - little grid rider | forexfactory | https://www.forexfactory.com/thread/736275-trio-orchestra-ea-a-free-no-expiry | MT4 thẳng | Trio Orchestra: lưới nhỏ miễn phí không hết hạn, thread dài có kết quả người dùng |
| 12 | Flexy Grid EA (Grid Trading) | forexfactory | https://www.forexfactory.com/thread/682126-flexy-grid-ea-grid-trading | MT4 thẳng | Flexy Grid EA: lưới cấu hình linh hoạt, file đã tải |
| 13 | Kashi Recovery Grid (KRG) | forexfactory | https://www.forexfactory.com/thread/1413269-kashi-recovery-grid-krg | MT4/MT5 thẳng | Kashi Recovery Grid: lưới gỡ lệnh XAUUSD, đã tải 1 file |
| 14 | Range breakout EA, ORB EA, Opening range breakout EA | forexfactory | https://www.forexfactory.com/thread/1407952-range-breakout-ea-orb-ea-opening-range-breakout | MT5 thẳng | Range Breakout/ORB EA: luật phiên rõ, đã tải 7 file |
| 15 | EA Friday Gold Rush | forexfactory | https://www.forexfactory.com/thread/1060592-ea-friday-gold-rush | MT4/MT5 thẳng | Friday Gold Rush: EA theo phiên XAUUSD/US30, đã tải 7 file |
| 16 | Three Pairs Hedging | forexfactory | https://www.forexfactory.com/thread/279648-three-pairs-hedging | MT4 thẳng | Three Pairs Hedging: hedge 3 cặp tương quan, đã tải 5 file |
| 17 | geraked/metatrader5 | github | https://github.com/geraked/metatrader5 | MT5 thẳng | 149 file MQL5, MIT; nhiều EA chiến lược kèm kết quả backtest trong README |
| 18 | zhutoutoutousan/profitable-expert-advisor | github | https://github.com/zhutoutoutousan/profitable-expert-advisor | MT5 thẳng | 952 file, ~691 file .set; EA vàng/bạc/NZDUSD H1 kèm thiết lập tối ưu |
| 19 | EA31337/EA31337 | github | https://github.com/EA31337/EA31337 | MT4/MT5 thẳng | Khung EA đa chiến lược GPL-3.0, CI backtest công khai |
| 20 | GeneralTradingSarl/expert-mt5 | github | https://github.com/GeneralTradingSarl/expert-mt5 | MT5 thẳng | ~2372 file EA MT5 mã mở (lưới, martingale, hedge, recovery) — kho lớn để lọc hàng loạt |
| 21 | GeneralTradingSarl/mql4_experts | github | https://github.com/GeneralTradingSarl/mql4_experts | MT4 (dịch MT5 hoặc chạy MT4) | ~2218 file EA MT4 mã mở |
| 22 | sajidmahamud835/grid-master-pro-mt5-ea | github | https://github.com/sajidmahamud835/grid-master-pro-mt5-ea | MT5 thẳng | Lưới hai chiều theo ATR, lot động, chặn DD; MIT |
| 23 | Drakkar-Software/OctoBot | github | https://github.com/Drakkar-Software/OctoBot | Python (crypto) | Bot Python GPL-3.0 có grid/DCA, backtest sẵn — tham chiếu luật dịch Python |
| 24 | ICTrading Signal 2 | mql5_signals | https://www.mql5.com/en/signals/926651 | Chỉ lịch sử (đối chiếu) | Signal 477 tuần, +491,9% (≈21,4%/năm), DD vốn 18,9%, PF 3,85 — công khai MQL5, chưa đo |
| 25 | Scalp IC Markets MT5 | mql5_signals | https://www.mql5.com/en/signals/1560883 | Chỉ lịch sử (đối chiếu) | Scalp đa cặp 253 tuần, ≈56,7%/năm, DD vốn 32,9% — công khai MQL5 |
| 26 | Gold Minion | mql5_signals | https://www.mql5.com/en/signals/2351061 | Chỉ lịch sử (đối chiếu) | Gold Minion XAUUSD 154 tuần, ≈83,1%/năm, DD vốn 7,2% — công khai MQL5 |
| 27 | SFE Impulse | mql5_signals | https://www.mql5.com/en/signals/2049326 | Chỉ lịch sử (đối chiếu) | SFE Impulse BTC/ETH 163 tuần, ≈54,2%/năm, DD vốn 7,9% — công khai MQL5 |
| 28 | Trading Hero 20k | mql5_signals | https://www.mql5.com/en/signals/544163 | Chỉ lịch sử (đối chiếu) | Trading Hero 20k 405 tuần, ≈27,2%/năm, DD vốn 33,8% — công khai MQL5 |

Danh sách tự động theo `diem_uu_tien` (40 mục đầu, chỉ để tham khảo):

| Điểm | id | Tên | Loại | Nền tảng | URL |
|---|---|---|---|---|---|
| 82 | gh_elrizwiraswara__nyao_scalper_mt5 | elrizwiraswara/nyao_scalper_mt5 | ea_hoan_thien | mt5 | https://github.com/elrizwiraswara/nyao_scalper_mt5 |
| 79.5 | gh_Marco210210__AI-Enhanced-HFT | Marco210210/AI-Enhanced-HFT | ea_hoan_thien | mt5 | https://github.com/Marco210210/AI-Enhanced-HFT |
| 78.3 | gh_tHeStRyNg__mt5_mql5_eas | tHeStRyNg/mt5_mql5_eas | ea_hoan_thien | mt5 | https://github.com/tHeStRyNg/mt5_mql5_eas |
| 78 | gh_Drakkar-Software__OctoBot | Drakkar-Software/OctoBot | ea_hoan_thien | python | https://github.com/Drakkar-Software/OctoBot |
| 78 | gh_matthewkastor__Metatrader | matthewkastor/Metatrader | ea_hoan_thien | mt4 | https://github.com/matthewkastor/Metatrader |
| 76.7 | mql5cb_78027 | 87.8 Percent from 2021 to YTD at 8.5 Percent MaxDD | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/78027 |
| 75.5 | mql5cb_78380 | 370 Percent from 2022 to 2026 at 10 Percent MaxDD. | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/78380 |
| 74.8 | gh_dryousufmesalm__Experts | dryousufmesalm/Experts | ea_hoan_thien | mt4_mt5 | https://github.com/dryousufmesalm/Experts |
| 74 | mql5cb_68764 | Easy Range Breakout EA - MT5 | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/68764 |
| 74 | mql5cb_71776 | XANDER Grid XAUUSD | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/71776 |
| 74 | mql5cb_71700 | RSI Grid EA Pro | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/71700 |
| 74 | mql5cb_71583 | ASQ Command Desk | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/71583 |
| 74 | mql5cb_71189 | ASQ Safe Scalping v1.20 | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/71189 |
| 74 | mql5cb_63193 | Quantum Gold Silver Trader | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/63193 |
| 74 | mql5cb_63569 | Martingale Pulse EA | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/63569 |
| 74 | mql5cb_62732 | EMA_RSI_RISK-EA | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/62732 |
| 74 | mql5cb_53022 | Smart Trend Follower | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/53022 |
| 74 | mql5cb_49272 | Simple Yet Effective Breakout Strategy | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/49272 |
| 74 | mql5cb_46339 | Advisor Based on RSI and Martingale | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/46339 |
| 74 | mql5cb_22854 | MA MACD Position averaging v2 | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/22854 |
| 74 | mql5cb_21511 | CCI and Martin | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/21511 |
| 74 | mql5cb_21331 | MartingailExpert | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/21331 |
| 74 | mql5cb_19464 | Martin | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/19464 |
| 74 | mql5cb_19459 | Bollinger Bands RSI | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/19459 |
| 74 | mql5cb_17439 | SilverTrend v3 | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/17439 |
| 74 | mql5cb_17284 | RSI EA | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/17284 |
| 74 | mql5cb_17122 | Angry Bird (Scalping) | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/17122 |
| 74 | mql5cb_16994 | Bollinger Bands | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/16994 |
| 74 | mql5cb_26324 | Reversing Martingale EA | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/26324 |
| 74 | mql5cb_23511 | hedger | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/23511 |
| 74 | mql5cb_23152 | RSI EA v2 | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/23152 |
| 74 | gh_geraked__metatrader5 | geraked/metatrader5 | ea_hoan_thien | mt5 | https://github.com/geraked/metatrader5 |
| 74 | gh_peterthomet__MetaTrader-5-and-4-Tools | peterthomet/MetaTrader-5-and-4-Tools | ea_hoan_thien | mt4_mt5 | https://github.com/peterthomet/MetaTrader-5-and-4-Tools |
| 74 | gh_kecoma1__Trading_BOT | kecoma1/Trading_BOT | ea_hoan_thien | mt5 | https://github.com/kecoma1/Trading_BOT |
| 74 | gh_santiago-cruzlopez__MQL5 | santiago-cruzlopez/MQL5 | ea_hoan_thien | mt5 | https://github.com/santiago-cruzlopez/MQL5 |
| 74 | gh_GifariKemal__xaubot-ai | GifariKemal/xaubot-ai | ea_hoan_thien | mt5 | https://github.com/GifariKemal/xaubot-ai |
| 74 | gh_sajidmahamud835__grid-master-pro-mt5-ea | sajidmahamud835/grid-master-pro-mt5-ea | ea_hoan_thien | mt5 | https://github.com/sajidmahamud835/grid-master-pro-mt5-ea |
| 73.8 | mql5cb_30560 | Periodic Range Breakout (Martingale) | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/30560 |
| 73.7 | mql5cb_17849 | Trade on qualified RSI | ea_hoan_thien | mt5 | https://www.mql5.com/en/code/17849 |
| 73.7 | gh_zhutoutoutousan__profitable-expert-advisor | zhutoutoutousan/profitable-expert-advisor | ea_hoan_thien | mt5 | https://github.com/zhutoutoutousan/profitable-expert-advisor |

## Lịch sử giao dịch

- Tổng 514 mục lịch sử (MQL5 Signals ≥26 tuần có lãi quy năm, statement đính kèm FF, FX Blue…). Có từng lệnh: 26 (statement .htm/.csv tải từ FF/forex-station/GitHub). MQL5 Signals chỉ có số tổng hợp + đường vốn; tab lịch sử lệnh cần đăng nhập → xem `reports/URL_BI_CHAN.md`.

## Nguồn bị chặn / không đọc được

Chi tiết từng URL để chủ dự án tự mở bằng Chrome: `reports/URL_BI_CHAN.md`.

- **Myfxbook**: 403 Cloudflare "Attention Required" mọi URL.
- **BabyPips forum**: 403 Cloudflare "Just a moment".
- **ZuluTrade**: CAPTCHA.
- **FX Blue**: dữ liệu render JS (Next.js), không lấy được bằng requests.
- **TradingView**: mã Pine hiển thị bằng JS; không gọi API nội bộ → chỉ lấy tên, mô tả, URL.
- **Gitee**: tìm kiếm cần JS, API v5 trả rỗng.
- **MQL5 Signals**: tab lịch sử lệnh cần đăng nhập; MQL5 giới hạn tốc độ (403 khi >~1,5 lượt/giây) → đã giãn 2,5–3 giây, không lách.
- **forexsystems.ru**: nay là trang tin, /forum 404.
- **mql.opentraders.ru, fx-prog.com, 59log.com, forexmt4indicators.com**: kết nối thất bại/hết giờ.
- **darwinex /darwins**: 404.
- **GogoJungle, fx-on**: sản phẩm trả phí: chỉ ghi tên, URL, số forward công khai.
- **forex-warez, yoforexea…**: trang phát tán lậu — cố ý bỏ qua.

## Ghi chú

- Phong cách gán bằng regex trên mô tả + mã, có thể dư nhãn (vd. "news" khi EA chỉ có bộ lọc tin).
- Ứng viên `chi_url` (chủ yếu từ chỉ mục ForexR → GitHub) chưa tải mã; ưu tiên thấp hơn.
- Ngưỡng lọc sau này dùng DD < 65%, lãi > 15%/năm (bộ lọc Python); số ở đây chỉ để xếp hàng test.
- Không đăng nhập, không mua, không vượt Cloudflare/captcha.
