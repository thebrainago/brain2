# README_FX – nghiên cứu cặp tiền & tài sản khác (XSD-20, 28/11/2026)

> Mục tiêu: xem cặp FX (nhất là AUD) và tài sản khác có thêm được hệ tín hiệu cho sổ Vàng/SP500 không.
> **Kết luận ngắn: không có edge hồi quy bền vững trên FX. AUD không đặc biệt. CFD chỉ có vài ứng viên giấy (US30, GER40) — chưa xác nhận tick MT5, không đưa vào sổ.**
> Mọi con số là MÔ PHỎNG PYTHON (engine2 bảo thủ) trừ phần ghi rõ MT5. KHÔNG CÓ = chưa đo. Lot = 1.0 chuẩn; cửa sổ IS 2025-06-02→2026-05-31, OOS 2026-06-01→2026-11-27.

## 1. Dữ liệu thật có gì
| Nguồn | Có | Giới hạn |
|---|---|---|
| MT5 XM (slot p6, Ultra Low, symbol `#`) M1 BID + spread từng nến | 2025-06-02 → 2026-11-27 (~18 tháng) | đã nâng `MaxBars` 50.000 → 1.000.000 trong `E:\mt5_tester\p6\config\common.ini` (bản gốc `.bak_fx`) |
| FX đã tải (15) | AUDUSD AUDJPY AUDNZD AUDCAD AUDCHF EURAUD GBPAUD NZDUSD NZDCAD NZDJPY NZDCHF EURUSD GBPUSD USDCAD EURJPY | chưa tải USDJPY EURGBP GBPJPY và một số cross khác |
| CFD đã tải (8) | SILVER.i#, OILCash#, US100Cash#, US30Cash#, JP225Cash#, BRENTCash#, GER40Cash#, UK100Cash# | US100 = NAS100 (anh đã tắt cảnh báo NAS100 — chỉ báo cáo nghiên cứu, không đề xuất bật alert) |
| Order-flow CME Sierra (.scid) | 6A 6E 6B 6C 6J (Z6), SI, CL | Z6 chỉ thanh khoản từ ~14/09/2026 (~9 tuần). Chỉ thăm dò, không đủ A/B. Không chạy syncTicks Fxaurum |
| Tick thật trong tester p6 | US500 / GOLD đủ 18 tháng. GER40, US30, NZDJPY chỉ có file stub 202611.tkc ~2 KB | test Model=4 bị "no history data" cho đến khi tải đủ .tkc |

Chi phí mô phỏng: spread từng nến Ultra Low + 0,5×trượt; swap từ `swap_long/swap_short` (nhân 3 thứ Tư, kể cả khi swap_mode=0); CFD chỉ số swap_mode=3 (lãi suất %) nên swap chỉ là xấp xỉ. Flatten thứ Sáu ≥21:00 server. Thời gian server Europe/Athens.

## 2. Họ tín hiệu hồi quy đã thử (≈47 biến thể × 4 phiên × lưới quản lý)
- z-score giá so MA (M5/M15/H1), RSI2 (± lọc EMA200), IBS, Asia-range fade / phá thất bại.
- Họ dài hạn H4/D1: z-score, RSI2, IBS (`L_*`).
- Spread/cointegration phần dư log-giá AUD vs NZD (cửa sổ 3 và 10 ngày).
- Quản lý: (a) scalp SL/TP theo ATR-H1, (b) giỏ DCA không SL + chốt giỏ (bước nhồi, TP, maxN 3/5), flatten cuối tuần.
- Phiên: all / Á (UTC 0-7) / London (7-12) / NY (12-20).

## 3. Kết quả sàng lọc (23 mã, 39.915 cấu hình giỏ, 27.977 scalp)
**Scalp SL/TP (kỳ vọng ATR-H1, đã trừ spread+trượt):** trung vị IS −0,23 ATR, OOS −0,30 ATR. Chọn theo IS: 7 cấu hình → **1 dương OOS**. Scalp hồi quy chết vì phí (spread ≈ 0,5 ATR-M5). Không đưa scalp nào vào sổ.

**Giỏ DCA (kiểu vàng/SP500 đang thắng):** chọn IS: lãi>0 và lãi/DD ≥3; qua OOS: lãi>0 và lãi/DD ≥1.
| Bộ tín hiệu | Cấu hình | Qua chọn IS | Qua OOS |
|---|---|---|---|
| **Thật (fade)** | 39.915 | 177 | **47** |
| **Placebo** (hướng ngẫu nhiên, cùng thời điểm) | 39.995 | 287 | **57** |
| **Gương (theo đà)** | 39.999 | 281 | **49** |
→ **Cả họ, tín hiệu thật không tốt hơn ngẫu nhiên** (47 vs 57 vs 49), kể cả sau khi thêm CFD.

Tỉ lệ dương cả IS lẫn OOS: AUD 6,5%; NZD 2,2%; FX khác 9,0%; CFD 18,6% (cao hơn FX nhưng placebo/gương cũng ra nhiều: xem từng mã ở mục 4). **AUD không đặc biệt.**

## 4. Ứng viên & pin kiểm (giỏ, 1 lot, USD) — kết luận từng tài sản

**FX (nhắc lại):**
| | NZDJPY `L_ibs_240` London, gap 1, TP 2, N3 | EURAUD `L_z240_50_2.0` NY, gap 2, TP 1, N3 |
|---|---|---|
| IS / OOS (DD OOS) | +8.000 / **+3.000 (DD 2.088)** | +2.534 / +2.282 (DD 1.778) |
| Placebo 40 seed | 97,5% | 90% |
| Spread ×2 (OOS) | **−934** (cả kỳ +1.479) | **−1.915** |
| Spread ×3 | −4.218 | −3.182 |
**EURAUD: LOẠI** (hỏng spread ×2, placebo <95%).
**NZDJPY: yếu** — OOS +3.000 / DD 2.088, sống trễ/swap/hai chiều, nhưng lãi OOS mất khi spread ×2, chỉ 22 giỏ / 6 tháng, phụ thuộc flatten thứ Sáu. Không đưa vào sổ khi chưa forward demo + tick MT5.

**CFD — số người qua cửa IS+OOS (thật / placebo / gương):** OIL 13 / 2 / 2; US100 13 / 7 / 7; US30 7 / 8 / 0; GER40 10 / 7 / 6; JP225 0 / 4 / 2; BRENT 0 / 4 / 8; UK100 0 / 0 / 5; Silver 0 / 0 / 3. JP225/BRENT/UK100/Silver: **không có ứng viên thật**. Nhiều “passer” cùng một tín hiệu, chỉ đổi gap/N.

Pin trên cấu hình đại diện (đã chạy `fx_battery.py`):

| | OIL `L_rsi2_1440` all, gap 2, TP 1, N3 | US100 `L_rsi2_1440` all, gap 1, TP 2, N3 | US30 `L_z240_20_2.5` NY, gap 1, TP 4, N5 | GER40 `z15_30_3.0` Á, gap 1, TP 1, N5 |
|---|---|---|---|---|
| OOS net / DD @ 1 lot | **+768 / 236** (37 giỏ, 37 thắng) | **+1.762 / 603** (34 giỏ) | **+7.053 / 2.286** (26 giỏ, 14 thắng) | **+1.687 / 545** (93 giỏ, IS +7.165) |
| Placebo 40 seed | **85%** | 95% | **100%** | **100%** |
| Spread ×2 (OOS net) | +765 | +1.762 | +7.291 | +1.231 |
| Spread ×3 (OOS net) | +765 | +1.762 | +7.189 | +414 |
| Trễ 2 nến / bỏ swap | gần như không đổi | không đổi | không đổi | +1.205 / +1.687 |
| Chỉ mua / chỉ bán | cả hai dương | cả hai dương | cả hai dương | cả hai dương |
| Tương quan sổ / lot DD=5% | −0,04 / 21,2 | **+0,26** / 8,3 | −0,04 / 2,19 | +0,01 / 9,17 |

**OIL — LOẠI.** Pin chi phí sống, nhưng placebo chỉ 85% (<95%). 37/37 giỏ thắng, lãi nhỏ: dễ là bias chọn. Không đưa vào sổ.

**US100 (NAS100) — không đề xuất.** Pin sống (placebo 95%, spread ×2 giữ +1.762), nhưng (i) đây là NAS100 — anh đã tắt cảnh báo, (ii) tương quan sổ +0,26, (iii) cả họ CFD thật không hơn placebo, (iv) 34 giỏ. Chỉ ghi nhận nghiên cứu, không bật tín hiệu.

**US30 — ứng viên giấy tốt nhất trong nhóm OIL/US100/US30.** OOS +7.053 / DD 2.286, placebo 100%, spread ×3 vẫn +7.189, DD sổ gộp không tăng (6,0%). Nhưng chỉ 26 giỏ / 14 thắng, US30 cùng họ chỉ số với SP500 (dù tương quan ngày của tín hiệu này đo được −0,04), chưa có tick MT5. **Chưa đưa vào sổ.**

**GER40 (ngoài ba mã trên, để đủ bức tranh):** pin đầy đủ nhất (placebo 100%, spread ×3 còn dương, hai chiều dương). Lưu ý: chọn từ lưới lớn, phiên Á thanh khoản mỏng, điền lệnh thật có thể kém. Biến thể z5_30_2.5 Á lãi OOS lớn hơn (+6.512 / DD 2.591) nhưng **hỏng spread ×3** (cả kỳ −1.297). Chưa tick MT5. **Chưa đưa vào sổ.**

## 5. Tác động sổ 100k và tài khoản 100 USD cent (OOS 6 tháng, sổ proxy v5_G30: +74.942, DD 6,0%)
Lot chỉnh để DD riêng của hệ = 5% của 100k (cent: DD riêng ≈ 5 USD).
| Thêm vào sổ | Corr ngày | Lot 5% | Lãi thêm 6T | DD sổ gộp | Cent 100 USD (6T) |
|---|---|---|---|---|---|
| NZDJPY | +0,20 | 2,44 | +7.312 | 6,9% | +7,3 USD |
| EURAUD (đã loại) | −0,14 | 2,81 | +6.418 | 7,2% | +6,4 |
| GER40 z15 Á | +0,01 | 9,17 | +15.470 | 7,0% | +15,5 |
| US30 z240 NY | −0,04 | 2,19 | +15.427 | 6,0% | +15,4 |
| US100 RSI2 (NAS100) | +0,26 | 8,30 | +14.619 | 6,3% | +14,6 |
| OIL RSI2 | −0,04 | 21,2 | +16.299 | 5,6% | +16,3 |

Lãi cent ~7–16 USD / 6 tháng, nhỏ so với hệ vàng/SP500 hiện có. **Không đề xuất thêm vào sổ hay mở lệnh.**

## 6. Order-flow futures CME → CFD (thăm dò, ~9 tuần)
90 phép thử (6A→AUDUSD, 6E→EURUSD, 6B→GBPUSD, 6C→USDCAD, SI→Silver; delta/imbalance/lệnh lớn 5/15/60 phút).
- 6A, 6E: không có tín hiệu. 6B yếu. **6C IC −0,029 (7/18), SI IC −0,036 (12/18, t tới −4,0)**: dòng lệnh lớn đảo chiều sau 15–60 phút.
- Lãi gộp fade z>2 ≈ 0,2–1,5 pip FX / ≈0,032 USD Silver — **dưới spread**. 26/90 phép |t|>2: có tín hiệu thống kê nhưng nhỏ hơn chi phí.

## 7. MT5 100% tick thật
Python kỳ vọng OOS @ 1 lot: NZDJPY +3.000 / DD 2.088 (22 lệnh vào); GER40 z15 +1.687 / DD 545 (21 lệnh); US30 +7.053 / DD 2.286 (9 lệnh). EA `BRAIN_XuLiLenh_fx` (flatten thứ Sáu, `InpTuanDong=true`), `InpTF=16385` (PERIOD_H1), CSV `InpVao=4`.
- Lần p4 / p6 đầu: 0 lệnh. Nguyên nhân 1: `InpTF=60` không phải PERIOD_H1 (ATR lỗi 4805, OnInit fail) — đã sửa `fx_mkq.py` → 16385.
- Lần p6 sau khi sửa TF: tester dừng “no history data”. Cả ba mã chỉ có stub tick 202611.tkc ~2 KB; không giống US500/GOLD (đủ file .tkc 18 tháng). Đang tải tick qua terminal p6 rồi chạy lại `q_p6_fx2.json`.
- Kết quả net/DD/số lệnh MT5 lúc này: **KHÔNG CÓ**.

## 8. Việc còn dang dở / lưu ý
- Chưa xác nhận tick MT5 (mục 7). Khi có file .tkc đủ tháng 2026-06..11, chạy `E:\GrokWork\mt5_runs\runq.py` + `q_p6_fx2.json` (slot p6, không đụng terminal XM chính).
- Có thể mở rộng thêm USDJPY/GBPJPY/EURGBP rồi `code/run_batch.sh`.
- Bảo mật: lần trước một lệnh trên máy nhà in nhầm biến môi trường (có AIBOX_API_KEY, SO_SANH_*). Không chép lại giá trị; anh nên đổi các key đó.

## 9. Chạy lại / cấu trúc
- `code/fxlib.py`, `fxsig.py`, `fx_screen.py`, `fx_basket.py` (`PLACEBO=0` placebo, `PLACEBO=-2` gương), `fx_select.py` / `fx_summary.py`, `fx_battery.py`, `fx_port.py`, `fx_of.py`, `fx_mt5prep.py`, `fx_mkq.py`, `engine2x.py`.
- Kết quả: `results/summary.json`, `of_ic.csv`, `bat_*.json`, `port_fx.json`. M1 thô không đẩy git (nằm `E:\GrokWork\bt_fx\m1`).
- EA: `ea/BRAIN_XuLiLenh_fx.mq5` = r5 + `InpTuanDong` (flatten thứ Sáu).
- Hàng đợi MT5: `mt5/q_p6_fx2.json`.
