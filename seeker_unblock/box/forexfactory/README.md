# Forex Factory Trade Explorer — module box

## Cách vượt Cloudflare

- `urllib` / curl thường → **403**.
- **curl_cffi** `impersonate="chrome"` + DoH `1.1.1.1` → homepage / calendar / tradeexplorer **200**.

## Endpoint đã đo

| URL | Kết quả |
|---|---|
| `/tradeexplorer` | 200 (SPA) |
| `/tradeexplorer/public-by-username?username=` | JSON `{username,user_id,explorers:[]}` |
| `/explorerapi.php?content=graphdata&id=` | JSON; **cần id explorer hợp lệ** (id giả → `invalid request`) |
| content khác | `graphdata`, `tradegraphdata`, `chartedtrade`, `positions` |
| Leaderboard list | chưa có endpoint list công khai (HTML không nhúng id) |

## Chạy

```bash
python3 .../forexfactory/fetch_ff.py --out /workspace/nguon_khac/forexfactory
python3 .../forexfactory/fetch_ff.py --username SomeUser
python3 .../forexfactory/fetch_ff.py --explorer-id 12345
```

## Mở khóa

1. Tìm username FF có Trade Explorer **Public**.
2. `public-by-username` → lấy `explorers[].id`.
3. Gọi `explorerapi.php` với id đó; hoặc CDP bắt XHR khi mở explorer.
4. Không lưu cookie login.

## Pacing

Warm `/tradeexplorer` trước mỗi batch API; ≥0.3s giữa request.
