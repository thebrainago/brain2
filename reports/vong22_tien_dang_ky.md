# Vòng 22 — Đăng ký trước (12/10/2026 16:3x giờ VN), viết TRƯỚC khi chạy. MÔ PHỎNG.

Mục tiêu: chạy lại các nhóm chiến lược chính của vòng 19 và chiến lược EMA vòng 21 trên M5, M15, M30, H1, H4, D1, W1.

## Dữ liệu
- Bộ 1 (2024–2026): 7 cặp FX, M5 HistData (BID) + spread THẬT theo giờ = `spread_tb` của H1 tick bid/ask cùng giờ, × 1,2 (markup XM). Gộp M15/M30/H1/H4 từ M5.
- Bộ 2: EURUSD 2018–2023 M5 (spread cố định 1,4 pip — không có ask), NZDUSD 2018–2023 M5 + spread thật theo giờ từ Dukascopy H1 bid/ask (`spread_open`), AUDCAD 2008–2023 M5 (spread cố định 2,5 pip), XAUUSD M5 2024–2026 (spread cố định 2 bps).
- US500/UK100: chỉ có H1 Yahoo → chạy H1, H4; M5–M30: CHƯA ĐO ĐƯỢC (không có nguồn miễn phí đủ dài).
- D1/W1: Yahoo EURUSD, USDJPY, AUDUSD, GBPUSD, S&P 500, vàng (như vòng 21); W1 gộp từ D1.

## Lưới (cố định / chuỗi × khung)
- 16 tín hiệu × 2 thoát (TP 1×ATR/SL 1,5×ATR; trailing 2×ATR), giữ tối đa 72 nến:
  ĐỘNG LƯỢNG ROC24, MACD0; BREAKOUT DINH20; ĐẢO CHIỀU RSI; MR MRZ; XU HƯỚNG DÀI DONCHIAN55, MA50_200; ĐA KHUNG MTF; GAP GAP_FILL;
  NEWS NEWS_FADE; SMC SWEEP, FVG; NẾN ENGULF, PINBAR; PHIÊN PHIEN_A, OPENING_RANGE (định nghĩa giữ nguyên vòng 19, tính theo số nến).
- EMA (vòng 21, lọc KHÔNG, thêm KHÔNG): MR EMA20 k2, MR EMA50 k3, PB EMA20 k2, PB EMA50 k2;
  ĐA KHUNG (phần chưa làm vòng 21): MR EMA20 k2 và PB EMA50 k2 chỉ lấy lệnh cùng hướng độ dốc EMA50 của khung lớn hơn 4 lần (đã đóng, không lookahead).
- 38 ô / chuỗi × khung; tổng ≈ 38 × 71 = 2.698 ô (sửa đếm trước khi chạy: 16 tín hiệu, không phải 15).

## Chi phí và phép thử
- TRƯỚC PHÍ: spread 0, trượt 0, không swap (chỉ để xem lợi thế thô).
- SAU PHÍ (chính): spread × 1 + trượt 0,5 pip mỗi chiều + swap (T-bill+2,5%/năm ≈ 2,5%/năm theo ngày giữ). Độ nhạy: trượt 0/1 pip, spread ×1,5.
- Pip: 0,0001 FX, 0,01 JPY, 0,1 USD vàng, 1 điểm chỉ số.
- Chia nửa đầu (phát hiện)/nửa sau (kiểm) theo thời gian; p một phía trên nửa kiểm; chỉ số/vàng trừ drift của nửa phát hiện.
- SL chạm trước khi SL và TP cùng nến; vào lệnh ở open nến kế tiếp.
- Holm cộng dồn từ 8.935 (+ toàn bộ ô SAU PHÍ đủ lệnh). Holm riêng cho TRƯỚC PHÍ chỉ để tham khảo, không phải cổng.
- SỐNG: Holm < 0,05, lãi cả hai nửa SAU PHÍ, lãi nửa kiểm ở spread × 1,5 và trượt 1 pip, maxDD < 80 %.
- Báo phí/lệnh (bps) so với biên độ |lãi/lỗ thô| trung bình mỗi lệnh.
