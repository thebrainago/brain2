# Order flow Fxaurum GCZ6 và basis GC − CFD

Viết lúc **2026-11-27 19:20 (giờ Việt Nam, UTC+7)**. Chỉ ghi số đã đo. Không gọi `syncTicks`/`syncHistory`.

## Data đã kéo (máy nhà, gateway `ws://127.0.0.1:9001/`)

Kéo lúc 19:03–19:04 UTC+7, 0 lỗi. Lưu `E:\brain2_tmp\vang\fxaurum\` và bản sao `vang/du_lieu/fxaurum/` trên box (file thô không đưa lên git).

| Mục | Số đo |
|---|---:|
| Nến 1 giờ GCZ6 | 1.648 |
| Nến 1 phút | 96.960 |
| flowRecs sweep | 191.044 |
| absorption | 193.463 |
| iceberg | 6.422 |
| stop-cascade | 3.394 |
| bigTrades (min 8) | 82.175 |
| Cửa sổ | 2026-08-20 → 2026-11-27 |

## Basis = GCZ6 − XM GOLD.i (cùng mốc UTC)

GOLD.i đổi từ máy chủ GMT+2 sang UTC (trừ 2 giờ). Khớp 827 nến giờ, 2026-08-20 08:00 UTC → 2026-10-12 15:00 UTC (GOLD.i chỉ có đến 12/10).

| Thống kê | USD |
|---|---:|
| Trung vị | +38,96 |
| Trung bình | +39,95 |
| P10 / P90 | +21,78 / +59,65 |
| Min / Max | −57,05 / +101,74 |

Trung vị theo tuần giảm dần: 23/08 **+61,40**; 30/08 +53,12; 06/09 +46,53; 13/09 +41,43; 20/09 +40,58; 27/09 +34,80; 04/10 +31,14; 11/10 +26,94; 18/10 **+20,51**. Đây là hợp đồng **tháng 12 (GCZ6)** so với CFD, không phải basis tháng gần. Trong cùng một ngày basis cũng dao động mạnh (ví dụ 20/08: +33 đến +90). **Phải tính lại mỗi lần**, không dùng số cố định +8 hay +9.

## Backtest lọc trên cửa sổ ~3 tháng (nến 1 phút GC, phí như M1: spread 20 điểm + trượt, chốt trong ngày, SL 2 ATR / TP 4 ATR, rủi ro 2%)

Cửa sổ mô phỏng: 2026-08-20 08:40 UTC → 2026-11-27 12:01 UTC, **0,271 năm**. CAGR năm hóa trên mẫu này **không ổn định** — ưu tiên số lệnh, lợi nhuận cả đoạn, PF, DD.

| Lọc | Lệnh | Thắng | PF | Lợi nhuận cả đoạn | CAGR năm hóa | DD tối đa | Đạt |
|---|---:|---:|---:|---:|---:|---:|---|
| ORB London 14:00–20:00 VN, không lọc flow | 261 | 32,57% | 0,88 | −40,65% | −85,41% | 57,87% | không |
| Cùng ORB, chỉ vào khi sweep 5 phút cùng chiều | 13 | 23,08% | 0,55 | −9,16% | −29,83% | 18,98% | không |

Cả hai tổ hợp **không ĐẠT** trên cửa sổ data Fxaurum hiện có (PF < 1, lợi nhuận âm sau phí). Số sweep rất lớn (191.044) nên lọc 5 phút vẫn có thể nhiễu; cần xem lại ngưỡng khối lượng khi làm tiếp.

Set C London GC đã nêu trong `thebrain-data/BAN_GIAO_QUY_TRINH_BAO_CAO_XAU.md` (~53 lệnh, ≈ +0,40R) là kết quả backtest cũ trên engine XAU, **không lặp lại** trong lần quét ORB đơn giản này.
