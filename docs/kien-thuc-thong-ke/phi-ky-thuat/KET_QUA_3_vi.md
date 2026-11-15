# Kết quả kiểm định 3: XÁC SUẤT ĐI TIẾP qua các bậc Sq9 (vàng & S&P 500)

**Câu hỏi.** Trong trend, khi giá **đóng cửa xuyên qua mức A** của thang Sq9, xác suất giá đi tiếp tới B, C, D (1, 2, 3 bậc kế tiếp) là bao nhiêu?
Và xác suất hồi ngược về A là bao nhiêu? Câu hỏi phụ: thang Sq9 có cho xác suất khác các thang khác không?

**Dữ liệu.**
- 1h: GC=F và ES=F từ 06/2024, ^GSPC (giờ RTH) từ 12/2023. IS = nửa đầu, OOS = nửa sau.
- Daily: GC=F từ 2008, ES=F và ^GSPC từ 2000. IS < 2016 ≤ OOS.

**Thang.** L(j) = (√P + j·bước/180)². Bước 45°, 90°, 180°.
- Neo trên 1h: đóng cửa ngày trước, mở phiên, swing high/low 10/5.
- Neo trên daily: pivot 20/20. Neo chỉ dùng sau khi đã xác nhận.

**Trend** (không nhìn trước):
- EMA200 + dốc EMA, EMA50 + dốc EMA.
- Riêng 1h có thêm trend D1 (EMA50 ngày, tính trên ngày đã đóng).

**Sự kiện.** close[t−1] ≥ A và close[t] < A − 0.1 ATR (ngược lại khi phá lên). Mỗi mức chỉ tính lần phá đầu tiên của mỗi neo.

**Đo trong H nến** (1h: 10/24/48; daily: 5/10/20):
- Chạm B/C/D: bất kỳ lúc nào, và "trước khi close lấy lại A".
- Hồi chạm A, close lại qua A, hồi ≥ 50% bậc.
- MFE/MAE, số nến tới B.

**Baseline:**
1. **shift**: cùng neo, thang dời pha ngẫu nhiên (0–1 bậc trong không gian √).
2. **eqpct**: thang cách đều theo %, cùng khoảng cách quanh neo.
3. **vô điều kiện**: một nến bất kỳ cùng trạng thái trend đi được cùng khoảng cách (×ATR) theo cùng hướng trong H nến.

**Kiểm định.** Bootstrap theo cụm (tuần cho 1h, tháng cho daily), 1000 lần. FDR Benjamini–Hochberg trên toàn bộ 18 468 phép (H giữa, theo từng neo và gộp neo, ALL/IS/OOS).

---
## 1. Bảng tra thực dụng (gộp các neo, trend EMA200, H = 24 nến cho 1h / 10 phiên cho daily)
Ô ghi: **Sq9** (thang đều % / vô điều kiện cùng khoảng cách ATR). Bảng đầy đủ cho mọi trend, H và neo:
`results3/lookup_pooled_anchors.csv` và `results3/lookup_by_anchor.csv`.

| Mã | Khung | Bước | Trường hợp | n | 1 bậc ≈ ATR | →B % | →C % | →D % | →B trước khi lấy lại A % | Hồi chạm A % | Close lại qua A % | →B IS / OOS | Nến tới B (trung vị) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ES=F | 1d | 45° | phá THEO trend | 897 | 0.7 | 85 (85/86) | 57 (59/60) | 38 (38/40) | 71.0 | 84 (84) | 65.0 | 80 / 90 | 1.0 |
| ES=F | 1d | 45° | phá NGƯỢC trend | 747 | 0.7 | 81 (82/83) | 58 (58/59) | 40 (40/41) | 65.0 | 88 (87) | 77.0 | 75 / 86 | 1.0 |
| ES=F | 1d | 90° | phá THEO trend | 505 | 1.3 | 62 (61/65) | 31 (29/31) | 15 (14/15) | 53.0 | 83 (82) | 64.0 | 52 / 70 | 2.0 |
| ES=F | 1d | 90° | phá NGƯỢC trend | 440 | 1.2 | 62 (63/64) | 31 (33/33) | 16 (15/17) | 48.0 | 85 (84) | 75.0 | 50 / 73 | 2.0 |
| ES=F | 1d | 180° | phá THEO trend | 253 | 2.5 | 34 (31/33) | 9 (7/10) | 3 (2/4) | 26.0 | 83 (81) | 66.0 | 21 / 44 | 4.0 |
| ES=F | 1d | 180° | phá NGƯỢC trend | 226 | 2.4 | 33 (37/36) | 7 (8/11) | 2 (3/4) | 25.0 | 85 (83) | 74.0 | 17 / 45 | 3.0 |
| ES=F | 1h | 45° | phá THEO trend | 3116 | 2.4 | 58 (57/57) | 25 (25/27) | 11 (11/14) | 38.0 | 88 (88) | 77.0 | 61 / 54 | 5.0 |
| ES=F | 1h | 45° | phá NGƯỢC trend | 2521 | 2.4 | 60 (60/60) | 28 (28/31) | 12 (12/16) | 38.0 | 86 (87) | 76.0 | 57 / 64 | 6.0 |
| ES=F | 1h | 90° | phá THEO trend | 1790 | 5.0 | 25 (25/27) | 6 (6/8) | 2 (2/3) | 16.0 | 87 (88) | 77.0 | 28 / 21 | 10.0 |
| ES=F | 1h | 90° | phá NGƯỢC trend | 1493 | 5.0 | 27 (26/30) | 7 (7/9) | 3 (3/3) | 17.0 | 86 (87) | 76.0 | 27 / 27 | 10.0 |
| ES=F | 1h | 180° | phá THEO trend | 1273 | 11.0 | 5 (5/6) | 1 (1/1) | 1 (0/0) | 4.0 | 87 (87) | 76.0 | 7 / 3 | 12.5 |
| ES=F | 1h | 180° | phá NGƯỢC trend | 1091 | 11.4 | 6 (5/7) | 1 (1/1) | 0 (0/0) | 3.0 | 86 (87) | 77.0 | 8 / 3 | 13.5 |
| GC=F | 1d | 45° | phá THEO trend | 644 | 0.9 | 83 (83/80) | 59 (61/56) | 40 (42/38) | 68.0 | 82 (80) | 69.0 | 81 / 85 | 1.0 |
| GC=F | 1d | 45° | phá NGƯỢC trend | 517 | 0.8 | 78 (80/78) | 53 (53/51) | 30 (31/34) | 59.0 | 84 (84) | 74.0 | 76 / 79 | 1.0 |
| GC=F | 1d | 90° | phá THEO trend | 364 | 1.6 | 64 (65/60) | 31 (31/30) | 16 (18/16) | 52.0 | 77 (77) | 64.0 | 58 / 67 | 2.0 |
| GC=F | 1d | 90° | phá NGƯỢC trend | 292 | 1.5 | 59 (61/56) | 24 (26/26) | 10 (11/13) | 46.0 | 80 (81) | 69.0 | 57 / 60 | 3.0 |
| GC=F | 1d | 180° | phá THEO trend | 189 | 3.1 | 34 (34/32) | 12 (12/11) | 4 (3/5) | 28.0 | 77 (76) | 66.0 | 25 / 40 | 4.0 |
| GC=F | 1d | 180° | phá NGƯỢC trend | 147 | 2.8 | 27 (31/31) | 5 (8/10) | 3 (3/4) | 23.0 | 78 (79) | 67.0 | 26 / 28 | 3.5 |
| GC=F | 1h | 45° | phá THEO trend | 3547 | 1.8 | 65 (65/64) | 35 (35/36) | 18 (18/21) | 44.0 | 87 (87) | 75.0 | 48 / 75 | 4.0 |
| GC=F | 1h | 45° | phá NGƯỢC trend | 2897 | 1.8 | 63 (63/62) | 32 (32/34) | 18 (18/19) | 41.0 | 87 (88) | 75.0 | 53 / 69 | 4.0 |
| GC=F | 1h | 90° | phá THEO trend | 1938 | 3.7 | 36 (36/37) | 11 (11/14) | 4 (4/6) | 24.0 | 86 (85) | 73.0 | 16 / 48 | 9.0 |
| GC=F | 1h | 90° | phá NGƯỢC trend | 1605 | 3.6 | 33 (33/34) | 11 (11/12) | 5 (5/5) | 22.0 | 86 (87) | 73.0 | 20 / 42 | 8.0 |
| GC=F | 1h | 180° | phá THEO trend | 1263 | 8.2 | 10 (10/12) | 2 (2/3) | 1 (1/1) | 7.0 | 85 (85) | 73.0 | 1 / 17 | 13.0 |
| GC=F | 1h | 180° | phá NGƯỢC trend | 1078 | 8.1 | 9 (9/9) | 2 (2/2) | 1 (1/1) | 5.0 | 85 (87) | 73.0 | 3 / 14 | 13.0 |
| ^GSPC | 1d | 45° | phá THEO trend | 936 | 0.8 | 82 (84/83) | 54 (56/57) | 35 (36/38) | 66.0 | 82 (81) | 67.0 | 79 / 86 | 1.0 |
| ^GSPC | 1d | 45° | phá NGƯỢC trend | 762 | 0.8 | 76 (78/79) | 54 (56/55) | 38 (38/38) | 57.0 | 88 (86) | 77.0 | 72 / 81 | 1.0 |
| ^GSPC | 1d | 90° | phá THEO trend | 527 | 1.5 | 60 (59/62) | 28 (27/30) | 12 (12/15) | 48.0 | 79 (78) | 64.0 | 49 / 70 | 2.0 |
| ^GSPC | 1d | 90° | phá NGƯỢC trend | 443 | 1.4 | 57 (59/62) | 28 (30/31) | 14 (16/15) | 42.0 | 85 (82) | 75.0 | 46 / 67 | 2.0 |
| ^GSPC | 1d | 180° | phá THEO trend | 269 | 2.8 | 30 (28/32) | 8 (8/9) | 2 (2/4) | 22.0 | 78 (77) | 65.0 | 21 / 38 | 4.0 |
| ^GSPC | 1d | 180° | phá NGƯỢC trend | 241 | 2.7 | 30 (32/33) | 8 (9/9) | 2 (3/3) | 22.0 | 85 (81) | 74.0 | 17 / 41 | 3.0 |
| ^GSPC | 1h | 45° | phá THEO trend | 1941 | 1.6 | 76 (75/75) | 44 (44/47) | 23 (23/27) | 48.0 | 86 (85) | 77.0 | 78 / 73 | 4.0 |
| ^GSPC | 1h | 45° | phá NGƯỢC trend | 1602 | 1.6 | 73 (73/73) | 48 (48/50) | 31 (30/34) | 47.0 | 88 (87) | 81.0 | 71 / 76 | 3.0 |
| ^GSPC | 1h | 90° | phá THEO trend | 1079 | 3.2 | 48 (47/49) | 15 (15/17) | 5 (5/7) | 30.0 | 84 (83) | 75.0 | 52 / 43 | 9.0 |
| ^GSPC | 1h | 90° | phá NGƯỢC trend | 906 | 3.3 | 48 (48/51) | 20 (19/23) | 6 (5/10) | 29.0 | 87 (86) | 79.0 | 49 / 47 | 7.0 |
| ^GSPC | 1h | 180° | phá THEO trend | 718 | 6.9 | 15 (14/17) | 3 (2/4) | 1 (1/1) | 9.0 | 84 (82) | 75.0 | 19 / 9 | 10.5 |
| ^GSPC | 1h | 180° | phá NGƯỢC trend | 617 | 7.2 | 18 (18/20) | 2 (2/4) | 0 (0/2) | 13.0 | 86 (86) | 78.0 | 21 / 16 | 14.0 |

Đọc ví dụ: vàng 1h, bước 90° (1 bậc ≈ 3.7 ATR giờ), trend giảm theo EMA200 và giá đóng cửa xuyên xuống A:
trong 24 giờ, khoảng **36%** tới B, **11%** tới C, **4%** tới D, và khoảng **86%** hồi chạm lại A.

---
## 2. Sq9 có thêm gì so với baseline?
| baseline | so_phep | p_nho_hon_005 | qua_FDR | qua_FDR_Sq9_tot_hon | hieu_TB | hieu_tuyet_doi_TB |
|---|---|---|---|---|---|---|
| eqpct | 7182 | 324 | 26 | 19 | -0.0 | 0.59 |
| shift | 7182 | 675 | 100 | 3 | -0.66 | 1.8 |
| uncond | 4104 | 722 | 316 | 3 | -1.02 | 2.04 |

- **So với thang đều % (eqpct): hiệu trung bình 0.0 điểm, |hiệu| trung bình 0.6 điểm.** Thang Sq9 và thang đều % cho xác suất gần như trùng nhau.
- **So với thang dời pha (shift):** Sq9 hơi **kém** hơn (−0.7 điểm trung bình). Phần kém này nằm gần hết ở neo mở phiên / đóng cửa ngày trước trên 1h:

| tf | anchor | B | Bpre | C | D | closeA | ret50 | touchA |
|---|---|---|---|---|---|---|---|---|
| 1d | piv20 | -0.2 | 0.1 | 0.2 | 0.1 | -0.8 | -0.2 | -0.1 |
| 1h | dopen | -3.3 | -1.7 | -1.5 | -0.6 | 0.6 | -4.8 | 0.2 |
| 1h | pdc | -1.8 | -1.5 | -0.7 | -0.2 | 0.0 | -3.0 | -0.2 |
| 1h | swh | -0.5 | -0.2 | -0.3 | -0.2 | -1.6 | -2.9 | -1.0 |
| 1h | swl | 0.4 | -0.3 | 0.5 | 0.2 | 0.2 | -0.4 | 0.0 |

  Lý do: thang Sq9 (và thang đều %) luôn có **một mức ngay tại giá neo**. Khoảng 66–77% sự kiện là "phá giá mở phiên / đóng cửa ngày trước",
  và sau đó giá ít đi tiếp hơn (ES 1h bước 90°: 18.5% tới B, so với 41% khi phá mức xa hơn). Đây là đặc tính của **giá neo**, không phải của góc Gann.
  Với neo swing và pivot daily, Sq9 ≈ shift ≈ eqpct.
- Trong 7 182 phép so với thang đều %, chỉ 19 phép qua FDR theo hướng Sq9 tốt hơn. Đa số hiệu < 2 điểm. Lớn nhất là ES daily, tới C cao hơn 3–5 điểm, nhưng chủ yếu ở IS, và với ^GSPC (gần như cùng chuỗi giá) thì không lặp lại. **Khoảng cách Sq9 không thêm thông tin.**

## 3. Các xác suất này có giá trị giao dịch không (bỏ qua chuyện Gann)?
- **So với vô điều kiện:** xác suất tới B/C/D sau khi phá mức **không cao hơn**, mà còn thấp hơn khoảng 1 điểm (trung bình −1.0; trong 316 phép qua FDR thì chỉ 3 phép là phá mức tốt hơn).
  Nghĩa là "giá vừa đóng cửa qua một mức" **không cho thêm thông tin** so với chuyện giá trong trend đó có thường xuyên đi xa được ngần ấy ATR hay không.
  Xác suất tới B gần như chỉ phụ thuộc **1 bậc bằng bao nhiêu ATR**: khoảng 1 ATR thì ~80%, 2–3 ATR thì ~55–65%, 5 ATR thì ~25–35%, 8–11 ATR thì ~5–15%.
- **Phá theo trend so với ngược trend:** theo trend chỉ hơn khoảng +0.8 điểm trong việc tới B. Hiệu so với vô điều kiện: theo trend −0.5, ngược trend −1.4. **Không có lợi thế theo trend đáng kể.**
- **Hồi về A rất thường xuyên:** 77–88% số lần giá chạm lại A trong H nến, và 64–80% có close lấy lại A. Con số này đúng bằng vô điều kiện, tức là do biến động bình thường.
  Muốn vào lệnh theo hướng phá thì nên tính trước là phần lớn trường hợp giá sẽ retest A.
- **Kém ổn định theo thời gian nếu tính theo giá:** chênh lệch P(tới B) giữa IS và OOS có trung vị 9.5 điểm (10% số ô lệch > 24 điểm).
  Lý do là biến động thay đổi theo giai đoạn, ví dụ vàng 1h bước 180°: 1% ở IS so với 17% ở OOS. Nếu quy về khoảng cách ATR thì xác suất ổn định hơn nhiều, nhưng khi đó cũng chẳng còn liên quan gì tới Gann.

## 4. Kết luận
| Câu hỏi | Trả lời |
|---|---|
| (a) Xác suất "qua A → B/C/D" có dùng được để giao dịch? | Dùng được như **bảng mô tả biến động** (1 bậc = n ATR → xác suất tới). Nhưng phá mức **không tạo lợi thế** so với một nến ngẫu nhiên cùng trend; xác suất tính theo mức giá cũng không ổn định giữa các giai đoạn. |
| (b) Khoảng cách Sq9 có thêm gì? | **Không.** Giống thang đều %. Hơi kém thang dời pha, nhưng đó là do có mức ngay tại giá neo (mở phiên / đóng cửa hôm trước), không phải do góc Gann. |
| Hồi ngược trend | 77–88% chạm lại A, 64–80% close lấy lại A trong H nến. Bằng mức ngẫu nhiên, nên không phải tín hiệu. |

## Tái chạy
```
cd tools/kiem_dinh/gann_sq9
.venv/bin/python test_c_continuation.py   # results3/events.pkl (~200k sự kiện)
.venv/bin/python analyze_c.py             # results3/lookup_*.csv, tests.csv (~3 phút)
.venv/bin/python make_summary3.py         # KET_QUA_3_vi.md
```
