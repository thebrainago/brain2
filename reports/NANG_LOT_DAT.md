# Nâng lot: hệ trượt chỉ vì CAGR ≤ 10% (DD < 80%)

Luật Anh (03/11/2026): *CAGR không cao thì nâng lot, miễn DD không quá* → hệ ĐẠT nếu có hệ số lot k cho CAGR > 10%/năm và max DD < 80% (equity ≤ 0 = cháy = trượt).

Sinh bởi `python -m nhan.nang_lot`. Chỉ số đo/chạy lại thật; ô '—' = CHƯA ĐO ĐƯỢC. k thử trên lưới 1, 1,25, 1,5, 1,75, 2, 2,5, 3, 3,5, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50 (dừng khi hỏng 2 mức liền).

Cách đo:
- **MÔ PHỎNG chạy lại lot×k**: chạy lại đúng mô phỏng Python (nhan/dich_nguoc, lot theo vốn = lãi kép, có swap/margin/stop-out). Vẫn là MÔ PHỎNG, chưa phải tester MT5.
- **MT5 phát lại deal×k**: bảng Deals trong báo cáo MT5 .htm, lãi/lỗ mỗi deal ×k trên cùng vốn (lot cố định). DD = max(DD số dư phát lại, k × DD equity báo cáo) → phần equity là XẤP XỈ.
- **XẤP XỈ tuyến tính**: chỉ có số tổng; net_k = k·net, DD_k ≈ k·DD.
- Chu kỳ < 2 năm = **quá ngắn** (không đủ để tin).

Tổng dòng xét: 130; có k đạt: 84; không k nào đạt: 46.

## Hệ đạt sau nâng lot

| Hệ | Mã | Năm | Nguồn | CAGR gốc % | DD gốc % | k nhỏ nhất CAGR>10 | k lớn nhất DD<80 | k đạt chọn | CAGR @k % | DD @k % | Cách đo | Ghi chú |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DichNguoc:UV1:swap_0_lac_quan:lot0.00025/1000 | AUDCAD | 18,77 | mo_phong_python | 3,09 | 15,41 | 3,00 | 5,00 | 3,00 | 10,02 | 43,58 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV1:swap_0_lac_quan:lot0.00025/1000 | EURGBP | 18,77 | mo_phong_python | 3,60 | 20,75 | 3,00 | 4,00 | 3,00 | 11,89 | 55,84 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV1:swap_0_lac_quan:lot0.0005/1000 | AUDCAD | 18,77 | mo_phong_python | 6,39 | 27,01 | 1,50 | 2,50 | 1,50 | 10,02 | 43,58 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV1:swap_0_lac_quan:lot0.0005/1000 | EURGBP | 18,77 | mo_phong_python | 7,58 | 36,94 | 1,50 | 2,00 | 1,50 | 11,89 | 55,84 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV1_luoi_hedge_tp35_(2330430):lot0.0005/1000 | AUDCAD | 18,77 | mo_phong_python | 6,39 | 27,01 | 2,50 | 2,50 | 2,50 | 10,48 | 67,53 | XẤP XỈ tuyến tính | MÔ PHỎNG |
| DichNguoc:UV2:swap_0_lac_quan:lot0.00025/1000 | EURGBP | 18,77 | mo_phong_python | 5,12 | 33,30 | 2,00 | 2,50 | 2,00 | 10,37 | 63,47 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| Telegram:EA4_MACD_200EMA_H4:swap_0_lac_quan | XAUUSD | 17,57 | mo_phong_python | 5,21 | 20,90 | 2,00 | 5,00 | 2,00 | 10,68 | 38,38 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| Telegram:EA4_MACD_200EMA_H4:swap_do_XM | XAUUSD | 17,57 | mo_phong_python | 3,92 | 24,24 | 3,00 | 5,00 | 3,00 | 11,28 | 59,20 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV1:swap_0_lac_quan:lot0.00025/1000 | NZDCAD | 15,75 | mo_phong_python | 2,60 | 13,70 | 3,50 | 6,00 | 3,50 | 10,30 | 45,69 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV1:swap_0_lac_quan:lot0.0005/1000 | NZDCAD | 15,75 | mo_phong_python | 5,40 | 27,57 | 1,75 | 3,50 | 1,75 | 10,30 | 45,69 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV1:swap_bao_thu:lot0.00025/1000 | NZDCAD | 15,75 | mo_phong_python | 1,62 | 15,47 | 5,00 | 5,00 | 5,00 | 11,01 | 70,41 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV1:swap_bao_thu:lot0.0005/1000 | NZDCAD | 15,75 | mo_phong_python | 3,39 | 31,00 | 2,50 | 2,50 | 2,50 | 11,01 | 70,41 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV1:swap_bao_thu:lot0.001/1000 | NZDCAD | 15,75 | mo_phong_python | 8,17 | 58,37 | 1,25 | 1,25 | 1,25 | 11,01 | 70,41 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV1:swap_do:lot0.00025/1000 | NZDCAD | 15,75 | mo_phong_python | 1,62 | 15,44 | 5,00 | 5,00 | 5,00 | 11,18 | 70,20 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV1:swap_do:lot0.0005/1000 | NZDCAD | 15,75 | mo_phong_python | 3,45 | 30,87 | 2,50 | 2,50 | 2,50 | 11,18 | 70,20 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV1:swap_do:lot0.001/1000 | NZDCAD | 15,75 | mo_phong_python | 8,33 | 58,08 | 1,25 | 1,25 | 1,25 | 11,18 | 70,20 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV2:swap_0_lac_quan:lot0.00025/1000 | NZDCAD | 15,75 | mo_phong_python | 4,70 | 8,98 | 2,50 | 8,00 | 2,50 | 12,25 | 20,37 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV2:swap_0_lac_quan:lot0.0005/1000 | NZDCAD | 15,75 | mo_phong_python | 9,48 | 16,16 | 1,25 | 4,00 | 1,25 | 12,25 | 20,37 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV2:swap_bao_thu:lot0.00025/1000 | NZDCAD | 15,75 | mo_phong_python | 4,20 | 9,46 | 2,50 | 8,00 | 2,50 | 10,51 | 21,46 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV2:swap_bao_thu:lot0.0005/1000 | NZDCAD | 15,75 | mo_phong_python | 8,43 | 16,96 | 1,25 | 4,00 | 1,25 | 10,51 | 21,46 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV2:swap_do:lot0.00025/1000 | NZDCAD | 15,75 | mo_phong_python | 4,22 | 9,44 | 2,50 | 8,00 | 2,50 | 10,62 | 21,34 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| DichNguoc:UV2:swap_do:lot0.0005/1000 | NZDCAD | 15,75 | mo_phong_python | 8,48 | 16,92 | 1,25 | 4,00 | 1,25 | 10,62 | 21,34 | MÔ PHỎNG chạy lại lot×k | MÔ PHỎNG |
| od_v2r2p_bg120_brainxlrsi_XM_KIEM_XM_CSV | AUDCAD# | 10,75 | mt5_tester | 3,75 | 15,47 | 4,00 | 5,00 | 4,00 | 10,55 | 61,88 | MT5 phát lại deal×k (DD equity XẤP XỈ) | real tick 25.0% |
| od_v2r2p_bg80_brainxlmrz_XM_KIEM_XM_CSV | AUDCAD# | 10,75 | mt5_tester | 6,34 | 19,00 | 2,00 | 4,00 | 2,00 | 10,31 | 38,00 | MT5 phát lại deal×k (DD equity XẤP XỈ) | real tick 25.0% |
| od_v2r2p_hs120_brainxlmrz_XM_KIEM_XM_CSV | AUDCAD# | 10,75 | mt5_tester | 5,53 | 19,79 | 2,50 | 4,00 | 2,50 | 10,62 | 49,47 | MT5 phát lại deal×k (DD equity XẤP XỈ) | real tick 25.0% |
| od_v2r2p_hs120_brainxlrsi_XM_KIEM_XM_CSV | AUDCAD# | 10,75 | mt5_tester | 6,07 | 17,47 | 2,50 | 4,00 | 2,50 | 11,47 | 43,67 | MT5 phát lại deal×k (DD equity XẤP XỈ) | real tick 25.0% |
| od_v2r2p_hs80_brainxlmrz_XM_KIEM_XM_CSV | AUDCAD# | 10,75 | mt5_tester | 5,53 | 19,79 | 2,50 | 4,00 | 2,50 | 10,62 | 49,47 | MT5 phát lại deal×k (DD equity XẤP XỈ) | real tick 25.0% |
| od_v2r2p_b120_mql5344ed0d8ab12c7f0_XM_CSV | NZDUSD# | 8,76 | mt5_tester | 3,52 | 5,32 | 4,00 | 15,00 | 4,00 | 10,60 | 21,28 | MT5 phát lại deal×k (DD equity XẤP XỈ) | real tick 31.0% |
| od_v2r2p_hs120_mql5344ed0d8ab12c7f0_XM_CSV | NZDUSD# | 8,76 | mt5_tester | 4,25 | 7,40 | 3,00 | 10,00 | 3,00 | 10,08 | 22,20 | MT5 phát lại deal×k (DD equity XẤP XỈ) | real tick 31.0% |
| od_v2r2p_mxp1_mql5344ed0d8ab12c7f0_XM_CSV | NZDUSD# | 8,76 | mt5_tester | 3,13 | 12,05 | 5,00 | 6,00 | 5,00 | 11,28 | 60,25 | MT5 phát lại deal×k (DD equity XẤP XỈ) | real tick 31.0% |
| od_v2relot_mql5344ed0d8ab12c7f0_XM_CSV | NZDUSD# | 8,74 | mt5_tester | 3,53 | 5,32 | 4,00 | 15,00 | 4,00 | 10,62 | 21,28 | MT5 phát lại deal×k (DD equity XẤP XỈ) | real tick 31.0% |
| od_v2relot_v2r2oos_dai19_mql5344ed0d8ab12c7f0_XM_CSV | NZDUSD# | 8,74 | mt5_tester | 3,53 | 5,32 | 4,00 | 15,00 | 4,00 | 10,62 | 21,28 | MT5 phát lại deal×k (DD equity XẤP XỈ) | real tick 31.0% |
| od_v2relot_v2r2p_b120_mql5344ed0d8ab12c7f0_XM_CSV | NZDUSD# | 8,74 | mt5_tester | 3,53 | 5,32 | 4,00 | 15,00 | 4,00 | 10,62 | 21,28 | MT5 phát lại deal×k (DD equity XẤP XỈ) | real tick 31.0% |
| od_v2r2p_b120_skea135e93ee32_XM_CSV | EURUSD# | 2,77 | mt5_real_tick | 1,96 | 2,18 | 6,00 | 30,00 | 6,00 | 10,88 | 13,08 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_b120_skea3279057100_XM_CSV | EURGBP# | 2,77 | mt5_real_tick | 8,99 | 20,09 | 1,25 | 3,50 | 1,25 | 11,05 | 25,11 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_b120_skeadd170ac7bf_XM_CSV | USDCAD# | 2,77 | mt5_real_tick | 6,63 | 8,60 | 1,75 | 8,00 | 1,75 | 11,16 | 15,05 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_b50_skea135e93ee32_XM_CSV | EURUSD# | 2,77 | mt5_real_tick | 2,67 | 4,27 | 4,00 | 15,00 | 4,00 | 10,03 | 17,08 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_b50_skea78384bbaf7_XM_CSV | USDCAD# | 2,77 | mt5_real_tick | 9,64 | 36,53 | 1,25 | 2,00 | 1,25 | 11,83 | 45,66 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_b80_skea3279057100_XM_CSV | EURGBP# | 2,77 | mt5_real_tick | 8,79 | 16,16 | 1,25 | 4,00 | 1,25 | 10,80 | 20,20 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_hs120_skea135e93ee32_XM_CSV | EURUSD# | 2,77 | mt5_real_tick | 2,07 | 2,49 | 6,00 | 30,00 | 6,00 | 11,43 | 14,94 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_b120_2600ea39abbd7b0f_XM_CSV | GBPNZD# | 2,76 | mt5_real_tick | 4,64 | 2,74 | 2,50 | 25,00 | 2,50 | 10,98 | 6,85 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_b120_skeaeee96c8430_XM_CSV | EURGBP# | 2,76 | mt5_real_tick | 2,86 | 4,37 | 4,00 | 15,00 | 4,00 | 10,70 | 17,48 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_b50_skeaeee96c8430_XM_CSV | EURGBP# | 2,76 | mt5_real_tick | 3,58 | 4,09 | 3,00 | 15,00 | 3,00 | 10,14 | 14,29 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_b80_skeaeee96c8430_XM_CSV | EURGBP# | 2,76 | mt5_real_tick | 3,57 | 4,99 | 3,00 | 15,00 | 3,00 | 10,13 | 14,97 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| DichNguoc:UV1_luoi_hedge_tp35_(2330430):lot0.0005/1000 | GBPUSD | 2,75 | mo_phong_python | 7,19 | 9,73 | 1,50 | 8,00 | 1,50 | 10,47 | 14,60 | XẤP XỈ tuyến tính | MÔ PHỎNG |
| od_v2lotscale_lotx1_full_ghep60ff9350c26c63ee_XM_CSV | GBPCAD# | 2,75 | mt5_real_tick | 1,34 | 1,90 | 10,00 | 40,00 | 10,00 | 12,21 | 19,00 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2lotscale_lotx1_full_mql5344ed0d8ab12c7f0_XM_CSV | NZDUSD# | 2,75 | mt5_real_tick | 2,18 | 6,76 | 5,00 | 10,00 | 5,00 | 10,19 | 33,80 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2lotscale_lotx1p5_full_ghep60ff9350c26c63ee_XM_CSV | GBPCAD# | 2,75 | mt5_real_tick | 1,78 | 2,51 | 8,00 | 30,00 | 8,00 | 12,94 | 20,08 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2lotscale_lotx1p5_full_mql5344ed0d8ab12c7f0_XM_CSV | NZDUSD# | 2,75 | mt5_real_tick | 2,98 | 9,65 | 4,00 | 8,00 | 4,00 | 11,11 | 38,60 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2lotscale_lotx2_full_ghep60ff9350c26c63ee_XM_CSV | GBPCAD# | 2,75 | mt5_real_tick | 2,65 | 3,67 | 5,00 | 20,00 | 5,00 | 12,21 | 18,35 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2lotscale_lotx2_full_mql5344ed0d8ab12c7f0_XM_CSV | NZDUSD# | 2,75 | mt5_real_tick | 4,35 | 13,24 | 2,50 | 6,00 | 2,50 | 10,34 | 33,10 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2lotscale_lotx3_full_ghep60ff9350c26c63ee_XM_CSV | GBPCAD# | 2,75 | mt5_real_tick | 3,93 | 5,32 | 3,00 | 15,00 | 3,00 | 11,09 | 15,96 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2lotscale_lotx3_full_mql5344ed0d8ab12c7f0_XM_CSV | NZDUSD# | 2,75 | mt5_real_tick | 6,45 | 18,52 | 1,75 | 4,00 | 1,75 | 10,88 | 32,41 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2lotscale_lotx4_full_ghep60ff9350c26c63ee_XM_CSV | GBPCAD# | 2,75 | mt5_real_tick | 5,18 | 6,86 | 2,50 | 10,00 | 2,50 | 12,21 | 17,15 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2lotscale_lotx4_full_mql5344ed0d8ab12c7f0_XM_CSV | NZDUSD# | 2,75 | mt5_real_tick | 8,51 | 23,37 | 1,25 | 3,00 | 1,25 | 10,47 | 29,21 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2verify_lot01_fixed_ghep60ff9350c26c63ee_XM_CSV | GBPCAD# | 2,75 | mt5_real_tick | 1,31 | 1,91 | 10,00 | 40,00 | 10,00 | 11,97 | 19,10 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2verify_lot01_full_ghep60ff9350c26c63ee_XM_CSV | GBPCAD# | 2,75 | mt5_real_tick | 8,65 | 5,57 | 1,25 | 12,00 | 1,25 | 10,63 | 6,96 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_b50_skea61c21a2049_XM_CSV | CADJPY# | 2,74 | mt5_real_tick | 7,82 | 15,21 | 1,50 | 5,00 | 1,50 | 11,39 | 22,82 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_b80_skea61c21a2049_XM_CSV | CADJPY# | 2,74 | mt5_real_tick | 4,94 | 6,93 | 2,50 | 10,00 | 2,50 | 11,67 | 17,32 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_hs120_skea61c21a2049_XM_CSV | CADJPY# | 2,74 | mt5_real_tick | 4,98 | 6,65 | 2,50 | 12,00 | 2,50 | 11,76 | 16,62 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_hs80_skea61c21a2049_XM_CSV | CADJPY# | 2,74 | mt5_real_tick | 3,47 | 4,77 | 3,50 | 15,00 | 3,50 | 11,35 | 16,70 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_mxm1_skea61c21a2049_XM_CSV | CADJPY# | 2,74 | mt5_real_tick | 3,97 | 3,59 | 3,00 | 20,00 | 3,00 | 11,21 | 10,77 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_mxp1_skea61c21a2049_XM_CSV | CADJPY# | 2,74 | mt5_real_tick | 4,08 | 4,33 | 3,00 | 15,00 | 3,00 | 11,50 | 12,99 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_tp120_skea61c21a2049_XM_CSV | CADJPY# | 2,74 | mt5_real_tick | 5,11 | 5,05 | 2,50 | 15,00 | 2,50 | 12,05 | 12,62 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2lotfix_full_mql5e52afb999eca4bd1_XM_CSV | EURGBP# | 2,74 | mt5_real_tick | 3,21 | 2,97 | 3,50 | 25,00 | 3,50 | 10,55 | 10,40 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2relot_v2r2xt_realtick_2600ea39abbd7b0f_XM_CSV | GBPNZD# | 2,74 | mt5_real_tick | 5,16 | 3,11 | 2,50 | 25,00 | 2,50 | 12,15 | 7,77 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2lotscale_lotx1_full_skea61c21a2049_XM_CSV | CADJPY# | 2,72 | mt5_real_tick | 3,46 | 3,05 | 3,50 | 25,00 | 3,50 | 11,34 | 10,67 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2lotscale_lotx1p5_full_skea61c21a2049_XM_CSV | CADJPY# | 2,72 | mt5_real_tick | 4,91 | 4,62 | 2,50 | 15,00 | 2,50 | 11,61 | 11,55 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2lotscale_lotx2_full_skea61c21a2049_XM_CSV | CADJPY# | 2,72 | mt5_real_tick | 6,90 | 5,99 | 1,50 | 12,00 | 1,50 | 10,08 | 8,98 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2relot_v2r2oos_dai19_skea61c21a2049_XM_CSV | CADJPY# | 2,72 | mt5_real_tick | 4,11 | 4,33 | 3,00 | 15,00 | 3,00 | 11,58 | 12,99 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2relot_v2r2p_b120_skea61c21a2049_XM_CSV | CADJPY# | 2,72 | mt5_real_tick | 3,46 | 3,05 | 3,50 | 25,00 | 3,50 | 11,34 | 10,67 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_b50_b0be91a35f43f34a_XM_CSV | USDCAD# | 2,71 | mt5_real_tick | 5,07 | 11,32 | 2,50 | 6,00 | 2,50 | 11,97 | 28,30 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2p_b80_b0be91a35f43f34a_XM_CSV | USDCAD# | 2,71 | mt5_real_tick | 5,07 | 11,32 | 2,50 | 6,00 | 2,50 | 11,97 | 28,30 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2r2oos_dai19_skea154c9fdee7_XM_CSV | GBPCAD# | 2,71 | mt5_real_tick | 5,50 | 7,37 | 2,00 | 10,00 | 2,00 | 10,56 | 14,74 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2relot_v2r2p_b120_skea135e93ee32_XM_CSV | EURUSD# | 2,62 | mt5_real_tick | 2,03 | 2,18 | 6,00 | 30,00 | 6,00 | 11,30 | 13,08 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2relot_v2r2xt_realtick_skea135e93ee32_XM_CSV | EURUSD# | 2,62 | mt5_real_tick | 2,14 | 2,49 | 5,00 | 30,00 | 5,00 | 10,05 | 12,45 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2relot_v2r2oos_dai19_b0be91a35f43f34a_XM_CSV | USDCAD# | 2,62 | mt5_real_tick | 4,28 | 11,32 | 2,50 | 6,00 | 2,50 | 10,22 | 28,30 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2relot_v2r2xt_realtick_b0be91a35f43f34a_XM_CSV | USDCAD# | 2,62 | mt5_real_tick | 4,28 | 11,32 | 2,50 | 6,00 | 2,50 | 10,22 | 28,30 | MT5 phát lại deal×k (DD equity XẤP XỈ) |  |
| od_v2lotfix_y2025_mql5e52afb999eca4bd1_XM_CSV | EURGBP# | 1,75 | mt5_real_tick | 3,53 | 3,05 | 3,00 | 25,00 | 3,00 | 10,34 | 9,15 | MT5 phát lại deal×k (DD equity XẤP XỈ) | quá ngắn |
| od_v2verify_lot01_y2025_ghep0bf2c31fbfc9dea0_XM_CSV | GBPCAD# | 1,75 | mt5_real_tick | 7,19 | 17,21 | 1,50 | 4,00 | 1,50 | 10,65 | 25,82 | MT5 phát lại deal×k (DD equity XẤP XỈ) | quá ngắn |
| od_v2verify_lot01_y2025_ghep60ff9350c26c63ee_XM_CSV | GBPCAD# | 1,75 | mt5_real_tick | 0,92 | 1,94 | 12,00 | 40,00 | 12,00 | 10,69 | 23,28 | MT5 phát lại deal×k (DD equity XẤP XỈ) | quá ngắn |
| od_v2verify_lot01_y2024_ghep60ff9350c26c63ee_XM_CSV | GBPCAD# | 1,00 | mt5_real_tick | 2,24 | 1,41 | 5,00 | 50,00 | 5,00 | 11,20 | 7,05 | MT5 phát lại deal×k (DD equity XẤP XỈ) | quá ngắn |
| od_v2lotfix_y2024_mql5e52afb999eca4bd1_XM_CSV | EURGBP# | 0,99 | mt5_real_tick | 0,86 | 2,16 | 12,00 | 30,00 | 12,00 | 10,27 | 25,92 | MT5 phát lại deal×k (DD equity XẤP XỈ) | quá ngắn |
| od_v2verify_lot01_oos_h1_ghep60ff9350c26c63ee_XM_CSV | GBPCAD# | 0,50 | mt5_real_tick | 1,74 | 0,99 | 6,00 | 50,00 | 6,00 | 10,68 | 5,94 | MT5 phát lại deal×k (DD equity XẤP XỈ) | quá ngắn |

## Không có k nào đạt

| Hệ | Mã | Năm | CAGR gốc % | DD gốc % | k nhỏ nhất CAGR>10 | k lớn nhất DD<80 | Cách đo |
|---|---|---|---|---|---|---|---|
| DichNguoc:UV1:swap_0_lac_quan:lot0.00025/1000 | AUDNZD | 18,77 | 2,15 | 13,17 | 5,00 | 4,00 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV1:swap_0_lac_quan:lot0.00025/1000 | EURCHF | 18,77 | -3,36 | 68,10 | — | 1,25 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV1:swap_0_lac_quan:lot0.0005/1000 | AUDNZD | 18,77 | 4,10 | 29,66 | 2,50 | 2,00 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV1:swap_0_lac_quan:lot0.001/1000 | AUDNZD | 18,77 | 8,21 | 64,88 | 1,25 | 1,00 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV1:swap_bao_thu:lot0.00025/1000 | AUDCAD | 18,77 | -1,83 | 38,62 | — | 2,00 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV1:swap_bao_thu:lot0.00025/1000 | AUDNZD | 18,77 | -4,87 | 69,28 | — | 1,00 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV1:swap_bao_thu:lot0.00025/1000 | EURGBP | 18,77 | -0,78 | 26,78 | — | 2,50 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV1:swap_bao_thu:lot0.0005/1000 | AUDCAD | 18,77 | -5,60 | 74,53 | — | 1,00 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV1:swap_bao_thu:lot0.0005/1000 | EURGBP | 18,77 | -1,83 | 55,52 | — | 1,25 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV1:swap_do:lot0.00025/1000 | AUDCAD | 18,77 | 1,06 | 15,71 | 5,00 | 4,00 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV1:swap_do:lot0.00025/1000 | AUDNZD | 18,77 | -0,01 | 18,05 | — | 3,50 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV1:swap_do:lot0.00025/1000 | EURGBP | 18,77 | 1,87 | 20,80 | 4,00 | 3,00 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV1:swap_do:lot0.0005/1000 | AUDCAD | 18,77 | 2,82 | 33,20 | 2,50 | 2,00 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV1:swap_do:lot0.0005/1000 | AUDNZD | 18,77 | -0,33 | 38,51 | — | 1,75 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV1:swap_do:lot0.0005/1000 | EURGBP | 18,77 | 4,21 | 45,30 | 2,00 | 1,50 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV1:swap_do:lot0.001/1000 | AUDCAD | 18,77 | 7,27 | 65,87 | 1,25 | 1,00 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV2:swap_0_lac_quan:lot0.00025/1000 | AUDCAD | 18,77 | 3,74 | 43,04 | — | 1,75 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV2:swap_0_lac_quan:lot0.00025/1000 | AUDNZD | 18,77 | 2,63 | 25,12 | 4,00 | 3,00 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV2:swap_0_lac_quan:lot0.00025/1000 | EURCHF | 18,77 | 4,74 | 57,49 | — | 1,25 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV2:swap_0_lac_quan:lot0.0005/1000 | AUDNZD | 18,77 | 5,26 | 45,39 | 2,00 | 1,50 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV2:swap_bao_thu:lot0.00025/1000 | AUDCAD | 18,77 | 1,05 | 44,42 | — | 1,75 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV2:swap_bao_thu:lot0.00025/1000 | AUDNZD | 18,77 | -0,58 | 35,53 | — | 2,00 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV2:swap_bao_thu:lot0.00025/1000 | EURCHF | 18,77 | -2,50 | 55,98 | — | 1,50 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV2:swap_bao_thu:lot0.00025/1000 | EURGBP | 18,77 | 2,87 | 34,45 | — | 3,00 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV2:swap_bao_thu:lot0.0005/1000 | AUDNZD | 18,77 | -1,35 | 76,23 | — | 1,00 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV2:swap_bao_thu:lot0.0005/1000 | EURGBP | 18,77 | 5,74 | 58,63 | — | 1,50 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV2:swap_do:lot0.00025/1000 | AUDCAD | 18,77 | 2,50 | 42,77 | — | 1,75 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV2:swap_do:lot0.00025/1000 | AUDNZD | 18,77 | 0,99 | 22,24 | — | 3,00 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV2:swap_do:lot0.00025/1000 | EURCHF | 18,77 | 1,74 | 53,02 | — | 1,50 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV2:swap_do:lot0.00025/1000 | EURGBP | 18,77 | 3,74 | 33,37 | 3,00 | 2,50 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV2:swap_do:lot0.0005/1000 | AUDNZD | 18,77 | 2,05 | 50,63 | — | 1,50 | MÔ PHỎNG chạy lại lot×k |
| DichNguoc:UV2:swap_do:lot0.0005/1000 | EURGBP | 18,77 | 7,48 | 63,75 | 1,50 | 1,25 | MÔ PHỎNG chạy lại lot×k |
| Telegram:CLMCA_C_V1_M15:swap_0_lac_quan | XAUUSD | 17,57 | 5,07 | 73,07 | — | 1,00 | MÔ PHỎNG chạy lại lot×k |
| Telegram:EA4_MACD_200EMA_H4:swap_bao_thu | XAUUSD | 17,57 | 2,30 | 30,32 | — | 4,00 | MÔ PHỎNG chạy lại lot×k |
| Telegram:EA5_Stoch_Pivot_M15:swap_0_lac_quan | XAUUSD | 17,57 | -0,03 | 2,03 | — | 50,00 | MÔ PHỎNG chạy lại lot×k |
| Telegram:EA5_Stoch_Pivot_M15:swap_bao_thu | XAUUSD | 17,57 | -0,03 | 2,03 | — | 50,00 | MÔ PHỎNG chạy lại lot×k |
| Telegram:EA5_Stoch_Pivot_M15:swap_do_XM | XAUUSD | 17,57 | -0,03 | 2,03 | — | 50,00 | MÔ PHỎNG chạy lại lot×k |
| mql5344 (dai han x1) | NZDUSD | — | 3,50 | 5,30 | — | — | THIẾU SỐ |
| mql5344 lot x4 cua so ngan | NZDUSD | — | 8,50 | 23,40 | — | — | THIẾU SỐ |
| od_v2r2p_b120_skea78384bbaf7_XM_CSV | USDCAD# | 2,77 | 5,12 | 44,89 | — | 1,75 | MT5 phát lại deal×k (DD equity XẤP XỈ) |
| od_v2r2p_b50_mql5344ed0d8ab12c7f0_XM_CSV | NZDUSD# | 8,76 | 0,71 | 21,57 | — | 3,50 | MT5 phát lại deal×k (DD equity XẤP XỈ) |
| od_v2r2p_b80_mql5344ed0d8ab12c7f0_XM_CSV | NZDUSD# | 8,76 | -0,36 | 21,70 | — | 3,50 | MT5 phát lại deal×k (DD equity XẤP XỈ) |
| od_v2r2p_bg80_brainxlrsi_XM_KIEM_XM_CSV | AUDCAD# | 10,75 | 4,51 | 52,41 | — | 1,50 | MT5 phát lại deal×k (DD equity XẤP XỈ) |
| od_v2r2p_hs80_mql5344ed0d8ab12c7f0_XM_CSV | NZDUSD# | 8,76 | -0,07 | 15,46 | — | 5,00 | MT5 phát lại deal×k (DD equity XẤP XỈ) |
| od_v2r2p_mxm1_mql5344ed0d8ab12c7f0_XM_CSV | NZDUSD# | 8,76 | 0,24 | 7,51 | — | 10,00 | MT5 phát lại deal×k (DD equity XẤP XỈ) |
| od_v2r2p_tp120_mql5344ed0d8ab12c7f0_XM_CSV | NZDUSD# | 8,76 | 3,21 | 22,47 | — | 3,50 | MT5 phát lại deal×k (DD equity XẤP XỈ) |
