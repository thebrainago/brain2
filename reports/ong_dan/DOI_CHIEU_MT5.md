# Đối chiếu lệnh MT5 với Python (chế độ VAO_CSV)

Cùng một CSV lệnh vào, cùng giá (nến EA xuất ra từ tester). Sai số cho phép: giờ mở lệch ≤ 1 nến; giá mở lệch ≤ 3 × spread + 0.05 % giá; lot lệch ≤ 1 bước; ≥ 95 % lệnh ghép được 1-1; tổng lãi/lỗ lệch ≤ 10 % hoặc ≤ 1 % vốn. Phía Python là MÔ PHỎNG, PHÍ TẠM; spread theo giờ lấy từ nến EA nếu có.

| Việc | Kết luận | Lệnh Py / MT5 / khớp | Tỉ lệ khớp | Lãi Py / MT5 (USD) | Lệch nến mở (trung vị) | Nguồn giá | Ghi chú |
|---|---|---|---|---|---|---|---|
| od_nhapcf8073245473d2a1_XM_CSV | LECH | 230 / 188 / 113 | 49.13 % | 958.13 / 1024.92 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 49.1% < 95% |
| od_skst299b0817f66d4096_XM_CSV | LECH | 24 / 27 / 0 | 0.0 % | 591.32 / 332.1 | None | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 0.0% < 95%; lech lai 259.22 > 59.13 USD |
| od_skst48a4616b10a6ff9c_XM_CSV | LECH | 6 / 6 / 0 | 0.0 % | 323.05 / 103.9 | None | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 0.0% < 95%; lech lai 219.15 > 32.31 USD |
| od_skst4ac0c7fd10781af4_XM_CSV | LECH | 87 / 69 / 0 | 0.0 % | 6896.08 / 5606.72 | None | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 0.0% < 95%; lech lai 1289.36 > 689.61 USD |
| od_skstaca366b679c75482_XM_CSV | LECH | 15 / 15 / 14 | 93.33 % | 327.29 / 339.41 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 93.3% < 95% |
| od_skstadd3a54f8edcbce2_XM_CSV | LECH | 16 / 15 / 14 | 87.5 % | 1099.58 / 1042.87 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 87.5% < 95% |
| od_skstc21c2acd239f3c87_XM_CSV | LECH | 21 / 20 / 18 | 85.71 % | 533.08 / 525.66 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 85.7% < 95% |
| od_mql5013314d527074d05_XM_CSV | LECH | 1541 / 1228 / 810 | 52.56 % | 7432.05 / 5174.51 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 52.6% < 95%; lech lai 2257.54 > 743.20 USD |
| od_mql504e8d5d4a7d0b684_XM_CSV | LECH | 410 / 406 / 375 | 91.46 % | 3244.32 / 3260.89 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 91.5% < 95% |
| od_mql514d2e7f097c4ff6e_XM_CSV | LECH | 46 / 54 / 35 | 64.81 % | 1372.24 / 1768.0 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 64.8% < 95%; lech lai 395.76 > 137.22 USD |
| od_mql5164edabb0bca1b7d_XM_CSV | LECH | 231 / 224 / 211 | 91.34 % | -977.79 / 1143.4 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 91.3% < 95%; lech lai 2121.19 > 97.78 USD |
| od_mql5250fc0146190663c_XM_CSV | LECH | 61 / 61 / 54 | 88.52 % | -998.34 / 341.34 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 88.5% < 95%; lech lai 1339.68 > 99.83 USD |
| od_mql5a790e25e547f0b57_XM_CSV | LECH | 32 / 31 / 29 | 90.62 % | 968.03 / 581.19 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 90.6% < 95%; lech lai 386.84 > 96.80 USD |
| od_mql5ad7d22b5b165a673_XM_CSV | LECH | 133 / 134 / 124 | 92.54 % | 741.36 / 1163.59 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 92.5% < 95%; lech lai 422.23 > 74.14 USD |
| od_mql5b39a9f3ba216fb47_XM_CSV | LECH | 25 / 392 / 10 | 2.55 % | -1018.23 / 669.83 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 2.6% < 95%; lech lai 1688.06 > 101.82 USD |
| od_mql5d8f573b8c2314bbf_XM_CSV | LECH | 113 / 106 / 106 | 93.81 % | 1561.11 / 2138.57 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 93.8% < 95%; lech lai 577.46 > 156.11 USD |
| od_mql5e31426a40a5897fc_XM_CSV | LECH | 15 / 15 / 14 | 93.33 % | 918.25 / 921.34 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 93.3% < 95% |
| od_mql5e3c3e4f028dbab72_XM_CSV | LECH | 130 / 120 / 104 | 80.0 % | 1246.77 / 1055.19 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 80.0% < 95%; lech lai 191.58 > 124.68 USD |
| od_mql5f3313c2c79f00c10_XM_CSV | LECH | 176 / 178 / 162 | 91.01 % | 2291.51 / 3115.86 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 91.0% < 95%; lech lai 824.35 > 229.15 USD |
| od_mql5f6a59c4de0d4f8be_XM_CSV | LECH | 62 / 50 / 24 | 38.71 % | 544.14 / 464.75 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 38.7% < 95%; lech lai 79.39 > 54.41 USD |
| od_mql5fd4bc285e11ab5a1_XM_CSV | LECH | 118 / 138 / 87 | 63.04 % | 633.34 / 1638.22 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 63.0% < 95%; lech lai 1004.88 > 63.33 USD |
| od_skea057b28a77f_XM_CSV | LECH | 392 / 349 / 300 | 76.53 % | -665.66 / 395.56 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 76.5% < 95%; lech lai 1061.22 > 66.57 USD |
| od_skea1f5e88bc8f_XM_CSV | LECH | 275 / 188 / 155 | 56.36 % | 1177.08 / 1827.54 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 56.4% < 95%; lech lai 650.46 > 117.71 USD |
| od_skea44640140cc_XM_CSV | LECH | 770 / 616 / 408 | 52.99 % | 15794.32 / 10071.93 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 53.0% < 95%; lech lai 5722.39 > 1579.43 USD |
| od_skea8897567020_XM_CSV | LECH | 181 / 154 / 39 | 21.55 % | 2674.91 / 1390.88 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 21.5% < 95%; lech lai 1284.03 > 267.49 USD |
| od_skeafdbf5bcad6_XM_CSV | LECH | 188 / 190 / 184 | 96.84 % | 1168.75 / 1726.01 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | lech lai 557.26 > 116.88 USD |
| od_tohop09a3b2ddc3e78dc8_XM_CSV | LECH | 68 / 69 / 62 | 89.86 % | 706.01 / 492.82 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 89.9% < 95%; lech lai 213.19 > 70.60 USD |
| od_tohopd315744077e1a7aa_XM_CSV | LECH | 55 / 59 / 43 | 72.88 % | 358.19 / 1535.02 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 72.9% < 95%; lech lai 1176.83 > 35.82 USD |
| od_skea894727cf4f_XM_CSV | LECH | 289 / 163 / 123 | 42.56 % | 868.51 / 563.94 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 42.6% < 95%; lech lai 304.57 > 86.85 USD |
| od_skeaa7cd39087e_XM_CSV | LECH | 468 / 351 / 219 | 46.79 % | 6434.66 / 7489.61 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 46.8% < 95%; lech lai 1054.95 > 643.47 USD |
| od_skeaaaa64fdbcb_XM_CSV | LECH | 65 / 51 / 23 | 35.38 % | 595.8 / 519.61 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 35.4% < 95%; lech lai 76.19 > 59.58 USD |
| od_skeaaba30a4e06_XM_CSV | LECH | 183 / 164 / 147 | 80.33 % | 821.5 / 727.88 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 80.3% < 95%; lech lai 93.62 > 82.15 USD |
| od_skea02906b7d6a_XM_CSV | LECH | 242 / 180 / 109 | 45.04 % | 3780.94 / 5948.86 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 45.0% < 95%; lech lai 2167.92 > 378.09 USD |
| od_skea3279057100_XM_CSV | LECH | 161 / 203 / 104 | 51.23 % | 1783.94 / 2835.33 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 51.2% < 95%; lech lai 1051.39 > 178.39 USD |
| od_skea5049c79288_XM_CSV | LECH | 106 / 83 / 30 | 28.3 % | 2191.18 / 1224.95 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 28.3% < 95%; lech lai 966.23 > 219.12 USD |
| od_skea9c34a60460_XM_CSV | LECH | 115 / 107 / 103 | 89.57 % | -752.45 / 3141.19 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 89.6% < 95%; lech lai 3893.64 > 75.24 USD |
| od_skeaff87f96be7_XM_CSV | LECH | 233 / 211 / 71 | 30.47 % | 1888.61 / 2243.01 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 30.5% < 95%; lech lai 354.40 > 188.86 USD |
| od_skea0075f624b3_XM_CSV | LECH | 192 / 139 / 65 | 33.85 % | 12030.0 / 4924.0 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 33.9% < 95%; lech lai 7106.00 > 1203.00 USD |
| od_018dcb1347276c97_XM_CSV | LECH | 91 / 76 / 69 | 75.82 % | 843.01 / 405.96 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 75.8% < 95%; lech lai 437.05 > 84.30 USD |
| od_3304d2fad28adef6_XM_CSV | LECH | 61 / 64 / 54 | 84.38 % | 782.32 / 408.78 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 84.4% < 95%; lech lai 373.54 > 78.23 USD |
| od_b0be91a35f43f34a_XM_CSV | LECH | 47 / 46 / 38 | 80.85 % | 1662.44 / 1684.11 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 80.9% < 95% |
| od_tohop16b0d75bb149f634_XM_CSV | LECH | 126 / 127 / 118 | 92.91 % | 6931.75 / 5078.62 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 92.9% < 95%; lech lai 1853.13 > 693.18 USD |
| od_skea0757c93eb3_XM_CSV | LECH | 3 / 2 / 2 | 66.67 % | 765.41 / 319.59 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 66.7% < 95%; lech lai 445.82 > 76.54 USD |
| od_skea0806a3a5e5_XM_CSV | LECH | 34 / 29 / 13 | 38.24 % | 1674.22 / 915.99 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 38.2% < 95%; lech lai 758.23 > 167.42 USD |
| od_skea0ca971ac32_XM_CSV | LECH | 41 / 27 / 18 | 43.9 % | 12295.58 / 4590.84 | 0.0 | GIÁ EA XUẤT (cùng giá MT5) | ti le khop 43.9% < 95%; lech lai 7704.74 > 1229.56 USD |
