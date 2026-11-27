# Trạng thái module vàng — để phiên sau chạy tiếp

Cập nhật **2026-11-27 19:39 (giờ Việt Nam, UTC+7)**.

## Đã xong phiên này

- Tiêu chí mới (t344u): **lãi ròng > 0 và DD < 80%** (bỏ CAGR > 10%). Lọc lại 4.148 tổ hợp: **1.714 ĐẠT** (trước 287). CSV: `ket_qua/quet_4148_dat_tieu_chi_moi.csv`.
- Mở rộng lưới / nhân lot / gỡ lệnh / hedge trên H1, H4, M15, M5: **624** tổ hợp, **273 ĐẠT** tiêu chí mới. M5: **0/156 ĐẠT**, hầu hết vỡ vốn (~−99%). Báo cáo: `bao_cao/QUET_TIN_HIEU.md` mục 8–9.
- Biên dịch và chạy MT5 Strategy Tester **chỉ khe p4**, một test một lúc, tick thật. p3/p5/p6 là junction tới `E:\\brain2_grok\\shared_bases` — không dùng. Đã chép lịch sử nến và tick vào `E:\\mt5_tester\\p4\\Bases` và `p4\\tester\\bases` (không gắn junction).
- Tick thật trên đĩa: **2025.08–2026.11**. Cửa sổ 2015/2018 chưa chạy được (không có tick; `FromDate=2025.08.01` bị `no history data` khi tester cố tải tick thiếu). Cửa sổ tick chạy thành công: **2025.09.01–2026.10.12** và **2025.10.01–2026.10.12**.
- Số đo tick (vốn 10.000 USD, 100% real ticks), chi tiết `bao_cao/MT5_DOI_CHIEU.md`:
  - Donchian 20+EMA 55, 2025.10.01–2026.10.12: **lãi −658,60**, CAGR −6,40%, DD 33,50%, 217 lệnh, PF 0,98 — **không ĐẠT**.
  - Donchian cùng EA, 2025.09.01–2026.10.12: **lãi +1.137,39**, CAGR 10,18%, DD 33,07%, 239 lệnh, PF 1,03 — ĐẠT.
  - Lưới EMA 55 lot 0,08, 2025.10.01–2026.10.12: **lãi +4.856,48**, CAGR 46,89%, DD 55,63%, 757 lệnh, PF 1,04 — ĐẠT.
  - Lưới cùng EA, 2025.09.01–2026.10.12: **lãi +10.045,60**, CAGR 86,94%, DD 48,08%, 819 lệnh, PF 1,08 — ĐẠT.
- Python cùng cửa sổ **lạc quan rõ** (lãi gấp ~5–10 lần, Donchian 12 tháng Python lãi / MT5 lỗ). Không dùng CAGR Python 2014–2026 làm quyết định.
- EA: `vang/ea/VANG_DonchianEMA.mq5`, `vang/ea/VANG_LuoiEMA.mq5`. Runner: `vang/ma/chay_tester_p4.py` (chỉ p4). Báo cáo thô máy nhà: `E:\\brain2_tmp\\vang\\mt5\\`.

## Việc còn lại

1. Chưa có tick 2015–2024: không xác nhận được cửa sổ dài trên Tester trừ khi tải tick đủ (tốn đĩa/mạng, dễ bị `downloading canceled` nếu mất kết nối). Nếu tải, chỉ lưu vào **p4\\Bases** và **p4\\tester\\bases**, không ghi shared_bases.
2. Hedge / gỡ lệnh / lưới M15 mới có số Python, **chưa** viết EA và chưa chạy tick p4. Nên xác nhận trên 2025.09.01–2026.10.12 trước, vì Python đang phóng đại lãi.
3. Order flow GCZ6 (ORB ± sweep) lần trước không ĐẠT — xem `bao_cao/ORDERFLOW.md`.
4. Không đụng g3, g12, p5, p6, terminal `C:\\Program Files\\XM Global MT5`. p5 có thể đang chạy metatester (phiên khác). Giữ RAM trống ≥ 6 GB (thực tế runner chờ ≥ 11 GB trước mỗi test).

## Lệnh resume nhanh

```bash
# box
cd /workspace/brain2 && git pull origin main --ff-only
PYTHONUTF8=1 python3 -m vang.ma.chay_quet_mo_rong
```

```bat
REM máy nhà — chỉ p4, một test một lúc
python -u C:\Users\DUNG\AppData\Local\Temp\chay_tester_p4.py
type E:\brain2_tmp\vang\mt5\chay_tester.log
```
