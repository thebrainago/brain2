# BÀN GIAO QUY TRÌNH BÁO CÁO XAUUSD (cập nhật 19/11/2026)

Tài liệu cho bot/phiên mới tiếp quản báo cáo scalp intraday XAUUSD CFD cho anh Việt Anh (nagi).
Trả lời tiếng Việt có dấu, gọn, gọi "anh". Chi tiết hạ tầng máy nhà xem `HANDOFF_XAU-System.md` cùng thư mục.

## 1. Lệnh kích hoạt
- Anh gõ **"1"** = làm báo cáo vùng canh ngay.
- Máy nhà BẬT: đọc `C:\GrokWork\engine\engine_state.json` + `C:\GrokWork\fxa_levels.json` (GEX tự tính, ưu tiên 0DTE). OTL chỉ để đối chiếu.
- Máy nhà TẮT: vẫn báo cáo, dùng OTL Telegram + giá CFD/GC lấy trực tiếp (ghi rõ "không có data máy nhà").
- Sau mỗi báo cáo "1" (khi máy nhà bật): ghi vùng vào `C:\GrokWork\zones.json` (task XAU-ZoneWatch đọc, báo Telegram khi chạm vùng, chỉ để xem chart, không phải lệnh).

## 2. Format báo cáo (giữ nguyên thứ tự)
1. Giá CFD XAUUSD hiện tại + giá GC (hợp đồng front, ghi mã, ví dụ GCZ6).
2. Basis GC − CFD (tính LẠI mỗi lần, xem mục 4).
3. Put Wall / Call Wall, Max Pain, Gamma Flip + Bias, GEX Regime (dương = biên độ hẹp, mean-revert; âm = dễ chạy).
4. Big Trades đáng chú ý (đã lọc, mục 5).
5. Vùng canh: 🔴/🟥 BÁN, 🟩 MUA, kèm SL / TP1 / TP2, quy đổi sang giá CFD.
6. 👉 Khuyến nghị: ưu tiên ít lệnh, xác suất cao, chỉ vào khi có TƯỜNG + XÁC NHẬN order flow.

## 3. Nguồn dữ liệu
| Dữ liệu | Nguồn chính | Dự phòng |
|---|---|---|
| Giá CFD XAUUSD | TradingView XAUUSD / Investing.com XAU/USD | trường CFD trong bảng OTL |
| Giá GC futures | Sierra Chart/Rithmic (FXAURUM gateway) máy nhà | Investing.com Gold Futures (kiểm tra timestamp!) |
| GEX: MP, Call/Put Wall, Gamma Flip | `fxa_levels.json` (task XAU-FxaLevels, ~10 phút/lần, GC/ES/NQ) | OTL Telegram |
| Order flow, tín hiệu set C | `engine_state.json`, `engine_signals.csv` (xau_engine.py) | không có |
| Big trades options vàng | OTL Telegram "OTL _ Data Alert Public" (t.me/AI_otl_Alert), topic "Gold _ Alert Bigtrade & Data" | không có |
| Snapshot OTL | topic "Gold_Snapshot" (ảnh 30 phút/lần, không đọc máy được) | |

OTL đọc qua Telegram Web trên máy bot (đã đăng nhập sẵn), CHỈ ĐỌC. Bảng OTL theo từng kỳ hạn: MP, POC, CBE (call break-even), PBE (put break-even), Sup, Res, $ call/put. Luôn ghi giờ bài OTL; quá vài giờ thì đánh dấu "chỉ tham khảo".

## 4. Cách tính toán
- **Basis = GC − CFD**, lấy hai giá CÙNG THỜI ĐIỂM, nguồn CFD thật. KHÔNG dùng giá trị mặc định (`cfd_basis_default` = 2 trong engine_config.json đã cũ).
  - Lưu ý: so với GC front (Z6), không so với ATM của kỳ hạn xa (OGF7) — lỗi 18/11 ra basis 31.6 là do so nhầm kỳ hạn.
- Giá CFD của vùng = giá GC − basis.
- Kỳ hạn GEX: ưu tiên 0DTE (Wxx/Rxx tuần), rồi weekly OG3, rồi monthly OGZ6 chỉ làm nền.
- Vùng canh: dựng quanh tường GEX/PBE/CBE/Sup/Res gần giá + cấu trúc cơ bản (IB, VWAP phiên, đỉnh/đáy ngày trước). SL ngoài tường 5–7 giá; TP1 về MP/POC/VWAP gần, TP2 tường đối diện.
- GEX Regime: giá trên Gamma Flip = dương (fade biên), dưới = âm (theo breakout).

## 5. Lọc big trade (đề xuất, chưa áp dụng live)
Chỉ coi là tín hiệu khi: có phía chủ động (mua/bán rõ), strike trong ~1–2% quanh ATM, DTE ≤ 1 tuần, size lớn so với OI, và nằm gần tường GEX / vùng của ta. Lệnh xa kỳ hạn, deep ITM, spread/cross = nhiễu/hedge, bỏ qua. Theo các nghiên cứu, print lớn đơn lẻ trên vàng KHÔNG có bằng chứng dự báo GC.

## 6. Kết quả backtest đang dùng (đừng làm lại)
- Edge duy nhất robust: **set C London GC** (14:00–20:00 UTC+7, c_ib_break_min 60, bắt buộc stacked imbalance): ~53 lệnh, ≈ +0.40R sau phí.
- Set C phiên Á: âm (−0.37R) → đã tắt.
- Nới IB break, retest mức bật, trailing: âm/không robust. 10 ý tưởng Brain Seeker: không có gì trade được. CME FX (6E/6J/6B/6A/6C): không có edge.
- Chỉ báo/TA thuần: không có edge trong backtest của ta. Tường GEX/Max Pain: vùng phản ứng CHƯA kiểm chứng → backtest khi `fxa_levels.json` đủ 3–4 tuần.
- Bộ thử nghiệm Telegram (đã duyệt, gắn nhãn thử nghiệm): Asia E 06:00–13:59 có lọc slope VWAP 60 phút; London pullback về VWAP sau phá IB/đỉnh đáy ngày trước (14:00–20:00).

## 7. Luật bắt buộc
- KHÔNG tự đổi vùng live, alert, luật. Anh nêu ý tưởng → trả lời bằng lý lẽ + dữ liệu, chờ anh quyết. Mọi thay đổi phải có lý thuyết + backtest.
- Nghiên cứu, backtest, thêm log-only: được làm không cần hỏi.
- KHÔNG đặt lệnh, KHÔNG copy-trade, FXAURUM chỉ dùng lấy data.
- KHÔNG đụng file license/đăng nhập Rithmic, KHÔNG sửa FXAURUM-Mod.Cht / FXAURUM-Winter-Mod.Cht (backup ở C:\SierraChart_Backup\FXAURUM_2026-11-16, so hash mỗi lần).
- KHÔNG tắt/chỉnh UAC, KHÔNG đổi cài đặt nguồn/sleep. Không lưu data lớn trên C: (dùng E:, giới hạn ~40 GB, MBO thô giữ ~10 phiên).
- Không bao giờ gửi mật khẩu/token qua chat, mail, git. Telegram: anh tự đăng nhập.
- Backup trước khi sửa file live.

## 8. Lịch zones.json
```json
{"updated":"YYYY-MM-DD HH:MM:SS","tz":"UTC+7","price_units":"GC futures","zones":[
 {"id":"BAN1","side":"BÁN","lo":0,"hi":0,"sl":0,"tp1":0,"tp2":0,"note":"","created":"","expires":"YYYY-MM-DD 23:59:00"},
 {"id":"BREAK_LO","side":"BREAK","level":0,"break_dir":"below","sl":0,"tp1":0,"tp2":0,"note":"","created":"","expires":""}]}
```
Watcher: tiền tố "📍 CHẠM VÙNG | chỉ để xem chart, không phải lệnh"; re-arm khi giá rời vùng ≥3 giá và 15 phút; tối đa 3 lần/vùng/ngày.

## 9. Việc tồn (19/11/2026)
- Khi máy nhà bật: làm lại báo cáo "1" với GEX của ta, ghi zones.json. Vùng đề xuất 19/11 (giá GC): BÁN 3775–3779 SL 3785 TP1 3760 TP2 3745; MUA 3735–3740 (chỉ khi có rejection) SL 3729 TP1 3754 TP2 3766; BREAK dưới 3727 mục tiêu 3700 SL 3736.
- Databento: tài khoản đã tạo + xác minh email, kẹt ở bước thẻ (anh chưa có thẻ). Có thẻ thì làm tiếp, không đăng ký lại.
- Đề xuất chờ duyệt: bộ đọc OTL có lọc big trade; nghiên cứu BTC.
- Backtest phản ứng tường GEX sau 3–4 tuần dữ liệu; ES/NQ vòng 2; review các flag log-only sau 4–6 tuần; routine MBO filter study 2/12 10:00; roll CLG7 trước ~10/12.
