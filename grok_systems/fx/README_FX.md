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

**US30 — pin Python đạt, ứng viên giấy mạnh; chưa đưa vào sổ (chờ MT5).** OOS +7.053 / DD 2.286, placebo 100%, spread ×3 vẫn +7.189, trễ/swap/khử xu hướng/hai chiều đều dương. Chỉ 26 giỏ / 14 thắng. Cùng họ chỉ số với SP500, nhưng tương quan ngày với sổ Cân bằng đo được thấp (ghép 100k +0,05; chỉ SP500 −0,07).

**GER40 z15 Á — pin Python đạt (đủ bộ như US30/NZDJPY); chưa đưa vào sổ (chờ MT5).** Placebo 100%; spread ×2 OOS +1.231 / DD 1.378; spread ×3 OOS còn +414 / DD 1.404; trễ 2 nến OOS +1.205; bỏ swap không đổi; khử/đảo xu hướng OOS +1.218 / +1.157; chỉ mua +1.352, chỉ bán +512. Gap 5% đẩy DD cả kỳ lên 7.267–7.875 (khoảng 4× DD cả kỳ 1.988). Lưu ý: chọn từ lưới lớn, phiên Á thanh khoản mỏng, điền lệnh thật có thể kém. Biến thể z5_30_2.5 Á lãi OOS lớn hơn (+6.512 / DD 2.591) nhưng **hỏng spread ×3** (cả kỳ −1.297) — không dùng.

## 5. Tác động sổ 100k Cân bằng, sổ chỉ SP500, và tài khoản 100 USD cent
**Toàn bộ mục này là Python (chờ MT5).** Sổ gốc = kịch bản Cân bằng đã chốt, vốn 100k, số **MT5 100% tick**: ghép Vàng+SP500 +161.631 / DD 6,8%; chỉ SP500 +81.769 / DD 9,4%. Đường vốn sổ được dựng lại từ equity từng hệ MT5 (khớp đúng net/DD chính thức). US30/GER40 ghép bằng equity Python ngoài mẫu, lot để DD riêng của hệ thêm = 5% của 100k (5.000 USD). Số liệu chi tiết: `results/port_official.json`.

| Thêm vào | Sổ | Corr ngày | Lot 5% | Lãi thêm 6T | DD sổ gộp |
|---|---|---|---|---|---|
| US30 | Ghép 100k Cân bằng | +0,05 | 2,19 | +15.427 | 6,8% → **6,2%** |
| GER40 | Ghép 100k Cân bằng | +0,01 | 9,17 | +15.470 | 6,8% → 6,8% |
| Cả hai (mỗi hệ lot 5%) | Ghép 100k Cân bằng | — | 2,19 + 9,17 | +30.897 | 6,8% → **6,3%** |
| US30 | Chỉ SP500 Cân bằng | −0,07 | 2,19 | +15.427 | 9,4% → 9,4% |
| GER40 | Chỉ SP500 Cân bằng | +0,02 | 9,17 | +15.470 | 9,4% → 10,0% |
| Cả hai (mỗi hệ lot 5%) | Chỉ SP500 Cân bằng | — | 2,19 + 9,17 | +30.897 | 9,4% → 10,9% |

Tài khoản **100 USD cent (sách SP500)**: DD riêng ≈ 5 USD → khoảng 0,0022 lot chuẩn US30 hoặc 0,0092 lot chuẩn GER40, lãi ước lượng **+15 USD / 6 tháng** mỗi hệ. **Cỡ hợp đồng Exness US30c / GER40c: KHÔNG CÓ.** File `symbols_xm.csv` là XM Ultra Low: 1 lot US30Cash# và GER40Cash# ≈ 1 USD/điểm (`tick_value` 0,01 / `tick_size` 0,01), lot tối thiểu 0,10 — lớn hơn lot 5 USD ở trên. Số cent chỉ là phép quy đổi theo lot chuẩn XM, không phải lệnh Exness.

(Tham chiếu cũ, sổ proxy Python v5_G30 +74.942 / DD 6,0%: NZDJPY corr +0,20, lot 2,44, +7.312, DD 6,9%, cent +7,3 — không khuyến nghị vì pin spread ×2 thất bại.)

**Đã có MT5 cho US30 (khớp) và GER40 (yếu hơn Python). Cả hai đều quá đắt ở lot tối thiểu XM trên vốn 100 USD — không thêm vào sổ.** Số 100k ở bảng trên chỉ là tham chiếu cũ.

## 6. Order-flow futures CME → CFD (thăm dò, ~9 tuần)
90 phép thử (6A→AUDUSD, 6E→EURUSD, 6B→GBPUSD, 6C→USDCAD, SI→Silver; delta/imbalance/lệnh lớn 5/15/60 phút).
- 6A, 6E: không có tín hiệu. 6B yếu. **6C IC −0,029 (7/18), SI IC −0,036 (12/18, t tới −4,0)**: dòng lệnh lớn đảo chiều sau 15–60 phút.
- Lãi gộp fade z>2 ≈ 0,2–1,5 pip FX / ≈0,032 USD Silver — **dưới spread**. 26/90 phép |t|>2: có tín hiệu thống kê nhưng nhỏ hơn chi phí.

## 7. MT5 100% tick thật
Cửa sổ OOS 2026.06.01–11.27, EA `BRAIN_XuLiLenh_fx`, flatten thứ Sáu 21:00, `InpTF=16385`, CSV `InpVao=4`, slot p6, 100% tick thật. **Số dưới đây ưu tiên vốn thật 100 USD (10k cent).** Lot tối thiểu XM Ultra Low = 0,10. Cỡ hợp đồng Exness cent: **KHÔNG CÓ**.

Lần chạy thành công: GER40 xong lúc ~19:58 (3635 giây, chạy từ 18:58); US30 21:09:40–21:16:29 (408 giây). PID an toàn: đã tắt đúng runq cũ 11396, p6 terminal 19628 và metatester 19588; **không đụng** XM chính 13548, claude, Sierra. `runq_fx` (PID 1528) chết lúc ~21:18 vì `tasklist` timeout khi đang theo dõi NZDJPY; tester NZDJPY (terminal 21988, agent 7672, bắt đầu 21:16:30) lúc đó vẫn chạy. Báo cáo NZDJPY: **KHÔNG CÓ** (chưa thu được file).

### 7.1. So sánh MT5 vs Python @ 1 lot

| Hệ | Python net / DD | MT5 net / DD | Lệnh / giỏ MT5 | PF | Tick | Lỗ giỏ lớn nhất | Ngày tệ nhất | Khớp? |
|---|---|---|---|---|---|---|---|---|
| US30 L_z240 NY | +7.053 / 2.286 | **+9.085 / 2.455** | 24 lệnh, 8 giỏ (7W 1L) | 17,02 | 100% real | **−567** (30/10 18:01–21:00) | **30/10/2026 −567** | Có: cùng dấu, lãi +29%, DD +7% |
| GER40 z15 Á | +1.687 / 545 | **+983 / 1.110** | 37 lệnh, 21 giỏ (19W 2L) | 2,07 | 100% real | **−684** (30/10 03:16–21:00, 3 chân, flatten) | **30/10/2026 −684** | Không: lãi chỉ còn 58%, DD gấp 2,0 lần |
| NZDJPY IBS London | +3.000 / 2.088 | **KHÔNG CÓ** | — | — | — | KHÔNG CÓ | KHÔNG CÓ | Chưa có số MT5. Python đã trượt spread ×2. |

Cả US30 và GER40 đều lỗ nặng cùng một ngày 30/10/2026 (flatten thứ Sáu) — nếu chạy chung, rủi ro cộng dồn.

### 7.2. Quy ra tài khoản 100 USD (XM min lot 0,10)

| Hệ | Min lot 0,10: lãi 6T / DD / lỗ giỏ lớn nhất | Lot để DD ≈ 5 USD | Kết luận 100 USD |
|---|---|---|---|
| US30 | **+909 / DD 245 / −57** | 0,0020 lot → khoảng +18,5 USD / 6T | **Quá đắt.** DD min lot 245 USD > vốn 100 USD. Lot 5 USD nhỏ hơn min 0,10. Không thêm vào sổ. |
| GER40 | **+98 / DD 111 / −68** | 0,0045 lot → khoảng +4,4 USD / 6T | **Quá đắt**, và MT5 yếu hơn Python. DD min lot 111 USD > vốn 100 USD. Không thêm vào sổ. |
| NZDJPY | KHÔNG CÓ | — | Không thêm (pin spread ×2 đã trượt; thiếu MT5). |

## 8. Chỉ số khác vs 100 USD (t173u, bước đầu)
GER/US30/US100 đắt vì min lot 0,10 × khoảng 1 USD/điểm, ATR giờ ~65–107 điểm → một nhịp ATR min lot đã ~7–11 USD. Đã có M1 sẵn: UK100, JP225 (và GER40/US30/US100). Các mã khác chưa tải M1 (p6 đang/đã chạy tester NZDJPY — chưa xuất được).

Chi phí 1 nhịp ATR H1 ngoài mẫu tại **lot tối thiểu XM** (tỷ giá từ M1: EURUSD 1,093; GBPUSD 1,309; AUDUSD 0,664; USDJPY 159,6 qua EURJPY/EURUSD):

| Mã XM | Min lot | USD/điểm tại min | ATR H1 | $ / ATR tại min | Đã có M1? | Sàng giỏ (lọc IS calmar≥3, OOS calmar≥1) |
|---|---|---|---|---|---|---|
| JP225Cash# | 0,10 | 0,00063 | 347 | **0,22** | Có | Thực 0 pass; placebo 4 pass — không có edge bền |
| UK100Cash# | 0,10 | 0,131 | 24 | **3,10** | Có | Thực 0 pass; placebo 0 — chưa có hệ đạt lọc |
| GER40Cash# | 0,10 | 0,109 | 65 | 7,09 | Có | Xem §7 — quá đắt ở min lot |
| US100Cash# | 0,10 | 0,100 | 106 | 10,61 | Có | Đã loại / NAS100 đang tắt cảnh báo |
| US30Cash# | 0,10 | 0,100 | 107 | 10,71 | Có | Xem §7 — quá đắt ở min lot |
| CHN50Cash# | 0,01 | 0,010 | KHÔNG CÓ M1 | — | Chưa | Ứng viên rẻ (min lot nhỏ). Exness cent: KHÔNG CÓ |
| GerMid50Cash# | 0,01 | 0,011 | KHÔNG CÓ M1 | — | Chưa | Ứng viên rẻ. Exness: KHÔNG CÓ |
| TaiwanCash# | 0,05 | 0,050 | KHÔNG CÓ M1 | — | Chưa | Trung bình. Exness: KHÔNG CÓ |
| AUS200Cash# | 0,10 | 0,066 | KHÔNG CÓ M1 | — | Chưa | Có thể rẻ hơn UK100. Exness: KHÔNG CÓ |
| CA60Cash# | 0,10 | 0,070 | KHÔNG CÓ M1 | — | Chưa | Exness: KHÔNG CÓ |
| EU50 / FRA40 / Spain / IT40 / NETH25 | 0,10 | 0,109 | KHÔNG CÓ M1 | — | Chưa | Cùng thang EUR với GER40. Exness: KHÔNG CÓ |
| SWI20Cash# | 0,10 | 0,120 | KHÔNG CÓ M1 | — | Chưa | Exness: KHÔNG CÓ |
| HK50Cash# / ChinaHCash# | 0,10 | KHÔNG CÓ (thiếu USDHKD) | KHÔNG CÓ M1 | — | Chưa | Có thể rẻ nếu 1 lot = 1 HKD/điểm. Exness: KHÔNG CÓ |

Kết luận tạm: trên vốn 100 USD, US30 / US100 / GER40 **không khả thi ở lot tối thiểu XM**. UK100 rẻ hơn nhưng chưa có hệ đạt lọc. JP225 rất rẻ nhưng tín hiệu không hơn bản giả. Cần tải M1 rồi chạy cùng pipeline cho CHN50, GerMid50, AUS200, EU50, FRA40, Spain, HK50, IT40, CA60, Taiwan khi p6 rảnh.

## 9. Việc còn dang dở / lưu ý
- **NZDJPY MT5: KHÔNG CÓ số.** Tester p6 21988/7672 đã chạy từ 21:16:30; `runq_fx` chết vì tasklist timeout; bộ theo dõi `fx_watch.py` (22160) không hỏi được PID (`tasklist` timeout). Cần thu `fx_nzdjpy_ibs240_ldn.htm` từ `E:\mt5_tester\p6` hoặc `E:\GrokWork\mt5_runs\reports` sang `C:\Users\DUNG\v3work\out\mt5\reports\`, đối chiếu Python, rồi mới ALL DONE.
- Tải M1 các chỉ số còn thiếu (p6, MaxBars đã 1.000.000), chạy screen/basket/placebo/battery, xếp theo DD USD tại min lot. Script sẵn: `pc_tools/dl_m1_idx.py`.
- Chép README/PDF/`port_official`/báo cáo MT5 mới vào `E:\GrokWork\bt_fx` khi shell máy nhà thông (CopyFromBox không ghi được ổ E).
- PDF tóm tắt cũ (2 trang, chưa có số MT5): `pdf/TomTat_NghienCuu_FX_2026-11-28.pdf` — cần bản cập nhật sau khi có NZDJPY.
- Bảo mật: lần trước một lệnh trên máy nhà in nhầm biến môi trường (có AIBOX_API_KEY, SO_SANH_*). Không chép lại giá trị; anh nên đổi các key đó.

## 10. Chạy lại / cấu trúc
- `code/fxlib.py`, `fxsig.py`, `fx_screen.py`, `fx_basket.py` (`PLACEBO=0` placebo, `PLACEBO=-2` gương), `fx_select.py` / `fx_summary.py`, `fx_battery.py`, `fx_port.py`, `fx_of.py`, `fx_mt5prep.py`, `fx_mkq.py`, `engine2x.py`.
- Kết quả: `results/summary.json`, `of_ic.csv`, `bat_*.json`, `port_fx.json`, `port_official.json`, `idx_cost.json`, `mt5/reports/`; PDF `pdf/TomTat_NghienCuu_FX_2026-11-28.pdf`. M1 thô không đẩy git (nằm `E:\GrokWork\bt_fx\m1`).
- EA: `ea/BRAIN_XuLiLenh_fx.mq5` = r5 + `InpTuanDong` (flatten thứ Sáu).
- Hàng đợi MT5: `mt5/q_p6_fx2.json`.
