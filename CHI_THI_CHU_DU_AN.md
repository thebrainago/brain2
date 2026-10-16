# CHỈ THỊ CỦA CHỦ DỰ ÁN — 16/10/2026 — ƯU TIÊN CAO NHẤT

**File này thắng mọi luật cũ mâu thuẫn với nó** (`CLAUDE.md` "Luật không được phá", `tai_lieu/VONG_LAP.md` "Luật cứng", `BAN_GIAO_GROK.md` mục 3 "cổng chặt",
`tai_lieu/KINH_NGHIEM.md` mục 4 "không được nới cổng" và mục 10, nhánh `de-xuat-cong-kiem-dinh` phần cổng). Claude ghi lại đúng lời chủ dự án, không diễn giải thêm.

## Lời chủ dự án (nguyên văn)

> "nhớ note vào cho grok thả lỏng hết những luật chặt chẽ. Tôi chỉ cần có lợi nhuận thôi. Và việc may mắn trong đầu tư hay lợi thế trong 1 trend là bình thường mà?
> Uptrend thì mua ở đâu cũng thắng, khủng hoảng ở đâu cũng lỗ. Sao cứ phải loại yếu tố may mắn đi? Và hệ thống này là để tìm những mảnh ghép vô tình dùng được
> thì các cậu lại luôn dẹp nó đi."

> "Việc của tôi là mở điện thoại vào app mt5 và giao dịch, tôi có thể đoán đúng hoặc sai thì đã có sl và tp. Hoặc nếu tôi sai thì sẽ chờ vùng giá đẹp để dca hoặc nhồi lệnh
> theo chiều giá chạy để cắt sai, hoặc tôi hedging... Cái tôi tìm kiếm là những phương pháp giao dịch, kĩ thuật xử lí hoặc những mốc giá/điểm/vùng trên chart nhiều giá trị
> để khai thác. [...] Sao các cậu cứ đi tìm và test cái gì đó rất hàn lâm và bác học vậy nhỉ."

## Hiểu đúng chủ dự án là ai

Một **trader giao dịch tay** trên MT5 điện thoại, lot nhỏ (0,01), có SL/TP. Hệ thống phục vụ người này, không phục vụ bài báo khoa học.
Thứ chủ dự án dùng được: **setup rõ ràng** (nhìn gì trên chart, vào đâu, SL/TP đâu, sai thì DCA/nhồi/hedge thế nào), **mốc giá/vùng giá**, **kỹ thuật xử lí lệnh**.
Thứ chủ dự án không đọc được và không cần: p-value, Holm, FDR, MDE, ICC, placebo.

## Luật mới

1. **Mục tiêu duy nhất: có lợi nhuận.** Đo bằng tiền (USD ở lot 0,01), không bằng mức ý nghĩa thống kê.
2. **Hạ xuống thành NHÃN THÔNG TIN, KHÔNG dùng để loại bất cứ ý tưởng nào:** p-value, Holm, FDR, LORD, placebo, MDE, "dương cả hai nửa", tiền đăng ký trước,
   "t_alpha > 5 nghi", "xác nhận là hàm ý nguyên", ngưỡng maxDD cứng, "phải thắng mua-giữ", cổng "đủ lệnh" theo thống kê. Ý tưởng vẫn được ghi kết quả; không ai bị gạt vì các nhãn này.
3. **May mắn, xu hướng, chế độ thị trường là hợp lệ.** Một mảnh ghép lãi vì uptrend, vì một giai đoạn, vì một phiên, vì một tài sản **vẫn được GIỮ**.
   Việc của hệ thống là gắn điều kiện ("chỉ ăn khi uptrend", "ăn 2024–2025", "ăn phiên Mỹ") để chủ dự án biết khi nào dùng, khi nào không — **không phải loại nó đi**.
   Mục đích của hệ thống chính là tìm những mảnh ghép tình cờ dùng được.
4. **Chỉ còn ba thứ GIỮ, vì chúng làm con số có THẬT, không phải vì "chặt chẽ":**
   a. **Chi phí thật của XM** (spread theo giờ, swap, hoa hồng, làm tròn lot, lot tối thiểu). Thiếu chi phí thật → ghi **CHƯA ĐO ĐƯỢC**, đừng ghi lãi.
   b. **Không dùng dữ liệu tương lai** khi tính tín hiệu (lỗi code, từng sinh ra 27 "hệ sống" giả ở vòng 25). Đây là lỗi lập trình, không phải tiêu chí học thuật.
   c. **Mô phỏng phải khớp MT5**, đặc biệt lưới/DCA (engine `luoi.chay` cũ lạc quan; dùng `luoi_duong`). Số chưa khớp thì dán nhãn "MÔ PHỎNG, có thể lạc quan".
   Canary (kiểm máy đo không hỏng) vẫn chạy; nếu hỏng thì **sửa máy đo**, không dùng làm lý do bỏ ý tưởng.
5. **Luật vận hành khác giữ nguyên:** không bí mật/mật khẩu trong git, không mua gì, không vượt chặn bot/Cloudflare, không đăng nhập mạng xã hội/Telegram, nhãn MÔ PHỎNG.

## Cách báo cáo cho chủ dự án

Tiếng thường, bằng tiền, ngay đầu báo cáo, mỗi setup một dòng/bảng nhỏ:
số lệnh · thắng/thua · lãi ròng USD cho lot 0,01 (ghi rõ 1 điểm giá = bao nhiêu USD) · lãi/lỗ TB mỗi lệnh · chuỗi thua dài nhất · sụt giảm tối đa bằng USD ·
vốn tối thiểu cần · theo tháng/năm · theo chế độ (tăng / giảm / đi ngang) · tệ nhất khi DCA/nhồi lệnh cần bao nhiêu vốn.
Số thống kê (nếu có) để ở phần cuối, nhãn "tham khảo". Không báo cáo "0 qua cổng"; báo cáo "đây là những gì kiếm được, trong điều kiện nào".

## Quản lí lệnh kiểu thủ công — mô phỏng như người làm tay

SL/TP cố định; **kéo SL về hoà vốn / dương** sau khi lãi X; **DCA ở vùng giá đẹp** khi sai; **nhồi lệnh thuận chiều giá chạy để cắt sai**; **hedging**.
Với mỗi kiểu: báo kết quả và **tình huống xấu nhất cần bao nhiêu vốn** (không phải điểm Sharpe).

## VIỆC SỐ 1 — test setup của chính chủ dự án (nguyên văn rồi bản hiểu)

> "SP500 mở phiên tăng sau đó quét judas swing về ONH thì tôi buy với lot 0,01 lời 5-6 usd tôi chốt hoặc kéo sl dương."

**Bản hiểu (Claude, CẦN chủ dự án xác nhận; thử nhiều biến thể, báo hết, đừng chọn riêng cái đẹp):**
- Tài sản: SP500 (XM `US500Cash`). Phiên Mỹ mở 09:30 giờ New York = 16:30 giờ server XM (giờ server lệch 1 tiếng vài tuần quanh đổi giờ mùa hè Mỹ/châu Âu — dùng múi giờ New York để định phiên).
- ONH = đỉnh của phiên đêm. **Repo không có định nghĩa ONH** (dự án SP500 phase 1 đã tách khỏi git 18/09 và nằm trên máy chủ dự án; Claude đã tìm trong cả hai repo và Google Drive: không thấy). Tạm dùng 18:00 NY hôm trước → 09:30 NY (Globex mở 18:00 NY);
  thử thêm 16:15 NY→09:30. **Chủ dự án / Grok: nếu thư mục SP500 phase 1 trên máy có chỗ ghi giờ tính ONH thì dùng giờ đó** và ghi vào đây. Thử cả ONL (đáy) cho kịch bản ngược.
- **Giờ**: server XM = EET/EEST (UTC+2/+3), **không phải "NY+7" cố định** như comment ở `nhan/moc_nam_cham.py` — 3–4 tuần mỗi năm (Mỹ đổi giờ trước/sau châu Âu) mở cửa phiên Mỹ rơi vào 15:30 server thay vì 16:30 (đo bằng khối lượng H1, 16/10). Luôn đổi sang giờ New York thật (`tz_localize('Europe/Athens')` → `tz_convert('America/New_York')`, xem `mau_thu/onh_h1.py`) rồi mới định phiên/ONH.
- "Mở phiên tăng": giá mở/đẩy lên trên hoặc quanh ONH sau 09:30. "Quét Judas swing về ONH": giá quay xuống chạm/xuyên ONH rồi bật lại (dạng quét thanh khoản).
- Vào BUY: (a) lệnh limit tại ONH, (b) khi nến M1/M5 đóng lại trên ONH sau khi quét. Thử cả hai.
- Chốt: **lãi 5–6 ĐIỂM GIÁ** (chủ dự án 16/10: *"Lời 5-6 giá đi cho dễ hiểu (còn tiền tự tôi đi lot)"*). Tính MỌI THỨ bằng điểm giá; quy ra tiền theo lot sau (lot do chủ dự án tự chọn).
  **Sàn chủ dự án đánh thật: Exness cent (US500M) và XM micro** (16/10). Bảng phí trong repo là XM Ultra Low; **spread/swap của Exness cent và XM micro CHƯA đo** — chờ chủ dự án đọc spread (ask − bid) trên MT5. Chạy với spread 0,6 / 1,5 / 3 điểm và báo điểm hoà vốn của spread (Claude đo trên H1: hoà vốn ở spread ≈ 3,4 điểm).
- **KHÔNG SL** (chủ dự án 16/10: *"tôi đánh không sl"*, *"có thể chịu lỗ cho tới khi giá quay lại hoặc các mức dca hoàn vốn"*). Thoát bằng TP / kéo SL dương khi đã lãi; khi sai thì **chờ giá quay lại** hoặc **DCA ở các mức hoàn vốn**.
  Với kiểu này win-rate gần 100 %, nên **KHÔNG dùng win-rate / lãi trung bình làm thước**. Thước là: **lỗ treo tối đa** (% giá trị và USD), **thời gian kẹt tối đa**, **số đơn vị DCA tối đa và vốn/margin cần để ngồi qua**, **swap cộng dồn trong lúc kẹt**. Mô phỏng DCA: bước theo %/ATR/mốc giá, số tầng, TP theo giá trung bình.
- Giá: M1 (HistData SPXUSD trên máy Grok; `reports/mt5_v27/gia_xm/US500Cash_H1.csv.gz` chỉ có H1, quá thô để thấy cú quét 5–15 phút đầu phiên). Phí: spread theo giờ XM thật (`reports/mt5_v27/spread_gio/US500Cash.csv`, trung vị ~0,55–0,6 điểm ở các giờ; bản Standard ước nhỉnh hơn).
- Báo cáo: bảng mọi biến thể, theo năm và theo chế độ (tăng/giảm), theo ngày trong tuần, lãi ròng sau spread tính bằng điểm và USD. Ghi rõ biến thể nào "ăn", biến thể nào "lỗ", và **vì sao** (cú quét có thật không).

## Mốc đầu tiên của Claude (H1, xấp xỉ) — Grok làm lại ở M1

Chi tiết: `reports/onh_h1_lan_dau.md`; script `mau_thu/onh_h1.py`, `mau_thu/onh_dca.py`. 852 setup (2016–2026), TP 0,07 % (~5,4 điểm), không SL, chờ đến cùng:
- **100 % lệnh cuối cùng chạm TP** (chỉ số Mỹ hồi lại), 74 % ngay trong phiên, 94 % trong 5 ngày. Nhưng **lâu nhất 704 ngày** (vào 13/01/2022), **lỗ treo tệ nhất −30,9 %** (vào 26/02/2020, kẹt ~100 ngày).
- Lãi/lệnh +6,0 bps trước swap, chỉ còn **+1,1 bps sau swap** (≈ 1,2 điểm mỗi đêm giữ, thứ Sáu ×3): vài lệnh kẹt lâu ăn gần hết lãi. Năm 2022 trung bình −20,9 bps/lệnh.
- **ONH-retest KHÔNG hơn mua đại lúc 09:00 NY mỗi ngày** (+1,8 bps) ở độ phân giải H1 — chưa kết luận về setup thật (vào bằng nến phút).
- DCA −0,5 %/−1 % × 3: chờ ngắn hơn nhưng vốn phình tới 4 đơn vị, lỗ treo tệ nhất ~100–120 % giá trị một đơn vị.

## Việc tiếp theo (theo thứ tự)

1. Việc số 1 ở trên. Báo cáo bằng tiếng thường như mục "Cách báo cáo".
2. Mở rộng cùng họ: các **mốc/vùng** quen thuộc của trader (ONH/ONL, PDH/PDL, giá mở cửa phiên Á/Âu/Mỹ, mốc tròn, vùng DCA đẹp) × hành vi (quét rồi bật, phá rồi retest, đuổi theo) trên SP500, NAS100, vàng, vài cặp FX. Seeker gom thêm kỹ thuật dạng này (ICT/SMC, quét thanh khoản, phiên giao dịch...).
3. **Danh mục mảnh ghép**: mỗi mảnh = điều kiện dùng + số tiền ở lot 0,01. Không loại mảnh nào vì "chỉ ăn trong một chế độ".
4. Làm phần xử lí lệnh (hoà vốn, DCA, nhồi, hedge) thành module mô phỏng đúng như người làm tay.

## Ghi chú cho Grok

- Phần kỹ thuật ở nhánh `de-xuat-cong-kiem-dinh` (thư mục `de_xuat/`) **không áp dụng như cổng**. Có thể dùng làm tham khảo khi cần gắn nhãn tham khảo, không dùng để loại.
- Nếu một luật cũ trong repo mâu thuẫn với file này: **file này thắng**; ghi vào `GHI_CHU_NANG_CAP_GROK.md` chỗ bạn thấy mâu thuẫn để chủ dự án xử lí.
- Báo chủ dự án 3–8 dòng, bằng lời thường: xong / chưa / kẹt / cần chủ dự án làm gì.
