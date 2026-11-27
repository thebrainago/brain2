# tay_v2 — ngữ cảnh lệnh tay và kiểm 7 bước

Xuất: 2026-11-27 20:36:41.625314+07:00 (giờ Việt Nam, UTC+7).

## 0. Lưu ý quan trọng về “cạnh <5 phút”

Lãi vàng giữ <5 phút (+40.950, WR 97,4%) **tập trung rất mạnh**: 38.523 đến từ 25/11/2026 với lot 1,00 sau khi nạp thêm 900.000 demo. Ba ngày 20, 21, 25/11 chiếm 98,7% lãi vàng. Trừ 25/11, lệnh <5 phút chỉ còn +2.427 (61 lệnh, WR 100%). Lệnh lot ≤ 0,10 và giữ <5 phút: n=155, **tất cả lãi**, +5.260,5, khe TP trung vị **4,00 USD**, giữ trung vị 1,40 phút — đây là số dùng để khớp máy (không lấy 3,12 vì đó là hòa trộn với lot 1,00, TP trung vị 1,59).

Khe DCA 5,47 / 14,5 phút và hedge 21,37 vẫn lấy từ toàn bộ lịch sử (thêm cùng chiều sau >2 giây / vào ngược).

## 1. Ngữ cảnh vào lệnh (vàng, gắn nến M1 + chỉ báo + Fxaurum)

| nhom | n | pnl | wr | S_cung | S_med | usopen | us | rej_thuan | bb_2sig | data_cung | data_nguoc | data_khac0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tat_ca | 866 | 60702.65 | 90.5 | 23.2 | 0.0 | 23.9 | 67.7 | 5.4 | 4.7 | 12.0 | 10.4 | 22.4 |
| thang | 784 | 91819.75 | 100.0 | 24.1 | 0.0 | 19.8 | 66.2 | 5.9 | 4.3 | 11.4 | 10.6 | 21.9 |
| thua | 82 | -31117.1 | 0.0 | 14.6 | 0.0 | 63.4 | 81.7 | 1.2 | 8.5 | 18.3 | 8.5 | 26.8 |
| nhanh_lai | 301 | 41084.54 | 100.0 | 14.6 | 0.0 | 22.9 | 84.4 | 1.7 | 3.0 | 5.3 | 1.0 | 6.3 |
| 30p_4h | 272 | -14929.93 | 80.5 | 36.0 | 0.0 | 38.6 | 55.5 | 9.9 | 4.0 | 17.6 | 15.8 | 33.5 |
| lot_le_0.1 | 641 | 33159.16 | 90.3 | 29.8 | 0.0 | 29.0 | 56.6 | 7.3 | 6.4 | 16.1 | 13.9 | 30.0 |
| lot_le_0.1_nhanh | 155 | 5260.54 | 100.0 | 28.4 | 0.0 | 44.5 | 69.7 | 3.2 | 5.8 | 10.3 | 1.9 | 12.3 |
| tru_25-11 | 469 | 35147.6 | 93.2 | 22.4 | 0.0 | 8.5 | 40.7 | 10.0 | 7.5 | 22.0 | 19.0 | 40.9 |
| my_20-07 | 619 | 47996.05 | 89.0 | 29.6 | 0.0 | 33.4 | 94.7 | 5.7 | 5.7 | 5.2 | 1.9 | 7.1 |
| london_14-20 | 196 | 11938.6 | 94.4 | 6.1 | 0.0 | 0.0 | 0.0 | 3.1 | 3.1 | 30.1 | 33.7 | 63.8 |

- Tỷ lệ vị thế vàng có điểm S cùng chiều ≥ 1: 23.2%. Nhóm nhanh-lãi: 14.6%.
- Nếu tỷ lệ S cùng chiều thấp: Anh vào tay theo quan sát, không đợi đủ điều kiện chỉ báo; máy dùng S≥1 sẽ **bỏ lỡ** nhiều lệnh của Anh, nhưng đó là bộ lọc 'tín hiệu' theo yêu cầu.

## 2. Máy tay_v2

- Vào cụm K lệnh lot cố định khi S (mua) hoặc S_short (bán) ≥ 1, phiên London+Mỹ (14h–07h VN) mặc định.
- TP từng lệnh theo khe giá đã khớp (vàng 4,00; US500 6,53 từ lot ≤0,10 giữ <5 phút lãi).
- DCA lot cố định (hệ số 1,0) mỗi khi giá đi ngược đúng khe (5,47 / 8,32).
- Hedge cụm 5×0,10 khi rổ đi ngược khe hedge (21,37 / 80).
- Đóng cả rổ khi lãi tổng (sau spread) > 0. Không SL cứng.
- Nến M1, trong nến **thận trọng** (nhánh bất lợi/DCA/hedge trước, TP sau). Không có tick XM trên box.
- Vốn 10.000 USD = 1.000.000 USC. Tiêu chí: lãi > 0, DD < 80%, không cháy.
- IS trước 2026-10-01, OOS từ 2026-10-01. Tham số khớp từ lịch sử deal (chủ yếu tháng 11, nằm trong OOS) — có rò thông tin hành vi, không phải tối ưu IS thuần.

## 3. Kết quả XAU

- M1 XM 2026-06-01 05:00:00 → 2026-11-26 19:04:00, 176632 nến, tín hiệu 58303. IS 120056, OOS 56176.

| ten | net | maxdd | dd_pct | maxfl | is_net | oos_net | net_sprx2 | dd_sprx2 | sharpe | dsr | n_en | n_tp | n_dca | n_hd | n_ro | max_tix | maxlots | blown | dat | dat_sprx2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tay_v2 | 98412.18 | 45386.14 | 453.86 | -46977.7 | 62491.61 | 35920.57 | -10007.58 | 31040.24 | 2.267 | 1.0 | 2115 | 6614 | 2392 | 947 | 2115 | 30 | 3.0 | False | False | False |
| tay_v2_xac_nhan | 110778.0 | 45386.14 | 453.86 | -46977.7 | 62731.41 | 48046.58 | -10007.58 | 31040.24 | 2.571 | 1.0 | 2220 | 7131 | 2544 | 1031 | 2220 | 30 | 3.0 | False | False | False |
| tay_v2_usonly | -10110.05 | 25672.38 | 256.72 | -27094.3 | -10110.05 | 0.0 | -10193.81 | 22908.16 | -0.851 | 0.0 | 215 | 1095 | 320 | 171 | 215 | 30 | 3.0 | True | False | False |
| tay_v2_phien_dip | -11135.05 | 20010.71 | 200.11 | -22397.62 | -11135.05 | 0.0 | 114857.94 | 32967.35 | -1.572 | 0.0 | 203 | 474 | 206 | 65 | 203 | 30 | 3.0 | True | False | False |
| lan_tp312 | 84901.52 | 45614.14 | 456.14 | -46977.7 | 46567.49 | 38334.03 | 84605.17 | 45655.54 | 1.779 | 0.0 | 1861 | 7831 | 2397 | 1091 | 1861 | 30 | 3.0 | False | False | False |
| lan_tp522 | 111869.06 | 45192.34 | 451.92 | -46977.7 | 64392.76 | 47476.31 | 98800.82 | 45336.32 | 2.756 | 1.0 | 2371 | 5498 | 2314 | 850 | 2371 | 30 | 3.0 | False | False | False |
| lan_gap4 | -10056.13 | 17080.83 | 170.81 | -18157.0 | -10056.13 | 0.0 | 88759.15 | 35621.44 | -1.59 | 0.0 | 150 | 382 | 212 | 45 | 150 | 30 | 3.0 | True | False | False |
| lan_gap8 | 132301.56 | 31070.66 | 310.71 | -32194.5 | 94571.7 | 37729.87 | 120672.47 | 22718.77 | 3.333 | 1.0 | 2769 | 6939 | 1975 | 1069 | 2769 | 30 | 3.0 | False | False | False |
| lan_hgap15 | -10033.38 | 15659.12 | 156.59 | -16095.29 | -10033.38 | 0.0 | -10143.55 | 14635.54 | -1.502 | 0.0 | 107 | 330 | 127 | 50 | 107 | 24 | 2.4 | True | False | False |
| lan_hgap30 | 125958.63 | 68481.96 | 684.82 | -69738.0 | 72618.98 | 53339.64 | 110328.56 | 67640.59 | 2.77 | 1.0 | 2343 | 9178 | 3187 | 1268 | 2343 | 30 | 3.0 | False | False | False |
| lan_maxL10 | 111645.4 | 45386.14 | 453.86 | -46977.7 | 67521.25 | 44124.16 | 131850.14 | 35173.53 | 2.65 | 1.0 | 2292 | 5343 | 1912 | 754 | 2292 | 20 | 2.0 | False | False | False |
| lan_maxL40 | 97497.73 | 45386.14 | 453.86 | -46977.7 | 61713.5 | 35784.24 | 99506.93 | 45445.14 | 2.302 | 1.0 | 2111 | 6616 | 2437 | 944 | 2111 | 42 | 4.2 | False | False | False |
| lan_maxL80 | 97497.73 | 45386.14 | 453.86 | -46977.7 | 61713.5 | 35784.24 | 99506.93 | 45445.14 | 2.302 | 1.0 | 2111 | 6616 | 2437 | 944 | 2111 | 42 | 4.2 | False | False | False |
| lan_tp159 | -10055.17 | 29614.49 | 296.14 | -30391.91 | -10055.17 | 0.0 | -10040.23 | 26245.93 | -0.337 | 0.0 | 348 | 3455 | 708 | 437 | 348 | 30 | 3.0 | True | False | False |

### Stress

| cfg | scenario | net | maxdd | dd_pct | maxfl | blown | dat | n_nen |
|---|---|---|---|---|---|---|---|---|
| tay_v2 | gap-10% tai day von | 95909.49 | 39481.37 | 394.81 | -41836.53 | False | False | nan |
| tay_v2_xac_nhan | gap-10% tai day von | 104706.27 | 39481.37 | 394.81 | -41836.53 | False | False | nan |
| tay_v2_phien_dip | gap-10% tai day von | -11135.05 | 20010.71 | 200.11 | -22397.62 | True | False | nan |
| tay_v2 | gap-20% tai day von | 83433.68 | 55425.14 | 554.25 | -56901.15 | False | False | nan |
| tay_v2_xac_nhan | gap-20% tai day von | 82721.49 | 55425.14 | 554.25 | -56901.15 | False | False | nan |
| tay_v2_phien_dip | gap-20% tai day von | -11135.05 | 20010.71 | 200.11 | -22397.62 | True | False | nan |
| tay_v2 | grind-20%/60ngay | -10157.92 | 42699.82 | 427.0 | -39281.73 | True | False | nan |
| tay_v2_xac_nhan | grind-20%/60ngay | -10157.92 | 42699.82 | 427.0 | -39281.73 | True | False | nan |
| tay_v2_phien_dip | grind-20%/60ngay | -10085.48 | 19308.41 | 193.08 | -19245.43 | True | False | nan |
| tay_v2 | grind-35%/120ngay | -10000.94 | 42375.94 | 423.76 | -39796.14 | True | False | nan |
| tay_v2_xac_nhan | grind-35%/120ngay | -10000.94 | 42375.94 | 423.76 | -39796.14 | True | False | nan |
| tay_v2_phien_dip | grind-35%/120ngay | -10122.2 | 19082.74 | 190.83 | -20358.91 | True | False | nan |
| tay_v2 | Q4-2018 | -10021.77 | 19384.72 | 193.85 | -20249.12 | True | False | 30162.0 |
| tay_v2_xac_nhan | Q4-2018 | -10021.77 | 19384.72 | 193.85 | -20249.12 | True | False | 30162.0 |
| tay_v2_phien_dip | Q4-2018 | -10075.12 | 28431.76 | 284.32 | -32461.92 | True | False | 30162.0 |
| tay_v2 | Covid 02-04/2020 | -10032.59 | 20566.77 | 205.67 | -25344.08 | True | False | 33792.0 |
| tay_v2_xac_nhan | Covid 02-04/2020 | -10032.59 | 20566.77 | 205.67 | -25344.08 | True | False | 33792.0 |
| tay_v2_phien_dip | Covid 02-04/2020 | -10332.28 | 63260.19 | 632.6 | -65924.19 | True | False | 33792.0 |
| tay_v2 | 2022 H1 | -11505.91 | 50124.16 | 501.24 | -46440.0 | True | False | 42036.0 |
| tay_v2_xac_nhan | 2022 H1 | -11505.91 | 50124.16 | 501.24 | -46440.0 | True | False | 42036.0 |
| tay_v2_phien_dip | 2022 H1 | -10292.18 | 23734.67 | 237.35 | -24383.63 | True | False | 42036.0 |
| tay_v2 | 2022 08-10 | -10085.71 | 14086.9 | 140.87 | -15610.75 | True | False | 24464.0 |
| tay_v2_xac_nhan | 2022 08-10 | -10085.71 | 14086.9 | 140.87 | -15610.75 | True | False | 24464.0 |
| tay_v2_phien_dip | 2022 08-10 | -10038.33 | 17212.37 | 172.12 | -16811.67 | True | False | 24464.0 |
| tay_v2 | 08-10/2023 | 32324.38 | 21461.64 | 214.62 | -22636.38 | False | False | 27991.0 |
| tay_v2_xac_nhan | 08-10/2023 | 32324.38 | 21461.64 | 214.62 | -22636.38 | False | False | 27991.0 |
| tay_v2_phien_dip | 08-10/2023 | 18947.7 | 34491.08 | 344.91 | -35236.21 | False | False | 27991.0 |
| tay_v2 | 07-08/2024 | -10003.37 | 11035.98 | 110.36 | -12587.01 | True | False | 15978.0 |
| tay_v2_xac_nhan | 07-08/2024 | -10003.37 | 11035.98 | 110.36 | -12587.01 | True | False | 15978.0 |
| tay_v2_phien_dip | 07-08/2024 | -10097.33 | 11402.74 | 114.03 | -14785.3 | True | False | 15978.0 |
| tay_v2 | 02-04/2025 | -10055.56 | 48058.46 | 480.58 | -49337.16 | True | False | 28840.0 |
| tay_v2_xac_nhan | 02-04/2025 | -10055.56 | 48058.46 | 480.58 | -49337.16 | True | False | 28840.0 |
| tay_v2_phien_dip | 02-04/2025 | -10020.7 | 23353.43 | 233.53 | -24446.94 | True | False | 28840.0 |

- tay_v2: sống 0/11 kịch bản (không cháy và DD<80%). Tệ nhất -11506 USD (-1150591 USC).
- tay_v2_xac_nhan: sống 0/11 kịch bản (không cháy và DD<80%). Tệ nhất -11506 USD (-1150591 USC).

## 3. Kết quả US500

- M1 XM 2026-06-01 05:00:00 → 2026-11-26 19:04:00, 176531 nến, tín hiệu 61398. IS 119922, OOS 56209.

| ten | net | maxdd | dd_pct | maxfl | is_net | oos_net | net_sprx2 | dd_sprx2 | sharpe | dsr | n_en | n_tp | n_dca | n_hd | n_ro | max_tix | maxlots | blown | dat | dat_sprx2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tay_v2 | 1712.59 | 253.92 | 2.54 | -347.19 | 1227.49 | 485.09 | 1198.93 | 256.51 | 2.561 | 1.0 | 2424 | 8673 | 3785 | 1037 | 2424 | 30 | 3.0 | False | True | True |
| tay_v2_xac_nhan | 1712.59 | 253.92 | 2.54 | -347.19 | 1227.49 | 485.09 | 1198.93 | 256.51 | 2.561 | 1.0 | 2424 | 8673 | 3785 | 1037 | 2424 | 30 | 3.0 | False | True | True |
| tay_v2_usonly | 1581.47 | 253.92 | 2.54 | -347.19 | 1007.11 | 574.35 | 1277.58 | 256.51 | 2.505 | 1.0 | 1962 | 7917 | 3476 | 913 | 1962 | 30 | 3.0 | False | True | True |
| tay_v2_phien_dip | 576.36 | 499.3 | 4.99 | -549.55 | 24.04 | 552.33 | 1268.32 | 502.57 | 0.952 | 0.0 | 975 | 3910 | 1912 | 407 | 975 | 30 | 3.0 | False | True | True |
| lan_tp312 | 1381.24 | 281.78 | 2.82 | -463.41 | 1003.4 | 377.85 | 1001.98 | 339.56 | 1.231 | 0.0 | 2118 | 19051 | 6245 | 2268 | 2118 | 30 | 3.0 | False | True | True |
| lan_tp522 | 1655.8 | 262.58 | 2.63 | -347.19 | 1166.25 | 489.55 | 1229.04 | 280.2 | 2.201 | 1.0 | 2296 | 11374 | 4404 | 1373 | 2296 | 30 | 3.0 | False | True | True |
| lan_gap4 | 2760.85 | 408.8 | 4.09 | -566.73 | 1690.76 | 1070.09 | 2210.55 | 332.35 | 2.271 | 1.0 | 3452 | 13865 | 6637 | 1858 | 3452 | 30 | 3.0 | False | True | True |
| lan_gap8 | 1669.9 | 255.15 | 2.55 | -351.03 | 1152.43 | 517.47 | 1332.92 | 361.3 | 2.436 | 1.0 | 2258 | 8937 | 3867 | 1088 | 2258 | 30 | 3.0 | False | True | True |
| lan_hgap15 | 1208.86 | 290.85 | 2.91 | -421.45 | 891.05 | 317.81 | 1009.26 | 352.24 | 1.689 | 0.0 | 1767 | 7207 | 2854 | 940 | 1767 | 30 | 3.0 | False | True | True |
| lan_hgap30 | 1380.85 | 354.66 | 3.55 | -497.77 | 961.91 | 418.94 | 869.72 | 306.32 | 1.633 | 0.0 | 2214 | 7456 | 3474 | 825 | 2214 | 30 | 3.0 | False | True | True |
| lan_maxL10 | 2023.6 | 157.15 | 1.57 | -176.96 | 1269.11 | 754.49 | 1626.94 | 238.95 | 4.024 | 1.0 | 2716 | 7676 | 2142 | 1155 | 2716 | 20 | 2.0 | False | True | True |
| lan_maxL40 | 1465.81 | 387.98 | 3.88 | -600.81 | 1137.82 | 327.99 | 808.88 | 416.75 | 2.072 | 1.0 | 2256 | 9271 | 3892 | 1134 | 2256 | 50 | 5.0 | False | True | True |
| lan_maxL80 | 1451.42 | 387.98 | 3.88 | -618.22 | 1137.82 | 313.61 | 862.49 | 416.75 | 2.055 | 1.0 | 2248 | 9391 | 3948 | 1148 | 2248 | 57 | 5.7 | False | True | True |

### Stress

| cfg | scenario | net | maxdd | dd_pct | maxfl | blown | dat | n_nen |
|---|---|---|---|---|---|---|---|---|
| tay_v2 | gap-10% tai day von | 902.65 | 1651.32 | 16.51 | -1858.98 | False | True | nan |
| tay_v2_xac_nhan | gap-10% tai day von | 902.65 | 1651.32 | 16.51 | -1858.98 | False | True | nan |
| tay_v2_phien_dip | gap-10% tai day von | 1719.33 | 1638.94 | 16.39 | -1830.96 | False | True | nan |
| tay_v2 | gap-20% tai day von | 750.17 | 3138.99 | 31.39 | -3328.55 | False | True | nan |
| tay_v2_xac_nhan | gap-20% tai day von | 750.17 | 3138.99 | 31.39 | -3328.55 | False | True | nan |
| tay_v2_phien_dip | gap-20% tai day von | 952.1 | 3127.4 | 31.27 | -3300.84 | False | True | nan |
| tay_v2 | grind-20%/60ngay | 856.08 | 245.11 | 2.45 | -367.65 | False | True | nan |
| tay_v2_xac_nhan | grind-20%/60ngay | 856.08 | 245.11 | 2.45 | -367.65 | False | True | nan |
| tay_v2_phien_dip | grind-20%/60ngay | 1152.32 | 191.57 | 1.92 | -298.66 | False | True | nan |
| tay_v2 | grind-35%/120ngay | 818.21 | 235.91 | 2.36 | -367.83 | False | True | nan |
| tay_v2_xac_nhan | grind-35%/120ngay | 818.21 | 235.91 | 2.36 | -367.83 | False | True | nan |
| tay_v2_phien_dip | grind-35%/120ngay | 1144.36 | 226.33 | 2.26 | -298.81 | False | True | nan |
| tay_v2 | Q4-2018 | 949.94 | 903.61 | 9.04 | -925.79 | False | True | 29375.0 |
| tay_v2_xac_nhan | Q4-2018 | 949.94 | 903.61 | 9.04 | -925.79 | False | True | 29375.0 |
| tay_v2_phien_dip | Q4-2018 | 1894.71 | 473.14 | 4.73 | -735.0 | False | True | 29375.0 |
| tay_v2 | Covid 02-04/2020 | 4273.27 | 830.46 | 8.3 | -1178.51 | False | True | 32192.0 |
| tay_v2_xac_nhan | Covid 02-04/2020 | 4273.27 | 830.46 | 8.3 | -1178.51 | False | True | 32192.0 |
| tay_v2_phien_dip | Covid 02-04/2020 | 1678.75 | 1683.7 | 16.84 | -1746.39 | False | True | 32192.0 |
| tay_v2 | 2022 H1 | 3168.82 | 527.77 | 5.28 | -646.7 | False | True | 40632.0 |
| tay_v2_xac_nhan | 2022 H1 | 3168.82 | 527.77 | 5.28 | -646.7 | False | True | 40632.0 |
| tay_v2_phien_dip | 2022 H1 | 3990.74 | 411.3 | 4.11 | -646.7 | False | True | 40632.0 |
| tay_v2 | 2022 08-10 | -343.18 | 1196.55 | 11.97 | -1193.8 | False | False | 23641.0 |
| tay_v2_xac_nhan | 2022 08-10 | -343.18 | 1196.55 | 11.97 | -1193.8 | False | False | 23641.0 |
| tay_v2_phien_dip | 2022 08-10 | 1665.86 | 407.39 | 4.07 | -507.34 | False | True | 23641.0 |
| tay_v2 | 08-10/2023 | 861.26 | 236.18 | 2.36 | -352.34 | False | True | 27069.0 |
| tay_v2_xac_nhan | 08-10/2023 | 861.26 | 236.18 | 2.36 | -352.34 | False | True | 27069.0 |
| tay_v2_phien_dip | 08-10/2023 | 1325.8 | 242.91 | 2.43 | -333.38 | False | True | 27069.0 |
| tay_v2 | 07-08/2024 | 833.53 | 322.97 | 3.23 | -512.19 | False | True | 15421.0 |
| tay_v2_xac_nhan | 07-08/2024 | 833.53 | 322.97 | 3.23 | -512.19 | False | True | 15421.0 |
| tay_v2_phien_dip | 07-08/2024 | 161.36 | 394.58 | 3.95 | -466.32 | False | True | 15421.0 |
| tay_v2 | 02-04/2025 | 624.22 | 1008.54 | 10.09 | -1304.36 | False | True | 27825.0 |
| tay_v2_xac_nhan | 02-04/2025 | 624.22 | 1008.54 | 10.09 | -1304.36 | False | True | 27825.0 |
| tay_v2_phien_dip | 02-04/2025 | 1574.57 | 479.54 | 4.8 | -507.1 | False | True | 27825.0 |

- tay_v2: sống 11/11 kịch bản (không cháy và DD<80%). Tệ nhất -343 USD (-34318 USC).
- tay_v2_xac_nhan: sống 11/11 kịch bản (không cháy và DD<80%). Tệ nhất -343 USD (-34318 USC).

Nhật ký bóng: `phong_cach_tay/ket_qua/shadow_tay_v2.csv`. Chạy 11.4 giây. Không đặt lệnh thật.

Cửa sổ sập dùng nến M5 parquet (mốc giờ parquet, scale 4000/7000), vẫn thô hơn cạnh <5 phút trên M1.

## Kết luận (số đo, giờ Việt Nam UTC+7)

**Lịch sử Anh không phải một cạnh scalping ổn định <5 phút trên lot nhỏ.** +40.951 (WR 97,4%) ở lệnh vàng giữ <5 phút có 38.523 từ riêng 25/11 với lot 1,00 sau khi nạp 900.000 demo. Lot ≤ 0,10 và giữ <5 phút: 155 lệnh, tất cả lãi, +5.260,5, TP trung vị 4,00 USD, giữ 1,40 phút — số này mới dùng để khớp máy. 20+21+25/11 chiếm 98,7% lãi vàng.

**Điều kiện vào lệnh — nên giữ / không giữ:**
- Giữ: phiên Mỹ 20–07 VN (84,4% lệnh lãi nhanh; 619 vị thế, +47.996). Cụm ~4 lệnh, lot cố định 0,10, TP ~4 USD, DCA khe 5,47, hedge khe ~21, đóng rổ khi lãi tổng.
- Không giữ như điều kiện bắt buộc: điểm S≥1 chỉ có ở **23,2%** mọi lệnh vàng và **14,6%** lệnh lãi nhanh. Râu M5 1,7%, BB ±2σ 3,0%, Fxaurum cùng chiều 5,3% ở nhóm lãi nhanh (10,4% còn ngược chiều trên toàn mẫu). Giờ 23 VN (+30.381, chủ yếu 25/11) gần như không có S hay data. Nhóm thua thậm chí có tỷ lệ 2 giờ đầu phiên Mỹ cao hơn (63,4% vs 19,8%).

**XAU `tay_v2` (vốn 10.000 USD = 1.000.000 USC, M1 trong nến thận trọng — không TP cùng nến đã DCA/hedge):** lãi ròng **+98.412,18** USD nhưng max DD **45.386,14 (453,86% vốn ban đầu)**, lỗ thả nổi −46.977,70 — **không đạt** tiêu chí DD < 80%. IS +62.492 / OOS +35.921. Spread ×2 cháy −10.008. Sống **0/11** stress. Lân cận phân hóa: một phần cháy (usonly, phien_dip, gap 4, hgap 15, TP 1,59); phần còn lại lãi 6 số với DD 310–685%. Máy không SL, sống nhờ lãi sớm rồi chịu DD lớn — không ổn định.

**US500 `tay_v2`:** **+1.712,59** USD (+171.259 USC), max DD **253,92 (2,54%)**, lỗ thả nổi −347,19, không cháy. IS +1.227,49 / OOS +485,09. Spread ×2 +1.198,93, DD 256,51, vẫn đạt. Sharpe 2,56, DSR 1,00. Sống **11/11** stress (tệ nhất 2022 08–10: −343,18, DD 12%, không cháy). Mọi lân cận (kể cả maxL 80, gap 4, TP 3,12/5,22) đều lãi, DD 1,6–4,1%. `tay_v2_phien_dip` +576,36, DD 4,99%, cũng đạt và sống 11/11. **Đây là cấu hình đạt 7 bước trên cửa sổ đo được** — vẫn chỉ là M1 (không tick XM), tham số khớp từ deal tháng 11 (trùng OOS về hành vi).

Trần 86–110 tầng không bị chạm (tối đa ~30 ticket / 3 lot). Không đặt lệnh thật.
