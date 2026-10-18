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

> "Cậu vẫn cứ lạc đề như thế, cái tôi nói là 1 ví dụ cho 1 hệ thống giao dịch. Còn tôi muốn cậu và grok phải tư duy theo hướng đó chứ không phải máy móc test cái gì đó tốn thời gian mà lạc đề." (16/10 tối)

## ⚑ VIỆC HIỆN TẠI (17/10, chủ dự án: "xem xét lại toàn bộ") — đọc `RA_SOAT_TOAN_BO.md` TRƯỚC mọi mục dưới
Xây hệ ĐƠN GIẢN từ mảnh đã có. Thứ tự: (1) đo phí + độ giãn trên **Exness cent và XM micro** bằng `mt5tools/do_phi_san.py` (`may_nha/DO_PHI_SAN.cmd`);
(2) chạy lại các EA đã có (`ea_demo/BRAIN_V24_MRZ_Trail_D1`, `RSI_Trail_D1`) với cấu hình đã lãi trong sổ cái MT5, trên tài khoản của chủ dự án: `mt5tools/chay_lai_tren_san.py chay` (`BRAIN_IBS_Demo` cần thêm luật thoát, hàng chờ #32);
(3) ghép bằng cộng đường vốn: `chay_lai_tren_san.py tong-ket` (chia lot theo mức sụt giảm chủ dự án chọn); (4) chạy demo. **Không xây engine mới, không quét tham số.**
**Tiêu chí (17/10, đã trong code): BA YẾU TỐ CỐT LÕI** — lãi sau phí và giãn · sụt giảm ≤ 80 % · lãi ≥ 10 %/năm (lot co giãn ⇒ lãi/sụt giảm ≥ 0,125). Không gì khác được loại hệ. Xem `BO_TIEU_CHI_MOI.md`; **hệ đã đạt: `DANH_SACH_HE_DAT.md`**. Hàng chờ máy nhà #37–#40.

## ⚑ SEEKER (18/10): tìm KHO EA / chỉ báo / chiến lược VẬN HÀNH ĐƯỢC. Đọc `tai_lieu/SEEKER_KHO_VAN_HANH.md`
> *"Các cậu luôn đi tìm một cách mơ màng, đào ở những nơi không có giá trị… Tôi cần những hệ thống giao dịch, những kho EA và indicator, strategy mà vận hành được. Phải xem xét từ khoá, ký hiệu, đọc cả file để tìm những kho, nguồn như trên. Lấy của họ về, chúng ta nghiên cứu, biến tấu và kết hợp."*

Ưu tiên: **kho mã** (như EA31337) → EA/bot xử lí lệnh (lưới, DCA, hedge, gỡ, chốt rổ) → chỉ báo và chiến lược có mã. Bài viết hay video chỉ khi có luật hoặc mã; bài báo học thuật để cuối. Nhận ra "chạy được" bằng **ký hiệu mã** (`OnTick`, `OrderSend`, `strategy.entry`, `IStrategy`…) và **đọc cả file**, không rút cả EA còn một luật vào lệnh. Lệnh: `python tru/seeker.py san-kho | tai-kho owner/repo | kiem-ke <thư mục>`.

## MỤC ĐÍCH CỦA THE BRAIN (chủ dự án 17/10 — đọc trước khi làm bất cứ gì)

> "Cậu đã giao dịch forex bao giờ chưa? Cái cậu làm là vẫn loanh quanh mớ lý thuyết và đi tìm đống hệ thống giao dịch học thuật và trong mơ, việc làm như thế tự chặt đứt hết mọi lợi thế mà cái game này có
> như dca gồng lệnh, gỡ lệnh, việc kết hợp các phương pháp và hệ thay vì đánh đơn hệ… cái tôi tạo ra cái the brain này là để cậu tìm kiếm và kết hợp nó lại với nhau."

**Sơ đồ gốc của chủ dự án (`SO_DO_HE_THONG.txt`) đã viết đúng điều này từ đầu** — các agent đọc nhưng làm ngược:
- *"việc sử dụng kỹ thuật quản lí lệnh tốt còn hơn việc có 1 entry tốt"* — ATR, trailing, hedging, buy/sell stop hai đầu, DCA, DCA tính vốn, đánh nhanh chốt nhanh.
- *"tìm kiếm và bóc tách các cơ chế, các loại chiến lược theo lối này để dựng thành các hệ thống TÍCH HỢP VÀ BỔ SUNG. Hệ quản lí lệnh này có thể quản trị độc lập hoặc làm 1 bộ quy tắc để tích hợp vào những hệ thống khác."*
- *"nếu có thể hãy thử kết hợp đa chỉ báo đa hệ thống mà chúng ta tìm được."* / Hephaestus = *ghép nút, sinh tổ hợp* ("10 trader có 20 kiểu dùng Ichimoku: cái biến thiên nằm ở CÁCH GHÉP").

**Chúng ta đã làm sai ở đâu (bản hiểu của Claude):** đánh giá từng mảnh ĐỨNG MỘT MÌNH như một hệ đơn-entry, qua cổng kiểu SL/rr/thống kê (cổng `rr ≥ 0,2` còn được viết để giết đúng DCA/không-SL), rồi vứt mảnh nào thua một mình.
Làm vậy tự chặt đứt các lợi thế của cuộc chơi: **gồng lệnh, DCA, gỡ lệnh, hedge, ghép nhiều phương pháp và nhiều hệ**. Một mảnh thua một mình có thể là nửa còn thiếu của một hệ ghép.

**Luật mới từ đây:**
1. **Đơn vị công việc là HỆ GHÉP, không phải một chiến lược đơn.** Hệ ghép = nhiều nguồn lệnh/phương pháp chạy cùng nhau + một bản đồ vùng chung (mốc của nhiều phương pháp trùng nhau thành vùng DCA/chốt) + một bộ quản lí gắn lên tất cả (gồng, DCA, nhồi theo chiều, hedge, **gỡ lệnh**: lãi của hệ này đóng lệnh kẹt của hệ kia).
2. **Cấm loại một mảnh chỉ vì nó thua khi đứng một mình hoặc vì nó không hợp cổng SL/rr.** Mảnh nào có cơ chế hiểu được thì GIỮ làm nguyên liệu ghép, gắn nhãn "vai trò": nguồn lệnh · mốc/vùng · bộ quản lí · bộ gỡ lệnh.
3. **Đo ở cấp TÀI KHOẢN, không đo từng lệnh**: đường vốn thả nổi, margin, thời gian kẹt, lỗ treo tối đa, thu nhập mỗi tháng của cả hệ ghép.
4. **Tìm tổ hợp bằng SUY LUẬN về sự bù nhau** (hệ A yếu ở trạng thái nào thì hệ B mạnh ở trạng thái đó; mốc của B làm vùng DCA cho A; lãi của B gỡ kẹt cho A), không bằng lưới tham số mù.
5. Các luật 16/10 (hạ cổng thống kê thành nhãn, giữ phí thật + không nhìn trước + khớp MT5) vẫn giữ.

## CÁCH TƯ DUY — ưu tiên hơn MỌI việc test (chủ dự án 16/10 tối)

Ví dụ ONH/Judas bên dưới là **MỘT VÍ DỤ của một KIỂU hệ thống giao dịch**. Đừng biến nó thành bài test riêng (không quét tham số, không tối ưu TP/SL của ví dụ).
Việc của Claude và Grok là **suy nghĩ như người thiết kế hệ thống giao dịch**: hiểu cấu trúc kiểu hệ này, tự nghĩ ra và ghép được nhiều hệ cùng kiểu, giải thích được vì sao nó có thể ra tiền và khi nào nó hỏng.

### Giải phẫu một hệ thống kiểu này — 5 khối (bản hiểu của Claude từ lời chủ dự án; chủ dự án sửa)
1. **Bối cảnh / thiên hướng**: xu hướng lớn (chỉ số Mỹ thiên tăng), mùa vụ, phiên giao dịch, độ biến động hôm nay.
2. **Mốc / vùng tham chiếu** và *vì sao tại đó có lệnh chờ / thanh khoản*: ONH/ONL, PDH/PDL, giá mở phiên, mốc tròn, pivot, gap chưa lấp.
3. **Sự kiện kích hoạt**: quét thanh khoản (Judas swing, false breakout), phá rồi retest, hấp thụ, đuổi theo.
4. **Vào lệnh + mục tiêu nhỏ**: limit tại mốc; chốt vài điểm; kéo SL về hoà vốn / dương khi đã lãi.
5. **Cây xử lí khi sai (không SL cứng)** — chỗ quyết định tiền: chờ giá quay lại · DCA ở vùng giá đẹp · nhồi lệnh theo chiều giá chạy để cắt sai · hedge. Mỗi nhánh dùng khi trạng thái thị trường nào, vốn/margin cần bao nhiêu, swap trong lúc kẹt.

### Với mỗi kỹ thuật / mốc / hệ, phải trả lời bằng LỜI (không cần code trước)
- a. **Ai ở phía bên kia** và vì sao giá hay quay lại / đi xuyên qua đây (lệnh chờ, stop, thanh khoản, hành vi phiên).
- b. **Khi nào nó hỏng**, dấu hiệu sớm để phân biệt "nhịp lùi trong xu hướng" với "đổi xu hướng".
- c. **Hỏng thì nhánh nào hợp**: hồi quy → chờ / DCA ở vùng đẹp; đổi xu hướng → nhồi theo chiều chạy để cắt sai / hedge.
- d. **Cái giá**: kẹt bao lâu, lỗ treo bao nhiêu điểm, vốn/margin, swap qua đêm.
- e. **Ghép**: hệ nào bù nhau (khác cơ chế), hệ nào xung đột.

### Bẫy đã biết (từ chính ghi chú SP500 của chủ dự án)
- **DCA (hồi quy) ghép vào setup breakout / continuation (động lượng) từng là thảm hoạ (−17.000 điểm)** — mà hệ ONH vào theo kiểu retest/continuation còn xử lí khi sai bằng chờ/DCA. Cây xử lí phải phân biệt hai trạng thái sau khi vào lệnh hỏng, không dùng một kiểu cho mọi trường hợp.
- Kiểu "kẹt thì giữ": tỉ lệ thắng gần 100 % là bình thường và **không chứng minh gì**; cái quan trọng là lỗ treo, thời gian kẹt, vốn, swap.
- Chỉ số Mỹ thiên tăng dài hạn nên "chờ giá về" thắng "cắt" trong mẫu 2016–2026, nhưng đã có lệnh kẹt 705 ngày (2022). Đó là rủi ro chấp nhận **có ý thức bằng vốn**, không phải bằng chứng an toàn.

### Cách làm việc từ bây giờ
- **LLM suy luận và thiết kế.** Mỗi hệ viết thành một "thẻ hệ thống" ngắn: 5 khối + cơ chế + nhánh hỏng + cái giá. Ít mà sâu.
- **SEEKER thu kỹ thuật / mốc từ thị trường thành thẻ theo 5 khối** (ai ở bên kia, mốc, sự kiện, vào, xử lí khi sai), không cần biến mọi thứ thành code để test.
- **Kiểm tra chỉ để NHÌN ĐƯỜNG ĐI RỦI RO** của một hệ chủ dự án đã chọn (lỗ treo, thời gian kẹt, vốn, swap): nhanh, ít, có chủ đích. Không để việc kiểm tra dẫn dắt hướng đi.
- **TẠM DỪNG cho tới khi chủ dự án nói tiếp:** quét lưới / tham số hàng loạt, vòng lặp máy móc tự chạy (v33 trở đi), MT5 farm / chạy đêm, nhân ví dụ ONH thành nhiều biến thể.
- **Không chắc ý chủ dự án thì hỏi một câu ngắn bằng lời thường**, đừng chạy thử cho chắc.

## Hiểu đúng chủ dự án là ai

Một **trader giao dịch tay** trên MT5 điện thoại, lot nhỏ (Exness cent, XM micro), thoát bằng TP/kéo SL dương, không SL cứng. Hệ thống phục vụ người này, không phục vụ bài báo khoa học.
Thứ chủ dự án dùng được: **setup rõ ràng** (nhìn gì trên chart, vào đâu, SL/TP đâu, sai thì DCA/nhồi/hedge thế nào), **mốc giá/vùng giá**, **kỹ thuật xử lí lệnh**.
Thứ chủ dự án không đọc được và không cần: p-value, Holm, FDR, MDE, ICC, placebo.

## Luật mới

1. **Mục tiêu duy nhất: có lợi nhuận.** Đo bằng tiền / điểm giá (tiền theo lot chủ dự án tự chọn), không bằng mức ý nghĩa thống kê.
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

## VÍ DỤ #1 — hệ ONH của chủ dự án (để HIỂU kiểu hệ thống; KHÔNG phải bài test cần quét biến thể)

> "SP500 mở phiên tăng sau đó quét judas swing về ONH thì tôi buy với lot 0,01 lời 5-6 usd tôi chốt hoặc kéo sl dương."

**Bản hiểu (Claude, CẦN chủ dự án xác nhận). Các gạch dưới đây để hiểu cấu trúc, không phải danh sách việc phải quét:**
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
- (Lược bỏ yêu cầu báo bảng mọi biến thể — chủ dự án 16/10 tối: không máy móc test tốn thời gian. Chỉ cần hiểu khối 1–5 của ví dụ này và nhìn đường đi rủi ro khi chủ dự án yêu cầu.)

## Số minh hoạ của Claude (H1, xấp xỉ) — chỉ để thấy ĐƯỜNG ĐI RỦI RO của kiểu "kẹt thì giữ"; KHÔNG làm lại ở M1, KHÔNG nhân thành quét

Chi tiết: `reports/onh_h1_lan_dau.md`; script `mau_thu/onh_h1.py`, `mau_thu/onh_dca.py`. 852 setup (2016–2026), TP 0,07 % (~5,4 điểm), không SL, chờ đến cùng:
- **100 % lệnh cuối cùng chạm TP** (chỉ số Mỹ hồi lại), 74 % ngay trong phiên, 94 % trong 5 ngày. Nhưng **lâu nhất 704 ngày** (vào 13/01/2022), **lỗ treo tệ nhất −30,9 %** (vào 26/02/2020, kẹt ~100 ngày).
- Lãi/lệnh +6,0 bps trước swap, chỉ còn **+1,1 bps sau swap** (≈ 1,2 điểm mỗi đêm giữ, thứ Sáu ×3): vài lệnh kẹt lâu ăn gần hết lãi. Năm 2022 trung bình −20,9 bps/lệnh.
- **ONH-retest KHÔNG hơn mua đại lúc 09:00 NY mỗi ngày** (+1,8 bps) ở độ phân giải H1 — chưa kết luận về setup thật (vào bằng nến phút).
- DCA −0,5 %/−1 % × 3: chờ ngắn hơn nhưng vốn phình tới 4 đơn vị, lỗ treo tệ nhất ~100–120 % giá trị một đơn vị.

## Việc tiếp theo (thay thế danh sách cũ, 17/10) — chi tiết và kết quả đầu ở `DE_XUAT_THAY_DOI_THE_BRAIN.md`

Chủ dự án 17/10: *"tìm những hệ thống giao dịch và những tín hiệu vào lệnh, kết hợp nó lại với nhau cùng với quản trị vốn … sưu tập tất cả những hệ thống có thể vào lệnh được … đơn hệ + tiêu chí học thuật nặng nề thì không đảm bảo kết quả tốt."*
1. **Claude**: `nhan/tai_khoan.py` (engine cấp tài khoản, **đã có v1**, 5 test) → mở sang nhiều tài sản + lệnh bán/hedge; hồ sơ trạng thái + điểm "bù nhau".
2. **Grok** (chỉ sau khi chủ dự án duyệt): thu **mọi nguồn vào lệnh được** thành **dòng lệnh vào** `LenhVao(nguon, chi_so, gia, chieu)`: luật đã dịch được → chạy thẳng; EA chưa dịch được → **chạy trên MT5 máy nhà để xuất danh sách lệnh vào** (không chấm đạt/trượt); lịch sử giao dịch → dòng sẵn. Bộ lọc chỉ hỏi "ra lệnh đo được không". Song song rút phần quản lí từ `input`/`.set`. Không quét tham số.
3. Chọn 2–3 hệ ghép cùng chủ dự án → bài "ngày tận thế" (2008/2020/2022/2025) → hồ sơ một trang.

## Ghi chú cho Grok

- Phần kỹ thuật ở nhánh `de-xuat-cong-kiem-dinh` (thư mục `de_xuat/`) **không áp dụng như cổng**. Có thể dùng làm tham khảo khi cần gắn nhãn tham khảo, không dùng để loại.
- Nếu một luật cũ trong repo mâu thuẫn với file này: **file này thắng**; ghi vào `GHI_CHU_NANG_CAP_GROK.md` chỗ bạn thấy mâu thuẫn để chủ dự án xử lí.
- Báo chủ dự án 3–8 dòng, bằng lời thường: xong / chưa / kẹt / cần chủ dự án làm gì.
