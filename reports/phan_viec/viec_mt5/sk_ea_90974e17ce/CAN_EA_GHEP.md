# victor-algo/channel :: Martingale.mq5

Hệ này đạt lọc Python 65/15 (MÔ PHỎNG, ĐO (XMGlobal-MT5_10) | QUY ĐỔI NZD->USD 0.5670 (đo lúc đo phí)) nhưng tín hiệu không viết được bằng các chế độ vào có sẵn của EA (nguồn lệnh ngoài, bộ lọc hoặc ghép nhiều nguồn). Từ 19/10/2026 hệ chạy MT5 bằng `BRAIN_XuLiLenh` chế độ VAO_CSV: file `*_CSV_vao.csv` (lệnh vào Python xuất, giờ server sàn) + `*_CSV.set` (tham số quản lí theo % giá) trong thư mục này; `doc_mt5` đối chiếu danh sách lệnh MT5 với Python.

Thông số Python tốt nhất:

```json
{
 "ma": "GBPNZD",
 "khung": "H1",
 "tham": {},
 "ql": {
  "tp_pct": 0.00235091,
  "dca_buoc_pct": 0.00111084,
  "dca_toi_da": 50,
  "dca_he_so_lot": 1.0,
  "hedge_khi_lo_pct": 0.0,
  "cat_lo_pct": 0.0,
  "lot_tren_1000": 0.01,
  "luoi_tac_gia": true,
  "dca_lot_tuyen_tinh": true
 }
}
```
