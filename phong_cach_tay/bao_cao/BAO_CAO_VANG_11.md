# Vàng tay_v2 — tối ưu sống 11 stress (t349)

Xuất: 2026-11-27 21:31 (giờ Việt Nam, UTC+7).

Không đặt lệnh thật. Vốn 10.000 USD = 1.000.000 USC (100 USC = 1 USD). Phần trăm DD không đổi khi chỉ đổi đơn vị.

Mốc trước tối ưu (L0=0,01 K=4 maxL=20 hfrac=1 lọc delta15, không khóa 30p): Jun–Nov **+14.032,99 USD, DD 34,24%**, stress **8/11** (gãy grind −20%, grind −35%, Covid).

## Kết quả quét

93 cấu hình (đóng lỗ tổng, guard ADX/EMA/D1, khe ATR, lot giảm theo tầng, hedge boost, tuổi rổ, cooldown, xác nhận chỉ báo). **Đạt Jun–Nov (lãi>0, DD<80%, không cháy): 90/93.**

**Sống đủ 11/11 stress và Jun–Nov đạt: 3 cấu hình**, cùng họ — L0=0,01 K=4 maxL=20 hfrac=1 lọc delta15, `adx_th=30` (dừng DCA mới khi ADX≥30 và slope EMA200 D1 / D1 one-way ngược rổ), `loss_close` 30–40% equity lúc mở rổ (đóng cả rổ, không phải SL từng lệnh), cooldown 240 nến sau đóng lỗ.

| ten | net USD | net USC | maxdd USD | DD% | maxfl USD | maxfl USC | IS | OOS | spr×2 net | spr×2 DD | Sharpe | DSR | stress | tệ nhất |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| lc30_adx30 (mặc định) | 15930.00 | 1.593.000 | 3107.91 | 31.08 | -3256.30 | -325.630 | 10997.76 | 4932.25 | 9181.92 | 45.00 | 3.669 | 1.00 | 11/11 | -1877.80 |
| lc35_adx30 | 15930.00 | 1.593.000 | 3107.91 | 31.08 | -3256.30 | -325.630 | 10997.76 | 4932.25 | 10540.08 | 45.45 | 3.669 | 1.00 | 11/11 | -1664.47 |
| lc40_adx30 | 15930.00 | 1.593.000 | 3107.91 | 31.08 | -3256.30 | -325.630 | 10997.76 | 4932.25 | 10540.08 | 45.45 | 3.669 | 1.00 | 11/11 | -1664.47 |

Jun–Nov của 30/35/40% lỗ tổng **trùng nhau** (trần 30% chưa kích trên cửa sổ gốc; lỗ thả nổi tệ nhất −3.256,30 USD = 32,56% vốn). Trần 35–40% chỉ khác ở spread×2 (lãi cao hơn) và một số cửa sổ sập.

## Mặc định đề xuất

`L0=0,01, K=4, maxL=20, TP=4,00, khe DCA=5,47, khe hedge=21,37, flcap=0,15, hfrac=1, dca_max_bars=0, loss_close=0,30, adx_th=30, h_boost=0, cooldown=240, max_age=0`, lọc delta15 cùng chiều hoặc trung tính.

Chọn **30% lỗ tổng** chứ không 40%: cùng số Jun–Nov, spread×2 vẫn đạt, nhưng 2022 H1 còn lãi (+2.605,68, DD 49,59%) và grind −35% chặt hơn (DD 44,49% so với 57,02%).

## 11 stress — mặc định lc30_adx30 (sống = không cháy, DD<80%)

| scenario | net USD | maxdd | DD% | cháy | sống | lãi>0 |
|---|---:|---:|---:|---|---|---|
| gap-10% tại đáy vốn | 11039.12 | 5576.77 | 55.77 | không | có | có |
| gap-20% tại đáy vốn | 8464.19 | 4576.34 | 45.76 | không | có | có |
| grind-20%/60 ngày | 10002.45 | 3976.80 | 39.77 | không | có | có |
| grind-35%/120 ngày | 3482.31 | 4449.07 | 44.49 | không | có | có |
| Q4-2018 | -1877.80 | 3323.59 | 33.24 | không | có | không |
| Covid 02-04/2020 | 2754.73 | 6487.09 | 64.87 | không | có | có |
| 2022 H1 | 2605.68 | 4959.00 | 49.59 | không | có | có |
| 2022 08-10 | -791.28 | 3579.63 | 35.80 | không | có | không |
| 08-10/2023 | 552.13 | 2747.31 | 27.47 | không | có | có |
| 07-08/2024 | 1375.01 | 1945.05 | 19.45 | không | có | có |
| 02-04/2025 | 2194.89 | 5164.70 | 51.65 | không | có | có |

Hai cửa sổ lỗ nhưng dưới 80% DD: Q4-2018 −1.877,80 USD (tệ nhất), 2022 08–10 −791,28. Cửa sổ sập M5 không có delta15 — lọc còn trung tính. Gap/grind tính lại ATR/ADX/EMA trên giá đã biến hình.

lc40_adx30 cũng 11/11; tệ nhất −1.664,47 (Q4-2018); 2022 H1 lỗ −1.466,25, DD 68,60%.

## Kiểm 7 bước (mặc định lc30_adx30)

1. IS/OOS: **đạt** — IS +10.997,76 USD (1.099.776 USC), OOS +4.932,25 USD (493.225 USC); DD IS 31,08%, OOS 1.971,55 USD (19,72%).
2. Spread ×2: **đạt** — +9.181,92 USD, DD 4.499,93 (45,00%).
3. 11 stress: **đạt 11/11**.
4. Lân cận: xem dưới — ổn ở `loss_close` 30–40% và cùng ADX 30; **vỡ** khi tăng lot, đổi K, tắt ADX, khe hedge 15, lot decay 0,7.
5. Lỗ thả nổi vs 80%: **đạt trên Jun–Nov** (−3.256,30 USD = −325.630 USC, 32,56% vốn). Tệ nhất trong 11 stress: Covid DD 64,87%.
6. Deflated Sharpe = 1,00 (không phân biệt). Sharpe 3,669.
7. Nhật ký bóng: `ket_qua/shadow_vang11.csv` (không đặt lệnh).

## Lân cận (gốc = lc30_adx30)

Jun–Nov + (một phần) 11 stress:

| biến | net | DD% | spr×2 net / DD | Jun–Nov đạt | stress |
|---|---:|---:|---|---|---|
| gốc (lc 30%, ADX 30) | 15930.00 | 31.08 | 9181.92 / 45.00 | có | 11/11, tệ −1877.80 |
| loss_close 25% | 10285.89 | 57.80 | 5179.48 / 69.24 | có | 10/11 |
| loss_close 35% hoặc 40% | 15930.00 | 31.08 | 10540.08 / 45.45 | có | 11/11, tệ −1664.47 |
| tắt ADX | 14032.99 | 34.24 | 8017.00 / 45.08 | có | 9/11 |
| ADX 20 | 14881.88 | 31.40 | 8900.18 / 43.93 | có | 10/11 (gãy 02–04/2025, DD 103,97%) |
| hfrac 0,5 | 9442.34 | 44.81 | 8441.34 / 44.13 | có | 10/11 |
| L0=0,02 | 16740.59 | 108.31 | — | không | 6/11 |
| K=3 | -216.02 | 88.67 | — | không | — |
| lot decay 0,7 | 6077.14 | 113.25 | — | không | — |
| hgap 15 | 3512.63 | 50.37 | 738.67 / 49.04 | có | 7/11 |
| hgap 28 | 10889.37 | 54.42 | 11509.47 / 53.30 | có | chưa đo 11 |
| TP 3 / 5 | 4017.60 / 8857.44 | 72.31 / 63.07 | đạt / đạt | có | chưa đo 11 |
| khe DCA 4 / 7 | 6983.88 / 14697.38 | 63.34 / 31.25 | 7: spr×2 DD 79,49% (sát) | có | chưa đo 11 |
| max_age 1380 (1 ngày) | 15699.23 | 17.51 | 11707.85 / 17.57 | có | 10/11 (gãy gap −20%, DD 95,82%) |
| khe ATR ×1,2 | 15101.84 | 21.12 | 13549.72 / 21.26 | có | 9/11 |
| cooldown 0 / 60 / 1380 | 15930.00 | 31.08 | đạt | có | (cùng đường Jun–Nov) |

Tuổi rổ 1 ngày và khe ATR cải thiện DD Jun–Nov nhưng **không sống đủ 11** (thường gãy gap −20% hoặc 02–04/2025). Không đưa vào mặc định.

## Các ý khác đã thử (không vào mặc định)

- Xác nhận vào thêm (S≥2, BB/VWAP, RSI, BB hoặc RSI): Jun–Nov vẫn đạt, DD thường thấp hơn (S2: +4.471–5.410, DD 17,49–23,53%; BB+VWAP +5.736,76 / DD 12,76%) nhưng **tối đa 10/11** stress (S2/trend gãy gap −20%; RSI/BB gãy 02–04/2025).
- Chỉ tuổi rổ 240/480 nến: Jun–Nov DD 13,14–26,41%, **10/11** (gãy gap −20%, DD 98–113%).
- Lot decay 0,85 + ADX 25: Jun–Nov +18.200,98 / DD 21,67%, **10/11** (gãy grind −35%, DD 84,59%).
- Không vào ngược trend lúc vào lệnh: 1/4 cấu hình đạt Jun–Nov; bản đạt thì 10/11.

Cái kéo 8/11 → 11/11 là **đóng lỗ tổng 30–40% equity + dừng DCA khi ADX≥30 ngược rổ**. flcap 15% vẫn là lan can (gần như không kích ở lot 0,01). Hedge boost không cần cho 11/11.

File: `ma/may_v2.py`, `ma/chay_vang_11.py`. Số: `ket_qua/vang11_*.csv`, `shadow_vang11.csv`. Không sửa `tin_hieu_data.py`.
