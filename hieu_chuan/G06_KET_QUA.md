# G06 — Giả thuyết có chủ đích từ gói the-brain (file 06) — 11/10/2026 (rạng sáng, giờ VN)

Mọi số là **MÔ PHỎNG** (`nhan/luoi_duong`, giá HistData M1 công khai) — không phải tiền thật, không phải MT5.
Không đổi cổng duyệt. Kế hoạch đóng băng TRƯỚC khi chạy: `G06_KE_HOACH.json` sha256 `c8c69e0f8483859b`
(commit `07d2edcc`, đẩy trước khi có số). Chạy: `python hieu_chuan/g06_audcad_2023752.py --nhan 4` (~14 phút, 4 nhân).

## 1. Ba giả thuyết trong 06 (số của the-brain — chưa đo lại trừ G-c)
| | nội dung | the-brain đã có gì | brain2 làm được trên máy này? |
|---|---|---|---|
| G-a | Quản lí lệnh quyết định, entry không (cùng luật lưới, đổi entry ngay/xu hướng/hồi quy/ngẫu nhiên) | chưa đo (sổ tay gt id 2, MỞ); P4 của brain2 đã cho thấy lưới "qua" trên nhiễu ~44–51 % | được, nhưng không đưa thứ đang ra tiền lại gần hơn — để sau |
| G-b | Chọn tài sản: lưới lãi trên tài sản hồi quy (cặp chéo FX, vàng), không trên chỉ số | bản đồ G0 14/09: AUDCAD, EURGBP 8/8 ô hồi quy, vàng 7/8, US100 0/8 — *nguồn gợi ý, chưa phải bằng chứng*; cấu hình PMG sống sót duy nhất +0,015 %/năm | được một phần (đối chứng nhiễu bên dưới chính là phép thử "hồi quy của AUDCAD có giúp lưới không") |
| G-c | Làm lại hệ đang có lãi (31 người thắng MQL5), chạy cả giai đoạn TRƯỚC khi hệ sống | R6: bóc cài đặt tín hiệu 2023752 (AUDCAD, sống ~3,1 năm, +258 %, DD công bố 41,6 %) từ 2.327 lệnh; engine cũ: khám phá 2018-01→2023-07 **+8,45 %/năm**, 70/70 ô có lãi; xác nhận +5,56 %/năm | lịch sử lệnh 31 ID cần đăng nhập MQL5 của chủ → KHÔNG; nhưng 2023752 đã được bóc sẵn → chạy được ngay |

**Chọn G-c trên tín hiệu 2023752** (gần "đang ra tiền" nhất: một hệ thật đang có lãi, luật đã bóc, chỉ cần giá công khai)
và gắn đối chứng nhiễu của G-b vào cùng phép đo.

## 2. Thiết kế (đóng băng)
- Luật: `ThamSo(buoc 21,2, he_so_buoc 1,2, tp 7,6, tran_tang 5, hai_chieu, lot 0,01 cộng 0,25, tia_lenh, bien_cap 4)`,
  vốn 10.000 USD, đòn bẩy 100. Giả định không từ tín hiệu: bien_cap, cap_moi_bar, lot gốc.
- Giá AUDCAD + USDCAD M1 HistData (EST → giờ Helsinki), đổi CAD→USD từng phút. Khám phá 2018-01-02 → 2023-07-02
  (TRƯỚC tín hiệu); xác nhận 2023-07-03 → 2025-02-17 (chồng đời sống tín hiệu → KHÔNG độc lập, chỉ để xem).
- Phí: spread 1,5 / 2,8 pip; swap theo từng lot qua rollover, tỉ lệ tháng = (r_AUD − r_CAD) FRED − markup XM đo 13/09/2026
  (`config/lai_suat_aud_cad_thang.csv`; markup mua 1,50 %/năm, bán 1,61 %/năm — giả định không đổi). 4 thứ tự giá trong nến.
- Nhiễu: 40 chuỗi đảo dấu từng nến M1 (giữ biên độ, phá hồi quy), spread 2,8, swap lịch sử.
- Luật kết luận: ĐẠT (mô phỏng) = lãi > 0 ở cả 8 biến thể + maxDD < 80 % + không stop-out + hơn nhiễu p ≤ 0,05;
  CHƯA ĐO ĐƯỢC nếu một năm thiếu > 5 % phút giao dịch hoặc dấu đổi giữa biến thể.

## 3. Kết quả
**Kết luận theo luật đóng băng: CHƯA ĐO ĐƯỢC** — HistData AUDCAD 2023 (tháng 2–7) thiếu ~22 % phút (độ phủ 0,78;
2018–2022: 0,975–0,992). Nói thẳng: phần dữ liệu sạch cho câu trả lời rõ là **LỖ**:

| khám phá 2018-01 → 2023-07 | lãi ròng | %/năm | maxDD | lệnh | swap |
|---|---|---|---|---|---|
| 8 biến thể (4 thứ tự × spread 1,5/2,8), có swap | −1.608 … −1.883 USD | **−2,9 … −3,4** | 16,9–19,3 % | 2.034–2.168 | ≈ −1.065 USD |
| spread 1,5, KHÔNG swap (gần thước "phí sàn" của the-brain) | −589 USD | −1,07 | 7,5 % | 2.034 | 0 |
| từng năm (gan_open, 2,8, có swap) | 2018 −552 · 2019 −213 · 2020 −629 · 2021 −391 · 2022 −125 · 2023H1 −199 USD | **6/6 năm lỗ** | ≤ 7 % | | |

- Thứ tự trong nến đổi ≤ 0,5 điểm %/năm (M1 phân giải đủ); dấu giống nhau ở cả 8 biến thể; không stop-out.
- **Nhiễu:** 40/40 chuỗi lỗ (trung vị −1.970 USD, p5–p95 −3.284…−1.190); AUDCAD thật −1.883 → **p = 0,44**:
  lưới này trên AUDCAD thật KHÔNG hơn giá chỉ có nhiễu cùng biên độ. 0/40 chuỗi nhiễu đạt luật chủ (lãi + DD < 80 %).
- **Xác nhận 2023-07 → 2025-02 (trong đời tín hiệu):** lãi ở cả 8 biến thể **+0,5 … +2,3 %/năm**, DD ≤ 2,6 % (2025 phủ 0,82 — kém).
  → cài đặt này "chạy" trong giai đoạn tín hiệu sống nhưng KHÔNG trong 5,5 năm trước đó.
- So với the-brain R6 (+8,45 %/năm khám phá): cùng cài đặt, brain2 ra −1,07 %/năm ngay cả không swap, spread thấp.
  Lý do khả dĩ (chưa tách riêng): engine cũ của the-brain lạc quan với tia lệnh (P1: +1…+33 điểm), lưới của the-brain
  không giới hạn 5 tầng như tín hiệu, phí sàn hằng số. Số +8,45 % **không tái lập được** trên brain2.

## 4. Đọc cho tiền
Cài đặt bóc từ 2023752, làm lại bằng luoi_duong, **không phải cơ chế bền**: lỗ đều từng năm 2018–2023 sau phí, không hơn
nhiễu; lãi chỉ xuất hiện ở 2023-07 → 2025-02 (trùng lúc tín hiệu sống). Ủng hộ nhánh "gặp may / hợp chế độ 2023–2026" của
giả thuyết gt id 4, không ủng hộ "cơ chế". G-b (hồi quy AUDCAD giúp lưới) không thấy ở cấu hình này (p = 0,44).
Giới hạn: lot thật, bien_cap, giờ dừng của tín hiệu chưa biết (bóc từ 449 lệnh); một tài sản; giá HistData ≠ giá XM;
2023 thiếu phút. Bước tiếp có giá trị tiền: chỉ khi có lịch sử lệnh đầy đủ (cần chủ đăng nhập MQL5) để bóc thêm luật
(giờ dừng, chốt theo tiền, lọc tin) — luật thiếu có thể là chỗ ra tiền thật của tín hiệu.
