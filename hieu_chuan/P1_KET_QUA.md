# P1 — Mô phỏng lưới brain2 so với 15 ô MT5 tester sạch (10/10/2026 khuya, giờ VN)

**Nhãn: MÔ PHỎNG so với TESTER MT5. Không có con số nào ở đây là tiền thật.**
Chạy lại: `python hieu_chuan/p1_gia_histdata.py <thư mục zip HistData> /workspace/du_lieu_fx`
rồi `python hieu_chuan/p1_chay.py` (~2,5 phút, một nhân) → `hieu_chuan/p1_ket_qua.json`.

## Đáp án và dữ liệu
- Đáp án: `hieu_chuan/p1_15o_tester.csv` = 15 ô H1 chất lượng lịch sử 100 % từ gói bàn giao the-brain
  (`du_lieu/hieu_chuan_125_o.csv`, commit 3c98274): AUDCAD 8 + NZDCAD 7, 2019.03.01 → 2019.08.31 (184 ngày),
  Model 0, vốn 10.000 USD, đòn bẩy 100, tester ghi swap = 0. Lãi/năm tester GỒM lãi/lỗ treo cuối cửa sổ, quy năm
  ngày/365,25. Chỉ số tự suy ra — không giá, không lệnh thô, không tên bot.
- Giá: **HistData.com M1 BID** (công khai, 0 đồng; gói pip `histdata`), giờ EST cố định (UTC−5) → đổi sang
  Europe/Helsinki (UTC+2/+3, giờ máy chủ kiểu XM) → gộp H1. Tải TRỰC TIẾP cặp chéo (không ghép từ cặp USD).
  Dukascopy (`tai_dukascopy_h1.py`) hôm nay hết thời gian kết nối TLS từ máy này (đang có 2 việc tải dài khác) →
  bỏ, ghi lại. Giá tester là của XM → so HÌNH DẠNG / độ lệch, không so từng nến.
- Tiền: lãi tính bằng CAD, đổi sang USD theo USDCAD (HistData) TẠI TỪNG NẾN.
- Spread: dữ liệu công khai không có → chạy 1,5 và 2,5 pip (GIẢ ĐỊNH), báo cả hai.
- Swap TẮT ở mọi mô phỏng (cùng thước với tester).

## Hai mô phỏng được đo
- **v3** = `nhan/luoi.chay` NGUYÊN TRẠNG (mỗi nến: thêm tầng ở LOW → chốt cặp tia ở HIGH → TP; lot không làm tròn).
- **đường giá** = `nhan/luoi_duong.chay_duong` (mới): luật EA lưới đầy đủ của the-brain (`ea_LuoiDayDu.mq5`, chỉ đọc
  ý): khớp tại NGƯỠNG, spread một lần mỗi lệnh, lot làm tròn 0,01 như MT5, 4 thứ tự giá trong nến
  (gần-open = `mo_phong._duong_bar`, thấp trước, cao trước, theo màu nến); thêm một lần chạy trên đường **M1**.

## Bảng 15 ô (lãi %/năm · maxDD % · số lệnh; chênh = mô phỏng − tester, điểm %/năm)
| o | ma | che_do | buoc/tp/tang | lot (he) | tia | tester lai·DD·lenh | the-brain v3 | brain2 v3 (1.5/2.5) | chenh v3 | duong min..max | chenh duong | khoang thu tu | DD v3 / duong(gan_open,1.5) / M1 | lenh v3 / duong / M1 | chenh M1 |
| 1 | AUDCAD | hai_chieu | 45/13/7 | 0.02 (0.4) | co | -2.3·2.1·162 | +0.1 | +0.1/-0.3 | +2.0..+2.4 | -2.7..-2.1 | -0.3..+0.2 | 0.1 | 0.4 / 2.1 / 2.0 | 133 / 168 / 171 | -0.3..0.1 |
| 2 | AUDCAD | ban | 20/13/8 | 0.08 (0.5) | co | +9.4·3.7·143 | +12.5 | +12.0/+10.5 | +1.1..+2.6 | +8.1..+9.7 | -1.3..+0.3 | 0.5 | 3.3 / 3.7 / 3.7 | 139 / 147 / 142 | -1.4..-0.3 |
| 3 | AUDCAD | mua | 20/34/6 | 0.02 (0.4) | - | -3.7·3.5·46 | -1.8 | -2.0/-2.1 | +1.6..+1.7 | -4.1..-3.8 | -0.4..-0.2 | 0.1 | 1.8 / 3.6 / 3.6 | 27 / 41 / 41 | -0.4..-0.3 |
| 4 | AUDCAD | hai_chieu | 12/45/6 | 0.04 (0.25) | - | -0.1·0.6·84 | -0.1 | -0.1/-0.2 | -0.1..+0.0 | -0.5..+0.5 | -0.4..+0.6 | 0.7 (phan giai kem) | 0.3 / 0.6 / 0.6 | 73 / 84 / 84 | -0.4..-0.1 |
| 5 | AUDCAD | mua | 60/8/5 | 0.5 (0.25) | - | -43.4·32.6·50 | -41.1 | -41.5/-44.7 | -1.3..+1.9 | -46.2..-43.0 | -2.8..+0.4 | 0.0 | 31.7 / 32.7 / 32.7 | 52 / 50 / 50 | -2.8..0.4 |
| 6 | AUDCAD | hai_chieu | 20/20/6 | 0.5 (0.15) | co | -10.8·7.4·137 | +26.2 | +22.0/+12.0 | +22.9..+32.8 | -13.4..-6.5 | -2.6..+4.3 | 0.8 | 7.6 / 4.3 / 4.3 | 173 / 158 / 158 | -2.6..3.5 |
| 7 | AUDCAD | hai_chieu | 80/10/6 | 0.5 (0.25) | - | -9.5·6.5·111 | -9.2 | -7.7/-14.6 | -5.1..+1.8 | -19.0..-12.3 | -9.5..-2.8 | 0.0 | 9.0 / 7.9 / 7.9 | 108 / 105 / 105 | -9.5..-2.8 |
| 8 | AUDCAD | ban | 20/45/6 | 0.15 (0.25) | co | +10.9·4.8·73 | +14.0 | +13.4/+12.1 | +1.2..+2.4 | +10.8..+12.8 | -0.2..+1.8 | 1.3 | 4.0 / 4.7 / 4.7 | 70 / 78 / 74 | -0.2..0.6 |
| 9 | NZDCAD | hai_chieu | 80/34/8 | 0.02 (0.5) | - | -3.8·2.4·64 | -1.1 | -0.6/-0.8 | +3.0..+3.1 | -4.0..-3.8 | -0.2..-0.0 | 0.0 | 0.5 / 2.3 / 2.3 | 60 / 67 / 67 | -0.2..-0.0 |
| 10 | NZDCAD | mua | 45/16/6 | 0.02 (0.5) | - | -7.2·4.4·35 | -4.1 | -3.8/-3.9 | +3.3..+3.4 | -7.1..-6.7 | +0.0..+0.5 | 0.4 | 2.5 / 4.4 / 4.4 | 34 / 35 / 35 | 0.0..0.1 |
| 11 | NZDCAD | hai_chieu | 20/10/7 | 0.04 (0.4) | co | -5.6·3.0·352 | +2.8 | +5.1/+3.0 | +8.5..+10.7 | -5.3..-1.8 | +0.3..+3.7 | 1.8 | 1.6 / 2.1 / 1.9 | 358 / 369 / 373 | 0.5..2.1 |
| 12 | NZDCAD | hai_chieu | 20/8/5 | 0.08 (0.15) | - | -5.4·2.8·244 | -4.0 | -2.0/-3.7 | +1.6..+3.3 | -5.0..-2.6 | +0.3..+2.8 | 0.4 | 1.5 / 1.6 / 1.6 | 231 / 262 / 265 | 0.4..2.5 |
| 13 | NZDCAD | mua | 80/6/6 | 0.3 (0.15) | - | -41.4·25.3·55 | -38.3 | -35.5/-38.0 | +3.5..+5.9 | -40.8..-38.4 | +0.7..+3.1 | 0.0 | 23.2 / 24.9 / 24.9 | 60 / 59 / 59 | 0.7..3.1 |
| 14 | NZDCAD | hai_chieu | 45/13/6 | 0.15 (0.4) | - | -8.6·4.7·145 | -8.6 | -4.6/-7.1 | +1.5..+4.0 | -8.2..-4.0 | +0.4..+4.6 | 1.7 | 3.8 / 3.3 / 3.1 | 145 / 145 / 147 | 0.7..3.2 |
| 15 | NZDCAD | ban | 12/13/7 | 0.3 (0.25) | - | +29.5·10.6·158 | +28.3 | +31.8/+28.8 | -0.7..+2.3 | +30.9..+35.6 | +1.4..+6.1 | 1.5 (phan giai kem) | 9.5 / 10.6 / 10.6 | 163 / 166 / 170 | 2.1..5.4 |
{

(“khoảng thứ tự” = chênh lớn nhất giữa 4 thứ tự giá trong nến cùng spread; > 5 điểm thì ghi CHƯA ĐO ĐƯỢC — không ô nào
vượt. “phân giải kém” = bước < 2 × biên độ nến H1 trung vị (~9 pip).)

## Kết luận đo được
1. **`luoi.chay` (v3) LẠC QUAN — đúng như the-brain đã thấy.** Lạc quan ở 11/15 ô (cận dưới chênh > 0).
   - Có tia lệnh (5 ô): **+1,1 … +32,8** điểm %/năm. Tệ nhất ô 6 (AUDCAD hai chiều 20/20, lot 0,5): tester **−10,8 %/năm**,
     v3 **+12…+22 %/năm** (lỗ thật thành lãi trong mô phỏng). Ô 11: tester −5,6, v3 +3…+5. Nguyên nhân: cặp tia chốt
     ở CỰC TRỊ nến chứ không ở giá ngưỡng (kiểm bằng `luoi_duong`: chốt tại ngưỡng → ô 6 về −6,5…−13,4).
   - Không tia (10 ô): −5,1 … +5,9, trung vị **+2,0**. Nguyên nhân chính: lot `nhan` hệ số < 1 không làm tròn
     (0,02×0,4² = 0,0032 lot, MT5 đặt 0,01) — bật làm tròn thì ô 9/10/3 về khớp (vd ô 10: −3,8 → −7,1, tester −7,2).
   - maxDD của v3 THẤP hơn tester ở 13/15 ô (vd ô 1: 0,4 % vs 2,1 %; ô 9: 0,5 % vs 2,4 %).
   - Hạng Spearman v3 ↔ tester **0,70** (y hệt engine v3 của the-brain: 0,70 — xác nhận phép đo nhất quán).
2. **Động cơ đường giá (`luoi_duong`) khớp tốt hơn nhiều:** chênh có tia **−2,6 … +4,3**, không tia **−9,5 … +6,1**
   (trung vị ≈ +0,2); cả 15/15 ô có chênh chạm vùng ±3 điểm ở ít nhất một spread; hạng Spearman **0,96**; maxDD và số lệnh
   gần tester (ô 5: 32,7 % vs 32,6 %; ô 15: 10,6 % vs 10,6 %).
   - Thứ tự giá trong nến chỉ đổi ≤ 1,8 điểm; **spread đổi nhiều hơn** (ô 7: −12,3 ở 1,5 pip vs −19,0 ở 2,5 pip) → khi
     không có spread thật từng nến, sai số lớn nhất là SPREAD, không phải thứ tự nến.
   - Đường M1 gần như trùng H1 (chênh M1 có tia −2,6…+3,5; không tia −9,5…+5,4) → ở H1, phần lệch còn lại chủ yếu do
     giá/spread khác sàn, không do nến an đường đi.
   - Lệch xấu nhất còn lại: ô 7 (bi quan −2,8…−9,5, phụ thuộc spread) và ô 15 (lạc quan +1,4…+6,1, bước 12 pip ~ biên
     độ nến → phân giải kém).
3. **Giới hạn:** 15 ô, một cửa sổ 6 tháng, 2 mã; không có lưới chờ lùi / chốt tiền / cắt lỗ; giá XM ≠ HistData; tester
   cũng chưa có swap (the-brain: swap lưới ~ −4,4 %/năm). Rổ EA trong `vong_thu_nghiem` (Breakout5 chốt đỉnh, rổ hedge
   Breakout2/2-2/3 — chạy bằng `mo_phong.chay_he`) có luật thoát KHÁC → **CHƯA ĐO ĐƯỢC** bằng 15 ô này.

## Dòng cảnh báo gắn cạnh số lãi lưới (đã gắn trong mã)
- `nhan/luoi.py`: `CANH_BAO_P1` + khoá `canh_bao_mo_phong` trong `chi_so()`:
  “mô phỏng lệch so với MT5 (P1, 15 ô): luoi.chay lạc quan +1,1…+32,8 điểm %/năm nếu có tia lệnh, −5,1…+5,9 nếu không”.
- `vong_thu_nghiem.py`: hệ có rổ in “mô phỏng lệch so với MT5: CHƯA ĐO ĐƯỢC cho rổ EA này …” (`canh_bao_mt5` trong JSON).
- Nhãn “đạt tiêu chí 25/09?” (lãi kiểm sau phí, maxDD < 80 %, không cháy) cạnh mọi cơ chế — chỉ NHÃN, không đổi GIỮ/BỎ.
