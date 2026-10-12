# Vòng 24 — Đăng ký trước (12/10/2026 ~17:45 giờ VN), viết TRƯỚC khi chạy. MÔ PHỎNG.

## Dữ liệu (Yahoo miễn phí, D1, tải 12/10/2026 vào /workspace/du_lieu_ngay/v24, không vào git)
- 28 cặp FX (8 đồng tiền chính, mọi tổ hợp), vàng GC, bạc SI, bạch kim PL, dầu CL/BZ, khí NG, đồng HG, nông sản ZC ZS ZW KC SB CC CT (hợp đồng liên tục — có bước nhảy khi đáo hạn, ghi rõ là hạn chế),
  chỉ số US (^GSPC ^NDX ^DJI ^RUT), EU (^GDAXI ^FTSE ^FCHI ^STOXX50E), Á (^N225 ^HSI ^AXJO ^KS11). Tổng 54 tài sản. Dùng từ 2004-01-01.
- H4 (chỉ cho TrendBreaker H4): 7 FX + XAUUSD 2024–2026 (gộp từ M5) + US500/UK100 H4 Yahoo.
- W1 gộp từ D1 (W-FRI).

## Hệ (tham số cố định, một luật chung cho mọi tài sản, không chỉnh theo tài sản) — 12 phép thử
1. PAXG_ST D1 (vòng 23: Supertrend 10/4, chỉ mua, thoát khi lật).
2. TRENDBREAKER D1 và 3. TRENDBREAKER H4 (vòng 23).
4–11. Đảo chiều/MR vòng 22: RSI và MRZ × thoát TP / TR2 × D1 / W1.
12. EMA hồi về D1 (vòng 21/22: MR EMA20 k=2, độ dốc phẳng, TP chạm EMA, SL 2 ATR).

## Chi phí
- Spread (tỷ lệ giá, ×1 và ×1,5): FX chính (EURUSD GBPUSD USDJPY AUDUSD NZDUSD USDCAD USDCHF) 1,5 bps; cặp chéo có EUR/GBP/JPY 3 bps; cặp chéo còn lại 4 bps;
  vàng 2; bạc 5; bạch kim 8; dầu 4; khí 10; đồng 6; nông sản 8; chỉ số US 1; EU 1,5; Á 3 bps.
- Trượt giá 0,5 bps mỗi chiều (độ nhạy 1 bps). Swap 2,5 %/năm theo ngày lịch giữ lệnh. Trước phí: 0 hết.
- Mọi tài sản trừ drift: lợi nhuận lệnh − hướng × drift/nến (đo ở nửa phát hiện của tài sản đó) × số nến giữ.

## Phép thử pooled
- Discovery < 2015-04-01 ≤ holdout (H4: chia đôi theo thời gian như vòng 23).
- p chính: t một phía của trung bình lợi nhuận lệnh ở holdout với sai số chuẩn **gom cụm theo tuần vào lệnh** (cluster-robust).
- Kiểm tra phụ: bootstrap khối theo tuần (2.000 lần) cho trung bình lợi nhuận lệnh holdout, p một phía.
- Holm cộng dồn từ 12.445 trên p chính.
- SỐNG: Holm < 0,05 VÀ bootstrap p < 0,05 VÀ lãi cả 2 nửa sau phí VÀ lãi holdout ở spread ×1,5 + trượt 1 bps VÀ maxDD < 80 % trên danh mục tỷ trọng đều (mỗi lệnh 1/số tài sản).
