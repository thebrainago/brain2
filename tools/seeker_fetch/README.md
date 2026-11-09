# seeker_fetch — cơ chế vượt chặn nguồn Seeker (chạy trên máy nhà)

Đo ngày 2026-11-09 trên DESKTOP-05PNLGF (IP dân dụng VNPT, Việt Nam). Không chứa mật khẩu, cookie hay hồ sơ trình duyệt.

## Ba lớp chặn đã gặp và cách vượt

| Lớp chặn | Triệu chứng | Cách vượt (đã đo được) |
|---|---|---|
| DNS nhà mạng VNPT | `myfxbook.com`, `fxblue.com` trả NXDOMAIN (requests: ConnectionError, curl: "Could not resolve host") | DNS-over-HTTPS 1.1.1.1: curl_cffi `CurlOpt.DOH_URL`; Edge: phân giải bằng DoH rồi `--host-resolver-rules="MAP host ip"` |
| DPI cắt bắt tay TLS theo SNI | `SSL_ERROR_SYSCALL` / timeout / `ERR_CONNECTION_CLOSED`, khoảng 1/3 lần kết nối qua (đo 2/6 với myfxbook) | Thử lại nhiều lần với kết nối mới (10 lần, timeout 15s); khi đã nối thì giữ phiên keep-alive. HTTP/3 (QUIC) không qua (0/6) |
| Cloudflare managed challenge (myfxbook XHR) | Playwright headless/headed tự khởi chạy: kẹt "Just a moment..." cả trên trang JSON | Mở **Edge thật** bằng `--remote-debugging-port` + hồ sơ riêng, rồi `playwright.connect_over_cdp` (navigator.webdriver=false): challenge tự qua, có `cf_clearance` |
| Rate limit | myfxbook 429 sau ~200 trang liên tiếp; mql5 403 tạm thời khi dò dồn dập | Giãn cách `SF_GAP` + lùi 20/40/60s khi 429/403 |
| Đăng nhập | MQL5 `/export/history` → 302 `auth_login`; tab Trading history: "To see trades in realtime, please log in" | Hồ sơ Edge riêng `profiles/mql5`, đăng nhập một lần (xem dưới) |

## Cài đặt (máy nhà, PowerShell)
```
cd E:\seeker_fetch
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install requests curl_cffi playwright
# dùng Edge có sẵn (channel msedge), không cần playwright install
```

## Công cụ
- `sf_fetch.py probe urls_probe.txt req,curl,pw,pwh` — dò mọi URL bằng 4 cách, ghi `out/probe.json`.
  `sf_fetch.py get URL OUT [--method curl|req|pw|pwh] [--profile DIR]` — tải 1 trang (giãn cách theo host, lùi khi 429/1015).
  Env: `SF_CHANNEL=msedge`, `SF_MIN_GAP` (4s), `SF_CONN_TRIES` (10), `SF_DOH`.
- `sf_myfxbook_history.py OID [OID...]` — tải **toàn bộ lịch sử lệnh công khai** của hệ Myfxbook, không cần đăng nhập hay captcha:
  `POST /systemPageGetHistoryFirstPage.json` (`invitation=&accountOid=OID`), rồi `GET /paging.html?pt=4&p=N&...` (20 lệnh/trang, tham số lấy từ nút phân trang).
  Kết quả `out/myfxbook/{OID}.csv` + trang thô `out/myfxbook/raw_{OID}/`. Cột lấy theo tiêu đề bảng (mỗi tài khoản khác nhau: có thể `lots` hoặc `sl,tp`).
  Edge CDP cổng 9333, hồ sơ `profiles/mfb_cdp`, PID ghi ở `out/edge_cdp.pid`.
- `sf_mql5_export.py ids.txt [N]` — xuất `/en/signals/{ID}/export/history` qua Edge CDP cổng 9334, hồ sơ `profiles/mql5`.
  Nếu chưa đăng nhập: thoát mã 2 với `NEED_LOGIN`. Đăng nhập một lần bằng một trong hai cách:
  1. `SF_LOGIN_WAIT=600`: script mở trang đăng nhập, người/agent desktop gõ tay, phiên được giữ trong `profiles/mql5`.
  2. `SF_MQL5_USER` / `SF_MQL5_PASS` đặt **chỉ trong tiến trình đó** (lấy từ vault, mục mql5.com), script điền `#Login`, `#Password`, bấm `#loginSubmit`. Không ghi ra file.
- `sf_sniff.py URL [chữ-để-bấm ...]` — mở trang bằng Edge thật (cổng 9335) và liệt kê mọi XHR/fetch (status, kích thước, URL), để tìm endpoint dữ liệu của nguồn mới. `SF_EXTRA_HOSTS` thêm host cần map DoH.

## An toàn
- Chỉ dừng tiến trình theo PID ghi trong `out/edge_*.pid` (`taskkill /PID <pid>`); không đụng claude.exe hay terminal XM.
- `profiles/` và `out/` chứa phiên/cookie: **không bao giờ** đưa lên git.
- Không đụng `E:\brain2_grok`.
