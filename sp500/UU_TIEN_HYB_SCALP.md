# Luật ưu tiên dữ liệu trong HYB+AG (US500 + XAU), kiểm 7 bước, và thử dùng làm lệnh/cụm giữ ngắn

Viết 27/11/2026 ~21:00 (giờ Việt Nam, UTC+7). Chỉ số đo. Không đặt lệnh thật, không đổi luật live.

**Mã:**
- `sp500/ma/uu_tien_hyb.py` (7 bước).
- `sp500/ma/scalp_cum.py` (giữ ngắn và cụm).
- `sp500/ma/bong_tin_hieu.py` (bước 7, nhật ký bóng).
- Bộ sinh tín hiệu dùng chung: `phong_cach_tay/tin_hieu_data.py`.

**Kết quả:** `ket_qua/uu_tien_hyb/`, `ket_qua/scalp_cum/`.

## Luật đem thử (lấy từ Phần 1)

- Điểm ưu tiên `uu_tien = 2·big30 + 1·delta15`, mỗi tín hiệu giữ 15′. Chiếu lên nến M1 XM: dùng từ nến bắt đầu sau phút futures ≥ 2′. Ngoài dữ liệu thì bằng 0.
- **VAO_UU_TIEN:** S ± 1 khi |uu_tien| ≥ 2 (có big trade). Ảnh hưởng cả vào lệnh lẫn DCA.
- **VAO_CHI_CONG:** chỉ cộng 1 khi uu_tien ≥ 2 (big trade mua), không trừ.
- **CHAN_DCA_big_nguoc:** vào lệnh giữ nguyên; DCA đợi khi big trade 30′ đang bán. Cách làm: thêm mảng SD riêng vào động cơ, thay `S[i]>=sd` bằng `SD[i]>=sd`. Không sửa gì khác.
- **CA_HAI:** VAO_UU_TIEN + CHAN_DCA.
- Mức VA/POC (`muc_hop_le`) không cắm vào vùng. Lần thử trước, thêm POC vào vùng làm DD tăng.

## Kết quả 7 bước

Cửa sổ có dữ liệu:
- ES: từ 14/09 (giờ máy chủ XM), vì ESZ6 trước kỳ chuyển hợp đồng khoảng 12/09 quá mỏng.
- GC: từ 20/08 (UTC+7).

"Nửa 1 / nửa 2" là hai nửa của cửa sổ đó; OOS tính từ 01/10.

### US500 (HYB+AG 1,5x, vốn 10k, s00 01/06–26/11)

| Biến thể | Lãi | MaxDD | Thả nổi tệ nhất | IS | OOS | Cửa sổ dữ liệu | Nửa 1 / nửa 2 | Spread 2x | Δ so gốc | p ngẫu nhiên | Lân cận dương | DSR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GOC | 1.501,90 | 575,97 | −908,82 | 687,91 | 813,99 | 770,99 | −28,62 / 799,61 | 1.461,06 | | | | |
| VAO_UU_TIEN | 1.000,71 | 1.021,90 | −1.142,44 | 683,33 | 317,38 | 269,80 | −33,21 / 303,01 | 945,93 | −501,19 | 0,99 | 2/15 | 0,593 |
| VAO_CHI_CONG | 1.431,05 | 646,81 | −908,82 | 682,95 | 748,10 | 700,15 | −33,58 / 733,73 | 1.356,97 | −70,84 | 0,98 | 2/15 | 0,817 |
| CHAN_DCA_big_nguoc | 1.028,71 | 1.021,90 | −1.142,44 | 687,91 | 340,80 | 297,80 | −28,62 / 326,43 | 1.003,97 | −473,19 | 0,96 | 2/15 | 0,603 |
| CA_HAI | 1.000,71 | 1.021,90 | −1.142,44 | 683,33 | 317,38 | 269,80 | −33,21 / 303,01 | 945,93 | −501,19 | 0,95 | 2/15 | 0,593 |

- Stress 11 kịch bản: không có dữ liệu orderflow nên điểm trung tính, kết quả bằng gốc. Sống 11/11; tệ nhất −2.719,17; thả nổi tệ nhất −4.676,56, tức 46,8% vốn 10k hoặc 15,6% vốn 30k.
- **Không biến thể nào vượt gốc.** Chặn DCA khi big trade bán làm mất chính những lớp mua đáy sinh lãi, maxDD tăng gần gấp đôi.

### XAU (cổng HYB+AG vàng của worker vàng, `vang/ma/may_hyb.py`, vốn 10k)

| Biến thể | Lãi | MaxDD (%) | IS | OOS | Cửa sổ dữ liệu | Nửa 1 / nửa 2 | Spread 2x | Δ so gốc | p ngẫu nhiên | Lân cận dương | DSR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GOC | 78,82 | 5.762,09 (57,6%) | −1.924,51 | 2.003,33 | 3.905,19 | 628,42 / 3.276,77 | −750,55 | | | | |
| VAO_UU_TIEN | −4.319,64 | 5.905,67 (59,1%) | −1.848,03 | −2.471,61 | −493,28 | 708,20 / −1.201,48 | −5.070,02 | −4.398,47 | 0,82 | 2/8 | 0,162 |
| VAO_CHI_CONG | 388,36 | 5.691,82 (56,9%) | −1.870,49 | 2.258,86 | 4.214,73 | 698,69 / 3.516,03 | −439,55 | +309,54 | 0,09 | 7/8 | 0,362 |
| CHAN_DCA_big_nguoc | −3.256,67 | 6.487,20 (64,9%) | −1.617,80 | −1.638,87 | 569,69 | 918,63 / −348,93 | −3.967,49 | −3.335,50 | 0,83 | 2/8 | 0,192 |
| CA_HAI | −3.020,39 | 6.450,45 (64,5%) | −1.559,24 | −1.461,15 | 805,97 | 980,50 / −174,53 | −3.727,13 | −3.099,22 | 0,73 | 2/8 | 0,202 |

- Baseline khớp số của worker vàng (+78,82 / 57,62%).
- Stress 4 kịch bản tổng hợp trên M1 (có dữ liệu):
  - VAO_CHI_CONG gần bằng gốc: gap −10% +3.427,74, gap −20% +13.595,87, grind −20% +5.803,35, grind −35% +4.910,66.
  - CA_HAI ở grind −20%: DD 6.275,77, thả nổi −6.012,10.
- 7 kịch bản sập M15 không có dữ liệu nên trung tính, bằng gốc. Riêng gốc vàng đã **cháy ở 2022 H1** (−18.154, DD 225,8%), và Covid có DD 67,6%.
- **Chỉ VAO_CHI_CONG có Δ dương:**
  - +309,54 trong cửa sổ dữ liệu, cả hai nửa đều tốt hơn gốc, 7/8 cấu hình lân cận dương.
  - Nhưng p ngẫu nhiên 0,09 (chưa đạt 0,05), DSR 0,362, spread 2x vẫn âm (−439,55).
  - Kết luận: **CHƯA ĐẠT**, chỉ là ứng viên. Còn vấn đề gốc là HYB+AG vàng chưa qua stress.

## Bước 7: nhật ký bóng (chạy rồi, chỉ ghi)

- **Script:** `sp500/ma/bong_tin_hieu.py`, cần `tin_hieu_data.py` cùng thư mục hoặc repo.
- **Cách hoạt động:**
  - Mỗi 60 giây kéo tick 120′ gần nhất của ESZ6 (CME) và GCZ6 (COMEX). Chỉ gọi RPC đọc `aggTrades`, không gọi sync.
  - Lúc khởi động, và khi sang phiên mới, kéo thêm phiên trước để có VAH/VAL/POC.
  - Mỗi phút đã đóng ghi một dòng vào `bong_tin_hieu.csv`: big30, delta15, cvd_pk, vah_val_pha, muc_fade, muc_hop_le, uu_tien, cong_dca_mua/ban, sig, kèm ghi chú "chi log, khong dat lenh".
- **Đang chạy trên máy nhà** từ 20:50 ngày 27/11, PID 16676.
  - Lệnh: `python bong_tin_hieu.py --ra C:\Users\DUNG\sp500_2711\bong\nhat_ky --vong 60 --lan 0`.
  - Thư mục làm việc: `C:\Users\DUNG\sp500_2711\bong\`. Log ở `bong.log` / `bong.err.log`.
  - Dừng: `taskkill /PID 16676 /F`, đúng PID này. Nếu Anh cần máy thì dừng theo VAN_HANH §10.
- **Lần thử 2 giờ đầu** (18:50–20:49, trước giờ phiên Mỹ ngày nghỉ lễ): ghi 205 dòng, 0 tín hiệu. Ngưỡng đã chỉnh theo dữ liệu trong phiên (ES chỉ đo giờ RTH).

## Lệnh / cụm giữ ngắn (Anh lướt dưới 5′)

**Cách đo:**
- Vào ở giá mở nến CFD kế tiếp; phí vòng tròn US500 1,00 điểm, vàng 0,30.
- ATR60 trung vị (biên độ nến 1′): US500 1,66; vàng 1,82.
- Cụm = 3 lệnh ở 3 nến liên tiếp. Mỗi lệnh chốt TP riêng, hết 5′ thì đóng, không SL.
- TP thử ba mức: 0,5 ATR, 1 ATR, và khe TP của Anh theo tay_v2 (vàng 4,00, US500 6,53).

**TB điểm/lệnh sau phí**

| Mã | Tín hiệu | n | 1′ | 2′ | 3′ | 5′ | 15′ | 60′ | Cụm TP 0,5 ATR | Cụm TP 1 ATR | Cụm TP tay |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| US500 | vah_val_pha | 168 | −0,94 | −0,80 | −0,93 | −0,41 | 0,17 | 3,68 | −3,24 | −2,45 | −1,88 |
| US500 | cvd_pk + delta15 | 121 | −1,26 | −0,79 | −0,56 | −0,29 | −1,04 | 5,23 | −1,41 | −0,74 | −1,06 |
| US500 | big30 thắng mức fade | 14 | −0,07 | 1,07 | 0,37 | −1,21 | 4,79 | 14,96 | −0,07 | 1,30 | 0,32 |
| XAU | big30 | 503 | −0,20 | −0,21 | −0,09 | −0,18 | 0,29 | 1,59 | −1,04 | −0,89 | −1,09 |
| XAU | big30 + delta15 | 384 | −0,18 | −0,30 | −0,13 | −0,07 | 0,01 | 2,01 | −0,93 | −0,77 | −0,96 |
| XAU | delta15 + mức fade | 172 | −0,23 | −0,27 | −0,34 | −0,13 | 0,21 | 0,95 | −0,90 | −0,74 | −0,72 |
| XAU | big30 thắng mức fade | 46 | 0,12 | 0,69 | 0,98 | 1,76 | 1,93 | 5,47 | 0,19 | 2,04 | 1,10 |

(Cụm = tổng của 3 lệnh. Đủ cột thắng%, PF, t, hai nửa, p trong `ket_qua/scalp_cum/scalp_*.csv`.)

- **Kết luận giữ ngắn:** các tín hiệu đạt ở Phần 1 **không có lợi thế ở 1–5′ sau phí** trên cả hai mã. Lợi thế chỉ hiện ra ở 30–60′. Ở 1–5′, phí ăn hết vì biến động 1′ chỉ cỡ 1,7–1,8 điểm.
- Ngoại lệ duy nhất dương ở 5′ là vàng **big30 thắng mức fade**: n46, +1,76 ở 5′; cụm TP 1 ATR +2,04/cụm, p 0,00. Nhưng nửa 1 / nửa 2 là +4,82 / −0,51, mẫu nhỏ, **chưa đạt**.

## Ghi cho worker Phần 2 (`phong_cach_tay/`)

- **Cách dùng:**
  ```
  from phong_cach_tay import tin_hieu_data as T
  F, M = T.tao('GC' | 'ES', ms_m1)
  ```
  `ms_m1` là giờ mở nến M1 theo UTC ms. Từ giờ máy chủ XM thì đổi bằng `T.ms_tu_gio_may_chu(...)`.
- `M` có các mảng theo nến M1: `sig_GC` / `sig_ES` (+1 / −1), `uu_tien`, `cong_dca_mua`, `cong_dca_ban`… Dùng thẳng làm `sig` cho `may_v2.run` được.
- Tôi không sửa tệp nào khác trong `phong_cach_tay/`.
- Theo số đo trên, dùng tín hiệu này cho cụm dưới 5′ thì âm sau phí. Chỉ nên dùng làm bộ lọc ngữ cảnh / giữ ≥ 30′.
