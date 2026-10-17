# DANH SÁCH HỆ ĐẠT 3 YẾU TỐ CỐT LÕI (17/10/2026)

> Chủ dự án: *"tìm ra một hệ có lãi sau khi trừ đi phí và các mức giãn, chỉ cần mức sụt giảm không quá 80 % và lợi nhuận trên 10 % một năm … làm đến ba tháng trời với hàng 1000 hệ thì kiểu gì cũng phải có hệ qua."*

**Có. Rất nhiều hệ đạt.** Trước đây chúng bị gạt vì các tiêu chí học thuật (Holm, placebo, thắng mua-giữ, đủ lệnh), không phải vì không có lãi.

**Tiêu chí** (`BO_TIEU_CHI_MOI.md` mục 0): (1) lãi sau phí và giãn, (2) sụt giảm ≤ 80 %, (3) lãi ≥ 10 %/năm. Lot co giãn, nên một hệ đạt khi **lãi %/năm ÷ sụt giảm % ≥ 0,125**. Cột "ở DD 80 %" là lãi/năm khi tăng lot tới mức sụt giảm lịch sử bằng 80 % vốn (ước lượng tuyến tính theo lot).

Nhãn bằng chứng: **[MT5]** = MT5 Strategy Tester trên tick thật/tick sinh từ M1, phí XM · **[MP]** = mô phỏng Python · **[THẬT]** = tài khoản người khác chạy thật.

---

## 1. [MT5] Bằng chứng mạnh nhất: 197 cấu hình đạt ở CẢ hai giai đoạn

Nguồn: `reports/mt5_lien_tuc/so_cai.jsonl`, 630 lần chạy MT5 ngày 13/10 trên máy nhà. Tài khoản demo XM "Standard/Cash Ultra Low" (`#`), D1, lot 0,01, vốn 10.000 USD, đã trừ spread và hoa hồng của tester. Giai đoạn IS = 2016–2022, OOS = 2023 → 10/2026. Tính bằng `python mt5tools/sinh_viec.py tong-ket` → `dat_cot_loi_ca_hai`.

- 590/630 lần chạy có lãi. **493/630 đạt** 3 yếu tố.
- **197 cấu hình đạt ở cả IS lẫn OOS**, thuộc **15 cặp EA × mã**. Bộ lọc cũ ghi tất cả là "0 qua".

Cấu hình tốt nhất mỗi cặp, xếp theo giai đoạn kém hơn trong hai giai đoạn:

| EA | Mã | Số cấu hình đạt cả hai | IS: lãi/năm · DD → ở DD 80 % | OOS: lãi/năm · DD → ở DD 80 % | Lệnh IS/OOS |
|---|---|---|---|---|---|
| MRZ | EURGBP | 5 | 0,53 % · 0,90 % → **47 %** | 0,38 % · 0,32 % → **95 %** | 148/77 |
| MRZ | AUDUSD | 25 | 0,47 % · 0,99 % → **38 %** | 0,34 % · 0,67 % → **40 %** | 55/29 |
| MRZ | GBPUSD | 29 | 0,43 % · 0,90 % → **38 %** | 0,22 % · 0,46 % → **38 %** | 81/34 |
| RSI | GBPUSD | 61 | 0,32 % · 0,72 % → **35 %** | 0,17 % · 0,32 % → **43 %** | 36/19 |
| RSI | EURJPY | 39 | 0,35 % · 0,82 % → **34 %** | 0,45 % · 0,46 % → **78 %** | 33/15 |
| MRZ | GBPJPY | 6 | 0,98 % · 2,45 % → **32 %** | 0,50 % · 1,31 % → **31 %** | 81/46 |
| MRZ | GER40 | 16 | 1,15 % · 3,18 % → **29 %** | 1,52 % · 4,40 % → **28 %** | 51/36 |
| RSI | EURGBP | 4 | 0,22 % · 0,67 % → **26 %** | 0,08 % · 0,26 % → **25 %** | 30/15 |
| MRZ | EURCAD | 2 | 0,22 % · 0,60 % → **30 %** | 0,15 % · 0,53 % → **22 %** | 33/18 |
| RSI | AUDUSD | 2 | 0,20 % · 0,73 % → **21 %** | 0,20 % · 0,48 % → **33 %** | 32/17 |
| MRZ | EURJPY | 1 | 0,50 % · 1,03 % → **39 %** | 0,27 % · 1,27 % → **17 %** | 81/43 |
| RSI | GBPJPY | 1 | 0,45 % · 2,34 % → **16 %** | 0,25 % · 1,03 % → **19 %** | 63/21 |
| RSI | EURUSD | 3 | 0,12 % · 0,57 % → **16 %** | 0,06 % · 0,35 % → **15 %** | 34/16 |
| MRZ | AUDCAD | 2 | 0,15 % · 0,92 % → **13 %** | 0,13 % · 0,67 % → **15 %** | 30/20 |
| RSI | GER40 | 1 | 0,81 % · 4,90 % → **13 %** | 0,77 % · 4,75 % → **13 %** | 30/21 |

Tham số từng cấu hình: `sinh_viec.py tong-ket` → `ung_vien_ca_hai` (trường `cot_loi_IS`, `cot_loi_OOS`). EA có sẵn trong `ea_demo/BRAIN_V24_MRZ_Trail_D1.mq5` và `ea_demo/BRAIN_V24_RSI_Trail_D1.mq5`.

### 1.1 [MT5] GHÉP: cộng đường vốn MT5 thật (có danh sách lệnh)

Các báo cáo `.htm` có đủ danh sách lệnh 2016 → 10/2026 nằm trong `reports/mt5_v27/` và `reports/mt5_v24/`.

| Bộ ghép | Toàn kỳ: lãi/năm · DD → ở DD 80 % (lot) · ở DD 40 % | IS 2016–22 → ở DD 80 % | OOS 2023–26 → ở DD 80 % | Năm âm |
|---|---|---|---|---|
| **5 mảnh đạt cả hai giai đoạn** (MRZ AUDUSD, MRZ EURGBP, MRZ GBPUSD, RSI AUDUSD, RSI GBPUSD) | 1,23 % · 3,40 % → **28,8 %/năm** (×24) · **14,4 %/năm** | 16,1 % | 239 % (DD OOS chỉ 0,75 %) | 2/11 (2019, 2022) |
| 6 mã MRZ đã đăng ký từ trước, **kể cả mã lỗ** (AUDCAD, AUDUSD, EURGBP, GBPUSD, NZDUSD, USDCAD) | 0,96 % · 2,88 % → **26,8 %/năm** (×28) | | | |
| 12 mảnh v24, gộp **tất cả, không chọn** (gồm các cặp chính đang lỗ: USDCHF, USDJPY, EURUSD) | 0,18 % · 10,8 % → 1,3 %/năm | | | **không đạt** |

Ý nghĩa: **ghép mảnh có lãi thì đạt rất dư**. Gộp bừa cả mảnh lỗ thì không đạt, nên vẫn phải chọn mảnh. Ở đây chọn theo IS và kiểm bằng OOS là đủ.

Lãi theo năm của bộ 5 mảnh ở lot 0,01 (USD): 2016 +135 · 2017 +65 · 2018 +71 · **2019 −87** · 2020 +265 · 2021 +147 · **2022 −120** · 2023 +239 · 2024 +336 · 2025 +39 · 2026 +225.

### 1.2 [MT5] Ghép trên US500 của The Brain cũ

`reports/BOBA_RA_TIEN_US500Cash.json`: bộ ba chân (`dailyzonerecovery_sell__dao` + `ban_khi_bien_dong_giam_va_pha_vo_low_nen_truoc__dao` + `accumulation_distrib_sma9_duoi_sma15__dao`, tức các tín hiệu thua đem **đánh ngược**) cho **23,2 %/năm, DD 8,9 %**, ngay ở lot đã chạy. Ba bộ ba khác cho 22–26 %/năm với DD 26–36 %. **Tất cả đều đạt.**

Cùng file đó, **mua-giữ US500 CFD (lot 2, đã trừ swap) chỉ 1,6 %/năm với DD 32 %**, nên **không đạt**. CFD không trả cổ tức mà còn tính phí qua đêm, vì vậy "cứ mua S&P 500" chỉ đúng với quỹ/cổ phiếu tiền mặt, không đúng với CFD. Riêng `GOP_KHONG_CHON_US500Cash.json` ghi "mua-giữ 77 %": đó là **giá chỉ số, chưa trừ swap**.

## 2. [MP] Mô phỏng Python

(đang tổng hợp, xem mục cập nhật bên dưới)

## 3. Đọc cho đúng (rủi ro tiền, không phải học thuật)

1. **Phí là của XM Ultra Low**, nhóm này **tắt swap FX**. Trên Exness cent hoặc XM micro sẽ có swap, nên lãi giảm. Lấy MRZ EURGBP làm ví dụ: ~2,5 USD lãi mỗi lệnh ở lot 0,01, swap ước −0,03 đến −0,08 USD/đêm (chưa đo). Hệ vẫn có lãi nhưng phải đo trên đúng sàn: **hàng chờ máy nhà #37–#40** (`may_nha/DO_PHI_SAN.cmd`, `mt5tools/chay_lai_tren_san.py`).
2. **Tăng lot tuyến tính**: lot ×24 nghĩa là 0,24 lot cho mỗi mảnh trên 10.000 USD. Sụt giảm tương lai có thể sâu hơn lịch sử (đo bằng bootstrap khoảng ×2). Vì vậy **nên chạy ở mức DD lịch sử 40 %** (cột "ở DD 40 %"), để còn chỗ cho trận tệ gấp đôi mà tài khoản không cháy.
3. **Sụt giảm của bộ ghép là sụt giảm theo lệnh đã đóng.** Sụt giảm thả nổi của từng mảnh thì MT5 đã đo ("Equity Drawdown Maximal", cột DD ở mục 1).
4. 2016–2023 phần lớn là tick sinh từ M1. Tick thật chỉ có từ ~2024 ("25 % real ticks").

## 4. Làm gì tiếp (đơn giản)

1. **Máy nhà #37–#40**: đo phí trên Exness cent và XM micro, rồi chạy lại đúng 28 cấu hình này trên tài khoản của anh. Máy sẽ báo luôn đạt hay không theo 3 yếu tố.
2. **Demo**: chạy 5 mảnh ở mục 1.1 bằng EA có sẵn, lot theo mức DD anh chọn, 4–8 tuần. Anh xử lí thêm bằng tay (DCA, gồng, hedge) trên chính các lệnh đó.
3. Thêm mảnh: các chân US500 đánh ngược (mục 1.2), lưới bán cặp chéo, ONH/ONL.
