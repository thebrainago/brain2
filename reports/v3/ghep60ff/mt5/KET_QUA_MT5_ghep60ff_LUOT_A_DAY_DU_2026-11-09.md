# ghep60ff adxngang GBPCAD H1 — Lượt A đầy đủ 2009–2026 + lot theo vốn (09/11/2026 tối, slot g12)

**Dữ liệu:** XM GBPCAD# trên máy nhà trước 2018 chỉ 59–467 KB/năm, server không có thêm. Dukascopy từ IP nhà: 503/timeout sau ~116 ngày → dừng, không vượt.
Dùng HistData M1 GBPCAD 2008–2026.10.09 (cùng nguồn Python, giờ EST+7 cố định như Python) → custom symbol `GBPCAD_HD` (gốc GBPCAD#, spread cố định 58 điểm = p90 XM micro). Script `NapGBPCAD_HD.mq5` (chỉ ở slot g12), 6.875.443 nến M1.
Model=1 (1 minute OHLC, chất lượng lịch sử 98–100%, **không có tick thật**). Quy đổi CAD→USD bằng USDCAD lịch sử của server.

| Lượt | Dữ liệu/Model | Lãi ròng | CAGR kép | CAGR sau swap ước | DD max | DD tương đối | PF | Lệnh | Rổ | Giữ max | Lot max |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A_hd 2009.01–2026.10 (lot CSV cố định) | HistData M1 OHLC | +114.600,81 | 15,25% | 15,32% (+1.262,4) | 16.302,48 (18,72%) | 50,74% | 2,09 | 1.350 | 867 | 32,2 ngày | 7,41 |
| B_hd 2024.01–2026.10 (đối chứng) | HistData M1 OHLC | +31.538,54 | 67,11% | 67,72% | 70,54% | 70,54% | 2,54 | 260 | — | 30,0 | 7,41 |
| B 2024.01–2026.10 (đã chạy 21:01) | XM real tick 99% | +25.729,77 | 58,27% | 58,96% | 75,11% | 75,11% | 2,35 | 257 | 165 | 30,4 | 7,41 |
| A_von (lot × equity/10.000) | HistData M1 OHLC | −9.552,06 | cháy | — | 98,72% | 98,72% | 0,77 | 69 | — | 8,7 | 9,55 |
| B_von (lot × equity/10.000) | XM real tick 99% | −9.756,45 | cháy | — | 98,95% | 98,95% | 0,63 | 75 | — | 20,2 | 6,15 |

- A_von: stop-out 07/07/2011 (equity đã lên ~34,4k, rổ 4 tầng 9,55 lot). B_von: stop-out 13/01/2025.
- HistData M1 OHLC lạc quan hơn real tick trên cùng 2024–2026: CAGR 67,11% vs 58,27%, DD 70,54% vs 75,11%.
- Python (12,81%/46,69%) dùng lot cố định (py_lenh 45 micro không đổi) và tỉ giá CAD 0,712 (10/2026) cho mọi năm → lãi USD 2011–2014 thấp hơn MT5 (vd 2011: Python 10.654 USD/47,6 lot, MT5 19.220 USD/53,1 lot; USDCAD 2011 ≈ 1,0).

**Kết luận:** lot CSV cố định: A_hd ĐẠT (DD 50,74% < 80%, CAGR 15,32% > 10%, nhãn: M1 OHLC, không real tick), B real tick ĐẠT → **ĐẠT V3 có nhãn**. Lot theo vốn: CHÁY cả A và B → không dùng.
