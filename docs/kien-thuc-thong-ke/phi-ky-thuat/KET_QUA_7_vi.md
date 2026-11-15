# KẾT QUẢ VÒNG 7 – 4 hướng có cơ sở nghiên cứu (vàng & S&P 500)

*Chạy ngày 14/11/2026 (giờ VN, UTC+7). Dữ liệu Yahoo tới phiên 13/11/2026. Mọi con số dưới đây lấy từ `results7/`, không có số ước đoán.*

## 0. Kết luận ngắn

| Hạng | Hướng | Kết quả |
|---|---|---|
| **1** | **Hồi về trung bình ngắn hạn trên S&P (IBS, RSI2/RSI3 + SMA200, đáy 10 phiên)** | Đây là hướng **duy nhất** dương ở cả 2 nửa và có ý nghĩa thống kê ở **cả 2 nửa** (p ngẫu nhiên IS ≤ 0.01, OOS ≈ 0.01–0.04). 10/64 phép thử qua FDR khi gộp 2 nửa. Trên **vàng thì không có tác dụng**. |
| 2 | Trend / momentum | 81/102 cấu hình dương cả 2 nửa, nhưng **không thắng ngẫu nhiên cùng phơi nhiễm** (p OOS ≥ 0.06) và **không thắng B&H** về Sharpe OOS. Giá trị thật của nó là **giảm MaxDD** (ví dụ ES C>SMA200: OOS DD 18.7% so với B&H 34.5%), chứ không phải tạo alpha. |
| 3 | Hiệu ứng lịch / thời gian | Overnight của S&P có thật (gộp phí, OOS Sharpe 0.72–0.82) nhưng **ở nửa IS bị phí ăn hết** (SPY: Sharpe trước phí 0.54, sau phí 0.03). Turn-of-month và pre-holiday dương nhưng không có ý nghĩa thống kê. Hiệu ứng theo giờ/phiên của vàng **đổi dấu giữa 2 nửa** nên là nhiễu. |
| 4 | Biến động & tin tức | Drift ngày FOMC **rất mạnh ở IS (p 0.001–0.002) nhưng biến mất ở OOS** (Sharpe ≈ 0.03–0.07): hiệu ứng đã bị khai thác hết. NR7 và inside bar: không. Theo hoặc ngược chiều sau CPI/NFP: nhiễu. Lọc VIX>20 làm mean-reversion "đậm" hơn nhưng ít lệnh. |

**Ứng viên tốt nhất: IBS < 0.2 trên ES (S&P futures), chỉ Long, giữ 1 phiên.** Dương ở cả 2 nửa sau phí, thắng B&H và trend baseline về Sharpe ở cả 2 nửa, và qua FDR p gộp (q = 0.038).
**Nhưng nó KHÔNG qua FDR nếu chỉ tính riêng OOS trên toàn bộ 306 phép thử** (q = 0.53). Trung thực mà nói, đây là edge **yếu–vừa**, có cơ sở học thuật, đã lặp lại được ở ES, ^GSPC và SPY, nhưng không phải "chén thánh".

## 1. Phương pháp (giống vòng 1–6)
- **Dữ liệu:**
  - GC=F daily từ 2008 (trước đó dữ liệu hỏng).
  - ES=F và ^GSPC daily từ 2000.
  - Thêm SPY từ 2000 để kiểm tra chéo: SPY có giá mở cửa thật và đã điều chỉnh cổ tức.
  - ^VIX tải từ Yahoo.
  - 1h: GC=F và ES=F từ 06/2024 tới 11/2026.
- **Ngày tin tức:**
  - FOMC: 159 cuộc họp định kỳ 2007–2026, lấy từ trang lịch của Fed.
  - CPI (321 lần) và NFP (323 lần) 2000–2026: ngày phát hành thật, lấy từ trang lưu trữ của BLS (qua Wayback vì BLS chặn bot).
  - Danh sách lưu ở `events/`.
- **Khớp lệnh:**
  - Tín hiệu lấy ở close của nến t, khớp ở **OPEN thật của nến t+1**.
  - Riêng bản "close" khớp ngay tại close nến tín hiệu (kiểu MOC như bài gốc của Connors). Bản này lạc quan hơn và được ghi rõ.
  - Overnight là close→open, intraday là open→close.
- **Phí:**
  - Mỗi lượt mua+bán trả 1 spread: vàng 0.3, ES 0.25, ^GSPC 0.5, SPY 0.02.
  - Có kiểm tra thêm với phí ×4.
- **Chia mẫu:** IS là trước 2016, OOS từ 2016 trở đi. Dữ liệu 1h chia đôi theo thời gian. Riêng ^GSPC overnight dùng từ 2014 và chia đôi.
- **Đối chứng:**
  - Buy & Hold.
  - Donchian20 và EMA20/100 long-only.
  - **Ngẫu nhiên cùng phơi nhiễm:** dịch vòng chuỗi vị thế 5000 lần trong từng nửa. Cách này giữ nguyên số lệnh, thời gian giữ lệnh và % thời gian có vị thế, chỉ phá timing.
  - Các test lịch, theo giờ và NR7 dùng t-test Welch.
- **So nhiều phép thử:** dùng Benjamini–Hochberg trên **toàn bộ 306 phép thử**, theo 2 cách:
  - (a) chỉ dùng p của OOS (rất khắt khe);
  - (b) p gộp 2 nửa theo Fisher. Với cách này, chiến lược phải **đồng thời** có p<0.05 ở từng nửa và q<0.10.
- **Lưới tham số:** khai báo trước, không tối ưu trên OOS.

## 2. Bảng theo hướng (top 12 mỗi hướng, xếp theo Sharpe thấp hơn trong 2 nửa)
Ký hiệu:
- ✅: qua FDR gộp và thắng B&H ở cả 2 nửa.
- 🟡: qua FDR gộp nhưng không thắng B&H về Sharpe ở cả 2 nửa.
- ❌: không đạt.

Cột "q OOS" là FDR chỉ dùng OOS, "q gộp" là FDR theo Fisher. Bảng đầy đủ 306 dòng nằm ở `results7/all_tests_fdr.csv`.

### 1_trend

| Mã | Chiến lược | Tham số/khớp | Sharpe IS | Sharpe OOS | p IS | p OOS | q OOS | q gộp | PF OOS | Lệnh OOS | MaxDD OOS % | B&H OOS | Trend BL OOS | Đạt? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ^GSPC 1d | SMA50/200 | L/open | 0.61 | 0.67 | 0.036 | 0.826 | 0.96 | 0.459 | 8.19 | 6 | 32.2 | 0.86 | 0.86 | ❌ |
| ES=F 1d | SMA50/200 | L/open | 0.57 | 0.58 | 0.045 | 0.873 | 0.98 | 0.523 | 9.88 | 6 | 34.5 | 0.76 | 0.77 | ❌ |
| ES=F 1d | TSMOM126 | L/open | 0.56 | 0.62 | 0.039 | 0.702 | 0.92 | 0.457 | 3.07 | 42 | 19.5 | 0.76 | 0.77 | ❌ |
| ^GSPC 1d | SMA50/200+VT15 | LS/open | 0.53 | 0.49 | 0.050 | 0.740 | 0.94 | 0.510 | 3.14 | 11 | 28.7 | 0.86 | 0.86 | ❌ |
| GC=F 1d | TSMOM252+VT15 | L/open | 0.49 | 0.54 | 0.175 | 0.717 | 0.93 | 0.674 | 2.97 | 36 | 35.2 | 0.79 | 0.73 | ❌ |
| ^GSPC 1d | SMA50/200+VT15 | L/open | 0.49 | 0.75 | 0.067 | 0.435 | 0.84 | 0.459 | 25.88 | 6 | 20.8 | 0.86 | 0.86 | ❌ |
| ^GSPC 1d | TSMOM126 | L/open | 0.47 | 0.76 | 0.043 | 0.525 | 0.88 | 0.417 | 3.88 | 41 | 19.3 | 0.86 | 0.86 | ❌ |
| ^GSPC 1d | TSMOM252 | L/open | 0.45 | 0.74 | 0.079 | 0.617 | 0.88 | 0.531 | 5.08 | 17 | 25.3 | 0.86 | 0.86 | ❌ |
| GC=F 1d | Donchian100+VT15 | L/open | 0.45 | 0.69 | 0.158 | 0.282 | 0.73 | 0.531 | 5.47 | 11 | 25.7 | 0.79 | 0.73 | ❌ |
| ES=F 1d | SMA50/200+VT15 | L/open | 0.45 | 0.68 | 0.142 | 0.415 | 0.84 | 0.565 | 18.97 | 6 | 22.1 | 0.76 | 0.77 | ❌ |
| ES=F 1d | TSMOM252 | L/open | 0.44 | 0.66 | 0.127 | 0.580 | 0.88 | 0.586 | 5.51 | 19 | 23.4 | 0.76 | 0.77 | ❌ |
| ES=F 1d | C>SMA200 | L/open | 0.44 | 0.77 | 0.105 | 0.192 | 0.68 | 0.388 | 3.86 | 31 | 18.7 | 0.76 | 0.77 | ❌ |

### 2_meanrev

| Mã | Chiến lược | Tham số/khớp | Sharpe IS | Sharpe OOS | p IS | p OOS | q OOS | q gộp | PF OOS | Lệnh OOS | MaxDD OOS % | B&H OOS | Trend BL OOS | Đạt? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SPY 1d | RSI3<20&>SMA200 | L/close | 0.82 | 0.81 | 0.003 | 0.036 | 0.53 | 0.039 | 2.82 | 93 | 11.3 | 0.90 | 0.93 | 🟡 |
| SPY 1d | Low10&>SMA200 | L/close | 0.80 | 0.77 | 0.005 | 0.061 | 0.53 | 0.046 | 2.17 | 116 | 10.0 | 0.90 | 0.93 | ❌ |
| ^GSPC 1d | Low10&>SMA200 | L/open | 0.81 | 0.74 | 0.005 | 0.066 | 0.53 | 0.046 | 2.04 | 115 | 13.1 | 0.86 | 0.86 | ❌ |
| ^GSPC 1d | IBS<0.2_1d | L/close | 0.70 | 0.71 | 0.000 | 0.058 | 0.53 | 0.011 | 1.46 | 418 | 12.7 | 0.86 | 0.86 | ❌ |
| ES=F 1d | Low10&>SMA200 | L/open | 0.82 | 0.70 | 0.004 | 0.076 | 0.53 | 0.046 | 2.04 | 111 | 11.0 | 0.76 | 0.77 | ❌ |
| SPY 1d | IBS<0.1_1d | L/open | 0.68 | 0.70 | 0.004 | 0.073 | 0.53 | 0.046 | 1.74 | 229 | 12.0 | 0.90 | 0.93 | ❌ |
| SPY 1d | IBS<0.2_1d | L/close | 0.74 | 0.68 | 0.001 | 0.116 | 0.59 | 0.038 | 1.45 | 389 | 15.9 | 0.90 | 0.93 | ❌ |
| ^GSPC 1d | IBS<0.2_1d | L/open | 0.68 | 0.85 | 0.000 | 0.020 | 0.53 | 0.011 | 1.57 | 418 | 9.6 | 0.86 | 0.86 | 🟡 |
| ES=F 1d | Low10&>SMA200 | L/close | 0.79 | 0.67 | 0.003 | 0.094 | 0.54 | 0.046 | 1.99 | 111 | 9.3 | 0.76 | 0.77 | ❌ |
| SPY 1d | IBS<0.1_1d | L/close | 0.73 | 0.66 | 0.003 | 0.078 | 0.53 | 0.046 | 1.61 | 229 | 13.2 | 0.90 | 0.93 | ❌ |
| ES=F 1d | IBS<0.1_1d | L/open | 0.66 | 0.72 | 0.005 | 0.034 | 0.53 | 0.046 | 1.86 | 165 | 12.7 | 0.76 | 0.77 | 🟡 |
| ^GSPC 1d | RSI3<20&>SMA200 | L/open | 0.68 | 0.65 | 0.006 | 0.120 | 0.60 | 0.074 | 2.30 | 91 | 12.0 | 0.86 | 0.86 | ❌ |

### 3_calendar

| Mã | Chiến lược | Tham số/khớp | Sharpe IS | Sharpe OOS | p IS | p OOS | q OOS | q gộp | PF OOS | Lệnh OOS | MaxDD OOS % | B&H OOS | Trend BL OOS | Đạt? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ES=F 1h | Overnight(16h->09h) | 2024-06+/open/close bar | 0.95 | 1.77 | 0.154 | 0.028 | 0.53 | 0.174 | 1.36 | 298 | 7.6 | 0.95 |  | ❌ |
| ES=F 1h | Session_Asia(18-03h) | long mỗi ngày/open/close bar | 0.66 | 0.81 | 0.235 | 0.188 | 0.68 | 0.531 | 1.15 | 305 | 3.2 | 0.95 |  | ❌ |
| GC=F 1d | DOW_Fri | giữ close->close/close | 0.75 | 0.55 | 0.131 | 0.476 | 0.85 | 0.577 | 1.11 | 528 | 16.6 | 0.79 | 0.73 | ❌ |
| ES=F 1d | DOW_Tue | giữ close->close/close | 0.53 | 0.88 | 0.128 | 0.409 | 0.84 | 0.556 | 1.18 | 563 | 9.3 | 0.76 | 0.77 | ❌ |
| SPY 1d | DOW_Tue | giữ close->close/close | 0.51 | 0.92 | 0.159 | 0.446 | 0.84 | 0.586 | 1.19 | 563 | 9.3 | 0.90 | 0.93 | ❌ |
| ES=F 1h | Session_London(03-08h) | long mỗi ngày/open/close bar | 0.41 | 1.47 | 0.329 | 0.055 | 0.53 | 0.370 | 1.32 | 299 | 2.4 | 0.95 |  | ❌ |
| SPY 1d | TurnOfMonth(-1..+3) | L/close | 0.33 | 0.46 | 0.133 | 0.364 | 0.82 | 0.531 | 1.49 | 131 | 9.9 | 0.90 | 0.93 | ❌ |
| GC=F 1d | DOW_Mon | giữ close->close/close | 0.35 | 0.33 | 0.291 | 0.622 | 0.88 | 0.708 | 1.06 | 496 | 20.2 | 0.79 | 0.73 | ❌ |
| SPY 1d | TurnOfMonth(-1..+3) | L/open | 0.27 | 0.53 | 0.232 | 0.304 | 0.76 | 0.586 | 1.60 | 131 | 11.4 | 0.90 | 0.93 | ❌ |
| ES=F 1d | TurnOfMonth(-1..+3) | L/open | 0.27 | 0.35 | 0.148 | 0.471 | 0.85 | 0.586 | 1.35 | 131 | 11.2 | 0.76 | 0.77 | ❌ |
| ES=F 1d | TurnOfMonth(-1..+3) | L/close | 0.26 | 0.32 | 0.170 | 0.533 | 0.88 | 0.599 | 1.33 | 131 | 10.6 | 0.76 | 0.77 | ❌ |
| ^GSPC 1d | TurnOfMonth(-1..+3) | L/close | 0.24 | 0.41 | 0.158 | 0.356 | 0.81 | 0.557 | 1.44 | 131 | 9.9 | 0.86 | 0.86 | ❌ |

### 4_volnews

| Mã | Chiến lược | Tham số/khớp | Sharpe IS | Sharpe OOS | p IS | p OOS | q OOS | q gộp | PF OOS | Lệnh OOS | MaxDD OOS % | B&H OOS | Trend BL OOS | Đạt? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ^GSPC 1d | NR7_breakout_1D | L/stop/open->close | 0.84 | 0.65 | 0.297 | 0.283 | 0.73 | 0.587 | 1.47 | 284 | 6.8 | 0.86 | 0.86 | ❌ |
| ^GSPC 1d | NR7_breakout_1D | LS/stop/open->close | 1.23 | 0.64 | 0.015 | 0.248 | 0.73 | 0.174 | 1.35 | 437 | 6.8 | 0.86 | 0.86 | ❌ |
| ^GSPC 1d | IBS<0.2|VIX>20 | L/open | 0.63 | 0.76 | 0.002 | 0.035 | 0.53 | 0.038 | 1.75 | 186 | 9.2 | 0.86 | 0.86 | 🟡 |
| GC=F 1d | NR7_breakout_3D | L/stop/open->close | 0.59 | 0.56 | 0.116 | 0.389 | 0.84 | 0.531 | 1.36 | 268 | 19.6 | 0.79 | 0.73 | ❌ |
| SPY 1d | RSI2<10&>SMA200|VIX>20 | L/open | 0.54 | 0.72 | 0.017 | 0.048 | 0.53 | 0.074 | 4.09 | 48 | 10.9 | 0.90 | 0.93 | 🟡 |
| ES=F 1d | IBS<0.2|VIX>20 | L/open | 0.54 | 0.72 | 0.019 | 0.037 | 0.53 | 0.071 | 1.76 | 176 | 17.5 | 0.76 | 0.77 | 🟡 |
| GC=F 1d | InsideBar_breakout_1D | L/stop/open->close | 0.58 | 0.52 | 0.155 | 0.125 | 0.62 | 0.386 | 1.39 | 217 | 6.4 | 0.79 | 0.73 | ❌ |
| SPY 1d | IBS<0.2|VIX>20 | L/open | 0.72 | 0.46 | 0.004 | 0.216 | 0.71 | 0.082 | 1.45 | 176 | 20.1 | 0.90 | 0.93 | ❌ |
| ^GSPC 1d | NR7_breakout_3D | L/stop/open->close | 0.51 | 0.46 | 0.202 | 0.496 | 0.87 | 0.617 | 1.31 | 284 | 20.2 | 0.86 | 0.86 | ❌ |
| GC=F 1d | InsideBar_breakout_3D | L/stop/open->close | 0.44 | 0.98 | 0.194 | 0.042 | 0.53 | 0.253 | 1.79 | 217 | 10.8 | 0.79 | 0.73 | ❌ |
| ES=F 1d | RSI2<10&>SMA200|VIX>20 | L/open | 0.41 | 0.82 | 0.061 | 0.016 | 0.53 | 0.082 | 4.61 | 46 | 10.0 | 0.76 | 0.77 | ❌ |
| ES=F 1d | RSI2<10&>SMA200|VIX<=20 | L/open | 0.39 | 0.42 | 0.099 | 0.252 | 0.73 | 0.442 | 2.14 | 64 | 10.5 | 0.76 | 0.77 | ❌ |

Thống kê theo hướng:

| Hướng | Số phép thử | Dương cả 2 nửa | Qua FDR chỉ OOS | Qua FDR gộp (p<0.05 mỗi nửa) | Thắng B&H cả 2 nửa | Sharpe IS trung vị | Sharpe OOS trung vị |
|---|---|---|---|---|---|---|---|
| 1 Trend | 102 | 81 | 0 | 0 | 5 | 0.24 | 0.54 |
| 2 Mean-reversion | 64 | 63 | 0 | **10** | 3 | 0.55 | 0.64 |
| 3 Lịch / thời gian | 50 | 23 | 0 | 0 | 3 | 0.17 | 0.54 |
| 4 Biến động & tin | 90 | 34 | 0 | 3 (đều là MR S&P lọc VIX>20) | 2 | 0.01 | 0.08 |

Baseline daily (Sharpe IS / OOS):
- ES B&H: 0.21 / 0.76, MaxDD OOS 34.5%.
- ^GSPC B&H: 0.21 / 0.86.
- SPY B&H: 0.30 / 0.90.
- Vàng B&H: 0.24 / 0.79.
- ES Donchian20: 0.17 / 0.68. ES EMA20/100: 0.31 / 0.77.

Chi tiết ở `results7/baselines_daily.csv`.

## 3. Chi tiết từng hướng

### Hướng 1 – Trend / momentum
- TSMOM, Donchian và SMA cross có Sharpe OOS 0.4–0.8, **xấp xỉ hoặc thấp hơn B&H**. Không cấu hình nào có p ngẫu nhiên OOS < 0.05. Cấu hình tốt nhất là TSMOM63+VT trên vàng (p = 0.06 OOS), nhưng p IS là 0.16.
- Bản Long/Short **tệ hơn rõ** trên S&P, vì bán khống một chỉ số có xu hướng tăng dài hạn.
- Vol-target 15% giúp Sharpe nhích lên một chút và giảm DD ở vàng, nhưng không tạo ra ý nghĩa thống kê.
- **Kết luận:** dùng trend như **bộ lọc rủi ro** (đứng ngoài khi C<SMA200) để cắt DD từ khoảng 34% xuống khoảng 19%. Đừng kỳ vọng nó đánh bại B&H.

### Hướng 2 – Mean-reversion (hạng 1)
- **Trên S&P:** cả 8 quy tắc đều dương ở cả 2 nửa, PF OOS 1.4–3.3, tỉ lệ thắng 60–80%, thời gian có vị thế chỉ 6–20%.
- **Trên vàng:**
  - Không quy tắc nào có ý nghĩa ở cả 2 nửa.
  - IBS khớp close cho OOS Sharpe 1.08, nhưng IS chỉ 0.23. Khi khớp open thật, OOS còn 0.20. Đây là do lệch giờ chốt giá của GC=F, không giao dịch được.
- **Phát hiện quan trọng:** trên SPY, khi khớp ở **open 9:30 hôm sau**, IBS yếu đi rõ (OOS 0.59, p = 0.21). Khi khớp ở close (MOC) thì IS 0.74 / OOS 0.68 (p OOS 0.12). Phần lớn edge nằm trong **đêm ngay sau ngày đóng cửa yếu**. Vì vậy phải vào lệnh ở close, hoặc ở giá mở lại phiên Globex của ES (~18:00 ET).

### Hướng 3 – Lịch / thời gian
- **Overnight vs intraday:**
  - SPY trước phí: overnight Sharpe IS 0.54 / OOS 0.86, intraday -0.01 / 0.40.
  - Sau phí 1 spread mỗi ngày: overnight IS 0.03 / OOS 0.72 (p OOS 0.009, p IS 0.45).
  - ES 1h (16h→09h): 0.95 / 1.77, nhưng chỉ có 2.4 năm dữ liệu.
  - Hiệu ứng có thật nhưng **phí và vòng quay hằng ngày** làm nó mong manh. Nó cũng không đạt ở nửa IS.
- **Turn-of-month (-1..+3):** S&P OOS 0.32–0.53, IS 0.24–0.33, p 0.14–0.52, không có ý nghĩa thống kê. Vàng OOS 0.87 nhưng IS 0.00.
- **Day-of-week:** không ổn định. Ví dụ thứ Hai: IS âm, OOS dương. Thứ Năm: OOS âm.
- **Pre-holiday:** dương ở cả 2 nửa nhưng p 0.07–0.29, chỉ khoảng 9 lệnh mỗi năm.
- **Vàng theo giờ/phiên (1h):**
  - Phiên London: IS Sharpe 2.29 → OOS -0.23.
  - Phiên Á: -0.06 → 1.46.
  - "Giờ tốt nhất IS": 1.62 → -0.61.
  - Kết luận là **đổi dấu, thuần nhiễu**. Chỉ có giờ 16h ET ở IS qua FDR (q = 0.015), sang OOS thì âm.

### Hướng 4 – Biến động & tin tức
- **FOMC (long ngày họp, close→close):** IS Sharpe 0.67–0.73 (p 0.001–0.002), OOS 0.03–0.07. Đây là ví dụ kinh điển về **suy giảm sau khi được công bố** (bài pre-FOMC drift của Lucca–Moench).
- **CPI / NFP:** cả theo chiều, giữ 1 hoặc 3 phiên, lẫn ngược chiều đều không ổn định giữa 2 nửa.
- **NR7 / Inside bar breakout:**
  - ES âm ở IS, Long/Short âm ở cả 2 nửa.
  - Vàng inside-bar Long 3D có OOS 0.98, nhưng IS 0.44 (p 0.19).
  - ^GSPC đẹp ở IS nhưng ES (giao dịch được) thì không, nên nhiều khả năng do dữ liệu ^GSPC cũ.
  - Lưu ý: Sharpe của NR7 tính theo lệnh, chỉ để tham khảo.
- **VIX:**
  - IBS<0.2 khi VIX>20: ES 0.54 / 0.72, ^GSPC 0.63 / 0.76.
  - RSI2 khi VIX>20: PF OOS 4.1–4.6.
  - Khi VIX ≤ 20, edge yếu hẳn. Tức là mean-reversion **phụ thuộc chế độ biến động cao**.
  - VIX spike mua 5 phiên: không có ý nghĩa thống kê.

## 4. Ứng viên tốt nhất – IBS<0.2 trên ES, Long, giữ 1 phiên
Quy tắc: IBS = (C−L)/(H−L) của nến ngày. Nếu IBS < 0.2 thì mua ở OPEN phiên kế tiếp (trên ES daily là giá mở lại Globex ~18:00 ET). Giữ 1 phiên. Nếu hôm sau IBS vẫn < 0.2 thì giữ tiếp.

| | IS 2000–2015 | OOS 2016–11/2026 |
|---|---|---|
| Sharpe (sau phí) | **0.60** (B&H 0.21; Donchian20 0.17; EMA 0.31) | **0.88** (B&H 0.76; trend BL 0.77) |
| CAGR | 5.8% (B&H 2.2%) | 8.0% (B&H 12.9%) |
| MaxDD | 24.6% (B&H 57.2%) | 17.9% (B&H 34.5%) |
| PF / số lệnh | 1.40 / 609 | 1.70 / 361 |
| % thời gian có vị thế | 19.6% | 16.1% |
| p ngẫu nhiên cùng phơi nhiễm | 0.005 | 0.015 |
| FDR | q gộp = 0.038 ✅ | q chỉ OOS = 0.53 ❌ |
| Phí ×4 | Sharpe 0.36 | Sharpe 0.81 |

**Kiểm tra chéo:**
- ^GSPC: 0.68 / 0.85 (p 0.0002 / 0.02).
- SPY khớp close: 0.74 / 0.68.
- SPY khớp open 9:30: 0.68 / 0.59, OOS không có ý nghĩa thống kê.
- IBS<0.1 trên ES khớp close: 0.63 / 0.79.
- 81% số năm có lãi (22/27 năm).
- Loại bỏ các ngày trong cửa sổ roll của ES: Sharpe toàn kỳ 0.68 (so với 0.71). Không phải do lỗi roll.

**Lưu ý trung thực:**
1. **Suy giảm và phụ thuộc chế độ.** Sharpe theo giai đoạn: 2000–04: 0.18 | 2005–09: 0.83 | 2010–14: 1.08 | **2015–19: 0.30** | 2020–26: 0.98. Edge chủ yếu đến từ các giai đoạn biến động cao (VIX>20). Trong thị trường êm, tăng đều, nó gần như bằng 0.
2. **Không qua FDR nếu chỉ dùng OOS.** Chỉ qua khi gộp 2 nửa. Có thể vẫn là may mắn, dù đã lặp lại trên 3 nguồn dữ liệu S&P.
3. **Không thay thế được B&H về lợi nhuận tuyệt đối.** Chỉ có vị thế khoảng 16–20% thời gian, CAGR thấp hơn B&H, nhưng DD bằng khoảng một nửa. Phù hợp làm lớp bổ sung, hoặc dùng đòn bẩy vừa phải.
4. **Phải vào lệnh ở close hoặc ngay sau close.** Vào ở open 9:30 hôm sau thì mất phần lớn edge. Với CFD US500, giờ chốt nến daily của broker phải khớp với giờ đóng cửa của Mỹ.
5. **Sức chứa (capacity):** với 1–vài hợp đồng ES/MES thì không vấn đề. Đây là hiệu ứng nổi tiếng (Connors, IBS) nên đông người đánh, có thể yếu dần tiếp.
6. **Không áp dụng cho vàng.**

Chiến lược Pine v6: `best_strategy_r7.pine`. Chưa compile-check trên TradingView. Mặc định khớp open nến sau, commission 2.5 USD/hợp đồng, slippage 1 tick. Có 2 bộ lọc tùy chọn tắt sẵn: VIX>20 và SMA200.

## 5. Hạn chế dữ liệu
- **^GSPC từ 2000 đến khoảng 2013:** giá Open trên Yahoo thường **bằng close hôm trước** (2000–05 khoảng 95%, 2012–13 khoảng 25%). Vì vậy:
  - Ở IS, "khớp open" của ^GSPC thực chất là khớp close;
  - Overnight của ^GSPC chỉ test từ 2014;
  - SPY được dùng làm bản sạch.
- **ES=F của Yahoo** là chuỗi hợp đồng gần nhất, không điều chỉnh roll. Đã kiểm tra lại cho ứng viên bằng cách loại cửa sổ roll.
- **Dữ liệu 1h** chỉ có từ 06/2024 đến 11/2026, mỗi nửa khoảng 14 tháng, trùng với giai đoạn vàng tăng mạnh. Kết luận theo giờ vì thế yếu.
- **Ngày tin tức:** CPI tháng 10/2025 không được công bố (chính phủ Mỹ đóng cửa). Kết quả FOMC theo ngày (close→close) không tách được thời điểm 14:00.
- **NR7/inside bar:** khi cả 2 mức stop bị chạm trong cùng phiên thì lấy kết quả xấu hơn (thận trọng). Sharpe tính theo lệnh.

## 6. File
- Scripts: `common7.py`, `test_h_trend.py`, `test_h_meanrev.py`, `test_h_calendar.py`, `test_h_volnews.py`, `make_summary7.py`, `analyze_h_best.py`.
- Kết quả: `results7/`, gồm:
  - `all_tests_fdr.csv`: 306 phép thử, có q OOS và q gộp;
  - `h1_trend.csv`, `h2_meanrev.csv`, `h3_calendar.csv`, `h3_hour_of_day.csv`, `h4_volnews.csv`, `baselines_daily.csv`;
  - `best_candidates_detail.csv`;
  - log chạy `run_*.log`.
- Pine: `best_strategy_r7.pine`.
- Ngày tin: `events/fomc_dates.txt`, `events/cpi_dates.txt`, `events/nfp_dates.txt`.
