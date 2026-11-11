# Nguồn live chart GEX, options flow và order flow

Ngày kiểm tra: 11/11/2026 (Asia/Saigon, UTC+7).  
Mục đích: lập danh sách trang công khai gần với [live.otldata.com](https://live.otldata.com/) để sau này có thể *canh chart như một người đang xem trang*, không cào API nội bộ, không vượt chặn.

Phương pháp: tìm trên web, mở/tải trang công khai (HTTP GET / WebFetch), đọc mô tả, bảng giá, FAQ và điều khoản khi tìm thấy dễ dàng. Không gọi API không có tài liệu, không bỏ qua `robots.txt` hay tường chống bot.

Kết quả HTTP ghi ở đây là lần thăm từ máy bot (mạng trung tâm dữ liệu), không phải từ máy nhà. Trang nào bị thử thách chống bot (ví dụ Barchart trả HTTP 202) được đánh dấu "chưa xác nhận nội dung đầy đủ", không kết luận là chết.

---

## 1. Cách dùng cho việc canh chart

Ưu tiên trang **miễn phí, không cần đăng nhập**, có sẵn lưới/mức GEX hoặc flow trên trang công khai, và khớp tài sản đang quan tâm: vàng (GC/GLD/GOLD), US500 (SPX/ES), US100 (NDX/NQ), US30 (YM/DJX — rất ít trang miễn phí), GER40 (DAX/ODAX), FX (chủ yếu COT hoặc snapshot EOD).

Hai lớp việc khác nhau:

- **Canh trực tiếp:** đọc mức gamma flip, call/put wall, net GEX, big trade quyền chọn, hoặc flow bất thường như đang ngồi xem chart.
- **Backtest:** chỉ dùng nguồn có lịch sử tải được hoặc API *chính thức có tài liệu*. Không suy ra lịch sử từ trang live.

Lưu ý chung: GEX công khai hầu hết là *ước lượng* từ open interest, giả định dealer đứng một phía. Công thức khác nhau giữa các trang nên số không khớp 1-1. Nhiều trang "GC" thực ra tính trên quyền chọn GLD rồi nhân tỉ lệ (~10,9) sang futures — khác sách quyền chọn trên futures GC/OG của CME.

---

## 2. Chính otldata

| Hạng mục | Kết quả kiểm tra 11/11/2026 |
|---|---|
| URL sống | [https://live.otldata.com/](https://live.otldata.com/) — HTTP 200, tiêu đề "Options Chart — Gold Options Grid" |
| `https://otldata.com/` và `www.otldata.com` | Lỗi SSL, không dùng được |
| Dữ liệu trên trang chủ | Lưới quyền chọn vàng: open interest / hợp đồng, bộ lọc phí quyền chọn (Min Premium), big trades (cửa sổ 8h / 24h / 1 ngày / tuần / tháng), sentiment theo strike, premium theo đáo hạn, 0DTE và weekly premium, net delta, **P8 — GEX**, **P9 — IV theo thời gian**, theta, tín hiệu LONG/SHORT Futures và CFD |
| Đường dẫn `/options/`, `/options/chart`, `/history`, `/api`, `/about`, `/contact`, `/docs`, `/terms`, `/privacy`, `/sitemap.xml` | HTTP 404 khi gọi trực tiếp (có thể là SPA chỉ chạy từ trang chủ) |
| Lịch sử / xuất file / API chính thức | **Không thấy.** Không có trang tải lịch sử, không có tài liệu API công khai |
| Liên hệ | Kênh Telegram công khai [t.me/AI_otl_Alert](https://t.me/AI_otl_Alert) ("OTL _ Data Alert Public", khoảng 722 thành viên lúc kiểm tra). Không thấy email, form liên hệ hay trang bán dữ liệu lịch sử |
| Đăng nhập | Trang chủ xem được không cần tài khoản (lúc kiểm tra) |
| `robots.txt` | `User-agent: *` / `Disallow: /` — **cấm crawler tự động toàn site** |
| Điều khoản | Không tìm thấy trang Terms. Chỉ có khuyến cáo rủi ro (kèm đoạn tiếng Việt trên footer) |

**Kết luận:** trang rất đúng việc canh vàng (lưới strike + GEX + IV + big trade). Không dùng được để backtest trừ khi chủ trang mở lịch sử/API, hoặc tự tính GEX từ dữ liệu quyền chọn OG/GC của Rithmic/Sierra rồi lưu dần. Khi canh hộ, chỉ xem như người dùng: không cào endpoint nội bộ, tôn trọng `robots.txt`, giữ nhịp chậm.

---

## 3. Shortlist xếp hạng (khoảng 8 trang đáng dùng trước)

### A. Để canh chart (miễn phí hoặc gần miễn phí)

1. **[WyckFlow GEX desk](https://wyckflow.com/gex)** — NQ, ES, GC/MGC. Không cần đăng nhập. Cập nhật khoảng 15–30 phút trong phiên Mỹ, nguồn quyền chọn trễ ~15 phút. Vàng suy từ GLD rồi đổi sang thang GC (× ~10,9). Có bảng "Recent sessions" trên trang (lịch sử ngắn trên web, chưa phải file backtest).
2. **[live.otldata.com](https://live.otldata.com/)** — Lưới quyền chọn vàng đầy đủ nhất trong nhóm miễn phí (GEX, IV, big trade, OI). Không có lịch sử. `robots.txt` cấm crawler.
3. **[GEX Metrix](https://www.gexmetrix.com/gex)** — SPX, NDX, SPY, QQQ, và mức quy ra giá ES/NQ. Không cần đăng nhập. Tính lại mỗi 15 phút từ dữ liệu trễ. **Không có vàng.** Điều khoản cấm scrape/bot (trừ crawler công cụ tìm kiếm được phép).
4. **[FlashAlpha GC GEX](https://flashalpha.com/futures/gc/gamma)** — Một trong số ít trang tính GEX *trên quyền chọn futures GC* (Black-76, nhân $100/điểm CME), không chỉ map từ GLD. Trang công khai lúc kiểm tra hiện net GEX, flip, call/put wall. API chính thức có tầng miễn phí (5 lệnh/ngày, trễ 15 phút, chủ yếu cổ phiếu đơn lẻ; futures CME nằm ở gói trả phí).
5. **[OptionCharts](https://optioncharts.io/options/SPY/gamma-exposure)** (đổi ticker thành GLD, QQQ, SPX…) — GEX theo strike, một đáo hạn miễn phí, dữ liệu trễ 15 phút, không bắt buộc tài khoản cho phần cơ bản. Flip/wall đa đáo hạn nằm sau gói trả phí. Có tải CSV trên một số chart; **không có API**.
6. **[Gamma Cockpit (DAX / GER40)](https://levels.gammacockpit.com/)** — Nguồn miễn phí hiếm cho GER40: OI, GEX, zero gamma, call/put wall từ dữ liệu thanh toán Eurex ODAX (ngày trước, ra mỗi sáng). Có lưu các ngày cũ trên site. Bản thời gian thực thuộc beta/trả phí.
7. **[tickstream GEX trễ 1 ngày](https://tick-stream.xyz/free-gex-levels-realtime)** — NQ, ES, vàng, bạc, dầu (map từ QQQ/SPY/GLD/SLV/USO) và vài cổ phiếu. Không đăng nhập. Làm mới ~90 giây nhưng **cố ý chậm một ngày**. Có chấm big option order trên chart. Phù hợp ôn lại phiên hơn là canh live.
8. **Flow quyền chọn miễn phí:** [InfoLib Unusual Options Flow](https://infolib.org/market-dashboard/unusual-options-flow) (không paywall, không bắt đăng nhập theo mô tả trang) hoặc [Xynth Flow](https://xynth.com/flow) (cần tài khoản miễn phí, có xuất CSV, API/tài khoản chịu điều khoản sàn). [Unusual Whales miễn phí](https://unusualwhales.com/live-options-flow/free) chỉ vài ticker hoặc toàn nền tảng trễ 2 phiên; có API chính thức khi trả phí.

**SpotGamma** ([biểu đồ SPX GEX miễn phí, cập nhật mỗi ngày](https://spotgamma.com/free-tools/spx-gamma-exposure/)) đáng bookmark nhưng chỉ SPX, một lần/ngày — kém hơn WyckFlow/GEX Metrix nếu cần canh trong phiên.

### B. Để backtest (có lịch sử hoặc API chính thức)

1. **[SqueezeMetrics DIX.csv](https://squeezemetrics.com/monitor/static/DIX.csv)** — File miễn phí, không cần đăng nhập. Cột `date,price,dix,gex`. Lúc tải: **3.907 dòng, từ 2011-05-02 đến 2026-11-10**. Đây là chuỗi GEX/DIX *của S&P 500*, không phải vàng hay từng strike. File `GEX.csv` riêng trả 404; dùng đúng `DIX.csv`. Gói live/API đầy đủ: 720 USD/tháng (mời, có API có tài liệu).
2. **[CFTC Commitments of Traders](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm)** — Nguồn chính thức, miễn phí, cập nhật hàng tuần. Có vàng, FX (6E, 6B…), chỉ số, nông sản. Tải được lịch sử dài. Bảng phụ: [realbacktesting COT](https://realbacktesting.com/tools/cot/).
3. **[tickstream GEX API](https://tick-stream.xyz/docs/gex)** — API có tài liệu. Gói lịch sử sâu hơn khoảng 69 USD/tháng (GEX Full, theo trang giá). Trang miễn phí chỉ trễ 1 ngày, không thay API.
4. **[FlashAlpha Historical API](https://flashalpha.com/api)** — Gói Alpha (khoảng 1.499 USD/tháng) quảng cáo replay từ **2017**. Tầng Free không có historical API. Điều khoản cấm scrape vượt mức gói và cấm tái phân phối.
5. **Chuỗi quyền chọn gốc để tự tính GEX:** [ThetaData](https://thetadata.net/), [Databento](https://databento.com/) (CME/COMEX, phù hợp GC/OG và ES/NQ). Đây là đường sạch nhất nếu muốn GEX vàng/futures đúng hợp đồng, có điểm-trong-thời-gian.
6. **[Unusual Whales API](https://unusualwhales.com/public-api)** — REST/WebSocket/MCP có tài liệu, dùng cho flow, dark pool, GEX khi đã mua gói API (tách với gói dashboard).
7. **Gamma Cockpit** — kho trang theo ngày cho DAX, đủ để dựng chuỗi mức hàng ngày thủ công; chưa thấy API xuất hàng loạt trên trang miễn phí.
8. **Dữ liệu nhà:** Sierra Chart (`.scid` / `.depth`) và Rithmic trên máy nhà — nguồn footprint, delta, big trade *thật* của futures, không thay thế được bằng web miễn phí.

---

## 4. Chi tiết từng nguồn (đã kiểm tra URL)

### 4.1. GEX / gamma / wall / flip

| Tên | URL | Tài sản / dữ liệu | Miễn phí hay trả phí | Tần suất / độ trễ | Lịch sử hoặc API | Đăng nhập | Ghi chú ToS / robots (nếu thấy) |
|---|---|---|---|---|---|---|---|
| OTL Data | https://live.otldata.com/ | Vàng: lưới OI, GEX, IV, big trade quyền chọn | Miễn phí xem trang | Live trên UI (chu kỳ "Next: 3 s" trên footer); không công bố nguồn/độ trễ chính thức | Không thấy | Không | `robots.txt` Disallow toàn site |
| WyckFlow | https://wyckflow.com/gex | NQ/NDX, ES/SPX, GC từ GLD | Desk web miễn phí, không đăng ký. Study MotiveWave là sản phẩm trả phí | 15–30 phút trong phiên London→NY; options trễ ~15 phút | Bảng phiên gần đây trên trang; lịch sử/API gắn với gói study | Không (desk) | Điều khoản chủ yếu cho add-on MotiveWave; cấm phá/overload dịch vụ |
| GEX Metrix | https://www.gexmetrix.com/gex | SPX, NDX, SPY, QQQ, ES, NQ. Không thấy GLD/GC | Trang levels miễn phí; có Plus/Pro | 15 phút, dữ liệu trễ | Trang có "historical snapshot" (trả phí?). Có nhắc API trong ToS | Không (trang free) | Cấm scrape, harvest, bot (trừ crawler tìm kiếm được phép) |
| tickstream | https://tick-stream.xyz/free-gex-levels-realtime | NQ, ES, GC, SI, CL (map ETF) + AAPL/NVDA… | Trang delayed miễn phí vĩnh viễn. Realtime/API trả phí (GEX Levels ~29, Greeks ~39, Full ~69 USD/tháng) | Trang free: chậm 1 ngày, làm mới ~90 giây | API chính thức, có gói lịch sử | Không (trang free) | Cấm tái phân phối raw feed; GEX derived cần add-on riêng nếu đem ra app khác |
| FlashAlpha | https://flashalpha.com/futures/gc/gamma và https://flashalpha.com/tools/gamma-exposure | GC options-on-futures; công cụ GEX đa ticker; ES/NQ/YM ở gói Growth+ | Xem trang + API Free 5 lệnh/ngày, trễ 15 phút, chủ yếu cổ phiếu. Basic ~79, Growth ~299, Alpha ~1.499 USD/tháng | Free: trễ 15 phút. Trả phí: live | Historical API từ 2017 (Alpha) | Free API cần email; trang GC xem được một phần | Cấm scrape vượt mức gói, cấm tái phân phối |
| SpotGamma | https://spotgamma.com/free-tools/spx-gamma-exposure/ | SPX (chart miễn phí). Hub trả phí: nhiều cổ phiếu, HIRO… | Chart SPX miễn phí. Essential khoảng 99 USD/tháng, Alpha khoảng 299 USD/tháng (cần đối chiếu lại khi mua) | Chart free: mỗi ngày | Lịch sử levels ngắn trên gói trả phí; không phải API-first | Không (chart free) | Dữ liệu thuộc sản phẩm trả phí, không dùng trang miễn phí như kho lịch sử |
| OptionCharts | https://optioncharts.io/options/SPY/gamma-exposure | Mọi ticker quyền chọn Mỹ (SPY, QQQ, GLD, SPX…) | Free: 1 đáo hạn, trễ 15 phút. Premium ~20 USD/tháng (năm). Ultimate realtime ~35 USD/tháng | 15 phút (Free/Premium); realtime ở Ultimate | Tải CSV một số chart; **không có API** | Không bắt buộc cho bản cơ bản | Không thấy lệnh cấm riêng khi đọc FAQ; không có API nên không có kênh chính thức để tự động hóa |
| QuantWheel | https://quantwheel.com/tools/gex-heatmap/gld | Heatmap GEX GLD (và ticker khác) | Có hạn mức miễn phí (lúc trang ghi 2 lượt/ngày) | Snapshot (ví dụ dữ liệu "as of Nov 6, 2026" lúc kiểm tra — không phải tick live) | Không thấy API/xuất lịch sử dài | Không | Chưa tìm thấy ToS chi tiết trên trang công cụ |
| FederGEX | https://www.federgex.com/ | Options: SPX, SPY, NDX, QQQ, GLD, USO. Futures DOM: ES, NQ, GC, CL | Free: kênh Telegram, GEX mỗi 15 phút, indicator NT8 cộng đồng. Pro: dashboard options (khoảng 16–25 EUR/tháng lúc ra mắt). Elite: DOM futures + API | Options chỉ trong RTH 09:30–16:00 New York. Free Telegram 15 phút, không realtime | API Elite có tài liệu, giới hạn tốc độ. Dashboard **không backfill** phiên đã qua | Cần tài khoản cho dashboard | FAQ dẫn Terms of Service; URL `/terms` trả 404 lúc kiểm tra |
| MenthorQ | https://menthorq.com/pricing/ và https://menthorq.com/landing/start-free/ | 1000+ ticker, có futures ES, NQ, GC, CL… GEX/gamma levels trên quyền chọn futures (điểm mạnh) | Free: dữ liệu trễ, mẫu mô hình, cần email. Premium 59 rồi 129 USD/tháng; Pro cao hơn | Free: delayed. Premium: realtime (futures realtime có add-on, và chỉ trong nền tảng) | Lịch sử trong gói trả phí; không dùng undocumented API | Có (cả free) | **Cấm bot, scraper, browser automation, API không tài liệu** nếu chưa có giấy phép viết |
| TholviGex | https://tholvitrader.com/tholvigex-web | ES, NQ, Gold (GLD); 0DTE / 1DTE / 90D; thêm tab COT, vol… | Trang marketing nói "mở tab là xem". URL `/tholvigex/live` lúc kiểm tra mở trang sản phẩm licence NinjaTrader/ATAS (trọn đời). **Chưa xác nhận bàn web miễn phí thật sự** | Quảng cáo live trong phiên | Không rõ kênh lịch sử web | Không rõ | Coi như sản phẩm desktop/trả phí cho đến khi xác nhận được UI web mở không cần mua |
| GEXmon | https://gexmon.app/ | SPX, ES, NDX, NQ, GC (GLD→GC) | Thử 3 ngày không cần thẻ; sau đó Pro khoảng 14,99 USD/tháng (hoặc ~149,99 USD/năm, giá founding) | Quảng cáo live trong phiên | Không thấy API/lịch sử dài trên trang marketing | Có | Có trang Terms |
| GEXBot | https://gexbot.com/ | Chủ yếu chỉ số và mã thanh khoản (khoảng 50+) | Trả phí (Classic khoảng 50 USD/tháng theo bài so sánh 2026) | Quảng cáo tính lại từng giây | Archive khoảng 90 ngày (theo bài so sánh, chưa mở được từ đây) | Có | Không đi sâu ToS trong lượt này |
| Robinflow | https://robinflow.io/gex | GEX heatmap đa ticker Mỹ | Có trial; gói rẻ (khoảng 19–39 USD/tháng theo blog của chính họ). Free: trang bị trễ vài phiên | Hourly với mã nóng (gói trả phí) | Phù hợp nghiên cứu hơn canh tức thì | Có thể cần tài khoản | — |
| Gamma Cockpit | https://levels.gammacockpit.com/ và https://gammacockpit.com/ | **DAX / GER40** từ ODAX Eurex, gồm cả quyền chọn ngày (ODAP) | Sơ đồ OI và gamma levels hàng ngày **miễn phí, không đăng nhập**. Intraday thuộc beta | Free: dữ liệu thanh toán ngày trước, ra buổi sáng | Nhiều trang theo ngày trên site (khoảng từ 07/2026 trở lại, lúc kiểm tra) | Không (bản ngày) | Tính trên OI Eurex, không phải ETF DAX niêm yết Mỹ |

**Barchart** có trang GEX theo ticker (ví dụ GLD, SPY) nhưng từ mạng bot trả HTTP 202 (thử thách chống bot), nên **chưa xác nhận nội dung lần này**. CSV thường nằm ở gói Premier. Không xếp vào shortlist cho đến khi mở được bằng trình duyệt.

**Volland** (`volland.io`) lúc kiểm tra chỉ còn trang mặc định của domain — loại khỏi danh sách. **GammaLens.com** đang rao bán tên miền — loại.

### 4.2. Options flow / big trade quyền chọn / dark pool

| Tên | URL | Dữ liệu | Miễn phí hay trả phí | Trễ | Lịch sử / API | Đăng nhập | ToS (nếu thấy) |
|---|---|---|---|---|---|---|---|
| InfoLib | https://infolib.org/market-dashboard/unusual-options-flow | Unusual options: print, Vol/OI, lọc, chart volume vs giá | Quảng cáo miễn phí, không paywall, không signup | Trang nói realtime; nếu trễ sẽ ghi rõ | Không thấy API chính thức | Không | Không tìm thấy `/terms` (404) |
| Xynth | https://xynth.com/flow | Toàn bộ print quyền chọn Mỹ, lọc sâu, sweep/block | Miễn phí với tài khoản (không cần thẻ, theo trang) | Realtime (theo trang; tài khoản để tuân licence dữ liệu sàn) | Lật lịch sử, **xuất CSV** | Có (free) | Có Terms; dữ liệu chịu điều khoản sàn |
| Unusual Whales | https://unusualwhales.com/live-options-flow/free , https://unusualwhales.com/dark-pool-flow , https://unusualwhales.com/pricing | Flow, GEX heatmap, dark pool, SPX MM exposure | Free: cả nền tảng trễ **2 phiên** (trang flow "free" từng giới hạn vài ticker, giá 15 phút). Basic ~50, Pro ~75, Max ~120 USD/tháng | Free trễ 2 ngày; trả phí realtime (SPX exposure 10 phút, Max 1 phút) | Tải daily options/dark pool ở gói trả phí. **API chính thức** (gói riêng) | Free cần tài khoản để dùng đủ dashboard | Dùng API chính thức, không cào site |
| Options Sight | https://www.optionssight.com/ | Quét 1 ticker miễn phí; live tape | Scan không cần tài khoản. Live realtime ở Pro; free trễ 15 phút | 15 phút (free) | Không rõ API | Không (scan) | — |
| Cheddar Flow | https://cheddarflow.com/ | Flow + GEX | Trial 7 ngày; Pro khoảng 99 USD/tháng | Realtime (trả phí) | Không đi sâu | Có | — |
| FlowAlgo | https://flowalgo.com/ | Options flow, dark pool | Trả phí | Realtime (trả phí) | — | Có | — |
| Tradytics | https://tradytics.com/ | Flow, dark pool, dealer gamma, AI | Có tầng free hạn chế (theo bài so sánh: block phiên trước) | Tùy gói | — | Có | — |
| FlowWatch | https://flowwatch.live/ | Flow "whale", mô phỏng | Trial khoảng 7 ngày rồi trả phí | — | Có mục historical trong marketing | Có | Thiên về học, kém ưu tiên |

### 4.3. Order flow futures / footprint / delta / thanh lý

Web miễn phí **hầu như không** có footprint hay cumulative delta đúng nghĩa của CME (cần book L2/L3). Phần này nằm trên phần mềm desktop và data feed nhà (Sierra + Rithmic), đúng hướng đã bàn.

| Tên | URL | Ghi chú |
|---|---|---|
| Bookmap | https://bookmap.com/ | Heatmap thanh khoản, iceberg, dark pool overlay. Phần mềm trả phí + phí data CME. Không phải trang web để canh hộ. |
| ATAS | https://atas.net/ | Footprint, cluster, delta. Desktop trả phí + data. |
| Datrena | https://datrena.com/Home | Trang mở được (200) nhưng nội dung rất mỏng; chưa đủ để xếp vào shortlist. |
| FederGEX Elite | https://www.federgex.com/ | DOM heatmap, bubbles (khớp lệnh), VWAP trên ES/NQ/GC/CL — gần nhất với "order flow web", nhưng trả phí và không backfill. |
| CoinGlass Liquidation Heatmap | https://www.coinglass.com/pro/futures/LiquidationHeatMap | Heatmap thanh lý **crypto**. Có symbol XAU nhưng đó là vàng CFD/crypto, **không phải GC COMEX**. Bản miễn phí thường chỉ BTC/ETH; XAU hay nằm sau Prime. Hữu ích nếu canh vàng crypto, không thay GEX CME. |
| Hyblock | https://hyblockcapital.com/ | Thanh lý / positioning crypto, trả phí. |
| GEX Monitor (crypto) | https://www.gexmonitor.com/ | GEX + whale radar **BTC/ETH/SOL trên Deribit**, không phải ES/GC. API đang mở dần. |

### 4.4. FX, US30, định vị tuần (COT)

| Tên | URL | Ghi chú |
|---|---|---|
| CrossVol EUR/USD GEX | https://crossvol.com/en/markets/eurusd/gamma-exposure-today/ | Snapshot công khai (lúc kiểm tra: cập nhật 2026-11-10 17:00 UTC): max pain, pin, từ quyền chọn euro futures. Live intraday nằm ở Terminal trả phí. Có trang cross-asset. Đây là nguồn FX GEX hiếm thấy ở tầng miễn phí, nhưng là EOD chứ không phải lưới live như otldata. |
| CFTC COT | https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm | Chính thức, miễn phí, hàng tuần. Vàng, FX majors, ES, dầu… Tải lịch sử được. Rất hợp lớp lọc xu hướng H4/D1, không phải điểm vào M1. |
| Realbacktesting COT | https://realbacktesting.com/tools/cot/ | Dashboard COT miễn phí, cập nhật tuần. |
| CBOE delayed SPX quotes | https://www.cboe.com/delayed_quotes/spx/options_quotes | Chuỗi quyền chọn SPX trễ của sàn. Không vẽ GEX sẵn, nhưng là nguồn gốc để tự tính. |
| US30 / YM / DJX | — | FlashAlpha ghi YM ở gói Growth+. MenthorQ có thể có futures Dow trong gói trả phí. **Không thấy trang GEX miễn phí chất lượng cho US30.** |

---

## 5. Lỗ hổng cần nhớ khi thiết kế hệ

- **Vàng:** otldata là lưới live gần nhất. WyckFlow / tickstream / FederGEX / QuantWheel phần lớn đi từ **GLD**. FlashAlpha và MenthorQ (trả phí) mới nhấn mạnh **options-on-futures GC**. Nếu vào lệnh GOLD trên XM, nên ghi rõ nguồn là GLD-map hay GC/OG thật.
- **GER40:** gần như chỉ Gamma Cockpit (Eurex ODAX) ở nhóm miễn phí.
- **FX:** không có otldata-kiểu grid miễn phí cho EURUSD/GBPUSD. CrossVol (snapshot) + CFTC COT là điểm bắt đầu. Quyền chọn FX/futures 6E/6B trên Rithmic, nếu gói có, vẫn là đường tự tính sạch hơn.
- **Footprint / big trade futures / cumulative delta:** không có web miễn phí đáng tin. Giữ Sierra + Rithmic làm nguồn sự thật; các trang trên chỉ thêm lớp GEX/flow quyền chọn.
- **Lịch sử GEX vàng dài:** hiện **không có file miễn phí** tương đương `DIX.csv`. Muốn backtest đúng vàng thì tự tính từ lịch sử quyền chọn GLD hoặc GC/OG (Databento / ThetaData / dữ liệu nhà), rồi lưu từ hôm nay nếu chỉ có live.

---

## 6. Quy tắc khi canh hộ (để lần sau làm đúng)

1. Chỉ đọc những gì trang **hiển thị công khai** trên UI, giống người xem chart. Không đảo API nội bộ, không giả vân tay, không đổi IP để tránh chặn.
2. Tôn trọng `robots.txt` và điều khoản: otldata cấm crawler; GEX Metrix và MenthorQ cấm scrape/bot; FlashAlpha và tickstream cấm lấy vượt gói và tái phân phối. Ưu tiên API chính thức khi đã có gói.
3. Giữ nhịp chậm (không mở dồn nhiều tab/phút). Một số site (Cloudflare, Barchart) đã chặn hoặc thử thách từ mạng bot.
4. Ghi rõ thời điểm, múi giờ Asia/Saigon, ticker, nguồn (GLD hay GC), và đây chỉ là ngữ cảnh vị thế — không phải tín hiệu vào lệnh.
5. Số liệu trên trang live không đủ để kết luận "đạt" theo tiêu chí CAGR/DD. Mọi bộ lọc GEX/flow vẫn phải chọn trên đoạn train, walk-forward, và so với vào lệnh ngẫu nhiên như quy trình hiện tại.

---

## 7. Việc nên làm tiếp (khi có máy hoặc phiên mới)

- Mở bằng trình duyệt (không phải HTTP thuần) các trang bị 202 hoặc SPA: Barchart GEX, TholviGex live, dashboard FederGEX/MenthorQ nếu Anh muốn dùng tầng free có tài khoản.
- Khi máy nhà bật: kiểm kê dữ liệu Sierra/Rithmic (mã, ngày bắt đầu, có bid/ask volume, có depth, có options OG/GC không) — đây vẫn là nút thắt của lớp footprint.
- Nếu cần lịch sử GEX vàng: bắt đầu ghi log thủ công/chính thức từ nguồn được phép, hoặc mua chuỗi lịch sử CME/OPRA rồi tự tính; đừng chờ otldata mở kho.
