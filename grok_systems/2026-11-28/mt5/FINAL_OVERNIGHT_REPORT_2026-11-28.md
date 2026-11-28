# BÁO CÁO MT5 TICK THẬT QUA ĐÊM — 28/11/2026 (giờ VN)

Toàn bộ là **số đo MT5 Strategy Tester, Model 4 = mọi tick thật, History Quality 100% real ticks**, đòn bẩy 1:500, không đặt lệnh thật. Slot `E:\mt5_tester\p6` (US500Cash#), `E:\mt5_tester\p4` (GOLD.i#). DD = Equity Drawdown Maximal (gồm lỗ thả nổi). Tổng **57 lượt**. Chi tiết 49 lượt trước: `SUMMARY_2026-11-28.md`. Bảng máy: `TONG_HOP_MT5_20261128.csv/.json`. Báo cáo htm: `reports\<config>.htm`.

## Lượt cuối: kiểm chứng ứng viên v2 (02:34–02:40)
EA `BRAIN_XuLiLenh` chế độ VAO_CSV (lệnh vào từ `mt5_ready_v2`, giờ server XM), M1, 2026.08.20–2026.11.27. EA **không có prune**; hedge xấp xỉ bằng ngưỡng lỗ % số dư (quy từ hgap giá). Vàng chạy bằng bản chép `p4\MQL5\Experts\BRAIN\BRAIN_XuLiLenh_v2711.ex5` (bản 27/11 có VAO_CSV; không ghi đè bản cũ).

### SP500
| Config | Mô tả | Kỳ | Vốn | Lãi ròng | DD equity max | DD $ | Lệnh | PF | Lãi & DD<80% | Python |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| v2_us_c1_hedge | US500 v2_c1 2 lot gap60x1.4 max3 TP6, hedge 0.5x khi lo 2.4% (~90 gia) | 2026.08.20–2026.11.27 M1 | 10000 | +1591.44 | 3.74% | 378.96 | 159 | 2.9 | ĐẠT | +1.677,64 / DD 3,86% |
| v2_us_c1_nohedge | US500 v2_c1 khong hedge | 2026.08.20–2026.11.27 M1 | 10000 | +1738.22 | 3.77% | 382.94 | 141 | 3.4 | ĐẠT |  |
| v2_us_c3_hedge | US500 v2_c3 1 lot gap45x1.4 max3 TP6, hedge 0.5x khi lo 3.87% (~180 gia), khong prune | 2026.08.20–2026.11.27 M1 | 10000 | +923.05 | 1.76% | 176.54 | 151 | 4.33 | ĐẠT | +899,91 / DD 1,79% |
| v2_us_c3_nohedge | US500 v2_c3 khong hedge | 2026.08.20–2026.11.27 M1 | 10000 | +923.05 | 1.76% | 176.54 | 151 | 4.33 | ĐẠT |  |

### Vàng
| Config | Mô tả | Kỳ | Vốn | Lãi ròng | DD equity max | DD $ | Lệnh | PF | Lãi & DD<80% | Python |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| v2_xau_c3_30k | XAU v2_c3 0.03x1.3 gap6x1.4 max4 TP3, hedge 0.5x khi lo 0.36% (~18 gia), khong prune | 2026.08.20–2026.11.27 M1 | 30000 | +2580.60 | 2.23% | 713.33 | 351 | 2.9 | ĐẠT | +3.160,06 / DD 2,21% (có prune); không prune +2.804 |
| v2_xau_c3_10k | XAU v2_c3 10k, hedge khi lo 1.08% (~18 gia) | 2026.08.20–2026.11.27 M1 | 10000 | +2593.20 | 6.02% | 720.35 | 347 | 2.97 | ĐẠT |  |
| v2_xau_c1_30k | XAU v2_c1 0.03 gap6x1.4 max4 TP3 khong hedge | 2026.08.20–2026.11.27 M1 | 30000 | +4924.44 | 6.24% | 2089.2 | 542 | 5.52 | ĐẠT | +4.900,23 / DD 6,91% (trên 30k) |
| v2_xau_c1_10k | XAU v2_c1 10k | 2026.08.20–2026.11.27 M1 | 10000 | +4924.44 | 15.47% | 2089.2 | 542 | 5.52 | ĐẠT |  |

Ghi chú: v2_us_c3 hedge trùng không hedge (hedge không kích hoạt). v2_us_c1 hedge kích hoạt: lãi giảm 1.738,22 → 1.591,44, DD gần như không đổi. Vàng 10k và 30k cùng giao dịch (cùng lãi), chỉ khác mẫu số DD; v2_xau_c3 10k khác 30k chút vì ngưỡng hedge % khác.

## Bảng tổng hợp tốt nhất đêm nay

### SP500
| Config | Mô tả | Kỳ | Vốn | Lãi ròng | DD equity max | DD $ | Lệnh | PF | Lãi & DD<80% | Python |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| x_long_dca_L050_lin | ro MUA lot 0.5 tang tuyen tinh | 2025.07.21–2026.11.27 H1 | 10000 | +8320.60 | 28.57% | 6352.29 | 1044 | 1.93 | ĐẠT |  |
| s_tayv2_h1_L050 | tay_v2 US500 L0 0.50 hedge 1x | 2025.07.21–2026.11.27 M1 | 10000 | +2395.68 | 26.38% | 3084.51 | 8223 | 4.33 | ĐẠT |  |
| s_tayv2_h1_L030 | tay_v2 US500 L0 0.30 hedge 1x | 2025.07.21–2026.11.27 M1 | 10000 | +1442.45 | 16.82% | 1853.65 | 8198 | 4.37 | ĐẠT |  |
| v_c5 | US500 c5 CSV, DCA 6 x2 lot max3, TP 6, khong hedge, khong prune | 2026.08.20–2026.11.27 M1 | 10000 | +2596.67 | 10.43% | 1098.19 | 248 | 18.21 | ĐẠT |  |
| v2_us_c1_nohedge | US500 v2_c1 khong hedge | 2026.08.20–2026.11.27 M1 | 10000 | +1738.22 | 3.77% | 382.94 | 141 | 3.4 | ĐẠT |  |
| v2_us_c1_hedge | US500 v2_c1 2 lot gap60x1.4 max3 TP6, hedge 0.5x khi lo 2.4% (~90 gia) | 2026.08.20–2026.11.27 M1 | 10000 | +1591.44 | 3.74% | 378.96 | 159 | 2.9 | ĐẠT |  |
| v2_us_c3_hedge | US500 v2_c3 1 lot gap45x1.4 max3 TP6, hedge 0.5x khi lo 3.87% (~180 gia), khong prune | 2026.08.20–2026.11.27 M1 | 10000 | +923.05 | 1.76% | 176.54 | 151 | 4.33 | ĐẠT |  |
| v_c1_nohedge | US500 c1 CSV, DCA 45x1.4 max3, TP ro 6, khong hedge, khong prune | 2026.08.20–2026.11.27 M1 | 10000 | +861.49 | 1.76% | 176.54 | 142 | 5.69 | ĐẠT |  |

### Vàng (mốc HedgeEMA H1 lot 0,08 10k, 2025.09.01–2026.11.27: +13.416,76 / DD 45,09% / 525 lệnh / PF 1,12)
| Config | Mô tả | Kỳ | Vốn | Lãi ròng | DD equity max | DD $ | Lệnh | PF | Lãi & DD<80% | Python |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| g_hema_h1_30k_L024 | HedgeEMA H1 30k lot 0.24 | 2025.09.01–2026.11.27 H1 | 30000 | +40250.28 | 45.09% | 15318.6 | 525 | 1.12 | ĐẠT |  |
| g_htay_lc10_L014 | HedgeTay lc10 mlc1 lotgoc 0.14 | 2025.09.01–2026.11.27 M1 | 10000 | +24152.41 | 68.79% | 8935.85 | 16013 | 1.12 | ĐẠT |  |
| g_hema_h1_L014 | HedgeEMA H1 lot 0.14 | 2025.09.01–2026.11.27 H1 | 10000 | +23479.33 | 72.55% | 8935.85 | 525 | 1.12 | ĐẠT |  |
| g_htay_gong_L016 | HedgeTay gong 10k lotgoc 0.16 | 2025.09.01–2026.11.27 M1 | 10000 | +23430.75 | 65.99% | 8603.07 | 31380 | 1.1 | ĐẠT |  |
| g_htay_lc10_L012_tay002 | HedgeTay lc10 lotgoc 0.12 tay L0 0.02 | 2025.09.01–2026.11.27 M1 | 10000 | +21155.46 | 58.84% | 7659.3 | 12046 | 1.12 | ĐẠT |  |
| g_htay_gong_10k | HedgeTay gong (khong dong lo tong) 10k | 2025.09.01–2026.11.27 M1 | 10000 | +10013.99 | 22.03% | 5417.51 | 31380 | 1.08 | ĐẠT |  |
| v2_xau_c1_30k | XAU v2_c1 0.03 gap6x1.4 max4 TP3 khong hedge | 2026.08.20–2026.11.27 M1 | 30000 | +4924.44 | 6.24% | 2089.2 | 542 | 5.52 | ĐẠT |  |
| v2_xau_c1_10k | XAU v2_c1 10k | 2026.08.20–2026.11.27 M1 | 10000 | +4924.44 | 15.47% | 2089.2 | 542 | 5.52 | ĐẠT |  |
| v2_xau_c3_30k | XAU v2_c3 0.03x1.3 gap6x1.4 max4 TP3, hedge 0.5x khi lo 0.36% (~18 gia), khong prune | 2026.08.20–2026.11.27 M1 | 30000 | +2580.60 | 2.23% | 713.33 | 351 | 2.9 | ĐẠT |  |
| v2_xau_c3_10k | XAU v2_c3 10k, hedge khi lo 1.08% (~18 gia) | 2026.08.20–2026.11.27 M1 | 10000 | +2593.20 | 6.02% | 720.35 | 347 | 2.97 | ĐẠT |  |

Lưu ý: cửa sổ 3 tháng (2026.08.20–11.27) và 15–16 tháng không so trực tiếp được lãi tuyệt đối. Kết quả v2 đều là lệnh vào chọn trên chính cửa sổ này (in-sample).
