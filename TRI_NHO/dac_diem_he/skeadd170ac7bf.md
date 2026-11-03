# Đặc điểm hệ `skeadd170ac7bf`

- Nguồn: mt5_real_tick
- Kiểu vào / quản lý lệnh: vào theo CSV lệnh của nguồn; DCA ngược (nhồi khi lỗ); tối đa 9 tầng, hệ số lot 1.6; TP 0.005 % giá
- Trạng thái: **TRƯỢT — lãi dương nhưng không đủ 10 %/năm trước khi DD chạm 80 % (lợi thế mỏng so với rủi ro)**
- Số lần chạy hợp lệ: 2 (bị thay thế do lỗi lot CSV: 6)
- Tỉ lệ thắng: 57,8 %
- Năm có lãi: 2024 (+489), 2025 (+358), 2026 (+1453)
- Thời gian giữ lệnh TB: CHƯA ĐO ĐƯỢC

## Mảnh tốt dùng lại được

- PF >= 1,3 ở ít nhất một biến thể
- DD thấp (< 15 %) mà vẫn có lãi — hợp làm mảnh nền / nâng lot
- có lãi 3/3 năm
- chạy có lãi trên: USDCAD# H1

## Các lần chạy

| Biến thể | Mã | Khung | Nguồn đo | Lot k | CAGR %/năm | DD % | PF | Lệnh |
|---|---|---|---|---|---|---|---|---|
| od_v2r2p_b120_skeadd170ac7bf_XM_CSV | USDCAD# | H1 | mt5_real_tick | 1.0 | 6,63 | 8,60 | 4,42 | 99 |
| od_v2r2p_b50_skeadd170ac7bf_XM_CSV | USDCAD# | H1 | mt5_real_tick | 1.0 | -100,00 | 100,00 | 4,42 | 19 |
