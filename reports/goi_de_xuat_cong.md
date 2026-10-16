# Gói việc: đề xuất cổng kiểm định (16/10/2026) — phiên [DOC], nhánh `de-xuat-cong-kiem-dinh`

## Đã làm gì
Tạo `de_xuat/` (README, 4 tài liệu, mẫu phản hồi cho Grok, `ma_mau/` 3 file). Không sửa file nào trong `nhan/`, `tru/`, `config/`, `v*.py`.
Thêm 1 dòng (mục 11) vào `START_HERE.md` trỏ tới `de_xuat/README.md`.

## Bằng chứng
- Đọc code: `v30.py:159`, `v31_moc.py:104,193`, `v32_luoi_moc.py:84,145`, `nhan/cong.py:47,98,108,361,460`, `v24.py:68`.
- Đọc số: `reports/vong30.json` (29 ô kiểm GĐ2, p nhỏ nhất 0,108, n trung vị 191), `reports/vong31_moc.json` (21 ô, p nhỏ nhất 0,241, n trung vị 239).
- `python -m pytest de_xuat/ma_mau -q` → 7 passed.
- `python de_xuat/ma_mau/mo_phong_dac_tinh.py` (seed cố định) → `de_xuat/ma_mau/ket_qua_mo_phong.md`.

## Số trước / sau
Không có số "sau": chưa đổi cổng nào. Trước (mô phỏng tổng hợp, giả định ICC): t-test từng lệnh nhận nhầm 13,1 % ở mức 5 % khi ICC = 0,3, gom cụm 4,9 %.
Ở n = 1.500, cạnh 10 bps: Holm k = 20 bắt 8,04/10 ô thật; Holm m = 20.503 bắt 2,21/10.

## Rủi ro còn lại
ICC và sd thật chưa đo (T1); đo tổng hợp giả định GĐ1/GĐ2 độc lập và cạnh không phân rã (power thật thấp hơn); chưa có bằng chứng cổng mới tìm ra cạnh thật.

## Việc chưa làm
T0–T8 trong `de_xuat/03_KE_HOACH_THU.md` (Grok / chủ dự án); gộp nhánh vào `main`; cập nhật `CLAUDE.md`/`README.md`/`KIEN_TRUC.md` (nằm ngoài gói này).
