# Đối chiếu MT5 tick thật vs Python — mặc định vàng 59672872

Xuất: 2026-11-27 21:55 (giờ Việt Nam, UTC+7, Asia/Saigon).

Không đặt lệnh thật. Vốn 10.000 USD = 1.000.000 USC (100 USC = 1 USD). Phần trăm DD không đổi khi chỉ đổi đơn vị.

Mặc định kiểm (commit `59672872`): cụm L0=0,01 K=4, maxL=20, TP=4,00, khe DCA=5,47, khe hedge=21,37, hfrac=1, flcap=0,15, đóng lỗ tổng 30% equity lúc mở rổ, ADX≥30 + slope EMA200 D1 / D1 one-way dừng DCA, cooldown 240 nến M1. **Bộ lọc delta15 không có trên MT5** — cả hai phía dưới đây là **không lọc**, trừ khi ghi rõ.

Slot p4 (`E:\mt5_tester\p4`), symbol XM micro `GOLD.i#`, Strategy Tester mô hình 4 (every tick based on real ticks), gửi 10.000, đòn bẩy testers 1:500 (Python `lev=1000` không dùng trong `may_v2`). Từ 2025.09.01 đến 2026.11.27. Không chạy slot khác dùng chung Bases; không tắt `claude.exe` hay terminal XM chính (PID 5968); chỉ taskkill theo PID do script phóng. Terminal p4 PID 12200 / metatester64 PID 1180, xong tự kết thúc.

## Kết quả MT5 (đo từ báo cáo tester)

Chạy 21:38:15–21:42:33 giờ VN, **257 giây**. Chất lượng lịch sử: **100% real ticks**. 439.543 nến, 109.154.552 tick. Chuyên gia `VANG_TayV2`. XMGlobal-MT5 10 (Build 6231).

| Chỉ số | MT5 |
|---|---:|
| Lãi ròng | **−9.994,02 USD (−999.402 USC)** |
| Lãi gộp | +2.672,50 |
| Lỗ gộp | −12.666,52 |
| DD vốn (equity) tuyệt đối | 9.994,02 |
| DD vốn tối đa | **10.040,01 USD (99,94%)** |
| DD số dư tối đa | 10.145,22 (99,94%) |
| Hệ số lãi | 0,21 |
| Kỳ vọng lệnh | −0,95 |
| Sharpe | −5,00 |
| Recovery factor | −1,00 |
| Số lệnh | 10.557 (21.114 deals) |
| Lệnh thắng | 10.426 (98,76%) |
| Lệnh thua | 131 (1,24%) |
| Mua / bán | 7.618 (thắng 98,99%) / 2.939 (thắng 98,16%) |
| Lãi lớn nhất / lỗ lớn nhất | +41,00 / **−551,51** |
| Lãi TB / lỗ TB | +0,26 / −96,69 |
| Chuỗi lỗ tối đa (số lệnh) | 10 lệnh, −1.659,48 |
| Chuỗi lỗ tối đa (tiền) | **−3.002,19 (9 lệnh)** |

Lần đầu “not enough money”: **2026.02.04 21:30 giờ Athens = 2026-02-05 02:30 giờ VN** (mùa đông, Athens+5), equity 30,42 USD, số dư 30,87. Sau đó tester vẫn chạy đến 27/11, liên tục từ chối vào lệnh; số dư còn **5,98 USD** (10.000 − 9.994,02). Không âm vì broker cắt khi hết ký quỹ.

## Python cùng cửa sổ, không delta15

M1 xuất đọc-only từ terminal XM chính (không `syncTicks`/`syncHistory`): 2025-09-01 01:00–2026-11-27 16:38 Athens (440.482 nến), đổi sang giờ VN rồi cắt. i0=400, bắt đầu mô phỏng 2025-09-01 11:40 giờ VN.

| Chỉ số | Python (M1 thận trọng) | MT5 (tick thật) |
|---|---:|---:|
| Lãi ròng | **−10.012,57 USD (−1.001.257 USC)** | **−9.994,02 USD (−999.402 USC)** |
| DD tối đa | **11.037,41 (110,37%)** | **10.040,01 (99,94%)** |
| Lỗ thả nổi tệ nhất | −3.473,02 | (báo cáo không tách; lỗ lệnh lớn nhất −551,51) |
| Cháy | có, equity −12,57 lúc **2026-02-11 22:03 giờ VN** | gần cháy, còn 5,98; lần đầu hết tiền 05/02 02:30 giờ VN |
| Số cụm vào / TP / DCA / hedge | 2.249 / 6.323 / 2.122 / 569 | 10.557 lệnh (sau khi cháy MT5 vẫn thử vào, bị từ chối — không so được 1-1) |

Tỷ lệ lãi Python/MT5 trên cửa sổ này **không** phải 4–9 lần như các EA trước (Donchian ~9×, lưới ~5,5–10×, hedge H1 ~4,5×). Cả hai **cùng cháy** quanh đầu tháng 2/2026, lãi ròng gần như trùng (−10.012 vs −9.994). Python bi quan hơn một chút ở DD vì cho equity âm; MT5 kẹp còn 5,98.

Đường vốn Python (không lọc, vốn đầu 10.000):

| Tháng | Equity cuối | Equity thấp nhất trong tháng | DD từ đỉnh toàn cục |
|---|---:|---:|---:|
| 2025-09 | 9.037,2 | 8.784,7 | 19,97% (đỉnh 10.976,7) |
| 2025-10 | 9.917,3 | 6.819,6 | 37,87% |
| 2025-11 | 7.515,9 | 7.256,4 | 33,89% |
| 2025-12 | 9.654,3 | 6.891,4 | 37,22% |
| 2026-01 | 1.381,2 | 1.381,2 | **87,47%** (đỉnh 11.024,8) |
| 2026-02…11 | −12,6 | −12,6 | 100,11% |

Lần đầu equity <5.000: 2026-01-29 06:39 giờ VN (4.749,61). <2.000: 2026-01-30 22:02 (1.964,95). <100: 2026-02-10 04:54 (95,79). ≤0: 2026-02-11 22:03.

## Cửa sổ Jun–Nov (để đối chiếu số 11/11 cũ)

Cùng tham số, **không delta15**, M1 Jun–Nov:

- CSV ngắn cũ (đến 26/11): **+16.408,03 USD, DD 31,08%**, lỗ thả nổi −3.256,30, IS +11.414,17 / OOS +4.993,86, spread×2 +9.459,99 / DD 4.499,93.
- CSV dài cắt tới 27/11: **+17.006,94 USD, DD 31,08%**.
- Có lọc delta15 (số đã công bố ở `BAO_CAO_VANG_11.md`): **+15.930,00, DD 31,08%**.

Chưa chạy lại tester MT5 chỉ riêng Jun–Nov: trên cửa sổ 2025.09–2026.11 tài khoản đã cháy từ tháng 2 nên đoạn Jun–Nov của test đó không còn ý nghĩa.

## Khác biệt máy (ghi nhận, không phải lỗi báo cáo)

- MT5 không có delta15.
- MT5 xử lý **mọi tick** (đóng rổ khi lãi tổng >0 trong nến, TP sàn từng lệnh); Python M1 thận trọng: giá bất lợi/DCA/hedge trước, cấm TP trong cùng nến đã thêm DCA/hedge.
- Testers p4 đòn bẩy 1:500; Python khai 1:1000 nhưng `may_v2` không dùng cột này.
- Sau khi cháy, MT5 tiếp tục gửi lệnh và bị “No money”, làm phình số lệnh.

## Kết luận đối chiếu

Mặc định `59672872` **sống 11/11 chỉ trên Jun–Nov 2026 + 7 cửa sổ sập + gap/grind giảm**. Trên cửa sổ tick thật 2025.09–2026.11, không lọc delta15, **cả MT5 lẫn Python đều cháy** (lỗ ~10.000 USD, DD ~100%). Phần 4–9 lần Python thổi phồng lãi **không xuất hiện** ở đây vì không còn lãi để so.

Chi tiết guard hai chiều: `BAO_CAO_VANG_2CHIEU.md`. EA: `vang/ea/VANG_TayV2.mq5`. Runner p4: `vang/ma/chay_tester_tayv2_p4.py`. Số MT5: `ket_qua/vang_tayv2_th9_th11_mt5.json`.
