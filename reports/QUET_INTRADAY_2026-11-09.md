# Quét intraday: Sweep+FVG, ORB, CHoCH: kết quả backtest (09/11/2026)

Báo cáo phân tích dữ liệu trên box (thư mục nháp `/workspace/quet_intraday`). Không sửa code brain2. Mọi số dưới đây lấy từ `ket_qua.json` và `tong_hop.json` do script trong thư mục đó sinh ra.

## Kết luận ngắn

- **Không có hệ nào sống qua phễu.** Có 84 ứng viên (hệ × mã × khung) và tổng cộng **8.820 biến thể tham số** đã thử. 62 ứng viên đạt ≥100 lệnh/năm OOS. Chỉ **1** ứng viên còn lãi sau phí ở OOS: ORB US100 M5. Ứng viên này rớt ở bước Sharpe OOS > 0,5 (OOS chỉ 0,32).
- Sweep+FVG (bản ICT “as traded”) **lỗ ngay cả trước phí**: các mẫu chẩn đoán (GBPCAD M15/H1, US100 M15) có R gộp chưa trừ spread khoảng −0,1 đến −0,3R/lệnh. Sau phí XM, R ròng trung bình từ −0,15 đến −0,54R/lệnh OOS trên cả 42 tổ hợp mã × khung.
- CHoCH H1 lỗ ở mọi mã (−0,04 đến −0,30R/lệnh OOS). CHoCH H4 chỉ có khoảng 20–40 lệnh/năm, nên không đạt điều kiện ≥100 lệnh/năm và walk-forward không chọn được tham số nào.
- **Chưa có hệ nào đáng viết EA MT5** theo tiêu chí đã ghi trước.

## Thay đổi so với kế hoạch ban đầu (theo yêu cầu của Anh, 08/11/2026 23:40 giờ VN)

- **Bỏ khóa 2 năm cuối làm holdout.** Toàn bộ dữ liệu được dùng trong walk-forward 12/3 tháng. Cột Sharpe holdout vì thế không có.
- **Bỏ bước chạy nguội sang cặp tương tự.** Mỗi mã được tối ưu riêng: walk-forward chọn tham số riêng cho từng mã, từng khung, từng quý.
- Các bước còn lại được giữ nguyên: ≥100 lệnh/năm, lãi sau phí, Sharpe OOS > 0,5, OOS không tệ hơn IS quá nhiều, so với vào lệnh ngẫu nhiên, độ nhạy tham số, bootstrap 500 lần, và ghi số biến thể đã thử.

## Dữ liệu

| Mã (tên XM) | Nguồn | Khoảng thời gian thật |
|---|---|---|
| GBPCAD | HistData M1 BID: 2017–2023 từ `du_lieu_fx/hd_dai`, 2024–10/2026 từ `hd28` (M5) | 02/01/2017 → 09/10/2026 (≈9,8 năm) |
| GBPNZD | HistData M1 BID: 2017–2023 từ `du_lieu_fx/hd_dai`, 2024–10/2026 từ `hd28` (M5) | 02/01/2017 → 09/10/2026 (≈9,8 năm) |
| EURGBP | HistData M1 BID: 2017–2023 từ `du_lieu_fx/hd_dai`, 2024–10/2026 từ `hd28` (M5) | 02/01/2017 → 09/10/2026 (≈9,8 năm) |
| AUDNZD | HistData M1 BID: 2017–2023 từ `du_lieu_fx/hd_dai`, 2024–10/2026 từ `hd28` (M5) | 02/01/2017 → 09/10/2026 (≈9,8 năm) |
| EURCHF | HistData M1 BID: 2017–2023 từ `du_lieu_fx/hd_dai`, 2024–10/2026 từ `hd28` (M5) | 02/01/2017 → 09/10/2026 (≈9,8 năm) |
| NZDUSD | HistData M1 BID: 2017–2023 từ `du_lieu_fx/hd_dai`, 2024–10/2026 từ `hd28` (M5) | 02/01/2017 → 09/10/2026 (≈9,8 năm) |
| USDCAD | HistData M1 BID: 2017–2023 từ `du_lieu_fx/hd_dai`, 2024–10/2026 từ `hd28` (M5) | 02/01/2017 → 09/10/2026 (≈9,8 năm) |
| XAUUSD | HistData M1 BID: 2017–2023 từ `du_lieu_fx/hd_dai`, 2024–10/2026 từ `hd28` (M5) | 02/01/2017 → 09/10/2026 (≈9,8 năm) |
| AUDCAD | HistData M5 nối dài từ 2008 (`hd28/audcad_m5_histdata_ny7_den202610.csv`) | 02/01/2017 → 09/10/2026 (≈9,8 năm) |
| GBPAUD | HistData M1 BID: 2017–2023 **tải mới hôm nay** (thư viện `histdata`, miễn phí) + `hd28` 2024–10/2026 | 02/01/2017 → 09/10/2026 (≈9,8 năm) |
| EURCAD | HistData M1 BID: 2017–2023 **tải mới hôm nay** (thư viện `histdata`, miễn phí) + `hd28` 2024–10/2026 | 02/01/2017 → 09/10/2026 (≈9,8 năm) |
| US100 (NSXUSD) | HistData M1 BID: 2017–2023 **tải mới hôm nay** (thư viện `histdata`, miễn phí) + `hd28` 2024–10/2026 | 02/01/2017 → 09/10/2026 (≈9,8 năm) |
| US500 (SPXUSD) | HistData M1 BID: 2017–2023 **tải mới hôm nay** (thư viện `histdata`, miễn phí) + `hd28` 2024–10/2026 | 02/01/2017 → 09/10/2026 (≈9,8 năm) |
| GER40 (GRXEUR) | HistData M1 BID: 2017–2023 **tải mới hôm nay** (thư viện `histdata`, miễn phí) + `hd28` 2024–10/2026 | 02/01/2017 → 09/10/2026 (≈9,8 năm) |

- Giờ được đổi về UTC (HistData dùng EST cố định UTC−5; tệp `ny7` dùng UTC+2). Giờ phiên NY, London, Frankfurt có tính DST (zoneinfo). Từ M5 gộp lên M15, H1 và H4.
- **US30: không có dữ liệu miễn phí phút trên HistData**, nên chưa test. Hai chỉ số khác nằm trong danh sách nhưng chưa test là EURNZD (có dữ liệu `hd28` từ 2024 nhưng thiếu 2017–2023, chưa tải) và NZDCAD (thiếu 2024–2026).
- Chỉ có giá BID. Không có spread lịch sử. Giá chỉ số HistData là CFD/tiền mặt của HistData, không phải giá XM. GER40 có các khoảng nghỉ/gap lớn, nên một số lệnh thoát ở giá mở gap tạo ra R ngoại lai. Đó là lý do có vài dòng GER40 với R trung bình dương nhưng CAGR âm.

## Phí (XM micro, số đo trong `brain2/config/phi_xm_micro.json`, ngày 21/10/2026)

- Spread: dùng **p90** cố định (thận trọng). GBPCAD 5,8 pip; GBPNZD 8,5; EURGBP 2,5; AUDNZD 4,5; EURCHF 3,4; GBPAUD 5,1; EURCAD 3,7; NZDUSD 2,8; USDCAD 3,2; GOLD 0,57 USD.
- AUDCAD **không có số đo**, nên giả định 5,0 pip. Chỉ số lấy từ `phi_xm_micro_that.csv` (Cash#, p90 giờ ban ngày): US100 2,8 điểm; US500 0,6; GER40 2,0.
- Hoa hồng = 0 (đã đo, tài khoản micro). Trượt giá khi dính SL: 0,5 pip FX, 0,2 USD vàng, 1 điểm US100/GER40, 0,25 điểm US500. Gap qua SL thì thoát ở giá mở cộng trượt giá.
- Swap: dùng số đo 06/10/2026, tính mỗi lần qua mốc 22:00 UTC. FX/vàng tính ×3 vào thứ Tư, chỉ số tính ×3 vào thứ Sáu. Swap lịch sử chưa đo được.
- Nến chạm cả SL lẫn TP thì tính là thua. Tín hiệu chỉ lấy từ nến đã đóng. Lệnh limit chỉ khớp khi giá xuyên qua limit ≥1 pip/điểm; với lệnh buy limit còn phải xuyên thêm 1 spread, vì dữ liệu là BID. Không tính TP trong nến khớp lệnh.
- Bỏ lệnh nếu khoảng SL < 3 × spread (ghi trước). Rủi ro mỗi lệnh 1% vốn, lãi kép. CAGR và DD đều tính theo quy ước này.

## Luật ghi trước

**1. Sweep + FVG** (M5, M15, H1). Lưới 192 biến thể/mã/khung:
- Swing được xác nhận theo fractal n ∈ {2, 3, 5}.
- Sweep: nến đóng có low xuyên swing low gần nhất rồi đóng lại trên mức đó (ngược lại với đỉnh). Mỗi mức chỉ dùng một lần.
- Trong vòng W ∈ {6, 12} nến, phải có FVG 3 nến theo hướng ngược lại, hình thành sau sweep.
- Đặt limit ở mép FVG hoặc giữa FVG (2 cách). Limit hết hạn sau W nến và bị hủy nếu giá chạm TP trước khi khớp.
- SL đặt sau điểm cực trị của sweep ±1 pip. TP là thanh khoản đối diện (swing gần nhất, yêu cầu RR ≥ 1) hoặc 1R, 1,5R, 2R.
- Lọc giờ: có/không, theo khung Silver Bullet: 3–4h London, 10–11h và 14–15h New York. Bias ngày: có/không (màu nến ngày trước, ngày chốt 17:00 NY).
- Giữ lệnh tối đa 96 nến M5 / 64 nến M15 / 48 nến H1.

**2. ORB** (M5). Lưới 36 biến thể/mã:
- Biên độ lấy từ 15, 30 hoặc 60 phút đầu phiên. US100/US500 bắt đầu 9:30 ET, GER40 9:00 giờ Frankfurt, FX và vàng 8:00 giờ London.
- Vào lệnh ở giá mở nến sau nến M5 đầu tiên đóng ngoài biên độ, trong vòng 3 giờ từ lúc mở phiên. Mỗi ngày tối đa 1 lệnh.
- SL ở cạnh kia, giữa biên độ, hoặc 3 × ATR14(M5). TP là 1R, 1,5R, 2R, hoặc đóng cuối phiên (16:00 ET, 17:30 Frankfurt, 16:30 London). Mọi lệnh đều đóng khi hết phiên.

**3. CHoCH** (H1, H4). Lưới 9 biến thể/mã/khung:
- Swing fractal n ∈ {2, 3, 5}. Cấu trúc đổi chiều khi nến đóng phá swing ngược xu hướng hiện tại.
- Vào ở giá đóng. SL sau swing đối diện gần nhất ±1 pip. TP 1R, 1,5R hoặc 2R.
- Giữ tối đa 120 nến H1 / 60 nến H4. Mỗi thời điểm chỉ có 1 lệnh.

**Kiểm định:** walk-forward. Cửa sổ train 12 tháng, test 3 tháng, trượt dần. Có 36 quý OOS, từ 01/2018 đến 10/2026.
- Mỗi quý chọn tham số có t-stat R cao nhất trong 12 tháng train, với điều kiện ≥100 lệnh trong train. Các đoạn OOS được nối lại để tính chỉ số.
- Phễu gồm các bước:
  1. ≥100 lệnh/năm OOS.
  2. R trung bình OOS > 0 sau phí.
  3. Sharpe OOS (theo ngày) > 0,5.
  4. Sharpe OOS ≥ 0,5 × Sharpe IS trung bình.
  5. Thắng vào lệnh ngẫu nhiên: 1.000 lần mô phỏng, cùng khoảng SL/TP, cùng thời hạn, ±45 ngày, p < 0,05.
  6. Độ nhạy: ≥60% tham số lân cận của bộ hay được chọn nhất có R > 0 trên toàn kỳ.
- Bootstrap 500 lần trên R OOS để tính DD. Tiêu chí brain2 (DD < 80%, CAGR > 10%) được ghi kèm để tham khảo.

## Phễu từng hệ

| Hệ | Ứng viên (mã×khung) | Biến thể đã thử | ≥100 lệnh/năm | Lãi sau phí | Sharpe OOS>0,5 | OOS≈IS | Thắng ngẫu nhiên | Độ nhạy |
|---|---|---|---|---|---|---|---|---|
| Sweep+FVG | 42 | 8064 | 37 | 0 | 0 | 0 | 0 | 0 |
| ORB | 14 | 504 | 12 | 1 | 0 | 0 | 0 | 0 |
| CHoCH | 28 | 252 | 13 | 0 | 0 | 0 | 0 | 0 |

**Hệ sống: 0.** Vì không có hệ sống nên bảng hệ sống để trống. Không có số bootstrap DD hay Sharpe holdout nào cho hệ đạt.

## Kết quả OOS walk-forward từng ứng viên (sau phí)

| Hệ | Mã | Khung | Tham số hay chọn | Lệnh/năm | Giữ TB (phút) | Win | PF | R TB | CAGR | DD | Sharpe IS | Sharpe OOS | Boot DD p50/p95 | Dừng ở |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| choch | AUDCAD | H4 | – | 0 | – | – | – | – | – | – | – | – | – | không quý nào có tham số ≥100 lệnh/12 tháng |
| choch | AUDNZD | H4 | – | 0 | – | – | – | – | – | – | – | – | – | không quý nào có tham số ≥100 lệnh/12 tháng |
| choch | EURCAD | H4 | – | 0 | – | – | – | – | – | – | – | – | – | không quý nào có tham số ≥100 lệnh/12 tháng |
| choch | EURCHF | H4 | – | 0 | – | – | – | – | – | – | – | – | – | không quý nào có tham số ≥100 lệnh/12 tháng |
| choch | EURGBP | H4 | – | 0 | – | – | – | – | – | – | – | – | – | không quý nào có tham số ≥100 lệnh/12 tháng |
| choch | GBPAUD | H4 | – | 0 | – | – | – | – | – | – | – | – | – | không quý nào có tham số ≥100 lệnh/12 tháng |
| choch | GBPCAD | H4 | – | 0 | – | – | – | – | – | – | – | – | – | không quý nào có tham số ≥100 lệnh/12 tháng |
| choch | GBPNZD | H4 | – | 0 | – | – | – | – | – | – | – | – | – | không quý nào có tham số ≥100 lệnh/12 tháng |
| choch | GER40 | H4 | – | 0 | – | – | – | – | – | – | – | – | – | không quý nào có tham số ≥100 lệnh/12 tháng |
| choch | US100 | H4 | – | 0 | – | – | – | – | – | – | – | – | – | không quý nào có tham số ≥100 lệnh/12 tháng |
| choch | NZDUSD | H4 | – | 0 | – | – | – | – | – | – | – | – | – | không quý nào có tham số ≥100 lệnh/12 tháng |
| choch | US500 | H4 | – | 0 | – | – | – | – | – | – | – | – | – | không quý nào có tham số ≥100 lệnh/12 tháng |
| choch | USDCAD | H4 | – | 0 | – | – | – | – | – | – | – | – | – | không quý nào có tham số ≥100 lệnh/12 tháng |
| choch | XAUUSD | H4 | – | 0 | – | – | – | – | – | – | – | – | – | không quý nào có tham số ≥100 lệnh/12 tháng |
| choch | XAUUSD | H1 | (3, 1) | 112 | 2256 | 50,0% | 0,93 | -0,04 | -4,6% | 48,4% | -0,08 | -0,34 | 45,3%/65,8% | lãi sau phí |
| choch | GER40 | H1 | (2, 2) | 52 | 2455 | 41,7% | 0,86 | -0,08 | -4,6% | 38,7% | -0,21 | -0,58 | 41,5%/61,7% | ≥100 lệnh/năm |
| choch | GBPAUD | H1 | (2, 1.5) | 118 | 2402 | 44,6% | 0,87 | -0,08 | -9,3% | 63,5% | -0,06 | -0,64 | 62,8%/79,0% | lãi sau phí |
| choch | US100 | H1 | (2, 1) | 128 | 1841 | 43,8% | 0,85 | -0,09 | -11,4% | 69,1% | -0,41 | -0,86 | 69,6%/81,8% | lãi sau phí |
| choch | US500 | H1 | (3, 1) | 119 | 2013 | 41,7% | 0,81 | -0,12 | -13,6% | 77,8% | -0,36 | -0,97 | 75,1%/86,0% | lãi sau phí |
| choch | GBPNZD | H1 | (2, 2) | 108 | 2726 | 39,9% | 0,75 | -0,17 | -17,0% | 80,9% | -0,56 | -1,30 | 81,8%/90,7% | lãi sau phí |
| choch | EURGBP | H1 | (2, 1.5) | 115 | 2440 | 40,2% | 0,77 | -0,16 | -17,5% | 83,9% | -0,72 | -1,36 | 83,2%/91,0% | lãi sau phí |
| choch | NZDUSD | H1 | (3, 1) | 116 | 2264 | 43,3% | 0,76 | -0,15 | -16,5% | 81,8% | -0,80 | -1,38 | 80,9%/88,9% | lãi sau phí |
| choch | EURCAD | H1 | (3, 1) | 121 | 2130 | 42,4% | 0,75 | -0,16 | -18,1% | 83,1% | -0,92 | -1,43 | 83,4%/90,8% | lãi sau phí |
| choch | GBPCAD | H1 | (2, 1.5) | 120 | 2130 | 38,1% | 0,72 | -0,19 | -21,5% | 88,8% | -0,73 | -1,70 | 88,7%/93,9% | lãi sau phí |
| choch | EURCHF | H1 | (2, 1.5) | 115 | 2406 | 44,4% | 0,70 | -0,20 | -21,0% | 88,7% | -1,46 | -1,76 | 88,1%/93,2% | lãi sau phí |
| choch | USDCAD | H1 | (3, 1.5) | 113 | 2369 | 37,4% | 0,69 | -0,22 | -22,2% | 89,1% | -0,87 | -1,82 | 89,5%/94,4% | lãi sau phí |
| choch | AUDCAD | H1 | (3, 1) | 112 | 2352 | 40,7% | 0,63 | -0,25 | -25,4% | 92,4% | -1,55 | -2,15 | 92,8%/96,1% | lãi sau phí |
| choch | AUDNZD | H1 | (3, 1) | 110 | 2532 | 41,7% | 0,57 | -0,30 | -28,7% | 95,4% | -2,07 | -2,57 | 95,0%/97,2% | lãi sau phí |
| orb | US100 | M5 | (60, 2, 0) | 231 | 168 | 34,3% | 1,07 | 0,05 | 5,7% | 36,9% | 0,89 | 0,32 | 58,8%/80,2% | Sharpe OOS |
| orb | US500 | M5 | (60, 0, 0) | 234 | 161 | 34,0% | 0,94 | -0,04 | -12,7% | 76,5% | 0,69 | -0,37 | 80,0%/92,9% | lãi sau phí |
| orb | GER40 | M5 | (15, 0, 0) | 226 | 214 | 37,0% | 0,89 | -0,07 | -17,7% | 86,8% | 0,28 | -0,68 | 86,5%/95,1% | lãi sau phí |
| orb | GBPAUD | M5 | (60, 0, 0) | 197 | 244 | 34,3% | 0,83 | -0,12 | -23,6% | 91,5% | -0,31 | -1,01 | 92,1%/97,3% | lãi sau phí |
| orb | AUDCAD | M5 | (60, 0, 0) | 24 | 324 | 34,3% | 0,52 | -0,33 | -7,9% | 51,5% | -2,40 | -1,32 | 52,9%/63,4% | ≥100 lệnh/năm |
| orb | EURCAD | M5 | (15, 0, 0) | 154 | 215 | 29,3% | 0,73 | -0,23 | -31,8% | 96,9% | -0,73 | -1,53 | 96,8%/98,9% | lãi sau phí |
| orb | XAUUSD | M5 | (60, 0, 0) | 204 | 209 | 30,0% | 0,74 | -0,21 | -37,8% | 99,1% | -0,63 | -1,55 | 98,7%/99,6% | lãi sau phí |
| orb | GBPCAD | M5 | (30, 0, 0) | 136 | 245 | 32,2% | 0,71 | -0,23 | -28,2% | 95,1% | -0,71 | -1,60 | 95,1%/97,9% | lãi sau phí |
| orb | EURGBP | M5 | (60, 0, 0) | 149 | 231 | 32,9% | 0,71 | -0,23 | -30,0% | 95,8% | -1,31 | -1,68 | 95,9%/98,4% | lãi sau phí |
| orb | NZDUSD | M5 | (60, 1, 0) | 126 | 243 | 30,0% | 0,68 | -0,27 | -30,3% | 95,8% | -1,05 | -1,71 | 96,0%/98,4% | lãi sau phí |
| orb | USDCAD | M5 | (30, 0, 0) | 145 | 226 | 28,9% | 0,69 | -0,27 | -33,8% | 97,4% | -1,26 | -1,76 | 97,7%/99,0% | lãi sau phí |
| orb | EURCHF | M5 | (60, 0, 2) | 122 | 252 | 38,6% | 0,65 | -0,24 | -26,3% | 93,2% | -1,77 | -2,03 | 93,5%/96,8% | lãi sau phí |
| orb | GBPNZD | M5 | (15, 0, 0) | 131 | 210 | 36,6% | 0,61 | -0,29 | -32,4% | 96,8% | -1,14 | -2,48 | 97,1%/98,5% | lãi sau phí |
| orb | AUDNZD | M5 | (60, 0, 1) | 38 | 270 | 34,4% | 0,36 | -0,42 | -15,1% | 77,3% | -3,65 | -2,62 | 76,2%/82,1% | ≥100 lệnh/năm |
| sweep | GER40 | H1 | (2, 0, 12, 1, 0, 0) | 53 | 1175 | 37,2% | 0,75 | -0,17 | -8,8% | 55,3% | -0,46 | -0,87 | 59,0%/72,8% | ≥100 lệnh/năm |
| sweep | US100 | H1 | (2, 1, 12, 2, 0, 0) | 108 | 1028 | 37,5% | 0,77 | -0,15 | -15,8% | 79,9% | -0,52 | -1,22 | 79,4%/88,9% | lãi sau phí |
| sweep | XAUUSD | H1 | (2, 0, 12, 2, 0, 0) | 107 | 1130 | 36,3% | 0,73 | -0,19 | -19,0% | 85,7% | -1,01 | -1,41 | 85,5%/92,2% | lãi sau phí |
| sweep | US500 | M15 | (2, 0, 12, 2, 1, 0) | 140 | 359 | 34,2% | 0,75 | -0,19 | -24,4% | 91,6% | -0,19 | -1,49 | 92,2%/96,6% | lãi sau phí |
| sweep | GER40 | M15 | (2, 0, 12, 0, 0, 0) | 172 | 399 | 31,5% | 0,64 | -0,31 | -48,8% | 99,7% | -0,88 | -1,52 | 99,7%/100,0% | lãi sau phí |
| sweep | US100 | M15 | (2, 0, 12, 1, 1, 0) | 133 | 418 | 37,6% | 0,73 | -0,19 | -23,0% | 90,7% | -0,31 | -1,58 | 90,8%/95,2% | lãi sau phí |
| sweep | US500 | H1 | (3, 0, 12, 1, 0, 0) | 110 | 1008 | 38,2% | 0,70 | -0,20 | -20,3% | 86,6% | -0,63 | -1,70 | 87,2%/92,9% | lãi sau phí |
| sweep | GBPAUD | H1 | (3, 0, 12, 2, 0, 0) | 109 | 1168 | 36,6% | 0,70 | -0,22 | -21,6% | 89,3% | -1,00 | -1,79 | 89,5%/94,0% | lãi sau phí |
| sweep | EURCAD | H1 | (3, 0, 12, 2, 0, 0) | 98 | 1104 | 36,1% | 0,63 | -0,27 | -23,8% | 90,8% | -1,59 | -2,14 | 91,1%/94,6% | ≥100 lệnh/năm |
| sweep | XAUUSD | M15 | (2, 1, 12, 2, 1, 0) | 124 | 432 | 36,5% | 0,64 | -0,27 | -29,4% | 95,9% | -1,18 | -2,18 | 95,6%/97,7% | lãi sau phí |
| sweep | GBPNZD | H1 | (3, 0, 12, 2, 0, 0) | 109 | 1133 | 35,3% | 0,61 | -0,30 | -28,4% | 94,8% | -1,54 | -2,24 | 95,0%/97,2% | lãi sau phí |
| sweep | US500 | M5 | (5, 1, 12, 2, 1, 0) | 137 | 128 | 34,0% | 0,64 | -0,28 | -32,3% | 96,9% | -0,87 | -2,25 | 97,0%/98,5% | lãi sau phí |
| sweep | GBPCAD | H1 | (2, 0, 12, 2, 0, 0) | 101 | 1243 | 34,8% | 0,60 | -0,30 | -26,9% | 93,8% | -1,42 | -2,34 | 94,1%/96,5% | lãi sau phí |
| sweep | AUDCAD | H1 | (2, 0, 12, 2, 0, 0) | 85 | 1338 | 34,2% | 0,56 | -0,35 | -26,1% | 93,0% | -2,51 | -2,54 | 93,2%/96,2% | ≥100 lệnh/năm |
| sweep | US100 | M5 | (2, 1, 6, 2, 1, 0) | 142 | 148 | 33,0% | 0,62 | -0,30 | -36,0% | 98,0% | -1,31 | -2,58 | 98,1%/99,2% | lãi sau phí |
| sweep | EURGBP | H1 | (2, 0, 12, 2, 0, 0) | 103 | 1356 | 31,9% | 0,56 | -0,35 | -30,8% | 96,1% | -2,07 | -2,66 | 96,2%/97,9% | lãi sau phí |
| sweep | NZDUSD | H1 | (2, 0, 12, 2, 0, 0) | 109 | 1031 | 34,1% | 0,57 | -0,33 | -31,1% | 96,2% | -1,81 | -2,68 | 96,3%/98,0% | lãi sau phí |
| sweep | USDCAD | H1 | (2, 1, 12, 2, 0, 0) | 102 | 1140 | 33,3% | 0,56 | -0,34 | -30,0% | 95,6% | -1,86 | -2,69 | 95,6%/97,6% | lãi sau phí |
| sweep | GBPAUD | M15 | (2, 1, 12, 2, 1, 0) | 119 | 382 | 33,1% | 0,59 | -0,33 | -33,1% | 97,4% | -1,40 | -2,76 | 97,2%/98,6% | lãi sau phí |
| sweep | EURCHF | H1 | (2, 0, 12, 1.5, 0, 0) | 79 | 1338 | 33,4% | 0,48 | -0,40 | -27,7% | 94,4% | -3,18 | -2,96 | 94,5%/96,4% | ≥100 lệnh/năm |
| sweep | XAUUSD | M5 | (5, 0, 6, 0, 0, 1) | 155 | 204 | 32,7% | 0,59 | -0,34 | -42,2% | 99,2% | -1,70 | -2,97 | 99,2%/99,7% | lãi sau phí |
| sweep | AUDNZD | H1 | (2, 0, 12, 1.5, 0, 0) | 92 | 1317 | 33,9% | 0,47 | -0,43 | -33,2% | 97,1% | -3,01 | -3,13 | 97,2%/98,4% | ≥100 lệnh/năm |
| sweep | EURCAD | M5 | (2, 0, 12, 2, 1, 0) | 121 | 261 | 31,4% | 0,52 | -0,39 | -38,6% | 98,6% | -2,19 | -3,15 | 98,7%/99,3% | lãi sau phí |
| sweep | GBPAUD | M5 | (2, 1, 12, 2, 1, 0) | 117 | 178 | 31,0% | 0,51 | -0,43 | -40,0% | 98,9% | -2,04 | -3,33 | 98,9%/99,4% | lãi sau phí |
| sweep | GBPCAD | M15 | (5, 0, 6, 1.5, 0, 0) | 124 | 506 | 32,2% | 0,51 | -0,40 | -40,0% | 98,9% | -2,25 | -3,44 | 98,9%/99,4% | lãi sau phí |
| sweep | GBPNZD | M15 | (5, 1, 6, 2, 0, 0) | 121 | 455 | 30,3% | 0,49 | -0,43 | -41,3% | 99,1% | -2,16 | -3,50 | 99,1%/99,5% | lãi sau phí |
| sweep | GER40 | M5 | (5, 1, 12, 1.5, 1, 0) | 154 | 182 | 31,5% | 0,52 | -0,42 | -48,8% | 99,8% | -1,82 | -3,58 | 99,7%/99,9% | lãi sau phí |
| sweep | USDCAD | M15 | (2, 0, 12, 2, 1, 0) | 118 | 551 | 30,3% | 0,47 | -0,44 | -41,1% | 99,0% | -2,42 | -3,71 | 99,1%/99,5% | lãi sau phí |
| sweep | EURCAD | M15 | (5, 1, 6, 1.5, 0, 0) | 129 | 367 | 33,1% | 0,49 | -0,41 | -41,9% | 99,2% | -2,32 | -3,76 | 99,2%/99,6% | lãi sau phí |
| sweep | GBPNZD | M5 | (5, 0, 6, 2, 0, 0) | 124 | 295 | 32,5% | 0,45 | -0,44 | -42,6% | 99,3% | -2,53 | -3,78 | 99,3%/99,6% | lãi sau phí |
| sweep | EURGBP | M15 | (5, 1, 6, 2, 0, 0) | 121 | 490 | 30,4% | 0,44 | -0,47 | -44,1% | 99,4% | -2,58 | -3,95 | 99,4%/99,7% | lãi sau phí |
| sweep | NZDUSD | M15 | (2, 1, 6, 2, 0, 0) | 127 | 411 | 28,4% | 0,44 | -0,51 | -48,0% | 99,7% | -2,75 | -3,99 | 99,7%/99,8% | lãi sau phí |
| sweep | EURGBP | M5 | (2, 1, 6, 2, 0, 0) | 115 | 249 | 28,0% | 0,40 | -0,53 | -45,8% | 99,5% | -3,22 | -4,00 | 99,6%/99,8% | lãi sau phí |
| sweep | GBPCAD | M5 | (2, 1, 6, 2, 0, 1) | 123 | 286 | 29,4% | 0,44 | -0,47 | -44,8% | 99,5% | -3,15 | -4,02 | 99,5%/99,7% | lãi sau phí |
| sweep | AUDCAD | M5 | (5, 0, 12, 2, 0, 0) | 118 | 361 | 32,4% | 0,38 | -0,47 | -43,1% | 99,3% | -3,95 | -4,14 | 99,3%/99,6% | lãi sau phí |
| sweep | AUDNZD | M5 | (3, 1, 12, 2, 0, 0) | 110 | 344 | 29,3% | 0,36 | -0,50 | -43,0% | 99,3% | -3,68 | -4,17 | 99,3%/99,6% | lãi sau phí |
| sweep | USDCAD | M5 | (5, 0, 12, 2, 1, 0) | 122 | 257 | 28,8% | 0,43 | -0,50 | -46,6% | 99,6% | -2,61 | -4,23 | 99,6%/99,8% | lãi sau phí |
| sweep | EURCHF | M15 | (5, 0, 12, 1, 0, 1) | 110 | 582 | 32,1% | 0,39 | -0,49 | -42,1% | 99,2% | -3,20 | -4,29 | 99,2%/99,5% | lãi sau phí |
| sweep | AUDCAD | M15 | (5, 0, 12, 1.5, 0, 0) | 121 | 628 | 30,6% | 0,40 | -0,50 | -45,9% | 99,6% | -3,37 | -4,35 | 99,5%/99,7% | lãi sau phí |
| sweep | EURCHF | M5 | (5, 0, 12, 2, 0, 1) | 119 | 317 | 27,6% | 0,37 | -0,54 | -47,8% | 99,7% | -3,60 | -4,37 | 99,7%/99,8% | lãi sau phí |
| sweep | AUDNZD | M15 | (2, 1, 12, 2, 0, 1) | 116 | 557 | 28,5% | 0,37 | -0,54 | -46,9% | 99,6% | -3,62 | -4,48 | 99,6%/99,8% | lãi sau phí |
| sweep | NZDUSD | M5 | (2, 1, 12, 1.5, 1, 0) | 125 | 265 | 30,0% | 0,39 | -0,53 | -49,1% | 99,7% | -3,26 | -4,49 | 99,7%/99,9% | lãi sau phí |

Cách đọc tham số: Sweep = (n, vào 0=mép/1=giữa FVG, W, TP 0=thanh khoản/R, lọc giờ, bias); ORB = (phút biên độ, SL 0=cạnh/1=giữa/2=ATR, TP R hoặc 0=cuối phiên); CHoCH = (n, TP R). CAGR âm vượt −100% là do vốn về 0 ở mức rủi ro 1%/lệnh.

## Ứng viên gần đạt nhất: ORB US100 M5

- OOS: 2028 lệnh (231/năm), win 34,3%, PF 1,07, R TB 0,05, CAGR 5,7%, DD 36,9%. Sharpe IS 0,89 → OOS 0,32, nên **rớt ở bước Sharpe OOS > 0,5**.
- Tham số hay được chọn nhất là (60, 2, 0), nhưng chỉ chiếm 22,2% số quý. Tham số đổi liên tục giữa các quý, tức là không ổn định. Độ nhạy 57,1%. Bootstrap DD p50 58,8%, p95 80,2%.
- Không đạt tiêu chí brain2 CAGR > 10% (DD < 80% thì đạt).
- Trên toàn kỳ, chỉ 7/36 biến thể ORB US100 và 2/36 biến thể US500 có R dương. Mọi cặp FX và vàng có 0/36 biến thể dương.

## Tóm tắt toàn kỳ (2017–10/2026, chưa walk-forward, chỉ để chẩn đoán)

| Hệ | Mã | Khung | Biến thể R>0 / có lệnh | Bản tốt nhất (≥100 lệnh/năm; H4 lấy bản tốt nhất) | Lệnh/năm | R TB | CAGR | DD |
|---|---|---|---|---|---|---|---|---|
| choch | AUDCAD | H1 | 0/9 | (3, 1) | 107 | -0,20 | -20,2% | 89,1% |
| choch | AUDCAD | H4 | 0/9 | (5, 1) | 24 | -0,04 | -1,0% | 14,3% |
| choch | AUDNZD | H1 | 0/9 | (3, 1) | 106 | -0,23 | -22,2% | 92,0% |
| choch | AUDNZD | H4 | 0/9 | (2, 1.5) | 34 | -0,11 | -3,9% | 38,3% |
| choch | EURCAD | H1 | 0/9 | (2, 1) | 154 | -0,15 | -20,8% | 90,2% |
| choch | EURCAD | H4 | 0/9 | (3, 1.5) | 27 | -0,02 | -0,6% | 21,6% |
| choch | EURCHF | H1 | 0/9 | (3, 1) | 106 | -0,21 | -20,4% | 89,5% |
| choch | EURCHF | H4 | 0/9 | (5, 1) | 21 | -0,04 | -1,0% | 16,5% |
| choch | EURGBP | H1 | 0/9 | (2, 1.5) | 121 | -0,14 | -16,5% | 85,6% |
| choch | EURGBP | H4 | 0/9 | (5, 2) | 21 | -0,00 | -0,2% | 17,8% |
| choch | GBPAUD | H1 | 0/9 | (2, 1) | 142 | -0,06 | -8,4% | 58,5% |
| choch | GBPAUD | H4 | 0/9 | (5, 1) | 23 | -0,07 | -1,7% | 21,0% |
| choch | GBPCAD | H1 | 0/9 | (3, 1) | 113 | -0,14 | -15,4% | 81,6% |
| choch | GBPCAD | H4 | 0/9 | (3, 1) | 31 | -0,06 | -1,9% | 22,8% |
| choch | GBPNZD | H1 | 0/9 | (3, 1) | 111 | -0,14 | -14,9% | 79,7% |
| choch | GBPNZD | H4 | 0/9 | (2, 1) | 41 | -0,13 | -5,5% | 44,2% |
| choch | GER40 | H1 | 0/9 | (2, 1) | 108 | -0,12 | -12,4% | 73,4% |
| choch | GER40 | H4 | 3/9 | (3, 2) | 25 | 0,79 | 8,3% | 32,1% |
| choch | US100 | H1 | 0/9 | (2, 1) | 144 | -0,10 | -14,2% | 81,8% |
| choch | US100 | H4 | 0/9 | (5, 1) | 23 | -0,01 | -0,2% | 12,9% |
| choch | NZDUSD | H1 | 0/9 | (3, 1) | 113 | -0,12 | -13,2% | 75,2% |
| choch | NZDUSD | H4 | 2/9 | (5, 1) | 21 | 0,03 | 0,5% | 9,5% |
| choch | US500 | H1 | 0/9 | (3, 1) | 112 | -0,08 | -9,2% | 66,4% |
| choch | US500 | H4 | 0/9 | (5, 1.5) | 20 | -0,03 | -0,8% | 13,9% |
| choch | USDCAD | H1 | 0/9 | (3, 1) | 112 | -0,16 | -16,5% | 82,8% |
| choch | USDCAD | H4 | 2/9 | (5, 1) | 22 | 0,05 | 1,0% | 11,4% |
| choch | XAUUSD | H1 | 0/9 | (3, 1) | 102 | -0,00 | -0,6% | 28,0% |
| choch | XAUUSD | H4 | 3/9 | (5, 1.5) | 21 | 0,02 | 0,3% | 12,4% |
| orb | AUDCAD | M5 | 0/36 | không bản nào ≥100 lệnh/năm | – | – | – | – |
| orb | AUDNZD | M5 | 0/36 | không bản nào ≥100 lệnh/năm | – | – | – | – |
| orb | EURCAD | M5 | 0/36 | (60, 0, 2) | 218 | -0,18 | -33,9% | 98,4% |
| orb | EURCHF | M5 | 0/36 | (60, 0, 1.5) | 164 | -0,22 | -31,2% | 97,5% |
| orb | EURGBP | M5 | 0/36 | (60, 1, 0) | 113 | -0,20 | -21,5% | 90,8% |
| orb | GBPAUD | M5 | 0/36 | (60, 0, 0) | 228 | -0,10 | -22,1% | 92,2% |
| orb | GBPCAD | M5 | 0/36 | (60, 0, 0) | 205 | -0,14 | -27,3% | 96,5% |
| orb | GBPNZD | M5 | 0/36 | (60, 0, 1.5) | 196 | -0,20 | -33,2% | 98,2% |
| orb | GER40 | M5 | 0/36 | (60, 0, 2) | 228 | -0,04 | -11,0% | 82,5% |
| orb | US100 | M5 | 7/36 | (60, 2, 0) | 219 | 0,03 | 4,2% | 42,0% |
| orb | NZDUSD | M5 | 0/36 | (60, 0, 2) | 203 | -0,22 | -36,4% | 98,9% |
| orb | US500 | M5 | 2/36 | (60, 0, 0) | 229 | 0,00 | -1,1% | 43,4% |
| orb | USDCAD | M5 | 0/36 | (60, 0, 1) | 209 | -0,22 | -37,5% | 99,0% |
| orb | XAUUSD | M5 | 0/36 | (60, 0, 0) | 211 | -0,14 | -27,1% | 96,6% |
| sweep | AUDCAD | H1 | 0/192 | (2, 0, 12, 1, 0, 0) | 104 | -0,37 | -32,2% | 97,8% |
| sweep | AUDCAD | M15 | 5/192 | (2, 0, 6, 1, 0, 0) | 104 | -0,40 | -34,6% | 98,4% |
| sweep | AUDCAD | M5 | 3/192 | (3, 1, 12, 1, 0, 0) | 125 | -0,45 | -43,5% | 99,6% |
| sweep | AUDNZD | H1 | 1/192 | (2, 0, 12, 1, 0, 0) | 109 | -0,38 | -34,3% | 98,4% |
| sweep | AUDNZD | M15 | 0/192 | (2, 0, 12, 1, 0, 0) | 214 | -0,47 | -63,7% | 100,0% |
| sweep | AUDNZD | M5 | 2/192 | (3, 0, 12, 1, 0, 1) | 109 | -0,45 | -39,3% | 99,2% |
| sweep | EURCAD | H1 | 5/192 | (3, 0, 12, 1, 0, 0) | 102 | -0,20 | -18,8% | 87,0% |
| sweep | EURCAD | M15 | 0/192 | (5, 0, 6, 1, 0, 0) | 154 | -0,37 | -43,7% | 99,6% |
| sweep | EURCAD | M5 | 0/192 | (2, 0, 12, 2, 1, 0) | 140 | -0,37 | -41,0% | 99,4% |
| sweep | EURCHF | H1 | 0/192 | (2, 0, 12, 1, 0, 0) | 106 | -0,38 | -33,4% | 98,1% |
| sweep | EURCHF | M15 | 0/192 | (5, 0, 12, 1, 0, 1) | 110 | -0,41 | -36,9% | 98,9% |
| sweep | EURCHF | M5 | 0/192 | (5, 1, 12, 1, 0, 0) | 168 | -0,49 | -56,7% | 100,0% |
| sweep | EURGBP | H1 | 0/192 | (2, 0, 12, 2, 0, 0) | 105 | -0,30 | -27,9% | 96,0% |
| sweep | EURGBP | M15 | 0/192 | (5, 1, 12, 1, 0, 0) | 170 | -0,39 | -49,4% | 99,9% |
| sweep | EURGBP | M5 | 1/192 | (3, 0, 12, 0, 0, 0) | 102 | -0,43 | -36,5% | 98,8% |
| sweep | GBPAUD | H1 | 0/192 | (3, 0, 12, 1.5, 0, 0) | 107 | -0,20 | -20,3% | 89,7% |
| sweep | GBPAUD | M15 | 0/192 | (2, 0, 12, 2, 1, 0) | 108 | -0,26 | -25,5% | 94,7% |
| sweep | GBPAUD | M5 | 0/192 | (3, 0, 12, 0, 0, 0) | 181 | -0,35 | -47,6% | 99,8% |
| sweep | GBPCAD | H1 | 0/192 | (2, 0, 12, 1, 0, 0) | 109 | -0,25 | -24,2% | 93,7% |
| sweep | GBPCAD | M15 | 1/192 | (5, 0, 6, 1, 0, 0) | 127 | -0,32 | -34,2% | 98,4% |
| sweep | GBPCAD | M5 | 0/192 | (2, 0, 12, 1.5, 1, 0) | 105 | -0,39 | -33,9% | 98,3% |
| sweep | GBPNZD | H1 | 0/192 | (2, 1, 12, 1, 0, 0) | 102 | -0,23 | -21,4% | 90,6% |
| sweep | GBPNZD | M15 | 0/192 | (2, 1, 6, 2, 0, 0) | 144 | -0,38 | -42,5% | 99,6% |
| sweep | GBPNZD | M5 | 0/192 | (3, 0, 6, 1, 0, 0) | 174 | -0,36 | -47,2% | 99,8% |
| sweep | GER40 | H1 | 8/192 | không bản nào ≥100 lệnh/năm | – | – | – | – |
| sweep | GER40 | M15 | 0/192 | (3, 0, 12, 0, 0, 1) | 101 | -0,05 | -14,8% | 84,2% |
| sweep | GER40 | M5 | 4/192 | (2, 0, 12, 1.5, 1, 1) | 123 | 0,32 | -19,4% | 95,2% |
| sweep | US100 | H1 | 25/192 | (3, 0, 12, 1, 0, 0) | 105 | -0,16 | -16,3% | 83,7% |
| sweep | US100 | M15 | 0/192 | (2, 0, 12, 1.5, 1, 0) | 114 | -0,15 | -15,9% | 82,3% |
| sweep | US100 | M5 | 0/192 | (3, 0, 6, 1.5, 1, 0) | 124 | -0,25 | -27,7% | 96,0% |
| sweep | NZDUSD | H1 | 4/192 | (2, 0, 12, 1, 0, 0) | 119 | -0,29 | -29,5% | 96,8% |
| sweep | NZDUSD | M15 | 0/192 | (3, 1, 12, 1, 0, 1) | 158 | -0,45 | -50,9% | 99,9% |
| sweep | NZDUSD | M5 | 0/192 | (5, 1, 6, 1, 0, 0) | 112 | -0,45 | -40,2% | 99,3% |
| sweep | US500 | H1 | 4/192 | (3, 0, 12, 1, 0, 0) | 106 | -0,13 | -13,0% | 75,1% |
| sweep | US500 | M15 | 0/192 | (2, 0, 12, 1, 1, 0) | 106 | -0,16 | -16,5% | 83,0% |
| sweep | US500 | M5 | 0/192 | (5, 0, 12, 1, 1, 0) | 155 | -0,22 | -29,9% | 96,9% |
| sweep | USDCAD | H1 | 1/192 | (2, 1, 12, 1, 0, 0) | 102 | -0,29 | -26,0% | 94,8% |
| sweep | USDCAD | M15 | 0/192 | (2, 0, 12, 2, 1, 0) | 101 | -0,32 | -28,2% | 96,2% |
| sweep | USDCAD | M5 | 0/192 | (5, 0, 12, 2, 1, 0) | 100 | -0,40 | -33,8% | 98,3% |
| sweep | XAUUSD | H1 | 0/192 | (2, 0, 12, 1.5, 0, 0) | 114 | -0,19 | -20,2% | 90,8% |
| sweep | XAUUSD | M15 | 0/192 | (2, 1, 12, 2, 1, 0) | 108 | -0,19 | -19,3% | 91,6% |
| sweep | XAUUSD | M5 | 0/192 | (5, 1, 12, 2, 1, 0) | 126 | -0,27 | -30,2% | 97,1% |

**Thang luật Sweep+FVG** (R ròng trung bình/lệnh trên mọi mã, khung và tham số còn lại):
- Lọc giờ: không lọc -0,38, có lọc Silver Bullet -0,34.
- Bias ngày: không -0,36, có -0,36.
- Điểm vào: mép FVG -0,35, giữa FVG -0,37.
- TP: thanh khoản -0,39, 1R -0,33, 1,5R -0,35, 2R -0,37.
- Không có luật nào kéo kết quả lên dương.

## Vì sao trượt

- **Phí XM so với khoảng SL:** hệ vào ra nhanh có SL nhỏ. Ví dụ Sweep GBPCAD M15 có SL trung vị chỉ khoảng 3,9 × spread, nên riêng spread đã ăn khoảng 0,25R mỗi lệnh. Brendan test trên NQ/ES, nơi phí rất nhỏ so với biến động; spread cặp cross của XM micro lớn hơn nhiều.
- **Khớp limit thận trọng:** lệnh FVG chỉ khớp khi giá xuyên qua limit. Đây đúng là lỗi chọn ngược mà Brendan cảnh báo: lệnh nào cũng khớp khi thua, nhưng hụt nhiều lệnh thắng. Vì thế R gộp đã âm trước cả phí.
- **ORB trên FX/vàng phiên London:** không có edge, R gộp ≈ 0 hoặc âm, toàn bộ 0/36 biến thể dương. Trên chỉ số Mỹ có edge nhỏ, nhưng không ổn định qua các quý.
- **CHoCH H1:** win rate ≈ 48% ở TP 1R, không đủ bù phí. CHoCH H4 gần hòa vốn ở vài mã nhưng chỉ khoảng 20–40 lệnh/năm, trái với yêu cầu nhiều lệnh.

## Đề xuất

1. **Chưa viết EA MT5** cho hệ nào trong ba hệ.
2. Nếu muốn đi tiếp, thử ORB trên US100/US500 với dữ liệu tick/spread thật của XM, vì spread Cash# ban ngày có thể thấp hơn p90 đã dùng. Trước khi viết EA, cần ghi trước một bộ tham số cố định và kiểm lại trên dữ liệu XM.
3. Sweep+FVG trên XM micro: chỉ đáng xem lại nếu có tài khoản spread thấp hơn (ví dụ Ultra Low #) và khoảng SL lớn hơn nhiều lần spread. Tuy vậy, hệ đã âm cả trước phí nên kỳ vọng thấp.
4. Bài học khớp với Brendan: khung càng nhanh thì phí càng ăn mất edge. Các hệ nhiều lệnh và vào ra nhanh trên forex cross của XM không sống được với bộ kiểm định này.

## Giới hạn và cảnh báo

- Dữ liệu chỉ có BID từ HistData, không phải feed XM. Spread được giữ cố định ở p90 đo tháng 10/2026, nên không phản ánh spread giãn lúc ra tin hoặc lúc rollover. Swap và hoa hồng lịch sử chưa đo được.
- US30, EURNZD và NZDCAD chưa test vì thiếu dữ liệu. Chỉ số GER40 có gap dữ liệu.
- Đã thử 8.820 biến thể. Nếu có hệ qua phễu thì vẫn phải hiệu chỉnh cho việc chạy nhiều phép thử, nhưng ở đây không có hệ nào qua.
- Script: `dung.py` (dữ liệu), `dongco.py` (phí, thoát lệnh), `he.py` (luật), `chay.py` (lưới), `phan_tich.py` (walk-forward, phễu), `tong_hop.py`, `bao_cao.py`.