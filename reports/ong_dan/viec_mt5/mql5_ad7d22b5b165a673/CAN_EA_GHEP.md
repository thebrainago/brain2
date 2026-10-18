# smizxe__mt5-agent-toolkit__src_Experts_RsiLevel/RsiLevel.mq5

Hệ này đạt lọc Python 65/15 (MÔ PHỎNG, PHÍ TẠM (swap XM:GBPUSDMICRO 2026-09-13; spread bang luu GBPUSDmicro, gio 23/0 x5)) nhưng chưa có EA MT5 biểu đạt được đúng nó (nguồn lệnh ngoài, bộ lọc hoặc ghép nhiều nguồn). Cần chế độ `BRAIN_XuLiLenh` đọc CSV lệnh / iCustom (bước 7a của bản rà soát, việc của Claude).

Thông số Python tốt nhất:

```json
{
 "ma": "GBPUSD",
 "khung": "H4",
 "tham": {},
 "ql": {
  "tp_pct": 0.003,
  "dca_buoc_pct": 0.005,
  "dca_toi_da": 3,
  "dca_he_so_lot": 1.0,
  "hedge_khi_lo_pct": 20.0,
  "lot_tren_1000": 3.0
 }
}
```
