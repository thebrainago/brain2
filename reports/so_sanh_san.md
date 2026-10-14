# SO SÁNH SÀN: XM Ultra Low (sàn chính) và Exness (đối chiếu) — 14/10/2026

**MÔ PHỎNG Python, KHÔNG PHẢI TIỀN THẬT.** Số trong bảng là kết quả chạy `so_sanh_san.py` (box). Chưa đo thì ghi CHƯA ĐO ĐƯỢC.

## 1. Cách làm
- **Giá:** D1 Yahoo đang có (`/workspace/du_lieu_ngay/v24`, từ 2004; AUDUSD từ 2006-05). Chưa dùng Dukascopy D1 vì chưa có sẵn đủ mã trên box → đây là hạn chế (lệch D1 Yahoo và D1 sàn, xem `tai_lieu/RA_SOAT_DU_LIEU_PHI.md` mục 5).
- **Vốn:** mỗi lệnh danh nghĩa cố định 10.000 USD (không lãi kép); maxDD tính theo USD trên đường lãi cộng dồn, % là so với 10.000 USD. Mỗi hệ chia đôi theo thời gian (mốc chia ghi ở từng hệ).
- **Định nghĩa hệ** (lần chạy này; trong repo không có một bộ tham số chuẩn duy nhất cho từng hệ, nên dùng định nghĩa ghi trong docstring `so_sanh_san.py`): IBS<0,2 mua lúc đóng cửa, bán lúc đóng cửa hôm sau; MRZ z=±2 trên SMA/STD n, vào lúc mở nến sau, dừng lỗ 1,5×ATR14, thoát khi z cắt 0 / trail k×ATR / hết 72 nến; RSI14 30/70, thoát khi cắt 50, trail 2×ATR, tối đa 72 nến.
- **Phí XM Ultra Low** (`phi_xm_that.py`, nguồn `reports/phi_xm_micro_that.csv` đo 13/10/2026): spread trung vị theo giờ server (00h cho hệ vào lúc mở nến, 23h cho IBS); trượt giá 0,5×spread mỗi chiều; hoa hồng 0 (CHƯA ĐO ĐƯỢC trên tài khoản); swap 2 kịch bản: `mien_swap` = như tester (FX/vàng DISABLED → 0, chỉ số Cash# vẫn bị tính vì swap_mode MARGIN_CCY), `swap_day_du` = dùng mức swap_long/short trong CSV cho cả FX. Lưu ý: swap chỉ số XM bị tính ở cả hai kịch bản nên hai dòng XM của IBS/GER40 trùng nhau.
- **Phí Exness** (`phi_exness.py`): spread theo giờ UTC × thứ trong tuần (trung vị, p90) đo từ kho tick công khai ticks.ex2archive.com, mẫu 3 tháng 2025-02, 2025-06, 2025-10, loại Standard và Raw_Spread; bảng gọn ở `/workspace/du_lieu_fx/exness/spread_exness.csv` (177 KB, file tick thô đã xoá). Giờ khớp: trung bình 21h và 22h UTC (≈ 00h server XM), IBS 20h UTC. Hoa hồng Raw 3,5 USD/lot/chiều cho FX; **hoa hồng Raw cho chỉ số: CHƯA ĐO ĐƯỢC → đang tính 0, nên Raw ở chỉ số nhìn rẻ hơn thực tế**. Swap: `mien_swap` = 0; `swap_day_du` = lấy mức swap XM làm xấp xỉ (Exness không công bố lịch sử swap trong kho). EURGBP/EURJPY không có mức swap nào đo được → CHƯA ĐO ĐƯỢC.
- Mức swap hiện tại áp cho cả 20 năm (lãi suất đã đổi nhiều) — chỉ là kiểm tra độ nhạy, không phải swap lịch sử.

Spread đo được lúc vào lệnh (bps): GER40 XM 00h 3,17 / Exness Std 2,46–2,63 / Raw 0,25–0,58; AUDUSD XM 00h 3,16 / Exness Std 2,58 (21h) 1,30 (22h) / Raw 1,39 / 0,31; GBPUSD XM 2,12 / Exness Std 1,52 / 0,59; USDCAD XM 2,17 / Exness Std 1,39 / 1,03; US500 lúc đóng cửa XM 23h 0,70 / Exness Std 0,67 / Raw 0; US100 XM 0,64 / Exness Std 0,60 / Raw 0,02. EURGBP/EURJPY trên XM: CHƯA ĐO ĐƯỢC.

"Sống" = PF > 1 ở **cả hai nửa**.

## 2. Kết quả

### IBS<0.2 US500
Dữ liệu 2004-01-02..2026-10-09, mốc chia 2015-05-22.

| Sàn | Kịch bản swap | Nửa 1: PF / lãi ròng USD / maxDD % / số lệnh | Nửa 2: PF / lãi ròng USD / maxDD % / số lệnh | Sống? |
|---|---|---|---|---|
| (giá thô, không phí) | — | 1.737 / 14579.59 / 13.41 / 568 | 1.346 / 7362.23 / 13.13 / 552 | |
| XM | mien_swap | 1.607 / 12516.79 / 13.75 / 568 | 1.242 / 5363.94 / 13.62 / 552 | CÓ |
| XM | swap_day_du | 1.607 / 12516.79 / 13.75 / 568 | 1.242 / 5363.94 / 13.62 / 552 | CÓ |
| Exness_Standard | mien_swap | 1.688 / 13820.03 / 13.51 / 568 | 1.306 / 6624.06 / 13.32 / 552 | CÓ |
| Exness_Standard | swap_day_du | 1.61 / 12557.69 / 13.74 / 568 | 1.244 / 5403.69 / 13.61 / 552 | CÓ |
| Exness_Raw | mien_swap | 1.737 / 14579.59 / 13.41 / 568 | 1.346 / 7362.23 / 13.13 / 552 | CÓ |
| Exness_Raw | swap_day_du | 1.656 / 13317.25 / 13.63 / 568 | 1.281 / 6141.85 / 13.42 / 552 | CÓ |

### IBS<0.2 US100
Dữ liệu 2004-01-02..2026-10-09, mốc chia 2015-05-22.

| Sàn | Kịch bản swap | Nửa 1: PF / lãi ròng USD / maxDD % / số lệnh | Nửa 2: PF / lãi ròng USD / maxDD % / số lệnh | Sống? |
|---|---|---|---|---|
| (giá thô, không phí) | — | 1.562 / 13312.76 / 18.17 / 555 | 1.616 / 15146.02 / 14.96 / 545 | |
| XM | mien_swap | 1.459 / 11265.86 / 18.68 / 555 | 1.519 / 13191.02 / 15.74 / 545 | CÓ |
| XM | swap_day_du | 1.459 / 11265.86 / 18.68 / 555 | 1.519 / 13191.02 / 15.74 / 545 | CÓ |
| Exness_Standard | mien_swap | 1.528 / 12646.65 / 18.35 / 555 | 1.583 / 14491.91 / 15.21 / 545 | CÓ |
| Exness_Standard | swap_day_du | 1.46 / 11305.45 / 18.67 / 555 | 1.521 / 13229.89 / 15.72 / 545 | CÓ |
| Exness_Raw | mien_swap | 1.561 / 13291.98 / 18.18 / 555 | 1.615 / 15125.61 / 14.97 / 545 | CÓ |
| Exness_Raw | swap_day_du | 1.492 / 11950.77 / 18.49 / 555 | 1.552 / 13863.58 / 15.48 / 545 | CÓ |

### MRZ AUDUSD z2 SMA50 trail3
Dữ liệu 2006-05-15..2026-10-12, mốc chia 2016-07-28.

| Sàn | Kịch bản swap | Nửa 1: PF / lãi ròng USD / maxDD % / số lệnh | Nửa 2: PF / lãi ròng USD / maxDD % / số lệnh | Sống? |
|---|---|---|---|---|
| (giá thô, không phí) | — | 0.799 / -2769.16 / 38.47 / 112 | 1.59 / 4455.98 / 10.95 / 100 | |
| XM | mien_swap | 0.757 / -3477.29 / 43.66 / 112 | 1.484 / 3823.72 / 12.51 / 100 | không |
| XM | swap_day_du | 0.733 / -3863.12 / 46.21 / 112 | 1.412 / 3348.89 / 13.7 / 100 | không |
| Exness_Standard | mien_swap | 0.773 / -3203.83 / 41.65 / 112 | 1.524 / 4067.88 / 11.75 / 100 | không |
| Exness_Standard | swap_day_du | 0.749 / -3589.66 / 44.21 / 112 | 1.45 / 3593.06 / 12.95 / 100 | không |
| Exness_Raw | mien_swap | 0.782 / -3048.95 / 40.5 / 112 | 1.544 / 4186.39 / 11.38 / 100 | không |
| Exness_Raw | swap_day_du | 0.758 / -3434.78 / 43.05 / 112 | 1.469 / 3711.57 / 12.57 / 100 | không |

### MRZ GBPUSD SMA20 hold72
Dữ liệu 2004-01-01..2026-10-12, mốc chia 2015-05-23.

| Sàn | Kịch bản swap | Nửa 1: PF / lãi ròng USD / maxDD % / số lệnh | Nửa 2: PF / lãi ròng USD / maxDD % / số lệnh | Sống? |
|---|---|---|---|---|
| (giá thô, không phí) | — | 0.863 / -1280.41 / 14.98 / 145 | 1.283 / 2571.91 / 10.54 / 158 | |
| XM | mien_swap | 0.803 / -1895.16 / 21.08 / 145 | 1.202 / 1902.05 / 11.05 / 158 | không |
| XM | swap_day_du | 0.772 / -2220.49 / 24.31 / 145 | 1.146 / 1406.68 / 11.65 / 158 | không |
| Exness_Standard | mien_swap | 0.833 / -1586.25 / 18.02 / 145 | 1.242 / 2238.65 / 10.8 / 158 | không |
| Exness_Standard | swap_day_du | 0.801 / -1911.59 / 21.24 / 145 | 1.184 / 1743.28 / 11.15 / 158 | không |
| Exness_Raw | mien_swap | 0.845 / -1456.86 / 16.73 / 145 | 1.256 / 2360.47 / 10.71 / 158 | không |
| Exness_Raw | swap_day_du | 0.813 / -1782.19 / 19.96 / 145 | 1.199 / 1865.1 / 11.06 / 158 | không |

### RSI EURJPY
Dữ liệu 2004-01-01..2026-10-12, mốc chia 2015-05-23.

| Sàn | Kịch bản swap | Nửa 1: PF / lãi ròng USD / maxDD % / số lệnh | Nửa 2: PF / lãi ròng USD / maxDD % / số lệnh | Sống? |
|---|---|---|---|---|
| (giá thô, không phí) | — | 0.753 / -2229.65 / 40.22 / 87 | 1.351 / 1681.28 / 8.94 / 79 | |
| XM | mien_swap | CHƯA ĐO ĐƯỢC (spread/swap XM cho ma nay CHUA DO DUOC (khong co trong phi_xm_micro_that.csv)) | | |
| XM | swap_day_du | CHƯA ĐO ĐƯỢC (spread/swap XM cho ma nay CHUA DO DUOC (khong co trong phi_xm_micro_that.csv)) | | |
| Exness_Standard | mien_swap | 0.709 / -2716.37 / 42.71 / 87 | 1.246 / 1239.31 / 9.95 / 79 | không |
| Exness_Standard | swap_day_du | CHƯA ĐO ĐƯỢC (swap day du Exness CHUA DO DUOC (khong co muc swap proxy)) | | |
| Exness_Raw | mien_swap | 0.724 / -2542.34 / 41.73 / 87 | 1.281 / 1390.59 / 9.61 / 79 | không |
| Exness_Raw | swap_day_du | CHƯA ĐO ĐƯỢC (swap day du Exness CHUA DO DUOC (khong co muc swap proxy)) | | |

### MRZ GER40
Dữ liệu 2004-01-02..2026-10-12, mốc chia 2015-05-23.

| Sàn | Kịch bản swap | Nửa 1: PF / lãi ròng USD / maxDD % / số lệnh | Nửa 2: PF / lãi ròng USD / maxDD % / số lệnh | Sống? |
|---|---|---|---|---|
| (giá thô, không phí) | — | 0.671 / -8013.77 / 93.75 / 153 | 1.479 / 7844.22 / 28.86 / 164 | |
| XM | mien_swap | 0.618 / -9678.44 / 105.86 / 153 | 1.337 / 5823.04 / 29.4 / 164 | không |
| XM | swap_day_du | 0.618 / -9678.44 / 105.86 / 153 | 1.337 / 5823.04 / 29.4 / 164 | không |
| Exness_Standard | mien_swap | 0.647 / -8792.41 / 98.12 / 153 | 1.417 / 7009.6 / 29.16 / 164 | không |
| Exness_Standard | swap_day_du | 0.624 / -9487.99 / 104.22 / 153 | 1.351 / 6027.18 / 29.33 / 164 | không |
| Exness_Raw | mien_swap | 0.667 / -8141.22 / 94.41 / 153 | 1.469 / 7707.61 / 28.91 / 164 | không |
| Exness_Raw | swap_day_du | 0.643 / -8836.8 / 98.6 / 153 | 1.401 / 6725.19 / 29.07 / 164 | không |

### MRZ EURGBP
Dữ liệu 2004-01-01..2026-10-12, mốc chia 2015-05-23.

| Sàn | Kịch bản swap | Nửa 1: PF / lãi ròng USD / maxDD % / số lệnh | Nửa 2: PF / lãi ròng USD / maxDD % / số lệnh | Sống? |
|---|---|---|---|---|
| (giá thô, không phí) | — | 1.086 / 683.94 / 17.79 / 159 | 1.328 / 2310.49 / 10.7 / 153 | |
| XM | mien_swap | CHƯA ĐO ĐƯỢC (spread/swap XM cho ma nay CHUA DO DUOC (khong co trong phi_xm_micro_that.csv)) | | |
| XM | swap_day_du | CHƯA ĐO ĐƯỢC (spread/swap XM cho ma nay CHUA DO DUOC (khong co trong phi_xm_micro_that.csv)) | | |
| Exness_Standard | mien_swap | 0.956 / -371.14 / 23.11 / 159 | 1.173 / 1295.23 / 12.03 / 153 | không |
| Exness_Standard | swap_day_du | CHƯA ĐO ĐƯỢC (swap day du Exness CHUA DO DUOC (khong co muc swap proxy)) | | |
| Exness_Raw | mien_swap | 0.998 / -15.79 / 20.89 / 159 | 1.221 / 1622.45 / 11.6 / 153 | không |
| Exness_Raw | swap_day_du | CHƯA ĐO ĐƯỢC (swap day du Exness CHUA DO DUOC (khong co muc swap proxy)) | | |

### MRZ USDCAD
Dữ liệu 2004-01-01..2026-10-12, mốc chia 2015-05-23.

| Sàn | Kịch bản swap | Nửa 1: PF / lãi ròng USD / maxDD % / số lệnh | Nửa 2: PF / lãi ròng USD / maxDD % / số lệnh | Sống? |
|---|---|---|---|---|
| (giá thô, không phí) | — | 1.154 / 1239.59 / 12.86 / 135 | 0.784 / -1856.04 / 20.45 / 160 | |
| XM | mien_swap | 1.078 / 653.47 / 13.99 / 135 | 0.717 / -2550.7 / 25.51 / 160 | không |
| XM | swap_day_du | 1.017 / 143.94 / 15.73 / 135 | 0.667 / -3093.1 / 30.93 / 160 | không |
| Exness_Standard | mien_swap | 1.111 / 913.49 / 13.49 / 135 | 0.746 / -2242.53 / 22.98 / 160 | không |
| Exness_Standard | swap_day_du | 1.048 / 403.96 / 15.23 / 135 | 0.694 / -2784.93 / 27.85 / 160 | không |
| Exness_Raw | mien_swap | 1.127 / 1038.44 / 13.25 / 135 | 0.76 / -2094.44 / 22.01 / 160 | không |
| Exness_Raw | swap_day_du | 1.063 / 528.92 / 14.99 / 135 | 0.708 / -2636.84 / 26.37 / 160 | không |

## 3. Tóm tắt
- **IBS<0,2 US500 và US100: sống ở mọi sàn, mọi kịch bản** (PF 1,24–1,74 ở cả hai nửa). Đây là hai hệ duy nhất sống.
- **MRZ AUDUSD, MRZ GBPUSD, RSI EURJPY, MRZ GER40, MRZ EURGBP: chết** — lỗ ngay cả giá thô ở nửa 1 (trừ EURGBP: giá thô sống nhưng sau phí Exness nửa 1 PF < 1; trên XM CHƯA ĐO ĐƯỢC). Nửa 2 có lãi → dấu hiệu chỉ hợp giai đoạn gần đây / chọn sau khi nhìn.
- **MRZ USDCAD: chết** (nửa 2 lỗ ngay cả giá thô).
- **Sàn rẻ hơn:** với các hệ vào lúc 00h server, XM Ultra Low đắt hơn Exness ở mọi mã đã đo (spread 00h của XM cao). IBS (khớp lúc đóng cửa) XM chênh Exness Standard rất ít; Exness Raw rẻ nhất nhưng hoa hồng chỉ số CHƯA ĐO ĐƯỢC.

## 4. Bonus XM (chỉ đọc trang và PDF điều khoản công khai, 14/10/2026)
Nguồn: https://www.xm.com/bonus ; PDF "XMGlobal Terms and Conditions Deposit Bonus Promotion (Feb 2026)", "Deposit Trading Bonus Program NRCs", "Bonus Program 100%" trên cloud.xm-cdn.com. (Trang chính xm.com/promotions trả 403 khi đọc từ box.)
- **Quan trọng nhất: bonus KHÔNG áp dụng cho tài khoản Ultra Low** ("The Promotion is not applicable for holders of XM Ultra Low, Swap-Free and Shares trading account(s)"). Bonus chỉ cho tài khoản **Standard hoặc Micro**. Nghĩa là muốn có bonus thì phải chạy Standard (spread đo được gấp ~2 lần Ultra Low, ví dụ EURUSD H1 1,54 so với 0,72 bps) — các kết quả XM ở trên (Ultra Low) **không** áp dụng cho tài khoản có bonus.
- **Bonus tính vào margin:** có — XM mô tả bonus là "extra margin", hiện thành Credit cạnh Balance; Equity = Balance + Credit + lãi/lỗ đang mở.
- **Rút được không:** bonus **không rút được**. Lãi tạo ra thì rút được. Rút tiền hoặc chuyển nội bộ làm **mất bonus** (tuỳ chương trình: mất theo tỉ lệ số tiền rút, hoặc mất toàn bộ ngay). Tài khoản ngủ (dormant) mất hết bonus. XM có quyền huỷ bonus khi nghi lạm dụng và **không chịu trách nhiệm nếu huỷ bonus gây stop out**.
- **Ảnh hưởng tới drawdown / cháy tài khoản:** bonus giúp Equity cao hơn nên **lùi điểm stop out** (giữ lệnh lâu hơn khi lỗ), nhưng lỗ thật vẫn trừ vào tiền gửi của mình. Khi rút một phần lúc đang có lệnh, bonus bị trừ theo tỉ lệ → Equity giảm đột ngột → có thể bị stop out. Vì vậy: tính drawdown và cỡ lot theo **tiền gửi thật (Balance), không tính Credit**; coi Credit là đệm có thể biến mất bất cứ lúc nào. Bonus làm rủi ro "lỗ hết tiền gửi trước khi bị stop out" **tăng** (vì stop out xảy ra muộn hơn).
