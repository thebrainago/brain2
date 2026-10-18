# diayuunr__ea-optimization-project__EA05_MACD_Momentum_EA05_MACD_Momentum/EA05_MACD_Momentum.mq5

Hệ này đạt lọc Python 65/15 (MÔ PHỎNG, PHÍ TẠM (swap XM:EURCHFMICRO 2026-09-13; spread bang luu EURCHFmicro, gio 23/0 x5) | QUY ĐỔI TẠM CHF->USD 1.1200) nhưng chưa có EA MT5 biểu đạt được đúng nó (nguồn lệnh ngoài, bộ lọc hoặc ghép nhiều nguồn). Cần chế độ `BRAIN_XuLiLenh` đọc CSV lệnh / iCustom (bước 7a của bản rà soát, việc của Claude).

Thông số Python tốt nhất:

```json
{
 "ma": "EURCHF",
 "khung": "H4",
 "tham": {},
 "ql": {
  "tp_pct": 0.005,
  "dca_buoc_pct": 0.008,
  "dca_toi_da": 8,
  "dca_he_so_lot": 1.0,
  "hedge_khi_lo_pct": 0.0,
  "lot_tren_1000": 3.0
 }
}
```
