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

## Ca máy nhà 7h30–15h (7h30 phút) — thêm 13/10/2026 (vòng 27). Thứ tự = ưu tiên
**Luật tester**: thư mục dữ liệu/Agents/Bases của MT5 trỏ sang **D:** hoặc RAM disk (vd. `R:\mt5_tester`), KHÔNG ổ C:; cuối mỗi việc xoá `Tester\Agent-*\` + `bases\...\history` tải về; ghi lại dung lượng đã xoá.
Nguồn bị chặn: chỉ đọc bằng trình duyệt thường như người dùng, không công cụ lách Cloudflare, không đăng nhập mạng xã hội; lưu tóm tắt luật + URL vào `reports/seeker_may_nha/`.

| # | Giờ | Việc | Ước tính | Trạng thái |
|---|---|---|---|---|
| 6 | 7:30 | Chuẩn bị: tạo RAM disk/`D:\mt5_tester`, trỏ tester, kiểm tài khoản XM thật, `git pull` | 15′ | CHỜ |
| 7 | 7:45 | Việc 1+3 ở trên: MRZ `InpGioVao=2` vs `0`, GBPUSD#/AUDUSD#, 2016→2026-10, real ticks (4 lần chạy) | 60′ | CHỜ |
| 8 | 8:45 | MRZ cấu hình đăng ký trên NZDUSD#, AUDCAD#, EURGBP#, USDCAD# (đa cặp, việc VONG_LAP 1) | 50′ | CHỜ |
| 9 | 9:35 | MRZ thoát trailing ATR×1,5 / ×2,5 / thời gian 5 nến trên AUDUSD#, GBPUSD# (6 lần, việc VONG_LAP 3) | 45′ | CHỜ |
| 10 | 10:20 | Stress: spread cố định ×1,5 (custom symbol hoặc "Random delay") trên cấu hình tốt nhất từ #7 | 25′ | CHỜ |
| 11 | 10:45 | Xuất spread thật theo giờ (tick history) 12 cặp FX + XAUUSD, US500, GER40 → CSV `reports/mt5_v27/spread_gio/` | 30′ | CHỜ |
| 12 | 11:15 | Xuất giá D1/H1 XM cho US500, GER40, XAUUSD 2010→ (đối chiếu Yahoo, việc VONG_LAP 9/22) | 20′ | CHỜ |
| 13 | 11:35 | Xoá dữ liệu tester + cache (D:/RAM), ghi dung lượng | 10′ | CHỜ |
| 14 | 11:45 | Đọc TradingView Scripts (bộ lọc Strategies, mean reversion/breakout, FX) — 20 mục mới: tóm tắt luật + URL | 45′ | CHỜ |
| 15 | 12:30 | TradingView Ideas FX D1 — 10 ý có luật rõ | 20′ | CHỜ |
| 16 | 12:50 | Forex Factory (forum EA threads + Trade Explorer công khai) — 10 luồng hệ có kết quả dài | 30′ | CHỜ |
| 17 | 13:20 | fxblue (trang thống kê công khai) — 10 tài khoản ≥ 2 năm, ghi phong cách/DD/giữ lệnh | 20′ | CHỜ |
| 18 | 13:40 | quantpedia (mục miễn phí) + quantifiedstrategies — chiến lược FX/chỉ số mùa vụ | 25′ | CHỜ |
| 19 | 14:05 | SSRN (box 403): tìm "FX anomaly", "turn of the month index", "currency carry momentum" — 10 bài, tóm tắt + URL | 20′ | CHỜ |
| 20 | 14:25 | babypips forum, arabictrader, forex_nawigator, gestaltu, quant.stackexchange, tutim_fxmacrodata/quantforhire (đều 403/captcha trên box) — mỗi nguồn 3 mục | 25′ | CHỜ |
| 21 | 14:50 | Đẩy báo cáo `reports/mt5_v27/*.htm` + CSV + tóm tắt nguồn, kiểm ổ C: không phình, xoá tester lần cuối | 10′ | CHỜ |
Tổng ≈ 7h30′. Nguồn cần đăng nhập (myfxbook, darwinex, collective2, zulutrade, ctrader, các API key) KHÔNG nằm trong ca — chỉ làm nếu chủ dự án tự đăng nhập.
