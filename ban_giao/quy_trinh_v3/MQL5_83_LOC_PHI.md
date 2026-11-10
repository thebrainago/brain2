# MQL5 83 tín hiệu — Cổng 0 phí XM + Cổng S (09/11/2026)

Giờ Việt Nam (Asia/Bangkok, UTC+7). **Không commit.**

Nguồn danh sách: `brain2/reports/MQL5_LOC_CHAT.md` (**83** ĐẠT lọc chặt).
Export lịch sử: `/workspace/mql5_hist/{ID}.csv` — **82** file; **2391347** Aurum Titan = NotFound.
Phí: `config/phi_xm_micro.json` (ĐO) ưu tiên; thiếu → `chi_phi_do.json` MICRO + `_spread_bar_mt5` (có nhãn nguồn/sàn).
Hoa hồng XM micro ĐO = **0**.

File kèm:
- `/workspace/quy_trinh_v3/phan_tich_mql5_hist.py`
- `/workspace/quy_trinh_v3/mql5_83_loc_phi_tom_tat.csv`
- `/workspace/quy_trinh_v3/mql5_83_loc_phi_ket_qua.json`

---

## 0. Đếm Cổng 0

| Kết luận | Số |
|---|---|
| **PASS** | **17** |
| **REJECT** | **61** |
| **CHƯA ĐO** | **5** |
| Tổng ID trong LOC_CHAT | **83** |

**Lý do REJECT chính** (một ID có thể nhiều lý do):
- edge/cost < 1.5: **57**
- net_E_price ≤ 0: **37**
- CAGR_ff/DD_ff cổng: **4**

- Cờ lưới (nhiều lệnh cùng chiều chồng): **78**
- Cờ martingale (lot tăng sau lỗ ≥25% lần kiểm): **3**
- All-one-direction (buy≥95% hoặc ≤5%): **7**
- Export có tổng Commission ≠ 0 (sàn gốc ECN): **40**

> Hầu hết REJECT vì **edge/cost < 1,5** sau khi gắn spread p90 + swap XM — đúng ý Anh: bỏ nhanh hệ sống nhờ spread sàn gốc hẹp.

---


## 0b. Đếm lại lưới (sau sửa detector — 09/11/2026 chiều)

Detector cũ: overlap≥5% hoặc max_cùng_chiều≥3 → **78/83** gắn lưới (quá nhạy; partial close / scale-in 2–3 lệnh có SL bị tính).

Detector mới:
1. Gộp partial cùng `(symbol, chiều, t_open)` trước khi đo.
2. Chỉ đo chồng lệnh **trong từng mã**.
3. Ba hạng:
   - `don_le`: max cùng chiều ≤ 2
   - `pyramid`: max 3–7 và có SL đáng kể (không phải lưới thuần)
   - `luoi`: max ≥ 8 **hoặc** (max ≥ 4 và SL% < 20)

| Hạng | Số ĐO |
|---|---|
| don_le | 8 |
| pyramid | 9 |
| luoi | 65 |
| khong_file | 1 |
| martingale (lot↑ sau lỗ) | 4 |

MCA100 → `pyramid` (max=3, SL=100%). Friday Pro → `pyramid` (max=5, SL=99.7%). Kivenara → `don_le` (max=1).


## 1. Phương pháp (đo / giả định)

| Bước | Chi tiết |
|---|---|
| Parse | 55 CSV round-trip; 27 CSV deal In/Out (Out ghép FIFO với chiều ngược). Bỏ `cancelled`. |
| Map mã | GOLD*/XAUUSD.* → XAUUSD; NAS100/NQ → US100; bóc `.fx/# /micro/-E`. |
| Gross | `chieu×(close−open)` (đơn vị giá). |
| Phí XM | Spread p90 + swap. POINTS: `swap_diem×point×hold×7/5`. Chỉ số non-POINTS: `−phi_nam×gia×hold/365`. |
| Cổng 0 | REJECT nếu net_E≤0 hoặc edge/cost<1,5 hoặc CAGR_ff≤10%/DD_ff≥80% (khi tính được). |
| CAGR_ff | **ƯỚC**: V0=10.000, rủi ro 1%/lệnh theo SL (không SL → `|net_price|`). Không phải equity tài khoản gốc. |
| US100/US500 | Chưa có trong phi_xm_micro; dùng chi_phi_do (NAS100 **FXCE**) + spread bar × gia — nhãn **CHƯA ĐỒNG BỘ XM**. |

---

## 2. Bảng PASS (17)

| # | ID | Tên | n | /năm | buy% | hold_med | e/c | net_E | CAGR_ff | DD_ff | lưới | S |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 2394758 | Harmonizer High Risk | 1332 | 642.6 | 46.8 | 1.178 | 1.786 | 0.000449 | 686.01 | 8.77 | True | trung/3 |
| 4 | 2360068 | Harmonizer Extreme | 1468 | 653.4 | 46.2 | 1.206 | 1.634 | 0.000364 | 556.25 | 9.81 | True | trung/3 |
| 7 | 2231030 | MSC Gold Stable Pro | 1192 | 474.1 | 83.6 | 0.004 | 2.443 | 0.8829 | 865.47 | 7.75 | True | yeu/1 |
| 8 | 2153920 | MCA100 | 433 | 145.7 | 88.0 | 0.019 | 2.614 | 1.077001 | 56.27 | 22.34 | True | trung/5 |
| 14 | 2265943 | The Gold Miner | 1393 | 678.6 | 60.8 | 0.775 | 2.414 | 2.641304 | 59.65 | 32.74 | True | trung/4 |
| 17 | 2351061 | Gold Minion | 822 | 274.4 | 64.7 | 0.223 | 5.298 | 4.163231 | 21.32 | 48.5 | True | yeu/1 |
| 19 | 2344620 | Friday Pro | 321 | 98.8 | 99.7 | 4.744 | 19.599 | 0.264266 | 21.13 | 12.06 | True | manh/7 |
| 21 | 2380604 | MSC Gold Fund Pro | 1903 | 570.9 | 66.4 | 0.008 | 3.034 | 1.280601 | 955.6 | 12.36 | True | yeu/1 |
| 23 | 2196457 | X117 Taoist nature | 1916 | 694.7 | 60.6 | 0.036 | 3.542 | 1.86385 | 280.33 | 38.03 | True | yeu/0 |
| 26 | 2242498 | Goldtrade Pro High Risk | 674 | 290.8 | 58.9 | 0.195 | 7.997 | 5.826584 | 53.04 | 41.0 | True | yeu/2 |
| 27 | 1725090 | My Son Trading Account | 1749 | 426.5 | 100.0 | 0.869 | 10.105 | 10.553198 | 781.02 | 12.37 | True | yeu/0 |
| 35 | 2042164 | PrismaForex | 2230 | 525.6 | 42.5 | 3.118 | 2.262 | 0.000804 | 563.58 | 18.54 | True | yeu/1 |
| 46 | 2229059 | Kivenara 8315m01f | 664 | 245.2 | 55.7 | 0.128 | 2.069 | 3.783014 | 22.05 | 14.36 | False | manh/10 |
| 54 | 2195619 | The Gold Reaper Live default settings | 1504 | 548.5 | 60.4 | 0.038 | 3.899 | 2.231817 | 248.73 | 27.13 | True | yeu/1 |
| 55 | 2272380 | NANO M0NEY CORP from FXGP WMC | 636 | 252.9 | 39.8 | 1.527 | 2.231 | 0.001128 | 53.28 | 24.21 | True | yeu/0 |
| 57 | 2183815 | Jaya bersama XM 1 | 461 | 164.0 | 66.4 | 1.636 | 34.846 | 0.414735 | 135.83 | 8.74 | True | yeu/0 |
| 60 | 2126101 | TriForce MT5 | 5773 | 1974.0 | 48.9 | 0.372 | 1.606 | 0.000187 | None | 30.73 | True | yeu/1 |

---

## 3. CHƯA ĐO (5)

| ID | Tên | Lý do ngắn |
|---|---|---|
| 2391347 | Aurum Titan | không có file export |
| 2049326 | SFE Impulse | phí XM chỉ cover 0/1125 lệnh (0%); thiếu: {'ETHUSD': 653, 'BTCUSD': 472}; CỜ:overlap_same_dir=732, max_cung_chieu_mo=11; SL_pct=0.0 |
| 2234719 | Navi | phí XM chỉ cover 0/1745 lệnh (0%); thiếu: {'BTCUSD': 1745}; CỜ:overlap_same_dir=1392, max_cung_chieu_mo=22; SL_pct=0.0 |
| 2198360 | XXX OIL | phí XM chỉ cover 0/8666 lệnh (0%); thiếu: {'OTHER:BRENT_ECN': 4566, 'OTHER:UKOIL_ECN': 2253, 'OTHER:CL_ECN': 1847}; CỜ:overlap_same_dir=4101 |
| 2103795 | Bitcoin Scalp Pro | phí XM chỉ cover 0/1469 lệnh (0%); thiếu: {'BTCUSD': 1469}; CỜ:overlap_same_dir=555, max_cung_chieu_mo=7; SL_pct=0.0 |

---

## 4. Top 10 cho V1

### 1. 2229059 — Kivenara 8315m01f (#46)
- Cổng 0: **PASS** — ok
- Phí: edge/cost=**2.069**, net_E_price=**3.783014**, cover=100.0%
- FF ƯỚC: CAGR_ff=22.05% DD_ff=14.36% · Meta MQL5 CAGR=51.71 DD=34.62
- Lệnh: n=664, 245.2/năm, hold_med=0.128d, max_concurrent=2, buy=55.7%, SL%=100.0
- Lưới/MG: grid=False martingale=False ()
- Cổng S: **manh** (10) — phút_vào=30 (100%); SL_offset_med=100 ổn định; TP_offset_med=165 ổn định; 2 chiều cân (56% buy); 1 mã
- B&H mã chính US100: ret giá 54.61%, CAGR giá ≈ 17.46%
- Lý do xếp V1: vào/ra tái lập được; SL gần 100% lệnh; không lưới; sống phí XM trên mẫu

### 2. 2244828 — Kivenara 815m52ff (#13)
- Cổng 0: **REJECT** — CAGR_ff=4.64/DD_ff=28.33 không đạt 10%/80%
- Phí: edge/cost=**3.573**, net_E_price=**9.244**, cover=100.0%
- FF ƯỚC: CAGR_ff=4.64% DD_ff=28.33% · Meta MQL5 CAGR=136.55 DD=36.81
- Lệnh: n=621, 238.0/năm, hold_med=0.133d, max_concurrent=1, buy=57.0%, SL%=100.0
- Lưới/MG: grid=False martingale=False ()
- Cổng S: **manh** (10) — phút_vào=0 (100%); SL_offset_med=100 ổn định; TP_offset_med=175 ổn định; 2 chiều cân (57% buy); 1 mã
- B&H mã chính US100: ret giá 47.91%, CAGR giá ≈ 16.19%
- Lý do xếp V1: vào/ra tái lập được; SL gần 100% lệnh; không lưới; phí OK nhưng CAGR_ff < 10% — vẫn đáng dịch luật

### 3. 2344620 — Friday Pro (#19)
- Cổng 0: **PASS** — CỜ:overlap_same_dir=91, max_cung_chieu_mo=5
- Phí: edge/cost=**19.599**, net_E_price=**0.264266**, cover=99.7%
- FF ƯỚC: CAGR_ff=21.13% DD_ff=12.06% · Meta MQL5 CAGR=90.41 DD=33.16
- Lệnh: n=321, 98.8/năm, hold_med=4.744d, max_concurrent=7, buy=99.7%, SL%=99.69
- Lưới/MG: grid=True martingale=False (overlap_same_dir=91, max_cung_chieu_mo=5)
- Cổng S: **manh** (7) — phút_vào=59 (100%); SL_offset_med=0.903 ổn định; TP_offset_med=1.603 ổn định; lệch chiều buy=100%
- B&H mã chính GBPJPY: ret giá 17.11%, CAGR giá ≈ 4.98%
- Lý do xếp V1: vào/ra tái lập được; SL gần 100% lệnh; sống phí XM trên mẫu; ⚠ lệch 1 chiều; ⚠ có overlap — cần trần tầng

### 4. 2153920 — MCA100 (#8)
- Cổng 0: **PASS** — CỜ:overlap_same_dir=169, max_cung_chieu_mo=3
- Phí: edge/cost=**2.614**, net_E_price=**1.077001**, cover=100.0%
- FF ƯỚC: CAGR_ff=56.27% DD_ff=22.34% · Meta MQL5 CAGR=171.15 DD=35.37
- Lệnh: n=433, 145.7/năm, hold_med=0.019d, max_concurrent=4, buy=88.0%, SL%=100.0
- Lưới/MG: grid=True martingale=False (overlap_same_dir=169, max_cung_chieu_mo=3)
- Cổng S: **trung** (5) — SL_offset_med=6.85 ổn định; TP_offset_med=8.53 ổn định
- B&H mã chính XAUUSD: ret giá 108.51%, CAGR giá ≈ 28.04%
- Lý do xếp V1: SL gần 100% lệnh; sống phí XM trên mẫu; ⚠ có overlap — cần trần tầng

### 5. 2265943 — The Gold Miner (#14)
- Cổng 0: **PASS** — CỜ:overlap_same_dir=1269, max_cung_chieu_mo=9; SL_pct=0.0
- Phí: edge/cost=**2.414**, net_E_price=**2.641304**, cover=100.0%
- FF ƯỚC: CAGR_ff=59.65% DD_ff=32.74% · Meta MQL5 CAGR=190.25 DD=44.95
- Lệnh: n=1393, 678.6/năm, hold_med=0.775d, max_concurrent=10, buy=60.8%, SL%=0.0
- Lưới/MG: grid=True martingale=False (overlap_same_dir=1269, max_cung_chieu_mo=9; SL_pct=0.0)
- Cổng S: **trung** (4) — phút_vào=0 (63%); 1 mã
- B&H mã chính XAUUSD: ret giá 51.24%, CAGR giá ≈ 22.33%
- Lý do xếp V1: sống phí XM trên mẫu; ⚠ có overlap — cần trần tầng

### 6. 2394758 — Harmonizer High Risk (#2)
- Cổng 0: **PASS** — CỜ:overlap_same_dir=618, max_cung_chieu_mo=17; SL_pct=0.0
- Phí: edge/cost=**1.786**, net_E_price=**0.000449**, cover=100.0%
- FF ƯỚC: CAGR_ff=686.01% DD_ff=8.77% · Meta MQL5 CAGR=482.14 DD=14.93
- Lệnh: n=1332, 642.6/năm, hold_med=1.178d, max_concurrent=24, buy=46.8%, SL%=0.0
- Lưới/MG: grid=True martingale=False (overlap_same_dir=618, max_cung_chieu_mo=17; SL_pct=0.0)
- Cổng S: **trung** (3) — phút_vào=15 (29%); 2 chiều cân (47% buy)
- B&H mã chính AUDCAD: ret giá 4.71%, CAGR giá ≈ 2.25%
- Lý do xếp V1: sống phí XM trên mẫu; ⚠ có overlap — cần trần tầng; ⚠ CAGR_ff rất cao — nghi proxy rủi ro; chỉ tham khảo

### 7. 2360068 — Harmonizer Extreme (#4)
- Cổng 0: **PASS** — CỜ:overlap_same_dir=690, max_cung_chieu_mo=17; SL_pct=0.0
- Phí: edge/cost=**1.634**, net_E_price=**0.000364**, cover=100.0%
- FF ƯỚC: CAGR_ff=556.25% DD_ff=9.81% · Meta MQL5 CAGR=350.43 DD=22.42
- Lệnh: n=1468, 653.4/năm, hold_med=1.206d, max_concurrent=24, buy=46.2%, SL%=0.0
- Lưới/MG: grid=True martingale=False (overlap_same_dir=690, max_cung_chieu_mo=17; SL_pct=0.0)
- Cổng S: **trung** (3) — phút_vào=15 (27%); 2 chiều cân (46% buy)
- B&H mã chính AUDCAD: ret giá 7.66%, CAGR giá ≈ 3.34%
- Lý do xếp V1: sống phí XM trên mẫu; ⚠ có overlap — cần trần tầng; ⚠ CAGR_ff rất cao — nghi proxy rủi ro; chỉ tham khảo

### 8. 2242498 — Goldtrade Pro High Risk (#26)
- Cổng 0: **PASS** — CỜ:overlap_same_dir=524, max_cung_chieu_mo=22; SL_pct=0.0
- Phí: edge/cost=**7.997**, net_E_price=**5.826584**, cover=100.0%
- FF ƯỚC: CAGR_ff=53.04% DD_ff=41.0% · Meta MQL5 CAGR=150.39 DD=60.45
- Lệnh: n=674, 290.8/năm, hold_med=0.195d, max_concurrent=22, buy=58.9%, SL%=0.0
- Lưới/MG: grid=True martingale=False (overlap_same_dir=524, max_cung_chieu_mo=22; SL_pct=0.0)
- Cổng S: **yeu** (2) — 2 chiều cân (59% buy); 1 mã
- B&H mã chính XAUUSD: ret giá 71.83%, CAGR giá ≈ 26.3%
- Lý do xếp V1: sống phí XM trên mẫu; ⚠ có overlap — cần trần tầng

### 9. 2351061 — Gold Minion (#17)
- Cổng 0: **PASS** — CỜ:overlap_same_dir=633, max_cung_chieu_mo=22; SL_pct=0.0
- Phí: edge/cost=**5.298**, net_E_price=**4.163231**, cover=100.0%
- FF ƯỚC: CAGR_ff=21.32% DD_ff=48.5% · Meta MQL5 CAGR=98.92 DD=29.66
- Lệnh: n=822, 274.4/năm, hold_med=0.223d, max_concurrent=22, buy=64.7%, SL%=0.0
- Lưới/MG: grid=True martingale=False (overlap_same_dir=633, max_cung_chieu_mo=22; SL_pct=0.0)
- Cổng S: **yeu** (1) — 1 mã
- B&H mã chính XAUUSD: ret giá 108.31%, CAGR giá ≈ 27.76%
- Lý do xếp V1: sống phí XM trên mẫu; ⚠ có overlap — cần trần tầng

### 10. 2195619 — The Gold Reaper Live default settings (#54)
- Cổng 0: **PASS** — CỜ:overlap_same_dir=1188, max_cung_chieu_mo=24; SL_pct=0.0
- Phí: edge/cost=**3.899**, net_E_price=**2.231817**, cover=100.0%
- FF ƯỚC: CAGR_ff=248.73% DD_ff=27.13% · Meta MQL5 CAGR=56.15 DD=45.64
- Lệnh: n=1504, 548.5/năm, hold_med=0.038d, max_concurrent=24, buy=60.4%, SL%=0.0
- Lưới/MG: grid=True martingale=False (overlap_same_dir=1188, max_cung_chieu_mo=24; SL_pct=0.0)
- Cổng S: **yeu** (1) — 1 mã
- B&H mã chính XAUUSD: ret giá 100.52%, CAGR giá ≈ 28.88%
- Lý do xếp V1: sống phí XM trên mẫu; ⚠ có overlap — cần trần tầng; ⚠ CAGR_ff rất cao — nghi proxy rủi ro; chỉ tham khảo

---

## 5. Broker gốc vs XM

- Profit/Swap/Commission trong CSV = **sàn gốc** (nhiều ECN có commission).
- Cổng 0 **thay** bằng spread p90 XM + swap XM (hoa hồng 0). Scalp trên spread hẹp gốc thường chết.
- Ví dụ #1 EA Happy Gold Eightcap (`1862128`): meta CAGR 237% nhưng edge/cost XM = **1,094** → REJECT.
- Vàng giữ lâu: swap XM GOLDmicro long −83,83 điểm/đêm (phi_xm_micro) ăn edge.
- US100: phí dùng NAS100 FXCE + spread bar quy đổi — cần đo lại trên XM trước khi tin CAGR_ff.

---

## 6. Việc cần Anh / bước sau

1. Code V1 trước cho **2229059** (và thử **2244828** cùng họ).
2. Đo `US100`/`US500`/`BTCUSD` vào `phi_xm_micro.json` trên tài khoản XM.
3. Export lại **2391347** nếu muốn đủ 83.
4. Các PASS còn lưới vàng: chỉ đưa V3 khi có `InpGiuToiDaNen` + so ngẫu nhiên.

*Tạo 2026-11-09 15:59 (UTC+7).*
