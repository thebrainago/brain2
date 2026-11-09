# seeker_unblock (cấp trên cùng) — công cụ Seeker cho máy nhà, bản đã rà soát 10/11/2026

Thư mục con `box/` là của worker khác, bản rà soát này không đụng tới.
Dữ liệu thô và CSV **không nằm trong git**: `/workspace/nguon_khac/home/` trên box, `E:\seeker_tools\out` trên máy nhà.

## Chính sách áp dụng
- Chỉ đọc trang **công khai** hoặc API có tài liệu, bằng `requests` thường với User-Agent trung thực.
- Không giả vân tay trình duyệt, không proxy/DoH để né chặn, không đổi IP.
- Không gọi endpoint nội bộ không có tài liệu.
- Không điều khiển trình duyệt hay phiên đăng nhập từ shell, không sao chép phiên.
- Gặp 403/429/503 hoặc trang chặn của Cloudflare thì **dừng ngay** (`net.SiteBan`), không thử lại.
- Không có mật khẩu, cookie, token hay link riêng trong code.

## Trạng thái hiện tại
- **Myfxbook đang chặn IP nhà** (Cloudflare 1015/429, bắt đầu khoảng 00:00 ngày 10/11 giờ VN).
  Nguyên nhân là bản cũ chạy 6 tiến trình song song (khoảng 2 request/giây). Không thu thập thêm.
- mql5.com: trang signal công khai đọc được từ IP nhà. Lịch sử lệnh cần đăng nhập nên **không hỗ trợ tự động**.

## Tệp và trạng thái
| Tệp | Trạng thái | Ghi chú |
|---|---|---|
| `net.py` | Dùng được | `requests`, nhịp theo host (mặc định 4 s), backoff khi lỗi kết nối, dừng ngay khi bị chặn |
| `mql5.py` | Dùng được (trang công khai) | Thống kê signal `/en/signals/{id}`, nhịp 4 s. Đo 09/11: 60/60, 0 lần bị chặn (khi đó còn dùng TLS giả Chrome; bản `requests` mới chưa chạy thật) |
| `myfxbook_discover.py` | Dùng được khi hết chặn | Trang danh sách công khai `/systems/N`, nhịp 5 s, dừng ngay khi bị chặn |
| `myfxbook.py` | **Chỉ parser offline** | `parse-html FILE` đọc bảng History đã lưu. Lệnh `fetch` thoát mã 2, vì endpoint XHR nội bộ đã bị vô hiệu hoá |
| `mql5_browser.py` | **Vô hiệu hoá** | Thoát mã 2 kèm hướng dẫn: Anh tự bấm Export trên trình duyệt của mình |
| `myfxbook_fix_auto.py`, `myfxbook_fix_offline.py` | Offline | Sửa thứ tự cột của CSV cũ. Cột suy ra kiểu này luôn là **UNVERIFIED** |
| `kiem_dinh_lich_su.py` | Offline | Đối chiếu CSV với HTML thô và meta; chỉ gán VERIFIED khi khớp tiêu đề cột thật |
| `tom_tat_myfxbook.py` | Offline | Tóm tắt mỗi hệ một dòng (chỉ là số mô tả, không phải kết quả cổng) |
| `probe.py`, `dl.py` | Chẩn đoán | 1 request mỗi URL, dừng khi bị chặn |
| `test_offline.py` | Test | 4 test không gọi mạng |

Đã xoá:
- `dpi_proxy.py`, công cụ tách gói ClientHello né chặn SNI của nhà mạng.
- `ech_test.py`.
- `pw_capture.py`, công cụ ghi XHR bằng Playwright.
- `save.py`, công cụ gửi header XHR.
- `myfxbook_fix_cols.py`, công cụ gọi XHR để lấy tiêu đề cột.

## Ghi chép chẩn đoán mạng (chỉ là tài liệu, không dùng để lách chặn của trang)
Đo ngày 09/11 từ IP nhà mạng VN: DNS nhà mạng trả NXDOMAIN cho myfxbook.com/fxblue.com, và kết nối TLS tới myfxbook bị reset
khoảng 7/8 lần bắt tay. Đây là lọc của nhà mạng. Còn lệnh chặn 1015/429 hiện tại là **chặn của chính Myfxbook**,
nên phải tôn trọng: chờ hết hạn, giảm tốc độ, hoặc dùng nguồn chính thức.

## Nguồn hợp lệ để có lịch sử lệnh
- **Myfxbook:** CSV export của trang (đã làm trước đó qua email "CSV File request", Anh tự thao tác) hoặc Myfxbook API chính thức.
- **MQL5:** Anh đăng nhập trên trình duyệt của mình, mở `/en/signals/{id}` rồi bấm Export history.
  Đặt CSV vào thư mục rồi chạy `loc_phi_nhanh.py --lenh`.

## Chạy
```
pip install --user requests beautifulsoup4
python3 test_offline.py
python3 myfxbook.py parse-html <file_history_da_luu>
python3 kiem_dinh_lich_su.py /workspace/nguon_khac/home/raw/mfb /workspace/nguon_khac/home/myfxbook 6426348 9900626 11992558
python3 mql5.py --ids-file ids.txt      (trang công khai, nhịp 4 s)
```
Báo cáo kiểm định: `reports/vong3/HOME_FETCHER_AUDIT_2026-11-10.md`.
