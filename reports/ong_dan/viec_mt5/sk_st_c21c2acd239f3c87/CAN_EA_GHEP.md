# huanghq2000/fx_trading :: StrategyTester-From2502-v3.0.htm

Hệ này đạt lọc Python 65/15 (MÔ PHỎNG, PHÍ TẠM (swap XM:EURUSDMICRO 2026-09-13; spread bang luu EURUSDmicro, gio 23/0 x5)) nhưng chưa có EA MT5 biểu đạt được đúng nó (nguồn lệnh ngoài, bộ lọc hoặc ghép nhiều nguồn). Cần chế độ `BRAIN_XuLiLenh` đọc CSV lệnh / iCustom (bước 7a của bản rà soát, việc của Claude).

Thông số Python tốt nhất:

```json
{
 "ma": "EURUSD",
 "khung": "H1",
 "tham": {},
 "ql": {
  "tp_pct": 0.002,
  "dca_buoc_pct": 0.005,
  "dca_toi_da": 5,
  "dca_he_so_lot": 1.3,
  "hedge_khi_lo_pct": 0.0,
  "lot_tren_1000": 10.0
 }
}
```
