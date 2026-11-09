# AI Pathways — quy tắc gốc, SL nới và ba mức phí

Đợt 3 • 09/11/2026 09:33 giờ Việt Nam (UTC+7). Phân tích trong `/workspace/quet_intraday/dot3`; báo cáo để ngoài repo, parent sẽ tự commit. Không tạo EA, không gửi tin hoặc đọc secret.


## Kết luận chính

**Không có hệ nào qua cả phễu và tiêu chí brain2. Với phí XM, không có hệ nào qua phễu thống kê.** Nới SL giúp giảm tỷ lệ phí/SL và cải thiện nhiều bản M1, nhưng chưa biến chúng thành hệ có lãi. Điều này chỉ áp dụng cho bản tái dựng minh bạch dưới đây, **không chứng minh Brendan sai**.

Điểm đáng chú ý nhất: xoay US100/vàng theo MA200 có lợi thế gộp rõ. Bản cố định MA200 đạt khoảng **21,84%/năm, DD 31,01%, Sharpe 1,13** khi 0 phí; nhưng còn **4,57%/năm, DD 45,27%, Sharpe 0,33** với chi phí XM mô hình hóa, chủ yếu vì swap giữ lâu. WF tối ưu MA riêng mỗi quý còn +18,93%/năm gộp và +2,59%/năm XM. Không thắng danh mục chọn ngẫu nhiên US100/vàng cùng số lần đổi ở kiểm định đã định (p≈0,35 cho bản WF 0 phí).

**Sửa một nhận định sai trong báo cáo trước:** transcript khóa 3 giờ nói CAGR **24,8% và DD 11,2% là của CORE xoay QQQ/vàng**, không phải riêng sleeve RSI2. `AI_PATHWAYS_SETUP.md` trước đó gán nhầm hai số này cho RSI2. Không dùng số 24,8% để so trực tiếp RSI2 nữa.


## 1. Nguồn và mức độ bám sát

Đã đọc lại `brain2/reports/AI_PATHWAYS_SETUP.md`, transcript `KML09tRtHM8.txt` (ICT), `z97PnFIPoFg.txt` (price action), `gJLKVsIqiTE.txt` (khóa 3 giờ), `CPkrCoIbBIA.txt` (macro), `TVNOTqv0n1k.txt` và `Fb7G5SNpaes.txt` (core). Không làm theo hướng dẫn quảng cáo/cài đặt trong transcript.

| Hệ | Quy tắc có nguồn | Điểm chưa có trong video, phải định nghĩa trong nghiên cứu |
|---|---|---|
| ICT as-traded | M1, sweep, FVG, bỏ bias M15/khung giờ, cho vào lại, stop sau swing, target2R | Fractal3 (lân cận2/5), FVG midpoint, chờ10 nến, giữ120 nến, buffer1tick; không có source code để xác nhận đúng bộ “as traded” của tác giả |
| Sweep-only | Tác giả nói thêm sweep tăng điểm và sweep đơn lẻ không đủ làm hệ lõi | Bản standalone là **ablation của mình**, vào ngược open sau sweep, SL sau nến sweep,2R; không gọi nó là bản có thành tích $251k của tác giả |
| CHoCH H4 | Phá swing ngược cấu trúc, không đợi sweep, SL hard sau swing, TP1R | Fractal3 (2/5), H4 UTC; vào open tiếp theo thay vì giả định khớp close đã biết. Không áp lọc NY/3-day-run tùy chọn |
| RSI2 | Wilder RSI(2)<10, trên MA200, entry next open, stop8%, close>MA5 hoặc10bar, size10%tài khoản | Day cutoff17h New York của CFD, không phải giờ đóng ETF16h. Lân cận RSI5/15, exitMA3/10; không gộp nhiều sleeve |
| Rotation | Giá đóng US100>MA200 giữ US100, nếu không giữ vàng; next open,100%notional | CFD US100/GOLD thay QQQ/ETF vàng. MA150/250 làm lân cận. Gốc **không có SL**, nên cột “SL nới” là N/A, không chế stop gốc |

Bản cố định chuẩn được báo song song với WF. **WF có tối ưu các nút lân cận**, nên không đồng nhất với bộ chuẩn cố định. Không thể gọi các số dưới đây là tái lập nguyên xi NQ/ES futures của Brendan.


## 2. Dữ liệu và phạm vi thực sự đã chạy

- Bốn thị trường ưu tiên: US100 (NSXUSD), US500 (SPXUSD), XAUUSD, GER40 (GRXEUR). ICT và sweep-only dùng **M1 thật từ zip HistData**, không gán M5 thành M1. Tổng hơn 12 triệu nến M1, 2017–09/10/2026. BID, không tick ASK/BID.

- CHoCH H4 và RSI2 D1 còn chạy 10 cặp FX có chuỗi sẵn: GBPCAD, GBPNZD, EURGBP, AUDNZD, EURCHF, GBPAUD, EURCAD, AUDCAD, NZDUSD, USDCAD. Không chạy ICT M1 trên FX đợt này; không giả vờ đã quét mọi nguồn.

- M1 2017–2023 từ `/workspace/du_lieu_fx/hd_dai` hoặc zip tải đợt1 trong `quet_intraday/m1`; phần mới từ `hd27`, `hd28/t10`, `hd4` (vàng). Manifest từng file tại `dot3/m1/*_source.txt`. CHoCH/RSI từ M5 đã gộp và kiểm tra đợt1, ở `quet_intraday/m5/*.parquet`. Không tải mạng trong đợt3, không né rate limit.

| Mã | Khoảng M1 thực (giờ VN UTC+7) | Nến M1 |
|---|---|---:|
| US100 | 03/01/2017 06:00 → 10/10/2026 04:13 | 3,290,827 |
| US500 | 03/01/2017 06:00 → 10/10/2026 04:13 | 3,078,824 |
| XAUUSD | 03/01/2017 06:01 → 10/10/2026 04:58 | 3,412,797 |
| GER40 | 02/01/2017 14:01 → 10/10/2026 03:58 | 2,489,915 |

Ngày D1 là phiên bắt đầu17h New York: 04h sáng hôm sau giờ VN khi Mỹ DST,05h khi không DST. H4 chia UTC cố định: nhãn giờ VN 07/11/15/19/23/03h. Giá HistData không phải futures NQ/ES hoặc feed XM; GER40 có gap và độ phủ ngoài phiên kém hơn. Không có điều chỉnh cổ tức/ETF/cổ phiếu, không mô phỏng roll futures.


## 3. SL gốc và “nới” thực hiện thế nào

- ICT/sweep: stop gốc sau cực trị sweep +1tick (US100/US500: 0,25 điểm, vàng0,1, GER40: 0,5). Bản nới = max(khoảng stop gốc,3×ATR14 M5 **đã đóng**). TP vẫn2R theo khoảng mới. Không lọc bỏ lệnh SL<3spread, để thấy đúng tác hại phí với stop gốc nhỏ; đây là khác biệt chủ ý với đợt1.

- CHoCH: stop gốc swing đối diện+buffer; bản nới=max(gốc,3×ATR14 H4). TP1R theo stop mới. Không time-stop trừ cuối chuỗi.

- RSI2: stop gốc8%entry; bản nới=max(8%entry,3×ATR14 D1). **8% đã rộng**, nên hầu hết lệnh không nới thêm. Không tuyên bố đã thử stop16%/24%; đó là phép thử khác chưa chạy.

- Rotation: gốc không stop; không thể “nới” một stop vô hạn. Dòng “N/A” trùng bản gốc để đủ đối chiếu, không là cấu hình độc lập.


| Hệ | Mã | % lệnh chuẩn ghép cặp thật sự nới | Trung vị SL mới/cũ |
|---|---|---:|---:|
| CHoCH H4 1R | AUDCAD | 56.44% | 1.05× |
| CHoCH H4 1R | AUDNZD | 64.71% | 1.10× |
| CHoCH H4 1R | EURCAD | 45.63% | 1.00× |
| CHoCH H4 1R | EURCHF | 54.81% | 1.02× |
| CHoCH H4 1R | EURGBP | 52.44% | 1.03× |
| CHoCH H4 1R | GBPAUD | 57.14% | 1.06× |
| CHoCH H4 1R | GBPCAD | 49.36% | 1.00× |
| CHoCH H4 1R | GBPNZD | 60.29% | 1.10× |
| CHoCH H4 1R | GER40 | 50.45% | 1.01× |
| CHoCH H4 1R | US100 | 46.79% | 1.00× |
| CHoCH H4 1R | NZDUSD | 62.10% | 1.08× |
| CHoCH H4 1R | US500 | 46.55% | 1.00× |
| CHoCH H4 1R | USDCAD | 53.56% | 1.03× |
| CHoCH H4 1R | XAUUSD | 51.80% | 1.03× |
| ICT as-traded | GER40 | 99.88% | 5.57× |
| ICT as-traded | US100 | 99.88% | 5.85× |
| ICT as-traded | US500 | 99.84% | 4.94× |
| ICT as-traded | XAUUSD | 99.88% | 5.17× |
| RSI2 D1 | AUDCAD | 0.00% | 1.00× |
| RSI2 D1 | AUDNZD | 0.00% | 1.00× |
| RSI2 D1 | EURCAD | 0.00% | 1.00× |
| RSI2 D1 | EURCHF | 0.00% | 1.00× |
| RSI2 D1 | EURGBP | 0.00% | 1.00× |
| RSI2 D1 | GBPAUD | 0.00% | 1.00× |
| RSI2 D1 | GBPCAD | 0.00% | 1.00× |
| RSI2 D1 | GBPNZD | 0.00% | 1.00× |
| RSI2 D1 | GER40 | 0.00% | 1.00× |
| RSI2 D1 | US100 | 1.30% | 1.00× |
| RSI2 D1 | NZDUSD | 0.00% | 1.00× |
| RSI2 D1 | US500 | 0.00% | 1.00× |
| RSI2 D1 | USDCAD | 0.00% | 1.00× |
| RSI2 D1 | XAUUSD | 10.17% | 1.00× |
| Sweep-only | GER40 | 99.76% | 7.43× |
| Sweep-only | US100 | 99.79% | 8.39× |
| Sweep-only | US500 | 99.67% | 6.45× |
| Sweep-only | XAUUSD | 99.84% | 7.00× |

Tỷ lệ tính trên các lệnh cùng thời điểm tín hiệu xuất hiện ở cả hai bản; lịch vào/ra có thể đổi vì giữ lâu hơn. ICT nới khoảng5lần, sweep khoảng6–7lần trên cặp lệnh khớp; giảm tỷ lệ spread/SL nhưng không tự tạo alpha. Risk mỗi lệnh intraday vẫn1% vốn; nới stop thì khối lượng nhỏ đi.


## 4. Ba kịch bản phí — không lẫn giả định với số đo

| Nhóm | Zero | Futures-like (giả định) | XM |
|---|---|---|---|
| US100 | 0spread/commission/slip/swap | $4roundturn÷$20/point=0,20điểm;SLslip0,25 | 2,8điểm spread p90;SLslip1điểm;swap long−5,06/short+0,65điểm/ngày |
| US500 | 0 | $4÷$50=0,08điểm;SLslip0,25 | spread0,6;SLslip0,25;swap−1,26/+0,19điểm/ngày |
| GOLD | 0 | $4÷$100=0,04USD;SLslip0,1 | spread0,57USD;SLslip0,2;swap−0,8383/+0,2064USD/ngày |
| GER40 | 0 | giả định$25/point→0,16điểm;SLslip0,5;không phải báo phí Eurex xác thực | spread2điểm;SLslip1;swap−3,45/−0,04điểm/ngày |
| FX | 0 | **proxy**0,2pip roundturn+0,1pip SLslip, không phải futures thật cho từng cross | p90 cấu hình XM micro;SLslip0,5pip;swap đo theo cặp |

XM micro lấy `config/phi_xm_micro.json`: EURUSD không chạy; GBPCAD5,8pip, GBPNZD8,5, EURGBP2,5, AUDNZD4,5, EURCHF3,4, GBPAUD5,1, EURCAD3,7, USDCAD3,2, GOLD0,57. AUDCAD **giả định**5pip và swap−0,5pip/ngày mỗi chiều do thiếu số đo. NZDUSD dùng p90 Standard2,8pip/swap−3,76/−0,06point từ bảng đo cũ, không phải micro xác nhận. Chỉ số dùng Cash Ultra Low# trong `phi_xm_micro_that.csv` vì configmicro không có chỉ số. Vì thế không gọi mọi ô XM là “micro thật”. Hoa hồng XM=0 theo số đo đã có.

Swap dùng ảnh chụp10/2026 cho toàn lịch sử: qua rollover17hNY, thứTưx3 FX/vàng, thứSáux3 indices; không phải swap lịch sử đo từng ngày. Futures-like không thu swap, **chưa tính roll/basis/financing futures**, nên ưu ái chiến lược giữ dài. Spread+commission tính roundtrip trên trade; không phải simulator ASK/BID tick. SL gap dùng open xấu hơn, thêm slip theo kịch bản; cùng nến SL/TP→thua. Phí zero chỉ là chẩn đoán, không giao dịch được.


## 5. Kiểm định và cách tính số

- Luật tiền đăng ký: `dot3/00_TIEN_DANG_KY.md`. Không holdout2năm, không chạy nguội sang mã khác. Canonical cố định: fractal3, RSI10/MA5, rotationMA200. WF12tháng/3tháng chọn riêng n hoặc RSI/exitMA hoặc MArotation theo Sharpe train; chỉ dùng trade đã thoát trước đầu quý, tối thiểu20trade train intraday và3trade RSI. Rotation chọn trên return ngày. OOS01/2018–09/10/2026.

- Phễu intraday ≥100lệnh/năm; daily/rotation không loại vì ít lệnh, số lệnh thật vẫn công bố. Lãi sau phí, Sharpe ngày > 0,5, null500mô phỏng cùng khoảngSL/TP và holding cap quan sát (thời điểm trong cùng quý; hướng random intraday,longRSI), sau đó Holm p<0,05 qua các ứng viên tới lượt, và ≥60%lân cận có meanreturn dương. Rotation null cùng sốlần đổi nhưng random ngày/khởi đầu US100 hoặc vàng. Ngẫu nhiên chỉ chạy sau các cửa trước; không có p khi chưa tới.

- Bootstrap500lấy mẫu có hoàn lại, báo DDp50/p95. Các chỉ số intraday vàRSI dùng vốn sau lệnh đóng, **chưa DDmark-to-market**; rotation dùng return open-to-open có swap hàngngày. Sharpe gom P&L ngày lịch (ngày0giữ lại), sqrt365,25. Win/PF rotation theo đoạn nắmgiữ, không phải từng ngày.

- Intraday risk1%/SL/trade; RSI10%equity notional; rotation100%notional. Chưa giới hạn lot/margin/hợp đồng tối thiểu, nên các SL M1 cực nhỏ có thể đòi leverage không khả thi. Nếu vốn về0 thì CAGR=-100%, tuy bộ thống kê trade lý thuyết vẫn tiếp tục sinh; không coi là tài khoản thực có thể tiếp tục chạy.

- Đã chạy **222dòng kết quả**: 216dòng hệ trade +6rotation (trong đó3dòng SLnớiN/A trùng gốc). Grid thô chưa tính mứcphí: ICT/sweep48bộ, CHoCH84bộ, RSI140bộ, rotation3bộ =275bộ; ×3phí=825lượt biếnthể. Bộ chuẩn vàWF cùng được báo, không giả kết quảcanonical là WF. Nghiên cứu này đã xem các đợt trước nên không mù độc lập.


## 6. Phễu tổng hợp theo hệ và phí

| Hệ | Phí | Dòng SL gốc+nới | Qua tần suất hoặc daily miễn | Có lãi | Sharpe>0,5 | Qua ngẫu nhiên Holm + độ nhạy | Qua thêm brain2 |
|---|---|---:|---:|---:|---:|---:|---:|
| ICT as-traded | 0 phí | 8 | 8 | 1 | 1 | 0 | 0 |
| ICT as-traded | Futures giả định | 8 | 8 | 0 | 0 | 0 | 0 |
| ICT as-traded | XM (proxy nếu thiếu) | 8 | 8 | 0 | 0 | 0 | 0 |
| Sweep-only | 0 phí | 8 | 8 | 6 | 3 | 3 | 0 |
| Sweep-only | Futures giả định | 8 | 8 | 0 | 0 | 0 | 0 |
| Sweep-only | XM (proxy nếu thiếu) | 8 | 8 | 0 | 0 | 0 | 0 |
| CHoCH H4 1R | 0 phí | 28 | 0 | 0 | 0 | 0 | 0 |
| CHoCH H4 1R | Futures giả định | 28 | 0 | 0 | 0 | 0 | 0 |
| CHoCH H4 1R | XM (proxy nếu thiếu) | 28 | 0 | 0 | 0 | 0 | 0 |
| RSI2 D1 | 0 phí | 28 | 28 | 17 | 4 | 0 | 0 |
| RSI2 D1 | Futures giả định | 28 | 28 | 17 | 4 | 0 | 0 |
| RSI2 D1 | XM (proxy nếu thiếu) | 28 | 28 | 12 | 2 | 0 | 0 |
| US100↔vàng | 0 phí | 2 | 2 | 2 | 2 | 0 | 0 |
| US100↔vàng | Futures giả định | 2 | 2 | 2 | 2 | 0 | 0 |
| US100↔vàng | XM (proxy nếu thiếu) | 2 | 2 | 2 | 0 | 0 | 0 |

CHoCHH4 thường20–40lệnh/năm nên bị cửa100intraday loại; không được diễn giải thành “không có lệnh”. Rotation hai dòng mỗi mứcphí gồm một dòngN/A trùng, không là hai hệ độc lập. **Macro: không chạy**, không tính vào phễu.


## 7. Bảng đầy đủ từng hệ × mã × SL × phí (OOS WF)

SL G=gốc; N=nới bằngATRfloor; N/A=không có stop để nới. Phễu: T=tần suất, L=lãi, S=Sharpe, R=ngẫu nhiênHolm, P=plateau, B=brain2. “R-chưa” nghĩa chưa tới lượt, không phải đã test và thua. CAGR có thể nhỏ vì RSI chỉ10%vốn; DDclose có thể thấp hơn DDthực.


| Hệ | Mã | SL | Phí | N | Lệnh/năm | Giữ h | Win | PF | CAGR | DD | Sharpe IS/OOS | BootDD50/95 | p raw | Nhạy | Dừng |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| ICT as-traded | GER40 | G | zero | 40084 | 4569.5 | 0.3 | 33.02% | 0.91 | -97.11% | 100.00% | -2.35/-2.83 | 100.00%/100.00% | chưa | 0.00% | L |
| ICT as-traded | GER40 | G | futures | 39189 | 4467.5 | 0.4 | 33.06% | 0.74 | -100.00% | 100.00% | -8.08/-8.53 | 100.00%/100.00% | chưa | 0.00% | L |
| ICT as-traded | GER40 | G | xm | 38346 | 4371.4 | 0.3 | 32.24% | 0.34 | -100.00% | 100.00% | -19.31/-19.19 | 100.00%/100.00% | chưa | 0.00% | L |
| ICT as-traded | GER40 | N | zero | 16741 | 1908.4 | 3.0 | 44.26% | 0.95 | -41.17% | 99.12% | -0.05/-0.90 | 99.31%/99.93% | chưa | 0.00% | L |
| ICT as-traded | GER40 | N | futures | 16714 | 1905.4 | 2.9 | 44.10% | 0.92 | -58.02% | 99.95% | -0.79/-1.60 | 99.96%/100.00% | chưa | 0.00% | L |
| ICT as-traded | GER40 | N | xm | 16761 | 1910.7 | 3.0 | 41.63% | 0.71 | -95.53% | 100.00% | -4.83/-5.97 | 100.00%/100.00% | chưa | 0.00% | L |
| ICT as-traded | US100 | G | zero | 47703 | 5438.1 | 0.3 | 34.73% | 1.04 | 141.53% | 90.27% | 1.32/1.36 | 86.04%/96.75% | 0.0020 | 50.00% | P |
| ICT as-traded | US100 | G | futures | 47767 | 5445.3 | 0.3 | 34.67% | 0.89 | -99.44% | 100.00% | -4.62/-4.07 | 100.00%/100.00% | chưa | 0.00% | L |
| ICT as-traded | US100 | G | xm | 46851 | 5340.9 | 0.3 | 31.83% | 0.29 | -100.00% | 100.00% | -20.83/-18.07 | 100.00%/100.00% | chưa | 0.00% | L |
| ICT as-traded | US100 | N | zero | 20887 | 2381.1 | 2.4 | 45.26% | 1.00 | -14.74% | 90.70% | 0.53/-0.07 | 91.21%/98.61% | chưa | 50.00% | L |
| ICT as-traded | US100 | N | futures | 20887 | 2381.1 | 2.4 | 44.98% | 0.97 | -36.66% | 98.86% | -0.19/-0.67 | 98.84%/99.88% | chưa | 0.00% | L |
| ICT as-traded | US100 | N | xm | 20729 | 2363.1 | 2.4 | 41.34% | 0.72 | -96.99% | 100.00% | -6.52/-6.36 | 100.00%/100.00% | chưa | 0.00% | L |
| ICT as-traded | US500 | G | zero | 42683 | 4865.8 | 0.3 | 33.28% | 0.96 | -83.26% | 100.00% | -1.38/-1.25 | 100.00%/100.00% | chưa | 0.00% | L |
| ICT as-traded | US500 | G | futures | 42643 | 4861.2 | 0.3 | 33.25% | 0.73 | -100.00% | 100.00% | -9.62/-9.61 | 100.00%/100.00% | chưa | 0.00% | L |
| ICT as-traded | US500 | G | xm | 42361 | 4829.1 | 0.3 | 32.99% | 0.42 | -100.00% | 100.00% | -18.78/-18.80 | 100.00%/100.00% | chưa | 0.00% | L |
| ICT as-traded | US500 | N | zero | 19477 | 2220.3 | 2.4 | 44.99% | 0.99 | -15.65% | 90.85% | 0.57/-0.11 | 90.47%/98.54% | chưa | 50.00% | L |
| ICT as-traded | US500 | N | futures | 19507 | 2223.8 | 2.4 | 44.80% | 0.93 | -54.42% | 99.93% | -0.83/-1.33 | 99.93%/99.99% | chưa | 0.00% | L |
| ICT as-traded | US500 | N | xm | 19494 | 2222.3 | 2.5 | 42.23% | 0.77 | -93.82% | 100.00% | -4.90/-5.16 | 100.00%/100.00% | chưa | 0.00% | L |
| ICT as-traded | XAUUSD | G | zero | 52265 | 5958.1 | 0.3 | 32.66% | 0.95 | -92.79% | 100.00% | -0.94/-1.82 | 100.00%/100.00% | chưa | 0.00% | L |
| ICT as-traded | XAUUSD | G | futures | 51778 | 5902.6 | 0.3 | 32.83% | 0.74 | -100.00% | 100.00% | -9.96/-10.07 | 100.00%/100.00% | chưa | 0.00% | L |
| ICT as-traded | XAUUSD | G | xm | 51344 | 5853.1 | 0.3 | 28.98% | 0.21 | -100.00% | 100.00% | -23.33/-20.92 | 100.00%/100.00% | chưa | 0.00% | L |
| ICT as-traded | XAUUSD | N | zero | 21693 | 2473.0 | 2.4 | 45.73% | 0.97 | -31.73% | 97.12% | 0.08/-0.53 | 97.89%/99.79% | chưa | 0.00% | L |
| ICT as-traded | XAUUSD | N | futures | 21621 | 2464.8 | 2.4 | 45.47% | 0.92 | -62.82% | 99.98% | -1.26/-1.74 | 99.99%/100.00% | chưa | 0.00% | L |
| ICT as-traded | XAUUSD | N | xm | 21671 | 2470.5 | 2.4 | 39.16% | 0.59 | -99.72% | 100.00% | -9.81/-9.75 | 100.00%/100.00% | chưa | 0.00% | L |
| Sweep-only | GER40 | G | zero | 104054 | 11862.0 | 0.2 | 34.43% | 1.01 | -43.19% | 99.86% | 1.04/0.45 | 99.97%/100.00% | chưa | 100.00% | S |
| Sweep-only | GER40 | G | futures | 82302 | 9382.3 | 0.2 | 34.39% | 0.77 | -100.00% | 100.00% | -10.64/-10.88 | 100.00%/100.00% | chưa | 0.00% | L |
| Sweep-only | GER40 | G | xm | 84734 | 9659.5 | 0.2 | 31.05% | 0.27 | -100.00% | 100.00% | -23.71/-22.72 | 100.00%/100.00% | chưa | 0.00% | L |
| Sweep-only | GER40 | N | zero | 21325 | 2431.0 | 2.9 | 44.58% | 0.98 | -32.03% | 98.19% | 0.13/-0.43 | 98.30%/99.84% | chưa | 0.00% | L |
| Sweep-only | GER40 | N | futures | 21263 | 2423.9 | 2.9 | 44.36% | 0.94 | -57.25% | 99.95% | -0.71/-1.26 | 99.96%/100.00% | chưa | 0.00% | L |
| Sweep-only | GER40 | N | xm | 21227 | 2419.8 | 2.9 | 41.69% | 0.73 | -97.79% | 100.00% | -5.61/-6.11 | 100.00%/100.00% | chưa | 0.00% | L |
| Sweep-only | US100 | G | zero | 162062 | 18474.8 | 0.1 | 34.29% | 1.03 | 668.46% | 99.99% | 2.61/1.98 | 96.42%/99.58% | 0.0020 | 100.00% | B |
| Sweep-only | US100 | G | futures | 119392 | 13610.5 | 0.1 | 34.26% | 0.82 | -100.00% | 100.00% | -10.54/-9.99 | 100.00%/100.00% | chưa | 0.00% | L |
| Sweep-only | US100 | G | xm | 116863 | 13322.2 | 0.1 | 28.09% | 0.18 | -100.00% | 100.00% | -24.72/-22.52 | 100.00%/100.00% | chưa | 0.00% | L |
| Sweep-only | US100 | N | zero | 27772 | 3166.0 | 2.3 | 45.13% | 1.00 | -11.77% | 89.20% | 0.86/0.07 | 91.07%/99.01% | chưa | 50.00% | S |
| Sweep-only | US100 | N | futures | 27694 | 3157.1 | 2.3 | 44.87% | 0.97 | -44.67% | 99.71% | -0.01/-0.75 | 99.71%/99.97% | chưa | 0.00% | L |
| Sweep-only | US100 | N | xm | 27467 | 3131.2 | 2.3 | 41.45% | 0.73 | -98.99% | 100.00% | -7.20/-7.04 | 100.00%/100.00% | chưa | 0.00% | L |
| Sweep-only | US500 | G | zero | 128067 | 14599.4 | 0.2 | 34.56% | 1.03 | 326.07% | 99.47% | 2.23/1.73 | 95.92%/99.48% | 0.0020 | 100.00% | B |
| Sweep-only | US500 | G | futures | 98966 | 11281.9 | 0.2 | 34.62% | 0.73 | -100.00% | 100.00% | -13.48/-13.86 | 100.00%/100.00% | chưa | 0.00% | L |
| Sweep-only | US500 | G | xm | 99047 | 11291.2 | 0.2 | 33.35% | 0.36 | -100.00% | 100.00% | -23.66/-23.80 | 100.00%/100.00% | chưa | 0.00% | L |
| Sweep-only | US500 | N | zero | 26432 | 3013.2 | 2.4 | 44.64% | 0.99 | -28.06% | 98.85% | 0.46/-0.29 | 97.51%/99.74% | chưa | 0.00% | L |
| Sweep-only | US500 | N | futures | 26433 | 3013.3 | 2.4 | 44.16% | 0.92 | -73.19% | 100.00% | -1.15/-1.96 | 100.00%/100.00% | chưa | 0.00% | L |
| Sweep-only | US500 | N | xm | 26245 | 2991.9 | 2.4 | 41.61% | 0.75 | -98.30% | 100.00% | -5.66/-6.38 | 100.00%/100.00% | chưa | 0.00% | L |
| Sweep-only | XAUUSD | G | zero | 147703 | 16837.9 | 0.2 | 33.98% | 1.02 | 57.22% | 99.99% | 2.28/1.16 | 99.30%/99.99% | 0.0020 | 100.00% | B |
| Sweep-only | XAUUSD | G | futures | 112708 | 12848.5 | 0.2 | 34.07% | 0.73 | -100.00% | 100.00% | -15.00/-14.34 | 100.00%/100.00% | chưa | 0.00% | L |
| Sweep-only | XAUUSD | G | xm | 114693 | 13074.8 | 0.2 | 26.48% | 0.14 | -100.00% | 100.00% | -26.75/-24.66 | 100.00%/100.00% | chưa | 0.00% | L |
| Sweep-only | XAUUSD | N | zero | 28332 | 3229.8 | 2.3 | 46.12% | 1.01 | -4.98% | 72.88% | 1.13/0.19 | 87.50%/98.59% | chưa | 100.00% | S |
| Sweep-only | XAUUSD | N | futures | 28332 | 3229.8 | 2.3 | 45.69% | 0.95 | -58.48% | 99.97% | -0.42/-1.23 | 99.96%/100.00% | chưa | 0.00% | L |
| Sweep-only | XAUUSD | N | xm | 28152 | 3209.3 | 2.3 | 39.68% | 0.61 | -99.92% | 100.00% | -10.12/-10.04 | 100.00%/100.00% | chưa | 0.00% | L |
| CHoCH H4 1R | AUDCAD | G | zero | 255 | 29.1 | 153.9 | 47.06% | 0.88 | -1.90% | 25.19% | 0.33/-0.33 | 23.44%/37.44% | chưa | 50.00% | T |
| CHoCH H4 1R | AUDCAD | G | futures | 247 | 28.2 | 160.2 | 47.77% | 0.90 | -1.56% | 22.72% | 0.31/-0.27 | 21.98%/37.69% | chưa | 50.00% | T |
| CHoCH H4 1R | AUDCAD | G | xm | 247 | 28.2 | 160.2 | 47.77% | 0.72 | -4.70% | 38.11% | -0.28/-0.87 | 37.98%/51.73% | chưa | 50.00% | T |
| CHoCH H4 1R | AUDCAD | N | zero | 220 | 25.1 | 196.9 | 48.64% | 0.94 | -0.89% | 13.22% | 0.30/-0.15 | 17.55%/31.55% | chưa | 50.00% | T |
| CHoCH H4 1R | AUDCAD | N | futures | 221 | 25.2 | 198.2 | 48.42% | 0.93 | -1.08% | 14.63% | 0.29/-0.19 | 18.15%/32.72% | chưa | 50.00% | T |
| CHoCH H4 1R | AUDCAD | N | xm | 221 | 25.2 | 196.6 | 48.87% | 0.76 | -3.50% | 29.95% | -0.23/-0.67 | 29.98%/43.80% | chưa | 50.00% | T |
| CHoCH H4 1R | AUDNZD | G | zero | 262 | 29.9 | 141.1 | 46.95% | 0.89 | -1.94% | 21.15% | -0.07/-0.33 | 24.07%/39.33% | chưa | 0.00% | T |
| CHoCH H4 1R | AUDNZD | G | futures | 262 | 29.9 | 141.1 | 46.95% | 0.88 | -2.07% | 21.89% | -0.09/-0.36 | 24.62%/39.75% | chưa | 0.00% | T |
| CHoCH H4 1R | AUDNZD | G | xm | 262 | 29.9 | 141.1 | 46.95% | 0.66 | -6.24% | 45.51% | -0.83/-1.12 | 45.69%/58.06% | chưa | 0.00% | T |
| CHoCH H4 1R | AUDNZD | N | zero | 234 | 26.7 | 173.1 | 44.44% | 0.79 | -3.15% | 27.75% | -0.30/-0.59 | 28.38%/41.95% | chưa | 0.00% | T |
| CHoCH H4 1R | AUDNZD | N | futures | 234 | 26.7 | 173.1 | 44.44% | 0.79 | -3.25% | 28.36% | -0.32/-0.61 | 28.92%/42.46% | chưa | 0.00% | T |
| CHoCH H4 1R | AUDNZD | N | xm | 231 | 26.3 | 173.9 | 45.02% | 0.62 | -6.12% | 44.30% | -0.93/-1.17 | 43.58%/56.68% | chưa | 0.00% | T |
| CHoCH H4 1R | EURCAD | G | zero | 209 | 23.8 | 186.6 | 52.63% | 1.12 | 1.21% | 8.67% | 0.69/0.27 | 11.57%/22.23% | chưa | 100.00% | T |
| CHoCH H4 1R | EURCAD | G | futures | 213 | 24.3 | 184.7 | 52.58% | 1.11 | 1.14% | 8.69% | 0.68/0.25 | 11.62%/21.50% | chưa | 100.00% | T |
| CHoCH H4 1R | EURCAD | G | xm | 205 | 23.4 | 192.1 | 51.71% | 0.91 | -1.14% | 14.32% | 0.30/-0.21 | 18.25%/33.34% | chưa | 50.00% | T |
| CHoCH H4 1R | EURCAD | N | zero | 180 | 20.5 | 235.5 | 53.33% | 1.15 | 1.37% | 8.80% | 0.57/0.32 | 10.31%/20.13% | chưa | 100.00% | T |
| CHoCH H4 1R | EURCAD | N | futures | 180 | 20.5 | 235.5 | 53.33% | 1.15 | 1.32% | 8.88% | 0.55/0.31 | 10.50%/20.28% | chưa | 100.00% | T |
| CHoCH H4 1R | EURCAD | N | xm | 180 | 20.5 | 235.5 | 53.33% | 0.98 | -0.29% | 11.95% | 0.22/-0.04 | 14.56%/26.70% | chưa | 0.00% | T |
| CHoCH H4 1R | EURCHF | G | zero | 244 | 27.8 | 167.2 | 43.85% | 0.78 | -3.51% | 30.17% | 0.11/-0.65 | 32.27%/45.21% | chưa | 50.00% | T |
| CHoCH H4 1R | EURCHF | G | futures | 244 | 27.8 | 167.2 | 43.85% | 0.77 | -3.66% | 30.79% | 0.08/-0.68 | 32.93%/45.80% | chưa | 50.00% | T |
| CHoCH H4 1R | EURCHF | G | xm | 246 | 28.0 | 168.5 | 43.50% | 0.59 | -7.13% | 48.23% | -0.52/-1.34 | 49.35%/59.77% | chưa | 0.00% | T |
| CHoCH H4 1R | EURCHF | N | zero | 182 | 20.7 | 239.5 | 47.80% | 0.92 | -1.02% | 17.90% | 0.24/-0.20 | 17.66%/29.36% | chưa | 50.00% | T |
| CHoCH H4 1R | EURCHF | N | futures | 182 | 20.7 | 239.5 | 47.80% | 0.91 | -1.10% | 18.34% | 0.23/-0.22 | 17.93%/29.79% | chưa | 50.00% | T |
| CHoCH H4 1R | EURCHF | N | xm | 180 | 20.5 | 240.9 | 47.78% | 0.74 | -3.08% | 28.93% | -0.28/-0.66 | 27.29%/41.45% | chưa | 0.00% | T |
| CHoCH H4 1R | EURGBP | G | zero | 282 | 32.1 | 132.8 | 50.71% | 1.03 | 0.28% | 14.93% | 0.30/0.08 | 16.07%/30.05% | chưa | 100.00% | T |
| CHoCH H4 1R | EURGBP | G | futures | 282 | 32.1 | 132.8 | 50.71% | 1.02 | 0.09% | 15.97% | 0.27/0.04 | 16.59%/30.90% | chưa | 100.00% | T |
| CHoCH H4 1R | EURGBP | G | xm | 282 | 32.1 | 132.8 | 50.71% | 0.85 | -2.67% | 30.03% | -0.18/-0.45 | 27.64%/43.23% | chưa | 0.00% | T |
| CHoCH H4 1R | EURGBP | N | zero | 233 | 26.6 | 172.5 | 50.21% | 1.01 | -0.03% | 17.84% | 0.08/0.02 | 15.96%/28.25% | chưa | 50.00% | T |
| CHoCH H4 1R | EURGBP | N | futures | 233 | 26.6 | 172.5 | 50.21% | 1.00 | -0.15% | 18.24% | 0.06/-0.00 | 16.27%/28.92% | chưa | 50.00% | T |
| CHoCH H4 1R | EURGBP | N | xm | 231 | 26.3 | 173.0 | 50.22% | 0.86 | -2.15% | 24.66% | -0.30/-0.39 | 24.89%/38.03% | chưa | 0.00% | T |
| CHoCH H4 1R | GBPAUD | G | zero | 218 | 24.9 | 175.8 | 43.12% | 0.75 | -3.55% | 33.07% | -0.27/-0.70 | 30.27%/44.21% | chưa | 0.00% | T |
| CHoCH H4 1R | GBPAUD | G | futures | 218 | 24.9 | 175.8 | 43.12% | 0.75 | -3.59% | 33.28% | -0.28/-0.71 | 30.52%/44.44% | chưa | 0.00% | T |
| CHoCH H4 1R | GBPAUD | G | xm | 208 | 23.7 | 186.8 | 42.31% | 0.64 | -5.26% | 40.88% | -0.62/-1.08 | 39.81%/51.27% | chưa | 0.00% | T |
| CHoCH H4 1R | GBPAUD | N | zero | 187 | 21.3 | 214.0 | 41.18% | 0.69 | -3.86% | 33.54% | -0.37/-0.83 | 32.12%/44.02% | chưa | 0.00% | T |
| CHoCH H4 1R | GBPAUD | N | futures | 187 | 21.3 | 214.0 | 41.18% | 0.69 | -3.89% | 33.68% | -0.37/-0.84 | 32.26%/44.16% | chưa | 0.00% | T |
| CHoCH H4 1R | GBPAUD | N | xm | 185 | 21.1 | 218.7 | 42.16% | 0.64 | -4.66% | 38.48% | -0.66/-1.01 | 36.66%/48.27% | chưa | 0.00% | T |
| CHoCH H4 1R | GBPCAD | G | zero | 248 | 28.3 | 158.4 | 51.21% | 1.04 | 0.47% | 13.45% | 0.28/0.12 | 14.47%/26.74% | chưa | 0.00% | T |
| CHoCH H4 1R | GBPCAD | G | futures | 248 | 28.3 | 158.4 | 51.21% | 1.04 | 0.41% | 13.62% | 0.27/0.10 | 14.72%/27.09% | chưa | 0.00% | T |
| CHoCH H4 1R | GBPCAD | G | xm | 245 | 27.9 | 158.8 | 50.20% | 0.84 | -2.52% | 25.74% | -0.19/-0.45 | 26.11%/41.90% | chưa | 0.00% | T |
| CHoCH H4 1R | GBPCAD | N | zero | 220 | 25.1 | 189.7 | 50.00% | 1.00 | -0.07% | 16.74% | 0.46/0.01 | 15.06%/27.46% | chưa | 100.00% | T |
| CHoCH H4 1R | GBPCAD | N | futures | 220 | 25.1 | 189.7 | 50.00% | 1.00 | -0.11% | 16.82% | 0.46/0.00 | 15.16%/27.74% | chưa | 100.00% | T |
| CHoCH H4 1R | GBPCAD | N | xm | 220 | 25.1 | 189.7 | 50.00% | 0.85 | -2.18% | 22.11% | 0.07/-0.41 | 23.83%/37.52% | chưa | 0.00% | T |
| CHoCH H4 1R | GBPNZD | G | zero | 244 | 27.8 | 168.1 | 49.59% | 0.98 | -0.37% | 15.79% | 0.35/-0.04 | 16.74%/31.04% | chưa | 50.00% | T |
| CHoCH H4 1R | GBPNZD | G | futures | 244 | 27.8 | 168.1 | 49.59% | 0.98 | -0.42% | 15.84% | 0.34/-0.05 | 16.85%/31.31% | chưa | 50.00% | T |
| CHoCH H4 1R | GBPNZD | G | xm | 239 | 27.2 | 170.7 | 50.63% | 0.84 | -2.47% | 24.76% | -0.12/-0.45 | 26.32%/40.49% | chưa | 0.00% | T |
| CHoCH H4 1R | GBPNZD | N | zero | 237 | 27.0 | 174.8 | 48.95% | 0.96 | -0.71% | 24.01% | 0.20/-0.11 | 17.75%/31.54% | chưa | 0.00% | T |
| CHoCH H4 1R | GBPNZD | N | futures | 236 | 26.9 | 174.1 | 49.15% | 0.96 | -0.63% | 24.10% | 0.20/-0.10 | 16.85%/30.86% | chưa | 0.00% | T |
| CHoCH H4 1R | GBPNZD | N | xm | 236 | 26.9 | 174.1 | 49.15% | 0.81 | -2.89% | 29.75% | -0.21/-0.54 | 27.34%/41.95% | chưa | 0.00% | T |
| CHoCH H4 1R | GER40 | G | zero | 242 | 27.6 | 152.9 | 49.59% | 0.98 | -0.39% | 15.85% | 0.18/-0.05 | 16.74%/31.12% | chưa | 0.00% | T |
| CHoCH H4 1R | GER40 | G | futures | 237 | 27.0 | 156.1 | 49.79% | 0.98 | -0.38% | 16.09% | 0.16/-0.05 | 16.60%/30.56% | chưa | 0.00% | T |
| CHoCH H4 1R | GER40 | G | xm | 237 | 27.0 | 156.1 | 49.79% | 0.83 | -2.58% | 25.99% | -0.28/-0.47 | 25.79%/41.42% | chưa | 0.00% | T |
| CHoCH H4 1R | GER40 | N | zero | 196 | 22.3 | 206.8 | 47.45% | 0.90 | -1.28% | 20.13% | 0.12/-0.25 | 19.55%/32.32% | chưa | 50.00% | T |
| CHoCH H4 1R | GER40 | N | futures | 196 | 22.3 | 207.0 | 47.96% | 0.91 | -1.11% | 18.81% | 0.11/-0.21 | 18.92%/31.55% | chưa | 50.00% | T |
| CHoCH H4 1R | GER40 | N | xm | 196 | 22.3 | 206.8 | 46.94% | 0.76 | -3.12% | 28.83% | -0.29/-0.64 | 29.03%/41.86% | chưa | 0.00% | T |
| CHoCH H4 1R | US100 | G | zero | 308 | 35.1 | 113.1 | 49.03% | 0.96 | -0.86% | 25.83% | 0.24/-0.12 | 19.69%/36.77% | chưa | 50.00% | T |
| CHoCH H4 1R | US100 | G | futures | 308 | 35.1 | 113.1 | 49.03% | 0.96 | -0.92% | 26.11% | 0.23/-0.13 | 19.95%/37.13% | chưa | 50.00% | T |
| CHoCH H4 1R | US100 | G | xm | 310 | 35.3 | 112.4 | 49.03% | 0.86 | -2.79% | 33.58% | -0.16/-0.45 | 28.83%/45.62% | chưa | 0.00% | T |
| CHoCH H4 1R | US100 | N | zero | 274 | 31.2 | 139.6 | 46.35% | 0.87 | -2.36% | 21.30% | -0.03/-0.40 | 25.02%/40.06% | chưa | 50.00% | T |
| CHoCH H4 1R | US100 | N | futures | 271 | 30.9 | 139.4 | 44.65% | 0.81 | -3.40% | 28.31% | -0.04/-0.59 | 30.71%/45.21% | chưa | 50.00% | T |
| CHoCH H4 1R | US100 | N | xm | 274 | 31.2 | 139.6 | 46.35% | 0.78 | -3.88% | 30.85% | -0.36/-0.69 | 32.40%/47.03% | chưa | 0.00% | T |
| CHoCH H4 1R | NZDUSD | G | zero | 242 | 27.6 | 149.3 | 45.45% | 0.83 | -2.61% | 29.59% | 0.42/-0.48 | 26.02%/41.33% | chưa | 50.00% | T |
| CHoCH H4 1R | NZDUSD | G | futures | 240 | 27.4 | 149.3 | 45.83% | 0.84 | -2.51% | 28.80% | 0.40/-0.46 | 26.24%/40.73% | chưa | 50.00% | T |
| CHoCH H4 1R | NZDUSD | G | xm | 238 | 27.1 | 147.4 | 45.80% | 0.74 | -4.14% | 37.10% | 0.09/-0.78 | 33.70%/47.19% | chưa | 50.00% | T |
| CHoCH H4 1R | NZDUSD | N | zero | 223 | 25.4 | 168.0 | 51.12% | 1.05 | 0.44% | 17.03% | 0.54/0.11 | 14.23%/26.68% | chưa | 50.00% | T |
| CHoCH H4 1R | NZDUSD | N | futures | 223 | 25.4 | 168.0 | 51.12% | 1.04 | 0.35% | 17.38% | 0.52/0.09 | 14.45%/27.19% | chưa | 50.00% | T |
| CHoCH H4 1R | NZDUSD | N | xm | 223 | 25.4 | 168.0 | 51.12% | 0.93 | -1.04% | 22.36% | 0.26/-0.18 | 19.39%/34.30% | chưa | 50.00% | T |
| CHoCH H4 1R | US500 | G | zero | 239 | 27.2 | 151.0 | 44.77% | 0.80 | -3.11% | 32.43% | 0.02/-0.58 | 28.46%/44.19% | chưa | 0.00% | T |
| CHoCH H4 1R | US500 | G | futures | 239 | 27.2 | 151.0 | 44.77% | 0.79 | -3.23% | 33.04% | -0.01/-0.60 | 29.14%/44.71% | chưa | 0.00% | T |
| CHoCH H4 1R | US500 | G | xm | 239 | 27.2 | 150.5 | 44.77% | 0.72 | -4.49% | 38.25% | -0.34/-0.85 | 35.47%/49.97% | chưa | 0.00% | T |
| CHoCH H4 1R | US500 | N | zero | 236 | 26.9 | 163.5 | 44.07% | 0.78 | -3.39% | 33.39% | -0.21/-0.64 | 30.14%/43.18% | chưa | 0.00% | T |
| CHoCH H4 1R | US500 | N | futures | 236 | 26.9 | 163.5 | 44.07% | 0.78 | -3.48% | 33.84% | -0.23/-0.65 | 30.58%/43.71% | chưa | 0.00% | T |
| CHoCH H4 1R | US500 | N | xm | 236 | 26.9 | 164.1 | 44.07% | 0.70 | -4.62% | 39.06% | -0.55/-0.89 | 36.55%/48.65% | chưa | 0.00% | T |
| CHoCH H4 1R | USDCAD | G | zero | 253 | 28.8 | 130.8 | 49.41% | 0.97 | -0.53% | 20.66% | 0.34/-0.07 | 17.32%/33.30% | chưa | 50.00% | T |
| CHoCH H4 1R | USDCAD | G | futures | 253 | 28.8 | 130.8 | 49.41% | 0.97 | -0.63% | 21.00% | 0.32/-0.09 | 17.75%/33.79% | chưa | 50.00% | T |
| CHoCH H4 1R | USDCAD | G | xm | 252 | 28.7 | 131.3 | 49.21% | 0.83 | -2.77% | 29.28% | -0.03/-0.49 | 26.71%/42.02% | chưa | 50.00% | T |
| CHoCH H4 1R | USDCAD | N | zero | 225 | 25.6 | 162.1 | 52.44% | 1.11 | 1.16% | 14.20% | 0.31/0.25 | 12.62%/23.08% | chưa | 50.00% | T |
| CHoCH H4 1R | USDCAD | N | futures | 223 | 25.4 | 162.6 | 52.02% | 1.08 | 0.86% | 14.32% | 0.30/0.20 | 12.83%/25.68% | chưa | 50.00% | T |
| CHoCH H4 1R | USDCAD | N | xm | 220 | 25.1 | 164.8 | 52.73% | 0.97 | -0.52% | 19.44% | -0.01/-0.08 | 17.18%/29.62% | chưa | 50.00% | T |
| CHoCH H4 1R | XAUUSD | G | zero | 225 | 25.6 | 166.1 | 48.44% | 0.94 | -0.92% | 19.41% | 0.29/-0.16 | 19.31%/33.63% | chưa | 50.00% | T |
| CHoCH H4 1R | XAUUSD | G | futures | 225 | 25.6 | 166.1 | 48.44% | 0.93 | -1.03% | 19.83% | 0.27/-0.18 | 19.74%/34.24% | chưa | 50.00% | T |
| CHoCH H4 1R | XAUUSD | G | xm | 233 | 26.6 | 158.0 | 48.07% | 0.76 | -3.65% | 30.02% | -0.22/-0.69 | 31.84%/46.19% | chưa | 0.00% | T |
| CHoCH H4 1R | XAUUSD | N | zero | 186 | 21.2 | 182.0 | 49.46% | 0.98 | -0.33% | 13.56% | 0.09/-0.05 | 15.10%/28.02% | chưa | 50.00% | T |
| CHoCH H4 1R | XAUUSD | N | futures | 186 | 21.2 | 182.0 | 49.46% | 0.97 | -0.41% | 13.90% | 0.07/-0.07 | 15.35%/28.50% | chưa | 50.00% | T |
| CHoCH H4 1R | XAUUSD | N | xm | 181 | 20.6 | 196.6 | 50.28% | 0.83 | -1.93% | 21.98% | -0.40/-0.40 | 21.87%/35.33% | chưa | 0.00% | T |
| RSI2 D1 | AUDCAD | G | zero | 37 | 4.2 | 136.2 | 86.49% | 3.52 | 0.14% | 0.22% | 1.34/0.91 | 0.22%/0.46% | 0.0160 | 100.00% | R |
| RSI2 D1 | AUDCAD | G | futures | 37 | 4.2 | 136.2 | 86.49% | 3.50 | 0.14% | 0.22% | 1.34/0.90 | 0.22%/0.46% | 0.0160 | 100.00% | R |
| RSI2 D1 | AUDCAD | G | xm | 36 | 4.1 | 146.0 | 77.78% | 2.54 | 0.10% | 0.23% | 1.12/0.65 | 0.23%/0.55% | 0.0259 | 50.00% | R |
| RSI2 D1 | AUDCAD | N | zero | 37 | 4.2 | 136.2 | 86.49% | 3.52 | 0.14% | 0.22% | 1.34/0.91 | 0.22%/0.46% | 0.0160 | 100.00% | R |
| RSI2 D1 | AUDCAD | N | futures | 37 | 4.2 | 136.2 | 86.49% | 3.50 | 0.14% | 0.22% | 1.34/0.90 | 0.22%/0.46% | 0.0160 | 100.00% | R |
| RSI2 D1 | AUDCAD | N | xm | 36 | 4.1 | 146.0 | 77.78% | 2.54 | 0.10% | 0.23% | 1.12/0.65 | 0.23%/0.55% | 0.0259 | 50.00% | R |
| RSI2 D1 | AUDNZD | G | zero | 51 | 5.8 | 148.2 | 64.71% | 1.76 | 0.06% | 0.24% | 0.98/0.49 | 0.22%/0.46% | chưa | 100.00% | S |
| RSI2 D1 | AUDNZD | G | futures | 51 | 5.8 | 148.2 | 64.71% | 1.75 | 0.06% | 0.24% | 0.98/0.48 | 0.22%/0.47% | chưa | 100.00% | S |
| RSI2 D1 | AUDNZD | G | xm | 48 | 5.5 | 157.5 | 60.42% | 1.45 | 0.04% | 0.25% | 0.80/0.32 | 0.27%/0.54% | chưa | 50.00% | S |
| RSI2 D1 | AUDNZD | N | zero | 51 | 5.8 | 148.2 | 64.71% | 1.76 | 0.06% | 0.24% | 0.98/0.49 | 0.22%/0.46% | chưa | 100.00% | S |
| RSI2 D1 | AUDNZD | N | futures | 51 | 5.8 | 148.2 | 64.71% | 1.75 | 0.06% | 0.24% | 0.98/0.48 | 0.22%/0.47% | chưa | 100.00% | S |
| RSI2 D1 | AUDNZD | N | xm | 48 | 5.5 | 157.5 | 60.42% | 1.45 | 0.04% | 0.25% | 0.80/0.32 | 0.27%/0.54% | chưa | 50.00% | S |
| RSI2 D1 | EURCAD | G | zero | 60 | 6.8 | 146.8 | 68.33% | 1.46 | 0.06% | 0.33% | 1.39/0.36 | 0.35%/0.71% | chưa | 100.00% | S |
| RSI2 D1 | EURCAD | G | futures | 60 | 6.8 | 146.8 | 68.33% | 1.45 | 0.06% | 0.34% | 1.39/0.35 | 0.35%/0.72% | chưa | 100.00% | S |
| RSI2 D1 | EURCAD | G | xm | 56 | 6.4 | 156.9 | 62.50% | 1.00 | -0.00% | 0.74% | 1.19/-0.00 | 0.52%/1.14% | chưa | 75.00% | L |
| RSI2 D1 | EURCAD | N | zero | 60 | 6.8 | 146.8 | 68.33% | 1.46 | 0.06% | 0.33% | 1.39/0.36 | 0.35%/0.71% | chưa | 100.00% | S |
| RSI2 D1 | EURCAD | N | futures | 60 | 6.8 | 146.8 | 68.33% | 1.45 | 0.06% | 0.34% | 1.39/0.35 | 0.35%/0.72% | chưa | 100.00% | S |
| RSI2 D1 | EURCAD | N | xm | 56 | 6.4 | 156.9 | 62.50% | 1.00 | -0.00% | 0.74% | 1.19/-0.00 | 0.52%/1.14% | chưa | 75.00% | L |
| RSI2 D1 | EURCHF | G | zero | 13 | 1.5 | 171.7 | 69.23% | 0.56 | -0.03% | 0.40% | 0.50/-0.19 | 0.39%/1.09% | chưa | 0.00% | L |
| RSI2 D1 | EURCHF | G | futures | 13 | 1.5 | 171.7 | 69.23% | 0.55 | -0.03% | 0.41% | 0.49/-0.19 | 0.39%/1.09% | chưa | 0.00% | L |
| RSI2 D1 | EURCHF | G | xm | 13 | 1.5 | 171.7 | 61.54% | 0.51 | -0.03% | 0.41% | 0.44/-0.21 | 0.40%/1.10% | chưa | 0.00% | L |
| RSI2 D1 | EURCHF | N | zero | 13 | 1.5 | 171.7 | 69.23% | 0.56 | -0.03% | 0.40% | 0.50/-0.19 | 0.39%/1.09% | chưa | 0.00% | L |
| RSI2 D1 | EURCHF | N | futures | 13 | 1.5 | 171.7 | 69.23% | 0.55 | -0.03% | 0.41% | 0.49/-0.19 | 0.39%/1.09% | chưa | 0.00% | L |
| RSI2 D1 | EURCHF | N | xm | 13 | 1.5 | 171.7 | 61.54% | 0.51 | -0.03% | 0.41% | 0.44/-0.21 | 0.40%/1.10% | chưa | 0.00% | L |
| RSI2 D1 | EURGBP | G | zero | 36 | 4.1 | 138.7 | 75.00% | 1.97 | 0.07% | 0.48% | 1.08/0.47 | 0.31%/0.69% | chưa | 100.00% | S |
| RSI2 D1 | EURGBP | G | futures | 36 | 4.1 | 138.7 | 75.00% | 1.96 | 0.07% | 0.48% | 1.07/0.47 | 0.31%/0.70% | chưa | 100.00% | S |
| RSI2 D1 | EURGBP | G | xm | 35 | 4.0 | 139.9 | 68.57% | 1.51 | 0.04% | 0.54% | 0.87/0.28 | 0.34%/0.81% | chưa | 100.00% | S |
| RSI2 D1 | EURGBP | N | zero | 36 | 4.1 | 138.7 | 75.00% | 1.97 | 0.07% | 0.48% | 1.08/0.47 | 0.31%/0.69% | chưa | 100.00% | S |
| RSI2 D1 | EURGBP | N | futures | 36 | 4.1 | 138.7 | 75.00% | 1.96 | 0.07% | 0.48% | 1.07/0.47 | 0.31%/0.70% | chưa | 100.00% | S |
| RSI2 D1 | EURGBP | N | xm | 35 | 4.0 | 139.9 | 68.57% | 1.51 | 0.04% | 0.54% | 0.87/0.28 | 0.34%/0.81% | chưa | 100.00% | S |
| RSI2 D1 | GBPAUD | G | zero | 67 | 7.6 | 157.6 | 67.16% | 1.51 | 0.11% | 0.84% | 0.76/0.42 | 0.56%/1.17% | chưa | 25.00% | S |
| RSI2 D1 | GBPAUD | G | futures | 67 | 7.6 | 157.6 | 65.67% | 1.50 | 0.11% | 0.84% | 0.76/0.42 | 0.56%/1.17% | chưa | 25.00% | S |
| RSI2 D1 | GBPAUD | G | xm | 67 | 7.6 | 157.6 | 59.70% | 1.23 | 0.06% | 0.91% | 0.54/0.21 | 0.66%/1.41% | chưa | 25.00% | S |
| RSI2 D1 | GBPAUD | N | zero | 67 | 7.6 | 157.6 | 67.16% | 1.51 | 0.11% | 0.84% | 0.76/0.42 | 0.56%/1.17% | chưa | 25.00% | S |
| RSI2 D1 | GBPAUD | N | futures | 67 | 7.6 | 157.6 | 65.67% | 1.50 | 0.11% | 0.84% | 0.76/0.42 | 0.56%/1.17% | chưa | 25.00% | S |
| RSI2 D1 | GBPAUD | N | xm | 67 | 7.6 | 157.6 | 59.70% | 1.23 | 0.06% | 0.91% | 0.54/0.21 | 0.66%/1.41% | chưa | 25.00% | S |
| RSI2 D1 | GBPCAD | G | zero | 57 | 6.5 | 159.2 | 64.91% | 0.94 | -0.01% | 0.71% | 0.67/-0.05 | 0.61%/1.34% | chưa | 50.00% | L |
| RSI2 D1 | GBPCAD | G | futures | 57 | 6.5 | 159.2 | 64.91% | 0.94 | -0.01% | 0.71% | 0.67/-0.06 | 0.61%/1.34% | chưa | 50.00% | L |
| RSI2 D1 | GBPCAD | G | xm | 57 | 6.5 | 159.2 | 59.65% | 0.84 | -0.03% | 0.81% | 0.57/-0.16 | 0.67%/1.45% | chưa | 0.00% | L |
| RSI2 D1 | GBPCAD | N | zero | 57 | 6.5 | 159.2 | 64.91% | 0.94 | -0.01% | 0.71% | 0.67/-0.05 | 0.61%/1.34% | chưa | 50.00% | L |
| RSI2 D1 | GBPCAD | N | futures | 57 | 6.5 | 159.2 | 64.91% | 0.94 | -0.01% | 0.71% | 0.67/-0.06 | 0.61%/1.34% | chưa | 50.00% | L |
| RSI2 D1 | GBPCAD | N | xm | 57 | 6.5 | 159.2 | 59.65% | 0.84 | -0.03% | 0.81% | 0.57/-0.16 | 0.67%/1.45% | chưa | 0.00% | L |
| RSI2 D1 | GBPNZD | G | zero | 64 | 7.3 | 171.8 | 71.88% | 0.92 | -0.02% | 0.82% | 0.69/-0.07 | 0.89%/1.87% | chưa | 50.00% | L |
| RSI2 D1 | GBPNZD | G | futures | 64 | 7.3 | 171.8 | 71.88% | 0.92 | -0.02% | 0.82% | 0.69/-0.08 | 0.90%/1.88% | chưa | 50.00% | L |
| RSI2 D1 | GBPNZD | G | xm | 63 | 7.2 | 178.7 | 68.25% | 0.78 | -0.06% | 0.93% | 0.54/-0.21 | 1.12%/2.39% | chưa | 25.00% | L |
| RSI2 D1 | GBPNZD | N | zero | 64 | 7.3 | 171.8 | 71.88% | 0.92 | -0.02% | 0.82% | 0.69/-0.07 | 0.89%/1.87% | chưa | 50.00% | L |
| RSI2 D1 | GBPNZD | N | futures | 64 | 7.3 | 171.8 | 71.88% | 0.92 | -0.02% | 0.82% | 0.69/-0.08 | 0.90%/1.88% | chưa | 50.00% | L |
| RSI2 D1 | GBPNZD | N | xm | 63 | 7.2 | 178.7 | 68.25% | 0.78 | -0.06% | 0.93% | 0.54/-0.21 | 1.12%/2.39% | chưa | 25.00% | L |
| RSI2 D1 | GER40 | G | zero | 67 | 7.6 | 145.8 | 62.69% | 0.97 | -0.02% | 1.56% | 1.00/-0.03 | 1.88%/4.27% | chưa | 75.00% | L |
| RSI2 D1 | GER40 | G | futures | 67 | 7.6 | 145.8 | 62.69% | 0.97 | -0.02% | 1.56% | 1.00/-0.03 | 1.89%/4.28% | chưa | 75.00% | L |
| RSI2 D1 | GER40 | G | xm | 59 | 6.7 | 149.7 | 62.71% | 0.73 | -0.16% | 2.40% | 0.73/-0.26 | 2.32%/5.25% | chưa | 25.00% | L |
| RSI2 D1 | GER40 | N | zero | 67 | 7.6 | 145.8 | 62.69% | 0.97 | -0.02% | 1.56% | 1.00/-0.03 | 1.88%/4.27% | chưa | 75.00% | L |
| RSI2 D1 | GER40 | N | futures | 67 | 7.6 | 145.8 | 62.69% | 0.97 | -0.02% | 1.56% | 1.00/-0.03 | 1.89%/4.28% | chưa | 75.00% | L |
| RSI2 D1 | GER40 | N | xm | 59 | 6.7 | 149.7 | 62.71% | 0.73 | -0.16% | 2.40% | 0.73/-0.26 | 2.32%/5.25% | chưa | 25.00% | L |
| RSI2 D1 | US100 | G | zero | 87 | 9.9 | 136.3 | 71.26% | 1.53 | 0.35% | 1.70% | 1.22/0.46 | 1.60%/3.33% | chưa | 75.00% | S |
| RSI2 D1 | US100 | G | futures | 87 | 9.9 | 136.3 | 71.26% | 1.53 | 0.35% | 1.70% | 1.22/0.46 | 1.60%/3.33% | chưa | 75.00% | S |
| RSI2 D1 | US100 | G | xm | 74 | 8.4 | 140.4 | 63.51% | 0.90 | -0.08% | 2.32% | 0.85/-0.10 | 2.26%/5.23% | chưa | 25.00% | L |
| RSI2 D1 | US100 | N | zero | 87 | 9.9 | 136.3 | 71.26% | 1.53 | 0.35% | 1.70% | 1.22/0.46 | 1.60%/3.33% | chưa | 75.00% | S |
| RSI2 D1 | US100 | N | futures | 87 | 9.9 | 136.3 | 71.26% | 1.53 | 0.35% | 1.70% | 1.22/0.46 | 1.60%/3.33% | chưa | 75.00% | S |
| RSI2 D1 | US100 | N | xm | 74 | 8.4 | 140.4 | 63.51% | 0.90 | -0.08% | 2.32% | 0.85/-0.10 | 2.26%/5.23% | chưa | 25.00% | L |
| RSI2 D1 | NZDUSD | G | zero | 47 | 5.4 | 172.6 | 57.45% | 0.98 | -0.00% | 0.83% | 0.89/-0.01 | 0.78%/1.72% | chưa | 50.00% | L |
| RSI2 D1 | NZDUSD | G | futures | 47 | 5.4 | 172.6 | 57.45% | 0.98 | -0.01% | 0.83% | 0.88/-0.02 | 0.79%/1.73% | chưa | 50.00% | L |
| RSI2 D1 | NZDUSD | G | xm | 46 | 5.2 | 174.2 | 52.17% | 0.75 | -0.06% | 1.15% | 0.69/-0.24 | 1.03%/1.96% | chưa | 25.00% | L |
| RSI2 D1 | NZDUSD | N | zero | 47 | 5.4 | 172.6 | 57.45% | 0.98 | -0.00% | 0.83% | 0.89/-0.01 | 0.78%/1.72% | chưa | 50.00% | L |
| RSI2 D1 | NZDUSD | N | futures | 47 | 5.4 | 172.6 | 57.45% | 0.98 | -0.01% | 0.83% | 0.88/-0.02 | 0.79%/1.73% | chưa | 50.00% | L |
| RSI2 D1 | NZDUSD | N | xm | 46 | 5.2 | 174.2 | 52.17% | 0.75 | -0.06% | 1.15% | 0.69/-0.24 | 1.03%/1.96% | chưa | 25.00% | L |
| RSI2 D1 | US500 | G | zero | 75 | 8.5 | 139.2 | 73.33% | 2.08 | 0.33% | 1.41% | 1.34/0.73 | 0.84%/1.65% | 0.1896 | 100.00% | R |
| RSI2 D1 | US500 | G | futures | 75 | 8.5 | 139.2 | 73.33% | 2.08 | 0.33% | 1.42% | 1.34/0.73 | 0.85%/1.65% | 0.1896 | 100.00% | R |
| RSI2 D1 | US500 | G | xm | 74 | 8.4 | 140.4 | 67.57% | 1.36 | 0.14% | 2.01% | 0.99/0.30 | 1.06%/2.22% | chưa | 100.00% | S |
| RSI2 D1 | US500 | N | zero | 75 | 8.5 | 139.2 | 73.33% | 2.08 | 0.33% | 1.41% | 1.34/0.73 | 0.84%/1.65% | 0.1896 | 100.00% | R |
| RSI2 D1 | US500 | N | futures | 75 | 8.5 | 139.2 | 73.33% | 2.08 | 0.33% | 1.42% | 1.34/0.73 | 0.85%/1.65% | 0.1896 | 100.00% | R |
| RSI2 D1 | US500 | N | xm | 74 | 8.4 | 140.4 | 67.57% | 1.36 | 0.14% | 2.01% | 0.99/0.30 | 1.06%/2.22% | chưa | 100.00% | S |
| RSI2 D1 | USDCAD | G | zero | 57 | 6.5 | 166.3 | 64.91% | 1.24 | 0.04% | 0.26% | 0.93/0.22 | 0.45%/0.99% | chưa | 75.00% | S |
| RSI2 D1 | USDCAD | G | futures | 57 | 6.5 | 166.3 | 64.91% | 1.24 | 0.04% | 0.26% | 0.93/0.21 | 0.45%/0.99% | chưa | 75.00% | S |
| RSI2 D1 | USDCAD | G | xm | 57 | 6.5 | 166.3 | 63.16% | 1.19 | 0.03% | 0.27% | 0.89/0.17 | 0.46%/1.01% | chưa | 75.00% | S |
| RSI2 D1 | USDCAD | N | zero | 57 | 6.5 | 166.3 | 64.91% | 1.24 | 0.04% | 0.26% | 0.93/0.22 | 0.45%/0.99% | chưa | 75.00% | S |
| RSI2 D1 | USDCAD | N | futures | 57 | 6.5 | 166.3 | 64.91% | 1.24 | 0.04% | 0.26% | 0.93/0.21 | 0.45%/0.99% | chưa | 75.00% | S |
| RSI2 D1 | USDCAD | N | xm | 57 | 6.5 | 166.3 | 63.16% | 1.19 | 0.03% | 0.27% | 0.89/0.17 | 0.46%/1.01% | chưa | 75.00% | S |
| RSI2 D1 | XAUUSD | G | zero | 62 | 7.1 | 156.8 | 62.90% | 0.77 | -0.16% | 2.50% | 1.03/-0.23 | 2.47%/5.16% | chưa | 100.00% | L |
| RSI2 D1 | XAUUSD | G | futures | 62 | 7.1 | 156.8 | 62.90% | 0.77 | -0.16% | 2.50% | 1.02/-0.23 | 2.47%/5.17% | chưa | 100.00% | L |
| RSI2 D1 | XAUUSD | G | xm | 64 | 7.3 | 159.8 | 56.25% | 0.59 | -0.32% | 2.76% | 0.34/-0.46 | 3.33%/6.53% | chưa | 0.00% | L |
| RSI2 D1 | XAUUSD | N | zero | 62 | 7.1 | 160.6 | 66.13% | 1.13 | 0.06% | 1.28% | 1.08/0.11 | 1.50%/3.39% | chưa | 100.00% | S |
| RSI2 D1 | XAUUSD | N | futures | 62 | 7.1 | 160.6 | 66.13% | 1.13 | 0.06% | 1.29% | 1.08/0.11 | 1.50%/3.40% | chưa | 100.00% | S |
| RSI2 D1 | XAUUSD | N | xm | 64 | 7.3 | 163.5 | 59.38% | 0.83 | -0.10% | 1.94% | 0.40/-0.17 | 2.13%/4.42% | chưa | 25.00% | L |
| US100↔vàng | US100↔XAUUSD | G | zero | 49 | 5.6 | 1560.5 | 42.86% | 5.35 | 18.93% | 31.01% | 1.22/1.00 | 27.47%/41.02% | 0.3513 | 100.00% | R |
| US100↔vàng | US100↔XAUUSD | G | futures | 49 | 5.6 | 1560.5 | 42.86% | 5.34 | 18.92% | 31.01% | 1.22/1.00 | 27.47%/41.03% | 0.3513 | 100.00% | R |
| US100↔vàng | US100↔XAUUSD | G | xm | 43 | 4.9 | 1779.3 | 25.58% | 1.44 | 2.59% | 48.46% | 0.26/0.23 | 42.75%/63.68% | chưa | 100.00% | S |
| US100↔vàng | US100↔XAUUSD | N/A | zero | 49 | 5.6 | 1560.5 | 42.86% | 5.35 | 18.93% | 31.01% | 1.22/1.00 | 27.47%/41.02% | 0.3513 | 100.00% | R |
| US100↔vàng | US100↔XAUUSD | N/A | futures | 49 | 5.6 | 1560.5 | 42.86% | 5.34 | 18.92% | 31.01% | 1.22/1.00 | 27.47%/41.03% | 0.3513 | 100.00% | R |
| US100↔vàng | US100↔XAUUSD | N/A | xm | 43 | 4.9 | 1779.3 | 25.58% | 1.44 | 2.59% | 48.46% | 0.26/0.23 | 42.75%/63.68% | chưa | 100.00% | S |

## 8. Canonical cố định: không tối ưu lại để đổi bộ gốc

| Hệ | Mã | SL | Phí | Lệnh/năm | PF | CAGR | DD | Sharpe |
|---|---|---|---|---:|---:|---:|---:|---:|
| ICT as-traded | GER40 | G | zero | 4868.3 | 0.91 | -97.98% | 100.00% | -2.90 |
| ICT as-traded | GER40 | G | futures | 4868.3 | 0.74 | -100.00% | 100.00% | -8.70 |
| ICT as-traded | GER40 | G | xm | 4868.3 | 0.33 | -100.00% | 100.00% | -19.84 |
| ICT as-traded | GER40 | N | zero | 1924.4 | 0.97 | -31.61% | 97.88% | -0.52 |
| ICT as-traded | GER40 | N | futures | 1924.4 | 0.93 | -52.65% | 99.87% | -1.25 |
| ICT as-traded | GER40 | N | xm | 1924.4 | 0.72 | -95.44% | 100.00% | -5.58 |
| ICT as-traded | US100 | G | zero | 6177.3 | 1.01 | -10.86% | 99.82% | 0.50 |
| ICT as-traded | US100 | G | futures | 6177.3 | 0.87 | -99.89% | 100.00% | -5.09 |
| ICT as-traded | US100 | G | xm | 6177.3 | 0.29 | -100.00% | 100.00% | -18.57 |
| ICT as-traded | US100 | N | zero | 2439.9 | 0.98 | -27.07% | 95.88% | -0.38 |
| ICT as-traded | US100 | N | futures | 2439.9 | 0.95 | -46.44% | 99.68% | -0.98 |
| ICT as-traded | US100 | N | xm | 2439.9 | 0.71 | -97.70% | 100.00% | -6.59 |
| ICT as-traded | US500 | G | zero | 5489.1 | 0.95 | -92.17% | 100.00% | -1.84 |
| ICT as-traded | US500 | G | futures | 5489.1 | 0.72 | -100.00% | 100.00% | -10.47 |
| ICT as-traded | US500 | G | xm | 5489.1 | 0.42 | -100.00% | 100.00% | -19.68 |
| ICT as-traded | US500 | N | zero | 2299.9 | 1.00 | -10.68% | 82.23% | 0.02 |
| ICT as-traded | US500 | N | futures | 2299.9 | 0.94 | -54.14% | 99.92% | -1.29 |
| ICT as-traded | US500 | N | xm | 2299.9 | 0.77 | -94.08% | 100.00% | -5.16 |
| ICT as-traded | XAUUSD | G | zero | 6342.3 | 0.96 | -91.12% | 100.00% | -1.49 |
| ICT as-traded | XAUUSD | G | futures | 6342.3 | 0.74 | -100.00% | 100.00% | -10.10 |
| ICT as-traded | XAUUSD | G | xm | 6342.3 | 0.20 | -100.00% | 100.00% | -20.92 |
| ICT as-traded | XAUUSD | N | zero | 2537.6 | 0.96 | -40.02% | 99.03% | -0.77 |
| ICT as-traded | XAUUSD | N | futures | 2537.6 | 0.91 | -68.99% | 100.00% | -2.04 |
| ICT as-traded | XAUUSD | N | xm | 2537.6 | 0.58 | -99.79% | 100.00% | -10.01 |
| Sweep-only | GER40 | G | zero | 11636.5 | 1.01 | -52.48% | 99.99% | 0.35 |
| Sweep-only | GER40 | G | futures | 11636.5 | 0.77 | -100.00% | 100.00% | -11.80 |
| Sweep-only | GER40 | G | xm | 11636.5 | 0.28 | -100.00% | 100.00% | -23.98 |
| Sweep-only | GER40 | N | zero | 2481.1 | 0.97 | -40.11% | 99.44% | -0.66 |
| Sweep-only | GER40 | N | futures | 2481.1 | 0.93 | -62.70% | 99.99% | -1.49 |
| Sweep-only | GER40 | N | xm | 2481.1 | 0.73 | -98.01% | 100.00% | -6.30 |
| Sweep-only | US100 | G | zero | 17653.3 | 1.04 | 1072.79% | 99.98% | 2.21 |
| Sweep-only | US100 | G | futures | 17653.3 | 0.82 | -100.00% | 100.00% | -11.06 |
| Sweep-only | US100 | G | xm | 17653.3 | 0.18 | -100.00% | 100.00% | -23.30 |
| Sweep-only | US100 | N | zero | 3208.5 | 1.02 | 5.99% | 68.04% | 0.40 |
| Sweep-only | US100 | N | futures | 3208.5 | 0.99 | -29.28% | 97.94% | -0.30 |
| Sweep-only | US100 | N | xm | 3208.5 | 0.74 | -98.81% | 100.00% | -6.59 |
| Sweep-only | US500 | G | zero | 14054.7 | 1.03 | 176.57% | 99.98% | 1.46 |
| Sweep-only | US500 | G | futures | 14054.7 | 0.72 | -100.00% | 100.00% | -15.12 |
| Sweep-only | US500 | G | xm | 14054.7 | 0.36 | -100.00% | 100.00% | -24.09 |
| Sweep-only | US500 | N | zero | 3032.4 | 1.00 | -19.16% | 95.51% | -0.08 |
| Sweep-only | US500 | N | futures | 3032.4 | 0.93 | -66.95% | 99.99% | -1.56 |
| Sweep-only | US500 | N | xm | 3032.4 | 0.77 | -97.76% | 100.00% | -5.79 |
| Sweep-only | XAUUSD | G | zero | 16349.6 | 1.02 | 165.08% | 99.72% | 1.45 |
| Sweep-only | XAUUSD | G | futures | 16349.6 | 0.73 | -100.00% | 100.00% | -15.62 |
| Sweep-only | XAUUSD | G | xm | 16349.6 | 0.14 | -100.00% | 100.00% | -25.35 |
| Sweep-only | XAUUSD | N | zero | 3278.2 | 1.00 | -14.67% | 89.13% | 0.01 |
| Sweep-only | XAUUSD | N | futures | 3278.2 | 0.94 | -63.33% | 99.99% | -1.41 |
| Sweep-only | XAUUSD | N | xm | 3278.2 | 0.60 | -99.94% | 100.00% | -10.19 |
| CHoCH H4 1R | AUDCAD | G | zero | 27.2 | 1.02 | 0.14% | 14.23% | 0.05 |
| CHoCH H4 1R | AUDCAD | G | futures | 27.2 | 1.01 | 0.04% | 14.48% | 0.03 |
| CHoCH H4 1R | AUDCAD | G | xm | 27.2 | 0.81 | -3.02% | 28.23% | -0.56 |
| CHoCH H4 1R | AUDCAD | N | zero | 24.5 | 1.02 | 0.13% | 11.90% | 0.05 |
| CHoCH H4 1R | AUDCAD | N | futures | 24.5 | 1.01 | 0.06% | 12.16% | 0.04 |
| CHoCH H4 1R | AUDCAD | N | xm | 24.5 | 0.82 | -2.56% | 24.89% | -0.49 |
| CHoCH H4 1R | AUDNZD | G | zero | 25.3 | 0.88 | -1.74% | 25.62% | -0.32 |
| CHoCH H4 1R | AUDNZD | G | futures | 25.3 | 0.87 | -1.85% | 25.94% | -0.34 |
| CHoCH H4 1R | AUDNZD | G | xm | 25.3 | 0.64 | -5.56% | 43.04% | -1.07 |
| CHoCH H4 1R | AUDNZD | N | zero | 23.3 | 0.83 | -2.22% | 22.99% | -0.44 |
| CHoCH H4 1R | AUDNZD | N | futures | 23.3 | 0.83 | -2.30% | 23.52% | -0.46 |
| CHoCH H4 1R | AUDNZD | N | xm | 23.3 | 0.63 | -5.40% | 41.40% | -1.09 |
| CHoCH H4 1R | EURCAD | G | zero | 23.0 | 1.05 | 0.40% | 9.92% | 0.11 |
| CHoCH H4 1R | EURCAD | G | futures | 23.0 | 1.04 | 0.34% | 10.11% | 0.10 |
| CHoCH H4 1R | EURCAD | G | xm | 23.0 | 0.89 | -1.48% | 15.84% | -0.29 |
| CHoCH H4 1R | EURCAD | N | zero | 22.0 | 1.15 | 1.47% | 10.83% | 0.34 |
| CHoCH H4 1R | EURCAD | N | futures | 22.0 | 1.15 | 1.42% | 10.99% | 0.32 |
| CHoCH H4 1R | EURCAD | N | xm | 22.0 | 0.99 | -0.25% | 16.53% | -0.03 |
| CHoCH H4 1R | EURCHF | G | zero | 26.1 | 0.92 | -1.17% | 19.32% | -0.20 |
| CHoCH H4 1R | EURCHF | G | futures | 26.1 | 0.91 | -1.30% | 19.71% | -0.23 |
| CHoCH H4 1R | EURCHF | G | xm | 26.1 | 0.70 | -4.61% | 34.48% | -0.89 |
| CHoCH H4 1R | EURCHF | N | zero | 21.9 | 0.90 | -1.24% | 12.65% | -0.24 |
| CHoCH H4 1R | EURCHF | N | futures | 21.9 | 0.89 | -1.33% | 13.02% | -0.26 |
| CHoCH H4 1R | EURCHF | N | xm | 21.9 | 0.71 | -3.75% | 29.17% | -0.78 |
| CHoCH H4 1R | EURGBP | G | zero | 26.9 | 0.92 | -1.28% | 25.24% | -0.22 |
| CHoCH H4 1R | EURGBP | G | futures | 26.9 | 0.91 | -1.43% | 26.04% | -0.25 |
| CHoCH H4 1R | EURGBP | G | xm | 26.9 | 0.76 | -3.73% | 37.17% | -0.70 |
| CHoCH H4 1R | EURGBP | N | zero | 24.7 | 0.92 | -1.16% | 20.20% | -0.21 |
| CHoCH H4 1R | EURGBP | N | futures | 24.7 | 0.91 | -1.26% | 20.53% | -0.23 |
| CHoCH H4 1R | EURGBP | N | xm | 24.7 | 0.78 | -3.13% | 30.09% | -0.61 |
| CHoCH H4 1R | GBPAUD | G | zero | 26.7 | 0.69 | -4.87% | 38.92% | -0.94 |
| CHoCH H4 1R | GBPAUD | G | futures | 26.7 | 0.69 | -4.91% | 39.14% | -0.95 |
| CHoCH H4 1R | GBPAUD | G | xm | 26.7 | 0.61 | -6.50% | 46.41% | -1.26 |
| CHoCH H4 1R | GBPAUD | N | zero | 23.4 | 0.75 | -3.43% | 31.54% | -0.70 |
| CHoCH H4 1R | GBPAUD | N | futures | 23.4 | 0.75 | -3.46% | 31.69% | -0.71 |
| CHoCH H4 1R | GBPAUD | N | xm | 23.4 | 0.66 | -4.83% | 38.45% | -0.99 |
| CHoCH H4 1R | GBPCAD | G | zero | 27.0 | 1.02 | 0.15% | 13.68% | 0.05 |
| CHoCH H4 1R | GBPCAD | G | futures | 27.0 | 1.02 | 0.10% | 13.93% | 0.04 |
| CHoCH H4 1R | GBPCAD | G | xm | 27.0 | 0.86 | -2.12% | 23.73% | -0.38 |
| CHoCH H4 1R | GBPCAD | N | zero | 24.3 | 1.13 | 1.36% | 7.83% | 0.30 |
| CHoCH H4 1R | GBPCAD | N | futures | 24.3 | 1.13 | 1.32% | 7.89% | 0.29 |
| CHoCH H4 1R | GBPCAD | N | xm | 24.3 | 0.95 | -0.70% | 10.70% | -0.12 |
| CHoCH H4 1R | GBPNZD | G | zero | 25.4 | 0.80 | -2.94% | 27.45% | -0.57 |
| CHoCH H4 1R | GBPNZD | G | futures | 25.4 | 0.80 | -2.98% | 27.69% | -0.57 |
| CHoCH H4 1R | GBPNZD | G | xm | 25.4 | 0.66 | -5.21% | 40.21% | -1.02 |
| CHoCH H4 1R | GBPNZD | N | zero | 21.5 | 0.95 | -0.68% | 21.75% | -0.12 |
| CHoCH H4 1R | GBPNZD | N | futures | 21.5 | 0.95 | -0.70% | 21.86% | -0.13 |
| CHoCH H4 1R | GBPNZD | N | xm | 21.5 | 0.79 | -2.62% | 28.66% | -0.54 |
| CHoCH H4 1R | GER40 | G | zero | 28.2 | 0.91 | -1.44% | 19.07% | -0.25 |
| CHoCH H4 1R | GER40 | G | futures | 28.2 | 0.90 | -1.54% | 19.68% | -0.26 |
| CHoCH H4 1R | GER40 | G | xm | 28.2 | 0.76 | -3.99% | 33.22% | -0.72 |
| CHoCH H4 1R | GER40 | N | zero | 23.9 | 0.99 | -0.19% | 14.71% | -0.02 |
| CHoCH H4 1R | GER40 | N | futures | 23.9 | 0.99 | -0.26% | 15.10% | -0.03 |
| CHoCH H4 1R | GER40 | N | xm | 23.9 | 0.82 | -2.50% | 26.98% | -0.48 |
| CHoCH H4 1R | US100 | G | zero | 31.5 | 0.94 | -1.09% | 19.69% | -0.17 |
| CHoCH H4 1R | US100 | G | futures | 31.5 | 0.94 | -1.14% | 19.92% | -0.18 |
| CHoCH H4 1R | US100 | G | xm | 31.5 | 0.83 | -2.92% | 27.96% | -0.50 |
| CHoCH H4 1R | US100 | N | zero | 28.2 | 0.87 | -2.00% | 22.70% | -0.36 |
| CHoCH H4 1R | US100 | N | futures | 28.2 | 0.87 | -2.04% | 22.87% | -0.36 |
| CHoCH H4 1R | US100 | N | xm | 28.2 | 0.78 | -3.43% | 29.49% | -0.64 |
| CHoCH H4 1R | NZDUSD | G | zero | 29.1 | 1.06 | 0.65% | 16.19% | 0.15 |
| CHoCH H4 1R | NZDUSD | G | futures | 29.1 | 1.05 | 0.53% | 16.62% | 0.13 |
| CHoCH H4 1R | NZDUSD | G | xm | 29.1 | 0.93 | -1.26% | 22.63% | -0.21 |
| CHoCH H4 1R | NZDUSD | N | zero | 26.6 | 1.12 | 1.36% | 14.18% | 0.29 |
| CHoCH H4 1R | NZDUSD | N | futures | 26.6 | 1.11 | 1.27% | 14.34% | 0.27 |
| CHoCH H4 1R | NZDUSD | N | xm | 26.6 | 0.99 | -0.21% | 18.17% | -0.01 |
| CHoCH H4 1R | US500 | G | zero | 26.3 | 0.98 | -0.34% | 13.74% | -0.04 |
| CHoCH H4 1R | US500 | G | futures | 26.3 | 0.98 | -0.44% | 14.10% | -0.06 |
| CHoCH H4 1R | US500 | G | xm | 26.3 | 0.88 | -1.78% | 19.24% | -0.33 |
| CHoCH H4 1R | US500 | N | zero | 24.4 | 0.81 | -2.71% | 26.23% | -0.53 |
| CHoCH H4 1R | US500 | N | futures | 24.4 | 0.80 | -2.80% | 26.59% | -0.55 |
| CHoCH H4 1R | US500 | N | xm | 24.4 | 0.72 | -4.02% | 32.70% | -0.81 |
| CHoCH H4 1R | USDCAD | G | zero | 27.0 | 1.01 | -0.02% | 20.25% | 0.02 |
| CHoCH H4 1R | USDCAD | G | futures | 27.0 | 1.00 | -0.11% | 20.56% | 0.01 |
| CHoCH H4 1R | USDCAD | G | xm | 27.0 | 0.87 | -2.03% | 27.39% | -0.36 |
| CHoCH H4 1R | USDCAD | N | zero | 25.1 | 1.12 | 1.32% | 17.78% | 0.29 |
| CHoCH H4 1R | USDCAD | N | futures | 25.1 | 1.12 | 1.26% | 18.01% | 0.27 |
| CHoCH H4 1R | USDCAD | N | xm | 25.1 | 0.97 | -0.49% | 24.35% | -0.07 |
| CHoCH H4 1R | XAUUSD | G | zero | 26.4 | 1.03 | 0.32% | 15.27% | 0.09 |
| CHoCH H4 1R | XAUUSD | G | futures | 26.4 | 1.03 | 0.22% | 15.67% | 0.07 |
| CHoCH H4 1R | XAUUSD | G | xm | 26.4 | 0.84 | -2.44% | 26.28% | -0.45 |
| CHoCH H4 1R | XAUUSD | N | zero | 24.3 | 1.01 | -0.01% | 13.60% | 0.02 |
| CHoCH H4 1R | XAUUSD | N | futures | 24.3 | 1.00 | -0.09% | 13.95% | 0.01 |
| CHoCH H4 1R | XAUUSD | N | xm | 24.3 | 0.82 | -2.52% | 28.09% | -0.48 |
| RSI2 D1 | AUDCAD | G | zero | 4.2 | 1.35 | 0.04% | 0.27% | 0.23 |
| RSI2 D1 | AUDCAD | G | futures | 4.2 | 1.34 | 0.03% | 0.27% | 0.22 |
| RSI2 D1 | AUDCAD | G | xm | 4.2 | 0.98 | -0.00% | 0.47% | -0.02 |
| RSI2 D1 | AUDCAD | N | zero | 4.2 | 1.35 | 0.04% | 0.27% | 0.23 |
| RSI2 D1 | AUDCAD | N | futures | 4.2 | 1.34 | 0.03% | 0.27% | 0.22 |
| RSI2 D1 | AUDCAD | N | xm | 4.2 | 0.98 | -0.00% | 0.47% | -0.02 |
| RSI2 D1 | AUDNZD | G | zero | 5.9 | 1.12 | 0.01% | 0.47% | 0.10 |
| RSI2 D1 | AUDNZD | G | futures | 5.9 | 1.11 | 0.01% | 0.47% | 0.10 |
| RSI2 D1 | AUDNZD | G | xm | 5.9 | 0.90 | -0.01% | 0.54% | -0.10 |
| RSI2 D1 | AUDNZD | N | zero | 5.9 | 1.12 | 0.01% | 0.47% | 0.10 |
| RSI2 D1 | AUDNZD | N | futures | 5.9 | 1.11 | 0.01% | 0.47% | 0.10 |
| RSI2 D1 | AUDNZD | N | xm | 5.9 | 0.90 | -0.01% | 0.54% | -0.10 |
| RSI2 D1 | EURCAD | G | zero | 5.8 | 2.37 | 0.11% | 0.29% | 0.77 |
| RSI2 D1 | EURCAD | G | futures | 5.8 | 2.35 | 0.11% | 0.29% | 0.77 |
| RSI2 D1 | EURCAD | G | xm | 5.8 | 1.95 | 0.08% | 0.30% | 0.60 |
| RSI2 D1 | EURCAD | N | zero | 5.8 | 2.37 | 0.11% | 0.29% | 0.77 |
| RSI2 D1 | EURCAD | N | futures | 5.8 | 2.35 | 0.11% | 0.29% | 0.77 |
| RSI2 D1 | EURCAD | N | xm | 5.8 | 1.95 | 0.08% | 0.30% | 0.60 |
| RSI2 D1 | EURCHF | G | zero | 2.3 | 0.23 | -0.07% | 0.63% | -0.46 |
| RSI2 D1 | EURCHF | G | futures | 2.3 | 0.23 | -0.07% | 0.64% | -0.46 |
| RSI2 D1 | EURCHF | G | xm | 2.3 | 0.20 | -0.07% | 0.66% | -0.49 |
| RSI2 D1 | EURCHF | N | zero | 2.3 | 0.23 | -0.07% | 0.63% | -0.46 |
| RSI2 D1 | EURCHF | N | futures | 2.3 | 0.23 | -0.07% | 0.64% | -0.46 |
| RSI2 D1 | EURCHF | N | xm | 2.3 | 0.20 | -0.07% | 0.66% | -0.49 |
| RSI2 D1 | EURGBP | G | zero | 4.4 | 1.69 | 0.06% | 0.44% | 0.40 |
| RSI2 D1 | EURGBP | G | futures | 4.4 | 1.68 | 0.06% | 0.44% | 0.39 |
| RSI2 D1 | EURGBP | G | xm | 4.4 | 1.30 | 0.03% | 0.49% | 0.19 |
| RSI2 D1 | EURGBP | N | zero | 4.4 | 1.69 | 0.06% | 0.44% | 0.40 |
| RSI2 D1 | EURGBP | N | futures | 4.4 | 1.68 | 0.06% | 0.44% | 0.39 |
| RSI2 D1 | EURGBP | N | xm | 4.4 | 1.30 | 0.03% | 0.49% | 0.19 |
| RSI2 D1 | GBPAUD | G | zero | 6.0 | 0.94 | -0.01% | 0.83% | -0.06 |
| RSI2 D1 | GBPAUD | G | futures | 6.0 | 0.93 | -0.01% | 0.84% | -0.06 |
| RSI2 D1 | GBPAUD | G | xm | 6.0 | 0.76 | -0.06% | 1.02% | -0.23 |
| RSI2 D1 | GBPAUD | N | zero | 6.0 | 0.94 | -0.01% | 0.83% | -0.06 |
| RSI2 D1 | GBPAUD | N | futures | 6.0 | 0.93 | -0.01% | 0.84% | -0.06 |
| RSI2 D1 | GBPAUD | N | xm | 6.0 | 0.76 | -0.06% | 1.02% | -0.23 |
| RSI2 D1 | GBPCAD | G | zero | 7.1 | 1.13 | 0.03% | 0.40% | 0.12 |
| RSI2 D1 | GBPCAD | G | futures | 7.1 | 1.13 | 0.03% | 0.40% | 0.12 |
| RSI2 D1 | GBPCAD | G | xm | 7.1 | 1.02 | 0.00% | 0.43% | 0.02 |
| RSI2 D1 | GBPCAD | N | zero | 7.1 | 1.13 | 0.03% | 0.40% | 0.12 |
| RSI2 D1 | GBPCAD | N | futures | 7.1 | 1.13 | 0.03% | 0.40% | 0.12 |
| RSI2 D1 | GBPCAD | N | xm | 7.1 | 1.02 | 0.00% | 0.43% | 0.02 |
| RSI2 D1 | GBPNZD | G | zero | 6.5 | 1.06 | 0.01% | 0.55% | 0.05 |
| RSI2 D1 | GBPNZD | G | futures | 6.5 | 1.06 | 0.01% | 0.55% | 0.05 |
| RSI2 D1 | GBPNZD | G | xm | 6.5 | 0.93 | -0.02% | 0.71% | -0.07 |
| RSI2 D1 | GBPNZD | N | zero | 6.5 | 1.06 | 0.01% | 0.55% | 0.05 |
| RSI2 D1 | GBPNZD | N | futures | 6.5 | 1.06 | 0.01% | 0.55% | 0.05 |
| RSI2 D1 | GBPNZD | N | xm | 6.5 | 0.93 | -0.02% | 0.71% | -0.07 |
| RSI2 D1 | GER40 | G | zero | 7.9 | 1.25 | 0.13% | 1.02% | 0.21 |
| RSI2 D1 | GER40 | G | futures | 7.9 | 1.25 | 0.12% | 1.02% | 0.20 |
| RSI2 D1 | GER40 | G | xm | 7.9 | 0.88 | -0.07% | 1.34% | -0.11 |
| RSI2 D1 | GER40 | N | zero | 7.9 | 1.25 | 0.13% | 1.02% | 0.21 |
| RSI2 D1 | GER40 | N | futures | 7.9 | 1.25 | 0.12% | 1.02% | 0.20 |
| RSI2 D1 | GER40 | N | xm | 7.9 | 0.88 | -0.07% | 1.34% | -0.11 |
| RSI2 D1 | US100 | G | zero | 8.4 | 1.17 | 0.12% | 2.03% | 0.15 |
| RSI2 D1 | US100 | G | futures | 8.4 | 1.16 | 0.12% | 2.04% | 0.15 |
| RSI2 D1 | US100 | G | xm | 8.4 | 0.88 | -0.11% | 2.86% | -0.13 |
| RSI2 D1 | US100 | N | zero | 8.4 | 1.17 | 0.12% | 2.03% | 0.15 |
| RSI2 D1 | US100 | N | futures | 8.4 | 1.16 | 0.12% | 2.04% | 0.15 |
| RSI2 D1 | US100 | N | xm | 8.4 | 0.88 | -0.11% | 2.86% | -0.13 |
| RSI2 D1 | NZDUSD | G | zero | 5.4 | 1.22 | 0.04% | 0.40% | 0.18 |
| RSI2 D1 | NZDUSD | G | futures | 5.4 | 1.21 | 0.04% | 0.40% | 0.17 |
| RSI2 D1 | NZDUSD | G | xm | 5.4 | 0.97 | -0.01% | 0.47% | -0.03 |
| RSI2 D1 | NZDUSD | N | zero | 5.4 | 1.22 | 0.04% | 0.40% | 0.18 |
| RSI2 D1 | NZDUSD | N | futures | 5.4 | 1.21 | 0.04% | 0.40% | 0.17 |
| RSI2 D1 | NZDUSD | N | xm | 5.4 | 0.97 | -0.01% | 0.47% | -0.03 |
| RSI2 D1 | US500 | G | zero | 9.5 | 1.96 | 0.38% | 1.42% | 0.74 |
| RSI2 D1 | US500 | G | futures | 9.5 | 1.95 | 0.38% | 1.43% | 0.74 |
| RSI2 D1 | US500 | G | xm | 9.5 | 1.40 | 0.19% | 2.01% | 0.37 |
| RSI2 D1 | US500 | N | zero | 9.5 | 1.96 | 0.38% | 1.42% | 0.74 |
| RSI2 D1 | US500 | N | futures | 9.5 | 1.95 | 0.38% | 1.43% | 0.74 |
| RSI2 D1 | US500 | N | xm | 9.5 | 1.40 | 0.19% | 2.01% | 0.37 |
| RSI2 D1 | USDCAD | G | zero | 6.4 | 1.18 | 0.04% | 0.36% | 0.17 |
| RSI2 D1 | USDCAD | G | futures | 6.4 | 1.18 | 0.03% | 0.36% | 0.16 |
| RSI2 D1 | USDCAD | G | xm | 6.4 | 1.14 | 0.03% | 0.36% | 0.13 |
| RSI2 D1 | USDCAD | N | zero | 6.4 | 1.18 | 0.04% | 0.36% | 0.17 |
| RSI2 D1 | USDCAD | N | futures | 6.4 | 1.18 | 0.03% | 0.36% | 0.16 |
| RSI2 D1 | USDCAD | N | xm | 6.4 | 1.14 | 0.03% | 0.36% | 0.13 |
| RSI2 D1 | XAUUSD | G | zero | 6.5 | 1.14 | 0.07% | 1.75% | 0.11 |
| RSI2 D1 | XAUUSD | G | futures | 6.5 | 1.13 | 0.07% | 1.75% | 0.11 |
| RSI2 D1 | XAUUSD | G | xm | 6.5 | 0.77 | -0.16% | 2.10% | -0.23 |
| RSI2 D1 | XAUUSD | N | zero | 6.5 | 1.35 | 0.16% | 1.32% | 0.26 |
| RSI2 D1 | XAUUSD | N | futures | 6.5 | 1.35 | 0.16% | 1.32% | 0.26 |
| RSI2 D1 | XAUUSD | N | xm | 6.5 | 0.88 | -0.07% | 2.10% | -0.11 |
| US100↔vàng | US100↔XAUUSD | G | zero | 3.5 | 10.00 | 21.84% | 31.01% | 1.13 |
| US100↔vàng | US100↔XAUUSD | G | futures | 3.5 | 9.98 | 21.83% | 31.01% | 1.13 |
| US100↔vàng | US100↔XAUUSD | G | xm | 3.5 | 1.82 | 4.57% | 45.27% | 0.33 |
| US100↔vàng | US100↔XAUUSD | N/A | zero | 3.5 | 10.00 | 21.84% | 31.01% | 1.13 |
| US100↔vàng | US100↔XAUUSD | N/A | futures | 3.5 | 9.98 | 21.83% | 31.01% | 1.13 |
| US100↔vàng | US100↔XAUUSD | N/A | xm | 3.5 | 1.82 | 4.57% | 45.27% | 0.33 |

## 9. Những gì sống ở phí0 nhưng KHÔNG giao dịch được

Có3bản sweep-only SLgốc qua cửa thống kê ở **phí0**, đều rớtDDbrain2. Đây là ablation do mình định nghĩa, không phải thành tích ICT của tác giả. Bảng không được dùng quảng bá CAGR: leverage giả định và DD gần mất hết vốn làm nó không khả thi.


| Mã | Lệnh/năm | PF | CAGR lý thuyết | DD | Sharpe | p raw |
|---|---:|---:|---:|---:|---:|---:|
| US500 | 14599 | 1.03 | 326.07% | 99.47% | 1.73 | 0.0020 |
| XAUUSD | 16838 | 1.02 | 57.22% | 99.99% | 1.16 | 0.0020 |
| US100 | 18475 | 1.03 | 668.46% | 99.99% | 1.98 | 0.0020 |

Phí futures-like chỉ$4roundturn đã làm các bản M1 này không còn lãi OOS. Phí XM càng nặng. Nới stop làm giảm turnover và phí/R nhưng alpha gộp cũng đổi, không phải cùng một chiến lược được “miễn phí” vì dời stop.


## 10. So với con số Brendan công bố

| Hệ | Tác giả nói | Nghiên cứu này | Có thể kết luận gì |
|---|---|---|---|
| ICT as-traded | ~$251k/2năm/1NQ;~1996lệnh/năm;34–52%win;đẹp nhất$455k,Sharpe13có cảnh báoperfectfills | M1HistData/CFD,fractal/FVG tái dựng;vài nghìn lệnh/năm,fees làm lỗ;SLnới cải thiệnPF nhưng chưa dương | Khác sốlệnh cho thấy không có đúng fullconfig tác giả;không so đôla NQ với CAGR risk1% |
| Sweep-only | Rule sweep tăng điểm33→69;standalone reversal khoảng50%;không có equitycurve code chuẩn | Một ablation vào open,TP2R,zeroedge mỏng nhưng DDgần100%;mất saucost | Không được gán thành công$251k cho sweep-only |
| CHoCHH4 | ~$62kNQ/$39kES trên2nămkhóa,39/48biếnthểdương,TP1R | ~20–40lệnh/năm phần lớn,không qua100intraday;khácfeed,phânbar vàconfirm | Không tái lập được con số đôla đó bằng CFD/risk% này |
| RSI2 | Rule rõ:stop8%,size10%;**không tìm thấy riêng CAGR24,8% của sleeve** | RSIUS500 có edgegộpnhỏ;XM làm SharpeWF~0,30;CAGR~0,14% do vốn10% và ítlệnh | Không so với24,8% core một cách sai lệch |
| QQQ/vàng core | Video này24,8%,DD11,2%(lock2025+);video khác33,8%,Sharpe1,66 giaiđoạnkhác | US100/GOLD fixedMA200:zero21,84%,DD31,01%;XM4,57%,DD45,27%.WF thấp hơn | Có xu hướnggộp;CFDswap và giaiđoạn khác làm sốkhác;không chépETF thànhCFDmiễnphí |

Trích transcript `gJLKVsIqiTE`: “this core strategy…24.8% a year…max draw down of11.2%…when it holds QQQ and when it holds gold”. Lỗi gán số choRSI nằm ở bản tổng hợp cũ, không phải lời tác giả.


## 11. Macro gate: thiếu gì?

Có sẵn VIX D1 trên box (`du_lieu_ngay/vix_d1_yahoo.csv`, `vix_dai_yahoo.csv`). Chưa có bộ đồng bộ/đã kiểm tra gồm: (1)VIXtermstructure, (2)%S&P500trênMA200 với danh sách thành phần theo từng thờiđiểm, (3)creditspread lịch sử/lag côngbố, (4)put/call, (5)factorcrowding/correlationfactor. Quan trọng hơn, transcript chỉ nói có6thước đo0–100/trọng số, **không ghi đủ hàm chuẩn hóa và weights** (chỉ có ảnhprompt trongvideo). Không tự bịa cách tính composite. Không có kết quảgate, không giả gate0,5 cứu được hệ.


## 12. Đề xuất, giới hạn và tái lập

1. Chưa viếtEA từ bảng này. Nếu tiếp tục tin core củaBrendan, đường hợp lý là test đúngQQQ/vàngETF bằng giá adjusted và sizing nguồn, hoặc xác nhận chi phí giữ CFD thật. Không suy luận bảnETF phải bị swap nhưCFD.

2. Nếu tiếp tục nớiSL intraday, cần fullconfig tác giả hoặc định nghĩa setup thủcông rõ hơn trước. As-traded gốc chưa có đủ dials để khẳng định sao chép hoàn toàn; sốlệnh lệch nhiều là tínhiệu cần kiểm tra.

3. RSI8% vốn đã là stoprộng; ATRfloor thường không đổi. Thử16% hay ATRkhungcaohơn là phép thử mới phải ghi trước, không gọi kết quả này đã phủ mọi cách nới.

4. Tất cả DDtradelist có thể bỏqua drawdown thả nổi; randomtest không mô phỏng margin/mincontract; phífutures$4là giả định;swapXM lịch sửchưa đo;không có finalholdout. Holm chỉ điều chỉnh các ứngviên tới lượt trong nghiêncứu này, không xóa toàn bộ selectionbias từ cácđợt nghiêncứu đã xem trước. Không có claimlợi nhuậnthật.

5. Các kiểm tra kỹ thuật đã qua: synthetic plantedTP10%,SLưu tiên nếu chạmcảhai,giáphẳng khôngsinhtínhiệu,finite/SLdương,entry không trước tínhiệu,WFkhông chồngtrade. Không có dữliệu/credential nào đưa lêngit.


Tái lập: `data.py` dựngM1; `engines.py` quy tắc/phí; `run.py` train/test; `fast_random.py` null500; `rotation.py`; `summarize.py`; `qa.py`; `report.py`. Kết quả máyđọc `ALL_RESULTS.json`, `WIDEN_EFFECT.json`, `ket/*.pkl`; tríchnguồn `extraits.txt` và `rsi_source.txt`. Sốlượt biếnthể và nguồn dữliệu đủ để parent kiểmtra. Chưa có commit/linkGitHub mới; parent sẽ tựcommit hai báo cáo.
