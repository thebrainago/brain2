# Đối chiếu MT5 tick thật với mô phỏng Python — vàng GOLD.i#

Viết lúc **2026-11-27 19:39 (giờ Việt Nam, UTC+7)**. Chỉ ghi số đã đo. Vốn đầu 10.000 USD, mã GOLD.i#, khe **p4** (bases riêng, không đụng p3/p5/p6/shared_bases), một test một lúc, Model=4 (Every tick based on real ticks).

## 1. Tick thật có trên máy

Trên `E:\mt5_tester\p4` (sao chép từ shared_bases, **không** gắn junction):

- Nến M1 `.hcc`: gần đủ từ 2014–2026 (trước 2014 file rất nhỏ).
- Tick `.tkc`: **2025.08–2026.11**. File 202508 chỉ 11,1 MB (tháng thiếu, nhỏ hơn các tháng đủ ~25–40 MB). File 202611 lúc đầu 2,2 MB rồi được máy bổ sung khi tester chạy.

Cửa sổ 2015–2026 và 2018–2026 **chưa chạy** được bằng tick thật: không có file tick trước 2025.08. Lần chạy `FromDate=2025.08.01` tester báo `preliminary downloading of history ticks canceled` rồi `no history data, stop testing` (mất kết nối khi đang tải tick thiếu). Cửa sổ tick dài nhất chạy thành công: **2025.09.01–2026.10.12**.

## 2. Kết quả Strategy Tester (100% real ticks)

| EA | Cửa sổ | Lãi ròng USD | CAGR kép | DD vốn tối đa | Lệnh | Thắng | PF | Chất lượng | Thời gian chạy | ĐẠT mới? |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| VANG_DonchianEMA (Donchian 20 + EMA 55, SL 2 ATR, TP 4 ATR, rủi ro 2%) | 2025.10.01–2026.10.12 | −658,60 | −6,40% | 33,50% | 217 | 34,10% | 0,98 | 100% real ticks | 143 s | không (lãi ≤ 0) |
| VANG_DonchianEMA | 2025.09.01–2026.10.12 | +1.137,39 | +10,18% | 33,07% | 239 | 35,15% | 1,03 | 100% real ticks | 50 s | có |
| VANG_LuoiEMA (lọc EMA 55, bước 1,5 ATR, 4 chân, TP 1,2 / SL 5, lot 0,08/chân) | 2025.10.01–2026.10.12 | +4.856,48 | +46,89% | 55,63% | 757 | 73,32% | 1,04 | 100% real ticks | 96 s | có |
| VANG_LuoiEMA | 2025.09.01–2026.10.12 | +10.045,60 | +86,94% | 48,08% | 819 | 74,36% | 1,08 | 100% real ticks | 101 s | có |

Tiêu chí ĐẠT mới (t344u): lãi ròng > 0 **và** DD tối đa < 80%. Không còn yêu cầu CAGR > 10%.

Khởi động Donchian 2025.10.01–2026.10.12: 96.296.227 tick, 6.053 nến H1, ~1.984 MB tick trong RAM, số dư cuối 9.341,40 USD. Lưới cùng cửa sổ: số dư cuối 14.856,48 USD.

Một số lệnh mở lúc nến H1 mới bị MT5 từ chối `[Market closed]` (ví dụ 2026.01.29 01:00, 2026.03.19 00:00). Python vào lệnh tại giá mở nến, không mô phỏng thị trường đóng.

## 3. Cùng cửa sổ, mô phỏng Python (nến H1, không swap, trừ spread+trượt như `mo_phong.py`)

| Chiến lược | Cửa sổ | Vốn cuối | CAGR kép | DD | Lệnh | Thắng | PF | Lot chân |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Donchian 20 + EMA 55, SL 2 / TP 4 ATR, rủi ro 2% | 2025.10.01–2026.10.12 | 18.201,7 | 78,93% | 22,51% | 231 | 38,96% | 1,20 | (kép 2%) |
| Donchian (như trên) | 2025.09.01–2026.10.12 | 20.668,0 | 92,16% | 23,40% | 254 | 38,98% | 1,21 | (kép 2%) |
| Lưới EMA 55, lot 0,08 | 2025.10.01–2026.10.12 | 57.568,9 | 447,6% | 66,86% | 715 | 93,15% | 1,36 | 0,08 |
| Lưới EMA 55, lot 0,08 | 2025.09.01–2026.10.12 | 65.510,0 | 442,5% | 54,11% | 783 | 93,61% | 1,41 | 0,08 |

Có swap (long −83,83 USD/lot/đêm) làm giảm vốn cuối nhưng không đổi chiều lãi/lỗ trên các cửa sổ ngắn này (xem `ket_qua/python_cua_so_tick_va_dai.csv`).

## 4. Độ lệch Python so với tick thật (số đo)

Cùng logic tín hiệu (Donchian cửa sổ 20 nến không gồm nến tín hiệu, lọc EMA 55, vào nến sau). Số lệnh gần nhau; lãi và tỷ lệ thắng thì Python **lạc quan rõ**.

**Donchian 2025.10.01–2026.10.12**

- Python: lãi +8.201,7 USD, PF 1,20, thắng 38,96%, 231 lệnh, DD 22,51%.
- MT5 tick: lãi **−658,60** USD, PF 0,98, thắng 34,10%, 217 lệnh, DD 33,50%.
- Cùng cửa sổ, Python ĐẠT, MT5 **không ĐẠT**.

**Donchian 2025.09.01–2026.10.12** (thêm tháng 9/2025)

- Python: lãi +10.668 USD, PF 1,21, 254 lệnh, DD 23,40%.
- MT5 tick: lãi **+1.137,39** USD, PF 1,03, thắng 35,15%, 239 lệnh, DD 33,07%.
- Cả hai ĐẠT tiêu chí mới, nhưng lãi Python gấp khoảng 9 lần lãi tick. Tháng 9/2025 đảo cửa sổ 12 tháng từ lỗ tick sang lãi nhỏ.

**Lưới lot 0,08, 2025.10.01–2026.10.12**

- Python: lãi +47.568,9 USD, PF 1,36, thắng 93,15%, 715 lần đóng, DD 66,86%.
- MT5 tick: lãi **+4.856,48** USD, PF 1,04, thắng 73,32%, 757 lần đóng, DD 55,63%.
- Cả hai ĐẠT. Lãi Python gấp khoảng 10 lần. Tỷ lệ thắng Python cao hơn 20 điểm phần trăm.

**Lưới lot 0,08, 2025.09.01–2026.10.12**

- Python: lãi +55.510 USD, PF 1,41, thắng 93,61%, 783 lần đóng, DD 54,11%.
- MT5 tick: lãi **+10.045,60** USD, PF 1,08, thắng 74,36%, 819 lần đóng, DD 48,08%.
- Cả hai ĐẠT. Lãi Python gấp khoảng 5,5 lần.

Kết luận đo được trên mẫu tick này: **số CAGR H1 cả mẫu 2014–2026 của Python (80–90% với Donchian/fractal) chưa được tick xác nhận** và không nên dùng để quyết định. Trên ~13 tháng tick, lưới vẫn lãi nhưng PF chỉ 1,04–1,08; Donchian chỉ còn biên mỏng (PF 1,03) và có cửa sổ 12 tháng lỗ.

Báo cáo HTML/JSON gốc trên máy nhà: `E:\brain2_tmp\vang\mt5\`.

## 5. Việc chưa làm trên MT5

- Cửa sổ 2015–2026 và 2018–2026 bằng tick thật: chưa có tick.
- EA hedge / gỡ lệnh / lưới M15: mới có số Python (mục báo cáo quét mở rộng), chưa xác nhận tick.

---

## 6. Hedge / gỡ lệnh / lưới nhân lot (đo 2026-11-27 19:46–19:55 UTC+7)

Cửa sổ **2025.09.01–2026.10.12**, GOLD.i#, vốn 10.000 USD, khe **p4**, Model=4, **100% real ticks**. Hàng đợi biến thiên lưới truyền thống còn lại **đã dừng** sau bốn test này (đổi hướng theo t345u; không chạy cửa sổ 2025.10.01 cho các EA mới).

| EA | Khung | Tham số chính | Lãi ròng USD | CAGR kép | DD vốn tối đa | Lệnh | Thắng | PF | ĐẠT mới? |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| VANG_HedgeEMA | H1 | EMA 55, đảo khi ngược 2 ATR, lot đảo 1,5×, TP 1,2 / SL 4 ATR, lot gốc 0,08 | **+13.051,52** | +111,98% | 45,09% | 467 | 70,02% | 1,13 | có |
| VANG_HedgeEMA | M15 | Cùng họ, lot gốc 0,16 | **−10.004,64** | — (vỡ vốn) | 100,10% | 1.497 | 66,40% | 0,97 | không |
| VANG_LuoiPhuc | H1 | Lưới b 1,5 / 4 chân / TP 1,2 / SL 5, lot 0,02, gỡ ×1,3 tối đa 2 bậc | **+2.511,40** | +22,33% | 26,93% | 819 | 74,36% | 1,08 | có |
| VANG_LuoiPhuc | H1 | Lưới cùng bước, nhân lot trong rổ ×1,5, lot chân 0,03, không gỡ | **+2.837,23** | +25,19% | 47,62% | 823 | 74,36% | 1,05 | có |

Cùng cửa sổ, mô phỏng Python nến (không swap):

| Chiến lược | Python vốn cuối (lãi) | Python DD | Python lệnh / PF | Ghi chú lệch |
|---|---:|---:|---|---|
| Hedge H1 lot 0,08 | 68.840,6 (+58.840,6) | 11,74% | 469 / 2,53 | Số lệnh gần khớp (467 vs 469). Lãi Python gấp ~4,5 lần; DD tick cao hơn nhiều. |
| Hedge M15 lot 0,16 | 180.874 (+170.874) | 6,10% | 1.652 / 1,98 | Python ĐẠT, MT5 **vỡ vốn**. Parquet M15 không phải giờ XM; không dùng số Python M15. |
| Gỡ H1 lot 0,02 ×1,3 bậc 2 | 27.895,4 (+17.895,4) | 37,33% | 783 / 1,40 | Cả hai ĐẠT. Lãi Python gấp ~7 lần; DD tick *thấp hơn* (26,93% vs 37,33%). |
| Lưới ×1,5 lot 0,03 | 26.049,3 (+16.049,3) | **94,80%** (không ĐẠT) | 804 / 1,20 | MT5 **ĐẠT** (DD 47,62%). Đây là trường hợp Python bi quan hơn tick về DD. |

Các EA: `vang/ea/VANG_HedgeEMA.mq5`, `vang/ea/VANG_LuoiPhuc.mq5`. JSON: `ket_qua/mt5_p4/tong_hop_hedge_th9.json`. HTML: `E:\brain2_tmp\vang\mt5\`.
