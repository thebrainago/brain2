Cập nhật chữa cháy vàng + US500 mặc định (20:50 UTC+7): `phong_cach_tay/bao_cao/BAO_CAO_VANG_AN_TOAN.md` — vàng L0=0,01 + lọc delta15: +14.032,99 USD, DD 34,24% (stress 8/11). US500 mặc định `p1_union_es`.

Xem báo cáo chung (cả XAU và US500) ở `phong_cach_tay/bao_cao/BAO_CAO_7_BUOC.md` và mã dùng chung `phong_cach_tay/`.

# Máy phong cách tay — kiểm 7 bước (XAU và US500)

Xuất báo cáo: 2026-11-27 20:27:21.405056+07:00 (giờ Việt Nam, UTC+7).

Máy: quy tắc tay đo từ lịch sử XM demo (không SL, vào cụm lot nhỏ, DCA khoảng+vùng, hedge cụm đóng nhanh, đóng theo lãi/lỗ tổng) cộng khối HYB+AG. Vào từ điểm chỉ báo truyền thống (BB M15, râu M5, 2 giờ đầu phiên Mỹ, ATR thấp); với vàng, tín hiệu Fxaurum chỉ được dùng khi chỉ báo cũng đồng thuận (S≥1). **Không đặt lệnh thật** (chỉ nhật ký bóng).

## Quy cách tài khoản cent

- Không tìm thấy terminal Exness cent (`E:\exness_cent` không tồn tại, không có process). Quy cách dùng giả định Exness Standard Cent phổ biến: tiền tệ USC, 100 USC = 1 USD; lot và giá như tài khoản standard; P/L và số dư ×100.
- Vàng: pv=100, bước 0,01, spread 0,20 giá, swap −83,83 / +20,64 USD/lot/đêm (tức ×100 USC).
- US500: pv=1, bước 0,10, spread 0,65 giá, swap −1,24 / +0,17 USD/lot/đêm.
- Vốn khởi điểm 10.000 USD = 1.000.000 USC — đủ vận hành so với kiểu nạp 10k→30k. Đòn bẩy 1:1000 như demo đo được; sàn cent có thể khác.
- Tiêu chí đạt: lãi ròng > 0, max DD < 80% vốn, không cháy (equity ≤ 0).

- IS: trước 2026-10-01; OOS: từ 2026-10-01 (UTC+7).
- 7 bước: (1) IS/OOS, (2) spread ×2, (3) 11 stress (7 cửa sổ sập lịch sử + 2 gap + 2 grind), (4) lân cận tham số, (5) cháy / lỗ thả nổi vs 80%, (6) Deflated Sharpe, (7) nhật ký bóng.

## XAU

- Dữ liệu M1 XM 2026-06-01 05:00:00 → 2026-11-26 19:04:00 (Europe/Athens → UTC+7), 176632 nến. IS 120056 nến, OOS 56176 nến.
- Spread 0.2, pv=100.0, bước lot 0.01. Cửa sổ sập scale về 4000.0 (parquet M5, mốc giờ parquet, **không phải** máy chủ XM).

| ten | net | maxdd | dd_pct | maxfl | is_net | oos_net | net_sprx2 | dd_sprx2 | sharpe | dsr | n_ro | blown | dat | dat_sprx2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tay_HYB_AG | -2240.13 | 7233.33 | 72.33 | -4459.81 | -4070.78 | 1830.65 | 1269.92 | 5532.77 | -0.521 | 0.0 | 586 | False | False | True |
| tay_xac_nhan | -5734.51 | 7215.12 | 72.15 | -4459.81 | -4052.57 | -1681.95 | -2174.54 | 5532.77 | -1.274 | 0.0 | 519 | False | False | False |
| lan_coef10 | -4468.06 | 6504.93 | 65.05 | -3979.05 | -3456.93 | -1011.13 | -1205.51 | 4163.55 | -1.135 | 0.0 | 659 | False | False | False |
| lan_coef13 | -4544.59 | 6363.02 | 63.63 | -5124.73 | -1935.04 | -2609.56 | -6155.55 | 7339.38 | -0.875 | 0.0 | 904 | False | False | False |
| lan_G2 | -3159.53 | 4735.5 | 47.36 | -4378.81 | -1918.13 | -1241.4 | -5579.37 | 7541.33 | -0.82 | 0.0 | 812 | False | False | False |
| lan_maxL10 | -5368.74 | 7215.12 | 72.15 | -4459.81 | -4107.48 | -1261.26 | -1108.29 | 4844.44 | -1.199 | 0.0 | 519 | False | False | False |

### Stress

| cfg | scenario | net | maxdd | dd_pct | maxfl | blown | dat | n_nen |
|---|---|---|---|---|---|---|---|---|
| tay_HYB_AG | gap-10% tai day von | -7559.61 | 13586.24 | 135.86 | -10812.71 | True | False | nan |
| tay_xac_nhan | gap-10% tai day von | -7541.4 | 13568.02 | 135.68 | -10812.71 | True | False | nan |
| tay_HYB_AG | gap-20% tai day von | -14615.93 | 19939.14 | 199.39 | -17165.62 | True | False | nan |
| tay_xac_nhan | gap-20% tai day von | -14597.72 | 19920.93 | 199.21 | -17165.62 | True | False | nan |
| tay_HYB_AG | grind-20%/60ngay | 4776.8 | 2637.36 | 26.37 | -3158.72 | False | True | nan |
| tay_xac_nhan | grind-20%/60ngay | 2183.81 | 3356.24 | 33.56 | -3158.72 | False | True | nan |
| tay_HYB_AG | grind-35%/120ngay | 2798.51 | 6679.73 | 66.8 | -6866.28 | False | True | nan |
| tay_xac_nhan | grind-35%/120ngay | 2660.49 | 6679.73 | 66.8 | -6866.28 | False | True | nan |
| tay_HYB_AG | Q4-2018 | 1408.2 | 1716.7 | 17.17 | -1567.54 | False | True | 10072.0 |
| tay_xac_nhan | Q4-2018 | 1408.2 | 1716.7 | 17.17 | -1567.54 | False | True | 10072.0 |
| tay_HYB_AG | Covid 02-04/2020 | -301.82 | 6078.19 | 60.78 | -6210.75 | False | False | 11264.0 |
| tay_xac_nhan | Covid 02-04/2020 | -301.82 | 6078.19 | 60.78 | -6210.75 | False | False | 11264.0 |
| tay_HYB_AG | 2022 H1 | -4955.13 | 6288.33 | 62.88 | -3030.89 | False | False | 14012.0 |
| tay_xac_nhan | 2022 H1 | -4955.13 | 6288.33 | 62.88 | -3030.89 | False | False | 14012.0 |
| tay_HYB_AG | 2022 08-10 | 1873.05 | 1310.45 | 13.1 | -1202.72 | False | True | 8155.0 |
| tay_xac_nhan | 2022 08-10 | 1873.05 | 1310.45 | 13.1 | -1202.72 | False | True | 8155.0 |
| tay_HYB_AG | 08-10/2023 | -3880.3 | 5967.24 | 59.67 | -5777.99 | False | False | 9332.0 |
| tay_xac_nhan | 08-10/2023 | -3880.3 | 5967.24 | 59.67 | -5777.99 | False | False | 9332.0 |
| tay_HYB_AG | 07-08/2024 | 1103.83 | 867.81 | 8.68 | -909.11 | False | True | 5326.0 |
| tay_xac_nhan | 07-08/2024 | 1103.83 | 867.81 | 8.68 | -909.11 | False | True | 5326.0 |
| tay_HYB_AG | 02-04/2025 | 3886.1 | 1318.35 | 13.18 | -1488.55 | False | True | 9614.0 |
| tay_xac_nhan | 02-04/2025 | 3886.1 | 1318.35 | 13.18 | -1488.55 | False | True | 9614.0 |

- tay_HYB_AG: sống 9/11 kịch bản (không cháy và DD<80%). Lãi/lỗ tệ nhất -14616 USD (-1461593 USC).
- tay_xac_nhan: sống 9/11 kịch bản (không cháy và DD<80%). Lãi/lỗ tệ nhất -14598 USD (-1459772 USC).

## US500

- Dữ liệu M1 XM 2026-06-01 05:00:00 → 2026-11-26 19:04:00 (Europe/Athens → UTC+7), 176531 nến. IS 119922 nến, OOS 56209 nến.
- Spread 0.65, pv=1.0, bước lot 0.1. Cửa sổ sập scale về 7000.0 (parquet M5, mốc giờ parquet, **không phải** máy chủ XM).

| ten | net | maxdd | dd_pct | maxfl | is_net | oos_net | net_sprx2 | dd_sprx2 | sharpe | dsr | n_ro | blown | dat | dat_sprx2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tay_HYB_AG | -450.88 | 874.95 | 8.75 | -559.54 | -175.7 | -275.18 | -650.45 | 1069.85 | -0.837 | 0.0 | 830 | False | False | False |
| tay_xac_nhan | -450.88 | 874.95 | 8.75 | -559.54 | -175.7 | -275.18 | -650.45 | 1069.85 | -0.837 | 0.0 | 830 | False | False | False |
| lan_coef10 | -282.3 | 645.63 | 6.46 | -444.79 | -11.81 | -270.49 | -712.63 | 961.98 | -0.667 | 0.0 | 754 | False | False | False |
| lan_coef13 | -983.79 | 1715.36 | 17.15 | -894.13 | 503.47 | -1487.25 | -1601.2 | 1848.19 | -1.433 | 0.0 | 1052 | False | False | False |
| lan_G2 | -549.52 | 962.12 | 9.62 | -606.98 | -179.43 | -370.09 | -807.72 | 1182.73 | -0.838 | 0.0 | 800 | False | False | False |
| lan_maxL10 | -499.05 | 899.48 | 8.99 | -553.54 | -170.69 | -328.36 | -652.29 | 1038.2 | -0.964 | 0.0 | 810 | False | False | False |

### Stress

| cfg | scenario | net | maxdd | dd_pct | maxfl | blown | dat | n_nen |
|---|---|---|---|---|---|---|---|---|
| tay_HYB_AG | gap-10% tai day von | 77.98 | 874.95 | 8.75 | -559.54 | False | True | nan |
| tay_xac_nhan | gap-10% tai day von | 77.98 | 874.95 | 8.75 | -559.54 | False | True | nan |
| tay_HYB_AG | gap-20% tai day von | 334.54 | 874.95 | 8.75 | -740.31 | False | True | nan |
| tay_xac_nhan | gap-20% tai day von | 334.54 | 874.95 | 8.75 | -740.31 | False | True | nan |
| tay_HYB_AG | grind-20%/60ngay | -1319.42 | 1824.47 | 18.24 | -1454.43 | False | False | nan |
| tay_xac_nhan | grind-20%/60ngay | -1319.42 | 1824.47 | 18.24 | -1454.43 | False | False | nan |
| tay_HYB_AG | grind-35%/120ngay | -7470.47 | 8245.72 | 82.46 | -7354.53 | False | False | nan |
| tay_xac_nhan | grind-35%/120ngay | -7470.47 | 8245.72 | 82.46 | -7354.53 | False | False | nan |
| tay_HYB_AG | Q4-2018 | 640.45 | 361.32 | 3.61 | -396.31 | False | True | 9856.0 |
| tay_xac_nhan | Q4-2018 | 640.45 | 361.32 | 3.61 | -396.31 | False | True | 9856.0 |
| tay_HYB_AG | Covid 02-04/2020 | -352.67 | 1476.42 | 14.76 | -1333.71 | False | False | 10743.0 |
| tay_xac_nhan | Covid 02-04/2020 | -352.67 | 1476.42 | 14.76 | -1333.71 | False | False | 10743.0 |
| tay_HYB_AG | 2022 H1 | -609.76 | 1179.45 | 11.79 | -1141.18 | False | False | 13544.0 |
| tay_xac_nhan | 2022 H1 | -609.76 | 1179.45 | 11.79 | -1141.18 | False | False | 13544.0 |
| tay_HYB_AG | 2022 08-10 | 513.42 | 683.44 | 6.83 | -732.94 | False | True | 7882.0 |
| tay_xac_nhan | 2022 08-10 | 513.42 | 683.44 | 6.83 | -732.94 | False | True | 7882.0 |
| tay_HYB_AG | 08-10/2023 | 89.61 | 335.1 | 3.35 | -261.94 | False | True | 9027.0 |
| tay_xac_nhan | 08-10/2023 | 89.61 | 335.1 | 3.35 | -261.94 | False | True | 9027.0 |
| tay_HYB_AG | 07-08/2024 | -145.67 | 349.87 | 3.5 | -350.69 | False | False | 5144.0 |
| tay_xac_nhan | 07-08/2024 | -145.67 | 349.87 | 3.5 | -350.69 | False | False | 5144.0 |
| tay_HYB_AG | 02-04/2025 | 848.06 | 385.11 | 3.85 | -539.33 | False | True | 9277.0 |
| tay_xac_nhan | 02-04/2025 | 848.06 | 385.11 | 3.85 | -539.33 | False | True | 9277.0 |

- tay_HYB_AG: sống 10/11 kịch bản (không cháy và DD<80%). Lãi/lỗ tệ nhất -7470 USD (-747047 USC).
- tay_xac_nhan: sống 10/11 kịch bản (không cháy và DD<80%). Lãi/lỗ tệ nhất -7470 USD (-747047 USC).

Nhật ký bóng: `/workspace/brain2/phong_cach_tay/ket_qua/shadow_phong_cach_tay.csv` (chỉ ghi, không đặt lệnh).
Chạy trong 7.9 giây.

US500: chưa gắn tín hiệu data ES/Fxaurum (Part 1); `tay_xac_nhan` trùng `tay_HYB_AG` trên cửa sổ này.
Vàng: OptionsDb chưa cho GEX/max pain, trọng số quyền chọn gần như không có mức thật.

## Kết luận (số đo)

Không cấu hình nào của máy phong cách tay **đạt** tiêu chí lãi ròng > 0 và DD < 80% trên cửa sổ Jun–Nov 2026.

- **XAU `tay_HYB_AG`:** lãi ròng −2.240,13 USD (−224.013 USC), max DD 7.233,33 (72,33%), lỗ thả nổi tệ nhất −4.459,81, không cháy. IS −4.070,78 / OOS +1.830,65. Sharpe −0,521, DSR 0,00. Sống 9/11 stress (cháy hai kịch bản gap 10% và 20% tại đáy vốn; tệ nhất −14.616). Lân cận (coef 1,0 / 1,3, G=2, maxL=10) đều lỗ. `tay_xac_nhan` (lọc Fxaurum) tệ hơn: −5.734,51. **Bất thường:** spread ×2 của `tay_HYB_AG` lại lãi +1.269,92, DD 5.532,77, đạt tiêu chí — đường lệnh đổi khi phí lớn hơn, không có nghĩa phí thấp hơn dễ lãi hơn; không dùng làm căn cứ giao dịch.
- **US500 `tay_HYB_AG`:** −450,88 USD (−45.088 USC), max DD 874,95 (8,75%), lỗ thả nổi −559,54, không cháy. IS −175,70 / OOS −275,18. Spread ×2 −650,45. Sharpe −0,837, DSR 0,00. Sống 10/11 stress (trượt `grind-35%/120ngay`, DD 82,46%, lỗ −7.470). `tay_xac_nhan` trùng baseline vì chưa gắn data ES. Lân cận tốt nhất `lan_coef10` vẫn lỗ −282,30.
- So sánh: cổng HYB+AG gốc trên vàng (coef 1,3, maxL 10, S thuần, giai đoạn B) từng +78,82 / DD 57,62% trên cùng M1 — máy tay (coef 1,15, maxL 15, lev 1:1000) khác tham số nên không tái lập số đó. US500 HYB+AG gốc từng +1.501,90 / maxDD 575,97 / sống 11/11; máy tay này không phải cùng cấu hình và **không** tái lập được số đó.
- Trần 15 tầng không bị chạm (vàng max 5 tầng, US500 max 7–8). Máy thận trọng hơn lịch sử tay (tối đa 86–110 lệnh cùng lúc) — đó là chủ đích để cent không cháy, nhưng cũng không bắt được lãi kiểu đóng nhanh <5 phút của Anh.

---

Cập nhật tay_v2: xem `phong_cach_tay/bao_cao/BAO_CAO_V2.md` (US500 đạt 7 bước +1.712,59 / DD 2,54%; vàng +98.412 nhưng DD 453,86%, không đạt).

---

Cập nhật P1 lọc tay_v2: `phong_cach_tay/bao_cao/BAO_CAO_V2_P1.md`. Vàng: cụm lãi nhanh không trùng 4 luật ĐẠT; lệnh thua hay ngược delta15 (50%). Lọc P1 trên vàng cháy hoặc DD >80%. US500: mọi lọc P1 đạt (ví dụ union +657,83 / DD 1,77%; sig_ES mặc định +375,64 / DD 0,57%).
