# Đối chiếu kết quả phiên kia (22/10–02/11) với main hiện tại

Lúc đo: 03/11/2026 ~08:45 (UTC+7). Main lúc đo: `b02b8942`. Chỉ ghi số đã đo; chỗ không đo được ghi CHƯA ĐO ĐƯỢC.
Tiêu chí ĐẠT (main, `fc595770`): max DD < 80% VÀ CAGR > 10%/năm; kết quả trước mốc vá lot 31/10 01:53 (UTC+7) = BI_THAY_THE.

## 1. Các nhánh chưa gộp

Không nhánh nào đã gộp vào main. Phiên kia chỉ đưa lên main `214cf760` (bàn giao EVOLUTION + `reports/kiem_toan_he_dat.md`), commit này ĐÃ có trong main.
Cột "trước/sau" = số commit nhánh có mà main không có / main có mà nhánh không có. `git cherry`: không commit nào của các nhánh đã được áp lại vào main dưới dạng khác.

| Nhánh | Nhánh có thêm | Main có thêm | Nội dung | Xung đột khi gộp thử (`git merge-tree`) |
|---|---|---|---|---|
| evo/llm-file-queue | 2 | 14 | hàng chờ LLM bằng file (`nhan/hang_cho_llm.py`), `hoi_json` ép JSON | `.gitignore` |
| evo/pass-audit-nghi-gon | 4 | 14 | + PASS audit mềm/cứng, rút gọn prompt NGHI, `bao_van_de` | `.gitignore` |
| evo/mt5-kha-dung-seeker | 5 | 14 | + `nhan/mt5_kha_dung.py`: box không có MT5 thì SEEKER không dồn việc | `.gitignore` |
| evo/phien-khe-artifact-va-guard | 6 | 14 | + cổng chặn thu hoạch khe đảo ngày, tắt cảnh báo FDR | `.gitignore` |
| evo/sua-hash-va-hang-cho | 7 | 14 | + cô lập `plan_hash` trong quantlab, NGHI tiêu thụ theo loại | `.gitignore` |
| evo/perf-quickwins | 4 | 14 | tăng tốc poll MT5, chu kỳ EVO/CAUKHO, index `so` | không |
| fix/r1-cpu-seeker-moi-quantlab-gates | 8 | 14 | 5 commit chung + watchdog/worker máy nhà + **sổ cái MT5 386 lần** | `.gitignore`; **nguy hiểm**: nhánh viết đè `reports/mt5_lien_tuc/so_cai.jsonl` 955 dòng → 386 dòng (gộp sẽ xoá 955 dòng của main mà không báo xung đột) |
| seeker/tin-hieu-cong-khai | 8 | 14 | dịch ngược tín hiệu công khai (FXBlue/MQL5/Myfxbook, Playwright), **sửa DCA pip theo mã**, `dca_rerun_sanity.json` | `.gitignore` |
| vong2/kiem-sau | 9 | 14 | `tools/vong2.py`/`vong3`/`vong4`, học từ sổ cái, **vá lot CSV (`scale_lot_for_hash_demo`, cờ `lot_csv_nghi_ngo`)** | `.gitignore` |

Hai nhánh cũ hơn (`claude/*`, `de-xuat-cong-kiem-dinh`) có từ 09–10/2026, ngoài phạm vi phiên kia.

Kiểm thử (chỉ chạy các tệp test mà nhánh thêm/sửa, trên box):
- vong2/kiem-sau: 89 đạt, 20 hỏng (phần lớn `test_khe_dao_ngay.py`).
- evo/sua-hash-va-hang-cho: 86 đạt, 15 hỏng (`test_khe_dao_ngay.py`).
- seeker/tin-hieu-cong-khai: 16 đạt, 1 hỏng (`test_hang_cho_llm.py::test_tri_tue_hoi_hang_cho`, lỗi sqlite).
- Lỗi do môi trường box hay do code: CHƯA ĐO ĐƯỢC.

## 2. Sổ cái MT5 386 lần (nhánh fix/r1…)

- Lúc chạy: 30/10 20:19 → 31/10 18:43 (UTC+7); 4 dòng không có giờ. `tong_ket_mt5.json` của nhánh: 386 lần thử, 0 IS, 0 OOS, 0 đạt cốt lõi.
- **Không dòng nào có trong sổ chung main** (0/386 trùng id; 0/386 trùng (tệp, giờ) với `so_cai.jsonl` 955 dòng của main; 242/386 tệp báo cáo chưa từng xuất hiện trong sổ).
- 251/386 dòng mang cờ `lot_csv_nghi_ngo` (EA đọc cột lot trong CSV thay cho InpLot0, trước bản vá). Main không có trường này ở dòng nào.
- Xét theo tiêu chí mới (đã nhập vào `TRI_NHO/so_ket_qua/ket_qua.csv`, 384 dòng mới, 2 dòng trùng bị khử):
  - BI_THAY_THE (trước 01:53): 246
  - CHUA_DO (thiếu số, lỗi, hoặc `lot_csv_nghi_ngo` sau mốc): 96
  - KHONG_DAT: 41 (cả 41 do CAGR ≤ 10%; không dòng nào có DD ≥ 80%)
  - **DAT: 1** — `od_v2verify_lot01_oos_h1_ghep0bf2c31fbfc9dea0` GBPCAD# H4, 02/01–01/07/2024 (0,496 năm), 100% real tick, net +678,59/10 000, CAGR 14,15%, DD 9,13%, 36 lệnh. Cửa sổ chỉ nửa năm; theo kiểm toán, CSV tín hiệu phủ đúng kỳ test nên đây không phải OOS sạch.
  - Trước mốc vá mà về số thì đạt: 1 (`od_mql5e52afb999eca4bd1` EURGBP#, CAGR 26,28%, DD 19,24%, 111 lệnh) → không tính.
- 144 tệp đã có trong sổ (từ lần chạy cũ 19–20/10); 20 trong số đó cho net khác hẳn (VD `od_skea44640140cc`: 10 075,87 lúc 19/10 → 0,0 lúc 30/10), đúng với lỗi lot ~100× ở bản cũ.

## 3. Lệch giữa báo cáo phiên kia và main

1. **Bản vá lot CSV chỉ có trên nhánh `vong2/kiem-sau` (commit `47430f3d`, 31/10 02:56)**, main KHÔNG có (`git grep lot_csv_nghi_ngo|force_scale` trên main: 0 kết quả; `mt5tools/sinh_viec.py` main không có `scale_lot_for_hash_demo`). Trong khi đó `TRI_NHO/TRANG_THAI.md` ghi "đã vá 31/10 01:53 (máy nhà, ngoài git)". Nếu máy nhà chạy việc MT5 VAO_CSV từ code main thì lỗi lot có thể quay lại; máy nhà đang chạy code nào: CHƯA ĐO ĐƯỢC.
2. **Sửa DCA pip theo mã** chỉ có trên `seeker/tin-hieu-cong-khai` (`41052c33`); main chưa có. Kết quả DCA trong main chưa qua bản sửa này.
3. **`plan_hash`**: main dùng `plan_hash` ở nhiều chỗ, nhưng bản cô lập trong quantlab (`56198f8f`) chỉ có trên `evo/sua-hash-va-hang-cho`.
4. **VONG2_KIEM_SAU.md (nhánh vong2)**: 40 "ứng viên PASS" (APY 39–617%/năm) đều đo lúc 30/10 22:22, trước mốc vá → theo main là BI_THAY_THE; không cái nào giữ được.
5. **Kiểm toán 5 hệ (`reports/kiem_toan_he_dat.md`, đã ở main) và sổ chung có chỗ mâu thuẫn:**

| Hệ | Số đo | Kiểm toán phiên kia | Sổ main hiện tại | Theo tiêu chí mới |
|---|---|---|---|---|
| skea61c CADJPY H4 lot×4 | CAGR 13,3%, DD 10,74%, 100% tick, 31/10 13:56 | hạ xuống ứng viên (cửa sổ = phủ CSV, IS) | DAT | ĐẠT về số; chưa có OOS sạch |
| brainxlmrz GBPUSD H4 (salvage) | CAGR 13,31%, DD 78,81%, 25% tick | hạ xuống ứng viên | DAT | ĐẠT về số nhưng DD sát trần, tick thấp |
| sk_ea_3279057100 EURGBP H1 | CAGR 12,2%, DD 14,8%, 31/10 16:37:51 | chưa giải mã điểm vào | CHUA_DO (thiếu giờ chạy) | **lật sang ĐẠT** nếu điền giờ 16:37:51 (sau mốc) |
| ghep_0bf2 GBPCAD H4 lot01 | CAGR 10,27–10,3%, DD 14,89%, 31/10 02:05:23 | hạ xuống ứng viên | CHUA_DO (thiếu giờ chạy) | **lật sang ĐẠT** (sát sàn 10%) nếu điền giờ |
| mql5344 NZDUSD H1 | CAGR 3,52% (dài) / 8,5% (×4 ngắn) | sai toán %/năm (từng báo ~12%) | CHUA_DO | KHÔNG ĐẠT |

Tiêu chí mới bỏ các cổng OOS/FDR/tick, nên 2 hệ đang CHUA_DO có thể lật sang ĐẠT chỉ vì thiếu giờ chạy. Tôi chưa sửa hai dòng này, cần anh quyết.

## 4. Đã làm
- Nhập 384 dòng sổ cái 386 lần vào `TRI_NHO/so_ket_qua/ket_qua.csv`, `tep_goc` = `origin/fix/r1-cpu-seeker-moi-quantlab-gates:reports/mt5_lien_tuc/so_cai.jsonl#<tệp>`, `commit` = `243ad95a`, ghi chú "nhap tu nhanh chua gop (phien kia)" và cờ `lot_csv_nghi_ngo` nếu có. Đã tạo lại `TONG_HOP.md`.
- Không gộp nhánh nào.

## 5. Đề xuất gộp
- Nên gộp sớm (sau khi xử lý `.gitignore`): phần mt5tools của `vong2/kiem-sau` (vá lot CSV), sửa DCA pip của `seeker/tin-hieu-cong-khai`, `evo/sua-hash-va-hang-cho` (đã chứa llm-file-queue, pass-audit, mt5-kha-dung, phien-khe). `evo/perf-quickwins` gộp được ngay, không có xung đột.
- KHÔNG gộp nguyên `fix/r1-…`, vì sẽ thay sổ cái 955 dòng bằng 386 dòng. Nếu cần thì chỉ lấy `ops/` và `tru/` bằng cherry-pick, còn sổ cái thì nối thêm vào (đã có trong sổ chung).
- Chạy lại các test `test_khe_dao_ngay.py` đang hỏng trên nhánh trước khi gộp.
