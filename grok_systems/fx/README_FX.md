# README_FX – nghiên cứu cặp tiền & tài sản khác (XSD-20, 28/11/2026)

> Mục tiêu: xem cặp FX (nhất là AUD) và tài sản khác có thêm được hệ tín hiệu cho sổ Vàng/SP500 không.
> **Kết luận ngắn: KHÔNG tìm thấy edge hồi quy bền vững trên FX/CFD khác. Không đưa hệ nào vào sổ.**
> Mọi con số là MÔ PHỎNG PYTHON (engine2 bảo thủ) trừ phần ghi rõ MT5. KHÔNG CÓ = chưa đo.

## 1. Dữ liệu thật có gì
| Nguồn | Có | Giới hạn |
|---|---|---|
| MT5 XM (slot p6, tài khoản Ultra Low, symbol `#`) M1 BID + spread từng nến | 2025-06-02 → 2026-11-27 (~18 tháng) | máy chủ giới hạn `MaxBars=50000`, đã nâng lên 1.000.000 trong `E:\mt5_tester\p6\config\common.ini` (bản gốc `.bak_fx`) |
| FX đã tải | AUDUSD AUDJPY AUDNZD AUDCAD AUDCHF EURAUD GBPAUD NZDUSD NZDCAD NZDJPY NZDCHF EURUSD GBPUSD USDCAD EURJPY | |
| CFD đã tải | SILVER.i#, OILCash#, US100Cash# (xem mục 7 nếu thiếu) | đang tải thêm US30, JP225, BRENT, GER40, UK100 – KHÔNG CÓ kết quả cho các mã chưa tải |
| Chưa tải được (tải chậm/treo) | USDJPY EURGBP GBPJPY CADJPY CHFJPY EURNZD GBPNZD GBPCAD EURCAD EURCHF USDCHF GBPCHF CADCHF | |
| Order-flow CME Sierra (.scid) | 6A 6E 6B 6C 6J (hợp đồng Z6), SI, CL | **Z6 chỉ có thanh khoản từ ~14/09/2026 (khoảng 9 tuần)**; trước đó gần như không có giao dịch. 6A kết thúc 18/11, SI/CL 20/11. Không có ZN/YM/NQ dài. Chỉ nghiên cứu thăm dò, không đủ để A/B |
| Fxaurum TickDb | chỉ ES/NQ/GC | không có FX futures (không chạy syncTicks) |

Chia mẫu: **IS = 2025-06-02 → 2026-05-31 (12 tháng)** để chọn; **OOS = 2026-06-01 → 2026-11-27** (cùng cửa sổ sổ Vàng/SP500) chỉ để kiểm.
Chi phí: spread từng nến của XM Ultra Low + 0,5×trượt giá; swap từ `symbol_info` (long/short, nhân 3 ngày thứ Tư); flatten thứ Sáu ≥21:00 server. Tài khoản Ultra Low có swap_mode=0 trên mã `#` nhưng tôi vẫn trừ swap (bảo thủ).
Lệnh: quy lot 1.0 chuẩn; JPY/CHF/CAD pv dùng tỷ giá hiện tại (sai số vài %).

## 2. Họ tín hiệu hồi quy đã thử (≈47 biến thể × 4 phiên × lưới quản lý)
- z-score giá so MA (M5/M15/H1, N=30/100, ngưỡng 2/2,5/3), RSI2 (có/không lọc xu hướng EMA200), IBS, Asia-range (fade phá biên / phá thất bại lúc London-NY).
- Họ dài hạn H4/D1: z-score, RSI2, IBS (`L_*`).
- Spread/cointegration: phần dư hồi quy log-giá AUD vs NZD (AUDUSD~NZDUSD, AUDCAD~NZDCAD, AUDJPY~NZDJPY, AUDCHF~NZDCHF, EURAUD~EURNZD, GBPAUD~GBPNZD), cửa sổ 3 và 10 ngày.
- Quản lý: (a) scalp SL/TP theo ATR-H1 (18 ô lưới), (b) giỏ DCA không SL + chốt giỏ (12–18 ô: bước nhồi, TP, maxN 3/5), khóa/flatten cuối tuần.
- Phiên: all / Á (UTC 0-7) / London (7-12) / NY (12-20).

## 3. Kết quả sàng lọc (16 mã, ~28k cấu hình giỏ, ~19,6k cấu hình scalp)
**Scalp SL/TP (kỳ vọng theo ATR-H1, đã trừ spread+trượt):** trung vị IS −0,32 ATR, OOS −0,43 ATR. Chỉ 0,10% cấu hình dương ở cả IS và OOS. Chọn theo IS (PF>1,15, t>2): 6 cấu hình → **0 dương ở OOS**. Chi phí FX (spread ≈1,3 pip AUDUSD) ≈ 0,5 ATR-M5 → scalp hồi quy chết vì phí. Không phí: edge chỉ +0,09 ATR.

**Giỏ DCA (đây là kiểu vàng/SP500 đang thắng):** tiêu chí chọn trên IS: lãi IS>0 và lãi/DD ≥3; vượt OOS: lãi OOS>0 và lãi/DD ≥1.
| Bộ tín hiệu | Cấu hình | Qua chọn IS | Qua OOS |
|---|---|---|---|
| **Thật (fade)** | 27.930 | 77 | **4** (thực chất 2 hệ, trùng tham số) |
| **Placebo** (hướng ngẫu nhiên, cùng thời điểm) | 27.994 | 155 | **25** |
| **Gương (theo đà)** | 27.982 | 155 | 20 |
→ **Tín hiệu thật không tốt hơn ngẫu nhiên** (4/77 vs 25/155). Đây là mức “may rủi do thử nhiều” (selection null).

Theo nhóm (tỉ lệ cấu hình dương cả IS lẫn OOS): AUD 6,5% (placebo 7,4%); NZD 2,2%; FX khác 9,0%; CFD (Silver) 4,5% (placebo 6,0%). **AUD không đặc biệt hơn nhóm khác**, AUDNZD và NZD-cross còn tệ hơn (đa số thua).
Mẫu “giỏ thắng 94% nhưng lỗ ròng” rất phổ biến: ví dụ AUDUSD z15 fade thắng 519/554 giỏ nhưng lỗ −13,8k/1 lot (đuôi trái).

## 4. Ứng viên sống sót & kiểm tra nghiêm ngặt (giỏ, 1 lot, USD)
| | NZDJPY `L_ibs_240` London, gap 1 ATR-H1, TP 2 ATR-H1, N3 | EURAUD `L_z240_50_2.0` NY, gap 2, TP 1, N3 |
|---|---|---|
| 18 tháng | +11.000, DD 2.374 | +4.815, DD 1.778 |
| IS / OOS | +8.000 / +3.000 (DD 2.088) | +2.534 / +2.282 |
| tháng dương | 15/18 (OOS: 4/6) | 14/18 |
| Placebo (40 seed) | 97,5% | 90% (<95) |
| Spread ×2 + trượt 1,0 | +1.479 (DD 5.523) | **−315** |
| Spread ×3 | **−4.218** | −3.182 |
| Trễ 2 nến | +10.859 | +4.701 |
| Bỏ swap | +11.847 | +5.203 |
| Detrend / đảo xu hướng | +10.987 / +10.969 | +3.345 / +2.194 |
| Chỉ mua / chỉ bán | +5.174 / +6.341 | +3.049 / +1.766 |
| Gap 5% | DD ≈10.700 (4,5× DD thường) | DD ≈17.900 (10×) |
**EURAUD: LOẠI** (hỏng khi spread ×2, placebo <95%).
**NZDJPY: ứng viên yếu nhất còn lại** – sống qua trễ, swap, hai chiều, nhưng (i) chọn ra từ ~28k cấu hình trong khi placebo cho 25 “sống sót”, (ii) chỉ ~22 giỏ trong 6 tháng OOS, (iii) lãi gần như mất hết khi spread ×2, (iv) tính chất “thắng” đến từ flatten thứ Sáu (cắt lỗ theo thời gian), (v) lãi OOS chỉ trong 3 tháng Aug–Nov. **Không khuyến nghị đưa vào sổ khi chưa forward demo.**

## 5. Tác động lên sổ 100k và tài khoản 100 USD cent (mô phỏng, sổ proxy = 12 hệ v5_G30, lãi 74.942, DD 6,0% trong 6 tháng)
| Thêm vào sổ | Tương quan PnL ngày với sổ | Lot để DD riêng = 5% của 100k | Lãi thêm 6T | DD sổ gộp |
|---|---|---|---|---|
| NZDJPY | +0,20 | 2,44 lot | +7.312 | 6,0% → 6,9% |
| EURAUD | −0,14 | 2,81 lot | +6.418 | 6,0% → 7,2% |
Tài khoản 100 USD cent: để DD riêng ≈5 USD cần ≈0,0024 lot chuẩn (≈0,24 lot cent) → **+7 USD/6 tháng** (+7%). Không đáng so với hệ vàng/SP500 hiện có (+82..130 USD). KHÔNG đề xuất.

## 6. Order-flow futures CME → CFD (thăm dò, ~9 tuần)
90 phép thử (6A→AUDUSD, 6E→EURUSD, 6B→GBPUSD, 6C→USDCAD, SI→Silver; delta/imbalance/lệnh lớn 5/15/60 phút, dự báo 15/60 phút, mẫu không chồng lấn).
- 6A→AUDUSD: IC trung bình −0,004, |t|≤2,5 (chỉ 2/18 vượt 2) → **không có tín hiệu**.
- 6E: −0,003. 6B −0,014 (4/18 |t|>2). **6C→USDCAD IC −0,029 (7/18), SI→Silver IC −0,036 (12/18, t tới −4,0)**: dòng lệnh mua/bán lớn **đảo chiều** sau 15–60 phút (giống ES/GC ta đã khai thác).
- Nhưng lãi gộp khi fade dòng lệnh z>2 chỉ ≈0,2–1,5 pip (FX) và ≈3,2 “pip” (0,032 USD) Silver 60 phút, **dưới spread (1–4,5 pip)** → chưa đủ lập hệ. Muốn thử cần tick thật + khớp lệnh tốt hơn hoặc mẫu dài hơn (hợp đồng Z6 mới thanh khoản từ tháng 9).
- Tổng 26/90 phép thử có |t|>2 (kỳ vọng ngẫu nhiên 4,5), 10 phép |t|>3: **có tín hiệu thống kê nhưng nhỏ hơn chi phí**.

## 7. MT5 100% tick thật
Xem mục 8 (cập nhật cuối). KHÔNG CÓ nếu mục 8 trống.

## 8. Việc còn dang dở / lưu ý vận hành
- Máy nhà chập chờn (lệnh PowerShell treo) nên tải tiếp CFD và chạy MT5 bị chậm; trạng thái chi tiết trong `STATUS.md`.
- Nếu muốn mở rộng: tải thêm USDJPY/GBPJPY/EURGBP và US30/JP225/GER40… rồi chạy `code/run_batch.sh <mã>`.
- Bảo mật: lần trước một lệnh trên máy nhà in nhầm biến môi trường (có AIBOX_API_KEY, SO_SANH_*). Không chép lại giá trị; anh nên đổi các key đó.

## 9. Chạy lại / cấu trúc
- `code/fxlib.py` (bảng M1, swap, engine giỏ), `fxsig.py` (họ tín hiệu), `fx_screen.py` (scalp), `fx_basket.py` (giỏ; `PLACEBO=0` placebo, `PLACEBO=-2` gương), `fx_select.py` / `fx_summary.py`, `fx_battery.py`, `fx_port.py`, `fx_of.py`, `fx_mt5prep.py`, `engine2x.py`.
- Kết quả: `results/*.json|csv` (summary.json, of_ic.csv, bat_*.json, port_fx.json); dữ liệu M1 thô KHÔNG đẩy lên git (nằm ở `E:\GrokWork\bt_fx\m1`).
- EA: `ea/BRAIN_XuLiLenh_fx.mq5` = r5 + `InpTuanDong` (flatten thứ Sáu thay vì hedge-lock), biên dịch trong slot p6.
