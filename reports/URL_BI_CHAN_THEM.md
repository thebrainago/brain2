# URL bị chặn, phần máy tự gom (tự sinh bởi `python tru/seeker.py url-bi-chan`)

Danh sách chọn tay theo nguồn nằm ở `reports/URL_BI_CHAN.md` (tác vụ Seeker đa nguồn, lưu vào `data/seeker_da_nguon/nhap_tay/<nguồn>/<id>.<đuôi>`). File này bổ sung phần máy tự gom. Cả hai thư mục đều được ống dẫn đọc.

Máy **không** vượt Cloudflare, captcha hay chặn bot, và không dùng Browser MCP hay CDP để lách. Anh mở các trang dưới đây bằng Chrome của mình (đăng nhập nếu cần), rồi lưu vào **thư mục nhập tay** (mặc định `E:\brain2_nhap\`, đổi bằng biến `BRAIN_NHAP_TAY` hoặc `thu_muc_nhap_tay` trong `config/ong_dan.json`). Nhận: `.mq4` `.mq5` `.ex4` `.ex5` `.set` `.htm` `.csv` (xuất lịch sử lệnh) `.pine` `.py` `.zip`:

- EA / chỉ báo: file `.mq4` / `.mq5` (hoặc `.ex4` / `.ex5` nếu chỉ có bản biên dịch), kèm `.set` cùng tên nếu có;
- statement hoặc báo cáo tester: lưu trang `.htm`;
- trang có mã hiển thị trên web: Ctrl+S, chọn "Webpage, HTML only".

Đặt tên file **bắt đầu bằng mã ở cột Mã** (ví dụ `U1a2b3c_ten_ea.mq5`) để danh sách tự đánh dấu ĐÃ NHẬP. Sau đó `python3 ong_dan.py chay` tự đọc, phân loại và đưa vào chuỗi. Trang trả phí đã bị loại (không mua gì).

## 1. Máy bị chặn khi đọc (7)

| Mã | URL | Nguồn | Lý do | Trạng thái |
|---|---|---|---|---|
| - | mql5_signals | nguon_can_trinh_duyet | trang render bang JS - HTML tho khong co link signal nao | chờ mở tay |
| - | reddit | nguon_can_trinh_duyet | 403 voi ca www.reddit.com lan old.reddit.com | chờ mở tay |
| - | myfxbook | nguon_can_trinh_duyet | SSLError khi bat tay | chờ mở tay |
| - | ssrn | nguon_can_trinh_duyet | SSLError khi bat tay | chờ mở tay |
| - | cftc_cot | nguon_can_trinh_duyet | 403 tu publicreporting.cftc.gov | chờ mở tay |
| - | darwinex | nguon_can_trinh_duyet | can dang nhap | chờ mở tay |
| - | fred | nguon_can_trinh_duyet | ConnectionReset - Banker da chuyen sang Yahoo/ECB/WorldBank | chờ mở tay |

## 2. Ứng viên chỉ có URL, cần mở tay để lấy mã / lệnh (0, điểm ưu tiên cao trước)

| Mã | Tên | Nguồn | Loại | Phong cách | URL | Trạng thái |
|---|---|---|---|---|---|---|
