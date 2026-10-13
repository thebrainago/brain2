# HÀNG CHỜ MÁY NHÀ (việc box không làm được). Cập nhật 13/10/2026 (vòng 27).
**Luật**: dữ liệu tester MT5 đặt ở ổ **D:** hoặc RAM disk, KHÔNG BAO GIỜ ổ C:; xoá sau khi chạy xong (Bases/history + tester cache).
Không đăng nhập mạng xã hội, không mua gì, không vượt Cloudflare bằng công cụ lách.

| # | Việc | Trạng thái |
|---|---|---|
| 1 | MT5 backtest EA MRZ mới (`ea_MeanRevZ5.mq5`/MRZ, `InpGioVao=2`) trên **GBPUSD#** và **AUDUSD#** 2016-01-01 → 2026-10, D1, "Every tick based on real ticks", tài khoản XM thật (Standard/Cash Ultra Low) | CHỜ |
| 2 | Cùng EA trên **GBPUSD** 2004–2015 (lịch sử dài; ghi chất lượng mô hình %) | CHỜ |
| 3 | So `InpGioVao=0` vs `2` cùng giai đoạn (đo chênh phí thật theo giờ) | CHỜ |
| 4 | Nguồn bị chặn trên box: TradingView scripts/ideas, fxblue, quantpedia (234 mục vòng 26) — đọc bằng trình duyệt thường ở máy nhà, chỉ lưu tóm tắt + URL | CHỜ |
| 5 | Báo cáo trả về: `reports/mt5_v27/*.htm` + CSV lệnh; box sẽ so với mô phỏng Python | CHỜ |
Sau khi xong: xoá dữ liệu tester ở D:/RAM disk.
