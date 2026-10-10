# Bộ EA mở rộng `mau_thu/mo_rong/` — nguồn và giấy phép

15 EA MT5 một file, lấy nguyên văn (không sửa) từ repo GitHub công khai **giấy phép MIT**
(bản sao LICENSE đặt trong từng thư mục, đúng điều kiện MIT: giữ thông báo bản quyền +
giấy phép). Chọn EA đơn giản một file, bỏ khung lớn (vd. geraked/metatrader5 dùng
`EAUtils.mqh` chung). Tải 10/10/2026 (`git clone --depth 1`).

| thư mục | repo | commit | bản quyền | file |
|---|---|---|---|---|
| santiago-cruzlopez | github.com/santiago-cruzlopez/MQL5 (`1_Expert_Advisors_EA/`) | 752b57e7bf245de282233fb9f9e5a6c1eb9fd4dd | (c) 2025 Santiago Cruz | 01_RSI_V1, 011_RSI_V2, 012_MA_V1, 013_Bollinger_Bands, 014_RSI_MA_V2, 015_Triple_MA, 016_CCI_2MAVG, 017_Ichi_ATR, 018_Price_Action, 019_ADX, 05_RSI_MA |
| terencebeauj | github.com/terencebeauj/Trading_bot_BollingerBands | 839fc5eac8595094a3cf9dcfb53664f281dbf225 | (c) 2020 Terence Beaujour | Basic_Bollinger_Bands |
| forexstrategystudio | github.com/forexstrategystudio/mql5-expert-advisors (`EMA_Crossover/`) | 7fe2e02ce96ee98352dfaaec6deaad46e6371268 | (c) 2026 Forex Strategy Studio | EMA Crossover |
| viprasol-tech | github.com/Viprasol-Tech/mt5-expert-advisor (`src/`) | 8876e2acbe3fd5726b97f8cfce98d4e585025e17 | (c) 2025 Viprasol Tech Private Limited | ViprasolMACrossEA |
| je-zhou | github.com/je-zhou/Forex-Algotrading-Strategies--MQL5- (`Strategies/Box Breakout/Deprecated/`) | 839a661ef7b6c0e01963aacd2598491fd1613a7a | (c) 2024 Jerry Zhou | Box Breakout v1.0 |

Dùng để ĐO lớp đọc MQL5 tổng quát hoá ra ngoài 10 file mẫu (`python mau_thu/do_moc_rong.py`),
không dùng làm đáp án để chỉnh bộ đọc cho vừa. Include ngoài (`NewC.mqh`, `Trail.mqh` của
santiago) không có trong repo — không cần cho phần vào lệnh đang đo.
