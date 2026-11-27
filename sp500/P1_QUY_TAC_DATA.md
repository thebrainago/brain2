# PHẦN 1 — Đo các quy tắc dữ liệu (XAU + SP500) trên dữ liệu Fxaurum

Viết lúc 27/11/2026 ~21:00 (giờ Việt Nam, UTC+7). Chỉ ghi số đã đo. Không đặt lệnh thật, không đổi luật live.
Mã: `ma/p1_quy_tac.py` (chạy `python3 p1_quy_tac.py ES|GC`), `ma/gom_tick_gc.py` (gom tick GCZ6 trên máy nhà), `ma/keo_tick_esz6.py`.
Kết quả thô: `ket_qua/p1/quy_tac_ES.csv`, `quy_tac_GC.csv`, `xung_dot_*.csv`, `meta_*.json`.

## (a) Bộ quy tắc đang có trong repo và cách quy ra luật đo được

Nguồn: `reports/nguon_live/NGUYEN_TAC_CANH_GAMMA_BIGTRADE.md`, `NGUON_LIVE_GEX_ORDERFLOW_2026-11-11.md`, `vang/bao_cao/ORDERFLOW.md`, `GIAI_DOAN_A.md`.

| Quy tắc gốc | Luật đo ở đây | Dữ liệu |
|---|---|---|
| Gamma flip: dưới flip (gamma âm) → trend/breakout | `gamma_am_theo_nen_manh`: gamma âm + nến 1′ thân > trung vị biên độ 30′ → theo chiều nến | `sp500_sys/hyb/levels_v2.jsonl` (ES, GC), chỉ 20–26/11 |
| Put wall = hỗ trợ, call wall = kháng cự | `wall_cham_fade` (chạm rồi đóng trong → đánh ngược); `wall_pha_theo` (đóng vượt → theo) | như trên (wall đã xếp hạng S/A/B/C không có lịch sử) |
| Strike bị đánh lớn → wall hôm sau | `oi_cum_cham_bat`: chạm 3 cụm OI lớn nhất → bật ngược | như trên |
| Big trade là bộ lọc hướng; cụm ≥ ~1 triệu USD/30′ | `big30_theo` / `big30_nguoc`: tổng (mua lớn − bán lớn) 30′ vượt phân vị 95% (nửa đầu) | ES: lệnh ≥ 20 hđ (~7 triệu USD); GC: lệnh ≥ 5 hđ (~1,8–2,3 triệu USD) |
| Footprint/delta, CVD | `delta15_theo/nguoc` (delta 15′ vượt phân vị 90%); `cvd_phan_ky` (đỉnh/đáy 30′ mới mà CVD không xác nhận) | tick có chiều chủ động |
| Hấp thụ | `hap_thu`: KL > 2× trung vị, \|delta\| > 20% KL, thân ≤ 25% biên độ → ngược chiều delta | dựng lại từ tick |
| VWAP | `vwap2sd_fade/pha`, `vwap_cat_theo` | tick |
| Volume profile | `vah_val_fade`, `vah_val_pha`, `poc_cham_bat` (VA 70% của phiên TRƯỚC) | ES: RTH; GC: phiên Globex 18:00–17:00 NY |
| flowRecs Fxaurum (sweep, absorption, iceberg, stop-cascade) | `flow_*_theo/nguoc`: tổng KL có dấu trong phút vượt phân vị 90% | chỉ GC, ~18–27/11 |
| Chạm wall + big trade cùng hướng + hấp thụ | tổ hợp `A + B` (B giữ cùng chiều trong 15′) | |

Không đo được: GEX/flip/wall nhiều kỳ đáo hạn (không có lịch sử, chỉ 1 tuần snapshot), big trade **quyền chọn** LC/SC/LP/SP (không có dữ liệu quyền chọn ES; OptionsDb chỉ có COMEX.GCZ6, chủ yếu 19–20/11, chưa đọc ra OI/wall), dịch chuyển wall.

## (b) Cách đo

- Dữ liệu: ESZ6 tick có chiều (Fxaurum aggTrades, 59 phiên RTH 28/08–25/11 sau khi bỏ phiên thiếu), GCZ6 tick (9,33 triệu tick do worker vàng xuất, 71 phiên 20/08–26/11).
- Sự kiện chốt ở cuối phút futures m. Vào ở giá MỞ nến CFD XM bắt đầu m+1′, ra ở giá MỞ sau H phút (5/15/30/60′). Giá CFD thật: US500Cash M1 và GOLD.i M1 (giờ máy chủ = NY + 7h; kiểm bằng tương quan lợi suất phút 0,995–0,997). Như vậy basis đã nằm sẵn trong giá CFD. Basis trung vị: ES − US500 = 50,59; GC − GOLD.i = 25,83.
- Phí vòng tròn: US500 1,00 điểm; vàng 0,30 (spread trung vị + trượt). Kết quả theo điểm CFD/lệnh; 1 lot US500 = 1 USD/điểm, 1 lot vàng = 100 USD/điểm.
- Giãn cách 15′ giữa hai sự kiện cùng quy tắc trong phiên. Ngưỡng phân vị chỉ chỉnh trên NỬA ĐẦU số phiên.
- Đối chứng 200 lần, cùng số lệnh, giờ ngẫu nhiên trong cùng khung 30′ của ngày:
  - p ngẫu nhiên: chiều ngẫu nhiên.
  - p cùng chiều: giữ đúng chiều của tín hiệu. Phép này loại phần lãi chỉ do xu hướng chung, ví dụ vàng giảm 4.500 → 3.570.
- ĐẠT khi: TB 60′ > 0, cả hai nửa > 0, p cùng chiều < 0,05, n ≥ 20.
- Lưu ý kiểm định bội: ES 62 phép, GC 102 phép. Ở mức 0,05, chỉ do may đã kỳ vọng khoảng 3 và 5 phép "có ý nghĩa".

## (c) Bảng xếp hạng (TB 60′ = điểm CFD/lệnh sau phí)

`A + B` = A có tín hiệu, B đang giữ CÙNG chiều. `A NGUOC B` = vào theo A trong khi B đang giữ NGƯỢC chiều (đo xung đột).
`DIEM_trong_so` có trọng số khớp trên nửa 1, nên chỉ nửa 2 là ngoài mẫu.

### SP500 (ESZ6 → US500Cash): 59 phiên 20260828–20261125, phí vòng tròn 1,00 điểm, 62 phép thử (n ≥ 20); 15 phép có p < 0,05, 7 phép ĐẠT

| # | Quy tắc / tổ hợp | Nhóm | n | TB 60′ (điểm, sau phí) | Thắng % | PF | t | Nửa 1 | Nửa 2 | p ngẫu nhiên | p cùng chiều | Đạt |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | big30_theo NGUOC vah_val_fade | xung dot | 23 | 15,60 | 80,0 | 13,63 | 2,62 | 5,22 | 18,20 | 0,000 | 0,000 | ĐẠT |
| 2 | vah_val_pha | ho so KL | 168 | 3,68 | 55,2 | 1,64 | 2,04 | 4,29 | 3,31 | 0,005 | 0,000 | ĐẠT |
| 3 | cvd_phan_ky + delta15_theo | to hop | 123 | 5,23 | 52,6 | 1,76 | 1,95 | 2,32 | 6,47 | 0,000 | 0,000 | ĐẠT |
| 4 | DIEM_trong_so>=1.0 | diem uu tien | 102 | 4,49 | 54,1 | 1,70 | 1,63 | 6,21 | 3,70 | 0,020 | 0,015 | ĐẠT |
| 5 | big30_theo + cvd_phan_ky | to hop | 60 | 5,56 | 60,8 | 1,85 | 1,47 | 8,94 | 4,52 | 0,015 | 0,005 | ĐẠT |
| 6 | cvd_phan_ky NGUOC vah_val_fade | xung dot | 55 | 4,26 | 54,5 | 1,69 | 1,40 | 3,43 | 4,69 | 0,010 | 0,040 | ĐẠT |
| 7 | UU_TIEN_big>delta>muc | luat uu tien | 504 | 0,98 | 49,5 | 1,13 | 0,88 | 0,43 | 1,25 | 0,015 | 0,040 | ĐẠT |
| 8 | delta15_theo NGUOC vah_val_fade | xung dot | 46 | 9,04 | 57,8 | 3,05 | 2,51 | -2,17 | 17,23 | 0,000 | 0,000 |  |
| 9 | cvd_phan_ky NGUOC gamma_am_theo_nen_manh | xung dot | 21 | 12,80 | 61,9 | 2,20 | 1,22 |  | 12,80 | 0,010 | 0,005 |  |
| 10 | delta15_theo + vwap_cat_theo | to hop | 135 | 2,84 | 51,9 | 1,33 | 1,07 | -0,00 | 4,03 | 0,045 | 0,025 |  |
| 11 | DIEM_trong_so>=0.6 | diem uu tien | 318 | 1,49 | 50,3 | 1,20 | 1,04 | -0,09 | 2,75 | 0,025 | 0,030 |  |
| 12 | cvd_phan_ky NGUOC vwap_cat_theo | xung dot | 278 | 1,36 | 52,2 | 1,19 | 1,02 | -0,91 | 3,88 | 0,045 | 0,035 |  |
| 13 | vah_val_fade NGUOC vwap2sd_fade | xung dot | 34 | 3,45 | 58,8 | 1,58 | 0,99 | 8,47 | 0,34 | 0,140 | 0,125 |  |
| 14 | cvd_phan_ky | delta/footprint | 728 | 0,50 | 48,4 | 1,08 | 0,68 | -0,26 | 1,31 | 0,005 | 0,020 |  |
| 15 | delta15_theo | delta/footprint | 479 | 0,75 | 46,9 | 1,10 | 0,63 | -0,97 | 1,50 | 0,020 | 0,040 |  |
| 16 | hap_thu | hap thu | 71 | 1,05 | 51,5 | 1,24 | 0,63 | 2,30 | -4,23 | 0,180 | 0,245 |  |
| 17 | big30_theo NGUOC vwap_cat_theo | xung dot | 38 | 3,15 | 55,9 | 1,37 | 0,61 | 10,10 | 2,48 | 0,075 | 0,160 |  |
| 18 | big30_theo + vwap_cat_theo | to hop | 48 | 2,29 | 55,8 | 1,29 | 0,60 | -0,83 | 3,12 | 0,150 | 0,095 |  |
| 19 | UU_TIEN_muc_chi_khi_big_khong_nguoc | luat uu tien | 913 | 0,40 | 48,4 | 1,06 | 0,58 | -0,14 | 0,99 | 0,020 | 0,030 |  |
| 20 | big30_theo NGUOC delta15_theo | xung dot | 35 | 2,88 | 55,2 | 1,30 | 0,56 | -8,41 | 5,24 | 0,125 | 0,125 |  |
| 21 | cvd_phan_ky NGUOC vwap2sd_fade | xung dot | 34 | 0,93 | 58,8 | 1,18 | 0,35 | 1,16 | 0,81 | 0,315 | 0,305 |  |
| 22 | delta15_theo NGUOC vwap2sd_fade | xung dot | 175 | 0,56 | 43,8 | 1,07 | 0,31 | 0,94 | 0,41 | 0,155 | 0,275 |  |
| 23 | UU_TIEN_big+delta_cung_chieu | luat uu tien | 121 | 0,22 | 49,5 | 1,03 | 0,10 | -3,34 | 1,07 | 0,275 | 0,215 |  |
| 24 | poc_cham_bat + vwap_cat_theo | to hop | 28 | 0,23 | 42,9 | 1,04 | 0,07 | -0,45 | 1,28 | 0,370 | 0,375 |  |
| 25 | poc_cham_bat NGUOC vwap2sd_fade | xung dot | 36 | 0,13 | 52,8 | 1,03 | 0,05 | 0,68 | -0,55 | 0,480 | 0,415 |  |
| 26 | poc_cham_bat NGUOC vwap_cat_theo | xung dot | 46 | 0,20 | 44,4 | 1,02 | 0,05 | -3,51 | 3,75 | 0,345 | 0,380 |  |
| 27 | hap_thu + vwap2sd_fade | to hop | 22 | -0,24 | 50,0 | 0,97 | -0,06 | 0,71 | -2,77 | 0,450 | 0,455 |  |
| 28 | poc_cham_bat NGUOC vah_val_fade | xung dot | 37 | -1,04 | 38,9 | 0,89 | -0,22 | -2,38 | 0,03 | 0,480 | 0,485 |  |
| 29 | UU_TIEN_chi_khi_big_xac_nhan | luat uu tien | 183 | -0,47 | 49,1 | 0,95 | -0,23 | -2,73 | 0,18 | 0,360 | 0,430 |  |
| 30 | DIEM_trong_so>=0.3 | diem uu tien | 751 | -0,24 | 47,7 | 0,97 | -0,27 | -0,85 | 0,30 | 0,130 | 0,195 |  |

Quy tắc đơn (ES), đủ danh sách:

| Quy tắc | n | TB 5′ | TB 15′ | TB 60′ | PF 60′ | Nửa 1 | Nửa 2 | p cùng chiều |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| big30_theo | 283 | -1,79 | -2,22 | -1,03 | 0,87 | -2,03 | -0,74 | 0,485 |
| big30_nguoc | 283 | -0,21 | 0,22 | -0,96 | 0,88 | 0,03 | -1,26 | 0,475 |
| delta15_theo | 479 | -1,17 | -0,64 | 0,75 | 1,10 | -0,97 | 1,50 | 0,040 |
| delta15_nguoc | 479 | -0,83 | -1,36 | -2,75 | 0,71 | -1,03 | -3,50 | 0,950 |
| cvd_phan_ky | 728 | -0,97 | -0,73 | 0,50 | 1,08 | -0,26 | 1,31 | 0,020 |
| hap_thu | 71 | -0,23 | 1,68 | 1,05 | 1,24 | 2,30 | -4,23 | 0,245 |
| vwap2sd_fade | 508 | -1,13 | -1,79 | -0,98 | 0,88 | -1,28 | -0,74 | 0,570 |
| vwap2sd_pha | 508 | -0,87 | -0,21 | -1,02 | 0,88 | -0,72 | -1,26 | 0,460 |
| vwap_cat_theo | 460 | -0,79 | -1,24 | -2,56 | 0,72 | -1,93 | -3,16 | 0,890 |
| vah_val_fade | 158 | -1,42 | -3,03 | -5,33 | 0,51 | -4,48 | -5,77 | 0,995 |
| vah_val_pha | 168 | -0,41 | 0,17 | 3,68 | 1,64 | 4,29 | 3,31 | 0,000 |
| poc_cham_bat | 99 | -1,03 | -2,08 | -1,75 | 0,78 | -2,30 | -1,19 | 0,585 |
| wall_cham_fade | 6 | 8,76 | 5,44 | -21,35 | 0,04 |  | -21,35 | 0,990 |
| wall_pha_theo | 7 | 0,10 | -4,43 | 0,84 | 1,09 |  | 0,84 | 0,380 |
| oi_cum_cham_bat | 4 | -17,80 | -27,07 | -12,26 | 0,74 |  | -12,26 |  |
| gamma_am_theo_nen_manh | 43 | -0,46 | -6,66 | -2,94 | 0,84 |  | -2,94 | 0,765 |

### XAU (GCZ6 → GOLD.i): 71 phiên 20260820–20261126, phí vòng tròn 0,30 điểm, 106 phép thử (n ≥ 20); 18 phép có p < 0,05, 11 phép ĐẠT

| # | Quy tắc / tổ hợp | Nhóm | n | TB 60′ (điểm, sau phí) | Thắng % | PF | t | Nửa 1 | Nửa 2 | p ngẫu nhiên | p cùng chiều | Đạt |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | big30_theo NGUOC poc_cham_bat | xung dot | 34 | 7,91 | 62,5 | 6,05 | 3,34 | 7,96 | 7,85 | 0,000 | 0,000 | ĐẠT |
| 2 | big30_theo NGUOC vwap_cat_theo | xung dot | 54 | 6,53 | 67,3 | 3,11 | 3,13 | 2,30 | 9,89 | 0,000 | 0,000 | ĐẠT |
| 3 | big30_theo + vwap_cat_theo | to hop | 58 | 6,93 | 65,5 | 2,72 | 2,62 | 3,30 | 10,19 | 0,000 | 0,000 | ĐẠT |
| 4 | delta15_theo + vah_val_fade | to hop | 125 | 2,97 | 58,4 | 1,85 | 2,49 | 3,54 | 1,51 | 0,000 | 0,000 | ĐẠT |
| 5 | big30_theo + delta15_theo | to hop | 387 | 2,01 | 52,1 | 1,42 | 2,48 | 0,58 | 3,17 | 0,005 | 0,000 | ĐẠT |
| 6 | big30_theo | big trade | 506 | 1,59 | 52,6 | 1,33 | 2,30 | 0,04 | 2,98 | 0,005 | 0,000 | ĐẠT |
| 7 | big30_theo + vah_val_fade | to hop | 26 | 6,71 | 50,0 | 3,40 | 2,21 | 6,33 | 7,72 | 0,000 | 0,000 | ĐẠT |
| 8 | big30_theo + poc_cham_bat | to hop | 27 | 6,66 | 65,4 | 2,59 | 1,89 | 0,77 | 14,69 | 0,000 | 0,010 | ĐẠT |
| 9 | delta15_theo + vwap2sd_fade | to hop | 159 | 1,62 | 59,5 | 1,36 | 1,43 | 2,62 | 0,18 | 0,030 | 0,045 | ĐẠT |
| 10 | delta15_theo + vwap_cat_theo | to hop | 241 | 1,45 | 51,9 | 1,30 | 1,41 | 1,34 | 1,57 | 0,045 | 0,025 | ĐẠT |
| 11 | cvd_phan_ky NGUOC hap_thu | xung dot | 237 | 0,85 | 50,6 | 1,23 | 1,13 | 0,74 | 0,97 | 0,065 | 0,040 | ĐẠT |
| 12 | big30_theo NGUOC hap_thu | xung dot | 83 | 2,91 | 59,0 | 1,74 | 1,91 | -0,02 | 4,94 | 0,025 | 0,020 |  |
| 13 | flow_ab_theo | flowRecs Fxaurum | 99 | 2,62 | 53,5 | 1,57 | 1,61 |  | 2,62 | 0,015 | 0,035 |  |
| 14 | big30_theo NGUOC vah_val_fade | xung dot | 58 | 3,16 | 58,9 | 1,72 | 1,55 | -1,13 | 7,45 | 0,025 | 0,035 |  |
| 15 | UU_TIEN_chi_khi_big_xac_nhan | luat uu tien | 406 | 1,21 | 50,9 | 1,23 | 1,52 | -0,36 | 2,67 | 0,015 | 0,020 |  |
| 16 | UU_TIEN_big+delta_cung_chieu | luat uu tien | 266 | 1,53 | 49,6 | 1,28 | 1,50 | -0,13 | 2,89 | 0,015 | 0,015 |  |
| 17 | cvd_phan_ky + vah_val_fade | to hop | 156 | 1,38 | 53,3 | 1,40 | 1,48 | 1,86 | 0,85 | 0,035 | 0,065 |  |
| 18 | delta15_theo NGUOC hap_thu | xung dot | 195 | 1,36 | 55,5 | 1,34 | 1,47 | -0,04 | 2,72 | 0,040 | 0,040 |  |
| 19 | oi_cum_cham_bat | wall/gamma | 21 | 3,54 | 66,7 | 1,98 | 1,17 |  | 3,54 | 0,085 | 0,130 |  |
| 20 | poc_cham_bat + vwap_cat_theo | to hop | 93 | 1,66 | 57,6 | 1,40 | 1,16 | 3,42 | 0,13 | 0,055 | 0,110 |  |
| 21 | delta15_theo NGUOC vah_val_fade | xung dot | 106 | 1,53 | 51,4 | 1,32 | 1,04 | -0,33 | 4,32 | 0,065 | 0,120 |  |
| 22 | flow_ice_theo + flow_sw_theo | to hop | 24 | 3,92 | 62,5 | 1,77 | 1,04 |  | 3,92 | 0,035 | 0,040 |  |
| 23 | big30_theo + cvd_phan_ky | to hop | 138 | 1,22 | 55,1 | 1,27 | 1,01 | -1,13 | 3,37 | 0,090 | 0,060 |  |
| 24 | cvd_phan_ky NGUOC flow_sw_theo | xung dot | 27 | 3,49 | 74,1 | 1,74 | 0,99 |  | 3,49 | 0,075 | 0,050 |  |
| 25 | cvd_phan_ky + delta15_theo | to hop | 255 | 0,92 | 47,8 | 1,20 | 0,98 | 1,35 | 0,51 | 0,060 | 0,060 |  |
| 26 | flow_cs_theo | flowRecs Fxaurum | 65 | 1,75 | 46,2 | 1,32 | 0,83 |  | 1,75 | 0,095 | 0,060 |  |
| 27 | big30_theo NGUOC vwap2sd_fade | xung dot | 140 | 1,21 | 50,4 | 1,19 | 0,81 | -0,82 | 2,89 | 0,105 | 0,090 |  |
| 28 | vah_val_fade NGUOC vwap2sd_fade | xung dot | 35 | 1,60 | 48,6 | 1,43 | 0,78 | 4,19 | -1,46 | 0,165 | 0,160 |  |
| 29 | cvd_phan_ky NGUOC gamma_am_theo_nen_manh | xung dot | 54 | 1,42 | 50,0 | 1,34 | 0,70 |  | 1,42 | 0,145 | 0,160 |  |
| 30 | cvd_phan_ky + flow_sw_theo | to hop | 36 | 1,99 | 44,4 | 1,39 | 0,70 |  | 1,99 | 0,140 | 0,215 |  |

Quy tắc đơn (GC), đủ danh sách:

| Quy tắc | n | TB 5′ | TB 15′ | TB 60′ | PF 60′ | Nửa 1 | Nửa 2 | p cùng chiều |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| big30_theo | 506 | -0,18 | 0,29 | 1,59 | 1,33 | 0,04 | 2,98 | 0,000 |
| big30_nguoc | 506 | -0,42 | -0,89 | -2,19 | 0,68 | -0,64 | -3,58 | 1,000 |
| delta15_theo | 1281 | -0,27 | -0,40 | 0,13 | 1,03 | -0,04 | 0,32 | 0,145 |
| delta15_nguoc | 1281 | -0,33 | -0,20 | -0,73 | 0,87 | -0,56 | -0,92 | 0,830 |
| cvd_phan_ky | 2455 | -0,24 | -0,17 | -0,20 | 0,96 | -0,29 | -0,11 | 0,270 |
| hap_thu | 691 | -0,24 | -0,40 | -0,79 | 0,83 | -0,34 | -1,27 | 0,895 |
| vwap2sd_fade | 1096 | -0,47 | -0,38 | -0,07 | 0,99 | 0,64 | -0,88 | 0,210 |
| vwap2sd_pha | 1096 | -0,13 | -0,22 | -0,53 | 0,89 | -1,24 | 0,28 | 0,805 |
| vwap_cat_theo | 917 | -0,18 | -0,16 | 0,04 | 1,01 | -0,42 | 0,48 | 0,230 |
| vah_val_fade | 616 | -0,38 | -0,54 | -0,64 | 0,87 | 0,52 | -2,22 | 0,635 |
| vah_val_pha | 513 | -0,45 | -0,55 | -0,31 | 0,94 | -1,82 | 1,64 | 0,555 |
| poc_cham_bat | 445 | -0,54 | -0,33 | -0,71 | 0,85 | -0,76 | -0,64 | 0,705 |
| wall_cham_fade | 2 |  |  |  |  |  |  |  |
| wall_pha_theo | 2 |  |  |  |  |  |  |  |
| oi_cum_cham_bat | 21 | -1,50 | 1,99 | 3,54 | 1,98 |  | 3,54 | 0,130 |
| gamma_am_theo_nen_manh | 105 | -0,92 | -2,64 | -2,67 | 0,58 |  | -2,67 | 0,960 |
| flow_sw_theo | 99 | -0,79 | -0,57 | 0,90 | 1,16 |  | 0,90 | 0,210 |
| flow_sw_nguoc | 99 | 0,19 | -0,03 | -1,50 | 0,78 |  | -1,50 | 0,820 |
| flow_ab_theo | 99 | -0,53 | -1,05 | 2,62 | 1,57 |  | 2,62 | 0,035 |
| flow_ab_nguoc | 99 | -0,07 | 0,45 | -3,22 | 0,57 |  | -3,22 | 0,975 |
| flow_ice_theo | 80 | 0,02 | 0,09 | 0,83 | 1,13 |  | 0,83 | 0,250 |
| flow_ice_nguoc | 80 | -0,62 | -0,69 | -1,43 | 0,80 |  | -1,43 | 0,740 |
| flow_cs_theo | 65 | -0,32 | 0,80 | 1,75 | 1,32 |  | 1,75 | 0,060 |
| flow_cs_nguoc | 65 | -0,28 | -1,40 | -2,35 | 0,69 |  | -2,35 | 0,895 |


## (d) Xử lý khi tín hiệu bất đồng (đo từ `xung_dot_*.csv`, TB 60′ điểm, nửa 1 / nửa 2)

| Sự kiện mức giá | big trade 30′ cùng chiều | big trade 30′ ngược chiều | không có big trade |
|---|---|---|---|
| GC chạm VAH/VAL đánh ngược | +9,56 (n23; 10,50 / 6,91) | −3,99 (n47; −2,18 / −6,05) | −0,79 (n527) |
| GC chạm POC | +7,84 (n13) | −3,94 (n22; −1,70 / −7,86) | −0,80 (n404) |
| GC CVD phân kỳ | +1,29 (n97) | −2,89 (n104; −1,40 / −3,94) | −0,13 (n2.136) |
| GC hấp thụ | −1,38 (n18) | −4,25 (n40; −5,43 / −3,18) | −0,55 (n602) |
| ES chạm VAH/VAL đánh ngược | +4,92 (n8) | −17,12 (n14) | −4,70 (n133) |
| ES phá VAH/VAL theo | +14,81 (n9) | −1,36 (n9) | +3,31 (n145; 4,10 / 2,76) |
| ES CVD phân kỳ | +10,26 (n54) | +6,71 (n43) | −0,80 (n612) |

Thứ tự ưu tiên rút ra (đưa vào điểm vào/điểm vùng của HYB+AG):

1. **Big trade 30′ thắng mức giá.** Trên vàng, mức giá (VA/POC/hấp thụ) bị big trade ngược chiều đều âm ở CẢ hai nửa. Khi xung đột thì bỏ lệnh fade, hoặc vào theo big trade:
   - GC `big30_theo NGUOC poc_cham_bat`: +7,91, n34, 7,96 / 7,85.
   - ES `big30_theo NGUOC vah_val_fade`: +15,60, n23.
2. **Delta 15′ đứng thứ hai.** Mức giá bị delta ngược chiều cũng âm (GC VA fade −2,64; hấp thụ −3,29).
3. **Mức giá đứng một mình (fade) không có lợi thế sau phí** trên cả hai mã, trừ ES phá VA theo chiều phá.
4. **Luật đề xuất cho điểm S/vùng:**
   - `+2·big30 + 1·delta15`.
   - Mức VA/POC/wall chỉ được tính khi big30 và delta15 không ngược chiều.
   - Nếu big30 ngược chiều mức thì điểm của mức = 0, và chặn DCA ở mức đó.
   - Kết quả đo: `UU_TIEN_big>delta>muc` ES +0,98 (n504; 0,43 / 1,25, p cùng chiều 0,040). `UU_TIEN_chi_khi_big_xac_nhan` GC +1,21 (n406; −0,36 / 2,68), chưa đạt ở nửa 1.

## Kết luận ngắn

- **SP500:**
  - Đơn lẻ vững nhất là `vah_val_pha`: +3,68 điểm/lệnh, n168, cả hai nửa dương, p cùng chiều 0,000.
  - Tổ hợp tốt: `cvd_phan_ky + delta15_theo` (+5,23, n123).
  - Fade VAH/VAL âm rõ (−5,33, n158), fade VWAP 2SD âm.
- **XAU:**
  - Đơn lẻ: `big30_theo` +1,59 điểm/lệnh (≈ 159 USD/lot), n506, p cùng chiều 0,000. Nhưng nửa 1 chỉ +0,04, nên lợi thế dồn vào nửa 2.
  - Tổ hợp: `big30 + delta15` +2,01 (n387); `delta15 + vah_val_fade` +2,97 (n125; 3,54 / 1,52).
  - flowRecs absorption theo +2,62 (n99, chỉ 1 tuần, chưa có nửa 1).
- Mẫu ngắn (3 tháng, 1 hợp đồng). Đây là **ứng viên** cho điểm S và vùng của HYB+AG (giai đoạn B, quy trình 7 bước), chưa phải hệ đạt.

## Giai đoạn B (thử cắm vào HYB+AG, ESZ6 đủ 59 phiên) — `ma/hyb_of.py`, `ma/hyb_of_kiem.py`, `ket_qua/hyb_of/`

- **Baseline HYB+AG 1,5x (s00, 01/06–26/11):** chạy lại khớp đúng: lãi +1.501,90 USD, maxDD 575,97, thả nổi tệ nhất −908,82, spread 2x +1.461,06, 11/11 stress sống, stress tệ nhất −2.719,17 / thả nổi −4.676,56. Mức thả nổi đó bằng 46,8% vốn 10k, hay 15,6% nếu tính 30k gồm nạp thêm.
- **Chặn vào/DCA khi orderflow giảm** (S −1 trong 15′):

  | Lọc | Δ lãi trong cửa sổ có ES | p ngẫu nhiên | Láng giềng dương |
  |---|---:|---:|---:|
  | big30 | −48,47 | 0,795 | 7/15 |
  | delta15 | −26,09 | 0,675 | 7/15 |
  | tổng hợp | −23,32 | 0,595 | 7/15 |

  Bản 25 phiên trước đó (+97,61, p 0,02, thư mục `ket_qua/hyb_of_25phien/`) **không giữ được** khi đủ dữ liệu.
- **Vùng POC ES phiên trước thêm vào vp:** lãi +1.741,08 nhưng maxDD 723,45 và thả nổi −1.236,07, đều xấu hơn baseline. Thêm cả VAH/VAL thì maxDD 1.709,49. **Không nhận.**
- **Stress:** 11 kịch bản stress không có orderflow, nên điểm giữ trung tính và kết quả bằng baseline.
- **Bước 7 (shadow log):** chưa chạy, vì cần thời gian thật về phía trước.
- **Kết luận B:** chưa có biến thể orderflow nào vượt baseline HYB+AG một cách vững. Ứng viên tiếp theo là luật ưu tiên ở mục (d) (big30 > delta15 > mức), dùng làm cổng DCA, chưa đo trong động cơ.
