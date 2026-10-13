# Vòng 27 — TIỀN ĐĂNG KÝ (ghi 13/10/2026 trước khi chạy, MÔ PHỎNG)
Hệ gốc: MRZ (z50 ±2, thoát TR2) — near-miss vòng 26 (AUDUSD/GBPUSD vào 02h). Luật Seeker: EMA12/26 (mql5 77653), RSI_Exhaustion (77738).
Seeker v27 (tiền xử lý bộ đọc) KHÔNG ra luật mới → không có ô "luật Seeker mới"; dùng 2 luật cũ làm bộ lọc ghép.
Lọc theo tầng: (1) trước phí, cả hai nửa > 0 mới sang (2) sau phí XM (spread đo theo giờ cho 7 FX chính; tài sản khác = bảng phi_xm_that/v24, ghi rõ) + trượt 0,5 bps/chiều; (3) áp lực ×1,5 spread + 1 bps.
Ô không qua tầng 1 vẫn tính 1 phép thử Holm với p = 1.
Ô (cố định trước):
- P1 D1 Yahoo 2004–2026, tách 2015-04-01: MRZ × {AUDUSD, GBPUSD} × {EMA_DONG, EMA_NGUOC, RSI_CAN (mua chỉ khi RSI14 D1 hôm trước < 35, bán > 65)} (6); MRZ pool FX chéo (mọi *_X ngoài 7 chính) (1); MRZ pool hàng hoá+chỉ số (1).
- P2 khung nhỏ H1/H4 từ HistData M5 2024–2026, tách 2025-05-15: MRZ × {H1, H4} × {AUDUSD, GBPUSD, POOL_FX7, POOL_MOI (EURJPY, GBPJPY, EURGBP, XAGUSD, WTI, SPX, NSX, DAX nếu tải được)} (8).
Qua = Holm cộng dồn < 0,05, p_boot < 0,05, cả hai nửa sau phí > 0, ×1,5 kiểm > 0, maxDD < 80 %.
