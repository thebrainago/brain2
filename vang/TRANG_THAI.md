# Trạng thái module vàng — để phiên sau chạy tiếp

Cập nhật **2026-11-27 20:16 (giờ Việt Nam, UTC+7)**.

## Đổi hướng (t345u)

**Không tiếp tục** lấy Donchian / EMA / lưới giá thuần làm gốc. Hai giai đoạn đúng:

1. **A — Tín hiệu data** từ Fxaurum GCZ6 (tick, 1m, big trade, sweep/absorption/iceberg) và OptionsDb (khi tìm thấy): delta/footprint, cụm big trade, đảo sweep, vùng absorption, VWAP/profile, wall/GEX/max pain. Quy sang GOLD.i bằng basis từng lúc.
2. **B — Gắn hệ xử lý lệnh** (nhồi / DCA / hedge khóa-gỡ / trailing / TP rổ) lấy từ thiết kế SP500 đêm 27/11.

Chi tiết: `bao_cao/HUONG_DI_DATA_VA_XU_LY_LENH.md`. `sp500/HE_XU_LY_LENH.md` đã có (khung chính HYB+AG 26/11). Nguồn máy: `E:\\backtests\\sp500_sys\\` (bản chép `vang/nguon_hyb/`).

## Số vừa đo (MT5 p4, tick thật, rồi dừng hàng đợi)

Cửa sổ 2025.09.01–2026.10.12, vốn 10.000 USD, 100% real ticks. Tiêu chí: lãi ròng > 0 và DD < 80%. Chi tiết `bao_cao/MT5_DOI_CHIEU.md` mục 6.

| EA | Khung | Lãi ròng | CAGR | DD | Lệnh | Thắng | PF | ĐẠT? |
|---|---|---:|---:|---:|---:|---:|---:|---|
| VANG_HedgeEMA (đảo 2 ATR ×1,5, lot 0,08) | H1 | **+13.051,52** | 111,98% | 45,09% | 467 | 70,02% | 1,13 | có |
| VANG_HedgeEMA (cùng họ, lot 0,16) | M15 | **−10.004,64** | vỡ vốn | 100,10% | 1.497 | 66,40% | 0,97 | không |
| VANG_LuoiPhuc (gỡ ×1,3, 2 bậc, lot 0,02) | H1 | **+2.511,40** | 22,33% | 26,93% | 819 | 74,36% | 1,08 | có |
| VANG_LuoiPhuc (nhân lot rổ ×1,5, lot 0,03) | H1 | **+2.837,23** | 25,19% | 47,62% | 823 | 74,36% | 1,05 | có |

Đã dừng hàng đợi (không chạy biến thiên lưới bước/chân/lot, không chạy cửa sổ 2025.10.01 cho EA mới). Python vẫn lệch: hedge H1 lãi gấp ~4,5 lần; hedge M15 Python lãi lớn trong khi tick vỡ vốn; lưới ×1,5 thì Python DD 94,8% (không ĐẠT) còn tick ĐẠT DD 47,62%.

## Data Fxaurum đã có (kéo 19:03–19:04 UTC+7, 0 lỗi)

1.648 nến 1h, 96.960 nến 1m, 191.044 sweep, 193.463 absorption, 6.422 iceberg, 82.175 big trades, gateway còn 6.144.531 tick GCZ6 (chưa xuất file). Basis trung vị +38,96 USD (827 giờ). ORB ± sweep lần trước **không ĐẠT** (PF 0,88 / 0,55). OptionsDb **đã tìm thấy** (20:01 UTC+7) tại `E:\\GrokWork\\FxaurumRithmic\\OptionsDb\\COMEX.GCZ6` (junction từ `%LOCALAPPDATA%\\FxaurumRithmic\\OptionsDb`): 9,59 GB, chủ yếu 19–20/11/2026. `optionRecordStatus` đang tắt. `optionHistory` chưa ra GEX/max pain (thiếu expiry / timeout).



## Giai đoạn A — số đo event-study (20:12 UTC+7)

Chi tiết `bao_cao/GIAI_DOAN_A.md`, bảng `ket_qua/event_study.csv`. Vào mở nến 1m kế, phí vòng tròn 0,21 giá, USD quy 1,00 lot.

Nến GC 1m: 2026-08-20 08:40 UTC → 2026-11-27 12:01 UTC (96.749 nến). Basis trung vị +24,94 (giảm ~56 tháng 8 xuống ~0 tháng 11). Tick đang xuất qua `aggTrades` (không sync), ~3,38 triệu tick lúc 20:16, chưa đủ để đo CVD/footprint.

Họ **PF 15 phút > 1** (sau phí):

| Tín hiệu | n | hit/PF/USD 15p | hit/PF/USD 60p | Cửa sổ |
|---|---:|---|---|---|
| cum50_60s (cụm big ≥50) | 290 | 50,3% / 1,10 / +9.283 | 49,3% / 1,11 / +17.599 | cả 3 tháng |
| vwap_tu_choi | 721 | 50,2% / 1,04 / +8.278 | 50,3% / 0,96 / −16.314 | cả 3 tháng |
| sw_dao_v5 (đảo sweep vol≥5) | 6.473 | 50,5% / 1,01 / +29.520 | 50,3% / 1,03 / +132.566 | chỉ 19–27/11 (flow local) |
| rule_pf15_tot (cộng 3 họ trên) | 2.845 | 49,9% / 1,01 / +7.555 | 50,7% / 1,04 / +58.408 | hỗn hợp |

`ab_v8` chỉ lãi ở 5 phút (PF 1,06); 15–60 phút lỗ. Quét 1m, iceberg, cụm ≥20, `rule_diem_ge2` đều PF < 1 sau phí.

## Giai đoạn B — cổng HYB+AG sang vàng (20:16 UTC+7)

Chi tiết `bao_cao/GIAI_DOAN_B_HYB.md`. Vốn 10.000, pv=100, bước lot 0,01 (K=3 → 0,03 lot), spread 0,20, Jun–Nov GOLD.i# M1. Tiêu chí: lãi > 0 và DD < 80%. Không đặt lệnh thật.

| Hệ | Lãi ròng | maxDD | DD% | IS / OOS | Spread ×2 | Sharpe / DSR | ĐẠT? |
|---|---:|---:|---:|---|---|---|---|
| baseline_HYB_AG | **+78,82** | 5.762 | 57,62% | −1.925 / **+2.003** | −751 (DD 60,8%) | 0,02 / 0,00 | có (thất bại spread ×2 và IS lỗ) |
| data_S_plus (cộng tín hiệu data vào S) | −4.148 | 5.764 | 57,64% | −1.935 / −2.212 | −4.914 | −0,87 / 0,00 | không |
| bài học K5 coef1,15 AG2x | +1.275 | 11.550 | **115,5%** (cháy) | +2.181 / −907 | −43 | 0,14 / 0,00 | không |
| lân cận coef1,15 / G=2 / th=2 / K=5 | tất cả lỗ hoặc cháy | 54–129% | — | — | — | — | không |

Stress 11 kịch bản (baseline): sống 10/11 (không cháy và DD<80%). **Cháy ở 2022 H1** (lãi −18.154, DD 22.583). Gap −10/−20% và grind −20%/−35% đều lãi trên M1 Jun–Nov (cần thận: gap được scale giá, có thể thiên lệch). 7 cửa sổ sập dùng parquet XAUUSD M15 (mốc giờ parquet, không phải máy chủ XM). Cùng cửa sổ, data_S_plus trùng baseline vì không có Fxaurum lịch sử.

**Kết luận ngắn:** cổng HYB+AG baseline vừa ĐẠT trên Jun–Nov nhưng IS lỗ, spread ×2 không ĐẠT, DSR 0, cháy 2022 H1 — chưa đủ để tin. Cộng tín hiệu data vào điểm S làm xấu đi trên cửa sổ này.

## Part 2 — phong cách tay (t348u, 27/11/2026 ~20:30 UTC+7)

Đã xong: đọc transcript XAUUSD Scalp Bot (agent `526b1021-…`); xuất chỉ-đọc XM Global MT5 (demo 345930355, 2870 deal, không SL tay); **không** tìm thấy Exness cent `E:\exness_cent` (không khởi động). Máy quy tắc + kiểm 7 bước XAU và US500 nằm ở `phong_cach_tay/`. Báo cáo: `phong_cach_tay/bao_cao/BAO_CAO_7_BUOC.md`, `QUY_TAC.md`, và bản sao `vang/bao_cao/PHONG_CACH_TAY.md` / `sp500/bao_cao/PHONG_CACH_TAY.md`.

- XAU `tay_HYB_AG`: −2.240,13 USD, DD 72,33%, không đạt (OOS +1.830 nhưng IS −4.071). Sống 9/11 stress (cháy gap 10%/20%). Xác nhận Fxaurum làm xấu (−5.735).
- US500 `tay_HYB_AG`: −450,88 USD, DD 8,75%, không đạt. Sống 10/11 (trượt grind −35%/120 ngày, DD 82,5%).
- Vốn 10.000 USD = 1.000.000 USC. Không đặt lệnh thật.

Còn: xuất tick GCZ6 (aggTrades) nếu còn chạy thì để nguyên, không tắt; không đụng g3, p3/p5/p6, không tắt terminal XM.

## tay_v2 (27/11/2026 ~20:37 UTC+7)

Máy gần phong cách tay hơn (cụm lot cố định, TP 4 USD, DCA 5,47, hedge 21, đóng rổ khi lãi). Chi tiết `phong_cach_tay/bao_cao/BAO_CAO_V2.md`.
- Vàng: +98.412 USD nhưng DD 453,86% — không đạt. Stress 0/11.
- US500: +1.712,59, DD 2,54%, spread ×2 đạt, sống 11/11 — đạt trên cửa sổ đo.
- Cạnh <5 phút +40.951 chủ yếu là 25/11 lot 1,00. Lot ≤0,10 <5 phút: +5.260, TP 4,00. S≥1 chỉ có ở 14,6% lệnh lãi nhanh.

## tay_v2 + lọc P1 (27/11/2026 ~20:45 UTC+7)

Dùng `phong_cach_tay/tin_hieu_data.py` (không sửa). Báo cáo `phong_cach_tay/bao_cao/BAO_CAO_V2_P1.md`.
- Vàng: lệnh lãi nhanh không trùng 4 luật ĐẠT (0%). Lệnh thua ngược delta15 50%. Máy cụm + lọc P1 cháy hoặc DD >80%.
- US500: lọc P1 đều đạt trên Jun–Nov; union +657,83 / DD 1,77%; `sig_ES` mặc định +375,64 / DD 0,57%.


## Chữa cháy vàng tay_v2 (27/11/2026 20:50 UTC+7)

Chi tiết `phong_cach_tay/bao_cao/BAO_CAO_VANG_AN_TOAN.md`. Vốn 10.000 USD = 1.000.000 USC. Không đặt lệnh thật.

- Cụm lỗ Anh: 82 lệnh −31.117; 50% ngược delta15; 86,7% lỗ ở 30p–4h (gần như hết là 25/11 lot 1). Không cấm giờ tin (0 lỗ trong khung 19:15–20:45 và 01:00–02:15 VN).
- Lưới 162 cấu hình (khóa DCA 30p): 36/166 đạt, chỉ L0=0,01. Tốt nhất trong lưới +9.731,71 / DD 71,45%, stress 5/11.
- **Mặc định** (bỏ khóa 30p — khóa này làm DD xấu hơn): L0=0,01 K=4 maxL=20 flcap=0,15 hfrac=1 lọc delta15. **+14.032,99 USD (1.403.299 USC), DD 34,24%**, IS +10.425,50 / OOS +3.607,48, spread×2 +9.216,99 / DD 45,45%. Stress **8/11** (gãy grind −20%/−35% và Covid). Chưa sạch 7 bước.
- US500 mặc định **`p1_union_es`**: +657,83, DD 1,77%, IS +148,21 / OOS +509,62 (ổn định hơn `uu_tien` dù lãi thấp hơn).
