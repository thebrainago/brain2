### 20.1 Phủ họ tín hiệu (coverage) — xem `COVERAGE.md`
- Vòng 6 thêm `newsig4` (93 spec/asset: naked POC, VA 80%, gap fill/go, NR-day, gap cuối tuần, mốc giờ cố định (London fix, NY close…), range-expansion, volume climax, cá mập tại cực trị, z-window 5/30/60 cho g1/g2/g3/imb/ar/fz/ad, VWAP trend pullback, NY IB, CVD lead) và `scalp2` (lưới SL/TP×hold 40 ô cho TẤT CẢ họ basket newsig1–4, 948 tổ hợp/asset), `newsig5` (đảo chiều pullback/IBS + 91 cặp đồng pha/asset).
- Tổng đã chạy: ~36k cấu hình basket + ~300k cấu hình scalp (2 tài sản). Ô duy nhất chưa thử được: gap qua đêm/cuối tuần (chỉ 8–15 sự kiện/6 tháng → không đủ mẫu), NQ/SI/CL lead-lag, GEX/flip/walls (KHÔNG CÓ dữ liệu).
- Cảnh báo cơ sở: basket không SL có thiên lệch dương — 53% cấu hình PLACEBO (vào lệnh ngẫu nhiên) cũng dương cả A và B → tiêu chí "A&B dương" vô nghĩa với basket nếu không có placebo-percentile, reverse-drift, delay.

### 20.2 Hệ mới vòng 6 (battery + MT5 100% real ticks)
| Mã | Tài sản | Tín hiệu | Lọc | Quản lý | Lot MT5 | MT5 net / DD | Python | Battery |
|---|---|---|---|---|---|---|---|---|
| g7 | XAU | `imb30z_fade2.0` (imbalance 30m |z|>2 → fade) | gt20, all | basket 8/4/4 + W | 0.04 | +7,544 / 8.9% | +6,849 / 10.4% | placebo 100, detrend +6,781, reverse +7,102, delay2 +6,448, long +2,946 / short +4,958, sx +6,266 |
| xs3 | XAU | `g1_30z_fade2.0` (lệnh lớn ngưỡng 1, 30m |z|>2 → fade) | gt20, all | scalp SL 13 / TP 8 / 90 bar | 0.30 | **+21,046 / 6.8%** (481 lệnh, PF 1.42) | +18,056 | cfg chọn trên A: B tB 3.08, flip-z 3.5, spread×2 +, delay2 + , 6/6 tháng |
| xs4 | XAU | `imb15z_fade3.0` | gt20, all | scalp SL 8 / TP 10 / 90 | 0.30 | +9,735 / 7.9% (270) | +11,246 | B tB 2.1, 6/6 |
| xs5 | XAU | `basis_rev` (basis futures−CFD lệch → hồi) | gt20, ny | scalp SL 8 / TP 6 / 90 | 0.30 | +7,019 / 3.8% (175) | +6,556 | B tB 1.9, 6/6 |
| xs6 | XAU | `g3_60z_mom3.0` (cá mập 60m |z|>3 → thuận) | none, ny | scalp SL 10 / TP 13 / 90 | 0.30 | +10,130 / 7.7% (95) | +9,575 | B tB 1.6, 5/6 — mẫu nhỏ |
| xs7 | XAU | `day_ext_fail` (phá đỉnh/đáy ngày thất bại) | gt20, ny | scalp SL 8 / TP 18 / 30 | 0.30 | +5,875 / 4.6% (89) | +6,482 | B tB 1.25, 6/6 — mẫu nhỏ |
| u15 | US500 | `fz5z_fade2.0` | none, ny | basket 60/3/6 + W | 1.5 | +2,649 / 11.9% | +2,859 / 14.6% | placebo 100 (tương quan 0.87 với u2) |
| u16 | US500 | `vclimax_fade_3` (volume climax tại đỉnh/đáy 60 bar → fade) | none, ldny | 60/4/8 + W | 1.0 | +1,818 / 8.7% | +2,169 | placebo 95 |
| u17 | US500 | `vclimax_mom_2` | none, ny | 60/4/8 + W | 2.0 | +3,030 / 9.8% | +3,546 | placebo 90 |
| u18 | US500 | `fz30z_fade2.0` | none, all | 60/4/8 + W | 1.5 | +1,879 / 12.4% | +1,970 | placebo 90 |
| u19 | US500 | `g2_60z_mom2.0` | none, all | 60/4/8 + W | 1.5 | +2,473 / 9.7% | +2,884 | placebo 90 |
- Scalp SL/TP theo GIÁ (USD/oz), cấu hình chọn trên nửa A rồi kiểm nửa B (OOS) — chống overfit. US500 scalp: không có hệ nào qua (B âm hoặc spread×2 âm).
- Loại sau battery: XAU g1_30z_mom/g2_30z_mom/ar30z_mom/fz30z_mom/g3_60z_mom basket (reverse-drift âm = ăn theo xu hướng giảm vàng), rexp_fade (B riêng âm), US500 fz5z_mom/imb5z_mom (placebo 80), rexp_mom/g1_30z_mom (placebo 40–45).

### 20.3 SỬA SỐ VÒNG 5 (quan trọng)
1. **Joint DD PortE**: bug phân loại g5 là US500 khi dựng equity → DD đúng là **14.9%** (không phải 13.2%); nửa lot **7.5%** (không phải 6.6%). Net không đổi (+101,301).
2. **Gap scalp**: vòng 5 coi scalp xs1/xs2 "miễn nhiễm gap" — SAI: gap xuyên SL. Vòng 6 tính cả vị thế scalp khi đang mở → gap-5% của các danh mục có scalp lot lớn cao hơn nhiều so với số vòng 5 (PortD-G30 "29%" bị đánh giá thấp).

### 20.4 Tìm combo (greedy theo tương quan + tối ưu lot, `opt6.py`)
- Vũ trụ 27 hệ đã pass (bỏ x2, g4). Greedy chọn theo Sharpe ngày của tổng (trọng số 1/DD): **g2 → xs6 → x1 → xs4 → xs7 → xs2 → u12 → xs3 → xs1 → u15 → u10 → g7 → g5 → xs5 → u17** (15 hệ, tương quan ngày giữa hệ mới với hệ cũ ≤0.27 trừ u15–u2 0.87, u18–u11 0.59).
- Chống overfit: tối ưu lot trên A rồi đo B, tối ưu trên B rồi đo A; **lot chốt = trung bình (lot tối ưu A, lot tối ưu B)**, scale cho vừa ràng buộc toàn mẫu, làm tròn bước lot (0.01 vàng, 0.1 US500).
- Kịch bản (ràng buộc Python: DD / spread×2 DD / gap-5%): an toàn 10/15/30, cân bằng 15/22/50, mạnh tay 19/28/không giới hạn gap.

### 20.5 KỊCH BẢN CHỐT (DD gộp đo trên MT5 = equity ghép theo timestamp, scale tuyến tính lot từ các run MT5 từng hệ; vốn 40k)
| Kịch bản | MT5 net | DD gộp | A / B | tháng+ | Nửa lot |
|---|---|---|---|---|---|
| **An toàn** | +33,686 | 3.6% | 15,629 / 18,056 | 6/6 | +16,843 / 1.8% |
| **Cân bằng** | +59,154 | 5.7% | 27,615 / 31,539 | 6/6 | +29,577 / 2.9% |
| **Mạnh tay** | +127,792 | 12.7% | 59,724 / 68,068 | 6/6 | +63,896 / 6.3% |
| Mạnh tay ×1.4 (DD<20% theo yêu cầu) | +177,154 | 17.1% | 82,724 / 94,430 | 6/6 | +88,577 / 8.6% |
| **Đánh tay** (7 scalp vàng) | +21,526 | 3.8% | 9,851 / 11,676 | 6/6 | +10,763 / 1.9% |
| Đánh tay ×2.5 | +53,770 | 9.6% | 24,596 / 29,173 | 6/6 | +26,885 / 4.8% |
| (so sánh) cả 27 hệ, mạnh tay | +124,667 | 12.4% | 53,480 / 71,187 | 6/6 | +62,334 / 6.2% |

- **An toàn — lot:** g2 0.02, xs6 0.12, x1 0.01, xs4 0.07, xs7 0.11, xs2 0.08, u12 2.3, xs3 0.07, xs1 0.16, u15 0.5, u10 1.3, xs5 0.11, u17 0.9. Python: net 32,301, DD 3.3%, spread×2+slip1 DD 4.8%, gap-5% 27%, A 15,421 / B 16,876.
- **Cân bằng — lot:** g2 0.04, xs6 0.21, x1 0.02, xs4 0.11, xs7 0.18, xs2 0.14, u12 2.7, xs3 0.12, xs1 0.27, u15 0.8, u10 1.6, g7 0.01, g5 0.01, xs5 0.19, u17 1.5. Python: net 56,742, DD 5.5%, spread×2+slip1 DD 8.1%, gap-5% 48%, A 27,138 / B 29,598.
- **Mạnh tay — lot:** g2 0.08, xs6 0.48, x1 0.06, xs4 0.26, xs7 0.4, xs2 0.41, u12 3.6, xs3 0.25, xs1 0.39, u15 1.8, u10 2.2, g7 0.03, g5 0.03, xs5 0.42, u17 2.7. Python: net 123,132, DD 12.1%, spread×2+slip1 DD 17.1%, gap-5% 98%, A 58,884 / B 64,236.
- **Đánh tay — lot:** xs1 0.15, xs2 0.08, xs3 0.08, xs4 0.06, xs5 0.1, xs6 0.09, xs7 0.1. Python: net 19,654, DD 4.3%, spread×2+slip1 DD 4.8%, gap-5% 29%, A 9,403 / B 10,252.
- Mạnh tay ×1.4: nhân mọi lot ở dòng "Mạnh tay" với 1.4 (u12 5.04, u10 3.08 vượt mức lot đã test MT5 riêng lẻ → rủi ro ngoại suy). Gap-5% Python ~137% vốn → một cú gap 5% có thể cháy tài khoản.
- Đánh tay ×2.5: xs1 .38, xs2 .20, xs3 .20, xs4 .15, xs5 .25, xs6 .22, xs7 .25 (tài khoản 30k).
- So với vòng 5: PortE (+101.3k, DD 14.9%) ↔ Mạnh tay (+127.8k, DD 12.7%) — tốt hơn cả net lẫn DD, và lot đã qua kiểm tra chéo A/B.

### 20.6 Cảnh báo vòng 6
- Đa kiểm định rất lớn (~336k cấu hình). Không hệ scalp nào sống sót hiệu chỉnh Bonferroni đầy đủ (t tối đa ~3.2 trên A+B); bảo vệ dựa vào: chọn cấu hình trên A – kiểm B, flip-z, spread×2, delay2, MT5. Cần forward demo.
- xs6, xs7 chỉ ~90 lệnh/6 tháng.
- Python DD của scalp chỉ tính lúc đóng lệnh (lạc quan); MT5 DD đã bao gồm thả nổi.
- Gap 5% đột ngột trong phiên vẫn là rủi ro lớn nhất; W chỉ xử lý gap cuối tuần/lễ.
## Vòng 6b (newsig5: inverse/pullback/IBS + 91 cặp đồng pha `pair:A+B` trong 30 bar) — HOÀN TẤT
### Hệ mới pass battery + MT5 (100% real ticks, khớp Python)
| Mã | Tín hiệu | Lọc | Kiểu / mgmt | Lot test | MT5 net / DD (lệnh) | Python |
|---|---|---|---|---|---|---|
| gp1 | pair `pw_break_flow` + `emapull` | none, all (XAU) | basket 8/4/4 | 0.06 | +9,237 / 8.5% (402) | 9,288 / 10.3% |
| gp2 | pair `sw_fade_15_1.8` + `dz_fade_15_2.0` | gt20, all | basket | 0.06 | +7,479 / 11.4% (354) | 7,463 / 14.6% |
| gp3 | pair `dz_fade_15_2.0` + `imb30z_fade2.0` | gt20, all | basket | 0.05 | +5,677 / 10.6% (361) | 5,102 / 12.7% |
| up1 | pair `sw_fade_15_1.8` + `sw_fade_15_1.5` | none, all (US500) | basket 60/4/8 | 2.0 | +4,245 / 7.4% (278) | 4,386 / 8.5% |
| up2 | pair `dz_mom_5_1.5` + `rnd_break_50` | none, ny | basket | 2.0 | +2,921 / 6.4% (202) | 2,998 / 7.8% |
| up3 | pair `sw_fade_15_1.5` + `vclimax_fade_3` | none, ldny | basket | 1.0 | +1,604 / 8.9% (193) | 1,861 / 10.6% |
| xs8 | pair `pd_break_flow` + `pw_break_flow` | gt20, ny (XAU) | SCALP SL10 TP18 H90 | 0.3 | +10,437 / 6.1% (86) | 9,894 |
| xs9 | pair `g3_60z_mom3.0` + `big3_mom_60_2.0` | none, ny | SCALP SL10 TP18 H90 | 0.3 | +11,815 / 11.0% (129) | 13,224 (chồng lấn xs6/xs2) |
| xs10 | pair `sw_fade_15_1.8` + `big3_mom_60_2.0` | gt20, all | SCALP SL10 TP18 H30 | 0.3 | +10,140 / 6.9% (120) | 10,123 (tB 3.09) |
Ghi chú: gp*/up* là TẬP CON của hệ cha (x1/g2/g7, u1/u7/u6/u12/u16) → greedy không chọn (trùng tín hiệu). Chỉ xs10 vào danh mục greedy (đứng thứ 2). Cặp scalp tốt nhất `big3_mom+emapull` = chính xs2 → xác nhận lại xs2. EA scalp: InpCatLoPct = 10×lot×100/30000×100 (vd lot 0.3 → 1.0%).

### KỊCH BẢN CHỐT CUỐI (opt7, universe 36 hệ, lot robust = trung bình lot tối ưu trên A và trên B; DD = equity MT5 gộp)
| Kịch bản | MT5 net 6T | DD MT5 | A / B | tháng+ | Nửa lot | Gap-5% Py | spread×2 DD Py |
|---|---|---|---|---|---|---|---|
| **An toàn** (14 hệ) | +36,064 | 3.7% | 16.8k / 19.3k | 6/6 | +18.0k / 1.9% | 27% | 5.1% |
| **Cân bằng** (15 hệ) | +63,102 | 6.3% | 29.2k / 33.9k | 6/6 | +31.6k / 3.2% | 48% | 7.7% |
| **Mạnh tay** (15 hệ) | +119,372 | 11.0% | 54.5k / 64.9k | 6/6 | +59.7k / 5.5% | 98% | 17.2% |
| Mạnh tay ×1.4 | +167,120 | 15.5% | 76.3k / 90.9k | 6/6 | | ~137% | ~24% |
| Mạnh tay ×1.7 (trần DD<20%) | +202,932 | 18.8% | 92.6k / 110.3k | 6/6 | | ~167% | ~29% |
| ALL-36 mạnh tay | +139,341 | 17.1% | 59.4k / 79.9k | 6/6 | +69.7k / 8.5% | 95% | 24.7% |
| **Đánh tay** 10 scalp xs1–xs10 | +20,143 | 3.3% | 9.4k / 10.8k | 6/6 | | 28% | 3.9% |
| Đánh tay ×3 | +60,430 | 9.9% | | 6/6 | | ~83% | |
| Đánh tay ×5 | +100,717 | 16.5% | | 6/6 | | ~139% | |
So với vòng 6a: An toàn +7%, Cân bằng +7% (DD ~bằng), Mạnh tay: lợi nhuận/DD 10.9 (6a: 10.1); ×1.7 = +202.9k/18.8% vs 6a ×1.5 +189.8k/19.0%. Đánh tay ×5 +100.7k/16.5% vs 6a ×4 +86.1k/15.4%.
**Lot (robust):**
- An toàn: g2 .02, xs10 .09, x1 .02, xs6 .12, xs4 .06, u15 .6, xs2 .09, xs7 .09, u12 2.6, xs3 .05, xs1 .08, u13 1.2, xs5 .09, g5 .01
- Cân bằng: g2 .03, xs10 .16, x1 .03, xs6 .20, xs4 .10, u15 .9, xs2 .12, xs7 .15, u12 3.2, xs3 .13, xs1 .15, g7 .01, u13 2.1, xs5 .16, g5 .02
- Mạnh tay: g2 .08, xs10 .31, x1 .05, xs6 .39, xs4 .20, u15 1.7, xs2 .32, xs7 .38, u12 3.1, xs3 .26, xs1 .34, g7 .02, u13 3.1, xs5 .32, g5 .02 (×1.4 / ×1.7: nhân tất cả, làm tròn bước lot)
- Đánh tay: xs1 .08, xs2 .06, xs3 .04, xs4 .04, xs5 .07, xs6 .05, xs7 .11, xs8 .08, xs9 .04, xs10 .06 (×3 / ×5)
**CẢNH BÁO:** các bậc ×1.4/×1.7/×5 chỉ thoả DD<20% trên lịch sử; gap 5% trong phiên ≈137–167% vốn và spread×2 DD ~24–29% → chỉ dùng sau forward demo, khuyến nghị thực tế: Cân bằng hoặc Mạnh tay ×1.0.
### Độ phủ không gian tìm kiếm: XONG
Mọi họ tín hiệu × {fade, momentum} × {basket, scalp} đã chạy (xem COVERAGE.md, ~39.6k cfg basket + ~340k cfg scalp). Ngoại lệ: gap qua đêm/cuối tuần (3–15 sự kiện → không đủ mẫu), NQ/SI/CL/GEX/MBO (KHÔNG CÓ dữ liệu).
