# juanmql__expert-advisors__B03_Stoch_Lento_H4/B03_Stoch_Lento_H4.mq5

Hệ này đạt lọc Python 65/15 (MÔ PHỎNG, PHÍ TẠM (swap XM:EURGBPMICRO 2026-09-13; spread bang luu EURGBPmicro, gio 23/0 x5) | QUY ĐỔI TẠM GBP->USD 1.2700) nhưng tín hiệu không viết được bằng các chế độ vào có sẵn của EA (nguồn lệnh ngoài, bộ lọc hoặc ghép nhiều nguồn). Từ 19/10/2026 hệ chạy MT5 bằng `BRAIN_XuLiLenh` chế độ VAO_CSV: file `*_CSV_vao.csv` (lệnh vào Python xuất, giờ server sàn) + `*_CSV.set` (tham số quản lí theo % giá) trong thư mục này; `doc_mt5` đối chiếu danh sách lệnh MT5 với Python.

Thông số Python tốt nhất:

```json
{
 "ma": "EURGBP",
 "khung": "H4",
 "tham": {},
 "ql": {
  "tp_pct": 0.002,
  "dca_buoc_pct": 0.003,
  "dca_toi_da": 3,
  "dca_he_so_lot": 1.0,
  "hedge_khi_lo_pct": 0.0,
  "lot_tren_1000": 10.0
 }
}
```
