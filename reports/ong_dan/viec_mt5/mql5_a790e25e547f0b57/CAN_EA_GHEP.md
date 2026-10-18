# juanmql__expert-advisors__B04_Bollinger_Reversion_M15/B04_Bollinger_Reversion_M15.mq5

Hệ này đạt lọc Python 65/15 (MÔ PHỎNG, PHÍ TẠM (swap XM:AUDNZDMICRO 2026-09-13; spread bang luu AUDNZD_M1_mq, gio 23/0 x5) | QUY ĐỔI TẠM NZD->USD 0.6000) nhưng chưa có EA MT5 biểu đạt được đúng nó (nguồn lệnh ngoài, bộ lọc hoặc ghép nhiều nguồn). Cần chế độ `BRAIN_XuLiLenh` đọc CSV lệnh / iCustom (bước 7a của bản rà soát, việc của Claude).

Thông số Python tốt nhất:

```json
{
 "ma": "AUDNZD",
 "khung": "H4",
 "tham": {},
 "ql": {
  "tp_pct": 0.003,
  "dca_buoc_pct": 0.003,
  "dca_toi_da": 0,
  "dca_he_so_lot": 1.6,
  "hedge_khi_lo_pct": 0.0,
  "lot_tren_1000": 10.0
 }
}
```
