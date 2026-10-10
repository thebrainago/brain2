# Ghi chú nâng cấp (Grok trên brain2) — 2026-10-10

## 1. Nút bóc tách EA mẫu (mau_thu/)
- Chạy `python mau_thu/do_moc.py` trên Linux: vẫn **0 cơ chế** từ 22 điểm vào lệnh.
- Nguyên nhân chính đã xác nhận:
  - Biến trung gian kiểu `bool upbreakout = current[0].high - (_Point*margin) > highrange;`
  - Parser `_GAN_BOOL` ban đầu không bắt được vì có tiền tố kiểu (`bool`, `int`...).
  - Đã patch `_GAN_BOOL` để chấp nhận tiền tố kiểu tùy chọn.
  - Sau patch, các tên biến như `downbreakout` biến mất khỏi danh sách “chưa diễn đạt được”, nhưng biểu thức bên trong (`current[0].high...`, `Tradesinfo.xxx`) vẫn không được dịch thành DSL vì `_toan_hang` / `_SS` chưa hỗ trợ truy cập mảng/chỉ báo MQL5 và biến đối tượng.

## 2. Hướng nâng cấp tiếp theo (ưu tiên)
- Mở rộng `_toan_hang` hoặc thêm lớp đơn giản hóa biểu thức MQL5 trước khi đưa vào DSL:
  - Nhận dạng `current[0].high/low/close/open`
  - `_Point`, `SymbolInfoDouble`, phép toán đơn giản
  - Biến đối tượng kiểu `Tradesinfo.xxx`
- Nối kết quả bóc tách thành công vào luồng `ngu_phap` → `mo_phong` (Python) để có thể kiểm thử mà không cần MT5.

## 3. Dữ liệu mẫu có sẵn
- `reports/`: nhiều file tổng kết (BANG_HE.json, AUDCAD_*.json/md, BENCH_QT_*.json...). Có thể dùng để kiểm tra luồng Python (bang_he, cham_diem, cong_ra_tien).
- Không có log tester thô hoặc dữ liệu giá.

## 4. Liên kết module đã kiểm tra
- `cong_ra_tien` đã được gọi từ `bang_he.py`, `cham_diem.py`, `vong_day_du.py`.
- `evo.py` đã có import và tương tác với `day_viec`.
- Còn nhiều module mồ côi (xem `b.py ban-do`).

## 5. Phần chạy được trên Linux ảo
- `b.py` và các lệnh chẩn đoán (ban-do, kien-truc, trang-thai, he, ngan-sach).
- Import các module chính.
- `mau_thu/do_moc.py`.
- Không chạy được: MT5, nao.db đầy đủ, data/, browser Seeker.

Tiếp tục: cải thiện parser biểu thức MQL5 và nối vào cổng kiểm định Python.

## 6. Prototype parser đơn giản (chạy được trên Linux)
Đã thử pattern cơ bản cho `current[0].high/low/close`. Có thể mở rộng thành lớp tiền xử lý trước khi gọi `_toan_hang`.

Các module liên quan cần nối:
- `doc_ma.py` (đã patch) → `ngu_phap.py` → `mo_phong.py` (Python backtest)
- `cong_ra_tien.py` đã được dùng bởi `bang_he.py` (có thể kiểm tra với dữ liệu reports/)

Tiếp theo: viết hàm chuẩn hóa biểu thức MQL5 đơn giản và tích hợp vào `doc_chien_luoc`.

## 7. Kết quả đo được (2026-10-10)
Sau các cải tiến có kiểm soát trong `doc_ma.py`:
- Trước: 0 / 22 điểm vào lệnh → 0 cơ chế
- Sau: 3 / 22 → **13.6%**
- 3 file mẫu đã ra được cơ chế: Breakout1, CurrencyStrength1, Pivots1

Các pattern còn lại cần xử lý tiếp:
- Biểu thức có `&&` / `||` phức tạp hơn
- Biến đối tượng (`Tradesinfo.xxx`)
- Hàm gọi (`PivotsIsPivotRange(...)`)

Đây là bước đầu có số liệu, không phải kết luận cuối.

## 8. Vòng lặp tối thiểu đã chạy được
Đã tạo `vong_thu_nghiem.py`:
- Quét `mau_thu/*.mq5`
- Bóc tách bằng `doc_chien_luoc`
- Sinh tín hiệu qua `ngu_phap._dieu_kien`
- Mô phỏng bằng `mo_phong.chay` trên dữ liệu giả lập
- Kết quả: 3 cơ chế chạy thành công, sinh lệnh và phơi nhiễm.

Đây là khung để sau này thay dữ liệu giả bằng dữ liệu thật và thêm bước tối ưu thông số.

## 9. Mục tiêu và logic làm việc (ghi nhớ)
**Mục tiêu cuối**: Vòng lặp liên tục
quét đầu vào → bóc tách cơ chế → kiểm định (Python/C++ thay MT5) → tối ưu thông số → giữ lại cơ chế/tính năng hay → học hỏi.

**Logic ưu tiên hiện tại**:
1. Nâng tỷ lệ bóc tách từ mẫu .mq5 (đo bằng `mau_thu/do_moc.py` và `vong_thu_nghiem.py`).
2. Giữ vòng lặp tối thiểu chạy được trên Linux.
3. Thêm tối ưu thông số cơ bản.
4. Commit + push mỗi bước có số liệu.
5. Cập nhật file này sau mỗi tiến bộ.

**Automation**: Đã tạo "Brain2 continuous improvement" — chạy hàng ngày 09:00 Asia/Ho_Chi_Minh. Đã kích hoạt chạy ngay.
