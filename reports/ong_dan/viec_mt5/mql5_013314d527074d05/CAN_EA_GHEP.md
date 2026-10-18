# shahadatnovel__3SMA-EA-in-mql4__3sma_mq4/3sma.mq4

Hệ này đạt lọc Python 65/15 (MÔ PHỎNG, PHÍ TẠM (swap XM:AUDCADMICRO 2026-09-13; spread bang luu AUDCAD_H1_dai, gio 23/0 x5) | QUY ĐỔI TẠM CAD->USD 0.7300) nhưng chưa có EA MT5 biểu đạt được đúng nó (nguồn lệnh ngoài, bộ lọc hoặc ghép nhiều nguồn). Cần chế độ `BRAIN_XuLiLenh` đọc CSV lệnh / iCustom (bước 7a của bản rà soát, việc của Claude).

Thông số Python tốt nhất:

```json
{
 "ma": "AUDCAD",
 "khung": "H1",
 "tham": {},
 "ql": {
  "tp_pct": 0.003,
  "dca_buoc_pct": 0.008,
  "dca_toi_da": 8,
  "dca_he_so_lot": 1.6,
  "hedge_khi_lo_pct": 0.0,
  "lot_tren_1000": 1.0
 }
}
```
