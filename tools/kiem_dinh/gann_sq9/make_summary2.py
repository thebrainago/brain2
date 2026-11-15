# Tạo KET_QUA_2_vi.md từ results2/
import pandas as pd
A = pd.read_csv("results2/testA_results.csv"); B = pd.read_csv("results2/testB_time_results.csv"); C = pd.read_csv("results2/testB_confluence.csv")
def md(df):
    cols = list(df.columns); s = "| " + " | ".join(map(str, cols)) + " |\n|" + "---|" * len(cols) + "\n"
    for _, r in df.iterrows(): s += "| " + " | ".join(str(r[c]) for c in cols) + " |\n"
    return s
a = A[(A.set == "ALL_MAJOR") & (A.baseline == "ctrlA")].copy()
a["cell"] = a.apply(lambda r: f"{r.sq9:.1f} / {r.base:.1f} ({r['diff']:+.1f}, p={r.p:.3f})", axis=1)
ta = a.pivot_table(index=["ticker", "period"], columns="metric", values="cell", aggfunc="first")[["touch", "hold5", "hold10", "rev1", "rev2"]].reset_index()
r = A[(A.set == "ALL_MAJOR") & (A.baseline == "randAnc")].copy()
r["cell"] = r.apply(lambda x: f"{x['diff']:+.1f} (p={x.p:.3f})", axis=1)
tr = r.pivot_table(index=["ticker", "period"], columns="metric", values="cell", aggfunc="first")[["touch", "hold5", "hold10", "rev1", "rev2"]].reset_index()
b = B.copy(); b["cell"] = b.apply(lambda x: f"{x.hit:.1f}/{x.base:.1f} p={x.p:.3f}", axis=1)
tb = b[b["T"] == 1].pivot_table(index=["ticker", "unit", "variant"], columns="period", values="cell", aggfunc="first")[["ALL", "IS", "OOS"]].reset_index()
ca = A[A.baseline == "ctrlA"]
txt = f"""# Kết quả kiểm định 2: Gann Sq9 từ đỉnh/đáy LỚN (giá) và Sq9 THỜI GIAN

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

{md(ta)}
**Đối chứng phụ (randAnc)**: neo ngẫu nhiên (high/low của một phiên ngẫu nhiên) với đúng góc Sq9. Bảng ghi hiệu Sq9 − randAnc.

{md(tr)}
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

{md(tb)}
- Có 144 phép (3 mã × 2 đơn vị × 4 biến thể × T 1/2 × ALL/IS/OOS). 15 phép p < 0.05, **0 phép qua FDR, 0 phép qua Bonferroni**.
  Hiệu số lớn nhất chỉ khoảng +2 đến +3.5 điểm trên nền 34–54%. Các phép cũng phụ thuộc nhau (T = 1 và 2 chồng nhau, ES và ^GSPC gần như cùng một chuỗi).
- Không phép nào đạt p < 0.05 ở **cả IS lẫn OOS**. Trong 5 phép có p < 0.05 ở IS, chỉ 2 phép giữ cùng dấu ở OOS.
  Vàng V1a/V1b (bars) có tín hiệu ở OOS (p 0.005–0.03) nhưng IS thì không. Đáng theo dõi tiếp, chưa phải bằng chứng.
- **Hợp lưu giá + thời gian** (pivot nhỏ trúng mục tiêu thời gian, bars, T = 1, gộp V1a–V3):

{md(C)}
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
"""
open("KET_QUA_2_vi.md", "w").write(txt)
print(ta.to_string()); print(tr.to_string())
