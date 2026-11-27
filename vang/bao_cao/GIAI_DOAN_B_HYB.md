# Giai đoạn B — cổng HYB+AG sang vàng XM (đo lường)

Máy xử lý lệnh: HYB + AG 1,5x (thiết kế 26/11, `E:\\backtests\\sp500_sys\\`). Cổng vàng: ATR M15, pv=100 USD / 1,00 giá / 1,00 lot, bước lot 0,01 (K=3 → vào 0,03 lot, tương đương ATR-scaled với 3×0,1 lot US500 pv=1). Spread mặc định 0,20 giá (20 pts M1). Vốn 10.000. Không SL cứng. **Không đặt lệnh thật** (chỉ nhật ký bóng).

- Dữ liệu: XM GOLD.i# M1 2026-06-01 05:00:00 → 2026-11-26 19:04:00, đổi Europe/Athens → UTC+7.
- IS: trước 2026-10-01; OOS: từ 2026-10-01.
- Tín hiệu data (cải thiện điểm S và mức VWAP/POC quy CFD): cụm big-trade ≥50, từ chối VWAP, đảo sweep (kho flow 18–27/11).

## Kết quả Jun–Nov (và IS/OOS, spread ×2)

| ten | net | maxdd | dd_pct | maxfl | is_net | oos_net | net_sprx2 | dd_sprx2 | sharpe | dsr | n_ro | blown | dat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline_HYB_AG | 78.82 | 5762.09 | 57.62 | -5124.73 | -1924.51 | 2003.33 | -750.55 | 6078.19 | 0.018 | 0.0 | 1049 | False | True |
| data_S_plus | -4147.51 | 5763.99 | 57.64 | -5124.73 | -1935.04 | -2212.48 | -4914.3 | 6380.16 | -0.87 | 0.0 | 995 | False | False |
| bai_hoc_K5_c115_AG2 | 1274.64 | 11549.74 | 115.5 | -10428.48 | 2181.49 | -906.85 | -42.93 | 10941.97 | 0.14 | 0.0 | 1070 | True | False |
| lan_coef115 | -5347.92 | 7215.12 | 72.15 | -4459.81 | -4107.48 | -1240.44 | -1084.71 | 4844.44 | -1.194 | 0.0 | 523 | False | False |
| lan_G2 | -3020.36 | 5389.49 | 53.89 | -5262.22 | -1238.21 | -1782.15 | -3684.79 | 5894.74 | -0.625 | 0.0 | 885 | False | False |
| lan_th2 | -6196.21 | 9500.51 | 95.01 | -7483.03 | -6128.58 | -67.63 | -7242.04 | 9724.67 | -0.944 | 0.0 | 1026 | False | False |
| lan_K5 | -9184.81 | 12889.77 | 128.9 | -11530.2 | -7925.42 | -1259.39 | -431.77 | 11721.32 | -1.033 | 0.0 | 892 | True | False |

Tiêu chí pass: lãi ròng > 0 và max DD < 80% vốn 10.000, không cháy (equity ≤ 0).

## 11 kịch bản stress

7 cửa sổ sập theo lịch US500, nến M15 từ parquet XAUUSD (mốc giờ parquet, **không phải** máy chủ XM), scale về 4000. 2 gap và 2 grind trên M1 GOLD.i# Jun–Nov.

| cfg | scenario | net | maxdd | dd_pct | maxfl | blown | dat | n_nen |
|---|---|---|---|---|---|---|---|---|
| baseline_HYB_AG | gap-10% tai day von | 4284.58 | 5723.09 | 57.23 | -5124.73 | False | True | nan |
| data_S_plus | gap-10% tai day von | 4097.83 | 5724.99 | 57.25 | -5124.73 | False | True | nan |
| baseline_HYB_AG | gap-20% tai day von | 13444.52 | 5723.09 | 57.23 | -5124.73 | False | True | nan |
| data_S_plus | gap-20% tai day von | 14217.28 | 5724.99 | 57.25 | -5124.73 | False | True | nan |
| baseline_HYB_AG | grind-20%/60ngay | 5831.44 | 2654.72 | 26.55 | -2810.82 | False | True | nan |
| data_S_plus | grind-20%/60ngay | 2702.32 | 4009.13 | 40.09 | -3635.87 | False | True | nan |
| baseline_HYB_AG | grind-35%/120ngay | 4737.91 | 2767.75 | 27.68 | -2805.82 | False | True | nan |
| data_S_plus | grind-35%/120ngay | 1441.84 | 4119.29 | 41.19 | -3901.42 | False | True | nan |
| baseline_HYB_AG | Q4-2018 | 1845.79 | 2145.47 | 21.45 | -2002.88 | False | True | 10072.0 |
| data_S_plus | Q4-2018 | 1845.79 | 2145.47 | 21.45 | -2002.88 | False | True | 10072.0 |
| baseline_HYB_AG | Covid 02-04/2020 | -1162.31 | 6757.7 | 67.58 | -7284.76 | False | False | 11264.0 |
| data_S_plus | Covid 02-04/2020 | -1162.31 | 6757.7 | 67.58 | -7284.76 | False | False | 11264.0 |
| baseline_HYB_AG | 2022 H1 | -18154.0 | 22583.45 | 225.83 | -11041.14 | True | False | 14012.0 |
| data_S_plus | 2022 H1 | -18154.0 | 22583.45 | 225.83 | -11041.14 | True | False | 14012.0 |
| baseline_HYB_AG | 2022 08-10 | 2228.15 | 1202.05 | 12.02 | -1495.43 | False | True | 8155.0 |
| data_S_plus | 2022 08-10 | 2228.15 | 1202.05 | 12.02 | -1495.43 | False | True | 8155.0 |
| baseline_HYB_AG | 08-10/2023 | -1133.45 | 2929.76 | 29.3 | -2420.23 | False | False | 9332.0 |
| data_S_plus | 08-10/2023 | -1133.45 | 2929.76 | 29.3 | -2420.23 | False | False | 9332.0 |
| baseline_HYB_AG | 07-08/2024 | 1329.44 | 980.69 | 9.81 | -1027.69 | False | True | 5326.0 |
| data_S_plus | 07-08/2024 | 1329.44 | 980.69 | 9.81 | -1027.69 | False | True | 5326.0 |
| baseline_HYB_AG | 02-04/2025 | 4421.33 | 1658.24 | 16.58 | -1725.73 | False | True | 9614.0 |
| data_S_plus | 02-04/2025 | 4421.33 | 1658.24 | 16.58 | -1725.73 | False | True | 9614.0 |

- baseline_HYB_AG: sống 10/11 kịch bản (không cháy và DD<80%). Lãi/lỗ tệ nhất -18154 USD.
- data_S_plus: sống 10/11 kịch bản (không cháy và DD<80%). Lãi/lỗ tệ nhất -18154 USD.

Nhật ký bóng: `/workspace/brain2/vang/ket_qua/shadow_hyb_vang.csv` (chỉ ghi, không đặt lệnh).
Chạy trong 16.3 giây.

Lưu ý: OptionsDb GCZ6 chỉ 19–20/11 và chưa đọc được GEX/max pain qua API trong phiên này, nên trọng số quyền chọn (1,5) gần như không có mức thật.
