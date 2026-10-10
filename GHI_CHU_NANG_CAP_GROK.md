# Ghi chú nâng cấp (Grok trên brain2) — 2026-10-10

## Cập nhật 10/10/2026 — Nâng tỷ lệ bóc tách

**Đo được bằng `mau_thu/do_moc.py`:**
- Trước: 3 / 22 = **13.6%**
- Sau cải tiến trong `nhan/doc_ma.py`: 6 / 22 = **27.3%**

### Cải tiến đã làm
- Tiền xử lý `&&` → `and`, `Tradesinfo.xxx` → `xxx`
- Special-case cho pattern midpoint `lowrange+((highrange-lowrange)/2)` → `midrange`
- Hỗ trợ so sánh có biểu thức số học đơn giản (thử parse bằng `_tuyen_tinh`)
- Vòng lặp `vong_thu_nghiem.py` chạy được 6 cơ chế trên dữ liệu giả lập

### Còn lại
- Boolean state flags (`initup`, `!initup`)
- Một số `true` từ guard phụ
- Biểu thức phức tạp hơn và hàm gọi khác

**Mục tiêu tiếp:** hoàn thiện vòng lặp quét → bóc tách → mô phỏng Python → tối ưu thông số cơ bản, và nâng tiếp tỷ lệ.
