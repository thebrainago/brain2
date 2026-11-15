# Ứng viên "chưa pass" đang vướng ở đâu (Evo, 15/11/2026)

Nguồn: `nao.db` QUANTLAB trên box (kết quả mới nhất, không tính bản bị thay), 1.236 giả thuyết có verdict. Dữ liệu đến 2026-10-02, holdout 60/40 bắt đầu 2023-05-08 (H4).

## 1. Ứng viên tồn đã chạy nốt
- Hàng đợi `viec` không còn việc chờ; `candidate_queue` rỗng (con trỏ 775).
- Vòng quét 1784 còn 7 cặp chưa chạy do `qua_gio` giết (USDCHF D1, USDJPY H1/H4/D1, XAUUSD H1/H4/D1). Đã chạy một lần riêng, không bật lại dieu_phoi: **0 giả thuyết được đăng ký**. Toàn bộ ~3.500 tổ hợp/cặp có Sharpe khám phá dưới MDE (ví dụ USDJPY D1: tốt nhất 0,83 < MDE 0,94). Nghĩa là đúng hay sai thì kiểm định cũng sẽ FAIL.
- Tồn thật sự: **164 dòng trong `reports/CHO_KIEM_TICK_MT5.md` chưa được kiểm**, 0 dòng đã kiểm. Việc `mt5_tick` chỉ ghi vào danh sách, chưa bao giờ chạy Strategy Tester. Đây là lỗ hổng của pipeline.

## 2. Trượt theo tiêu chí chuẩn (OOS ≥30 lệnh, PF ≥1,20, Sharpe ≥0,30, lãi >0, p ≤0,05; đã tính phí)
| Tiêu chí trượt | Số ứng viên (/1.236) |
|---|---|
| p > 0,05 so với placebo | 1.176 |
| PF < 1,20 | 1.078 |
| Sharpe < 0,30 | 1.007 |
| Lãi OOS ≤ 0 | 708 |
| Lệnh OOS < 30 | 464 |
| **Qua cả 5 tiêu chí** | **17** |

Cổng của repo (1.004 FAIL): placebo 1.004, alpha 987, lãi 10%/DD 80% 957, edge vượt spread 900, hơn mua-giữ 872, đủ lệnh 359, ăn khe đảo ngày 169.
Lưu ý: 237 "PASS" của repo là PASS Python ở chế độ `loi_nhuan` (đã tắt FDR; 220/237 trượt placebo), nên không phải pass theo chuẩn trên. Chính `quantlab.py` cũng ghi rằng holdout cũ đã bị nhìn nhiều lần, nên không phát PASS cuối từ đó.

## 3. Nguyên nhân (một ứng viên có thể dính nhiều nhóm)
| Nhóm nguyên nhân | Số |
|---|---|
| Âm ở OOS dù đủ lệnh (edge chỉ có trong IS, tức khớp quá khứ) | 470 |
| Dương nhưng không hơn dịch ngẫu nhiên (p > 0,05) | 468 |
| Quá ít lệnh OOS | 464 |
| Phí ăn hết edge (lãi gộp dương, sau phí âm) | 293 (95 ca swap chiếm >50% phí) |
| Dương nhưng PF thấp | 24 |
| DD > 30% | 10 |
| Vào lệnh chưa giải mã (replay statement) | 0 trong sổ này; nhánh replay vẫn không bao giờ tính là pass |

Gốc rễ: đã thử khoảng 1.236 biến thể. Với p ≤ 0,05, chỉ do may mắn đã có thể ra khoảng 62 ca qua. Thực tế có 17 ca, nên **chưa phân biệt được với nhiễu**. Thêm vào đó, mỗi tài sản đơn lẻ có MDE cao (khoảng 0,5–0,9 Sharpe), lớn hơn mọi edge thực tế (0,2–0,4).

## 4. Cách khắc phục
| Cách | Trung thực? |
|---|---|
| Gộp nhiều cặp chéo/khung với **luật đóng băng** để có nhiều lệnh OOS hơn (đã có `kham_pha_gop`) | Trung thực |
| Thu hẹp không gian tìm kiếm (ít biến thể, đăng ký trước) để giảm phạt đa kiểm định | Trung thực |
| Walk-forward re-fit, chấm điểm chỉ trên các đoạn chưa nhìn | Trung thực, tốn CPU |
| Thoát lệnh theo phí: chỉ vào khi biên kỳ vọng > k×spread, chuyển H1 sang H4/D1, tránh giữ qua đêm khi swap âm | Trung thực nếu chốt k trước |
| Bộ lọc chế độ chốt **trước** (SMA200, VIX ≥ 20 theo tài liệu) | Trung thực nếu cố định trước; chọn sau khi xem OOS là overfit |
| Dữ liệu forward thật (sau 2026-10-02) + demo/MT5 tick | Cách duy nhất cho ra pass thật |
| Hạ ngưỡng, chọn biến thể tốt nhất trên OOS, chỉnh tham số theo holdout | **Overfit, không làm** |

## 5. Thử nghiệm: chuyển luật sang cặp khác (đóng băng tham số, có phí, holdout 2023-05 đến 2026-10)
Lấy 17 ca qua chuẩn, chạy nguyên luật trên 10 cặp FX khác:
- Dương trên ≥ 7/10 cặp: `mat_can_bang_lenh_dong_cua` EURUSD H4 (9/10), `mua_ibs_thap_kl_mong…` AUDCAD H4 (9/10, nhưng PF chỉ 1,0–1,2), `mua_khoi_luong_can_kiet…` AUDNZD H1 (8/10), `pamxa_buy_signal` EURGBP D1 (7/10), `ns_keltner20_<_q5_giu1` EURGBP D1 (7/10), `long_smc_entry` EURGBP D1 (7/10).
- 11 ca còn lại dương trên ≤ 6/10 cặp, nhiều khả năng là may mắn. Ví dụ AUDCHF H1 "nến đầu ngày" có Sharpe 3,16 nhưng phí bằng 2 lần lãi và chỉ dương 4/10 cặp.
- Cảnh báo: các cặp dùng cùng giai đoạn và tương quan với nhau; holdout đã bị nhìn. `mat_can_bang_lenh_dong_cua` từng **−1,65% trên MT5 tester** (15/09), nên Python và MT5 đang lệch nhau.

## Kết luận
**Không có ứng viên nào pass thật.** 6 ứng viên trên là "ứng viên mạnh hơn", bước tiếp: kiểm MT5 tick và forward demo, không đổi tham số.
