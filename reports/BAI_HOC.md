# Bài học từ sổ cái MT5 (learning loop)

Lúc: 2026-10-30 22:23 (Asia/Bangkok, UTC+7).

Nguồn: `so_cai*.jsonl` (máy nhà + box). Pass = lãi sau phí, DD ≤ 80 %, ≥ 10 %/năm.

## Tóm tắt

- Dòng ledger unique: **1072**
- PASS: **864** (80.6 %)
- Priors máy: `data/bai_hoc.json` (tools/vong2.py đọc `trong_so`).
- Thẻ `nhan.bai_hoc`: 5 thẻ ghi từ vòng học này.

## Key lessons

- **[huong_dang_mo]** Gia dinh MT5 dang an (so_cai) — khac pass=629 rate=94%; skea pass=105 rate=85%; mql5 pass=73 rate=81%; ghep pass=19 rate=95%; tohop pass=17 rate=90%
- **[su_that_tai_san]** Khung thoi gian manh nhat — H4 pass=143 fail=8 rate=95% apy_tb=59.88
- **[huong_dang_mo]** Kieu vao (InpVao) dang an — unknown p=589 f=40; CSV_lenh p=273 f=43
- **[su_that_tai_san]** Cap co nhieu PASS — GBPUSD pass=269 rate=98%; AUDUSD pass=87 rate=99%; EURJPY pass=80 rate=100%; EURGBP pass=72 rate=96%; GER40CASH pass=70 rate=81%; AUDCAD pass=54 rate=90%
- **[bay_do_luong]** Suat PASS so_cai (muc tieu 1000/ngay → ≥5 ung vien) — n=1072 pass=864 ti_le=0.806

## Gia đình EA

| key | n | pass | fail | rate | net_tb | dd_tb | apy_tb | w |
|---|---|---|---|---|---|---|---|---|
| khac | 677 | 629 | 40 | 94% | 230.83 | 3.39 | 44.37 | 17 |
| skea | 158 | 105 | 18 | 85% | 2032.96 | 38.77 | 71.68 | 17 |
| mql5 | 136 | 73 | 17 | 81% | 1074.96 | 33.23 | 33.14 | 15 |
| ghep | 20 | 19 | 1 | 95% | 5687.25 | 40.29 | 205.84 | 17 |
| tohop | 26 | 17 | 2 | 90% | 928.96 | 30.15 | 21.2 | 15 |
| skst | 40 | 15 | 5 | 75% | 3273.56 | 44.01 | 250.07 | 17 |
| brainxlmrz | 6 | 2 | 0 | 100% | 9306.4 | 38.09 | 86.58 | — |
| v2cn | 2 | 2 | 0 | 100% | 1653.57 | 49.55 | 59.8 | — |
| v2tf | 2 | 2 | 0 | 100% | 716.04 | 49.86 | 25.89 | — |
| brainxlrsi | 5 | 0 | 2 | 0% | None | None | None | — |

## Khung

| key | n | pass | fail | rate | net_tb | dd_tb | apy_tb | w |
|---|---|---|---|---|---|---|---|---|
| D1 | 633 | 587 | 40 | 94% | 163.15 | 1.1 | None | 15 |
| H4 | 194 | 143 | 8 | 95% | 1704.19 | 37.26 | 59.88 | 17 |
| H1 | 245 | 134 | 37 | 78% | 2193.74 | 36.32 | 86.0 | 17 |

## Cặp

| key | n | pass | fail | rate | net_tb | dd_tb | apy_tb | w |
|---|---|---|---|---|---|---|---|---|
| GBPUSD | 275 | 269 | 4 | 98% | 168.1 | 3.19 | 26.87 | 15 |
| AUDUSD | 88 | 87 | 1 | 99% | 244.65 | 3.93 | 39.94 | 15 |
| EURJPY | 80 | 80 | 0 | 100% | 162.6 | 0.71 | None | 15 |
| EURGBP | 95 | 72 | 3 | 96% | 932.35 | 29.92 | 44.0 | 17 |
| GER40CASH | 86 | 70 | 16 | 81% | 352.71 | 3.08 | None | 15 |
| AUDCAD | 75 | 54 | 6 | 90% | 526.46 | 2.37 | 86.58 | 17 |
| GBPNZD | 40 | 38 | 0 | 100% | 1687.92 | 32.31 | 55.24 | 17 |
| EURUSD | 60 | 35 | 5 | 88% | 1796.19 | 32.32 | 146.32 | 17 |
| GBPCAD | 51 | 31 | 7 | 82% | 5385.26 | 34.6 | 198.9 | 17 |
| EURCAD | 33 | 16 | 7 | 70% | 1328.45 | 19.73 | 68.42 | 17 |
| GBPJPY | 15 | 15 | 0 | 100% | 345.68 | 5.75 | 23.71 | 15 |
| USDCAD | 16 | 13 | 1 | 93% | 2306.24 | 43.55 | 91.93 | 17 |
| AUDNZD | 14 | 12 | 0 | 100% | 711.38 | 22.61 | 25.96 | 15 |
| XAUUSD | 23 | 10 | 4 | 71% | 1805.15 | 46.77 | 62.78 | 17 |
| EURCHF | 14 | 9 | 2 | 82% | 1401.45 | 38.81 | 52.46 | 17 |

## Kiểu vào

| key | n | pass | fail | rate | net_tb | dd_tb | apy_tb | w |
|---|---|---|---|---|---|---|---|---|
| unknown | 635 | 589 | 40 | 94% | 165.02 | 1.12 | 38.45 | 15 |
| CSV_lenh | 426 | 273 | 43 | 86% | 1896.05 | 37.02 | 72.68 | 17 |
| MRZ | 6 | 2 | 0 | 100% | 9306.4 | 38.09 | 86.58 | — |
| RSI | 5 | 0 | 2 | 0% | None | None | None | — |

## TP bucket

| key | n | pass | fail | rate | net_tb | dd_tb | apy_tb | w |
|---|---|---|---|---|---|---|---|---|
| tp_none | 635 | 589 | 40 | 94% | 165.02 | 1.12 | 38.45 | 15 |
| tp_pct_0.3-0.6% | 288 | 183 | 36 | 84% | 1888.57 | 35.41 | 71.36 | 17 |
| tp_pct_<0.3% | 138 | 90 | 7 | 93% | 1911.28 | 40.3 | 75.41 | 17 |
| tpg_<0.0050 | 11 | 2 | 2 | 50% | 9306.4 | 38.09 | 86.58 | — |

## Bước DCA

| key | n | pass | fail | rate | net_tb | dd_tb | apy_tb | w |
|---|---|---|---|---|---|---|---|---|
| buoc_gia_or_none | 730 | 646 | 52 | 93% | 271.26 | 3.95 | 41.03 | 17 |
| buoc_0.5-1% | 207 | 130 | 18 | 88% | 1662.9 | 38.75 | 66.08 | 17 |
| buoc_>=1% | 70 | 49 | 11 | 82% | 1921.92 | 36.23 | 70.49 | 17 |
| buoc_<0.5% | 65 | 39 | 4 | 91% | 3790.87 | 37.77 | 144.05 | 17 |

## Cách feed-back

1. `tools/vong2.py` — `nap_priors()` cộng điểm family/tf/ma khi xếp PASS.
2. `nhan.bai_hoc.tra` — NGHI/uu_tien hỏi trước khi đào hướng mới.
3. Chạy lại sau mỗi phiên MT5: `python tools/hoc_tu_so_cai.py`.
