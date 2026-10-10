# Ghi chú nâng cấp (Grok trên brain2) — 2026-10-10

## Trạng thái hiện tại
- **Tỷ lệ bóc tách**: 3/22 = **13.6%** (đã khôi phục sau khi commit 394266a6 làm hỏng file thành PLACEHOLDER)
- Vòng lặp tối thiểu `vong_thu_nghiem.py` chạy được 3 cơ chế trên dữ liệu giả lập.

## Việc đã làm
- Patch bắt biến trung gian, tiền xử lý MQL5 cơ bản, fallback identifier.
- Tạo vòng thí nghiệm quét → bóc tách → mô phỏng Python.
- Khôi phục file bị hỏng.

## Mục tiêu
Vòng lặp liên tục: quét đầu vào → bóc tách cơ chế → kiểm định (Python) → tối ưu thông số → giữ lại cái hay.

## Ưu tiên tiếp
1. Nâng tỷ lệ bóc tách lên ≥40% (xử lý &&, Tradesinfo, biểu thức phức tạp hơn) — làm cẩn thận, kiểm tra ngay sau mỗi thay đổi.
2. Thêm tối ưu thông số cơ bản vào vòng lặp.
3. Commit chỉ khi test pass.
