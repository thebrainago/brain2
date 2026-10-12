# Vòng 23 — Đăng ký trước (12/10/2026 ~17:30 giờ VN), viết TRƯỚC khi chạy. MÔ PHỎNG.

Nguồn luật: trang script công khai TradingView (WebFetch 12/10/2026, HTTP 200 cả 15 trang). Chỉ có MÔ TẢ (không chép/đọc mã Pine),
nên mọi bản dịch là **bản dịch theo mô tả công khai**. Tham số tác giả không ghi rõ trong mô tả → chọn TRƯỚC ở bảng dưới, không tối ưu.
Lưu ý: tên trong hàng chờ khác tên trang thật ở 3 ID: VW4M6aCA = "NAS100 3-Min Breakout + Reverse After SL"; CDhXq8DM = "Nifty Futures ORB - Smart Trail";
sf4Hf10r = "8PM (MGC 5M)". Dịch theo trang thật.

| ID | Tên dịch | Luật (tóm tắt) | Khung gốc | Khung chạy |
|---|---|---|---|---|
| PdJvHIfQ | HTF_LEVEL | H/L nến khung lớn trước (H4; D1→W1); chạm đầu tiên ghi cực trị; vào khi đóng vượt cả mức và cực trị chạm; SL đáy/đỉnh 10 nến; TP 2R | — | M15 H1 H4 D1 |
| o9qty0BL | PAXG_ST | Supertrend(10,4) lật lên → mua; lật xuống → thoát; chỉ mua; bỏ phần nhồi lệnh (là sizing) | H4 | M15 H1 H4 D1 |
| 2u7KKcCG | TRENDBREAKER | Trendline qua 2 pivot (n=5) hạ dần/nâng dần; đóng vượt line + 0,1 ATR; AO làm mượt quay đầu; mỗi line 1 lần, hết hạn 100 nến; SL 1,5 ATR, TP 2R, BE 1R, trail 2 ATR từ 2R | — | M15 H1 H4 D1 |
| asmZOvXE | EMA_FIB | Nến mở ≤ cả EMA50 và R1 Fib (P+0,382·(H−L) kỳ trước: ngày; H4→tuần; D1→tháng), đóng trên cả hai; SL đáy nến tín hiệu; TP 2R | — | M15 H1 H4 D1 |
| G6KZH6HX | PULLBACK | EMA20>EMA50 và EMA50 > 10 nến trước; RSI(4) ≤ 30; trong 5 nến đóng > đỉnh nến trước; SL đáy cửa sổ − 0,5 ATR; trail đóng − 3 ATR | H1 | M15 H1 H4 D1 |
| LcA4mcE6 | CONFLUENCE | Điểm 0–100 = xu hướng(EMA20/100) + RSI14 + ER20 (đủ ở 0,4) + ATR percentile 100 (đủ 0,2–0,8) + volume trung tính 10; vào khi cắt lên 70, thoát < 40; trail 3 ATR | H1 | M15 H1 H4 D1 |
| U0wTnRuE | APEX | Range filter(100, 2,5) + Heikin-Ashi làm mượt(10/10) + HA khung lớn (nến đã đóng) cùng hướng, lần đầu đồng thuận; SMI(10,3,3) không quá ±60; trail 2 ATR | M5 | M5 M15 H1 H4 D1 |
| Z8EhgIzs | TREND_ENGINE | Tracker = Supertrend(10,2) lật; điểm 6 phiếu (tracker, giá vs linreg50, dốc linreg, RSI>50, RSI>SMA14 RSI, +DI>−DI) ≥ 50 %; SL/trail theo tracker; thoát khi lật ngược | — | M15 H1 H4 D1 |
| rvBgD3aP | ELLIOTT | Zigzag pivot n=5; sóng đẩy 5 sóng hợp lệ ≥ 1,5 ATR; chế độ Reversal: vào ngược khi pivot 5 xác nhận, SL quá đỉnh 5 + 0,1 ATR, TP 0,5 thoái lui, RR ≥ 1, tối đa 100 nến | H1–H4 | M15 H1 H4 D1 |
| a9lBrLZx | CRT | Nến 4H UTC trước (loại doji thân<10 %, marubozu thân>90 %, lệch râu>4×); quét dưới + đóng lại trong trên nến tăng (cùng nến/nến sau); dốc linreg50 cùng hướng; SL cực trị quét; TP 2R. H4→nến D1, D1→W1 | M5 | M5 M15 H1 H4 D1 |
| hDvlx4ut | FVG_BOS | Swing 5; BOS/CHoCH; FVG cùng hướng sau sự kiện, cỡ 0,6–1,25 ATR (đổi 5–10 tick ES M1 sang ATR); hồi ≥ 50 %; đóng trên đỉnh FVG và mức cấu trúc; SL nến giữa; TP 3R; BE ở 50 % tới TP; phiên 8:45–10:45 Chicago (≤ H1) | M1 (dùng M5) | M5 M15 H1 H4 D1 |
| VW4M6aCA | NAS100_LOWVOL | Cần nến volume thấp nhất thật → **CHƯA ĐO ĐƯỢC** (không có volume thật; không giả lập bằng tick) | M3 | — |
| CDhXq8DM | ORB_SMART | OR 15 phút đầu phiên (FX/vàng: London 08:00); độ rộng ≤ 0,5 %; vào đến +5h15; SL rộng hơn của biên đối diện / 1,5 ATR; trail 3/2/1 ATR theo R, swing 5 nến (lấy cái sát hơn); nến ngược > 1 ATR → thoát; đóng hết +6h; 1 lệnh/chiều/ngày | M5 | M5 M15 |
| sf4Hf10r | GOLD_8PM | Nến 5 phút 20:00 NY; lần đóng vượt 1 ghi mức BO (đỉnh/đáy nến đó); lần đóng vượt BO → vào; SL biên đối diện; TP 2,25R; hết hạn 21:35; CN–T4 | M5 | M5 |
| N6ZDwigU | TLO_BOX | Hộp giờ mở Tokyo (09:00–10:00 JST); phá vỡ đầu tiên; retest ±0,12 ATR trong 80 nến; đóng xác nhận ngoài hộp; SL 2 chiều cao hộp; TP 1 chiều cao; BE +1R. Chỉ số: CHƯA ĐO ĐƯỢC (chỉ có H1 Yahoo, không khớp giờ) | — | M5 M15 H1 |

Dữ liệu: FX 7 cặp + XAUUSD M5 2024–2026 (BID; spread thật theo giờ cho FX, cố định 2 bps cho vàng), gộp M15/H1/H4; D1: Yahoo EURUSD, USDJPY, AUDUSD,
GBPUSD, S&P 500, vàng; US500/UK100 H1/H4 Yahoo. Khung không định nghĩa được cho script → ghi CHƯA ĐO ĐƯỢC.

Chi phí/phép thử như vòng 22: trước phí (spread 0, trượt 0, không swap) và sau phí (spread XM ×1 + trượt 0,5 pip mỗi chiều + swap), độ nhạy ×1,5 + trượt 1 pip;
vào ở open nến kế tiếp; SL trước khi cùng nến; chia đôi theo thời gian; vàng/chỉ số trừ drift nửa phát hiện. Holm cộng dồn từ 11.270.
SỐNG: Holm < 0,05, lãi cả hai nửa sau phí, lãi nửa kiểm ở ×1,5 + trượt 1 pip, maxDD < 80 %.

## Ghép chéo (cố định trước)
- Tín hiệu (6): HTF_LEVEL, TRENDBREAKER, EMA_FIB, CRT, FVG_BOS, ELLIOTT.
- Bộ lọc trạng thái (5): hướng Supertrend(10,4) [PAXG]; hướng điểm CONFLUENCE (điểm chiều đó ≥ 50); điểm TREND_ENGINE cùng dấu ≥ 3; hướng Range filter [APEX]; chế độ xu hướng PULLBACK (EMA20/50 + dốc).
- Quản lý lệnh (2): gốc của script; chandelier 22 nến × 3 ATR (bỏ TP).
- 6 × 5 × 2 = 60 tổ hợp × 8 chuỗi (7 FX + vàng) × 2 khung (M15, H1) = 960 ô.
