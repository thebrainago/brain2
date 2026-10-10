# Ghi chú nâng cấp (Grok trên brain2) — 2026-10-10

## Trạng thái hiện tại
- **Tỷ lệ bóc tách**: 10/22 = **45.5%** (tăng từ 13.6% nhờ xử lý &&/||, Tradesinfo, giữ cơ chế khi có phần parse được)
- Vòng lặp `vong_thu_nghiem.py` chạy được 10 cơ chế trên dữ liệu giả lập (đã thêm placeholder tối ưu thông số).

## Việc đã làm
- Tiền xử lý MQL5: && → and, || → or, Tradesinfo.initprice/hedgeprice → close, initup → 1.
- _tach_va hỗ trợ tách cả and và or.
- Nới rule: giữ cơ chế nếu có ≥1 điều kiện DSL parse được (ghi nhận phần chưa parse vào chua_dien_dat_duoc).
- Commit 700d395a, đo lại bằng mau_thu/do_moc.py xác nhận 45.5%.

## Mục tiêu
Vòng lặp liên tục: quét đầu vào → bóc tách cơ chế → kiểm định (Python) → tối ưu thông số → giữ lại cái hay.

## Ưu tiên tiếp
1. Xử lý biểu thức phức tạp hơn (lowrange + arithmetic, function calls) để tăng thêm tỷ lệ.
2. Thêm tối ưu thông số cơ bản vào vòng lặp (grid nhỏ quanh giá trị mặc định nếu có input).
3. Commit chỉ khi test pass, luôn kèm số đo.
