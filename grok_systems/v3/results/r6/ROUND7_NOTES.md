## Vòng 7 — Kịch bản vốn 100k, và danh mục chỉ Vàng / chỉ SP500
Cập nhật: 2026-11-28 15:30 (Asia/Saigon). Khóa hedge cuối tuần (W) BẬT cho mọi basket. Lot làm tròn bước sàn: vàng 0.01, chỉ số 0.1. DD = DD gộp equity MT5 (scale tuyến tính từ deals tick thật đã có; không chạy lại Strategy Tester). Lot robust = trung bình lot tối ưu trên nửa A và nửa B, rồi scale cho vừa ràng buộc DD/spread×2/gap-5%. Mọi kịch bản dưới đây lãi **6/6 tháng**.

So với vốn 40k (vòng 6b): gần như tuyến tính ×2.5 (cùng hệ, lot × ~2.5). Lợi ích đa dạng hóa: cùng vốn 100k, danh mục **chung hai tài sản** có DD thấp hơn rõ và lãi cao hơn danh mục chỉ một tài sản.

**Khuyến nghị thực tế:** Cân bằng hoặc Mạnh tay ×1.0; chạy demo nửa lot trước. Các bậc nhân lot (×1.4/×1.7/×5) chỉ thoả DD<20% trên lịch sử — gap 5% trong phiên có thể vượt 100% vốn, spread×2 đẩy DD lên ~20–29%.

### 12.1 Cả hai tài sản, vốn 100k (15 hệ greedy; đánh tay = 10 scalp vàng)
| Kịch bản | MT5 net 6T | DD MT5 | A / B | Nửa lot | Gap-5% (Py) | spread×2 DD (Py) |
|---|---|---|---|---|---|---|
| **An toàn** | +96,123 | 3.7% | 44.7k / 51.4k | +48.1k / 1.9% | 28.4% | 5.0% |
| **Cân bằng** | +161,631 | 6.8% | 75.0k / 86.6k | +80.8k / 3.4% | 48.3% | 8.4% |
| **Mạnh tay** | +304,204 | 11.0% | 139.3k / 164.9k | +152.1k / 5.5% | 98.8% | 16.9% |
| Mạnh tay ×1.4 | +426,366 | 15.5% | 195.1k / 230.9k | | ~138% | ~24% |
| Mạnh tay ×1.7 | +517,672 | 18.7% | 236.9k / 280.3k | | ~168% | ~29% |
| **Đánh tay** xs1–xs10 | +72,846 | 3.6% | 33.6k / 39.2k | +36.4k / 1.8% | 29.2% | 4.3% |
| Đánh tay ×3 | +218,538 | 10.8% | | | ~88% | |
| Đánh tay ×5 | +364,231 | 18.0% | | | ~146% | |

**Lot An toàn / Cân bằng / Mạnh tay / Mạnh tay ×1.7** (15 hệ):
| Hệ | An toàn | Cân bằng | Mạnh tay | ×1.7 |
|---|---|---|---|---|
| g2 | 0.05 | 0.09 | 0.20 | 0.34 |
| xs10 | 0.24 | 0.40 | 0.79 | 1.34 |
| x1 | 0.05 | 0.07 | 0.12 | 0.20 |
| xs6 | 0.30 | 0.52 | 0.99 | 1.68 |
| xs4 | 0.15 | 0.26 | 0.51 | 0.87 |
| u15 | 1.6 | 2.4 | 4.4 | 7.5 |
| xs2 | 0.24 | 0.31 | 0.81 | 1.38 |
| xs7 | 0.23 | 0.39 | 0.96 | 1.63 |
| u12 | 6.5 | 8.1 | 7.7 | 13.1 |
| xs3 | 0.14 | 0.33 | 0.66 | 1.12 |
| xs1 | 0.20 | 0.38 | 0.85 | 1.45 |
| g7 | 0.01 | 0.02 | 0.05 | 0.09 |
| u13 | 3.2 | 5.2 | 7.7 | 13.1 |
| xs5 | 0.24 | 0.40 | 0.80 | 1.36 |
| g5 | 0.03 | 0.06 | 0.07 | 0.12 |

**Lot đánh tay** (10 scalp vàng, vốn 100k): xs1 0.30, xs2 0.21, xs3 0.17, xs4 0.15, xs5 0.24, xs6 0.16, xs7 0.35, xs8 0.28, xs9 0.15, xs10 0.22. Bậc ×3 / ×5: nhân tất cả rồi làm tròn 0.01.

Tháng (An toàn, USD): 18.8k, 18.0k, 13.0k, 10.9k, 14.6k, 20.7k.

### 12.2 Chỉ Vàng, vốn 100k và 50k (8 hệ greedy: g2, xs10, x1, xs6, xs4, xs7, xs2, gp2)
Tối ưu riêng (không lấy subset của danh mục chung). gp2 vào vì không còn các hệ SP500 để đa dạng hóa. **Mạnh tay gốc** vượt DD 20% trên MT5 (100k: 21.4%; 50k: 20.7%) dù Python báo 18.2%/17.6% — đã cắt lot (×0.906 / ×0.938) để DD MT5 = 19.3%.

| Vốn | Kịch bản | MT5 net | DD MT5 | A / B | Gap-5% | sx2 DD | Lot |
|---|---|---|---|---|---|---|---|
| **100k** | An toàn | +74,963 | 6.9% | 34.7k / 40.3k | 29.3% | 7.9% | g2 .10, xs10 .42, x1 .05, xs6 .28, xs4 .26, xs7 .46, xs2 .32, gp2 .05 |
| 100k | Cân bằng | +126,015 | 11.7% | 58.4k / 67.6k | 49.2% | 13.7% | g2 .17, xs10 .70, x1 .09, xs6 .46, xs4 .43, xs7 .78, xs2 .54, gp2 .08 |
| 100k | **Mạnh tay (đã cắt)** | +208,221 | 19.3% | 96.4k / 111.8k | 82.2% | 20.9% | g2 .25, xs10 1.18, x1 .14, xs6 .81, xs4 .72, xs7 1.26, xs2 .91, gp2 .14 |
| 100k | Đánh tay xs1–xs10 | +71,064 | 3.5% | 33.1k / 38.0k | 29.2% | 4.2% | xs1 .29, xs2 .20, xs3 .14, xs4 .15, xs5 .24, xs6 .16, xs7 .38, xs8 .29, xs9 .15, xs10 .22 |
| 100k | Đánh tay ×5 | +355,318 | 17.6% | | ~146% | | nhân ×5, làm tròn 0.01 |
| **50k** | An toàn | +36,069 | 5.5% | 16.6k / 19.4k | 28.0% | 7.8% | g2 .05, xs10 .21, x1 .02, xs6 .14, xs4 .13, xs7 .23, xs2 .16, gp2 .02 |
| 50k | Cân bằng | +61,656 | 11.0% | 28.5k / 33.1k | 48.3% | 12.9% | g2 .08, xs10 .35, x1 .04, xs6 .23, xs4 .21, xs7 .39, xs2 .27, gp2 .04 |
| 50k | **Mạnh tay (đã cắt)** | +106,622 | 19.3% | 49.3k / 57.3k | 84.3% | 21.6% | g2 .13, xs10 .61, x1 .07, xs6 .41, xs4 .37, xs7 .65, xs2 .47, gp2 .07 |
| 50k | Đánh tay | +34,876 | 3.5% | 16.2k / 18.7k | 28.7% | 4.1% | xs1 .14, xs2 .10, xs3 .07, xs4 .07, xs5 .12, xs6 .08, xs7 .19, xs8 .14, xs9 .07, xs10 .11 |
| 50k | Đánh tay ×5 | +174,378 | 17.3% | | | | nhân ×5, làm tròn 0.01 |

### 12.3 Chỉ SP500, vốn 100k và 50k (5 hệ greedy: u13, u12, u2, up1, up2)
Tối ưu riêng. up1/up2 vào (tập con của u1/u7/u6+u12) vì greedy một tài sản chọn chúng thay cho hệ cha. **Không có scalp US500 pass.** Lot Mạnh tay 100k khá lớn (u12 22.6, u13 21.0) — cần kiểm tra trần lot của sàn trước khi chạy. Tháng 8 yếu nhất nhưng vẫn dương.

| Vốn | Kịch bản | MT5 net | DD MT5 | A / B | Gap-5% | sx2 DD | Lot (u13 / u12 / u2 / up1 / up2) |
|---|---|---|---|---|---|---|---|
| **100k** | An toàn | +49,551 | 5.5% | 20.2k / 29.4k | 29.6% | 7.7% | 6.8 / 5.2 / 4.0 / 5.6 / 6.6 |
| 100k | Cân bằng | +81,769 | 9.4% | 33.1k / 48.7k | 49.6% | 12.6% | 11.0 / 8.5 / 6.9 / 9.4 / 10.7 |
| 100k | Mạnh tay | +167,946 | 18.8% | 69.0k / 99.0k | 99.8% | 24.4% | 21.0 / 22.6 / 12.6 / 19.0 / 20.3 |
| **50k** | An toàn | +24,776 | 5.5% | 10.1k / 14.7k | 29.6% | 7.7% | 3.4 / 2.6 / 2.0 / 2.8 / 3.3 |
| 50k | Cân bằng | +40,645 | 9.3% | 16.5k / 24.2k | 49.2% | 12.5% | 5.5 / 4.2 / 3.4 / 4.7 / 5.3 |
| 50k | Mạnh tay | +83,900 | 18.8% | 34.4k / 49.5k | 99.8% | 24.4% | 10.5 / 11.3 / 6.3 / 9.5 / 10.1 |

### 12.4 Cách tái lập
```
cd v3/code && python opt8.py          # → results/r6/opt8.json (tái dùng U6.pkl, W bật)
cd v3/r4  && python joint8.py         # → r4/joint8.json (scale deals MT5, cap truyền vào, cắt lot nếu DD>19.5%)
```
File: `results/r6/opt8.json`, `r4/joint8.json`, `results/r6/ROUND7_NOTES.md`.

### 12.5 Caveat thêm (vòng 7)
1. Không chạy lại tester MT5: số joint là scale tuyến tính từ deals đã xác minh 100% real ticks (sai số 1–6% như trước). Riêng Mạnh tay chỉ-vàng, DD MT5 lệch lên trên Python nên đã cắt lot.
2. Gap 5% trong phiên không chặn được bằng SL — chỉ giảm bằng lot. Mạnh tay (chung hoặc một tài sản) có gap ≈ 82–100% vốn (bậc nhân còn cao hơn).
3. Vẫn 6 tháng mẫu, multiple testing; cần forward demo nửa lot trước khi tăng.
