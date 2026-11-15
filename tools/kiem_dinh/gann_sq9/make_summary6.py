# -*- coding: utf-8 -*-
import pandas as pd, numpy as np
S = pd.read_csv("results6/spiral_tests.csv"); B = pd.read_csv("results6/charts_best_IS_to_OOS.csv")
F = pd.read_csv("results6/charts_fake_vs_real.csv"); R = pd.read_csv("results6/charts_all.csv")
A = {}
for tag in ["GCF_1d", "ESF_1d", "GSPC_1d", "GCF_1h", "ESF_1h", "GSPC_1h"]:
    A[tag] = np.load(f"results6/spiral_acc_{tag}.npy")
L = []
w = L.append
w("# KẾT QUẢ TEST 6: FIBONACCI XOẮN ỐC VÀ CÁC LOẠI CHART PHI CHUẨN (Vàng và S&P 500)\n")
w("**Dữ liệu:**")
w("- **Nến ngày:** GC=F từ 2008, ES=F và ^GSPC từ 2000 đến 13/11/2026. IS/OOS tách ở 01/01/2016.")
w("- **Nến 1h:** GC=F và ES=F từ 06/2024, ^GSPC phiên chính từ 12/2023, đến 13/11/2026. IS/OOS chia đôi theo thời gian.")
w("- **Nến 15m:** GC=F và ES=F, chỉ khoảng 60 ngày (04/09 → 13/11/2026). Mỗi nửa chỉ khoảng 1 tháng, nên chỉ để tham khảo.")
w("- **Phí:** spread vàng 0,3, ES 0,25, ^GSPC 0,5 điểm. Mỗi lần đổi vị thế trả nửa spread.")
w("- **Hiệu chỉnh nhiều phép thử:** FDR Benjamini–Hochberg.\n")
w("## TÓM TẮT KẾT LUẬN\n")
w("| Phương pháp | Kết luận | Lý do chính |")
w("|---|---|---|")
w("| Fibo xoắn ốc, chạm đường xoắn (giữ / hồi) | **Không có edge** | Bằng xoắn ốc có hệ số ngẫu nhiên. 0/432 lát cắt qua FDR. Riêng ES 1h có hồi ≥1 ATR nhỉnh hơn (+5 điểm), nhưng giảm từ IS sang OOS và q=0,11 → *yếu, chưa xác nhận* |")
w("| Fibo xoắn ốc, mốc thời gian | **Không có edge** | Tỷ lệ trúng đảo chiều bằng hoặc thấp hơn xoắn ốc ngẫu nhiên ở cả 6 bộ dữ liệu |")
w("| Heikin Ashi (đổi màu, nến không bóng) | **Không có edge** | Khớp ở giá thật thì Sharpe quanh 0. Khớp ở giá HA thì đẹp ảo, Sharpe 2–20 |")
w("| Renko (đảo N brick, đếm brick) | **Không có edge** | Không qua được bootstrap. Bản khớp ảo cũng bị thổi phồng |")
w("| Point & Figure (double, triple, catapult) | **Không có edge** | Double top/bottom chỉ là một kiểu đi theo trend, ngang Donchian. Triple và catapult quá ít tín hiệu (3–27 lệnh) |")
w("| Three Line Break | **Không có edge** | Không hơn đối chứng |")
w("| Kagi (yin/yang) | **Không có edge** (yếu) | Đảo 3 ATR, chỉ mua, gần như là cầm vàng/chỉ số dài hạn (≈ Buy & Hold). Vàng 1h OOS Sharpe 1,54 nhưng p=0,19 |")
w("\n**Có gì thắng được trend-following đơn giản ở OOS không?** Không có gì thắng một cách có ý nghĩa.")
c = B[~B.method.str.startswith("BL_")]
w(f"- Đã chọn {len(c)} cấu hình (mỗi phương pháp × bộ dữ liệu, tốt nhất ở IS). Ở OOS:")
w(f"  - Bootstrap p<0,05: **{(c.p_boot < .05).sum()}**. FDR q<0,05: **{(c.q < .05).sum()}**.")
w(f"  - Hơn đối chứng Donchian/EMA (chọn tốt nhất IS): {c.hon_BL.sum()}/{len(c)}.")
w(f"  - Hơn Buy & Hold: {c.hon_BH.sum()}/{len(c)}.")
w(f"  - Hơn cả hai: {(c.hon_BL & c.hon_BH).sum()}/{len(c)}, gần bằng mức may rủi.")
w("- Các trường hợp \"hơn cả hai\" tập trung ở:")
w("  - **Vàng 1h:** nửa sau thuận lợi cho trend-following nói chung. Donchian N=20, dù không phải cấu hình được chọn ở IS, cũng đạt Sharpe 0,95, trong khi Buy & Hold chỉ 0,31. Các chart phi chuẩn đạt 0,8–1,0, ngang Donchian. Riêng Kagi 1,54 nhưng p=0,19.")
w("  - **ES 15m:** OOS chỉ khoảng 1 tháng nên là nhiễu.")
w("- Chart phi chuẩn **không làm gì hơn trend-following thường**. Chúng chỉ là một cách lọc nhiễu khác.\n")

w("---\n## PHẦN 1: FIBONACCI XOẮN ỐC\n")
w("**Thiết lập:**")
w("- **Tâm và bán kính:** tâm là pivot lớn 20/20 hoặc 60/60, chỉ dùng từ nến xác nhận nên không nhìn trước. Bán kính đầu bằng chân sóng đầu tiên, tức từ pivot tới cực trị ngược lại trước khi xác nhận.")
w("- **Công thức:** r = a·φ^(2θ/π). Xét cả 2 chiều quay.")
w("- **Tỷ lệ giá/thời gian:** có 2 cách:")
w("  - (A) 1 nến tương ứng 1 ATR.")
w("  - (B) theo chân sóng, chân sóng nằm ở góc 45°.")
w("- **Sự kiện giá:** lần đầu giá chạm mỗi nhánh xoắn (±0,2 ATR). Đo hai chỉ tiêu:")
w("  - **Giữ 5 nến:** không đóng cửa xuyên qua mức.")
w("  - **Hồi:** bật ≥1 ATR trong 10 nến, trước khi phá.")
w("- **Mốc thời gian:** nến mà xoắn ốc cắt trục ngang (giá = giá neo), cộng hình chiếu bán kính khi cắt trục dọc. \"Trúng\" là có swing 10/10 trong ±3 nến.")
w("- **Đối chứng (200 lần rút mỗi neo):**")
w("  - Hệ số tăng g ngẫu nhiên trong U(1,3–2,0), bỏ khoảng ±0,05 quanh φ.")
w("  - Xoay ngẫu nhiên ±90°.")
w("  - Cả hai cùng lúc.")
w("  - p tính theo phân phối của 200 lần rút.\n")
w("**Kết quả gộp (φ so với xoắn ốc ngẫu nhiên, cả g lẫn góc xoay):**\n")
w("| Dữ liệu | Neo | Chỉ tiêu | n (φ) | φ % | Ngẫu nhiên % | z | p | q |")
w("|---|---|---|---|---|---|---|---|---|")
g = S[(S.lat_cat == "GOP_TAT_CA") & (S.doi_chung == "rand_both")]
nanc = {}
for _, r in g.iterrows():
    nm = {"giu5": "Giữ 5 nến", "hoi1ATR": "Hồi ≥1 ATR", "moc_tg_trung_dao_chieu": "Mốc t.gian trúng đảo chiều"}[r.chi_tieu]
    w(f"| {r.data.replace('_', ' ')} | pivot 20/20+60/60 | {nm} | {r.n_phi} | {r.P_phi:.1f} | {r.P_null:.1f} | {r.z:+.2f} | {r.p:.3f} | {r.q:.2f} |")
w("\n**IS và OOS của các chỗ lệch đáng chú ý:**\n")
w("| Dữ liệu | Giai đoạn | n | Giữ φ / ngẫu nhiên | Hồi φ / ngẫu nhiên |")
w("|---|---|---|---|---|")
for tag in ["ESF_1h", "GSPC_1h", "GSPC_1d", "GCF_1h"]:
    Aa = A[tag]
    for pi, pn in ((0, "IS"), (2, "OOS")):
        r = Aa[0, 0, :, :, pi].sum((0, 1)); nl = Aa[3, :, :, :, pi].sum((1, 2))
        h = [f"{100*r[k]/r[0]:.1f} / {100*(nl[:,k]/nl[:,0]).mean():.1f} (z {(r[k]/r[0]-(nl[:,k]/nl[:,0]).mean())/(nl[:,k]/nl[:,0]).std():+.1f})" for k in (1, 2)]
        w(f"| {tag.replace('_',' ')} | {pn} | {int(r[0])} | {h[0]} | {h[1]} |")
sub = S[S.lat_cat != "GOP_TAT_CA"]
w(f"\nĐã thử **{len(sub)} lát cắt** (dữ liệu × tỷ lệ × chiều quay × IS/OOS × chỉ tiêu × đối chứng).")
w(f"- Có {(sub.p < .05).sum()} lát p<0,05 (chỉ riêng may rủi đã cho khoảng {0.05*len(sub):.0f}). Trong đó chỉ {((sub.p<.05)&(sub.z>0)).sum()} lát nghiêng về φ.")
w(f"- FDR q<0,05: **{(sub.q < .05).sum()}**.")
w("- Không lát nào lặp lại được ở cả IS lẫn OOS.\n")
w("**Kết luận Phần 1:**")
w("- Đường xoắn φ không giữ giá tốt hơn xoắn ốc có hệ số hoặc góc xoay bất kỳ. Riêng ^GSPC nến ngày, φ còn kém hơn ở IS.")
w("- Mốc thời gian của xoắn ốc trúng đảo chiều ngang mức ngẫu nhiên.")
w("- Thêm một vấn đề: xoắn ốc phụ thuộc hoàn toàn vào cách quy đổi \"1 nến = bao nhiêu giá\". Cả 2 cách quy đổi đều không cho kết quả.\n")

w("---\n## PHẦN 2: CHART PHI CHUẨN\n")
w("**Nguyên tắc chống ảo:**")
w("- Nến HA, brick, cột và đường chỉ được biết khi đã hoàn thành ở giá đóng cửa của nến thật, dựng từ giá đóng cửa.")
w("- Tín hiệu xuất hiện ở close t → **khớp ở giá mở cửa THẬT của nến t+1**.")
w("- Bản \"ảo\" dùng cùng tín hiệu nhưng khớp ở giá HA close hoặc giá brick. Đây chính là kiểu backtest \"Renko/HA đẹp như mơ\" hay thấy trên mạng: bạn không thể mua được ở giá HA vì đó là giá trung bình, không phải giá thị trường.\n")
w("**Chiến lược đã thử:**")
w("- **HA:** đổi màu N nến (N=1/2/3); nến không bóng dưới (hoặc trên) k nến, thoát khi đổi màu.")
w("- **Renko:** box 0,5/1/2×ATR động, hoặc box log 1/2×ATR% cố định. Đảo chiều sau N brick (N=1/2/3); đếm M brick (M=3/5) rồi thoát khi có brick ngược.")
w("- **Point & Figure:** box 0,5/1/2×ATR% (log), đảo 3 ô. Tín hiệu double top/bottom, triple, catapult.")
w("- **Three Line Break:** 2/3/4 đường.")
w("- **Kagi:** đảo 0,5/1/2/3 ATR, mua khi yang, bán khi yin.")
w("- Mỗi chiến lược chạy 2 chế độ: Long/Short (LS) và chỉ Long (L).\n")
w("**Đối chứng:**")
w("- Donchian 20/55 và EMA 10/50, 20/100 trên nến thường, chọn tốt nhất ở IS.")
w("- Buy & Hold.")
w("- Block-bootstrap nến OOS (khối 20 nến, 300 lần): chạy đúng cấu hình đã chọn trên dữ liệu đã xáo khối, để xem chiến lược có khai thác được cấu trúc thật hay chỉ ăn theo drift.\n")
w("### 2a. Cấu hình tốt nhất IS, kết quả OOS: Sharpe ròng (p bootstrap)\n")
B["ds"] = B.ticker.str.replace("=F", "").str.replace("^", "") + " " + B.tf
order = ["GC 1d", "ES 1d", "GSPC 1d", "GC 1h", "ES 1h", "GSPC 1h", "GC 15m", "ES 15m"]
B["cell"] = B.OOS_sharpe.round(2).astype(str) + " (p" + B.p_boot.round(2).astype(str) + ")"
p = B.pivot_table(index="method", columns="ds", values="cell", aggfunc="first")[order].fillna("–")
bh = B.groupby("ds").BH_OOS_sharpe.first()[order].round(2).astype(str)
p.loc["**Buy & Hold**"] = bh.values
w(p.to_markdown()); w("")
w("PnF triple và catapult để trống \"–\" là vì ở IS có dưới 10 lệnh. Chi tiết PF, kỳ vọng R, win, maxDD, số lệnh ở `results6/charts_best_IS_to_OOS.csv`.\n")
w("### 2b. Chi tiết OOS các cấu hình chọn (nến ngày và 1h)\n")
cols = ["ds", "method", "param", "mode", "IS_sharpe", "OOS_sharpe", "OOS_PF", "OOS_expR", "OOS_win", "OOS_trades", "OOS_maxdd_pct", "p_boot", "q"]
t = B[B.tf.isin(["1d", "1h"])][cols].round(2)
t.columns = ["Dữ liệu", "PP", "Tham số", "Chế độ", "Sharpe IS", "Sharpe OOS", "PF OOS", "Kỳ vọng R (ATR)", "Win %", "Lệnh", "MaxDD %", "p boot", "q"]
w(t.to_markdown(index=False)); w("")
w("*R = lãi/lỗ mỗi lệnh chia cho ATR lúc vào lệnh. MaxDD tính trên lợi nhuận cộng dồn theo % giá, với 1 hợp đồng.*\n")
w("### 2c. Khớp giá \"ảo\" so với khớp giá thật (OOS, chế độ Long/Short, tham số nhạy nhất)\n")
x = R[(R.method.isin(["HA_doi_mau", "Renko_dao_N"])) & (R.param.isin(["N=1", "ATRx0.5,N=1"])) & (R["mode"] == "LS") & (R.period == "OOS")]
x = x.pivot_table(index=["ticker", "tf", "method"], columns="fill", values=["sharpe", "PF", "win", "tot_ret_pct"]).round(2)
x.columns = [f"{a} {('ẢO' if b=='ao' else 'THẬT')}" for a, b in x.columns]
w(x.reset_index().to_markdown(index=False)); w("")
w("**Trung vị trên toàn lưới tham số (cả IS và OOS):**\n")
w(F.rename(columns=dict(method="PP", tf="Khung", sharpe_ao_tb="Sharpe ảo", sharpe_that_tb="Sharpe thật", chenh_tb="Chênh", PF_ao_tb="PF ảo", PF_that_tb="PF thật")).to_markdown(index=False))
w("\n→ **Ảo lớn nhất ở Heikin Ashi.** Ví dụ HA đổi màu trên ES 1h: khớp ảo cho Sharpe 10,8, PF 3,1; khớp thật cho Sharpe −0,6, PF 0,93. Renko cũng bị thổi phồng: Sharpe tăng khoảng 1–2, PF lên khoảng 1,5–1,9.")
w("PnF, Kagi và Line Break dựng từ giá đóng cửa nên bản ảo không đẹp hơn.")
w("Trên TradingView, backtest trên chart Renko/HA mà không bật \"Fill orders using standard OHLC\" sẽ rơi đúng vào cái bẫy này.\n")
w("## HẠN CHẾ")
w("- **ES=F nến ngày** là chuỗi liên tục chưa điều chỉnh roll, nên có bước nhảy khi chuyển hợp đồng mỗi quý. ^GSPC dùng làm kiểm chứng.")
w("- Dữ liệu 1h chỉ khoảng 2,4 năm. Dữ liệu 15m chỉ khoảng 60 ngày, nên chỉ để tham khảo.")
w("- **Bootstrap giữ nguyên drift của OOS**, nên p đo phần lợi nhuận \"vượt trên drift\". Hệ chỉ mua có lời là do thị trường tăng, không phải do chart.")
w("- Brick, cột và đường dựng từ giá đóng cửa. Dựng từ high/low sẽ cho thêm tín hiệu nhưng phải giả định thứ tự giá trong nến, rất dễ tạo ảo.\n")
w("## FILE")
w("- Script: `test_f_spiral.py`, `analyze_f.py`, `test_g_charts.py`, `analyze_g.py`, `make_summary6.py`, `common6.py`.")
w("- `results6/`:")
w("  - Phần 1: `spiral_tests.csv`, `spiral_acc_*.npy`.")
w("  - Phần 2: `charts_all.csv` (toàn lưới, cả khớp thật lẫn khớp ảo), `charts_best_IS_to_OOS.csv`, `charts_boot.csv`, `charts_fake_vs_real.csv`.")
open("KET_QUA_6_vi.md", "w").write("\n".join(L))
print("ok")
