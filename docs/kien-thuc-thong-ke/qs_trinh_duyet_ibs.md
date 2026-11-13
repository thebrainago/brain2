# Quantified Strategies – số liệu đọc trực tiếp bằng trình duyệt (2026-11-13)

Nguồn: https://www.quantifiedstrategies.com/ibs-internal-bar-strength-indicator-strategies/
Cách lấy: trình duyệt trên máy chủ Grok Bot (theo quy cách trong docs/ban-giao/SEEKER_DANG_NHAP_ban_giao.md). Sau bài này site bật xác minh chống bot (captcha báo "Server responded with 404 / Verification failed"), chưa đọc thêm được.

IBS = (Close - Low) / (High - Low)

| # | Thị trường | Quy tắc | Giai đoạn | Số lệnh | Lãi TB/lệnh | Win rate | CAGR | Max DD |
|---|---|---|---|---|---|---|---|---|
| 1 | SPY | Mua đóng cửa khi IBS < 0.2; bán đóng cửa khi IBS > 0.8 | 1993 – nay | 919 | 0.41% | 68% | 12.5% (B&H 9.9%) | -26% |
| 2 | QQQ | Như trên | từ khi niêm yết – nay | 742 | 0.56% | không ghi | 16.6% | không ghi |
| 3 | SPY | Chỉ dùng IBS cho cả vào và ra (ngưỡng không hiện trong đoạn đọc được) | 1993 – nay | 583 | không ghi | 74% | 15.3% | 22% |

Ghi chú áp dụng cho brain2: khớp hướng với các ứng viên IBS thấp + lọc xu hướng đang dẫn đầu trong NGHI/SEEKER. Số liệu là cổ phiếu Mỹ khung ngày; phải kiểm lại trên cặp chéo H4 trước khi coi là tín hiệu. Chưa pass.
