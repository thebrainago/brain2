# Đặc điểm hệ `cb`

- Nguồn: https://www.mql5.com/en/code/48961
- Kiểu vào / quản lý lệnh: tham số: lotStart
- Trạng thái: **TRƯỢT — lãi dương nhưng không đủ 10 %/năm trước khi DD chạm 80 % (lợi thế mỏng so với rủi ro)**
- Số lần chạy hợp lệ: 9 (bị thay thế do lỗi lot CSV: 0)
- Tỉ lệ thắng: 98,5 %
- Năm có lãi: 2016 (+117), 2017 (+112), 2018 (+148), 2019 (+134), 2020 (+121), 2021 (+117), 2022 (+165), 2023 (+135), 2024 (+130), 2025 (+151), 2026 (-388)
- Thời gian giữ lệnh TB: CHƯA ĐO ĐƯỢC

## Mảnh tốt dùng lại được

- PF >= 1,3 ở ít nhất một biến thể
- DD thấp (< 15 %) mà vẫn có lãi — hợp làm mảnh nền / nâng lot
- có lãi 10/11 năm
- chạy có lãi trên: EURUSDmicro H1
- tỉ lệ thắng cao (98 %) — điểm vào/TP nhỏ đáng giữ

## Các lần chạy

| Biến thể | Mã | Khung | Nguồn đo | Lot k | CAGR %/năm | DD % | PF | Lệnh |
|---|---|---|---|---|---|---|---|---|
| cb_48961 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 4.0 | 3,02 | 27,72 | 2,97 | 478.0 |
| cb_48961 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 2.0 | 1,62 | 14,21 | 2,97 | 478.0 |
| cb_48961 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 1.0 | 0,84 | 7,19 | 2,97 | 478.0 |
| cb_71189 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 1.0 | -0,09 | 1,10 | 0,77 | 512.0 |
| cb_71189 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 2.0 | -0,18 | 2,19 | 0,77 | 512.0 |
| cb_71189 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 4.0 | -0,36 | 4,38 | 0,77 | 512.0 |
| cb_70796 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g5 | 4.0 | -44,41 | 100,01 | 0,61 | 603.0 |
| cb_70796 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g5 | 1.0 | -100,00 | 100,10 | 0,84 | 5974.0 |
| cb_70796 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g5 | 2.0 | -100,00 | 100,76 | 0,83 | 2897.0 |
