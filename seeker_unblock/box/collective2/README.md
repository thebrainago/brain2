# Collective2 — gỡ nghẽn từ box

Không lưu API key / cookie.

## Nghẽn đo được (09/11/2026)

| Endpoint | Kết quả |
|---|---|
| `collective2.com/strategy/csv/{id}` | **200** CSV lệnh đóng (công khai) |
| `collective2.com/details/{id}` | **200** HTML + `csvUrl` trong JSON nhúng |
| `collective2.com/forex-systems`, `/leaderboard` | **200** nhưng danh sách chủ yếu render JS; vẫn bắt được một phần `strategyId` |
| `api.collective2.com` / GetStrategyHistoricalClosedTrades | **404** hoặc **Offline for Maintenance** |
| `trade.collective2.com` | Homepage mockup tĩnh — bỏ |

## Cách chạy

```bash
# khám phá ID rồi tải (lọc forex ≥2 năm)
python3 seeker_unblock/box/collective2/fetch_c2.py --fx-only --min-years 2 --out /workspace/nguon_khac/collective2 --pace 0.4

# tải đúng ID
python3 seeker_unblock/box/collective2/fetch_c2.py 134962085 --out /workspace/nguon_khac/collective2
```

Cột CSV (ĐO): `Open Time ET,Side,Qty Open,Symbol,Avg Price Open,Qty Closed,Closed Time ET,Avg Price Closed,Trade P/L,...`.

Forex dùng `EUR/USD` (có `/`). Cổ phiếu/futures (`TQQQ`, `@MNQZ6`) → bỏ trước Cổng 0 XM.

## Pacing

0,3–0,5 s/request. Leaderboard ~30–40 ID mỗi lần quét HTML.

## ĐO đợt 1

| ID | Tên | năm | fx% | Cổng 0 |
|---|---|---:|---:|---|
| 134962085 | FOREX VIX-3 | 5,592 | 98% | REJECT net_E≤0; e/c 0,97 |
| 122467834 | Tendency Forex | 2,597 | 100% | REJECT e/c 0,44 |
| 94987184 | Just Forex Trades | 10,185 | 100% | REJECT net_E≤0 |
| 140118626 | ECFXBB | 3,252 | 100% | REJECT e/c 0,40 |
| 128801236 | MULTI FX PURE | 5,309 | 98% | REJECT net_E≤0 |
| 128454494 | Deep in the money | 5,229 | 100% | REJECT CAGR/DD (n=14) |

Nhiều hệ ≥2 năm trên C2 là cổ phiếu/futures — không đưa vào Cổng 0 phí XM FX.
