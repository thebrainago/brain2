# TRẠNG THÁI SP500 — cập nhật 27/11/2026 19:25 (giờ Việt Nam)

## Đang chạy
- **Không có gì đang chạy.** Mọi terminal và tester do việc SP500 mở trên máy nhà đều đã tự tắt hoặc đã dừng theo đúng PID. Terminal XM chính (`C:\Program Files\XM Global MT5`) không bị đụng.
- Routine của bot vẫn tạm dừng (từ t335).

## Đã xong
- Mô-đun `sp500/` gồm mã, EA, kết quả và báo cáo `BAO_CAO_2026-11-27.md`.
- Lưới Python 4.950 biến thể, walk-forward và bộ ghép.
- MT5: 48 bộ BatDay chạy tick thật; 25 test Lịch/IBS (model 2 cho 10 năm, model 4 cho tick thật).
- Đã kéo ESZ6 bằng Fxaurum (chỉ RPC đọc).

## Ứng viên hiện tại
- **IBS < 0,1, SMA200, giữ 3 ngày, mua 15:50 NY** (`ea/SP500_Lich.mq5`, CheDo=4). Trên MT5, đòn bẩy 5: 17,6 %/năm, DD 40,8 % (DD tính theo số dư khi đóng lệnh), 133 lệnh, 2017–2026.

## Tệp và đường dẫn trên máy nhà
- Thư mục làm việc: `C:\Users\DUNG\sp500_2711\`. Chứa chuỗi test `chuoi4\chuoi4.ps1` (mẫu có chặn RAM), các CSV kết quả, và `esz6\*.json` (dữ liệu Fxaurum).
- EA đã biên dịch: `E:\mt5_tester\p6\MQL5\Experts\sp500\` và `E:\mt5_tester\p3\MQL5\Experts\sp500\`.
- Tệp `.set`/`.ini` ở `E:\mt5_tester\p6\` (tên `sp500_*.ini`).

## Cách tiếp tục
1. Box: đọc `README.md`, chạy `ma/du_lieu.py` trước nếu thư mục tạm bị mất.
2. MT5: chỉ dùng **p6**. Không chạy song song với p3, p5, g2… vì các slot này dùng chung Bases. Phối hợp với việc vàng (p3, p4) qua `vang/`.
3. Chạy một test: chép mẫu `.ini` trong `E:\mt5_tester\p6\`, khởi động bằng `terminal64.exe /portable /config:<ini>` rồi chờ terminal tự tắt. CSV giao dịch nằm ở `%APPDATA%\MetaQuotes\Terminal\Common\Files\sp500_*.csv`. Chuyển CSV đi, tổng hợp bằng `ma/tong_mt5.py`.
4. Không dùng Optimization với model 1 trên 10 năm, vì agent ăn tới 22 GB RAM.

## Đo MT5 hai hệ walk-forward (worker WF, 27/11/2026 19:55 giờ Việt Nam)
- Chi tiết: `ket_qua/MT5_WF_2711.md`. **Số TẠM** trên `US500Cash#` Ultra Low 345930355 (chưa có slot micro `US500Cash`).
- swing_rsi2_L5 (lịch WF) 2020-01→2026-11, model 1 phút OHLC: CAGR 15,5%, DD 56,2%, 69 lệnh → đạt tạm; spread 0,80: 15,3%/56,2%. Model giá mở: 17,8%/57,1%.
- bat_day_chi_none_L10: −26,8%/88,7% → trượt (tick thật 2025-07→: −31,1%).
- **Phát hiện lỗi giờ:** `ma/du_lieu.py` coi dữ liệu M5 (thực là UTC) là EST ⇒ phiên Python lệch 5 giờ; số Python trong ngày cần chạy lại (`ma/du_lieu_utc.py`).
- Lưu ý: slot dùng chung Bases (`E:\brain2_grok\shared_bases`); chạy song song với p6 vẫn ra kết quả nhưng hay lỗi agent/timeout lần đầu (script tự chạy lại 1 lần). Model 1 phút từ 2016/2017 làm agent ăn 9–21 GB RAM → đã dừng theo PID; dùng model 2 cho 10 năm.
- Không có gì của worker WF đang chạy.

## Cập nhật 27/11/2026 19:55 (giờ Việt Nam)
- **Hướng mới (t345u):** dừng lưới truyền thống. (A) tín hiệu từ dữ liệu Fxaurum (orderflow dựng lại từ tick, big trade, volume profile, mức quyền chọn). (B) ghép với hệ xử lý lệnh của phiên 26/11 tối (xem `HE_XU_LY_LENH.md`).
- Đo xong trên MT5 p6: TOM n3 đã sửa lịch NYSE (model 2, 2017–2026, L5): lãi +1.516,61 USD/10.000, 112 lệnh, DD vốn thả nổi 65,9 %. IBS (model 2, L5): +43.974,69 USD, 134 lệnh, DD thả nổi 52,7 %. IBS tick thật 21/07/2025–26/11/2026: L3 +36,3 % DD 11,4 %; L5 +63,7 % DD 18,8 %; L8 +106,5 % DD 29,3 %.
- Model 1 (M1) mỗi test 2 năm ăn ~20 GB RAM (26 → 5,3 GB) nên đã bỏ; DD thả nổi theo từng 2 năm tính lại bằng nến M5 XM: `ket_qua/ibs_dd_noi_m5_xm.json`.
- Đối chiếu MT5–Python trên cùng dữ liệu XM: `ma/doi_chieu_xm.py`, `ket_qua/doi_chieu_xm_mt5.json`.
- Lưới DCA/lưới/gỡ lệnh 10.236 biến thể: `ma/luoi_dca.py`, `ket_qua/loc_lai_tieu_chi_moi.json`. EA `ea/SP500_Dca.mq5`. Chuỗi tick `C:\Users\DUNG\sp500_2711\chuoi7\` (chờ slot trống).
- 21:00 27/11: PHẦN 1 cho XAU + SP500 xong vòng đầu: `P1_QUY_TAC_DATA.md` (bảng xếp hạng quy tắc, luật ưu tiên khi bất đồng). HYB+AG chạy lại khớp (+1.501,90 / maxDD 575,97 / 11/11). Cắm orderflow ESZ6 vào S/vp: chưa vượt baseline (59 phiên).
- 21:00 27/11: luật ưu tiên (big30>delta15>mức) trong HYB+AG: US500 mọi biến thể kém gốc (−71 đến −501); XAU chỉ cộng mua +309,5 nhưng p 0,09, DSR 0,36 → chưa đạt. Giữ 1–5′ âm sau phí cả 2 mã. Nhật ký bóng chạy trên máy nhà, PID 16676. Xem `UU_TIEN_HYB_SCALP.md`.
- 21:30 27/11: tín hiệu dữ liệu làm lọc ngữ cảnh (`LOC_NGU_CANH_DANH_MUC.md`): hệ số lot trong HYB+AG US500 làm xấu (−452 đến −654, p 0,98); tay_v2 US500 ×1,5/×0,5 +920,39 / DD 1,81% (gốc +657,83) — ứng viên. Lệnh phụ 60′ US500 union +697,02 / DD 1,49% (p 0,00, DSR 0,58). Danh mục HYB US500 + tay US500: +2.159,72 / DD 4,73%, stress 11/11 (chặn trên). Bóng PID 16676 chạy: ES cvd_pk 14 phút, delta15 1; GC cvd_pk 6.
