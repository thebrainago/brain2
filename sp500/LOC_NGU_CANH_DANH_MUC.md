# Tín hiệu dữ liệu làm BỘ LỌC NGỮ CẢNH + lệnh phụ 30–60′ + danh mục chung vốn (27/11, 21:30 giờ VN)

Mã: `sp500/ma/danh_muc.py`. Kết quả: `sp500/ket_qua/danh_muc/` (`a_he_so_lot.csv`, `a_doi_chung.csv`, `b_lenh_phu.csv`, `c_tuong_quan_ngay.csv`, `c_danh_muc.csv`, `c_stress_gop.csv`, `meta.json`).
Không đặt lệnh thật, không đổi luật live. Vốn 10.000 USD = 1.000.000 USC (USC = USD × 100). Chỉ số đo được.

Cách chạy: engine HYB+AG (`vang/nguon_hyb/sim_ag.py`, `vang/ma/may_hyb.py`) và tay_v2 (`phong_cach_tay/ma/may_v2.py`) được **đọc từ bản đã commit (git HEAD)** rồi vá khi chạy vào `/workspace/sp500_2711/eng/`; không sửa file của worker khác. tay_v2 US500 = cấu hình mặc định của worker Phần 2 (`P_v2("US500")`, lọc `p1_union_es`); tay_v2 XAU = cấu hình mặc định vàng an toàn (`L0 0,01, K4, maxL20, flcap 0,15, hedge 1×`, lọc delta15). Chạy lại khớp số của họ: US500 +657,83 / DD 1,77%; XAU +14.032,99 / DD 34,24%.

Ngữ cảnh C = chiều tín hiệu ĐẠT mới nhất của Phần 1, giữ H phút: US500 = `vah_val_pha`, nếu không có thì `cvd_pk + delta15 cùng chiều` (= `p1_union_es`); vàng = big30 thắng mức fade, nếu không có thì big30 + delta15.

## (a) Hệ số lot theo chiều dữ liệu (không chặn lệnh)

Lot vào/DCA × mA khi cùng chiều C, × mO khi ngược chiều, × 1 khi không có C. "cs_dl" = lãi trong cửa sổ có dữ liệu ES (28/08–25/11).

| Hệ | Biến thể | Lãi USD | maxDD | DD % | IS | OOS | Spread ×2 | cs_dl | nửa 1 / nửa 2 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| HYB+AG US500 | gốc | 1.501,90 | 559,38 | 5,59 | 689,55 | 812,34 | 1.461,06 | 786,25 | −8,08 / 794,33 |
| HYB+AG US500 | H60 ×1,5/×0,5 | 984,78 | 1.624,85 | 16,25 | 694,58 | 290,20 | 959,08 | 348,46 | −3,30 / 351,76 |
| HYB+AG US500 | H60 ×1/×0,5 | 1.033,56 | 1.378,72 | 13,79 | 684,74 | 348,82 | 1.016,06 | 387,98 | −13,14 / 401,12 |
| HYB+AG US500 | tốt nhất (H30 ×1/×0,5) | 1.050,31 | 1.555,64 | 15,56 | 687,45 | 362,86 | 1.029,70 | 414,10 | −10,30 / 424,40 |
| tay_v2 US500 | gốc (L0 0,10) | 657,83 | 177,43 | 1,77 | 148,32 | 509,51 | 538,00 | 697,47 | 163,71 / 533,76 |
| tay_v2 US500 | H60 ×1,5/×0,5 | 920,39 | 181,12 | 1,81 | 196,14 | 724,25 | 772,33 | 977,60 | 139,02 / 838,58 |
| tay_v2 US500 | H30 ×1,5/×0,5 | 900,31 | 176,19 | 1,76 | 194,31 | 706,00 | 742,80 | 957,52 | 206,44 / 751,08 |
| tay_v2 US500 | H60 ×2/×0,5 | 1.136,28 | 285,39 | 2,85 | 249,94 | 886,34 | 954,98 | 1.211,06 | 201,05 / 1.010,01 |

Đầy đủ 24 dòng trong `a_he_so_lot.csv`.

- **HYB+AG US500: KHÔNG ĐẠT.** Mọi hệ số đều kém gốc 452–654 USD. DD tăng từ 5,59% lên 13,8–21,4%. Đối chứng xáo trộn ngữ cảnh (dịch theo ngày, 50 lần) p = 0,98. Láng giềng tham số: chỉ 5/15 dương. Lý do: HYB+AG chỉ mua, nên nhân lot khi dữ liệu "cùng chiều" làm rổ DCA lớn hơn đúng lúc giá đang đi ngược.
- **tay_v2 US500: CÓ CẢI THIỆN, nhưng phần lớn là tăng đòn bẩy.** 93,7% lệnh vào của `p1_union_es` vốn đã cùng chiều C (ngược chiều chỉ 3,5%). Đối chứng đúng là tăng lot đều:
  - L0 0,15: +977,52, DD 2,76%, spread ×2 +795,48.
  - L0 0,20: +1.311,77, DD 3,74%.
  - So lãi/DD: ×1,5/×0,5 đạt 920,39/181,12 = 5,08, tốt hơn lot đều 0,15 (3,54) và gốc (3,71).
  - Phần lợi thật đến từ nhân lot ở các lần DCA theo ngữ cảnh lúc DCA.
  - Đối chứng xáo trộn p = 0,00 (đối chứng yếu, vì xáo trộn chủ yếu làm mất sự cùng chiều). Láng giềng (K 4/6, tp 5/8, gap 6,5/10) 6/6 dương, trung vị +506.
  - Stress: các cửa sổ crash không có dữ liệu Fxaurum, nên C = 0 và kết quả trùng bản gốc (đạt). 4 kịch bản tổng hợp chưa chạy lại cho hệ số lot.
  - Chưa tính DSR cho (a).
  - Kết luận: **ứng viên** ×1,5/×0,5 (H30 hoặc H60) cho tay_v2 US500. Chưa đạt đủ 7 bước.

## (b) Lệnh phụ giữ 30–60′ (rủi ro riêng)

US500 1 lot (1 USD/điểm), vàng 0,05 lot (5 USD/điểm). Vào giá mở nến kế tiếp, mỗi lúc chỉ giữ 1 lệnh. Phí = spread trung vị + trượt 2 lần. SL tùy chọn = 10 × ATR1′(60).

| Mã | Tín hiệu | Giữ | n | Lãi USD | TB/lệnh | Thắng % | maxDD | Spread ×2 | Nửa 1 / Nửa 2 | p ngẫu nhiên | DSR |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| US500 | union (pha VAH/VAL, nếu không có thì CVD+delta15) | 60′ | 165 | 697,02 | 4,22 | 54,5 | 148,57 (1,49%) | 598,02 | 202,13 / 494,89 | 0,00 | 0,582 |
| US500 | pha VAH/VAL | 60′ | 104 | 386,57 | 3,72 | 56,7 | 163,17 | 324,17 | 191,51 / 195,06 | 0,03 | 0,516 |
| US500 | CVD+delta15 | 60′ | 87 | 203,76 | 2,34 | 48,3 | 194,04 | 151,56 | 78,32 / 125,44 | 0,06 | 0,210 |
| Vàng | big30 thắng mức fade | 60′ | 33 | 769,25 | 23,31 | 63,6 | 298,35 | 736,25 | 344,15 / 425,10 | 0,09 | 0,846 |
| Vàng | big30+delta15 | 60′ | 198 | 1.523,90 | 7,70 | 48,5 | 794,35 | 1.325,90 | −290,50 / 1.814,40 | 0,05 | 0,148 |

- Láng giềng (giữ 30/45/90′, có/không SL):
  - US500 union: mọi biến thể đều dương (+292 đến +697), spread ×2 đều dương.
  - US500 CVD+delta15: biến thể 30/45′ âm khi spread ×2.
  - Vàng big30 thắng mức fade: mọi biến thể dương (+377 đến +946).
  - Vàng big30+delta15: nửa 1 âm ở giữ 60/90′.
- DSR đều < 0,95, nên **chưa đạt bước 6**. Dữ liệu chỉ có 3 tháng (59 phiên ES, 71 phiên GC).
- Ứng viên tốt nhất:
  - US500 union 60′: p 0,00, hai nửa dương, ×2 dương.
  - Vàng big30 thắng mức fade 60′: n chỉ 33, p 0,09.
- Stress: cửa sổ crash không có dữ liệu nên không có lệnh. Rủi ro gap khi đang giữ 1 lệnh là số tính, không phải số đo:
  - gap 10% ≈ 680 USD (US500 1 lot) và 2.000 USD (vàng 0,05 lot).
  - gap 20% gấp đôi.
- Bóng (bước 7): `bong_tin_hieu.py` đã ghi đủ cột `vah_val_pha`, `cvd_pk`, `delta15_giu`, `big30`, `muc_fade`.

## (c) Danh mục chung vốn 10.000 USD (trục phút chung 01/06–26/11)

Tương quan lãi/lỗ ngày:

| | HYB US500 | HYB XAU | tay US500 | tay XAU | phụ US500 | phụ XAU |
|---|---:|---:|---:|---:|---:|---:|
| HYB US500 | 1 | −0,026 | 0,040 | −0,264 | 0,003 | −0,166 |
| HYB XAU | | 1 | 0,024 | −0,312 | 0,057 | 0,173 |
| tay US500 | | | 1 | 0,090 | 0,261 | −0,000 |
| tay XAU | | | | 1 | −0,107 | −0,084 |

| Danh mục | Lãi USD | Lãi USC | maxDD gộp | DD % | Tổng DD riêng | Vốn thấp nhất | IS | OOS | Spread ×2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| HYB US500 + tay US500 | 2.159,72 | 215.972 | 473,00 | 4,73 | 736,82 | 9.621,92 | 837,87 | 1.321,85 | 1.999,06 |
| HYB US500 + tay US500 + phụ US500 | 2.856,74 | 285.674 | 458,57 | 4,59 | 885,39 | 9.621,92 | 973,20 | 1.883,54 | 2.696,08 |
| HYB US500 + tay US500 + tay XAU | 16.192,71 | 1.619.271 | 3.288,74 | 32,89 | 4.160,41 | 9.713,37 | 11.284,12 | 4.908,59 | 11.216,05 |
| Cả 4 hệ | 16.271,53 | 1.627.153 | 3.899,90 | 39,00 | 9.881,41 | 8.291,47 | 9.345,13 | 6.926,40 | 10.465,50 |
| Cả 4 hệ + lệnh phụ | 18.588,95 | 1.858.895 | 4.001,00 | 40,01 | 10.894,58 | 8.291,47 | 9.302,36 | 9.286,59 | 12.782,92 |

Spread ×2 của lệnh phụ chưa được đưa vào cột ×2 của danh mục; cột đó dùng ×1 cho lệnh phụ.

Stress gộp (`c_stress_gop.csv`) = tổng maxDD của từng hệ trong cùng kịch bản. Đây là chặn trên, chưa phải mô phỏng chung vốn.

- **HYB US500 + tay US500:** 11/11 kịch bản < 80% của 10k, tệ nhất 4.707,21 USD (grind −35%).
- **+ tay XAU:**
  - Chỉ 4/11 kịch bản < 80% của 10k, nhưng 11/11 < 80% của 30k (tệ nhất 19.379,85 = 64,6% của 30k).
  - Bản thân tay XAU cháy ở grind −35%/120 ngày và Covid, với DD 119–147% ở 3 kịch bản.
- **Cả 4 hệ:** HYB XAU kéo DD lên 39% và stress không qua (gap DD 5.723; 2022 H1 trước đó đã cháy). **Không đạt.**

**Kết luận (c):**
- Lõi chung vốn đạt cả 7 bước theo chặn trên là **HYB+AG US500 + tay_v2 US500**: DD 4,73%, IS và OOS dương, ×2 dương, stress 11/11. Có thể thêm lệnh phụ US500 union 60′ ở mức "ứng viên", vì DSR 0,58.
- Thêm tay XAU cho lãi lớn và tương quan âm với HYB US500 (−0,26), nhưng chỉ qua stress khi tính cả nạp thêm lên 30k. Trong 2 kịch bản, hệ XAU cháy nếu đứng riêng trên 10k.
- Không đưa HYB XAU vào danh mục.

## Bóng (PID 16676, đọc lúc 21:29 27/11, giờ VN)

- Tiến trình vẫn chạy (bắt đầu 20:50:50).
- Có 268 dòng (ghi từ 20:50:54 đến 21:28:09; vòng đầu ghi lùi lại từ 19:56).
- Số phút có tín hiệu khác 0:
  - **ES:** `cvd_pk` 14 phút (−1 lúc 19:56 và 20:09, còn lại +1 từ 20:27 đến 21:23). `delta15` +1 có 1 phút (21:27), kéo `uu_tien` = 1. `big30`, `vah_val_pha`, `muc_fade`, `sig` đều = 0.
  - **GC:** `cvd_pk` +1 có 6 phút (20:14, 21:08–21:15). Các cột khác = 0.
- Từ `cvd_pk` +1 lúc 21:23 và `delta15` +1 lúc 21:27, theo định nghĩa (giữ 15′) sẽ có lệnh "CVD+delta15" mua lúc 21:27. Chỉ ghi nhận, không đặt lệnh.
