# Vòng 28 — TIỀN ĐĂNG KÝ (ghi 13/10/2026 18h3x giờ VN, chu kỳ 4 vòng lặp, TRƯỚC khi chạy; MÔ PHỎNG)
Việc: hàng P1 trong `tai_lieu/VONG_LAP.md` việc 1, 2, 3, 4 (+ 7 = kiểm áp lực, không thêm ô Holm). Không xem kết quả trước khi ghi tệp này.

## Hệ gốc (cố định, không sửa tham số)
MRZ: z = (close − SMA50) / STD50 trên D1; z < −2 → mua, z > +2 → bán; tín hiệu ở close nến i, vào open nến i+1.
Dừng ban đầu E ∓ 1,5·ATR14(i); TR2 = trailing best_close ∓ 2·ATR14; giữ tối đa 72 nến (động cơ `v22.chay`).
"Vào 02h" = proxy như vòng 26/27: giá vào là open D1 Yahoo, spread lấy trung vị đo theo giờ lúc 02h server (`v26.sp_gio`).

## Dữ liệu, tách
D1 Yahoo `/workspace/du_lieu_ngay/v24` (`v24.tai_d1()`, từ 2004-01-01). Phát hiện < 2015-04-01 ≤ kiểm. W1 = resample W-FRI từ D1.

## Phí (lọc theo tầng)
1. TRƯỚC phí: spread 0, không trượt/swap (trừ drift nửa phát hiện như v24.tra). Cả hai nửa > 0 mới sang tầng 2; không thì dừng, vẫn tính 1 phép thử Holm với p = 1.
2. SAU phí XM: spread đo theo giờ 02h cho FX7 (AUDUSD, GBPUSD, NZDUSD, EURUSD, USDJPY, USDCAD, USDCHF); AUDCAD = bảng `v24.bps_of` (4 bps, CHƯA có spread đo) + trượt 0,5 bps/chiều + swap 2,5 %/năm (bảo thủ, KN 9).
3. ÁP LỰC (việc 7): spread ×1,5 + trượt 1 bps/chiều + swap 2,5 %/năm.

## Ô (11 ô Holm, ≤ 12)
| # | việc | nhóm tài sản | lọc / thoát | nhãn |
|---|---|---|---|---|
| 1 | P1-1 | POOL4 = AUDUSD+NZDUSD+AUDCAD+GBPUSD gộp n | MRZ gốc, TR2 | [hồi quy · FX pool · D1 02h · TR2 cố định] |
| 2 | P1-2 | AUDUSD | chỉ vào khi ADX14(i) < 20 HOẶC ATR14%(i) < trung vị 250 nến trước (shift 1); TR2 | [hồi quy × chế độ] |
| 3 | P1-2 | GBPUSD | như ô 2 | [hồi quy × chế độ] |
| 4 | P1-3 | AUDUSD | trailing 1,5·ATR | [hồi quy · trailing] |
| 5 | P1-3 | AUDUSD | trailing 2,5·ATR | [hồi quy · trailing] |
| 6 | P1-3 | AUDUSD | thoát thời gian: open sau 5 nến giữ, dừng ban đầu 1,5·ATR, không trailing | [hồi quy · thời gian] |
| 7 | P1-3 | GBPUSD | trailing 1,5·ATR | |
| 8 | P1-3 | GBPUSD | trailing 2,5·ATR | |
| 9 | P1-3 | GBPUSD | thoát thời gian 5 nến | |
| 10 | P1-4 | POOL4 | mua chỉ khi close W1 tuần đã đóng gần nhất (nhãn tuần ≤ ngày tín hiệu) > EMA20 W1; bán chỉ khi < | [hồi quy × xu hướng · FX pool · D1+W1 · TR2] |
| 11 | P1-4 | FX7 | như ô 10 | |

Tham chiếu (KHÔNG đếm Holm lại, đã đếm vòng 26): MRZ TR2 02h AUDUSD, GBPUSD đơn lẻ (cho P1-3 so TR2).
Báo thêm (mô tả, không Holm): phân rã từng tài sản trong POOL4.

## Thống kê, cổng QUA
p = t một phía gom cụm theo tuần vào lệnh trên nửa kiểm (`v24.p_cum`); p_boot = bootstrap khối tuần (`v24.p_boot`, RNG seed 2800+số ô).
Holm CỘNG DỒN từ 12.949 phép thử cũ (v27.holm_cu() + 16 ô vòng 27) + 11 ô này → 12.960.
QUA = Holm adj p < 0,05 VÀ p_boot < 0,05 VÀ sau phí dương CẢ HAI nửa VÀ áp lực kiểm > 0 VÀ maxDD < 80 %. < 30 lệnh/nửa → CHƯA ĐO ĐƯỢC (p = 1).
Kết quả = MÔ PHỎNG.
