# FX Blue — gỡ nghẽn từ box

Giờ Việt Nam (Asia/Bangkok). Không lưu mật khẩu / cookie / token.

## Nghẽn đo được (09/11/2026)

| URL cũ | Kết quả |
|---|---|
| `fxblue.com/users` (không username) | **404** (site Next.js đổi) |
| `fxblue.com/leaderboard`, `/market` | **404** |
| `fxblue.com/users/{user}/csv` | **200** CSV công khai nếu account public |
| Cùng URL khi private | 200 nhưng body `(Only allowed when logged in)` |
| Cloudflare | **không** chặn box trên CSV/stats (khác Myfxbook) |

## Cách lấy lịch sử từng lệnh

```bash
python3 seeker_unblock/box/fxblue/fetch_fxblue.py liehtw icmarkets-demo --out /workspace/nguon_khac/fxblue --pace 0.5
```

- Endpoint CSV: `https://www.fxblue.com/users/{username}/csv`
- Stats HTML: `https://api.fxblue.com/users/{username}/stats` (có dòng `History N days`)
- RSS chỉ open/recent: `https://www.fxblue.com/users/{username}/rss`

Cột CSV (ĐO): `Type,Ticket,Symbol,Lots,Buy/sell,Open price,Close price,Open time,Close time,...Profit,Swap,Commission`.

Lọc `Type=Closed position`. Bỏ `Close time` bắt đầu `1970` (lệnh còn mở ghi sai).

## Pacing

- Mặc định **0,5 s**/request. Không spam danh bạ — site không còn leaderboard công khai dễ quét.
- Username phải biết trước (search web / Anh gửi / index Seeker).

## Khi cần trình duyệt máy nhà

1. Mở `https://www.fxblue.com/users/{user}/stats` đã login `thebrainalgo` (nếu CSV báo login wall).
2. Bấm export / mở `/csv` trong cùng session.
3. Tài khoản ĐO cần login: `solid_gold_fund` (1323 ngày), `24hourfxsignals`, `steady_compounding`.

## Cổng 0

Sau khi có CSV: `python3 /workspace/quy_trinh_v3/nguon_khac_dot1_loc_phi.py` (parser FX Blue trong script đó).

## ĐO đợt 1 (≥2 năm, CSV public)

| user | năm | n closed | Cổng 0 |
|---|---:|---:|---|
| liehtw | 2,704 | 5961 | REJECT e/c 1,32 (lưới); XAUEUR đơn PASS |
| icmarkets-demo | 3,747 | 19381 | REJECT e/c 1,01 (lưới; dữ liệu cắt 2020) |
| night-hawk | 2,838* | 1745 | REJECT e/c 0,49 (lưới; *cửa sổ lệnh parse được từ 2024) |
| xmglobal | 1,79 | 5697 | REJECT; <2y |
