# BÀN GIAO máy nhà — 05/11/2026 16:30 (UTC+7)

Phiên Grok Bot sắp hết token → dừng nhận việc mới. Phiên sau đọc file này trước.

## 1. Trạng thái đo lúc 16:20 (UTC+7)
- CPU 14%, RAM trống 12,1/31,9 GB. Ổ trống: C 35,8 GB · D 19,9 GB · E 103,4 GB.
- WARP: Connected, network healthy.
- Orch PID 17160 SỐNG: `python may_nha\tho_mt5.py --song-song --tran 5` (cwd D:\brain2_tho).
- Worker g1–g5 sống (PID 9136/6096/1080/10640/4616), mỗi worker: `tho_mt5.py --slot E:\brain2_grok\mt5_slots\gN --may desktop-05pnlgf_gN --cho-toi-da 14400`.
- terminal64 = 4, metatester64 = 4 (đang chạy ở g1, g4, g5 + 1).
- Hàng đợi: can_test 103 (v2* 32, cs/cb* 36, khác/vòng1 35) · da_test 71 · dang_lam 5:
  - g1: v2cd_adxngang_ghepe9b41c33d4deee54_H4 (nhận 15:55)
  - g2: v2cd_adxngang_ghep60ff9350c26c63ee_H1 (15:51)
  - g3: v2cd_adxngang_skea154c9fdee7_H4 (16:17)
  - g4: v2cd_adxngang_mql5344ed0d8ab12c7f0_H1 (15:58)
  - g5: v2cd_adxngang_mql5e52afb999eca4bd1_H1 (16:01)
- KHÔNG kill: để orch/worker chạy nốt. Nếu job dang_lam treo > --cho-toi-da (4h) thì trả file từ `hang_doi/dang_lam_desktop-05pnlgf_gN/` về `hang_doi/can_test/`.

## 2. Cách vận hành
```
cd D:\brain2_tho
set PYTHONUTF8=1
set BRAIN_SLOTS=E:\brain2_grok\mt5_slots\g1;...;g12;E:\mt5_tester\p5   (danh sách slot)
set BRAIN_RAM_TRONG_MIN_GB=6
python may_nha\tho_mt5.py --song-song --tran 5
```
- Slot: `E:\brain2_grok\mt5_slots\g1..g12` + `E:\mt5_tester\p5`. Bases dùng chung: `E:\brain2_grok\shared_bases` (junction `<slot>\Tester\Bases`).
- RAM gate: chờ 180s nếu RAM trống < ngưỡng; luôn giữ ≥ 6 GB trống.
- Không kill XM terminal chính (tài khoản thật/demo chính) và tiến trình claude.
- Dung lượng: ghi E trước, rồi D, cuối cùng C.
- Không đọc E:\api.txt; không commit secret.
- File KHÔNG commit: config/ma_nguon_con_tro.json, config/ngan_sach_nhip.json, nhat_ky/kho_co_che_ghi.log, reports/EVO_SUC_KHOE.md, reports/VONG_DAY_DU.json.
- Git: không autostash/rebase/force/reset --hard; worker tự commit hang_doi.

## 3. Bases từng slot
| Slot | Bases |
|---|---|
| g1–g5 | REAL (đang test; g1 còn REAL — đổi junction khi rảnh) |
| g6–g12 | junction → shared_bases |
| E:\mt5_tester\p5 | junction → shared_bases |
| p3, p4, p6 | chưa có Bases |
Cách đổi khi slot rảnh (không có metatester của slot): xoá/đổi tên `Tester\Bases` REAL → `mklink /J <slot>\Tester\Bases E:\brain2_grok\shared_bases`.

## 4. Ưu tiên hàng đợi
vòng 2 (v2qd/v2cd) → cs/cb (portfolio/ghép) → vòng 1.

## 5. ĐẠT hôm nay 05/11 (da_test, DD<80% & CAGR>10%)
| Job | k | CAGR %/năm | DD % |
|---|---|---|---|
| v2qd_gian13_ghepe9b41c33d4deee54_H4 | 10 | 374,00 | 36,40 |
| v2qd_trailatr_ghep60ff9350c26c63ee_H1 | 10 | 232,35 | 39,57 |
| v2qd_gian13_mql5e52afb999eca4bd1_H1 | 10 | 130,68 | 42,53 |
| v2qd_catlo40_ghepe9b41c33d4deee54_H4 | 1 | 122,48 | 35,97 |
| v2qd_trailatr_mql5e52afb999eca4bd1_H1 | 10 | 99,55 | 67,17 |
| v2qd_trailatr_ghep0bf2c31fbfc9dea0_H4 | 1 | 73,62 | 41,23 |
| v2qd_catlo40_ghep60ff9350c26c63ee_H1 | 1 | 64,40 | 20,23 |
| v2qd_trailatr_2600ea39abbd7b0f_H1 | 3 | 51,81 | 60,97 |
| v2qd_trailatr_b0be91a35f43f34a_H4 | 1 | 41,42 | 67,05 |
| v2qd_trailatr_skea154c9fdee7_H4 | 1 | 40,76 | 50,57 |
| v2cd_adxngang_2600ea39abbd7b0f_H1 | 3 | 38,04 | 39,37 |
| v2cd_adxngang_b0be91a35f43f34a_H4 | 1 | 33,48 | 67,15 |
| v2qd_gian13_mql5344ed0d8ab12c7f0_H1 | 2 | 25,67 | 54,48 |
| v2qd_catlo40_ghep0bf2c31fbfc9dea0_H4 | 1 | 22,32 | 74,80 |
| v2qd_catlo40_skea154c9fdee7_H4 | 1 | 16,42 | 53,39 |
| v2qd_trailatr_mql5344ed0d8ab12c7f0_H1 | 1 | 13,53 | 54,88 |
| v2qd_catlo40_mql5344ed0d8ab12c7f0_H1 | 1 | 12,28 | 44,01 |
TRƯỢT: v2cd_adxngang_ghep0bf2…_H4, v2qd_trailatr_ghepe9b4…_H4. CHƯA ĐO ĐƯỢC: v2qd_gian13_skea154c9fdee7_H4. PF chi tiết: xem `hang_doi/bao_cao/*.htm`.

## 6. Vấn đề còn mở
- Map mã GBPCADmicro → GBPCAD# chưa xử lý xong.
- Log Agent MT5 trong slot phình nhiều GB → dọn định kỳ.
- Usage Grok Bot gần full.
- Routine canh máy nhà 30′ đang PAUSE.
- Working tree máy nhà còn file chưa commit do worker (hang_doi/bao_cao, ket_qua_csv, 3 da_test sửa) — worker sẽ tự commit.

## 7. Việc phiên sau
1. Resume routine canh (hoặc giãn 60′).
2. Chạy nốt queue: vòng 2 → cs → vòng 1.
3. Ghép portfolio từ các hệ ĐẠT.
4. Lọc ADX/regime/news.
5. Đưa CSV kết quả về repo.
6. Lấy dữ liệu M1 2008–2023 để test out-of-sample.
7. Đổi Bases g1–g5 sang junction khi slot rảnh.
## 8. Báo cáo PDF hệ đạt vòng 2 (05/11)
- `reports/VONG_2_HE_DAT_2026-11-05.pdf` (+ nguồn `.md`): 34 hệ, PF/lệnh/giữ TB-max/max mở, nhóm đáng xem & cần nghi. In-sample; thời gian giữ không thực tế.
