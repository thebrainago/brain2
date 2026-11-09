# seeker_unblock/box — fetchers chạy trên box (không ghi đè top-level máy nhà)

Mỗi thư mục = một nguồn. Có `fetch_*.py` + README tiếng Việt (endpoint, nghẽn/gỡ, pacing, cách chạy).

| Module | Box fetch trade CSV? | Ghi chú ĐO 09–10/11/2026 |
|---|---|---|
| `fxblue/` | **Có** | `/users/{u}/csv` public |
| `collective2/` | **Có** | `/strategy/csv/{id}` |
| `darwinex/` | Series only | filters API 401; HTML `/invest/{T}` |
| `zulutrade/` | Chưa (401) | gateway + OAuth; cần CDP |
| `forexfactory/` | Một phần | curl_cffi bypass CF; cần explorer id |
| `signalstart/` | Chưa | login wall |
| `common/` | — | `http_box.py`, `http_cf.py` |

**Không** lưu password/cookie/token. Worker máy nhà dùng `/workspace/brain2/seeker_unblock/*.py` (top-level) — không ghi đè.
