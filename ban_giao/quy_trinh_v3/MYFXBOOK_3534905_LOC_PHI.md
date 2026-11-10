# Myfxbook 3534905 — Cổng 0 phí XM

Giờ Việt Nam (Asia/Bangkok, UTC+7). **Không commit.** Ngày ĐO: 09/11/2026.

| Mục | Giá trị |
|---|---|
| Tài khoản | **3534905** IC Markets **FERRARI2009** (EUR) |
| Export | `/workspace/myfxbook/3534905.csv` |
| Lệnh ĐO | **2708** Buy/Sell (bỏ Deposit/Withdrawal/SUMMAR) |
| Khoảng | 2019-08-19 → 2026-11-06 (**7.217** năm) |
| /năm | **375.2** |
| buy% | 59.1 |
| hold med | **0.0333 ngày** (~48 phút) |
| Script | `myfxbook_3534905_loc_phi.py` · JSON `myfxbook_3534905_loc_phi.json` |

Cổng 0 (cùng logic `loc_phi_nhanh` / MQL5): **REJECT** nếu `net_E_price≤0` hoặc `edge/cost<1.5` hoặc (khi PASS phí) `CAGR_ff≤10%` / `DD_ff≥80%`.

Rebuild XM (đơn vị giá):  
`gross = chiều×(close−open)` · `net = gross − spread_p90_XM + swap_XM(hold)` · `cost = spread + max(−swap,0)` · hoa hồng XM micro ĐO = **0**.

---

## 1. IC Markets (ĐO CSV) vs XM (ước Cổng 0)

| | IC Markets (sàn gốc) | XM micro (Cổng 0) |
|---|---|---|
| Spread | Raw (nằm trong Open/Close) | **p90** từ `phi_xm_micro` / fallback bar |
| Commission | **ĐO** Σ = **−1206.62 EUR** (med **4.30 EUR / lot** RT) | **0** |
| Swap | **ĐO** Σ = **−259.51 EUR** | ƯỚC POINTS × hold × 7/5 |
| Profit giá (cột Profit) | Σ **+2917.85 EUR** | — |
| Net tài khoản EUR | Σ Profit+Comm+Swap = **+1451.72 EUR** (E/lệnh **+0.536**) | `net_E_price` **−0.003429** (âm) |

> Hệ sống được trên IC nhờ **spread hẹp + commission cố định**; khi đổi sang **spread p90 XM** (không hoa hồng), expectancy giá **âm**.

---

## 2. Tổng (ALL 16 mã)

| Chỉ tiêu | ĐO |
|---|---|
| avg pips (tính lại từ giá) | **+4.48** |
| XM E[spread] (giá) | 0.02960 |
| XM E[swap] (giá) | −0.00055 |
| XM E[cost] | 0.03018 |
| XM E[gross] | 0.02672 |
| **net_E_price** | **−0.003429** |
| **edge/cost** | **0.885** (&lt; 1.5) |
| fee cover | 100% (2708/2708) |
| CAGR_ff / DD_ff (ƯỚC risk 1%) | 13.18% / **96.58%** |
| Hạng lưới | **luoi** (max cùng chiều = **8**, grid=True, martingale=False) |
| **Kết luận** | **REJECT** — net_E≤0; edge/cost&lt;1.5 |

---

## 3. Theo từng mã

| Symbol | n | avg pips | hold_med_d | XM sp90 (pips) | net_E_price | e/c | hang | Nguồn phí | Kết luận |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| GBPCAD | 740 | 1.84 | 0.031 | 5.8 | −0.000401 | 0.31 | luoi | phi_xm_micro | REJECT |
| EURAUD | 452 | 3.05 | 0.027 | 4.0 | −0.000107 | 0.74 | pyramid | phi_xm_micro | REJECT |
| EURSGD | 344 | 1.95 | 0.033 | **12.53** | −0.001067 | 0.15 | pyramid | **FALLBACK** chi_phi_do+bar | REJECT |
| EURCAD | 189 | 2.25 | 0.035 | 3.7 | −0.000149 | 0.60 | pyramid | phi_xm_micro | REJECT |
| GBPUSD | 154 | 3.15 | 0.033 | 2.6 | **+0.000053** | **1.20** | pyramid | phi_xm_micro | REJECT (e/c&lt;1.5) |
| CHFJPY | 133 | 3.88 | 0.045 | 4.4 | −0.005541 | 0.88 | don_le | phi_xm_micro | REJECT |
| XAUUSD | 128 | 52.12 | 0.005 | 57.0 | −0.060072 | 0.90 | don_le | phi_xm_micro | REJECT |
| EURGBP | 125 | 1.18 | 0.048 | 2.5 | −0.000135 | 0.47 | don_le | phi_xm_micro | REJECT |
| USDCAD | 125 | 0.61 | 0.044 | 3.2 | −0.000261 | 0.19 | pyramid | phi_xm_micro | REJECT |
| GBPAUD | 95 | 0.27 | 0.044 | 5.1 | −0.000489 | 0.05 | pyramid | phi_xm_micro | REJECT |
| EURUSD | 90 | 1.95 | 0.038 | 2.2 | −0.000029 | 0.87 | pyramid | phi_xm_micro | REJECT |
| EURCHF | 63 | 1.32 | 0.090 | 3.4 | −0.000200 | 0.39 | pyramid | phi_xm_micro | REJECT |
| AUDCAD | 36 | 0.99 | 0.050 | 2.77 | −0.000181 | 0.35 | luoi | **FALLBACK** | REJECT |
| USDCHF | 18 | 3.54 | 0.039 | 2.89 | **+0.000053** | **1.18** | don_le | **FALLBACK** | REJECT (e/c&lt;1.5) |
| CADCHF | 15 | 0.28 | 0.166 | 6.98 | −0.000667 | 0.04 | don_le | **FALLBACK** | REJECT |
| AUDUSD | 1 | 4.00 | 0.006 | 2.5 | — | — | don_le | phi_xm_micro | **CHƯA ĐO** (n=1) |

**FALLBACK** (không có trong `phi_xm_micro.json`): **EURSGD, AUDCAD, USDCHF, CADCHF** — dùng `chi_phi_do` *MICRO* + `_spread_bar_mt5` XM (nhãn rõ trong JSON).

---

## 4. Lưới / martingale

| | ĐO |
|---|---|
| max cùng chiều (sau gộp partial, trong từng mã) | **8** |
| Hạng ALL | **luoi** |
| grid flag | **True** |
| martingale (lot↑ sau lỗ ≥25% lần kiểm) | **False** |
| Theo mã | GBPCAD+AUDCAD → luoi; nhiều mã pyramid (max 3–7 + SL); XAU/CHFJPY/EURGBP/USDCHF/CADCHF → don_le |

---

## 5. Subset mã có sống sót?

| Tập | Symbols | Kết quả |
|---|---|---|
| PASS đơn mã (net_E&gt;0 ∧ e/c≥1.5 ∧ CAGR/DD) | **∅** | không mã nào |
| net_E&gt;0 ∧ e/c≥1.5 (bỏ qua CAGR) | **∅** | GBPUSD e/c=1.20; USDCHF e/c=1.18 — cả hai &lt;1.5 |
| Bỏ EURSGD (fallback đắt, sp90≈12.5 pip) | phần còn lại vẫn net_E tổng âm / e/c&lt;1.5 | không cứu được ALL |

→ **Không có subset mã nào vượt Cổng 0.**

---

## 6. Verdict

**REJECT** toàn tài khoản và từng mã (trừ AUDUSD n=1 = CHƯA ĐO).

- IC net **+1451.72 EUR** / 7.2 năm; XM rebuild **net_E_price&lt;0**, **edge/cost=0.89**.
- Edge pip mỏng (avg ~1–4 pip FX; hold ~0.5–2 giờ) không đủ bù spread p90 XM.
- Cờ **lưới** (max=8); không martingale.
- EURSGD thiếu `phi_xm_micro` → fallback spread ~12.5 pip (nặng nhất).

**Không đưa sang V1.** Không commit.
