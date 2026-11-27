# Kết quả quét tín hiệu vàng — XM GOLD CFD

Viết lúc **2026-11-27 19:10 (giờ Việt Nam, UTC+7)**. Chỉ ghi số đã đo trong lần quét này.

## 1. Phạm vi và cách đo

- Tài khoản mô phỏng: micro quy về **GOLD.i#**, vốn đầu 10.000 USD, lot tối thiểu 0,01, hợp đồng 100 ounce/lot.
- Tín hiệu tính lúc **đóng nến i**, vào lệnh tại **mở nến i+1**. Nếu SL và TP cùng nến thì tính **SL** (thận trọng).
- Phí đã trừ: XM GOLD.i# (tài khoản micro quy về mã #). Spread = cột spread nến khi > 0 (có từ 2018-10-10); trước đó và khi = 0 thì dùng trung vị đã đo 16 điểm H1 / 20 điểm M1 (0,16 / 0,20 USD/ounce). Mỗi chiều = nửa spread + trượt 0,5×spread (giả định thận trọng, chưa đo demo). Hoa hồng 0. Vốn đầu 10.000 USD, rủi ro 2% vốn/lệnh theo khoảng SL. Mặc định swap = 0 như tester Ultra Low (DISABLED). Một số tổ hợp tốt nhất được chạy lại với swap đủ (long −83,83 USD/lot/đêm, short +20,64, nhân 3 đêm thứ Tư).
- Mô phỏng Python trên nến OHLC (chưa phải tester MT5 tick thật).
- Tiêu chí ĐẠT: CAGR kép > 10%/năm **và** DD tối đa < 80% **và** ≥ 20 lệnh **và** vốn cuối > 0.
- Đã sửa lỗi nhìn trước của tín hiệu fractal (bản đầu D1 bị sai); số dưới đây là bản đã sửa.

### Nguồn dữ liệu

| Khung | Nguồn | Khoảng | Mốc giờ | Số nến / tổ hợp / ĐẠT |
|---|---|---|---|---|
| D1 | XM GOLD.i D1 | 2010-01-04 → 2026-10-12 | máy chủ XM GMT+2 |  tổ hợp 694, ĐẠT 0 |
| H4 | Gộp từ XM GOLD.i H1 | 2014-01-02 → 2026-10-12 | máy chủ XM GMT+2 |  tổ hợp 1501, ĐẠT 93 |
| H1 | XM GOLD.i H1 đủ giờ (2010–2012 chỉ có D1, 2013 thiếu nến — không dùng) | 2014-01-02 → 2026-10-12 | máy chủ XM GMT+2 |  tổ hợp 1501, ĐẠT 192 |
| M15 | Gộp từ parquet M5 HistData | 2017-01-02 → 2026-10-09 | mốc parquet, không phải máy chủ XM |  tổ hợp 226, ĐẠT 1 |
| M5 | parquet M5 HistData | 2017-01-02 → 2026-10-09 | mốc parquet, không phải máy chủ XM |  tổ hợp 226, ĐẠT 1 |

Tổng **4148** tổ hợp đã đo (tín hiệu đơn × bộ lọc × quản trị, cộng lưới/DCA). Số ĐẠT: **287** (gần hết nằm ở H1/H4 phá vỡ theo xu hướng).

## 2. Mua giữ (không đòn bẩy, đã trừ spread+trượt vào/ra)

| Khung | Từ | Đến | Năm | CAGR kép | DD tối đa | Lợi nhuận | Đạt |
|---|---|---|---:|---:|---:|---:|---|
| D1 | 2010-01-04 | 2026-10-12 | 16.77 | 8.15% | 44.69% | 272.0% | không |
| H1 | 2014-01-02 | 2026-10-12 | 12.77 | 10.07% | 28.76% | 240.6% | có |
| H4 | 2014-01-02 | 2026-10-12 | 12.77 | 10.07% | 28.70% | 240.6% | có |
| M15 | 2017-01-02 | 2026-10-09 | 9.76 | 14.16% | 29.15% | 264.2% | có |
| M5 | 2017-01-02 | 2026-10-09 | 9.76 | 14.14% | 29.18% | 263.8% | có |

Mua giữ H1/H4 (2014–2026) vừa ĐẠT (10,07% / DD 28,7%). Mua giữ D1 (2010–2026) **không ĐẠT** (8,15% / DD 44,69%) vì gồm giai đoạn giảm 2011–2015. M15/M5 (2017–2026) 14,14–14,16% / DD 29,2%.

## 3. Tổ hợp tốt nhất (không swap), xếp ĐẠT rồi CAGR

Cảnh báo: CAGR cả mẫu H1 rất cao vì vốn tăng mạnh năm 2015–2017 rồi kép 2%/lệnh trên hàng nghìn lệnh (PF chỉ khoảng 1,2–1,4). Xem mục 5 (tách giai đoạn).

| Hạng | Khung | Vào | Lọc | Quản trị | CAGR kép | DD tối đa | Lệnh | Thắng | PF | Từ | Đến | Đạt |
|---:|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | H1 | fractal | khong | atr_sl20_tp40 | 91.44% | 31.14% | 3371 | 42.27% | 1.36 | 2014-01-02 | 2026-10-12 | có |
| 2 | H1 | fractal | khong | atr_sl15_tp30 | 89.24% | 34.40% | 5596 | 39.08% | 1.25 | 2014-01-02 | 2026-10-12 | có |
| 3 | H1 | fractal | khong | atr_sl20_tp20 | 88.59% | 38.02% | 6719 | 55.71% | 1.21 | 2014-01-02 | 2026-10-12 | có |
| 4 | H1 | fractal | ema_trend_55 | atr_sl20_tp40 | 87.67% | 28.55% | 3248 | 41.19% | 1.30 | 2014-01-02 | 2026-10-12 | có |
| 5 | H1 | fractal | khong | atr_sl20_time24 | 87.36% | 35.11% | 4760 | 44.31% | 1.25 | 2014-01-02 | 2026-10-12 | có |
| 6 | H1 | fractal | ema_trend_55 | atr_sl15_tp30 | 87.12% | 40.99% | 5233 | 38.72% | 1.24 | 2014-01-02 | 2026-10-12 | có |
| 7 | H1 | fractal | ema_trend_200 | atr_sl20_tp40 | 86.83% | 30.74% | 2928 | 40.92% | 1.33 | 2014-01-02 | 2026-10-12 | có |
| 8 | H1 | fractal | ema_trend_55 | atr_sl20_tp20 | 84.65% | 66.23% | 6224 | 55.21% | 1.22 | 2014-01-02 | 2026-10-12 | có |
| 9 | H1 | fractal | ema_trend_55 | atr_sl20_time24 | 84.04% | 55.30% | 4417 | 43.49% | 1.23 | 2014-01-02 | 2026-10-12 | có |
| 10 | H1 | fractal | ema_trend_200 | atr_sl15_tp30 | 83.73% | 39.04% | 4492 | 38.49% | 1.22 | 2014-01-02 | 2026-10-12 | có |
| 11 | H1 | donchian_20 | ema_trend_55 | atr_sl20_tp40 | 83.35% | 23.87% | 2526 | 42.00% | 1.26 | 2014-01-02 | 2026-10-12 | có |
| 12 | H1 | donchian_20 | ema_trend_200 | atr_sl20_tp40 | 83.17% | 24.06% | 2180 | 42.43% | 1.31 | 2014-01-02 | 2026-10-12 | có |
| 13 | H1 | donchian_20 | khong | atr_sl20_tp40 | 83.12% | 25.29% | 2561 | 41.90% | 1.26 | 2014-01-02 | 2026-10-12 | có |
| 14 | H1 | donchian_55 | khong | atr_sl15_tp30 | 82.41% | 36.36% | 2011 | 43.96% | 1.40 | 2014-01-02 | 2026-10-12 | có |
| 15 | H1 | donchian_55 | ema_trend_55 | atr_sl15_tp30 | 82.41% | 36.36% | 2011 | 43.96% | 1.40 | 2014-01-02 | 2026-10-12 | có |
| 16 | H1 | donchian_55 | ema_trend_200 | atr_sl15_tp30 | 82.22% | 32.72% | 1901 | 44.24% | 1.42 | 2014-01-02 | 2026-10-12 | có |
| 17 | H1 | fractal | dow_tru_thu6 | atr_sl20_tp40 | 82.05% | 25.64% | 2980 | 40.50% | 1.21 | 2014-01-02 | 2026-10-12 | có |
| 18 | H1 | fractal | mua_vu_8_2 | atr_sl20_tp40 | 81.90% | 31.20% | 1850 | 43.19% | 1.41 | 2014-01-02 | 2026-10-12 | có |
| 19 | H1 | donchian_20 | ema_trend_55 | atr_sl15_tp30 | 81.32% | 30.78% | 3335 | 40.39% | 1.22 | 2014-01-02 | 2026-10-12 | có |
| 20 | H1 | fractal | dow_tru_thu6 | atr_sl20_tp20 | 81.10% | 63.14% | 5602 | 55.07% | 1.19 | 2014-01-02 | 2026-10-12 | có |
| 21 | H1 | donchian_20 | khong | atr_sl15_tp30 | 80.78% | 34.58% | 3419 | 40.07% | 1.21 | 2014-01-02 | 2026-10-12 | có |
| 22 | H1 | donchian_20 | ema_trend_55 | atr_sl20_time24 | 80.76% | 29.14% | 2977 | 45.55% | 1.22 | 2014-01-02 | 2026-10-12 | có |
| 23 | H1 | donchian_55 | ema_trend_200 | atr_sl20_tp40 | 80.74% | 28.44% | 1570 | 43.82% | 1.36 | 2014-01-02 | 2026-10-12 | có |
| 24 | H1 | fractal | ema_trend_200 | atr_sl20_tp20 | 80.44% | 59.17% | 5391 | 55.20% | 1.30 | 2014-01-02 | 2026-10-12 | có |
| 25 | H1 | donchian_20 | ema_trend_200 | atr_sl15_tp30 | 80.32% | 28.77% | 2814 | 40.90% | 1.25 | 2014-01-02 | 2026-10-12 | có |

## 4. Tốt nhất mỗi họ tín hiệu (không swap)

| Họ / vào | Khung | Lọc | Quản trị | CAGR kép | DD tối đa | Lệnh | Thắng | PF | Đạt |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| fractal | H1 | khong | atr_sl20_tp40 | 91.44% | 31.14% | 3371 | 42.27% | 1.36 | có |
| donchian_20 | H1 | ema_trend_55 | atr_sl20_tp40 | 83.35% | 23.87% | 2526 | 42.00% | 1.26 | có |
| donchian_55 | H1 | khong | atr_sl15_tp30 | 82.41% | 36.36% | 2011 | 43.96% | 1.40 | có |
| gia_cat_sma50 | H1 | ema_trend_55 | atr_sl20_tp40 | 34.69% | 61.63% | 1620 | 38.70% | 1.14 | có |
| macd | H1 | adx_25 | atr_sl15_tp30 | 30.24% | 66.00% | 1053 | 40.36% | 1.08 | có |
| orb_london | H1 | ema_trend_55 | atr_sl20_tp40 | 26.28% | 47.57% | 2512 | 36.74% | 1.09 | có |
| ibs | H1 | adx_25 | atr_sl20_tp40 | 25.34% | 75.84% | 2061 | 37.02% | 1.03 | có |
| adx_di | H1 | ema_trend_55 | atr_sl20_tp40 | 24.82% | 29.07% | 1107 | 39.02% | 1.13 | có |
| luoi_dca | H1 | ema_trend_55 | luoi_b1.5_c4_tp1.2_sl5.0 | 24.12% | 19.72% | 8293 | 92.23% | 1.30 | có |
| orb_ny | H1 | chi_mua | atr_sl20_tp40 | 17.28% | 54.17% | 1003 | 38.09% | 1.15 | có |
| orb_a | H1 | adx_25 | atr_sl20_tp40 | 16.36% | 34.90% | 819 | 38.71% | 1.10 | có |
| mua_giu | M15 | khong | mua_giu_khong_don_bay | 14.16% | 29.15% | 1 | 100.00% | 99.00 | có |
| ichimoku_tk | H4 | dow_tru_thu6 | atr_sl20_trail15 | 13.93% | 22.99% | 580 | 45.34% | 1.39 | có |
| ema_9_21 | H1 | adx_25 | atr_sl20_eod | 12.49% | 29.16% | 786 | 48.60% | 1.20 | có |
| orb_london_anh | H1 | adx_25 | atr_sl20_time24 | 7.79% | 68.36% | 1063 | 40.92% | 1.08 | không |
| bb_fade | H4 | chi_mua | atr_sl20_tp40 | 6.85% | 31.01% | 379 | 38.26% | 1.22 | không |
| zscore_20_2 | H4 | chi_mua | atr_sl20_tp40 | 6.85% | 31.01% | 379 | 38.26% | 1.22 | không |
| ema_21_55 | H1 | ema_trend_200 | atr_sl15_tp30 | 6.37% | 58.27% | 860 | 36.51% | 1.08 | không |
| rsi_30_70 | H4 | phien_ny | atr_sl20_trail15 | 5.72% | 11.77% | 246 | 44.72% | 1.41 | không |
| sma_50_200 | H4 | ema_trend_200 | atr_sl20_trail15 | 2.82% | 11.93% | 108 | 43.52% | 1.57 | không |
| rsi_20_80 | H4 | phien_a | atr_sl20_trail15 | 2.44% | 7.41% | 50 | 48.00% | 1.97 | không |

Nhóm **hồi quy** (RSI, Bollinger, z-score) phần lớn không ĐẠT. IBS ĐẠT ở vài tổ hợp H1/H4 nhưng DD cao (51–76%) và PF sát 1,0. Nhóm **xu hướng chậm** (SMA 50/200, EMA 21/55) không ĐẠT. Phá vỡ Donchian / fractal / ORB London trên H1–H4 là nhóm ĐẠT nhiều nhất.

## 5. Tách giai đoạn — đường vốn liên tục (không reset chỉ báo)

Tổ hợp **H1 donchian_20 + ema_trend_55 + sl 2 ATR / tp 4 ATR**, không swap, phí như trên. P&L từng năm chia cho vốn tại đầu năm (đường vốn chạy suốt 2014–2026).

| Năm | Lệnh | Thắng | Lợi nhuận năm |
|---|---:|---:|---:|
| 2014 | 188 | 41.5% | 107.93% |
| 2015 | 164 | 52.4% | 453.37% |
| 2016 | 131 | 64.9% | 955.05% |
| 2017 | 128 | 67.2% | 351.73% |
| 2018 | 180 | 40.0% | 19.13% |
| 2019 | 211 | 36.0% | 3.33% |
| 2020 | 197 | 43.7% | 41.12% |
| 2021 | 223 | 33.2% | 0.12% |
| 2022 | 230 | 37.4% | 12.98% |
| 2023 | 223 | 39.5% | 12.20% |
| 2024 | 234 | 35.0% | 4.42% |
| 2025 | 249 | 38.2% | 23.18% |
| 2026 | 168 | 39.9% | 48.47% |

Cả mẫu 2014-01-02 → 2026-10-12: CAGR kép **83,35%**, DD **23,87%**, 2526 lệnh, thắng 42,00%, PF 1,26, vốn cuối 23.086.353 USD. Có swap đủ: CAGR **79,20%**, DD **27,05%**, cùng 2526 lệnh (ĐẠT).

Lợi nhuận năm 2015–2017 cực lớn (453%, 955%, 352%) vì tỷ lệ thắng 52–67% trong thị trường vàng có xu hướng, kết hợp rủi ro 2% kép. Từ sau giai đoạn đó:

- 2018-01 → 2026-10 (vốn đầu năm 2018 = 5.483.842 USD, vốn cuối 23.086.353 USD, 8,78 năm): CAGR kép **17,79%** (23.086.353 / 5.483.842, 8,78 năm) (vẫn > 10%).
- 2022-01 → 2026-10 (vốn đầu 2022 = 9.537.413 USD): CAGR kép **20,35%** (23.086.353 / 9.537.413, 4,77 năm).
- Năm yếu: 2019 +3,33%, 2021 +0,12%, 2024 +4,42%. Không có năm âm trên tổ hợp này trong mẫu (P&L theo năm dương).

Các tổ hợp fractal H1 có CAGR cả mẫu còn cao hơn (tới 91,44% không swap; 88,62% có swap) nhưng nhiều lệnh hơn (3.371–6.719) và DD khi thêm swap có thể lên 77%. Donchian 20 + lọc EMA 55 là tổ hợp cân hơn (DD 23,9% không swap / 27,1% có swap).

## 6. Chạy lại top với swap đầy đủ

| Khung | Vào | Lọc | Quản trị | CAGR kép | DD tối đa | Lệnh | PF | Đạt (có swap) |
|---|---|---|---|---:|---:|---:|---:|---|
| H1 | fractal | khong | atr_sl20_tp40 | 88.62% | 31.40% | 3371 | 1.35 | có |
| H1 | fractal | khong | atr_sl15_tp30 | 86.43% | 57.30% | 5596 | 1.25 | có |
| H1 | fractal | ema_trend_55 | atr_sl20_tp40 | 84.14% | 31.96% | 3248 | 1.29 | có |
| H1 | fractal | ema_trend_55 | atr_sl15_tp30 | 83.86% | 55.52% | 5233 | 1.23 | có |
| H1 | fractal | khong | atr_sl20_tp20 | 83.32% | 77.57% | 6719 | 1.25 | có |
| H1 | fractal | ema_trend_200 | atr_sl20_tp40 | 81.41% | 66.60% | 2928 | 1.36 | có |
| H1 | donchian_55 | khong | atr_sl15_tp30 | 80.49% | 50.55% | 2011 | 1.39 | có |
| H1 | donchian_55 | ema_trend_55 | atr_sl15_tp30 | 80.49% | 50.55% | 2011 | 1.39 | có |
| H1 | donchian_20 | ema_trend_200 | atr_sl20_tp40 | 79.40% | 39.91% | 2180 | 1.30 | có |
| H1 | donchian_20 | ema_trend_55 | atr_sl20_tp40 | 79.20% | 27.05% | 2526 | 1.25 | có |
| H1 | donchian_20 | khong | atr_sl20_tp40 | 78.78% | 28.47% | 2561 | 1.24 | có |
| H1 | fractal | khong | atr_sl20_time24 | 78.39% | 74.80% | 4760 | 1.23 | có |
| H1 | fractal | ema_trend_200 | atr_sl15_tp30 | 65.75% | 87.35% | 4492 | 1.25 | không |
| H1 | fractal | ema_trend_55 | atr_sl20_tp20 | 65.19% | 77.28% | 6224 | 1.24 | có |
| H1 | fractal | ema_trend_55 | atr_sl20_time24 | 55.90% | 77.21% | 4417 | 1.19 | có |

Hầu hết top H1 vẫn ĐẠT sau swap; một tổ hợp fractal + ema 200 + sl 1,5 ATR **trượt** vì DD 87,35%.

## 7. Lưới / DCA

Có **15** biến thể lưới ĐẠT (chủ yếu H1). Tốt nhất: H1 + lọc EMA 55 + bước 1,5 ATR, tối đa 4 chân, TP 1,2 ATR, SL tổng 5 ATR: CAGR kép **24,12%**, DD **19,72%**, 8293 lần đóng lưới, thắng 92,23%, PF 1,30. Cảnh báo: mô phỏng lưới trên nến H1 (thêm chân tại giá mở) **lạc quan hơn tick**; tỷ lệ thắng rất cao có thể không giữ được trên tester tick thật.

## 8. Order flow Fxaurum (đo 19:04–19:20 UTC+7)

Đã kéo xong GCZ6: 1.648 nến 1h, 96.960 nến 1m, 191.044 sweep, 193.463 absorption, 6.422 iceberg, 82.175 big trades, 0 lỗi. Chi tiết: `bao_cao/ORDERFLOW.md`.

Basis GCZ6 − GOLD.i (827 giờ trùng, 20/08–12/10/2026 UTC): trung vị **+38,96 USD**, trung bình +39,95, min −57,05, max +101,74; trung vị tuần giảm từ +61,40 (23/08) xuống +20,51 (18/10). Đây là hợp đồng tháng 12, phải tính lại mỗi lần.

ORB London 14:00–20:00 VN trên nến 1 phút GC, 20/08–27/11/2026 (0,271 năm), SL 2 ATR / TP 4 ATR, chốt trong ngày, phí M1: **261 lệnh**, thắng 32,57%, PF **0,88**, lợi nhuận cả đoạn **−40,65%**, DD 57,87% — không ĐẠT. Thêm lọc sweep 5 phút cùng chiều: **13 lệnh**, PF 0,55, lợi nhuận −9,16%, DD 18,98% — không ĐẠT.

## 9. Việc còn lại

- Chưa chạy xác nhận MetaTrader 5 tick thật trên khe p3/p4 (khe đã đăng nhập XMGlobal-MT5 10; lúc kiểm 19:01 UTC+7 RAM trống 26,44 GB, đủ để mở tester).
- Chưa ghép GEX/wall (thiếu lịch sử tường đủ dài). Lọc order flow cần thử lại với ngưỡng khối lượng (số sweep thô rất lớn).

