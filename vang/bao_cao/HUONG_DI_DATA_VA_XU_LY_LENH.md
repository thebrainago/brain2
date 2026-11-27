# Hướng đi đúng (t345u): tín hiệu data Fxaurum + hệ xử lý lệnh

Viết lúc **2026-11-27 19:57 (giờ Việt Nam, UTC+7)**. Đây là kế hoạch chuyển hướng, **chưa phải số backtest mới** của lớp tín hiệu data.

## Hai giai đoạn

**A. Tín hiệu từ data (vào/ra lệnh)** — không lấy tín hiệu chính từ Donchian/EMA/lưới giá thuần. Nguồn: Fxaurum GCZ6 đã kéo và (khi tìm thấy) OptionsDb trên máy nhà:

- Tái dựng delta / footprint từ tick GC.
- Cụm big trade (đã có 82.175 lệnh lớn, ngưỡng min 8).
- Đảo chiều sau sweep, vùng absorption, iceberg.
- VWAP / volume profile.
- Mức quyền chọn: wall, GEX, max pain.
- Mọi mức futures quy sang XM GOLD.i bằng **basis từng thời điểm** (đã đo: trung vị GCZ6−GOLD.i = +38,96 USD trên 827 giờ, thay đổi theo tuần; xem `ORDERFLOW.md`). Không dùng basis cố định.

**B. Sau khi có tín hiệu data**, mới gắn hệ xử lý lệnh (hedge / nhồi / DCA / gỡ / trailing / khóa và mở khóa / TP rổ) — lấy thiết kế phiên SP500 đêm 27/11, không lấy Donchian/lưới giá làm gốc.

File `sp500/HE_XU_LY_LENH.md` **chưa có** trên `main` lúc 19:57 UTC+7 (worker SP500 đang soạn). Tạm thời trong repo đã có:

- `sp500/ma/dca.py` — `k_dca`, `k_luoi`, `k_go` (DCA rổ, lưới, gỡ/zone recovery, chốt theo TP rổ, nhân lot).
- `sp500/ea/SP500_Dca.mq5` — bản MT5: hệ 1 DCA rổ (bước ATR, nhân lot, TP quanh giá TB, SL tùy chọn); hệ 2 gỡ lệnh đảo chiều trong vùng ATR, đóng hết khi tổng lãi ≥ TP rổ. Đóng hết cuối phiên Mỹ (không giữ qua đêm) — phần này là của SP500, vàng phải xem lại phiên và swap.

Lần ORB ± sweep trước trên cửa sổ Fxaurum ~3 tháng **không ĐẠT** (PF 0,88 và 0,55). Lần sau: ngưỡng khối lượng, cụm big trade, absorption, VWAP, và basis từng lúc — rồi mới nối engine xử lý lệnh.

## Data đang có (đo khi kéo, 19:03–19:04 UTC+7)

Gateway `ws://127.0.0.1:9001/`. Cửa sổ 2026-08-20 → 2026-11-27. **Không** gọi `syncTicks`/`syncHistory`.

| Mục | Số |
|---|---:|
| Nến 1h GCZ6 | 1.648 |
| Nến 1m | 96.960 |
| Sweep | 191.044 |
| Absorption | 193.463 |
| Iceberg | 6.422 |
| Stop-cascade | 3.394 |
| Big trades | 82.175 |
| Tick GCZ6 *có trong gateway* | 6.144.531 (51 phiên) |

`keo_fxaurum.py` **chưa xuất file tick thô** (chỉ nến, flow, bigTrades). Delta/footprint cần kéo `aggTrades`/tick từ gateway vào file, vẫn không gọi sync. File thô: `E:\brain2_tmp\vang\fxaurum\` và `vang/du_lieu/fxaurum/` (không commit file lớn).

OptionsDb: lúc viết **chưa thấy** thư mục/tên đó ở tầng trên của E:\, D:\, `C:\Users\DUNG`. Cần tìm tiếp trên máy nhà ở phiên sau.

Kho GC khoảng 3 tháng: hợp để kiểm lọc order flow / vào trong ngày, **không đủ** backtest nhiều năm.
