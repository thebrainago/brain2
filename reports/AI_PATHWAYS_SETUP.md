# Kênh AI Pathways (Brendan): toàn bộ setup giao dịch và cách backtest

Ngày lập: 08/11/2026 (giờ Việt Nam). Nguồn: phụ đề tự động tiếng Anh của từng video, lấy bằng youtube-transcript-api.
Mọi con số dưới đây đều do tác giả nói trong video. Ô ghi "không nêu" nghĩa là video không có số đó.

> **Lưu ý lớn:** tác giả chủ yếu test cổ phiếu/ETF Mỹ (SPY, QQQ, sector ETF), vàng (ETF GLD), crypto ngày và futures NQ/ES khung phút.
> Video ICT ghi rõ là **không test forex và vàng**. Chưa có số nào của anh ta áp trực tiếp cho XM/MT5.

## 1. Video đã đọc và video bỏ qua

Kênh có khoảng 60 video. 23 video liên quan trading đã được đọc:

**Đọc toàn bộ phụ đề (14 video):**
- [Claude Tested Over 9,000 Trading Strategies](https://youtu.be/nLQhKkjkuWI)
- [Claude Tested 100,000 Price Action Strategies](https://youtu.be/z97PnFIPoFg)
- [Claude Tested Over 25,000 ICT Strategies](https://youtu.be/KML09tRtHM8)
- [How To Backtest Properly With Claude Code](https://youtu.be/lIMu8ysJW68)
- [How To Actually Find A Profitable Strategy With Claude](https://youtu.be/Fb7G5SNpaes)
- [Claude Ranks Every Trading Style From Worst to Best](https://youtu.be/zGmsARTATvQ)
- [Claude Tests The Most Misunderstood Concept In Trading (VIX)](https://youtu.be/WPLkK4M9aDY)
- [Which Trading Psychology Concepts Actually Work?](https://youtu.be/9rBgnMnDp_0)
- [How To Actually Use Claude Code for Trading Strategies (Like a Quant) – HMM](https://youtu.be/EUSXhJNwRqI)
- [How To Actually Build a Trading Bot With Claude Code (Fully Automated)](https://youtu.be/y_bsjZThP0o)
- [I Built a Profitable AI Agent Day Trader (n8n)](https://youtu.be/rDf3TfHlGmk)
- [I Tested Letting Claude Trade For A Month and Made $102k](https://youtu.be/RetsRS5u-8Q)
- [Everything I've Learned Trading With Claude In 18 Minutes](https://youtu.be/CPkrCoIbBIA)

**Đọc theo các câu có số liệu hoặc luật (lọc tự động, vì phần còn lại chủ yếu là hướng dẫn cài đặt):**
- [How To Actually Build an AI Trading Bot With Claude (3 Hour Course)](https://youtu.be/gJLKVsIqiTE)
- [How To Actually Use GPT-6 Astra For Trading](https://youtu.be/TVNOTqv0n1k)
- [MIT Researchers Built An AI Hedge Fund](https://youtu.be/w-8XSCgwzHw)
- [10 Ways To Actually Use Jev For Trading](https://youtu.be/ib5R3Jib75A)
- [Here's How Claude Can Make You A Better Trader](https://youtu.be/qh3AohVimGw)
- [Build a Self Learning AI Trading Agent with Hermes](https://youtu.be/VfiwA1YThSc)
- [How To Turn Claude Into Your Personal Hedge Fund](https://youtu.be/ANUXcTgrpg0)
- [Claude Will Change Trading Forever](https://youtu.be/G7zv25c7Z8M)
- [TradingView Indicators to AI Agents (n8n)](https://youtu.be/Bxs9QmdOLoI)
- [How I Use ChatGPT-5 to Analyze and Trade Stocks](https://youtu.be/cyLQYYsZRoA)
- [AI Agent Tracks Politician Stock Trades](https://youtu.be/l4DB0Gtoz-Q)
- [AI Agents Find Winning Memecoins](https://youtu.be/ImpjIEEcpCU)
- [AI Agent Crypto Quant (n8n)](https://youtu.be/28-o-SNST_c)

**Bỏ qua:** khoảng 35 video về AI, n8n, kinh doanh, coding, bất động sản, SEO, cá cược thể thao (RMF4IWbMxg4) và "100 Ways To Use AI for Investing" (uFmexDIhRM4, chỉ là danh sách ý tưởng).

## 2. Bảng toàn bộ setup

| # | Setup | Thị trường | Khung | Luật vào | SL | TP / thoát | Lọc | Sizing | Số liệu (IS / OOS / holdout) | Kết luận của tác giả |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Xoay QQQ/vàng (trend core)** | QQQ, vàng | D1 | Giá đóng QQQ trên MA200 thì giữ QQQ, dưới MA200 thì giữ vàng | không có | Đổi tài sản khi cắt MA200 | MA200 | 100% vốn (lõi) | Holdout 2023→nay: **33,8%/năm, Sharpe 1,66**, khoảng 5 lệnh/năm; test lùi 50 năm; video Astra: 2 hệ sống/159 đều là biến thể của hệ này | **Giữ**, là lõi danh mục |
| 2 | Xoay vòng momentum ETF | 50 ETF | Tháng | Mỗi tháng giữ 5 ETF gần đỉnh 52 tuần nhất | không có | Tái cân bằng hàng tháng; ra tiền mặt khi SPY dưới MA200 | MA200 của SPY | Chia đều (không nêu chi tiết) | Sống qua phễu (khoảng 155 ý tưởng → 5 hệ) | **Giữ** |
| 3 | Bắt đáy SPY theo biên độ ngày | SPY | D1 | Giá đóng nằm trong 10% thấp nhất của biên độ ngày, chỉ số vẫn trên MA200 | không nêu | Thoát ở nến đóng mạnh hoặc sau 3 ngày | MA200 | không nêu | Sống qua phễu | **Giữ** |
| 4 | **Bắt đáy RSI2** (khóa 3 giờ) | QQQ (tốt nhất), SPY | D1 | RSI(2) < 10, giá trên MA200, vào ở giá mở nến sau | **8% dưới giá vào** (lệnh stop đặt sẵn ở broker) | Đóng trên MA5 hoặc sau 10 ngày, cái nào đến trước | MA200 | 10% tài khoản mỗi lệnh | Lock test: **24,8%/năm, maxDD 11,2%**; winner lớn hơn loser 1,3 lần; test độ nhạy với RSI < 5 / < 15 và MA3 / MA10 | **Giữ** (sleeve) |
| 5 | Breakout biên độ 30 phút đầu (ORB) | NQ futures | Trong ngày | Phá biên độ 30 phút đầu phiên | không nêu | không nêu | không nêu | không nêu | Là hệ trong ngày duy nhất sống trong danh mục 5 hệ | **Giữ** |
| 6 | Lớp sizing nhắm volatility | Danh mục | — | — | — | — | — | Scale vị thế để danh mục chạy khoảng 20% vol | — | **Giữ**, dùng làm lớp sizing |
| 7 | **CHoCH H4** (price action) | NQ, ES | H4 | Nến đóng đầu tiên phá ngược cấu trúc (change of character), **không chờ sweep**, vào ở giá đóng | Sau swing gần nhất (stop cứng) | **TP = 1R** | Tùy chọn: chỉ phiên New York; bỏ lệnh cùng chiều chuỗi chạy 3 ngày | 1 hợp đồng | Holdout 2 năm: **≈ $62k (NQ), ≈ $39k (ES)**; 39/48 bản có lãi; khoảng 2/3 bản phổ biến có lãi | **Giữ**, là setup price action tốt nhất |
| 8 | Flip zone (kháng cự cũ thành hỗ trợ) | NQ, ES | Nhiều khung | Lần retest đầu tiên | — | — | — | — | Giữ giá tốt hơn đường ngẫu nhiên **+11,5 điểm % (NQ), +10,9 (ES)** | Hữu ích làm tín hiệu/lọc |
| 9 | Level hỗ trợ/kháng cự | NQ, ES | — | — | — | — | — | — | Level giữ giá 51,1% số lần; chạm 1 lần hơn ngẫu nhiên 9 điểm %, chạm 4 lần 6,1 điểm % (chạm nhiều lần **không** mạnh hơn) | Level có thật; số lần chạm không quan trọng |
| 10 | Sweep đứng riêng | NQ, ES | — | — | — | — | — | — | Chỉ đảo chiều khoảng một nửa số lần; trên holdout, CHoCH có thêm sweep thì lỗ | **Loại** làm lõi |
| 11 | **ICT Silver Bullet "as traded"** | NQ, ES | M1 | Bắt buộc có sweep, đánh ngược phía vừa bị quét, vào ở FVG M1 | Sau swing | Mục tiêu 2:1 hoặc thoát theo thời gian | **Bỏ** bias 15 phút; không cần khung giờ silver bullet | 1 hợp đồng | 25.000 bản → 420 sống (1,7%); holdout 2 năm: bản tốt nhất **$455k**, Sharpe 13 (tác giả nói không thực tế); bản as traded **$251k**; khoảng 1.996 lệnh/năm; 62–68% tháng dương; có chuỗi thua 19 ngày liên tiếp; win rate 34–52% | Sweep là luật duy nhất thêm edge (điểm 33 → 69); bias 15 phút làm tụt còn 0,16. Tác giả coi đây là mean reversion |
| 12 | ICT bản textbook (M5 / M1) | NQ, ES | M5, M1 | Đúng như sách dạy | | | | | M5 chết ở bậc Sharpe; M1 chết ở bậc chạy nguội trên ES; bản M5 khoảng 34 lệnh/năm | **Loại** |
| 13 | Mean reversion trơn (RSI, Bollinger, Keltner) | 30 tài sản (ETF, vàng, dầu, trái phiếu, BTC, ETH, cổ phiếu lớn) | D1, 15 năm | Giá lệch xa trung bình | không nêu | Quay về trung bình | — | — | 9.000 bản → 524 → 478; **64% số hệ sống là mean reversion**; RSI reversion sống trên 20 mã, Keltner trên 18 mã | **Giữ**, là nền tảng |
| 14 | Trend/breakout trơn (MA cross, Turtle, dual momentum) | 30 tài sản | D1 | — | — | — | — | — | Trung bình âm; Turtle trên AAPL điểm 1,18 (cao nhất); dual momentum NVDA có DD bootstrap −51% và −61% | **Chỉ dùng theo tình huống/regime** |
| 15 | Momentum cắt ngang (cross-sectional) | Rổ tài sản | — | Long mạnh nhất, short yếu nhất | — | — | — | — | Điểm cao hơn hẳn momentum đơn lẻ (vốn gần 0) | Giữ |
| 16 | Xếp hạng tốc độ giao dịch (breakout vs Bollinger fade) | NQ, ES, SPY, QQQ | M1 → D1 | Cùng luật, chỉ đổi tốc độ | | | | | Scalp M1 (khoảng 1.800 lệnh/năm): Sharpe gộp +0,575, ròng **−2,8**, **−15,9%/năm**, phí bằng 5,98 lần edge. Day trade M5: −0,613, khoảng −3%/năm. H1 giữ qua đêm: dương. Bán premium quyền chọn: 9,2%/năm, DD 29% (2020). Position trading: 9,2%/năm, DD khoảng 10%. **Swing D1: Sharpe khoảng 0,8, khoảng 8%/năm, DD 7%**. Giữ SPY: 16%/năm. Giữ QQQ: 20%/năm | Khung càng chậm càng tốt, đúng trên cả 20 giai đoạn con |
| 17 | Lọc ngày theo VIX/biến động | NQ, ES | Trong ngày | 408 hệ, 9 thước đo biến động | | | | | Không thước đo nào còn có ích sau khi tính slippage; phí lớn gấp khoảng 11 lần lợi ích của bộ lọc tốt nhất | **Loại** VIX làm bộ lọc vào/ra. **Giữ**: ngày biến động mạnh thì TP phải ≥ SL; giảm size ngày vol cao làm dao động giảm 42% |
| 18 | HMM regime 7 trạng thái + 7/8 xác nhận | BTC | H1 | Regime tăng và đạt ≥ 7/8 điều kiện (RSI < 90, momentum, vol, volume, ADX, giá, MACD) | không nêu (bản aggressive có trailing stop) | Thoát khi regime đổi sang giảm hoặc crash; cooldown 48 giờ | HMM | Đòn bẩy 2,5x | Backtest 2 năm: **+65%, DD 41%** (bản demo đầu); không có OOS | Chỉ là demo, **không có kiểm định** |
| 19 | Bot HMM theo regime vol (Alpaca) | Cổ phiếu/ETF | D1 / 5 phút | Phân bổ theo regime: vol thấp thì đầu tư 95% với đòn bẩy 1,25x | Mỗi lệnh rủi ro 1% | — | HMM 3–7 trạng thái, regime phải giữ ≥ 3 nến | Circuit breaker: lỗ 2%/ngày thì giảm nửa size; 3%/ngày đóng hết; 5%/tuần giảm nửa; DD 10% thì dừng hẳn | Walk-forward IS 252 ngày / OOS 6 tháng; không nêu kết quả | Khung xây dựng; chỉ paper |
| 20 | Macro gate + scanner + điểm Claude | S&P 500 | D1 | Điểm macro > 70: vào đủ vốn; 40–70: giảm size; < 40: đứng ngoài | — | — | VIX, cấu trúc kỳ hạn VIX, % cổ phiếu trên MA200, chênh lệch tín dụng, put/call, crowding | Trộn quant/Claude 60/40 | Không có số | Ý tưởng, chưa kiểm định |
| 21 | Bộ lọc thị trường của Astra | QQQ/vàng | D1 | VIX cao trong khi độ rộng thị trường > 50% thì giữ vàng 5 ngày | | | | | Là phần đẩy danh mục lên khoảng 33%/năm | Giữ (overlay) |
| 22 | Cặp đồng liên kết (hàng hóa, làm cho khách) | Hàng hóa | — | Z-score spread vượt ngưỡng | — | Thoát khi spread quay về | Kiểm tra đồng liên kết | — | Không có số | Ví dụ |
| 23 | EMA20/50 cắt nhau + lọc tin xấu bằng Jev | Cổ phiếu Mỹ | D1 | EMA20 cắt lên EMA50; bỏ nếu rủi ro tin xấu > 50% | | | | | 5,7% → 7,4% (theo Trade Rank, 1 giai đoạn) | Lọc tin có ích chút ít |
| 24 | Agent AI ra lệnh (n8n, politician, memecoin, GPT-5 đọc chart) | Cổ phiếu, crypto | M1/M15/H1 | LLM tự quyết định | LLM đưa ra | LLM đưa ra | | | Không có backtest | Không kiểm định được; tác giả tự nói không nên đưa ảnh chart cho LLM đọc |

**Danh mục cuối (khóa 3 giờ):** lõi 100% QQQ/vàng cộng các sleeve (bắt đáy RSI2, breakout, ...). Lock test: **khoảng 28,7–29%/năm, maxDD 13%**. Năm 2022 có đợt sụt khoảng 30% (con số khác nhau giữa các đoạn trong video). Sleeve tự tắt khi DD gấp 2 lần DD tệ nhất trong test; lõi tắt khi DD gấp 1,5 lần (DD tệ nhất của lõi khoảng 28%).

## 3. Kết quả đánh thật / paper

| Hệ | Thời gian | Tài khoản | Kết quả | DD / số lệnh / win rate | Khác backtest |
|---|---|---|---|---|---|
| Danh mục LEAPS + cổ phiếu vốn hóa nhỏ do Claude chọn (OSCR, NBIS, NOW, HIMS, MP, Nokia; call NOK $20 và NOW $120 hết hạn 15/1/2027) | Tháng 5 (≈ 30 ngày) | **Robinhood thật**, mở mới | **$66k → $169k (+155%)** | **Không nêu** | Tự nói **không backtest được**, có người quyết định, không có SL/TP cố định. Không có sao kê hay danh sách lệnh |
| Bot Alpaca (HMM, khóa 3 giờ) | Demo | **Paper** | Không có P&L; chỉ báo paper khớp backtest (33 test pass) | — | Chỉ kiểm tra kỹ thuật khớp lệnh |

Video không đưa ra kết quả live hay prop nào khác. Mọi video đều khuyên chạy paper 1–2 tháng trước khi dùng tiền thật.

## 4. Quy trình backtest và chống overfit

1. **Ghi trước** (pre-registration) ý tưởng, luật, tham số và tiêu chí đạt; đếm toàn bộ số biến thể đã thử.
2. **Dữ liệu:** dữ liệu ngày từ Yahoo; NQ/ES phút mua của vendor (16 năm, 11 triệu nến). Điều chỉnh dữ liệu tránh giá ảo (ví dụ cú giảm 50% do chia tách).
3. **Phí luôn bật:** khoảng 0,05% mỗi chiều cho ETF (khoảng 0,1% cả vòng); slippage 1 tick; slippage nặng hơn vào ngày biến động; tính phí vay khi dùng đòn bẩy. Nến chạm cả SL và TP thì tính là thua. Tín hiệu lấy ở giá đóng, vào lệnh ở giá mở nến sau.
4. **Chống nhìn trước:** dùng `lfilter` thay vì `filtfilt`; HMM chỉ chạy forward algorithm.
5. **Kiểm tra engine bằng edge cài sẵn:** gắn +1% vào dữ liệu giả; engine phải trả lại khoảng 0,6–1,2% mỗi lệnh.
6. **Quét diện rộng có kiểm soát:** mỗi phán đoán chủ quan thành một "nút vặn"; lấy mẫu ngẫu nhiên đều (25.000 hoặc 40.000 bản) cộng các bản phổ biến test theo tên.
7. **Phễu:** ≥ 100 lệnh → lãi sau phí → Sharpe OOS > 0,5 → DD < 35% → không có khoảng cách IS/OOS bất thường → hiệu chỉnh may rủi khi chạy nhiều phép thử → so với vào lệnh ngẫu nhiên hoặc lệnh ngược chiều → **chạy nguội trên tài sản thứ hai (NQ → ES)** → **holdout 2 năm khóa, chạy đúng 1 lần**.
8. **Walk-forward:** tối ưu 12 tháng, test mù 3 tháng (hoặc IS 252 ngày / OOS 6 tháng); chỉ ghép lợi nhuận OOS. Ví dụ: RSI+SMA lãi 199% IS nhưng khoảng 5% WF; Butterworth+ATR lãi trên 1.500% IS nhưng 7% WF.
9. **Bootstrap / Monte Carlo:** xáo thứ tự lệnh 500–1.000 lần; xem xác suất lỗ và DD trung bình của 5% kịch bản xấu nhất.
10. **Độ nhạy / plateau:** tham số lân cận (ví dụ MA 150/250 quanh 200, lookback 18/22 quanh 20) cũng phải tốt. Ví dụ: SMA cross trên SPY lãi 31% ở bản gốc, nhưng chỉnh tham số thì kết quả dao động từ +33% đến −9,5%, tức là hệ mong manh.
11. **Stress test giai đoạn xấu nhất (2000–2009):** loại được bản QQQ đòn bẩy (DD 85%).
12. **Nhất quán theo họ:** cả vùng tham số phải tốt, không chỉ một điểm.
13. **Cỡ mẫu:** 10 lệnh với win rate 55% thì khoảng tin cậy là 25–85%; 100 lệnh: 45–65%; 400 lệnh: 50–60%. Cần khoảng 800 lệnh mới biết edge thật.
14. **Danh mục:** thêm lần lượt từng sleeve làm tăng return/DD nhiều nhất; kiểm tra tương quan; giảm size ngày vol cao.
15. **Chạy thật:** paper ≥ 1–2 tháng, so paper với backtest; kill switch (DD sleeve gấp 2 lần DD test thì tắt); circuit breaker theo ngày/tuần; rủi ro 1%/lệnh (2% thì xác suất mất nửa tài khoản là 56%, 5% thì gần như chắc chắn).

## 5. Đề xuất cho brain2 (MT5/XM): chỉ đề xuất, chưa tạo job

Thứ tự ưu tiên:

1. **Bắt đáy RSI2 có lọc MA200** trên **US500, US100, US30, GER40** khung D1.
   - Luật: RSI(2) < 10 và giá đóng trên MA200 thì mua ở giá mở nến sau. SL 8%. Thoát khi đóng trên MA5 hoặc sau 10 nến.
   - Lưới độ nhạy: RSI < 5 / 10 / 15, MA thoát 3 / 5 / 10, MA lọc 150 / 200 / 250.
   - Lý do: đây là setup có số đẹp nhất trên chỉ số Mỹ; giữ lệnh ngắn (≤ 10 ngày) nên swap CFD của XM ít ảnh hưởng.
   - Cần tính swap long chỉ số của XM mỗi đêm.
2. **Xoay vòng xu hướng MA200: US100 ↔ GOLD** (D1).
   - Lý do: đây là lõi của anh ta (33,8%/năm holdout). Trên XM là CFD nên **swap giữ lâu ngày là chi phí lớn**: phải trừ swap long US100/GOLD thực tế trong backtest. Đặt kỳ vọng thấp hơn ETF.
   - Biến thể: thêm overlay "VIX cao + độ rộng > 50% thì giữ vàng 5 ngày" (cần dữ liệu VIX ngoài MT5, nên để sau).
3. **CHoCH H4, TP = 1R, SL sau swing, không sweep** trên forex cross (EURGBP, GBPCAD, AUDCAD, NZDCAD, GBPNZD...), XAUUSD và các chỉ số.
   - Lý do: hợp khung H4 brain2 đang làm, là setup đảo chiều/mean reversion, và giữ lệnh ngắn.
   - Cần định nghĩa swing bằng fractal N nến (lưới N = 2 / 3 / 5).
4. **Mean reversion trơn D1/H4** (RSI, Bollinger, Keltner) trên forex cross, quét như vòng 1 nhưng **bắt buộc chạy nguội**: tối ưu trên một cặp rồi chạy nguyên trên cặp tương tự (ví dụ AUDCAD → NZDCAD, EURGBP → EURCHF).
5. **ORB 30 phút đầu phiên Mỹ trên US100** (M5/M15). Ưu tiên thấp vì phí khung nhỏ ăn mạnh; chỉ test nếu spread XM thấp.
6. **Không nên dịch:** lọc ngày theo VIX, HMM BTC đòn bẩy, các agent LLM, ICT M1 tần suất cao (phí và spread XM sẽ ăn hết edge).

**Gợi ý thứ tự hàng đợi:** (1) RSI2-MA200 trên 4 chỉ số D1 → (2) CHoCH H4 trên khoảng 8 cross và vàng → (3) xoay US100/GOLD có swap → (4) mean reversion cross với bước chạy nguội.

Mọi job nên áp quy trình mục 4: khóa 2 năm cuối làm holdout, walk-forward, bootstrap 500 lần, lưới độ nhạy, tối thiểu 100 lệnh, Sharpe OOS > 0,5, và báo riêng số IS/OOS. Tiêu chí ĐẠT hiện tại (DD < 80%) lỏng hơn nhiều so với 35% của tác giả; nên báo thêm một cột theo ngưỡng này.
