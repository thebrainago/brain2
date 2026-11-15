# Kết quả kiểm định 2: Gann Sq9 từ đỉnh/đáy LỚN (giá) và Sq9 THỜI GIAN

Dữ liệu daily Yahoo: **GC=F từ 01/2008** (trước 2008 khoảng 35% số nến có H = L, dữ liệu hỏng nên bỏ), **ES=F và ^GSPC từ 2000** đến 13/11/2026.
Chia mẫu theo ngày xác nhận neo: **trong mẫu (IS) trước 2016**, **ngoài mẫu (OOS) từ 2016**. Khung 1h không dùng vì chỉ có khoảng 2 năm, quá ngắn cho đỉnh/đáy lớn.

**Neo lớn** (không nhìn trước: chỉ dùng sau khi đã xác nhận): pivot 20/20 và 60/60 (đỉnh và đáy), ATH (pivot 20/20 là đỉnh cao nhất tính tới lúc đó),
đỉnh/đáy năm (biết vào phiên đầu năm sau). Mỗi pivot chỉ tính 1 lần khi gộp.
Số neo: GC 149, ES 194, ^GSPC 204.

---
## TEST A: Mức giá Sq9 từ neo lớn
Mức ở các góc 45°..1440° (4 vòng, 32 mức mỗi phía), sống 250 phiên. Khoảng chạm ±0.2 ATR(14).
Giữ 5/10 = không có close nào xuyên qua mức trong 5/10 phiên sau khi chạm. Hồi 1/2 = bật ngược ≥ 1/2 ATR trong 10 phiên, trước khi bị phá.

**Đối chứng chính (ctrlA)**: cùng neo, góc lệch ngẫu nhiên ±22.5°. Đây là phép thử "góc Gann có đặc biệt không".
Ô bảng ghi Sq9 / đối chứng (hiệu, p). p lấy bằng bootstrap theo cụm neo, 2000 lần, hai phía.

| ticker | period | touch | hold5 | hold10 | rev1 | rev2 |
|---|---|---|---|---|---|---|
| ES=F | ALL | 36.5 / 36.4 (+0.1, p=0.150) | 40.8 / 40.6 (+0.2, p=0.692) | 29.4 / 29.2 (+0.3, p=0.537) | 51.6 / 51.0 (+0.6, p=0.235) | 31.3 / 31.0 (+0.3, p=0.406) |
| ES=F | IS | 27.8 / 27.7 (+0.0, p=0.582) | 42.0 / 42.2 (-0.1, p=0.834) | 30.2 / 30.3 (-0.1, p=0.839) | 53.2 / 52.7 (+0.5, p=0.551) | 31.9 / 32.0 (-0.1, p=0.882) |
| ES=F | OOS | 49.7 / 49.6 (+0.1, p=0.104) | 39.7 / 39.2 (+0.5, p=0.416) | 28.6 / 28.1 (+0.5, p=0.306) | 50.0 / 49.3 (+0.7, p=0.241) | 30.5 / 29.9 (+0.6, p=0.246) |
| GC=F | ALL | 31.0 / 30.9 (+0.0, p=0.556) | 36.9 / 36.0 (+1.0, p=0.068) | 27.8 / 26.8 (+1.0, p=0.024) | 46.0 / 45.2 (+0.8, p=0.154) | 28.7 / 28.1 (+0.6, p=0.242) |
| GC=F | IS | 29.9 / 29.8 (+0.1, p=0.576) | 33.2 / 32.4 (+0.8, p=0.331) | 28.1 / 26.3 (+1.8, p=0.005) | 41.7 / 41.0 (+0.8, p=0.421) | 29.5 / 28.0 (+1.5, p=0.064) |
| GC=F | OOS | 31.7 / 31.6 (+0.0, p=0.599) | 39.5 / 38.5 (+1.0, p=0.118) | 27.6 / 27.1 (+0.5, p=0.466) | 48.7 / 48.1 (+0.6, p=0.419) | 28.2 / 28.3 (-0.1, p=0.913) |
| ^GSPC | ALL | 35.5 / 35.5 (+0.0, p=0.650) | 34.9 / 34.9 (+0.0, p=0.975) | 25.4 / 25.3 (+0.1, p=0.776) | 45.8 / 45.8 (-0.0, p=0.998) | 29.5 / 29.2 (+0.3, p=0.506) |
| ^GSPC | IS | 28.0 / 27.9 (+0.1, p=0.125) | 37.5 / 37.4 (+0.1, p=0.847) | 27.9 / 27.5 (+0.4, p=0.481) | 48.4 / 48.2 (+0.2, p=0.744) | 31.7 / 31.3 (+0.4, p=0.472) |
| ^GSPC | OOS | 47.8 / 47.9 (-0.1, p=0.191) | 32.2 / 32.4 (-0.2, p=0.690) | 23.0 / 23.2 (-0.2, p=0.622) | 43.1 / 43.5 (-0.4, p=0.534) | 27.1 / 27.0 (+0.1, p=0.899) |

**Đối chứng phụ (randAnc)**: neo ngẫu nhiên (high/low của một phiên ngẫu nhiên) với đúng góc Sq9. Bảng ghi hiệu Sq9 − randAnc.

| ticker | period | touch | hold5 | hold10 | rev1 | rev2 |
|---|---|---|---|---|---|---|
| ES=F | ALL | -0.3 (p=0.807) | +1.5 (p=0.093) | +2.2 (p=0.034) | +1.8 (p=0.071) | +2.0 (p=0.027) |
| ES=F | IS | -10.0 (p=0.001) | +2.5 (p=0.044) | +2.9 (p=0.018) | +3.2 (p=0.011) | +2.5 (p=0.027) |
| ES=F | OOS | +14.3 (p=0.001) | +0.7 (p=0.615) | +1.4 (p=0.365) | +0.5 (p=0.782) | +1.1 (p=0.414) |
| GC=F | ALL | -1.6 (p=0.132) | +1.9 (p=0.110) | +1.7 (p=0.099) | +0.9 (p=0.428) | +1.1 (p=0.265) |
| GC=F | IS | -2.5 (p=0.101) | -0.6 (p=0.693) | +3.5 (p=0.012) | -2.4 (p=0.170) | +2.9 (p=0.040) |
| GC=F | OOS | -1.2 (p=0.462) | +3.7 (p=0.019) | +0.5 (p=0.706) | +3.2 (p=0.024) | -0.2 (p=0.907) |
| ^GSPC | ALL | -0.5 (p=0.707) | +0.4 (p=0.684) | +0.5 (p=0.646) | +0.1 (p=0.963) | +0.3 (p=0.780) |
| ^GSPC | IS | -8.9 (p=0.001) | +3.0 (p=0.005) | +3.0 (p=0.007) | +2.6 (p=0.016) | +2.5 (p=0.020) |
| ^GSPC | OOS | +13.4 (p=0.001) | -2.6 (p=0.095) | -2.4 (p=0.152) | -3.1 (p=0.057) | -2.3 (p=0.149) |

- So với ctrlA (cùng neo, khác góc): mọi hiệu số nằm trong khoảng ±2 điểm %. Có 12/150 phép p < 0.05 (kỳ vọng do may rủi khoảng 7.5), nhưng **không phép nào qua được FDR hay Bonferroni**.
  Phép mạnh nhất là GC giữ 10 phiên IS +1.8 (p = 0.005), sang OOS chỉ còn +0.45 (p = 0.47), tức là **không lặp lại**.
- So với randAnc: chênh lệch tỷ lệ chạm đổi dấu giữa hai giai đoạn (IS −9 đến −10, OOS +13 đến +14). Đó là hiệu ứng xu hướng thị trường, không phải hiệu ứng góc.
  Hold và hồi của neo thật cao hơn neo ngẫu nhiên khoảng +2 đến +3 điểm ở IS, nhưng OOS không lặp lại (^GSPC OOS còn âm).
  Nếu có thì đây là tác dụng của việc dùng **đỉnh/đáy thật** làm neo, không phải của các góc Sq9, vì cùng neo đó các góc lệch ±22.5° cho kết quả y hệt.
- **Kết luận Test A: KHÔNG có edge của góc Sq9.**

---
## TEST B: Sq9 thời gian
Mục tiêu tính từ phiên pivot lớn, chỉ lấy mục tiêu nằm **sau** ngày xác nhận và không quá 400. Có 4 biến thể:
- V1a: cùng nan hoa với giá pivot (√n ≡ √P mod 2).
- V1b: chữ thập 90° tính từ vị trí giá pivot (mod 0.5).
- V2: các số trên 8 nan hoa Sq9 ((2k+1)², 4k²+1, 4k²±2k+1, 4k²±k+1, 4k²±3k+1).
- V3: giá ↔ thời gian (|Sq9(giá quy về 100–1000, góc) − giá|).

Đếm theo phiên giao dịch (bars) và theo ngày lịch (cal). "Trúng" = có pivot nhỏ 5/5 trong ±T phiên/ngày quanh mục tiêu.
Baseline là hoán vị 2000 lần: dời cả tập mục tiêu của mỗi neo một đoạn ngẫu nhiên từ 2T+1 đến 30 (giữ nguyên khoảng cách giữa các mục tiêu). p là một phía.

Bảng dưới là T = 1, mỗi ô ghi %trúng / %baseline, p. Bảng đầy đủ có cả T = 2 trong `results2/testB_time_results.csv`.

| ticker | unit | variant | ALL | IS | OOS |
|---|---|---|---|---|---|
| ES=F | bars | V1a | 34.0/33.5 p=0.323 | 34.0/34.2 p=0.588 | 34.1/32.3 p=0.157 |
| ES=F | bars | V1b | 31.9/33.5 p=0.998 | 32.4/34.2 p=0.994 | 31.2/32.4 p=0.928 |
| ES=F | bars | V2 | 33.9/33.4 p=0.064 | 35.2/34.1 p=0.009 | 32.1/32.4 p=0.716 |
| ES=F | bars | V3 | 32.7/33.4 p=0.957 | 33.7/34.0 p=0.768 | 31.4/32.4 p=0.962 |
| ES=F | cal | V1a | 22.2/23.2 p=0.822 | 24.2/23.6 p=0.341 | 19.4/22.7 p=0.976 |
| ES=F | cal | V1b | 23.3/23.3 p=0.523 | 24.1/23.8 p=0.333 | 22.1/22.6 p=0.744 |
| ES=F | cal | V2 | 23.5/23.4 p=0.313 | 24.3/23.9 p=0.125 | 22.4/22.7 p=0.769 |
| ES=F | cal | V3 | 23.4/23.3 p=0.409 | 23.7/23.8 p=0.591 | 22.9/22.6 p=0.276 |
| GC=F | bars | V1a | 36.8/34.4 p=0.035 | 34.6/33.7 p=0.330 | 38.3/34.9 p=0.025 |
| GC=F | bars | V1b | 35.2/34.5 p=0.143 | 32.7/33.7 p=0.832 | 36.9/35.1 p=0.016 |
| GC=F | bars | V2 | 34.5/34.5 p=0.504 | 33.5/33.6 p=0.607 | 35.3/35.2 p=0.420 |
| GC=F | bars | V3 | 34.9/34.6 p=0.225 | 33.6/33.7 p=0.534 | 35.7/35.2 p=0.137 |
| GC=F | cal | V1a | 23.3/24.0 p=0.694 | 22.5/23.3 p=0.658 | 23.9/24.4 p=0.612 |
| GC=F | cal | V1b | 23.6/24.0 p=0.758 | 23.0/23.5 p=0.735 | 24.0/24.3 p=0.649 |
| GC=F | cal | V2 | 24.2/24.0 p=0.253 | 23.8/23.5 p=0.258 | 24.5/24.3 p=0.354 |
| GC=F | cal | V3 | 24.0/24.0 p=0.463 | 23.4/23.6 p=0.669 | 24.4/24.2 p=0.313 |
| ^GSPC | bars | V1a | 33.2/33.5 p=0.609 | 34.3/33.7 p=0.336 | 31.4/33.1 p=0.829 |
| ^GSPC | bars | V1b | 34.1/33.4 p=0.117 | 34.9/33.7 p=0.037 | 32.7/33.0 p=0.654 |
| ^GSPC | bars | V2 | 34.2/33.5 p=0.009 | 34.5/33.8 p=0.021 | 33.7/33.0 p=0.108 |
| ^GSPC | bars | V3 | 32.8/33.3 p=0.889 | 33.1/33.4 p=0.732 | 32.4/33.1 p=0.864 |
| ^GSPC | cal | V1a | 23.8/23.0 p=0.234 | 24.8/23.0 p=0.093 | 22.1/22.9 p=0.699 |
| ^GSPC | cal | V1b | 24.0/23.1 p=0.029 | 24.1/23.2 p=0.067 | 23.9/23.0 p=0.128 |
| ^GSPC | cal | V2 | 23.4/23.2 p=0.197 | 23.6/23.2 p=0.177 | 23.1/23.0 p=0.437 |
| ^GSPC | cal | V3 | 23.1/23.1 p=0.436 | 23.2/23.1 p=0.381 | 23.0/23.1 p=0.553 |

- Có 144 phép (3 mã × 2 đơn vị × 4 biến thể × T 1/2 × ALL/IS/OOS). 15 phép p < 0.05, **0 phép qua FDR, 0 phép qua Bonferroni**.
  Hiệu số lớn nhất chỉ khoảng +2 đến +3.5 điểm trên nền 34–54%. Các phép cũng phụ thuộc nhau (T = 1 và 2 chồng nhau, ES và ^GSPC gần như cùng một chuỗi).
- Không phép nào đạt p < 0.05 ở **cả IS lẫn OOS**. Trong 5 phép có p < 0.05 ở IS, chỉ 2 phép giữ cùng dấu ở OOS.
  Vàng V1a/V1b (bars) có tín hiệu ở OOS (p 0.005–0.03) nhưng IS thì không. Đáng theo dõi tiếp, chưa phải bằng chứng.
- **Hợp lưu giá + thời gian** (pivot nhỏ trúng mục tiêu thời gian, bars, T = 1, gộp V1a–V3):

| ticker | pivots | at_target | near_sq9_at_target | near_sq9_not_target | near_mid_at_target | p_target_vs_not | p_sq9_vs_mid |
|---|---|---|---|---|---|---|---|
| ES=F | 8446 | 5893 | 47.5479 | 44.7709 | 49.3467 | 0.01 | 0.9678 |
| GC=F | 6824 | 4799 | 40.9044 | 36.5926 | 41.8212 | 0.0005 | 0.7955 |
| ^GSPC | 8865 | 6261 | 42.4693 | 39.8618 | 43.4276 | 0.0123 | 0.8462 |

  Pivot trúng mục tiêu thời gian có vẻ gần mức Sq9 hơn (p 0.0005–0.012). Nhưng mức lệch 22.5° (near_mid) ở cùng nhóm đó còn cao hơn,
  và so trực tiếp Sq9 với mức lệch thì p = 0.80–0.97. Nghĩa là chênh lệch đến từ chỗ mục tiêu thời gian dày ở gần neo, nơi giá cũng gần neo và các mức dày hơn, **không phải từ góc Sq9**.
  Ngoài ra khoảng 70% số pivot rơi vào một mục tiêu nào đó, vì 4 biến thể gộp lại quá dày nên phép thử này yếu.
- **Kết luận Test B: KHÔNG có edge. Riêng thời gian Sq9 trên vàng là tín hiệu rất yếu, chưa lặp lại được giữa IS và OOS.**

---
## Tóm tắt
| Phép thử | Kết luận | Ngoài mẫu |
|---|---|---|
| A. Mức giá Sq9 từ neo lớn vs góc lệch ±22.5° | Không có edge (hiệu < 2 điểm, 0 phép qua FDR) | Không lặp lại |
| A. vs neo ngẫu nhiên | Khác biệt do chế độ thị trường hoặc do bản thân đỉnh/đáy, không phải do góc | Đổi dấu |
| B. Sq9 thời gian (4 biến thể × bars/cal) | Không có edge (0/144 qua FDR) | Không lặp lại |
| B. Hợp lưu giá + thời gian | Không có edge (Sq9 không hơn mức lệch) | – |

## Tái chạy
```
cd tools/kiem_dinh/gann_sq9
.venv/bin/python test_a_major_price.py   # results2/testA_results.csv, testA_clusters.csv
.venv/bin/python test_b_sq9_time.py      # results2/testB_time_results.csv, testB_confluence*.csv
.venv/bin/python make_summary2.py        # KET_QUA_2_vi.md
```
Lưu ý: kết quả daily của vàng trong KET_QUA_vi.md (lần 1) dùng dữ liệu từ 2000, gồm cả các nến H = L bị hỏng. Kết luận lần 1 không đổi (Sq9 vẫn ≈ ngẫu nhiên).
