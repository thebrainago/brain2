# sp500/ — mô-đun riêng cho SP500 (XM US500Cash, tài khoản micro)

Tạo ngày 27/11/2026 theo chỉ thị của Anh (t341u, t342u). Mọi việc SP500 nằm trong thư mục này; vàng nằm ở `vang/`, bàn giao chung ở `ban_giao/`.

## Cấu trúc

| Đường dẫn | Nội dung |
|---|---|
| `ma/cau_hinh.py` | Đường dẫn dữ liệu. Biến môi trường `SP500_TAM` (thư mục tạm, mặc định `/workspace/sp500_2711`) và `SP500_M5` (HistData SPXUSD BID M5, mặc định `/workspace/quet_intraday/m5/spxusd.parquet`). |
| `ma/du_lieu.py` | Đổi giờ HistData (EST cố định) sang giờ New York, cắt phiên RTH 09:30–16:00, tạo bảng ngày. Chạy đầu tiên. |
| `ma/dong_co.py` | Động cơ mô phỏng: chi phí XM (spread 0,8 điểm khứ hồi, swap mua 5,77 %/năm, swap bán lấy 0), các bộ lọc xu hướng (SMA50/100/200, độ dốc SMA, ADX, ghép), hàm `ket_qua` tính CAGR và DD (có tính đáy trong ngày) theo đòn bẩy. |
| `ma/he.py` | Thư viện tín hiệu: ORB, vào theo giờ, bắt đáy trong ngày, kéo về VWAP gần đúng, gap (lấp/theo), RSI2, IBS, qua đêm, cuối tháng (TOM), Donchian, mua-giữ. |
| `ma/luoi.py`, `luoi2.py`, `luoi3.py` | Ba lưới tham số (3.330 + 680 + 940 = 4.950 biến thể × 8 mức đòn bẩy). |
| `ma/wf.py` | Walk-forward: mỗi năm chọn biến thể tốt nhất trên 3 năm trước rồi áp cho năm sau. |
| `ma/to_hop.py` | Bộ ghép: chọn chân theo Sharpe 2017–2021, tương quan < 0,6; ghép đơn/cặp/bộ ba; 2022–2026 là ngoài mẫu. |
| `ma/ben_vung.py` | Kiểm độ nhạy phí: spread 0,8 / 1,5 / 3,0 điểm, trượt 0,5 điểm. |
| `ma/keo_esz6.py` | Chạy **trên máy nhà**: kéo ESZ6 (klines 1m, bigTrades, flowRecs) từ gateway Fxaurum `ws://127.0.0.1:9001/`. Chỉ RPC đọc, không gọi syncTicks/syncHistory. |
| `ma/tong_mt5.py` | Tổng hợp CSV giao dịch do EA xuất ra thành CAGR, DD, số lệnh, swap. |
| `ea/SP500_BatDay.mq5` | EA bắt đáy trong phiên Mỹ (limit tại Open − k×ATR, TP về Open, đóng 15:50 NY). |
| `ea/SP500_Lich.mq5` | EA theo lịch: bit1 TOM, bit2 qua đêm thứ Hai, bit4 IBS. Xuất CSV giao dịch vào thư mục Common của MT5. |
| `ket_qua/` | Kết quả gọn đã đo (JSON/CSV). Thư mục `ket_qua/boba_v3/` là của phiên khác, không sửa. |
| `BAO_CAO_2026-11-27.md` | Báo cáo kết quả đợt 27/11. |
| `TRANG_THAI.md` | Đang chạy gì, tiếp tục thế nào. |

## Chạy lại (box)

```bash
cd sp500/ma
python3 du_lieu.py          # tạo rth_m5.parquet, ngay.parquet trong SP500_TAM
python3 luoi.py && python3 luoi2.py && python3 luoi3.py   # ~1,5 phút trên 6 nhân
python3 wf.py && python3 to_hop.py && python3 ben_vung.py
```

## MT5 trên máy nhà (quy tắc)

- Slot SP500 được dùng: **p6** (và p1 nếu dựng xong; hiện p1 chưa có terminal). p3, p4 để cho việc vàng.
- p3, p5, p6, g2, g3, g4 **dùng chung Bases** qua junction `E:\brain2_grok\shared_bases`. Hai terminal chạy cùng lúc trên các slot này sẽ khóa tệp lịch sử (lỗi 32). Chỉ chạy một terminal trên nhóm này tại một thời điểm.
- Tối ưu hóa MT5 tự mở 20 agent. Với model M1 OHLC 10 năm, một agent ăn tới 22 GB RAM. **Không** dùng Optimization với model 1 trên 10 năm. Chạy test đơn lẻ, model 2 (giá mở M5) cho hệ theo lịch/IBS, và model 4 (tick thật) cho giai đoạn có tick.
- Tick thật XM của US500Cash# chỉ có từ **21/07/2025**.
- Chuỗi test có chặn RAM: dừng khi RAM trống < 6 GB hoặc quá 40 phút (xem `C:\Users\DUNG\sp500_2711\chuoi4\chuoi4.ps1`).
- Mã trên tài khoản slot: `US500Cash#` (1 lot = 1 USD/điểm, phí hoa hồng 0).

## Tiêu chí của Anh

Lãi kép CAGR > 10 %/năm và DD < 80 % sau phí XM (spread, swap, hoa hồng). Không khóa holdout 2 năm; tối ưu riêng từng mã. Chỉ báo số đã đo.
