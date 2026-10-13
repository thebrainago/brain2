# Vòng 26 — tiền đăng ký (13/10/2026 sáng, TRƯỚC khi chạy) — MÔ PHỎNG
Cơ sở: MT5 v24 (reports/mt5_v24): MRZ trailing D1 lãi trên GBPUSD/AUDUSD, lỗ EURUSD; phí XM thật (phi_xm_that.py): không swap FX, spread lúc 00h gấp 2–3×.
Hệ: MRZ_TR2_D1, RSI_TR2_D1 (v19.tin_hieu + v22.chay, stop 1,5 ATR, trailing 2 ATR, giữ tối đa 72 nến). Ghép phong cách (luôn ghép):
- KHONG (gốc), XU_HUONG (chỉ vào theo hướng dốc EMA200), VOL_THAP (ATR14 < trung vị ATR14 250 nến trước — chế độ đi ngang),
- DANH_MUC: gộp lệnh hệ + DINH20_TR2_D1 (phá vỡ/xu hướng) cùng nhóm tài sản.
Nhóm tài sản: GBPUSD, AUDUSD, POOL_FX (7 cặp chính).
Phần A (Yahoo D1 2004–2026, tách 2015-04-01 phát hiện/kiểm): vào = open D1 kế tiếp làm PROXY cho giờ +1..+3h; phí spread XM trung vị (không phải spread 00h). Đối chiếu một ô phí 00h.
Phần B (M5 HistData giờ server NY+7, 2024-01→2026-09, tách 2025-05-15): nến D1 dịch giờ k = 0,1,2,3 (ngày bắt đầu lúc k:00) → tín hiệu tại đóng nến, vào open nến kế = k:00 thật. k=0 phí spread 00h XM, k≥1 spread trung vị XM. Chỉ hệ gốc (KHONG).
Phí sau: spread XM + trượt 0,5 bps/chiều, swap 0. Căng: spread ×1,5 + trượt 1 bps.
Qua = Holm cộng dồn (12.819 + số ô vòng này) < 0,05 VÀ boot < 0,05 VÀ TB phát hiện > 0 VÀ TB kiểm > 0 (sau phí) VÀ căng kiểm > 0 VÀ maxDD < 80 %.
Seeker (phần C): luật mới bộ đọc dịch được → D1 pool FX + GBPUSD/AUDUSD, trước phí → sau phí XM; cùng cổng, cộng vào họ Holm.
## Sửa phí (8:41, trước lần chạy chính)
Lần chạy sơ bộ dùng bảng phi_xm_that (54 ô, lưu reports/vong26_so_bo_phi_bang.json, 0 sống) — VẪN đếm vào Holm.
Lần chính: spread = trung vị spread mở nến H1 đo từ du_lieu_fx/*_h1_tick_ba_ny7.csv theo giờ server (GBPUSD 00h 3,9 bps ≈ 5,2 pip... 02h 0,74 bps; AUDUSD 00h 5,3 bps, 02h 1,65 bps). Phần A dùng spread 02h (giờ vào mặc định EA), đối chiếu 00h. Phần B dùng spread giờ k. AUDUSD MT5 2004–2015 chất lượng 4 % → coi là chưa kiểm chứng.
