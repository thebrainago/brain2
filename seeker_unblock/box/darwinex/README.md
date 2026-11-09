# Darwinex — gỡ nghẽn từ box (series-level)

Không tạo API token / không lưu OAuth. Lệnh từng trade **không** công khai.

## Nghẽn đo được (09/11/2026)

| Endpoint | Kết quả |
|---|---|
| `/invest/{TICKER}` | **200** HTML (return total, annualized) |
| `/api/filters/products/all` | **401** (đổi so với 14/08/2026 từng public) |
| `api.darwinex.com/darwininfo|quotes` | cần Bearer token |
| Redirect loop trang chủ | có thể gặp; dùng thẳng `/invest/TICKER` |

## Cách chạy

```bash
python3 seeker_unblock/box/darwinex/fetch_darwinex.py --limit 12 --out /workspace/nguon_khac/darwinex --pace 0.5
```

Universe mặc định: `reports/darwinex_darwins.json` (snapshot 1000 DARWIN, 14/08/2026).

Output: `{TICKER}.csv` (metric series), `series_gate.json`, HTML gốc `{TICKER}.html`.

## Cổng 0

Chỉ **series-level**: ước CAGR từ return 2y `(1+r)^(1/2)-1`, so DD 2y. **Không** rebuild phí XM từng lệnh.

Muốn quote history đầy đủ → Anh đăng ký Darwinex free + cấp data-API token trên máy nhà (module top-level `seeker_unblock/`, không phải thư mục `box/`).

## ĐO đợt 1 (12 ticker)

Tất cả SERIES_PASS theo ngưỡng CAGR≈>10% & |DD|<80% (số từ snapshot + HTML).
