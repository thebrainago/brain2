# Backtest MT5 vong 27 (may nha, 13/10/2026 toi) - BACKTEST MT5, KHONG PHAI TIEN THAT
XM Global MT5 build 6231, tk DEMO XMGlobal-MT5 10 (nhom Standard/Cash Ultra Low, hau to `#`), Model=4 "Every tick based on real ticks",
D1, deposit 10.000 USD, lot 0,01, leverage 1:30. EA `ea_demo/BRAIN_V24_MRZ_Trail_D1` (+ `BRAIN_V24_Chung.mqh`, them input InpTrATR/InpGiuToiDa, mac dinh = v24).
Terminal portable o D:\mt5_tester\p1,p2 va E:\mt5_tester\p3,p4 (khong o C:), uu tien Idle.

| bao cao | net USD | lenh | PF | DD equity max | chat luong | deal dau |
|---|---|---|---|---|---|---|
| v27_MRZ_AUDCAD__g2_2016 | +28.34 | 86 | 1.09 | 83.01 (0.83%) | 25% real ticks | 2018.06.07 |
| v27_MRZ_AUDUSD__g0_2016 | +232.27 | 105 | 1.46 | 108.89 (1.08%) | 25% real ticks | 2016.01.08 |
| v27_MRZ_AUDUSD__g2_2016 | +250.71 | 78 | 1.70 | 101.39 (1.01%) | 25% real ticks | 2018.04.24 |
| v27_MRZ_AUDUSD__g2_giu5_2016 | +102.50 | 108 | 1.28 | 94.32 (0.94%) | 25% real ticks | 2018.04.24 |
| v27_MRZ_AUDUSD__g2_tr15_2016 | +151.66 | 97 | 1.40 | 99.72 (0.99%) | 25% real ticks | 2018.04.24 |
| v27_MRZ_AUDUSD__g2_tr25_2016 | +363.82 | 65 | 2.12 | 97.17 (0.96%) | 25% real ticks | 2018.04.24 |
| v27_MRZ_EURGBP__g2_2016 | +304.13 | 84 | 1.78 | 101.53 (1.01%) | 25% real ticks | 2016.01.08 |
| v27_MRZ_GBPUSD__g0_2004 | +89.48 | 119 | 1.07 | 428.68 (4.22%) | 0% real ticks | 2004.01.06 |
| v27_MRZ_GBPUSD__g0_2016 | +343.47 | 115 | 1.38 | 257.99 (2.50%) | 25% real ticks | 2016.01.04 |
| v27_MRZ_GBPUSD__g2_2004 | +137.47 | 115 | 1.11 | 374.15 (3.68%) | 0% real ticks | 2004.01.06 |
| v27_MRZ_GBPUSD__g2_2016 | +368.27 | 114 | 1.43 | 246.78 (2.39%) | 25% real ticks | 2016.01.04 |
| v27_MRZ_GBPUSD__g2_giu5_2016 | +191.26 | 140 | 1.22 | 116.25 (1.14%) | 25% real ticks | 2016.01.04 |
| v27_MRZ_GBPUSD__g2_tr15_2016 | +311.85 | 133 | 1.35 | 153.18 (1.47%) | 25% real ticks | 2016.01.04 |
| v27_MRZ_GBPUSD__g2_tr25_2016 | +319.27 | 105 | 1.36 | 310.57 (3.00%) | 25% real ticks | 2016.01.04 |
| v27_MRZ_NZDUSD__g2_2016 | -72.20 | 84 | 0.84 | 125.34 (1.25%) | 25% real ticks | 2018.04.24 |
| v27_MRZ_USDCAD__g2_2016 | +155.68 | 99 | 1.34 | 131.69 (1.28%) | 25% real ticks | 2016.01.12 |

Ghi chu:
- "25% real ticks": XM chi co tick that tu ~2024-01; 2016-2023 la tick sinh tu M1. 2004-2015: 0% real ticks (tick sinh tu M1).
- **Nghi van**: voi InpGioVao=2, AUDUSD#/NZDUSD#/AUDCAD# deal dau 2018-04-24 (g0 AUDUSD bat dau 2016-01-08) -> g2 bo lo 2016-2018 tren cac ma nay
  (lich su M1 thieu gio 02h? hoac ChuaToiGio() chan). So g0 vs g2 AUDUSD vi vay KHONG cung giai doan. GBPUSD# hai ban cung bat dau 2016-01-04 -> so sanh hop le.
- Stress spread x1,5 (#10) CHUA chay: tester real-ticks khong co he so spread; can custom symbol.
- `spread_gio/*.csv`: spread theo gio server (point), tick XM 04-10/2026 (6 thang); `_tom_tat.csv` 00h vs trung vi ca ngay.
- `gia_xm/*`: gia D1/H1 XM (US500Cash#, GER40Cash#, GOLD.i#) tu 2010/2011 (H1 nen gzip).
