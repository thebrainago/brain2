# Banker · Tổng hợp báo cáo tổ chức

Chuyên mục con của vai **Banker** (xem `roles/BANKER.md`): thu thập và tổng hợp các báo cáo triển vọng thị trường của các tổ chức lớn, rồi rút ra dự báo và hướng hành động.

## 4 nguyên tắc
1. **Chỉ nguồn uy tín, chất lượng cao**: lấy PDF gốc từ trang chính thức của tổ chức, không dùng bản đăng lại hay ảnh chụp. Danh sách nguồn ở `NGUON.md`.
2. **Trích dữ kiện chính xác**: mỗi con số đều ghi nguồn (tổ chức, tên báo cáo) và ngày phát hành hoặc ngày chốt số liệu.
3. **Đối chiếu nhiều dự báo một cách có chọn lọc**: tách phần các tổ chức đồng thuận, phần còn khác nhau, và mức độ tin cậy; luôn ghi ngày chốt số liệu (cut-off) của từng báo cáo.
4. **Rút ra dự báo và hướng hành động** theo 3 khung: ngắn hạn (0–3 tháng), trung hạn (6–12 tháng), dài hạn (2 năm trở lên). **Tách rõ** dữ kiện lấy từ báo cáo và phần suy luận của mình.

## Cấu trúc
- `NGUON.md` — danh sách nguồn tier-1 và các kênh dùng để phát hiện báo cáo mới.
- `bao_cao/<ky>/` — file .txt trích từ PDF gốc, kèm `nguon.json` (URL, ngày).
- `TONG_HOP_<YYYY-MM>.md` — bản tổng hợp của từng kỳ.
- `tai_bao_cao.py` — tải PDF, trích văn bản bằng pdftotext, ghi vào `bao_cao/<ky>/` và cập nhật `nguon.json`.
  - Ví dụ: `python banker_bao_cao/tai_bao_cao.py <url_pdf> --ky 2026-11_Q4 --to-chuc SC --ngay 2026-10-30`
  - Không commit file PDF lớn hơn ~2MB; chỉ commit file .txt và chỉ mục.
