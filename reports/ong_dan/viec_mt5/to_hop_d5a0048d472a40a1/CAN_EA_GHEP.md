# Tổ hợp: ma_ban_ema21_duoi_ema50_va_ema50_duoi_em + ql tp0.003 dca0.003x5 hs1.0 hedge0.0

Hệ này đạt lọc Python 65/15 (MÔ PHỎNG, PHÍ TẠM (swap XM:NZDUSDMICRO 2026-09-13; spread bang luu NZDUSDmicro, gio 23/0 x5)) nhưng chưa có EA MT5 biểu đạt được đúng nó (nguồn lệnh ngoài, bộ lọc hoặc ghép nhiều nguồn). Cần chế độ `BRAIN_XuLiLenh` đọc CSV lệnh / iCustom (bước 7a của bản rà soát, việc của Claude).

Thông số Python tốt nhất:

```json
{
 "ma": "NZDUSD",
 "khung": "H1",
 "tham": {},
 "ql": {
  "tp_pct": 0.003,
  "dca_buoc_pct": 0.003,
  "dca_toi_da": 5,
  "dca_he_so_lot": 1.0,
  "hedge_khi_lo_pct": 0.0,
  "lot_tren_1000": 3.0
 }
}
```
