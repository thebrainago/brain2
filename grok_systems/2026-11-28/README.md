# Hệ thống đã lọc — SP500 & Vàng — 28/11/2026

Bản lưu các bộ tín hiệu đã lọc xong đêm 27–28/11/2026 (giờ Việt Nam, **Asia/Saigon, UTC+7**).

Mục đích: một chỗ để xem nhanh hệ nào được giữ, vào lệnh theo điều kiện nào, quản lý giỏ ra sao, và số liệu **MT5 tick thật 100%** so với **mô phỏng Python bảo thủ**.

**Trạng thái chung:** các bộ `v2` là **ứng viên chạy thử tiến mẫu (forward-test)** trên demo. Chúng được chọn trên chính cửa sổ 3 tháng 20/08–27/11/2026 nên mới là kết quả trong mẫu. Chưa đặt lệnh thật.

## Nên chạy thử bộ nào trước

Trên vốn 10.000 USD mỗi mã (vàng v2 cũng đã đo trên 30.000):

| Thứ tự | Bộ | Lý do |
|---|---|---|
| 1 | **US500_v2_c1** (nên bắt đầu bản **không hedge**, song song theo dõi bản hedge 0,5×) | Lãi MT5 +1.738 USD, DD 3,77%, qua spread×3 / đảo chiều / gap ±20%. Exness **Raw** an toàn hơn Standard khi giãn spread. |
| 2 | **US500_v2_c3** | Bản 1,0 lot an toàn hơn: +923 USD, DD 1,76%, PF 4,33. |
| 3 | **XAU_v2_c3** | Vàng hai chiều, DD thấp nhất: +2.581 USD / DD 2,23% trên 30k (hoặc +2.593 / DD 6,02% trên 10k). |
| 4 | **XAU_v2_c1** | Lãi cao hơn c3 nhưng DD lớn hơn: +4.924 USD, DD 6,24% (30k) / 15,47% (10k). Qua bài đảo chiều +21%. |
| Song song (dài hạn, không dùng tick Fxaurum) | `x_long_dca_L050_lin` (SP500) và `HedgeTay_gong` lot 0,08 hoặc `HedgeTay lc10` 0,12+tay 0,02 (vàng) | Đã kiểm 15–16 tháng trên MT5 tick thật. |

Ghép thử Python **US500 v2_c1 + XAU v2_c1** trên vốn 20k: lãi **+6.577,87 USD**, sụt giảm tối đa **9,29%**, tương quan 0,12 — hai mã gần như không đi cùng nhau.

**Lưu ý vận hành:** tín hiệu v2 cần tick hợp đồng tương lai Fxaurum sống (ES/GC). Chỉ riêng MT5 không tự tạo được tín hiệu này. Máy nhà phải tính tín hiệu rồi đẩy file lệnh vào EA.

## Cách đọc thông số quản lý lệnh

- **L0 / lot:** khối lượng lớp đầu.
- **Giãn (gap × gstep):** nếu giá chạy ngược thì nhồi lớp sau, khoảng cách lớp k là `gap × gstep^(k-1)`.
- **Tối đa lớp (maxN):** không nhồi thêm sau mức này.
- **Chốt giỏ (TP):** đóng cả giỏ khi tổng lãi đạt mức đặt sẵn (điểm × tổng lot chính). **Không có SL.**
- **Hedge:** mở lệnh ngược chiều khi lỗ tới ngưỡng (khoảng giá hoặc % số dư trên EA).
- **Prune / tỉa:** EA `BRAIN_XuLiLenh` dùng khi kiểm chứng CSV **không có prune**. Với US500 v2, prune hầu như không kích hoạt nên số MT5 vẫn khớp Python.

---

## Bảng hệ được giữ

Số MT5 là Strategy Tester, mô hình mọi tick thật, History Quality 100%, đòn bẩy 1:500, **không đặt lệnh thật**. Slot `E:\mt5_tester\p6` (US500Cash#), `E:\mt5_tester\p4` (GOLD.i#). DD = Equity Drawdown Maximal (gồm lỗ thả nổi).

### SP500 — cửa sổ 3 tháng (20/08–27/11/2026, M1)

| Tên | Tín hiệu vào lệnh | Lot / giãn / lớp / TP / hedge | MT5 tick thật (vốn 10k) | Python | Trạng thái |
|---|---|---|---|---|---|
| **v2_c1** | Sweep 15p, fade khi z > 1,8; ADX > 20; hai chiều; London/NY | 2,0 lot ×1; giãn 60×1,4; tối đa 3 lớp; chốt giỏ 6 giá; prune 1,5 (không kích hoạt) | Không hedge: **+1.738,22**, DD **3,77%**, 141 lệnh, PF 3,40. Có hedge 0,5× @ ~90 giá: **+1.591,44**, DD **3,74%**, 159 lệnh, PF 2,90 | +1.677,64 / DD 3,86%; spread×3 +557; gương +1.594 / DD 3,96% | **forward-test candidate** |
| **v2_c3** | Cùng tín hiệu v2_c1 | 1,0 lot ×1; giãn 45×1,4; tối đa 3; TP 6; prune 1,2; hedge 0,5× @ 180 (MT5 không kích hoạt) | **+923,05**, DD **1,76%**, 151 lệnh, PF 4,33 | +899,91 / DD 1,79% | **forward-test candidate** |
| **v2_c2** | Cùng tín hiệu v2_c1 | 1,0 lot ×1; giãn 45×1,4; tối đa 3; TP 6; hedge 0,75× @ 180; có compounding | *Chưa chạy MT5 tick thật* | +936,12 / DD 1,88%; spread×3 +157; gương +910 | **forward-test candidate** (chưa có MT5) |
| **c1** (v1) | Sweep fade z > 2,0; ADX > 20; hai chiều; London/NY | 1,0 lot ×1; giãn 45×1,4; tối đa 3; TP 6; hedge 0,5× @ 112,5 (MT5 không kích hoạt) | **+861,49**, DD **1,76%**, 142 lệnh, PF 5,69 | +874,33 / DD 1,79%; gương +868. **Không chịu spread×3 (−340)** — đây là lý do có bản v2 | forward-test candidate (bản cũ) |
| **c2** (v1) | VWAP momentum, **chỉ bán**, London/NY | 0,3 lot ×2; giãn 45×1,4; tối đa 3; TP 6; hedge 1,0× @ 112,5 (không kích hoạt) | **+188,48**, DD **0,45%**, 90 lệnh, PF 3,93 | +190,27 / DD 0,48% | forward-test candidate (nhỏ, bảo thủ) |
| **c5** (v1) | Sweep fade z > 2,0; ADX > 20; hai chiều; London/NY | 1,0 lot ×2; giãn 6×1,0; tối đa 3; TP 6; không hedge | **+2.596,67**, DD **10,43%**, 248 lệnh, PF 18,21 | +2.716 / DD 11,07%. **Cháy nếu gap ±20%** | giữ có điều kiện |

### SP500 — dài hạn 16 tháng (21/07/2025–27/11/2026, vốn 10k)

| Tên | Tín hiệu / cách vào | Lot / quản lý | MT5 tick thật | Python | Trạng thái |
|---|---|---|---|---|---|
| **x_long_dca_L050_lin** | Chỉ mua, nhồi DCA khung H1 (không dùng order-flow) | Lot 0,5 tăng tuyến tính | **+8.320,60**, DD **28,57%**, 1.044 lệnh, PF 1,93 | không có | **forward-test candidate** |
| **tay_v2 L050** | Hệ tay_v2, hedge 1× | L0 0,50 | **+2.395,68**, DD **26,38%**, 8.223 lệnh, PF 4,33 | không có | **forward-test candidate** |
| **tay_v2 L030** | Hệ tay_v2, hedge 1× | L0 0,30 | **+1.442,45**, DD **16,82%**, 8.198 lệnh, PF 4,37 | không có | **forward-test candidate** |

### Vàng hai chiều — cửa sổ 3 tháng (20/08–27/11/2026, M1)

Các bộ v1 chỉ ăn chiều giảm đã bị loại. Hai bộ dưới đây được thiết kế hai chiều và đã qua bài đảo chiều gương (+21%).

| Tên | Tín hiệu vào lệnh | Lot / giãn / lớp / TP / hedge | MT5 tick thật | Python | Trạng thái |
|---|---|---|---|---|---|
| **v2_c1** | VWAP reversion, \|độ lệch\| > 3 ATR; ADX > 20; hai chiều; mọi giờ | 0,03 lot ×1; giãn 6×1,4; tối đa 4 lớp; chốt giỏ 3 giá; **không hedge** | Vốn 30k: **+4.924,44**, DD **6,24%**, 542 lệnh, PF 5,52. Vốn 10k: cùng lãi, DD **15,47%** | +4.900,23 / DD 6,91% (trên 30k); gương +4.556 / DD 7,1% | **forward-test candidate** |
| **v2_c3** | Sweep fade z > 1,8; ADX > 20; hai chiều; London/NY | 0,03 ×1,3; giãn 6×1,4; tối đa 4; TP 3; prune 1,5 (EA không có); hedge 0,5× @ ~18 giá | Vốn 30k: **+2.580,60**, DD **2,23%**, 351 lệnh, PF 2,90. Vốn 10k: **+2.593,20**, DD **6,02%**, 347 lệnh, PF 2,97 | +3.160,06 / DD 2,21% (có prune); không prune +2.804; gương +3.211 / DD 2,2% | **forward-test candidate** (bền hơn) |

### Vàng — dài hạn 15 tháng (01/09/2025–27/11/2026)

| Tên | Tín hiệu / cách vào | Lot / quản lý | MT5 tick thật | Python | Trạng thái |
|---|---|---|---|---|---|
| **HedgeEMA H1 L024** | Đường EMA khung H1 (không dùng order-flow) | Lot 0,24 trên vốn 30k | **+40.250,28**, DD **45,09%**, 525 lệnh, PF 1,12 | không có | **forward-test candidate** (DD cao) |
| **HedgeTay lc10 L012 + tay 0,02** | Hệ HedgeTay lc10 (nguồn EA không có trong repo) | Lot gốc 0,12, tay 0,02, vốn 10k | **+21.155,46**, DD **58,84%**, 12.046 lệnh, PF 1,12 | không có | **forward-test candidate** (cân bằng trên 10k) |
| **HedgeTay gồng lot 0,08** | HedgeTay gồng lỗ, không đóng lỗ tổng | Lot gốc 0,08 | Vốn 10k: **+10.013,99**, DD **22,03%**. Vốn 30k (10k+20k nạp): cùng lãi, DD **12,15%**. 31.380 lệnh, PF 1,08 | không có | **forward-test candidate** (an toàn nhất nhóm HedgeTay) |

Biến thể liên quan đã đo, không đưa vào nhóm ưu tiên: `HedgeTay lc10` lot 0,14 đạt +24.152,41 nhưng DD 68,79%.

---

## Đã loại (tóm tắt)

- **Vàng v1 c1–c5:** mọi bộ điểm cao trong Python chỉ ăn nhịp vàng giảm 21%; khi đảo chiều gương đều lỗ nặng hoặc cháy.
- **XAU_v2_c2:** phụ thuộc prune (không prune lỗ 2.373 USD); Exness Standard ×2 cháy. Không forward-test.
- **US500_c3:** test gương lỗ (−171, DD 14,4%).
- **US500_c4:** placebo chỉ 15th percentile, không vượt nhóm ngẫu nhiên.
- **SP500_Dca** (`s_dcaA`, `s_goB`): mọi bản lỗ hoặc cháy (DD 15–100%).
- **HedgeEMA lot ≥ 0,16 trên vốn 10k:** DD vượt 80% (L016 80,74%, L020 95,91%).
- **TayV2 tỉa trên vàng** (`g_tia_*`): lỗ nặng hoặc cháy.
- **Lọc vĩ mô / IBS** trong quét 3 tháng: lọc vĩ mô làm kết quả kém đi; IBS yếu nhất.
- **Engine Python cũ** (cho nhồi rồi chốt trong cùng nến): lạc quan, đã loại.

---

## Cấu trúc thư mục này

```
README.md                                          — tài liệu này
HuongDan_BoTinHieu_SP500_Vang_2026-11-28.pdf      — hướng dẫn có hình (12 trang)
configs/
  systems_kept.json                                — bảng hệ giữ, máy đọc được
  US500_v2_top3.json, XAU_v2_top3.json             — cấu hình Python v2
  US500_top5.json, XAU_top5.json                   — cấu hình Python v1 (gồm cả bộ đã loại)
entries/                                           — danh sách lệnh vào (giờ server XM = NY+7)
sets/
  p6/                                              — .ini + .set tester US500
  p4/                                              — .ini + .set tester vàng
mt5/
  FINAL_OVERNIGHT_REPORT_2026-11-28.md
  SUMMARY_2026-11-28.md
  TONG_HOP_MT5_20261128.csv / .json
  reports_nho/                                     — báo cáo htm/png của hệ giữ, chỉ file < 5 MB
python/
  SUMMARY.md, SUMMARY_V2.md
  v2_US500_finalists.csv, v2_XAU_finalists.csv
code/                                              — engine mô phỏng Python (engine.py, v2.py, …)
```

Báo cáo htm của nhóm HedgeTay dài 23–61 MB nên **không** đưa vào đây; chúng vẫn nằm tại `E:\GrokWork\mt5_runs\reports\`. Kết quả đã tóm trong CSV/JSON và README.

Bản sao dữ liệu box (kèm PDF) cũng có tại `E:\GrokWork\bt_3m\box_results\results\`.

## Nguồn kiểm chứng

- Mô phỏng Python: nến XM M1 (spread thật từng nến), tick Fxaurum gộp 1 phút, engine bảo thủ (cực trị bất lợi trước; không nhồi rồi chốt cùng nến; trượt 0,5×spread; swap XM; stop-out khi equity < 50% margin).
- MT5: `BRAIN_XuLiLenh` chế độ VAO_CSV cho các bộ v2/v1 CSV; các hệ dài hạn dùng EA tương ứng (`x_long_dca`, `tay_v2`, `HedgeEMA`, `HedgeTay`).
- Tổng 57 lượt MT5 tick thật trong đêm 28/11/2026. Máy nhà đã tắt sạch lúc **02:41 (UTC+7)** sau khi sàn CME đóng cửa.

## Việc chưa làm trong gói này

Forward-test demo XM và Exness Raw, đo phí Raw thật, và chạy MT5 gộp hai mã để xem sụt giảm chung — cần bật máy và cài lên demo, tài khoản thật giữ tắt AutoTrading.
