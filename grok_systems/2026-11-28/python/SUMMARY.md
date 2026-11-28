# bt_3m — SP500 + Vàng, quét 3 tháng Fxaurum (XSD-10) — KẾT QUẢ MÔ PHỎNG PYTHON, CHƯA PHẢI MT5
Cửa sổ: 2026-08-20 → 2026-11-26 12:04 UTC. Nến XM M1 (bid, spread thật từng nến, ask = bid + spread), giờ server XM = giờ New York + 7h
(đã kiểm bằng tương quan với CME: UTC+3 tháng 9, UTC+2 tháng 11). Futures Fxaurum (ms epoch UTC) gộp theo phút UTC.
Chú ý thị trường trong cửa sổ: US500 7712 → 7228 (−6%), GOLD 4525 → 3570 (−21%) ⇒ chiều bán được hưởng lợi; có test gương (đảo chiều xu hướng).

Engine (code/engine.py): không SL; nhồi DCA (gap × gstep^k, lot × mult^k, maxN), hedge (khi đủ maxN và giá đi ngược hgap, lot = hr × lot chính, TP hedge tại giá đóng nến),
chốt non lớp mới nhất (trim), tỉa lớp lỗ nặng nhất bằng lãi đã gom (prune_k), chốt tổng (btp điểm × tổng lot chính), lot tăng theo vốn (comp).
Bảo thủ: trong nến xét cực trị bất lợi trước; nến nào vừa nhồi/hedge thì KHÔNG cho chốt; khớp nhồi khi gap qua mức thì lấy giá open; trượt giá 0,5×spread mỗi lệnh;
swap XM (US500 −1,24/+0,17, triple thứ Sáu; vàng −83,83/+20,64, triple thứ Tư); stop-out khi equity < 50% margin (US500 1:100, vàng 1:500).
Vàng: vốn 10k + nạp 20k khi equity < 3k; DD tính trên 30k. US500: vốn 10k.
Kiểm định: 3 fold (F1 20/08–30/09, F2 tháng 10, F3 tháng 11), spread×2/×3 + trượt 1×, vào trễ 2 nến, test gương, sốc gap ±5/10/20% tại lúc phơi nhiễm lớn nhất,
placebo 20 seed (giữ thời điểm, chiều ngẫu nhiên), DSR (N = 400.896 cấu hình/mã).
Bản engine cũ (lạc quan: cho nhồi rồi chốt trong cùng nến) đã bị loại; kết quả cũ để ở _biased_old_engine/, KHÔNG dùng.
Top 5 mỗi mã: mt5_ready/US500_top5.json, mt5_ready/XAU_top5.json (+ *_entries.csv giờ server XM, *_signal_minutes.csv).
Nhật ký chi tiết: *_stageC_candidates.csv, *_stageC_summary.json.
