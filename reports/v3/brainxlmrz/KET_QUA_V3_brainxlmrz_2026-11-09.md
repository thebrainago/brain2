# V3 brainxlmrz GBPUSD# H4 — lần chạy thật đầu tiên (09/11/2026, máy nhà)

**CHƯA WF**: tham số cố định (bộ gốc salvage), chưa có lịch walk-forward 12/3.

- EA: `BRAIN\BRAIN_XuLiLenh.ex5` bản 30/10 (mq5 hash B10A892B, cùng bản dựng báo cáo salvage), slot portable `E:\brain2_grok\mt5_slots\g12` (tài khoản demo XM, Bases junction `shared_bases`).
- `.set`: `brainxlmrz_GBPUSD_H4_goc.set`, dựng lại đúng 48 input từ phần Inputs của `salvage\od_v2r2cap_gbpusd_brainxlmrz_XM_KIEM_XM_CSV.htm` (thư mục salvage không có file .set). InpVao=1, N=100, Z=2, Lot0=0.1, MaxTang=9, Buoc=TP=0.002876, hedge tắt.
- Model=4 (mỗi tick theo tick thật), vốn 10.000 USD, đòn bẩy 1:500, đến 2026.10.31.

| Lượt | Kỳ | Tick thật | Lãi ròng | CAGR kép | DD equity max (tuyệt đối) | DD equity tương đối | PF | Lệnh | Giữ max | Lot mở max | Swap tester | Kết luận |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 2014.01–2026.10 | 22% | −10.030,30 | cháy | 11.163,60 (101,44%) | 101,44% | 0,09 | 43 | 81,5 ngày | 0,9 | 0,00 | **CHÁY**: stop-out 14/11/2014, test dừng |
| A2 | 2016.01–2026.10 | 26% | +29.276,40 | 13,46% | 21.733,00 (78,81%) | **92,03%** (18.561,10) | 5,68 | 1.009 | 714,0 ngày | 1,8 | 0,00 | **TRƯỢT** (DD > 80%) |
| B | 2024.01–2026.10 | 99% | +8.110,60 | 23,34% | 2.871,80 (21,39%) | 21,39% | 5,13 | 281 | 22,8 ngày | 1,1 | 0,00 | đạt riêng lượt B |

**Swap:** symbol `GBPUSD#` trên tài khoản demo đang đăng nhập trả swap = 0 cho mọi deal. Ước hậu kỳ bằng swap XM micro đo 10/2026 (mua −4,35, bán −2,96 điểm/lot/đêm, ×3 đêm thứ 4): A2 −7.025,9 → CAGR 11,42%; B −576,4 → CAGR 21,94%; A −444,1. Đây là ước tính, không phải số tester.
**Không chạy được trên GBPUSDmicro**: tài khoản demo trên g12 và g2 không có symbol này ("symbol GBPUSDmicro not exist").

**Kết luận V3:** TRƯỢT. Lượt A nối dài cháy từ 2014; bắt đầu 2016 thì DD equity 92,03%. Lượt B chỉ là giai đoạn thuận lợi 2024–2026.
