# Vòng 25 — Đăng ký trước (12/10/2026 ~20:00 giờ VN), viết TRƯỚC khi chạy mô phỏng. MÔ PHỎNG.

## Nguồn EA
- 25 thư mục GitHub mới của Seeker (tải 12/10 16:40–17:00, commit 26521043), 201 gói MQL5 Code Base (vòng 19), 52 EA trong `data/cau_kho/ea_ra_co_che`.
- Đọc bằng bộ đọc HIỆN CÓ, KHÔNG sửa (`nhan/doc_ma.doc_chien_luoc`, MQL4 qua `nhan/mql4_chuan.chuan_hoa` — cùng đường với `nhan/cau_kho_ma.do_kho`).
  Kiểm kê trước khi chạy (đã đếm, chưa mô phỏng): 53 EA duy nhất ra ≥ 1 cơ chế, 85 cơ chế duy nhất (khử trùng theo vào/ra/chiều/giữ/SL-TP).
- Dịch tay (EA bộ đọc không dịch được, luật vào/ra rõ, ưu tiên có .set) — 4 EA:
  1. ASQ_SafeScalping (MQL5 71189, dùng .set `XAUUSD_M5_v2`): EMA50/200 cách ≥ 0,3 ATR50, close trên/dưới cả hai, phá đỉnh/đáy 15 nến (đệm 0,3 ATR),
     RSI14 trong [45,65] mua / [35,55] bán, close > close trước, EMA20/50 khung lớn (H1 cho M5/M15; khung ×4 cho khung khác), giờ 8–17 server (bỏ thứ Sáu sau 14h);
     SL 300 / TP 450 điểm, BE ở 150 điểm; trailing bắt đầu 200 điểm, cách 100 điểm. Bỏ: chốt từng phần, giới hạn 4 lệnh/ngày, lọc tin. Nhãn: breakout + xu hướng.
  2. EarnForex RSI_EA (GitHub): RSI14 cắt lên 20 → mua, cắt xuống 80 → bán; thoát ngược chiều khi cắt; không SL/TP (mặc định 0). Nhãn: đảo chiều.
  3. moving_average_cross.mq4 (GitHub): SMA12 cắt lên SMA40 (nến đã đóng) → mua; chỉ mua; SL 30 / TP 70 điểm. Nhãn: xu hướng.
  4. MACD_Sample.mq4 (GitHub, mẫu MetaQuotes): MACD(12,26,9) < 0 cắt lên signal, |MACD| > 3 điểm, EMA26 đi lên → mua (đối xứng bán); thoát khi cắt ngược với |MACD| > 2 điểm; TP 50 điểm, trailing 30 điểm. Nhãn: động lượng.
  Không dịch: EA dùng chỉ báo tự viết (vd. RSI_MA_Trader đọc buffer indicator riêng), ML/neural, lưới/hedge/martingale, tiện ích quản lý lệnh.
- "Điểm" = point của mã: FX 0,00001 (JPY 0,001), vàng 0,01, bạc 0,001, chỉ số/hàng hóa khác 0,01. Tham số gốc của EA (không tối ưu), kể cả khi khung/tài sản khác khung tác giả.

## Mô phỏng
- Cơ chế bộ đọc: phơi nhiễm `ngu_phap.sinh_tu_spec` (biết ở close i) → lệnh vào ở open i+1 khi phơi nhiễm 0 → ≠ 0; SL/TP theo `sltp` của bộ đọc
  (điểm hoặc hệ số ATR), `het_bar` nếu có; không có SL/TP hoặc có điều kiện ra → thoát ở open kế khi phơi nhiễm về 0. Cơ chế `trong_bar` chạy xấp xỉ theo close (ghi nhãn).
- Khung: M15, H1, H4 trên 8 chuỗi (7 FX + XAUUSD 2024–2026, tách 2025-05-15) và D1 trên 54 tài sản vòng 24 (từ 2004, tách 2015-04-01).
- Pooled: một luật chung; p chính = t gom cụm theo tuần vào lệnh; bootstrap khối tuần kiểm tra phụ (như `v24.py`). Trước phí và sau phí
  (spread ×1 + trượt 0,5 bps mỗi chiều + swap 2,5 %/năm; độ nhạy ×1,5 + trượt 1 bps). Mọi tài sản trừ drift nửa phát hiện. SL trước khi SL và TP cùng nến.
- Holm cộng dồn từ 12.457. SỐNG: như vòng 24.

## Ghép chéo (giới hạn)
- Chọn 10 cơ chế có trung bình sau phí NỬA PHÁT HIỆN cao nhất ở H1-pool và 10 ở D1-pool (không nhìn nửa kiểm).
- × 2 bộ lọc xu hướng (hướng Supertrend 10/4; giá cùng phía EMA200) × quản lý chandelier 22 nến × 3 ATR (thay thoát gốc) = 40 tổ hợp.
