# HÀNG CHỜ MÁY NHÀ (việc box không làm được).
> 🔺 **17/10/2026: ưu tiên #37–#40 (đo phí + chạy lại trên TÀI KHOẢN CỦA ANH) trước mọi việc khác**, xem cuối tệp và `BO_TIEU_CHI_MOI.md`.
 Cập nhật 14/10/2026 02h41 (giờ VN) — vòng lặp box chu kỳ 6 (hang_cho_may_nha).

> ⏸ **CA MÁY NHÀ 7h37 ĐANG TẠM DỪNG** (13/10/2026, chủ dự án báo máy nhà không chạy sáng 14/10). KHÔNG giả định máy nhà chạy;
> hàng dưới đây để sẵn cho lúc chủ dự án bảo **resume**. Khi resume: làm mục **MỚI/CHỜ** theo thứ tự ở phần "Hàng cho lần resume" (#27→), rồi mới tới `chay_lien_tuc.py`.
> Tóm tắt trạng thái bảng cũ #1–#26: XONG 14 · MỘT PHẦN 5 · BỊ CHẶN 3 · CHỜ/CHỜ CHỦ DỰ ÁN 4. Hàng resume #27–#36: **MỚI 8** (#27–#30, #32–#34) · CHỜ 1 (#31 stress ×1,5) · BỊ CHẶN/BỎ QUA 1 (#35) · lặp mỗi ca 1 (#36). Seeker S11–S13: CHỜ 1 · MỘT PHẦN 1 · XONG 1.

**Luật**: dữ liệu tester MT5 đặt ở ổ **D:** hoặc RAM disk, KHÔNG BAO GIỜ ổ C:; xoá sau khi chạy xong (Bases/history + tester cache).

## CA MÁY NHÀ KHÔNG BAO GIỜ DỪNG KHI HẾT HÀNG (13/10/2026 tối, chủ dự án) — áp cho ca 7h37 hằng ngày và mọi ca tối
1. Làm các việc CHỜ trong bảng theo thứ tự.
2. Hết việc trong bảng → `python mt5tools/chay_lien_tuc.py --den <giờ hết ca − 35 phút>` (vd ca 7h37–15h: `--den 14:25`). Script tự sinh việc (`mt5tools/sinh_viec.py`: lưới tham số, mã mới, khung H1/H4/D1, near-miss, IS→OOS), tự chọn số MT5 theo mức (`dieu_phoi_song_song.py`: MAX=4 khi không chơi game, THẤP=0 khi có game/toàn màn hình), ưu tiên Idle, slot ở D:/E:.
3. Song song: box chạy `phan_tich_luoi_box.py` (Python) — xem VONG_LAP.md.
4. Hết giờ: copy `reports/mt5_lien_tuc/so_cai.jsonl` + `sinh_viec.py tong-ket` về repo, xoá `p*\Tester`, `p*\bases\*\history|ticks`, `D:\mt5_lien_tuc\rep`, đóng MT5, KHÔNG tắt máy.
Không đăng nhập mạng xã hội, không mua gì, không vượt Cloudflare bằng công cụ lách.

| # | Việc | Trạng thái |
|---|---|---|
| 1 | MT5 backtest EA MRZ mới (`ea_demo/BRAIN_V24_MRZ_Trail_D1.mq5` (+ `.set`, `InpGioVao=2`; kèm `BRAIN_V24_Chung.mqh`) — không dùng `ea_MeanRevZ5.mq5` (hệ z5 US100 khác)) trên **GBPUSD#** và **AUDUSD#** 2016-01-01 → 2026-10, D1, "Every tick based on real ticks", tài khoản XM thật (Standard/Cash Ultra Low) | XONG 13/10 tối (reports/mt5_v27) |
| 2 | Cùng EA trên **GBPUSD** 2004–2015 (lịch sử dài; ghi chất lượng mô hình %) | XONG 13/10 tối (0% real ticks) |
| 3 | So `InpGioVao=0` vs `2` cùng giai đoạn (đo chênh phí thật theo giờ) | XONG 13/10 tối (GBPUSD hợp lệ; AUDUSD g2 bắt đầu 2018 → nghi vấn) |
| 4 | Nguồn bị chặn trên box: TradingView scripts/ideas, fxblue, quantpedia (234 mục vòng 26) — đọc bằng trình duyệt thường ở máy nhà, chỉ lưu tóm tắt + URL | MỘT PHẦN (403 nhiều, xem SEEKER_MAY_NHA_v27.md) |
| 5 | Báo cáo trả về: `reports/mt5_v27/*.htm` + CSV lệnh; box sẽ so với mô phỏng Python | XONG 13/10 tối |
Sau khi xong: xoá dữ liệu tester ở D:/RAM disk.

## Ca máy nhà 7h30–15h (7h30 phút) — thêm 13/10/2026 (vòng 27). Thứ tự = ưu tiên
**Luật tester**: thư mục dữ liệu/Agents/Bases của MT5 trỏ sang **D:** hoặc RAM disk (vd. `R:\mt5_tester`), KHÔNG ổ C:; cuối mỗi việc xoá `Tester\Agent-*\` + `bases\...\history` tải về; ghi lại dung lượng đã xoá.
Nguồn bị chặn: chỉ đọc bằng trình duyệt thường như người dùng, không công cụ lách Cloudflare, không đăng nhập mạng xã hội; lưu tóm tắt luật + URL vào `reports/seeker_may_nha/`.

| # | Giờ | Việc | Ước tính | Trạng thái |
|---|---|---|---|---|
| 6 | 7:30 | Chuẩn bị: tạo RAM disk/`D:\mt5_tester`, trỏ tester, kiểm tài khoản XM thật, `git pull` | 15′ | XONG 13/10 tối (D:/E:, chưa RAM disk) |
| 7 | 7:45 | Việc 1+3 ở trên: MRZ `ea_demo/BRAIN_V24_MRZ_Trail_D1` `InpGioVao=2` vs `0`, GBPUSD#/AUDUSD#, 2016→2026-10, real ticks (4 lần chạy) | 60′ | XONG 13/10 tối |
| 8 | 8:45 | MRZ cấu hình đăng ký trên NZDUSD#, AUDCAD#, EURGBP#, USDCAD# (đa cặp, việc VONG_LAP 1) | 50′ | XONG 13/10 tối |
| 9 | 9:35 | MRZ thoát trailing ATR×1,5 / ×2,5 / thời gian 5 nến trên AUDUSD#, GBPUSD# (6 lần, việc VONG_LAP 3) | 45′ | XONG 13/10 tối (input InpTrATR/InpGiuToiDa) |
| 10 | 10:20 | Stress: spread cố định ×1,5 (custom symbol hoặc "Random delay") trên cấu hình tốt nhất từ #7 | 25′ | CHƯA (cần custom symbol) → gộp vào #31 |
| 11 | 10:45 | Xuất spread thật theo giờ (tick history) 12 cặp FX + XAUUSD, US500, GER40 → CSV `reports/mt5_v27/spread_gio/` | 30′ | XONG 13/10 tối (6 tháng tick) |
| 12 | 11:15 | Xuất giá D1/H1 XM cho US500, GER40, XAUUSD 2010→ (đối chiếu Yahoo, việc VONG_LAP 9/22) | 20′ | XONG 13/10 tối |
| 13 | 11:35 | Xoá dữ liệu tester + cache (D:/RAM), ghi dung lượng | 10′ | XONG 13/10 tối |
| 14 | 11:45 | Đọc TradingView Scripts (bộ lọc Strategies, mean reversion/breakout, FX) — 20 mục mới: tóm tắt luật + URL | 45′ | MỘT PHẦN (danh sách 12 URL, chi tiết bị CloudFront chặn) |
| 15 | 12:30 | TradingView Ideas FX D1 — 10 ý có luật rõ | 20′ | BỊ CHẶN 403 |
| 16 | 12:50 | Forex Factory (forum EA threads + Trade Explorer công khai) — 10 luồng hệ có kết quả dài | 30′ | MỘT PHẦN (4 luồng) |
| 17 | 13:20 | fxblue (trang thống kê công khai) — 10 tài khoản ≥ 2 năm, ghi phong cách/DD/giữ lệnh | 20′ | BỊ CHẶN 404 (URL đổi) |
| 18 | 13:40 | quantpedia (mục miễn phí) + quantifiedstrategies — chiến lược FX/chỉ số mùa vụ | 25′ | MỘT PHẦN (13 trang miễn phí) |
| 19 | 14:05 | SSRN (box 403): tìm "FX anomaly", "turn of the month index", "currency carry momentum" — 10 bài, tóm tắt + URL | 20′ | BỊ CHẶN 403 |
| 20 | 14:25 | babypips forum, arabictrader, forex_nawigator, gestaltu, quant.stackexchange, tutim_fxmacrodata/quantforhire (đều 403/captcha trên box) — mỗi nguồn 3 mục | 25′ | MỘT PHẦN (gestaltu+fxmacrodata ok; còn lại 403) |
| 21 | 14:50 | Đẩy báo cáo `reports/mt5_v27/*.htm` + CSV + tóm tắt nguồn, kiểm ổ C: không phình, xoá tester lần cuối | 10′ | XONG 13/10 tối |
Tổng ≈ 7h30′. Nguồn cần đăng nhập (myfxbook, darwinex, collective2, zulutrade, ctrader, các API key) KHÔNG nằm trong ca — chỉ làm nếu chủ dự án tự đăng nhập.

## Thêm 13/10 tối (vòng 27)
| # | Việc | Trạng thái |
|---|---|---|
| 22 | Chủ dự án mở/đăng nhập lại hồ sơ Chrome AI (.browser_thebrain, CDP 9224, thebrainago) trên máy nhà — cần cho Seeker đọc nguồn đăng nhập + follow (đã cho phép follow, chỉ follow) | XONG 13/10 tối (hồ sơ mới `D:\browser_thebrain`, đăng nhập tay; xem mục SEEKER dưới) |
| 23 | Quét lại nguồn đã follow mỗi ca máy nhà (1 lần/ngày), ghi mục mới vào đây | CHỜ (chưa follow tài khoản nào; gộp với S11) |
| 24 | Soi vì sao InpGioVao=2 trên AUDUSD#/NZDUSD#/AUDCAD# không vào lệnh trước 2018-04-24 (log tester) rồi chạy lại so g0/g2 | XONG 13/10 (XM AUD/NZD# không có M1 trước 2018-05; so lại 2018-05→: reports/mt5_v27/README.md) |
| 25 | Stress spread ×1,5 bằng custom symbol (việc #10) | CHỜ → gộp vào #31 |
| 26 | RAM disk (ImDisk/AIM) — cần chủ dự án đồng ý cài phần mềm ngoài Python | CHỜ CHỦ DỰ ÁN |

## SEEKER Chrome máy nhà CDP 9224 (13/10/2026 tối) — quét lại HẰNG NGÀY (mã S để khỏi trùng số bảng trên)
Chrome AI: `D:\browser_thebrain`, `--remote-debugging-port=9224`, hiện cửa sổ (đăng nhập tay, Google thebrainago). Không lưu mật khẩu/cookie vào repo.
Đã đăng nhập: Forex Factory, FX Blue, Collective2, Darwinex, ZuluTrade, X, Facebook, Myfxbook, Babypips (trang chính; forum SSO lỗi). Chưa: SSRN (miền email không hợp lệ), TikTok (cần ngày sinh), cTrader/QuantPedia (BỎ QUA), TradingView/MQL5 (để sau, cần mạng khác — không dùng WARP).
Follow: CHƯA follow tài khoản nào. Chỉ đọc: không đăng/like/nhắn tin/tham gia nhóm.

| # | Việc hằng ngày | Lệnh | Trạng thái |
|---|---|---|---|
| S11 | Quét lại nguồn theo dõi (`config/nguon_theo_doi.json`, chu_ky_gio=24: FF Trading Systems, Myfxbook Systems, C2 grid, Darwinex, ZuluTrade, FX Blue, Babypips, tìm X/Facebook "forex backtest strategy") | `python seeker_kham_pha_sau.py --quet-lai --ghi` (Chrome 9224 phải mở) | CHỜ (ca tạm dừng; chưa chạy lần nào sau 13/10) |
| S12 | Khám phá sâu từ nguồn mới (độ sâu 2, ngân sách 25–60 trang, 600–900 s) → ứng viên vào `config/nguon_seeker.json` (tu_sinh, THU) + `data/nguon_seeker/HANG_DOI_KHAM_PHA.json` | `python seeker_kham_pha_sau.py --hat <url...> --ghi` | MỘT PHẦN (13/10: 25 trang, 827 ứng viên, 50 nguồn thêm) |
| S13 | Tóm tắt luật + URL → `reports/seeker_may_nha/` (không mã bên thứ ba) | thủ công / box | 13/10: SEEKER_MAY_NHA_9224_20261013.md (FF 8 luồng) |

## HÀNG CHO LẦN RESUME (thêm 14/10/2026 02h41, chu kỳ 6) — thứ tự = ưu tiên
**Nguồn số liệu**: `python mt5tools/sinh_viec.py tong-ket` trên `reports/mt5_lien_tuc/so_cai.jsonl` (máy nhà đẩy 5fcec69a, 630 lần thử MT5 13/10 19:24–23:21 giờ VN, tất cả D1).
Đây là **BACKTEST MT5 (tester XM demo)**, không phải tiền thật; IS 2016–2022 phần lớn "0% real ticks" (tick sinh từ M1), OOS 2023–2026-10 "73% real ticks".

**Tổng kết sổ cái (đo trên box 14/10 02h40)**: 630 lần thử = 379 IS + 251 OOS (MRZ 331, RSI 299); 252 lần đạt ngưỡng IS (PF ≥ 1,25, ≥ 30 lệnh, net > 0);
**242 ứng viên đạt cả IS và OOS** (223 kết quả khác nhau — nhiều biến thể `InpTrATR` cho kết quả trùng); **Holm: 0/379** (p IS nhỏ nhất 0,0158; cần ≤ 0,05/379 ≈ 1,3·10⁻⁴; 24 lần p < 0,05).
Toàn bộ DD equity < 5 % và net sau spread/swap XM tester > 0 → cổng lãi + DD đạt, nhưng **CHƯA QUA** vì Holm cộng dồn (sổ MT5 379 + box 13.000) → **0 hệ qua cổng**.
So khớp MT5 ↔ Python box (`box_luoi_python_chi_tiet.jsonl.gz`, cùng khoá): 589/630 khớp khoá, **553/589 (93,9 %) cùng dấu net**, tương quan PF 0,84 (trung vị PF MT5 1,69 / Python 1,65) → mô phỏng box dùng được để lọc trước.

Ứng viên tốt nhất mỗi (EA, mã) (IS → OOS, net USD lot 0,01 / lệnh / PF; chọn theo PF OOS có phạt n < 30):
| EA | Mã | Số ứng viên | Tham số (GioVao, GiuToiDa, SL, TR, …) | IS | OOS |
|---|---|---|---|---|---|
| MRZ | GER40Cash# | 27 | g0, giữ 20, z2,0 N50, SL1,5, TR2,0 | +647 / 60 / 1,50 | +607 / 39 / 1,71 |
| MRZ | GBPJPY# | 6 | g2, giữ 72, z1,5 N20, SL2,0, TR3,0 | +468 / 71 / 1,54 | +374 / 32 / 2,52 |
| MRZ | EURGBP# | 6 | g2, giữ 5, z1,5 N50, SL2,0, TR2,5 | +349 / 149 / 1,61 | +143 / 77 / 1,99 |
| MRZ | AUDUSD# | 27 | g2, giữ 72, z1,5 N50, SL2,0, TR3,0 | +135 / 45 / 1,42 | +261 / 23 / 5,26 |
| MRZ | GBPUSD# | 36 | g2, giữ 20, z2,5 N20, SL1,5, TR1,5 | +127 / 39 / 1,42 | +158 / 18 / 4,36 |
| MRZ | EURJPY# | 1 | g2, giữ 20, z2,0 N50, SL1,5, TR2,0 | +351 / 81 / 1,77 | +100 / 43 / 1,39 |
| RSI | GBPUSD# | 75 | g2, giữ 72, RSI 25/70, SL1,0, TR2,0 | +99 / 46 / 1,32 | +260 / 18 / 5,66 |
| RSI | EURJPY# | 39 | g2, giữ 72, RSI 30/75, SL2,0, TR1,5 | +220 / 34 / 2,08 | +143 / 15 / 4,71 |
| RSI | GER40Cash# | 7 | g2, giữ 20, RSI 30/75, SL1,5, TR2,0 | +245 / 34 / 1,32 | +375 / 21 / 1,76 |
| RSI | GBPJPY# / AUDUSD# / EURGBP# / EURUSD# | 1–4 | xem tong-ket | PF 1,3–1,8 | PF 1,5–2,6 (n 15–21) |
Âm/không đạt: RSI US500Cash# (24 lần, PF 0,78–1,13), MRZ US500Cash# (PF 0,45–0,69). OOS trượt sau khi đạt IS: 9 (MRZ GBPUSD# 6, AUDCAD# 2, EURGBP# 1) — **chỉ ghi, không chỉnh tham số theo OOS**.

| # | Việc (máy nhà, MT5 ở D:/E:, không C:) | Ước tính | Trạng thái |
|---|---|---|---|
| 27 | **Mẫu ngoài thứ hai 2004–2015** (chỉ mã có M1 đủ: GBPUSD#, EURGBP#, GBPJPY#, EURJPY#; GER40Cash# kiểm lịch sử trước) cho cấu hình tốt nhất mỗi (EA, mã) ở bảng trên — tham số CỐ ĐỊNH, 1 lần/cấu hình, ghi chất lượng mô hình % | 60′ | MỚI |
| 28 | **Đa mã cùng tham số cố định**: MRZ GER40 cấu hình trên → US30Cash#, FRA40Cash#, EU50Cash#, UK100Cash#; RSI GBPUSD cấu hình trên → EURUSD#, AUDUSD#, USDCAD#, NZDUSD# (không tối ưu lại) | 45′ | MỚI |
| 29 | MRZ AUDCAD# — 1 cấu hình đạt IS **chưa có OOS** trong sổ cái → chạy OOS 2023→2026-10 | 5′ | MỚI |
| 30 | Soi EA: 17 nhóm biến thể chỉ khác `InpTrATR` cho **net trùng hệt** (vd. MRZ GER40 IS TR2,0/2,5/3,0 đều +647,03) → trailing không kích hoạt hay bị `InpGiuToiDa` cắt trước? Đọc log tester 1 lần; 1 lần thử RSI AUDUSD# g0 IS ra 0 lệnh, chất lượng "0%" (lt_RSI_AUDUSD_D1_IS_48168086) → kiểm lỗi | 20′ | MỚI |
| 31 | **Stress spread ×1,5 bằng custom symbol** (gộp #10/#25): tạo custom symbol từ tick XM (GBPUSD#, AUDUSD#, GER40Cash#) với spread ×1,5, chạy lại top 3 ứng viên #27 + MRZ AUDUSD TR2 v27 | 45′ | CHỜ (từ 13/10) |
| 32 | **IBS<0,2 US500Cash#/US100Cash# (vòng 29, VONG_LAP 30)** — mô phỏng Yahoo qua Holm 13.000 (p_holm 0,003 / 0,0015). Cần EA mới: vào gần close 23h server, thoát khi close > high hôm trước (≤ 10 ngày); `BRAIN_IBS_Demo.mq5` hiện là luật vòng 13 (giữ 1 ngày) → cần thêm input thoát rồi biên dịch MetaEditor ở máy nhà; spread ×1,5 qua #31 | 60′ | MỚI (box viết EA trước khi resume nếu kịp) |
| 33 | **Ô vòng 28 cần MT5** (mô phỏng, 0 qua Holm): MRZ AUDUSD lọc ADX14<20/ATR% thấp (60,4 bps kiểm sau phí), MRZ AUDUSD TR2,5 (131 bps, p 0,0004), MRZ POOL4/FX7 lọc W1 EMA20 — EA `BRAIN_V24_MRZ_Trail_D1` cần thêm input lọc chế độ + W1 (box viết, máy nhà biên dịch) | 40′ | MỚI |
| 34 | **Nguồn bị chặn — đọc bằng trình duyệt thường, không công cụ lách**: fxblue (URL `/users` 404 → tìm URL thống kê công khai mới từ trang chủ khi đã đăng nhập), Forex Factory (còn 6 luồng của #16), babypips forum (SSO lỗi → thử lại 1 lần), gestaltu/fxmacrodata (đọc tiếp) | 40′ | MỚI/MỘT PHẦN |
| 35 | **Nguồn chặn cả máy nhà — KHÔNG làm tới khi có mạng khác hợp lệ (không WARP)**: TradingView scripts/ideas + Pine Gold Breakout 15M @WillyAlgoTrader (VONG_LAP 34), MQL5, SSRN (403 + email không hợp lệ), quant.stackexchange, arabictrader. **BỎ QUA**: QuantPedia (đặt lại mật khẩu lỗi), cTrader (cần SĐT). X đọc được từ box (công cụ x) → không cần máy nhà | — | BỊ CHẶN / BỎ QUA |
| 36 | Cuối ca: đẩy sổ cái + `sinh_viec.py tong-ket`, xoá `p*\Tester`, `bases\*\history|ticks`, ghi dung lượng đã xoá; kiểm C: không phình | 10′ | MỖI CA |
Hết bảng → `chay_lien_tuc.py --den <giờ hết ca − 35′>` như luật đầu tệp (sinh_viec ưu tiên near-miss/hàng xóm của ứng viên trên).
Vướng cần chủ dự án: (1) bảo **resume** ca 7h37; (2) RAM disk (#26, cài ImDisk/AIM — cần đồng ý); (3) follow tài khoản nguồn (#23, chỉ follow); (4) mạng khác hợp lệ cho TradingView/MQL5 (#35) nếu muốn.

## PHÍ + CHẠY LẠI TRÊN TÀI KHOẢN CỦA ANH (thêm 17/10/2026, Claude). Ưu tiên CAO NHẤT, thứ tự = ưu tiên
Lí do: mọi số phí đã đo đều là XM **Ultra Low `#`** (swap FX tắt), **không phải hai tài khoản anh đánh** (Exness cent, XM micro). Tiêu chí mới (`BO_TIEU_CHI_MOI.md`) chỉ hỏi "lãi ròng sau phí THẬT > 0", nên phí phải là phí sàn của anh.
Chuẩn bị: mỗi sàn **một terminal MT5 portable riêng** ở D:/E: (vd `D:\mt5_tester\exness_cent`, `D:\mt5_tester\xm_micro`), **anh tự đăng nhập** tài khoản của mình. Claude/Grok không cần và không lưu mật khẩu. Không dùng slot p1–p4 (đang đăng nhập XM Ultra Low).

| # | Việc | Lệnh | Ước tính | Trạng thái |
|---|---|---|---|---|
| 37 | **Đo phí** từng tài khoản: spread theo giờ (tick 14 ngày), giãn đổi ngày, spread đầu tuần, gap cuối tuần, swap ra tiền/đêm ở lot nhỏ nhất, margin + margin hedge, stop-out, hedging/netting, tiền của TP 5 giá. Kèm **lịch sử lệnh thật 365 ngày** (hoa hồng thật, giờ giữ, số lần nhồi, đóng bằng TP hay bằng tay) | `may_nha\DO_PHI_SAN.cmd "D:\mt5_tester\exness_cent\terminal64.exe"`, rồi chạy lại với `xm_micro` | 10′/sàn | MỚI |
| 38 | Xem trước danh sách việc: 28 cấu hình (MRZ/RSI D1 đã lãi cả IS và OOS trên sổ cái 13/10, mỗi cặp EA × mã tối đa 2) gán sang tên mã của sàn | `python mt5tools/chay_lai_tren_san.py danh-sach --ma-san reports/phi_san/<server>/ma_san.json` | 1′ | MỚI |
| 39 | **Chạy lại trên tài khoản của anh** (2016 → 10/2026, Model=4 tick thật, tham số CỐ ĐỊNH, không tối ưu). Script tự chép + biên dịch EA nếu slot có `metaeditor64.exe`. Cent: `--tien USC --von 10000` (tester không nhận USC thì dùng `--tien USD --von 100`; đòn bẩy tự lấy từ `tai_khoan.json`) | `python mt5tools/chay_lai_tren_san.py chay --slot D:\mt5_tester\exness_cent --ma-san reports/phi_san/<server>/ma_san.json --tien USC --von 10000` | ~2–3 giờ/sàn | MỚI |
| 40 | Tổng kết + ghép: lãi/năm từng mảnh trên phí sàn anh, spread chịu thêm được mỗi lệnh, mảnh nào làm bộ ghép tốt hơn, đạt hay không 3 yếu tố cốt lõi (lãi ≥ 10 %/năm ở sụt giảm ≤ 80 %). Đẩy `reports/phi_san/` và `reports/mt5_san_chu/` lên git | `python mt5tools/chay_lai_tren_san.py tong-ket --ma-san ... --von 10000 --dd-muc-tieu 80` | 1′ | MỚI |
Sau #37–#40: chạy `chay_lien_tuc.py` như cũ. `sinh_viec.py` (ngưỡng hạ 17/10) đã xếp sẵn **92 cấu hình mới được chạy OOS** (MRZ AUDCAD 42, GBPUSD 20, AUDUSD 13, RSI US500 9, …), tự lấy trước.
`lenh_cua_anh.csv` là lịch sử giao dịch của anh: **anh quyết định có đẩy lên git hay không**. `lich_su_tom_tat.csv` chỉ có số tổng.

## XỬ LÍ LỆNH TRÊN MT5 (thêm 17/10/2026 tối, Claude) — làm ngay sau #37
Chủ dự án: *"phí giao dịch, tính điểm giá chạy, spread, các cách entry, DCA xử lí lệnh khi sai, trailing vị thế có lợi, hedging cân bằng lệnh"*. EA mới `ea_demo/BRAIN_XuLiLenh.mq5`: MỘT bộ máy rổ lệnh. MT5 tự tính điểm, spread, swap, hoa hồng theo sàn đang kết nối, không còn Python đoán point.

| # | Việc | Lệnh | Ước tính | Trạng thái |
|---|---|---|---|---|
| 41 | Biên dịch EA trong MetaEditor của slot (script tự chép vào `MQL5\Experts\BRAIN\` và gọi `metaeditor64.exe /compile` nếu có). **Báo lỗi biên dịch nếu có**: EA viết trên cloud, chưa biên dịch lần nào | (tự động ở #42) | 5′ | MỚI |
| 42 | Chạy 27 kịch bản. MRZ D1 GBPUSD/AUDUSD/EURGBP × 5 cách xử lí (chỉ TP+trailing · DCA 5 tầng lot đều · DCA lot tăng · DCA + hedge/gỡ · nhồi thuận). XAUUSD/US500/GER40 H1 không tín hiệu × 4 cách. Chạy trên tài khoản của anh (sau #37) **và** trên slot XM Ultra Low để so | `python mt5tools/chay_xu_li_lenh.py chay --slot <slot> --ma-san reports/phi_san/<server>/ma_san.json --tien USC` (MRZ D1 trước: `--chi _D1_`) | D1 ~2′/lần · H1 ~15–30′/lần | MỚI |
| 43 | Tổng kết: bảng lãi/năm, sụt giảm vốn (gồm lỗ thả nổi), lãi ở DD 80 %, đạt 3 yếu tố. Đẩy `reports/xu_li_lenh/` lên git | `python mt5tools/chay_xu_li_lenh.py tong-ket --ma-san ...` | 1′ | MỚI |

