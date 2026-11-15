# Kiểm định IBS mean-reversion trên 4 cặp chéo

Cập nhật: 2026-11-15 07:28 (Asia/Saigon, UTC+7)

Kiểm định quy tắc IBS (Internal Bar Strength) kiểu Quantified Strategies trên AUDCAD, AUDNZD, EURCAD, CADJPY. Mục tiêu: xem edge từng thấy trên cổ phiếu Mỹ (SPY/QQQ) có chuyển được sang cặp chéo forex không, và có dùng được cho tín hiệu / xác nhận DCA trong bộ hỗ trợ trading không.

**Kết luận: không có biến thể nào đạt “passed”.** Toàn bộ khung ngày (D1) lỗ sau phí trên OOS. Trên H4, chỉ AUDNZD long có lọc SMA200, thoát khi IBS>0,8 / tối đa 4 nến, có lãi rất mỏng ở cả IS và OOS (OOS: PF 1,01, Sharpe 0,04) — nên chỉ là **ứng viên yếu**, không đủ vững về mặt kinh tế. Bản không lọc SMA200 hòa vốn OOS nhưng lỗ trên IS, tính là không edge.

## Quy tắc và chuẩn kiểm

- IBS = (Close − Low) / (High − Low). Long khi IBS < 0,2; short đối xứng khi IBS > 0,8.
- Biến thể: có/không lọc xu hướng close > SMA200 (long) hoặc close < SMA200 (short); thoát sau 1 nến, hoặc khi IBS đảo chiều (long: IBS>0,8; short: IBS<0,2) và tối đa 4 nến.
- Tín hiệu tại **đóng cửa nến t**, khớp **giá mở cửa thật nến t+1**, thoát tại mở cửa. Không chồng lệnh.
- Phí: spread cố định 2,0 / 3,0 / 2,5 / 2,0 pip lần lượt cho AUDCAD, AUDNZD, EURCAD, CADJPY; cộng swap ước lượng 0,5–0,6 pip mỗi đêm lịch (luôn tính là chi phí, không lấy swap có lợi). 1 pip = 0,0001, riêng CADJPY = 0,01.
- Tách IS/OOS theo ngày, báo riêng. D1 cả 4 cặp: trước/sau 2019-01-01. EURCAD H4: cùng mốc 2019. AUDCAD và AUDNZD H4: tách 2022-01-01 vì dữ liệu H1 thật chỉ có từ 2018-04 (nếu tách 2019 thì IS quá ngắn).
- Đối chứng: dịch vòng chuỗi vị thế trong từng giai đoạn (1000 lần, cùng số lệnh / thời gian giữ), rồi tính lại Sharpe đã trừ phí. p là tỷ lệ lần ngẫu nhiên có Sharpe ≥ chiến lược.
- Sharpe và %/năm tính trên chuỗi lợi nhuận theo lịch (kể cả nến không có lệnh), theo thời gian lịch thực, không chỉ các ngày có lệnh.
- Gọi **passed** chỉ khi OOS đứng một mình: ≥30 lệnh, PF ≥ 1,20, Sharpe ≥ 0,30, lãi trung bình > 0, và p ≤ 0,05 so với baseline. PF ≈ 1,01 và Sharpe ≈ 0 không đủ (dễ đảo dấu nếu spread/swap lệch một chút). Nếu chỉ có lãi mỏng nhưng hơn ngẫu nhiên: **ứng viên yếu**. Còn lại: **không edge**.

## Dữ liệu

| Cặp | Khung | Nguồn | Từ | Đến | Số nến | Tách OOS |
|---|---|---|---|---|---:|---|
| AUDCAD | D1 | Yahoo Finance `AUDCAD=X` (đã lọc nến OHLC lỗi, range=0, thứ Bảy) | 2003-12-01 | 2026-11-13 | 5833 | 2019-01-01 |
| AUDNZD | D1 | Yahoo `AUDNZD=X`, cùng cách lọc | 2003-12-01 | 2026-11-13 | 5803 | 2019-01-01 |
| EURCAD | D1 | Yahoo `EURCAD=X`, cùng cách lọc | 2003-12-01 | 2026-11-13 | 5871 | 2019-01-01 |
| CADJPY | D1 | Yahoo `CADJPY=X`, cùng cách lọc | 2004-08-19 | 2026-11-13 | 5596 | 2019-01-01 |
| EURCAD | H4 | Resample 4 giờ từ H1 trên box (`/workspace/brain2/data/EURCAD_H1.parquet`), chỉ đoạn H1 thật từ 2007-05-11 | 2007-05-11 | 2026-10-02 | 30111 | 2019-01-01 |
| AUDCAD | H4 | Resample từ `AUDCAD_H1.parquet`, H1 thật từ 2018-04-14 | 2018-04-16 | 2026-10-02 | 13152 | 2022-01-01 |
| AUDNZD | H4 | Resample từ `AUDNZD_H1.parquet`, H1 thật từ 2018-04-14 | 2018-04-16 | 2026-10-02 | 13152 | 2022-01-01 |

Không có H4/H1 cho CADJPY trên box, nên cặp này chỉ chạy D1. File H1 của AUDCAD/AUDNZD trước 4/2018 (EURCAD trước 5/2007) thực chất là nến ngày đóng mốc 00:00, đã bỏ khi dựng H4. Không commit chuỗi giá thô.

## Bảng OOS — khung ngày (D1, tách 2019)

| Cặp | Biến thể | Lệnh | Win% | Lãi TB % | PF | Sharpe | %/năm | p vs ngẫu nhiên | Sharpe ngẫu nhiên | Kết luận |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| AUDCAD | Long IBS<0,2, giữ 1 nến | 356 | 45,79 | -0,034 | 0,82 | -0,49 | -1,58 | 0,584 | -0,42 | không edge |
| AUDCAD | Long IBS<0,2 + SMA200, giữ 1 nến | 171 | 46,20 | -0,045 | 0,74 | -0,53 | -0,98 | 0,758 | -0,29 | không edge |
| AUDCAD | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | 264 | 40,15 | -0,060 | 0,80 | -0,45 | -2,31 | 0,699 | -0,31 | không edge |
| AUDCAD | Long IBS<0,2 + SMA200, thoát IBS>0,8 / tối đa 4 nến | 127 | 37,80 | -0,081 | 0,73 | -0,43 | -1,33 | 0,722 | -0,22 | không edge |
| AUDCAD | Short IBS>0,8, giữ 1 nến | 355 | 45,63 | -0,038 | 0,79 | -0,59 | -1,73 | 0,626 | -0,49 | không edge |
| AUDCAD | Short IBS>0,8 + SMA200, giữ 1 nến | 183 | 45,36 | -0,030 | 0,83 | -0,34 | -0,72 | 0,498 | -0,34 | không edge |
| AUDCAD | Short IBS>0,8 + SMA200, thoát IBS<0,2 / tối đa 4 nến | 136 | 37,50 | -0,092 | 0,72 | -0,49 | -1,62 | 0,798 | -0,27 | không edge |
| AUDCAD | Long+short + SMA200, giữ 1 nến | 354 | 45,76 | -0,037 | 0,79 | -0,60 | -1,69 | 0,697 | -0,42 | không edge |
| AUDCAD | Long+short + SMA200, thoát IBS đối / tối đa 4 nến | 263 | 37,64 | -0,087 | 0,73 | -0,65 | -2,93 | 0,801 | -0,35 | không edge |
| AUDNZD | Long IBS<0,2, giữ 1 nến | 241 | 48,13 | -0,038 | 0,73 | -0,62 | -1,18 | 0,660 | -0,48 | không edge |
| AUDNZD | Long IBS<0,2 + SMA200, giữ 1 nến | 141 | 44,68 | -0,057 | 0,61 | -0,74 | -1,03 | 0,858 | -0,38 | không edge |
| AUDNZD | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | 199 | 42,21 | -0,053 | 0,78 | -0,48 | -1,38 | 0,766 | -0,27 | không edge |
| AUDNZD | Long IBS<0,2 + SMA200, thoát IBS>0,8 / tối đa 4 nến | 116 | 41,38 | -0,102 | 0,61 | -0,72 | -1,51 | 0,945 | -0,22 | không edge |
| AUDNZD | Short IBS>0,8, giữ 1 nến | 375 | 43,47 | -0,028 | 0,79 | -0,60 | -1,33 | 0,104 | -1,00 | không edge |
| AUDNZD | Short IBS>0,8 + SMA200, giữ 1 nến | 159 | 47,17 | -0,009 | 0,93 | -0,12 | -0,19 | 0,055 | -0,65 | không edge |
| AUDNZD | Short IBS>0,8 + SMA200, thoát IBS<0,2 / tối đa 4 nến | 111 | 38,74 | -0,059 | 0,76 | -0,38 | -0,85 | 0,295 | -0,56 | không edge |
| AUDNZD | Long+short + SMA200, giữ 1 nến | 300 | 46 | -0,032 | 0,77 | -0,58 | -1,22 | 0,313 | -0,74 | không edge |
| AUDNZD | Long+short + SMA200, thoát IBS đối / tối đa 4 nến | 227 | 39,65 | -0,083 | 0,67 | -0,80 | -2,40 | 0,760 | -0,55 | không edge |
| EURCAD | Long IBS<0,2, giữ 1 nến | 367 | 48,50 | -0,020 | 0,88 | -0,32 | -0,98 | 0,478 | -0,35 | không edge |
| EURCAD | Long IBS<0,2 + SMA200, giữ 1 nến | 199 | 50,25 | -0,008 | 0,95 | -0,09 | -0,23 | 0,337 | -0,25 | không edge |
| EURCAD | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | 275 | 38,91 | -0,079 | 0,73 | -0,66 | -2,81 | 0,936 | -0,24 | không edge |
| EURCAD | Long IBS<0,2 + SMA200, thoát IBS>0,8 / tối đa 4 nến | 145 | 42,76 | -0,032 | 0,89 | -0,23 | -0,82 | 0,560 | -0,18 | không edge |
| EURCAD | Short IBS>0,8, giữ 1 nến | 361 | 41,83 | -0,045 | 0,74 | -0,73 | -2,06 | 0,850 | -0,40 | không edge |
| EURCAD | Short IBS>0,8 + SMA200, giữ 1 nến | 184 | 42,39 | -0,037 | 0,78 | -0,48 | -0,88 | 0,722 | -0,27 | không edge |
| EURCAD | Short IBS>0,8 + SMA200, thoát IBS<0,2 / tối đa 4 nến | 137 | 40,88 | -0,051 | 0,82 | -0,33 | -0,92 | 0,649 | -0,21 | không edge |
| EURCAD | Long+short + SMA200, giữ 1 nến | 383 | 46,48 | -0,022 | 0,86 | -0,37 | -1,11 | 0,499 | -0,38 | không edge |
| EURCAD | Long+short + SMA200, thoát IBS đối / tối đa 4 nến | 281 | 41,99 | -0,038 | 0,86 | -0,36 | -1,62 | 0,599 | -0,27 | không edge |
| CADJPY | Long IBS<0,2, giữ 1 nến | 395 | 47,59 | -0,045 | 0,82 | -0,51 | -2,36 | 0,903 | -0,11 | không edge |
| CADJPY | Long IBS<0,2 + SMA200, giữ 1 nến | 250 | 48 | -0,034 | 0,85 | -0,33 | -1,13 | 0,803 | -0,07 | không edge |
| CADJPY | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | 311 | 41,16 | -0,121 | 0,71 | -0,77 | -4,84 | 1,000 | 0,06 | không edge |
| CADJPY | Long IBS<0,2 + SMA200, thoát IBS>0,8 / tối đa 4 nến | 195 | 43,08 | -0,069 | 0,81 | -0,39 | -1,78 | 0,938 | 0,05 | không edge |
| CADJPY | Short IBS>0,8, giữ 1 nến | 373 | 47,45 | -0,044 | 0,82 | -0,50 | -2,15 | 0,461 | -0,54 | không edge |
| CADJPY | Short IBS>0,8 + SMA200, giữ 1 nến | 139 | 43,17 | -0,073 | 0,74 | -0,48 | -1,33 | 0,665 | -0,34 | không edge |
| CADJPY | Short IBS>0,8 + SMA200, thoát IBS<0,2 / tối đa 4 nến | 108 | 28,70 | -0,319 | 0,41 | -1,06 | -4,49 | 0,995 | -0,35 | không edge |
| CADJPY | Long+short + SMA200, giữ 1 nến | 389 | 46,27 | -0,048 | 0,80 | -0,56 | -2,44 | 0,764 | -0,29 | không edge |
| CADJPY | Long+short + SMA200, thoát IBS đối / tối đa 4 nến | 303 | 37,62 | -0,162 | 0,62 | -1,05 | -6,37 | 0,994 | -0,17 | không edge |

Không biến thể nào có PF > 1 hoặc Sharpe > 0 trên OOS. Lãi trung bình mỗi lệnh khoảng −0,01% đến −0,32%. Win rate phần lớn dưới 50%. Lọc SMA200 làm giảm số lệnh nhưng không đảo được dấu lỗ. Kết quả IS (trước 2019) cũng cùng hướng: PF thường < 1, Sharpe ≤ 0.

## Bảng OOS — khung H4

| Cặp | Biến thể | Lệnh | Win% | Lãi TB % | PF | Sharpe | %/năm | p vs ngẫu nhiên | Sharpe ngẫu nhiên | Kết luận |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| EURCAD | Long IBS<0,2, giữ 1 nến | 2314 | 50,43 | -0,003 | 0,95 | -0,34 | -1,05 | 0,001 | -1,72 | không edge |
| EURCAD | Long IBS<0,2 + SMA200, giữ 1 nến | 1035 | 50,63 | -0,006 | 0,92 | -0,33 | -0,76 | 0,012 | -1,14 | không edge |
| EURCAD | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | 1730 | 57,34 | -0,005 | 0,95 | -0,29 | -1,29 | 0,026 | -0,91 | không edge |
| EURCAD | Long IBS<0,2 + SMA200, thoát IBS>0,8 / tối đa 4 nến | 811 | 59,68 | -0,002 | 0,98 | -0,07 | -0,28 | 0,047 | -0,64 | không edge |
| EURCAD | Short IBS>0,8, giữ 1 nến | 2135 | 46,14 | -0,010 | 0,83 | -1,01 | -2,86 | 0,033 | -1,72 | không edge |
| EURCAD | Short IBS>0,8 + SMA200, giữ 1 nến | 973 | 44,09 | -0,018 | 0,70 | -1,33 | -2,27 | 0,691 | -1,14 | không edge |
| EURCAD | Short IBS>0,8 + SMA200, thoát IBS<0,2 / tối đa 4 nến | 796 | 55,65 | -0,020 | 0,81 | -0,74 | -2,05 | 0,526 | -0,72 | không edge |
| EURCAD | Long+short + SMA200, giữ 1 nến | 2008 | 47,46 | -0,012 | 0,82 | -1,07 | -3,02 | 0,111 | -1,64 | không edge |
| EURCAD | Long+short + SMA200, thoát IBS đối / tối đa 4 nến | 1588 | 57,62 | -0,011 | 0,89 | -0,56 | -2,35 | 0,140 | -0,96 | không edge |
| AUDCAD | Long IBS<0,2, giữ 1 nến | 1326 | 43,97 | -0,021 | 0,74 | -1,82 | -5,87 | 0,506 | -1,85 | không edge |
| AUDCAD | Long IBS<0,2 + SMA200, giữ 1 nến | 661 | 44,93 | -0,025 | 0,69 | -1,52 | -3,44 | 0,671 | -1,30 | không edge |
| AUDCAD | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | 984 | 54,47 | -0,011 | 0,91 | -0,46 | -2,27 | 0,117 | -0,94 | không edge |
| AUDCAD | Long IBS<0,2 + SMA200, thoát IBS>0,8 / tối đa 4 nến | 517 | 53,97 | -0,024 | 0,80 | -0,78 | -2,62 | 0,604 | -0,67 | không edge |
| AUDCAD | Short IBS>0,8, giữ 1 nến | 1326 | 46,15 | -0,010 | 0,87 | -0,83 | -2,75 | 0,013 | -2,05 | không edge |
| AUDCAD | Short IBS>0,8 + SMA200, giữ 1 nến | 547 | 44,97 | -0,007 | 0,90 | -0,38 | -0,88 | 0,033 | -1,32 | không edge |
| AUDCAD | Short IBS>0,8 + SMA200, thoát IBS<0,2 / tối đa 4 nến | 427 | 51,99 | -0,014 | 0,89 | -0,40 | -1,35 | 0,156 | -0,83 | không edge |
| AUDCAD | Long+short + SMA200, giữ 1 nến | 1208 | 44,95 | -0,017 | 0,79 | -1,35 | -4,29 | 0,216 | -1,85 | không edge |
| AUDCAD | Long+short + SMA200, thoát IBS đối / tối đa 4 nến | 933 | 53,48 | -0,018 | 0,85 | -0,78 | -3,63 | 0,292 | -1,05 | không edge |
| AUDNZD | Long IBS<0,2, giữ 1 nến | 1366 | 45,97 | -0,012 | 0,81 | -1,37 | -3,29 | 0,031 | -3,12 | không edge |
| AUDNZD | Long IBS<0,2 + SMA200, giữ 1 nến | 771 | 46,95 | -0,008 | 0,86 | -0,74 | -1,33 | 0,040 | -2,35 | không edge |
| AUDNZD | Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | 1041 | 55,43 | 0,000 | 1,01 | 0,03 | 0,03 | 0,001 | -1,55 | không edge |
| AUDNZD | Long IBS<0,2 + SMA200, thoát IBS>0,8 / tối đa 4 nến | 619 | 56,06 | 0,001 | 1,01 | 0,04 | 0,07 | 0,020 | -1,21 | ứng viên yếu |
| AUDNZD | Short IBS>0,8, giữ 1 nến | 1368 | 43,42 | -0,015 | 0,75 | -1,85 | -4,30 | 0,017 | -3,59 | không edge |
| AUDNZD | Short IBS>0,8 + SMA200, giữ 1 nến | 439 | 43,28 | -0,020 | 0,70 | -1,24 | -1,80 | 0,084 | -2,08 | không edge |
| AUDNZD | Short IBS>0,8 + SMA200, thoát IBS<0,2 / tối đa 4 nến | 345 | 55,65 | -0,013 | 0,85 | -0,50 | -0,98 | 0,035 | -1,32 | không edge |
| AUDNZD | Long+short + SMA200, giữ 1 nến | 1210 | 45,62 | -0,012 | 0,80 | -1,36 | -3,11 | 0,033 | -3,09 | không edge |
| AUDNZD | Long+short + SMA200, thoát IBS đối / tối đa 4 nến | 953 | 55,72 | -0,005 | 0,94 | -0,32 | -1,05 | 0,021 | -1,73 | không edge |

Trên H4, win rate của biến thể thoát theo IBS đảo chiều thường > 50%, nhưng lãi mỗi lệnh bị spread + swap ăn hết. Sharpe ngẫu nhiên rất âm vì số lệnh lớn (hàng trăm đến hơn 2.000) nên trả phí nhiều; **vượt baseline âm chưa có nghĩa là có edge giao dịch**.

### Hai ứng viên yếu (AUDNZD H4)

Hai dòng long AUDNZD (thoát khi IBS>0,8 / tối đa 4 nến) có PF OOS hơi trên 1. Xem kỹ IS thì chỉ bản có lọc SMA200 là cùng chiều (và vẫn rất mỏng):

| Biến thể | Giai đoạn | Lệnh | Win% | Lãi TB % | PF | Sharpe | %/năm | p | Sharpe ngẫu nhiên |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | IS (2018-04 → 2021-12) | 820 | 58,17 | -0,005 | 0,94 | -0,31 | -1,13 | 0,001 | -1,93 |
| Long IBS<0,2, thoát IBS>0,8 / tối đa 4 nến | OOS (2022-01 → 2026-10) | 1041 | 55,43 | 0,000 | 1,01 | 0,03 | 0,03 | 0,001 | -1,55 |
| Long IBS<0,2 + SMA200, thoát IBS>0,8 / tối đa 4 nến | IS (2018-04 → 2021-12) | 362 | 58,01 | 0,003 | 1,03 | 0,13 | 0,27 | 0,001 | -1,30 |
| Long IBS<0,2 + SMA200, thoát IBS>0,8 / tối đa 4 nến | OOS (2022-01 → 2026-10) | 619 | 56,06 | 0,001 | 1,01 | 0,04 | 0,07 | 0,020 | -1,21 |

Biến thể không lọc SMA200 **thất bại trên IS** (PF 0,94, Sharpe −0,31) rồi chỉ hòa vốn mỏng trên OOS — không đồng nhất, không nên xem là ứng viên. Biến thể có SMA200 cùng dấu dương rất nhẹ ở cả IS và OOS (PF 1,03 / 1,01, Sharpe 0,13 / 0,04). Một pip phí đội thêm, hoặc swap thực tế kém hơn ước lượng 0,6 pip/đêm, là đủ để mất lãi. Không đủ điều kiện “passed”, chưa đưa vào bộ hỗ trợ trading.

## Ý nghĩa cho bộ hỗ trợ

- Số liệu Quantified Strategies (SPY +0,41%/lệnh, QQQ +0,56%/lệnh, khung ngày, cổ phiếu Mỹ) **không chuyển** sang 4 cặp chéo này trên D1 sau spread/swap.
- Không dùng IBS < 0,2 / IBS > 0,8 như tín hiệu standalone hay như xác nhận DCA trên các cặp này, cho đến khi có kiểm định khác (ví dụ kết hợp stretch so với MA50, dữ liệu sàn tốt hơn, hoặc phí thực của tài khoản) cho kết quả OOS đủ mạnh.
- SMA200 trên H4 chỉ dài khoảng 8 tuần, không phải SMA200 ngày của tài liệu gốc — đã ghi rõ khi đọc kết quả H4.

## Hạn chế

- Yahoo FX thiếu nhiều nến thứ Sáu và có nến Chủ Nhật (mở tuần); chất lượng OHLC kém hơn dữ liệu sàn. Đây là nguồn D1 dài nhất sẵn có, nhưng không phải chất lượng broker.
- H4 lấy từ parquet H1 trên box (không commit); chưa xác nhận timezone sàn. CADJPY không có H4.
- Swap là ước lượng thô, cùng dấu chi phí cho cả long và short, không theo lịch sử lãi suất thực.
- Baseline dịch vòng giữ nguyên mật độ lệnh; p nhỏ trên H4 nhiều khi chỉ vì chiến lược **lỗ ít hơn** baseline cũng lỗ vì phí.
- Đây chưa phải kiểm thử SEEKER đầy đủ (chưa FDR trên nhiều giả thuyết như một cổng pass/fail, chưa dữ liệu tick). Mọi mục vẫn chưa pass SEEKER.

## Script

Mã chạy lại: [`tools/kiem_dinh/evo/ibs_cap_cheo.py`](../../tools/kiem_dinh/evo/ibs_cap_cheo.py). Cần Python với pandas/numpy/pyarrow, thư mục Yahoo CSV và (tuỳ chọn) file H1 parquet. Không ghi dữ liệu giá lên Git.
