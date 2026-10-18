# zhihua045-ui__free-mt5-ea-source-code__RSI_SinglePosition/RSI_SinglePosition.mq5

Hệ này đạt lọc Python 65/15 (MÔ PHỎNG, PHÍ TẠM (swap XM:GBPNZDMICRO 2026-09-13; spread bang luu GBPNZDmicro, gio 23/0 x5) | QUY ĐỔI TẠM NZD->USD 0.6000) nhưng tín hiệu không viết được bằng các chế độ vào có sẵn của EA (nguồn lệnh ngoài, bộ lọc hoặc ghép nhiều nguồn). Từ 19/10/2026 hệ chạy MT5 bằng `BRAIN_XuLiLenh` chế độ VAO_CSV: file `*_CSV_vao.csv` (lệnh vào Python xuất, giờ server sàn) + `*_CSV.set` (tham số quản lí theo % giá) trong thư mục này; `doc_mt5` đối chiếu danh sách lệnh MT5 với Python.

Thông số Python tốt nhất:

```json
{
 "ma": "GBPNZD",
 "khung": "H1",
 "tham": {},
 "ql": {
  "tp_pct": 0.005,
  "dca_buoc_pct": 0.008,
  "dca_toi_da": 8,
  "dca_he_so_lot": 1.3,
  "hedge_khi_lo_pct": 10.0,
  "lot_tren_1000": 1.0
 }
}
```
