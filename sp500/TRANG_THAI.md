# TRẠNG THÁI SP500 — cập nhật 27/11/2026 19:25 (giờ Việt Nam)

## Đang chạy
- **Không có gì đang chạy.** Mọi terminal và tester do việc SP500 mở trên máy nhà đều đã tự tắt hoặc đã dừng theo đúng PID. Terminal XM chính (`C:\Program Files\XM Global MT5`) không bị đụng.
- Routine của bot vẫn tạm dừng (từ t335).

## Đã xong
- Mô-đun `sp500/` gồm mã, EA, kết quả và báo cáo `BAO_CAO_2026-11-27.md`.
- Lưới Python 4.950 biến thể, walk-forward và bộ ghép.
- MT5: 48 bộ BatDay chạy tick thật; 25 test Lịch/IBS (model 2 cho 10 năm, model 4 cho tick thật).
- Đã kéo ESZ6 bằng Fxaurum (chỉ RPC đọc).

## Ứng viên hiện tại
- **IBS < 0,1, SMA200, giữ 3 ngày, mua 15:50 NY** (`ea/SP500_Lich.mq5`, CheDo=4). Trên MT5, đòn bẩy 5: 17,6 %/năm, DD 40,8 % (DD tính theo số dư khi đóng lệnh), 133 lệnh, 2017–2026.

## Tệp và đường dẫn trên máy nhà
- Thư mục làm việc: `C:\Users\DUNG\sp500_2711\`. Chứa chuỗi test `chuoi4\chuoi4.ps1` (mẫu có chặn RAM), các CSV kết quả, và `esz6\*.json` (dữ liệu Fxaurum).
- EA đã biên dịch: `E:\mt5_tester\p6\MQL5\Experts\sp500\` và `E:\mt5_tester\p3\MQL5\Experts\sp500\`.
- Tệp `.set`/`.ini` ở `E:\mt5_tester\p6\` (tên `sp500_*.ini`).

## Cách tiếp tục
1. Box: đọc `README.md`, chạy `ma/du_lieu.py` trước nếu thư mục tạm bị mất.
2. MT5: chỉ dùng **p6**. Không chạy song song với p3, p5, g2… vì các slot này dùng chung Bases. Phối hợp với việc vàng (p3, p4) qua `vang/`.
3. Chạy một test: chép mẫu `.ini` trong `E:\mt5_tester\p6\`, khởi động bằng `terminal64.exe /portable /config:<ini>` rồi chờ terminal tự tắt. CSV giao dịch nằm ở `%APPDATA%\MetaQuotes\Terminal\Common\Files\sp500_*.csv`. Chuyển CSV đi, tổng hợp bằng `ma/tong_mt5.py`.
4. Không dùng Optimization với model 1 trên 10 năm, vì agent ăn tới 22 GB RAM.
