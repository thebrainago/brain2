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
