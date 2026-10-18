# Tổ hợp: ma_ban_sma10_tre1_tren_sma30_tre1_va_sma + loc bien dong ATR14 <= 1% + ql tp0.003 dca0.012x8 hs1.0 hedge10.0

Hệ này đạt lọc Python 65/15 (MÔ PHỎNG, PHÍ TẠM (swap XM:EURGBPMICRO 2026-09-13; spread bang luu EURGBPmicro, gio 23/0 x5) | QUY ĐỔI TẠM GBP->USD 1.2700) nhưng chưa có EA MT5 biểu đạt được đúng nó (nguồn lệnh ngoài, bộ lọc hoặc ghép nhiều nguồn). Cần chế độ `BRAIN_XuLiLenh` đọc CSV lệnh / iCustom (bước 7a của bản rà soát, việc của Claude).

Thông số Python tốt nhất:

```json
{
 "ma": "EURGBP",
 "khung": "H1",
 "tham": {},
 "ql": {
  "tp_pct": 0.005,
  "dca_buoc_pct": 0.005,
  "dca_toi_da": 8,
  "dca_he_so_lot": 1.0,
  "hedge_khi_lo_pct": 20.0,
  "lot_tren_1000": 10.0
 }
}
```
