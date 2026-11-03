# Seeker qua mạng máy nhà — 2026-11-03 (UTC+7)

## Cách chạy
- Máy nhà Windows (92c57ab1…), python `requests` phóng bằng `Start-Process`, ưu tiên **BelowNormal**; kiểm thêm bằng `curl.exe` (DNS hệ thống và DoH 1.1.1.1). Không proxy/VPN, không vượt captcha/anti-bot.
- Không đụng terminal64/metatester64/claude.exe/Riot; tiến trình mình phóng tự kết thúc, không cần taskkill.

## Kết quả truy cập
| Trang | Kết quả từ máy nhà |
|---|---|
| Myfxbook | Chặn mạng: DNS ISP không phân giải; DoH → TLS reset |
| Forex Factory | Chặn mạng: như Myfxbook |
| forex-station | Chặn mạng: có IP (Cloudflare) nhưng TLS reset |
| LiteFinance | Chặn mạng: TLS reset |
| Exness social trading | Không phân giải tên miền (kể cả DoH) |
| exness.com (trang chính) | 200 OK nhưng chỉ là trang tiếp thị, không có dữ liệu hệ |

Mạng máy nhà (ISP VN) chặn các trang này ở tầng DNS/SNI, còn nặng hơn box. Theo quy tắc không vượt chặn → ghi lại và bỏ.

## Ứng viên
- Ứng viên tìm được: **0**. Vào hàng đợi `hang_doi/can_test`: **0** (không có lịch sử thật nào được đọc nên không thêm làn A hay làn B).

## Ảnh hưởng tới thợ MT5
- CPU tổng: trước **16,3%**, sau **16,1%** (trung bình 3 mẫu × 2 giây). 6 tiến trình terminal64/metatester64 vẫn chạy. Không làm chậm.
- Kết luận: máy nhà chạy được Seeker song song với 3 luồng MT5 (rất nhẹ), nhưng mạng nhà không mở được các trang mục tiêu.

## Đề xuất
- Dùng nguồn mở được: MQL5 Code Base/Signals (đã có trong `web.yaml`), trang Myfxbook mà người dùng tự mở bằng trình duyệt có VPN do chính họ bật rồi xuất statement vào `data/`.
- Chi tiết đo: `seeker/nguon/may_nha_truy_cap.yaml`; HTML thô (nếu có) ở `data/seeker_may_nha/` trên máy nhà (gitignore).
