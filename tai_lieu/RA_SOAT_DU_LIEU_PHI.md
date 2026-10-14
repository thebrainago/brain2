# RÀ SOÁT DỮ LIỆU VÀ PHÍ — tạm dừng tìm hệ mới (14/10/2026)

Quy ước: chỉ ghi số đo được thật (nguồn ghi kèm). Chưa đo thì ghi **CHƯA ĐO ĐƯỢC**. Thông tin lấy từ trang công khai ghi rõ "theo trang công khai" — đó là quảng cáo của sàn, không phải số đo.
Máy nhà DESKTOP-05PNLGF tắt → mọi việc làm trên box + web công khai. Không đăng ký tài khoản nào.

## 0. Phát hiện quan trọng nhất

1. **Nhóm tài khoản thật không phải "Standard" thường.** Trong `reports/phi_xm_micro_that.csv` (đọc symbol_info 13/10/2026), mã có hậu tố `#` nằm ở đường dẫn `Forex\Standard Ultra Low\...`, chỉ số ở `Derivatives\Cash Ultra Low\...`, vàng ở `Spot Metals Ultra Low I`. Tức là tài khoản demo đang dùng là **XM Ultra Low (biến thể Standard Ultra Low)**, không phải Standard. Mã không hậu tố (`EURUSD`, nhóm `Standard`) spread gấp ~2 lần.
2. **Swap của mã `#` FX và vàng/bạc = `DISABLED`** (dù trường swap_long/short vẫn có số). Tester MT5 vì vậy **không trừ swap** cho FX/vàng. Tiền thật (nếu tài khoản không phải Islamic/swap-free) có thể bị tính swap → backtest có thể đang **lạc quan**. Chỉ số `Cash#` có swap_mode `MARGIN_CCY`, ngày 3 lần = Thứ Sáu.
3. **Spread lúc 00h server đắt hơn 2–5 lần** giữa ngày (số đo bên dưới) — EA D1 vào lúc mở nến chịu giá đắt.
4. **Chỉ số CFD trong tester 2016–2026 = 0 lệnh, 0 tick** (US500/UK100/GER40), trước 2016 quality 11–12% → **không có backtest chỉ số tin được trên XM**.

## 1. Tài khoản XM đang dùng (XMGlobal-MT5 10, demo, nhóm Ultra Low, hậu tố `#`)

Nguồn: `reports/phi_xm_micro_that.csv` (symbol_info + spread bar M1 20.000 nến, H1 30.000 nến, tick 3 ngày), `phi_xm_that.py`, `reports/mt5_v24/tong_hop.json`.

### 1.1 Bảng đã đo (spread tính bằng bps = phần vạn giá)

| Mã | contract | tick size | tick value (USD/lot) | swap long | swap short | swap_mode | ngày ×3 | spread H1 trung vị | spread lúc 00h | spread tick 3 ngày | H1 có từ | D1 có từ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EURUSD# | 100000 | 0.00001 | 1.0 | -7.58 | 1.42 | DISABLED | Thứ Tư | 0.72 | 1.46 | 0.89 | 2021-12-14 | 1992-06 |
| GBPUSD# | 100000 | 0.00001 | 1.0 | -4.65 | -2.94 | DISABLED | Thứ Tư | 0.60 | 2.20 | 0.83 | 2021-12-14 | 1993-05 |
| USDJPY# | 100000 | 0.001 | 0.63 | 2.11 | -29.59 | DISABLED | Thứ Tư | 0.52 | 1.50 | 0.70 | 2021-12-14 | 1992-10 |
| USDCHF# | 100000 | 0.00001 | 1.20 | 4.74 | -14.03 | DISABLED | Thứ Tư | 1.33 | 4.56 | 1.68 | 2021-12-14 | 1992-10 |
| USDCAD# | 100000 | 0.00001 | 0.70 | 2.62 | -11.40 | DISABLED | Thứ Tư | 1.16 | 2.33 | 1.40 | 2021-12-14 | 1993-04 |
| AUDUSD# | 100000 | 0.00001 | 1.0 | -1.62 | -2.52 | DISABLED | Thứ Tư | 1.83 | 3.38 | 1.72 | 2021-12-14 | **2007-06** |
| NZDUSD# | 100000 | 0.00001 | 1.0 | -3.76 | -0.06 | DISABLED | Thứ Tư | 3.10 | 5.34 | 3.57 | 2021-12-14 | **2007-06** |
| GOLD.i# | 100 | 0.01 | 1.0 | -83.83 | 20.64 | DISABLED | Thứ Tư | 0.65 | 0.63 | 0.62 | 2021-09-14 | 2001-06 |
| SILVER.i# | 5000 | 0.001 | 5.0 | -18.91 | 4.42 | DISABLED | Thứ Tư | 8.19 | 8.72 | 8.24 | 2021-09-14 | 2006-12 |
| US500Cash# | 1 | 0.01 | 0.01 | -1.26 | 0.19 | MARGIN_CCY | Thứ Sáu | 1.00 | 1.02 | 0.83 | 2021-09-10 | 2011-08 |
| US100Cash# | 1 | 0.01 | 0.01 | -5.06 | 0.65 | MARGIN_CCY | Thứ Sáu | 0.97 | 1.39 | 0.89 | 2021-09-10 | 2011-09 |
| US30Cash# | 1 | 0.01 | 0.01 | -8.39 | 1.28 | MARGIN_CCY | Thứ Sáu | 0.97 | 1.14 | 0.77 | 2021-09-10 | 2011-08 |
| GER40Cash# | 1 | 0.01 | 0.01 (EUR) | -3.45 | -0.04 | MARGIN_CCY | Thứ Sáu | 0.95 | 3.69 | 0.81 | 2021-08-12 | 2011-07 |
| UK100Cash# | 1 | 0.01 | 0.01 (GBP) | -1.96 | 0.21 | MARGIN_CCY | Thứ Sáu | 2.10 | 7.41 | 1.60 | 2021-07-19 | 2011-08 |
| OILCash# | 100 | 0.01 | 1.0 | 0.0 | 0.0 | MARGIN_CCY | Thứ Sáu | 3.99 | 3.71 | 3.25 | 2021-09-14 | 2010-08 |

Spread theo **từng giờ** (trung vị + p90 theo giờ server, 24 ô) đã có trong cột `H1_spread_pts_med_by_hour`/`..._p90_by_hour` của CSV cho mọi mã trên. Ví dụ (điểm): GER40Cash# 00h=800, 10–18h=150, 23h=765; UK100Cash# 00h=620, 10–18h=130; USDCHF# 00h=39, còn lại 11; EURUSD#/AUDUSD# 00h ~2 lần giờ khác.
Lưu ý: spread H1 trong MT5 là spread **nhỏ nhất** trong nến (cách MT5 lưu), nên có thể thấp hơn spread lúc khớp lệnh thật.

### 1.2 Đã có / còn thiếu (cho từng mục)

| Mục | Trạng thái |
|---|---|
| Spread theo giờ | ĐÃ CÓ cho 15 mã `#` (+ mã Standard không hậu tố, futures) — nhưng chỉ ~5 năm gần (H1 từ 2021). Spread **trước 2021: CHƯA ĐO ĐƯỢC** (XM không lưu). Spread lúc tin tức / thứ Hai mở cửa: CHƯA ĐO ĐƯỢC riêng. |
| Swap long/short, ngày ×3 | ĐÃ CÓ giá trị hiện tại (bảng trên). Nhưng: FX/kim loại `#` là DISABLED → **swap thực tế áp dụng cho tài khoản là bao nhiêu: CHƯA ĐO ĐƯỢC** (cần giữ lệnh qua đêm trên demo và đọc deal swap). **Lịch sử swap theo thời gian: CHƯA ĐO ĐƯỢC** (MT5 chỉ cho giá trị hiện tại). Đơn vị swap FX là POINTS (với mã không hậu tố). |
| Hoa hồng | **CHƯA ĐO ĐƯỢC** trên tài khoản. Symbol_info không chứa hoa hồng; báo cáo tester v24 chưa được rà cột commission. Trang công khai XM ghi Ultra Low "lower swap fees and commissions" nhưng không đọc được bảng số (trang chính trả 403/nội dung rút gọn khi đọc từ box). |
| Contract size, tick value | ĐÃ CÓ (bảng trên). tick value của mã định giá ngoài USD (JPY, CHF, CAD, EUR, GBP) thay đổi theo tỉ giá — tester dùng tỉ giá lịch sử, Python cần quy đổi tương tự. |
| Phí qua đêm CFD chỉ số | Có swap_long/short điểm hiện tại (MARGIN_CCY, ×3 Thứ Sáu). Công thức XM (lãi suất chuẩn ± markup) và lịch sử: **CHƯA ĐO ĐƯỢC**. Điều chỉnh cổ tức (dividend adjustment) trên chỉ số Cash: **CHƯA ĐO ĐƯỢC**. |
| Trượt giá | **CHƯA ĐO ĐƯỢC** (tester Model=1 không mô phỏng trượt; chưa có lệnh demo thật đo giá yêu cầu vs giá khớp). |
| Lịch sử tick thật | Real ticks XM thường chỉ dày từ ~2024-01 (ghi chú vận hành, chưa có con số % chính xác theo mã → CHƯA ĐO ĐƯỢC chi tiết). Quality tester v24 (OHLC M1): FX chính 2004–2015 91%, 2016–2026 92–96%; **AUDUSD 2004–2015 4%**, 2016–2026 73%; GOLD 2004–2015 12% (2016–2026 treo agent, không báo cáo); OIL 2004 7%, 2016 84%; **US500/UK100/GER40 2004 11–12%, 2016–2026 quality 89–91% nhưng 0 tick, 0 lệnh** ("cannot generate history data"). |
| Lỗ hổng dữ liệu đã biết | AUD/NZD `#`: D1 chỉ từ 2007-06, M1 thiếu trước ~2018-05. Chỉ số Cash, dầu, vàng: không có M1 trước ~2016. Chỉ số 2016–2026: tester không sinh được lịch sử (cache 11–21 GB). |

### 1.3 Đối chiếu loại tài khoản XM (trang công khai)
- Đọc https://www.xm.com/account-types từ box (14/10/2026): hiện chỉ còn **Standard, Ultra Low, Shares** (tối thiểu 5 USD / 5 USD / 10.000 USD); **không thấy tài khoản Zero** trên trang này. Ultra Low: "low spreads and even lower swap fees and commissions". Bảng số chi tiết (spread trung bình, hoa hồng) **không đọc được** (trang con bị rút gọn/403 từ box) → CHƯA ĐO ĐƯỢC từ nguồn công khai.
- Số đo thật của ta: Ultra Low (`#`) spread H1 EURUSD 0.72 bps vs Standard (không hậu tố) 1.54 bps; GBPUSD 0.60 vs 1.51; AUDUSD 1.83 vs 3.20.
- Kết luận: để backtest, **Ultra Low (`#`) là hợp nhất trong XM** vì đúng là tài khoản đang dùng và spread thấp, *với điều kiện* làm rõ swap (DISABLED trong tester ≠ chắc chắn 0 khi chạy thật) và hoa hồng. Standard đắt spread gấp ~2. Zero: không còn thấy trên trang công khai → CHƯA ĐO ĐƯỢC.

## 2. Exness (chỉ đọc web công khai)

### 2.1 Loại tài khoản (theo trang công khai, get.exness.help cập nhật 02/10/2026 và exness.com/pro-accounts)
| Loại | Spread (từ) | Hoa hồng | Ghi chú |
|---|---|---|---|
| Standard Cent | 0.3 pip | không | hậu tố -c |
| Standard | 0.2 pip | không | |
| Pro | 0.1 pip | không | khớp Instant |
| Raw Spread | 0.0 pip | tối đa 3.50 USD/lot/chiều | khớp Market |
| Zero | 0.0 pip | từ 0.05 USD/lot/chiều (tuỳ mã) | 0 spread ở top 30 mã phần lớn thời gian |

Swap: trạng thái **swap-free mặc định** cho toàn Personal Area, áp dụng cho FX chính (AUDUSD, EURUSD, GBPUSD, NZDUSD, USDCAD, USDCHF, USDJPY), nhiều cặp phụ, XAUUSD, XAGUSD, USOIL, UKOIL, **toàn bộ chỉ số**, crypto. Có thể **mất** swap-free nếu thường giữ lệnh lớn qua đêm (thuật toán chấm). → Với hệ D1 giữ nhiều đêm, không được giả định swap = 0 vĩnh viễn.

### 2.2 Dữ liệu tick lịch sử công khai — **CÓ, đã tải thử**
- `https://ticks.ex2archive.com/ticks/` trả danh mục JSON công khai (không cần đăng nhập). Có thư mục theo mã và **theo loại tài khoản**: `EURUSD` (Standard), `EURUSD_Raw_Spread`, `EURUSD_Standart_Plus`, `EURUSD_Zero_Spread`, `EURUSDm`, `EURUSDc`…; cũng có `XAUUSD`, `US500`, `USTEC`, `DE30`, `UK100`, `USOIL`, `AUDUSD`.
- Năm bắt đầu (đo 14/10/2026): EURUSD từ **2015-08**, AUDUSD từ 2015, XAUUSD từ 2015; US500/USTEC/DE30/UK100/USOIL từ **2019**; EURUSD_Raw_Spread từ 2020. Cập nhật tới 2026-10-13.
- Mẫu đã tải: `ticks/EURUSD/2024/01/Exness_EURUSD_2024_01.zip` (9,38 MB nén, 83 MB CSV, 1.354.843 tick). Định dạng: `"Exness","Symbol","Timestamp","Bid","Ask"`, timestamp UTC đến mili-giây (vd `2024-01-01 22:05:16.191Z`). **Có cả Bid và Ask → spread thật từng tick.**
- Spread đo trên mẫu này (bỏ cuối tuần, 1.349.449 tick): trung vị **0.552 bps**, p90 0.645 bps. Theo giờ UTC: 00–21h ≈ 0.55; **22h = 3.97 bps**; 23h = 0.74 (giờ rollover đắt ~7 lần).
- Chất lượng lịch sử tick trong MT5 tester của Exness: **CHƯA ĐO ĐƯỢC** (cần tài khoản/terminal).

## 3. So sánh nguồn dữ liệu

| Nguồn | Lịch sử | Tick thật | Spread thật | Chỉ số / vàng | Miễn phí | Đã kiểm trên box |
|---|---|---|---|---|---|---|
| **Dukascopy** (datafeed công khai) | FX chính từ ~2003; kiểm 2004 EURUSD, XAUUSD có file tick; USA500IDXUSD 2013 có file | Có (bid/ask, volume) | Có (spread ECN Dukascopy, không phải XM) | Có vàng, CFD chỉ số (độ dài từng mã CHƯA ĐO ĐƯỢC đủ) | Có | Có: 3 URL trả 200 (14/10); repo đã có `tai_dukascopy_*.py`. Máy chủ chập chờn (lần 2 lỗi TLS). |
| **Exness ex2archive** | FX/vàng từ 2015, chỉ số/dầu từ 2019 | Có | Có, của chính sàn, theo loại tài khoản | Có | Có | Có, mẫu ở mục 2.2 |
| TrueFX | (theo hiểu biết chung ~2009+, chỉ FX) | Có (tick ngân hàng) | Có (spread liên ngân hàng, rất hẹp) | Không | Có (cần đăng ký) | Trang trả 301, chưa tải → CHƯA ĐO ĐƯỢC |
| HistData | FX từ ~2000 (M1), tick ~2010+ | Một phần | Tick có bid/ask; M1 chỉ bid → không có spread | Có XAUUSD, vài chỉ số | Có | Trang tải 200; repo có `gop_histdata_*.py`. Năm cụ thể CHƯA ĐO ĐƯỢC lại |
| Tickstory | Dùng lại dữ liệu Dukascopy | Có | Có (của Dukascopy) | Như Dukascopy | Bản cơ bản miễn phí, phần mềm Windows | Không chạy được trên box (Windows) |
| MQL5/MetaQuotes | Lịch sử do từng sàn cung cấp; MetaQuotes-Demo có lịch sử riêng | Tuỳ sàn | Tuỳ sàn | Tuỳ sàn | Có | Trang tài liệu docs đọc được (200). Không vượt chống bot. Không có kho tải tick công khai |
| Darwinex | Lịch sử tick qua FTP cho khách | Có | Có | Có | Cần tài khoản | CHƯA ĐO ĐƯỢC |
| IC Markets / Pepperstone | Lịch sử trong MT5 của sàn, không có kho tải công khai | Real ticks trong tester gần đây | Có trong tester | Có | Cần tài khoản demo | CHƯA ĐO ĐƯỢC |

(Cột không đánh "Đã kiểm" là theo hiểu biết chung/trang công khai, cần xác minh trước khi dựa vào.)

## 4. Phương án chuẩn đề xuất

1. **Giá chuẩn: Dukascopy** (bid+ask tick/M1, dài nhất: FX từ ~2003, vàng, một số chỉ số) cho giai đoạn dài. **Kiểm chéo bằng Exness ex2archive** từ 2015 (FX, vàng) / 2019 (chỉ số): đo chênh giá mid giữa hai nguồn; nếu lệch nhỏ thì yên tâm.
2. **Phí ghép vào: sàn sẽ chạy thật.** Nếu ở lại XM → dùng bảng XM Ultra Low ở mục 1. Nếu cân nhắc Exness → dùng chính spread tick Exness (đã có lịch sử theo loại tài khoản, thứ XM không có).
3. **Cách ghép:**
   - Spread: bảng spread theo **giờ trong ngày × ngày trong tuần** của sàn (trung vị và p90, theo bps), áp vào giờ khớp lệnh của EA; trước giai đoạn có số đo của sàn thì dùng tỉ lệ (spread sàn / spread Dukascopy cùng giờ) đo ở giai đoạn chồng lấn nhân với spread Dukascopy lịch sử. Thử lại với p90 để kiểm tra độ nhạy.
   - Swap: tính theo từng đêm giữ lệnh, ×3 đúng ngày của sàn (FX/vàng XM: Thứ Tư; chỉ số Cash XM: Thứ Sáu), dùng giá trị đo thật; chạy 2 kịch bản: swap = 0 (swap-free) và swap đầy đủ; nếu hệ chỉ có lời khi swap = 0 thì coi là rủi ro.
   - Hoa hồng: cộng cố định USD/lot/chiều theo số đo thật (XM: CHƯA ĐO ĐƯỢC; Exness Raw ≤3.5, Zero ≥0.05 theo trang).
   - Trượt giá: cộng thêm 0.5× spread mỗi chiều làm mặc định thận trọng cho tới khi có số đo; giờ 00h/rollover dùng p90.
4. **Cần đo trên demo khi máy nhà bật lại:**
   - Hoa hồng thật trên XM `#` (mở/đóng 1 lệnh 0,01 lot mỗi mã, đọc deal commission).
   - Swap thật: giữ 0,01 lot long và short qua đêm thứ Tư (FX/vàng) và thứ Sáu (chỉ số), đọc deal swap → xác nhận DISABLED có nghĩa 0 hay không.
   - Trượt giá: 20–50 lệnh thị trường mỗi mã ở 00h, 02h, giữa phiên; ghi giá yêu cầu vs giá khớp vs thời gian.
   - % real ticks theo năm cho từng mã trong tester (đọc "History quality" và "real ticks").
   - Điều chỉnh cổ tức chỉ số Cash# (deal "dividend").
   - Spread theo tick 1–2 tuần liên tục (thay vì min-spread của H1).
   - Nếu được phép mở demo Exness: chất lượng lịch sử trong tester Exness.

## 5. Danh sách lỗi có thể đã xảy ra trong backtest (để rà sau)

1. **Look-ahead**: dùng close nến D1 để quyết định rồi vào lệnh ở chính giá close/open cùng nến; chỉ báo tính trên nến chưa đóng; chuẩn hoá z-score bằng toàn bộ chuỗi.
2. **Spread 00h**: Python dùng spread trung vị trong khi EA vào lúc 00h (đắt 2–5×); MT5 H1 lưu spread nhỏ nhất nên còn thấp hơn thực tế.
3. **Swap**: tester không tính swap cho mã `#` (DISABLED) trong khi Python cũ trừ 2,5%/năm → hai kết quả không cùng giả định; giá trị swap hiện tại áp cho cả 20 năm quá khứ là sai (lãi suất đã đổi nhiều).
4. **Giá tính swap / ngày ×3** sai (Thứ Tư vs Thứ Sáu), lễ.
5. **Lệch D1 Yahoo vs D1 sàn**: Yahoo đóng nến theo giờ khác (NY/UTC), sàn XM GMT+2/+3 → nến Chủ nhật, high/low khác, tín hiệu khác. Chỉ số Yahoo (^GSPC) là chỉ số tiền mặt, không phải CFD (khác giờ giao dịch, không có cổ tức điều chỉnh).
6. **Lỗ hổng dữ liệu**: AUD trước 2018-05 (quality 4%), chỉ số trước 2016 → giai đoạn này "lệnh" chỉ là tick 00h giả; chỉ số 2016–2026 0 lệnh bị hiểu nhầm là "không lỗ".
7. **[Market closed] lúc 00:00**: lệnh bị từ chối/lùi giờ (đã sửa EA e87e1905, cần kiểm lại các vòng trước đó).
8. **Survivorship / chọn mã**: chọn mã đã chạy tốt trong quá khứ; bỏ mã chết; chọn tài sản sau khi xem kết quả.
9. **Multiple testing**: quét rất nhiều hệ/tham số → kết quả tốt nhất do may; cần FDR/Deflated Sharpe, holdout chưa từng chạm, đếm số lần thử thật.
10. **Rò holdout**: dùng holdout nhiều lần để chọn → holdout không còn sạch.
11. **Quy đổi tick value** mã ngoài USD (JPY/CHF/CAD/GER40 EUR/UK100 GBP) theo tỉ giá cố định.
12. **Đơn vị lot tối thiểu chỉ số 0,1** khác FX 0,01 → so sánh net USD giữa mã sai lệch.
13. **Múi giờ/DST**: giờ server XM đổi theo DST, giờ vào lệnh 02h lệch 1 giờ nửa năm.
14. **Trượt giá = 0** trong tester Model=1.
15. **Cổ tức/rollover hợp đồng** chỉ số Cash và dầu (OILCash là CFD theo futures → có điều chỉnh khi đổi kỳ hạn).
16. **Fill bar giả** trong OHLC M1: TP/SL cùng nến không biết cái nào chạm trước.

## Kiểm thử đã chạy
`pytest test_do_phi_xm.py test_chi_phi_v2.py test_chi_phi_xuat_xu.py test_lop_va_phi_tai_san.py test_p3_phi_thoi_ky.py test_chat_luong_du_lieu.py` → **52 passed** (14/10/2026, box).
