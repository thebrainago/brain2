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
