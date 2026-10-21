# Vòng 2 — kết quả (tự sinh bởi `python -m nhan.vong2`)

Lúc chạy: 2026-10-21 08:52 (giờ box, UTC+7). Ngưỡng tầng: xem `tai_lieu/VONG_2.md`.

**Nhãn:** cột MT5 = ĐO THẬT (lệnh real tick vòng 1); equity *tái dựng* từ lệnh + giá H1 của chính lần chạy MT5; stress phí, Monte Carlo, Python = **MÔ PHỎNG**.

## 1. Kiểm tra chặt trên lệnh MT5 thật

| id | Symbol | TF | Năm | Lệnh | Lãi kép BC % | Lãi kép tái dựng % | Lãi kép stress % (MÔ PHỎNG) | DD BC % | DD equity tái dựng % | DD lệnh đóng % | DD stress % | MC DD equity p95 % (stress, MÔ PHỎNG) | WF 3 đoạn %/năm | Py/MT5 | Tầng |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| od_skea8897567020_XM_CSV | GBPNZDmicro | H1 | 2.76 | 154 | 37.3 | 37.3 | 33.0 | 45.6 | 43.6 | 10.0 | 45.8 | 80.7 | 49 / 51 / 17 | 1.24 | B |
| od_mql5a790e25e547f0b57_XM_CSV | AUDNZDmicro | H4 | 2.74 | 31 | 17.5 | 17.5 | 16.2 | 20.9 | 19.6 | 1.5 | 19.9 | 40.7 | 12 / 17 / 22 | 0.99 | B |
| od_skst4ac0c7fd10781af4_XM_CSV | EURUSDmicro | H1 | 1.34 | 73 | 330.2 | 331.4 | 310.9 | 49.5 | 45.5 | 0.0 | 47.7 | 51.8 | 1171 / 365 / 62 | 0.97 | C |
| od_ghep9c03cef0b89f948f_XM_CSV | GBPCADmicro |  | 2.76 | 129 | 173.2 | 173.5 | 167.2 | 60.0 | 59.1 | 0.8 | 61.6 | 75.7 | 487 / 166 / 41 | — | C |
| od_ghepea3b5db61a7c4792_XM_CSV | GBPCADmicro |  | 2.76 | 279 | 147.1 | 147.3 | 141.9 | 45.6 | 44.4 | 0.0 | 46.8 | 82.6 | 441 / 80 / 59 | — | C |
| od_skea44640140cc_XM_CSV | GBPCADmicro | H1 | 2.76 | 616 | 138.6 | 138.8 | 130.9 | 45.8 | 43.6 | 0.0 | 45.9 | 66.4 | 396 / 86 / 51 | 1.03 | C |
| od_ghepe9b41c33d4deee54_XM_CSV | GBPNZDmicro |  | 2.76 | 135 | 122.7 | 122.9 | 119.5 | 43.6 | 41.5 | 0.0 | 42.5 | 71.8 | 343 / 68 / 50 | — | C |
| od_tohop16b0d75bb149f634_XM_CSV | GBPCADmicro | H1 | 2.76 | 127 | 92.2 | 92.3 | 88.4 | 55.9 | 55.2 | 0.0 | 57.7 | 77.7 | 120 / 79 / 78 | 0.97 | C |
| od_skea0075f624b3_XM_CSV | GBPNZDmicro | H1 | 2.74 | 139 | 91.2 | 91.4 | 86.6 | 52.8 | 50.1 | 0.0 | 52.6 | 84.4 | 175 / 74 / 48 | 1.02 | C |
| od_ghepc9f8a1b857b9a416_XM_CSV | GBPCADmicro |  | 2.76 | 122 | 89.5 | 89.6 | 85.9 | 51.4 | 50.8 | 0.0 | 53.1 | 84.5 | 152 / 86 / 51 | — | C |
| od_ghep6f5c193256881f31_XM_CSV | GBPCADmicro |  | 2.76 | 324 | 86.2 | 86.3 | 75.1 | 49.3 | 50.2 | 0.0 | 58.3 | 84.8 | 108 / 107 / 49 | — | C |
| od_skea0ca971ac32_XM_CSV | GBPNZDmicro | H4 | 2.76 | 27 | 85.9 | 86.0 | 83.3 | 50.6 | 45.7 | 1.0 | 46.6 | 81.8 | 210 / 70 / 22 | 1.13 | C |
| od_skstadd3a54f8edcbce2_XM_CSV | EURUSDmicro | H1 | 1.34 | 15 | 70.3 | 70.5 | 65.6 | 60.8 | 62.8 | 0.0 | 64.2 | 65.5 | 50 / 119 / 47 | 1.05 | C |
| od_skea0b8298aa53_XM_CSV | GOLDmicro | H1 | 2.76 | 16 | 68.0 | 68.1 | 67.0 | 43.2 | 43.3 | 0.0 | 43.6 | 42.5 | 97 / 8 / 125 | 1.21 | C |
| od_skea8771fe6061_XM_CSV | EURCHFmicro |  | 2.72 | 30 | 67.1 | 67.2 | 64.0 | 37.7 | 37.8 | 0.0 | 39.2 | 42.8 | 114 / 74 / 26 | — | C |
| od_ghep60ff9350c26c63ee_XM_CSV | GBPCADmicro |  | 2.76 | 322 | 66.9 | 67.0 | 62.4 | 23.1 | 22.8 | 0.0 | 24.1 | 47.4 | 104 / 71 / 39 | — | C |
| od_mql5f3313c2c79f00c10_XM_CSV | EURGBPmicro | H4 | 2.74 | 178 | 66.1 | 66.2 | 60.5 | 50.6 | 52.5 | 6.4 | 57.8 | 78.5 | 170 / -28 / 120 | 1.03 | C |
| od_skeab536f57733_XM_CSV | EURUSDmicro |  | 2.76 | 249 | 64.4 | 64.5 | 61.8 | 39.8 | 39.4 | 6.8 | 40.8 | 57.1 | 84 / 97 / 16 | — | C |
| od_ghep0bf2c31fbfc9dea0_XM_CSV | GBPCADmicro |  | 2.76 | 78 | 62.2 | 62.2 | 52.4 | 52.5 | 52.2 | 8.4 | 57.7 | 92.3 | 122 / 49 / 31 | — | C |
| od_skeaa7cd39087e_XM_CSV | GOLDmicro | H1 | 2.76 | 351 | 60.0 | 60.0 | 53.5 | 60.6 | 55.6 | 56.8 | 58.5 | 85.4 | 71 / 232 / -29 | 0.69 | C |
| od_skeadd170ac7bf_XM_CSV | USDCADmicro |  | 2.76 | 109 | 54.0 | 54.1 | 52.4 | 54.6 | 53.8 | 5.4 | 55.4 | 81.0 | 54 / 25 / 90 | — | C |
| od_skeaff87f96be7_XM_CSV | GBPCADmicro | H1 | 2.75 | 211 | 53.3 | 53.4 | 50.5 | 31.7 | 40.9 | 9.6 | 42.5 | 58.3 | 62 / 52 / 46 | 1.05 | C |
| od_skea5fdf89aa94_XM_CSV | USDJPYmicro |  | 1.85 | 6 | 47.7 | 47.8 | 46.8 | 49.2 | 47.8 | 0.0 | 48.2 | 54.1 | 52 / 113 / -0 | — | C |
| od_skea3279057100_XM_CSV | EURGBPmicro | H1 | 2.76 | 203 | 44.7 | 44.8 | 31.0 | 64.0 | 63.4 | 36.3 | 76.3 | 93.7 | 147 / -11 / 44 | -0.57 | C |
| od_b0be91a35f43f34a_XM_CSV | USDCADmicro | H4 | 2.71 | 46 | 44.0 | 44.0 | 39.6 | 58.6 | 57.2 | 0.0 | 61.8 | 88.7 | 82 / 25 / 31 | 0.95 | C |
| od_skead5df5bc834_XM_CSV | GOLDmicro |  | 2.76 | 268 | 41.0 | 41.0 | 38.9 | 47.7 | 47.2 | 6.7 | 49.1 | 62.3 | 37 / 55 / 32 | — | C |
| od_skea31214192bc_XM_CSV | GBPNZDmicro |  | 2.64 | 36 | 39.6 | 39.6 | 32.7 | 29.8 | 29.6 | 0.0 | 32.0 | 44.7 | 54 / 40 / 26 | — | C |
| od_skeadc40280363_XM_CSV | CADJPYmicro |  | 2.76 | 160 | 39.6 | 39.6 | 37.7 | 38.8 | 37.2 | 8.3 | 37.4 | 47.6 | 66 / 57 / 4 | — | C |
| od_skea02906b7d6a_XM_CSV | GOLDmicro | H4 | 2.76 | 180 | 39.2 | 39.3 | 35.1 | 70.3 | 65.0 | 64.5 | 66.9 | 89.2 | 92 / 115 / -39 | 0.13 | C |
| od_skea154c9fdee7_XM_CSV | GBPCADmicro |  | 2.72 | 182 | 38.3 | 38.3 | 34.6 | 56.5 | 57.0 | 3.4 | 59.8 | 77.7 | 55 / 38 / 24 | — | C |
| od_skea89d6f8661b_XM_CSV | AUDUSDmicro |  | 2.68 | 75 | 37.1 | 37.1 | 34.4 | 31.3 | 32.6 | 2.0 | 33.5 | 48.3 | 61 / 4 / 54 | — | C |
| od_skstc21c2acd239f3c87_XM_CSV | EURUSDmicro | H1 | 1.34 | 20 | 37.0 | 37.1 | 34.4 | 49.7 | 46.3 | 0.0 | 46.9 | 47.7 | 22 / 70 / 23 | 1.01 | C |
| od_skea45b39eb1d5_XM_CSV | AUDJPYmicro | H4 | 2.76 | 202 | 36.1 | 36.1 | 29.5 | 46.0 | 46.0 | 7.5 | 50.8 | 63.4 | 80 / 16 / 21 | 0.87 | C |
| od_skea5049c79288_XM_CSV | GBPCADmicro | H4 | 2.71 | 83 | 34.8 | 34.8 | 33.2 | 30.4 | 30.0 | 9.9 | 31.0 | 53.3 | 63 / 11 / 35 | 1.15 | C |
| od_skeaa3d6925a71_XM_CSV | AUDUSDmicro |  | 2.74 | 533 | 32.5 | 32.6 | 26.7 | 56.0 | 52.7 | 44.0 | 54.9 | 81.5 | 121 / 72 / -39 | — | C |
| od_ghep89811dee41bce6b9_XM_CSV | GOLDmicro |  | 2.76 | 92 | 32.3 | 32.4 | 31.4 | 39.5 | 39.0 | 7.4 | 40.0 | 54.8 | 31 / 38 / 29 | — | C |
| od_mql5fd4bc285e11ab5a1_XM_CSV | EURCHFmicro | H4 | 2.76 | 138 | 31.0 | 31.0 | 28.8 | 49.3 | 46.5 | 20.1 | 47.5 | 64.0 | 57 / 42 / -0 | 0.76 | C |
| od_skea61c21a2049_XM_CSV | CADJPYmicro |  | 2.74 | 219 | 29.2 | 29.2 | 25.8 | 28.3 | 27.1 | 3.1 | 28.7 | 36.6 | 35 / 37 / 17 | — | C |
| od_mql5e3c3e4f028dbab72_XM_CSV | EURCADmicro | H4 | 2.76 | 120 | 29.0 | 29.1 | 27.6 | 18.4 | 18.0 | 1.5 | 18.3 | 25.2 | 47 / 19 / 23 | 1.07 | C |
| od_mql5e31426a40a5897fc_XM_CSV | GBPUSDmicro | H4 | 2.59 | 15 | 28.7 | 28.7 | 28.0 | 58.7 | 55.9 | 0.0 | 56.4 | 63.6 | 40 / 17 / 30 | 1.00 | C |
| od_skea2f7862a741_XM_CSV | AUDUSDmicro |  | 2.61 | 71 | 28.5 | 28.6 | 25.6 | 17.9 | 16.2 | 0.0 | 17.1 | 18.9 | 33 / 28 / 23 | — | C |
| od_2600ea39abbd7b0f_XM_CSV | GBPNZDmicro |  | 2.76 | 131 | 27.7 | 27.8 | 25.1 | 27.1 | 25.3 | 5.8 | 25.3 | 53.0 | 26 / 40 / 18 | — | C |
| od_ghepeab4082becc0e276_XM_CSV | EURGBPmicro |  | 2.74 | 124 | 27.6 | 27.7 | 26.6 | 54.0 | 56.3 | 0.1 | 57.3 | 70.1 | 29 / -22 / 87 | — | C |
| od_skea0c762cdb38_XM_CSV | CHFJPYmicro | H4 | 2.55 | 39 | 27.5 | 27.6 | 25.8 | 19.9 | 20.2 | 0.0 | 20.4 | 27.9 | 29 / 37 / 17 | 1.03 | C |
| od_skeaf7a71f885d_XM_CSV | GBPNZDmicro |  | 2.76 | 479 | 27.5 | 27.5 | 23.4 | 35.4 | 32.0 | 14.3 | 35.1 | 65.4 | 14 / 41 / 30 | — | C |
| od_mql5ad7d22b5b165a673_XM_CSV | GBPUSDmicro | H4 | 2.76 | 134 | 27.2 | 27.2 | 25.1 | 55.0 | 53.6 | 10.1 | 55.0 | 74.4 | 28 / 37 / 17 | 0.72 | C |
| od_skeafdbf5bcad6_XM_CSV | EURCADmicro | H1 | 2.76 | 190 | 26.4 | 26.5 | 17.8 | 18.2 | 18.9 | 29.8 | 20.9 | 50.5 | 45 / 64 / -12 | 0.91 | C |
| od_skeabc8157a270_XM_CSV | NZDJPYmicro |  | 2.74 | 292 | 25.2 | 25.2 | 20.8 | 60.2 | 59.5 | 8.6 | 62.0 | 66.4 | 36 / 10 / 30 | — | C |
| od_mql5d8f573b8c2314bbf_XM_CSV | EURAUDmicro | H1 | 2.76 | 106 | 24.4 | 24.5 | 19.5 | 41.4 | 47.1 | 41.7 | 49.2 | 58.6 | 82 / 43 / -26 | 1.28 | C |
| od_skea0806a3a5e5_XM_CSV | AUDNZDmicro | H1 | 2.76 | 29 | 24.4 | 24.4 | 23.3 | 25.9 | 24.6 | 4.5 | 25.0 | 44.0 | 19 / 14 / 41 | 0.95 | C |
| od_skstaca366b679c75482_XM_CSV | EURUSDmicro | H1 | 1.34 | 15 | 24.4 | 24.4 | 22.6 | 18.2 | 18.3 | 0.0 | 18.4 | 21.0 | 15 / 27 / 33 | 0.96 | C |
| od_skea0cc19095a9_XM_CSV | GBPNZDmicro | H1 | 2.76 | 429 | 24.3 | 24.3 | 20.8 | 28.9 | 27.5 | 3.9 | 28.7 | 39.6 | 23 / 33 / 18 | 0.85 | C |
| od_skea0ab6e87da9_XM_CSV | EURGBPmicro |  | 2.74 | 245 | 22.8 | 22.8 | 18.1 | 75.7 | 74.4 | 2.3 | 79.1 | 86.5 | 18 / 34 / 18 | — | C |
| od_skea363d6c8238_XM_CSV | NZDJPYmicro |  | 2.68 | 63 | 22.6 | 22.6 | 21.6 | 33.0 | 30.5 | 0.0 | 30.8 | 39.0 | 22 / 31 / 16 | — | C |
| od_skea66a65a142a_XM_CSV | GBPNZDmicro |  | 2.76 | 263 | 22.4 | 22.5 | 12.2 | 53.0 | 50.2 | 28.3 | 55.1 | 90.6 | 47 / 52 / -20 | — | C |
| od_0557d803384c6211_XM_CSV | GBPUSDmicro |  | 2.76 | 182 | 22.1 | 22.2 | 19.2 | 47.1 | 46.1 | 3.4 | 46.9 | 55.5 | 30 / 23 / 14 | — | C |
| od_skeaaba30a4e06_XM_CSV | USDJPYmicro | H4 | 2.76 | 164 | 21.9 | 21.9 | 20.2 | 49.7 | 48.1 | 5.6 | 48.4 | 57.4 | 39 / 17 / 12 | 0.89 | C |
| od_nhapcf8073245473d2a1_XM_CSV | EURGBPmicro | H4 | 2.76 | 188 | 20.8 | 20.8 | 17.8 | 67.8 | 78.2 | 18.1 | 81.9 | 92.1 | 16 / -22 / 114 | 1.34 | C |
| od_skeae2482b06a4_XM_CSV | GBPUSDmicro |  | 2.76 | 1338 | 20.6 | 20.6 | 17.3 | 41.9 | 41.2 | 6.2 | 42.3 | 50.0 | 28 / 25 / 9 | — | C |
| od_skea09c76b6df5_XM_CSV | GBPAUDmicro |  | 2.70 | 224 | 20.2 | 20.2 | 16.3 | 34.5 | 34.4 | 3.0 | 35.8 | 72.8 | 30 / 19 / 12 | — | C |
| od_mql5b39a9f3ba216fb47_XM_CSV | CHFJPYmicro | H1 | 2.76 | 392 | 19.6 | 19.6 | 18.2 | 27.1 | 28.6 | 16.4 | 29.7 | 40.1 | 27 / 22 / 11 | 0.86 | C |
| od_mql525573694a7f03d3a_XM_CSV | EURGBPmicro | H1 | 2.76 | 282 | 19.5 | 19.5 | 17.4 | 31.5 | 33.4 | 1.6 | 35.2 | 49.0 | 20 / -13 / 61 | 1.04 | C |
| od_skea5539346824_XM_CSV | EURGBPmicro |  | 2.72 | 233 | 19.2 | 19.3 | 14.9 | 46.5 | 48.9 | 2.2 | 53.4 | 65.5 | 20 / -15 / 67 | — | C |
| od_skeaf88d932deb_XM_CSV | GOLDmicro |  | 2.76 | 605 | 18.8 | 18.9 | 16.5 | 53.0 | 53.2 | 7.6 | 53.7 | 62.2 | 12 / 20 / 25 | — | C |
| od_mql5b5a04d7c15935f8b_XM_CSV | GBPNZDmicro | H1 | 2.76 | 208 | 18.3 | 18.3 | 14.7 | 33.3 | 29.3 | 12.9 | 31.8 | 55.4 | 6 / 26 / 24 | 0.98 | C |
| od_skead0a7af9f8b_XM_CSV | AUDJPYmicro |  | 2.74 | 158 | 17.9 | 17.9 | 16.7 | 8.4 | 7.2 | 0.0 | 7.2 | 7.9 | 22 / 21 / 11 | — | C |
| od_skea0ab4d307d3_XM_CSV | EURNZDmicro | H1 | 2.76 | 286 | 17.4 | 17.5 | 14.0 | 48.6 | 38.8 | 7.7 | 40.3 | 62.7 | 23 / 23 / 7 | 0.74 | C |
| od_tohop564be9bb91406c57_XM_CSV | GBPUSDmicro | H1 | 2.72 | 62 | 17.4 | 17.4 | 16.3 | 26.2 | 26.9 | 0.0 | 27.5 | 38.5 | 19 / 17 / 17 | 1.00 | C |
| od_skea135e93ee32_XM_CSV | EURUSDmicro | H1 | 2.76 | 57 | 17.3 | 17.4 | 16.6 | 20.1 | 18.3 | 0.7 | 18.6 | 27.9 | 11 / 26 / 15 | 0.99 | C |
| od_skeaf3d30ea9da_XM_CSV | GBPAUDmicro |  | 2.76 | 956 | 16.9 | 16.9 | 13.9 | 47.2 | 44.4 | 2.0 | 45.0 | 49.6 | 18 / 16 / 19 | — | C |
| od_tohop09a3b2ddc3e78dc8_XM_CSV | EURUSDmicro | H4 | 2.76 | 69 | 15.6 | 15.6 | 14.5 | 32.0 | 31.6 | 15.2 | 32.4 | 44.5 | 22 / 8 / 18 | 1.41 | C |
| od_tohopc2d52300cc825dff_XM_CSV | AUDNZDmicro | H1 | 2.74 | 144 | 14.4 | 14.4 | 11.6 | 25.6 | 26.1 | 19.4 | 29.1 | 45.4 | -15 / 32 / 34 | 1.25 | C |
| od_3304d2fad28adef6_XM_CSV | USDCADmicro | H4 | 2.59 | 64 | 14.2 | 14.2 | 9.1 | 40.2 | 47.3 | 23.6 | 51.5 | 60.4 | 19 / 26 / -1 | 1.86 | C |
| od_mql5e52afb999eca4bd1_XM_CSV | EURGBPmicro | H1 | 2.76 | 110 | 13.7 | 13.7 | 11.7 | 24.9 | 30.0 | 17.4 | 31.7 | 58.9 | 10 / 2 / 33 | 1.09 | C |
| od_skea7eec0ab393_XM_CSV | GBPAUDmicro |  | 2.70 | 294 | 13.1 | 13.1 | 8.6 | 53.0 | 59.5 | 38.8 | 62.5 | 81.8 | 56 / 18 / -21 | — | C |
| od_tohop9acc6e0d2f784cb9_XM_CSV | GBPCADmicro | H1 | 2.72 | 59 | 12.9 | 12.9 | 12.4 | 10.6 | 10.4 | 0.0 | 10.4 | 19.1 | 17 / 8 / 15 | 0.97 | C |
| od_018dcb1347276c97_XM_CSV | EURNZDmicro | H4 | 2.72 | 76 | 12.1 | 12.1 | 10.8 | 18.4 | 14.8 | 3.2 | 15.0 | 28.8 | 8 / 22 / 7 | 0.96 | C |
| od_skea0757c93eb3_XM_CSV | EURNZDmicro | H4 | 2.76 | 2 | 10.6 | 10.6 | 10.2 | 29.2 | 17.4 | 0.0 | 17.4 | 18.3 | 35 / 0 / -0 | 0.91 | C |

Lí do chưa lên tầng (rút gọn):

- `od_skst4ac0c7fd10781af4_XM_CSV` (C): thiếu A: lịch sử MT5 1.3 < 2.5 năm; lệnh 73 < 100; đa cặp None < 50% — thiếu B: lịch sử MT5 1.3 < 2.0 năm; đa cặp None < 30%
- `od_ghep9c03cef0b89f948f_XM_CSV` (C): thiếu A: DD equity stress 61.6 > 60%; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_ghepea3b5db61a7c4792_XM_CSV` (C): thiếu A: MC DD p95 82.6 > 80%; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea44640140cc_XM_CSV` (C): thiếu A: đa cặp 12 < 50% — thiếu B: đa cặp 12 < 30%
- `od_ghepe9b41c33d4deee54_XM_CSV` (C): thiếu A: Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_tohop16b0d75bb149f634_XM_CSV` (C): thiếu A: đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea0075f624b3_XM_CSV` (C): thiếu A: MC DD p95 84.37 > 80%; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_ghepc9f8a1b857b9a416_XM_CSV` (C): thiếu A: MC DD p95 84.51 > 80%; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_ghep6f5c193256881f31_XM_CSV` (C): thiếu A: MC DD p95 84.82 > 80%; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea0ca971ac32_XM_CSV` (C): thiếu A: MC DD p95 81.83 > 80%; lệnh 27 < 100; đa cặp None < 50%; OOS Python None < 10% — thiếu B: lệnh 27 < 30; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skstadd3a54f8edcbce2_XM_CSV` (C): thiếu A: lịch sử MT5 1.3 < 2.5 năm; DD equity stress 64.2 > 60%; lệnh 15 < 100; đa cặp None < 50% — thiếu B: lịch sử MT5 1.3 < 2.0 năm; lệnh 15 < 30; đa cặp None < 30%
- `od_skea0b8298aa53_XM_CSV` (C): thiếu A: lệnh 16 < 100; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: lệnh 16 < 30; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea8771fe6061_XM_CSV` (C): thiếu A: lệnh 30 < 100; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_ghep60ff9350c26c63ee_XM_CSV` (C): thiếu A: Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_mql5f3313c2c79f00c10_XM_CSV` (C): thiếu A: đoạn WF tệ nhất -27.65 < 5%; đa cặp 4 < 50%; cao nguyên 0.33 < 0.6 — thiếu B: đoạn WF tệ nhất -27.65 < 0%; đa cặp 4 < 30%; cao nguyên 0.33 < 0.4
- `od_skeab536f57733_XM_CSV` (C): thiếu A: Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_ghep0bf2c31fbfc9dea0_XM_CSV` (C): thiếu A: MC DD p95 92.34 > 80%; lệnh 78 < 100; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50% — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skeaa7cd39087e_XM_CSV` (C): thiếu A: MC DD p95 85.38 > 80%; đoạn WF tệ nhất -29.39 < 5%; Python/MT5 0.69 ngoài 0.8–1.25; đa cặp None < 50% — thiếu B: đoạn WF tệ nhất -29.39 < 0%; Python/MT5 0.69 ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%
- `od_skeadd170ac7bf_XM_CSV` (C): thiếu A: MC DD p95 80.99 > 80%; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skeaff87f96be7_XM_CSV` (C): thiếu A: đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea5fdf89aa94_XM_CSV` (C): thiếu A: lịch sử MT5 1.9 < 2.5 năm; đoạn WF tệ nhất -0.0 < 5%; lệnh 6 < 100; Python/MT5 None ngoài 0.8–1.25 — thiếu B: lịch sử MT5 1.9 < 2.0 năm; lệnh 6 < 30; Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%
- `od_skea3279057100_XM_CSV` (C): thiếu A: DD equity stress 76.3 > 60%; MC DD p95 93.66 > 80%; đoạn WF tệ nhất -10.63 < 5%; Python/MT5 -0.57 ngoài 0.8–1.25 — thiếu B: đoạn WF tệ nhất -10.63 < 0%; Python/MT5 -0.57 ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%
- `od_b0be91a35f43f34a_XM_CSV` (C): thiếu A: DD equity stress 61.8 > 60%; MC DD p95 88.74 > 80%; lệnh 46 < 100; đa cặp None < 50% — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skead5df5bc834_XM_CSV` (C): thiếu A: Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea31214192bc_XM_CSV` (C): thiếu A: lệnh 36 < 100; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skeadc40280363_XM_CSV` (C): thiếu A: đoạn WF tệ nhất 4.13 < 5%; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea02906b7d6a_XM_CSV` (C): thiếu A: DD equity stress 66.9 > 60%; MC DD p95 89.22 > 80%; đoạn WF tệ nhất -38.61 < 5%; Python/MT5 0.13 ngoài 0.8–1.25 — thiếu B: đoạn WF tệ nhất -38.61 < 0%; Python/MT5 0.13 ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%
- `od_skea154c9fdee7_XM_CSV` (C): thiếu A: Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea8897567020_XM_CSV` (B): thiếu A: MC DD p95 80.66 > 80%; đa cặp 36 < 50%
- `od_skea89d6f8661b_XM_CSV` (C): thiếu A: đoạn WF tệ nhất 4.5 < 5%; lệnh 75 < 100; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50% — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skstc21c2acd239f3c87_XM_CSV` (C): thiếu A: lịch sử MT5 1.3 < 2.5 năm; lệnh 20 < 100; đa cặp None < 50% — thiếu B: lịch sử MT5 1.3 < 2.0 năm; lệnh 20 < 30; đa cặp None < 30%
- `od_skea45b39eb1d5_XM_CSV` (C): thiếu A: đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea5049c79288_XM_CSV` (C): thiếu A: lệnh 83 < 100; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skeaa3d6925a71_XM_CSV` (C): thiếu A: MC DD p95 81.5 > 80%; đoạn WF tệ nhất -38.69 < 5%; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50% — thiếu B: đoạn WF tệ nhất -38.69 < 0%; Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%
- `od_ghep89811dee41bce6b9_XM_CSV` (C): thiếu A: lệnh 92 < 100; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_mql5fd4bc285e11ab5a1_XM_CSV` (C): thiếu A: đoạn WF tệ nhất -0.03 < 5%; Python/MT5 0.76 ngoài 0.8–1.25; đa cặp 12 < 50%; OOS Python 8.84 < 10% — thiếu B: đoạn WF tệ nhất -0.03 < 0%; đa cặp 12 < 30%
- `od_skea61c21a2049_XM_CSV` (C): thiếu A: Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_mql5e3c3e4f028dbab72_XM_CSV` (C): thiếu A: đa cặp 20 < 50%; cao nguyên 0.11 < 0.6 — thiếu B: đa cặp 20 < 30%; cao nguyên 0.11 < 0.4
- `od_mql5e31426a40a5897fc_XM_CSV` (C): thiếu A: lệnh 15 < 100; đa cặp 20 < 50% — thiếu B: lệnh 15 < 30; đa cặp 20 < 30%
- `od_skea2f7862a741_XM_CSV` (C): thiếu A: lệnh 71 < 100; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_2600ea39abbd7b0f_XM_CSV` (C): thiếu A: Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_ghepeab4082becc0e276_XM_CSV` (C): thiếu A: đoạn WF tệ nhất -22.49 < 5%; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: đoạn WF tệ nhất -22.49 < 0%; Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%
- `od_skea0c762cdb38_XM_CSV` (C): thiếu A: lệnh 39 < 100; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skeaf7a71f885d_XM_CSV` (C): thiếu A: Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_mql5ad7d22b5b165a673_XM_CSV` (C): thiếu A: Python/MT5 0.72 ngoài 0.8–1.25; đa cặp 24 < 50%; OOS Python 9.59 < 10% — thiếu B: đa cặp 24 < 30%
- `od_skeafdbf5bcad6_XM_CSV` (C): thiếu A: đoạn WF tệ nhất -11.79 < 5%; đa cặp 4 < 50%; OOS Python -7.71 < 10% — thiếu B: đoạn WF tệ nhất -11.79 < 0%; đa cặp 4 < 30%; OOS Python -7.71 < 0%
- `od_skeabc8157a270_XM_CSV` (C): thiếu A: DD equity stress 62.0 > 60%; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_mql5d8f573b8c2314bbf_XM_CSV` (C): thiếu A: đoạn WF tệ nhất -26.48 < 5%; Python/MT5 1.28 ngoài 0.8–1.25; đa cặp 16 < 50%; OOS Python -37.69 < 10% — thiếu B: đoạn WF tệ nhất -26.48 < 0%; đa cặp 16 < 30%; OOS Python -37.69 < 0%
- `od_skea0806a3a5e5_XM_CSV` (C): thiếu A: lệnh 29 < 100; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: lệnh 29 < 30; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skstaca366b679c75482_XM_CSV` (C): thiếu A: lịch sử MT5 1.3 < 2.5 năm; lệnh 15 < 100; đa cặp None < 50% — thiếu B: lịch sử MT5 1.3 < 2.0 năm; lệnh 15 < 30; đa cặp None < 30%
- `od_skea0cc19095a9_XM_CSV` (C): thiếu A: đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea0ab6e87da9_XM_CSV` (C): thiếu A: DD equity stress 79.1 > 60%; MC DD p95 86.48 > 80%; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50% — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea363d6c8238_XM_CSV` (C): thiếu A: lệnh 63 < 100; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea66a65a142a_XM_CSV` (C): thiếu A: lãi kép sau stress 12.2 < 15%; MC DD p95 90.64 > 80%; đoạn WF tệ nhất -19.57 < 5%; Python/MT5 None ngoài 0.8–1.25 — thiếu B: đoạn WF tệ nhất -19.57 < 0%; Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%
- `od_0557d803384c6211_XM_CSV` (C): thiếu A: Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skeaaba30a4e06_XM_CSV` (C): thiếu A: đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_nhapcf8073245473d2a1_XM_CSV` (C): thiếu A: DD equity stress 81.9 > 60%; MC DD p95 92.06 > 80%; đoạn WF tệ nhất -22.26 < 5%; Python/MT5 1.34 ngoài 0.8–1.25 — thiếu B: DD equity stress 81.9 > 80%; đoạn WF tệ nhất -22.26 < 0%; đa cặp 4 < 30%; cao nguyên 0.38 < 0.4
- `od_skeae2482b06a4_XM_CSV` (C): thiếu A: Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea09c76b6df5_XM_CSV` (C): thiếu A: Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_mql5b39a9f3ba216fb47_XM_CSV` (C): thiếu A: cao nguyên 0.11 < 0.6 — thiếu B: cao nguyên 0.11 < 0.4
- `od_mql525573694a7f03d3a_XM_CSV` (C): thiếu A: đoạn WF tệ nhất -12.65 < 5%; đa cặp 16 < 50%; cao nguyên 0.5 < 0.6 — thiếu B: đoạn WF tệ nhất -12.65 < 0%; đa cặp 16 < 30%
- `od_skea5539346824_XM_CSV` (C): thiếu A: lãi kép sau stress 14.9 < 15%; đoạn WF tệ nhất -15.05 < 5%; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50% — thiếu B: đoạn WF tệ nhất -15.05 < 0%; Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%
- `od_skeaf88d932deb_XM_CSV` (C): thiếu A: Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_mql5b5a04d7c15935f8b_XM_CSV` (C): thiếu A: lãi kép sau stress 14.7 < 15%; đa cặp 24 < 50%; OOS Python 5.79 < 10%; cao nguyên 0.12 < 0.6 — thiếu B: đa cặp 24 < 30%; cao nguyên 0.12 < 0.4
- `od_skead0a7af9f8b_XM_CSV` (C): thiếu A: Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_mql5a790e25e547f0b57_XM_CSV` (B): thiếu A: lệnh 31 < 100
- `od_skea0ab4d307d3_XM_CSV` (C): thiếu A: lãi kép sau stress 14.0 < 15%; Python/MT5 0.74 ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_tohop564be9bb91406c57_XM_CSV` (C): thiếu A: lệnh 62 < 100; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea135e93ee32_XM_CSV` (C): thiếu A: lệnh 57 < 100; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skeaf3d30ea9da_XM_CSV` (C): thiếu A: lãi kép sau stress 13.9 < 15%; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_tohop09a3b2ddc3e78dc8_XM_CSV` (C): thiếu A: lãi kép sau stress 14.5 < 15%; lệnh 69 < 100; Python/MT5 1.41 ngoài 0.8–1.25; đa cặp 28 < 50% — thiếu B: Python/MT5 1.41 ngoài 0.7–1.4; đa cặp 28 < 30%
- `od_tohopc2d52300cc825dff_XM_CSV` (C): thiếu A: lãi kép sau stress 11.6 < 15%; đoạn WF tệ nhất -15.31 < 5%; đa cặp None < 50%; OOS Python None < 10% — thiếu B: đoạn WF tệ nhất -15.31 < 0%; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_3304d2fad28adef6_XM_CSV` (C): thiếu A: lãi kép sau stress 9.1 < 15%; đoạn WF tệ nhất -0.75 < 5%; lệnh 64 < 100; Python/MT5 1.86 ngoài 0.8–1.25 — thiếu B: lãi kép sau stress 9.1 < 10%; đoạn WF tệ nhất -0.75 < 0%; Python/MT5 1.86 ngoài 0.7–1.4; đa cặp None < 30%
- `od_mql5e52afb999eca4bd1_XM_CSV` (C): thiếu A: lãi kép sau stress 11.7 < 15%; đoạn WF tệ nhất 1.59 < 5%; đa cặp 12 < 50% — thiếu B: đa cặp 12 < 30%
- `od_skea7eec0ab393_XM_CSV` (C): thiếu A: lãi kép sau stress 8.6 < 15%; DD equity stress 62.5 > 60%; MC DD p95 81.75 > 80%; đoạn WF tệ nhất -21.39 < 5% — thiếu B: lãi kép sau stress 8.6 < 10%; đoạn WF tệ nhất -21.39 < 0%; Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%
- `od_tohop9acc6e0d2f784cb9_XM_CSV` (C): thiếu A: lãi kép sau stress 12.4 < 15%; lệnh 59 < 100; đa cặp None < 50%; OOS Python None < 10% — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_018dcb1347276c97_XM_CSV` (C): thiếu A: lãi kép sau stress 10.8 < 15%; lệnh 76 < 100; đa cặp None < 50%; OOS Python None < 10% — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea0757c93eb3_XM_CSV` (C): thiếu A: lãi kép sau stress 10.2 < 15%; đoạn WF tệ nhất 0.0 < 5%; lệnh 2 < 100; đa cặp None < 50% — thiếu B: lệnh 2 < 30; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4

## 2. Python (MÔ PHỎNG): mặc định tác giả, khung, đa cặp, lưới + cao nguyên

| id | Gốc %/năm | Gốc DD % | OOS 30% %/năm | Mặc định tác giả %/năm | Khung khác | Cặp khác không lỗ | Cao nguyên gốc | Tốt nhất (cao nguyên) | Phép thử | Giây |
|---|---|---|---|---|---|---|---|---|---|---|
| od_ghep9c03cef0b89f948f_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_ghepea3b5db61a7c4792_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_ghepe9b41c33d4deee54_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_tohop16b0d75bb149f634_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea0075f624b3_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_ghepc9f8a1b857b9a416_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_ghep6f5c193256881f31_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea0ca971ac32_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea0b8298aa53_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea8771fe6061_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_ghep60ff9350c26c63ee_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skeab536f57733_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_ghep0bf2c31fbfc9dea0_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skeaa7cd39087e_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skeadd170ac7bf_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skeaff87f96be7_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea5fdf89aa94_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea3279057100_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_b0be91a35f43f34a_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skead5df5bc834_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea31214192bc_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skeadc40280363_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea02906b7d6a_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea154c9fdee7_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea89d6f8661b_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea45b39eb1d5_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea5049c79288_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skeaa3d6925a71_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_ghep89811dee41bce6b9_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea61c21a2049_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea2f7862a741_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_2600ea39abbd7b0f_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_ghepeab4082becc0e276_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea0c762cdb38_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skeaf7a71f885d_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skeabc8157a270_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea0806a3a5e5_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea0cc19095a9_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea0ab6e87da9_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea363d6c8238_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea66a65a142a_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_0557d803384c6211_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skeaaba30a4e06_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skeae2482b06a4_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea09c76b6df5_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea5539346824_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skeaf88d932deb_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skead0a7af9f8b_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea0ab4d307d3_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_tohop564be9bb91406c57_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea135e93ee32_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skeaf3d30ea9da_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_tohopc2d52300cc825dff_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_3304d2fad28adef6_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea7eec0ab393_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_tohop9acc6e0d2f784cb9_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_018dcb1347276c97_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea0757c93eb3_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skst4ac0c7fd10781af4_XM_CSV | 344.1 | 55.8 | 124.5 | 344.1 | H4 -100/168, H1 344/56 | — | 0.75 | 421.3%/năm, DD 40.1%, OOS 176.5, CN 1.0 | 93 | 4 |
| od_skea44640140cc_XM_CSV | 139.2 | 46.3 | 59.5 | 139.2 | H4 133/54, H1 139/46 | 12% (25 cặp) | 0.80 | 171.3%/năm, DD 51.1%, OOS 72.0, CN 1.0 | 118 | 27 |
| od_mql5e3c3e4f028dbab72_XM_CSV | 31.0 | 18.3 | 25.2 | 31.0 | H1 -24/91, H4 31/18 | 20% (25 cặp) | 0.11 | 41.7%/năm, DD 33.0%, OOS 28.4, CN 1.0 | 118 | 8 |
| od_skstaca366b679c75482_XM_CSV | 23.9 | 18.4 | 53.1 | 23.9 | H4 -38/96, H1 24/18 | — | 0.67 | 85.3%/năm, DD 66.1%, OOS 104.8, CN 1.0 | 93 | 4 |
| od_mql5f3313c2c79f00c10_XM_CSV | 59.4 | 56.3 | 72.5 | 59.4 | H1 -100/103, H4 59/56 | 4% (25 cặp) | 0.33 | 63.2%/năm, DD 49.8%, OOS 57.2, CN 1.0 | 118 | 9 |
| od_skstadd3a54f8edcbce2_XM_CSV | 73.9 | 63.6 | 186.2 | 73.9 | H4 -100/129, H1 74/64 | — | 0.57 | 63.3%/năm, DD 44.7%, OOS 175.9, CN 1.0 | 93 | 3 |
| od_skeafdbf5bcad6_XM_CSV | 23.0 | 18.7 | -7.7 | 23.0 | H4 10/33, H1 23/19 | 4% (25 cặp) | 1.00 | 95.1%/năm, DD 27.5%, OOS 33.8, CN 1.0 | 118 | 25 |
| od_mql5a790e25e547f0b57_XM_CSV | 17.3 | 19.6 | 20.0 | 17.3 | H1 25/23, H4 17/20 | 56% (25 cặp) | 0.89 | 25.8%/năm, DD 21.0%, OOS 41.2, CN 1.0 | 118 | 6 |
| od_skstc21c2acd239f3c87_XM_CSV | 41.3 | 52.9 | 91.5 | 41.3 | H4 -100/125, H1 41/53 | — | 0.75 | 94.5%/năm, DD 63.9%, OOS 145.0, CN 1.0 | 93 | 4 |
| od_skea8897567020_XM_CSV | 46.1 | 48.6 | 20.7 | 46.1 | H4 49/34, H1 46/49 | 36% (25 cặp) | 1.00 | 59.4%/năm, DD 39.9%, OOS 37.9, CN 1.0 | 118 | 29 |
| od_mql5b39a9f3ba216fb47_XM_CSV | 18.6 | 46.5 | 16.1 | 18.6 | H4 -5/81, H1 19/46 | 56% (25 cặp) | 0.11 | không có điểm qua chống quá khớp | 118 | 24 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | 30.8 | 50.0 | 8.8 | 30.8 | H1 -100/100, H4 31/50 | 12% (25 cặp) | 0.57 | 33.8%/năm, DD 53.0%, OOS 17.1, CN 1.0 | 118 | 10 |
| od_mql5e31426a40a5897fc_XM_CSV | 26.5 | 59.0 | 35.4 | 26.5 | H1 -16/75, H4 27/59 | 20% (25 cặp) | 0.71 | 14.8%/năm, DD 17.8%, OOS 14.4, CN 1.0 | 118 | 4 |
| od_mql525573694a7f03d3a_XM_CSV | 18.8 | 31.8 | 41.2 | 18.8 | H4 11/41, H1 19/32 | 16% (25 cặp) | 0.50 | 42.2%/năm, DD 44.2%, OOS 10.3, CN 1.0 | 118 | 48 |
| od_mql5b5a04d7c15935f8b_XM_CSV | 16.8 | 24.6 | 5.8 | 16.8 | H4 11/20, H1 17/25 | 24% (25 cặp) | 0.12 | 33.1%/năm, DD 45.7%, OOS 30.5, CN 1.0 | 118 | 27 |
| od_mql5ad7d22b5b165a673_XM_CSV | 18.6 | 61.3 | 9.6 | 18.6 | H1 12/83, H4 19/61 | 24% (25 cặp) | 0.78 | 15.5%/năm, DD 14.9%, OOS 11.4, CN 1.0 | 118 | 7 |
| od_tohop09a3b2ddc3e78dc8_XM_CSV | 20.3 | 21.4 | 14.5 | 20.3 | H1 37/39, H4 20/21 | 28% (25 cặp) | 0.71 | 14.5%/năm, DD 17.2%, OOS 14.6, CN 1.0 | 118 | 6 |
| od_mql5d8f573b8c2314bbf_XM_CSV | 27.4 | 34.8 | -37.7 | 27.4 | H4 19/46, H1 27/35 | 16% (25 cặp) | 0.44 | không có điểm qua chống quá khớp | 118 | 16 |
| od_mql5e52afb999eca4bd1_XM_CSV | 11.0 | 26.1 | 10.8 | 11.0 | H4 8/34, H1 11/26 | 12% (25 cặp) | 0.86 | 51.9%/năm, DD 53.1%, OOS 65.7, CN 1.0 | 118 | 44 |
| od_nhapcf8073245473d2a1_XM_CSV | 23.8 | 60.2 | 44.1 | 23.8 | H1 15/61, H4 24/60 | 4% (25 cặp) | 0.38 | 40.9%/năm, DD 48.0%, OOS 47.3, CN 1.0 | 118 | 16 |

## 3. Ghép cùng cặp (MÔ PHỎNG)

| Gốc | B | Phong cách B | Kiểu | %/năm | DD % | OOS %/năm | Lệnh | Gốc %/năm / DD % |
|---|---|---|---|---|---|---|---|---|
| od_skst4ac0c7fd10781af4_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 69.3 | 62.4 | 55.1 | 42 | 344.1 / 55.8 |
| od_skst4ac0c7fd10781af4_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | -100.0 | 109.3 | — | 3 | 344.1 / 55.8 |
| od_skst4ac0c7fd10781af4_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | -100.0 | 104.7 | — | 116 | 344.1 / 55.8 |
| od_skst4ac0c7fd10781af4_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 4.7 | 8.2 | 0.0 | 2 | 344.1 / 55.8 |
| od_skst4ac0c7fd10781af4_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | -100.0 | 104.4 | — | 123 | 344.1 / 55.8 |
| od_skst4ac0c7fd10781af4_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 126.5 | 80.4 | -26.9 | 266 | 344.1 / 55.8 |
| od_skst4ac0c7fd10781af4_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 69.3 | 62.4 | 55.1 | 42 | 344.1 / 55.8 |
| od_skst4ac0c7fd10781af4_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | -100.0 | 109.3 | — | 3 | 344.1 / 55.8 |
| od_skst4ac0c7fd10781af4_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | -100.0 | 104.7 | — | 116 | 344.1 / 55.8 |
| od_skea44640140cc_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 87.8 | 74.7 | 128.0 | 300 | 139.2 / 46.3 |
| od_skea44640140cc_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | 125.3 | 84.8 | 2.9 | 1599 | 139.2 / 46.3 |
| od_skea44640140cc_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 117.2 | 91.4 | 3.7 | 1160 | 139.2 / 46.3 |
| od_skea44640140cc_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 139.2 | 46.3 | 59.5 | 625 | 139.2 / 46.3 |
| od_skea44640140cc_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | 202.3 | 76.2 | 63.9 | 1250 | 139.2 / 46.3 |
| od_skea44640140cc_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | 139.2 | 46.3 | 59.5 | 625 | 139.2 / 46.3 |
| od_skea44640140cc_XM_CSV | mql5_e3c3e4f028dbab72 | trend | xac_nhan | 66.8 | 96.5 | 19.8 | 196 | 139.2 / 46.3 |
| od_skea44640140cc_XM_CSV | mql5_e3c3e4f028dbab72 | trend | them_lenh | 144.3 | 49.2 | 70.1 | 1073 | 139.2 / 46.3 |
| od_skea44640140cc_XM_CSV | mql5_e3c3e4f028dbab72 | trend | nguoc | -100.0 | 101.3 | — | 33 | 139.2 / 46.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | sk_ea_fdbf5bcad6 | basket,breakout,mean_reversion,trend | xac_nhan | 14.9 | 10.9 | 16.8 | 51 | 31.0 / 18.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | sk_ea_fdbf5bcad6 | basket,breakout,mean_reversion,trend | them_lenh | 36.3 | 33.2 | 52.8 | 479 | 31.0 / 18.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | sk_ea_fdbf5bcad6 | basket,breakout,mean_reversion,trend | nguoc | 16.6 | 66.8 | 48.0 | 330 | 31.0 / 18.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 14.3 | 22.1 | 22.2 | 50 | 31.0 / 18.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | 54.8 | 38.1 | 3.9 | 395 | 31.0 / 18.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 56.7 | 34.6 | 29.0 | 323 | 31.0 / 18.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 1.4 | 1.5 | 1.1 | 4 | 31.0 / 18.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | 10.3 | 71.8 | 28.7 | 308 | 31.0 / 18.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 5.9 | 89.6 | 88.8 | 250 | 31.0 / 18.3 |
| od_skstaca366b679c75482_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 5.7 | 17.8 | 8.6 | 8 | 23.9 / 18.4 |
| od_skstaca366b679c75482_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | -90.7 | 99.9 | 0.0 | 8 | 23.9 / 18.4 |
| od_skstaca366b679c75482_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 23.9 | 26.9 | -8.1 | 77 | 23.9 / 18.4 |
| od_skstaca366b679c75482_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 0.0 | 0.0 | 0.0 | 0 | 23.9 / 18.4 |
| od_skstaca366b679c75482_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | 0.9 | 59.0 | 5.5 | 98 | 23.9 / 18.4 |
| od_skstaca366b679c75482_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 24.7 | 33.2 | 19.0 | 72 | 23.9 / 18.4 |
| od_skstaca366b679c75482_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 5.7 | 17.8 | 8.6 | 8 | 23.9 / 18.4 |
| od_skstaca366b679c75482_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | -90.7 | 99.9 | 0.0 | 8 | 23.9 / 18.4 |
| od_skstaca366b679c75482_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | 23.9 | 26.9 | -8.1 | 77 | 23.9 / 18.4 |
| od_mql5f3313c2c79f00c10_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 24.7 | 84.3 | -10.7 | 105 | 59.4 / 56.3 |
| od_mql5f3313c2c79f00c10_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | -100.0 | 103.7 | — | 43 | 59.4 / 56.3 |
| od_mql5f3313c2c79f00c10_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | -100.0 | 102.0 | — | 60 | 59.4 / 56.3 |
| od_mql5f3313c2c79f00c10_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 24.7 | 84.3 | -10.7 | 105 | 59.4 / 56.3 |
| od_mql5f3313c2c79f00c10_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | -100.0 | 103.7 | — | 43 | 59.4 / 56.3 |
| od_mql5f3313c2c79f00c10_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | -100.0 | 102.0 | — | 60 | 59.4 / 56.3 |
| od_mql5f3313c2c79f00c10_XM_CSV | mql5_e3c3e4f028dbab72 | trend | xac_nhan | 0.0 | 0.0 | 0.0 | 0 | 59.4 / 56.3 |
| od_mql5f3313c2c79f00c10_XM_CSV | mql5_e3c3e4f028dbab72 | trend | them_lenh | 81.8 | 32.6 | 61.3 | 277 | 59.4 / 56.3 |
| od_mql5f3313c2c79f00c10_XM_CSV | mql5_e3c3e4f028dbab72 | trend | nguoc | 77.3 | 35.4 | 63.1 | 246 | 59.4 / 56.3 |
| od_skstadd3a54f8edcbce2_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 16.0 | 59.9 | 23.1 | 8 | 73.9 / 63.6 |
| od_skstadd3a54f8edcbce2_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | -100.0 | 105.4 | — | 12 | 73.9 / 63.6 |
| od_skstadd3a54f8edcbce2_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 75.8 | 87.1 | -37.1 | 146 | 73.9 / 63.6 |
| od_skstadd3a54f8edcbce2_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 0.0 | 0.0 | 0.0 | 0 | 73.9 / 63.6 |
| od_skstadd3a54f8edcbce2_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | -100.0 | 100.1 | — | 79 | 73.9 / 63.6 |
| od_skstadd3a54f8edcbce2_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 70.8 | 60.2 | -17.8 | 126 | 73.9 / 63.6 |
| od_skstadd3a54f8edcbce2_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 16.0 | 59.9 | 23.1 | 8 | 73.9 / 63.6 |
| od_skstadd3a54f8edcbce2_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | -100.0 | 105.4 | — | 12 | 73.9 / 63.6 |
| od_skstadd3a54f8edcbce2_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | 75.8 | 87.1 | -37.1 | 146 | 73.9 / 63.6 |
| od_skeafdbf5bcad6_XM_CSV | mql5_e3c3e4f028dbab72 | trend | xac_nhan | -15.9 | 61.6 | -6.9 | 16 | 23.0 / 18.7 |
| od_skeafdbf5bcad6_XM_CSV | mql5_e3c3e4f028dbab72 | trend | them_lenh | 5.1 | 47.2 | -25.7 | 285 | 23.0 / 18.7 |
| od_skeafdbf5bcad6_XM_CSV | mql5_e3c3e4f028dbab72 | trend | nguoc | 28.2 | 40.4 | -8.1 | 254 | 23.0 / 18.7 |
| od_skeafdbf5bcad6_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 30.7 | 21.6 | -3.2 | 142 | 23.0 / 18.7 |
| od_skeafdbf5bcad6_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | 27.4 | 43.7 | -17.7 | 290 | 23.0 / 18.7 |
| od_skeafdbf5bcad6_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 31.5 | 39.9 | -10.8 | 274 | 23.0 / 18.7 |
| od_skeafdbf5bcad6_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 11.1 | 30.3 | 9.9 | 40 | 23.0 / 18.7 |
| od_skeafdbf5bcad6_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | 5.9 | 52.0 | -30.3 | 329 | 23.0 / 18.7 |
| od_skeafdbf5bcad6_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 5.9 | 44.2 | -22.7 | 293 | 23.0 / 18.7 |
| od_mql5a790e25e547f0b57_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 16.3 | 17.2 | 20.5 | 28 | 17.3 / 19.6 |
| od_mql5a790e25e547f0b57_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | 38.3 | 36.7 | 57.0 | 93 | 17.3 / 19.6 |
| od_mql5a790e25e547f0b57_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 17.3 | 19.6 | 20.0 | 30 | 17.3 / 19.6 |
| od_mql5a790e25e547f0b57_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 6.3 | 12.6 | 4.3 | 10 | 17.3 / 19.6 |
| od_mql5a790e25e547f0b57_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | -49.0 | 91.0 | -79.0 | 74 | 17.3 / 19.6 |
| od_mql5a790e25e547f0b57_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | -100.0 | 100.4 | — | 26 | 17.3 / 19.6 |
| od_mql5a790e25e547f0b57_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 16.3 | 17.2 | 20.5 | 28 | 17.3 / 19.6 |
| od_mql5a790e25e547f0b57_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | 38.3 | 36.7 | 57.0 | 93 | 17.3 / 19.6 |
| od_mql5a790e25e547f0b57_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | 17.3 | 19.6 | 20.0 | 30 | 17.3 / 19.6 |
| od_skstc21c2acd239f3c87_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 9.0 | 46.1 | 16.4 | 11 | 41.3 / 52.9 |
| od_skstc21c2acd239f3c87_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | -100.0 | 104.6 | — | 36 | 41.3 / 52.9 |
| od_skstc21c2acd239f3c87_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 52.4 | 58.7 | -48.5 | 266 | 41.3 / 52.9 |
| od_skstc21c2acd239f3c87_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 0.0 | 0.0 | 0.0 | 0 | 41.3 / 52.9 |
| od_skstc21c2acd239f3c87_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | -100.0 | 102.6 | — | 276 | 41.3 / 52.9 |
| od_skstc21c2acd239f3c87_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 16.4 | 80.6 | -64.6 | 191 | 41.3 / 52.9 |
| od_skstc21c2acd239f3c87_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 9.0 | 46.1 | 16.4 | 11 | 41.3 / 52.9 |
| od_skstc21c2acd239f3c87_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | -100.0 | 104.6 | — | 36 | 41.3 / 52.9 |
| od_skstc21c2acd239f3c87_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | 52.4 | 58.7 | -48.5 | 266 | 41.3 / 52.9 |
| od_skea8897567020_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 46.1 | 48.6 | 20.7 | 170 | 46.1 / 48.6 |
| od_skea8897567020_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | 76.0 | 61.9 | 36.7 | 316 | 46.1 / 48.6 |
| od_skea8897567020_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 46.1 | 48.6 | 20.7 | 170 | 46.1 / 48.6 |
| od_skea8897567020_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 41.8 | 37.9 | 26.4 | 136 | 46.1 / 48.6 |
| od_skea8897567020_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | -42.3 | 91.8 | -79.2 | 497 | 46.1 / 48.6 |
| od_skea8897567020_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | -100.0 | 106.6 | — | 133 | 46.1 / 48.6 |
| od_skea8897567020_XM_CSV | mql5_e3c3e4f028dbab72 | trend | xac_nhan | 30.8 | 34.6 | 20.5 | 97 | 46.1 / 48.6 |
| od_skea8897567020_XM_CSV | mql5_e3c3e4f028dbab72 | trend | them_lenh | -100.0 | 102.3 | — | 201 | 46.1 / 48.6 |
| od_skea8897567020_XM_CSV | mql5_e3c3e4f028dbab72 | trend | nguoc | -100.0 | 105.0 | — | 135 | 46.1 / 48.6 |
| od_mql5b39a9f3ba216fb47_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 18.6 | 46.5 | 16.1 | 393 | 18.6 / 46.5 |
| od_mql5b39a9f3ba216fb47_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | 27.5 | 76.9 | 24.2 | 1210 | 18.6 / 46.5 |
| od_mql5b39a9f3ba216fb47_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 18.6 | 46.5 | 16.1 | 393 | 18.6 / 46.5 |
| od_mql5b39a9f3ba216fb47_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 0.2 | 0.6 | 0.3 | 6 | 18.6 / 46.5 |
| od_mql5b39a9f3ba216fb47_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | 15.0 | 49.6 | 33.1 | 1044 | 18.6 / 46.5 |
| od_mql5b39a9f3ba216fb47_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 14.7 | 59.2 | 27.9 | 738 | 18.6 / 46.5 |
| od_mql5b39a9f3ba216fb47_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 18.6 | 46.5 | 16.1 | 393 | 18.6 / 46.5 |
| od_mql5b39a9f3ba216fb47_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | 27.5 | 76.9 | 24.2 | 1210 | 18.6 / 46.5 |
| od_mql5b39a9f3ba216fb47_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | 18.6 | 46.5 | 16.1 | 393 | 18.6 / 46.5 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 35.1 | 56.0 | 16.5 | 71 | 30.8 / 50.0 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | 35.9 | 85.2 | 6.7 | 297 | 30.8 / 50.0 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | -100.0 | 100.4 | — | 87 | 30.8 / 50.0 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 17.6 | 36.9 | -3.9 | 68 | 30.8 / 50.0 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | -100.0 | 108.5 | — | 30 | 30.8 / 50.0 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | -100.0 | 108.5 | — | 30 | 30.8 / 50.0 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 35.1 | 56.0 | 16.5 | 71 | 30.8 / 50.0 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | 35.9 | 85.2 | 6.7 | 297 | 30.8 / 50.0 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | -100.0 | 100.4 | — | 87 | 30.8 / 50.0 |
| od_mql5e31426a40a5897fc_XM_CSV | mql5_ad7d22b5b165a673 | mean_reversion | xac_nhan | 0.0 | 0.0 | 0.0 | 0 | 26.5 / 59.0 |
| od_mql5e31426a40a5897fc_XM_CSV | mql5_ad7d22b5b165a673 | mean_reversion | them_lenh | 35.4 | 66.8 | 48.8 | 47 | 26.5 / 59.0 |
| od_mql5e31426a40a5897fc_XM_CSV | mql5_ad7d22b5b165a673 | mean_reversion | nguoc | 30.2 | 81.1 | 58.9 | 37 | 26.5 / 59.0 |
| od_mql5e31426a40a5897fc_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 16.0 | 10.0 | 21.9 | 8 | 26.5 / 59.0 |
| od_mql5e31426a40a5897fc_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | 23.3 | 65.5 | 13.3 | 33 | 26.5 / 59.0 |
| od_mql5e31426a40a5897fc_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 37.5 | 50.9 | 38.1 | 34 | 26.5 / 59.0 |
| od_mql5e31426a40a5897fc_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 6.7 | 7.5 | 7.1 | 3 | 26.5 / 59.0 |
| od_mql5e31426a40a5897fc_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | 29.6 | 92.3 | 26.6 | 49 | 26.5 / 59.0 |
| od_mql5e31426a40a5897fc_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 14.4 | 75.8 | 64.4 | 34 | 26.5 / 59.0 |
| od_mql525573694a7f03d3a_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 17.2 | 33.6 | 46.3 | 233 | 18.8 / 31.8 |
| od_mql525573694a7f03d3a_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | 18.7 | 63.1 | 81.5 | 746 | 18.8 / 31.8 |
| od_mql525573694a7f03d3a_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 17.6 | 33.9 | 39.1 | 630 | 18.8 / 31.8 |
| od_mql525573694a7f03d3a_XM_CSV | nhap_cf8073245473d2a1 | mean_reversion | xac_nhan | 12.7 | 37.8 | 46.8 | 199 | 18.8 / 31.8 |
| od_mql525573694a7f03d3a_XM_CSV | nhap_cf8073245473d2a1 | mean_reversion | them_lenh | 17.3 | 71.1 | 139.1 | 786 | 18.8 / 31.8 |
| od_mql525573694a7f03d3a_XM_CSV | nhap_cf8073245473d2a1 | mean_reversion | nguoc | 15.1 | 77.8 | 142.7 | 767 | 18.8 / 31.8 |
| od_mql525573694a7f03d3a_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 6.1 | 19.8 | 0.6 | 155 | 18.8 / 31.8 |
| od_mql525573694a7f03d3a_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | 12.0 | 50.0 | 47.5 | 546 | 18.8 / 31.8 |
| od_mql525573694a7f03d3a_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 12.0 | 49.8 | 48.5 | 545 | 18.8 / 31.8 |
| od_mql5b5a04d7c15935f8b_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 14.5 | 20.6 | 10.8 | 76 | 16.8 / 24.6 |
| od_mql5b5a04d7c15935f8b_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | 18.4 | 40.3 | 4.3 | 495 | 16.8 / 24.6 |
| od_mql5b5a04d7c15935f8b_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | 21.8 | 30.7 | 15.2 | 456 | 16.8 / 24.6 |
| od_mql5b5a04d7c15935f8b_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 14.5 | 20.6 | 10.8 | 76 | 16.8 / 24.6 |
| od_mql5b5a04d7c15935f8b_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | 18.4 | 40.3 | 4.3 | 495 | 16.8 / 24.6 |
| od_mql5b5a04d7c15935f8b_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 21.8 | 30.7 | 15.2 | 456 | 16.8 / 24.6 |
| od_mql5b5a04d7c15935f8b_XM_CSV | mql5_e3c3e4f028dbab72 | trend | xac_nhan | 0.0 | 0.0 | 0.0 | 0 | 16.8 / 24.6 |
| od_mql5b5a04d7c15935f8b_XM_CSV | mql5_e3c3e4f028dbab72 | trend | them_lenh | 17.6 | 90.2 | 3.8 | 484 | 16.8 / 24.6 |
| od_mql5b5a04d7c15935f8b_XM_CSV | mql5_e3c3e4f028dbab72 | trend | nguoc | 18.4 | 36.5 | 5.5 | 359 | 16.8 / 24.6 |
| od_mql5ad7d22b5b165a673_XM_CSV | mql5_e31426a40a5897fc | trend | xac_nhan | 0.0 | 0.0 | 0.0 | 0 | 18.6 / 61.3 |
| od_mql5ad7d22b5b165a673_XM_CSV | mql5_e31426a40a5897fc | trend | them_lenh | 28.8 | 92.4 | 14.3 | 151 | 18.6 / 61.3 |
| od_mql5ad7d22b5b165a673_XM_CSV | mql5_e31426a40a5897fc | trend | nguoc | 28.7 | 92.5 | 14.3 | 150 | 18.6 / 61.3 |
| od_mql5ad7d22b5b165a673_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 3.8 | 30.8 | -23.7 | 51 | 18.6 / 61.3 |
| od_mql5ad7d22b5b165a673_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | 18.7 | 85.8 | -28.9 | 267 | 18.6 / 61.3 |
| od_mql5ad7d22b5b165a673_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 18.0 | 89.2 | -29.3 | 254 | 18.6 / 61.3 |
| od_mql5ad7d22b5b165a673_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 3.8 | 30.8 | -23.7 | 51 | 18.6 / 61.3 |
| od_mql5ad7d22b5b165a673_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | 18.7 | 85.8 | -28.9 | 267 | 18.6 / 61.3 |
| od_mql5ad7d22b5b165a673_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | 18.0 | 89.2 | -29.3 | 254 | 18.6 / 61.3 |
| od_tohop09a3b2ddc3e78dc8_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 0.0 | 0.0 | 0.0 | 0 | 20.3 / 21.4 |
| od_tohop09a3b2ddc3e78dc8_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | -100.0 | 101.8 | — | 71 | 20.3 / 21.4 |
| od_tohop09a3b2ddc3e78dc8_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | -100.0 | 101.8 | — | 71 | 20.3 / 21.4 |
| od_tohop09a3b2ddc3e78dc8_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 1.5 | 8.5 | 3.8 | 4 | 20.3 / 21.4 |
| od_tohop09a3b2ddc3e78dc8_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | -100.0 | 101.4 | — | 124 | 20.3 / 21.4 |
| od_tohop09a3b2ddc3e78dc8_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 18.0 | 72.5 | -17.7 | 156 | 20.3 / 21.4 |
| od_tohop09a3b2ddc3e78dc8_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 0.0 | 0.0 | 0.0 | 0 | 20.3 / 21.4 |
| od_tohop09a3b2ddc3e78dc8_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | -100.0 | 101.8 | — | 71 | 20.3 / 21.4 |
| od_tohop09a3b2ddc3e78dc8_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | -100.0 | 101.8 | — | 71 | 20.3 / 21.4 |
| od_mql5d8f573b8c2314bbf_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | -21.9 | 75.3 | -80.8 | 55 | 27.4 / 34.8 |
| od_mql5d8f573b8c2314bbf_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | -36.5 | 90.8 | -92.9 | 165 | 27.4 / 34.8 |
| od_mql5d8f573b8c2314bbf_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | -1.2 | 71.0 | -76.8 | 176 | 27.4 / 34.8 |
| od_mql5d8f573b8c2314bbf_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | -85.9 | 99.6 | -99.9 | 7 | 27.4 / 34.8 |
| od_mql5d8f573b8c2314bbf_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | 29.0 | 46.6 | -44.1 | 237 | 27.4 / 34.8 |
| od_mql5d8f573b8c2314bbf_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 17.2 | 47.9 | -51.7 | 203 | 27.4 / 34.8 |
| od_mql5d8f573b8c2314bbf_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | -21.9 | 75.3 | -80.8 | 55 | 27.4 / 34.8 |
| od_mql5d8f573b8c2314bbf_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | -36.5 | 90.8 | -92.9 | 165 | 27.4 / 34.8 |
| od_mql5d8f573b8c2314bbf_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | -1.2 | 71.0 | -76.8 | 176 | 27.4 / 34.8 |
| od_mql5e52afb999eca4bd1_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 23.2 | 42.3 | 20.4 | 88 | 11.0 / 26.1 |
| od_mql5e52afb999eca4bd1_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | 19.4 | 47.2 | 42.0 | 392 | 11.0 / 26.1 |
| od_mql5e52afb999eca4bd1_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 16.7 | 50.8 | 40.0 | 212 | 11.0 / 26.1 |
| od_mql5e52afb999eca4bd1_XM_CSV | nhap_cf8073245473d2a1 | mean_reversion | xac_nhan | 11.0 | 26.1 | 10.8 | 108 | 11.0 / 26.1 |
| od_mql5e52afb999eca4bd1_XM_CSV | nhap_cf8073245473d2a1 | mean_reversion | them_lenh | 23.5 | 41.4 | 17.4 | 255 | 11.0 / 26.1 |
| od_mql5e52afb999eca4bd1_XM_CSV | nhap_cf8073245473d2a1 | mean_reversion | nguoc | 16.0 | 52.5 | 43.0 | 230 | 11.0 / 26.1 |
| od_mql5e52afb999eca4bd1_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | -11.1 | 48.9 | -37.3 | 52 | 11.0 / 26.1 |
| od_mql5e52afb999eca4bd1_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | -3.4 | 69.5 | -24.6 | 154 | 11.0 / 26.1 |
| od_mql5e52afb999eca4bd1_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 2.7 | 51.8 | -12.5 | 157 | 11.0 / 26.1 |
| od_nhapcf8073245473d2a1_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | -11.8 | 97.0 | -41.2 | 99 | 23.8 / 60.2 |
| od_nhapcf8073245473d2a1_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | -100.0 | 101.9 | — | 95 | 23.8 / 60.2 |
| od_nhapcf8073245473d2a1_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 32.0 | 67.1 | 65.0 | 335 | 23.8 / 60.2 |
| od_nhapcf8073245473d2a1_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | -11.8 | 97.0 | -41.2 | 99 | 23.8 / 60.2 |
| od_nhapcf8073245473d2a1_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | -100.0 | 101.9 | — | 95 | 23.8 / 60.2 |
| od_nhapcf8073245473d2a1_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | 32.0 | 67.1 | 65.0 | 335 | 23.8 / 60.2 |
| od_nhapcf8073245473d2a1_XM_CSV | mql5_e3c3e4f028dbab72 | trend | xac_nhan | 21.2 | 18.2 | 8.3 | 81 | 23.8 / 60.2 |
| od_nhapcf8073245473d2a1_XM_CSV | mql5_e3c3e4f028dbab72 | trend | them_lenh | 30.7 | 56.0 | 44.3 | 259 | 23.8 / 60.2 |
| od_nhapcf8073245473d2a1_XM_CSV | mql5_e3c3e4f028dbab72 | trend | nguoc | 23.8 | 60.6 | 44.1 | 201 | 23.8 / 60.2 |

## 4. Danh mục từ lệnh MT5 thật, DD trên equity tái dựng theo giờ

| # | Hệ | Lãi kép %/năm | DD equity % | Tương quan ngày max | Kỳ |
|---|---|---|---|---|---|
| 1 | od_ghep60ff9350c26c63ee_XM_CSV<br>od_ghepe9b41c33d4deee54_XM_CSV<br>od_skead0a7af9f8b_XM_CSV<br>od_skea8771fe6061_XM_CSV | 76.9 | 14.1 | 0.20 | 2024-01-10 → 2026-09-30 |
| 2 | od_skea44640140cc_XM_CSV<br>od_ghepe9b41c33d4deee54_XM_CSV<br>od_skead0a7af9f8b_XM_CSV<br>od_skea8771fe6061_XM_CSV | 98.5 | 20.7 | 0.17 | 2024-01-10 → 2026-09-30 |
| 3 | od_ghep9c03cef0b89f948f_XM_CSV<br>od_ghepe9b41c33d4deee54_XM_CSV<br>od_skea8771fe6061_XM_CSV<br>od_skea2f7862a741_XM_CSV | 119.7 | 25.6 | 0.19 | 2024-02-19 → 2026-09-30 |
| 4 | od_ghepea3b5db61a7c4792_XM_CSV<br>od_ghepe9b41c33d4deee54_XM_CSV<br>od_skea8771fe6061_XM_CSV<br>od_skea2f7862a741_XM_CSV | 108.5 | 24.6 | 0.20 | 2024-02-19 → 2026-09-30 |
| 5 | od_skead0a7af9f8b_XM_CSV<br>od_ghepea3b5db61a7c4792_XM_CSV<br>od_ghepe9b41c33d4deee54_XM_CSV<br>od_skea8771fe6061_XM_CSV | 101.5 | 24.9 | 0.20 | 2024-01-10 → 2026-09-30 |
| 6 | od_skea0075f624b3_XM_CSV<br>od_ghepea3b5db61a7c4792_XM_CSV<br>od_skea8771fe6061_XM_CSV<br>od_skea2f7862a741_XM_CSV | 98.7 | 25.6 | 0.22 | 2024-02-19 → 2026-09-30 |
| 7 | od_skea0ca971ac32_XM_CSV<br>od_ghepea3b5db61a7c4792_XM_CSV<br>od_skea8771fe6061_XM_CSV<br>od_skea2f7862a741_XM_CSV | 97.4 | 26.9 | 0.25 | 2024-02-19 → 2026-09-30 |

## 5. Hàng chờ MT5 vòng 2

Việc mới lần này: 70; tổng trong `reports/vong2/hang_cho_vong2.jsonl`: 64. Máy nhà chỉ lấy khi đặt `BRAIN_VONG2=1`.

## 6. Vòng 2 SÂU — cả 78 hệ ĐẠT, chỉ dùng lệnh MT5 thật (`python -m nhan.vong2_sau`)

Lúc chạy: 2026-10-21 09:11 (giờ box, UTC+7). Đo được 78/78 hệ (lỗi: 0). Cột TF trống trong `UNG_VIEN.md` được điền từ dòng *Period* của báo cáo MT5 `.htm`. **Stress phí, ghép, danh mục, Monte Carlo = MÔ PHỎNG** (cộng equity tái dựng từ lệnh MT5 thật, vốn 1.000 USD/hệ). Hoa hồng thật XM micro: **CHƯA ĐO ĐƯỢC** (báo cáo = 0) → thử 0 / 7 / 14 USD/100k.

Tóm tắt: 75/78 hệ vẫn ≥ 10%/năm và DD equity ≤ 80% sau stress spread ×1,5 + hoa hồng 7 USD; 58/78 sau spread ×3 + 14 USD. 43 hệ “bền” (qua stress, ≥ 2 năm, ≥ 30 lệnh, không đoạn WF âm, MC DD p95 ≤ 80%).

### 6.1 Stress phí + cảnh báo quá khớp (xếp theo lãi sau stress ×1,5 / DD)

| id | Symbol | TF | Năm | Lệnh | %/năm MT5 | DD equity % | ×1,5+7 | ×2+7 | ×3+14 | WF 3 đoạn | MC DD p95 | Bền | Cảnh báo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| od_skst4ac0c7fd10781af4_XM_CSV | EURUSDmicro | H1 | 1.34 | 73 | 331.4 | 45.5 | 310.9 | 300.0 | 267.7 | 1171 / 365 / 62 | 51.8 |  | lịch sử ngắn 1.3 năm; 1 đoạn WF gánh 73% lãi; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_ghepea3b5db61a7c4792_XM_CSV | GBPCADmicro | H4* | 2.76 | 279 | 147.3 | 44.4 | 141.9 | 138.3 | 128.7 | 441 / 80 / 59 | 82.6 |  | 1 đoạn WF gánh 76% lãi; MC DD p95 83% > 80%; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea44640140cc_XM_CSV | GBPCADmicro | H1 | 2.76 | 616 | 138.8 | 43.6 | 130.9 | 125.5 | 110.8 | 396 / 86 / 51 | 66.4 | ✔ | 1 đoạn WF gánh 74% lãi; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_ghepe9b41c33d4deee54_XM_CSV | GBPNZDmicro | H4* | 2.76 | 135 | 122.9 | 41.5 | 119.5 | 117.2 | 111.3 | 343 / 68 / 50 | 71.8 | ✔ | 1 đoạn WF gánh 74% lãi; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_ghep9c03cef0b89f948f_XM_CSV | GBPCADmicro | H1* | 2.76 | 129 | 173.5 | 59.1 | 167.2 | 162.9 | 151.6 | 487 / 166 / 41 | 75.7 | ✔ | 1 đoạn WF gánh 70% lãi; 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_ghep60ff9350c26c63ee_XM_CSV | GBPCADmicro | H1* | 2.76 | 322 | 67.0 | 22.8 | 62.4 | 59.4 | 51.0 | 104 / 71 / 39 | 47.4 | ✔ | 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skead0a7af9f8b_XM_CSV | AUDJPYmicro | H4* | 2.74 | 158 | 17.9 | 7.2 | 16.7 | 15.8 | 13.6 | 22 / 21 / 11 | 7.9 | ✔ | chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea0ca971ac32_XM_CSV | GBPNZDmicro | H4 | 2.76 | 27 | 86.0 | 45.7 | 83.3 | 81.4 | 76.6 | 210 / 70 / 22 | 81.8 |  | ít lệnh 27; 1 đoạn WF gánh 70% lãi; MC DD p95 82% > 80%; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea0075f624b3_XM_CSV | GBPNZDmicro | H1 | 2.74 | 139 | 91.4 | 50.1 | 86.6 | 83.2 | 74.4 | 175 / 74 / 48 | 84.4 |  | MC DD p95 84% > 80%; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea8771fe6061_XM_CSV | EURCHFmicro | H4* | 2.72 | 30 | 67.2 | 37.8 | 64.0 | 61.9 | 56.3 | 114 / 74 / 26 | 42.8 | ✔ | chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_ghepc9f8a1b857b9a416_XM_CSV | GBPCADmicro | H4* | 2.76 | 122 | 89.6 | 50.8 | 85.9 | 83.4 | 76.9 | 152 / 86 / 51 | 84.5 |  | MC DD p95 85% > 80%; 3 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_tohop16b0d75bb149f634_XM_CSV | GBPCADmicro | H1 | 2.76 | 127 | 92.3 | 55.2 | 88.4 | 85.8 | 79.0 | 120 / 79 / 78 | 77.7 | ✔ | chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea2f7862a741_XM_CSV | AUDUSDmicro | H4* | 2.61 | 71 | 28.6 | 16.2 | 25.6 | 23.4 | 17.9 | 33 / 28 / 23 | 18.9 | ✔ | chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skeab536f57733_XM_CSV | EURUSDmicro | H4* | 2.76 | 249 | 64.5 | 39.4 | 61.8 | 60.4 | 56.1 | 84 / 97 / 16 | 57.1 | ✔ | 3 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea0b8298aa53_XM_CSV | GOLDmicro | H1 | 2.76 | 16 | 68.1 | 43.3 | 67.0 | 66.5 | 65.0 | 97 / 8 / 125 | 42.5 |  | ít lệnh 16; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_mql5e3c3e4f028dbab72_XM_CSV | EURCADmicro | H4 | 2.76 | 120 | 29.1 | 18.0 | 27.6 | 26.8 | 24.4 | 47 / 19 / 23 | 25.2 | ✔ | 3 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_ghep6f5c193256881f31_XM_CSV | GBPCADmicro | H1* | 2.76 | 324 | 86.3 | 50.2 | 75.1 | 67.2 | 43.0 | 108 / 107 / 49 | 84.8 |  | MC DD p95 85% > 80%; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea0c762cdb38_XM_CSV | CHFJPYmicro | H4 | 2.55 | 39 | 27.6 | 20.2 | 25.8 | 24.9 | 22.2 | 29 / 37 / 17 | 27.9 | ✔ | chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skstaca366b679c75482_XM_CSV | EURUSDmicro | H1 | 1.34 | 15 | 24.4 | 18.3 | 22.6 | 21.7 | 18.9 | 15 / 27 / 33 | 21.0 |  | lịch sử ngắn 1.3 năm; ít lệnh 15; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skeaff87f96be7_XM_CSV | GBPCADmicro | H1 | 2.75 | 211 | 53.4 | 40.9 | 50.5 | 48.6 | 43.5 | 62 / 52 / 46 | 58.3 | ✔ | 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_tohop9acc6e0d2f784cb9_XM_CSV | GBPCADmicro | H1 | 2.72 | 59 | 12.9 | 10.4 | 12.4 | 12.1 | 11.4 | 17 / 8 / 15 | 19.1 | ✔ | chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_mql5f3313c2c79f00c10_XM_CSV | EURGBPmicro | H4 | 2.74 | 178 | 66.2 | 52.5 | 60.5 | 56.7 | 46.1 | 170 / -28 / 120 | 78.5 |  | có đoạn WF âm (-28%/năm); 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea5049c79288_XM_CSV | GBPCADmicro | H4 | 2.71 | 83 | 34.8 | 30.0 | 33.2 | 32.1 | 29.2 | 63 / 11 / 35 | 53.3 | ✔ | 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea31214192bc_XM_CSV | GBPNZDmicro | H4* | 2.64 | 36 | 39.6 | 29.6 | 32.7 | 27.6 | 13.4 | 54 / 40 / 26 | 44.7 | ✔ | chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea89d6f8661b_XM_CSV | AUDUSDmicro | H1* | 2.68 | 75 | 37.1 | 32.6 | 34.4 | 32.5 | 27.6 | 61 / 4 / 54 | 48.3 | ✔ | 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skstadd3a54f8edcbce2_XM_CSV | EURUSDmicro | H1 | 1.34 | 15 | 70.5 | 62.8 | 65.6 | 63.0 | 55.3 | 50 / 119 / 47 | 65.5 |  | lịch sử ngắn 1.3 năm; ít lệnh 15; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skeadc40280363_XM_CSV | CADJPYmicro | H1* | 2.76 | 160 | 39.6 | 37.2 | 37.7 | 36.4 | 33.0 | 66 / 57 / 4 | 47.6 | ✔ | 4 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_ghep0bf2c31fbfc9dea0_XM_CSV | GBPCADmicro | H4* | 2.76 | 78 | 62.2 | 52.2 | 52.4 | 45.3 | 23.8 | 122 / 49 / 31 | 92.3 |  | 1 đoạn WF gánh 61% lãi; MC DD p95 92% > 80%; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_2600ea39abbd7b0f_XM_CSV | GBPNZDmicro | H1* | 2.76 | 131 | 27.8 | 25.3 | 25.1 | 23.2 | 18.3 | 26 / 40 / 18 | 53.0 | ✔ | 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea5fdf89aa94_XM_CSV | USDJPYmicro | H4* | 1.85 | 6 | 47.8 | 47.8 | 46.8 | 46.4 | 44.9 | 52 / 113 / -0 | 54.1 |  | lịch sử ngắn 1.9 năm; ít lệnh 6; 1 đoạn WF gánh 68% lãi; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skeadd170ac7bf_XM_CSV | USDCADmicro | H1* | 2.76 | 109 | 54.1 | 53.8 | 52.4 | 51.4 | 48.6 | 54 / 25 / 90 | 81.0 |  | MC DD p95 81% > 80%; 7 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skeaa7cd39087e_XM_CSV | GOLDmicro | H1 | 2.76 | 351 | 60.0 | 55.6 | 53.5 | 51.0 | 40.8 | 71 / 232 / -29 | 85.4 |  | có đoạn WF âm (-29%/năm); 1 đoạn WF gánh 77% lãi; MC DD p95 85% > 80%; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea61c21a2049_XM_CSV | CADJPYmicro | H4* | 2.74 | 219 | 29.2 | 27.1 | 25.8 | 23.4 | 16.9 | 35 / 37 / 17 | 36.6 | ✔ | 3 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea0806a3a5e5_XM_CSV | AUDNZDmicro | H1 | 2.76 | 29 | 24.4 | 24.6 | 23.3 | 22.5 | 20.6 | 19 / 14 / 41 | 44.0 |  | ít lệnh 29; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skeafdbf5bcad6_XM_CSV | EURCADmicro | H1 | 2.76 | 190 | 26.5 | 18.9 | 17.8 | 12.4 | -5.7 | 45 / 64 / -12 | 50.5 |  | có đoạn WF âm (-12%/năm); 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea135e93ee32_XM_CSV | EURUSDmicro | H1 | 2.76 | 57 | 17.4 | 18.3 | 16.6 | 16.2 | 14.9 | 11 / 26 / 15 | 27.9 | ✔ | chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_mql5a790e25e547f0b57_XM_CSV | AUDNZDmicro | H4 | 2.74 | 31 | 17.5 | 19.6 | 16.2 | 15.3 | 12.9 | 12 / 17 / 22 | 40.7 | ✔ | 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skead5df5bc834_XM_CSV | GOLDmicro | H1* | 2.76 | 268 | 41.0 | 47.2 | 38.9 | 38.0 | 34.8 | 37 / 55 / 32 | 62.3 | ✔ | chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_ghep89811dee41bce6b9_XM_CSV | GOLDmicro | H4* | 2.76 | 92 | 32.4 | 39.0 | 31.4 | 31.0 | 29.7 | 31 / 38 / 29 | 54.8 | ✔ | chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea0cc19095a9_XM_CSV | GBPNZDmicro | H1 | 2.76 | 429 | 24.3 | 27.5 | 20.8 | 18.4 | 11.8 | 23 / 33 / 18 | 39.6 | ✔ | 4 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea8897567020_XM_CSV | GBPNZDmicro | H1 | 2.76 | 154 | 37.3 | 43.6 | 33.0 | 29.8 | 21.3 | 49 / 51 / 17 | 80.7 |  | MC DD p95 81% > 80%; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skstc21c2acd239f3c87_XM_CSV | EURUSDmicro | H1 | 1.34 | 20 | 37.1 | 46.3 | 34.4 | 33.0 | 28.9 | 22 / 70 / 23 | 47.7 |  | lịch sử ngắn 1.3 năm; ít lệnh 20; 1 đoạn WF gánh 61% lãi; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skeaf7a71f885d_XM_CSV | GBPNZDmicro | H1* | 2.76 | 479 | 27.5 | 32.0 | 23.4 | 20.5 | 12.7 | 14 / 41 / 30 | 65.4 | ✔ | 6 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_018dcb1347276c97_XM_CSV | EURNZDmicro | H4 | 2.72 | 76 | 12.1 | 14.8 | 10.8 | 10.0 | 7.8 | 8 / 22 / 7 | 28.8 | ✔ | 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea363d6c8238_XM_CSV | NZDJPYmicro | H4* | 2.68 | 63 | 22.6 | 30.5 | 21.6 | 20.9 | 19.1 | 22 / 31 / 16 | 39.0 | ✔ | chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_b0be91a35f43f34a_XM_CSV | USDCADmicro | H4 | 2.71 | 46 | 44.0 | 57.2 | 39.6 | 37.0 | 29.4 | 82 / 25 / 31 | 88.7 |  | MC DD p95 89% > 80%; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea45b39eb1d5_XM_CSV | AUDJPYmicro | H4 | 2.76 | 202 | 36.1 | 46.0 | 29.5 | 24.6 | 10.7 | 80 / 16 / 21 | 63.4 | ✔ | 1 đoạn WF gánh 69% lãi; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_mql5b39a9f3ba216fb47_XM_CSV | CHFJPYmicro | H1 | 2.76 | 392 | 19.6 | 28.6 | 18.2 | 17.4 | 15.2 | 27 / 22 / 11 | 40.1 | ✔ | 5 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_mql5fd4bc285e11ab5a1_XM_CSV | EURCHFmicro | H4 | 2.76 | 138 | 31.0 | 46.5 | 28.8 | 27.3 | 23.3 | 57 / 42 / -0 | 64.0 |  | có đoạn WF âm (-0%/năm); 5 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea154c9fdee7_XM_CSV | GBPCADmicro | H4* | 2.72 | 182 | 38.3 | 57.0 | 34.6 | 32.2 | 25.5 | 55 / 38 / 24 | 77.7 | ✔ | 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_tohop564be9bb91406c57_XM_CSV | GBPUSDmicro | H1 | 2.72 | 62 | 17.4 | 26.9 | 16.3 | 15.7 | 13.8 | 19 / 17 / 17 | 38.5 | ✔ | chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea0757c93eb3_XM_CSV | EURNZDmicro | H4 | 2.76 | 2 | 10.6 | 17.4 | 10.2 | 10.1 | 9.6 | 35 / 0 / -0 | 18.3 |  | ít lệnh 2; 1 đoạn WF gánh 100% lãi; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea02906b7d6a_XM_CSV | GOLDmicro | H4 | 2.76 | 180 | 39.3 | 65.0 | 35.1 | 33.4 | 27.1 | 92 / 115 / -39 | 89.2 |  | có đoạn WF âm (-39%/năm); MC DD p95 89% > 80%; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_mql525573694a7f03d3a_XM_CSV | EURGBPmicro | H1 | 2.76 | 282 | 19.5 | 33.4 | 17.4 | 16.1 | 12.6 | 20 / -13 / 61 | 49.0 |  | có đoạn WF âm (-13%/năm); 1 đoạn WF gánh 75% lãi; 5 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skeaa3d6925a71_XM_CSV | AUDUSDmicro | H4* | 2.74 | 533 | 32.6 | 52.7 | 26.7 | 22.3 | 10.3 | 121 / 72 / -39 | 81.5 |  | có đoạn WF âm (-39%/năm); 1 đoạn WF gánh 63% lãi; MC DD p95 82% > 80%; 18 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_mql5e31426a40a5897fc_XM_CSV | GBPUSDmicro | H4 | 2.59 | 15 | 28.7 | 55.9 | 28.0 | 27.6 | 26.5 | 40 / 17 / 30 | 63.6 |  | ít lệnh 15; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_mql5b5a04d7c15935f8b_XM_CSV | GBPNZDmicro | H1 | 2.76 | 208 | 18.3 | 29.3 | 14.7 | 11.9 | 4.9 | 6 / 26 / 24 | 55.4 | ✔ | 3 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea3279057100_XM_CSV | EURGBPmicro | H1 | 2.76 | 203 | 44.8 | 63.4 | 31.0 | 20.6 | -18.1 | 147 / -11 / 44 | 93.7 |  | có đoạn WF âm (-11%/năm); 1 đoạn WF gánh 77% lãi; MC DD p95 94% > 80%; 10 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea09c76b6df5_XM_CSV | GBPAUDmicro | H4* | 2.70 | 224 | 20.2 | 34.4 | 16.3 | 13.9 | 7.0 | 30 / 19 / 12 | 72.8 | ✔ | chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_ghepeab4082becc0e276_XM_CSV | EURGBPmicro | H4* | 2.74 | 124 | 27.7 | 56.3 | 26.6 | 25.9 | 24.2 | 29 / -22 / 87 | 70.1 |  | có đoạn WF âm (-22%/năm); 1 đoạn WF gánh 75% lãi; 3 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_mql5ad7d22b5b165a673_XM_CSV | GBPUSDmicro | H4 | 2.76 | 134 | 27.2 | 53.6 | 25.1 | 24.1 | 20.8 | 28 / 37 / 17 | 74.4 | ✔ | 4 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_tohop09a3b2ddc3e78dc8_XM_CSV | EURUSDmicro | H4 | 2.76 | 69 | 15.6 | 31.6 | 14.5 | 13.9 | 12.2 | 22 / 8 / 18 | 44.5 | ✔ | chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_tohopc2d52300cc825dff_XM_CSV | AUDNZDmicro | H1 | 2.74 | 144 | 14.4 | 26.1 | 11.6 | 9.6 | 4.4 | -15 / 32 / 34 | 45.4 |  | có đoạn WF âm (-15%/năm); 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skeae2482b06a4_XM_CSV | GBPUSDmicro | H1* | 2.76 | 1338 | 20.6 | 41.2 | 17.3 | 15.6 | 10.2 | 28 / 25 / 9 | 50.0 | ✔ | 8 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skeaaba30a4e06_XM_CSV | USDJPYmicro | H4 | 2.76 | 164 | 21.9 | 48.1 | 20.2 | 19.3 | 16.6 | 39 / 17 / 12 | 57.4 | ✔ | chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_0557d803384c6211_XM_CSV | GBPUSDmicro | H4* | 2.76 | 182 | 22.2 | 46.1 | 19.2 | 17.6 | 12.7 | 30 / 23 / 14 | 55.5 | ✔ | 3 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_mql5d8f573b8c2314bbf_XM_CSV | EURAUDmicro | H1 | 2.76 | 106 | 24.5 | 47.1 | 19.5 | 16.5 | 7.4 | 82 / 43 / -26 | 58.6 |  | có đoạn WF âm (-26%/năm); 1 đoạn WF gánh 65% lãi; 1 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_mql5e52afb999eca4bd1_XM_CSV | EURGBPmicro | H1 | 2.76 | 110 | 13.7 | 30.0 | 11.7 | 10.4 | 6.9 | 10 / 2 / 33 | 58.9 | ✔ | 1 đoạn WF gánh 74% lãi; 6 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea0ab4d307d3_XM_CSV | EURNZDmicro | H1 | 2.76 | 286 | 17.5 | 38.8 | 14.0 | 11.8 | 5.5 | 23 / 23 / 7 | 62.7 | ✔ | 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skeabc8157a270_XM_CSV | NZDJPYmicro | H4* | 2.74 | 292 | 25.2 | 59.5 | 20.8 | 17.6 | 8.9 | 36 / 10 / 30 | 66.4 | ✔ | chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skeaf3d30ea9da_XM_CSV | GBPAUDmicro | H1* | 2.76 | 956 | 16.9 | 44.4 | 13.9 | 12.2 | 7.0 | 18 / 16 / 19 | 49.6 | ✔ | 4 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skeaf88d932deb_XM_CSV | GOLDmicro | H1* | 2.76 | 605 | 18.9 | 53.2 | 16.5 | 15.5 | 12.0 | 12 / 20 / 25 | 62.2 | ✔ | chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea5539346824_XM_CSV | EURGBPmicro | H1* | 2.72 | 233 | 19.3 | 48.9 | 14.9 | 12.1 | 4.0 | 20 / -15 / 67 | 65.5 |  | có đoạn WF âm (-15%/năm); 1 đoạn WF gánh 77% lãi; 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea0ab6e87da9_XM_CSV | EURGBPmicro | H4* | 2.74 | 245 | 22.8 | 74.4 | 18.1 | 15.0 | 6.2 | 18 / 34 / 18 | 86.5 |  | MC DD p95 86% > 80%; 2 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea66a65a142a_XM_CSV | GBPNZDmicro | H1* | 2.76 | 263 | 22.5 | 50.2 | 12.2 | 4.1 | -23.1 | 47 / 52 / -20 | 90.6 |  | có đoạn WF âm (-20%/năm); MC DD p95 91% > 80%; 3 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_nhapcf8073245473d2a1_XM_CSV | EURGBPmicro | H4 | 2.76 | 188 | 20.8 | 78.2 | 17.8 | 15.8 | 10.3 | 16 / -22 / 114 | 92.1 |  | có đoạn WF âm (-22%/năm); 1 đoạn WF gánh 88% lãi; MC DD p95 92% > 80%; 10 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_3304d2fad28adef6_XM_CSV | USDCADmicro | H4 | 2.59 | 64 | 14.2 | 47.3 | 9.1 | 6.0 | -3.3 | 19 / 26 / -1 | 60.4 |  | có đoạn WF âm (-1%/năm); chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |
| od_skea7eec0ab393_XM_CSV | GBPAUDmicro | H4* | 2.70 | 294 | 13.1 | 59.5 | 8.6 | 5.9 | -2.2 | 56 / 18 / -21 | 81.8 |  | có đoạn WF âm (-21%/năm); 1 đoạn WF gánh 76% lãi; MC DD p95 82% > 80%; 8 lệnh còn mở cuối kỳ; chỉ đo trên 1 cặp (chưa có chuyển cặp MT5) |

\* TF lấy từ báo cáo MT5 `.htm`.

### 6.2 Ghép cùng cặp từ lệnh MT5 thật (2 hệ chạy song song, MÔ PHỎNG)

Đã đo 207 đôi. “Bù trừ” = DD tổng thấp hơn DD lớn hơn của 2 hệ ít nhất 5 điểm.

| Symbol | Hệ | %/năm | DD % | A %/năm / DD | B %/năm / DD | Tương quan ngày | Bù trừ |
|---|---|---|---|---|---|---|---|
| EURUSDmicro | `od_skst4ac0c7fd10781af4_XM_CSV`<br>`od_skstaca366b679c75482_XM_CSV` | 192.5 | 38.9 | 331.4 / 45.5 | 24.4 / 18.3 | 0.41 | có |
| EURUSDmicro | `od_skst4ac0c7fd10781af4_XM_CSV`<br>`od_skstc21c2acd239f3c87_XM_CSV` | 196.7 | 44.5 | 331.4 / 45.5 | 37.1 / 46.3 | 0.70 | không |
| EURUSDmicro | `od_skst4ac0c7fd10781af4_XM_CSV`<br>`od_skstadd3a54f8edcbce2_XM_CSV` | 210.0 | 48.4 | 331.4 / 45.5 | 70.5 / 62.8 | 0.58 | có |
| GBPCADmicro | `od_ghep9c03cef0b89f948f_XM_CSV`<br>`od_ghepea3b5db61a7c4792_XM_CSV` | 160.8 | 45.1 | 173.5 / 59.1 | 147.3 / 44.4 | 0.91 | có |
| GBPCADmicro | `od_ghepea3b5db61a7c4792_XM_CSV`<br>`od_skea44640140cc_XM_CSV` | 142.9 | 42.0 | 147.3 / 44.4 | 138.8 / 43.6 | 0.78 | không |
| GBPNZDmicro | `od_ghepe9b41c33d4deee54_XM_CSV`<br>`od_skea31214192bc_XM_CSV` | 88.8 | 26.7 | 122.9 / 41.5 | 39.6 / 29.6 | 0.16 | có |
| GBPCADmicro | `od_ghep60ff9350c26c63ee_XM_CSV`<br>`od_skea44640140cc_XM_CSV` | 108.4 | 33.1 | 67.0 / 22.8 | 138.8 / 43.6 | 0.87 | có |
| GBPCADmicro | `od_ghep9c03cef0b89f948f_XM_CSV`<br>`od_tohop16b0d75bb149f634_XM_CSV` | 138.9 | 43.7 | 173.5 / 59.1 | 92.3 / 55.2 | 0.65 | có |
| GBPNZDmicro | `od_ghepe9b41c33d4deee54_XM_CSV`<br>`od_skea66a65a142a_XM_CSV` | 84.8 | 26.7 | 122.9 / 41.5 | 22.5 / 50.2 | 0.08 | có |
| GBPNZDmicro | `od_2600ea39abbd7b0f_XM_CSV`<br>`od_ghepe9b41c33d4deee54_XM_CSV` | 86.1 | 27.4 | 27.8 / 25.3 | 122.9 / 41.5 | 0.15 | có |
| GBPNZDmicro | `od_ghepe9b41c33d4deee54_XM_CSV`<br>`od_skeaf7a71f885d_XM_CSV` | 86.0 | 27.6 | 122.9 / 41.5 | 27.5 / 32.0 | -0.01 | có |
| GBPCADmicro | `od_skea44640140cc_XM_CSV`<br>`od_tohop9acc6e0d2f784cb9_XM_CSV` | 93.9 | 30.2 | 138.8 / 43.6 | 12.9 / 10.4 | 0.78 | có |
| GBPCADmicro | `od_skea44640140cc_XM_CSV`<br>`od_tohop16b0d75bb149f634_XM_CSV` | 117.7 | 38.0 | 138.8 / 43.6 | 92.3 / 55.2 | 0.65 | có |
| GBPCADmicro | `od_ghep60ff9350c26c63ee_XM_CSV`<br>`od_ghepea3b5db61a7c4792_XM_CSV` | 113.5 | 37.3 | 67.0 / 22.8 | 147.3 / 44.4 | 0.91 | có |
| GBPCADmicro | `od_ghep9c03cef0b89f948f_XM_CSV`<br>`od_skea44640140cc_XM_CSV` | 157.2 | 52.3 | 173.5 / 59.1 | 138.8 / 43.6 | 0.77 | có |

### 6.3 Danh mục (tất cả hệ qua stress) — tương quan ngày ≤ 0.3, tối đa 2 hệ/cặp, đã đo 13787 nhóm (MÔ PHỎNG)

| Loại | Hệ | Cặp | Vốn USD | %/năm | DD equity % | Sau stress ×1,5+7: %/năm / DD |
|---|---|---|---|---|---|---|
| điểm lãi/DD | `od_ghep60ff9350c26c63ee_XM_CSV`<br>`od_ghepe9b41c33d4deee54_XM_CSV`<br>`od_skea0b8298aa53_XM_CSV`<br>`od_skea8771fe6061_XM_CSV`<br>`od_skeadd170ac7bf_XM_CSV` | EURCHFmicro, GBPCADmicro, GBPNZDmicro, GOLDmicro, USDCADmicro | 5000 | 78.6 | 11.9 | 75.8 / 12.4 |
| điểm lãi/DD | `od_ghep60ff9350c26c63ee_XM_CSV`<br>`od_skea0b8298aa53_XM_CSV`<br>`od_skea31214192bc_XM_CSV`<br>`od_skea89d6f8661b_XM_CSV`<br>`od_skeadc40280363_XM_CSV` | AUDUSDmicro, CADJPYmicro, GBPCADmicro, GBPNZDmicro, GOLDmicro | 5000 | 50.9 | 7.8 | 47.7 / 8.0 |
| điểm lãi/DD | `od_ghepe9b41c33d4deee54_XM_CSV`<br>`od_skea0b8298aa53_XM_CSV`<br>`od_skea8771fe6061_XM_CSV`<br>`od_skea89d6f8661b_XM_CSV`<br>`od_skeadd170ac7bf_XM_CSV` | AUDUSDmicro, EURCHFmicro, GBPNZDmicro, GOLDmicro, USDCADmicro | 5000 | 73.8 | 11.3 | 71.4 / 11.7 |
| lãi cao nhất, DD ≤ 20% | `od_ghepe9b41c33d4deee54_XM_CSV`<br>`od_skea0b8298aa53_XM_CSV`<br>`od_skea44640140cc_XM_CSV`<br>`od_skea8771fe6061_XM_CSV` | EURCHFmicro, GBPCADmicro, GBPNZDmicro, GOLDmicro | 4000 | 103.5 | 19.6 | 99.2 / 20.6 |
| lãi cao nhất, DD ≤ 30% | `od_ghep9c03cef0b89f948f_XM_CSV`<br>`od_ghepe9b41c33d4deee54_XM_CSV`<br>`od_skea0b8298aa53_XM_CSV` | GBPCADmicro, GBPNZDmicro, GOLDmicro | 3000 | 128.6 | 29.8 | 124.5 / 30.6 |
| lãi cao nhất, DD ≤ 40% | `od_ghep9c03cef0b89f948f_XM_CSV`<br>`od_ghepe9b41c33d4deee54_XM_CSV` | GBPCADmicro, GBPNZDmicro | 2000 | 150.4 | 36.9 | 145.4 / 38.1 |
| lãi cao nhất, DD ≤ 60% | `od_ghep9c03cef0b89f948f_XM_CSV`<br>`od_ghepe9b41c33d4deee54_XM_CSV` | GBPCADmicro, GBPNZDmicro | 2000 | 150.4 | 36.9 | 145.4 / 38.1 |

### 6.3 Danh mục (chỉ hệ “bền”) — tương quan ngày ≤ 0.3, tối đa 2 hệ/cặp, đã đo 5774 nhóm (MÔ PHỎNG)

| Loại | Hệ | Cặp | Vốn USD | %/năm | DD equity % | Sau stress ×1,5+7: %/năm / DD |
|---|---|---|---|---|---|---|
| điểm lãi/DD | `od_ghep60ff9350c26c63ee_XM_CSV`<br>`od_ghepe9b41c33d4deee54_XM_CSV`<br>`od_skea8771fe6061_XM_CSV`<br>`od_skeadc40280363_XM_CSV`<br>`od_skeaf7a71f885d_XM_CSV` | CADJPYmicro, EURCHFmicro, GBPCADmicro, GBPNZDmicro | 5000 | 70.4 | 11.1 | 67.1 / 11.8 |
| điểm lãi/DD | `od_ghep60ff9350c26c63ee_XM_CSV`<br>`od_mql5e3c3e4f028dbab72_XM_CSV`<br>`od_skea0c762cdb38_XM_CSV`<br>`od_skea31214192bc_XM_CSV`<br>`od_skeadc40280363_XM_CSV` | CADJPYmicro, CHFJPYmicro, EURCADmicro, GBPCADmicro, GBPNZDmicro | 5000 | 41.1 | 6.6 | 37.7 / 7.1 |
| điểm lãi/DD | `od_ghep60ff9350c26c63ee_XM_CSV`<br>`od_ghepe9b41c33d4deee54_XM_CSV`<br>`od_skea8771fe6061_XM_CSV`<br>`od_skead5df5bc834_XM_CSV`<br>`od_skeaf7a71f885d_XM_CSV` | EURCHFmicro, GBPCADmicro, GBPNZDmicro, GOLDmicro | 5000 | 70.6 | 11.4 | 67.3 / 12.1 |
| lãi cao nhất, DD ≤ 20% | `od_ghepe9b41c33d4deee54_XM_CSV`<br>`od_skea44640140cc_XM_CSV`<br>`od_skea8771fe6061_XM_CSV`<br>`od_skeab536f57733_XM_CSV` | EURCHFmicro, EURUSDmicro, GBPCADmicro, GBPNZDmicro | 4000 | 102.8 | 19.4 | 98.2 / 20.4 |
| lãi cao nhất, DD ≤ 30% | `od_ghep9c03cef0b89f948f_XM_CSV`<br>`od_ghepe9b41c33d4deee54_XM_CSV`<br>`od_skea8771fe6061_XM_CSV` | EURCHFmicro, GBPCADmicro, GBPNZDmicro | 3000 | 128.2 | 28.3 | 123.7 / 29.7 |
| lãi cao nhất, DD ≤ 40% | `od_ghep9c03cef0b89f948f_XM_CSV`<br>`od_ghepe9b41c33d4deee54_XM_CSV` | GBPCADmicro, GBPNZDmicro | 2000 | 150.4 | 36.9 | 145.4 / 38.1 |
| lãi cao nhất, DD ≤ 60% | `od_ghep9c03cef0b89f948f_XM_CSV`<br>`od_ghepe9b41c33d4deee54_XM_CSV` | GBPCADmicro, GBPNZDmicro | 2000 | 150.4 | 36.9 | 145.4 / 38.1 |

### 6.4 Kiểm tra quá khớp khi CHỌN danh mục: chọn trên đoạn trước 2025-08-22, đo đoạn sau (MÔ PHỎNG)

| Hệ (chọn trên IS) | IS %/năm | IS DD % | OOS %/năm | OOS DD % |
|---|---|---|---|---|
| `od_ghepe9b41c33d4deee54_XM_CSV`<br>`od_mql5d8f573b8c2314bbf_XM_CSV`<br>`od_skea8771fe6061_XM_CSV`<br>`od_skeaa3d6925a71_XM_CSV`<br>`od_skeaa7cd39087e_XM_CSV` | 121.7 | 9.2 | 39.6 | 37.0 |
| `od_ghepe9b41c33d4deee54_XM_CSV`<br>`od_mql5e3c3e4f028dbab72_XM_CSV`<br>`od_skea8771fe6061_XM_CSV`<br>`od_skeaa3d6925a71_XM_CSV`<br>`od_skeaa7cd39087e_XM_CSV` | 117.8 | 9.0 | 52.4 | 32.5 |
| `od_ghepe9b41c33d4deee54_XM_CSV`<br>`od_skea8771fe6061_XM_CSV`<br>`od_skeaa3d6925a71_XM_CSV`<br>`od_skeaa7cd39087e_XM_CSV`<br>`od_skeadc40280363_XM_CSV` | 122.6 | 9.4 | 49.3 | 33.4 |
| `od_ghep60ff9350c26c63ee_XM_CSV`<br>`od_ghepe9b41c33d4deee54_XM_CSV`<br>`od_skea8771fe6061_XM_CSV`<br>`od_skeaa3d6925a71_XM_CSV`<br>`od_skeaa7cd39087e_XM_CSV` | 128.9 | 10.0 | 61.8 | 36.8 |
| `od_ghepe9b41c33d4deee54_XM_CSV`<br>`od_skea363d6c8238_XM_CSV`<br>`od_skea8771fe6061_XM_CSV`<br>`od_skeaa3d6925a71_XM_CSV`<br>`od_skeaa7cd39087e_XM_CSV` | 115.8 | 9.1 | 51.4 | 32.5 |
| *Chia đều cả 71 hệ (không chọn)* | | | 56.4 | 21.5 |

→ DD của danh mục “tốt nhất trong mẫu” tăng mạnh ngoài mẫu: số DD 7–20 % ở bảng 6.3 là **lạc quan**, cần cộng biên an toàn.

### 6.5 Hàng chờ

Việc MT5 vòng 2 có hệ gốc nằm trong các danh mục trên được cộng 10 điểm ưu tiên (`danh_muc_v2_sau=true`): 6 việc. Hệ không có tín hiệu Python trên box (bản dịch ở máy nhà) → không sinh được việc chuyển cặp/khung: **CHƯA ĐO ĐƯỢC**.
