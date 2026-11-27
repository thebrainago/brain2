# tay_v2 + lọc tín hiệu data Phần 1

Xuất: 2026-11-27 20:41:31.872310+07:00 (giờ Việt Nam, UTC+7).

Dùng `phong_cach_tay/tin_hieu_data.py` (không sửa). Tổ hợp vàng ĐẠT thêm từ cột generator + VWAP/POC/VA trên cùng bảng phút (đúng định nghĩa `p1_quy_tac.py`).
Chiều lên M1: trễ 60 giây (vào mở nến m+1 như P1), giữ 15 phút. `p1_sig_*_mac_dinh` dùng `tao()` mặc định (trễ 120 giây, giữ 1 phút).
Vốn 10.000 USD = 1.000.000 USC. Không đặt lệnh thật. Cửa sổ sập M5 không có tick Fxaurum — lọc P1 = 0.

## Khớp với cụm lịch sử của Anh

### Vàng (GOLD.i#)

| nhom | n | pnl | wr | big30_giu_co | big30_giu_cung | big30_giu_nguoc | delta15_giu_co | delta15_giu_cung | delta15_giu_nguoc | union4_co | union4_cung | union4_nguoc | big30_d15_co | big30_d15_cung | big30_d15_nguoc | d15_vahfade_co | d15_vahfade_cung | d15_vahfade_nguoc | big30_vwap_co | big30_vwap_cung | big30_vwap_nguoc | big30_poc_win_co | big30_poc_win_cung | big30_poc_win_nguoc | uu_tien_co | uu_tien_cung | uu_tien_nguoc | sig_GC_co | sig_GC_cung | sig_GC_nguoc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tat_ca | 866 | 60702.65 | 90.5 | 4.6 | 1.7 | 2.9 | 52.4 | 31.3 | 21.1 | 2.8 | 1.3 | 1.5 | 2.8 | 1.3 | 1.5 | 0.0 | 0.0 | 0.0 | 0.3 | 0.0 | 0.3 | 0.1 | 0.0 | 0.1 | 53.7 | 31.5 | 22.2 | 3.5 | 1.7 | 1.7 |
| thang | 784 | 91819.75 | 100.0 | 4.7 | 1.8 | 2.9 | 51.9 | 33.8 | 18.1 | 2.8 | 1.3 | 1.5 | 2.8 | 1.3 | 1.5 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 | 0.4 | 0.1 | 0.0 | 0.1 | 53.3 | 34.3 | 19.0 | 3.4 | 1.8 | 1.7 |
| thua | 82 | -31117.1 | 0.0 | 3.7 | 1.2 | 2.4 | 57.3 | 7.3 | 50.0 | 2.4 | 1.2 | 1.2 | 2.4 | 1.2 | 1.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 57.3 | 4.9 | 52.4 | 3.7 | 1.2 | 2.4 |
| nhanh_lai | 301 | 41084.54 | 100.0 | 0.0 | 0.0 | 0.0 | 29.6 | 17.3 | 12.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 29.6 | 17.3 | 12.3 | 0.0 | 0.0 | 0.0 |
| 30p_4h | 272 | -14929.93 | 80.5 | 4.4 | 1.5 | 2.9 | 68.0 | 41.9 | 26.1 | 3.7 | 0.7 | 2.9 | 3.7 | 0.7 | 2.9 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 0.0 | 0.4 | 68.0 | 42.3 | 25.7 | 4.4 | 1.5 | 2.9 |
| lot_le_0.1 | 641 | 33159.16 | 90.3 | 6.2 | 2.3 | 3.9 | 69.3 | 40.7 | 28.5 | 3.7 | 1.7 | 2.0 | 3.7 | 1.7 | 2.0 | 0.0 | 0.0 | 0.0 | 0.5 | 0.0 | 0.5 | 0.2 | 0.0 | 0.2 | 71.0 | 41.0 | 30.0 | 4.7 | 2.3 | 2.3 |
| lot_le_0.1_nhanh | 155 | 5260.54 | 100.0 | 0.0 | 0.0 | 0.0 | 57.4 | 33.5 | 23.9 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 57.4 | 33.5 | 23.9 | 0.0 | 0.0 | 0.0 |
| tru_25-11 | 469 | 35147.6 | 93.2 | 8.5 | 3.2 | 5.3 | 63.5 | 38.6 | 24.9 | 5.1 | 2.3 | 2.8 | 5.1 | 2.3 | 2.8 | 0.0 | 0.0 | 0.0 | 0.6 | 0.0 | 0.6 | 0.2 | 0.0 | 0.2 | 65.9 | 39.0 | 26.9 | 6.4 | 3.2 | 3.2 |

Cột `_co` = % vị thế có tín hiệu ≠ 0 tại lúc vào (giữ 15′). `_cung` / `_nguoc` so với chiều lệnh.

### US500

| nhom | n | pnl | wr | big30_giu_co | big30_giu_cung | big30_giu_nguoc | delta15_giu_co | delta15_giu_cung | delta15_giu_nguoc | uu_tien_co | uu_tien_cung | uu_tien_nguoc | sig_ES_co | sig_ES_cung | sig_ES_nguoc | vah_val_pha_co | vah_val_pha_cung | vah_val_pha_nguoc | cvd_d15_co | cvd_d15_cung | cvd_d15_nguoc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tat_ca | 228 | -113.01 | 51.8 | 38.2 | 6.6 | 31.6 | 50.9 | 44.3 | 6.6 | 50.9 | 19.3 | 31.6 | 19.3 | 12.7 | 6.6 | 0.0 | 0.0 | 0.0 | 19.3 | 12.7 | 6.6 |
| thang | 118 | 251.65 | 100.0 | 50.8 | 11.0 | 39.8 | 62.7 | 51.7 | 11.0 | 62.7 | 22.9 | 39.8 | 35.6 | 24.6 | 11.0 | 0.0 | 0.0 | 0.0 | 35.6 | 24.6 | 11.0 |
| thua | 110 | -364.66 | 0.0 | 24.5 | 1.8 | 22.7 | 38.2 | 36.4 | 1.8 | 38.2 | 15.5 | 22.7 | 1.8 | 0.0 | 1.8 | 0.0 | 0.0 | 0.0 | 1.8 | 0.0 | 1.8 |
| nhanh_lai | 54 | 49.25 | 100.0 | 85.2 | 24.1 | 61.1 | 100.0 | 75.9 | 24.1 | 100.0 | 38.9 | 61.1 | 51.9 | 27.8 | 24.1 | 0.0 | 0.0 | 0.0 | 51.9 | 27.8 | 24.1 |
| 30p_4h | 75 | 41.43 | 46.7 | 33.3 | 0.0 | 33.3 | 61.3 | 61.3 | 0.0 | 61.3 | 28.0 | 33.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| lot_le_0.1 | 202 | -157.55 | 53.0 | 43.1 | 7.4 | 35.6 | 46.0 | 38.6 | 7.4 | 46.0 | 10.4 | 35.6 | 21.8 | 14.4 | 7.4 | 0.0 | 0.0 | 0.0 | 21.8 | 14.4 | 7.4 |
| lot_le_0.1_nhanh | 48 | 23.53 | 95.8 | 100.0 | 31.2 | 68.8 | 100.0 | 68.8 | 31.2 | 100.0 | 31.2 | 68.8 | 62.5 | 31.2 | 31.2 | 0.0 | 0.0 | 0.0 | 62.5 | 31.2 | 31.2 |
| tru_25-11 | 103 | -58.44 | 45.6 | 0.0 | 0.0 | 0.0 | 5.8 | 5.8 | 0.0 | 5.8 | 5.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Kiểm 7 bước

### XAU

- M1 2026-06-01 05:00:00 → 2026-11-26 19:04:00. Số bar có tín hiệu: {'tay_v2': 58303, 'p1_sig_GC_mac_dinh': 5996, 'p1_union4': 9699, 'p1_big30_d15': 7306, 'p1_d15_vahfade': 2547, 'p1_big30_vwap': 1117, 'p1_big30_poc_win': 652, 'p1_uu_tien': 37288, 'tay_v2_xac_nhan_p1': 1617, 'tay_v2_chan_big_nguoc': 55466}.

| ten | net | maxdd | dd_pct | maxfl | is_net | oos_net | net_sprx2 | dd_sprx2 | sharpe | dsr | n_en | n_tp | blown | dat | dat_sprx2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tay_v2 | 98412.18 | 45386.14 | 453.86 | -46977.7 | 62491.61 | 35920.57 | -10007.58 | 31040.24 | 2.267 | 1.0 | 2115 | 6614 | False | False | False |
| p1_union4 | -10079.33 | 11804.23 | 118.04 | -13590.7 | -10079.33 | 0.0 | -10464.71 | 11999.61 | -2.015 | 0.0 | 33 | 69 | True | False | False |
| p1_big30_d15 | -10579.33 | 12452.23 | 124.52 | -14238.7 | -10579.33 | 0.0 | -10335.51 | 11999.61 | -2.106 | 0.0 | 33 | 69 | True | False | False |
| p1_sig_GC_mac_dinh | -10037.53 | 11509.23 | 115.09 | -13295.7 | -10037.53 | 0.0 | -10622.71 | 11999.61 | -2.293 | 0.0 | 26 | 68 | True | False | False |
| tay_v2_xac_nhan_p1 | -10155.93 | 11390.23 | 113.9 | -13176.7 | -10155.93 | 0.0 | -10208.31 | 11351.61 | -2.36 | 0.0 | 16 | 64 | True | False | False |
| tay_v2_chan_big_nguoc | 105286.71 | 45386.14 | 453.86 | -46977.7 | 60667.85 | 44618.86 | -10007.58 | 31040.24 | 2.407 | 1.0 | 2376 | 6974 | False | False | False |
| p1_uu_tien | -10164.71 | 18249.36 | 182.49 | -19241.7 | -10164.71 | 0.0 | -11183.6 | 17255.36 | -0.971 | 0.0 | 159 | 398 | True | False | False |
| p1_d15_vahfade | 31123.51 | 26446.34 | 264.46 | -26895.7 | 24281.01 | 6842.5 | 29223.08 | 26585.34 | 2.093 | 1.0 | 507 | 1305 | False | False | False |
| p1_big30_vwap | -10350.86 | 13019.53 | 130.2 | -16531.87 | -10350.86 | 0.0 | -10392.18 | 13420.79 | -1.917 | 0.0 | 32 | 316 | True | False | False |
| p1_big30_poc_win | -10173.93 | 20060.82 | 200.61 | -21909.97 | 3958.3 | -14132.22 | -10233.13 | 19694.79 | -1.369 | 0.0 | 156 | 292 | True | False | False |

| cfg | scenario | net | maxdd | dd_pct | blown | dat | n_nen |
|---|---|---|---|---|---|---|---|
| tay_v2 | gap-10% tai day von | 95909.49 | 39481.37 | 394.81 | False | False | nan |
| p1_union4 | gap-10% tai day von | -10198.92 | 11762.13 | 117.62 | True | False | nan |
| tay_v2_xac_nhan_p1 | gap-10% tai day von | -10058.53 | 11178.93 | 111.79 | True | False | nan |
| tay_v2_chan_big_nguoc | gap-10% tai day von | 97918.63 | 39481.37 | 394.81 | False | False | nan |
| tay_v2 | gap-20% tai day von | 83433.68 | 55425.14 | 554.25 | False | False | nan |
| p1_union4 | gap-20% tai day von | -10370.16 | 20101.92 | 201.02 | True | False | nan |
| tay_v2_xac_nhan_p1 | gap-20% tai day von | 20791.89 | 3213.16 | 32.13 | False | True | nan |
| tay_v2_chan_big_nguoc | gap-20% tai day von | 87616.19 | 55425.14 | 554.25 | False | False | nan |
| tay_v2 | grind-20%/60ngay | -10157.92 | 42699.82 | 427.0 | True | False | nan |
| p1_union4 | grind-20%/60ngay | -10091.85 | 12555.06 | 125.55 | True | False | nan |
| tay_v2_xac_nhan_p1 | grind-20%/60ngay | 18839.06 | 5497.27 | 54.97 | False | True | nan |
| tay_v2_chan_big_nguoc | grind-20%/60ngay | -10157.92 | 42699.82 | 427.0 | True | False | nan |
| tay_v2 | grind-35%/120ngay | -10000.94 | 42375.94 | 423.76 | True | False | nan |
| p1_union4 | grind-35%/120ngay | -10620.86 | 15612.76 | 156.13 | True | False | nan |
| tay_v2_xac_nhan_p1 | grind-35%/120ngay | 16791.35 | 5092.94 | 50.93 | False | True | nan |
| tay_v2_chan_big_nguoc | grind-35%/120ngay | -10000.94 | 42375.94 | 423.76 | True | False | nan |
| tay_v2 | Q4-2018 | -10021.77 | 19384.72 | 193.85 | True | False | 30162.0 |
| tay_v2_chan_big_nguoc | Q4-2018 | -10021.77 | 19384.72 | 193.85 | True | False | 30162.0 |
| p1_union4 | Q4-2018 | 0.0 | 0.0 | 0.0 | False | False | 30162.0 |
| tay_v2_xac_nhan_p1 | Q4-2018 | 0.0 | 0.0 | 0.0 | False | False | 30162.0 |
| tay_v2 | Covid 02-04/2020 | -10032.59 | 20566.77 | 205.67 | True | False | 33792.0 |
| tay_v2_chan_big_nguoc | Covid 02-04/2020 | -10032.59 | 20566.77 | 205.67 | True | False | 33792.0 |
| p1_union4 | Covid 02-04/2020 | 0.0 | 0.0 | 0.0 | False | False | 33792.0 |
| tay_v2_xac_nhan_p1 | Covid 02-04/2020 | 0.0 | 0.0 | 0.0 | False | False | 33792.0 |
| tay_v2 | 2022 H1 | -11505.91 | 50124.16 | 501.24 | True | False | 42036.0 |
| tay_v2_chan_big_nguoc | 2022 H1 | -11505.91 | 50124.16 | 501.24 | True | False | 42036.0 |
| p1_union4 | 2022 H1 | 0.0 | 0.0 | 0.0 | False | False | 42036.0 |
| tay_v2_xac_nhan_p1 | 2022 H1 | 0.0 | 0.0 | 0.0 | False | False | 42036.0 |
| tay_v2 | 2022 08-10 | -10085.71 | 14086.9 | 140.87 | True | False | 24464.0 |
| tay_v2_chan_big_nguoc | 2022 08-10 | -10085.71 | 14086.9 | 140.87 | True | False | 24464.0 |
| p1_union4 | 2022 08-10 | 0.0 | 0.0 | 0.0 | False | False | 24464.0 |
| tay_v2_xac_nhan_p1 | 2022 08-10 | 0.0 | 0.0 | 0.0 | False | False | 24464.0 |
| tay_v2 | 08-10/2023 | 32324.38 | 21461.64 | 214.62 | False | False | 27991.0 |
| tay_v2_chan_big_nguoc | 08-10/2023 | 32324.38 | 21461.64 | 214.62 | False | False | 27991.0 |
| p1_union4 | 08-10/2023 | 0.0 | 0.0 | 0.0 | False | False | 27991.0 |
| tay_v2_xac_nhan_p1 | 08-10/2023 | 0.0 | 0.0 | 0.0 | False | False | 27991.0 |
| tay_v2 | 07-08/2024 | -10003.37 | 11035.98 | 110.36 | True | False | 15978.0 |
| tay_v2_chan_big_nguoc | 07-08/2024 | -10003.37 | 11035.98 | 110.36 | True | False | 15978.0 |
| p1_union4 | 07-08/2024 | 0.0 | 0.0 | 0.0 | False | False | 15978.0 |
| tay_v2_xac_nhan_p1 | 07-08/2024 | 0.0 | 0.0 | 0.0 | False | False | 15978.0 |
| tay_v2 | 02-04/2025 | -10055.56 | 48058.46 | 480.58 | True | False | 28840.0 |
| tay_v2_chan_big_nguoc | 02-04/2025 | -10055.56 | 48058.46 | 480.58 | True | False | 28840.0 |
| p1_union4 | 02-04/2025 | 0.0 | 0.0 | 0.0 | False | False | 28840.0 |
| tay_v2_xac_nhan_p1 | 02-04/2025 | 0.0 | 0.0 | 0.0 | False | False | 28840.0 |

- tay_v2: sống 0/11 (không cháy, DD<80%). Tệ nhất -11506 USD.
- p1_union4: sống 7/11 (không cháy, DD<80%). Tệ nhất -10621 USD.
- tay_v2_xac_nhan_p1: sống 10/11 (không cháy, DD<80%). Tệ nhất -10059 USD.
- tay_v2_chan_big_nguoc: sống 0/11 (không cháy, DD<80%). Tệ nhất -11506 USD.

### US500

- M1 2026-06-01 05:00:00 → 2026-11-26 19:04:00. Số bar có tín hiệu: {'tay_v2': 61398, 'p1_sig_ES_mac_dinh': 561, 'p1_vah_pha': 2943, 'p1_cvd_d15': 2175, 'p1_uu_tien': 13106, 'tay_v2_xac_nhan_p1': 1348, 'tay_v2_chan_big_nguoc': 59625, 'p1_union_es': 4779}.

| ten | net | maxdd | dd_pct | maxfl | is_net | oos_net | net_sprx2 | dd_sprx2 | sharpe | dsr | n_en | n_tp | blown | dat | dat_sprx2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tay_v2 | 1712.59 | 253.92 | 2.54 | -347.19 | 1227.49 | 485.09 | 1198.93 | 256.51 | 2.561 | 1.0 | 2424 | 8673 | False | True | True |
| p1_union_es | 657.83 | 177.43 | 1.77 | -239.49 | 148.21 | 509.62 | 538.0 | 160.79 | 2.621 | 1.0 | 610 | 1861 | False | True | True |
| p1_vah_pha | 371.77 | 177.43 | 1.77 | -200.29 | 105.51 | 266.27 | 300.11 | 174.16 | 2.375 | 1.0 | 383 | 1013 | False | True | True |
| p1_sig_ES_mac_dinh | 375.64 | 57.33 | 0.57 | -63.86 | 74.77 | 300.88 | 297.7 | 165.11 | 3.518 | 1.0 | 325 | 456 | False | True | True |
| tay_v2_xac_nhan_p1 | 315.59 | 253.92 | 2.54 | -321.19 | 54.14 | 261.45 | 253.21 | 256.51 | 1.03 | 0.0 | 295 | 1437 | False | True | True |
| tay_v2_chan_big_nguoc | 1690.37 | 253.92 | 2.54 | -347.19 | 1227.24 | 463.14 | 1207.86 | 256.51 | 2.53 | 1.0 | 2416 | 8550 | False | True | True |
| p1_uu_tien | 792.71 | 253.92 | 2.54 | -321.19 | 93.14 | 699.57 | 608.21 | 256.51 | 1.998 | 1.0 | 743 | 3045 | False | True | True |
| p1_cvd_d15 | 380.16 | 253.92 | 2.54 | -321.19 | 45.96 | 334.2 | 319.83 | 256.51 | 1.197 | 0.0 | 335 | 1220 | False | True | True |

| cfg | scenario | net | maxdd | dd_pct | blown | dat | n_nen |
|---|---|---|---|---|---|---|---|
| tay_v2 | gap-10% tai day von | 902.65 | 1651.32 | 16.51 | False | True | nan |
| p1_union_es | gap-10% tai day von | 539.99 | 165.02 | 1.65 | False | True | nan |
| tay_v2_xac_nhan_p1 | gap-10% tai day von | 277.04 | 226.52 | 2.27 | False | True | nan |
| tay_v2_chan_big_nguoc | gap-10% tai day von | 899.93 | 1651.32 | 16.51 | False | True | nan |
| tay_v2 | gap-20% tai day von | 750.17 | 3138.99 | 31.39 | False | True | nan |
| p1_union_es | gap-20% tai day von | 450.82 | 163.39 | 1.63 | False | True | nan |
| tay_v2_xac_nhan_p1 | gap-20% tai day von | 215.47 | 231.78 | 2.32 | False | True | nan |
| tay_v2_chan_big_nguoc | gap-20% tai day von | 742.23 | 3138.99 | 31.39 | False | True | nan |
| tay_v2 | grind-20%/60ngay | 856.08 | 245.11 | 2.45 | False | True | nan |
| p1_union_es | grind-20%/60ngay | 450.82 | 163.39 | 1.63 | False | True | nan |
| tay_v2_xac_nhan_p1 | grind-20%/60ngay | 215.47 | 231.78 | 2.32 | False | True | nan |
| tay_v2_chan_big_nguoc | grind-20%/60ngay | 848.14 | 245.11 | 2.45 | False | True | nan |
| tay_v2 | grind-35%/120ngay | 818.21 | 235.91 | 2.36 | False | True | nan |
| p1_union_es | grind-35%/120ngay | 301.49 | 168.15 | 1.68 | False | True | nan |
| tay_v2_xac_nhan_p1 | grind-35%/120ngay | 122.38 | 177.68 | 1.78 | False | True | nan |
| tay_v2_chan_big_nguoc | grind-35%/120ngay | 810.75 | 235.91 | 2.36 | False | True | nan |
| tay_v2 | Q4-2018 | 949.94 | 903.61 | 9.04 | False | True | 29375.0 |
| tay_v2_chan_big_nguoc | Q4-2018 | 949.94 | 903.61 | 9.04 | False | True | 29375.0 |
| p1_union_es | Q4-2018 | 0.0 | 0.0 | 0.0 | False | False | 29375.0 |
| tay_v2_xac_nhan_p1 | Q4-2018 | 0.0 | 0.0 | 0.0 | False | False | 29375.0 |
| tay_v2 | Covid 02-04/2020 | 4273.27 | 830.46 | 8.3 | False | True | 32192.0 |
| tay_v2_chan_big_nguoc | Covid 02-04/2020 | 4273.27 | 830.46 | 8.3 | False | True | 32192.0 |
| p1_union_es | Covid 02-04/2020 | 0.0 | 0.0 | 0.0 | False | False | 32192.0 |
| tay_v2_xac_nhan_p1 | Covid 02-04/2020 | 0.0 | 0.0 | 0.0 | False | False | 32192.0 |
| tay_v2 | 2022 H1 | 3168.82 | 527.77 | 5.28 | False | True | 40632.0 |
| tay_v2_chan_big_nguoc | 2022 H1 | 3168.82 | 527.77 | 5.28 | False | True | 40632.0 |
| p1_union_es | 2022 H1 | 0.0 | 0.0 | 0.0 | False | False | 40632.0 |
| tay_v2_xac_nhan_p1 | 2022 H1 | 0.0 | 0.0 | 0.0 | False | False | 40632.0 |
| tay_v2 | 2022 08-10 | -343.18 | 1196.55 | 11.97 | False | False | 23641.0 |
| tay_v2_chan_big_nguoc | 2022 08-10 | -343.18 | 1196.55 | 11.97 | False | False | 23641.0 |
| p1_union_es | 2022 08-10 | 0.0 | 0.0 | 0.0 | False | False | 23641.0 |
| tay_v2_xac_nhan_p1 | 2022 08-10 | 0.0 | 0.0 | 0.0 | False | False | 23641.0 |
| tay_v2 | 08-10/2023 | 861.26 | 236.18 | 2.36 | False | True | 27069.0 |
| tay_v2_chan_big_nguoc | 08-10/2023 | 861.26 | 236.18 | 2.36 | False | True | 27069.0 |
| p1_union_es | 08-10/2023 | 0.0 | 0.0 | 0.0 | False | False | 27069.0 |
| tay_v2_xac_nhan_p1 | 08-10/2023 | 0.0 | 0.0 | 0.0 | False | False | 27069.0 |
| tay_v2 | 07-08/2024 | 833.53 | 322.97 | 3.23 | False | True | 15421.0 |
| tay_v2_chan_big_nguoc | 07-08/2024 | 833.53 | 322.97 | 3.23 | False | True | 15421.0 |
| p1_union_es | 07-08/2024 | 0.0 | 0.0 | 0.0 | False | False | 15421.0 |
| tay_v2_xac_nhan_p1 | 07-08/2024 | 0.0 | 0.0 | 0.0 | False | False | 15421.0 |
| tay_v2 | 02-04/2025 | 624.22 | 1008.54 | 10.09 | False | True | 27825.0 |
| tay_v2_chan_big_nguoc | 02-04/2025 | 624.22 | 1008.54 | 10.09 | False | True | 27825.0 |
| p1_union_es | 02-04/2025 | 0.0 | 0.0 | 0.0 | False | False | 27825.0 |
| tay_v2_xac_nhan_p1 | 02-04/2025 | 0.0 | 0.0 | 0.0 | False | False | 27825.0 |

- tay_v2: sống 11/11 (không cháy, DD<80%). Tệ nhất -343 USD.
- p1_union_es: sống 11/11 (không cháy, DD<80%). Tệ nhất 0 USD.
- tay_v2_xac_nhan_p1: sống 11/11 (không cháy, DD<80%). Tệ nhất 0 USD.
- tay_v2_chan_big_nguoc: sống 11/11 (không cháy, DD<80%). Tệ nhất -343 USD.

Chạy 9.9 giây. Nhật ký bóng: `ket_qua/shadow_tay_v2_p1.csv`.

## Kết luận (số đo, giờ Việt Nam UTC+7)

Generator: `phong_cach_tay/tin_hieu_data.py` (không sửa). Tổ hợp vàng ĐẠT dựng thêm từ cùng bảng phút. Chiều M1: trễ 60 giây + giữ 15 phút (như P1 vào m+1, B giữ 15′). `p1_sig_*_mac_dinh` là `tao()` mặc định (trễ 120 giây, giữ 1 phút). Vốn 10.000 USD = 1.000.000 USC.

### Cụm lịch sử của Anh có khớp luật P1 không?

**Vàng — hầu như không vào đúng 4 luật ĐẠT**, và lệnh lãi nhanh (<5 phút) **không bao giờ** trùng union4 / big30+d15 / big30+VWAP / big30-tại-POC / big30 giữ (0%). union4 chỉ có ở 2,8% mọi lệnh (cùng chiều 1,3%, ngược 1,5%) — không tách lãi/lỗ. d15+VA fade = 0% trên toàn bộ 866 vị thế (tín hiệu hiếm, lệnh Anh dồn 20–25/11).

Điều *có* tín hiệu: **delta 15′ đang giữ**. Toàn mẫu 52,4% có delta15; lệnh **thắng** cùng chiều 33,8% / ngược 18,1%; lệnh **thua** cùng chiều chỉ 7,3% / **ngược 50,0%**. `uu_tien` (2·big30+delta15, ở đây gần như delta15 vì big30 hiếm) cùng mô hình (thua ngược 52,4%). **Có cơ sở dùng delta15 cùng chiều để xác nhận, và tránh vào ngược delta15.** Big30 giữ chỉ 4,6% lệnh — luật “mức bị big30 ngược thì cấm” ít khi áp được lên sổ tay của Anh.

**US500 — khớp rõ hơn ở tín hiệu tổng hợp ES.** `sig_ES` / `cvd+delta15`: 35,6% lệnh thắng có tín hiệu, 24,6% cùng chiều; lệnh thua chỉ 1,8%. Lệnh lãi nhanh: 51,9% có tín hiệu (cùng 27,8%, ngược 24,1% — lẫn). Big30 giữ: thắng 50,8% nhưng **ngược 39,8% > cùng 11%** — Anh không theo big30 trên US500. `vah_val_pha` = 0% tại lúc vào. Trước 25/11 gần như không có tín hiệu (ngoài phủ ES hoặc khác giờ).

### Máy cụm + lọc P1 (7 bước)

**XAU:** vào theo 4 luật ĐẠT / `sig_GC` / `uu_tien` đều **cháy** (lãi khoảng −10.000 đến −10.600, DD 114–182%, 16–159 rổ rồi vỡ). `p1_d15_vahfade` +31.123,62 nhưng DD 26.446 (264,46%) — không đạt. `tay_v2_chan_big_nguoc` +105.286,71, DD 453,86% — cùng bệnh máy tay_v2, không đạt. `tay_v2_xac_nhan_p1` (S≥1 và union4 cùng chiều) cháy, chỉ 16 rổ. **Không cấu hình vàng + P1 nào đạt lãi > 0 và DD < 80%.** Cửa sổ sập M5 không có tick Fxaurum nên lọc P1 = không vào; số “sống” ở đó không có ý nghĩa.

**US500: mọi lọc P1 đều đạt trên Jun–Nov**, DD thấp, spread ×2 vẫn đạt:

| Hệ | Lãi ròng | maxDD (%% vốn) | IS / OOS | Spread ×2 | Đạt |
|---|---:|---:|---|---:|---|
| tay_v2 (không lọc P1) | +1.712,59 | 253,92 (2,54%) | +1.227 / +485 | +1.198,93 | có |
| p1_union_es (VA phá + CVD+delta15) | +657,83 | 177,43 (1,77%) | +148 / **+510** | +538,00 | có |
| p1_sig_ES_mac_dinh | +375,64 | **57,33 (0,57%)** | +75 / +301 | +297,70 | có |
| p1_uu_tien | +792,71 | 253,92 (2,54%) | +93 / **+700** | +608,21 | có |
| p1_vah_pha | +371,77 | 177,43 (1,77%) | +106 / +266 | +300,11 | có |
| tay_v2_xac_nhan_p1 | +315,59 | 253,92 (2,54%) | +54 / +261 | +253,21 | có |
| tay_v2_chan_big_nguoc | +1.690,37 | 253,92 (2,54%) | +1.227 / +463 | +1.207,86 | có |

US500 sống 11/11 stress trên các hệ trên (cửa sổ sập của lọc P1 thuần = 0 lệnh). Lọc P1 **giảm lãi, giảm hoặc giữ DD**, OOS của `p1_union_es` và `p1_uu_tien` tốt hơn IS. Đây là cửa sổ 6 tháng + tín hiệu chỉ từ ~28/08; chưa phải bằng chứng ngoài mẫu dài.

**Thực dụng:** trên vàng, P1 không giải thích cụm lãi nhanh của Anh và chưa vào được bằng cụm lot 0,10 mà không cháy; chỉ có ý **tránh ngược delta15**. Trên US500, luật ĐẠT P1 (nhất là `sig_ES` / union / ưu tiên) là bộ lọc vào cụm **ổn hơn**, dù lãi nhỏ hơn tay_v2 không lọc.
