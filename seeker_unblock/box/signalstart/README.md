# SignalStart — module box

## Hiện trạng (ĐO 09–10/11/2026)

- Homepage + `/search-signals` = 200 HTML, **không** nhúng system id / trade CSV.
- `/login` = 200 — dữ liệu system nằm sau đăng nhập.
- Không có endpoint CSV công khai kiểu FX Blue `/users/{u}/csv` hay C2 `/strategy/csv/{id}`.

## Chạy

```bash
python3 /workspace/brain2/seeker_unblock/box/signalstart/fetch_signalstart.py
```

## Mở khóa

Login máy nhà → CDP bắt XHR khi xem system → điền endpoint (không cookie/token).
