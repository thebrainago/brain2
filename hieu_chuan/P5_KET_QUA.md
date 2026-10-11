# P5 — Luật LOẠI SỚM nhanh trước MT5 (11/10/2026, giờ VN)

**Nhãn: MÔ PHỎNG so với TESTER MT5. Ước lượng, không phải quy luật 100 %. Không có con số nào là tiền thật.**
Chạy lại: `python3 hieu_chuan/p5_loai_som.py` (đọc `p1_ket_qua.json`, < 1 giây) → `p5_ket_qua.json`.

## Luật (của chủ dự án, 11/10/2026)
Mô phỏng **maxDD > 65 %** HOẶC **lãi mô phỏng < 10 %/năm** → loại sớm, không tốn thời gian MT5.
Trong `vong_thu_nghiem.py` đây CHỈ LÀ NHÃN (`loai_som_nhanh`, in cạnh nhãn 25/09 và P4 cho hệ có rổ lưới/hedge);
cổng GIỮ/BỎ không đổi.

## Đo trên 15 ô MT5 sạch (P1: AUDCAD/NZDCAD H1, 6 tháng 2019)
| động cơ | biến thể | giết ô MT5 lãi | giết ô MT5 lãi ≥ 10 %/năm | lọt ô MT5 lỗ |
|---|---|---|---|---|
| `luoi_duong` (mới) | 120 | 8 (đều là ô 2: MT5 **+9,4 %/năm** < 10 %, đúng ý luật) | **0** | **0** / 96 |
| `luoi.chay` v3 (cũ) | 30 | 0 | 0 | **2** (ô 6: MT5 −10,8 %/năm, mô phỏng +12…+22) |

Kết luận đo được:
1. Với động cơ đường giá, luật lãi < 10 %/năm không giết oan ô MT5 nào đáng giữ theo chính luật đó, và không để lọt ô lỗ.
2. Với động cơ cũ lạc quan (v3), luật vẫn để lọt ô 6 (trái dấu) → nhãn chỉ đáng tin khi số lãi đến từ động cơ đã hiệu
   chuẩn (P1). Rổ EA trong vòng (Breakout5, rổ hedge) chạy `mo_phong.chay_he` → độ lệch so với MT5 **CHƯA ĐO ĐƯỢC**.
3. Ngưỡng **maxDD 65 %: CHƯA ĐO ĐƯỢC** trên MT5 — 15 ô chỉ có DD ≤ 33 %. Mô phỏng mới DD gần tester (ô 5: 32,7 vs 32,6),
   v3 thấp hơn tester ở 13/15 ô → nếu dùng v3, DD 65 % mô phỏng có thể là DD thật cao hơn.
4. Giới hạn: 15 ô, một cửa sổ 6 tháng, 2 mã, không swap. Cần thêm ô MT5 (đặc biệt ô DD 50–90 %) để chốt ngưỡng DD.
