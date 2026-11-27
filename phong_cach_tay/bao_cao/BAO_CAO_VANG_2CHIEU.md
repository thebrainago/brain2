# Vàng tay_v2 — stress hai chiều và guard (sau đối chiếu MT5)

Xuất: 2026-11-27 21:55 (giờ Việt Nam, UTC+7, Asia/Saigon).

Không đặt lệnh thật. Vốn 10.000 USD = 1.000.000 USC. Sống = không cháy và DD < 80%.

`sp500/STRESS_CHUNG_VON.md` (commit `2d445567`) đo thấy mặc định 11/11 gãy khi vàng **tăng**: gap vàng +20% tại đáy vốn 18/06/2026 00:33 giờ VN cho tay XAU DD **11.765,26** trên 10k; +10% cũng vượt 80%. Bộ 11 stress cũ chỉ thử gap/grind **giảm**.

## Bộ stress mở rộng (15 kịch bản)

Thêm vào `chay_vang_11.stress_11(..., hai_chieu=True)`:

- gap **+10%** và **+20%** tại cùng đáy vốn Jun–Nov (2026-06-18 00:33 giờ VN, giá 4.381,98, tín hiệu đang bán, ADX 17,5 < 30 nên chưa khóa DCA).
- grind **+20%/60 ngày** và **+35%/120 ngày** từ 2026-06-01.

Cộng 4 giảm + 7 cửa sổ sập = **15**. Gap/grind tính lại ATR/ADX/EMA trên giá đã biến hình. Cửa sổ sập M5 không có delta15 (lọc trung tính). Gap/grind Jun–Nov giữ đồng hồ nên vẫn áp được delta15 khi cấu hình dùng lọc đó.

Tại đáy vốn, tín hiệu là **bán**. Gap tăng đánh vào cụm ngắn; `loss_close` 30% vẫn cắt một rổ (lỗ thả nổi mặc định chỉ −3.116), nhưng vào lại chiều ngắn sau dịch mức +20% (biên đô-la lớn hơn) làm DD chồng — đó là nguồn DD 117,65%, không phải một nhát mark-to-market 11k.

## Mặc định 59672872 trên bộ 15 (lọc delta15)

Jun–Nov gốc không đổi: +15.930,00, DD 31,08%.

| scenario | net USD | DD% | sống |
|---|---:|---:|---|
| gap−10% tại đáy vốn | 10412,54 | 47,26 | có |
| gap−20% tại đáy vốn | 7951,10 | 45,81 | có |
| grind−20%/60 ngày | 9051,15 | 39,77 | có |
| grind−35%/120 ngày | 2503,84 | 44,48 | có |
| **gap+10% tại đáy vốn** | 5682,69 | **92,04** | **không** |
| **gap+20% tại đáy vốn** | 1352,08 | **117,65** | **không** |
| grind+20%/60 ngày | 10423,32 | 47,19 | có |
| grind+35%/120 ngày | 6367,51 | 62,81 | có |
| Q4-2018 | −1877,80 | 33,24 | có |
| Covid 02-04/2020 | 2754,73 | 64,87 | có |
| 2022 H1 | 2605,68 | 49,59 | có |
| 2022 08-10 | −791,28 | 35,80 | có |
| 08-10/2023 | 552,13 | 27,47 | có |
| 07-08/2024 | 1375,01 | 19,45 | có |
| 02-04/2025 | 2194,89 | 51,65 | có |

**13/15.** Gap +20% DD 11.765,26 USD khớp đúng số stress chung vốn. Bản không delta15 cũng 13/15, cùng hai kịch bản gãy. Grind tăng thì sống.

Chỉ kéo dài cooldown (1.380–20.000) hoặc chỉ `max_lc` 1–3, hoặc chỉ trần short 0,08–0,12, hoặc cấm short hẳn: **không** đủ 15/15 (cấm short còn 11/15). Trần short 0,04 đơn độc: 14/15, gãy 02–04/2025 (DD 109,29%).

## Ứng viên sống 15/15

Hai lớp guard mới trong `may_v2` (P[29] `max_lc`, P[30] `short_cap`; 0 = tắt, không đổi số cũ khi không bật):

1. **`short_cap=0,04`** — trần tổng lot chiều ngắn (cụm vào + DCA). Chiều dài không cắt.
2. **`max_lc=N`** — sau N lần đóng lỗ tổng thì không mở rổ mới đến hết cửa sổ (cầu dao).
3. Kết hợp với **cooldown dài** sau đóng lỗ (không cần tắt hẳn máy).

| ten | Jun–Nov net / DD | spr×2 net / DD | stress 15 | tệ nhất net / DD | 2025.09–2026.11 không d15 net / DD |
|---|---|---|---:|---|---|
| gốc 59672872 | +15.930,00 / 31,08% | +9.181,92 / 45,00% | 13/15 | +1.352 / **117,65%** | **−10.012,57 / 110,37% (cháy 11/02 22:03)** |
| short_cap 0,04 + max_lc 2 | +9.959,63 / 21,74% | +8.867,26 / 21,74% | **15/15** | −3.655,43 / 69,34% | −2.675,63 / 35,27% (không cháy, **dừng sau 2 lần đóng lỗ**, OOS=0) |
| **short_cap 0,04 + cooldown 20.000** | **+9.959,63 / 21,74%** | **+8.867,26 / 21,74%** | **15/15** | −2.207,69 / 66,08% | **+2.359,88 / 66,24% (không cháy)** |

Cùng Jun–Nov với `short_cap=0,04` (trần 30% lỗ tổng không kích trên cửa sổ gốc): IS +4.446,83 / OOS +5.512,80, Sharpe 3,310, lỗ thả nổi tệ nhất −2.122,56, max lots chiều ngắn bị kẹp 0,04 (chiều dài vẫn có thể lên 0,30).

### `short_cap=0,04` + cooldown 20.000 nến M1 (~14,5 ngày theo 1.380 nến/ngày) — đề xuất ứng viên

20.000 nến ≈ 14–15 ngày phiên, rồi được vào lại. Không phải tắt máy vĩnh viễn.

Jun–Nov (có delta15): **+9.959,63 USD (995.963 USC), DD 21,74%**. IS +4.446,83 (444.683 USC) / OOS +5.512,80 (551.280 USC). Spread×2 +8.867,26 / DD 2.173,62 (21,74%).

15 stress (sống đủ):

| scenario | net USD | DD% | sống |
|---|---:|---:|---|
| gap−10% | 4574,80 | 54,81 | có |
| gap−20% | 1606,90 | 66,08 | có |
| grind−20%/60 ngày | 16116,87 | 15,15 | có |
| grind−35%/120 ngày | 11020,61 | 26,36 | có |
| gap+10% | 1766,45 | 56,86 | có |
| gap+20% | 14445,65 | 55,68 | có |
| grind+20%/60 ngày | 5369,50 | 61,26 | có |
| grind+35%/120 ngày | 14379,26 | 50,29 | có |
| Q4-2018 | −2207,69 | 31,78 | có |
| Covid 02-04/2020 | −765,54 | 57,35 | có |
| 2022 H1 | 243,16 | 35,07 | có |
| 2022 08-10 | 1920,23 | 17,83 | có |
| 08-10/2023 | 1266,87 | 27,47 | có |
| 07-08/2024 | 2160,44 | 19,45 | có |
| 02-04/2025 | −901,37 | 39,74 | có |

Tệ nhất lãi: Q4-2018 −2.207,69. Tệ nhất DD: gap−20% 66,08%.

Cửa sổ dài 2025.09.01–2026.11.27, **không delta15** (cùng cửa sổ MT5): **+2.359,88 USD (235.988 USC), DD 66,24%**, không cháy, lỗ thả nổi tệ nhất −4.832,80, equity thấp nhất 4.125,20 lúc 2026-03-05 20:23 giờ VN. IS +3.903,87 / **OOS −1.543,99**. Spread×2 cửa sổ này **−5.629,73, DD 93,34% — không đạt**. Sharpe 0,250.

Đường vốn cửa sổ dài (ứng viên):

| Tháng | Equity cuối | Thấp nhất | DD từ đỉnh |
|---|---:|---:|---:|
| 2025-09 | 8.713,3 | 8.460,8 | 21,29% |
| 2025-10 | 6.958,7 | 6.316,5 | 41,24% |
| 2025-11 | 5.521,8 | 5.521,8 | 48,63% |
| 2025-12 | 8.548,5 | 5.372,3 | 50,02% |
| 2026-01 | 6.374,2 | 6.374,2 | 40,70% |
| 2026-02 | 5.250,2 | 5.250,2 | 51,16% |
| 2026-03 | 6.438,2 | 4.125,2 | 61,62% |
| 2026-04 | 8.824,6 | 5.939,4 | 44,75% |
| 2026-05 | 11.797,8 | 6.783,0 | 42,57% |
| 2026-06…09 | hồi tới 13.903,9 (cuối 9) |  | đỉnh sau đó DD OOS ~33% |
| 2026-11 | 12.359,9 | 10.712,3 | 33,30% |

### Lân cận (đo)

- `short_cap=0,04` + cooldown 13.800: Jun–Nov giống, 15/15 (DD tệ 60,13%), cửa sổ dài +1.815,73 / DD 71,26%; spr×2 dài −4.583,90 / 94,81% — không đạt spr×2 dài.
- `short_cap=0,04` + cooldown 27.600: Jun–Nov giống, 15/15 (DD tệ 69,00%), cửa sổ dài **−8.176,03 / DD 95,05%** — không đạt.
- `short_cap=0,04` + cooldown 1.380 hoặc 2.760: 15/15 trên Jun–Nov stress, nhưng cửa sổ dài DD 101–105%.
- `short_cap=0,03` + max_lc 2: 15/15, Jun–Nov chỉ +1.545,04 / DD 41,87%.
- `short_cap=0,05` + max_lc 2: 13/15, gãy gap−10% và gap+20%.
- `short_cap=0,04` + max_lc 1 hoặc 3: 15/15 Jun–Nov; cửa sổ dài vẫn âm vì cầu dao dừng sớm (OOS=0).

`max_lc=2` là cầu dao sống tốt trên bộ 15 và không cháy cửa sổ dài, nhưng **ngừng giao dịch sau 2 lần đóng lỗ** (trên cửa sổ dài là tháng 10/2025), nên không lấy được đoạn lãi Jun–Nov nếu chạy liên tục từ 09/2025.

## Kiểm 7 bước — chỉ trên Jun–Nov, ứng viên short_cap 0,04 + cooldown 20.000

1. IS/OOS: **đạt** — IS +4.446,83, OOS +5.512,80; DD Jun–Nov 21,74%.
2. Spread ×2: **đạt** — +8.867,26, DD 21,74%.
3. Stress: **đạt 15/15** (bộ cũ 11 cộng 4 kịch bản vàng tăng).
4. Lân cận: ổn với cooldown 13.800–20.000 và `max_lc` 1–3 khi giữ `short_cap=0,04`; **vỡ** khi `short_cap=0,05` (13/15) hoặc cooldown 27.600 trên cửa sổ dài.
5. Lỗ thả nổi vs 80%: đạt Jun–Nov (−2.122,56 = 21,23% vốn). Tệ nhất bộ 15: gap−20% DD 66,08%.
6. Sharpe Jun–Nov 3,310. DSR kiểu cũ vẫn không phân biệt (nhóm trước = 1,00).
7. Nhật ký bóng: không đặt lệnh; số nằm ở `ket_qua/vang_2chieu_*.csv`.

**Chưa đạt 7 bước trên cửa sổ 2025.09–2026.11:** OOS lỗ, spread×2 DD 93,34%. Chưa chạy lại Strategy Tester p4 cho ứng viên này (chỉ đo Python). EA đã thêm `InpShortCap` và `InpMaxLc`, **mặc định 0** để bản EA vẫn khớp test MT5 của `59672872`.

## Kết luận (chỉ số đo)

1. Mặc định `59672872` **không** chịu cửa sổ tick 2025.09–2026.11 (MT5 −9.994,02 / DD 99,94%; Python −10.012,57 / DD 110,37%) và **không** chịu gap vàng +10%/+20% (DD 92,04% / 117,65%).
2. Guard sống đủ hai chiều trên Jun–Nov: **`short_cap=0,04` + cooldown 20.000 nến** (và biến thể cầu dao `short_cap=0,04` + `max_lc=2`).
3. Ứng viên cooldown 20.000 còn **lãi +2.359,88, DD 66,24%, không cháy** trên đúng cửa sổ MT5 (Python, không delta15) — nhưng OOS và spread×2 cửa sổ đó chưa đạt. Chưa xác nhận bằng tick MT5.

File: `ma/may_v2.py`, `ma/chay_vang_11.py`, `ma/chay_vang_2chieu.py`, `vang/ea/VANG_TayV2.mq5`. Số: `ket_qua/vang_2chieu_*.csv`, `ket_qua/vang_tayv2_th9_th11_mt5.json`. Không sửa `tin_hieu_data.py`.
