# Trạng thái module vàng — để phiên sau chạy tiếp

Cập nhật **2026-11-27 19:15 (giờ Việt Nam, UTC+7)**.

## Đã xong

- Tạo thư mục `vang/` (mã, cấu hình, báo cáo tiếng Việt có dấu), **không đụng** `sp500/`.
- Quét 4148 tổ hợp trên D1, H4, H1, M15, M5. Số ĐẠT (CAGR kép > 10%, DD < 80%, ≥ 20 lệnh): **287** (D1: 0, H4: 93, H1: 192, M15: 1 chỉ mua-giữ, M5: 1 chỉ mua-giữ).
- Báo cáo: `bao_cao/QUET_TIN_HIEU.md`, `bao_cao/GIAI_DOAN.md`. CSV: `ket_qua/quet_*_khong_swap.csv`, `ket_qua/quet_gop_toan_bo_khong_swap.csv`, `ket_qua/quet_top_co_swap_2026-11-27_1900.csv`, `ket_qua/pnl_theo_nam.csv`.
- Tín hiệu fractal: đã sửa lỗi nhìn trước (bản đầu trên D1 không dùng).
- Máy nhà 19:01 UTC+7: RAM trống **26,44 GB / 31,91 GB**, CPU 27%, C còn 3,2 GB, D 15,8 GB, E 56,2 GB. Cổng Fxaurum 9001 **mở**. Khe `E:\mt5_tester\p3` và `p4` **có** terminal và đã đăng nhập `XMGlobal-MT5 10`. `p1` không tồn tại; `p6` có (dành cho worker SP500 — không dùng).
- Đã chép `keo_fxaurum.py` và `kiem_may_nha.py` vào `E:\brain2_tmp\vang\`. Đã kéo xong GCZ6 lúc 19:04 UTC+7 (1.648 nến 1h, 96.960 nến 1m, 191.044 sweep, 193.463 absorption, 6.422 iceberg, 82.175 big trades, 0 lỗi). File thô: `E:\\brain2_tmp\\vang\\fxaurum\\` và `vang/du_lieu/fxaurum/` (không commit file lớn). **Không** gọi `syncTicks`/`syncHistory`.

## Tổ hợp đáng xem lại (số đo, không swap, H1 2014-01-02 → 2026-10-12)

1. `donchian_20` + `ema_trend_55` + `atr_sl20_tp40`: CAGR kép 83,35%, DD 23,87%, 2526 lệnh, thắng 42,00%, PF 1,26. Có swap: 79,20% / 27,05%. CAGR 2018–2026 trên đường vốn liên tục: **17,79%**; 2022–2026: **20,35%**.
2. `donchian_20` + không lọc + cùng quản trị: 83,12% / 25,29%, 2561 lệnh. Có swap: 78,78% / 28,47%.
3. Lưới H1 `ema_trend_55` bước 1,5 ATR, 4 chân, TP 1,2 / SL 5: 24,12% / 19,72%, 8293 lần đóng (mô phỏng nến H1, có thể lạc quan).

Chi tiết và họ không ĐẠT: xem `bao_cao/QUET_TIN_HIEU.md`. CAGR cả mẫu H1 bị kéo mạnh bởi năm 2015–2017; đọc mục tách giai đoạn trước khi kết luận.

## Việc còn lại (làm tiếp khi resume)

1. Order flow lần đầu (ORB London ± lọc sweep 5 phút trên GC 1m, 20/08–27/11/2026) **không ĐẠT** (PF 0,88 và 0,55, lợi nhuận −40,65% và −9,16%). Lần sau: lọc theo ngưỡng khối lượng sweep/absorption/iceberg, phá IB kiểu set C, quy đổi giá CFD bằng basis vừa đo (trung vị GCZ6−GOLD.i = +38,96 USD trên 827 giờ, giảm dần theo tuần — tính lại mỗi lần). Xem `bao_cao/ORDERFLOW.md`.
2. **Xác nhận MT5 tick thật** trên **chỉ p3 và p4** (không p1/p6, không `--song-song`, không đụng terminal `C:\\Program Files\\XM Global MT5`). Giữ RAM trống ≥ 6 GB (đủ điều kiện lúc 19:01). Viết EA/.set cho top Donchian H1, so với số Python.
3. Không đổi cấu hình nguồn điện, không taskkill theo tên, không đụng file chưa commit trong `E:\\brain2_grok`.

## Lệnh resume nhanh

```bash
# box
cd /workspace/brain2 && git pull origin main --ff-only
PYTHONUTF8=1 python3 -m vang.ma.orderflow
```

```bat
REM máy nhà — xem kéo data đã xong chưa
type E:\brain2_tmp\vang\fxaurum\keo.log
```
