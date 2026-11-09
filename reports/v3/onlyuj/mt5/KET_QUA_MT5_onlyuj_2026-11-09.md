# OnlyUJ (MQL5 2245675) V3 MT5 — USDJPY# H1 (09/11/2026, slot g12)

EA `OnlyUJ_V3.mq5` (chỉ ở slot g12): range Asia H1 giờ 0–7 cùng ngày (giờ server), từ giờ 8 giá vượt đỉnh → MUA / thủng đáy → BÁN, 1 lệnh/ngày, 1 vị thế; SL 1,00×slm, TP 1,50×tpm (JPY); rủi ro 1% equity/lệnh (OrderCalcProfit); giữ tối đa 30 ngày.
Lịch slm/tpm: **theo năm** từ `v1_onlyuj_by_year.json` (train năm trước), 2009 = 0,75/1,0 (params_sample). Lịch quý đầy đủ của V1 không có file → chưa đúng WF 12/3 quý.
Swap ước: XM micro USDJPY mua +2,11 / bán −29,59 điểm/lot/đêm ×3 thứ 4, 1 điểm/lot = 0,6326 USD.

| Lượt | Tick thật | Lãi ròng | CAGR kép | CAGR sau swap ước | DD max/tương đối | PF | Lệnh | Thắng % | Giữ max | Lot max |
|---|---|---|---|---|---|---|---|---|---|---|
| B 2024.01–2026.10 | 99% | −320,07 | −1,14% | −4,68% (−949,9) | 21,57% / 21,57% | 0,99 | 379 | 36,15% | 14,2 ngày | 0,24 |
| A 2009.01–2026.10 | 15% | +1.339,12 | 0,71% | −3,20% (−5.740,4) | 33,73% / 33,73% | 1,01 | 1.541 | — | 22,0 ngày | 0,29 |

Python V1: CAGR +32,01%, DD 17,22%, theo năm 2024 +100,13%, 2025 +62,68%. Kiểm độc lập trên box (HistData M5 2024–10/2026, cùng luật, SL chạm trước): (0,75/0,75) 306 lệnh, thắng 38,6%, kỳ vọng −0,033R/lệnh; (0,75/1,25) 232 lệnh, +0,196R → khớp MT5, không khớp Python. Mã Python V1 của OnlyUJ không còn trên box để soi lỗi.

**Kết luận: TRƯỢT V3** (A và B đều CAGR < 10%).
