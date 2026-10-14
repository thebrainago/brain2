# SO SÁNH SÀN — chuẩn mới: **XM Standard** (mã không hậu tố, tài khoản có bonus) — cập nhật 14/10/2026

**MÔ PHỎNG Python, KHÔNG PHẢI TIỀN THẬT.** Chưa đo thì ghi CHƯA ĐO ĐƯỢC.

## 1. Cách làm
- Giá: D1 Yahoo đang có (`/workspace/du_lieu_ngay/v24`, từ 2004; AUDUSD từ 2006-05) — chưa dùng Dukascopy D1 (chưa có đủ mã trên box).
- Mỗi lệnh danh nghĩa cố định 10.000 USD, không lãi kép; maxDD % so với 10.000 USD. Chia đôi giai đoạn theo thời gian.
- Định nghĩa hệ: xem docstring `so_sanh_san.py` (IBS<0,2 mua đóng cửa – bán đóng cửa hôm sau; MRZ z=±2, SL 1,5×ATR, thoát z cắt 0 / trail / 72 nến; RSI14 30/70).
- **XM_Standard (MẶC ĐỊNH, `phi_xm_that.TAI_KHOAN_MAC_DINH="Standard"`)**: spread theo giờ server từ `reports/phi_xm_micro_that.csv` (mã không hậu tố) cho AUDUSD, GBPUSD, USDCAD (00h). Swap Standard có swap_mode POINTS (tính thật) → **cả hai kịch bản đều trừ swap** (hai dòng trùng nhau). Hoa hồng 0. Trượt giá 0,5×spread mỗi chiều.
  - **ƯỚC (không phải đo):** GER40Cash#->Standard, US100Cash#->Standard, US500Cash#->Standard — CSV không có chỉ số bản Standard, nên spread = spread Ultra Low cùng giờ × tỉ lệ trung vị Standard/Ultra Low của 7 cặp FX đo được ở cùng giờ (23h: 1.82; 00h: 1.39). Swap chỉ số dùng mức của mã Cash# (MARGIN_CCY).
  - EURJPY, EURGBP: CHƯA ĐO ĐƯỢC ở cả Standard lẫn Ultra Low.
- XM_UltraLow, Exness_Standard, Exness_Raw: như bản trước (chỉ để so sánh). Hoa hồng Raw cho chỉ số CHƯA ĐO ĐƯỢC (đang tính 0).
- "Sống" = PF > 1 ở cả hai nửa.

## 2. Kết quả

### IBS<0.2 US500
Dữ liệu 2004-01-02..2026-10-09, mốc chia 2015-05-22.

| Sàn | Kịch bản swap | Nửa 1: PF / lãi ròng USD / maxDD % / số lệnh | Nửa 2: PF / lãi ròng USD / maxDD % / số lệnh | Sống? |
|---|---|---|---|---|
| (giá thô) | — | 1.737 / 14579.59 / 13.41 / 568 | 1.346 / 7362.23 / 13.13 / 552 | |
| XM_Standard | mien_swap | 1.568 / 11861.86 / 13.84 / 568 | 1.21 / 4727.46 / 14.08 / 552 | CÓ |
| XM_Standard | swap_day_du | 1.568 / 11861.86 / 13.84 / 568 | 1.21 / 4727.46 / 14.08 / 552 | CÓ |
| XM_UltraLow | mien_swap | 1.607 / 12516.79 / 13.75 / 568 | 1.242 / 5363.94 / 13.62 / 552 | CÓ |
| XM_UltraLow | swap_day_du | 1.607 / 12516.79 / 13.75 / 568 | 1.242 / 5363.94 / 13.62 / 552 | CÓ |
| Exness_Standard | mien_swap | 1.688 / 13820.03 / 13.51 / 568 | 1.306 / 6624.06 / 13.32 / 552 | CÓ |
| Exness_Standard | swap_day_du | 1.61 / 12557.69 / 13.74 / 568 | 1.244 / 5403.69 / 13.61 / 552 | CÓ |
| Exness_Raw | mien_swap | 1.737 / 14579.59 / 13.41 / 568 | 1.346 / 7362.23 / 13.13 / 552 | CÓ |
| Exness_Raw | swap_day_du | 1.656 / 13317.25 / 13.63 / 568 | 1.281 / 6141.85 / 13.42 / 552 | CÓ |

### IBS<0.2 US100
Dữ liệu 2004-01-02..2026-10-09, mốc chia 2015-05-22.

| Sàn | Kịch bản swap | Nửa 1: PF / lãi ròng USD / maxDD % / số lệnh | Nửa 2: PF / lãi ròng USD / maxDD % / số lệnh | Sống? |
|---|---|---|---|---|
| (giá thô) | — | 1.562 / 13312.76 / 18.17 / 555 | 1.616 / 15146.02 / 14.96 / 545 | |
| XM_Standard | mien_swap | 1.431 / 10688.48 / 18.83 / 555 | 1.492 / 12624.04 / 15.96 / 545 | CÓ |
| XM_Standard | swap_day_du | 1.431 / 10688.48 / 18.83 / 555 | 1.492 / 12624.04 / 15.96 / 545 | CÓ |
| XM_UltraLow | mien_swap | 1.459 / 11265.86 / 18.68 / 555 | 1.519 / 13191.02 / 15.74 / 545 | CÓ |
| XM_UltraLow | swap_day_du | 1.459 / 11265.86 / 18.68 / 555 | 1.519 / 13191.02 / 15.74 / 545 | CÓ |
| Exness_Standard | mien_swap | 1.528 / 12646.65 / 18.35 / 555 | 1.583 / 14491.91 / 15.21 / 545 | CÓ |
| Exness_Standard | swap_day_du | 1.46 / 11305.45 / 18.67 / 555 | 1.521 / 13229.89 / 15.72 / 545 | CÓ |
| Exness_Raw | mien_swap | 1.561 / 13291.98 / 18.18 / 555 | 1.615 / 15125.61 / 14.97 / 545 | CÓ |
| Exness_Raw | swap_day_du | 1.492 / 11950.77 / 18.49 / 555 | 1.552 / 13863.58 / 15.48 / 545 | CÓ |

### MRZ AUDUSD z2 SMA50 trail3
Dữ liệu 2006-05-15..2026-10-12, mốc chia 2016-07-28.

| Sàn | Kịch bản swap | Nửa 1: PF / lãi ròng USD / maxDD % / số lệnh | Nửa 2: PF / lãi ròng USD / maxDD % / số lệnh | Sống? |
|---|---|---|---|---|
| (giá thô) | — | 0.799 / -2769.16 / 38.47 / 112 | 1.59 / 4455.98 / 10.95 / 100 | |
| XM_Standard | mien_swap | 0.717 / -4152.84 / 48.33 / 112 | 1.374 / 3090.21 / 14.51 / 100 | không |
| XM_Standard | swap_day_du | 0.717 / -4152.84 / 48.33 / 112 | 1.374 / 3090.21 / 14.51 / 100 | không |
| XM_UltraLow | mien_swap | 0.757 / -3477.29 / 43.66 / 112 | 1.484 / 3823.72 / 12.51 / 100 | không |
| XM_UltraLow | swap_day_du | 0.733 / -3863.12 / 46.21 / 112 | 1.412 / 3348.89 / 13.7 / 100 | không |
| Exness_Standard | mien_swap | 0.773 / -3203.83 / 41.65 / 112 | 1.524 / 4067.88 / 11.75 / 100 | không |
| Exness_Standard | swap_day_du | 0.749 / -3589.66 / 44.21 / 112 | 1.45 / 3593.06 / 12.95 / 100 | không |
| Exness_Raw | mien_swap | 0.782 / -3048.95 / 40.5 / 112 | 1.544 / 4186.39 / 11.38 / 100 | không |
| Exness_Raw | swap_day_du | 0.758 / -3434.78 / 43.05 / 112 | 1.469 / 3711.57 / 12.57 / 100 | không |

### MRZ GBPUSD SMA20 hold72
Dữ liệu 2004-01-01..2026-10-12, mốc chia 2015-05-23.

| Sàn | Kịch bản swap | Nửa 1: PF / lãi ròng USD / maxDD % / số lệnh | Nửa 2: PF / lãi ròng USD / maxDD % / số lệnh | Sống? |
|---|---|---|---|---|
| (giá thô) | — | 0.863 / -1280.41 / 14.98 / 145 | 1.283 / 2571.91 / 10.54 / 158 | |
| XM_Standard | mien_swap | 0.751 / -2462.02 / 26.71 / 145 | 1.118 / 1143.5 / 12.43 / 158 | không |
| XM_Standard | swap_day_du | 0.751 / -2462.02 / 26.71 / 145 | 1.118 / 1143.5 / 12.43 / 158 | không |
| XM_UltraLow | mien_swap | 0.803 / -1895.16 / 21.08 / 145 | 1.202 / 1902.05 / 11.05 / 158 | không |
| XM_UltraLow | swap_day_du | 0.772 / -2220.49 / 24.31 / 145 | 1.146 / 1406.68 / 11.65 / 158 | không |
| Exness_Standard | mien_swap | 0.833 / -1586.25 / 18.02 / 145 | 1.242 / 2238.65 / 10.8 / 158 | không |
| Exness_Standard | swap_day_du | 0.801 / -1911.59 / 21.24 / 145 | 1.184 / 1743.28 / 11.15 / 158 | không |
| Exness_Raw | mien_swap | 0.845 / -1456.86 / 16.73 / 145 | 1.256 / 2360.47 / 10.71 / 158 | không |
| Exness_Raw | swap_day_du | 0.813 / -1782.19 / 19.96 / 145 | 1.199 / 1865.1 / 11.06 / 158 | không |

### RSI EURJPY
Dữ liệu 2004-01-01..2026-10-12, mốc chia 2015-05-23.

| Sàn | Kịch bản swap | Nửa 1: PF / lãi ròng USD / maxDD % / số lệnh | Nửa 2: PF / lãi ròng USD / maxDD % / số lệnh | Sống? |
|---|---|---|---|---|
| (giá thô) | — | 0.753 / -2229.65 / 40.22 / 87 | 1.351 / 1681.28 / 8.94 / 79 | |
| XM_Standard | mien_swap | CHƯA ĐO ĐƯỢC (spread/swap XM cho ma nay CHUA DO DUOC (khong co trong phi_xm_micro_that.csv)) | | |
| XM_Standard | swap_day_du | CHƯA ĐO ĐƯỢC (spread/swap XM cho ma nay CHUA DO DUOC (khong co trong phi_xm_micro_that.csv)) | | |
| XM_UltraLow | mien_swap | CHƯA ĐO ĐƯỢC (spread/swap XM cho ma nay CHUA DO DUOC (khong co trong phi_xm_micro_that.csv)) | | |
| XM_UltraLow | swap_day_du | CHƯA ĐO ĐƯỢC (spread/swap XM cho ma nay CHUA DO DUOC (khong co trong phi_xm_micro_that.csv)) | | |
| Exness_Standard | mien_swap | 0.709 / -2716.37 / 42.71 / 87 | 1.246 / 1239.31 / 9.95 / 79 | không |
| Exness_Standard | swap_day_du | CHƯA ĐO ĐƯỢC (swap day du Exness CHUA DO DUOC (khong co muc swap proxy)) | | |
| Exness_Raw | mien_swap | 0.724 / -2542.34 / 41.73 / 87 | 1.281 / 1390.59 / 9.61 / 79 | không |
| Exness_Raw | swap_day_du | CHƯA ĐO ĐƯỢC (swap day du Exness CHUA DO DUOC (khong co muc swap proxy)) | | |

### MRZ GER40
Dữ liệu 2004-01-02..2026-10-12, mốc chia 2015-05-23.

| Sàn | Kịch bản swap | Nửa 1: PF / lãi ròng USD / maxDD % / số lệnh | Nửa 2: PF / lãi ròng USD / maxDD % / số lệnh | Sống? |
|---|---|---|---|---|
| (giá thô) | — | 0.671 / -8013.77 / 93.75 / 153 | 1.479 / 7844.22 / 28.86 / 164 | |
| XM_Standard | mien_swap | 0.607 / -10059.16 / 109.15 / 153 | 1.31 / 5414.95 / 29.55 / 164 | không |
| XM_Standard | swap_day_du | 0.607 / -10059.16 / 109.15 / 153 | 1.31 / 5414.95 / 29.55 / 164 | không |
| XM_UltraLow | mien_swap | 0.618 / -9678.44 / 105.86 / 153 | 1.337 / 5823.04 / 29.4 / 164 | không |
| XM_UltraLow | swap_day_du | 0.618 / -9678.44 / 105.86 / 153 | 1.337 / 5823.04 / 29.4 / 164 | không |
| Exness_Standard | mien_swap | 0.647 / -8792.41 / 98.12 / 153 | 1.417 / 7009.6 / 29.16 / 164 | không |
| Exness_Standard | swap_day_du | 0.624 / -9487.99 / 104.22 / 153 | 1.351 / 6027.18 / 29.33 / 164 | không |
| Exness_Raw | mien_swap | 0.667 / -8141.22 / 94.41 / 153 | 1.469 / 7707.61 / 28.91 / 164 | không |
| Exness_Raw | swap_day_du | 0.643 / -8836.8 / 98.6 / 153 | 1.401 / 6725.19 / 29.07 / 164 | không |

### MRZ EURGBP
Dữ liệu 2004-01-01..2026-10-12, mốc chia 2015-05-23.

| Sàn | Kịch bản swap | Nửa 1: PF / lãi ròng USD / maxDD % / số lệnh | Nửa 2: PF / lãi ròng USD / maxDD % / số lệnh | Sống? |
|---|---|---|---|---|
| (giá thô) | — | 1.086 / 683.94 / 17.79 / 159 | 1.328 / 2310.49 / 10.7 / 153 | |
| XM_Standard | mien_swap | CHƯA ĐO ĐƯỢC (spread/swap XM cho ma nay CHUA DO DUOC (khong co trong phi_xm_micro_that.csv)) | | |
| XM_Standard | swap_day_du | CHƯA ĐO ĐƯỢC (spread/swap XM cho ma nay CHUA DO DUOC (khong co trong phi_xm_micro_that.csv)) | | |
| XM_UltraLow | mien_swap | CHƯA ĐO ĐƯỢC (spread/swap XM cho ma nay CHUA DO DUOC (khong co trong phi_xm_micro_that.csv)) | | |
| XM_UltraLow | swap_day_du | CHƯA ĐO ĐƯỢC (spread/swap XM cho ma nay CHUA DO DUOC (khong co trong phi_xm_micro_that.csv)) | | |
| Exness_Standard | mien_swap | 0.956 / -371.14 / 23.11 / 159 | 1.173 / 1295.23 / 12.03 / 153 | không |
| Exness_Standard | swap_day_du | CHƯA ĐO ĐƯỢC (swap day du Exness CHUA DO DUOC (khong co muc swap proxy)) | | |
| Exness_Raw | mien_swap | 0.998 / -15.79 / 20.89 / 159 | 1.221 / 1622.45 / 11.6 / 153 | không |
| Exness_Raw | swap_day_du | CHƯA ĐO ĐƯỢC (swap day du Exness CHUA DO DUOC (khong co muc swap proxy)) | | |

### MRZ USDCAD
Dữ liệu 2004-01-01..2026-10-12, mốc chia 2015-05-23.

| Sàn | Kịch bản swap | Nửa 1: PF / lãi ròng USD / maxDD % / số lệnh | Nửa 2: PF / lãi ròng USD / maxDD % / số lệnh | Sống? |
|---|---|---|---|---|
| (giá thô) | — | 1.154 / 1239.59 / 12.86 / 135 | 0.784 / -1856.04 / 20.45 / 160 | |
| XM_Standard | mien_swap | 0.997 / -26.19 / 16.06 / 135 | 0.65 / -3294.74 / 32.95 / 160 | không |
| XM_Standard | swap_day_du | 0.997 / -26.19 / 16.06 / 135 | 0.65 / -3294.74 / 32.95 / 160 | không |
| XM_UltraLow | mien_swap | 1.078 / 653.47 / 13.99 / 135 | 0.717 / -2550.7 / 25.51 / 160 | không |
| XM_UltraLow | swap_day_du | 1.017 / 143.94 / 15.73 / 135 | 0.667 / -3093.1 / 30.93 / 160 | không |
| Exness_Standard | mien_swap | 1.111 / 913.49 / 13.49 / 135 | 0.746 / -2242.53 / 22.98 / 160 | không |
| Exness_Standard | swap_day_du | 1.048 / 403.96 / 15.23 / 135 | 0.694 / -2784.93 / 27.85 / 160 | không |
| Exness_Raw | mien_swap | 1.127 / 1038.44 / 13.25 / 135 | 0.76 / -2094.44 / 22.01 / 160 | không |
| Exness_Raw | swap_day_du | 1.063 / 528.92 / 14.99 / 135 | 0.708 / -2636.84 / 26.37 / 160 | không |

## 3. Tóm tắt (XM Standard)
- **Sống: IBS<0,2 US500** (PF 1.568 / 1.21) và **IBS<0,2 US100** (PF 1.431 / 1.492). Spread chỉ số Standard là ƯỚC.
- Chết: MRZ AUDUSD, MRZ GBPUSD, MRZ GER40 (nửa 1 PF < 1), MRZ USDCAD (cả hai nửa PF < 1). RSI EURJPY, MRZ EURGBP: phí XM CHƯA ĐO ĐƯỢC (giá thô nửa 1 của EURJPY đã lỗ).

## 4. Rủi ro bonus — tính maxDD và cỡ lot theo TIỀN GỬI THẬT, không tính Credit
Điều khoản công khai (xm.com/bonus, PDF điều khoản trên cloud.xm-cdn.com): bonus là Credit (margin thêm), không rút được; rút tiền/chuyển nội bộ làm mất bonus (theo tỉ lệ hoặc toàn bộ tuỳ chương trình); tài khoản ngủ mất bonus; XM có thể huỷ bonus và không chịu trách nhiệm nếu việc huỷ gây stop out.
Quy tắc từ nay:
1. **Cỡ lot tính trên Balance (tiền gửi), bỏ Credit.** Với danh nghĩa 10.000 USD/lệnh như mô phỏng (đòn bẩy 1× trên 10.000 USD tiền gửi): US500Cash ≈ 1.28 lot, US100Cash ≈ 0.33 lot (giá 13/10/2026; lot tối thiểu chỉ số 0,1).
2. **maxDD tính trên tiền gửi.** Nếu lỡ tính lot theo Balance + Credit với bonus 100% thì danh nghĩa gấp đôi → maxDD trên tiền gửi gấp đôi:

| Hệ (XM Standard) | maxDD nửa 1 / nửa 2 (lot theo tiền gửi) | Nếu lot theo Balance+Credit (bonus 100%) |
|---|---|---|
| IBS<0.2 US500 | 1383.78 USD = 13.84% / 1408.39 USD = 14.08% | 27.68% / 28.16% |
| IBS<0.2 US100 | 1883.17 USD = 18.83% / 1595.59 USD = 15.96% | 37.66% / 31.92% |

3. Stop out kiểm tra theo Equity = Balance + Credit + lãi/lỗ mở; Credit làm stop out xảy ra muộn hơn → có thể lỗ gần hết tiền gửi trước khi bị đóng lệnh. Đặt ngưỡng dừng riêng theo tiền gửi (ví dụ dừng hệ khi lỗ vượt maxDD lịch sử × 1,5 tính trên Balance) thay vì dựa vào stop out.
4. Không rút tiền khi đang có lệnh mở (bonus bị trừ ngay → Equity tụt → có thể stop out).
5. Bonus chỉ áp dụng Standard/Micro; Ultra Low không có bonus.
