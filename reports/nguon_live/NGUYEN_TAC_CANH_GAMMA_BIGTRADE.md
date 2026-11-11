# Nguyên tắc canh Gamma / Wall / Big trade + nguồn dữ liệu (11/11/2026)

## 1. Ý tưởng hệ thống (3 lớp)
1. **Rule vào lệnh gốc**: các hệ brain2 đã lọc (vd ghep60ff GBPCAD H1) = quyết định "vào ở đâu".
2. **Lớp vị thế quyền chọn**: GEX, gamma flip, call/put wall, big trade = quyết định "có nên vào không, vào bao nhiêu".
3. **Lớp xác nhận order flow**: footprint, delta, big trade futures từ Sierra Chart + Rithmic (CME: GC, ES, NQ, 6B, 6E…) = điểm vào chính xác.
- Forex spot/CFD là OTC → tick volume XM không dùng làm footprint được; order flow thật phải lấy từ futures CME.
- Kiểm định giữ như cũ: chọn tham số chỉ trên train, walk-forward, so với vào lệnh ngẫu nhiên, tính phí/trượt giá thật, tối ưu riêng từng mã.

## 2. Đọc GEX / Wall
- **Gamma flip**: trên flip = gamma dương, dealer mua đáy bán đỉnh → thị trường dao động, hợp đánh hồi. Dưới flip = gamma âm, dealer đánh theo hướng giá → trend, biến động mạnh, hợp breakout.
- **Put wall** = hỗ trợ (strike có GEX put lớn nhất). **Call wall** = kháng cự / nam châm.
- Gamma âm mà phá put wall → bán dễ tăng tốc; đứng ngoài hoặc đánh theo.
- **Biên độ ngày ≈ giá × IV ATM / √252** (vd 4035 × 21,4% / 15,87 ≈ ±54).

## 3. Xếp hạng vùng S/A/B/C
- **S**: mức trùng nhiều nguồn và nhiều kỳ đáo hạn (vd GC 4000: put wall FlashAlpha + wSup OTL kỳ tháng, tuần, 2 ngày). Hợp đặt limit nhất.
- **A**: trùng 2 nguồn/kỳ (vd gamma flip FlashAlpha 4105 + wRes kỳ 2 ngày 4100).
- **B**: 1 kỳ dài hoặc xa giá hơn 1,5 độ lệch chuẩn ngày.
- **C**: mức chỉ của kỳ 0–1 ngày hoặc pivot nhỏ (giá đóng cửa hôm trước); hết hiệu lực khi kỳ đáo hạn.

## 4. Đặt limit theo wall — KHÔNG set and forget
- Wall khác nhau theo kỳ đáo hạn; wall kỳ ngắn biến mất khi đáo hạn.
- OI cập nhật mỗi sáng phiên Mỹ; big trade lớn có thể dời wall trong phiên.
- Quy trình: đặt limit vùng S/A trong ngày → kiểm tra lại mỗi sáng và sau ~21:30 giờ VN → dời nếu wall đổi.

## 5. Quy đổi giá future/chỉ số/ETF → CFD XM
- Chênh lệch = giá gốc − giá CFD, đo cùng thời điểm, **tính lại mỗi lần**, không dùng số cố định.
- Mức CFD = mức gốc − chênh lệch.
- Mức tính theo GLD: nhân tỉ lệ (giá vàng / giá GLD, ≈ ×10,9) trước, rồi mới trừ chênh lệch.
- Vàng: GC − XAUUSD ≈ chi phí carry (11/11 ≈ +8). US500/US100: CFD bám ES/NQ, chênh do cổ tức + lãi suất. GER40: CFD bám sát DAX tiền mặt.
- Chênh lệch nhảy khi future chuyển kỳ hạn.

## 6. Dùng big trade
- Là **bộ lọc hướng + đánh dấu mức**, không phải tín hiệu vào trực tiếp (có thể là lệnh phòng hộ).
- Mã: LC mua call, SC bán call, LP mua put, SP bán put. LC + SP = nghiêng tăng; LP + SC = nghiêng giảm.
- Strike bị đánh lớn → OI tăng → dễ thành wall hôm sau (vd 11/11: SP 3900 ~1,3 triệu USD = vùng đáy phe lớn tin không thủng).
- Kỳ 0–2 ngày: ảnh hưởng giá trong ngày. Kỳ xa (tháng 2–4/2027): chỉ là hướng dài hạn.
- Vào lệnh khi: giá chạm wall + big trade cùng hướng + footprint GC thấy hấp thụ/delta đảo chiều.
- Cảnh báo khi cụm big trade ≥ ~1 triệu USD cùng hướng/strike trong 30 phút.
- Cần ghi big trade hằng ngày để đo: tỉ lệ thắng khi dòng call nghiêng mạnh, strike bị đánh có thành wall hôm sau không.

## 7. Nguồn dữ liệu
### Canh trực tiếp (miễn phí)
| Nguồn | Tài sản | Ghi chú |
|---|---|---|
| [OTL Data](https://live.otldata.com/) | Vàng (OG/G2 nhiều kỳ) | Wall từng kỳ, bull/bear, big trade, IV. robots.txt cấm crawler → chỉ xem bằng trình duyệt như người dùng. Liên hệ: [Telegram AI_otl_Alert](https://t.me/AI_otl_Alert) |
| [FlashAlpha GC](https://flashalpha.com/futures/gc/gamma) | Vàng (quyền chọn futures GC) | Flip, call/put wall, net GEX, IV; API free 5 lần/ngày |
| [WyckFlow GEX](https://wyckflow.com/gex) | ES, NQ, GC (từ GLD ×10,9) | Không đăng nhập, 15–30 phút, chỉ trong phiên Mỹ |
| [GEXMetrix](https://www.gexmetrix.com/gex) | SPX/NDX/ES/NQ | 15 phút; ToS cấm scrape |
| [OptionCharts](https://optioncharts.io/options/SPY/gamma-exposure) | SPY, QQQ, GLD… | Trễ 15 phút, 1 đáo hạn free, có CSV |
| [Gamma Cockpit](https://levels.gammacockpit.com/) | GER40/DAX (ODAX) | Mức theo ngày |
| [tick-stream](https://tick-stream.xyz/free-gex-levels-realtime) | ES/NQ/vàng | Free trễ 1 ngày; API ~69 USD/tháng |
| [SpotGamma free](https://spotgamma.com/free-tools/spx-gamma-exposure/) | SPX | Chart ngày |
| [CrossVol](https://crossvol.com/en/markets/eurusd/gamma-exposure-today/) | FX (EURUSD…) | Snapshot cuối ngày |
| [Infolib flow](https://infolib.org/market-dashboard/unusual-options-flow) | Options flow Mỹ | Không đăng ký |
| [Xynth flow](https://xynth.com/flow) | Options flow | Tài khoản free, xuất CSV |
| [Unusual Whales free](https://unusualwhales.com/live-options-flow/free) | Options flow | Trễ 2 phiên |

### Có lịch sử để backtest
- [SqueezeMetrics DIX/GEX CSV](https://squeezemetrics.com/monitor/static/DIX.csv): miễn phí, 2011 → nay, chỉ S&P 500.
- [CFTC COT](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm): hằng tuần, vàng/FX/chỉ số.
- FlashAlpha Historical API (từ 2017, ~1.499 USD/tháng); tick-stream API (~69 USD/tháng).
- Tự tính GEX từ chuỗi quyền chọn gốc: Databento (CME GC/OG, ES/NQ), ThetaData, hoặc Rithmic nếu gói có options.
- Giá nhanh: Yahoo chart (GC=F, GLD), api.gold-api.com (XAU spot).
- Footprint CME: chỉ Sierra Chart + Rithmic (file .scid có bid/ask volume, .depth sổ lệnh).

## 8. Nguyên tắc chung
- Chỉ đọc dữ liệu hiển thị công khai như người xem; không dùng API nội bộ không tài liệu, không cào trang cấm, không vượt chặn/đổi IP lách ban.
- Chỉ báo số liệu đọc được, không suy đoán; ghi rõ nguồn và giờ.
- Lưu mỗi lần đọc (wall, flip, chênh lệch, big trade) thành JSONL để tích dữ liệu backtest (trên máy bot: /workspace/canh_chart/muc_gamma.jsonl, big_trade_vang.jsonl).
- Lịch canh của bot: 14:00–23:30 giờ VN, thứ 2–6, mỗi 30 phút; chỉ nhắn khi giá chạm/phá wall, wall S/A dịch chuyển, hoặc cụm big trade lớn.

## 9. Ảnh chụp 11/11/2026 ~07:50–07:58 (giờ VN)
- XAUUSD 4.034,7; GC 4.042,8; chênh ≈ +8,1. FlashAlpha: gamma âm, net GEX −192,3 triệu USD, flip 4.105,34, call wall 4.200, put wall 4.000, IV 21,4%.
- OTL wSup/wRes: tháng 4.000/10.000; tuần 4.000/4.200; 1 ngày 4.025/4.175; 2 ngày 4.000/4.100.
- Vùng XAUUSD: S mua 3.990–3.995; A bán 4.092–4.097; B 4.167–4.192; C mua ngắn ~4.017.
