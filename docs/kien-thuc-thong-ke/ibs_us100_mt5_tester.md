# Kết quả Strategy Tester — IBS_US100 (XM demo, máy nhà)

Cập nhật: 2026-11-15 09:42 (Asia/Saigon, UTC+7)

**Nhãn: ứng viên – chưa pass.** Chỉ chạy tester / demo. Không phải đã vượt cổng SEEKER, không dùng để chạy live.

## Môi trường

- Terminal: bản portable tester `E:\mt5_tester\p5` (XM Global MT5 build 6231), tài khoản **demo**, không đụng slot live.
- Mã sàn: `US100Cash#` (tên `US100Cash` không còn trên server này).
- Khoảng yêu cầu: 2015.01.01–2026.11.15. Lệnh đầu tiên: 2016.06.08 02:00; lệnh cuối: 2026.11.10 01:15. Năm 2015 không có lệnh (lịch sử M1/M15 đầu kỳ mỏng).
- Mô hình: Open prices trên khung **M15** (EA vẫn đọc nến D1). Model “Open prices only” trên D1 chỉ sinh tick 00:00 lúc CFD đóng cửa nên mọi lệnh thất bại (`retcode=10018`). Model “1 minute OHLC” trên D1 chiếm ~22 GB RAM và bị dừng sau ~8 phút, chưa ra báo cáo.
- Nạp: 10 000 USD, đòn bẩy 1:100, lot cố định 0.10, `InpAckDemoOnly=true`, IBS 0.20 / 0.80, tối đa 4 nến, không lọc VIX/spread.
- Compile: 0 lỗi, 0 cảnh báo (`metaeditor64.exe /portable /compile`).

## Sửa EA (không đổi quy tắc)

Thêm retry trong cùng nến D1 nếu tick đầu gặp *market closed*, rồi khớp ở tick mở phiên (thường 01:15, đôi khi 02:00). Vẫn: tín hiệu lúc đóng nến t, khớp mở phiên nến t+1; không vào lại ngay nến vừa thoát.

## Kết quả tester (báo cáo MT5)

| Chỉ số | MT5 US100Cash# | Kỳ vọng Python (QQQ / ^NDX, OOS 2015+) |
|---|---:|---|
| Số lệnh | 350 | 371 / 395 |
| Win% | 66.57% | 63.3% / 62.5% |
| Profit factor | 1.38 | 1.51 / 1.41 |
| Lãi ròng (lot 0.10, vốn 10k) | +1 169.14 USD | — (không cùng cỡ lệnh) |
| Sharpe (MT5) | 0.77 | 0.71 / 0.61 (cách tính khác) |
| Max DD vốn 10k, lot 0.10 | 4.57% (equity) | — |
| Swap / hoa hồng | swap −547.50; hoa hồng 0 | phí giả định trong script |

`%/năm` trên tài khoản không so được trực tiếp với bảng Yahoo: lot 0.10 chỉ bằng 0,1× giá chỉ số (danh nghĩa ~451 USD lúc lệnh đầu, ~2 644 USD lúc lệnh cuối). Lãi tài khoản: +11.69% tổng, CAGR ~1.07%/năm.

Quy về **danh nghĩa 1× chỉ số** (lãi/swap chia danh nghĩa lúc vào, ghép lãi): lãi TB +0.25%/lệnh, PF 1.38, win 66.57%, CAGR ~7.88%/năm, max DD ~20.1% trên 10.42 năm (2016.06–2026.11). Gần kỳ vọng ^NDX (+0.25%/lệnh, PF 1.41, ~8.13%/năm, DD 22.5%) hơn QQQ (~9.7%/năm, PF 1.51).

## Theo năm (lãi ròng lot 0.10, và % nếu 1× danh nghĩa)

| Năm | Lệnh | Win% (theo P/L ròng) | P/L lot 0.10 | % 1× danh nghĩa |
|---:|---:|---:|---:|---:|
| 2016 | 14 | 57.1% | −6.76 | −1.36% |
| 2017 | 25 | 60.0% | +33.60 | +5.35% |
| 2018 | 34 | 61.8% | −103.24 | −15.50% |
| 2019 | 31 | 74.2% | +119.20 | +17.61% |
| 2020 | 43 | 74.4% | +323.53 | +34.84% |
| 2021 | 35 | 65.7% | +270.77 | +20.86% |
| 2022 | 44 | 59.1% | −24.84 | −0.05% |
| 2023 | 37 | 75.7% | +254.42 | +20.40% |
| 2024 | 34 | 58.8% | −32.75 | −2.59% |
| 2025 | 25 | 68.0% | −4.51 | −2.99% |
| 2026 | 28 | 71.4% | +339.72 | +15.21% |

Năm dương (1×): 2017, 2019–2021, 2023, 2026 (6/11). Năm 2022 gần hòa trên CFD sàn này, không lỗ 11–16% như chuỗi Yahoo. 2018 là năm lỗ nặng (−15.5% 1×).

## Kết luận

- Compile được, tester chạy được trên demo, quy tắc vào/ra khớp đặc tả sau khi retry mở phiên.
- PF / win% / lãi TB% / CAGR 1× / DD 1× cùng hướng với kỳ vọng ^NDX 2015+, hơi yếu hơn QQQ — đúng tầm “ứng viên, chưa pass”.
- Lịch sử 2015 thiếu; quality trong báo cáo là n/a; fill ở M15 open (không phải tick thật mọi phút).
- Không đủ để gọi là pass. Không chạy live.
