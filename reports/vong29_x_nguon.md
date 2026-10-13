# Vòng 29 — khai thác X (Twitter) 13/10/2026 — MÔ PHỎNG
X MCP: 20 lệnh gọi (1 lỗi tên user), ~380 bài duy nhất đọc, 102 tài khoản. Chỉ lưu tóm tắt + URL.

## Tài khoản tín hiệu cao (thêm vào config/nguon_seeker.json, khoá `x_*`)
| Tài khoản | Hạng | Vì sao | Quét lại |
|---|---|---|---|
| @QuantifiedStrat | A | luật D1 đầy đủ (RSI, ToM, qua đêm, NR7, GLD inside-day) | tuần |
| @EmpiricaLab | A | chạy lại luật newsletter có phí, placebo vào ngẫu nhiên, Deflated Sharpe; code Discord | tuần |
| @crowcaw | B | dựng lại luật QQQ RSI4/EMA100/VWAP | tháng |
| @HelloNhuga | B | phê bình overfit, 20 hệ vàng → 2 sống | 2 tuần |
| @priceactionlab | B | tín hiệu mẫu giá ETF | tháng |
| @RB_Tradingltd, @WillyAlgoTrader (Pine gold breakout 15M mở), @Kranky_Trades (KARMA phạm vi Á EURUSD), @algojan (vàng H1 theo giờ) | C | rule một phần/marketing | tháng |
Loại: @fxmath (ML hộp đen, quảng cáo), @Mirakami_FX, @Emmytechfx (không có luật).

## Luật trích (đã thử ở reports/vong29_x.json)
R1 RSI5<30 & close>SMA200, thoát RSI5>50 [hồi quy|chỉ số|D1|thoát điều kiện] https://x.com/EmpiricaLab/status/2109388610394870000
R2 RSI4<30 & EMA100 lên, thoát RSI4>50 (bỏ VWAP) https://x.com/crowcaw/status/2106280698839769244
R3 Triple RSI (RSI5<30, giảm 3 ngày, RSI 3 ngày trước<60, >SMA200) https://x.com/QuantifiedStrat/status/2101295243115000032
R4 Turn-of-month: mua close ngày giao dịch thứ 5 từ cuối, bán close ngày thứ 3 tháng mới https://x.com/QuantifiedStrat/status/2101295244461371440
R5 3 ngày giảm → mua close bán open https://x.com/QuantifiedStrat/status/2107530074039705685
R6 IBS<0,2 → mua close, thoát close>high hôm trước (≤10 ngày) https://x.com/EmpiricaLab/status/2109585194638295144
R7 close < max(H,10) − 2,5·TB(H−L,25) & IBS<0,3, thoát close>high hôm trước https://x.com/EmpiricaLab/status/2107933995199533554
R8 giữ qua đêm mọi đêm https://x.com/QuantifiedStrat/status/2109342013154029733

## Chưa thử (xếp hàng VONG_LAP mục 30–34)
EURUSD H1 BB(20,2)+RSI14<30+ADX<20 thoát giữa BB https://x.com/grok/status/2101259559155216455 ;
GLD inside→outside day phá hỏng https://x.com/QuantifiedStrat/status/2106665819044257992 ; NR7 + lọc https://x.com/QuantifiedStrat/status/2106805298019058073 ;
Gold breakout 15M Pine mở https://x.com/WillyAlgoTrader/status/2109773530552578276 ; KARMA phạm vi Á EURUSD https://x.com/Kranky_Trades/status/2106735010325921988 ;
Vàng qua đêm placebo/Deflated Sharpe https://x.com/EmpiricaLab/status/2107909043377332416
