# Ứng viên MT5 (cộng dồn, tự sinh bởi `mt5tools/bao_cao_phien.py`)

Mỗi hệ một dòng, số **đo thật** từ báo cáo MT5 real tick (`reports/ong_dan/ket_qua_mt5/od_*.htm`), tài khoản XM micro 1:500, vốn trong báo cáo. Chuẩn cuối của chủ dự án: sụt giảm ≤ 80 %, lãi ≥ 10 %/năm sau phí (lãi/năm = lãi ròng / vốn / số năm của **kỳ trong báo cáo**). Lãi kép ghi kèm để so với Python. Chạy sai symbol → CHƯA ĐO ĐƯỢC, phải chạy lại.

Cập nhật: 20/10/2026 09:59 (giờ máy chạy).

| Kết luận | id | EA/nguồn | Symbol | TF | Lãi ròng | %/năm | %/năm kép | Sụt giảm % | PF | Lệnh | Kỳ | Phiên đo | Chất lượng tick | Ghi chú |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ĐẠT | od_skea44640140cc_XM_CSV | sk_ea_44640140cc | GBPCADmicro | H1 | 10075.87 | 364.38 | 138.61 | 32.53 | 4.32 | 616 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_tohop16b0d75bb149f634_XM_CSV | to_hop_16b0d75bb149f634 | GBPCADmicro | H1 | 5078.62 | 183.84 | 92.19 | 55.87 | 4.71 | 127 | 2023.12.27–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_skea0075f624b3_XM_CSV | sk_ea_0075f624b3 | GBPNZDmicro | H1 | 4922.39 | 179.43 | 91.25 | 37.26 | 3.15 | 139 | 2024.01.03–2026.10.01 | 2026-10-19 | 100% real ticks |  |
| ĐẠT | od_skea0ca971ac32_XM_CSV | sk_ea_0ca971ac32 | GBPNZDmicro | H4 | 4533.59 | 164.28 | 85.88 | 37.07 | 80.19 | 27 | 2023.12.28–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_mql5f3313c2c79f00c10_XM_CSV | mql5_f3313c2c79f00c10 | EURGBPmicro | H4 | 3026.52 | 110.21 | 66.07 | 50.64 | 4.32 | 178 | 2024.01.02–2026.10.01 | 2026-10-19 | 100% real ticks |  |
| ĐẠT | od_skeaa7cd39087e_XM_CSV | sk_ea_a7cd39087e | GOLDmicro | H1 | 2665.71 | 96.40 | 59.96 | 60.59 | 1.39 | 351 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_skeaff87f96be7_XM_CSV | sk_ea_ff87f96be7 | GBPCADmicro | H1 | 2247.33 | 81.51 | 53.30 | 23.40 | 3.10 | 211 | 2023.12.29–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_skstadd3a54f8edcbce2_XM_CSV | sk_st_add3a54f8edcbce2 | EURUSDmicro | H1 | 1042.87 | 77.74 | 70.32 | 60.76 | 7.31 | 15 | 2025.01.30–2026.06.04 | 2026-10-19 | 100% real ticks |  |
| ĐẠT | od_skea3279057100_XM_CSV | sk_ea_3279057100 | EURGBPmicro | H1 | 1779.61 | 64.36 | 44.73 | 64.02 | 1.24 | 203 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_b0be91a35f43f34a_XM_CSV | b0be91a35f43f34a | USDCADmicro | H4 | 1684.11 | 62.13 | 43.95 | 53.65 | 0.00 | 46 | 2024.01.15–2026.10.01 | 2026-10-19 | 100% real ticks |  |
| ĐẠT | od_skea02906b7d6a_XM_CSV | sk_ea_02906b7d6a | GOLDmicro | H4 | 1496.80 | 54.13 | 39.22 | 70.34 | 1.26 | 180 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_skea8897567020_XM_CSV | sk_ea_8897567020 | GBPNZDmicro | H1 | 1400.85 | 50.66 | 37.26 | 35.56 | 1.90 | 154 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_mql5013314d527074d05_XM_CSV | mql5_013314d527074d05 | AUDCADmicro | H1 | 5162.99 | 48.08 | 18.45 | 27.26 | 2.59 | 1228 | 2016.01.05–2026.10.01 | 2026-10-19 | 25% real ticks | chất lượng tick thấp (25% real ticks) |
| ĐẠT | od_skea5049c79288_XM_CSV | sk_ea_5049c79288 | GBPCADmicro | H4 | 1246.00 | 45.97 | 34.79 | 30.42 | 3.07 | 83 | 2024.01.15–2026.10.01 | 2026-10-19 | 100% real ticks |  |
| ĐẠT | od_mql5fd4bc285e11ab5a1_XM_CSV | mql5_fd4bc285e11ab5a1 | EURCHFmicro | H4 | 1106.60 | 40.06 | 30.96 | 49.29 | 1.83 | 138 | 2023.12.27–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_skstc21c2acd239f3c87_XM_CSV | sk_st_c21c2acd239f3c87 | EURUSDmicro | H1 | 525.66 | 39.18 | 37.01 | 49.71 | 4.50 | 20 | 2025.01.30–2026.06.04 | 2026-10-19 | 100% real ticks |  |
| ĐẠT | od_mql504e8d5d4a7d0b684_XM_CSV | mql5_04e8d5d4a7d0b684 | NZDUSDmicro | H4 | 3260.89 | 37.21 | 17.99 | 44.94 | 2.15 | 406 | 2017.12.26–2026.10.01 | 2026-10-19 | 31% real ticks | chất lượng tick thấp (31% real ticks) |
| ĐẠT | od_mql5e3c3e4f028dbab72_XM_CSV | mql5_e3c3e4f028dbab72 | EURCADmicro | H4 | 1023.49 | 37.01 | 29.03 | 11.85 | 6.21 | 120 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_mql5e31426a40a5897fc_XM_CSV | mql5_e31426a40a5897fc | GBPUSDmicro | H4 | 921.34 | 35.57 | 28.68 | 58.66 | 0.00 | 15 | 2024.02.28–2026.10.01 | 2026-10-19 | 100% real ticks |  |
| ĐẠT | od_mql5ad7d22b5b165a673_XM_CSV | mql5_ad7d22b5b165a673 | GBPUSDmicro | H4 | 944.20 | 34.15 | 27.18 | 55.00 | 2.36 | 134 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_skeafdbf5bcad6_XM_CSV | sk_ea_fdbf5bcad6 | EURCADmicro | H1 | 912.90 | 33.01 | 26.44 | 12.81 | 1.94 | 190 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_mql5d8f573b8c2314bbf_XM_CSV | mql5_d8f573b8c2314bbf | EURAUDmicro | H1 | 830.72 | 30.04 | 24.44 | 39.95 | 1.60 | 106 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_skea0806a3a5e5_XM_CSV | sk_ea_0806a3a5e5 | AUDNZDmicro | H1 | 829.37 | 29.99 | 24.41 | 25.88 | 10.57 | 29 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_skeaaba30a4e06_XM_CSV | sk_ea_aba30a4e06 | USDJPYmicro | H4 | 727.88 | 26.32 | 21.87 | 45.79 | 2.07 | 164 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_skstaca366b679c75482_XM_CSV | sk_st_aca366b679c75482 | EURUSDmicro | H1 | 339.41 | 25.35 | 24.39 | 18.20 | 0.00 | 15 | 2025.01.30–2026.06.03 | 2026-10-19 | 100% real ticks |  |
| ĐẠT | od_nhapcf8073245473d2a1_XM_CSV | nhap_cf8073245473d2a1 | EURGBPmicro | H4 | 687.05 | 24.85 | 20.82 | 51.53 | 1.42 | 188 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_mql5b39a9f3ba216fb47_XM_CSV | mql5_b39a9f3ba216fb47 | CHFJPYmicro | H1 | 638.48 | 23.11 | 19.57 | 27.06 | 1.81 | 392 | 2023.12.27–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_mql5a790e25e547f0b57_XM_CSV | mql5_a790e25e547f0b57 | AUDNZDmicro | H4 | 557.33 | 20.30 | 17.51 | 20.87 | 24.36 | 31 | 2024.01.02–2026.10.01 | 2026-10-19 | 100% real ticks |  |
| ĐẠT | od_tohop09a3b2ddc3e78dc8_XM_CSV | to_hop_09a3b2ddc3e78dc8 | EURUSDmicro | H4 | 492.82 | 17.82 | 15.59 | 32.00 | 2.41 | 69 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| ĐẠT | od_3304d2fad28adef6_XM_CSV | 3304d2fad28adef6 | USDCADmicro | H4 | 408.78 | 15.78 | 14.15 | 40.16 | 1.66 | 64 | 2024.02.28–2026.10.01 | 2026-10-19 | 100% real ticks |  |
| ĐẠT | od_018dcb1347276c97_XM_CSV | 018dcb1347276c97 | EURNZDmicro | H4 | 365.94 | 13.43 | 12.13 | 18.45 | 5.55 | 76 | 2024.01.10–2026.10.01 | 2026-10-19 | 100% real ticks |  |
| ĐẠT | od_skea0757c93eb3_XM_CSV | sk_ea_0757c93eb3 | EURNZDmicro | H4 | 319.59 | 11.56 | 10.55 | 29.25 | 0.00 | 2 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks |  |
| TRƯỢT | od_mql514d2e7f097c4ff6e_XM_CSV | mql5_14d2e7f097c4ff6e | NZDUSDmicro | H1 | 1742.30 | 19.88 | 12.20 | 81.63 | 68.79 | 54 | 2017.12.26–2026.10.01 | 2026-10-19 | 31% real ticks | sut giam 81.6% > 80%; chất lượng tick thấp (31% real ticks) |
| TRƯỢT | od_mql5164edabb0bca1b7d_XM_CSV | mql5_164edabb0bca1b7d | NZDUSDmicro | H1 | -1012.56 | -11.55 | -100.00 | 101.36 | 0.57 | 224 | 2017.12.26–2026.10.01 | 2026-10-19 | 31% real ticks | sut giam 101.4% > 80%; lai -11.6%/nam < 10%; chất lượng tick thấp (31% real ticks) |
| TRƯỢT | od_mql5250fc0146190663c_XM_CSV | mql5_250fc0146190663c | NZDUSDmicro | H1 | -1017.33 | -11.61 | -100.00 | 102.69 | 0.39 | 61 | 2017.12.27–2026.10.01 | 2026-10-19 | 31% real ticks | sut giam 102.7% > 80%; lai -11.6%/nam < 10%; chất lượng tick thấp (31% real ticks) |
| TRƯỢT | od_skea057b28a77f_XM_CSV | sk_ea_057b28a77f | EURCADmicro | H1 | -617.06 | -22.31 | -29.33 | 71.10 | 0.67 | 349 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks | lai -22.3%/nam < 10% |
| TRƯỢT | od_skea9c34a60460_XM_CSV | sk_ea_9c34a60460 | GBPCADmicro | H1 | -914.50 | -33.07 | -58.91 | 97.94 | 0.82 | 107 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks | sut giam 97.9% > 80%; lai -33.1%/nam < 10% |
| TRƯỢT | od_skeaaaa64fdbcb_XM_CSV | sk_ea_aaa64fdbcb | GBPCADmicro | H1 | -988.29 | -35.78 | -80.01 | 99.07 | 0.42 | 51 | 2023.12.27–2026.10.01 | 2026-10-19 | 99% real ticks | sut giam 99.1% > 80%; lai -35.8%/nam < 10% |
| TRƯỢT | od_skea894727cf4f_XM_CSV | sk_ea_894727cf4f | EURCADmicro | H4 | -993.51 | -35.93 | -83.83 | 99.52 | 0.50 | 163 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks | sut giam 99.5% > 80%; lai -35.9%/nam < 10% |
| TRƯỢT | od_mql5f6a59c4de0d4f8be_XM_CSV | mql5_f6a59c4de0d4f8be | GBPCADmicro | H1 | -994.69 | -35.97 | -84.96 | 99.55 | 0.41 | 50 | 2023.12.26–2026.10.01 | 2026-10-19 | 99% real ticks | sut giam 99.5% > 80%; lai -36.0%/nam < 10% |
| TRƯỢT | od_skea1f5e88bc8f_XM_CSV | sk_ea_1f5e88bc8f | EURGBPmicro | H1 | -988.78 | -36.12 | -80.60 | 99.41 | 0.76 | 188 | 2024.01.05–2026.10.01 | 2026-10-19 | 100% real ticks | sut giam 99.4% > 80%; lai -36.1%/nam < 10% |
| TRƯỢT | od_tohopd315744077e1a7aa_XM_CSV | to_hop_d315744077e1a7aa | EURGBPmicro | H1 | -1012.16 | -36.64 | -100.00 | 100.44 | 0.71 | 59 | 2023.12.27–2026.10.01 | 2026-10-19 | 99% real ticks | sut giam 100.4% > 80%; lai -36.6%/nam < 10% |
| CHƯA ĐO ĐƯỢC | od_skst299b0817f66d4096_XM_CSV | sk_st_299b0817f66d4096 | EURUSD# | H1 | -967.16 | CHƯA ĐO ĐƯỢC | CHƯA ĐO ĐƯỢC | 98.12 | 0.57 | 27 | 2025.01.30–2026.06.03 | 2026-10-19 | 100% real ticks | SAI SYMBOL EURUSD# (việc EURUSDmicro) - CHƯA ĐO ĐƯỢC |
| CHƯA ĐO ĐƯỢC | od_skst48a4616b10a6ff9c_XM_CSV | sk_st_48a4616b10a6ff9c | EURUSD# | H1 | -984.40 | CHƯA ĐO ĐƯỢC | CHƯA ĐO ĐƯỢC | 98.67 | 0.10 | 6 | 2025.01.30–2026.06.03 | 2026-10-19 | 100% real ticks | SAI SYMBOL EURUSD# (việc EURUSDmicro) - CHƯA ĐO ĐƯỢC |
| CHƯA ĐO ĐƯỢC | od_skst4ac0c7fd10781af4_XM_CSV | sk_st_4ac0c7fd10781af4 | EURUSD# | H1 | 5606.72 | CHƯA ĐO ĐƯỢC | CHƯA ĐO ĐƯỢC | 53.91 | 7.44 | 69 | 2025.01.30–2026.06.03 | 2026-10-19 | 100% real ticks | SAI SYMBOL EURUSD# (việc EURUSDmicro) - CHƯA ĐO ĐƯỢC |
