# V1 — Kivenara (2229059) + MCA100 (2153920) + Friday Pro (2344620)

Giờ Việt Nam (Asia/Bangkok, UTC+7). **Không commit.** Ngày ĐO: 09/11/2026.

Nguồn: `/workspace/mql5_hist/{ID}.csv`, phí XM `phi_xm_micro.json` / `chi_phi_do.json`, giá NQ=F (Yahoo) + XAU HistData NY7. Script: `v1_kivenara_mca100.py`. JSON: `v1_dich_nguoc_ket_qua.json`.

Ngưỡng chấp luật: **match ≥ 60%** (cùng chiều, ±1 bar khi có TF). V1 pass: **DD&lt;80%** và **CAGR&gt;10%** (OOS, WF 12/3, phí XM, hold_cap 30 ngày, risk 1%/lệnh, tối ưu SL/TP mult chỉ trên train).

---

## 0. Đếm lại lưới (cập nhật `MQL5_83_LOC_PHI.md` §0b)

Detector cũ gắn lưới **78/83** (quá nhạy: partial close / pending Buy–Sell Stop / multi-symbol).

Detector mới (gộp partial → đo trong từng mã → 3 hạng):

| Hạng | Số ĐO |
|---|---|
| **don_le** (max cùng chiều ≤2) | **8** |
| **pyramid** (max 3–7 + SL đáng kể) | **9** |
| **luoi** (max≥8 hoặc max≥4 & SL%&lt;20) | **65** |
| khong_file (2391347) | 1 |
| martingale (lot↑ sau lỗ) | **4** |

- Kivenara **2229059** → `don_le` (max=1, SL%=100)
- MCA100 **2153920** → `pyramid` (max=3, SL%=100)
- Friday Pro **2344620** → `pyramid` (max=5, SL%=99.7)

→ “Lưới thuần” ĐO = **65/83**, không còn 78.

---

## 1. Dịch ngược luật

### 1.1 Kivenara 2229059 (US100/NAS100)

| Mục | ĐO |
|---|---|
| n lệnh | 664 |
| Khoảng | 2024-02-21 → 2026-11-06 |
| Giờ vào | **18:30** (664/664) |
| buy% | 55.7 |
| SL med / TP med (điểm giá) | **100** / **165** |
| hold med | 3.06 giờ |
| Comment thoát | `[sl]` 645 · `[tp]` 9 · khác 10 |
| Win rate (profit&gt;0) | 57.4%; med profit 0.01 lot = 1.54 (nhiều `[sl]` vẫn + nhờ trail) |

**Match hướng (giá NQ=F):**

| Luật | Khung | ok/tot | match | ≥60% |
|---|---|---|---|---|
| **h1_off3_sma50** (close &gt; SMA50, broker GMT+3) | H1 | 533/591 | **90.2%** | **CÓ** |
| h1_off2_sma50 | H1 | 526/591 | 89.0% | CÓ |
| h1_off3_sma20 | H1 | 468/591 | 79.2% | CÓ |
| d1_prior_bull (nến D1 trước xanh) | D1 | 423/664 | **63.7%** | **CÓ** |
| d1_close_gt_prior | D1 | 419/664 | 63.1% | CÓ |
| d1_close_gt_sma20 | D1 | 390/664 | 58.7% | KHÔNG |

**Luật chấp nhận (chính):** vào **18:30 server (GMT+3)**, hướng = **sign(close − SMA50)** H1 bar vừa đóng; SL ban đầu 100, TP 165 (TP ít khi chạm; SL thường trail).

### 1.2 MCA100 2153920 (chủ yếu XAUUSD)

| Mục | ĐO |
|---|---|
| n XAU / tổng | 428 / 433 (EURUSD 3, GBPUSD 2) |
| Khoảng | 2023-11-15 → 2026-11-05 |
| buy% XAU | **88.3** |
| SL med / TP med | **6.85** / **8.54** |
| hold med | 0.43 giờ |
| Pending thô | Buy Stop 274 · Sell Stop 104 · Buy Limit 17 (hầu hết cancelled) |

**Match hướng / cấu trúc (XAU H1 HistData):**

| Luật | ok/tot | match | ≥60% | Ghi chú |
|---|---|---|---|---|
| h1_close_gt_sma50 | 422/428 | **98.6%** | CÓ | ≈ always_buy trong bull XAU |
| h1_close_gt_sma20 | 420/428 | 98.1% | CÓ | cùng kiểu |
| always_buy_baseline | 378/428 | **88.3%** | (baseline) | không phải luật 2 chiều |
| regen D1 breakout off=5 **dir_only** | 388/426 | 91.1% | CÓ* | *hướng thôi, không khớp giờ |
| regen D1 breakout off=5 **dir+time±2h** | 238/428 | **55.6%** | **KHÔNG** | |
| regen off=0 dir+time±2h | 210/428 | 49.1% | KHÔNG | |
| entry ≈ prior D1 extreme ±10 | 256/428 | 59.8% | KHÔNG (sát ngưỡng) | |
| entry ≈ prior H1 extreme ±5 | 210/428 | 49.1% | KHÔNG | |

**Kết luận luật MCA:** filter hướng H1 SMA đạt ≥60% nhưng **không tách biệt baseline buy 88%** (vàng uptrend 2023–2026). Luật pending tái tạo (BuyStop/SellStop từ cực trị D1) **không đạt ≥60% khi yêu cầu cùng giờ ±2h**. Offset pending vs prior H1 high med **+33.6** (không dính sát H1); vs prior D1 high med **+5.3** (31% trong ±0.5).

→ Chấp nhận có điều kiện: **hướng theo trend H1**; **không chấp nhận** luật đặt pending đầy đủ (thiếu khớp thời điểm). V1 vẫn chạy thử breakout D1 off=5 (dir_only ≥60%) để có số OOS.

---

## 2. V1 walk-forward (OOS)

Cấu hình chung: WF **12 tháng train / 3 tháng test**; SL/TP mult ∈ {0.75,1,1.25(,1.5)} chọn **chỉ trên train**; hold_cap **30 ngày**; risk **1%** equity/lệnh; phí = spread p90 + swap XM (US100 từ `chi_phi_do`+spread_bar FXCE — nhãn chưa đồng bộ XM; XAU từ `phi_xm_micro`); bootstrap 500; so random-entry.

### 2.1 Kivenara H1 (luật h1_sma50 @18:30 GMT+3) — proxy NQ=F H1 ~2024-06→2026-11

| Chỉ tiêu | ĐO |
|---|---|
| n OOS | 486 |
| years | 2.10 |
| trades/yr | 231.5 |
| **CAGR** | **−9.33%** |
| **DD** | **29.82%** |
| Sharpe (xấp xỉ theo lệnh) | −0.49 |
| equity cuối (V0=10k) | 8141 |
| boot CAGR p50 / p05 | −10.44% / −38.27% |
| random-entry CAGR p50 / p95 | −7.49% / +17.33% |
| beat random? | **Không** |
| **Verdict** | **REJECT** (CAGR≤10%) |

### 2.2 Kivenara D1 (luật d1_prior_bull) — NQ=F D1 2008→2026

| Chỉ tiêu | ĐO |
|---|---|
| n OOS | 1015 |
| years | 17.51 |
| trades/yr | 58.0 |
| **CAGR** | **−5.54%** |
| **DD** | **73.31%** |
| Sharpe | −0.41 |
| equity cuối | 3684 |
| boot CAGR p50 / p05 | −5.48% / −19.48% |
| random-entry CAGR p50 / p95 | −2.48% / −0.55% |
| beat random? | **Không** |
| **Verdict** | **REJECT** |

### 2.3 MCA100 XAU D1 breakout off=5, SL=6.85, TP=8.54 — H1 2009→2026

| Chỉ tiêu | ĐO |
|---|---|
| n OOS | 1339 |
| years | 16.50 |
| trades/yr | 81.1 |
| **CAGR** | **−7.08%** |
| **DD** | **72.54%** |
| Sharpe | −0.68 |
| equity cuối | 2978 |
| boot CAGR p50 / p05 | −6.93% / −21.59% |
| random-entry CAGR p50 / p95 | −2.83% / −1.03% |
| beat random? | **Không** |
| **Verdict** | **REJECT** |

---

## 3. Friday Pro 2344620 vs buy-and-hold sau swap

Hạng `pyramid` (max cùng chiều=5). buy% **99.7%** → gần long-only có chọn lọc.

| Mã | n | years | buy% | B&H giá ret | B&H CAGR | B&H CAGR sau swap long 1 lot* | net hệ (broker CSV) |
|---|---|---|---|---|---|---|---|
| GBPJPY | 162 | 3.249 | 100 | +17.11% | **4.98%** | **5.76%** | +245.28 |
| USDJPY | 158 | 3.218 | 100 | +10.14% | **3.05%** | **3.75%** | +414.50 |

\*Swap liên tục theo `chi_phi_do` XM MICRO (GBPJPY swap_mua=+3.09 POINTS → long **được** swap, nên CAGR sau swap &gt; CAGR giá). B&H ĐO từ giá open lệnh đầu → close lệnh cuối trong CSV (không phải series OHLC độc lập).

**Đọc nhanh:** hệ gần B&H JPY-cross; B&H sau swap CAGR ~3.8–5.8%/năm — **dưới** ngưỡng V1 CAGR&gt;10%. Không chạy WF đầy đủ (không có luật vào 2 chiều tách B&H).

---

## 4. Verdict tổng

| ID | Tên | Lưới (mới) | Luật match≥60% | V1 OOS | Verdict |
|---|---|---|---|---|---|
| 2229059 | Kivenara | don_le | **CÓ** — H1 SMA50 @18:30 (90.2%); D1 prior_bull (63.7%) | H1 CAGR −9.3% DD 29.8%; D1 CAGR −5.5% DD 73.3% | **REJECT V1** |
| 2153920 | MCA100 | pyramid | Hướng H1 SMA CÓ nhưng ≈ buy-baseline 88%; pending+giờ **KHÔNG** (≥55.6%) | Breakout thử CAGR −7.1% DD 72.5% | **REJECT V1** / luật vào đầy đủ chưa đạt |
| 2344620 | Friday Pro | pyramid | ~B&H (buy 99.7%) | B&H sau swap CAGR 3.8–5.8% | **Không đạt** ngưỡng CAGR&gt;10% |

**Không commit.** File cập nhật: `MQL5_83_LOC_PHI.md` §0b, `grid_recount.json`, `V1_KIVENARA_MCA100.md`, `v1_dich_nguoc_ket_qua.json`.
