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
