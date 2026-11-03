# Đánh giá Seeker trên box + thiết kế song song box/máy nhà (03/11/2026, UTC+7)

## 1. Trang đã đăng ký bằng thebrainago@gmail.com (từ Gmail, không ghi mật khẩu/mã)
| Trang | Tên hiển thị | Ngày (UTC+7) | Liên quan tìm EA/lịch sử kiểm chứng |
|---|---|---|---|
| MQL5.community | Vanh1799 | mail từ 15/09 | **Cao** – Signals, Market |
| Myfxbook | vanhvanhvanh | mail từ 25/08 | **Cao** – nhưng box bị Cloudflare 403 |
| FX Blue | thebrainalgo | 13/09 (đăng ký), 13/10 (mã) | **Cao** – thống kê tài khoản công khai |
| Forex Factory | vanhvanh | 13/10 | Trung bình – diễn đàn/Trade Explorer |
| cTrader ID / cTrader Store | thebrainago | 13/10 | Trung bình – cBot, copy strategy |
| TradingView | (theo dõi QuantAlgo, MarkitTick, AlgoAlpha…) | mail từ 06/09 | Trung bình – strategy Pine |
| Quantpedia | (newsletter) | 13/10 | Trung bình – chiến lược học thuật |
| Babypips | thebrainago | 13/10 | Thấp |
| FMP (financialmodelingprep) | (API key, không ghi) | 30/08 | Thấp – dữ liệu |
| OKX | UID có trong mail | 02/11 (xác minh xong) | Thấp – sàn crypto |
| X | @Thebrainago | 13/10 | Thấp (không tin MXH) |
| Reddit | (r/algotrading digest) | 03/10 | Thấp |
| Facebook | Vanh Vanh | 13/10 | Không |
| GitHub | thebrainago | — | Hạ tầng |
| Suno, Foody, Google | — | — | Không |
Không thấy mail đăng ký Exness, LiteFinance, Telegram, Darwinex, ZuluTrade.

## 2. Số đo Seeker trên box (đo thật)
- Box: 8 nhân, RAM 15 GiB (dùng 10, còn ~4,9 GiB), load ~1,3–1,9, không swap.
- Lần quét công khai 03/11 05:41→06:00 (~19 phút, `data/cong_khai/run.log`): 1600 id MQL5, 1562 đọc được (97,6%), 38 không đọc; **1065 ĐẠT** (68,2%), 483 ĐẠT có tuổi ≥12 tháng.
- Nguồn bị chặn từ box: Myfxbook (Cloudflare 403), Exness Social Trading & my.litefinance.vn (TLS), LiteFinance chi tiết trader (chuyển hướng) → 16 trader CHƯA ĐO ĐƯỢC.
- Sổ `ket_qua.csv` 2291 dòng: CONG_KHAI 1065 ĐẠT; mt5 (máy nhà) 1 real_tick ĐẠT + 1 salvage ĐẠT, ~1187 BỊ_THAY_THẾ; mô phỏng python 6 ĐẠT /14 KHÔNG ĐẠT.
- **Khoảng trống chính:** ĐẠT công khai ≠ EA có mã. Số tín hiệu ĐẠT dẫn tới EA test được: mới có 2 EA nháp từ dịch ngược top10 (commit 06e5d924), chưa có kết quả real-tick → CHƯA ĐO ĐƯỢC tỷ lệ chuyển đổi.
- Seeker web/Telegram/X cũ: heartbeat cuối 12/08 → không chạy liên tục; số mục/lần chạy CHƯA ĐO ĐƯỢC.

## 3. Đề xuất
**Có**, nên có 1 phiên Grok Bot chuyên Seeker trên box (khám phá rẻ, hiệu quả 68% ĐẠT/19 phút), nhưng thước đo phải là "EA test được", không phải "tín hiệu ĐẠT".
- **Box:** quét MQL5 Signals/Market định kỳ (cache 72h), FX Blue công khai, Telegram, TradingView strategy → dịch ngược lịch sử deal → sinh EA nháp MQL5 + mô phỏng python lọc sơ bộ; đẩy vào hàng đợi.
- **Máy nhà (Windows, MT5, IP nhà):** real-tick tester cho EA nháp/EX5, Myfxbook/Exness/LiteFinance (bị chặn từ box), đăng nhập MQL5 tải/thuê demo EX5, ghi kết quả.
- **Đồng bộ qua git:** `hang_doi/can_test/*.json` (box ghi) → máy nhà pull, test, ghi `hang_doi/da_test/*.json` + dòng `ket_qua.csv` → push; mỗi việc 1 file (tránh xung đột), có khóa `dang_lam_<may>`. Máy nhà offline thì hàng đợi tích lại, không chặn box.
- Ưu tiên: top tín hiệu ĐẠT tuổi ≥12 tháng có kiểu lệnh dịch ngược được (lưới/xu hướng đơn giản).
