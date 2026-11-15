# Kết quả kiểm định Gann Square of 9 – Vàng & S&P 500 (Python)

Dữ liệu Yahoo Finance (tải 14/11/2026): GC=F, ES=F 1h (24/06/2024 → 13/11/2026), ^GSPC 1h (18/12/2023 → 13/11/2026, giờ RTH);
daily GC=F / ES=F / ^GSPC từ 2000 → 13/11/2026. Thang giá k = 1.

Tham số mặc định: khoảng chạm ±0.2×ATR(14), cửa sổ chạm X = 20 nến, xác nhận giữ/phá M = 5 nến,
điểm hồi = bật ngược ≥ 1.0×ATR, swing 10/5. Logic = bản indicator đã sửa (`gann_sq9_indicator_fixed.pine`).

**Định nghĩa**
- touch% = % mức bị chạm trong X nến.
- hold% = trong các mức đã chạm và đã ngã ngũ, % mức giữ được M nến (hỗ trợ + kháng cự) thay vì bị close xuyên qua.
- rev% = % mức đã chạm trở thành điểm hồi (giữ được và bật ngược ≥ 1 ATR).
- `_rand` = **đối chứng**: các mức có góc ngẫu nhiên nằm trong ±22.5° quanh mỗi góc Gann (cùng khoảng cách, chỉ khác "pha"), gộp theo đúng phân bố số mức của Sq9.
  z_hold = z-score của hold% Sq9 so với đối chứng (|z| > 2 mới đáng chú ý).

## 1. Gộp mọi góc: Sq9 vs đối chứng ngẫu nhiên

| ticker | tf | anchor | levels | touch | touch_rand | hold | hold_rand | z_hold | rev | rev_rand |
|---|---|---|---|---|---|---|---|---|---|---|
| GC=F | 1h | pdc | 9760 | 11.1 | 11.6 | 43.6 | 42.8 | 0.5 | 39.0 | 37.3 |
| GC=F | 1h | dopen | 9808 | 10.9 | 11.2 | 43.7 | 40.4 | 2.2 | 38.7 | 36.7 |
| GC=F | 1h | swh | 9904 | 12.0 | 12.0 | 46.0 | 46.4 | -0.3 | 41.8 | 41.5 |
| GC=F | 1h | swl | 9392 | 12.6 | 12.3 | 41.8 | 42.9 | -0.8 | 36.9 | 38.1 |
| ES=F | 1h | pdc | 9808 | 8.0 | 9.2 | 38.5 | 37.9 | 0.3 | 32.8 | 32.6 |
| ES=F | 1h | dopen | 9776 | 7.9 | 8.7 | 37.7 | 36.9 | 0.5 | 34.5 | 32.6 |
| ES=F | 1h | swh | 9760 | 9.5 | 9.9 | 41.5 | 42.9 | -0.8 | 36.5 | 36.9 |
| ES=F | 1h | swl | 9472 | 10.7 | 10.8 | 38.9 | 38.1 | 0.6 | 32.1 | 32.4 |
| ^GSPC | 1h | pdc | 11600 | 15.3 | 15.0 | 37.7 | 38.9 | -1.0 | 33.4 | 35.2 |
| ^GSPC | 1h | dopen | 11600 | 14.4 | 14.4 | 36.4 | 39.0 | -2.2 | 32.9 | 33.8 |
| ^GSPC | 1h | swh | 3696 | 16.5 | 16.6 | 35.9 | 36.1 | -0.1 | 32.0 | 34.0 |
| ^GSPC | 1h | swl | 3264 | 19.1 | 19.1 | 33.8 | 32.7 | 0.5 | 31.0 | 29.5 |
| GC=F | 1d | pdc | 103856 | 26.7 | 26.7 | 35.5 | 35.4 | 0.2 | 33.5 | 33.4 |
| GC=F | 1d | dopen | 103280 | 26.6 | 26.8 | 35.4 | 35.2 | 0.6 | 33.4 | 33.2 |
| GC=F | 1d | swh | 4736 | 27.4 | 27.4 | 33.3 | 31.3 | 1.5 | 31.6 | 29.7 |
| GC=F | 1d | swl | 4400 | 26.1 | 26.5 | 35.0 | 35.7 | -0.5 | 33.3 | 33.4 |
| ES=F | 1d | pdc | 103984 | 34.3 | 34.2 | 38.9 | 39.1 | -0.4 | 36.3 | 36.2 |
| ES=F | 1d | dopen | 103760 | 34.2 | 34.2 | 39.1 | 38.8 | 1.3 | 36.4 | 36.1 |
| ES=F | 1d | swh | 4544 | 32.1 | 31.6 | 40.4 | 40.1 | 0.3 | 37.2 | 37.1 |
| ES=F | 1d | swl | 4064 | 33.3 | 34.4 | 39.4 | 39.3 | 0.1 | 37.0 | 36.3 |
| ^GSPC | 1d | pdc | 107472 | 32.3 | 32.4 | 33.3 | 33.4 | -0.7 | 31.5 | 31.7 |
| ^GSPC | 1d | dopen | 107488 | 32.3 | 32.3 | 33.2 | 33.4 | -1.0 | 31.5 | 31.7 |
| ^GSPC | 1d | swh | 4640 | 30.5 | 30.2 | 33.2 | 33.7 | -0.4 | 31.6 | 32.4 |
| ^GSPC | 1d | swl | 3984 | 32.9 | 31.8 | 33.3 | 32.4 | 0.7 | 31.6 | 30.8 |

## 2. Theo góc (gộp mọi mã, khung, loại neo)

| angle | touch | touch_rand | hold | hold_rand | rev | rev_rand | touches |
|---|---|---|---|---|---|---|---|
| 45.0 | 70.3 | 70.2 | 34.4 | 34.3 | 32.4 | 32.2 | 67181.0 |
| 90.0 | 50.9 | 50.8 | 35.3 | 35.2 | 33.0 | 32.9 | 48631.0 |
| 135.0 | 35.5 | 35.8 | 35.9 | 36.3 | 33.7 | 33.9 | 33907.0 |
| 180.0 | 24.4 | 24.7 | 36.4 | 36.9 | 33.8 | 34.2 | 23351.0 |
| 225.0 | 17.4 | 17.6 | 39.1 | 38.4 | 36.4 | 35.6 | 16601.0 |
| 270.0 | 12.4 | 12.5 | 40.4 | 40.9 | 37.5 | 38.2 | 11831.0 |
| 315.0 | 9.0 | 8.9 | 40.7 | 40.6 | 38.4 | 38.4 | 8565.0 |
| 360.0 | 6.6 | 6.7 | 41.2 | 40.0 | 38.8 | 37.8 | 6337.0 |

## 3. Kết luận

- **Không thấy lợi thế của góc Gann Sq9.** Touch%, hold% và rev% của mức Sq9 gần như trùng với mức ngẫu nhiên cùng khoảng cách
  (chênh lệch trung bình < 1 điểm %). Trong 192 phép so (mã × khung × neo × góc) chỉ 1 phép có z > 1.96, ít hơn số dương tính giả kỳ vọng (~5).
  24 phép gộp: 1 phép z = +2.2 (GC 1h, neo mở phiên) và 1 phép z = −2.2 (^GSPC 1h, neo mở phiên), đúng kiểu nhiễu ngẫu nhiên.
- Tỷ lệ chạm giảm đều theo khoảng cách (45° ~70% trên khung D, ~45% trên 1h; 360° chỉ vài %), đây là hệ quả của biến động chứ không phải của Gann.
- Sau khi chạm, chỉ khoảng 33–46% mức "giữ" được 5 nến. Nghĩa là phần lớn mức bị xuyên qua, kể cả mức Sq9.
- Lưu ý: neo ngày trước và mở phiên trên khung D tạo một bộ mức mỗi ngày nên các mẫu chồng lấn và tương quan. z-score ở đó bị phóng đại, nên kết luận "không có lợi thế" càng chắc.

## 4. Mô phỏng nhanh strategy (SL 1×ATR qua mức, TP = mức Sq9 kế tiếp, phí 0.01%/chiều)

| ticker | tf | anchor | levels | trades | win | avg_bp | pf | total |
|---|---|---|---|---|---|---|---|---|
| GC=F | 1h | pdc | sq9 | 693 | 60.61 | -5.12 | 0.84 | -35.49 |
| GC=F | 1h | pdc | control-22.5 | 1045 | 66.22 | -0.26 | 0.99 | -2.7 |
| GC=F | 1h | swh | sq9 | 674 | 59.5 | -1.97 | 0.93 | -13.31 |
| GC=F | 1h | swh | control-22.5 | 884 | 61.31 | -2.98 | 0.89 | -26.35 |
| GC=F | 1h | swl | sq9 | 657 | 56.16 | -4.82 | 0.85 | -31.67 |
| GC=F | 1h | swl | control-22.5 | 854 | 62.53 | -2.14 | 0.92 | -18.32 |
| ES=F | 1h | pdc | sq9 | 483 | 55.69 | -5.74 | 0.77 | -27.73 |
| ES=F | 1h | pdc | control-22.5 | 799 | 64.21 | 0.97 | 1.06 | 7.73 |
| ES=F | 1h | swh | sq9 | 506 | 52.96 | -4.23 | 0.82 | -21.4 |
| ES=F | 1h | swh | control-22.5 | 706 | 56.23 | -3.49 | 0.83 | -24.65 |
| ES=F | 1h | swl | sq9 | 577 | 56.67 | 0.61 | 1.03 | 3.51 |
| ES=F | 1h | swl | control-22.5 | 722 | 53.32 | -5.3 | 0.76 | -38.25 |
| ^GSPC | 1h | pdc | sq9 | 428 | 65.65 | -2.34 | 0.9 | -10.04 |
| ^GSPC | 1h | pdc | control-22.5 | 612 | 64.22 | -4.25 | 0.8 | -25.99 |
| ^GSPC | 1h | swh | sq9 | 335 | 57.91 | -3.96 | 0.84 | -13.25 |
| ^GSPC | 1h | swh | control-22.5 | 405 | 61.73 | -5.45 | 0.76 | -22.07 |
| ^GSPC | 1h | swl | sq9 | 328 | 57.01 | -2.63 | 0.89 | -8.63 |
| ^GSPC | 1h | swl | control-22.5 | 369 | 63.14 | -1.42 | 0.93 | -5.24 |
| GC=F | 1d | pdc | sq9 | 318 | 77.99 | 3.9 | 1.07 | 12.39 |
| GC=F | 1d | pdc | control-22.5 | 845 | 75.15 | -9.24 | 0.82 | -78.12 |
| GC=F | 1d | swh | sq9 | 550 | 66.91 | -5.73 | 0.91 | -31.53 |
| GC=F | 1d | swh | control-22.5 | 609 | 69.79 | -0.11 | 1.0 | -0.7 |
| GC=F | 1d | swl | sq9 | 514 | 66.93 | -3.72 | 0.94 | -19.14 |
| GC=F | 1d | swl | control-22.5 | 520 | 69.23 | -6.09 | 0.9 | -31.65 |
| ^GSPC | 1d | pdc | sq9 | 428 | 70.56 | -38.83 | 0.54 | -166.2 |
| ^GSPC | 1d | pdc | control-22.5 | 1085 | 73.18 | -20.53 | 0.65 | -222.78 |
| ^GSPC | 1d | swh | sq9 | 667 | 67.77 | -11.17 | 0.81 | -74.48 |
| ^GSPC | 1d | swh | control-22.5 | 735 | 66.67 | -19.12 | 0.69 | -140.57 |
| ^GSPC | 1d | swl | sq9 | 603 | 67.66 | -20.13 | 0.73 | -121.38 |
| ^GSPC | 1d | swl | control-22.5 | 618 | 65.86 | -20.71 | 0.72 | -127.99 |

Kết quả lẫn lộn, đa số PF < 1. Mức Sq9 không thắng đều so với bản đối chứng lệch −22.5°. Strategy chỉ là công cụ nghiên cứu, không phải hệ thống giao dịch.

## 5. Tái chạy

```
cd tools/kiem_dinh/gann_sq9
.venv/bin/python sq9_stats.py             # -> results/per_angle.csv, totals.csv, levels.csv.gz
.venv/bin/python make_summary.py          # -> results/pooled_vs_random.csv, by_angle_all.csv
.venv/bin/python strategy_sim.py          # -> results/strategy_sim.csv
.venv/bin/python sq9_stats.py --legacy --out results_legacy   # mô phỏng lỗi của bản indicator gốc
```
Tuỳ chọn: `--X`, `--M`, `--tol` (×ATR), `--rev`.
