# ZuluTrade — module box

## Cách vượt nghẽn (hiện trạng)

- Site là **SPA Vue**. Dữ liệu traders/leaders **không** nằm trong HTML.
- API thật qua gateway: `https://www.zulutrade.com/zulutrade-gateway/`
- OAuth: `POST …/auth-server/oauth/token` — mọi `GET …/api/*` trả **401** nếu chưa Bearer.
- Client id/secret nhúng trong bundle SPA công khai — **không** chép vào repo / artifact.
- `api.zulutrade.com` → 502.

## Endpoint đã đo

| URL | Kết quả |
|---|---|
| `/traders`, `/leaders` | 200 HTML shell |
| `zulutrade-gateway/api/*` | **401** unauthorized |
| `auth-server/oauth/token` | 401 không credential user |
| Template `api/providers/performance/topTraders/search` | cần auth |

## Chạy

```bash
python3 /workspace/brain2/seeker_unblock/box/zulutrade/fetch_zulutrade.py --out /workspace/nguon_khac/zulutrade
```

## Mở khóa (máy nhà)

1. Login ZuluTrade.
2. CDP/DevTools bắt XHR ranking + trades.
3. Điền URL (không cookie) vào `ZULU_JSON_ENDPOINTS`.
4. Không commit token/cookie/secret.

## Pacing

`PacedClient` mặc định 0.5s/request.
