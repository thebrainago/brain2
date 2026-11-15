# KẾT QUẢ TEST 6: FIBONACCI XOẮN ỐC VÀ CÁC LOẠI CHART PHI CHUẨN (Vàng và S&P 500)

**Dữ liệu:**
- **Nến ngày:** GC=F từ 2008, ES=F và ^GSPC từ 2000 đến 13/11/2026. IS/OOS tách ở 01/01/2016.
- **Nến 1h:** GC=F và ES=F từ 06/2024, ^GSPC phiên chính từ 12/2023, đến 13/11/2026. IS/OOS chia đôi theo thời gian.
- **Nến 15m:** GC=F và ES=F, chỉ khoảng 60 ngày (04/09 → 13/11/2026). Mỗi nửa chỉ khoảng 1 tháng, nên chỉ để tham khảo.
- **Phí:** spread vàng 0,3, ES 0,25, ^GSPC 0,5 điểm. Mỗi lần đổi vị thế trả nửa spread.
- **Hiệu chỉnh nhiều phép thử:** FDR Benjamini–Hochberg.

## TÓM TẮT KẾT LUẬN

| Phương pháp | Kết luận | Lý do chính |
|---|---|---|
| Fibo xoắn ốc, chạm đường xoắn (giữ / hồi) | **Không có edge** | Bằng xoắn ốc có hệ số ngẫu nhiên. 0/432 lát cắt qua FDR. Riêng ES 1h có hồi ≥1 ATR nhỉnh hơn (+5 điểm), nhưng giảm từ IS sang OOS và q=0,11 → *yếu, chưa xác nhận* |
| Fibo xoắn ốc, mốc thời gian | **Không có edge** | Tỷ lệ trúng đảo chiều bằng hoặc thấp hơn xoắn ốc ngẫu nhiên ở cả 6 bộ dữ liệu |
| Heikin Ashi (đổi màu, nến không bóng) | **Không có edge** | Khớp ở giá thật thì Sharpe quanh 0. Khớp ở giá HA thì đẹp ảo, Sharpe 2–20 |
| Renko (đảo N brick, đếm brick) | **Không có edge** | Không qua được bootstrap. Bản khớp ảo cũng bị thổi phồng |
| Point & Figure (double, triple, catapult) | **Không có edge** | Double top/bottom chỉ là một kiểu đi theo trend, ngang Donchian. Triple và catapult quá ít tín hiệu (3–27 lệnh) |
| Three Line Break | **Không có edge** | Không hơn đối chứng |
| Kagi (yin/yang) | **Không có edge** (yếu) | Đảo 3 ATR, chỉ mua, gần như là cầm vàng/chỉ số dài hạn (≈ Buy & Hold). Vàng 1h OOS Sharpe 1,54 nhưng p=0,19 |

**Có gì thắng được trend-following đơn giản ở OOS không?** Không có gì thắng một cách có ý nghĩa.
- Đã chọn 65 cấu hình (mỗi phương pháp × bộ dữ liệu, tốt nhất ở IS). Ở OOS:
  - Bootstrap p<0,05: **0**. FDR q<0,05: **0**.
  - Hơn đối chứng Donchian/EMA (chọn tốt nhất IS): 28/65.
  - Hơn Buy & Hold: 24/65.
  - Hơn cả hai: 15/65, gần bằng mức may rủi.
- Các trường hợp "hơn cả hai" tập trung ở:
  - **Vàng 1h:** nửa sau thuận lợi cho trend-following nói chung. Donchian N=20, dù không phải cấu hình được chọn ở IS, cũng đạt Sharpe 0,95, trong khi Buy & Hold chỉ 0,31. Các chart phi chuẩn đạt 0,8–1,0, ngang Donchian. Riêng Kagi 1,54 nhưng p=0,19.
  - **ES 15m:** OOS chỉ khoảng 1 tháng nên là nhiễu.
- Chart phi chuẩn **không làm gì hơn trend-following thường**. Chúng chỉ là một cách lọc nhiễu khác.

---
## PHẦN 1: FIBONACCI XOẮN ỐC

**Thiết lập:**
- **Tâm và bán kính:** tâm là pivot lớn 20/20 hoặc 60/60, chỉ dùng từ nến xác nhận nên không nhìn trước. Bán kính đầu bằng chân sóng đầu tiên, tức từ pivot tới cực trị ngược lại trước khi xác nhận.
- **Công thức:** r = a·φ^(2θ/π). Xét cả 2 chiều quay.
- **Tỷ lệ giá/thời gian:** có 2 cách:
  - (A) 1 nến tương ứng 1 ATR.
  - (B) theo chân sóng, chân sóng nằm ở góc 45°.
- **Sự kiện giá:** lần đầu giá chạm mỗi nhánh xoắn (±0,2 ATR). Đo hai chỉ tiêu:
  - **Giữ 5 nến:** không đóng cửa xuyên qua mức.
  - **Hồi:** bật ≥1 ATR trong 10 nến, trước khi phá.
- **Mốc thời gian:** nến mà xoắn ốc cắt trục ngang (giá = giá neo), cộng hình chiếu bán kính khi cắt trục dọc. "Trúng" là có swing 10/10 trong ±3 nến.
- **Đối chứng (200 lần rút mỗi neo):**
  - Hệ số tăng g ngẫu nhiên trong U(1,3–2,0), bỏ khoảng ±0,05 quanh φ.
  - Xoay ngẫu nhiên ±90°.
  - Cả hai cùng lúc.
  - p tính theo phân phối của 200 lần rút.

**Kết quả gộp (φ so với xoắn ốc ngẫu nhiên, cả g lẫn góc xoay):**

| Dữ liệu | Neo | Chỉ tiêu | n (φ) | φ % | Ngẫu nhiên % | z | p | q |
|---|---|---|---|---|---|---|---|---|
| ESF 1d | pivot 20/20+60/60 | Giữ 5 nến | 347 | 38.0 | 37.8 | +0.08 | 0.940 | 0.96 |
| ESF 1d | pivot 20/20+60/60 | Hồi ≥1 ATR | 347 | 47.8 | 46.9 | +0.38 | 0.741 | 0.87 |
| ESF 1d | pivot 20/20+60/60 | Mốc t.gian trúng đảo chiều | 3424 | 36.0 | 36.9 | -1.06 | 0.269 | 0.67 |
| ESF 1h | pivot 20/20+60/60 | Giữ 5 nến | 900 | 42.3 | 40.8 | +1.15 | 0.274 | 0.67 |
| ESF 1h | pivot 20/20+60/60 | Hồi ≥1 ATR | 900 | 52.3 | 46.9 | +3.69 | 0.010 | 0.11 |
| ESF 1h | pivot 20/20+60/60 | Mốc t.gian trúng đảo chiều | 8668 | 42.2 | 42.8 | -1.09 | 0.284 | 0.67 |
| GCF 1d | pivot 20/20+60/60 | Giữ 5 nến | 304 | 36.8 | 35.0 | +0.80 | 0.438 | 0.74 |
| GCF 1d | pivot 20/20+60/60 | Hồi ≥1 ATR | 304 | 44.7 | 43.0 | +0.70 | 0.502 | 0.74 |
| GCF 1d | pivot 20/20+60/60 | Mốc t.gian trúng đảo chiều | 2763 | 41.5 | 41.0 | +0.59 | 0.567 | 0.77 |
| GCF 1h | pivot 20/20+60/60 | Giữ 5 nến | 874 | 43.9 | 43.7 | +0.17 | 0.900 | 0.94 |
| GCF 1h | pivot 20/20+60/60 | Hồi ≥1 ATR | 874 | 50.1 | 49.6 | +0.32 | 0.756 | 0.87 |
| GCF 1h | pivot 20/20+60/60 | Mốc t.gian trúng đảo chiều | 8140 | 39.5 | 40.3 | -1.58 | 0.119 | 0.49 |
| GSPC 1d | pivot 20/20+60/60 | Giữ 5 nến | 354 | 24.9 | 31.5 | -3.05 | 0.010 | 0.11 |
| GSPC 1d | pivot 20/20+60/60 | Hồi ≥1 ATR | 354 | 36.2 | 41.0 | -2.04 | 0.035 | 0.24 |
| GSPC 1d | pivot 20/20+60/60 | Mốc t.gian trúng đảo chiều | 3559 | 35.6 | 36.3 | -0.80 | 0.448 | 0.74 |
| GSPC 1h | pivot 20/20+60/60 | Giữ 5 nến | 290 | 40.7 | 37.4 | +1.32 | 0.214 | 0.64 |
| GSPC 1h | pivot 20/20+60/60 | Hồi ≥1 ATR | 290 | 47.9 | 44.1 | +1.43 | 0.174 | 0.55 |
| GSPC 1h | pivot 20/20+60/60 | Mốc t.gian trúng đảo chiều | 2875 | 41.5 | 40.9 | +0.72 | 0.433 | 0.74 |

**IS và OOS của các chỗ lệch đáng chú ý:**

| Dữ liệu | Giai đoạn | n | Giữ φ / ngẫu nhiên | Hồi φ / ngẫu nhiên |
|---|---|---|---|---|
| ESF 1h | IS | 470 | 43.6 / 40.0 (z +1.9) | 53.6 / 46.1 (z +3.5) |
| ESF 1h | OOS | 430 | 40.9 / 41.5 (z -0.3) | 50.9 / 47.8 (z +1.5) |
| GSPC 1h | IS | 126 | 37.3 / 37.4 (z -0.0) | 43.7 / 44.1 (z -0.1) |
| GSPC 1h | OOS | 164 | 43.3 / 37.4 (z +1.6) | 51.2 / 44.2 (z +2.0) |
| GSPC 1d | IS | 231 | 22.1 / 31.3 (z -3.8) | 32.0 / 41.2 (z -3.3) |
| GSPC 1d | OOS | 123 | 30.1 / 31.7 (z -0.4) | 43.9 / 40.5 (z +0.8) |
| GCF 1h | IS | 435 | 49.0 / 44.4 (z +2.1) | 54.3 / 49.8 (z +1.8) |
| GCF 1h | OOS | 439 | 39.0 / 43.0 (z -1.8) | 46.0 / 49.4 (z -1.5) |

Đã thử **432 lát cắt** (dữ liệu × tỷ lệ × chiều quay × IS/OOS × chỉ tiêu × đối chứng).
- Có 21 lát p<0,05 (chỉ riêng may rủi đã cho khoảng 22). Trong đó chỉ 9 lát nghiêng về φ.
- FDR q<0,05: **0**.
- Không lát nào lặp lại được ở cả IS lẫn OOS.

**Kết luận Phần 1:**
- Đường xoắn φ không giữ giá tốt hơn xoắn ốc có hệ số hoặc góc xoay bất kỳ. Riêng ^GSPC nến ngày, φ còn kém hơn ở IS.
- Mốc thời gian của xoắn ốc trúng đảo chiều ngang mức ngẫu nhiên.
- Thêm một vấn đề: xoắn ốc phụ thuộc hoàn toàn vào cách quy đổi "1 nến = bao nhiêu giá". Cả 2 cách quy đổi đều không cho kết quả.

---
## PHẦN 2: CHART PHI CHUẨN

**Nguyên tắc chống ảo:**
- Nến HA, brick, cột và đường chỉ được biết khi đã hoàn thành ở giá đóng cửa của nến thật, dựng từ giá đóng cửa.
- Tín hiệu xuất hiện ở close t → **khớp ở giá mở cửa THẬT của nến t+1**.
- Bản "ảo" dùng cùng tín hiệu nhưng khớp ở giá HA close hoặc giá brick. Đây chính là kiểu backtest "Renko/HA đẹp như mơ" hay thấy trên mạng: bạn không thể mua được ở giá HA vì đó là giá trung bình, không phải giá thị trường.

**Chiến lược đã thử:**
- **HA:** đổi màu N nến (N=1/2/3); nến không bóng dưới (hoặc trên) k nến, thoát khi đổi màu.
- **Renko:** box 0,5/1/2×ATR động, hoặc box log 1/2×ATR% cố định. Đảo chiều sau N brick (N=1/2/3); đếm M brick (M=3/5) rồi thoát khi có brick ngược.
- **Point & Figure:** box 0,5/1/2×ATR% (log), đảo 3 ô. Tín hiệu double top/bottom, triple, catapult.
- **Three Line Break:** 2/3/4 đường.
- **Kagi:** đảo 0,5/1/2/3 ATR, mua khi yang, bán khi yin.
- Mỗi chiến lược chạy 2 chế độ: Long/Short (LS) và chỉ Long (L).

**Đối chứng:**
- Donchian 20/55 và EMA 10/50, 20/100 trên nến thường, chọn tốt nhất ở IS.
- Buy & Hold.
- Block-bootstrap nến OOS (khối 20 nến, 300 lần): chạy đúng cấu hình đã chọn trên dữ liệu đã xáo khối, để xem chiến lược có khai thác được cấu trúc thật hay chỉ ăn theo drift.

### 2a. Cấu hình tốt nhất IS, kết quả OOS: Sharpe ròng (p bootstrap)

| method          | GC 1d         | ES 1d        | GSPC 1d       | GC 1h        | ES 1h         | GSPC 1h       | GC 15m        | ES 15m        |
|:----------------|:--------------|:-------------|:--------------|:-------------|:--------------|:--------------|:--------------|:--------------|
| BL_Donchian     | 0.65 (p0.38)  | 0.68 (p0.5)  | 0.63 (p0.65)  | 0.95 (p0.33) | -0.09 (p0.84) | -0.81 (p0.82) | 1.3 (p0.53)   | -0.23 (p0.52) |
| BL_EMA          | 0.49 (p0.26)  | 0.7 (p0.49)  | 0.72 (p0.54)  | 0.29 (p0.58) | 0.01 (p0.76)  | 0.55 (p0.68)  | 1.8 (p0.5)    | -2.13 (p0.76) |
| HA_doi_mau      | 0.7 (p0.53)   | 0.47 (p0.58) | 0.53 (p0.6)   | 0.92 (p0.38) | 0.23 (p0.54)  | 0.64 (p0.54)  | -0.49 (p0.52) | -1.08 (p0.5)  |
| HA_khong_bong   | -0.18 (p0.52) | 0.28 (p0.54) | 0.35 (p0.56)  | 0.22 (p0.44) | 0.49 (p0.49)  | 0.73 (p0.5)   | -1.36 (p0.49) | -0.45 (p0.52) |
| Kagi            | 0.7 (p0.41)   | 0.7 (p0.48)  | 0.82 (p0.44)  | 1.54 (p0.19) | 0.55 (p0.57)  | 0.44 (p0.7)   | 0.32 (p0.63)  | 1.33 (p0.48)  |
| Line_Break      | 0.38 (p0.6)   | 0.62 (p0.44) | 0.42 (p0.72)  | 0.87 (p0.34) | 0.11 (p0.7)   | 0.21 (p0.62)  | -6.1 (p0.83)  | 3.42 (p0.43)  |
| PnF_catapult    | –             | –            | -0.43 (p0.92) | 0.66 (p0.26) | –             | –             | –             | –             |
| PnF_double      | 0.79 (p0.26)  | 0.73 (p0.45) | 0.65 (p0.69)  | 0.97 (p0.29) | 1.3 (p0.32)   | 0.35 (p0.74)  | 0.98 (p0.55)  | 0.86 (p0.46)  |
| PnF_triple      | 0.47 (p0.13)  | 0.0 (p0.74)  | 0.64 (p0.18)  | -0.16 (p0.7) | -0.2 (p0.57)  | 0.29 (p0.25)  | 0.8 (p0.5)    | –             |
| Renko_dao_N     | 0.42 (p0.53)  | 0.62 (p0.6)  | 0.96 (p0.29)  | 0.83 (p0.3)  | -0.08 (p0.81) | -0.28 (p0.9)  | -0.09 (p0.66) | 2.93 (p0.52)  |
| Renko_dem_brick | 0.33 (p0.4)   | 0.29 (p0.81) | 0.1 (p0.84)   | 1.0 (p0.28)  | -0.59 (p0.81) | 0.78 (p0.33)  | -0.43 (p0.6)  | 1.42 (p0.68)  |
| **Buy & Hold**  | 0.79          | 0.76         | 0.85          | 0.31         | 0.94          | 1.5           | -2.91         | -1.52         |

PnF triple và catapult để trống "–" là vì ở IS có dưới 10 lệnh. Chi tiết PF, kỳ vọng R, win, maxDD, số lệnh ở `results6/charts_best_IS_to_OOS.csv`.

### 2b. Chi tiết OOS các cấu hình chọn (nến ngày và 1h)

| Dữ liệu   | PP              | Tham số       | Chế độ   |   Sharpe IS |   Sharpe OOS |   PF OOS |   Kỳ vọng R (ATR) |   Win % |   Lệnh |   MaxDD % |   p boot |    q |
|:----------|:----------------|:--------------|:---------|------------:|-------------:|---------:|------------------:|--------:|-------:|----------:|---------:|-----:|
| GC 1d     | BL_Donchian     | N=20          | L        |        0.11 |         0.65 |     4.13 |              2.82 |   57.14 |     28 |     24.76 |     0.38 | 0.85 |
| GC 1d     | BL_EMA          | 20/100        | LS       |        0.19 |         0.49 |     2.73 |              4.21 |   31.25 |     32 |     39.12 |     0.26 | 0.85 |
| GC 1d     | HA_doi_mau      | N=2           | L        |        0.33 |         0.7  |     1.57 |              0.4  |   44.83 |    203 |     25.94 |     0.53 | 0.85 |
| GC 1d     | HA_khong_bong   | k=1           | LS       |        0.08 |        -0.18 |     0.95 |             -0.01 |   37.36 |    463 |     78.57 |     0.52 | 0.85 |
| GC 1d     | Kagi            | dao=3ATR      | L        |        0.12 |         0.7  |     8.59 |              9.35 |   61.54 |     13 |     25.8  |     0.41 | 0.85 |
| GC 1d     | Line_Break      | 2LB           | L        |       -0.13 |         0.38 |     1.21 |              0.31 |   43.42 |    152 |     28    |     0.6  | 0.85 |
| GC 1d     | PnF_double      | box=0.5xATR%  | L        |       -0.09 |         0.79 |     2.94 |              3.66 |   59.26 |     27 |     20    |     0.26 | 0.85 |
| GC 1d     | PnF_triple      | box=0.5xATR%  | LS       |       -0.08 |         0.47 |     2.86 |              2.5  |   58.82 |     17 |     24.07 |     0.13 | 0.85 |
| GC 1d     | Renko_dao_N     | log1xATR%,N=1 | L        |        0.36 |         0.42 |     1.5  |              1    |   42.62 |     61 |     22.08 |     0.53 | 0.85 |
| GC 1d     | Renko_dem_brick | log1xATR%,M=3 | L        |        0.21 |         0.33 |     1.72 |              0.88 |   53.85 |     39 |     24.7  |     0.4  | 0.85 |
| ES 1d     | BL_Donchian     | N=55          | L        |        0.23 |         0.68 |     5.92 |              5.39 |   54.54 |     11 |     27.14 |     0.5  | 0.85 |
| ES 1d     | BL_EMA          | 10/50         | L        |        0.42 |         0.7  |     3.61 |              1.49 |   48.39 |     31 |     19.5  |     0.49 | 0.85 |
| ES 1d     | HA_doi_mau      | N=2           | L        |       -0.08 |         0.47 |     1.31 |              0.22 |   50.73 |    205 |     24.76 |     0.58 | 0.85 |
| ES 1d     | HA_khong_bong   | k=2           | L        |       -0.26 |         0.28 |     1.23 |              0.18 |   45.56 |    169 |     25.59 |     0.54 | 0.85 |
| ES 1d     | Kagi            | dao=3ATR      | L        |        0.59 |         0.7  |    18.29 |             10.44 |   71.43 |      7 |     25.67 |     0.48 | 0.85 |
| ES 1d     | Line_Break      | 4LB           | L        |       -0.16 |         0.62 |     1.52 |              0.89 |   53.12 |     64 |     36.58 |     0.44 | 0.85 |
| ES 1d     | PnF_double      | box=1xATR%    | L        |        0.24 |         0.73 |     3.96 |              3.28 |   50    |     10 |     37.29 |     0.45 | 0.85 |
| ES 1d     | PnF_triple      | box=1xATR%    | LS       |        0.07 |         0    |     0.86 |             -2.19 |   16.67 |      6 |     31.71 |     0.74 | 0.86 |
| ES 1d     | Renko_dao_N     | ATRx2,N=1     | L        |        0.37 |         0.62 |     5.46 |              2.89 |   56.25 |     16 |     25.19 |     0.6  | 0.85 |
| ES 1d     | Renko_dem_brick | ATRx2,M=3     | L        |        0.23 |         0.29 |     2.26 |              1.82 |   61.54 |     13 |     20.04 |     0.81 | 0.86 |
| GSPC 1d   | BL_Donchian     | N=55          | L        |        0.19 |         0.63 |     4.74 |              5.42 |   50    |     12 |     27.64 |     0.65 | 0.85 |
| GSPC 1d   | BL_EMA          | 10/50         | L        |        0.3  |         0.72 |     3.6  |              1.9  |   58.06 |     31 |     19.15 |     0.54 | 0.85 |
| GSPC 1d   | HA_doi_mau      | N=2           | L        |       -0.16 |         0.53 |     1.32 |              0.26 |   52.28 |    197 |     29.26 |     0.6  | 0.85 |
| GSPC 1d   | HA_khong_bong   | k=1           | L        |       -0.54 |         0.35 |     1.16 |              0.09 |   48.12 |    266 |     24.27 |     0.56 | 0.85 |
| GSPC 1d   | Kagi            | dao=3ATR      | L        |        0.5  |         0.82 |     4.98 |              8.02 |   70    |     10 |     26.17 |     0.44 | 0.85 |
| GSPC 1d   | Line_Break      | 4LB           | L        |       -0.01 |         0.42 |     1.35 |              0.74 |   50.82 |     61 |     46.68 |     0.72 | 0.86 |
| GSPC 1d   | PnF_catapult    | box=0.5xATR%  | LS       |       -0.28 |        -0.43 |     0.02 |             -1.92 |   25    |      4 |     11.02 |     0.92 | 0.92 |
| GSPC 1d   | PnF_double      | box=2xATR%    | L        |        0.16 |         0.65 |     6.57 |              8.45 |   66.67 |      6 |     33.06 |     0.69 | 0.85 |
| GSPC 1d   | PnF_triple      | box=1xATR%    | LS       |        0.16 |         0.64 |    23.3  |              4.02 |   66.67 |      3 |     10    |     0.18 | 0.85 |
| GSPC 1d   | Renko_dao_N     | log2xATR%,N=3 | L        |        0.35 |         0.96 |    18.38 |              9.58 |   85.71 |      7 |     21.45 |     0.29 | 0.85 |
| GSPC 1d   | Renko_dem_brick | ATRx2,M=3     | LS       |        0.19 |         0.1  |     1.25 |              1.47 |   54.54 |     22 |     36.93 |     0.84 | 0.86 |
| GSPC 1h   | BL_Donchian     | N=55          | LS       |        0.88 |        -0.81 |     0.6  |             -1.85 |   17.86 |     28 |     23.43 |     0.82 | 0.86 |
| GSPC 1h   | BL_EMA          | 20/100        | L        |        1.45 |         0.55 |     0.99 |             -0.44 |   26.32 |     19 |      9.88 |     0.68 | 0.85 |
| GSPC 1h   | HA_doi_mau      | N=2           | L        |        0.54 |         0.64 |     1.12 |              0.03 |   41.53 |    183 |     10.58 |     0.54 | 0.85 |
| GSPC 1h   | HA_khong_bong   | k=1           | L        |        0.72 |         0.73 |     1.18 |              0.05 |   41.36 |    220 |      7.6  |     0.5  | 0.85 |
| GSPC 1h   | Kagi            | dao=3ATR      | L        |        1.95 |         0.44 |     1.24 |              0.1  |   38.46 |     13 |      8.04 |     0.7  | 0.85 |
| GSPC 1h   | Line_Break      | 2LB           | L        |        1    |         0.21 |     1.06 |             -0.08 |   40.28 |    144 |      7.12 |     0.62 | 0.85 |
| GSPC 1h   | PnF_double      | box=1xATR%    | L        |        0.73 |         0.35 |     1.14 |              0.23 |   40    |     15 |      8.97 |     0.74 | 0.86 |
| GSPC 1h   | PnF_triple      | box=0.5xATR%  | LS       |        0.25 |         0.29 |     1.36 |              0.5  |   35.71 |     14 |      4.44 |     0.25 | 0.85 |
| GSPC 1h   | Renko_dao_N     | ATRx2,N=1     | L        |        1.02 |        -0.28 |     0.66 |             -1.37 |   25    |     28 |     13.64 |     0.9  | 0.92 |
| GSPC 1h   | Renko_dem_brick | ATRx1,M=5     | L        |        1.51 |         0.78 |     1.58 |              0.28 |   34.78 |     23 |      3.54 |     0.33 | 0.85 |
| GC 1h     | BL_Donchian     | N=20          | L        |        1.7  |         0.95 |     1.58 |              1.05 |   41.67 |     60 |     14.82 |     0.33 | 0.85 |
| GC 1h     | BL_EMA          | 10/50         | L        |        2.19 |         0.29 |     1.07 |              0.35 |   26.8  |     97 |     25.25 |     0.58 | 0.85 |
| GC 1h     | HA_doi_mau      | N=2           | L        |        2.16 |         0.92 |     1.16 |              0.11 |   41.75 |    527 |     14.49 |     0.38 | 0.85 |
| GC 1h     | HA_khong_bong   | k=1           | L        |        2.18 |         0.22 |     1.04 |              0.03 |   33.58 |    539 |     19.11 |     0.44 | 0.85 |
| GC 1h     | Kagi            | dao=0.5ATR    | L        |        2.46 |         1.54 |     1.53 |              0.46 |   40.98 |    183 |     11.85 |     0.19 | 0.85 |
| GC 1h     | Line_Break      | 4LB           | L        |        2.52 |         0.87 |     1.34 |              0.52 |   53.26 |     92 |     17.09 |     0.34 | 0.85 |
| GC 1h     | PnF_catapult    | box=0.5xATR%  | LS       |        0.42 |         0.66 |     2.19 |              1.2  |   69.23 |     13 |      2.69 |     0.26 | 0.85 |
| GC 1h     | PnF_double      | box=0.5xATR%  | L        |        1.92 |         0.97 |     1.31 |              0.45 |   38.21 |    123 |     15.74 |     0.29 | 0.85 |
| GC 1h     | PnF_triple      | box=0.5xATR%  | L        |        1.2  |        -0.16 |     0.86 |             -0.23 |   31.58 |     19 |      5.28 |     0.7  | 0.85 |
| GC 1h     | Renko_dao_N     | ATRx0.5,N=1   | L        |        2.43 |         0.83 |     1.18 |              0.12 |   37.22 |    317 |     11.86 |     0.3  | 0.85 |
| GC 1h     | Renko_dem_brick | log1xATR%,M=3 | L        |        2.42 |         1    |     1.28 |              0.31 |   38.65 |    163 |     11.56 |     0.28 | 0.85 |
| ES 1h     | BL_Donchian     | N=55          | L        |        0.96 |        -0.09 |     0.91 |             -0.3  |   35.29 |     34 |      9.87 |     0.84 | 0.86 |
| ES 1h     | BL_EMA          | 20/100        | L        |        0.67 |         0.01 |     0.98 |             -0.11 |   29.79 |     47 |     13.5  |     0.76 | 0.86 |
| ES 1h     | HA_doi_mau      | N=1           | L        |        1.15 |         0.23 |     1.03 |              0.01 |   37.28 |    845 |     12.19 |     0.54 | 0.85 |
| ES 1h     | HA_khong_bong   | k=2           | L        |        1.63 |         0.49 |     1.11 |              0.06 |   37.47 |    355 |      6.93 |     0.49 | 0.85 |
| ES 1h     | Kagi            | dao=3ATR      | L        |        0.77 |         0.55 |     1.35 |              0.4  |   44.44 |     27 |      8.89 |     0.57 | 0.85 |
| ES 1h     | Line_Break      | 4LB           | L        |        0.01 |         0.11 |     1.01 |             -0.23 |   45.67 |    127 |      6.35 |     0.7  | 0.85 |
| ES 1h     | PnF_double      | box=0.5xATR%  | L        |        0.87 |         1.3  |     1.54 |              0.33 |   43.59 |     78 |      5.35 |     0.32 | 0.85 |
| ES 1h     | PnF_triple      | box=2xATR%    | LS       |        0.5  |        -0.2  |     0.51 |             -0.81 |   33.33 |      6 |      8.1  |     0.57 | 0.85 |
| ES 1h     | Renko_dao_N     | ATRx2,N=3     | L        |        1.28 |        -0.08 |     0.9  |             -2.1  |   29.41 |     17 |     10.38 |     0.81 | 0.86 |
| ES 1h     | Renko_dem_brick | log2xATR%,M=3 | LS       |        1.01 |        -0.59 |     0.74 |             -0.48 |   33.33 |     63 |     10.93 |     0.81 | 0.86 |

*R = lãi/lỗ mỗi lệnh chia cho ATR lúc vào lệnh. MaxDD tính trên lợi nhuận cộng dồn theo % giá, với 1 hợp đồng.*

### 2c. Khớp giá "ảo" so với khớp giá thật (OOS, chế độ Long/Short, tham số nhạy nhất)

| ticker   | tf   | method      |   PF ẢO |   PF THẬT |   sharpe ẢO |   sharpe THẬT |   tot_ret_pct ẢO |   tot_ret_pct THẬT |   win ẢO |   win THẬT |
|:---------|:-----|:------------|--------:|----------:|------------:|--------------:|-----------------:|-------------------:|---------:|-----------:|
| ES=F     | 15m  | HA_doi_mau  |    2.92 |      0.91 |       12.44 |         -1.08 |            29.97 |              -2.07 |    47.64 |      33.86 |
| ES=F     | 15m  | Renko_dao_N |    1.92 |      1.18 |        7.54 |          2.5  |            14.78 |               4.25 |    37.77 |      31.47 |
| ES=F     | 1d   | HA_doi_mau  |    3.17 |      0.85 |        3.2  |         -0.15 |           427.23 |             -29.2  |    50.23 |      38.89 |
| ES=F     | 1d   | Renko_dao_N |    1.59 |      0.89 |        1.04 |          0.01 |           163.91 |               2.4  |    41.33 |      35.66 |
| ES=F     | 1h   | HA_doi_mau  |    3.11 |      0.93 |       10.77 |         -0.63 |           167.91 |             -11.69 |    48.11 |      34.5  |
| ES=F     | 1h   | Renko_dao_N |    1.53 |      0.92 |        3.21 |         -0.61 |            50.26 |             -10.74 |    41.19 |      35.22 |
| GC=F     | 15m  | HA_doi_mau  |    2.9  |      0.8  |       20.22 |         -3.28 |            42.05 |              -8.41 |    46.35 |      32.03 |
| GC=F     | 15m  | Renko_dao_N |    1.37 |      0.86 |        4.51 |         -1.47 |            11.86 |              -4.49 |    39.15 |      34.19 |
| GC=F     | 1d   | HA_doi_mau  |    3.17 |      0.95 |        2.97 |         -0.13 |           411.45 |             -24.21 |    45.23 |      35.98 |
| GC=F     | 1d   | Renko_dao_N |    2.53 |      1.24 |        1.41 |          0.19 |           214.52 |              34.38 |    48.87 |      37.59 |
| GC=F     | 1h   | HA_doi_mau  |    3.5  |      1.03 |       12.19 |          0.35 |           368.99 |              12.3  |    47.66 |      34.15 |
| GC=F     | 1h   | Renko_dao_N |    1.92 |      1.14 |        4.57 |          0.84 |           146.96 |              29.93 |    43.31 |      35.75 |
| ^GSPC    | 1d   | HA_doi_mau  |    2.39 |      0.84 |        2.37 |         -0.3  |           337.96 |             -50.95 |    43.86 |      36.2  |
| ^GSPC    | 1d   | Renko_dao_N |    1.45 |      0.83 |        0.92 |         -0.18 |           145.5  |             -31.23 |    41.54 |      34.36 |
| ^GSPC    | 1h   | HA_doi_mau  |    1.9  |      0.86 |        4.51 |         -0.93 |            67.95 |             -16.72 |    42.35 |      36.16 |
| ^GSPC    | 1h   | Renko_dao_N |    1.52 |      0.86 |        2.12 |         -0.66 |            34.78 |             -11.49 |    43.28 |      35.96 |

**Trung vị trên toàn lưới tham số (cả IS và OOS):**

| PP              | Khung   |   Sharpe ảo |   Sharpe thật |   Chênh |   PF ảo |   PF thật |
|:----------------|:--------|------------:|--------------:|--------:|--------:|----------:|
| HA_doi_mau      | 15m     |        4.62 |         -0.95 |    4.56 |    1.4  |      0.91 |
| HA_doi_mau      | 1d      |        0.64 |         -0.15 |    0.48 |    1.37 |      0.91 |
| HA_doi_mau      | 1h      |        2.66 |          0.41 |    1.43 |    1.44 |      1.06 |
| HA_khong_bong   | 15m     |        7.41 |         -0.99 |    8.81 |    2.08 |      0.9  |
| HA_khong_bong   | 1d      |        1.42 |         -0.16 |    1.62 |    2.12 |      0.88 |
| HA_khong_bong   | 1h      |        4.97 |          0.63 |    3.93 |    2.5  |      1.1  |
| Kagi            | 15m     |       -1.12 |         -1    |    0.04 |    0.82 |      0.8  |
| Kagi            | 1d      |        0.16 |          0.16 |    0    |    1.29 |      1.34 |
| Kagi            | 1h      |        0.45 |          0.47 |   -0.05 |    1.22 |      1.19 |
| Line_Break      | 15m     |       -0.7  |         -0.69 |   -0.1  |    0.9  |      0.91 |
| Line_Break      | 1d      |       -0.18 |         -0.16 |    0    |    0.86 |      0.85 |
| Line_Break      | 1h      |        0.09 |          0.09 |   -0.04 |    1.01 |      1.02 |
| PnF_catapult    | 15m     |       -2.63 |         -2.03 |   -0.05 |    0    |      0    |
| PnF_catapult    | 1d      |       -0.09 |         -0.05 |   -0.05 |    0.16 |      0.25 |
| PnF_catapult    | 1h      |       -0.55 |         -0.34 |   -0.12 |    0.28 |      0.54 |
| PnF_double      | 15m     |       -2.38 |         -1.22 |   -1.51 |    0.46 |      0.75 |
| PnF_double      | 1d      |        0.02 |          0.19 |   -0.19 |    0.99 |      1.47 |
| PnF_double      | 1h      |        0.04 |          0.69 |   -0.65 |    1    |      1.31 |
| PnF_triple      | 15m     |       -0.8  |          0    |   -0.52 |    0.27 |      0.6  |
| PnF_triple      | 1d      |       -0    |          0.08 |   -0.1  |    0.71 |      1.4  |
| PnF_triple      | 1h      |       -0.24 |          0.07 |   -0.31 |    0.74 |      1.05 |
| Renko_dao_N     | 15m     |        1.65 |         -0.34 |    2.37 |    1.36 |      0.9  |
| Renko_dao_N     | 1d      |        0.53 |          0.16 |    0.36 |    1.8  |      1.17 |
| Renko_dao_N     | 1h      |        1.47 |          0.37 |    1.07 |    1.71 |      1.12 |
| Renko_dem_brick | 15m     |        2.48 |          0.04 |    2.15 |    1.63 |      1    |
| Renko_dem_brick | 1d      |        0.4  |          0.03 |    0.34 |    1.83 |      1.05 |
| Renko_dem_brick | 1h      |        1.33 |          0.22 |    1.14 |    1.78 |      1.08 |

→ **Ảo lớn nhất ở Heikin Ashi.** Ví dụ HA đổi màu trên ES 1h: khớp ảo cho Sharpe 10,8, PF 3,1; khớp thật cho Sharpe −0,6, PF 0,93. Renko cũng bị thổi phồng: Sharpe tăng khoảng 1–2, PF lên khoảng 1,5–1,9.
PnF, Kagi và Line Break dựng từ giá đóng cửa nên bản ảo không đẹp hơn.
Trên TradingView, backtest trên chart Renko/HA mà không bật "Fill orders using standard OHLC" sẽ rơi đúng vào cái bẫy này.

## HẠN CHẾ
- **ES=F nến ngày** là chuỗi liên tục chưa điều chỉnh roll, nên có bước nhảy khi chuyển hợp đồng mỗi quý. ^GSPC dùng làm kiểm chứng.
- Dữ liệu 1h chỉ khoảng 2,4 năm. Dữ liệu 15m chỉ khoảng 60 ngày, nên chỉ để tham khảo.
- **Bootstrap giữ nguyên drift của OOS**, nên p đo phần lợi nhuận "vượt trên drift". Hệ chỉ mua có lời là do thị trường tăng, không phải do chart.
- Brick, cột và đường dựng từ giá đóng cửa. Dựng từ high/low sẽ cho thêm tín hiệu nhưng phải giả định thứ tự giá trong nến, rất dễ tạo ảo.

## FILE
- Script: `test_f_spiral.py`, `analyze_f.py`, `test_g_charts.py`, `analyze_g.py`, `make_summary6.py`, `common6.py`.
- `results6/`:
  - Phần 1: `spiral_tests.csv`, `spiral_acc_*.npy`.
  - Phần 2: `charts_all.csv` (toàn lưới, cả khớp thật lẫn khớp ảo), `charts_best_IS_to_OOS.csv`, `charts_boot.csv`, `charts_fake_vs_real.csv`.