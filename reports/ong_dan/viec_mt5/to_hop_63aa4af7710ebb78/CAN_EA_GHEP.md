# Tổ hợp: ma_mua_close_tren_tuyen_tinh_va_gio_bang + loc bien dong ATR14 <= 1% + khoa khi lo 10% so du, mo khoa 0,5%, go 

Hệ này đạt lọc Python 65/15 (MÔ PHỎNG, ĐO (XMGlobal-MT5_10)) nhưng tín hiệu không viết được bằng các chế độ vào có sẵn của EA (nguồn lệnh ngoài, bộ lọc hoặc ghép nhiều nguồn). Từ 19/10/2026 hệ chạy MT5 bằng `BRAIN_XuLiLenh` chế độ VAO_CSV: file `*_CSV_vao.csv` (lệnh vào Python xuất, giờ server sàn) + `*_CSV.set` (tham số quản lí theo % giá) trong thư mục này; `doc_mt5` đối chiếu danh sách lệnh MT5 với Python.

Thông số Python tốt nhất:

```json
{
 "ma": "EURCAD",
 "khung": "H4",
 "tham": {},
 "ql": {
  "tp_pct": 0.003,
  "dca_buoc_pct": 0.005,
  "dca_toi_da": 3,
  "dca_he_so_lot": 1.0,
  "hedge_khi_lo_pct": 10.0,
  "lot_tren_1000": 1.0
 }
}
```
