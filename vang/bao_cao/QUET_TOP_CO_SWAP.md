# Top tổ hợp ĐẠT — chạy lại có swap đầy đủ

Viết lúc 2026-11-27, giờ Việt Nam (UTC+7). Phí XM GOLD.i# (micro quy về #): spread trung vị H1 16 điểm (0,16 USD/ounce) khi cột spread nến = 0; khi có cột spread (từ 2018-10-10) dùng spread nến. Mỗi chiều = nửa spread + trượt 0,5×spread (giả định thận trọng, chưa đo demo). Hoa hồng 0. Mặc định swap = 0 như tester Ultra Low (DISABLED); một phần tổ hợp tốt nhất được chạy lại với swap đủ (long −83,83 USD/lot/đêm, short +20,64, nhân 3 thứ Tư).

- Tổng tổ hợp đã đo: **15**
- Tổ hợp ĐẠT (CAGR kép > 10%/năm, DD tối đa < 80%, ≥ 20 lệnh, vốn cuối > 0): **14**

## Mua giữ (không đòn bẩy, đã trừ spread+trượt vào/ra)

## Tổ hợp tốt nhất (sắp theo ĐẠT, rồi CAGR)

| Hạng | Khung | Vào | Lọc | Quản trị | CAGR | DD | Lệnh | Thắng | PF | Từ | Đến | Swap | Đạt |
|---:|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|---|
| 0 | H1 | fractal | khong | atr_sl20_tp40 | 88.62% | 31.40% | 3371 | 42.3% | 1.35 | 2014-01-02 | 2026-10-12 | True | có |
| 1 | H1 | fractal | khong | atr_sl15_tp30 | 86.43% | 57.30% | 5596 | 39.1% | 1.25 | 2014-01-02 | 2026-10-12 | True | có |
| 3 | H1 | fractal | ema_trend_55 | atr_sl20_tp40 | 84.14% | 31.96% | 3248 | 41.2% | 1.29 | 2014-01-02 | 2026-10-12 | True | có |
| 5 | H1 | fractal | ema_trend_55 | atr_sl15_tp30 | 83.86% | 55.52% | 5233 | 38.7% | 1.23 | 2014-01-02 | 2026-10-12 | True | có |
| 2 | H1 | fractal | khong | atr_sl20_tp20 | 83.32% | 77.57% | 6719 | 55.7% | 1.25 | 2014-01-02 | 2026-10-12 | True | có |
| 6 | H1 | fractal | ema_trend_200 | atr_sl20_tp40 | 81.41% | 66.60% | 2928 | 40.9% | 1.36 | 2014-01-02 | 2026-10-12 | True | có |
| 13 | H1 | donchian_55 | khong | atr_sl15_tp30 | 80.49% | 50.55% | 2011 | 44.0% | 1.39 | 2014-01-02 | 2026-10-12 | True | có |
| 14 | H1 | donchian_55 | ema_trend_55 | atr_sl15_tp30 | 80.49% | 50.55% | 2011 | 44.0% | 1.39 | 2014-01-02 | 2026-10-12 | True | có |
| 11 | H1 | donchian_20 | ema_trend_200 | atr_sl20_tp40 | 79.40% | 39.91% | 2180 | 42.4% | 1.30 | 2014-01-02 | 2026-10-12 | True | có |
| 10 | H1 | donchian_20 | ema_trend_55 | atr_sl20_tp40 | 79.20% | 27.05% | 2526 | 42.0% | 1.25 | 2014-01-02 | 2026-10-12 | True | có |
| 12 | H1 | donchian_20 | khong | atr_sl20_tp40 | 78.78% | 28.47% | 2561 | 41.9% | 1.24 | 2014-01-02 | 2026-10-12 | True | có |
| 4 | H1 | fractal | khong | atr_sl20_time24 | 78.39% | 74.80% | 4760 | 44.3% | 1.23 | 2014-01-02 | 2026-10-12 | True | có |
| 7 | H1 | fractal | ema_trend_55 | atr_sl20_tp20 | 65.19% | 77.28% | 6224 | 55.2% | 1.24 | 2014-01-02 | 2026-10-12 | True | có |
| 8 | H1 | fractal | ema_trend_55 | atr_sl20_time24 | 55.90% | 77.21% | 4417 | 43.5% | 1.19 | 2014-01-02 | 2026-10-12 | True | có |
| 9 | H1 | fractal | ema_trend_200 | atr_sl15_tp30 | 65.75% | 87.35% | 4492 | 38.5% | 1.25 | 2014-01-02 | 2026-10-12 | True | không |

## Tín hiệu vào — tổ hợp tốt nhất mỗi tín hiệu (mọi lọc/QT)

| Vào | Khung | Lọc | Quản trị | CAGR | DD | Lệnh | Đạt |
|---|---|---|---|---:|---:|---:|---|
| donchian_20 | H1 | ema_trend_200 | atr_sl20_tp40 | 79.40% | 39.91% | 2180 | có |
| donchian_55 | H1 | khong | atr_sl15_tp30 | 80.49% | 50.55% | 2011 | có |
| fractal | H1 | khong | atr_sl20_tp40 | 88.62% | 31.40% | 3371 | có |
