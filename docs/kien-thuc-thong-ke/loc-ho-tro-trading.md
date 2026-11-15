# Lọc cho bộ hỗ trợ trading (bias, DCA, vùng tín hiệu)

Cập nhật: 2026-11-13 15:44 (Asia/Saigon, UTC+7)

Nguyên tắc: thống kê cổ phiếu/chỉ số Mỹ **không được copy nguyên ngưỡng sang forex**. Chỉ giữ ý tưởng, rồi test trên AUDCAD, AUDNZD, EURCAD, CADJPY (ưu tiên, ít USD). Mọi mục dưới đây đều **chưa pass SEEKER**.

## Nên đưa vào test (ưu tiên cao)

### 1. Vùng stretch so với MA50 của chính cặp — tín hiệu + DCA
- Nguồn: EVO tự tính (`evo-ma50-forex-crosses`, đối chiếu `evo-ma50-dji-dinh-gay`).
- Vì sao: trên Dow/S&P, "cách MA50 24% là gãy" **không xảy ra** (max DJ 14,99% năm 2020; max SPX 15,40% năm 1982). Đỉnh 60 phiên rồi giảm ≥10% có d trung bình chỉ **4,81% (DJ)** và **4,99% (SPX)**. Trên 4 cặp chéo, p99 khoảng **4,3–6,7%**; khi vừa vượt p99, **50–73%** episode có drawdown ≥3% trong 60 phiên, và **83–100%** có lúc đóng cửa dưới MA50.
- Mã hóa (ứng viên):
  - `d = (Close-MA50)/MA50*100` trên D1 (và test thêm H4).
  - Vùng tín hiệu short / không đuổi mua: `d >= p99` (hoặc p99,5) của chính cặp.
  - Vùng tín hiệu long / không đuổi bán: `d <= p1` (hoặc p5).
  - DCA: chỉ bổ sung ngược hướng stretch khi d ở cực hạn **và** có xác nhận (IBS thấp/cao, hoặc nến đóng hướng về MA50). Không DCA vì "còn cách 24%".
- Cờ SEEKER: **có**. Cần chạy trên dữ liệu Dukascopy/MT5, không chỉ Yahoo, và trên H4.

### 2. Mean-reversion có lọc trend (kiểu Connors Multiple Days Down) — tín hiệu + bias
- Nguồn: QS `qs-connors-multiple-days-down` (2.210 lệnh, +0,31%/lệnh, CAGR 6,4%, 2000–2020, **cổ phiếu**; win rate chưa lấy được; rule cần đối chiếu toàn văn).
- Mã hóa (ứng viên): ≥4/5 phiên giảm, dưới SMA5, **trên** SMA200 (lọc không bắt dao rơi); thoát khi đóng cửa lại trên SMA5. Short đối xứng.
- Forex: ý tưởng chuyển được; số 0,31% không chuyển.
- Cờ SEEKER: **có**.

### 3. IBS cực hạn — tín hiệu / xác nhận DCA
- Nguồn: QS Turnaround Tuesday + IBS < 0,2 (270 lệnh SPY 1993–9/2021, +0,33%/lệnh, thắng 57%).
- Mã hóa: `IBS = (Close-Low)/(High-Low)`. Long khi IBS < 0,2 (hoặc 0,25) sau phiên giảm; short khi IBS > 0,8. Có thể kết hợp với điều kiện d (mục 1).
- Lịch "thứ Hai" của Mỹ: test riêng, không cứng hóa.
- Cờ SEEKER: **có**.

## Có thể dùng như bias nhẹ (ưu tiên trung bình / thấp)

- **Đóng cửa vs MA50 / MA200**: bias xu hướng. Không phải lệnh.
- **Turnaround / weekday**: test "phiên đầu tuần giảm mạnh rồi đảo" trên từng cặp (`qs-turnaround-tuesday-spy-1pct`, `qs-weekday-after-down-day`). Không copy +0,22%.
- **Mùa vụ Almanac / Detrick** (Santa +1,3% từ 1950; Best Six Months +7,0% và tăng 76% số lần — S&P): chỉ bias lịch, ưu tiên thấp, phải tự đếm trên forex nếu còn dùng.
- **Breadth / sentiment Mỹ** (Zweig Thrust 19 lần từ 1928; S&P AD 2,02 với 44/48 thắng cửa 12 tháng từ 1942; Bespoke 93,44% mã trên MA50 = 0,5% số ngày từ 1990): **không** thành vùng giá forex. Tối đa là bias risk-on/off khi có dữ liệu, chưa xây trong lượt này.
- **Bulkowski failure / busted**: bài học "pattern thất bại nhiều hơn lời đồn, và đổi theo thập niên" (14% → 28% thất bại 10% với breakout lên, 13.932 mẫu 1991–2008). Ứng viên: test breakout thất bại trên H4/D1, **tự tính %**, không dùng 10%/24%/40% của cổ phiếu.

## Không đưa vào bộ hỗ trợ forex

- Ngưỡng **24% trên MA50** như điều kiện "đỉnh gãy" của Dow/S&P.
- January Barometer 84% / Trifecta 93,1% (cổ phiếu Mỹ, 1 quan sát/năm, số Trifecta dừng ở alert 2018).
- Turnaround trên SSO đòn bẩy 2x.
- Mọi bảng premium chưa mở được (NDR, nhiều report Bespoke/SentimenTrader).
- Tweet chưa xác minh của các tài khoản X.

## Ghi nhớ mẫu nhỏ

Nhiều mục nổi tiếng có N rất nhỏ: 1–11 episode MA50 trên Dow ở ngưỡng cao; 19 Zweig Thrust; 10 "Sell in May tốt nhất"; 29 lần Trifecta (số 2018). Viết vào tool thì phải hiện N, không hiện mỗi % thắng.
