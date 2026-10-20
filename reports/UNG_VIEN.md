# Ứng viên MT5 (cộng dồn, tự sinh bởi `mt5tools/bao_cao_phien.py`)

Mỗi hệ một dòng, số **đo thật** từ báo cáo MT5 real tick (`reports/ong_dan/ket_qua_mt5/od_*.htm`), tài khoản XM micro 1:500, vốn trong báo cáo (1.000 USD). **Chuẩn cuối (kiểm toán 20/10/2026):**

- **%/năm:** lãi **kép** (chặt hơn lãi đơn) trên **kỳ trong báo cáo**, tính bằng (1 + lãi ròng/vốn)^(1/số năm) − 1. Đạt khi ≥ 10 %.
- **Sụt giảm:** lấy theo **vốn (equity)**, là số lớn hơn giữa *Equity Drawdown Maximal %* và *Relative %*. Đạt khi ≤ 80 %.
- **Loại:** có stop-out thì TRƯỢT. Sai symbol (không phải `*micro` của việc) hoặc tick < 90 % thì CHƯA ĐO ĐƯỢC.
- **Phí:** spread và swap đã nằm trong báo cáo real tick. Hoa hồng trong báo cáo XM micro bằng 0, hoa hồng thật **CHƯA ĐO ĐƯỢC**.
- **Trùng:** cùng thẻ + symbol + TF, hoặc cùng kết quả, chỉ đếm một lần.

Cập nhật: 20/10/2026 20:01 (giờ máy chạy). Đếm (không trùng): ĐẠT 30, TRƯỢT 9, CHƯA ĐO ĐƯỢC 6; trùng bỏ 0.

## Bảng xếp hạng (ĐẠT, không trùng, theo %/năm kép)

| # | id | Symbol | TF | Lãi ròng | %/năm kép | %/năm đơn | DD vốn % | Lệnh | Số năm | Py/MT5 | Điểm yếu |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | od_skea44640140cc_XM_CSV | GBPCADmicro | H1 | 10075.87 | 138.61 | 364.38 | 45.83 | 616 | 2.77 | 1.03 | — |
| 2 | od_tohop16b0d75bb149f634_XM_CSV | GBPCADmicro | H1 | 5078.62 | 92.19 | 183.84 | 55.87 | 127 | 2.76 | 0.97 | — |
| 3 | od_skea0075f624b3_XM_CSV | GBPNZDmicro | H1 | 4922.39 | 91.25 | 179.43 | 52.77 | 139 | 2.74 | 1.02 | — |
| 4 | od_skea0ca971ac32_XM_CSV | GBPNZDmicro | H4 | 4533.59 | 85.88 | 164.28 | 50.61 | 27 | 2.76 | 1.13 | ít lệnh (27 < 30) |
| 5 | od_skstadd3a54f8edcbce2_XM_CSV | EURUSDmicro | H1 | 1042.87 | 70.32 | 77.74 | 60.76 | 15 | 1.34 | 1.05 | ít lệnh (15 < 30); lịch sử ngắn (1.3 năm) |
| 6 | od_mql5f3313c2c79f00c10_XM_CSV | EURGBPmicro | H4 | 3026.52 | 66.07 | 110.21 | 50.64 | 178 | 2.75 | 1.03 | — |
| 7 | od_skeaa7cd39087e_XM_CSV | GOLDmicro | H1 | 2665.71 | 59.96 | 96.40 | 60.59 | 351 | 2.77 | 0.69 | Python/MT5 0.69 ngoài 0,8–1,25 |
| 8 | od_skeaff87f96be7_XM_CSV | GBPCADmicro | H1 | 2247.33 | 53.30 | 81.51 | 31.72 | 211 | 2.76 | 1.05 | — |
| 9 | od_skea3279057100_XM_CSV | EURGBPmicro | H1 | 1779.61 | 44.73 | 64.36 | 64.02 | 203 | 2.77 | -0.57 | 10 lệnh còn mở bị đóng cuối kỳ; Python/MT5 -0.57 ngoài 0,8–1,25 |
| 10 | od_b0be91a35f43f34a_XM_CSV | USDCADmicro | H4 | 1684.11 | 43.95 | 62.13 | 58.65 | 46 | 2.71 | 0.95 | không đóng lệnh lỗ nào (PF vô hạn; DD vốn 59%) |
| 11 | od_skea02906b7d6a_XM_CSV | GOLDmicro | H4 | 1496.80 | 39.22 | 54.13 | 70.34 | 180 | 2.77 | 0.13 | Python/MT5 0.13 ngoài 0,8–1,25 |
| 12 | od_skea8897567020_XM_CSV | GBPNZDmicro | H1 | 1400.85 | 37.26 | 50.66 | 45.65 | 154 | 2.77 | 1.24 | — |
| 13 | od_skstc21c2acd239f3c87_XM_CSV | EURUSDmicro | H1 | 525.66 | 37.01 | 39.18 | 49.71 | 20 | 1.34 | 1.01 | ít lệnh (20 < 30); lịch sử ngắn (1.3 năm) |
| 14 | od_skea5049c79288_XM_CSV | GBPCADmicro | H4 | 1246.00 | 34.79 | 45.97 | 30.42 | 83 | 2.71 | 1.15 | — |
| 15 | od_mql5fd4bc285e11ab5a1_XM_CSV | EURCHFmicro | H4 | 1106.60 | 30.96 | 40.06 | 49.29 | 138 | 2.76 | 0.76 | 5 lệnh còn mở bị đóng cuối kỳ; Python/MT5 0.76 ngoài 0,8–1,25 |
| 16 | od_mql5e3c3e4f028dbab72_XM_CSV | EURCADmicro | H4 | 1023.49 | 29.03 | 37.01 | 18.35 | 120 | 2.77 | 1.07 | 3 lệnh còn mở bị đóng cuối kỳ |
| 17 | od_mql5e31426a40a5897fc_XM_CSV | GBPUSDmicro | H4 | 921.34 | 28.68 | 35.57 | 58.66 | 15 | 2.59 | 1.00 | ít lệnh (15 < 30); không đóng lệnh lỗ nào (PF vô hạn; DD vốn 59%) |
| 18 | od_mql5ad7d22b5b165a673_XM_CSV | GBPUSDmicro | H4 | 944.20 | 27.18 | 34.15 | 55.00 | 134 | 2.77 | 0.72 | 4 lệnh còn mở bị đóng cuối kỳ; Python/MT5 0.72 ngoài 0,8–1,25 |
| 19 | od_skeafdbf5bcad6_XM_CSV | EURCADmicro | H1 | 912.90 | 26.44 | 33.01 | 18.22 | 190 | 2.77 | 0.91 | — |
| 20 | od_mql5d8f573b8c2314bbf_XM_CSV | EURAUDmicro | H1 | 830.72 | 24.44 | 30.04 | 41.35 | 106 | 2.77 | 1.28 | Python/MT5 1.28 ngoài 0,8–1,25 |
| 21 | od_skea0806a3a5e5_XM_CSV | AUDNZDmicro | H1 | 829.37 | 24.41 | 29.99 | 25.88 | 29 | 2.77 | 0.95 | ít lệnh (29 < 30) |
| 22 | od_skstaca366b679c75482_XM_CSV | EURUSDmicro | H1 | 339.41 | 24.39 | 25.35 | 18.20 | 15 | 1.34 | 0.96 | ít lệnh (15 < 30); lịch sử ngắn (1.3 năm); không đóng lệnh lỗ nào (PF vô hạn; DD vốn 18%) |
| 23 | od_skeaaba30a4e06_XM_CSV | USDJPYmicro | H4 | 727.88 | 21.87 | 26.32 | 49.68 | 164 | 2.77 | 0.89 | — |
| 24 | od_nhapcf8073245473d2a1_XM_CSV | EURGBPmicro | H4 | 687.05 | 20.82 | 24.85 | 67.75 | 188 | 2.77 | 1.34 | 10 lệnh còn mở bị đóng cuối kỳ; Python/MT5 1.34 ngoài 0,8–1,25 |
| 25 | od_mql5b39a9f3ba216fb47_XM_CSV | CHFJPYmicro | H1 | 638.48 | 19.57 | 23.11 | 27.06 | 392 | 2.76 | 0.86 | 5 lệnh còn mở bị đóng cuối kỳ |
| 26 | od_mql5a790e25e547f0b57_XM_CSV | AUDNZDmicro | H4 | 557.33 | 17.51 | 20.30 | 20.87 | 31 | 2.75 | 0.99 | — |
| 27 | od_tohop09a3b2ddc3e78dc8_XM_CSV | EURUSDmicro | H4 | 492.82 | 15.59 | 17.82 | 32.00 | 69 | 2.77 | 1.41 | Python/MT5 1.41 ngoài 0,8–1,25 |
| 28 | od_3304d2fad28adef6_XM_CSV | USDCADmicro | H4 | 408.78 | 14.15 | 15.78 | 40.16 | 64 | 2.59 | 1.86 | Python/MT5 1.86 ngoài 0,8–1,25 |
| 29 | od_018dcb1347276c97_XM_CSV | EURNZDmicro | H4 | 365.94 | 12.13 | 13.43 | 18.45 | 76 | 2.72 | 0.96 | — |
| 30 | od_skea0757c93eb3_XM_CSV | EURNZDmicro | H4 | 319.59 | 10.55 | 11.56 | 29.25 | 2 | 2.77 | 0.91 | ít lệnh (2 < 30); không đóng lệnh lỗ nào (PF vô hạn; DD vốn 29%) |

## Tất cả

| Kết luận | id | EA/nguồn | Symbol | TF | Lãi ròng | %/năm kép | %/năm đơn | DD vốn % | PF | Lệnh | Stop-out | Swap | Kỳ | Chất lượng tick | Lí do / nhãn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ĐẠT | od_skea44640140cc_XM_CSV | sk_ea_44640140cc | GBPCADmicro | H1 | 10075.87 | 138.61 | 364.38 | 45.83 | 4.32 | 616 | 0 | 110.63 | 2023.12.26–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_tohop16b0d75bb149f634_XM_CSV | to_hop_16b0d75bb149f634 | GBPCADmicro | H1 | 5078.62 | 92.19 | 183.84 | 55.87 | 4.71 | 127 | 0 | 55.23 | 2023.12.27–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_skea0075f624b3_XM_CSV | sk_ea_0075f624b3 | GBPNZDmicro | H1 | 4922.39 | 91.25 | 179.43 | 52.77 | 3.15 | 139 | 0 | -477.31 | 2024.01.03–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_skea0ca971ac32_XM_CSV | sk_ea_0ca971ac32 | GBPNZDmicro | H4 | 4533.59 | 85.88 | 164.28 | 50.61 | 80.19 | 27 | 0 | -626.10 | 2023.12.28–2026.10.01 | 99% real ticks | ít lệnh (27 < 30) |
| ĐẠT | od_skstadd3a54f8edcbce2_XM_CSV | sk_st_add3a54f8edcbce2 | EURUSDmicro | H1 | 1042.87 | 70.32 | 77.74 | 60.76 | 7.31 | 15 | 0 | -23.15 | 2025.01.30–2026.06.04 | 100% real ticks | ít lệnh (15 < 30); lịch sử ngắn (1.3 năm) |
| ĐẠT | od_mql5f3313c2c79f00c10_XM_CSV | mql5_f3313c2c79f00c10 | EURGBPmicro | H4 | 3026.52 | 66.07 | 110.21 | 50.64 | 4.32 | 178 | 0 | -811.59 | 2024.01.02–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_skeaa7cd39087e_XM_CSV | sk_ea_a7cd39087e | GOLDmicro | H1 | 2665.71 | 59.96 | 96.40 | 60.59 | 1.39 | 351 | 0 | -2461.95 | 2023.12.26–2026.10.01 | 99% real ticks | Python/MT5 0.69 ngoài 0,8–1,25 |
| ĐẠT | od_skeaff87f96be7_XM_CSV | sk_ea_ff87f96be7 | GBPCADmicro | H1 | 2247.33 | 53.30 | 81.51 | 31.72 | 3.10 | 211 | 0 | 7.06 | 2023.12.29–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_skea3279057100_XM_CSV | sk_ea_3279057100 | EURGBPmicro | H1 | 1779.61 | 44.73 | 64.36 | 64.02 | 1.24 | 203 | 0 | -2009.05 | 2023.12.26–2026.10.01 | 99% real ticks | 10 lệnh còn mở bị đóng cuối kỳ; Python/MT5 -0.57 ngoài 0,8–1,25 |
| ĐẠT | od_b0be91a35f43f34a_XM_CSV | b0be91a35f43f34a | USDCADmicro | H4 | 1684.11 | 43.95 | 62.13 | 58.65 | 0.00 | 46 | 0 | 248.19 | 2024.01.15–2026.10.01 | 100% real ticks | không đóng lệnh lỗ nào (PF vô hạn; DD vốn 59%) |
| ĐẠT | od_skea02906b7d6a_XM_CSV | sk_ea_02906b7d6a | GOLDmicro | H4 | 1496.80 | 39.22 | 54.13 | 70.34 | 1.26 | 180 | 0 | -2454.35 | 2023.12.26–2026.10.01 | 99% real ticks | Python/MT5 0.13 ngoài 0,8–1,25 |
| ĐẠT | od_skea8897567020_XM_CSV | sk_ea_8897567020 | GBPNZDmicro | H1 | 1400.85 | 37.26 | 50.66 | 45.65 | 1.90 | 154 | 0 | -241.45 | 2023.12.26–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_skstc21c2acd239f3c87_XM_CSV | sk_st_c21c2acd239f3c87 | EURUSDmicro | H1 | 525.66 | 37.01 | 39.18 | 49.71 | 4.50 | 20 | 0 | -9.83 | 2025.01.30–2026.06.04 | 100% real ticks | ít lệnh (20 < 30); lịch sử ngắn (1.3 năm) |
| ĐẠT | od_skea5049c79288_XM_CSV | sk_ea_5049c79288 | GBPCADmicro | H4 | 1246.00 | 34.79 | 45.97 | 30.42 | 3.07 | 83 | 0 | 13.93 | 2024.01.15–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_mql5fd4bc285e11ab5a1_XM_CSV | mql5_fd4bc285e11ab5a1 | EURCHFmicro | H4 | 1106.60 | 30.96 | 40.06 | 49.29 | 1.83 | 138 | 0 | -774.63 | 2023.12.27–2026.10.01 | 99% real ticks | 5 lệnh còn mở bị đóng cuối kỳ; Python/MT5 0.76 ngoài 0,8–1,25 |
| ĐẠT | od_mql5e3c3e4f028dbab72_XM_CSV | mql5_e3c3e4f028dbab72 | EURCADmicro | H4 | 1023.49 | 29.03 | 37.01 | 18.35 | 6.21 | 120 | 0 | -147.80 | 2023.12.26–2026.10.01 | 99% real ticks | 3 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_mql5e31426a40a5897fc_XM_CSV | mql5_e31426a40a5897fc | GBPUSDmicro | H4 | 921.34 | 28.68 | 35.57 | 58.66 | 0.00 | 15 | 0 | -69.66 | 2024.02.28–2026.10.01 | 100% real ticks | ít lệnh (15 < 30); không đóng lệnh lỗ nào (PF vô hạn; DD vốn 59%) |
| ĐẠT | od_mql5ad7d22b5b165a673_XM_CSV | mql5_ad7d22b5b165a673 | GBPUSDmicro | H4 | 944.20 | 27.18 | 34.15 | 55.00 | 2.36 | 134 | 0 | -93.62 | 2023.12.26–2026.10.01 | 99% real ticks | 4 lệnh còn mở bị đóng cuối kỳ; Python/MT5 0.72 ngoài 0,8–1,25 |
| ĐẠT | od_skeafdbf5bcad6_XM_CSV | sk_ea_fdbf5bcad6 | EURCADmicro | H1 | 912.90 | 26.44 | 33.01 | 18.22 | 1.94 | 190 | 0 | -725.49 | 2023.12.26–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_mql5d8f573b8c2314bbf_XM_CSV | mql5_d8f573b8c2314bbf | EURAUDmicro | H1 | 830.72 | 24.44 | 30.04 | 41.35 | 1.60 | 106 | 0 | -535.68 | 2023.12.26–2026.10.01 | 99% real ticks | Python/MT5 1.28 ngoài 0,8–1,25 |
| ĐẠT | od_skea0806a3a5e5_XM_CSV | sk_ea_0806a3a5e5 | AUDNZDmicro | H1 | 829.37 | 24.41 | 29.99 | 25.88 | 10.57 | 29 | 0 | -49.78 | 2023.12.26–2026.10.01 | 99% real ticks | ít lệnh (29 < 30) |
| ĐẠT | od_skstaca366b679c75482_XM_CSV | sk_st_aca366b679c75482 | EURUSDmicro | H1 | 339.41 | 24.39 | 25.35 | 18.20 | 0.00 | 15 | 0 | -8.29 | 2025.01.30–2026.06.03 | 100% real ticks | ít lệnh (15 < 30); lịch sử ngắn (1.3 năm); không đóng lệnh lỗ nào (PF vô hạn; DD vốn 18%) |
| ĐẠT | od_skeaaba30a4e06_XM_CSV | sk_ea_aba30a4e06 | USDJPYmicro | H4 | 727.88 | 21.87 | 26.32 | 49.68 | 2.07 | 164 | 0 | -273.00 | 2023.12.26–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_nhapcf8073245473d2a1_XM_CSV | nhap_cf8073245473d2a1 | EURGBPmicro | H4 | 687.05 | 20.82 | 24.85 | 67.75 | 1.42 | 188 | 0 | -905.01 | 2023.12.26–2026.10.01 | 99% real ticks | 10 lệnh còn mở bị đóng cuối kỳ; Python/MT5 1.34 ngoài 0,8–1,25 |
| ĐẠT | od_mql5b39a9f3ba216fb47_XM_CSV | mql5_b39a9f3ba216fb47 | CHFJPYmicro | H1 | 638.48 | 19.57 | 23.11 | 27.06 | 1.81 | 392 | 0 | -138.91 | 2023.12.27–2026.10.01 | 99% real ticks | 5 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_mql5a790e25e547f0b57_XM_CSV | mql5_a790e25e547f0b57 | AUDNZDmicro | H4 | 557.33 | 17.51 | 20.30 | 20.87 | 24.36 | 31 | 0 | -29.33 | 2024.01.02–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_tohop09a3b2ddc3e78dc8_XM_CSV | to_hop_09a3b2ddc3e78dc8 | EURUSDmicro | H4 | 492.82 | 15.59 | 17.82 | 32.00 | 2.41 | 69 | 0 | 21.34 | 2023.12.26–2026.10.01 | 99% real ticks | Python/MT5 1.41 ngoài 0,8–1,25 |
| ĐẠT | od_3304d2fad28adef6_XM_CSV | 3304d2fad28adef6 | USDCADmicro | H4 | 408.78 | 14.15 | 15.78 | 40.16 | 1.66 | 64 | 0 | -17.20 | 2024.02.28–2026.10.01 | 100% real ticks | Python/MT5 1.86 ngoài 0,8–1,25 |
| ĐẠT | od_018dcb1347276c97_XM_CSV | 018dcb1347276c97 | EURNZDmicro | H4 | 365.94 | 12.13 | 13.43 | 18.45 | 5.55 | 76 | 0 | -122.34 | 2024.01.10–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_skea0757c93eb3_XM_CSV | sk_ea_0757c93eb3 | EURNZDmicro | H4 | 319.59 | 10.55 | 11.56 | 29.25 | 0.00 | 2 | 0 | -8.62 | 2023.12.26–2026.10.01 | 99% real ticks | ít lệnh (2 < 30); không đóng lệnh lỗ nào (PF vô hạn; DD vốn 29%) |
| TRƯỢT | od_skea057b28a77f_XM_CSV | sk_ea_057b28a77f | EURCADmicro | H1 | -617.06 | -29.33 | -22.31 | 71.10 | 0.67 | 349 | 0 | -528.05 | 2023.12.26–2026.10.01 | 99% real ticks | lai -29.3%/nam < 10%; 6 lệnh còn mở bị đóng cuối kỳ |
| TRƯỢT | od_skea9c34a60460_XM_CSV | sk_ea_9c34a60460 | GBPCADmicro | H1 | -914.50 | -58.91 | -33.07 | 97.94 | 0.82 | 107 | 3 | 32.06 | 2023.12.26–2026.10.01 | 99% real ticks | STOP-OUT 3 lần; sut giam 97.9% > 80%; lai -58.9%/nam < 10%; 3 lệnh còn mở bị đóng cuối kỳ |
| TRƯỢT | od_skeaaaa64fdbcb_XM_CSV | sk_ea_aaa64fdbcb | GBPCADmicro | H1 | -988.29 | -80.01 | -35.78 | 99.07 | 0.42 | 51 | 3 | -463.99 | 2023.12.27–2026.10.01 | 99% real ticks | STOP-OUT 3 lần; sut giam 99.1% > 80%; lai -80.0%/nam < 10% |
| TRƯỢT | od_skea1f5e88bc8f_XM_CSV | sk_ea_1f5e88bc8f | EURGBPmicro | H1 | -988.78 | -80.60 | -36.12 | 99.41 | 0.76 | 188 | 2 | -910.20 | 2024.01.05–2026.10.01 | 100% real ticks | STOP-OUT 2 lần; sut giam 99.4% > 80%; lai -80.6%/nam < 10% |
| TRƯỢT | od_skea894727cf4f_XM_CSV | sk_ea_894727cf4f | EURCADmicro | H4 | -993.51 | -83.83 | -35.93 | 99.52 | 0.50 | 163 | 2 | -296.36 | 2023.12.26–2026.10.01 | 99% real ticks | STOP-OUT 2 lần; sut giam 99.5% > 80%; lai -83.8%/nam < 10% |
| TRƯỢT | od_mql5f6a59c4de0d4f8be_XM_CSV | mql5_f6a59c4de0d4f8be | GBPCADmicro | H1 | -994.69 | -84.96 | -35.97 | 99.55 | 0.41 | 50 | 3 | -438.62 | 2023.12.26–2026.10.01 | 99% real ticks | STOP-OUT 3 lần; sut giam 99.5% > 80%; lai -85.0%/nam < 10% |
| TRƯỢT | od_mql5164edabb0bca1b7d_XM_CSV | mql5_164edabb0bca1b7d | NZDUSDmicro | H1 | -1012.56 | -100.00 | -11.55 | 101.36 | 0.57 | 224 | 3 | -361.43 | 2017.12.26–2026.10.01 | 31% real ticks | STOP-OUT 3 lần; sut giam 101.4% > 80%; lai -100.0%/nam < 10%; 3 lệnh còn mở bị đóng cuối kỳ |
| TRƯỢT | od_mql5250fc0146190663c_XM_CSV | mql5_250fc0146190663c | NZDUSDmicro | H1 | -1017.33 | -100.00 | -11.61 | 102.69 | 0.39 | 61 | 4 | -106.33 | 2017.12.27–2026.10.01 | 31% real ticks | STOP-OUT 4 lần; sut giam 102.7% > 80%; lai -100.0%/nam < 10%; 3 lệnh còn mở bị đóng cuối kỳ |
| TRƯỢT | od_tohopd315744077e1a7aa_XM_CSV | to_hop_d315744077e1a7aa | EURGBPmicro | H1 | -1012.16 | -100.00 | -36.64 | 100.44 | 0.71 | 59 | 5 | -10.25 | 2023.12.27–2026.10.01 | 99% real ticks | STOP-OUT 5 lần; sut giam 100.4% > 80%; lai -100.0%/nam < 10%; 4 lệnh còn mở bị đóng cuối kỳ |
| CHƯA ĐO ĐƯỢC | od_skst4ac0c7fd10781af4_XM_CSV | sk_st_4ac0c7fd10781af4 | EURUSD# | H1 | 5606.72 | 309.71 | 418.78 | 53.91 | 7.44 | 69 | 0 | 0.00 | 2025.01.30–2026.06.03 | 100% real ticks | SAI SYMBOL EURUSD# (việc EURUSDmicro); lịch sử ngắn (1.3 năm) |
| CHƯA ĐO ĐƯỢC | od_mql5013314d527074d05_XM_CSV | mql5_013314d527074d05 | AUDCADmicro | H1 | 5162.99 | 18.45 | 48.08 | 58.44 | 2.59 | 1228 | 0 | 331.92 | 2016.01.05–2026.10.01 | 25% real ticks | chất lượng tick 25% real ticks < 90% |
| CHƯA ĐO ĐƯỢC | od_mql504e8d5d4a7d0b684_XM_CSV | mql5_04e8d5d4a7d0b684 | NZDUSDmicro | H4 | 3260.89 | 17.99 | 37.21 | 64.30 | 2.15 | 406 | 0 | -665.45 | 2017.12.26–2026.10.01 | 31% real ticks | chất lượng tick 31% real ticks < 90% |
| CHƯA ĐO ĐƯỢC | od_mql514d2e7f097c4ff6e_XM_CSV | mql5_14d2e7f097c4ff6e | NZDUSDmicro | H1 | 1742.30 | 12.20 | 19.88 | 81.63 | 68.79 | 54 | 0 | 89.90 | 2017.12.26–2026.10.01 | 31% real ticks | chất lượng tick 31% real ticks < 90% |
| CHƯA ĐO ĐƯỢC | od_skst299b0817f66d4096_XM_CSV | sk_st_299b0817f66d4096 | EURUSD# | H1 | -967.16 | -92.20 | -72.24 | 98.12 | 0.57 | 27 | 2 | 0.00 | 2025.01.30–2026.06.03 | 100% real ticks | SAI SYMBOL EURUSD# (việc EURUSDmicro); ít lệnh (27 < 30); lịch sử ngắn (1.3 năm) |
| CHƯA ĐO ĐƯỢC | od_skst48a4616b10a6ff9c_XM_CSV | sk_st_48a4616b10a6ff9c | EURUSD# | H1 | -984.40 | -95.53 | -73.53 | 98.67 | 0.10 | 6 | 2 | 0.00 | 2025.01.30–2026.06.03 | 100% real ticks | SAI SYMBOL EURUSD# (việc EURUSDmicro); ít lệnh (6 < 30); lịch sử ngắn (1.3 năm) |
