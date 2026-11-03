# Đặc điểm hệ `cb`

- Nguồn: https://www.mql5.com/en/code/71700
- Kiểu vào / quản lý lệnh: tham số: LOT_MULTIPLIER
- Trạng thái: **TRƯỢT — lãi dương nhưng không đủ 10 %/năm trước khi DD chạm 80 % (lợi thế mỏng so với rủi ro)**
- Số lần chạy hợp lệ: 17 (bị thay thế do lỗi lot CSV: 0)
- Tỉ lệ thắng: 38,4 %
- Năm có lãi: 2016 (-172), 2017 (-16), 2018 (+58), 2019 (-263), 2020 (-474), 2021 (-246), 2022 (-1080), 2023 (+176), 2024 (-149), 2025 (-79), 2026 (-61)
- Thời gian giữ lệnh TB: CHƯA ĐO ĐƯỢC

## Mảnh tốt dùng lại được

- PF >= 1,3 ở ít nhất một biến thể
- DD thấp (< 15 %) mà vẫn có lãi — hợp làm mảnh nền / nâng lot
- chạy có lãi trên: EURUSDmicro H1

## Các lần chạy

| Biến thể | Mã | Khung | Nguồn đo | Lot k | CAGR %/năm | DD % | PF | Lệnh |
|---|---|---|---|---|---|---|---|---|
| cb_48961 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 4.0 | 3,02 | 27,72 | 2,97 | 478.0 |
| cb_48961 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 2.0 | 1,62 | 14,21 | 2,97 | 478.0 |
| cb_48961 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 1.0 | 0,84 | 7,19 | 2,97 | 478.0 |
| cb_71189 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 1.0 | -0,09 | 1,10 | 0,77 | 512.0 |
| cb_70052 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_p5 | 1.0 | -0,09 | 1,10 | 0,77 | 512.0 |
| cb_71189 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 2.0 | -0,18 | 2,19 | 0,77 | 512.0 |
| cb_70052 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_p5 | 2.0 | -0,18 | 2,19 | 0,77 | 512.0 |
| cb_71189 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 4.0 | -0,36 | 4,38 | 0,77 | 512.0 |
| cb_70052 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_p5 | 4.0 | -0,36 | 4,38 | 0,77 | 512.0 |
| cb_58268 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_p5 | 1.0 | -2,41 | 24,84 | 0,74 | 315.0 |
| cb_58268 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_p5 | 2.0 | -5,60 | 48,95 | 0,74 | 315.0 |
| cb_71700 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g8 | 2.0 | -12,41 | 101,16 | 0,86 | 335.0 |
| cb_58268 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_p5 | 4.0 | -21,26 | 95,09 | 0,74 | 315.0 |
| cb_70796 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g5 | 4.0 | -44,41 | 100,01 | 0,61 | 603.0 |
| cb_70796 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g5 | 1.0 | -100,00 | 100,10 | 0,84 | 5974.0 |
| cb_70796 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g5 | 2.0 | -100,00 | 100,76 | 0,83 | 2897.0 |
| cb_71700 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g8 | 4.0 | -100,00 | 109,84 | 0,72 | 128.0 |
