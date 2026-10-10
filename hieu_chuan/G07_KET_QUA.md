# G07 — G-b "chọn tài sản": lưới có lãi trên tài sản hồi quy, không trên chỉ số? (11/10/2026)

Mọi số là **MÔ PHỎNG** (`nhan/luoi_duong`, M1 HistData công khai) — không phải tiền thật, không phải MT5.
Kế hoạch đóng băng TRƯỚC khi chạy: `G07_KE_HOACH.json` sha `eddb7e748b7924e9`, commit `85249b90` (đã push trước khi có số).
Chạy: `/workspace/venv/bin/python hieu_chuan/g07_chon_tai_san.py` (805 lần chạy, 29 phút, 7 nhân) → `g07_ket_qua.json`.

## Thiết lập (tóm tắt — đầy đủ trong kế hoạch)
- Luật lưới G06 (tín hiệu 2023752): bước 21,2 pip ×1,2, lot cộng 0,25 từ 0,01, TP 7,6, tỉa lệnh, 5 tầng, hai chiều, vốn 10.000 USD
  mới mỗi năm, đòn bẩy 100. Không tối ưu.
- Chuyển sang tài sản khác: giá × k_y = R_AUDCAD(y−1)/R(y−1) (R = trung vị biên độ ngày năm trước) → mỗi tầng = cùng phần biên độ ngày
  như AUDCAD; spread nhân cùng k. AUDCAD k = 1 → năm 2018 −5,54 %/năm **trùng G06 từng số** (kiểm chéo).
- Năm 2023 bị loại ở cả 5 tài sản (HistData thiếu ~13 % nến) → 7 năm hợp lệ: 2018–2022, 2024, 2025.
- Phí: spread thấp/cao + swap tháng (xem kế hoạch). Chỉ số: swap là GIẢ ĐỊNH ∓(r_USD ± 2,5 %), bỏ cổ tức.

## Kết quả (biến thể xấu nhất có swap; nhiễu = 20 chuỗi đảo dấu từng nến M1, spread cao + swap)

| Tài sản | nhóm | năm lãi | trung vị %/năm | không swap (spread thấp) | maxDD max | stop-out | tổng 7 năm | nhiễu: trung vị %/năm, năm lãi | p hơn nhiễu | p kém nhiễu |
|---|---|---|---|---|---|---|---|---|---|---|
| AUDCAD | hồi quy | 0/7 | −2,13 | +0,21 (4/7 năm lãi) | 7,0 % | 0 | −2.155 USD | −4,44; 5 % | 0,14 | 0,90 |
| EURGBP | hồi quy | 1/7 | −5,33 | −0,14 (3/7) | 14,2 % | 0 | −3.125 USD | −7,18; 6 % | 0,095 | 0,95 |
| XAUUSD | hồi quy | 0/7 | −3,89 | −2,55 (1/7) | 20,6 % | 0 | −4.057 USD | −2,09; 30 % | 0,95 | 0,095 |
| NSXUSD | chỉ số | 0/7 | −5,11 | −4,24 (2/7) | 17,3 % | 0 | −5.248 USD | −3,71; 19 % | 0,90 | 0,14 |
| SPXUSD | chỉ số | 0/7 | −11,97 | −9,79 (0/7) | 24,2 % | 0 | −9.166 USD | −5,00; 16 % | 1,00 | **0,048** |

## Kết luận theo luật đóng băng: **G-b BÁC BỎ** (trên mô phỏng brain2, bộ luật này)
- Không tài sản "hồi quy" nào LÃI sau phí; không cái nào hơn nhiễu với p ≤ 0,05. Luật chủ (lãi + DD < 80 %): **0/5 tài sản đạt**.
- Phần ĐÚNG HƯỚNG của G-b (chỉ là xu hướng, không đạt ngưỡng): hai cặp chéo FX tốt hơn chuỗi nhiễu của chính nó (p 0,14 / 0,095),
  hai chỉ số kém hơn nhiễu (SPX p 0,048 — đáng kể; NAS 0,14). Tức hồi quy cặp chéo có giúp lưới một chút, xu hướng chỉ số có hại —
  nhưng phần giúp nhỏ hơn phí: AUDCAD không swap + spread thấp chỉ +0,21 %/năm trung vị, có swap −2,13.
- **Vàng KHÔNG cư xử như cặp chéo** ở đây: kém nhiễu (p 0,095), 2025 −18,6 %/năm (xu hướng tăng mạnh). Gợi ý the-brain "vàng 7/8
  hồi quy" không chuyển thành lãi lưới.
- DD đều thấp (≤ 25 %) vì lưới chỉ 5 tầng + lot nhỏ: lỗ đến từ phí + chốt lỗ cuối năm, không phải cháy tài khoản.

## Giới hạn
Một bộ luật (2023752) chuyển theo biên độ — luật khác (nhiều tầng hơn, lot nhân) có thể khác; không quét để tránh chọn bừa (P4).
Giá HistData ≠ giá sàn; swap chỉ số là giả định; spread lịch sử CHƯA ĐO ĐƯỢC (dùng hằng số thấp/cao). Không MT5.
