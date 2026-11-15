# Chỉ thị SEEKER — bám xu hướng tăng chỉ số Mỹ

Phiên: 2026-11-15 (Asia/Saigon). Nhánh `evo/huong-xu-huong-chi-so`. Không đụng `main`, không bật điều phối / routine, không tài khoản thật.

Anh Vanh: chỉ số (US500, US100) có bản chất tăng dài hạn; cần chiến lược bám theo, và lọc nốt ứng viên cũ cùng hướng đó.

Đọc trước: `docs/evo/BAI_HOC_VA_PHI.md` (nhánh `evo/sua-tieu-chi`, đủ mục 1–7) và `docs/evo/PREREG_GIA_THUYET_2026-11-15_KET_QUA.md`.

## 1. Phạm vi phiên mới

- Chiều: **long-only / long-biased**. Không săn short thuần, không scalping FX.
- Tài sản: **US500, US100** chính; US30, US2000 phụ. Tên XM: `US500Cash#`, `US100Cash#`, `US30Cash#`, `US2000Cash#`.
- Khung: **D1 / H4**. Không ưu tiên H1 trở xuống (phí/lãi gộp xấu hơn, bài 3).
- Mục tiêu vận hành: lời sau phí, DD tối đa 80%, ≥ 10%/năm, vào lệnh theo luật, OOS thật.

## 2. Gia đình cần tìm

1. **Time-series momentum** (12–1 tháng, absolute momentum trên chính chỉ số).
2. **Bộ lọc MA / chế độ** (SMA 10 tháng Faber, SMA200, EMA50/200 — đứng ngoài khi dưới đường).
3. **Dual momentum** (absolute + relative giữa US100/US500/trái phiếu hoặc tiền mặt).
4. **Vol-targeting / risk parity exposure** (giảm lot khi vol/VIX cao, tăng khi êm — không nhầm với “cắt lỗ thảm họa 6–10%” đã thất bại ở bài 6).
5. **Mua nhịp giảm trong xu hướng tăng** (dip khi đã trên SMA200 / chế độ tăng; khác mean-reversion thuần không lọc trend).
6. **Đòn bẩy theo chế độ** (1–1.5× khi trên bộ lọc; không 2–3× buy-and-hold trần).

Ưu tiên nguồn đã có track record / bài nghiên cứu (Faber, Moskowitz TSMOM, Antonacci, CTA long-equity, paper có OOS), không quét EA diễn đàn vô tội vạ.

## 3. Việc không lặp lại

Đã kiểm, **không sống sót** (không viết EA mới, không gắn thêm demo):

| Việc | Kết quả ngắn |
|---|---|
| IBS rổ US100+US500+US30 | OOS 5.7%/năm, p = 0.16; IS lỗ nặng |
| IBS US500 đơn | OOS p = 0.051, trượt cửa; yếu hơn US100 đơn (p = 0.073) |
| IBS US100 (ứng viên demo 3×) | Cửa p không đạt trong bài tiền đăng ký; edge yếu |
| RSI(2)<10 + SMA200 US100 | OOS p = 0.42; IS/OOS đều mỏng |
| Đáy 5 phiên, giữ 5 phiên US100 | OOS p = 0.41 |
| Long close→open (overnight) US100/US500 | Spread + financing ~6.5%/năm ăn hết; Sharpe OOS âm |
| Trước lễ NYSE ∪ FOMC US100 | OOS p = 0.39 |
| SMA 10 tháng 1× US100 (Faber) | OOS ~8%/năm, p = 0.46: **drift, không phải edge vào lệnh** |
| IBS rổ GER40+JP225+UK100+XAU | OOS Sharpe −0.10, p = 0.91 |
| Đòn bẩy 2–3× buy-and-hold | Vỡ trần DD 80% (2000, 2022) |
| Không SL / giữ đến hòa vốn ở 3× | Cháy (2022-10, 1987) |
| 32 cách SL/TP/trailing/chốt sớm trên IBS US100 | Không cách nào thắng bản gốc trên IS |
| Cắt lỗ thảm họa 6–10% / ATR 3–5 + giảm lot VIX | Không qua IS, không giảm DD 3× OOS |

US30 IBS đơn và XAU turn-of-month từng đẹp OOS thô nhưng **không nằm trong 8 giả thuyết chính** — muốn xét phải tiền đăng ký lại, không được chọn sau khi nhìn.

Cặp USD FX: ưu tiên thấp (đứng yên).

## 4. Chuẩn so với mua-và-giữ (bắt buộc)

Hệ xu hướng **không được gọi là đạt chỉ vì lãi dương**. Phải thắng **mua-và-giữ cùng tài sản, cùng cửa sổ, cùng phí XM**, ở rủi ro / phơi nhiễm tương đương:

- Sharpe cao hơn buy-and-hold, **hoặc**
- Lãi gần bằng và DD thấp hơn rõ,

rồi mới xét cửa OOS (≥ 30 lệnh nếu hệ vào/ra thường xuyên; hệ chế độ tháng được xét theo Sharpe / CAGR / p, như cửa (g) bài tiền đăng ký), p random-shift ≤ 0.05, BH-FDR trên tập **đã đóng băng trước test**.

Lệch phơi nhiễm (hệ đứng ngoài 20–30% thời gian, hoặc chỉ vào 5% bar) phải so Sharpe/Calmar, hoặc đòn bẩy để DD/phơi nhiễm tương đương — không lấy CAGR nhỏ rồi gọi là “thắng” vì DD thấp.

Tune chỉ trên IS (< 2016), đóng băng, nhìn OOS (2016+) **một lần**. Python lạc quan hơn MT5: hệ còn sống mới đưa tester.

## 5. Mô hình phí (XM Ultra Low demo, đo 15/11/2026)

| Mã | Spread trung vị | Financing long | Triple |
|---|---|---|---|
| US500Cash# | 0.55 điểm | 6.49%/năm | Thứ Sáu |
| US100Cash# | 1.95 điểm | 6.48%/năm | Thứ Sáu |
| US30Cash# | 3.90 điểm | 6.48%/năm | Thứ Sáu |
| US2000Cash# | 0.45 điểm | 6.82%/năm | Thứ Sáu |

Nguồn: `docs/evo/costs_xm_us_index.json` (kho IBS) / bài học phí. Không vào lệnh giờ 00:00 server (rollover). Lot tối thiểu / bước US100Cash# = 0.1. Đòn bẩy 1:1000, stop-out 20%: ở 3×, giá ngược ~33% là cháy. Tỷ lệ financing cố định 6.5% hơi chặt với giai đoạn lãi suất thấp 2016–2021 và không đúng từng năm 1970–2015 — OOS 2016+ vẫn phải trừ phí hiện tại.

**Chuẩn buy-and-hold 1× sau phí (Yahoo D1, cùng mô hình, 2016-01-01 → 2026-11-13):** US100 ~11.0%/năm, Sharpe 0.59, DD 40.6%; US500 ~5.8%/năm, Sharpe 0.44, DD 32.7%. US500 1× **không đạt** cửa 10%/năm sau swap. Đây là đối thủ, không phải sàn để “có lãi là được”.

## 6. Tiền đăng ký + FDR

Mỗi lô giả thuyết: viết luật + tham số + cửa IS/OOS, commit đóng băng, **rồi mới** chạy. Tập nhỏ, có lý do kinh tế. Benjamini–Hochberg trên đúng N đã đăng ký. Không tối ưu lại sau OOS. Ô “xác nhận” ngoài tập chính không được đưa vào EA/demo.

## 7. SEEKER đọc hướng ở đâu

Không có file “hướng phiên” trên `main` trước đây. Seeker đọc:

| Chỗ | Vai trò |
|---|---|
| `config/nguon_seeker.json` | Danh sách nguồn HTTP/RSS — không phải đề bài phiên |
| `keywords_nguon.py` `DANH_MUC` + `config/keyword_bo_sung.json` | Ngân hàng từ khóa (tự nạp khi import) |
| `nguon_kham_pha.py` | Vòng khám phá dùng một danh sách danh mục cứng |
| `nhan/nguon_seeker.py` | Đã có phong cách `xu_huong` (GitHub query) |
| `roles/SEEKER.md` | Mô tả vai |

Trên nhánh này (không đổi hành vi `main`):

- **Chỉ thị đủ:** file này.
- **Hợp đồng phiên (máy đọc được):** `config/huong_seeker.json` — `keywords_nguon._tai_huong_seeker()` gộp `tu_khoa` vào `DANH_MUC["xu_huong_chi_so"]` nếu file có; file vắng thì như cũ.
- Cùng danh mục cũng nằm trong `config/keyword_bo_sung.json`.
- `nguon_kham_pha.py` thêm `xu_huong_chi_so` vào vòng từ khóa (`.get`, an toàn nếu thiếu).
- `roles/SEEKER.md` trỏ về file này.

Không bật Seeker 24/7 từ nhánh này nếu điều phối đang tắt — chỉ thị để **phiên mới** khi anh yêu cầu chạy.

---

## 8. Lọc ứng viên cũ (nao.db, đọc 15/11/2026)

Kho chính `gia_thuyet` **không có** US100 / US30 / US2000. Chỉ **US500CASH: 46 hệ** (D1 16, H4 12, H1 18). Không hệ nào vào `khang_dinh` / MT5.

- 17 “PASS” Python cũ, 29 FAIL. Cửa sổ ngắn (~4.1 năm H1/H4, ~6.3 năm D1) — **không phải** IS < 2016 / OOS 2016+ trên lịch sử dài.
- Họ: quay về trung bình 21, xu hướng 11, biến động 6, phá vỡ 4, dòng tiền 2, lịch 1, phiên 1.
- 11 hệ `ho=xu_huong` trên US500: 4 PASS cũ (`ema_cross_sell` D1 là **short**; `z_swap_meter_short` H1 là short; `bieu_diep_xu_huong_chinh_tren_khung_nho` H1 p=0.06; `theo_xu_huong_khi_bien_dong_em` H1 p=0.46). Không hệ long-trend nào thắng buy-and-hold về lãi ở 1×. `z_swap_meter_short` chỉ hơi hơn Sharpe (0.61 vs 0.55) nhưng CAGR 1.5% vs BH 9.2%.
- Cờ “thắng BH” trong `cong` (4 thắng lãi, 6 thắng Sharpe) hầu hết là hệ **phơi nhiễm rất thấp** đã khớp rủi ro, hoặc mẫu bé (ví dụ `demand_zone_touch_rejection` H4: 12 lệnh, PF 17.9, DD −0.1%, p=0.025 — dấu hiệu khớp nhiễu). Không hệ nào là pass thật.
- Toàn kho: 180 giả thuyết `ho=xu_huong` (mọi symbol, chủ yếu FX). 41 PASS cũ. Không dùng FX làm ứng viên “bám chỉ số Mỹ”.

Bảng 46 dòng: `docs/evo/loc_us500_nao_db.txt`.

US100 IBS (và các giả thuyết 15/11) **không nằm** trong `nao.db`; đã kiểm riêng, không phải hệ xu hướng.

## 9. Kiểm lại nhẹ 5 luật (D1, phí XM, vs mua-và-giữ)

Mã: `tools/kiem_dinh/evo/loc_xu_huong_chi_so.py`. Dữ liệu Yahoo `gspc` / `ndx` (1970/1985–2026-11-13), fill open kế, financing thứ Sáu ×3. IS < 2016, OOS ≥ 2016. **Không** random-shift, **không** tiền đăng ký — không được gọi là pass. Bảng thô: `docs/evo/loc_xu_huong_chi_so_bang.txt`.

Đối chiếu Faber US100 với bài tiền đăng ký: IS 26 lệnh, 4.8%/năm, Sharpe 0.34, DD 48.6%; OOS ~8%/năm, Sharpe 0.53, DD 28.7% — khớp.

| Luật | US500 OOS (vs BH 5.8% / Sh 0.44 / DD 33%) | US100 OOS (vs BH 11.0% / Sh 0.59 / DD 41%) | Kết luận |
|---|---|---|---|
| Faber SMA 10 tháng 1× | 1.5%, Sh 0.19, DD 29% | 7.9%, Sh 0.53, DD 29% | Không thắng BH. Đúng bài học: drift, p đã = 0.46 |
| Lọc SMA200 | 3.2%, Sh 0.34, DD 25% | 9.4%, Sh 0.62, DD 24% | US100 OOS Sharpe **nhỉnh** 0.03, DD thấp hơn, nhưng CAGR thấp hơn BH; IS **thua** BH (3.8% / 0.30 vs 5.8% / 0.35). Chưa đăng ký, chưa có p — **không pass** |
| EMA50 > EMA200 | 2.6%, Sh 0.26, DD 30% | 9.8%, Sh 0.59, DD 29% | US100 Sharpe hòa BH, DD thấp hơn, lãi thấp hơn. Không pass |
| RSI(2)<15 giữ 1 (ứng viên cũ) | 4.1%, Sh 0.55, DD 21%; **IS −5.8%, Sh −0.64, DD 98%** | 5.4%, Sh 0.56, DD 18%; IS âm | OOS đẹp / IS đổ — không xét |
| Dip 10 bar + SMA200, giữ 7 (dịch D1 từ H4 cũ) | 1.4%, Sh 0.48, 19 lệnh, exp 5% | 1.1%, Sh 0.42, 10 lệnh, exp 3% | Không đủ lệnh, không tới 10%/năm, không phải cùng phơi nhiễm |

**Không ứng viên cũ nào, và không luật nào trong 5 lần kiểm lại, đạt pass thật so với mua-và-giữ trên OOS.** Gần nhất là lọc SMA200 trên US100 (OOS Sharpe hơi hơn, DD thấp hơn, lãi thấp hơn, IS không xác nhận). Nếu muốn kiểm chính thức: tiền đăng ký mới, nhìn OOS một lần, so đúng chuẩn mục 4 — không đưa vào EA/demo chỉ vì ô OOS này.

Buy-and-hold US100 1× sau phí đã ≥ 10%/năm và DD < 80% trên OOS: hệ mới phải thắng *cái đó*, không phải thắng “số dương”.

## 10. Việc chưa làm / không làm trong lượt này

- Không viết EA, không testers, không đổi forward demo (US100 IBS 3× vẫn là ứng viên đang chạy, không phải hệ xu hướng).
- Không đẩy/merge `main`.
- 73 `khang_dinh` còn CHO_KIEM không phải chỉ số — để nguyên.
