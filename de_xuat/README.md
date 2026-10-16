# de_xuat/ — Đề xuất về tiêu chí và thuật toán tìm phương pháp giao dịch tốt

**Trạng thái: ĐỀ XUẤT. Chưa duyệt. Chưa đổi cổng nào. Chưa module nào trong `nhan/`, `tru/`, `config/` bị sửa.**
Soạn bởi Claude (phiên cloud 16/10/2026), theo yêu cầu chủ dự án — chủ dự án muốn Grok đọc, phản biện và (nếu đồng ý) làm các việc "chế độ bóng".

## Đọc theo thứ tự (khoảng 15 phút)

| File | Nội dung | Ai cần đọc |
|---|---|---|
| `01_CHAN_DOAN.md` | Cổng v19–v32 sai ở đâu: hai bộ tiêu chí mâu thuẫn, m quá lớn, p quá lỏng, thiếu sức phát hiện. Có số | Grok |
| `02_TIEU_CHI_VA_PHEU.md` | "Tốt" theo tiền nghĩa là gì; phễu 6 tầng; công thức từng thuật toán | Grok |
| `03_KE_HOACH_THU.md` | Việc T0–T8 ở **chế độ bóng**, tiền đăng ký, tiêu chí chuyển bóng → chính, rủi ro | Grok |
| `04_CAU_HOI_CHU_DU_AN.md` | Cái chỉ chủ dự án quyết (V, C, π, mức DD, kiểu thua, forward demo, ngân sách) | Chủ dự án |
| `PHAN_HOI_GROK.md` | Mẫu để Grok ghi đồng ý / phản biện / kết quả | Grok điền |
| `ma_mau/` | Mã mẫu 7 test + bài đo tổng hợp (không nằm trong đường ống) | Grok chạy |

## Tóm tắt 6 dòng

1. Hai bộ cổng cùng tồn tại: `nhan/cong.py` (p/FDR là **nhãn**, đã có LORD, ngưỡng suy từ kinh tế) và các vòng `v19–v32` (**Holm cộng dồn 20.503** làm cổng cứng, không gọi `cong.py`).
2. Holm đang chia cho **mọi ô đã sàng**, trong khi sau sàng GĐ1 chỉ ≤ 20 ứng viên được kiểm trên GĐ2 → quá chặt.
3. `ttest_1samp` trên từng lệnh coi lệnh độc lập → quá lỏng khi lệnh cùng cụm (ICC 0,3 → nhận nhầm 13,1 % ở mức danh nghĩa 5 %; MÔ PHỎNG).
4. Với ~190–240 lệnh GĐ2 mỗi ô (số thật v30/v31), cạnh nhỏ hơn ~13–37 bps không thể thấy dù hiệu chỉnh kiểu nào → "0 qua" không nói được "không có cạnh". Cỡ mẫu quan trọng hơn cách hiệu chỉnh.
5. Kết luận "0 sống" của v30–v31 **vẫn đúng**: p GĐ2 thô nhỏ nhất 0,108 và 0,241; không ô nào đạt 0,05 kể cả chưa hiệu chỉnh.
6. Đề xuất: định nghĩa "tốt" = cận dưới tăng trưởng log cùng rủi ro; phễu 6 tầng có forward demo làm trọng tài (demo rẻ → các tầng trước nới FDR); kiểm bằng p gom cụm + hiệu chỉnh theo k + null cấp họ + MDE kèm kết luận âm.

## Luật cho Grok khi làm việc với thư mục này

- **Chưa được làm:** đổi quyết định QUA/KHÔNG của bất kỳ vòng nào; sửa `config/*.json` (kể cả `nguong.json`); sửa `nhan/cong.py`; import `ma_mau/*` vào đường ống;
  tái dùng GĐ2 của v30–v32 để xác nhận sau khi đã dùng chẩn đoán (T5); điền số vào `04_CAU_HOI_CHU_DU_AN.md` thay chủ dự án.
- **Được làm (chế độ bóng, chỉ thêm số đo):** T0–T7 trong `03_KE_HOACH_THU.md`. Không dùng MT5 tester, không ghi `nao.db`, không đổi cột `Qua?`.
- Ghi nhãn **MÔ PHỎNG** cho mọi số mô phỏng; số chưa đo ghi **CHƯA ĐO ĐƯỢC**, không ghi ÂM. Tiền đăng ký trước khi chạm dữ liệu chưa nhìn.
- Nếu không đồng ý điểm nào: ghi vào `PHAN_HOI_GROK.md` kèm số đo, đừng sửa `01`–`04` cho khớp.
- Không đưa khóa/token/mật khẩu vào git (luật chung).

## Những gì đã kiểm và chưa kiểm

| Đã kiểm | Cách |
|---|---|
| Trích dẫn dòng code, p GĐ2 nhỏ nhất, số lệnh GĐ2 của v30/v31 | đọc `v30.py`, `v31_moc.py`, `v32_luoi_moc.py`, `nhan/cong.py`, `reports/vong30.json`, `reports/vong31_moc.json` |
| Mã mẫu đúng như tài liệu | `python -m pytest de_xuat/ma_mau -q` → 7 passed (16/10/2026) |
| Bảng A/B trong `01` | `python de_xuat/ma_mau/mo_phong_dac_tinh.py`, ~11 giây, seed cố định |

| **Chưa** kiểm | Ghi chú |
|---|---|
| ICC, sd thật của lệnh v30–v32 | việc T1; số trong `01` dùng giả định ICC ∈ {0; 0,1; 0,3}, sd = 100 bps |
| Bất kỳ số nào trên MT5 hoặc dữ liệu giá | cloud không có `data/`, `nao.db`, MT5 |
| Rằng cổng mới tìm ra cạnh thật | đề xuất làm cổng trung thực hơn, không hứa có cạnh |
| `reports/vong32.json` | không có file này; v32 không đăng ký ô nào (0 ô kiểm GĐ2) |

## Cách đưa vào `main`

Thư mục này hiện nằm ở nhánh `de-xuat-cong-kiem-dinh`, **chưa ở `main`**. Chủ dự án quyết định gộp (hoặc bảo Claude gộp).
Sau khi gộp, `START_HERE.md` mục 11 trỏ tới file này.
