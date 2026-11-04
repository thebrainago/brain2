# Đặc điểm hệ `cb`

- Nguồn: https://www.mql5.com/en/code/69545
- Kiểu vào / quản lý lệnh: tham số: iLots
- Trạng thái: **TRƯỢT — lãi dương nhưng không đủ 10 %/năm trước khi DD chạm 80 % (lợi thế mỏng so với rủi ro)**
- Số lần chạy hợp lệ: 44 (bị thay thế do lỗi lot CSV: 0)
- Tỉ lệ thắng: 31,4 %
- Năm có lãi: 2016 (-541), 2017 (-66), 2018 (-602), 2019 (-1616), 2020 (-676), 2021 (-1376), 2022 (-793), 2023 (-262), 2024 (-1025), 2025 (-953), 2026 (-1224)
- Thời gian giữ lệnh TB: CHƯA ĐO ĐƯỢC

## Mảnh tốt dùng lại được

- PF >= 1,3 ở ít nhất một biến thể
- DD thấp (< 15 %) mà vẫn có lãi — hợp làm mảnh nền / nâng lot
- chạy có lãi trên: EURUSDmicro H1, GOLDmicro H1

## Các lần chạy

| Biến thể | Mã | Khung | Nguồn đo | Lot k | CAGR %/năm | DD % | PF | Lệnh |
|---|---|---|---|---|---|---|---|---|
| cb_48961 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 4.0 | 3,02 | 27,72 | 2,97 | 478.0 |
| cb_62713 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g1 | 2.0 | 2,07 | 41,19 | 2,06 | 431.0 |
| cb_62713 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g1 | 4.0 | 1,87 | 51,99 | 1,35 | 414.0 |
| cb_48961 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 2.0 | 1,62 | 14,21 | 2,97 | 478.0 |
| cb_62713 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g1 | 1.0 | 1,61 | 25,86 | 1,79 | 406.0 |
| cb_48961 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 1.0 | 0,84 | 7,19 | 2,97 | 478.0 |
| cb_72278 | GOLDmicro | H1 | mt5_tho_desktop-05pnlgf_g1 | 2.0 | 0,17 | 19,41 | 1,01 | 1746.0 |
| cb_74582 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g1 | 1.0 | -0,01 | 0,80 | 0,99 | 497.0 |
| cb_74582 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g1 | 2.0 | -0,01 | 1,60 | 0,99 | 497.0 |
| cb_74582 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g1 | 4.0 | -0,02 | 3,19 | 0,99 | 497.0 |
| cb_71189 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 1.0 | -0,09 | 1,10 | 0,77 | 512.0 |
| cb_70052 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_p5 | 1.0 | -0,09 | 1,10 | 0,77 | 512.0 |
| cb_71189 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 2.0 | -0,18 | 2,19 | 0,77 | 512.0 |
| cb_70052 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_p5 | 2.0 | -0,18 | 2,19 | 0,77 | 512.0 |
| cb_72278 | GOLDmicro | H1 | mt5_tho_desktop-05pnlgf_g1 | 1.0 | -0,31 | 21,97 | 0,96 | 1494.0 |
| cb_71189 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 4.0 | -0,36 | 4,38 | 0,77 | 512.0 |
| cb_70052 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_p5 | 4.0 | -0,36 | 4,38 | 0,77 | 512.0 |
| cb_72278 | GOLDmicro | H1 | mt5_tho_desktop-05pnlgf_g1 | 4.0 | -0,60 | 22,15 | 0,97 | 1697.0 |
| cb_62684 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g11 | 1.0 | -0,67 | 8,56 | 0,89 | 1235.0 |
| cb_74135 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 1.0 | -0,78 | 24,27 | 0,97 | 1518.0 |
| cb_63698 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g10 | 1.0 | -0,89 | 11,15 | 0,92 | 780.0 |
| cb_62684 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g11 | 2.0 | -1,39 | 16,95 | 0,89 | 1235.0 |
| cb_74135 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 2.0 | -1,62 | 41,62 | 0,97 | 1518.0 |
| cb_63698 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g10 | 2.0 | -1,87 | 21,94 | 0,92 | 780.0 |
| cb_58268 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_p5 | 1.0 | -2,41 | 24,84 | 0,74 | 315.0 |
| cb_62684 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g11 | 4.0 | -2,88 | 32,26 | 0,89 | 1231.0 |
| cb_48139 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 1.0 | -3,47 | 45,77 | 0,94 | 2780.0 |
| cb_74135 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 4.0 | -3,56 | 64,77 | 0,97 | 1518.0 |
| cb_63698 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g10 | 4.0 | -4,17 | 42,53 | 0,92 | 780.0 |
| cb_58268 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_p5 | 2.0 | -5,60 | 48,95 | 0,74 | 315.0 |
| cb_48139 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 2.0 | -8,87 | 79,40 | 0,94 | 2780.0 |
| cb_71700 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g8 | 2.0 | -12,41 | 101,16 | 0,86 | 335.0 |
| cb_69545 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g5 | 1.0 | -20,35 | 91,44 | 0,91 | 69845.0 |
| cb_58268 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_p5 | 4.0 | -21,26 | 95,09 | 0,74 | 315.0 |
| cb_70796 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g5 | 4.0 | -44,41 | 100,01 | 0,61 | 603.0 |
| cb_69545 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g5 | 2.0 | -47,26 | 100,03 | 0,91 | 38834.0 |
| cb_70796 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g5 | 1.0 | -100,00 | 100,10 | 0,84 | 5974.0 |
| cb_70796 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g5 | 2.0 | -100,00 | 100,76 | 0,83 | 2897.0 |
| cb_71700 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g8 | 4.0 | -100,00 | 109,84 | 0,72 | 128.0 |
| cb_48139 | EURUSDmicro | H1 | mt5_tho_desktop-05pnlgf_g2 | 4.0 | -100,00 | 100,41 | 0,93 | 1720.0 |
