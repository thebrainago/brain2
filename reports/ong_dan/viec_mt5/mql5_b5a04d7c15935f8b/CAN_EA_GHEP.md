# zhihua045-ui__free-mt5-ea-source-code__RSI_SinglePosition/RSI_SinglePosition.mq5

Hệ này đạt lọc Python 65/15 (MÔ PHỎNG, PHÍ TẠM (swap XM:GBPNZDMICRO 2026-09-13; spread bang luu GBPNZDmicro, gio 23/0 x5) | QUY ĐỔI TẠM NZD->USD 0.6000) nhưng chưa có EA MT5 biểu đạt được đúng nó (nguồn lệnh ngoài, bộ lọc hoặc ghép nhiều nguồn). Cần chế độ `BRAIN_XuLiLenh` đọc CSV lệnh / iCustom (bước 7a của bản rà soát, việc của Claude).

Thông số Python tốt nhất:

```json
{
 "ma": "GBPNZD",
 "khung": "H1",
 "tham": {},
 "ql": {
  "tp_pct": 0.005,
  "dca_buoc_pct": 0.008,
  "dca_toi_da": 8,
  "dca_he_so_lot": 1.3,
  "hedge_khi_lo_pct": 10.0,
  "lot_tren_1000": 1.0
 }
}
```
