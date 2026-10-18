# Tổ hợp: ma_ban_gio_tren_14_va_gio_duoi_18_va_rsi + loc gio 07-20 server + DCA deu 0,5% x5, TP 0,2%

Hệ này đạt lọc Python 65/15 (MÔ PHỎNG, PHÍ TẠM (swap XM:EURGBPMICRO 2026-09-13; spread bang luu EURGBPmicro, gio 23/0 x5) | QUY ĐỔI TẠM GBP->USD 1.2700) nhưng chưa có EA MT5 biểu đạt được đúng nó (nguồn lệnh ngoài, bộ lọc hoặc ghép nhiều nguồn). Cần chế độ `BRAIN_XuLiLenh` đọc CSV lệnh / iCustom (bước 7a của bản rà soát, việc của Claude).

Thông số Python tốt nhất:

```json
{
 "ma": "EURGBP",
 "khung": "H4",
 "tham": {},
 "ql": {
  "tp_pct": 0.002,
  "dca_buoc_pct": 0.005,
  "dca_toi_da": 5,
  "dca_he_so_lot": 1.0,
  "hedge_khi_lo_pct": 0.0,
  "lot_tren_1000": 10.0
 }
}
```
