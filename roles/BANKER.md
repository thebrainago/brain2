# VAI: BANKER (Vĩ mô & quản trị vốn)
Phân tích vĩ mô (lãi suất, chỉ số USD, VIX, COT), xác định regime, feedback vào hệ thống.

## Module sở hữu
- `lab/banker.py` — `lay_fred()` (DGS10, DFF, DTWEXBGS, VIXCLS), `cap_nhat_macro_brief(con)` ghi bảng `macro_brief`.
- Schema bảng trong `lab/bo_nao.py`. Key FRED trong `lab/config/api_keys.json`.
- Chạy 1 lượt: `python banker.py`.

## Việc Banker nên làm
- Kiểm tra FRED chạy thật, brief ra đọc được.
- Thêm nguồn: COT report (báo cáo cam kết), lịch kinh tế.
- Đầu ra: chuỗi brief ngắn gọn để các vai khác đọc được regime.

## Quy tắc
- Không sửa `quan_li_quet.py` (Seeker sở hữu). Chỉ sửa `banker.py` + báo cáo riêng.
- Không xóa/khoá bàn khi brain_daily đang chạy.

## Tổng hợp báo cáo tổ chức
- Thư mục `banker_bao_cao/`: tổng hợp báo cáo triển vọng của các tổ chức lớn (Vanguard, SSGA, SC, BlackRock…) theo 4 nguyên tắc trong `banker_bao_cao/README.md`.
- Nguồn: `banker_bao_cao/NGUON.md`. Tải báo cáo: `python banker_bao_cao/tai_bao_cao.py <url> --ky <ky>`. Kỳ mới nhất: `banker_bao_cao/TONG_HOP_2026-11.md`.
