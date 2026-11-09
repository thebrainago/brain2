# Myfxbook đợt 1 — Cổng 0 phí XM (+ Cổng S/V1 nếu đủ điều kiện)

Giờ Việt Nam (Asia/Bangkok, UTC+7). **Không commit.** Ngày ĐO: 09/11/2026.

Script: `myfxbook_dot1_loc_phi.py` · JSON `myfxbook_dot1_loc_phi.json` · Cổng S/V1 `myfxbook_dot1_cong_s_v1.json`.

Cổng 0 (cùng logic `loc_phi_nhanh` / MQL5): **REJECT** nếu `net_E_price≤0` hoặc `edge/cost<1.5` hoặc (khi PASS phí) `CAGR_ff≤10%` / `DD_ff≥80%.

Rebuild XM (đơn vị giá): `gross = chiều×(close−open)` · `net = gross − spread_p90_XM + swap_XM(hold)` · `cost = spread + max(−swap,0)` · hoa hồng XM micro ĐO = **0**.

Hạng lưới/pyramid/đơn lệnh: cùng detector MQL5 83 (`detect_grid_martingale` + ngưỡng max_cung / SL%).

---

## 0. Bảng tổng

| ID | Hệ | n | năm | /năm | hang | max | cover% | net_E | e/c | CAGR_ff | DD_ff | Cổng 0 |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 11204017 | NoPain MT5 | 5896 | 5.021 | 1174.17 | luoi | 10 | 100.0 | -0.00077825 | -1.267 | — | — | **REJECT** |
| 8016551 | R Factor Portfolio Mean Reversal | 34720 | 6.766 | 5131.21 | pyramid | 7 | 95.1 | -0.00804408 | 0.4636 | -82.115 | 99.999 | **REJECT** |
| 8365278 | R Factor JM Portfolio | 10218 | 6.53 | 1564.77 | pyramid | 4 | 100.0 | -0.00073259 | 0.6225 | -48.523 | 99.117 | **REJECT** |
| 11576068 | Rainy Strategies Multi-Strategy | 11724 | 1.393 | 8415.58 | luoi | 20 | 59.5 | 1.224 | 1.990 | 280667.4 | 75.309 | **PASS** |
| 11730585 | MidasAlgo | 2573 | 1.819 | 1414.9 | luoi | 7 | 100.0 | 5.344e-05 | 1.110 | 71793.9 | 11.486 | **REJECT** |
| 11583686 | Bitcoin Adi FBS | 1382 | 2.126 | 649.91 | luoi | 34 | 0.0 | — | — | — | — | **CHUA_DO** |

### Verdict nhanh

| ID | Verdict | Lý do chính |
|---|---|---|
| 11204017 | **REJECT** | net_E_price=-0.000778252≤0; edge/cost=-1.267<1.5 |
| 8016551 | **REJECT** | net_E_price=-0.00804408≤0; edge/cost=0.464<1.5 · mã PASS đơn: XAUAUD, XAUEUR |
| 8365278 | **REJECT** | net_E_price=-0.000732594≤0; edge/cost=0.623<1.5 |
| 11576068 | **PASS** | PASS Cổng 0 · mã PASS đơn: AUDCAD, AUDCHF, CHFJPY, XAGUSD, XAUUSD |
| 11730585 | **REJECT** | edge/cost=1.110<1.5 · mã PASS đơn: AUDCAD |
| 11583686 | **CHUA_DO** | phí cover 0/1382; thiếu {'BTCUSD': 1382} |

---

## 11204017 — NoPain MT5

| Mục | Giá trị |
|---|---|
| Export | `/workspace/myfxbook/11204017.csv` |
| Lệnh ĐO | **5896** Buy/Sell |
| Khoảng | 2021-11-01 → 2026-11-09 (**5.021** năm) |
| /năm | **1174.17** |
| buy% | 50.47 |
| hold med | **0.2479 ngày** |
| Hạng | **luoi** (max cùng chiều=10, grid=True, martingale=True, SL%=0.0) |
| fee cover | 100.0% |

### XM rebuild (ALL)

| Chỉ tiêu | ĐO |
|---|---|
| avg pips | **-4.422** |
| XM E[spread] (giá) | 0.00027684 |
| XM E[swap] (giá) | -5.921e-05 |
| XM E[cost] | 0.00034913 |
| XM E[gross] | -0.0004422 |
| **net_E_price** | **-0.00077825** |
| **edge/cost** | **-1.2666** |
| CAGR_ff / DD_ff (ƯỚC risk 1%) | None / **None** |
| **Kết luận** | **REJECT** — net_E_price=-0.000778252≤0; edge/cost=-1.267<1.5 |

Sàn gốc (cột CSV, nếu có): ΣProfit=4013.62 · ΣComm=0.0 · ΣSwap=-288.13 · ΣNet≈3725.49.

### Theo mã (top / PASS / đáng chú ý)

| Symbol | n | avg pips | hold_med_d | net_E | e/c | hang | CAGR_ff | DD_ff | Kết luận |
|---|---:|---:|---:|---:|---:|---|---:|---:|---|
| AUDCAD | 5896 | -4.422 | 0.2479 | -0.00077825 | -1.2666 | luoi | None | None | **REJECT** |

---

## 8016551 — R Factor Portfolio Mean Reversal

| Mục | Giá trị |
|---|---|
| Export | `/workspace/myfxbook/8016551.csv` |
| Lệnh ĐO | **34720** Buy/Sell |
| Khoảng | 2020-02-03 → 2026-11-09 (**6.766** năm) |
| /năm | **5131.21** |
| buy% | 46.06 |
| hold med | **0.0583 ngày** |
| Hạng | **pyramid** (max cùng chiều=7, grid=True, martingale=False, SL%=100.0) |
| fee cover | 95.1% |
| thiếu phí | `{'BTCUSD': 767, 'ETHUSD': 296, 'USDSGD': 455, 'XAUCHF': 81, 'XAUJPY': 89}` |

### XM rebuild (ALL)

| Chỉ tiêu | ĐO |
|---|---|
| avg pips | **23.788** |
| XM E[spread] (giá) | 0.0142066 |
| XM E[swap] (giá) | -0.00100174 |
| XM E[cost] | 0.01545336 |
| XM E[gross] | 0.00716426 |
| **net_E_price** | **-0.00804408** |
| **edge/cost** | **0.4636** |
| CAGR_ff / DD_ff (ƯỚC risk 1%) | -82.115 / **99.999** |
| **Kết luận** | **REJECT** — net_E_price=-0.00804408≤0; edge/cost=0.464<1.5 |

Sàn gốc (cột CSV, nếu có): ΣProfit=16295.76 · ΣComm=-11966.69 · ΣSwap=-4266.27 · ΣNet≈62.8.

### Theo mã (top / PASS / đáng chú ý)

| Symbol | n | avg pips | hold_med_d | net_E | e/c | hang | CAGR_ff | DD_ff | Kết luận |
|---|---:|---:|---:|---:|---:|---|---:|---:|---|
| GBPUSD | 3141 | 1.622 | 0.0424 | -0.00011308 | 0.5892 | pyramid | -2.155 | 64.703 | **REJECT** |
| EURGBP | 2373 | 0.747 | 0.0521 | -0.00018592 | 0.2858 | pyramid | -9.79 | 56.33 | **REJECT** |
| EURUSD | 2191 | 0.523 | 0.0451 | -0.00018491 | 0.2171 | pyramid | 42.008 | 12.884 | **REJECT** |
| EURAUD | 2187 | 2.297 | 0.0556 | -0.00019368 | 0.5387 | pyramid | -18.608 | 75.181 | **REJECT** |
| GBPAUD | 2145 | 1.729 | 0.0507 | -0.00035946 | 0.3248 | pyramid | -22.743 | 77.231 | **REJECT** |
| EURCAD | 1886 | 1.58 | 0.0635 | -0.0002334 | 0.4036 | pyramid | -16.012 | 69.363 | **REJECT** |
| AUDCAD | 1865 | 2.254 | 0.0722 | -8.44e-05 | 0.719 | pyramid | -8.307 | 43.82 | **REJECT** |
| GBPCAD | 1766 | 1.53 | 0.0688 | -0.00045242 | 0.2525 | don_le | -4.439 | 73.113 | **REJECT** |
| USDJPY | 1740 | 0.862 | 0.0316 | -0.01874366 | 0.3128 | pyramid | -42.505 | 97.417 | **REJECT** |
| USDCAD | 1717 | 1.421 | 0.0715 | -0.00019966 | 0.4099 | pyramid | -12.425 | 59.278 | **REJECT** |
| CADJPY | 95 | 8.278 | 0.4007 | 0.02378026 | 1.4031 | don_le | -0.263 | 19.021 | **REJECT** |
| XAUAUD | 94 | 3525.532 | 0.0521 | 0.3383392 | 24.7226 | don_le | 41.436 | 1.356 | **PASS** |
| XAUGBP | 88 | 1325.0 | 0.0771 | 0.11508227 | 7.6072 | don_le | 9.022 | 1.248 | **REJECT** |
| XAUEUR | 68 | 963.235 | 0.074 | 0.06770861 | 2.8518 | don_le | 11.637 | 3.264 | **PASS** |

Mã PASS đơn: **XAUAUD, XAUEUR**.
Soft (net_E>0 ∧ e/c≥1.5, có thể trượt CAGR): XAUAUD, XAUEUR, XAUGBP.

---

## 8365278 — R Factor JM Portfolio

| Mục | Giá trị |
|---|---|
| Export | `/workspace/myfxbook/8365278.csv` |
| Lệnh ĐO | **10218** Buy/Sell |
| Khoảng | 2020-04-28 → 2026-11-09 (**6.53** năm) |
| /năm | **1564.77** |
| buy% | 45.24 |
| hold med | **0.0389 ngày** |
| Hạng | **pyramid** (max cùng chiều=4, grid=True, martingale=False, SL%=100.0) |
| fee cover | 100.0% |

### XM rebuild (ALL)

| Chỉ tiêu | ĐO |
|---|---|
| avg pips | **1.211** |
| XM E[spread] (giá) | 0.00185981 |
| XM E[swap] (giá) | -8.916e-05 |
| XM E[cost] | 0.00195398 |
| XM E[gross] | 0.00121637 |
| **net_E_price** | **-0.00073259** |
| **edge/cost** | **0.6225** |
| CAGR_ff / DD_ff (ƯỚC risk 1%) | -48.523 / **99.117** |
| **Kết luận** | **REJECT** — net_E_price=-0.000732594≤0; edge/cost=0.623<1.5 |

Sàn gốc (cột CSV, nếu có): ΣProfit=0.0 · ΣComm=0.0 · ΣSwap=0.0 · ΣNet≈0.0.

### Theo mã (top / PASS / đáng chú ý)

| Symbol | n | avg pips | hold_med_d | net_E | e/c | hang | CAGR_ff | DD_ff | Kết luận |
|---|---:|---:|---:|---:|---:|---|---:|---:|---|
| GBPUSD | 1860 | 1.335 | 0.0229 | -0.00012965 | 0.5074 | pyramid | 20.94 | 24.139 | **REJECT** |
| EURUSD | 1378 | 1.071 | 0.0285 | -0.0001155 | 0.4793 | pyramid | 22.478 | 5.595 | **REJECT** |
| EURAUD | 790 | 2.261 | 0.0424 | -0.00018238 | 0.5518 | pyramid | -6.639 | 36.535 | **REJECT** |
| EURCAD | 713 | 1.788 | 0.0493 | -0.00019695 | 0.4758 | don_le | -6.996 | 32.602 | **REJECT** |
| USDCAD | 695 | 1.681 | 0.0708 | -0.0001649 | 0.5017 | don_le | -5.012 | 28.61 | **REJECT** |
| EURGBP | 620 | 0.798 | 0.0458 | -0.00017156 | 0.3171 | don_le | -5.051 | 23.463 | **REJECT** |
| USDJPY | 601 | 1.275 | 0.0056 | -0.01392648 | 0.4768 | pyramid | -27.244 | 82.017 | **REJECT** |
| AUDUSD | 555 | 0.603 | 0.0708 | -0.00019757 | 0.2337 | pyramid | -5.969 | 28.9 | **REJECT** |
| AUDCAD | 525 | 0.793 | 0.0465 | -0.00020285 | 0.2807 | don_le | -6.905 | 24.854 | **REJECT** |
| EURSGD | 457 | 0.912 | 0.0437 | -0.00117207 | 0.0722 | don_le | -37.001 | 76.089 | **REJECT** |
| EURJPY | 407 | 0.894 | 0.041 | 0.00770652 | 7.2426 | don_le | 4.395 | 4.822 | **REJECT** |
Soft (net_E>0 ∧ e/c≥1.5, có thể trượt CAGR): EURJPY.

---

## 11576068 — Rainy Strategies Multi-Strategy

| Mục | Giá trị |
|---|---|
| Export | `/workspace/myfxbook/11576068.csv` |
| Lệnh ĐO | **11724** Buy/Sell |
| Khoảng | 2025-06-18 → 2026-11-09 (**1.393** năm) |
| /năm | **8415.58** |
| buy% | 48.0 |
| hold med | **0.0278 ngày** |
| Hạng | **luoi** (max cùng chiều=20, grid=True, martingale=False, SL%=0.0) |
| fee cover | 59.5% |
| thiếu phí | `{'SPOTCR': 86, 'BTCUSD': 4347, 'GER40': 281, 'SPCX.U': 9, 'AMD.US': 1, 'NATGAS': 6, 'COPPER': 3, 'RBLX.U': 2, 'GRAB.U': 10, 'GOOG.U': 1, 'SUGAR': 2}` |

### XM rebuild (ALL)

| Chỉ tiêu | ĐO |
|---|---|
| avg pips | **135.472** |
| XM E[spread] (giá) | 1.0896241 |
| XM E[swap] (giá) | -0.1190077 |
| XM E[cost] | 1.22230997 |
| XM E[gross] | 2.43238226 |
| **net_E_price** | **1.22375046** |
| **edge/cost** | **1.99** |
| CAGR_ff / DD_ff (ƯỚC risk 1%) | 280667.389 / **75.309** |
| **Kết luận** | **PASS** — đạt ngưỡng |

Sàn gốc (cột CSV, nếu có): ΣProfit=339057.03 · ΣComm=-23236.95 · ΣSwap=-9312.27 · ΣNet≈306507.81.

### Theo mã (top / PASS / đáng chú ý)

| Symbol | n | avg pips | hold_med_d | net_E | e/c | hang | CAGR_ff | DD_ff | Kết luận |
|---|---:|---:|---:|---:|---:|---|---:|---:|---|
| XAUUSD | 4938 | 221.0 | 0.0097 | 1.55608274 | 3.2828 | luoi | 41042.622 | 77.818 | **PASS** |
| BTCUSD | 4347 | -36.061 | 0.0444 | None | None | luoi | None | None | **CHUA_DO** |
| US30 | 605 | -3.221 | 0.0174 | -8.86785745 | -0.5704 | luoi | 77.455 | 18.788 | **REJECT** |
| US100 | 461 | 18.16 | 0.0417 | 14.815057 | 5.4296 | luoi | -38.475 | 52.326 | **REJECT** |
| US500 | 313 | -1.237 | 0.0271 | -1.99995918 | -1.6204 | luoi | -63.657 | 67.554 | **REJECT** |
| GER40 | 281 | 2.798 | 0.0194 | None | None | luoi | None | None | **CHUA_DO** |
| GBPAUD | 174 | 4.415 | 0.0816 | -9.621e-05 | 0.8211 | don_le | 201.54 | 1.01 | **REJECT** |
| AUDCAD | 149 | 10.249 | 0.1458 | 0.00055851 | 2.1498 | luoi | 22.923 | 8.712 | **PASS** |
| EURAUD | 144 | 5.226 | 0.0833 | 0.0001036 | 1.2392 | don_le | 106.786 | 3.95 | **REJECT** |
| SPOTCR | 86 | 382.209 | 0.4753 | None | None | luoi | None | None | **CHUA_DO** |
| CHFJPY | 26 | 24.681 | 4.6222 | 0.08434451 | 1.5192 | luoi | 17.943 | 2.0 | **PASS** |
| AUDCHF | 25 | 22.368 | 4.0028 | 0.00142476 | 2.7546 | don_le | 16.7 | 1.99 | **PASS** |
| GBPUSD | 21 | 26.614 | 7.0417 | 0.00206135 | 4.4351 | luoi | 6.249 | 1.02 | **REJECT** |
| EURUSD | 19 | 17.984 | 6.1299 | 0.00168035 | 8.1287 | luoi | 0.784 | 3.969 | **REJECT** |
| XAGUSD | 16 | 7232.5 | 0.0146 | 0.7308217 | 869.7091 | luoi | 314.095 | 1.0 | **PASS** |

Mã PASS đơn: **AUDCAD, AUDCHF, CHFJPY, XAGUSD, XAUUSD**.
Soft (net_E>0 ∧ e/c≥1.5, có thể trượt CAGR): AUDCAD, AUDCHF, CHFJPY, EURUSD, GBPUSD, US100, XAGUSD, XAUUSD.

---

## 11730585 — MidasAlgo

| Mục | Giá trị |
|---|---|
| Export | `/workspace/myfxbook/11730585.csv` |
| Lệnh ĐO | **2573** Buy/Sell |
| Khoảng | 2025-01-14 → 2026-11-09 (**1.819** năm) |
| /năm | **1414.9** |
| buy% | 44.97 |
| hold med | **0.3979 ngày** |
| Hạng | **luoi** (max cùng chiều=7, grid=True, martingale=False, SL%=0.0) |
| fee cover | 100.0% |

### XM rebuild (ALL)

| Chỉ tiêu | ĐO |
|---|---|
| avg pips | **4.293** |
| XM E[spread] (giá) | 0.00026572 |
| XM E[swap] (giá) | -0.00011016 |
| XM E[cost] | 0.00038686 |
| XM E[gross] | 0.00042932 |
| **net_E_price** | **5.344e-05** |
| **edge/cost** | **1.1097** |
| CAGR_ff / DD_ff (ƯỚC risk 1%) | 71793.929 / **11.486** |
| **Kết luận** | **REJECT** — edge/cost=1.110<1.5 |

Sàn gốc (cột CSV, nếu có): ΣProfit=7233.12 · ΣComm=-792.0 · ΣSwap=-1113.3 · ΣNet≈5327.82.

### Theo mã (top / PASS / đáng chú ý)

| Symbol | n | avg pips | hold_med_d | net_E | e/c | hang | CAGR_ff | DD_ff | Kết luận |
|---|---:|---:|---:|---:|---:|---|---:|---:|---|
| AUDCAD | 1011 | 8.992 | 0.7576 | 0.00045535 | 1.9533 | luoi | 1944.501 | 9.643 | **PASS** |
| AUDUSD | 573 | 1.149 | 0.1382 | -0.00019054 | 0.3762 | luoi | 2897.336 | 5.852 | **REJECT** |
| EURGBP | 528 | 1.178 | 0.2007 | -0.00022435 | 0.3406 | luoi | 28.584 | 30.202 | **REJECT** |
| EURUSD | 245 | 3.384 | 0.1583 | 9.952e-05 | 1.3703 | luoi | 251.348 | 2.0 | **REJECT** |
| EURCHF | 207 | -0.398 | 1.3903 | -0.00051073 | -0.0783 | luoi | 66.446 | 5.899 | **REJECT** |
| NZDCAD | 7 | -15.2 | 2.4896 | None | None | luoi | -48.968 | 2.99 | **CHUA_DO** |
| AUDNZD | 2 | 17.3 | 1.2625 | None | None | don_le | 46.013 | 0.0 | **CHUA_DO** |

Mã PASS đơn: **AUDCAD**.
Soft (net_E>0 ∧ e/c≥1.5, có thể trượt CAGR): AUDCAD.

---

## 11583686 — Bitcoin Adi FBS

| Mục | Giá trị |
|---|---|
| Export | `/workspace/myfxbook/11583686.csv` |
| Lệnh ĐO | **1382** Buy/Sell |
| Khoảng | 2024-09-23 → 2026-11-09 (**2.126** năm) |
| /năm | **649.91** |
| buy% | 100.0 |
| hold med | **0.3288 ngày** |
| Hạng | **luoi** (max cùng chiều=34, grid=True, martingale=False, SL%=0.0) |
| fee cover | 0.0% |
| thiếu phí | `{'BTCUSD': 1382}` |

### XM rebuild (ALL)

| Chỉ tiêu | ĐO |
|---|---|
| avg pips | **963.738** |
| XM E[spread] (giá) | None |
| XM E[swap] (giá) | None |
| XM E[cost] | None |
| XM E[gross] | None |
| **net_E_price** | **None** |
| **edge/cost** | **None** |
| CAGR_ff / DD_ff (ƯỚC risk 1%) | None / **None** |
| **Kết luận** | **CHUA_DO** — phí cover 0/1382; thiếu {'BTCUSD': 1382} |

Sàn gốc (cột CSV, nếu có): ΣProfit=17080.83 · ΣComm=0.0 · ΣSwap=0.0 · ΣNet≈17080.83.

### Theo mã (top / PASS / đáng chú ý)

| Symbol | n | avg pips | hold_med_d | net_E | e/c | hang | CAGR_ff | DD_ff | Kết luận |
|---|---:|---:|---:|---:|---:|---|---:|---:|---|
| BTCUSD | 1382 | 963.738 | 0.3288 | None | None | luoi | None | None | **CHUA_DO** |

---

## Cổng S / V1 (chỉ don_le hoặc pyramid PASS)

Điều kiện: Cổng 0 PASS **và** hang ∈ {don_le, pyramid}. Hệ lưới (Rainy ALL, NoPain, MidasAlgo) **không** đưa Cổng S.

### Ứng viên

| Nguồn | Symbol | hang | n | Cổng 0 | Ghi chú |
|---|---|---|---:|---|---|
| 8016551 R Factor | XAUAUD | don_le | 94 | PASS | e/c=24.72 · CAGR_ff=41.4 · DD_ff=1.4 |
| 8016551 R Factor | XAUEUR | don_le | 68 | PASS | e/c=2.85 · CAGR_ff=11.6 · DD_ff=3.3 |
| 11576068 Rainy | AUDCHF | don_le | 25 | PASS | always_sell 100%; hold med ~96h |
| 11576068 Rainy | XAUUSD/AUDCAD/… | luoi | — | PASS mã | **bỏ** Cổng S (lưới) |
| 11730585 MidasAlgo | AUDCAD | luoi | 1011 | PASS mã | **bỏ** Cổng S (lưới) |

### Cổng S — luật đọc được

Nguồn giá V1: XAUUSD HistData NY7 ÷ FX Dukascopy H1 UTC (synth).

| Symbol | Luật | Match chiều | Match giờ 23+DOW | SL/TP med | ≥60%? |
|---|---|---:|---:|---|---|
| XAUAUD | giờ 23 + DOW Mon/Tue/Thu; chiều = fade 6 nến H1 (off 0h); SL/TP med từ lệnh | **64.89%** (61/94) | 96.81% | 3.5/0.98 | **có** |
| XAUEUR | giờ 23 + DOW Mon/Tue/Thu; chiều = fade 4 nến H1 (off 1h); SL/TP med từ lệnh | **67.65%** (46/68) | 98.53% | 3.5/0.52 | **có** |
| Rainy AUDCHF | always Sell | **100.0%** | — | hold_med=96.07h | có (n=25) |

Nhận xét: XAUAUD/XAUEUR gần như chỉ vào **giờ 23** các ngày **Mon/Tue/Thu**, hold ≤3h, TP≪SL (mean-reversion). Chiều = fade 4–6 nến H1.

### V1 WF 12/3 (XM, risk 1%, params chỉ trên train)

| Symbol | years | /năm | n_oos | CAGR% | DD% | Sharpe | vs random p50 | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| XAUAUD fade6/off0 | 10.76 | 118.96 | 1280 | **-28.73** | **97.639** | -4.609 | -31.149 (beat=True) | **REJECT** |
| XAUEUR fade4/off1 | 10.76 | 120.82 | 1300 | **-12.983** | **82.83** | -1.792 | -12.019 (beat=False) | **REJECT** |
| Rainy AUDCHF always_sell | — | — | — | — | — | — | — | **CHƯA ĐO** — CHUA_DO — không có chuỗi AUDCHF H1 dài trên box; n=25 quá mỏng cho WF 12/3 tin cậy |

> Phí XAUAUD từ fallback MetaQuotes (contract=100); XAUEUR từ XM micro (contract=1). Synth giá = XAUUSD/FX — đủ để ĐO chiều/WF, không thay tick thật broker.

---

## Verdict tổng

| Hệ | Cổng 0 | Cổng S | V1 |
|---|---|---|---|
| NoPain 11204017 | **REJECT** (net_E<0, lưới+martingale) | — | — |
| R Factor Mean Rev 8016551 | **REJECT** ALL (net_E<0, e/c=0.46); XAUAUD/XAUEUR PASS đơn | XAUAUD/XAUEUR match ≥60% | **REJECT** cả hai (CAGR âm, DD>80) |
| R Factor JM 8365278 | **REJECT** (net_E<0, e/c=0.62) | — | — |
| Rainy 11576068 | **PASS** ALL (net_E>0, e/c=1.99, DD_ff=75.3) nhưng **lưới** max=20 | chỉ AUDCHF don_le (n=25) | CHƯA ĐO (thiếu H1 / n mỏng) |
| MidasAlgo 11730585 | **REJECT** ALL (e/c=1.11<1.5); AUDCAD PASS nhưng lưới | — | — |
| Bitcoin Adi 11583686 | **CHƯA ĐO** (0% fee cover BTCUSD) | — | — |

**Không hệ nào PASS V1.** Rainy PASS Cổng 0 nhưng hạng lưới → không đẩy V1 theo quy tắc đơn lệnh/pyramid. Không commit.
