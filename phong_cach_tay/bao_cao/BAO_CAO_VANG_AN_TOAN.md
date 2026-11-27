# Vàng tay_v2 — chữa cháy (lọc delta15, lot nhỏ, trần lỗ thả nổi)

Xuất: 2026-11-27 20:50 (giờ Việt Nam, UTC+7).

Không đặt lệnh thật. Vốn 10.000 USD = 1.000.000 USC (100 USC = 1 USD). Phần trăm DD không đổi khi chỉ đổi đơn vị.

## Cụm lỗ vàng của Anh — cái gì khác?

82 lệnh lỗ, tổng −31.117,10 USD. **86,7% số lỗ** nằm ở giữ 30 phút–4 giờ (53 lệnh, −26.965). Phiên Mỹ 20–07 VN chiếm −30.799 (68 lệnh, 82,9% số lệnh lỗ). Giờ 22 VN −8.452; giờ 23 VN −20.133. Thứ Tư 25/11 một mình −26.867 (50 lệnh; lot ≥1: −20.133).

Loại 25/11, lệnh 30p–4h lỗ chỉ còn −318 (12 lệnh) — “hố 30p–4h” gần như là ngày lot 1,00. Lot ≤0,10: 62 lệnh lỗ −10.898 (không kể 25/11: 32 lệnh, −4.251).

**Ngược delta15:** 50,0% lệnh lỗ vào ngược delta 15′ (chỉ 7,3% cùng chiều). Lot ≤0,10 lỗ: ngược 66,1%. Lệnh thắng: cùng chiều 33,8% / ngược 18,1%. Lãi nhanh <5 phút ít khi có delta15 (29,6%).

Khung tin điển hình (19:15–20:45 và 01:00–02:15 VN, kiểu NFP/CPI/FOMC): **0 lệnh lỗ**, lãi dương — **không cấm giờ tin** từ sổ này (không có lịch tin riêng). Không cấm giờ 22–23 VN: đó cũng là giờ lãi lớn của Anh.

| nhom | n | pnl | d15_co | d15_cung | d15_nguoc | us | hold_med |
|---|---|---|---|---|---|---|---|
| thua_tat_ca | 82 | -31117.1 | 57.3 | 7.3 | 50.0 | 82.9 | 76.31 |
| thua_lot<=0.1 | 62 | -10898.43 | 75.8 | 9.7 | 66.1 | 77.4 | 76.34 |
| thua_tru_25-11 | 32 | -4250.53 | 53.1 | 18.8 | 34.4 | 56.2 | 216.11 |
| thua_30p-4h | 53 | -26965.39 | 64.2 | 7.5 | 56.6 | 77.4 | 76.32 |
| thua_30p-4h_tru_25-11 | 12 | -318.49 | 33.3 | 33.3 | 0.0 | 0.0 | 216.09 |
| thang | 784 | 91819.75 | 51.9 | 33.8 | 18.1 | 70.3 | 11.52 |
| nhanh_lai | 301 | 41084.54 | 29.6 | 17.3 | 12.3 | 84.4 | 1.44 |

## Luật tránh đưa vào máy

1. **Không vào ngược delta15** — chỉ vào cùng chiều hoặc khi delta15 trung tính. Tín hiệu chỉ báo S≥1 phiên London+Mỹ: 58.303 nến → còn 51.106 sau lọc (chặn 7.197 nến ngược).
2. **Lot nhỏ:** cơ sở 0,01 (không 0,10; 0,03–0,05 không đạt DD <80% trên lưới). Cụm K=4, trần tầng 20, hedge 1× khối chính.
3. **Trần lỗ thả nổi `flcap` % equity:** chỉ ngừng DCA mới, **không phải SL cứng**, không đóng rổ. Ở lot 0,01, flcap 8–40% gần như không kích (trần tầng / độ sâu giá tới trước); flcap 5% chỉ đổi nhẹ số DCA (2.979 → 2.951). Vẫn để 15% làm lan can.
4. **Không khóa dừng DCA sau 30 phút** trên cấu hình mặc định. Luật này lấy từ hố 30p–4h trên sổ Anh, nhưng trên máy lot 0,01 + lọc delta15 + hedge 1×, khóa 30 nến **làm xấu**: lãi +9.731,71 / DD 71,45% so với không khóa +14.032,99 / DD 34,24%. Không cấm giờ Mỹ hay giờ tin.

## Quét 162 cấu hình (cố định dừng DCA 30 nến)

L0 ∈ {0,01, 0,03, 0,05}, K ∈ {2,3,4}, maxL ∈ {10,20,40}, flcap ∈ {15%, 25%, 40%}, hfrac ∈ {0,5, 1,0}, cộng 4 đối chứng. Lọc delta15, `dca_max_bars=30`.

**Đạt (lãi>0, DD<80%, không cháy) trên Jun–Nov: 36/166**, tất cả là L0=0,01. Họ L0=0,03 DD ~214%; L0=0,05 lỗ hoặc DD ~336–357% (nhiều cấu hình cháy). hfrac=0,5 với K=2 hoặc K=4 trượt 80% (DD 82–90%); hfrac=1,0 kéo DD xuống 71%. flcap 15/25/40% cho **cùng một đường** khi đã khóa 30 nến — trần lỗ không kích.

Đối chứng: lot 0,10 không lọc (máy v2 cũ) +98.412, DD **453,86%**. Lot 0,03 + khóa 30p + flcap, không lọc: +25.661, DD 214,70%. Lot 0,03 + delta15, **không** khóa 30p, flcap 25%, hfrac 0,5: **cháy** (−10.050).

Mẫu đạt tốt nhất trong lưới (vẫn bị khóa 30p): L0=0,01 K=4 maxL=20 hfrac=1: **+9.731,71, DD 71,45%**, IS +5.442,19 / OOS +4.289,51, spread×2 +9.529,67 / DD 65,59% (đạt), stress chỉ **5/11**.

## Cấu hình mặc định (sau khi bỏ khóa 30 phút)

`L0=0,01, K=4, maxL=20, TP=4,00, khe DCA=5,47, khe hedge=21,37, flcap=15%, hfrac=1,0, dca_max_bars=0`, lọc delta15 cùng chiều hoặc trung tính.

Cửa sổ M1 XM Jun–Nov 2026, vốn 10.000 USD = 1.000.000 USC:

| ten | net USD | net USC | maxdd USD | DD% | maxfl | IS | OOS | spr×2 net | spr×2 DD | Sharpe | DSR | đạt gốc | đạt spr×2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| flcap15 không khóa 30p (mặc định) | 14032.99 | 1.403.299 | 3423.59 | 34.24 | -3653.71 | 10425.50 | 3607.48 | 9216.99 | 45.45 | 3.298 | 1.00 | có | có |
| cùng lot, khóa DCA 30p | 9731.71 | 973.171 | 7144.92 | 71.45 | -7281.03 | 5442.19 | 4289.51 | 9529.67 | 65.59 | 2.326 | 1.00 | có | có |
| dca_max=15 + flcap 15% | 15517.44 | 1.551.744 | 6232.41 | 62.32 | -6283.50 | 9030.35 | 6487.09 | 10886.98 | 31.00 | 4.132 | 1.00 | có | có |
| dca_max=60 + flcap 15% | 10162.36 | 1.016.236 | 5748.53 | 57.49 | -5664.49 | 4865.83 | 5296.53 | 8627.12 | 57.31 | 2.542 | 1.00 | có | có |

Lãi mặc định +14.032,99 USD = +1.403.299 USC. DD 34,24% của 10.000 USD (lỗ thả nổi tệ nhất −3.653,71 USD = −365.371 USC, dưới 80%). IS và OOS đều lãi. Spread ×2 vẫn đạt.

### 11 stress (mặc định: 8/11 sống — chưa đủ 11/11)

Sống = không cháy và DD <80%. Cửa sổ sập M5 parquet **không có delta15 lịch sử** — lọc còn trung tính (giữ tín hiệu chỉ báo). Scale giá về 4000.

| scenario | net | maxdd | DD% | cháy | sống |
|---|---:|---:|---:|---|---|
| gap-10% tại đáy vốn | 12113.44 | 3142.40 | 31.42 | không | có |
| gap-20% tại đáy vốn | 8861.28 | 5534.77 | 55.35 | không | có |
| grind-20%/60 ngày | -8059.86 | 12830.83 | 128.31 | không | không |
| grind-35%/120 ngày | -10001.79 | 13795.91 | 137.96 | có | không |
| Q4-2018 | -1794.72 | 3612.67 | 36.13 | không | có |
| Covid 02-04/2020 | -8727.08 | 12961.88 | 129.62 | không | không |
| 2022 H1 | -2016.86 | 7991.01 | 79.91 | không | có |
| 2022 08-10 | 1149.15 | 3579.63 | 35.80 | không | có |
| 08-10/2023 | 1857.86 | 2215.91 | 22.16 | không | có |
| 07-08/2024 | 1276.17 | 1945.05 | 19.45 | không | có |
| 02-04/2025 | 495.42 | 5735.47 | 57.35 | không | có |

Cùng cấu hình nhưng khóa DCA 30p chỉ sống **5/11**. `dca_max=15` sống 7/11 (vượt grind −35% nhưng vẫn cháy Covid và trượt grind −20%, 2022 H1, 02–04/2025).

### Lân cận tham số (cùng L0=0,01 K=4 maxL=20 hfrac=1, lọc delta15)

| biến | net | DD% | IS / OOS | đạt 80% |
|---|---:|---:|---|---|
| gốc (TP 4, khe 5,47, hgap 21,37, không khóa 30p) | 14032.99 | 34.24 | 10425 / 3607 | có |
| TP 3,00 (có khóa 30p) | 9467.21 | 71.52 | 5165 / 4302 | có |
| TP 5,00 (có khóa 30p) | 10315.88 | 65.69 | 5462 / 4854 | có |
| khe DCA 4,00 (có khóa 30p) | 12219.62 | 65.65 | 6379 / 5841 | có |
| khe DCA 7,00 (có khóa 30p) | 9694.20 | 65.66 | 4955 / 4740 | có |
| hgap 15 | -4430.62 | 97.95 | 1851 / −6282 | không |
| hgap 28 | 3354.98 | 92.47 | 9637 / −6282 | không |

L0 ≥ 0,03 không đạt 80%. Hedge khe 15 hoặc 28 gãy OOS. TP 3–5 và khe DCA 4–7 vẫn đạt trên cửa sổ gốc (khi còn khóa 30p). Máy nhạy khe hedge — giữ 21,37.

## Kết luận 7 bước (vàng mặc định)

1. IS/OOS: **đạt** (cả hai nửa lãi).
2. Spread ×2: **đạt** (+9.216,99, DD 45,45%).
3. 11 stress: **không đạt đủ** (8/11; gãy grind −20%, grind −35% cháy, Covid DD 130%).
4. Lân cận: ổn ở lot 0,01 + hedge 1×; vỡ khi tăng lot hoặc đổi khe hedge.
5. Lỗ thả nổi vs 80%: **đạt trên cửa sổ gốc** (−36,5%); không đạt ở vài cửa sổ sập/grind.
6. Deflated Sharpe = 1,00 — không phân biệt (Sharpe 3,30 trên đường gốc).
7. Nhật ký bóng: `ket_qua/shadow_vang_an_toan.csv` (họ khóa 30p; không đặt lệnh).

**Cửa sổ Jun–Nov đạt lãi > 0 và DD < 80%. Toàn bộ 7 bước chưa sạch vì stress.** So với tay_v2 cũ (+98.412 / DD 453%) đây là bước chữa cháy đo được, không phải giấy phép giao dịch thật.

## US500: lọc mặc định theo ổn định OOS

Cả `p1_union_es` và `p1_uu_tien` đều đạt Jun–Nov, spread ×2, và sống 11/11 stress (cửa sổ sập không có tick Fxaurum → 0 lệnh, không được tính là “sống thật”).

| ten | net | DD% | IS | OOS | IS DD | OOS DD | spr×2 net | spr×2 DD | Sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| p1_union_es | 657.83 | 1.77 | 148.21 | 509.62 | 26.55 | 177.43 | 538.00 | 160.79 | 2.621 |
| p1_uu_tien | 792.71 | 2.54 | 93.14 | 699.57 | 166.03 | 253.92 | 608.21 | 256.51 | 1.998 |
| tay_v2 (không lọc) | 1712.59 | 2.54 | 1227.49 | 485.09 | 200.03 | 253.92 | 1198.93 | 256.51 | 2.561 |

**Khuyến nghị mặc định: `p1_union_es`.** Lý do ổn định OOS: DD chặt hơn (1,77% so với 2,54% — uu_tien không giảm DD so với máy không lọc); IS vẫn lãi và chiếm tỷ lệ lớn hơn (OOS/IS ≈ 3,4 so với 7,5); spread ×2 đạt với DD thấp hơn. `uu_tien` thắng lãi tuyệt đối và OOS (+699,57) nhưng IS yếu và phụ thuộc nửa sau.

File: `ma/may_v2.py` (flcap, hfrac, dca_max_bars), `ma/chay_vang_an_toan.py`. Số: `ket_qua/vang_an_toan_*.csv`, `vang_cum_thua.csv`. Không sửa `tin_hieu_data.py`.
