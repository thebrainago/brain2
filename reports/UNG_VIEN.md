# Ứng viên MT5 (cộng dồn, tự sinh bởi `mt5tools/bao_cao_phien.py`)

Mỗi hệ một dòng, số **đo thật** từ báo cáo MT5 real tick (`reports/ong_dan/ket_qua_mt5/od_*.htm`), tài khoản XM micro 1:500, vốn trong báo cáo (1.000 USD). **Chuẩn cuối (kiểm toán 20/10/2026):**

- **%/năm:** lãi **kép** (chặt hơn lãi đơn) trên **kỳ trong báo cáo**, tính bằng (1 + lãi ròng/vốn)^(1/số năm) − 1. Đạt khi ≥ 10 %.
- **Sụt giảm:** lấy theo **vốn (equity)**, là số lớn hơn giữa *Equity Drawdown Maximal %* và *Relative %*. Đạt khi ≤ 80 %.
- **Loại:** có stop-out thì TRƯỢT. Sai symbol (không phải `*micro` của việc) hoặc tick < 90 % thì CHƯA ĐO ĐƯỢC.
- **Phí:** spread và swap đã nằm trong báo cáo real tick. Hoa hồng trong báo cáo XM micro bằng 0, hoa hồng thật **CHƯA ĐO ĐƯỢC**.
- **Trùng:** cùng thẻ + symbol + TF, hoặc cùng kết quả, chỉ đếm một lần.

Cập nhật: 21/10/2026 00:07 (giờ máy chạy). Đếm (không trùng): ĐẠT 78, TRƯỢT 10, CHƯA ĐO ĐƯỢC 6; trùng bỏ 0.

## Bảng xếp hạng (ĐẠT, không trùng, theo %/năm kép)

| # | id | Symbol | TF | Lãi ròng | %/năm kép | %/năm đơn | DD vốn % | Lệnh | Số năm | Py/MT5 | Điểm yếu |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | od_skst4ac0c7fd10781af4_XM_CSV | EURUSDmicro | H1 | 6052.01 | 330.16 | 452.04 | 49.55 | 73 | 1.34 | 0.97 | lịch sử ngắn (1.3 năm) |
| 2 | od_ghep9c03cef0b89f948f_XM_CSV | GBPCADmicro |  | 15108.44 | 173.22 | 546.37 | 59.95 | 129 | 2.77 | CHƯA ĐO ĐƯỢC | — |
| 3 | od_ghepea3b5db61a7c4792_XM_CSV | GBPCADmicro |  | 11134.21 | 147.05 | 403.45 | 45.63 | 279 | 2.76 | CHƯA ĐO ĐƯỢC | — |
| 4 | od_skea44640140cc_XM_CSV | GBPCADmicro | H1 | 10075.87 | 138.61 | 364.38 | 45.83 | 616 | 2.77 | 1.03 | — |
| 5 | od_ghepe9b41c33d4deee54_XM_CSV | GBPNZDmicro |  | 8151.56 | 122.69 | 294.79 | 43.57 | 135 | 2.77 | CHƯA ĐO ĐƯỢC | — |
| 6 | od_tohop16b0d75bb149f634_XM_CSV | GBPCADmicro | H1 | 5078.62 | 92.19 | 183.84 | 55.87 | 127 | 2.76 | 0.97 | — |
| 7 | od_skea0075f624b3_XM_CSV | GBPNZDmicro | H1 | 4922.39 | 91.25 | 179.43 | 52.77 | 139 | 2.74 | 1.02 | — |
| 8 | od_ghepc9f8a1b857b9a416_XM_CSV | GBPCADmicro |  | 4833.48 | 89.47 | 175.14 | 51.44 | 122 | 2.76 | CHƯA ĐO ĐƯỢC | 3 lệnh còn mở bị đóng cuối kỳ |
| 9 | od_ghep6f5c193256881f31_XM_CSV | GBPCADmicro |  | 4570.11 | 86.21 | 165.43 | 49.31 | 324 | 2.76 | CHƯA ĐO ĐƯỢC | — |
| 10 | od_skea0ca971ac32_XM_CSV | GBPNZDmicro | H4 | 4533.59 | 85.88 | 164.28 | 50.61 | 27 | 2.76 | 1.13 | ít lệnh (27 < 30) |
| 11 | od_skstadd3a54f8edcbce2_XM_CSV | EURUSDmicro | H1 | 1042.87 | 70.32 | 77.74 | 60.76 | 15 | 1.34 | 1.05 | ít lệnh (15 < 30); lịch sử ngắn (1.3 năm) |
| 12 | od_skea0b8298aa53_XM_CSV | GOLDmicro | H1 | 3196.44 | 67.98 | 115.59 | 43.18 | 16 | 2.77 | 1.21 | ít lệnh (16 < 30) |
| 13 | od_skea8771fe6061_XM_CSV | EURCHFmicro |  | 3047.07 | 67.06 | 111.85 | 37.74 | 30 | 2.72 | CHƯA ĐO ĐƯỢC | — |
| 14 | od_ghep60ff9350c26c63ee_XM_CSV | GBPCADmicro |  | 3120.90 | 66.88 | 112.86 | 23.05 | 322 | 2.77 | CHƯA ĐO ĐƯỢC | — |
| 15 | od_mql5f3313c2c79f00c10_XM_CSV | EURGBPmicro | H4 | 3026.52 | 66.07 | 110.21 | 50.64 | 178 | 2.75 | 1.03 | — |
| 16 | od_skeab536f57733_XM_CSV | EURUSDmicro |  | 2946.87 | 64.38 | 106.67 | 39.79 | 249 | 2.76 | CHƯA ĐO ĐƯỢC | 3 lệnh còn mở bị đóng cuối kỳ |
| 17 | od_ghep0bf2c31fbfc9dea0_XM_CSV | GBPCADmicro |  | 2807.11 | 62.17 | 101.51 | 52.49 | 78 | 2.77 | CHƯA ĐO ĐƯỢC | — |
| 18 | od_skeaa7cd39087e_XM_CSV | GOLDmicro | H1 | 2665.71 | 59.96 | 96.40 | 60.59 | 351 | 2.77 | 0.69 | Python/MT5 0.69 ngoài 0,8–1,25 |
| 19 | od_skeadd170ac7bf_XM_CSV | USDCADmicro |  | 2300.30 | 54.00 | 83.19 | 54.64 | 109 | 2.77 | CHƯA ĐO ĐƯỢC | 7 lệnh còn mở bị đóng cuối kỳ |
| 20 | od_skeaff87f96be7_XM_CSV | GBPCADmicro | H1 | 2247.33 | 53.30 | 81.51 | 31.72 | 211 | 2.76 | 1.05 | — |
| 21 | od_skea5fdf89aa94_XM_CSV | USDJPYmicro |  | 1056.06 | 47.70 | 57.14 | 49.24 | 6 | 1.85 | CHƯA ĐO ĐƯỢC | ít lệnh (6 < 30); lịch sử ngắn (1.8 năm) |
| 22 | od_skea3279057100_XM_CSV | EURGBPmicro | H1 | 1779.61 | 44.73 | 64.36 | 64.02 | 203 | 2.77 | -0.57 | 10 lệnh còn mở bị đóng cuối kỳ; Python/MT5 -0.57 ngoài 0,8–1,25 |
| 23 | od_b0be91a35f43f34a_XM_CSV | USDCADmicro | H4 | 1684.11 | 43.95 | 62.13 | 58.65 | 46 | 2.71 | 0.95 | không đóng lệnh lỗ nào (PF vô hạn; DD vốn 59%) |
| 24 | od_skead5df5bc834_XM_CSV | GOLDmicro |  | 1586.33 | 41.01 | 57.37 | 47.74 | 268 | 2.77 | CHƯA ĐO ĐƯỢC | — |
| 25 | od_skea31214192bc_XM_CSV | GBPNZDmicro |  | 1416.77 | 39.61 | 53.57 | 29.81 | 36 | 2.64 | CHƯA ĐO ĐƯỢC | không đóng lệnh lỗ nào (PF vô hạn; DD vốn 30%) |
| 26 | od_skeadc40280363_XM_CSV | CADJPYmicro |  | 1515.44 | 39.60 | 54.80 | 38.80 | 160 | 2.77 | CHƯA ĐO ĐƯỢC | 4 lệnh còn mở bị đóng cuối kỳ |
| 27 | od_skea02906b7d6a_XM_CSV | GOLDmicro | H4 | 1496.80 | 39.22 | 54.13 | 70.34 | 180 | 2.77 | 0.13 | Python/MT5 0.13 ngoài 0,8–1,25 |
| 28 | od_skea154c9fdee7_XM_CSV | GBPCADmicro |  | 1416.99 | 38.26 | 52.02 | 56.45 | 182 | 2.72 | CHƯA ĐO ĐƯỢC | — |
| 29 | od_skea8897567020_XM_CSV | GBPNZDmicro | H1 | 1400.85 | 37.26 | 50.66 | 45.65 | 154 | 2.77 | 1.24 | — |
| 30 | od_skea89d6f8661b_XM_CSV | AUDUSDmicro |  | 1328.45 | 37.07 | 49.56 | 31.32 | 75 | 2.68 | CHƯA ĐO ĐƯỢC | — |
| 31 | od_skstc21c2acd239f3c87_XM_CSV | EURUSDmicro | H1 | 525.66 | 37.01 | 39.18 | 49.71 | 20 | 1.34 | 1.01 | ít lệnh (20 < 30); lịch sử ngắn (1.3 năm) |
| 32 | od_skea45b39eb1d5_XM_CSV | AUDJPYmicro | H4 | 1340.19 | 36.08 | 48.56 | 46.01 | 202 | 2.76 | 0.87 | — |
| 33 | od_skea5049c79288_XM_CSV | GBPCADmicro | H4 | 1246.00 | 34.79 | 45.97 | 30.42 | 83 | 2.71 | 1.15 | — |
| 34 | od_skeaa3d6925a71_XM_CSV | AUDUSDmicro |  | 1166.80 | 32.49 | 42.45 | 55.95 | 533 | 2.75 | CHƯA ĐO ĐƯỢC | 18 lệnh còn mở bị đóng cuối kỳ |
| 35 | od_ghep89811dee41bce6b9_XM_CSV | GOLDmicro |  | 1169.58 | 32.33 | 42.30 | 39.50 | 92 | 2.77 | CHƯA ĐO ĐƯỢC | — |
| 36 | od_mql5fd4bc285e11ab5a1_XM_CSV | EURCHFmicro | H4 | 1106.60 | 30.96 | 40.06 | 49.29 | 138 | 2.76 | 0.76 | 5 lệnh còn mở bị đóng cuối kỳ; Python/MT5 0.76 ngoài 0,8–1,25 |
| 37 | od_skea61c21a2049_XM_CSV | CADJPYmicro |  | 1020.37 | 29.22 | 37.19 | 28.28 | 219 | 2.74 | CHƯA ĐO ĐƯỢC | 3 lệnh còn mở bị đóng cuối kỳ |
| 38 | od_mql5e3c3e4f028dbab72_XM_CSV | EURCADmicro | H4 | 1023.49 | 29.03 | 37.01 | 18.35 | 120 | 2.77 | 1.07 | 3 lệnh còn mở bị đóng cuối kỳ |
| 39 | od_mql5e31426a40a5897fc_XM_CSV | GBPUSDmicro | H4 | 921.34 | 28.68 | 35.57 | 58.66 | 15 | 2.59 | 1.00 | ít lệnh (15 < 30); không đóng lệnh lỗ nào (PF vô hạn; DD vốn 59%) |
| 40 | od_skea2f7862a741_XM_CSV | AUDUSDmicro |  | 927.56 | 28.53 | 35.48 | 17.89 | 71 | 2.61 | CHƯA ĐO ĐƯỢC | — |
| 41 | od_2600ea39abbd7b0f_XM_CSV | GBPNZDmicro |  | 966.04 | 27.73 | 34.97 | 27.10 | 131 | 2.76 | CHƯA ĐO ĐƯỢC | — |
| 42 | od_ghepeab4082becc0e276_XM_CSV | EURGBPmicro |  | 953.97 | 27.63 | 34.74 | 53.99 | 124 | 2.75 | CHƯA ĐO ĐƯỢC | 3 lệnh còn mở bị đóng cuối kỳ |
| 43 | od_skea0c762cdb38_XM_CSV | CHFJPYmicro | H4 | 859.78 | 27.53 | 33.69 | 19.87 | 39 | 2.55 | 1.03 | — |
| 44 | od_skeaf7a71f885d_XM_CSV | GBPNZDmicro |  | 956.40 | 27.47 | 34.59 | 35.37 | 479 | 2.77 | CHƯA ĐO ĐƯỢC | 6 lệnh còn mở bị đóng cuối kỳ |
| 45 | od_mql5ad7d22b5b165a673_XM_CSV | GBPUSDmicro | H4 | 944.20 | 27.18 | 34.15 | 55.00 | 134 | 2.77 | 0.72 | 4 lệnh còn mở bị đóng cuối kỳ; Python/MT5 0.72 ngoài 0,8–1,25 |
| 46 | od_skeafdbf5bcad6_XM_CSV | EURCADmicro | H1 | 912.90 | 26.44 | 33.01 | 18.22 | 190 | 2.77 | 0.91 | — |
| 47 | od_skeabc8157a270_XM_CSV | NZDJPYmicro |  | 852.80 | 25.21 | 31.09 | 60.21 | 292 | 2.74 | CHƯA ĐO ĐƯỢC | — |
| 48 | od_mql5d8f573b8c2314bbf_XM_CSV | EURAUDmicro | H1 | 830.72 | 24.44 | 30.04 | 41.35 | 106 | 2.77 | 1.28 | Python/MT5 1.28 ngoài 0,8–1,25 |
| 49 | od_skea0806a3a5e5_XM_CSV | AUDNZDmicro | H1 | 829.37 | 24.41 | 29.99 | 25.88 | 29 | 2.77 | 0.95 | ít lệnh (29 < 30) |
| 50 | od_skstaca366b679c75482_XM_CSV | EURUSDmicro | H1 | 339.41 | 24.39 | 25.35 | 18.20 | 15 | 1.34 | 0.96 | ít lệnh (15 < 30); lịch sử ngắn (1.3 năm); không đóng lệnh lỗ nào (PF vô hạn; DD vốn 18%) |
| 51 | od_skea0cc19095a9_XM_CSV | GBPNZDmicro | H1 | 824.76 | 24.30 | 29.83 | 28.87 | 429 | 2.77 | 0.85 | 4 lệnh còn mở bị đóng cuối kỳ |
| 52 | od_skea0ab6e87da9_XM_CSV | EURGBPmicro |  | 755.56 | 22.77 | 27.54 | 75.67 | 245 | 2.74 | CHƯA ĐO ĐƯỢC | — |
| 53 | od_skea363d6c8238_XM_CSV | NZDJPYmicro |  | 729.36 | 22.62 | 27.16 | 32.97 | 63 | 2.69 | CHƯA ĐO ĐƯỢC | — |
| 54 | od_skea66a65a142a_XM_CSV | GBPNZDmicro |  | 750.16 | 22.43 | 27.13 | 52.95 | 263 | 2.77 | CHƯA ĐO ĐƯỢC | 3 lệnh còn mở bị đóng cuối kỳ |
| 55 | od_0557d803384c6211_XM_CSV | GBPUSDmicro |  | 738.33 | 22.13 | 26.70 | 47.09 | 182 | 2.77 | CHƯA ĐO ĐƯỢC | 3 lệnh còn mở bị đóng cuối kỳ |
| 56 | od_skeaaba30a4e06_XM_CSV | USDJPYmicro | H4 | 727.88 | 21.87 | 26.32 | 49.68 | 164 | 2.77 | 0.89 | — |
| 57 | od_nhapcf8073245473d2a1_XM_CSV | EURGBPmicro | H4 | 687.05 | 20.82 | 24.85 | 67.75 | 188 | 2.77 | 1.34 | 10 lệnh còn mở bị đóng cuối kỳ; Python/MT5 1.34 ngoài 0,8–1,25 |
| 58 | od_skeae2482b06a4_XM_CSV | GBPUSDmicro |  | 678.20 | 20.61 | 24.55 | 41.86 | 1338 | 2.76 | CHƯA ĐO ĐƯỢC | 8 lệnh còn mở bị đóng cuối kỳ |
| 59 | od_skea09c76b6df5_XM_CSV | GBPAUDmicro |  | 646.05 | 20.21 | 23.86 | 34.49 | 224 | 2.71 | CHƯA ĐO ĐƯỢC | — |
| 60 | od_mql5b39a9f3ba216fb47_XM_CSV | CHFJPYmicro | H1 | 638.48 | 19.57 | 23.11 | 27.06 | 392 | 2.76 | 0.86 | 5 lệnh còn mở bị đóng cuối kỳ |
| 61 | od_mql525573694a7f03d3a_XM_CSV | EURGBPmicro | H1 | 634.44 | 19.46 | 22.97 | 31.48 | 282 | 2.76 | 1.04 | 5 lệnh còn mở bị đóng cuối kỳ |
| 62 | od_skea5539346824_XM_CSV | EURGBPmicro |  | 616.27 | 19.25 | 22.60 | 46.52 | 233 | 2.73 | CHƯA ĐO ĐƯỢC | — |
| 63 | od_skeaf88d932deb_XM_CSV | GOLDmicro |  | 611.33 | 18.83 | 22.11 | 52.96 | 605 | 2.77 | CHƯA ĐO ĐƯỢC | — |
| 64 | od_mql5b5a04d7c15935f8b_XM_CSV | GBPNZDmicro | H1 | 590.17 | 18.26 | 21.34 | 33.29 | 208 | 2.77 | 0.98 | 3 lệnh còn mở bị đóng cuối kỳ |
| 65 | od_skead0a7af9f8b_XM_CSV | AUDJPYmicro |  | 572.83 | 17.93 | 20.86 | 8.40 | 158 | 2.75 | CHƯA ĐO ĐƯỢC | — |
| 66 | od_mql5a790e25e547f0b57_XM_CSV | AUDNZDmicro | H4 | 557.33 | 17.51 | 20.30 | 20.87 | 31 | 2.75 | 0.99 | — |
| 67 | od_skea0ab4d307d3_XM_CSV | EURNZDmicro | H1 | 560.23 | 17.45 | 20.26 | 48.57 | 286 | 2.77 | 0.74 | Python/MT5 0.74 ngoài 0,8–1,25 |
| 68 | od_tohop564be9bb91406c57_XM_CSV | GBPUSDmicro | H1 | 546.97 | 17.41 | 20.12 | 26.23 | 62 | 2.72 | 1.00 | — |
| 69 | od_skea135e93ee32_XM_CSV | EURUSDmicro | H1 | 555.97 | 17.34 | 20.11 | 20.15 | 57 | 2.77 | 0.99 | — |
| 70 | od_skeaf3d30ea9da_XM_CSV | GBPAUDmicro |  | 540.92 | 16.93 | 19.56 | 47.17 | 956 | 2.77 | CHƯA ĐO ĐƯỢC | 4 lệnh còn mở bị đóng cuối kỳ |
| 71 | od_tohop09a3b2ddc3e78dc8_XM_CSV | EURUSDmicro | H4 | 492.82 | 15.59 | 17.82 | 32.00 | 69 | 2.77 | 1.41 | Python/MT5 1.41 ngoài 0,8–1,25 |
| 72 | od_tohopc2d52300cc825dff_XM_CSV | AUDNZDmicro | H1 | 445.82 | 14.38 | 16.25 | 25.60 | 144 | 2.74 | 1.25 | — |
| 73 | od_3304d2fad28adef6_XM_CSV | USDCADmicro | H4 | 408.78 | 14.15 | 15.78 | 40.16 | 64 | 2.59 | 1.86 | Python/MT5 1.86 ngoài 0,8–1,25 |
| 74 | od_mql5e52afb999eca4bd1_XM_CSV | EURGBPmicro | H1 | 425.41 | 13.71 | 15.41 | 24.94 | 110 | 2.76 | 1.09 | 6 lệnh còn mở bị đóng cuối kỳ |
| 75 | od_skea7eec0ab393_XM_CSV | GBPAUDmicro |  | 394.40 | 13.08 | 14.58 | 53.01 | 294 | 2.70 | CHƯA ĐO ĐƯỢC | 8 lệnh còn mở bị đóng cuối kỳ |
| 76 | od_tohop9acc6e0d2f784cb9_XM_CSV | GBPCADmicro | H1 | 390.28 | 12.86 | 14.33 | 10.57 | 59 | 2.72 | 0.97 | — |
| 77 | od_018dcb1347276c97_XM_CSV | EURNZDmicro | H4 | 365.94 | 12.13 | 13.43 | 18.45 | 76 | 2.72 | 0.96 | — |
| 78 | od_skea0757c93eb3_XM_CSV | EURNZDmicro | H4 | 319.59 | 10.55 | 11.56 | 29.25 | 2 | 2.77 | 0.91 | ít lệnh (2 < 30); không đóng lệnh lỗ nào (PF vô hạn; DD vốn 29%) |

## Tất cả

| Kết luận | id | EA/nguồn | Symbol | TF | Lãi ròng | %/năm kép | %/năm đơn | DD vốn % | PF | Lệnh | Stop-out | Swap | Kỳ | Chất lượng tick | Lí do / nhãn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ĐẠT | od_skst4ac0c7fd10781af4_XM_CSV | sk_st_4ac0c7fd10781af4 | EURUSDmicro | H1 | 6052.01 | 330.16 | 452.04 | 49.55 | 5.98 | 73 | 0 | -81.14 | 2025.01.30–2026.06.03 | 100% real ticks | lịch sử ngắn (1.3 năm) |
| ĐẠT | od_ghep9c03cef0b89f948f_XM_CSV | od | GBPCADmicro |  | 15108.44 | 173.22 | 546.37 | 59.95 | 4.03 | 129 | 0 | 203.72 | 2023.12.26–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_ghepea3b5db61a7c4792_XM_CSV | od | GBPCADmicro |  | 11134.21 | 147.05 | 403.45 | 45.63 | 7.98 | 279 | 0 | 158.48 | 2023.12.28–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_skea44640140cc_XM_CSV | sk_ea_44640140cc | GBPCADmicro | H1 | 10075.87 | 138.61 | 364.38 | 45.83 | 4.32 | 616 | 0 | 110.63 | 2023.12.26–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_ghepe9b41c33d4deee54_XM_CSV | od | GBPNZDmicro |  | 8151.56 | 122.69 | 294.79 | 43.57 | 5.35 | 135 | 0 | -615.31 | 2023.12.26–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_tohop16b0d75bb149f634_XM_CSV | to_hop_16b0d75bb149f634 | GBPCADmicro | H1 | 5078.62 | 92.19 | 183.84 | 55.87 | 4.71 | 127 | 0 | 55.23 | 2023.12.27–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_skea0075f624b3_XM_CSV | sk_ea_0075f624b3 | GBPNZDmicro | H1 | 4922.39 | 91.25 | 179.43 | 52.77 | 3.15 | 139 | 0 | -477.31 | 2024.01.03–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_ghepc9f8a1b857b9a416_XM_CSV | od | GBPCADmicro |  | 4833.48 | 89.47 | 175.14 | 51.44 | 4.54 | 122 | 0 | 88.37 | 2023.12.28–2026.10.01 | 99% real ticks | 3 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_ghep6f5c193256881f31_XM_CSV | od | GBPCADmicro |  | 4570.11 | 86.21 | 165.43 | 49.31 | 2.39 | 324 | 0 | 70.80 | 2023.12.27–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_skea0ca971ac32_XM_CSV | sk_ea_0ca971ac32 | GBPNZDmicro | H4 | 4533.59 | 85.88 | 164.28 | 50.61 | 80.19 | 27 | 0 | -626.10 | 2023.12.28–2026.10.01 | 99% real ticks | ít lệnh (27 < 30) |
| ĐẠT | od_skstadd3a54f8edcbce2_XM_CSV | sk_st_add3a54f8edcbce2 | EURUSDmicro | H1 | 1042.87 | 70.32 | 77.74 | 60.76 | 7.31 | 15 | 0 | -23.15 | 2025.01.30–2026.06.04 | 100% real ticks | ít lệnh (15 < 30); lịch sử ngắn (1.3 năm) |
| ĐẠT | od_skea0b8298aa53_XM_CSV | sk_ea_0b8298aa53 | GOLDmicro | H1 | 3196.44 | 67.98 | 115.59 | 43.18 | 41.38 | 16 | 0 | -88.77 | 2023.12.26–2026.10.01 | 99% real ticks | ít lệnh (16 < 30) |
| ĐẠT | od_skea8771fe6061_XM_CSV | od | EURCHFmicro |  | 3047.07 | 67.06 | 111.85 | 37.74 | 16.73 | 30 | 0 | 83.88 | 2024.01.10–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_ghep60ff9350c26c63ee_XM_CSV | od | GBPCADmicro |  | 3120.90 | 66.88 | 112.86 | 23.05 | 3.90 | 322 | 0 | 41.26 | 2023.12.26–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_mql5f3313c2c79f00c10_XM_CSV | mql5_f3313c2c79f00c10 | EURGBPmicro | H4 | 3026.52 | 66.07 | 110.21 | 50.64 | 4.32 | 178 | 0 | -811.59 | 2024.01.02–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_skeab536f57733_XM_CSV | od | EURUSDmicro |  | 2946.87 | 64.38 | 106.67 | 39.79 | 2.08 | 249 | 0 | -276.36 | 2023.12.27–2026.10.01 | 99% real ticks | 3 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_ghep0bf2c31fbfc9dea0_XM_CSV | od | GBPCADmicro |  | 2807.11 | 62.17 | 101.51 | 52.49 | 9.06 | 78 | 0 | 121.03 | 2023.12.26–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_skeaa7cd39087e_XM_CSV | sk_ea_a7cd39087e | GOLDmicro | H1 | 2665.71 | 59.96 | 96.40 | 60.59 | 1.39 | 351 | 0 | -2461.95 | 2023.12.26–2026.10.01 | 99% real ticks | Python/MT5 0.69 ngoài 0,8–1,25 |
| ĐẠT | od_skeadd170ac7bf_XM_CSV | od | USDCADmicro |  | 2300.30 | 54.00 | 83.19 | 54.64 | 4.42 | 109 | 0 | -411.27 | 2023.12.26–2026.10.01 | 99% real ticks | 7 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_skeaff87f96be7_XM_CSV | sk_ea_ff87f96be7 | GBPCADmicro | H1 | 2247.33 | 53.30 | 81.51 | 31.72 | 3.10 | 211 | 0 | 7.06 | 2023.12.29–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_skea5fdf89aa94_XM_CSV | od | USDJPYmicro |  | 1056.06 | 47.70 | 57.14 | 49.24 | 38.09 | 6 | 0 | 4.77 | 2024.11.25–2026.10.01 | 100% real ticks | ít lệnh (6 < 30); lịch sử ngắn (1.8 năm) |
| ĐẠT | od_skea3279057100_XM_CSV | sk_ea_3279057100 | EURGBPmicro | H1 | 1779.61 | 44.73 | 64.36 | 64.02 | 1.24 | 203 | 0 | -2009.05 | 2023.12.26–2026.10.01 | 99% real ticks | 10 lệnh còn mở bị đóng cuối kỳ; Python/MT5 -0.57 ngoài 0,8–1,25 |
| ĐẠT | od_b0be91a35f43f34a_XM_CSV | b0be91a35f43f34a | USDCADmicro | H4 | 1684.11 | 43.95 | 62.13 | 58.65 | 0.00 | 46 | 0 | 248.19 | 2024.01.15–2026.10.01 | 100% real ticks | không đóng lệnh lỗ nào (PF vô hạn; DD vốn 59%) |
| ĐẠT | od_skead5df5bc834_XM_CSV | od | GOLDmicro |  | 1586.33 | 41.01 | 57.37 | 47.74 | 2.32 | 268 | 0 | -332.65 | 2023.12.26–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_skea31214192bc_XM_CSV | od | GBPNZDmicro |  | 1416.77 | 39.61 | 53.57 | 29.81 | 0.00 | 36 | 0 | -18.27 | 2024.02.08–2026.10.01 | 100% real ticks | không đóng lệnh lỗ nào (PF vô hạn; DD vốn 30%) |
| ĐẠT | od_skeadc40280363_XM_CSV | od | CADJPYmicro |  | 1515.44 | 39.60 | 54.80 | 38.80 | 2.74 | 160 | 0 | -257.35 | 2023.12.26–2026.10.01 | 99% real ticks | 4 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_skea02906b7d6a_XM_CSV | sk_ea_02906b7d6a | GOLDmicro | H4 | 1496.80 | 39.22 | 54.13 | 70.34 | 1.26 | 180 | 0 | -2454.35 | 2023.12.26–2026.10.01 | 99% real ticks | Python/MT5 0.13 ngoài 0,8–1,25 |
| ĐẠT | od_skea154c9fdee7_XM_CSV | od | GBPCADmicro |  | 1416.99 | 38.26 | 52.02 | 56.45 | 2.60 | 182 | 0 | -242.02 | 2024.01.10–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_skea8897567020_XM_CSV | sk_ea_8897567020 | GBPNZDmicro | H1 | 1400.85 | 37.26 | 50.66 | 45.65 | 1.90 | 154 | 0 | -241.45 | 2023.12.26–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_skea89d6f8661b_XM_CSV | od | AUDUSDmicro |  | 1328.45 | 37.07 | 49.56 | 31.32 | 28.73 | 75 | 0 | -172.05 | 2024.01.26–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_skstc21c2acd239f3c87_XM_CSV | sk_st_c21c2acd239f3c87 | EURUSDmicro | H1 | 525.66 | 37.01 | 39.18 | 49.71 | 4.50 | 20 | 0 | -9.83 | 2025.01.30–2026.06.04 | 100% real ticks | ít lệnh (20 < 30); lịch sử ngắn (1.3 năm) |
| ĐẠT | od_skea45b39eb1d5_XM_CSV | sk_ea_45b39eb1d5 | AUDJPYmicro | H4 | 1340.19 | 36.08 | 48.56 | 46.01 | 8.07 | 202 | 0 | 140.01 | 2023.12.28–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_skea5049c79288_XM_CSV | sk_ea_5049c79288 | GBPCADmicro | H4 | 1246.00 | 34.79 | 45.97 | 30.42 | 3.07 | 83 | 0 | 13.93 | 2024.01.15–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_skeaa3d6925a71_XM_CSV | od | AUDUSDmicro |  | 1166.80 | 32.49 | 42.45 | 55.95 | 1.48 | 533 | 0 | -500.48 | 2024.01.01–2026.10.01 | 99% real ticks | 18 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_ghep89811dee41bce6b9_XM_CSV | od | GOLDmicro |  | 1169.58 | 32.33 | 42.30 | 39.50 | 3.11 | 92 | 0 | -149.34 | 2023.12.26–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_mql5fd4bc285e11ab5a1_XM_CSV | mql5_fd4bc285e11ab5a1 | EURCHFmicro | H4 | 1106.60 | 30.96 | 40.06 | 49.29 | 1.83 | 138 | 0 | -774.63 | 2023.12.27–2026.10.01 | 99% real ticks | 5 lệnh còn mở bị đóng cuối kỳ; Python/MT5 0.76 ngoài 0,8–1,25 |
| ĐẠT | od_skea61c21a2049_XM_CSV | od | CADJPYmicro |  | 1020.37 | 29.22 | 37.19 | 28.28 | 2.15 | 219 | 0 | -187.04 | 2024.01.03–2026.10.01 | 100% real ticks | 3 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_mql5e3c3e4f028dbab72_XM_CSV | mql5_e3c3e4f028dbab72 | EURCADmicro | H4 | 1023.49 | 29.03 | 37.01 | 18.35 | 6.21 | 120 | 0 | -147.80 | 2023.12.26–2026.10.01 | 99% real ticks | 3 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_mql5e31426a40a5897fc_XM_CSV | mql5_e31426a40a5897fc | GBPUSDmicro | H4 | 921.34 | 28.68 | 35.57 | 58.66 | 0.00 | 15 | 0 | -69.66 | 2024.02.28–2026.10.01 | 100% real ticks | ít lệnh (15 < 30); không đóng lệnh lỗ nào (PF vô hạn; DD vốn 59%) |
| ĐẠT | od_skea2f7862a741_XM_CSV | od | AUDUSDmicro |  | 927.56 | 28.53 | 35.48 | 17.89 | 5.81 | 71 | 0 | -44.24 | 2024.02.19–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_2600ea39abbd7b0f_XM_CSV | od | GBPNZDmicro |  | 966.04 | 27.73 | 34.97 | 27.10 | 2.09 | 131 | 0 | -466.05 | 2023.12.27–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_ghepeab4082becc0e276_XM_CSV | od | EURGBPmicro |  | 953.97 | 27.63 | 34.74 | 53.99 | 3.38 | 124 | 0 | -206.81 | 2024.01.02–2026.10.01 | 100% real ticks | 3 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_skea0c762cdb38_XM_CSV | sk_ea_0c762cdb38 | CHFJPYmicro | H4 | 859.78 | 27.53 | 33.69 | 19.87 | 5.74 | 39 | 0 | -87.83 | 2024.03.13–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_skeaf7a71f885d_XM_CSV | od | GBPNZDmicro |  | 956.40 | 27.47 | 34.59 | 35.37 | 1.63 | 479 | 0 | -480.74 | 2023.12.26–2026.10.01 | 99% real ticks | 6 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_mql5ad7d22b5b165a673_XM_CSV | mql5_ad7d22b5b165a673 | GBPUSDmicro | H4 | 944.20 | 27.18 | 34.15 | 55.00 | 2.36 | 134 | 0 | -93.62 | 2023.12.26–2026.10.01 | 99% real ticks | 4 lệnh còn mở bị đóng cuối kỳ; Python/MT5 0.72 ngoài 0,8–1,25 |
| ĐẠT | od_skeafdbf5bcad6_XM_CSV | sk_ea_fdbf5bcad6 | EURCADmicro | H1 | 912.90 | 26.44 | 33.01 | 18.22 | 1.94 | 190 | 0 | -725.49 | 2023.12.26–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_skeabc8157a270_XM_CSV | od | NZDJPYmicro |  | 852.80 | 25.21 | 31.09 | 60.21 | 1.69 | 292 | 0 | -140.25 | 2024.01.03–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_mql5d8f573b8c2314bbf_XM_CSV | mql5_d8f573b8c2314bbf | EURAUDmicro | H1 | 830.72 | 24.44 | 30.04 | 41.35 | 1.60 | 106 | 0 | -535.68 | 2023.12.26–2026.10.01 | 99% real ticks | Python/MT5 1.28 ngoài 0,8–1,25 |
| ĐẠT | od_skea0806a3a5e5_XM_CSV | sk_ea_0806a3a5e5 | AUDNZDmicro | H1 | 829.37 | 24.41 | 29.99 | 25.88 | 10.57 | 29 | 0 | -49.78 | 2023.12.26–2026.10.01 | 99% real ticks | ít lệnh (29 < 30) |
| ĐẠT | od_skstaca366b679c75482_XM_CSV | sk_st_aca366b679c75482 | EURUSDmicro | H1 | 339.41 | 24.39 | 25.35 | 18.20 | 0.00 | 15 | 0 | -8.29 | 2025.01.30–2026.06.03 | 100% real ticks | ít lệnh (15 < 30); lịch sử ngắn (1.3 năm); không đóng lệnh lỗ nào (PF vô hạn; DD vốn 18%) |
| ĐẠT | od_skea0cc19095a9_XM_CSV | sk_ea_0cc19095a9 | GBPNZDmicro | H1 | 824.76 | 24.30 | 29.83 | 28.87 | 1.66 | 429 | 0 | -373.98 | 2023.12.26–2026.10.01 | 99% real ticks | 4 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_skea0ab6e87da9_XM_CSV | od | EURGBPmicro |  | 755.56 | 22.77 | 27.54 | 75.67 | 1.57 | 245 | 0 | -189.78 | 2024.01.03–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_skea363d6c8238_XM_CSV | od | NZDJPYmicro |  | 729.36 | 22.62 | 27.16 | 32.97 | 3.77 | 63 | 0 | -54.50 | 2024.01.24–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_skea66a65a142a_XM_CSV | od | GBPNZDmicro |  | 750.16 | 22.43 | 27.13 | 52.95 | 1.17 | 263 | 0 | -910.44 | 2023.12.26–2026.10.01 | 99% real ticks | 3 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_0557d803384c6211_XM_CSV | od | GBPUSDmicro |  | 738.33 | 22.13 | 26.70 | 47.09 | 2.30 | 182 | 0 | -44.79 | 2023.12.26–2026.10.01 | 99% real ticks | 3 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_skeaaba30a4e06_XM_CSV | sk_ea_aba30a4e06 | USDJPYmicro | H4 | 727.88 | 21.87 | 26.32 | 49.68 | 2.07 | 164 | 0 | -273.00 | 2023.12.26–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_nhapcf8073245473d2a1_XM_CSV | nhap_cf8073245473d2a1 | EURGBPmicro | H4 | 687.05 | 20.82 | 24.85 | 67.75 | 1.42 | 188 | 0 | -905.01 | 2023.12.26–2026.10.01 | 99% real ticks | 10 lệnh còn mở bị đóng cuối kỳ; Python/MT5 1.34 ngoài 0,8–1,25 |
| ĐẠT | od_skeae2482b06a4_XM_CSV | od | GBPUSDmicro |  | 678.20 | 20.61 | 24.55 | 41.86 | 1.54 | 1338 | 0 | -95.46 | 2023.12.27–2026.10.01 | 99% real ticks | 8 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_skea09c76b6df5_XM_CSV | od | GBPAUDmicro |  | 646.05 | 20.21 | 23.86 | 34.49 | 1.98 | 224 | 0 | -249.81 | 2024.01.16–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_mql5b39a9f3ba216fb47_XM_CSV | mql5_b39a9f3ba216fb47 | CHFJPYmicro | H1 | 638.48 | 19.57 | 23.11 | 27.06 | 1.81 | 392 | 0 | -138.91 | 2023.12.27–2026.10.01 | 99% real ticks | 5 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_mql525573694a7f03d3a_XM_CSV | mql5_25573694a7f03d3a | EURGBPmicro | H1 | 634.44 | 19.46 | 22.97 | 31.48 | 2.22 | 282 | 0 | -165.35 | 2023.12.27–2026.10.01 | 99% real ticks | 5 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_skea5539346824_XM_CSV | od | EURGBPmicro |  | 616.27 | 19.25 | 22.60 | 46.52 | 1.77 | 233 | 0 | -179.75 | 2024.01.09–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_skeaf88d932deb_XM_CSV | od | GOLDmicro |  | 611.33 | 18.83 | 22.11 | 52.96 | 2.12 | 605 | 0 | -166.99 | 2023.12.26–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_mql5b5a04d7c15935f8b_XM_CSV | mql5_b5a04d7c15935f8b | GBPNZDmicro | H1 | 590.17 | 18.26 | 21.34 | 33.29 | 1.45 | 208 | 0 | -350.29 | 2023.12.26–2026.10.01 | 99% real ticks | 3 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_skead0a7af9f8b_XM_CSV | od | AUDJPYmicro |  | 572.83 | 17.93 | 20.86 | 8.40 | 7.97 | 158 | 0 | -30.43 | 2024.01.02–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_mql5a790e25e547f0b57_XM_CSV | mql5_a790e25e547f0b57 | AUDNZDmicro | H4 | 557.33 | 17.51 | 20.30 | 20.87 | 24.36 | 31 | 0 | -29.33 | 2024.01.02–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_skea0ab4d307d3_XM_CSV | sk_ea_0ab4d307d3 | EURNZDmicro | H1 | 560.23 | 17.45 | 20.26 | 48.57 | 1.39 | 286 | 0 | -246.97 | 2023.12.26–2026.10.01 | 99% real ticks | Python/MT5 0.74 ngoài 0,8–1,25 |
| ĐẠT | od_tohop564be9bb91406c57_XM_CSV | to_hop_564be9bb91406c57 | GBPUSDmicro | H1 | 546.97 | 17.41 | 20.12 | 26.23 | 2.54 | 62 | 0 | -37.13 | 2024.01.12–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_skea135e93ee32_XM_CSV | sk_ea_135e93ee32 | EURUSDmicro | H1 | 555.97 | 17.34 | 20.11 | 20.15 | 4.52 | 57 | 0 | -25.70 | 2023.12.26–2026.10.01 | 99% real ticks |  |
| ĐẠT | od_skeaf3d30ea9da_XM_CSV | od | GBPAUDmicro |  | 540.92 | 16.93 | 19.56 | 47.17 | 1.56 | 956 | 0 | -88.02 | 2023.12.26–2026.10.01 | 99% real ticks | 4 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_tohop09a3b2ddc3e78dc8_XM_CSV | to_hop_09a3b2ddc3e78dc8 | EURUSDmicro | H4 | 492.82 | 15.59 | 17.82 | 32.00 | 2.41 | 69 | 0 | 21.34 | 2023.12.26–2026.10.01 | 99% real ticks | Python/MT5 1.41 ngoài 0,8–1,25 |
| ĐẠT | od_tohopc2d52300cc825dff_XM_CSV | to_hop_c2d52300cc825dff | AUDNZDmicro | H1 | 445.82 | 14.38 | 16.25 | 25.60 | 1.66 | 144 | 0 | -48.66 | 2024.01.03–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_3304d2fad28adef6_XM_CSV | 3304d2fad28adef6 | USDCADmicro | H4 | 408.78 | 14.15 | 15.78 | 40.16 | 1.66 | 64 | 0 | -17.20 | 2024.02.28–2026.10.01 | 100% real ticks | Python/MT5 1.86 ngoài 0,8–1,25 |
| ĐẠT | od_mql5e52afb999eca4bd1_XM_CSV | mql5_e52afb999eca4bd1 | EURGBPmicro | H1 | 425.41 | 13.71 | 15.41 | 24.94 | 1.39 | 110 | 0 | -452.87 | 2023.12.28–2026.10.01 | 99% real ticks | 6 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_skea7eec0ab393_XM_CSV | od | GBPAUDmicro |  | 394.40 | 13.08 | 14.58 | 53.01 | 1.20 | 294 | 0 | -496.33 | 2024.01.17–2026.10.01 | 100% real ticks | 8 lệnh còn mở bị đóng cuối kỳ |
| ĐẠT | od_tohop9acc6e0d2f784cb9_XM_CSV | to_hop_9acc6e0d2f784cb9 | GBPCADmicro | H1 | 390.28 | 12.86 | 14.33 | 10.57 | 7.80 | 59 | 0 | 1.99 | 2024.01.10–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_018dcb1347276c97_XM_CSV | 018dcb1347276c97 | EURNZDmicro | H4 | 365.94 | 12.13 | 13.43 | 18.45 | 5.55 | 76 | 0 | -122.34 | 2024.01.10–2026.10.01 | 100% real ticks |  |
| ĐẠT | od_skea0757c93eb3_XM_CSV | sk_ea_0757c93eb3 | EURNZDmicro | H4 | 319.59 | 10.55 | 11.56 | 29.25 | 0.00 | 2 | 0 | -8.62 | 2023.12.26–2026.10.01 | 99% real ticks | ít lệnh (2 < 30); không đóng lệnh lỗ nào (PF vô hạn; DD vốn 29%) |
| TRƯỢT | od_skea057b28a77f_XM_CSV | sk_ea_057b28a77f | EURCADmicro | H1 | -617.06 | -29.33 | -22.31 | 71.10 | 0.67 | 349 | 0 | -528.05 | 2023.12.26–2026.10.01 | 99% real ticks | lai -29.3%/nam < 10%; 6 lệnh còn mở bị đóng cuối kỳ |
| TRƯỢT | od_skea9c34a60460_XM_CSV | sk_ea_9c34a60460 | GBPCADmicro | H1 | -914.50 | -58.91 | -33.07 | 97.94 | 0.82 | 107 | 3 | 32.06 | 2023.12.26–2026.10.01 | 99% real ticks | STOP-OUT 3 lần; sut giam 97.9% > 80%; lai -58.9%/nam < 10%; 3 lệnh còn mở bị đóng cuối kỳ |
| TRƯỢT | od_skea78384bbaf7_XM_CSV | od | USDCADmicro |  | -979.76 | -75.60 | -35.43 | 99.60 | 0.82 | 219 | 3 | 205.02 | 2023.12.26–2026.10.01 | 99% real ticks | STOP-OUT 3 lần; sut giam 99.6% > 80%; lai -75.6%/nam < 10%; 3 lệnh còn mở bị đóng cuối kỳ |
| TRƯỢT | od_skeaaaa64fdbcb_XM_CSV | sk_ea_aaa64fdbcb | GBPCADmicro | H1 | -988.29 | -80.01 | -35.78 | 99.07 | 0.42 | 51 | 3 | -463.99 | 2023.12.27–2026.10.01 | 99% real ticks | STOP-OUT 3 lần; sut giam 99.1% > 80%; lai -80.0%/nam < 10% |
| TRƯỢT | od_skea1f5e88bc8f_XM_CSV | sk_ea_1f5e88bc8f | EURGBPmicro | H1 | -988.78 | -80.60 | -36.12 | 99.41 | 0.76 | 188 | 2 | -910.20 | 2024.01.05–2026.10.01 | 100% real ticks | STOP-OUT 2 lần; sut giam 99.4% > 80%; lai -80.6%/nam < 10% |
| TRƯỢT | od_skea894727cf4f_XM_CSV | sk_ea_894727cf4f | EURCADmicro | H4 | -993.51 | -83.83 | -35.93 | 99.52 | 0.50 | 163 | 2 | -296.36 | 2023.12.26–2026.10.01 | 99% real ticks | STOP-OUT 2 lần; sut giam 99.5% > 80%; lai -83.8%/nam < 10% |
| TRƯỢT | od_mql5f6a59c4de0d4f8be_XM_CSV | mql5_f6a59c4de0d4f8be | GBPCADmicro | H1 | -994.69 | -84.96 | -35.97 | 99.55 | 0.41 | 50 | 3 | -438.62 | 2023.12.26–2026.10.01 | 99% real ticks | STOP-OUT 3 lần; sut giam 99.5% > 80%; lai -85.0%/nam < 10% |
| TRƯỢT | od_mql5164edabb0bca1b7d_XM_CSV | mql5_164edabb0bca1b7d | NZDUSDmicro | H1 | -1012.56 | -100.00 | -11.55 | 101.36 | 0.57 | 224 | 3 | -361.43 | 2017.12.26–2026.10.01 | 31% real ticks | STOP-OUT 3 lần; sut giam 101.4% > 80%; lai -100.0%/nam < 10%; 3 lệnh còn mở bị đóng cuối kỳ |
| TRƯỢT | od_mql5250fc0146190663c_XM_CSV | mql5_250fc0146190663c | NZDUSDmicro | H1 | -1017.33 | -100.00 | -11.61 | 102.69 | 0.39 | 61 | 4 | -106.33 | 2017.12.27–2026.10.01 | 31% real ticks | STOP-OUT 4 lần; sut giam 102.7% > 80%; lai -100.0%/nam < 10%; 3 lệnh còn mở bị đóng cuối kỳ |
| TRƯỢT | od_tohopd315744077e1a7aa_XM_CSV | to_hop_d315744077e1a7aa | EURGBPmicro | H1 | -1012.16 | -100.00 | -36.64 | 100.44 | 0.71 | 59 | 5 | -10.25 | 2023.12.27–2026.10.01 | 99% real ticks | STOP-OUT 5 lần; sut giam 100.4% > 80%; lai -100.0%/nam < 10%; 4 lệnh còn mở bị đóng cuối kỳ |
| CHƯA ĐO ĐƯỢC | od_mql5013314d527074d05_XM_CSV | mql5_013314d527074d05 | AUDCADmicro | H1 | 5162.99 | 18.45 | 48.08 | 58.44 | 2.59 | 1228 | 0 | 331.92 | 2016.01.05–2026.10.01 | 25% real ticks | chất lượng tick 25% real ticks < 90% |
| CHƯA ĐO ĐƯỢC | od_mql504e8d5d4a7d0b684_XM_CSV | mql5_04e8d5d4a7d0b684 | NZDUSDmicro | H4 | 3260.89 | 17.99 | 37.21 | 64.30 | 2.15 | 406 | 0 | -665.45 | 2017.12.26–2026.10.01 | 31% real ticks | chất lượng tick 31% real ticks < 90% |
| CHƯA ĐO ĐƯỢC | od_mql5344ed0d8ab12c7f0_XM_CSV | mql5_344ed0d8ab12c7f0 | NZDUSDmicro | H1 | 3263.62 | 17.99 | 37.24 | 52.51 | 3.31 | 546 | 0 | -197.63 | 2017.12.26–2026.10.01 | 31% real ticks | chất lượng tick 31% real ticks < 90%; 4 lệnh còn mở bị đóng cuối kỳ |
| CHƯA ĐO ĐƯỢC | od_mql514d2e7f097c4ff6e_XM_CSV | mql5_14d2e7f097c4ff6e | NZDUSDmicro | H1 | 1742.30 | 12.20 | 19.88 | 81.63 | 68.79 | 54 | 0 | 89.90 | 2017.12.26–2026.10.01 | 31% real ticks | chất lượng tick 31% real ticks < 90% |
| CHƯA ĐO ĐƯỢC | od_skst299b0817f66d4096_XM_CSV | sk_st_299b0817f66d4096 | EURUSD# | H1 | -967.16 | -92.20 | -72.24 | 98.12 | 0.57 | 27 | 2 | 0.00 | 2025.01.30–2026.06.03 | 100% real ticks | SAI SYMBOL EURUSD# (việc EURUSDmicro); ít lệnh (27 < 30); lịch sử ngắn (1.3 năm) |
| CHƯA ĐO ĐƯỢC | od_skst48a4616b10a6ff9c_XM_CSV | sk_st_48a4616b10a6ff9c | EURUSD# | H1 | -984.40 | -95.53 | -73.53 | 98.67 | 0.10 | 6 | 2 | 0.00 | 2025.01.30–2026.06.03 | 100% real ticks | SAI SYMBOL EURUSD# (việc EURUSDmicro); ít lệnh (6 < 30); lịch sử ngắn (1.3 năm) |
