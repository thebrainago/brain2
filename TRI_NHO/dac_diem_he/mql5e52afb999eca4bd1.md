# Đặc điểm hệ `mql5e52afb999eca4bd1`

- Nguồn: mt5_real_tick
- Kiểu vào / quản lý lệnh: vào theo CSV lệnh của nguồn; DCA ngược (nhồi khi lỗ); tối đa 9 tầng, hệ số lot 1.0; TP 0.003 % giá
- Trạng thái: **TRƯỢT — lãi dương nhưng không đủ 10 %/năm trước khi DD chạm 80 % (lợi thế mỏng so với rủi ro)**
- Số lần chạy hợp lệ: 3 (bị thay thế do lỗi lot CSV: 16)
- Tỉ lệ thắng: 74,8 %
- Năm có lãi: 2024 (+714), 2025 (+668), 2026 (-139)
- Thời gian giữ lệnh TB: CHƯA ĐO ĐƯỢC

## Mảnh tốt dùng lại được

- PF >= 1,3 ở ít nhất một biến thể
- DD thấp (< 15 %) mà vẫn có lãi — hợp làm mảnh nền / nâng lot
- chạy có lãi trên: EURGBP# H1
- tỉ lệ thắng cao (75 %) — điểm vào/TP nhỏ đáng giữ

## Các lần chạy

| Biến thể | Mã | Khung | Nguồn đo | Lot k | CAGR %/năm | DD % | PF | Lệnh |
|---|---|---|---|---|---|---|---|---|
| od_v2lotfix_y2025_mql5e52afb999eca4bd1_XM_CSV | EURGBP# | H1 | mt5_real_tick | 1.0 | 3,53 | 3,05 | 1,51 | 83 |
| od_v2lotfix_full_mql5e52afb999eca4bd1_XM_CSV | EURGBP# | H1 | mt5_real_tick | 1.0 | 3,21 | 2,97 | 1,51 | 111 |
| od_v2lotfix_y2024_mql5e52afb999eca4bd1_XM_CSV | EURGBP# | H1 | mt5_real_tick | 1.0 | 0,86 | 2,16 | 1,51 | 45 |
