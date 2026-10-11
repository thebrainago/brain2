# G08 — G-a "quản trị rổ quyết định hơn entry?" trên AUDCAD / EURGBP (11/10/2026)

Mọi số là **MÔ PHỎNG** (`nhan/luoi_duong`, M1 HistData công khai) — không phải tiền thật, không phải MT5.
Kế hoạch đóng băng TRƯỚC khi chạy: `G08_KE_HOACH.json` sha `d065186fb65a7bcc`, commit `1e21217b` (đã push trước khi có số).
Chạy: `/workspace/venv/bin/python hieu_chuan/g08_quan_tri_ro.py --nhan 2` (1848 lần chạy, 16.156 s ≈ 4,5 giờ, 2 nhân) → `g08_ket_qua.json`.
(Bản chạy đầu 7 nhân kẹt ở 400/1848 hơn 3 giờ → đã cắt, chạy lại 2 nhân; kế hoạch và sha không đổi.)

## Thiết lập
Như G07 (lưới 2023752, chuyển k theo biên độ năm trước, 7 năm hợp lệ 2018–2022, 2024, 2025, vốn 10.000 USD mới mỗi năm,
spread cao + swap tháng cho luật, spread thấp + swap báo thêm). 6 biến thể quản trị đăng ký trước, KHÔNG quét:
V0 gốc · V1 bước ×2 (42,4 pip) · V2 tối đa 10 tầng · V3 bỏ TP, đuôi đỉnh 7,6/3,8 · V4 bỏ TP, chốt rổ ≥ 1 USD · V5 gốc + dừng rổ sau 120 giờ.
Nhiễu: CÙNG 20 seed đảo dấu từng nến M1 cho mọi biến thể. **Kiểm chéo:** V0 = G07 từng số (AUDCAD −2.154,81; EURGBP −3.125,18 USD).

## Kết quả (spread cao + swap; tổng 7 năm)

| Biến thể | Tài sản | tổng USD | trung vị %/năm | spread thấp %/năm | maxDD max | năm đạt luật chủ (thật) | tỉ lệ năm nhiễu đạt | p hơn nhiễu | Δ so V0 USD | p hơn gốc |
|---|---|---|---|---|---|---|---|---|---|---|
| V0 gốc | AUDCAD | −2.155 | −2,13 | −1,14 | 7,0 % | 0/7 | 5 % | 0,14 | — | — |
| V0 gốc | EURGBP | −3.125 | −5,33 | −2,47 | 14,2 % | 1/7 (2018) | 6 % | 0,095 | — | — |
| V1 bước ×2 | AUDCAD | −2.004 | −2,51 | −1,72 | 10,8 % | 1/7 (2024) | 12 % | 0,38 | +151 | 0,95 |
| V1 bước ×2 | EURGBP | −2.727 | −4,13 | −2,80 | 14,6 % | 1/7 (2018) | 17 % | 0,24 | +398 | 0,86 |
| V2 10 tầng | AUDCAD | −3.909 | −3,37 | −2,17 | 21,4 % | 1/7 (2024) | 24 % | 0,38 | −1.754 | 0,62 |
| V2 10 tầng | EURGBP | −1.692 | −2,67 | +0,03 | 20,3 % | 3/7 (2018, 2020, 2022) | 26 % | 0,14 | +1.433 | 0,19 |
| V3 đuôi đỉnh | AUDCAD | −2.160 | −1,98 | −1,04 | 7,1 % | 0/7 | 7 % | 0,19 | −6 | 0,71 |
| V3 đuôi đỉnh | EURGBP | −3.073 | −5,01 | −2,29 | 11,0 % | 1/7 (2018) | 9 % | 0,14 | +52 | 0,57 |
| V4 chốt 1 USD | AUDCAD | **−1.408** | −1,31 | −0,46 | 6,6 % | 1/7 (2024) | 9 % | 0,14 | +747 | 0,43 |
| V4 chốt 1 USD | EURGBP | −3.965 | −5,48 | −2,63 | 12,9 % | 1/7 (2018) | 6 % | 0,19 | −839 | 0,81 |
| V5 dừng 120 h | AUDCAD | −2.920 | −3,52 | −0,96 | 9,2 % | 0/7 | 0 % | **0,048** | −765 | **0,048** |
| V5 dừng 120 h | EURGBP | −5.308 | −4,57 | −1,45 | 18,9 % | 0/7 | 0 % | **0,048** | −2.183 | 0,095 |

Không năm nào stop-out; maxDD mọi ô ≤ 21,4 %. **Không (biến thể, tài sản) nào LAI** (tổng 7 năm > 0).

## Kết luận theo luật đóng băng: **G-a MỘT PHẦN** — nhưng về tiền là **BÁC BỎ thực chất**
- `ung_vien` = [] (không ô nào LAI). `mot_phan` = V5/AUDCAD, V5/EURGBP — chỉ vì p hơn nhiễu = 0,048 (mức nhỏ nhất có thể với 20 seed).
- Đọc đúng V5: dừng rổ sau 120 giờ làm giá thật **lỗ NHIỀU HƠN** gốc (−765 / −2.183 USD), nhưng làm chuỗi nhiễu lỗ còn nặng hơn
  (nhiễu trung vị −9,1 / −14,0 %/năm). "Hơn nhiễu" = "đỡ tệ hơn nhiễu", không đưa gì lại gần tiền. p hơn gốc 0,048 trên AUDCAD
  cũng vậy: Δ âm nhưng ít âm hơn Δ trên nhiễu. Với 12 phép so, một ô p ≤ 0,05 xảy ra do may ~46 % (đã ghi trong kế hoạch).
- Biến thể tốt nhất theo tiền: **V4 chốt rổ ≥ 1 USD trên AUDCAD** — vẫn lỗ −1.408 USD/7 năm (−1,31 %/năm trung vị; spread thấp −0,46),
  p hơn nhiễu 0,14, p hơn gốc 0,43 → không đạt gì. V2 EURGBP có 3/7 năm đạt luật chủ và spread thấp ~0 (+0,03 %/năm), nhưng nhiễu
  cùng biến thể cũng đạt 26 % số năm và DD gấp đôi → không hơn may.
- Luật chủ (lãi + DD < 80 %) theo năm: tối đa 3/14 ô-năm (V2), các biến thể khác 0–2/14; tỉ lệ này ngang tỉ lệ năm nhiễu đạt.
- Kết luận: với lưới 2023752 trên hai cặp chéo, **đổi quản trị rổ (trong 5 cách đã khóa) không biến lỗ thành lãi sau phí**; phí
  (spread + swap) vẫn là thứ quyết định. Không nới cổng.

## Giới hạn
Chỉ 5 cách quản trị, một bộ entry (2023752), hai tài sản; phần "đổi entry" của G-a chưa làm. Giá HistData ≠ giá sàn; spread lịch sử
CHƯA ĐO ĐƯỢC (hằng số thấp/cao). 20 seed nhiễu → p nhỏ nhất 0,048. Không MT5.
