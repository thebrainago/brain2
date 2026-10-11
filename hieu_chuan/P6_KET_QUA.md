# P6 — Hiệu chuẩn ngưỡng LOẠI SỚM nhanh (11/10/2026, giờ VN)

**MÔ PHỎNG so với TESTER MT5 + chuỗi CHỈ NHIỄU. Không có con số nào là tiền thật. Chỉ là NHÃN, không đổi GIỮ/BỎ.**
Chạy lại (< 1 giây, chỉ đọc số đã có): `python3 hieu_chuan/p6_hieu_chuan_loai_som.py` → `p6_ket_qua.json`.

Luật gốc của chủ dự án (P5): mô phỏng maxDD > 65 % HOẶC lãi < 10 %/năm → loại trước MT5. Quét DD ∈ {30…80}, lãi ∈ {0…15}.

## (a) 15 ô MT5 sạch (P1, AUDCAD/NZDCAD H1, 6 tháng 2019) — luoi_duong 8 biến thể/ô
MT5 lãi: ô 2 (+9,4 %/năm), ô 8 (+10,9), ô 15 (+29,5); 12 ô lỗ. DD MT5 cao nhất 32,6 % → **ngưỡng DD không đo được trên MT5**.
| lãi tối thiểu | giết oan (ô MT5 lãi bị loại) | lọt (ô MT5 lỗ không bị loại) |
|---|---|---|
| 0 % | 0/24 | 3/96 (ô 4, MT5 −0,15) |
| **2…8 %** | **0/24** | **0/96** |
| 10 % (gốc) | 8/24 (ô 2, MT5 +9,4 %) | 0/96 |
| 15 % | 16/24 (ô 2, 8) | 0/96 |
Khoảng sạch: ô MT5 lỗ có mô phỏng cao nhất +0,5 %/năm; ô MT5 lãi có mô phỏng thấp nhất +8,1 %/năm → chọn **5 %** (giữa, dư ±3 điểm).
Mô phỏng − MT5 trên ô lãi: TB +1,1, tối đa +6,1 điểm/năm (lạc quan nhẹ). DD: biến thể XẤU NHẤT khớp MT5 trong ≤ 4 % mọi ô DD ≥ 2 %;
biến thể đơn lẻ có thể thấp hơn MT5 tới ×1,9 (ô 6, 11, 12, 14) → dùng biến thể xấu nhất khi đọc DD.
Động cơ cũ v3: ô 6 (MT5 −10,8) mô phỏng +12…+22 → **không ngưỡng lãi nào dưới 22 % chặn được**; nhãn vô nghĩa với số v3.

## (b) Chuỗi chỉ nhiễu (p4_ket_qua.json: rw 100 + garch 50 chuỗi) — tỉ lệ LỌT GIẢ (càng thấp càng tốt)
| cặp (DD, lãi) | lưới chọn tốt nhất, kiểm ngoài mẫu | R2 8 biến thể | EA lưới (đường ống vòng) | EA lệnh đơn | EA hedge |
|---|---|---|---|---|---|
| luật chủ 80/0 | 49 % | 49 % | 71 % | 19 % | 16 % |
| gốc 65/10 | 36 % | 36 % | 67 % | 1,8 % | 4,9 % |
| đề xuất 65/5 | 39 % | 40 % | 67 % | 5,0 % | 8,0 % |
| đề xuất 50/5 | 32 % | 34 % | 63 % | 5,0 % | 8,0 % |
| 50/10 | 29 % | 30 % | 63 % | 1,8 % | 4,9 % |
→ **Không cặp nào là bộ lọc nhiễu**: lưới trên nhiễu vẫn lọt 30–67 %. Phân biệt lưới thật/giả vẫn phải nhờ placebo (nhãn P4 Đ2).
Hạ DD 65 → 50 giảm lọt nhiễu lưới ~1/5 (39 → 32 %); hạ lãi 10 → 5 tăng lọt nhiễu lệnh đơn 1,8 → 5 %.

## (c) Lưới có phí P3 (g07/g08 theo năm: thật vs nhiễu cùng cấu trúc) + 6 hệ Breakout P3
- g07 (5 tài sản, 70 năm-tài sản thật / 700 nhiễu): 65/10 lọt 0 thật / 0 % nhiễu; 65/5 hoặc 50/5: 0 thật / 2,6 % nhiễu. DD thật tối đa 24 %.
- g08 (quản trị rổ AUDCAD/EURGBP, 168 / 1680): 65/10: 0 / 0,2 %; 65/5 hoặc 50/5: 2 / 1,3 %. DD thật tối đa 21 % → DD 50 vs 65 không đổi gì.
- Breakout P3 (EURUSD 2016-21): cả 5 hệ bị loại ở mọi cặp (Breakout5 lãi +26,8 %/năm nhưng DD 95 %; còn lại lỗ) — khớp cổng.

## Đề xuất (CHƯA CHỐT — chờ chủ dự án)
1. **DD > 65 % hoặc lãi < 5 %/năm** (đọc trên biến thể luoi_duong xấu nhất): 0/24 giết oan, 0/96 lọt trên 15 ô MT5; gốc 65/10 giết oan ô +9,4 %.
2. **DD > 50 % hoặc lãi < 5 %/năm** (chặt hơn ở DD): cùng kết quả 15 ô; nhiễu lưới lọt 32 % thay vì 39 %. Lý do DD 50: ngưỡng DD
   chưa đo được trên MT5 (> 33 %), biến thể đơn lẻ có thể thấp hơn MT5 ×1,9 → 80 % / 1,6 ≈ 50 % cho dư.
- Trong `vong_thu_nghiem.py`: nhãn gốc 65/10 GIỮ NGUYÊN; thêm `de_xuat_p6` (65/5, 50/5) in cạnh — chỉ nhãn.
- Giới hạn: 15 ô, 1 cửa sổ 6 tháng, 2 mã, không swap trên MT5; 3 ô MT5 lãi. Rổ EA trong vòng chạy `mo_phong.chay_he` → lệch MT5
  CHƯA ĐO ĐƯỢC. Cần ô MT5 có DD 40–90 % để chốt ngưỡng DD.
