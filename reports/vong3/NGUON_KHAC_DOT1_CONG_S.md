# Cổng S / V1 — RC 105 + Tendency EURUSD + ứng viên

Giờ VN Asia/Bangkok. ĐO 2026-11-09 23:59.

## A. C2 143135149 RC 105 ForEx (toàn TK PASS don_le ≥2y)

- C2 author KishoreRamaraju3; mô tả truncated: major pairs, Medium Risk — **không** nêu luật vào lệnh.
- n=724, hold med=4.416h, SL/TP=0% trên statement, session ET={'ny_et': 289, 'asia_et': 154, 'ny_aft_et': 90, 'london_et': 191}
- Feature H1 overlap n_feat≈156/724 (giá từ ~2024).

### Rule match (best)

| Family | match% | ok/tot |
|---|---:|---|
| above_below_ma200 | 78.21 | 122/156 |
| session_breakout_H4 | 75.56 | 34/45 |
| session_breakout_H4_lonNY | 75.0 | 24/32 |
| session_breakout_H1 | 73.02 | 46/63 |
| session_breakout_H12_lonNY | 72.0 | 18/25 |
| session_breakout_H1_lonNY | 71.74 | 33/46 |
| session_breakout_D1_lonNY | 69.77 | 30/43 |
| session_breakout_H12 | 67.86 | 19/28 |
| session_breakout_D1 | 67.31 | 35/52 |
| ma_trend_20_50 | 66.67 | 104/156 |
| breakout_or_mid_H1 | 63.46 | 99/156 |
| breakout_or_mid_D1 | 62.18 | 97/156 |

- ≥60%: 15 · ≥70%: 6 · best **above_below_ma200 78.21%**

### V1 WF 12/3 RC105 (EURUSD/GBPUSD/USDJPY) — tất cả REJECT

| Symbol/Rule | verdict | CAGR% | DD% | n_oos | beat_rand |
|---|---|---:|---:|---:|:---:|
| EURUSD/above_below_ma200 | **REJECT** | -40.103 | 59.741 | 444 | False |
| EURUSD/ma_trend_20_50 | **REJECT** | -36.122 | 54.468 | 420 | False |
| EURUSD/session_breakout_H1 | **REJECT** | -10.33 | 27.36 | 332 | True |
| EURUSD/session_breakout_H4 | **REJECT** | -1.279 | 2.193 | 3 | False |
| GBPUSD/above_below_ma200 | **REJECT** | -40.406 | 59.167 | 506 | False |
| GBPUSD/ma_trend_20_50 | **REJECT** | -20.877 | 35.523 | 451 | True |
| GBPUSD/session_breakout_H1 | **REJECT** | -19.33 | 29.953 | 360 | True |
| GBPUSD/session_breakout_H4 | **REJECT** | -5.543 | 6.491 | 6 | False |
| USDJPY/above_below_ma200 | **REJECT** | -58.344 | 78.024 | 627 | False |
| USDJPY/ma_trend_20_50 | **REJECT** | -49.629 | 68.735 | 622 | False |
| USDJPY/session_breakout_H1 | **REJECT** | -48.614 | 65.981 | 464 | False |
| USDJPY/session_breakout_H4 | **REJECT** | 1.73 | 2.264 | 3 | True |

## B. C2 122467834 Tendency Forex / EURUSD (mã con PASS don_le ≥2y)

- Cổng 0 mã: n=380, y=2.565, hang=don_le, e/c≈1.6812685066024227, CAGR_ff≈40.97732671407801, DD≈12.274220698317839 → **PASS**
- Trades 2019-02→2021-09; H1 HistData 2018–2023; n_feat=380
- Hold med h=6.488; session={'ny_et': 125, 'ny_aft': 45, 'asia': 92, 'london_et': 118}

### Rule match Tendency EURUSD

| Family | match% | ok/tot |
|---|---:|---|
| fade_bb | 78.12 | 25/32 |
| fade_H12 | 73.16 | 169/231 |
| dopen_rev | 65.61 | 248/378 |
| fade_D1 | 61.75 | 176/285 |
| fade_rsi | 60.61 | 100/165 |
| fade_H4 | 56.35 | 173/307 |
| fade_H1 | 55.4 | 195/352 |
| ma20_50 | 53.95 | 205/380 |
| ma200 | 51.32 | 195/380 |
| mid_H4 | 46.05 | 175/380 |
| mid_H1 | 44.74 | 170/380 |
| breakout_H4 | 44.1 | 71/161 |

### V1 Tendency EURUSD

| Rule | verdict | CAGR% | DD% | n_oos | beat_rand | rand_p50 |
|---|---|---:|---:|---:|:---:|---:|
| ma200 | **REJECT** | -28.355 | 60.119 | 644 | True | -33.194 |
| ma20_50 | **REJECT** | -21.874 | 50.441 | 626 | True | -33.197 |
| brk_h1 | **REJECT** | -26.103 | 58.344 | 528 | True | -28.113 |
| fade_H12 | **REJECT** | -17.427 | 34.868 | 440 | True | -32.175 |
| dopen_rev | **REJECT** | -27.137 | 49.846 | 464 | True | -31.168 |

## C. Don_le PASS phí subset ≥2y (scan)

| Source/ID | Symbol | n | years | e/c |
|---|---|---:|---:|---:|
| collective2/122467834 | EURCHF | 96 | 2.22 | 1.780 |
| collective2/122467834 | EURUSD | 380 | 2.57 | 1.681 |
| collective2/122467834 | NZDJPY | 51 | 2.32 | 1.801 |
| collective2/94987184 | USDCHF | 84 | 6.79 | 1.782 |
| collective2/94987184 | AUDCAD | 37 | 6.7 | 2.069 |
| collective2/94987184 | EURUSD | 30 | 6.67 | 9.924 |
| collective2/94987184 | NZDCAD | 48 | 6.67 | 2.032 |
| collective2/94987184 | EURGBP | 50 | 5.8 | 9.816 |
| collective2/94987184 | CADCHF | 79 | 5.83 | 1.574 |
| collective2/94987184 | NZDUSD | 47 | 5.45 | 4.424 |
| collective2/94987184 | GBPAUD | 60 | 5.44 | 7.212 |
| collective2/94987184 | GBPCAD | 30 | 5.38 | 3.350 |
| collective2/94987184 | AUDUSD | 46 | 4.78 | 4.835 |
| collective2/143135149 | GBPUSD | 58 | 2.56 | 2.470 |
| collective2/143135149 | EURUSD | 73 | 2.46 | 4.796 |
| collective2/143135149 | USDJPY | 49 | 2.38 | 2.595 |
| collective2/143135149 | EURCAD | 35 | 2.13 | 1.682 |

## D. Ứng viên cũ

| Ứng viên | Cổng S | V1 |
|---|---|---|
| liehtw/XAUEUR, multiprofit/USDCAD, free-forex-signal | CHUA_GIAI_MA | chưa |

**Kết luận:** Match chiều ≥60–78% tìm được (RC105 breakout/MA; Tendency fade), nhưng **V1 WF chưa PASS**. Chưa đẩy V3. Hunt thêm FX Blue/C2: không có don_le/pyramid PASS ≥2y **toàn TK** mới (ngoài RC105).

As-of: 2026-11-09 23:59:20 Asia/Bangkok.