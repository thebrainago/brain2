# Quan sát vận hành máy nhà – đêm 20/10 → sáng 21/10/2026

Ghi bởi Grok Bot (routine "Canh máy nhà đêm 20/10"), mỗi lần kiểm thêm một mục. Chỉ ghi số đo thật; chỗ nào chưa có thì ghi CHƯA ĐO ĐƯỢC.

## Lần kiểm 20:38–20:46

**Ảnh chụp tài nguyên (20:38–20:45):** CPU 27–32 % (20 luồng logic), RAM trống 23,9 GB lúc 20:38 rồi còn 8,7 GB lúc 20:45 khi 3 việc tầng 2 chạy, ổ trống C 21,3 GB, D 22,3 GB, E 199,6 GB.

**Hàng MT5:**
- Từ 19:26 đến 20:38 chỉ có **1 slot** (C:\mt5_tester\p7) thật sự test, 4 slot kia bị terminal do `kiem_may.py` mở chiếm chỗ. Tức là khoảng 70 phút bỏ phí 4/5 slot. Đã sửa code (d4100d3d), Claude đóng các terminal treo lúc 20:22, và `chay_lien_tuc.py` được khởi động lại lúc 20:38:38 với 5 slot (p1, p7, p3, p6, p4), PID 7136.
- Sổ cái từ 19h đến 20:41: 6 bản ghi, gồm 5 tầng 1 và 1 tầng 2 (od_skea0cc19095a9: net 824,76, 429 lệnh, PF 1,66, DD 28,87 %, chạy 1218 s).
- Thời gian tầng 1 đo được: 66 s, 93 s, 102 s, 129 s. Trong đó riêng khâu tải lịch sử và nối agent chiếm khoảng 20–110 s mỗi lần (p6 bắt đầu 20:38:49, agent mới test lúc 20:39:38; p4 bắt đầu 20:38:52, test lúc 20:40:55).
- **Trùng cổng agent:** lúc 20:39:04 metatester của p7 và p3 cùng mở 127.0.0.1:3001. Lượt p3 (od_skea4d01476642_XM_CSV_T1) ra báo cáo hỏng (kỳ M0 1970, 0 lệnh, chất lượng 0 %, 24 s), lượt chạy lại xong bình thường sau 129 s (192 lệnh, tầng 1 TRƯỢT). Mất khoảng 30 s cộng một lần khởi động.
- **RAM tầng 2 thật:** metatester tầng 2 dùng 4,2 GB, 4,9 GB và 5,9 GB (đo 20:45), trong khi `config/dieu_phoi.json` giả định `ram_moi_slot_tang2_gb` = 2,5. Tổng 10 tiến trình MT5 của slot dùng 16,3 GB.

**Dịch LLM:** lượt 200 thẻ (xong 20:34): đạt 107, hỏng 93, lỗi LLM 0, 237 lần gọi, 1.517.659 token vào và 1.245.952 token ra. Trong số hỏng, 69 thẻ là KHONG_RA_SPEC_PY (74 % số hỏng). Tốc độ khoảng 200 thẻ trong 29 phút (20:05→20:34), còn 2.252 thẻ chờ, ước khoảng 5,5 giờ nữa nếu giữ tốc độ này. Lượt mới chạy từ 20:34:22.

**Seeker:** đang chờ vì hàng đầu vào còn đủ (MT5 200 việc, 2.300 thẻ chưa dịch). Hợp lý.

**Ngồi chờ:** bước 6 của `chay_toi_nay.ps1` (ong_dan chay) chờ khoá `ong_dan_chay.lock` từ 20:05:15 đến 20:34:16, tức 29 phút, vì lượt dịch 200 thẻ giữ khoá.

**Lỗi khoá (đã sửa code):** lúc 20:34:16 bước 6 lấy khoá (PID 10256), 6 giây sau `dieu_phoi_may_nha.py` thấy lượt dịch cũ xong thì xoá khoá vô điều kiện rồi phóng lượt dịch mới và ghi đè PID 14000. Hệ quả là `ong_dan chay` và `dich_llm` đang chạy song song trên cùng CSDL SQLite (timeout 60 s nên chưa thấy lỗi). Đã sửa: `_tha_khoa(pid)` chỉ xoá khoá khi khoá còn ghi PID của chính nó, kèm test mới (43 passed). Tiến trình điều phối đang chạy vẫn dùng mã cũ, mã mới có hiệu lực từ phiên sau.

### Đề xuất
1. **Tách khoá theo loại việc:** dịch LLM chủ yếu chờ mạng, `ong_dan chay` tốn CPU. Nếu hai việc ghi các dòng khác nhau của CSDL thì cho chạy song song có chủ đích (bật WAL cho SQLite) thay vì bắt bước 6 chờ 29 phút trong lúc CPU chỉ 27–32 %.
2. **Cổng agent riêng cho mỗi slot** (hoặc giãn 10 s giữa hai lần phóng) để tránh trùng 127.0.0.1:3001, đỡ một lượt chạy hỏng mỗi lần trùng.
3. **Sửa `ram_moi_slot_tang2_gb` từ 2,5 lên khoảng 5,0** theo số đo thật 4,2–5,9 GB, để bộ điều phối không cho thêm tầng 2 khi RAM thật không đủ. RAM là giới hạn chính của tầng 2, CPU còn dư nhiều.
4. **CPU còn rảnh khoảng 65 %:** tầng 1 nhẹ RAM (terminal 100–190 MB, metatester tầng 1 khoảng 30–280 MB), nên có thể thêm slot tầng 1 (E:\mt5_tester\p5 đã có sẵn nhưng không nằm trong BRAIN_SLOTS) để lọc nhanh hơn trong khi 3 slot tầng 2 giữ RAM.
5. **Giữ sẵn lịch sử trong slot:** 20–110 s tải lịch sử mỗi lượt tầng 1 chiếm phần lớn thời gian một lượt 66–129 s. Đồng bộ trước lịch sử các symbol hay dùng vào từng slot sẽ rút ngắn tầng 1 đáng kể.
6. **Giảm phí dịch:** khoảng 25.800 token cho mỗi thẻ dịch đạt (2.763.611 token / 107). KHONG_RA_SPEC_PY chiếm 69/200 thẻ, ước khoảng 34 % token của lượt. Nên xem lại prompt hoặc lọc trước những thẻ không có mã cơ chế để bớt gọi thừa.

**Bài học git trên máy nhà (20:53):** không dùng `pull --rebase --autostash` khi vòng MT5 đang chạy. Autostash làm `so_cai.jsonl` lùi 2 phút, khiến 4 việc tầng 1 bị chạy lại (351 giây slot). Đề xuất: tách các tệp sổ cái, báo cáo chạy liên tục ra khỏi cây git (ghi vào `data/` rồi chỉ sao chép vào `reports/` lúc báo cáo), để mọi lần pull hay push trên máy nhà luôn có cây sạch.


## Lần kiểm 21:01-21:15

**Ảnh chụp tài nguyên:** 21:01 CPU 8-9 % (chỉ 3 metatester tầng 2), RAM trống 9,3 / 31,9 GB, ổ trống C 19,1 GB, D 20,2 GB, E 196,1 GB. 21:12 có 5 việc MT5: CPU 18 %, RAM trống 3,9 GB (bộ điều phối hạ muc_mt5 về tong=0, việc đang chạy giữ nguyên).

**Hàng MT5:** sổ cái 710 dòng lúc 21:01 (703 lúc khôi phục 20:53). Từ 20:47 đến 21:02 xong 9 lượt tầng 1 (7 QUA, 2 TRUOT, 63-246 s mỗi lượt) và 2 lượt tầng 2 real tick (od_skea0ab4d307d3 944 s, od_mql525573694a7f03d3a 1158 s). UNG_VIEN.md: ĐẠT 30 (20:01) lên 33 (21:02).

**Slot rỗi vì hết việc tầng 1 XM:** 20:56:18-21:04:12 p4 rỗi 8 phút, p3 rỗi 6 phút (tới 21:02:18), p6 rỗi 2 phút. Lúc đó `sinh_viec.lay_viec(san='XM', chi_tang1=True)` trả 0 việc; trong hang_cho_mt5.jsonl có 144 việc ống dẫn thì 72 là Exness (máy này không có slot Exness nên không bao giờ chạy). Việc tầng 1 mới chỉ xuất hiện khi `ong_dan chay` ghi lại hang_cho_mt5.jsonl lúc 21:03:54 (6 việc XM). CPU chỉ 8-9 % trong khoảng đó.

**Số đo bộ điều phối gây hiểu nhầm:** su_dung.jsonl luôn ghi hang_mt5 = 200 (đếm có trần, gồm khoảng 2.830 việc cũ không phải ống dẫn), nên Seeker luôn bị chặn với lý do "MT5 200 việc" trong khi việc tầng 1 XM sẵn sàng thật chỉ 0-6. slot_tong ghi 4 trong khi chay_lien_tuc chạy 5 slot (p7 không được đếm).

**Dịch LLM (số thật từ dp_dich_llm.out.txt):**
- Lượt 2 (20:34-20:57, 1400 s): 200 thẻ, ĐẠT 68, HỎNG 132 (KHONG_RA_SPEC_PY 114 = 57 %), 225 lần gọi, 1.655.430 token vào + 914.201 token ra, tức khoảng 37.800 token cho mỗi thẻ ĐẠT (lượt 1 khoảng 25.800).
- Lượt 3 (20:57-21:05): 164 thẻ, 144 lấy từ cache (bản sửa dùng lại cache khác model chạy đúng), ĐẠT 100, 56 lần gọi, 116.384 vào + 90.894 ra; token suy luận 74.472 = 82 % token ra.
- **Sự cố hết quota ai-box từ ~20:58:** HTTP 403 insufficient_user_quota (số dư -144,6 đ, kiểm 21:06). 6 lượt 20:58-21:11, mỗi lượt ~1 phút, ghi 1.067 lỗi LOI_LLM lên 575 thẻ, 492 thẻ lên loi_lan=2. Model dự phòng cũng 403 (cùng tài khoản). Đã sửa code (hết quota thì CHUA_CHAY_DUOC, dừng lượt, rc=3, điều phối nghỉ 15 phút) và trả lại loi_lan cho 575 thẻ. Trong lúc lặp dich_llm hỏng, ô ống dẫn (khoá ong_dan_chay.lock) bị chiếm nên Python (toi_uu, loc, sinh_mt5, nguồn việc tầng 1) không được chạy từ bộ điều phối.
- Không dừng được bộ điều phối để đổi cấu hình: tiến trình chạy quyền admin, shell của Grok không có quyền (Access denied), và dieu_phoi_may_nha.py chỉ đọc config/dieu_phoi.json lúc khởi động.

### Đề xuất
1. **Nạp quota ai-box** (chỉ Anh làm được) và đặt cảnh báo số dư: trước mỗi lượt dich_llm gọi thử 1 lần rẻ; hết quota thì nghỉ và báo, thay vì đốt lượt.
2. **Bộ điều phối đọc lại config/dieu_phoi.json mỗi chu kỳ** (hoặc theo mtime), để tắt hay bật một bước chỉ cần sửa tệp, không phải giết tiến trình admin.
3. **Giảm token suy luận của qwen3.7-max:** 82 % token ra ở lượt 3 là suy luận. Thử A/B 20 EA với `tham_so_them` (tắt thinking hoặc đặt thinking_budget) xem tỷ lệ ĐẠT có giữ được không trước khi bật.
4. **Lọc trước thẻ khó ra spec:** KHONG_RA_SPEC_PY chiếm 57 % lượt 2. Bỏ qua trước khi gọi LLM các tệp không có hàm vào lệnh (OnTick/OrderSend/strategy.entry) hoặc chỉ là thư viện, chỉ báo.
5. **Nuôi hàng tầng 1 XM liên tục:** khi số việc tầng 1 XM sẵn sàng thấp hơn số slot rỗi, ưu tiên ô ống dẫn chạy Python (sinh_mt5) trước dịch. Không sinh việc Exness trên máy này (hoặc tách hàng riêng) để số đếm hàng phản ánh đúng. Thay hang_mt5 = 200 bằng số việc tầng 1 / tầng 2 của sàn XM.

**Bổ sung 21:20 - metatester mồ côi:** QUA GIO chỉ kill terminal64, metatester64 con (PID 8448, p1) chạy tiếp 4 phút sau đó với 5,98 GB RAM, kéo RAM trống xuống 3,9 GB và chặn mọi việc mới (muc tong=0). Ngoài ra p1 bị phóng việc mới (21:10:31) trong khi metatester cũ vẫn chạy trên cùng thư mục. Đã giết đúng PID và sửa mã (giet_cay). Việc tầng 2 dài nhất đo được tối nay: 944 s, 1158 s, và od_skea0e88e1df54 > 1807 s (quá hạn, chạy lại).

6. **Hạn giờ tầng 2 theo độ dài kỳ và số tick** thay cho 1800 s cố định: việc H1 2,77 năm real tick đã chạy 944-1807 s khi 3 tầng 2 chạy song song. Việc quá hạn bị chạy lại từ đầu, mất thêm 30 phút slot mỗi lần.


## Lần kiểm 21:31-21:45

**Ảnh chụp tài nguyên 21:31:** RAM trống 13,3 / 31,9 GB, CPU 16 % (21:33, su_dung.jsonl), ổ trống C 13,2 GB, D 20,1 GB, E 192,8 GB. muc_mt5: tong 5, tang2 3. Chỉ 3 metatester chạy (p1 5,99 GB, p7 3,90 GB, p3 2,00 GB).

**Hàng MT5:** sổ cái 710 dòng (21:01) lên 728 (21:31), 18 lượt trong 30 phút. Tầng 2 real tick xong từ 21:02 đến 21:32 (số đo trong chay.log): od_skst4ac0c7fd10781af4 net 6.052,01 / 73 lệnh / DD 49,55 % (64 s); od_mql5e52afb999eca4bd1 net 425,41 (1.221 s); od_mql5b5a04d7c15935f8b net 590,17 (1.051 s); od_skea0b8298aa53 GOLD H1 net 3.196,44 / 16 lệnh / PF 41,38 / DD 34,25 % (238 s); od_skea0c762cdb38 CHFJPY H4 net 859,78 / DD 19,87 % (343 s); od_skea135e93ee32 EURUSD H1 net 555,97 / DD 18,53 % (172 s); od_skea45b39eb1d5 AUDJPY H4 net 1.340,19 / DD 46,01 % (584 s); od_tohop564be9bb91406c57 net 546,97 / DD 26,23 % (188 s). UNG_VIEN.md chưa cập nhật từ 21:02 (ĐẠT 33), lần báo cáo kế ~22:02.

**Slot rỗi dù có việc:** p4 và p6 rỗi 21:07-21:42 (35 phút mỗi slot, tổng 70 phút slot) vì hàng tầng 1 XM chính = 0. Cùng lúc hàng box có 38 việc tầng 1 XM (`lay_viec(chi_tang1=True)` thử khô: BRAIN_HANG_BOX=0 → 0 việc, =1 → 38 việc). Đã chạy lại chay_lien_tuc với BRAIN_HANG_BOX=1 lúc 21:42; 21:43 cả 5 slot chạy.

**Việc quá giờ lặp:** od_skea0e88e1df54_XM_CSV (H4, tầng 2) quá 1.800 s hai lần liền (1.807 s lúc 21:10, 1.812 s lúc 21:41), tổng 60 phút slot p1 không ra kết quả; nay chạm SO_LAN_THU_TOI_DA = 2 nên bị bỏ. Lần 2 vẫn để metatester mồ côi (PID 668, 6 GB) vì tiến trình chạy mã trước bản sửa giet_cay. Dòng sổ cái QUA GIO ghi `slot` rỗng, nên không biết được slot nào từ sổ cái.

**Rủi ro git cuối phiên (đã sửa):** `ket_thuc()` của chay_lien_tuc vẫn dùng `pull --rebase --autostash` lúc 07:00 — đúng lỗi đã làm lùi sổ cái lúc 20:53. Đã đổi sang fetch + merge thường; tiến trình mới (PID 15104) dùng bản sửa.

**LLM:** ai-box vẫn hết quota (lượt 21:27: 8 lần gọi, 8 lỗi, 200 thẻ CHUA_CHAY_DUOC, 0 token). 3.765 thẻ chờ dịch. Nguồn việc mới tối nay chỉ còn từ box (dịch tay).

### Đề xuất
1. **Bật BRAIN_HANG_BOX=1 mặc định** trong chay_toi_nay.ps1 cho phiên sau (đã bật tay cho phiên này), vì khi LLM máy nhà dừng thì hàng box là nguồn tầng 1 duy nhất.
2. **Giới hạn tầng 2 theo RAM thật thay vì trần 3:** lúc 21:31 còn 13,3 GB trống với 3 tầng 2 (2,0-6,0 GB mỗi việc), đủ cho việc tầng 2 thứ tư mà vẫn trên sàn 4 GB.
3. **Ghi `slot` vào dòng QUA GIO** và hạ hạn cho việc đã quá giờ một lần (hoặc đẩy xuống cuối hàng) để không mất thêm 30 phút slot cho lần thử thứ hai.
4. **Theo dõi metatester mồ côi** bằng canh_metatester_mo_coi.ps1 cho tới khi mọi tiến trình đều chạy bản có giet_cay.
