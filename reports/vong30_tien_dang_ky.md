# Vòng 30 — TIỀN ĐĂNG KÝ (sinh tự động từ giai đoạn 1, TRƯỚC khi xem giai đoạn 2). MÔ PHỎNG

Giai đoạn 1: H1/H4 trước 2025-06-01, D1 trước 2015-04-01. Ngưỡng sóng (p50/p70/p90, tỉ lệ hồi) chỉ từ GĐ1, ZigZag k=2 ATR.
Phí XM Ultra Low: spread trung vị H1 (bps) + 1 bps trượt khứ hồi; swap 0 (nhóm # DISABLED). Gộp 12 tài sản, một cấu hình chung mỗi khung.
Volume: CHƯA ĐO ĐƯỢC — cột tick_volume HistData chỉ là số nến M1 trong nến M5 (≤5), Yahoo D1 không có; bộ phát hiện volume bị loại.
Chọn: ô GĐ1 có n ≥ 30 và PF > 1, xếp theo tb_bps×√n, tối đa 10 mỗi chiều. Ô kiểm ở GĐ2 (một phía t, lợi nhuận/lệnh > 0).
Holm cộng dồn: họ trước 13000 + 6 ô luật p70/p90 (3 khung × 2) + 3 ô luật thuận gốc + số tổ hợp dưới đây.

| # | Chiều | Khung | Tổ hợp | GĐ1 n | win % | PF | bps/lệnh |
|---|---|---|---|---|---|---|---|
| 1 | nguoc | D1 | ibs+nen | 99 | 47.5 | 1.2 | 21.84 |
| 2 | nguoc | H4 | p90+macd | 59 | 18.6 | 2.2 | 23.73 |
| 3 | nguoc | H4 | rsi_dk+macd | 112 | 33.0 | 1.33 | 14.35 |
| 4 | nguoc | H1 | pin+macd | 124 | 38.7 | 1.52 | 10.28 |
| 5 | nguoc | D1 | p90+macd | 74 | 14.9 | 1.24 | 13.19 |
| 6 | nguoc | H1 | p90+macd | 216 | 16.7 | 1.53 | 5.94 |
| 7 | nguoc | H1 | p70+pin | 358 | 35.8 | 1.15 | 2.83 |
| 8 | nguoc | H1 | pin+gio | 574 | 39.4 | 1.07 | 1.38 |
| 9 | nguoc | D1 | pin+rsi_dk | 60 | 31.7 | 1.03 | 4.05 |
| 10 | nguoc | H1 | macd+gio | 1078 | 42.4 | 1.04 | 0.91 |
| 11 | thuan | D1 | nen | 102 | 26.5 | 1.8 | 42.15 |
| 12 | thuan | D1 | macd | 316 | 19.9 | 1.36 | 21.65 |
| 13 | thuan | D1 | nen+ma200 | 49 | 32.7 | 1.87 | 50.28 |
| 14 | thuan | D1 | pin+ma200 | 118 | 25.4 | 1.54 | 26.79 |
| 15 | thuan | D1 | pin | 204 | 23.5 | 1.38 | 19.36 |
| 16 | thuan | D1 | macd+ma200 | 184 | 20.7 | 1.31 | 19.28 |
| 17 | thuan | D1 | nen+ibs | 53 | 22.6 | 1.6 | 35.49 |
| 18 | thuan | D1 | ma200 | 459 | 21.4 | 1.18 | 11.72 |
| 19 | thuan | D1 | nen+pin | 32 | 25.0 | 1.92 | 37.73 |
| 20 | thuan | D1 | macd+pin | 55 | 20.0 | 1.37 | 18.3 |
