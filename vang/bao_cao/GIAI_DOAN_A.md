# Giai đoạn A — event-study tín hiệu dữ liệu GCZ6 (vàng XM)

Đo lúc (Asia/Saigon, UTC+7). Giá CFD = GC − basis từng phút (GOLD.i# đổi Europe/Athens → UTC). Vào tại **mở nến 1m kế** sau sự kiện. Chi phí vòng tròn 0,21 giá (20 pts spread M1 + 0,5 trượt mỗi phía). USD quy 1,00 lot (100 USD / 1,00 giá). Tiêu chí: lãi ròng > 0, DD sẽ đo ở giai đoạn B.

- Nến 1m GC: 2026-08-20 08:40:00+00:00 → 2026-11-27 12:01:00+00:00 (96749 nến).
- Basis trung vị toàn cửa sổ: 24.94 (giảm dần ~56 tháng 8 xuống ~0 tháng 11; thay đổi basis 15 phút std 0.36).
- Tick footprint: CHƯA (đang xuất aggTrades, không gọi syncTicks/syncHistory) (0.0 MB).

## Bảng event-study (hit / PF / USD 1 lot)

| Tín hiệu | n | 5 phút | 15 phút | 60 phút |
|---|---:|---|---|---|
| quet_dao_30 | 9322 | 47.5% / 0.87 / -184157 | 48.4% / 0.88 / -267546 | 49.9% / 0.95 / -204324 |
| rule_diem_ge2 | 7794 | 47.8% / 0.91 / -112048 | 49.3% / 0.93 / -134905 | 50.2% / 0.95 / -182884 |
| sw_dao_v5 | 6473 | 49.6% / 1.00 / -2566 | 50.5% / 1.01 / 29520 | 50.3% / 1.03 / 132566 |
| quet_dao_60 | 6435 | 48.4% / 0.91 / -88821 | 49.5% / 0.91 / -136728 | 50.4% / 0.95 / -133946 |
| ab_v8 | 3961 | 49.8% / 1.06 / 46813 | 50.7% / 0.98 / -22405 | 47.9% / 0.90 / -257187 |
| cs_dao | 3394 | 49.5% / 0.95 / -32842 | 49.9% / 0.99 / -8685 | 50.7% / 1.03 / 71110 |
| rule_pf15_tot | 2845 | 49.0% / 0.98 / -9877 | 49.9% / 1.01 / 7555 | 50.7% / 1.04 / 58408 |
| ice_an | 2412 | 46.6% / 0.79 / -113639 | 47.1% / 0.80 / -178511 | 48.1% / 0.88 / -186552 |
| cum20_60s | 1450 | 45.0% / 0.83 / -55286 | 47.0% / 0.96 / -17862 | 49.1% / 0.95 / -40496 |
| cum20_5s | 1162 | 44.1% / 0.80 / -55397 | 46.0% / 0.95 / -20121 | 49.6% / 0.99 / -7531 |
| poc_bat | 1037 | 46.3% / 0.88 / -20461 | 49.9% / 0.90 / -29044 | 49.3% / 1.04 / 16891 |
| vwap_cat | 809 | 46.2% / 0.90 / -13568 | 49.6% / 0.96 / -9232 | 49.7% / 0.99 / -6283 |
| vwap_tu_choi | 721 | 50.1% / 0.98 / -2288 | 50.2% / 1.04 / 8278 | 50.3% / 0.96 / -16314 |
| cum50_60s | 290 | 48.6% / 0.95 / -3311 | 50.3% / 1.10 / 9283 | 49.3% / 1.11 / 17599 |

## Phạm vi từng họ

- Big-trade / quét 1m / VWAP / POC: gần như cả cửa sổ GC (20/08–27/11/2026).
- flowRecs (sweep/absorption/iceberg): chỉ kho local ~18–27/11/2026 (không gọi sync).

## OptionsDb

Tìm thấy tại `E:\GrokWork\FxaurumRithmic\OptionsDb\COMEX.GCZ6` (junction từ `%LOCALAPPDATA%\FxaurumRithmic\OptionsDb`), 9,59 GB, chủ yếu 19–20/11/2026 (bbo.fxop rất lớn; core.fxop vài MB). `optionRecordStatus`: recorder đang tắt, không symbol. `optionHistory` không `expirations` trả rỗng hoặc timeout. Chưa suy ra được tường/GEX/max pain (sẽ đọc lại qua API với expiry sau khi xuất tick xong).

## Quy tắc vào đơn giản

Cộng hướng các tín hiệu trên cùng nến; vào khi |điểm| ≥ 2. Kết quả dòng `rule_diem_ge2` trong bảng.

Chạy trong 6.9 giây.
