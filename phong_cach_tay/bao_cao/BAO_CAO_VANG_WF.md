# Vàng tay_v2 — tối ưu cửa sổ đầy 2025.09–2026.11, walk-forward, đối chiếu MT5

Xuất: 2026-11-27 22:25 (giờ Việt Nam, UTC+7, Asia/Saigon).

Không đặt lệnh thật. Vốn 10.000 USD = 1.000.000 USC (100 USC = 1 USD). Tiêu chí sống: lãi > 0, DD < 80% vốn ban đầu, trên **cả** cửa sổ đầy và **mỗi** fold walk-forward, spread ×2, 15 stress hai chiều. Cửa sổ: 2025.09.01–2026.11.27, **không lọc delta15** (tín hiệu đó không có trước tháng 6).

Commit `1b487659` đã đẩy lên `origin/main` (push thường, không force): `2d445567..1b487659`.

**Kết luận ngắn:** ứng viên Python `flat_orphan=1`, `maxL=8` đạt mọi cửa Python (+57.231,94 / DD 13,14%, WF 12/12, stress 15/15, spr×2 đạt) nhưng **thất bại hoàn toàn trên MT5 p4 tick thật** (net −9.993,99, DD 99,94%). Máy Python **không** phải proxy đáng tin trên cửa sổ này. Chưa có cấu hình nào đạt tiêu chí trên MT5 full window. Không đưa ra mặc định sống để giao dịch.

## 1. Bài học cửa sổ Jun–Nov

Cửa sổ Jun–Nov 2026 bắt đầu **sau** khi mặc định 59672872 đã cháy nếu chạy từ 09/2025, nên giấu cú sập. Python mặc định (cùng cửa sổ đầy, không lọc): net −10.012,57, DD 110,37%, cháy 11/02/2026 22:03 giờ VN. MT5 mặc định (p4, tick thật, cùng cửa sổ, 21:38:15–21:42:33 giờ VN, 257 giây): net −9.994,02, DD 99,94%, 10.557 lệnh, PF 0,21, hết tiền 05/02/2026 02:30 giờ VN (equity 30,42). Hai bên cùng cháy, nhưng đường vốn giữa chừng **không giống nhau** (mục 3).

## 2. Chẩn đoán Python: tháng 1–2/2026 (mặc định, không lọc)

Trên máy Python, vàng đi một chiều lên kèm dao động lớn: 4.325,53 (01/01) → 5.076,46 (12/02), **+17,36%**, đỉnh 5.598,01 ngày 29/01, rồi đổ 295 điểm ngày 30/01 (5.280 → 4.985). Trong tháng 1, slope gần như luôn dương (38.873 nến + / 299 nến −).

Đường vốn Python mặc định: cuối 12/2025 còn 9.654; đỉnh ~10.989 (09/01); 21/01 còn 7.989 sau một rổ −3.321,97; 29/01 còn 3.531; 30/01 còn 1.964; cháy 11/02/2026 22:03 giờ VN, equity −12,57.

Tám rổ lỗ kiểu đóng lỗ tổng (pnl ≤ −1.000) cộng −18.334 USD. Tháng 1 có 6 rổ nặng:

| Mở (giờ VN) | Đóng | pnl | lot | giá vào→ra | tín hiệu | slope / ADX |
|---|---|---:|---:|---|---:|---|
| 09/01 22:40 | 21/01 08:27 | −3.321,97 | 0,20 | 4.513→4.822 (giá lên) | mua | +1 / 24,8 |
| 23/01 15:07 | 28/01 08:07 | −2.589,69 | 0,24 | 4.945→5.198 (giá lên) | mua | +1 / 17,3 |
| 29/01 03:55 | 29/01 06:39 | −2.188,76 | 0,26 | 5.371→5.588 | **bán** | +1 / 19,8 |
| 29/01 21:50 | 29/01 22:10 | −1.527,94 | 0,30 | 5.507→5.425 | mua đỉnh | +1 / 23,6 |
| 30/01 16:50 | 30/01 17:37 | −1.275,19 | 0,21 | 4.965→5.079 | mua | +1 / 55,2 |
| 30/01 21:52 | 30/01 22:02 | −1.030,63 | 0,27 | 5.078→4.990 | mua | +1 / 46,8 |

Hai rổ “mua” đầu đóng lỗ nặng trong khi giá đóng **cao hơn** giá vào: lệnh chính đã chạm TP +4 trên sóng lên, hedge 1× bị bỏ lại, máy coi như **lật rổ sang bán** (`n_main=0` thì `main_s = −side[0]`) rồi còn có thể DCA chiều ngắn đúng lúc vàng tăng. Trên Python, đây là cơ chế giết tài khoản, không phải “thiếu short_cap” là chính (tổng rổ Dec–Feb: mua −6.709, bán −440). ADX lúc mở hai rổ lớn < 30 nên khóa DCA ngược không kích. Cooldown 240 nến (~4 giờ) không chặn chồng đóng lỗ 30% trên equity đang teo. Guard then chốt phía Python: `flat_orphan=1` (đóng hedge mồ côi, không lật rổ).

## 3. Chẩn đoán MT5: cháy từ tháng 10/2025, không đợi tháng 1

Đối chiếu p4, GOLD.i#, every tick based on real ticks, 2025.09.01–2026.11.27, vốn 10k, đòn 1:500. Thời gian lệnh bên dưới là giờ máy chủ XM (Europe/Athens; giờ VN = Athens +4 mùa hè / +5 mùa đông).

### 3.1. Ứng viên Python `maxL=8` + `FlatOrphan=1` (EA v1.01)

Chạy 22:05:34–22:10:14 giờ VN, 278 giây, PID terminal 1404, magic 2026112792. Compile ok. Input đúng: InpMaxL=8, InpFlatOrphan=1, InpMaxLc=0, InpShortCap=0, các thông số khác giữ 59672872. 439.543 nến, 109.154.552 tick, 100% real ticks.

| Chỉ số MT5 | Số |
|---|---:|
| Lãi ròng | **−9.993,99 USD** |
| DD vốn (balance) tối đa | 10.085,48 (99,94%) |
| DD equity tối đa | 10.039,98 (99,94%) |
| PF | 0,28 |
| Số lệnh | 20.625 (mua 14.838 / bán 5.787) |
| Lệnh thắng | 20.469 (99,24%), trung bình +0,19 |
| Lệnh thua | 156 (0,76%), trung bình −89,08 |
| Thắng / thua lớn nhất | +56,91 / −408,60 |
| Chuỗi thua tối đa | 8 lệnh, **−3.002,40** (đúng rổ 01/10) |
| Swap / hoa hồng trên báo cáo | 0,00 / 0,00 |
| Đỉnh balance | 10.091,49 lúc 2025.09.04 16:42:27 Athens |
| Balance < 8.000 | 2025.10.01 10:52:31 (7.906,29) |
| Balance < 2.000 | 2026.01.02 20:15:05 (1.927,11) |
| Balance < 10 | 2026.01.19 13:41:12 (8,20) |
| Kết thúc | 6,01 lúc 2026.06.10 18:05:13 (gần như chết từ giữa tháng 1) |

Đường vốn theo tháng (balance cuối sau lệnh đóng):

| Tháng | Balance cuối | Ghi chú |
|---|---:|---|
| 2025.09 | 10.091,49 (chốt 05/09 15:30 — sau đó chỉ **nắm** 8 lệnh bán) | |
| 2025.10 | 3.061,51 | bốn rổ đóng lỗ chồng |
| 2025.11 | 2.790,65 | |
| 2025.12 | 2.264,08 | |
| 2026.01 | 8,20 (19/01) | chết chức năng |
| 2026.03 / 06 | 8,24 / 6,01 | vài lệnh tàn |

Rổ đóng lỗ tổng 01/10/2025 10:52:31 Athens: **8 lệnh T2_DCA bán**, tổng **−3.002,40 USD** (đúng ~30% equity lúc mở rổ). Vào 02–05/09 (3.505,91–3.566,95), nắm suốt rally đến 3.878,42 (~một tháng). Lệnh chính gốc đã TP/đóng trước đó; máy tiếp tục DCA bán đến `maxL=8`, rồi `loss_close` 30%. Đây **không** phải hedge mồ côi (`T2_HEDGE`) — `FlatOrphan` không chặn được rổ bán DCA ngược sóng tăng.

Các ngày lỗ nặng tiếp theo (các lệnh lỗ < −10 USD cộng lại): 16/10 −2.163,84 (8 bán, vào ~4.005–4.083, đóng 4.303); 21/10 −1.644,71 (8 mua DCA, đổ trong ngày 4.353→4.164); 28/10 −1.158,00 (5 mua DCA); 14/11 −973,53; 12/12 −907,61; 29/12 −859,69; 02/01 −901,75 (gồm 4 `T2_HEDGE` bán). Tài khoản chết vì **chồng loss_close** hai chiều, bắt đầu từ rổ bán tháng 9–10, không phải chỉ short_cap hay chỉ tháng 1–2.

`short_cap` một mình **không đủ**: 0,04 lot × sóng 400 USD ≈ 1.600 USD, trong khi ngưỡng `loss_close` 30% vẫn là 3.000 USD — rổ nhỏ hơn sẽ bị nắm lâu hơn cho đến khi lỗ chạm 3.000.

### 3.2. Mặc định 59672872 trên MT5 (maxL=20, không FlatOrphan) — để so

Cùng tester, 21:38:15–21:42:33 giờ VN: net −9.994,02, DD 99,94%, 10.557 lệnh. Đỉnh 10.151,20 (17/09 21:01). **Cuối 09/2025 đã còn 7.222,83** (thấp 7.149,01). Tháng 10 còn dữ liệu đóng đến 03/10 (7.384,80) rồi nhảy sang tháng 12 (4.001,64) — nhiều khả năng nắm rổ dài. 30/01 còn 597,89; 05/02 còn 8,56; kết 5,98. Vậy MT5 mặc định cũng đã mất ~28% trong tháng 9, trong khi Python mặc định cuối tháng 12 vẫn ~9.654. Hai máy **đã lệch từ tháng 9**, dù cùng cháy vào tháng 1–2.

### 3.3. Python cùng cấu hình `maxL=8` + `flat_orphan=1` — lệch hoàn toàn

Cửa sổ Python (giờ VN, i0=400 nên bắt đầu 2025-09-01 11:40, bỏ ~5,5 giờ đầu 01/09 so với lệnh MT5 01:05 Athens):

| Tháng | Python equity cuối (thấp nhất) | MT5 balance cuối |
|---|---:|---:|
| 09/2025 | 11.833 (thấp 9.987) | 10.091 (nắm 8 bán từ 05/09) |
| 10/2025 | 14.873 (thấp 11.630) | **3.062** |
| 11/2025 | 17.065 | 2.791 |
| 12/2025 | 20.461 | 2.264 |
| 01/2026 | 26.716 (thấp 20.124, sống) | **8,20** |
| 11/2026 | 67.232 | 6,01 |

Python ngày 01/10: cuối 11.940, thấp 11.728 — **không có** rổ −3.002. pv=100, L0=0,01 đúng hệ số vàng XM, nên đây không phải lỗi nhân 100. Máy Python không mở/không nắm rổ bán 8 tầng suốt 02/09–01/10 (M1 OHLC, lệch múi giờ đặc trưng, lệch tín hiệu, hoặc TP/DCA khác tick thật). Do đó mọi số Python (WF 12/12, 15/15, spr×2, +57k / DD 13%) **không được coi là đã xác minh**.

## 4. Kết quả quét Python (chỉ để lưu, đã bị MT5 bác)

Giữ L0=0,01 K=4 TP=4,00 khe 5,47/21,37 hfrac=1 flcap=0,15 loss_close=0,30 adx_th=30 cooldown=240. Không delta15. Walk-forward: 12 fold tháng test 12/2025–11/2026, 3 tháng train / 1 tháng test, vốn 10k mới mỗi fold.

### 4.1. Ứng viên `flat_orphan=1`, `maxL=8`

| Chỉ số | Số Python |
|---|---:|
| Lãi ròng | +57.231,94 USD (5.723.194 USC) |
| DD tối đa | 1.314 USD (13,14%) |
| Lỗ thả nổi tệ nhất | −778,14 |
| IS (trước 01/10/2026) / OOS | +51.003,82 / +6.228,12 |
| Spread ×2 | +45.572,45 / DD 12,99% |
| Sharpe | 6,969 |
| Cụm vào / DCA / hedge | 17.220 / 12.105 / 5.895 |
| max lots | 0,18 |
| WF | **12/12** (tệ nhất lãi 09/2026 +1.465,12; tệ nhất DD 12,03%) |
| 15 stress | **15/15** (tệ nhất lãi Q4-2018 +1.719,50; tệ nhất DD gap−20% 56,73%; gap+20% +76.792,83 / 15,77%) |
| MT5 cùng cấu hình | **không đạt** (−9.993,99 / 99,94%) |

Fold Python tháng 1: +6.233,70 / DD 9,75%. Lân cận maxL 6–10 + orphan: cả cụm đạt trên Python (maxL=6 +68.341,43 / 10,85%; maxL=7 DD thấp nhất 9,91%). Không orphan, maxL=8: +9.360,27 / DD 98,67%, WF 8/12, stress 8/15.

Chọn maxL=8 vì giữa dải 6–10, không tối đa hóa lãi. Lựa chọn này **đúng trên Python, sai trên tick thật**.

### 4.2. Guard khác trên Python (maxL=20 trừ khi ghi chú)

`flat_orphan` alone, maxL=20: +36.767,37 / DD **82,41%** — không đạt ngưỡng 80%. `orphan` + cooldown 20.000: +33.454,47 / 73,34%, spr×2 đạt, WF 11/12 (tháng 1 −1.151,40), stress 14/15 (gap+20% DD 80,19%). Kitchen (short_cap 0,04 + orphan + dca_mode=2 + max_lc 2 / 6.900 nến + day 15% + week 30% + eq_lot): +23.783,01 / DD 86,44%, WF 11/12 — không đạt trên Python. Ứng viên vòng trước `short_cap=0,04` + cooldown 20.000 (không orphan): cửa sổ dài +2.359,88 / 66,24%, spr×2 **không** đạt, WF 7/12.

## 5. Guard đã thiết kế và đưa vào EA

Đúng bệnh MT5 (rổ bán DCA nắm rally + chồng loss_close hai chiều):

| Guard | Việc làm | Có trong máy Python | Có trong EA |
|---|---|---|---|
| `flat_orphan` | Đóng hedge mồ côi, không lật rổ | có | có (v1.01+, mặc định 1) |
| `short_cap` | Trần lot chiều ngắn | có | có (trước đó) |
| `dca_mode` 0/1/2 | 0=ADX dừng DCA ngược; 1=DCA chỉ cùng slope; 2=cả tín hiệu vào chỉ cùng slope | có | **có từ v1.02** |
| `lc_period` / `lc_pause` + `max_lc` | Sau N lần đóng lỗ trong cửa sổ N nến M1 thì nghỉ | có | **có từ v1.02** (`max_lc` không period = dừng vĩnh viễn như cũ) |
| `day_loss` / `week_loss` | Dừng vào/DCA mới khi lỗ ngày / 5 ngày roll ≥ X × equity đầu kỳ | có | **có từ v1.02** |
| `eq_lot` | Giảm K và maxL theo min(1, balance / vốn ban đầu), không tăng | có | **có từ v1.02** |
| `loss_close` | Đóng cả rổ khi lỗ tổng ≥ X × equity lúc mở | có | có sẵn |

Input mới mặc định **0 = tắt**, không đổi hành vi cũ nếu không gán. `short_cap` một mình không cắt rổ −3.002 (xem 3.1). Cần `dca_mode=2` để không DCA/vào bán trong sóng tăng, cộng chặn chồng (`lc_pause`, `day_loss`, `week_loss`). Máy Python chưa mô phỏng đúng tháng 9–10 nên không chọn được bộ này bằng quét Python.

## 6. MT5 p4 — cấu hình guard (EA v1.02)

Cùng an toàn p4: GOLD.i#, M1, every tick real ticks, 2025.09.01–2026.11.27, vốn 10k, đòn 1:500. Không tắt terminal XM chính (PID 5968), không chạy slot khác dùng chung Bases.

Input thêm so với or8: InpShortCap=0,04, InpDcaMode=2, InpMaxLc=2, InpLcPeriod=6900, InpLcPause=6900, InpDayLoss=0,15, InpWeekLoss=0,20, InpEqLot=1, InpMagic=2026112793, tên `vang_tayv2_guard_th9_th11`. Compile ok lúc 22:19 giờ VN, phong PID 12492.

Chạy 22:18:59–22:23:51 giờ VN, 287 giây, PID terminal 12492. Compile ok. 100% real ticks.

| Chỉ số MT5 | Số |
|---|---:|
| Lãi ròng | **−8.941,37 USD** (còn 1.058,63) |
| DD equity tối đa | 10.049,77 (**90,47%**) |
| PF | 0,44 |
| Số lệnh | 34.421 (T2_MAIN 32.802 / T2_DCA 1.187 / T2_HEDGE 432) |
| Lệnh thắng | 33.804 (98,21%) |
| Đỉnh balance | 11.135,61 lúc 2025.10.21 01:23:40 Athens |
| Balance < 8.000 | 2025.10.28 08:44:43 (7.774,23) |
| Balance < 5.000 | 2026.03.19 08:48:42 (4.953,17) |
| Balance < 2.000 | 2026.06.10 17:57:42 (1.994,98) |
| Kết thúc | 1.058,63 lúc 2026.09.28 04:01:56 (không còn lệnh sau đó) |

Đường vốn cuối tháng: 09/2025 **10.397** (sống qua rally, **không** còn rổ bán −3.002 ngày 01/10) → 10/2025 8.014 → 11/2025 8.261 → 12/2025 9.273 → 01/2026 5.292 → 02/2026 5.436 → 03/2026 4.031 → 05/2026 2.850 → 06/2026 2.016 → 09/2026 1.059.

`dca_mode=2` + `short_cap=0,04` **có tác dụng** đúng bệnh tháng 9–10: tháng 9 lãi +397, ngày 01/10 còn 10.451, leo đến đỉnh 11.136 (21/10). Sau đó vẫn chết vì `loss_close` 30% **chiều mua**:

- 28/10/2025 08:44: 8 lệnh đóng, **−3.310,19** (11.136 → 7.775).
- Khôi phục chậm đến 10.282 ngày 28/01/2026.
- 29/01 17:28: 8 lệnh, **−3.093,39** (→ 7.297); 30/01 **−2.245,49** (→ 5.292). Hai rổ trong hai ngày — `max_lc=2` mới pause sau rổ thứ hai, nên không chặn cú 30/01.
- Tiếp tục chảy: 19/03 −1.663,86; 19/05 −1.220,91; 10/06 −855,10; 28/09 −451,99.

`day_loss` / `week_loss` chỉ chặn vào/DCA **sau** khi rổ 30% đã đóng, không cắt sẵn cú −3.000. Muốn có cửa trên MT5 cần `loss_close` chặt hơn (ví dụ 10–15%) và/hoặc `max_lc=1` (nghỉ ngay sau một rổ). Chưa chạy thêm test trong lượt này.

**Không đạt** tiêu chí lãi > 0 và DD < 80%.

## 7. Việc chưa xong / hạn chế

- Chưa có cấu hình đạt lãi > 0 và DD < 80% trên MT5 tick thật cửa sổ đầy.
- Cần chỉnh máy Python (hoặc ghi nhật ký EA) cho khớp lệnh tháng 9–10 trước khi quét tiếp. Không tối ưu thêm trên Python khi chưa khớp.
- Báo cáo tester không ghi swap (0,00) dù một số lệnh nắm nhiều tuần — số ròng MT5 có thể hơi khác tài khoản thật có swap (bán vàng XM swap dương).
- Không đặt lệnh thật, không đẩy commit này trừ khi được yêu cầu.

File: `phong_cach_tay/ma/may_v2.py`, `phong_cach_tay/ma/chay_vang_wf.py`, `vang/ea/VANG_TayV2.mq5` (v1.02), `vang/ma/chay_tester_tayv2_p4.py`, `phong_cach_tay/ket_qua/vang_wf_*.csv`, `vang_mt5_or8_*.csv`. Không sửa `tin_hieu_data.py`.
