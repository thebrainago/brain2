# OnlyUJ 2245675 — luật V1 PASS

ĐO 09/11/2026. Không commit (Anh).

## Tín hiệu gốc (MQL5)
- Symbol: USDJPY · n=751 · buy% 50.7 · e/c Cổng 0 = 1.25 (sát ngưỡng)
- hang: don_le · không SL/TP cố định trên export

## Luật tái tạo (match 65.1%)
1. Lấy range **Asia phiên trước**: H1 giờ 0–7 (TZ HistData NY+7).
2. Từ giờ **8** ngày hiện tại: Buy Stop = Asia high, Sell Stop = Asia low (whichever hits first).
3. SL **100 pip** (1.00), TP **150 pip** (1.50) — base; WF nhân slm/tpm ∈ {0.75,1,1.25(,1.5)} chỉ trên train 12 tháng.
4. Hold tối đa 30 ngày; risk 1% equity/lệnh; phí XM micro.

## V1 OOS (2008–2026 H1)
| | |
|---|---|
| CAGR | **+32.01%** |
| DD | **17.22%** |
| Sharpe | **1.62** |
| trades/yr | 69.2 |
| beat random | có (rand p50 −2.8%) |

## Bước tiếp
- V2: ổn định TZ broker vs NY7; kiểm tra chi phí IC vs XM; OOS theo năm.
- Không tăng lot / không lưới.

## Ổn định theo năm (train năm trước → test năm, tiếp nối equity)

- Năm dương: **15/17**
- Năm âm: 2019 (-10.0%), 2020 (-4.0%)
- Equity tích lũy (V0=10k, risk 1%): **712,489** cuối 2026

| Năm | n | ret% | slm | tpm |
|---:|---:|---:|---:|---:|
| 2010 | 41 | +19.65 | 0.75 | 1.5 |
| 2011 | 43 | +7.30 | 0.75 | 0.75 |
| 2012 | 39 | +5.51 | 0.75 | 0.75 |
| 2013 | 102 | +47.09 | 0.75 | 0.75 |
| 2014 | 44 | +5.84 | 0.75 | 1.25 |
| 2015 | 74 | +25.58 | 0.75 | 0.75 |
| 2016 | 114 | +67.53 | 0.75 | 0.75 |
| 2017 | 49 | +24.32 | 0.75 | 1.25 |
| 2018 | 56 | +23.49 | 0.75 | 0.75 |
| 2019 | 42 | -10.01 | 0.75 | 0.75 |
| 2020 | 35 | -3.96 | 1.25 | 1 |
| 2021 | 34 | +8.66 | 0.75 | 0.75 |
| 2022 | 94 | +30.53 | 1.25 | 0.75 |
| 2023 | 115 | +72.34 | 0.75 | 0.75 |
| 2024 | 118 | +100.13 | 0.75 | 0.75 |
| 2025 | 91 | +62.68 | 0.75 | 1.25 |
| 2026 | 59 | +52.11 | 0.75 | 0.75 |
