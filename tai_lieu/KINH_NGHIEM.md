# KINH NGHIỆM GIAO DỊCH (rút từ vòng 1–26, cập nhật vòng 27). Tất cả là MÔ PHỎNG trừ khi ghi MT5.
1. **Kết quả quá đẹp = lỗi trước.** Vòng 25 lần đầu ra 27 "hệ sống" do lookahead (mảng thoát dùng s[i+1]); sửa xong còn 0. Mọi hàm tín hiệu phải có test cắt dữ liệu.
2. **Phí ăn hết cạnh khung nhỏ.** RSI_Exhaustion M5 EURUSD có lãi GỘP cả hai nửa nhưng spread XM ≈ 68 % biên độ nến M5 trung vị → ròng âm (kiểm −4,1 %). Khung M5/M15 chỉ đáng thử khi cạnh thô > ~3× spread.
3. **Giờ vào lệnh quan trọng ngang tín hiệu.** Spread 00h server (mở nến D1) đắt gấp 3–5 lần 02h (GBPUSD 3,9 vs 0,74 bps; AUDUSD 5,3 vs 1,65). Hệ D1 nên vào lệch giờ (EA MRZ `InpGioVao=2`).
4. **Near-miss tốt nhất tới nay:** MRZ (z50 ±2, TR2) D1 AUDUSD vào 02h: sau phí 29,5 / 67,8 bps/lệnh, p 0,008, DD 15 % — nhưng Holm cộng dồn 1,0 → KHÔNG qua. Không được nới cổng.
5. **Ghép danh mục với hệ phá vỡ (DINH20) làm xấu đi** mọi nhóm vòng 26; lọc EMA200 làm còn < 30 lệnh/nửa → CHƯA ĐO ĐƯỢC.
6. **Lưới/martingale**: Sharpe/t không đủ để giữ; đuôi stop-out kiểu MT5 phải mô phỏng, nếu không lãi giả.
7. **Dữ liệu MT5 cũ của XM yếu** (AUDUSD 2004–2015 chất lượng mô hình ~4 %) → giai đoạn cũ chưa kiểm chứng MT5.
8. **Bộ đọc EA**: phần lớn EA tải về là công cụ (guard/panel/calculator, không có điều kiện vào) — tỷ lệ dịch thấp (3/78) không chủ yếu do bộ đọc. Lý do thật còn lại: hàm trả hướng int qua biến cục bộ (`dir = CheckBreakout()`), lệnh trong vòng for/while, so sánh chuỗi trạng thái.
9. **Swap**: nhóm '#' tài khoản XM thật swap DISABLED; mô hình cũ trừ 2,5 %/năm — giữ để bảo thủ.
10. **Holm cộng dồn** đã > 12.900 phép thử: một hệ cần p một phía cỡ < 4e-6 mới qua. Ưu tiên ít ô, có chủ đích, đa tài sản (gộp tăng n), thay vì quét lưới rộng.
11. **Spread ×1,5 + trượt 1 bps** là phép thử áp lực bắt buộc; nhiều hệ chết ở đây.
12. Nguồn TradingView/fxblue/quantpedia bị 403/Cloudflare trên box → CHƯA ĐO ĐƯỢC, không vượt; chuyển sang máy nhà.
13. **(Chu kỳ 3, 13/10) Đo bộ đọc trên TOÀN KHO, không chỉ lô mới.** Kho 3.204 tệp duy nhất (md5): 726 công cụ không có lệnh đặt, 100 không phải EA, 2.378 EA có lệnh → dịch được 81 → 85 (3,41 % → 3,57 %). Tỷ lệ dịch thấp là đuôi dài: mỗi EA hỏng thường có 2–3 chỗ chặn nối nhau (sửa chỗ đầu chỉ lộ chỗ sau). Lý do hàng đầu còn lại: điều kiện chưa dịch được (881), gọi hàm phụ (465), không tìm được guard (356).
14. **Ba ngôi `cond ? trade.Buy : trade.Sell` từng sinh luật NGƯỢC CHIỀU.** Sau chuyên biệt hoá, `(true) ? Buy : Sell` không được gập → bộ đọc nhận CẢ HAI chiều cho mỗi chỗ gọi: 3 EA (EA_Template, RsiLevel, RsiReversal) mỗi cái có 2 luật sai chiều (bán khi cắt lên). Đã gập hằng → còn 2 luật đúng. Luật từ bộ đọc phải được đối chiếu chiều với mã gốc trước khi tin.
15. **Bộ đọc chặn nhầm `if(A && B) F();`** (lý do "sau toán tử điều kiện"): kiểm `and/or/?` trên cả câu lệnh thay vì phần còn lại sau `if(...)`. Test đơn vị nhỏ bắt được cả lỗi else treo (`if(a) if(b) x; else …`) trước khi đưa vào kho.
16. **(Chu kỳ 4, vòng 28) Near-miss MRZ AUDUSD không lan sang cặp anh em.** Pool AUDUSD+NZDUSD+AUDCAD+GBPUSD (cấu hình cố định z50 ±2, TR2, 02h): sau phí 6,0 / 26,2 bps/lệnh, p 0,025 — nhưng NZDUSD ≈ 0 cả hai nửa (−2,9 / +1,1), AUDCAD phát hiện +0,5; AUDUSD gánh pool. Cạnh "AUDUSD" nhiều khả năng là may mắn một chuỗi (MÔ PHỎNG).
17. **Chọn thoát theo tài sản = khớp nhiễu.** Trailing 2,5·ATR làm AUDUSD đẹp nhất từ trước (sau phí 42,6 / 131 bps, p 0,0004) nhưng GBPUSD cùng thoát rơi ở tầng 1 (phát hiện −9,6); thoát thời gian 5 nến và 1,5·ATR GBPUSD cũng âm nửa đầu. Không có thoát nào tốt trên cả hai cặp → không chọn thoát theo từng cặp.
18. **Lọc W1 EMA20 (chỉ hồi quy thuận xu hướng tuần)** cho bps/lệnh cao, DD rất thấp (FX7: 61,8 / 36,4 bps, DD 1,9 %) nhưng chỉ 46–98 lệnh/nửa → p 0,07–0,09; lọc mạnh cắt n quá nhiều để qua Holm 12.960. Hướng có ích hơn: tăng n (nhiều cặp hơn, khung H4) với cùng lọc, không thêm lọc.

## 13/10/2026 tối — ca máy nhà vòng 27 (MT5 liên tục)
- MT5 portable mới chép KHÔNG có `config\accounts.dat` → "tester not started because the account is not specified", terminal tắt sau ~12 s; vòng lặp phóng job kế → MT5 nhấp nháy trước mặt chủ dự án. Luôn chép accounts.dat + common.ini, và có fail-fast (job < 90 s không báo cáo → dừng hàng).
- `robocopy /XD Tester` bỏ qua CẢ `MQL5\Profiles\Tester` → thiếu .set → tester chạy tham số MẶC ĐỊNH mà không báo lỗi. Luôn kiểm input trong .htm (InpXxx=) sau khi chạy.
- Một terminal portable chỉ chạy một phiên: gọi `MetaTrader5.initialize(path=slot)` trong khi slot đang test → job tester hỏng ngay. Dùng slot riêng (E:\mt5_tester\p5) cho xuất dữ liệu.
- XM AUDUSD#/NZDUSD# (và AUDCAD#) KHÔNG có M1 trước ~2018-05 → tester chỉ có tick 00h → `InpGioVao>0` không vào lệnh trước 2018-05. So sánh giờ vào phải cùng giai đoạn có M1.
- Real ticks XM chỉ có từ 2024-01 ("25% real ticks" cho 2016-2026; 0% cho IS 2016-2022).
- Spread XM 00h server gấp 5-10 lần trung vị ngày (GBPUSD 11,4 vs 1,3 pip; GBPJPY 22 vs 2,7).
- MT5 ↔ Python (phan_tich_luoi_box) trên 207 biến thể trùng: cùng số lệnh (trung vị tỉ lệ 1,0), PF tương quan 0,83, cùng dấu PF>1 194/207.
- psutil trên Windows: "System Idle Process" (pid 0) báo ~100% → phải loại khi đo tải người dùng.
- Path.replace không chuyển được giữa ổ (E:→D:) → dùng shutil.move.
- Mỗi mã mới tải lịch sử ~0,3-0,6 GB/slot; chạy qua đêm cần dọn cache khi ổ < 6 GB (`don_neu_day`).
- Hồ sơ Chrome thebrainago đăng nhập (.browser_thebrain) đã mất sau cài lại Windows; Chrome hồ sơ mới từ IP nhà vẫn bị 403 ở TradingView chi tiết/SSRN/StackExchange.

## 13/10/2026 — khai thác X (vòng 29, MÔ PHỎNG)
19. **X nhiều nhiễu**: ~380 bài đọc, chỉ ~2 tài khoản (QuantifiedStrat, EmpiricaLab) cho luật đủ chi tiết để code; phần lớn là quảng cáo EA/ML hộp đen, PF/win-rate không có điều kiện vào. Ưu tiên tài khoản tự chạy lại có phí + placebo.
20. **Dữ liệu Yahoo FX OHLC không dùng cho luật dựa high/low**: IBS GBPUSD holdout 58 bps PF 4,3 trên Yahoo nhưng chỉ 6,9 bps PF 1,25 trên HistData 2024–26 → loại. Luật IBS/range phải đo trên OHLC broker.
21. **Hồi quy ngắn hạn chỉ số Mỹ vẫn sống** sau spread XM: IBS<0,2 US500/US100 qua Holm cộng dồn 13.000 (p_holm 0,003 / 0,0015). Cảnh báo: khớp cùng close tín hiệu, giá cash Yahoo, swap #=0; chưa MT5. DAX không lặp lại → cạnh đặc thù Mỹ.
22. **Hiệu ứng qua đêm**: chỉ số Mỹ qua đêm mọi đêm âm/≈0 sau spread ở phát hiện; vàng qua đêm dương cả hai nửa (4,7/4,5 bps) nhưng chưa qua Holm.
23. Ngân sách X: tìm kiếm `from:A OR from:B` gom nhiều tài khoản/lệnh gọi tiết kiệm hơn get_users_posts; tên user sai làm hỏng cả truy vấn.
24. **(Chu kỳ 7) Yahoo chart API `period1=0` cắt lịch sử về 1970** (^GSPC/^N225). Luôn giữ bản dài (`gspc_dai_yahoo.csv`) và chỉ *nối* ngày mới; không ghi đè bằng kết quả API một phát. Yêu cầu P3-22 ≥1990 vẫn đạt với N225 từ 1970.
25. **(Chu kỳ 7) Dukascopy datafeed không ổn định theo lần gọi**: cùng URL BID H1 có thể 200 rồi ASK 503 trong vài phút. Thử 1 lần; nếu 503 ghi CHƯA ĐO ĐƯỢC, không hammer. Ưu tiên khai thác CSV `*_h1_duka_ba_*` đã có để ra hình dạng spread theo giờ (ECN ≠ XM).

## 13/10/2026 22h44 — tốc độ hệ thống (chu kỳ 5 vòng lặp box)
24. **Đo trước khi tối ưu**: cProfile `phan_tich_luoi_box.py` cho thấy ~60 % thời gian nằm ở `mask.iloc[j]` (pandas tra từng phần tử) chứ không ở mô phỏng; đổi mặt nạ IS/OOS sang mảng numpy là thắng lớn nhất. Đọc lại CSV spread cho mỗi ô lưới (thiếu cache) là lãng phí thứ hai.
25. **Tách phần không phụ thuộc tham số**: ATR/RSI tính 1 lần/chuỗi, z-score 1 lần/(chuỗi, N) dùng cho mọi ngưỡng z; mô phỏng không phụ thuộc giờ vào ngoài phí cố định → chạy 1 lần phí 0 rồi trừ phí (cùng phép trừ → trùng từng bit). Giữ nguyên công thức Python gốc thay vì numpy rolling để kết quả không lệch ở biên ngưỡng.
26. **Kết quả đo (box 8 lõi)**: lưới 38.736 lần thử 27 mã D1 XM: 49,7 s → 9,2 s tuần tự (×5,4) → 2,6 s với 8 tiến trình (×19). Đầu ra chi tiết và tổng kết trùng tuyệt đối với bản cũ → không ảnh hưởng sổ Holm. Lưới lớn hơn (H1/H4, nhiều cặp) giờ rẻ: ưu tiên tăng n thay vì thêm lọc (KN 18).
27. **Bộ test đầy đủ có tác dụng phụ**: chạy cả 227 tệp test (>11 phút) ghi đè `reports/BANG_HE.json`, `reports/EVO_SUC_KHOE.md`, `nhat_ky/kho_co_che_ghi.log` → luôn `git checkout` các tệp đó sau khi chạy, chỉ chạy test liên quan trong chu kỳ.



## Chuẩn phí (14/10/2026): XM STANDARD có bonus
- Tài khoản chạy thật: **XM Standard (mã KHÔNG hậu tố, có bonus)**. Từ nay mọi kiểm tra mặc định dùng phí XM Standard: `phi_xm_that.TAI_KHOAN_MAC_DINH = "Standard"`, hàm `spread_gio_bps_tk`, `swap_dem_tk`, hoa hồng 0, trượt giá 0,5×spread mỗi chiều.
- Swap Standard được tính thật (swap_mode POINTS), khác Ultra Low `#` (FX/vàng DISABLED trong tester) → backtest trên tài khoản `#` lạc quan hơn.
- Spread chỉ số bản Standard CHƯA ĐO: đang ƯỚC = Ultra Low × tỉ lệ Standard/Ultra Low của FX cùng giờ. Phải đo khi máy nhà bật.
- Bonus: cỡ lot và maxDD tính theo tiền gửi thật (Balance), không tính Credit; không rút tiền khi đang có lệnh. Chi tiết: `reports/so_sanh_san.md` mục 4.
