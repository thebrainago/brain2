# Kho kiến thức thống kê (công khai)

Cập nhật: 2026-11-13 15:44 (Asia/Saigon, UTC+7)

Thư mục này thu **các thống kê đã công bố công khai** từ SentimenTrader, Bespoke, Quantified Strategies, Ryan Detrick (Carson / trước đây LPL), Stock Trader's Almanac, ThePatternSite (Bulkowski), cộng **thống kê MA50 do EVO tự tính**. Mục tiêu: làm tài liệu dùng chung cho các phiên EVO/SEEKER, và lọc ý nào có thể hỗ trợ bias, vùng DCA, vùng tín hiệu trên cặp chéo forex.

## Không phải gì

- Không phải toàn bộ tri thức trả phí của các hãng trên. Phần lớn bảng forward của SentimenTrader, Bespoke, NDR, Almanac nằm sau tường phí — **không đoán số**.
- Không phải kết quả đã vượt kiểm SEEKER. Mọi mục gắn `seeker_test: true` chỉ là **ứng viên cần test**, chưa pass.
- Không có mật khẩu, cookie, token, hay `tai_khoan.json`.
- Không commit chuỗi giá thô (Yahoo). Có thể tải lại ^DJI, ^GSPC, và các mã FX=X.

## Phương pháp

- Nguồn công khai, URL ghi kèm. Trạng thái tải: `http_200` (mở được), `http_200_bot_wall` (URL sống nhưng chặn bot; số liệu từ đoạn được máy tìm kiếm lập chỉ mục), `search_indexed` (tương tự, bài Bespoke).
- QuantifiedStrategies.com trả HTTP 200 nhưng hiện "Bot Verification" khi tải tự động; số QS vì thế phải đối chiếu lại trên trình duyệt trước khi mã hóa chốt.
- Tài khoản X (@sentimentrader, @bespokeinvest, @RyanDetrick, @WillieDelwiche, @MikeZaccardi): lượt này không thu tweet có hệ thống. Đã lấy bài blog/web của cùng tác giả khi có số. Delwiche và Zaccardi: chưa có mục đủ điều kiện — không bịa.
- Ned Davis Research: chưa có trang miễn phí đủ bảng số.

## Cấu trúc

| File | Nội dung |
| --- | --- |
| [items.json](items.json) | Mọi mục, schema thống nhất (rule, thị trường, mẫu, kết quả, URL, vai trò tool, cờ SEEKER) |
| [loc-ho-tro-trading.md](loc-ho-tro-trading.md) | Lọc ứng viên bias / DCA / tín hiệu, cách mã hóa, mức ưu tiên test |
| [ma50/ket_qua.md](ma50/ket_qua.md) | Kết quả tự tính khoảng cách MA50 |
| [ma50/](ma50/) | CSV/JSON số liệu MA50 |
| [nguon/](nguon/) | Ghi chú theo nguồn |

## Số mục

Hiện có **21 mục** trong `items.json`. Ứng viên ưu tiên cao cho bộ hỗ trợ trading (forex crosses): thống kê MA50 do EVO tính trên chính cặp, IBS / mean-reversion kiểu Connors, ý tưởng "kéo quá xa MA50 thì chờ hồi". Các thống kê mùa vụ và breadth cổ phiếu Mỹ chủ yếu chỉ làm bias rất nhẹ, hoặc không dùng.
