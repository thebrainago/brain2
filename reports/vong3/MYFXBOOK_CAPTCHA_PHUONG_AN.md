# Myfxbook captcha / Cloudflare — phương án vận hành

Giờ VN. Cập nhật 09/11/2026.

## Hiện trạng ĐO
- `myfxbook.com/systems` và `/api` từ IP box: **HTTP 403** (Cloudflare).
- Export lịch sử cần session trình duyệt; CSV **3534905** đã lấy được trước đó → Cổng 0 REJECT (`MYFXBOOK_3534905_LOC_PHI.md`).

## Tự động được tới đâu
1. **Browser subagent (box hoặc CDP máy nhà)** mở trang export → **tự thử** captcha checkbox / press-and-hold (skill sign-in).
2. Nếu fail → **request_box_help** một lần (Anh thao tác). Không hỏi lại trong chat OTP/captcha text.
3. **Không** bypass CF bằng scrapers không session; không mua giải captcha ngoài.

## Ưu tiên hạ tầng
- Ưu tiên **Chrome CDP máy nhà** profile nguồn theo dõi (đã ghi SEEKER) — IP nhà ít dính CF hơn box.
- Giữ cookie session sau khi Anh giải 1 lần để bot export các hệ trong `myfxbook/systems.txt`.

## Khi Anh online
1. Chạy export lần lượt URL trong `/workspace/myfxbook/systems.txt`.
2. Captcha hiện → handoff; xong bot tiếp tục tải CSV → Cổng 0.
