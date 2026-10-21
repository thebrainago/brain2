# Vòng 2 — kết quả (tự sinh bởi `python -m nhan.vong2`)

Lúc chạy: 2026-10-20 22:17 (giờ box, UTC+7). Ngưỡng tầng: xem `tai_lieu/VONG_2.md`.

**Nhãn:** cột MT5 = ĐO THẬT (lệnh real tick vòng 1); equity *tái dựng* từ lệnh + giá H1 của chính lần chạy MT5; stress phí, Monte Carlo, Python = **MÔ PHỎNG**.

## 1. Kiểm tra chặt trên lệnh MT5 thật

| id | Symbol | TF | Năm | Lệnh | Lãi kép BC % | Lãi kép tái dựng % | Lãi kép stress % (MÔ PHỎNG) | DD BC % | DD equity tái dựng % | DD lệnh đóng % | DD stress % | MC DD equity p95 % (stress, MÔ PHỎNG) | WF 3 đoạn %/năm | Py/MT5 | Tầng |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| od_skea8897567020_XM_CSV | GBPNZDmicro | H1 | 2.76 | 154 | 37.3 | 37.3 | 33.0 | 45.6 | 43.6 | 10.0 | 45.8 | 80.7 | 49 / 51 / 17 | 1.24 | B |
| od_mql5a790e25e547f0b57_XM_CSV | AUDNZDmicro | H4 | 2.74 | 31 | 17.5 | 17.5 | 16.2 | 20.9 | 19.6 | 1.5 | 19.9 | 40.7 | 12 / 17 / 22 | 0.99 | B |
| od_skea44640140cc_XM_CSV | GBPCADmicro | H1 | 2.76 | 616 | 138.6 | 138.8 | 130.9 | 45.8 | 43.6 | 0.0 | 45.9 | 66.4 | 396 / 86 / 51 | 1.03 | C |
| od_tohop16b0d75bb149f634_XM_CSV | GBPCADmicro | H1 | 2.76 | 127 | 92.2 | 92.3 | 88.4 | 55.9 | 55.2 | 0.0 | 57.7 | 77.7 | 120 / 79 / 78 | 0.97 | C |
| od_skea0075f624b3_XM_CSV | GBPNZDmicro | H1 | 2.74 | 139 | 91.2 | 91.4 | 86.6 | 52.8 | 50.1 | 0.0 | 52.6 | 84.4 | 175 / 74 / 48 | 1.02 | C |
| od_skea0ca971ac32_XM_CSV | GBPNZDmicro | H4 | 2.76 | 27 | 85.9 | 86.0 | 83.3 | 50.6 | 45.7 | 1.0 | 46.6 | 81.8 | 210 / 70 / 22 | 1.13 | C |
| od_skstadd3a54f8edcbce2_XM_CSV | EURUSDmicro | H1 | 1.34 | 15 | 70.3 | 70.5 | 65.6 | 60.8 | 62.8 | 0.0 | 64.2 | 65.5 | 50 / 119 / 47 | 1.05 | C |
| od_mql5f3313c2c79f00c10_XM_CSV | EURGBPmicro | H4 | 2.74 | 178 | 66.1 | 66.2 | 60.5 | 50.6 | 52.5 | 6.4 | 57.8 | 78.5 | 170 / -28 / 120 | 1.03 | C |
| od_skeaa7cd39087e_XM_CSV | GOLDmicro | H1 | 2.76 | 351 | 60.0 | 60.0 | 53.5 | 60.6 | 55.6 | 56.8 | 58.5 | 85.4 | 71 / 232 / -29 | 0.69 | C |
| od_skeaff87f96be7_XM_CSV | GBPCADmicro | H1 | 2.75 | 211 | 53.3 | 53.4 | 50.5 | 31.7 | 40.9 | 9.6 | 42.5 | 58.3 | 62 / 52 / 46 | 1.05 | C |
| od_skea3279057100_XM_CSV | EURGBPmicro | H1 | 2.76 | 203 | 44.7 | 44.8 | 31.0 | 64.0 | 63.4 | 36.3 | 76.3 | 93.7 | 147 / -11 / 44 | -0.57 | C |
| od_b0be91a35f43f34a_XM_CSV | USDCADmicro | H4 | 2.71 | 46 | 44.0 | 44.0 | 39.6 | 58.6 | 57.2 | 0.0 | 61.8 | 88.7 | 82 / 25 / 31 | 0.95 | C |
| od_skea02906b7d6a_XM_CSV | GOLDmicro | H4 | 2.76 | 180 | 39.2 | 39.3 | 35.1 | 70.3 | 65.0 | 64.5 | 66.9 | 89.2 | 92 / 115 / -39 | 0.13 | C |
| od_skstc21c2acd239f3c87_XM_CSV | EURUSDmicro | H1 | 1.34 | 20 | 37.0 | 37.1 | 34.4 | 49.7 | 46.3 | 0.0 | 46.9 | 47.7 | 22 / 70 / 23 | 1.01 | C |
| od_skea5049c79288_XM_CSV | GBPCADmicro | H4 | 2.71 | 83 | 34.8 | 34.8 | 33.2 | 30.4 | 30.0 | 9.9 | 31.0 | 53.3 | 63 / 11 / 35 | 1.15 | C |
| od_mql5fd4bc285e11ab5a1_XM_CSV | EURCHFmicro | H4 | 2.76 | 138 | 31.0 | 31.0 | 28.8 | 49.3 | 46.5 | 20.1 | 47.5 | 64.0 | 57 / 42 / -0 | 0.76 | C |
| od_mql5e3c3e4f028dbab72_XM_CSV | EURCADmicro | H4 | 2.76 | 120 | 29.0 | 29.1 | 27.6 | 18.4 | 18.0 | 1.5 | 18.3 | 25.2 | 47 / 19 / 23 | 1.07 | C |
| od_mql5e31426a40a5897fc_XM_CSV | GBPUSDmicro | H4 | 2.59 | 15 | 28.7 | 28.7 | 28.0 | 58.7 | 55.9 | 0.0 | 56.4 | 63.6 | 40 / 17 / 30 | 1.00 | C |
| od_mql5ad7d22b5b165a673_XM_CSV | GBPUSDmicro | H4 | 2.76 | 134 | 27.2 | 27.2 | 25.1 | 55.0 | 53.6 | 10.1 | 55.0 | 74.4 | 28 / 37 / 17 | 0.72 | C |
| od_skeafdbf5bcad6_XM_CSV | EURCADmicro | H1 | 2.76 | 190 | 26.4 | 26.5 | 17.8 | 18.2 | 18.9 | 29.8 | 20.9 | 50.5 | 45 / 64 / -12 | 0.91 | C |
| od_mql5d8f573b8c2314bbf_XM_CSV | EURAUDmicro | H1 | 2.76 | 106 | 24.4 | 24.5 | 19.5 | 41.4 | 47.1 | 41.7 | 49.2 | 58.6 | 82 / 43 / -26 | 1.28 | C |
| od_skea0806a3a5e5_XM_CSV | AUDNZDmicro | H1 | 2.76 | 29 | 24.4 | 24.4 | 23.3 | 25.9 | 24.6 | 4.5 | 25.0 | 44.0 | 19 / 14 / 41 | 0.95 | C |
| od_skstaca366b679c75482_XM_CSV | EURUSDmicro | H1 | 1.34 | 15 | 24.4 | 24.4 | 22.6 | 18.2 | 18.3 | 0.0 | 18.4 | 21.0 | 15 / 27 / 33 | 0.96 | C |
| od_skea0cc19095a9_XM_CSV | GBPNZDmicro | H1 | 2.76 | 429 | 24.3 | 24.3 | 20.8 | 28.9 | 27.5 | 3.9 | 28.7 | 39.6 | 23 / 33 / 18 | 0.85 | C |
| od_skeaaba30a4e06_XM_CSV | USDJPYmicro | H4 | 2.76 | 164 | 21.9 | 21.9 | 20.2 | 49.7 | 48.1 | 5.6 | 48.4 | 57.4 | 39 / 17 / 12 | 0.89 | C |
| od_nhapcf8073245473d2a1_XM_CSV | EURGBPmicro | H4 | 2.76 | 188 | 20.8 | 20.8 | 17.8 | 67.8 | 78.2 | 18.1 | 81.9 | 92.1 | 16 / -22 / 114 | 1.34 | C |
| od_mql5b39a9f3ba216fb47_XM_CSV | CHFJPYmicro | H1 | 2.76 | 392 | 19.6 | 19.6 | 18.2 | 27.1 | 28.6 | 16.4 | 29.7 | 40.1 | 27 / 22 / 11 | 0.86 | C |
| od_mql525573694a7f03d3a_XM_CSV | EURGBPmicro | H1 | 2.76 | 282 | 19.5 | 19.5 | 17.4 | 31.5 | 33.4 | 1.6 | 35.2 | 49.0 | 20 / -13 / 61 | — | C |
| od_skea0ab4d307d3_XM_CSV | EURNZDmicro | H1 | 2.76 | 286 | 17.4 | 17.5 | 14.0 | 48.6 | 38.8 | 7.7 | 40.3 | 62.7 | 23 / 23 / 7 | 0.74 | C |
| od_tohop09a3b2ddc3e78dc8_XM_CSV | EURUSDmicro | H4 | 2.76 | 69 | 15.6 | 15.6 | 14.5 | 32.0 | 31.6 | 15.2 | 32.4 | 44.5 | 22 / 8 / 18 | 1.41 | C |
| od_3304d2fad28adef6_XM_CSV | USDCADmicro | H4 | 2.59 | 64 | 14.2 | 14.2 | 9.1 | 40.2 | 47.3 | 23.6 | 51.5 | 60.4 | 19 / 26 / -1 | 1.86 | C |
| od_018dcb1347276c97_XM_CSV | EURNZDmicro | H4 | 2.72 | 76 | 12.1 | 12.1 | 10.8 | 18.4 | 14.8 | 3.2 | 15.0 | 28.8 | 8 / 22 / 7 | 0.96 | C |
| od_skea0757c93eb3_XM_CSV | EURNZDmicro | H4 | 2.76 | 2 | 10.6 | 10.6 | 10.2 | 29.2 | 17.4 | 0.0 | 17.4 | 18.3 | 35 / 0 / -0 | 0.91 | C |

Lí do chưa lên tầng (rút gọn):

- `od_skea44640140cc_XM_CSV` (C): thiếu A: đa cặp 12 < 50% — thiếu B: đa cặp 12 < 30%
- `od_tohop16b0d75bb149f634_XM_CSV` (C): thiếu A: đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea0075f624b3_XM_CSV` (C): thiếu A: MC DD p95 84.37 > 80%; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea0ca971ac32_XM_CSV` (C): thiếu A: MC DD p95 81.83 > 80%; lệnh 27 < 100; đa cặp None < 50%; OOS Python None < 10% — thiếu B: lệnh 27 < 30; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skstadd3a54f8edcbce2_XM_CSV` (C): thiếu A: lịch sử MT5 1.3 < 2.5 năm; DD equity stress 64.2 > 60%; lệnh 15 < 100; đa cặp None < 50% — thiếu B: lịch sử MT5 1.3 < 2.0 năm; lệnh 15 < 30; đa cặp None < 30%
- `od_mql5f3313c2c79f00c10_XM_CSV` (C): thiếu A: đoạn WF tệ nhất -27.65 < 5%; đa cặp 4 < 50%; cao nguyên 0.33 < 0.6 — thiếu B: đoạn WF tệ nhất -27.65 < 0%; đa cặp 4 < 30%; cao nguyên 0.33 < 0.4
- `od_skeaa7cd39087e_XM_CSV` (C): thiếu A: MC DD p95 85.38 > 80%; đoạn WF tệ nhất -29.39 < 5%; Python/MT5 0.69 ngoài 0.8–1.25; đa cặp None < 50% — thiếu B: đoạn WF tệ nhất -29.39 < 0%; Python/MT5 0.69 ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%
- `od_skeaff87f96be7_XM_CSV` (C): thiếu A: đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea3279057100_XM_CSV` (C): thiếu A: DD equity stress 76.3 > 60%; MC DD p95 93.66 > 80%; đoạn WF tệ nhất -10.63 < 5%; Python/MT5 -0.57 ngoài 0.8–1.25 — thiếu B: đoạn WF tệ nhất -10.63 < 0%; Python/MT5 -0.57 ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%
- `od_b0be91a35f43f34a_XM_CSV` (C): thiếu A: DD equity stress 61.8 > 60%; MC DD p95 88.74 > 80%; lệnh 46 < 100; đa cặp None < 50% — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea02906b7d6a_XM_CSV` (C): thiếu A: DD equity stress 66.9 > 60%; MC DD p95 89.22 > 80%; đoạn WF tệ nhất -38.61 < 5%; Python/MT5 0.13 ngoài 0.8–1.25 — thiếu B: đoạn WF tệ nhất -38.61 < 0%; Python/MT5 0.13 ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%
- `od_skea8897567020_XM_CSV` (B): thiếu A: MC DD p95 80.66 > 80%; đa cặp 36 < 50%
- `od_skstc21c2acd239f3c87_XM_CSV` (C): thiếu A: lịch sử MT5 1.3 < 2.5 năm; lệnh 20 < 100; đa cặp None < 50% — thiếu B: lịch sử MT5 1.3 < 2.0 năm; lệnh 20 < 30; đa cặp None < 30%
- `od_skea5049c79288_XM_CSV` (C): thiếu A: lệnh 83 < 100; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_mql5fd4bc285e11ab5a1_XM_CSV` (C): thiếu A: đoạn WF tệ nhất -0.03 < 5%; Python/MT5 0.76 ngoài 0.8–1.25; đa cặp 12 < 50%; OOS Python 8.84 < 10% — thiếu B: đoạn WF tệ nhất -0.03 < 0%; đa cặp 12 < 30%
- `od_mql5e3c3e4f028dbab72_XM_CSV` (C): thiếu A: đa cặp 20 < 50%; cao nguyên 0.11 < 0.6 — thiếu B: đa cặp 20 < 30%; cao nguyên 0.11 < 0.4
- `od_mql5e31426a40a5897fc_XM_CSV` (C): thiếu A: lệnh 15 < 100; đa cặp 20 < 50% — thiếu B: lệnh 15 < 30; đa cặp 20 < 30%
- `od_mql5ad7d22b5b165a673_XM_CSV` (C): thiếu A: Python/MT5 0.72 ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skeafdbf5bcad6_XM_CSV` (C): thiếu A: đoạn WF tệ nhất -11.79 < 5%; đa cặp 4 < 50%; OOS Python -7.71 < 10% — thiếu B: đoạn WF tệ nhất -11.79 < 0%; đa cặp 4 < 30%; OOS Python -7.71 < 0%
- `od_mql5d8f573b8c2314bbf_XM_CSV` (C): thiếu A: đoạn WF tệ nhất -26.48 < 5%; Python/MT5 1.28 ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: đoạn WF tệ nhất -26.48 < 0%; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea0806a3a5e5_XM_CSV` (C): thiếu A: lệnh 29 < 100; đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: lệnh 29 < 30; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skstaca366b679c75482_XM_CSV` (C): thiếu A: lịch sử MT5 1.3 < 2.5 năm; lệnh 15 < 100; đa cặp None < 50% — thiếu B: lịch sử MT5 1.3 < 2.0 năm; lệnh 15 < 30; đa cặp None < 30%
- `od_skea0cc19095a9_XM_CSV` (C): thiếu A: đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skeaaba30a4e06_XM_CSV` (C): thiếu A: đa cặp None < 50%; OOS Python None < 10%; cao nguyên None < 0.6 — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_nhapcf8073245473d2a1_XM_CSV` (C): thiếu A: DD equity stress 81.9 > 60%; MC DD p95 92.06 > 80%; đoạn WF tệ nhất -22.26 < 5%; Python/MT5 1.34 ngoài 0.8–1.25 — thiếu B: DD equity stress 81.9 > 80%; đoạn WF tệ nhất -22.26 < 0%; đa cặp None < 30%; OOS Python None < 0%
- `od_mql5b39a9f3ba216fb47_XM_CSV` (C): thiếu A: cao nguyên 0.11 < 0.6 — thiếu B: cao nguyên 0.11 < 0.4
- `od_mql525573694a7f03d3a_XM_CSV` (C): thiếu A: đoạn WF tệ nhất -12.65 < 5%; Python/MT5 None ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: đoạn WF tệ nhất -12.65 < 0%; Python/MT5 None ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%
- `od_mql5a790e25e547f0b57_XM_CSV` (B): thiếu A: lệnh 31 < 100
- `od_skea0ab4d307d3_XM_CSV` (C): thiếu A: lãi kép sau stress 14.0 < 15%; Python/MT5 0.74 ngoài 0.8–1.25; đa cặp None < 50%; OOS Python None < 10% — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_tohop09a3b2ddc3e78dc8_XM_CSV` (C): thiếu A: lãi kép sau stress 14.5 < 15%; lệnh 69 < 100; Python/MT5 1.41 ngoài 0.8–1.25; đa cặp None < 50% — thiếu B: Python/MT5 1.41 ngoài 0.7–1.4; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_3304d2fad28adef6_XM_CSV` (C): thiếu A: lãi kép sau stress 9.1 < 15%; đoạn WF tệ nhất -0.75 < 5%; lệnh 64 < 100; Python/MT5 1.86 ngoài 0.8–1.25 — thiếu B: lãi kép sau stress 9.1 < 10%; đoạn WF tệ nhất -0.75 < 0%; Python/MT5 1.86 ngoài 0.7–1.4; đa cặp None < 30%
- `od_018dcb1347276c97_XM_CSV` (C): thiếu A: lãi kép sau stress 10.8 < 15%; lệnh 76 < 100; đa cặp None < 50%; OOS Python None < 10% — thiếu B: đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4
- `od_skea0757c93eb3_XM_CSV` (C): thiếu A: lãi kép sau stress 10.2 < 15%; đoạn WF tệ nhất 0.0 < 5%; lệnh 2 < 100; đa cặp None < 50% — thiếu B: lệnh 2 < 30; đa cặp None < 30%; OOS Python None < 0%; cao nguyên None < 0.4

## 2. Python (MÔ PHỎNG): mặc định tác giả, khung, đa cặp, lưới + cao nguyên

| id | Gốc %/năm | Gốc DD % | OOS 30% %/năm | Mặc định tác giả %/năm | Khung khác | Cặp khác không lỗ | Cao nguyên gốc | Tốt nhất (cao nguyên) | Phép thử | Giây |
|---|---|---|---|---|---|---|---|---|---|---|
| od_tohop16b0d75bb149f634_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea0075f624b3_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea0ca971ac32_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skeaa7cd39087e_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skeaff87f96be7_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea3279057100_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_b0be91a35f43f34a_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea02906b7d6a_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea5049c79288_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea0806a3a5e5_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea0cc19095a9_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skeaaba30a4e06_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea0ab4d307d3_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_3304d2fad28adef6_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_018dcb1347276c97_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea0757c93eb3_XM_CSV | CHƯA ĐO ĐƯỢC trên box: thẻ chưa có tín hiệu đã dịch / phép thử trong cache box (bản dịch ở máy nhà, không gọi LLM) |||||||||
| od_skea44640140cc_XM_CSV | 139.2 | 46.3 | 59.5 | 139.2 | H4 133/54, H1 139/46 | 12% (25 cặp) | 0.80 | 171.3%/năm, DD 51.1%, OOS 72.0, CN 1.0 | 118 | 36 |
| od_mql5e3c3e4f028dbab72_XM_CSV | 31.0 | 18.3 | 25.2 | 31.0 | H1 -24/91, H4 31/18 | 20% (25 cặp) | 0.11 | 41.7%/năm, DD 33.0%, OOS 28.4, CN 1.0 | 118 | 9 |
| od_skstaca366b679c75482_XM_CSV | 23.9 | 18.4 | 53.1 | 23.9 | H4 -38/96, H1 24/18 | — | 0.67 | 85.3%/năm, DD 66.1%, OOS 104.8, CN 1.0 | 93 | 4 |
| od_mql5f3313c2c79f00c10_XM_CSV | 59.4 | 56.3 | 72.5 | 59.4 | H1 -100/103, H4 59/56 | 4% (25 cặp) | 0.33 | 63.2%/năm, DD 49.8%, OOS 57.2, CN 1.0 | 118 | 11 |
| od_skstadd3a54f8edcbce2_XM_CSV | 73.9 | 63.6 | 186.2 | 73.9 | H4 -100/129, H1 74/64 | — | 0.57 | 63.3%/năm, DD 44.7%, OOS 175.9, CN 1.0 | 93 | 3 |
| od_skeafdbf5bcad6_XM_CSV | 23.0 | 18.7 | -7.7 | 23.0 | H4 10/33, H1 23/19 | 4% (25 cặp) | 1.00 | 95.1%/năm, DD 27.5%, OOS 33.8, CN 1.0 | 118 | 31 |
| od_mql5a790e25e547f0b57_XM_CSV | 17.3 | 19.6 | 20.0 | 17.3 | H1 25/23, H4 17/20 | 56% (25 cặp) | 0.89 | 25.8%/năm, DD 21.0%, OOS 41.2, CN 1.0 | 118 | 7 |
| od_skstc21c2acd239f3c87_XM_CSV | 41.3 | 52.9 | 91.5 | 41.3 | H4 -100/125, H1 41/53 | — | 0.75 | 94.5%/năm, DD 63.9%, OOS 145.0, CN 1.0 | 93 | 4 |
| od_skea8897567020_XM_CSV | 46.1 | 48.6 | 20.7 | 46.1 | H4 49/34, H1 46/49 | 36% (25 cặp) | 1.00 | 59.4%/năm, DD 39.9%, OOS 37.9, CN 1.0 | 118 | 36 |
| od_mql5b39a9f3ba216fb47_XM_CSV | 18.6 | 46.5 | 16.1 | 18.6 | H4 -5/81, H1 19/46 | 56% (25 cặp) | 0.11 | không có điểm qua chống quá khớp | 118 | 28 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | 30.8 | 50.0 | 8.8 | 30.8 | H1 -100/100, H4 31/50 | 12% (25 cặp) | 0.57 | 33.8%/năm, DD 53.0%, OOS 17.1, CN 1.0 | 118 | 12 |
| od_mql5e31426a40a5897fc_XM_CSV | 26.5 | 59.0 | 35.4 | 26.5 | H1 -16/75, H4 27/59 | 20% (25 cặp) | 0.71 | 14.8%/năm, DD 17.8%, OOS 14.4, CN 1.0 | 118 | 5 |

## 3. Ghép cùng cặp (MÔ PHỎNG)

| Gốc | B | Phong cách B | Kiểu | %/năm | DD % | OOS %/năm | Lệnh | Gốc %/năm / DD % |
|---|---|---|---|---|---|---|---|---|
| od_skea44640140cc_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 87.8 | 74.7 | 128.0 | 300 | 139.2 / 46.3 |
| od_skea44640140cc_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | 125.3 | 84.8 | 2.9 | 1599 | 139.2 / 46.3 |
| od_skea44640140cc_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 117.2 | 91.4 | 3.7 | 1160 | 139.2 / 46.3 |
| od_skea44640140cc_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 139.2 | 46.3 | 59.5 | 625 | 139.2 / 46.3 |
| od_skea44640140cc_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | 202.3 | 76.2 | 63.9 | 1250 | 139.2 / 46.3 |
| od_skea44640140cc_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | 139.2 | 46.3 | 59.5 | 625 | 139.2 / 46.3 |
| od_skea44640140cc_XM_CSV | mql5_e3c3e4f028dbab72 | trend | xac_nhan | 66.8 | 96.5 | 19.8 | 196 | 139.2 / 46.3 |
| od_skea44640140cc_XM_CSV | mql5_e3c3e4f028dbab72 | trend | them_lenh | 144.3 | 49.2 | 70.1 | 1073 | 139.2 / 46.3 |
| od_skea44640140cc_XM_CSV | mql5_e3c3e4f028dbab72 | trend | nguoc | -100.0 | 101.3 | — | 33 | 139.2 / 46.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | sk_ea_fdbf5bcad6 | basket,breakout,mean_reversion,trend | xac_nhan | 14.9 | 10.9 | 16.8 | 51 | 31.0 / 18.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | sk_ea_fdbf5bcad6 | basket,breakout,mean_reversion,trend | them_lenh | 36.3 | 33.2 | 52.8 | 479 | 31.0 / 18.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | sk_ea_fdbf5bcad6 | basket,breakout,mean_reversion,trend | nguoc | 16.6 | 66.8 | 48.0 | 330 | 31.0 / 18.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 14.3 | 22.1 | 22.2 | 50 | 31.0 / 18.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | 54.8 | 38.1 | 3.9 | 395 | 31.0 / 18.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 56.7 | 34.6 | 29.0 | 323 | 31.0 / 18.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 1.4 | 1.5 | 1.1 | 4 | 31.0 / 18.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | 10.3 | 71.8 | 28.7 | 308 | 31.0 / 18.3 |
| od_mql5e3c3e4f028dbab72_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 5.9 | 89.6 | 88.8 | 250 | 31.0 / 18.3 |
| od_skstaca366b679c75482_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 5.7 | 17.8 | 8.6 | 8 | 23.9 / 18.4 |
| od_skstaca366b679c75482_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | -90.7 | 99.9 | 0.0 | 8 | 23.9 / 18.4 |
| od_skstaca366b679c75482_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 23.9 | 26.9 | -8.1 | 77 | 23.9 / 18.4 |
| od_skstaca366b679c75482_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 0.0 | 0.0 | 0.0 | 0 | 23.9 / 18.4 |
| od_skstaca366b679c75482_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | 0.9 | 59.0 | 5.5 | 98 | 23.9 / 18.4 |
| od_skstaca366b679c75482_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 24.7 | 33.2 | 19.0 | 72 | 23.9 / 18.4 |
| od_skstaca366b679c75482_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 5.7 | 17.8 | 8.6 | 8 | 23.9 / 18.4 |
| od_skstaca366b679c75482_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | -90.7 | 99.9 | 0.0 | 8 | 23.9 / 18.4 |
| od_skstaca366b679c75482_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | 23.9 | 26.9 | -8.1 | 77 | 23.9 / 18.4 |
| od_mql5f3313c2c79f00c10_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 24.7 | 84.3 | -10.7 | 105 | 59.4 / 56.3 |
| od_mql5f3313c2c79f00c10_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | -100.0 | 103.7 | — | 43 | 59.4 / 56.3 |
| od_mql5f3313c2c79f00c10_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | -100.0 | 102.0 | — | 60 | 59.4 / 56.3 |
| od_mql5f3313c2c79f00c10_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 24.7 | 84.3 | -10.7 | 105 | 59.4 / 56.3 |
| od_mql5f3313c2c79f00c10_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | -100.0 | 103.7 | — | 43 | 59.4 / 56.3 |
| od_mql5f3313c2c79f00c10_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | -100.0 | 102.0 | — | 60 | 59.4 / 56.3 |
| od_mql5f3313c2c79f00c10_XM_CSV | mql5_e3c3e4f028dbab72 | trend | xac_nhan | 0.0 | 0.0 | 0.0 | 0 | 59.4 / 56.3 |
| od_mql5f3313c2c79f00c10_XM_CSV | mql5_e3c3e4f028dbab72 | trend | them_lenh | 81.8 | 32.6 | 61.3 | 277 | 59.4 / 56.3 |
| od_mql5f3313c2c79f00c10_XM_CSV | mql5_e3c3e4f028dbab72 | trend | nguoc | 77.3 | 35.4 | 63.1 | 246 | 59.4 / 56.3 |
| od_skstadd3a54f8edcbce2_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 16.0 | 59.9 | 23.1 | 8 | 73.9 / 63.6 |
| od_skstadd3a54f8edcbce2_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | -100.0 | 105.4 | — | 12 | 73.9 / 63.6 |
| od_skstadd3a54f8edcbce2_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 75.8 | 87.1 | -37.1 | 146 | 73.9 / 63.6 |
| od_skstadd3a54f8edcbce2_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 0.0 | 0.0 | 0.0 | 0 | 73.9 / 63.6 |
| od_skstadd3a54f8edcbce2_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | -100.0 | 100.1 | — | 79 | 73.9 / 63.6 |
| od_skstadd3a54f8edcbce2_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 70.8 | 60.2 | -17.8 | 126 | 73.9 / 63.6 |
| od_skstadd3a54f8edcbce2_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 16.0 | 59.9 | 23.1 | 8 | 73.9 / 63.6 |
| od_skstadd3a54f8edcbce2_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | -100.0 | 105.4 | — | 12 | 73.9 / 63.6 |
| od_skstadd3a54f8edcbce2_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | 75.8 | 87.1 | -37.1 | 146 | 73.9 / 63.6 |
| od_skeafdbf5bcad6_XM_CSV | mql5_e3c3e4f028dbab72 | trend | xac_nhan | -15.9 | 61.6 | -6.9 | 16 | 23.0 / 18.7 |
| od_skeafdbf5bcad6_XM_CSV | mql5_e3c3e4f028dbab72 | trend | them_lenh | 5.1 | 47.2 | -25.7 | 285 | 23.0 / 18.7 |
| od_skeafdbf5bcad6_XM_CSV | mql5_e3c3e4f028dbab72 | trend | nguoc | 28.2 | 40.4 | -8.1 | 254 | 23.0 / 18.7 |
| od_skeafdbf5bcad6_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 30.7 | 21.6 | -3.2 | 142 | 23.0 / 18.7 |
| od_skeafdbf5bcad6_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | 27.4 | 43.7 | -17.7 | 290 | 23.0 / 18.7 |
| od_skeafdbf5bcad6_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 31.5 | 39.9 | -10.8 | 274 | 23.0 / 18.7 |
| od_skeafdbf5bcad6_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 11.1 | 30.3 | 9.9 | 40 | 23.0 / 18.7 |
| od_skeafdbf5bcad6_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | 5.9 | 52.0 | -30.3 | 329 | 23.0 / 18.7 |
| od_skeafdbf5bcad6_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 5.9 | 44.2 | -22.7 | 293 | 23.0 / 18.7 |
| od_mql5a790e25e547f0b57_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 16.3 | 17.2 | 20.5 | 28 | 17.3 / 19.6 |
| od_mql5a790e25e547f0b57_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | 38.3 | 36.7 | 57.0 | 93 | 17.3 / 19.6 |
| od_mql5a790e25e547f0b57_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 17.3 | 19.6 | 20.0 | 30 | 17.3 / 19.6 |
| od_mql5a790e25e547f0b57_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 6.3 | 12.6 | 4.3 | 10 | 17.3 / 19.6 |
| od_mql5a790e25e547f0b57_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | -49.0 | 91.0 | -79.0 | 74 | 17.3 / 19.6 |
| od_mql5a790e25e547f0b57_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | -100.0 | 100.4 | — | 26 | 17.3 / 19.6 |
| od_mql5a790e25e547f0b57_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 16.3 | 17.2 | 20.5 | 28 | 17.3 / 19.6 |
| od_mql5a790e25e547f0b57_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | 38.3 | 36.7 | 57.0 | 93 | 17.3 / 19.6 |
| od_mql5a790e25e547f0b57_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | 17.3 | 19.6 | 20.0 | 30 | 17.3 / 19.6 |
| od_skstc21c2acd239f3c87_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 9.0 | 46.1 | 16.4 | 11 | 41.3 / 52.9 |
| od_skstc21c2acd239f3c87_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | -100.0 | 104.6 | — | 36 | 41.3 / 52.9 |
| od_skstc21c2acd239f3c87_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 52.4 | 58.7 | -48.5 | 266 | 41.3 / 52.9 |
| od_skstc21c2acd239f3c87_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 0.0 | 0.0 | 0.0 | 0 | 41.3 / 52.9 |
| od_skstc21c2acd239f3c87_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | -100.0 | 102.6 | — | 276 | 41.3 / 52.9 |
| od_skstc21c2acd239f3c87_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 16.4 | 80.6 | -64.6 | 191 | 41.3 / 52.9 |
| od_skstc21c2acd239f3c87_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 9.0 | 46.1 | 16.4 | 11 | 41.3 / 52.9 |
| od_skstc21c2acd239f3c87_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | -100.0 | 104.6 | — | 36 | 41.3 / 52.9 |
| od_skstc21c2acd239f3c87_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | 52.4 | 58.7 | -48.5 | 266 | 41.3 / 52.9 |
| od_skea8897567020_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 46.1 | 48.6 | 20.7 | 170 | 46.1 / 48.6 |
| od_skea8897567020_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | 76.0 | 61.9 | 36.7 | 316 | 46.1 / 48.6 |
| od_skea8897567020_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 46.1 | 48.6 | 20.7 | 170 | 46.1 / 48.6 |
| od_skea8897567020_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 41.8 | 37.9 | 26.4 | 136 | 46.1 / 48.6 |
| od_skea8897567020_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | -42.3 | 91.8 | -79.2 | 497 | 46.1 / 48.6 |
| od_skea8897567020_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | -100.0 | 106.6 | — | 133 | 46.1 / 48.6 |
| od_skea8897567020_XM_CSV | mql5_e3c3e4f028dbab72 | trend | xac_nhan | 30.8 | 34.6 | 20.5 | 97 | 46.1 / 48.6 |
| od_skea8897567020_XM_CSV | mql5_e3c3e4f028dbab72 | trend | them_lenh | -100.0 | 102.3 | — | 201 | 46.1 / 48.6 |
| od_skea8897567020_XM_CSV | mql5_e3c3e4f028dbab72 | trend | nguoc | -100.0 | 105.0 | — | 135 | 46.1 / 48.6 |
| od_mql5b39a9f3ba216fb47_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 18.6 | 46.5 | 16.1 | 393 | 18.6 / 46.5 |
| od_mql5b39a9f3ba216fb47_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | 27.5 | 76.9 | 24.2 | 1210 | 18.6 / 46.5 |
| od_mql5b39a9f3ba216fb47_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 18.6 | 46.5 | 16.1 | 393 | 18.6 / 46.5 |
| od_mql5b39a9f3ba216fb47_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 0.2 | 0.6 | 0.3 | 6 | 18.6 / 46.5 |
| od_mql5b39a9f3ba216fb47_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | 15.0 | 49.6 | 33.1 | 1044 | 18.6 / 46.5 |
| od_mql5b39a9f3ba216fb47_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 14.7 | 59.2 | 27.9 | 738 | 18.6 / 46.5 |
| od_mql5b39a9f3ba216fb47_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 18.6 | 46.5 | 16.1 | 393 | 18.6 / 46.5 |
| od_mql5b39a9f3ba216fb47_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | 27.5 | 76.9 | 24.2 | 1210 | 18.6 / 46.5 |
| od_mql5b39a9f3ba216fb47_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | 18.6 | 46.5 | 16.1 | 393 | 18.6 / 46.5 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 35.1 | 56.0 | 16.5 | 71 | 30.8 / 50.0 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | 35.9 | 85.2 | 6.7 | 297 | 30.8 / 50.0 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | -100.0 | 100.4 | — | 87 | 30.8 / 50.0 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 17.6 | 36.9 | -3.9 | 68 | 30.8 / 50.0 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | -100.0 | 108.5 | — | 30 | 30.8 / 50.0 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | -100.0 | 108.5 | — | 30 | 30.8 / 50.0 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | xac_nhan | 35.1 | 56.0 | 16.5 | 71 | 30.8 / 50.0 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | them_lenh | 35.9 | 85.2 | 6.7 | 297 | 30.8 / 50.0 |
| od_mql5fd4bc285e11ab5a1_XM_CSV | sk_ea_8897567020 | mean_reversion,ml_ai,news,prop_risk,scalping,session,trend | nguoc | -100.0 | 100.4 | — | 87 | 30.8 / 50.0 |
| od_mql5e31426a40a5897fc_XM_CSV | mql5_ad7d22b5b165a673 | mean_reversion | xac_nhan | 0.0 | 0.0 | 0.0 | 0 | 26.5 / 59.0 |
| od_mql5e31426a40a5897fc_XM_CSV | mql5_ad7d22b5b165a673 | mean_reversion | them_lenh | 35.4 | 66.8 | 48.8 | 47 | 26.5 / 59.0 |
| od_mql5e31426a40a5897fc_XM_CSV | mql5_ad7d22b5b165a673 | mean_reversion | nguoc | 30.2 | 81.1 | 58.9 | 37 | 26.5 / 59.0 |
| od_mql5e31426a40a5897fc_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | xac_nhan | 16.0 | 10.0 | 21.9 | 8 | 26.5 / 59.0 |
| od_mql5e31426a40a5897fc_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | them_lenh | 23.3 | 65.5 | 13.3 | 33 | 26.5 / 59.0 |
| od_mql5e31426a40a5897fc_XM_CSV | sk_ea_44640140cc | mean_reversion,ml_ai | nguoc | 37.5 | 50.9 | 38.1 | 34 | 26.5 / 59.0 |
| od_mql5e31426a40a5897fc_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | xac_nhan | 6.7 | 7.5 | 7.1 | 3 | 26.5 / 59.0 |
| od_mql5e31426a40a5897fc_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | them_lenh | 29.6 | 92.3 | 26.6 | 49 | 26.5 / 59.0 |
| od_mql5e31426a40a5897fc_XM_CSV | mql5_f3313c2c79f00c10 | mean_reversion | nguoc | 14.4 | 75.8 | 64.4 | 34 | 26.5 / 59.0 |

## 4. Danh mục từ lệnh MT5 thật, DD trên equity tái dựng theo giờ

| # | Hệ | Lãi kép %/năm | DD equity % | Tương quan ngày max | Kỳ |
|---|---|---|---|---|---|
| 1 | od_skea44640140cc_XM_CSV<br>od_skea0075f624b3_XM_CSV<br>od_mql5e3c3e4f028dbab72_XM_CSV<br>od_mql5f3313c2c79f00c10_XM_CSV | 89.5 | 22.5 | 0.24 | 2024-01-03 → 2026-09-30 |
| 2 | od_skea0ca971ac32_XM_CSV<br>od_skea44640140cc_XM_CSV<br>od_mql5e3c3e4f028dbab72_XM_CSV<br>od_mql5f3313c2c79f00c10_XM_CSV | 88.2 | 26.1 | 0.24 | 2024-01-02 → 2026-09-30 |
| 3 | od_skeaff87f96be7_XM_CSV<br>od_skea0ca971ac32_XM_CSV<br>od_mql5e3c3e4f028dbab72_XM_CSV<br>od_mql5f3313c2c79f00c10_XM_CSV | 61.2 | 22.0 | 0.21 | 2024-01-02 → 2026-09-30 |
| 4 | od_tohop16b0d75bb149f634_XM_CSV<br>od_skea0ca971ac32_XM_CSV<br>od_mql5e3c3e4f028dbab72_XM_CSV<br>od_mql5f3313c2c79f00c10_XM_CSV | 71.8 | 26.1 | 0.24 | 2024-01-02 → 2026-09-30 |
| 5 | od_skea5049c79288_XM_CSV<br>od_skea0ca971ac32_XM_CSV<br>od_mql5e3c3e4f028dbab72_XM_CSV<br>od_mql5f3313c2c79f00c10_XM_CSV | 58.1 | 22.6 | 0.27 | 2024-01-15 → 2026-09-30 |

## 5. Hàng chờ MT5 vòng 2

Việc mới lần này: 39 (bỏ 3 việc ghép trùng tín hiệu → còn 36); tổng trong `reports/vong2/hang_cho_vong2.jsonl`: 36. Máy nhà chỉ lấy khi đặt `BRAIN_VONG2=1`.
