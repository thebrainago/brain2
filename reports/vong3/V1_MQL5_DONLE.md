# V1 — MQL5 don_le (+ pyramid e/c≥1.2) + Seeker đợt 2

Giờ Việt Nam (Asia/Bangkok, UTC+7). Báo cáo phân tích **Anh commit**. Phương án vận hành đã đẩy git (`2b0bcc0a`). Ngày ĐO: 09/11/2026.

---

## 0. Phạm vi

**don_le (8)** — loại **2229059** đã V1 REJECT:

| ID | Tên | e/c | Xử lý |
|---|---|---:|---|
| 1862128 | Happy Gold | 1.094 | Bỏ (&lt;1.2) |
| 2342395 | KUHN | 0.168 | Bỏ |
| **2244828** | Kivenara 815m52ff | 3.573 | RE+V1 |
| **2269966** | BreakZone | 1.285 | RE+V1 |
| **2245675** | OnlyUJ | 1.250 | RE+V1 |
| **2250577** | Golden System 2 | 2.571 | RE+V1 |
| 2356275 | LANCER | −0.106 | Bỏ |
| 2229059 | Kivenara 8315 | 2.069 | Đã REJECT |

**Pyramid** PASS / e/c≥1.2: MCA100 + Friday Pro (đã làm); **2392805** UZUNAMI88; **2337217** Top Cat S.

---

## 1. Match luật (≥60%)

| ID | Luật | Match | Ghi chú |
|---|---|---:|---|
| 2244828 | H1 SMA50 off2 @18:00 | **88.9%** | D1 prior_bull 64.1% |
| 2250577 | H1 SMA20 → D1 SMA20 | H1 99.6% / D1 **76.1%** | SL/TP 6.72/25.96 |
| 2269966 | H1 SMA50 → D1 SMA50 | H1 99.8% / D1 **63.9%** | |
| 2392805 XAU | H1 SMA20 → D1 SMA20 | H1 93.1% / D1 **72.9%** | |
| **2245675** | Asia range break (H0–7 prior) | **65.1%** (255/392) | H1 SMA max 59.4% &lt;60 |
| **2337217** | Fade SMA50 | **78.5%** | ≈ always_sell 71.2% |

---

## 2. V1 OOS (WF 12/3, XM, risk 1%)

| ID | Luật V1 | years | /năm | CAGR% | DD% | Sharpe | Verdict |
|---|---|---:|---:|---:|---:|---:|---|
| 2244828 | H1 SMA50 SL100 TP175 | 1.35 | 237 | **+8.24** | 22.2 | 0.36 | **REJECT** (CAGR≤10; thắng random) |
| 2244828 | D1 prior_bull | 17.5 | 56 | −6.97 | 75.9 | −0.57 | REJECT |
| 2250577 | D1 SMA20 | 16.5 | 87 | −17.6 | 96.3 | −0.67 | REJECT |
| 2269966 | D1 SMA50 | 16.5 | 122 | −41.5 | ~100 | −1.59 | REJECT |
| 2392805 XAU | D1 SMA20 | 16.4 | 63 | −11.8 | 88.3 | −0.74 | REJECT |
| 2337217 | D1 fade SMA50 | 1.5 | 131 | −87.7 | 95.7 | −11 | REJECT |
| 2229059 | (trước) H1 | 2.1 | 231 | −9.33 | 29.8 | −0.49 | REJECT |
| 2153920 | (trước) breakout | 16.5 | 81 | −7.08 | 72.5 | −0.68 | REJECT |
| **2245675** | Asia H0–7 break SL100/TP150 | **17.5** | **69.2** | **+32.01** | **17.2** | **1.62** | **PASS** |

### 2245675 OnlyUJ — **PASS V1** (H1 2008–2026)

- Match Asia range break (prior day H0–7) trên lệnh thật: **65.1%** (255/392).
- Dữ liệu: HistData H1 2008–2023 NY7 + M5/Duka 2024–2026 (`usdjpy_h1_2008_2023_ny7.csv`).
- V1 WF 12/3, SL base 100 pip / TP 150, mult tối ưu train, XM `phi_xm_micro`, risk 1%, hold_cap 30d:
  - n OOS **1210** · **69.2**/năm · **CAGR +32.01%** · **DD 17.22%** · Sharpe **1.62**
  - boot p50/p05: 32.0% / 30.0% · random-entry p50 **−2.78%** · **beat_random=true**
- D1 Yahoo prior-day H/L (proxy kém hơn Asia): CAGR −1.92% DD 44% → REJECT — cho thấy **khung Asia H0–7** là phần quan trọng của luật.
- File: `v1_onlyuj_asia_h1_dai.json`.


Friday Pro: B&H sau swap CAGR 3.8–5.8% — không đạt 10%.

JSON: `v1_donle_ket_qua.json`.

---

## 3. Seeker đợt 2

File: `/workspace/quy_trinh_v3/mql5_dot2_ids.txt` (**60 ID**, đã push `reports/vong3/`).

- T1 brief chặt: **10** · XM: **8** · XAU: **28** · hard-grid page: **0**
- Nới age≥18 / ≤5sym vì pool tuổi≥24≤3sym sau loại 83 hist quá mỏng
- Meta: `mql5_dot2_meta.json`

Anh export history → Cổng 0 đợt 2.

---

## 4. Myfxbook captcha

Đã push `reports/vong3/MYFXBOOK_CAPTCHA_PHUONG_AN.md`:
- Box IP = CF **403**; cần browser session (box hoặc CDP máy nhà)
- Subagent tự thử captcha; handoff khi Anh online
- Không bypass CF / không thuê giải captcha

---

## 5. Verdict

| Hạng mục | Kết quả |
|---|---|
| V1 don_le/pyramid đủ dữ liệu dài | **1 PASS** = OnlyUJ 2245675 |
| **OnlyUJ Asia-break** | **PASS** CAGR **+32.0%** DD **17.2%** Sharpe 1.62 (H1 2008–2026) |
| Gần nhất (không PASS) | Kivenara 815 H1 CAGR +8.2% DD 22% |
| Seeker đợt 2 | **60 ID** sẵn |
| Myfxbook | Chờ session khi Anh về |

**Không commit** báo cáo phân tích trong `/workspace/quy_trinh_v3/` (Anh commit). Đã push phương án + dot2 IDs lên `brain2` main.
