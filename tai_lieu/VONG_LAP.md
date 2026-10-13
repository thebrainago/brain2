# VÒNG LẶP NGHIÊN CỨU LIÊN TỤC (thiết kế, bắt đầu vòng 27 — 13/10/2026)
Chạy trên BOX (không phải máy nhà). Mỗi chu kỳ lấy MỘT việc ở đầu hàng, làm xong → đẩy xuống cuối hàng (xoay vòng 5 việc).
Trạng thái máy: `vong_lap_state.json` (con trỏ hàng) + `reports/vong_lap_nhat_ky.json` (nhật ký từng chu kỳ; `vong_lap_log.json` ở gốc là dữ liệu cũ không liên quan, giữ nguyên).

Vận hành máy nhà + box (ổ đĩa, slot MT5, điều phối, lịch ca, trình duyệt, Cloudflare): `tai_lieu/KINH_NGHIEM_VAN_HANH.md`.

## Luật cứng (mọi việc)
- Chỉ số ĐO ĐƯỢC; mô phỏng ghi "mô phỏng"; không đo được ghi "CHƯA ĐO ĐƯỢC".
- QUA = lãi sau phí XM thật (`phi_xm_that.py`, spread đo theo giờ khi có) VÀ maxDD < 80 %, dương cả hai nửa
  (phát hiện/kiểm), tiền đăng ký trước (`reports/vongNN_tien_dang_ky.md`), không nhìn trước (test cắt dữ liệu),
  Holm CỘNG DỒN (mọi ô đã thử, kể cả ô dừng ở tầng 1 với p = 1). Sau vòng 27: xem `reports/vong27.json` → `ho_holm`.
- Lọc theo tầng: (1) cạnh thô TRƯỚC phí, cả hai nửa > 0 → (2) đa tài sản SAU phí XM thật → (3) quản trị/ghép.
- Luôn ghép chéo phong cách (hồi quy × xu hướng × động lượng × giờ vào); thử cả khung nhỏ (M5/H1/H4) và lớn (D1/W1).
- Không bí mật / mã EA bên thứ ba trong git (mã chỉ ở `data/cau_kho/`, git bỏ qua; repo giữ tóm tắt luật + URL).
- Commit/push CHỈ khi test xanh; cập nhật `GHI_CHU_NANG_CAP_GROK.md` mỗi chu kỳ.
- Không vượt Cloudflare/chặn bot, không đăng nhập mạng xã hội, không Telegram, không mua gì.

## KHÔNG BAO GIỜ CẠN VIỆC (13/10/2026 tối, chủ dự án) — áp cho vòng lặp box
Khi hàng việc P1–P3 trống hoặc đang chờ máy nhà: box chạy `python phan_tich_luoi_box.py <thư mục D1 XM> ` (lưới cùng `mt5tools/sinh_viec.py`, IS 2016–2022 / OOS 2023–2026-10, phí spread XM theo giờ) và `python mt5tools/sinh_viec.py tong-ket` trên `reports/mt5_lien_tuc/so_cai.jsonl` (sổ cái MT5 máy nhà) → so khớp MT5 ↔ Python, đẩy near-miss lên đầu. Mọi lần thử đều ghi sổ cái → đếm Holm.

## Hàng 5 việc xoay vòng
1. **Nạp dữ liệu** — thêm tài sản/khung miễn phí tải được (HistData M1 qua thư viện `histdata`, Dukascopy datafeed
   khi không 503, Yahoo D1). Ghi nguồn vào `/workspace/du_lieu_fx/NGUON_DU_LIEU.md`; dữ liệu NGOÀI repo.
2. **Seeker + bộ đọc** — tải mã công khai (mql5 Code Base, GitHub API), sửa lý do hỏng hàng đầu của `nhan/doc_ma.py`
   / `nhan/tien_xu_ly_ea.py`, đo lại tỷ lệ dịch trên toàn bộ EA đã tải (số trước/sau).
3. **Vòng thử** — tiền đăng ký → chạy `vNN.py` → Holm cộng dồn → ghi bảng mô phỏng.
4. **Tốc độ hệ thống + bài học** — đo profile (cProfile), thêm đệm/vector hoá/song song khi rẻ; cập nhật `tai_lieu/KINH_NGHIEM.md`.
5. **Hàng chờ máy nhà** — cập nhật `tai_lieu/HANG_CHO_MAY_NHA.md` (việc chỉ máy nhà làm được: MT5 tester, nguồn bị chặn trên box).

## Một chu kỳ
`git pull` → đọc con trỏ → làm việc → `pytest` các test liên quan → cập nhật GHI_CHU + KINH_NGHIEM (+ `tai_lieu/KINH_NGHIEM_VAN_HANH.md` nếu có bài học vận hành) → commit/push nếu xanh → tăng con trỏ.

## Hàng việc nghiên cứu xếp hạng (thêm 13/10/2026, vòng 27) — lấy theo thứ tự P1 → P3, mỗi chu kỳ ≥ 1 việc
Nhãn: [phong cách | tài sản | khung | quản trị]. Mọi ô phải tiền đăng ký, cộng Holm dồn, ghép chéo ≥ 2 phong cách khi có thể.
Ngân sách Holm: mỗi việc ≤ 12 ô (bài học 10). Kết quả = MÔ PHỎNG cho tới khi MT5 máy nhà xác nhận.

### P1 — near-miss & ghép chéo (giá trị cao nhất)
1. ✅ [đã chạy vòng 28, chu kỳ 4, 0 qua — `reports/vong28.json`] **MRZ AUDUSD 02h — xác nhận ngoài mẫu đa cặp gộp**: chạy đúng cấu hình đăng ký (z50 ±2, TR2) trên pool AUDUSD+NZDUSD+AUDCAD+GBPUSD gộp n, 1 ô duy nhất, không sửa tham số. [hồi quy | FX pool | D1 vào 02h | TR2 cố định] (KN 3,4,10)
2. ✅ [đã chạy vòng 28, chu kỳ 4, 0 qua — `reports/vong28.json`] **MRZ × lọc chế độ ADX/biến động thấp**: chỉ vào khi ADX14 < 20 hoặc ATR% dưới trung vị 1 năm. [hồi quy × chế độ | AUDUSD,GBPUSD | D1 02h | TR2] (KN 4)
3. ✅ [đã chạy vòng 28 phần MRZ, chu kỳ 4, 0 qua — `reports/vong28.json`; RSI trailing chưa chạy] **D1 RSI/MRZ trailing — chuẩn hoá thoát**: so TR2 vs trailing ATR×{1,5;2,5} vs thoát theo thời gian 5 nến; 6 ô. [hồi quy | GBPUSD,AUDUSD | D1 02h | trailing/thời gian]
4. ✅ [đã chạy vòng 28, chu kỳ 4, 0 qua — `reports/vong28.json`] **MRZ × xu hướng W1 (ghép)**: chỉ mua hồi khi W1 trên EMA20 (và ngược lại). [hồi quy × xu hướng | FX pool | D1+W1 | TR2]
5. **M5 hồi quy cạnh thô 0,5–1,6 bps → nâng khung**: cùng tín hiệu tổng hợp lên M30/H1 để cạnh thô > 3× spread (KN 2); chỉ qua tầng 1 mới sang phí. [hồi quy | EURUSD,GBPUSD,USDJPY | M30/H1 | thoát thời gian]
6. **M5 hồi quy chỉ giờ spread rẻ**: giới hạn 08–16h London, bỏ rollover 23–01h; so cạnh thô theo giờ với spread đo theo giờ. [hồi quy × giờ | EURUSD | M5 | SL/TP ATR]
7. ✅ [đã chạy vòng 28, chu kỳ 4, 0 qua — `reports/vong28.json`] **Stress bắt buộc cho mọi near-miss**: spread ×1,5 + trượt 1 bps + swap 2,5 %/năm trên các ô 1–4 (không tính thêm ô Holm, là kiểm áp lực). [mọi | FX | D1 | —] (KN 11)
8. **Động lượng chéo tiền tệ (cross-sectional) × MRZ**: xếp hạng 12 cặp theo lợi suất 3 tháng, chỉ MRZ theo hướng động lượng. [động lượng × hồi quy | 12 cặp FX | D1/W1 | danh mục cân rủi ro]

### P2 — họ phong cách chưa thử
9. **Mùa vụ chỉ số (cuối tháng / trước nghỉ lễ)**: turn-of-month 4 ngày trên US500/GER40 Yahoo D1. [mùa vụ | chỉ số | D1 | giữ cố định N ngày]
10. **Carry × xu hướng**: carry dương + giá trên SMA100; dữ liệu lãi suất FRED. [vĩ mô carry × xu hướng | FX G10 | D1/W1 | danh mục]
11. **Phá vỡ phiên Á → London (ORB)**: biên phiên 00–07h server, vào phá vỡ 08–10h, SL đối biên. [phá vỡ × giờ | GBPUSD,EURUSD,GER40 | M5/H1 | SL biên, TP 1,5R] (nguồn gh_orb_mt5)
12. **Hồi quy cặp/chênh (AUDCAD, EURGBP) z-score H4**: [hồi quy cặp | AUDCAD,EURGBP | H4 | thoát z=0]
13. **Biến động co giãn (NR7/inside bar) × xu hướng D1**: [phá vỡ × xu hướng | FX pool, vàng | D1 | trailing ATR]
14. **Vàng/chỉ số khoảng trống đầu tuần**: gap thứ Hai lấp trong tuần. [hồi quy gap | XAUUSD, US500 | H1 | thời gian]
15. **Quản trị lệnh như biến độc lập**: trên 1 tín hiệu chuẩn (MRZ), so cố định-lot vs vol-target vs pyramid 2 bước; 3 ô. [quản trị | AUDUSD | D1 | sizing]

### P2 — bộ đọc EA (Seeker), đo trước/sau trên toàn kho đã tải
16. **Biến hướng cục bộ**: theo luồng `int dir = CheckX(); if(dir==1) Buy` → gán điều kiện của hàm vào luật; test đơn vị mới trong `test_huong_int_mql.py`.
17. **Lệnh trong vòng for/while**: nhận diện `for(...) { if(cond) OrderSend/trade.Buy }` (thường lặp symbol/vị trí) → bóc điều kiện ngoài vòng.
18. **Chuỗi trạng thái**: `state=="BUY_SETUP"` / enum trạng thái → máy trạng thái 2 bước (setup → trigger).
19. **Lọc công cụ trước dịch**: phân loại guard/panel/calculator ra khỏi mẫu số, báo tỷ lệ dịch trên "EA có điều kiện vào" (KN 8).

### P3 — dữ liệu (nguồn miễn phí không bị chặn)
20. ✅ [chu kỳ 7, 14/10 06h3x] **HistData M1 → H1/H4** AUDCAD/EURGBP/NZDUSD/XAUUSD — gộp từ M5 hd28 (`gop_m5_len_h1_h4.py`); H1 115.910/17.265/17.260/16.400 bar → `hd_ck7/`; NGUON_DU_LIEU.md.
21. ✅ [chu kỳ 7] **FRED G10 + DTWEXBGS** — 15/15 seri `fredgraph.csv` (không UA); `du_lieu_ngay/fred/` + `fred_g10_policy_thang.csv` 334 tháng 1999-01→2026-10; DTWEXBGS 5.208 ngày.
22. ✅ [chu kỳ 7] **Yahoo D1** ^GSPC 24.812 (1927→2026-10-12), ^GDAXI 9.808 (1987→), ^N225 13.958 (1970→; API cắt trước 1970). Đủ ≥1990; đối chiếu XM vẫn chờ máy nhà.
23. ✅ [chu kỳ 7, một phần] **Dukascopy spread theo giờ** — thử BID OK / ASK 503 (không hammer); bảng theo giờ từ CSV `*_h1_duka_ba_*` sẵn có (8 cặp) → `hd_ck7/*_spread_theo_gio_*` (ECN, KHÔNG phải XM). Tải ASK mới: CHƯA ĐO ĐƯỢC.

### P3 — tốc độ
24. ✅ [chu kỳ 5: `phan_tich_luoi_box.py` 49,7 s → 9,2 s tuần tự] **Đệm chỉ báo dùng chung** (z-score/ATR/RSI tính 1 lần mỗi chuỗi, cache theo băm dữ liệu) — đo cProfile trước/sau.
25. ✅ [chu kỳ 5: theo mã, 8 tiến trình → 2,6 s, đầu ra trùng bit] **Song song theo ô** (ProcessPool, 1 tiến trình/ô) cho vòng thử; đo thời gian/ô.
26. **Parquet thay CSV** cho chuỗi M5/M1 (đọc nhanh hơn, ngoài repo).
27. **Seeker tải song song có giới hạn** (≤ 4 kết nối/miền, tôn trọng 429/robots) cho nguồn mới ở `config/nguon_seeker.json` (khai_bao_tai = vong27_quet_box_13102026).

### P3 — Seeker nguồn mới (thêm 13/10, 24 nguồn đọc được + SSRN bị chặn)
28. Tải và bóc luật từ 11 repo GitHub mới (Pine/backtrader/MQL5, giấy phép MIT/Apache; chỉ lưu tóm tắt + URL) → đưa luật dịch được vào việc 3 của hàng xoay vòng.
29. Đọc arXiv/OpenAlex mới (FX anomaly, intraday seasonality, carry/momentum) → trích giả thuyết có thể kiểm, tiền đăng ký.

### P2 — luật từ X (thêm 13/10 vòng 29, chi tiết reports/vong29_x_nguon.md)
30. **IBS<0,2 chỉ số (US500/US100) trên giá XM thật H1→D1, vào 23h server, ×1,5 spread** — 2 ô qua Holm cộng dồn ở MÔ PHỎNG Yahoo; xác nhận MT5 Tester. [hồi quy | US500,US100 | D1 | thoát close>high trước]
31. **Vàng giữ qua đêm** (p_holm 0,16): đo trên XAUUSD M5 HistData theo giờ phiên XM, spread theo giờ. [qua đêm | vàng | H1 | thời gian]
32. **EURUSD H1 BB+RSI+ADX hồi quy** (dữ liệu eurusd_h1_tick_ba). [hồi quy | EURUSD | H1 | thoát giữa BB]
33. **Phạm vi Á → phá vỡ (KARMA) EURUSD M5** gộp với việc 11. [phá vỡ phiên | EURUSD | M5 | SL biên]
34. **Pine Gold Breakout 15M (WillyAlgoTrader)** — tải mã mở, dịch sang Python. [phá vỡ | vàng | M15 | SL/TP]
