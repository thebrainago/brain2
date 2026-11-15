# Tạo KET_QUA_3_vi.md từ results3/
import pandas as pd, numpy as np
L = pd.read_csv("results3/lookup_pooled_anchors.csv"); T = pd.read_csv("results3/tests.csv")
def md(df):
    cols = list(df.columns); s = "| " + " | ".join(map(str, cols)) + " |\n|" + "---|" * len(cols) + "\n"
    for _, r in df.iterrows(): s += "| " + " | ".join(str(r[c]) for c in cols) + " |\n"
    return s
x = L[(((L.tf == "1h") & (L.H == 24)) | ((L.tf == "1d") & (L.H == 10))) & (L.trend == "EMA200")].copy()
f = lambda a, b, c: f"{a:.0f} ({b:.0f}/{c:.0f})"
lk = pd.DataFrame({
    "Mã": x.ticker, "Khung": x.tf, "Bước": x.step.astype(str) + "°", "Trường hợp": x.case.map({"with": "phá THEO trend", "counter": "phá NGƯỢC trend"}),
    "n": x.n_sq9, "1 bậc ≈ ATR": x.stepATR_med.round(1),
    "→B %": [f(a, b, c) for a, b, c in zip(x.B, x.B_eq, x.B_unc)],
    "→C %": [f(a, b, c) for a, b, c in zip(x.C, x.C_eq, x.C_unc)],
    "→D %": [f(a, b, c) for a, b, c in zip(x.D, x.D_eq, x.D_unc)],
    "→B trước khi lấy lại A %": x.Bpre.round(0),
    "Hồi chạm A %": [f"{a:.0f} ({b:.0f})" for a, b in zip(x.touchA, x.touchA_unc)],
    "Close lại qua A %": x.closeA.round(0),
    "→B IS / OOS": [f"{a:.0f} / {b:.0f}" for a, b in zip(x.B_IS, x.B_OOS)],
    "Nến tới B (trung vị)": x.barsB_med,
})
def summ(b):
    y = T[T.baseline == b]
    return dict(baseline=b, so_phep=len(y), p_nho_hon_005=int((y.p < .05).sum()), qua_FDR=int((y.q_fdr < .05).sum()),
                qua_FDR_Sq9_tot_hon=int(((y.q_fdr < .05) & (y["diff"] > 0)).sum()), hieu_TB=round(y["diff"].mean(), 2), hieu_tuyet_doi_TB=round(y["diff"].abs().mean(), 2))
S = pd.DataFrame([summ(b) for b in ("eqpct", "shift", "uncond")])
ba = T[(T.level == "by_anchor") & (T.period == "ALL") & (T.baseline == "shift")].pivot_table(index=["tf", "anchor"], columns="metric", values="diff", aggfunc="mean").round(1).reset_index()
dIS = (L.B_IS - L.B_OOS).abs()
txt = f"""# Kết quả kiểm định 3: XÁC SUẤT ĐI TIẾP qua các bậc Sq9 (vàng & S&P 500)

**Câu hỏi.** Trong trend, khi giá **đóng cửa xuyên qua mức A** của thang Sq9, xác suất giá đi tiếp tới B, C, D (1, 2, 3 bậc kế tiếp) là bao nhiêu?
Và xác suất hồi ngược về A là bao nhiêu? Câu hỏi phụ: thang Sq9 có cho xác suất khác các thang khác không?

**Dữ liệu.**
- 1h: GC=F và ES=F từ 06/2024, ^GSPC (giờ RTH) từ 12/2023. IS = nửa đầu, OOS = nửa sau.
- Daily: GC=F từ 2008, ES=F và ^GSPC từ 2000. IS < 2016 ≤ OOS.

**Thang.** L(j) = (√P + j·bước/180)². Bước 45°, 90°, 180°.
- Neo trên 1h: đóng cửa ngày trước, mở phiên, swing high/low 10/5.
- Neo trên daily: pivot 20/20. Neo chỉ dùng sau khi đã xác nhận.

**Trend** (không nhìn trước):
- EMA200 + dốc EMA, EMA50 + dốc EMA.
- Riêng 1h có thêm trend D1 (EMA50 ngày, tính trên ngày đã đóng).

**Sự kiện.** close[t−1] ≥ A và close[t] < A − 0.1 ATR (ngược lại khi phá lên). Mỗi mức chỉ tính lần phá đầu tiên của mỗi neo.

**Đo trong H nến** (1h: 10/24/48; daily: 5/10/20):
- Chạm B/C/D: bất kỳ lúc nào, và "trước khi close lấy lại A".
- Hồi chạm A, close lại qua A, hồi ≥ 50% bậc.
- MFE/MAE, số nến tới B.

**Baseline:**
1. **shift**: cùng neo, thang dời pha ngẫu nhiên (0–1 bậc trong không gian √).
2. **eqpct**: thang cách đều theo %, cùng khoảng cách quanh neo.
3. **vô điều kiện**: một nến bất kỳ cùng trạng thái trend đi được cùng khoảng cách (×ATR) theo cùng hướng trong H nến.

**Kiểm định.** Bootstrap theo cụm (tuần cho 1h, tháng cho daily), 1000 lần. FDR Benjamini–Hochberg trên toàn bộ 18 468 phép (H giữa, theo từng neo và gộp neo, ALL/IS/OOS).

---
## 1. Bảng tra thực dụng (gộp các neo, trend EMA200, H = 24 nến cho 1h / 10 phiên cho daily)
Ô ghi: **Sq9** (thang đều % / vô điều kiện cùng khoảng cách ATR). Bảng đầy đủ cho mọi trend, H và neo:
`results3/lookup_pooled_anchors.csv` và `results3/lookup_by_anchor.csv`.

{md(lk)}
Đọc ví dụ: vàng 1h, bước 90° (1 bậc ≈ 3.7 ATR giờ), trend giảm theo EMA200 và giá đóng cửa xuyên xuống A:
trong 24 giờ, khoảng **36%** tới B, **11%** tới C, **4%** tới D, và khoảng **86%** hồi chạm lại A.

---
## 2. Sq9 có thêm gì so với baseline?
{md(S)}
- **So với thang đều % (eqpct): hiệu trung bình 0.0 điểm, |hiệu| trung bình 0.6 điểm.** Thang Sq9 và thang đều % cho xác suất gần như trùng nhau.
- **So với thang dời pha (shift):** Sq9 hơi **kém** hơn (−0.7 điểm trung bình). Phần kém này nằm gần hết ở neo mở phiên / đóng cửa ngày trước trên 1h:

{md(ba)}
  Lý do: thang Sq9 (và thang đều %) luôn có **một mức ngay tại giá neo**. Khoảng 66–77% sự kiện là "phá giá mở phiên / đóng cửa ngày trước",
  và sau đó giá ít đi tiếp hơn (ES 1h bước 90°: 18.5% tới B, so với 41% khi phá mức xa hơn). Đây là đặc tính của **giá neo**, không phải của góc Gann.
  Với neo swing và pivot daily, Sq9 ≈ shift ≈ eqpct.
- Trong 7 182 phép so với thang đều %, chỉ 19 phép qua FDR theo hướng Sq9 tốt hơn. Đa số hiệu < 2 điểm. Lớn nhất là ES daily, tới C cao hơn 3–5 điểm, nhưng chủ yếu ở IS, và với ^GSPC (gần như cùng chuỗi giá) thì không lặp lại. **Khoảng cách Sq9 không thêm thông tin.**

## 3. Các xác suất này có giá trị giao dịch không (bỏ qua chuyện Gann)?
- **So với vô điều kiện:** xác suất tới B/C/D sau khi phá mức **không cao hơn**, mà còn thấp hơn khoảng 1 điểm (trung bình −1.0; trong 316 phép qua FDR thì chỉ 3 phép là phá mức tốt hơn).
  Nghĩa là "giá vừa đóng cửa qua một mức" **không cho thêm thông tin** so với chuyện giá trong trend đó có thường xuyên đi xa được ngần ấy ATR hay không.
  Xác suất tới B gần như chỉ phụ thuộc **1 bậc bằng bao nhiêu ATR**: khoảng 1 ATR thì ~80%, 2–3 ATR thì ~55–65%, 5 ATR thì ~25–35%, 8–11 ATR thì ~5–15%.
- **Phá theo trend so với ngược trend:** theo trend chỉ hơn khoảng +0.8 điểm trong việc tới B. Hiệu so với vô điều kiện: theo trend −0.5, ngược trend −1.4. **Không có lợi thế theo trend đáng kể.**
- **Hồi về A rất thường xuyên:** 77–88% số lần giá chạm lại A trong H nến, và 64–80% có close lấy lại A. Con số này đúng bằng vô điều kiện, tức là do biến động bình thường.
  Muốn vào lệnh theo hướng phá thì nên tính trước là phần lớn trường hợp giá sẽ retest A.
- **Kém ổn định theo thời gian nếu tính theo giá:** chênh lệch P(tới B) giữa IS và OOS có trung vị {dIS.median():.1f} điểm (10% số ô lệch > {dIS.quantile(.9):.0f} điểm).
  Lý do là biến động thay đổi theo giai đoạn, ví dụ vàng 1h bước 180°: 1% ở IS so với 17% ở OOS. Nếu quy về khoảng cách ATR thì xác suất ổn định hơn nhiều, nhưng khi đó cũng chẳng còn liên quan gì tới Gann.

## 4. Kết luận
| Câu hỏi | Trả lời |
|---|---|
| (a) Xác suất "qua A → B/C/D" có dùng được để giao dịch? | Dùng được như **bảng mô tả biến động** (1 bậc = n ATR → xác suất tới). Nhưng phá mức **không tạo lợi thế** so với một nến ngẫu nhiên cùng trend; xác suất tính theo mức giá cũng không ổn định giữa các giai đoạn. |
| (b) Khoảng cách Sq9 có thêm gì? | **Không.** Giống thang đều %. Hơi kém thang dời pha, nhưng đó là do có mức ngay tại giá neo (mở phiên / đóng cửa hôm trước), không phải do góc Gann. |
| Hồi ngược trend | 77–88% chạm lại A, 64–80% close lấy lại A trong H nến. Bằng mức ngẫu nhiên, nên không phải tín hiệu. |

## Tái chạy
```
cd tools/kiem_dinh/gann_sq9
.venv/bin/python test_c_continuation.py   # results3/events.pkl (~200k sự kiện)
.venv/bin/python analyze_c.py             # results3/lookup_*.csv, tests.csv (~3 phút)
.venv/bin/python make_summary3.py         # KET_QUA_3_vi.md
```
"""
open("KET_QUA_3_vi.md", "w").write(txt)
print(S.to_string())
