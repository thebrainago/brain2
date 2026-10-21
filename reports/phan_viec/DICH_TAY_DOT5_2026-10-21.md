# Grok Bot dịch tay — đợt 5 (21/10/2026)

Dịch bởi `grokbot-tay` (0 lần gọi API trả phí, dich_llm=false). Ưu tiên: EA có tín hiệu vào rõ ràng kèm DCA/hedge/recovery/TP nhỏ, dạng Python.
Bộ sinh: `data/tho_box/dich_tay_grok/viet3.py` (thư mục data/ không commit).

## Số lượng
- EA dịch: 16 → 16 thẻ (Python). Kiểm tra `thu`: 16/16 đạt (ScalpingV3 lúc đầu ra 0 lệnh, đã sửa: so với BB nến trước).
- `ghi`: 16/16 từ cache, goi_moi=0.
- Lọc 65/15 (lot thật): **DAT 5**, TRUOT 11, CHUA_DO_DUOC 0.
- MT5: 10 việc VAO_CSV mới (5 thẻ × XM + Exness).

## Thẻ đạt lọc (số đo trên box, chưa có MT5)
| Thẻ | EA | Mã/Khung | Lãi %/năm | DD % |
|---|---|---|---|---|
| sk_ea_37d18e3ece | ZONE_RECOVERY_AREA_II | EURCAD H1 | 62.568 | 55.933 |
| sk_ea_c67d5d31e9 | Ichimoku EA v1.3 | GBPCAD H4 | 32.967 | 27.058 |
| sk_ea_42415c4f24 | Trickerless_RHMP (gần đúng) | EURGBP H1 | 24.542 | 50.377 |
| sk_ea_94672bd399 | GBPJPY_EA_scalper_n6 (BB 2.5σ) | GBPJPY H4 | 24.110 | 43.377 |
| sk_ea_5056669865 | Zone_Recovery_Formula | GBPCHF H1 | 22.992 | 36.773 |

## Trượt (lãi %/năm, DD %)
AUDNZD H4 ZONE_RECOVERY_AREA 14.258/52.713; GBPNZD H4 HEDG_SYSTEM 14.020/10.620; EURAUD H4 BTC_TrendFusion 13.887/32.855;
GBPCAD H1 Zone_Recovery_Area_V3 13.605/13.798; EURUSD H4 Structured MACD 13.431/36.603; USDCAD H4 MartingalePulse 6.326/34.070;
GBPUSD H1 ScalpingEA_V3 5.666/19.050; CADJPY H1 ViperGrid 5.007/54.690; GBPNZD H4 MFriel 1.614/6.778;
EURAUD H1 XANDER_Gold_Recovery -0.024/23.100; AUDNZD H1 DollarTrader -3.398/9.343.

## Ghi chú
- Ở họ Zone Recovery, nhánh BÁN không bao giờ chạy được (lỗi gắn else); bản dịch giữ đúng như vậy: chỉ MUA. MACD gốc chạy trên MN1, bản dịch dùng MACD trên khung hiện tại (gần đúng).
- MT5: CHƯA ĐO ĐƯỢC (việc đã xếp hàng).
