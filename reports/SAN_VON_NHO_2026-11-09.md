# Sàn & hình thức đầu tư vốn nhỏ cho nhà đầu tư ở Việt Nam

**Ngày:** 09/11/2026 (giờ Bangkok, UTC+7) · **Phạm vi:** nghiên cứu web và tính chi phí. Không mở tài khoản, không gửi tin, không commit. · **Bối cảnh:** hiện chỉ dùng Fmarket. Muốn chi phí thấp hơn CFD FX của XM, chịu được buy&hold, cho phép đi lệnh nhỏ.

> **Đây không phải tư vấn đầu tư hay tư vấn pháp lý.** Mọi phí đều đọc từ trang chính thức ngày 09/11/2026 và có thể thay đổi. Dòng nào ghi **chưa xác minh** là chưa đọc được trên nguồn chính thức. Không có số nào được bịa ra.

## 1. Tóm tắt nhanh

- **CFD của XM tốn tiền chủ yếu vì swap, không phải vì spread.** Swap qua đêm XM đo ngày 06/10/2026, quy theo giá hiện tại: US100 ≈5.98%/năm, vàng ≈7.29%/năm. Nếu chạy hệ xoay vòng MA200 (≈81% thời gian giữ US100) thì riêng swap đã tốn khoảng **6,2% vốn/năm**. Spread chỉ cộng thêm khoảng 0,03%/năm. Đây là lý do backtest dot3 rớt từ CAGR 21,8% (không phí) xuống 4,6% (phí XM).
- **Phương án rẻ nhất về chi phí: cổ phiếu/ETF thật, mua lẻ (fractional).** Ví dụ QQQ cho chân Nasdaq-100, GLD cho chân vàng. Cách này không có swap, chỉ mất phí quản lý quỹ (0,18–0,40%/năm) và vài USD phí lệnh. Với vốn $2.000, tổng chi phí khoảng 0,6%/năm, so với khoảng 6,3%/năm khi dùng XM CFD.
- **Rủi ro pháp lý cần biết (trình bày trung tính).** Khoản 1 Điều 5 Nghị định 135/2015/NĐ-CP quy định: *"Nhà đầu tư là cá nhân có quốc tịch Việt Nam chỉ được thực hiện đầu tư gián tiếp ra nước ngoài dưới hình thức tham gia chương trình thưởng cổ phiếu phát hành ở nước ngoài."* Văn bản được trích lại qua [Thư viện Pháp luật, 25/06/2025](https://thuvienphapluat.vn/phap-luat/chi-duoc-thuc-hien-dau-tu-gian-tiep-ra-nuoc-ngoai-duoi-hinh-thuc-nao-doi-voi-nha-dau-tu-la-ca-nhan--540484-223165.html). Mình **chưa xác minh** tình trạng hiệu lực hiện hành trên Công báo. Như vậy, mua chứng khoán hoặc ETF nước ngoài qua sàn nước ngoài **không nằm trong** hình thức mà điều khoản này cho phép. Với tài sản mã hóa, Nghị quyết 05/2025/NQ-CP quy định giao dịch qua tổ chức không được Bộ Tài chính cấp phép có thể bị xử phạt sau thời hạn chuyển tiếp. Nên hỏi luật sư hoặc ngân hàng trước khi chuyển tiền ra nước ngoài.
- **Kênh trong nước hợp lệ rõ ràng nhưng không làm được đúng chiến lược US100/vàng:** Fmarket, ETF VN30 (E1VFVN30), phái sinh VN30F, vàng SJC hoặc vàng nhẫn.

## 2. Xếp hạng đề xuất

| # | Lựa chọn | Vì sao | Điểm yếu chính |
|---|---|---|---|
| 1 | **IBKR Pro, ETF thật mua lẻ (QQQ/GLD hoặc tương đương)** | Có Việt Nam trong danh sách quốc gia mở tài khoản. Không yêu cầu vốn tối thiểu. Mua lẻ từ 1 USD. Phí $1/lệnh. Không swap. Có API (TWS/REST/FIX). Do SEC/FINRA cùng nhiều cơ quan khác quản lý. | Mua bán cổ phiếu ngoài nước vướng NĐ 135/2015 (mục 1). Phải chuyển khoản quốc tế, phí ngân hàng chưa xác minh. Mỹ khấu trừ thuế cổ tức (mức áp cho người VN chưa xác minh). Chỉ giao dịch trong phiên Mỹ. |
| 2 | **eToro, ETF thật** | Hoa hồng ETF $0, không phí qua đêm với vị thế thật, có thể mua bằng số tiền nhỏ. Việt Nam có trong danh sách chọn nước ở trang phí. | Phí rút $5 (tối thiểu rút $30). Phí đổi VND/USD chưa xác minh. eToro ghi rằng một số lệnh BUY không đòn bẩy *có thể được thực hiện dưới dạng CFD*. Pháp nhân phục vụ VN có thể là eToro (Seychelles), chưa xác minh trực tiếp. Không có API giao dịch công khai cho cá nhân (chưa xác minh). Vướng NĐ 135 giống mục 1. |
| 3 | **Exness, CFD swap-free (Standard hoặc Standard Cent)** | Gần với cách anh đang làm nhất (MT5, lệnh 0,01 lot, Standard Cent nạp tối thiểu $10). Exness ghi chỉ số và XAUUSD thuộc nhóm swap-free mặc định, nên về lý thuyết bỏ được khoản chi phí lớn nhất của XM. | Exness ghi rõ trạng thái swap-free **có thể bị thu hồi** nếu thường xuyên giữ khối lượng lớn qua đêm, đúng kiểu giữ nhiều tuần. Spread Exness chưa xác minh. Giấy phép offshore (FSA Seychelles và các nơi khác). Tư cách nhận khách VN chưa xác minh trực tiếp (VN không có trong danh sách loại trừ trên trang liên hệ tiếng Việt). |
| 4 | **Kênh trong nước: Fmarket / ETF E1VFVN30 qua DragonX–KIS / VN30F** | Hợp pháp rõ ràng, nạp rút bằng VND, mua lẻ được (ETF lô nhỏ, CCQ mở theo số tiền). | Không phải US100/vàng. VN30F mỗi hợp đồng lớn so với vốn $500. Phí quản lý tài sản ký quỹ SSI tối thiểu 100.000 đ/tháng. |
| 5 | **Binance PAXG (chỉ cho chân vàng)** | Spot 0,1%/chiều, mua lẻ được, Việt Nam không có trong danh sách quốc gia bị cấm của Binance (bản 05/01/2026). | Không có chân Nasdaq tương đương được quản lý. Phải để tiền ở stablecoin khi không giữ vàng. NQ 05/2025: sàn không được Bộ Tài chính cấp phép có rủi ro bị xử phạt. Phí lưu trữ PAXG chưa xác minh. Perpetual có funding chưa xác minh (fetch timeout). |
| – | Micro futures (MNQ/MES/MGC) | Phí sàn rẻ (IBKR micro $0,25/chiều, tổng mô hình ≈$0,61). | **Loại vì quá lớn so với vốn nhỏ.** Một hợp đồng MNQ ≈ $61,753 danh nghĩa, MGC ≈ $41,952, 1OZ ≈ $4,195. Với vốn $500–2.000, đòn bẩy sẽ ×20–120. Futures còn có chi phí roll (carry) ngầm. |

## 3. Chi phí ước tính mỗi năm: hệ xoay vòng US100/vàng MA200

Giả định lấy từ dot3/dot4 (MA200 cố định, dữ liệu 2018 đến 10/2026):

- Giữ US100 **81%** thời gian, vàng 19%.
- **3,42 lần đổi/năm**, tức ≈6,84 chân lệnh/năm.
- Giá proxy ngày 08/10/2026: US100 30.877, vàng 4.195.

Bảng chưa gồm thuế, phí chuyển tiền quốc tế và chênh lệch tỷ giá (đều **chưa xác minh**).

| Lựa chọn | $500: giao dịch | $500: giữ | $500: tổng/năm | $2.000: giao dịch | $2.000: giữ | $2.000: tổng/năm | Ghi chú |
|---|---|---|---|---|---|---|---|
| XM CFD (Cash#/GOLDmicro) | $0.17 | $31.16 | **$31.33** (6.27%) | $0.68 | $124.62 | **$125.30** (6.27%) | swap đo 06/10/2026; spread p90 |
| IBKR Pro Fixed – QQQ/GLD lẻ | $7.22 | $1.11 | **$8.33** (1.67%) | $8.35 | $4.44 | **$12.79** (0.64%) | $1/lệnh ×6,84 chân + SEC + giả định 1bp spread/chân |
| eToro – ETF thật QQQ/GLD | $0.34 | $1.11 | **$1.45** (0.29%) | $1.37 | $4.44 | **$5.80** (0.29%) | hoa hồng ETF 0; chưa gồm phí đổi tiền nạp & $5/lần rút |
| Exness swap-free (nếu giữ được trạng thái) | $0.17 | $0.00 | **$0.17** (0.03%) | $0.68 | $0.00 | **$0.68** (0.03%) | spread Exness CHƯA XÁC MINH → dùng spread XM làm proxy |
| Exness nếu mất swap-free (stress) | $0.17 | $31.16 | **$31.33** (6.27%) | $0.68 | $124.62 | **$125.30** (6.27%) | giả định swap ngang XM, chưa xác minh biểu swap Exness |

Cách đọc bảng:

- **XM CFD:** "giữ" là swap long (US100Cash# −5,06 điểm/đêm, GOLD −0,8383/đêm, tính 365 đêm). Spread lấy p90 (US100 2,8; GOLDmicro 0,57).
- **IBKR:** phí lệnh mua lẻ theo chú thích biểu phí là $1/lệnh, trần 1% giá trị lệnh. Với lệnh $500–2.000 thì phí là $1. SEC fee 0,0000206 × giá trị bán. "Giữ" là phí quản lý quỹ QQQ 0,18% và GLD 0,40% theo tỷ trọng thời gian. Spread ETF giả định 1bp mỗi chân. Ở mức $500, khoản $1/lệnh chiếm khoảng 1,4%/năm. Nếu dùng biểu Tiered ($0,35 tối thiểu) thì khoản này còn khoảng 1/3.
- **eToro:** hoa hồng ETF 0, không phí qua đêm, không phí lưu ký. Chưa tính phí rút $5/lần và phí đổi tiền khi nạp (chưa xác minh).
- **Exness:** swap = 0 *nếu* giữ được trạng thái swap-free. Dòng "stress" giả định bị thu hồi và chịu swap ngang XM. Biểu swap thật của Exness chưa xác minh.
- **Hiệu ứng lên lợi nhuận (dot4):** chạy hệ trên ETF proxy với phí IBKR cho CAGR 21,25% (DD 30,9%, Sharpe 1,11). Cùng hệ đó với phí XM CFD chỉ còn 4,57% (DD 45,3%).

## 4. So sánh theo 5 nhóm

### 4.1 Cổ phiếu/ETF Mỹ mua lẻ

| Sàn | VN mở được? | Vốn tối thiểu / lệnh nhỏ nhất | Phí giao dịch | Chi phí giữ | Nạp/rút | API | Cấp phép |
|---|---|---|---|---|---|---|---|
| [IBKR](https://www.interactivebrokers.com/en/trading/fractional-trading.php) | **Có:** Vietnam nằm trong danh sách quốc gia của IBKR (đọc 09/11/2026) | $0 (Pro) / mua lẻ từ $1, hơn 10.500 mã | Fixed $0,005/cổ, tối thiểu $1, tối đa 1% · Tiered $0,0035, tối thiểu $0,35 · SEC 0,0000206 × giá trị bán · TAF miễn 01/10–31/12/2026 | Chỉ phí quản lý quỹ ETF | Chuyển khoản quốc tế (phí ngân hàng VN chưa xác minh) | TWS / Client Portal REST / FIX | SEC/FINRA (Mỹ) và các nơi khác |
| [eToro](https://www.etoro.com/trading/fees/) | Có Vietnam trong ô chọn nước của trang phí. Điều kiện mở tài khoản **chưa xác minh** | Chưa xác minh | ETF $0; cổ phiếu $1–2/chiều; CFD 0,15% | ETF/cổ phiếu thật: không phí qua đêm, không phí lưu ký | Rút $5, tối thiểu $30; phí đổi tiền chưa xác minh | Không có API công khai (chưa xác minh) | eToro (Seychelles) FSAS SD076 và các pháp nhân khác |
| Saxo | **Không:** VN không có trong danh sách quốc gia (dot4) | – | Classic US ETF 0,08% | – | – | OpenAPI | – |
| moomoo | **Không:** VN không có trong danh sách (dot4) | – | – | – | – | OpenAPI | – |
| Tiger | **Chưa xác minh** (trang OpenAPI timeout) | – | – | – | – | – | – |
| Stock CFD Exness/XM | Có (đang dùng XM) | 0,01 lot | Spread/hoa hồng | **Có swap** (Exness ghi cổ phiếu không thuộc nhóm swap-free) | MT5 | MT5 | Offshore |

### 4.2 Micro futures

| Kênh | VN mở được? | Phí | Ghi chú |
|---|---|---|---|
| IBKR (MNQ/MES/MGC) | Có (cùng tài khoản IBKR) | $0,25/chiều phí môi giới. Tổng mô hình MNQ/MES ≈$0,61, MGC ≈$0,96 | Danh nghĩa quá lớn cho vốn $500–2.000 (mục 2). Futures carry 2–5% làm CAGR giảm còn 19,3–15,8% (dot4) |
| AMP Futures | **Chưa xác minh** (trang danh sách quốc gia trả 403) | Chưa xác minh | Nạp tối thiểu $100 (dot4) |
| NinjaTrader | **Chưa xác minh** | Gói free: micro $0,39/chiều | – |
| eToro futures (beta) | Chưa xác minh với VN | Micro $0,75 + $0,77 phí sàn. 1-Ounce Gold $0,75 + $0,57 | Không phí qua đêm với micro futures |

### 4.3 Vàng/cổ phiếu token hóa và perpetual

| Kênh | VN mở được? | Phí | Chi phí giữ | Pháp lý VN |
|---|---|---|---|---|
| [Binance spot PAXG](https://www.binance.com/en/fee/trading) | VN không có trong [danh sách quốc gia bị cấm, bản 05/01/2026](https://bin.bnbstatic.com/static/cms/cg08ou2ak0tn7mcplvfg/file/2dead3dd5d9bccb32694e2f0fe5c7f2c6b583e7a6f851296edef7088340e6df5.pdf). Điều khoản 2.1(f) loại trừ những nơi việc sử dụng là bất hợp pháp | 0,1%/0,1% (giảm 25% nếu trả phí bằng BNB). PAXG/U maker 0 từ 05/03/2026 (lấy từ trích dẫn tìm kiếm; WebFetch timeout) | Phí lưu trữ PAXG/XAUT **chưa xác minh** | [NQ 05/2025/NQ-CP](https://xaydungchinhsach.chinhphu.vn/toan-van-nghi-quyet-so-5-2025-nq-cp-ve-trien-khai-thi-diem-thi-truong-tai-san-ma-hoa-tai-viet-nam-119250909184045221.htm), Điều 7.2: sau 6 tháng kể từ khi tổ chức đầu tiên được cấp phép, giao dịch qua tổ chức không được cấp phép có thể bị xử phạt. Hiện đã có tổ chức nào được cấp phép chưa: **chưa xác minh** |
| OKX / Bybit | **Chưa xác minh** | Chưa xác minh | Chưa xác minh | Như trên |
| Perpetual (vàng, chỉ số) | – | – | Funding trả mỗi 8 giờ (hoặc theo kỳ) **chính là chi phí giữ lệnh**. Lãi suất funding **chưa xác minh** | Như trên |

### 4.4 CFD swap-free / cent

| Sàn | VN | Lệnh nhỏ | Swap | Cấp phép |
|---|---|---|---|---|
| [Exness](https://www.exness.com/vi/standard-accounts/) | Có trang tiếng Việt chính thức. VN không có trong danh sách loại trừ trên [trang liên hệ](https://www.exness.com/vi/contact/). Tư cách nhận khách VN **chưa xác minh trực tiếp** | Standard Cent: nạp tối thiểu $10, lot 0,01 (theo trích dẫn tìm kiếm trang Exness) | [Swap-free mặc định](https://get.exness.help/hc/en-us/articles/4402341895570-Swap-free-status) cho majors, XAUUSD, chỉ số, crypto. Cổ phiếu vẫn bị tính swap. **Có thể bị thu hồi** nếu thường xuyên giữ khối lượng lớn qua đêm | [FSA Seychelles SD025, CBCS…](https://www.exness.com/regulation/) |
| [Pepperstone](https://pepperstone.com/vi-vn/) | Có trang tiếng Việt và hotline 1800 4929 | Chưa xác minh | Có swap (Islamic chưa xác minh với VN) | Pháp nhân Bahamas, đòn bẩy bán lẻ 200:1 |
| [IC Markets](https://www.icmarkets.com/global/vn/help-resources/help-centre) | Có trung tâm trợ giúp tiếng Việt | Chưa xác minh | Chưa xác minh | Chưa xác minh |

### 4.5 Kênh trong nước

| Kênh | Lệnh nhỏ / vốn | Phí | Chi phí giữ | Ghi chú |
|---|---|---|---|---|
| [Fmarket, ví dụ DCDS](https://fmarket.vn/quy/DCDS) | Mua theo số tiền | Mua 0%. Bán 1,5% (<12 tháng), 0,5% (12–24 tháng), 0% (≥24 tháng) | Phí quản lý nằm trong NAV (mức cụ thể chưa xác minh) | Phù hợp buy&hold; bán sớm thì phí cao |
| [ETF E1VFVN30 / FUEVFVND qua DragonX–KIS](https://dautu.dragoncapital.com.vn/product/etf) | NAV E1VFVN30 ≈33.091 đ/ccq | 0,03%/lệnh (DragonX miễn phí môi giới, chỉ trả phí sở). Thuế bán 0,1% theo luật chung | Phí quản lý 0,65%/năm (MIDCAP tới 0,80%) | Thanh toán T+2 |
| [Phái sinh VN30F (SSI)](https://www.ssi.com.vn/khach-hang-ca-nhan/bieu-phi/bieu-gia-dich-vu-giao-dich-chu-dong) | 1 hợp đồng, ký quỹ ban đầu ≈17% (nguồn thứ cấp, **chưa xác minh**) | 2.000 đ/HĐ online + 2.700 HNX + 2.550 VSDC | Quản lý TS ký quỹ 0,0024%/tháng, **tối thiểu 100.000 đ/tháng** (≈1,2 triệu đ/năm). Roll mỗi tháng | Với vốn nhỏ, phí tối thiểu hằng tháng chiếm tỷ trọng lớn |
| Vàng SJC / nhẫn | Theo chỉ/lượng | Chênh mua–bán **chưa xác minh** (bảng giá SJC trả về trống) | Không có, ngoài chi phí cất giữ | Không có lệnh tự động hay API |

## 5. Lưu ý pháp lý và thuế (trung tính)

1. **Đầu tư gián tiếp ra nước ngoài:** NĐ 135/2015, Điều 5.1 (trích ở mục 1). Pháp lệnh Ngoại hối cũng hạn chế chuyển ngoại tệ ra nước ngoài theo mục đích. Mình chưa đọc bản gốc trên Công báo, nên **chưa xác minh** hiệu lực hiện hành và các văn bản sửa đổi.
2. **Tài sản mã hóa:** NQ 05/2025/NQ-CP (hiệu lực 09/09/2025, thí điểm 5 năm). Đ4.7: giao dịch bằng VND. Đ4.9: thuế áp như chứng khoán. Đ7.2: rủi ro bị xử phạt khi dùng tổ chức không được cấp phép.
3. **CFD/forex offshore:** chưa tìm thấy văn bản cấp phép riêng tại VN (chưa xác minh). Các sàn trong báo cáo được cấp phép ở nước ngoài, không phải ở VN.
4. **Thuế Mỹ:** cổ tức ETF Mỹ trả cho người nước ngoài bị khấu trừ tại nguồn (mức 30% mặc định; hiệp định thuế Mỹ–VN có hiệu lực hay chưa: **chưa xác minh**). Người không cư trú còn chịu thuế estate Mỹ với tài sản Mỹ trên ngưỡng (chi tiết chưa xác minh). Một số ETF UCITS niêm yết ở Ireland có thể thay thế; IBKR có giao dịch được, nhưng chưa kiểm phí.

## 6. Nguồn và trạng thái link (kiểm tra 09/11/2026)

| Link | Trạng thái |
|---|---|
| interactivebrokers.com/en/trading/fractional-trading.php | 200 |
| etoro.com/trading/fees/ | 200 |
| exness.com/regulation/ · exness.com/vi/contact/ · exness.com/vi/standard-accounts/ | 200 / đọc qua WebFetch và tìm kiếm |
| get.exness.help (Swap-free status) | Đọc được bằng WebFetch; curl trả 403 (chặn bot) |
| binance.com/en/fee/trading | 202 (trang JS). Nội dung lấy từ trích dẫn tìm kiếm |
| PDF quốc gia bị cấm của Binance (bnbstatic) | 200 |
| fmarket.vn/quy/DCDS · dautu.dragoncapital.com.vn/product/etf · ssi.com.vn biểu phí | 200 |
| pepperstone.com/vi-vn/ · icmarkets.com/global/vn/... | 200 |
| xaydungchinhsach.chinhphu.vn (toàn văn NQ 05/2025) | 200 |
| thuvienphapluat.vn (NĐ 135/2015 Điều 5) | Đọc được bằng WebFetch; curl trả 403 |
| sjc.com.vn | curl trả 403; bảng giá trống → chưa xác minh |

Nguồn affiliate (onforex, wikitoro, tradersunion, datawallet) **không** được dùng làm bằng chứng. Số liệu XM lấy từ `brain2/config/phi_xm_micro.json` và `brain2/reports/phi_xm_micro_that.csv`. Mô hình chi phí nằm ở `quet_intraday/dot5/san_von_nho.py`, kết quả ở `chi_phi.json`.
