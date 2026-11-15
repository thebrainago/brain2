# Tạo KET_QUA_4_vi.md
import pandas as pd, numpy as np
L = pd.read_csv("results4/lookup.csv"); T = pd.read_csv("results4/tests.csv")
S = pd.read_csv("results4/scalp_all.csv"); B = pd.read_csv("results4/scalp_best_IS_to_OOS.csv")
HM = {"1h": 24, "15m": 48, "5m": 144, "1d": 10}
def md(df):
    cols = list(df.columns); s = "| " + " | ".join(map(str, cols)) + " |\n|" + "---|" * len(cols) + "\n"
    for _, r in df.iterrows(): s += "| " + " | ".join(str(r[c]) for c in cols) + " |\n"
    return s
x = L[(L.D == 5) & (L.conf == "R3") & (L.apply(lambda r: r.H == HM[r.tf], axis=1))].copy()
want = [("sq9", "hoi", "45°"), ("sq9", "hoi", "90°"), ("sq9", "hoi", "135°"), ("sq9", "hoi", "180°"), ("sq9", "tiep", "45°"), ("sq9", "tiep", "90°"),
        ("fib", "hoi", "38.2%"), ("fib", "hoi", "50.0%"), ("fib", "hoi", "61.8%"), ("fib", "tiep", "127.2%")]
rows = []
for (tk, tf), g in x.groupby(["ticker", "tf"], sort=False):
    for st, side, lab in want:
        r = g[(g.set == st) & (g.side == side) & (g.label == lab)]
        if not len(r): continue
        r = r.iloc[0]
        rows.append({"Mã": tk, "Khung": tf, "H": int(r.H), "n": int(r.n),
                     "Mục tiêu": ("Sq9 " if st == "sq9" else "Fib ") + ("↑hồi " if side == "hoi" else "↓tiếp ") + lab,
                     "Chạm %": f"{r.P:.0f}" + (f" ({r.P_shift:.0f})" if st == "sq9" else ""),
                     "Chạm sạch %": f"{r.P_clean:.0f}", "Cách neo (ATR)": f"{r.dATR_med:+.1f}", "% cú sập": f"{r.pctDrop_med:+.0f}",
                     "Nến tới": r.bars_med, "MAE trung vị / P80 (ATR)": f"{r.MAE_med:.1f} / {r.MAE_p80:.1f}",
                     "Còn phía trước giá vào %": f"{r.valid:.0f}"})
LK = pd.DataFrame(rows)
f = x[(x.set == "sq9") & (x.side == "hoi")][["ticker", "tf", "label", "first_hoi", "first_tiep", "first_khong"]]
f = f[f.label.isin(["45°", "90°"])].round(0)
f.columns = ["Mã", "Khung", "Góc", "Hồi chạm trước %", "Đi tiếp chạm trước %", "Không chạm cái nào %"]
def summ(b, st):
    y = T[(T.baseline == b) & (T.set == st)]
    return dict(so_sanh=f"{st} vs {b}", so_phep=len(y), p_005=int((y.p < .05).sum()), qua_FDR=int((y.q_fdr < .05).sum()),
                qua_FDR_va_tot_hon=int(((y.q_fdr < .05) & (y["diff"] > 0)).sum()), hieu_TB_diem=round(y["diff"].mean(), 2))
SM = pd.DataFrame([summ("shift", "sq9"), summ("curve", "fib"), summ("curve", "sq9")])
sc = S.groupby(["set", "side"]).agg(so_combo=("R_IS", "size"), R_TB_IS=("R_IS", "mean"), R_TB_OOS=("R_OOS", "mean"),
                                    ty_le_IS_duong=("R_IS", lambda v: 100 * (v > 0).mean()), ty_le_OOS_duong=("R_OOS", lambda v: 100 * (v > 0).mean())).round(3).reset_index()
best = B.sort_values("R_IS", ascending=False).groupby(["ticker", "tf"]).head(1)
best = best[["ticker", "tf", "D", "conf", "set", "side", "label", "H", "SL", "n_IS", "n_OOS", "R_IS", "R_OOS", "win_OOS", "p_OOS", "p_bonf"]].round(3)
txt = f"""# Kết quả kiểm định 4: Scalp sau cú sập / cú tăng mạnh, neo đáy (đỉnh) bằng Sq9

**Kịch bản** (đúng ví dụ của Vanh): giá 4000 sập về 3920 rồi hồi lên một nhịp, lấy 3920 làm neo.
Các mức Sq9 **trên** neo là mục tiêu **hồi**, các mức **dưới** neo là mục tiêu **đi tiếp**. Cú tăng mạnh thì làm đối xứng: neo đỉnh. Kết quả dưới đây gộp cả hai chiều.

**Dữ liệu:**
- 1h: GC=F, ES=F (06/2024 → 11/2026), ^GSPC giờ RTH (12/2023 →).
- 15m và 5m: 60 ngày gần nhất (09 → 11/2026), mẫu nhỏ.
- Daily: GC từ 2008, ES/^GSPC từ 2000.
- OOS: nửa sau dữ liệu (daily: từ 2016).

**Sự kiện** (không nhìn trước):
- Cú sập: từ đỉnh trong 24 nến xuống đáy ≥ D×ATR14, với D = 3, 5, 8.
- Xác nhận đáy: pivot (5 nến trái, R = 2/3/5 nến phải), hoặc "b1" (close bật ≥ 1 ATR khỏi đáy mà chưa thủng đáy).
- Vào lệnh tại close của nến xác nhận.

**Mục tiêu:**
- Sq9 45/90/135/180/270/360° trên và dưới neo.
- Fib hồi 23.6–78.6% của cú sập, Fib mở rộng 127.2/161.8/200%.

**Đối chứng:**
1. Góc Sq9 lệch ngẫu nhiên ±22.5°, 3 lần rút, cùng sự kiện. Đây là phép so **cùng khoảng cách** chính xác nhất.
2. Đường cong P(chạm | khoảng cách ATR), dựng từ lưới neo ± m·ATR với m từ 0.25 đến 12.
3. Fib.

Lưu ý: trong cùng một sự kiện, "mục tiêu cách neo đúng bằng khoảng ATR của mức Sq9" chính là cùng một mức giá. Vì vậy so với khoảng cách ATR chỉ có nghĩa khi gộp nhiều sự kiện (đối chứng 2).
Đối chứng 2 bị lệch với Sq9: Sq9 cách neo một tỷ lệ % cố định của giá, nên khi thị trường yên thì tính ra rất nhiều ATR. Vì thế phép so chính để trả lời câu hỏi "Sq9 có thêm gì so với khoảng cách" là đối chứng 1.

Kiểm định: bootstrap theo tuần (daily: theo tháng), FDR.

---
## 1. Bảng tra (D ≥ 5 ATR, đáy pivot R = 3, H = 24 nến 1h / 48 nến 15m / 144 nến 5m / 10 phiên daily)
- **Chạm %**: Sq9 (trong ngoặc là góc lệch ngẫu nhiên).
- **Chạm sạch**: mục tiêu hồi chạm trước khi thủng neo; mục tiêu đi tiếp chạm trước khi giá hồi quá 50% cú sập.
- **MAE**: giá đi ngược bao nhiêu ATR trước khi chạm, dùng để đặt SL.
- **Còn phía trước giá vào**: % số lần mục tiêu vẫn còn ở phía có lãi khi vào lệnh. Ví dụ Sq9 ↑45° thường đã bị vượt ngay trong nhịp hồi xác nhận đáy.

Bảng đầy đủ cho mọi D, kiểu xác nhận, H và mục tiêu nằm trong `results4/lookup.csv`.

{md(LK)}
**Mục tiêu nào chạm trước** (Sq9 cùng góc: hồi ↑ hay đi tiếp ↓):

{md(f)}
---
## 2. Sq9 có hơn mức cùng khoảng cách và Fib không?
{md(SM)}
- **Sq9 so với góc lệch ±22.5° (cùng khoảng cách):** hiệu trung bình −0.2 điểm. Trong 1 704 phép chỉ có 4 phép qua FDR theo hướng Sq9 tốt hơn. **Sq9 không thêm gì.**
- **Fib so với đường cong khoảng cách:** hiệu −0.3 điểm. **Fib cũng không thêm gì.** Xác suất chạm chỉ do khoảng cách (tính theo ATR hoặc theo % cú sập) quyết định.
- **Sq9 so với đường cong:** −2.8 điểm, nhưng góc lệch ngẫu nhiên cũng thấp y như vậy. Đây là lệch phương pháp (Sq9 cố định theo % giá), không phải Sq9 tệ hơn.

## 3. Scalp: có combo nào kỳ vọng dương và giữ được ở OOS?
Có {len(S)} combo: mã × khung × D × kiểu xác nhận × mục tiêu × SL × H. R đã trừ spread (vàng 0.3, ES 0.25, ^GSPC 0.5). Cùng nến chạm cả TP lẫn SL thì tính là thua.

{md(sc)}
- **Lệnh hồi (long sau đáy, SL dưới neo):** kỳ vọng ≈ 0R ở cả IS lẫn OOS. Mục tiêu gần chạm nhiều nhưng lãi nhỏ, nên cộng lại hoà vốn sau spread.
- **Lệnh đi tiếp (short theo trend, SL = vào + k·ATR):** IS trung bình +0.14R, OOS chỉ +0.05R. Góc lệch ngẫu nhiên cho y hệt (+0.14 / +0.05), nên phần dương này **không đến từ Sq9**.
  Phần dương đến từ việc giữ lệnh theo trend tới hết H với SL chặt (lãi đuôi dài, tỷ lệ thắng chỉ 13–34%). Nó cũng không ổn định: OOS khung 1h là −0.01R, 15m là −0.14R.
- **Combo tốt nhất trên IS của từng mã/khung, kiểm tra trên OOS:**

{md(best)}
  Trong 60 combo top-IS (5 combo cho mỗi mã/khung), **không combo nào có OOS dương còn ý nghĩa sau hiệu chỉnh Bonferroni**.
  Hai combo gần nhất: vàng 1h D8 R2 Sq9 ↓45° SL 1 ATR, OOS +0.45R, p = 0.04; ^GSPC daily D3 ↓360° SL 0.5 ATR H 20, OOS +0.54R, p = 0.006.
  Sau hiệu chỉnh cả hai đều p > 0.3. Mục tiêu ↓360° gần như không bao giờ chạm, nên lệnh đó thực chất là "short giữ 20 phiên", chẳng liên quan gì tới mục tiêu.
  Nhiều combo IS rất đẹp (+1 đến +6R ở 5m/15m) sang OOS thành âm: overfit trên mẫu 60 ngày.

## 4. Kết luận
| Câu hỏi | Trả lời |
|---|---|
| (a) Mục tiêu nào hay chạm nhất? | Mục tiêu **hồi gần nhất**: Sq9 ↑45° hoặc Fib 23.6–38.2%, chạm khoảng 70–80% trong H nến. Nhưng phần lớn đã bị vượt ngay trong nhịp hồi xác nhận đáy (chỉ 34–60% còn ở phía trước giá vào). Mục tiêu hồi luôn chạm nhiều hơn mục tiêu đi tiếp cùng góc (vàng/ES 1h ↑45°: khoảng 70% chạm trước, so với khoảng 15% cho ↓45°). Xác suất giảm dần theo khoảng cách. |
| (b) Sq9 có hơn mức cùng khoảng cách ATR và Fib? | **Không.** Sq9 ≈ góc lệch ngẫu nhiên (−0.2 điểm), Fib ≈ đường cong khoảng cách (−0.3 điểm). Chỉ khoảng cách quyết định. |
| (c) Scalp kỳ vọng dương giữ được OOS? | **Không có combo nào đạt ý nghĩa thống kê.** Lệnh hồi ≈ 0R sau spread. Lệnh đi tiếp dương nhẹ nhưng không ổn định và không nhờ Sq9. |

**Gợi ý thực dụng:** nếu vẫn muốn scalp hồi sau cú sập, dùng mục tiêu theo khoảng cách ATR / % cú sập trong bảng trên (ví dụ chạm sạch ~40–55% cho hồi 38–50%), với SL ≥ MAE P80 (≈ 1.5–2 ATR trên 1h).
Bảng này chỉ cho biết **tỷ lệ chạm**. Nó **không** tạo lợi thế sau phí: tỷ lệ chạm cao luôn đi kèm lãi nhỏ so với rủi ro.

## Tái chạy
```
cd tools/kiem_dinh/gann_sq9
.venv/bin/python test_d_impulse.py    # results4/targets.pkl, grid.pkl (~2 phút)
.venv/bin/python analyze_d.py         # results4/lookup.csv, tests.csv, scalp_all.csv, scalp_best_IS_to_OOS.csv (~3 phút)
.venv/bin/python make_summary4.py     # KET_QUA_4_vi.md
```
"""
open("KET_QUA_4_vi.md", "w").write(txt)
print(LK[LK.Khung.isin(["1h", "1d"])].to_string(index=False)); print(f.to_string(index=False)); print(best.to_string(index=False))
