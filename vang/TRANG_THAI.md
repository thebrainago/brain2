# Trạng thái module vàng — để phiên sau chạy tiếp

Cập nhật **2026-11-27 19:57 (giờ Việt Nam, UTC+7)**.

## Đổi hướng (t345u)

**Không tiếp tục** lấy Donchian / EMA / lưới giá thuần làm gốc. Hai giai đoạn đúng:

1. **A — Tín hiệu data** từ Fxaurum GCZ6 (tick, 1m, big trade, sweep/absorption/iceberg) và OptionsDb (khi tìm thấy): delta/footprint, cụm big trade, đảo sweep, vùng absorption, VWAP/profile, wall/GEX/max pain. Quy sang GOLD.i bằng basis từng lúc.
2. **B — Gắn hệ xử lý lệnh** (nhồi / DCA / hedge khóa-gỡ / trailing / TP rổ) lấy từ thiết kế SP500 đêm 27/11.

Chi tiết: `bao_cao/HUONG_DI_DATA_VA_XU_LY_LENH.md`. `sp500/HE_XU_LY_LENH.md` **chưa có** trên git lúc 19:57; tạm dùng `sp500/ma/dca.py` và `sp500/ea/SP500_Dca.mq5`.

## Số vừa đo (MT5 p4, tick thật, rồi dừng hàng đợi)

Cửa sổ 2025.09.01–2026.10.12, vốn 10.000 USD, 100% real ticks. Tiêu chí: lãi ròng > 0 và DD < 80%. Chi tiết `bao_cao/MT5_DOI_CHIEU.md` mục 6.

| EA | Khung | Lãi ròng | CAGR | DD | Lệnh | Thắng | PF | ĐẠT? |
|---|---|---:|---:|---:|---:|---:|---:|---|
| VANG_HedgeEMA (đảo 2 ATR ×1,5, lot 0,08) | H1 | **+13.051,52** | 111,98% | 45,09% | 467 | 70,02% | 1,13 | có |
| VANG_HedgeEMA (cùng họ, lot 0,16) | M15 | **−10.004,64** | vỡ vốn | 100,10% | 1.497 | 66,40% | 0,97 | không |
| VANG_LuoiPhuc (gỡ ×1,3, 2 bậc, lot 0,02) | H1 | **+2.511,40** | 22,33% | 26,93% | 819 | 74,36% | 1,08 | có |
| VANG_LuoiPhuc (nhân lot rổ ×1,5, lot 0,03) | H1 | **+2.837,23** | 25,19% | 47,62% | 823 | 74,36% | 1,05 | có |

Đã dừng hàng đợi (không chạy biến thiên lưới bước/chân/lot, không chạy cửa sổ 2025.10.01 cho EA mới). Python vẫn lệch: hedge H1 lãi gấp ~4,5 lần; hedge M15 Python lãi lớn trong khi tick vỡ vốn; lưới ×1,5 thì Python DD 94,8% (không ĐẠT) còn tick ĐẠT DD 47,62%.

## Data Fxaurum đã có (kéo 19:03–19:04 UTC+7, 0 lỗi)

1.648 nến 1h, 96.960 nến 1m, 191.044 sweep, 193.463 absorption, 6.422 iceberg, 82.175 big trades, gateway còn 6.144.531 tick GCZ6 (chưa xuất file). Basis trung vị +38,96 USD (827 giờ). ORB ± sweep lần trước **không ĐẠT** (PF 0,88 / 0,55). OptionsDb chưa tìm thấy ở tầng trên E:\\ / D:\\ / `C:\\Users\\DUNG`.

## Việc phiên sau

1. `git pull` — đọc `sp500/HE_XU_LY_LENH.md` khi worker SP500 đẩy lên.
2. Giai đoạn A: xuất tick/aggTrades từ gateway (không `syncTicks`/`syncHistory`), dựng delta/footprint, cụm big trade, sweep đảo, absorption, VWAP; tìm OptionsDb; basis từng lúc sang GOLD.i.
3. Giai đoạn B: nối tín hiệu data với engine xử lý lệnh, rồi mới test tick **p4**, một test một lúc.
4. Không đụng g3, p3/p5/p6, terminal XM chính. RAM trống ≥ 6 GB.

## Lệnh resume

```bash
cd /workspace/brain2 && git pull origin main --ff-only
# đọc sp500/HE_XU_LY_LENH.md nếu đã có
ls vang/du_lieu/fxaurum/
```
