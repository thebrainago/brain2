# RÀ SOÁT TOÀN BỘ THE BRAIN — 17/10/2026 (Claude, theo yêu cầu chủ dự án)

> Chủ dự án: *"Góc độ bây giờ là xây dựng hệ thống ĐƠN GIẢN, tập hợp từ những hệ thống mã ghép nhỏ đã có sẵn. Lợi thế của người giao dịch nhỏ lẻ là có thể nhồi lại, gỡ lại, chờ thời gian để vị thế từ hoà thành lãi. Lọc chặt theo kinh tế học thuật thì không hệ nào bắt được. Phải đo lại tất cả các mức phí, mức giãn, tổng kết phương pháp/tín hiệu nào vào lệnh được và xử lí lệnh cho nó … xem xét lại toàn bộ."*

**Một câu:** hệ thống đã từng tìm ra nhiều mảnh vào lệnh có lãi — kể cả trên **MT5 tester thật** — rồi tự gạt đi bằng bộ lọc học thuật. Không cần xây thêm máy; cần **nhặt lại, đo phí đúng tài khoản của anh, ghép đơn giản, chạy demo**.

Ghi nhãn bằng chứng: **[MT5]** = MT5 tester thật · **[MP]** = mô phỏng Python (có thể lạc quan) · **[THẬT]** = tài khoản người khác chạy thật · **[CHƯA ĐO]**.

---

## 1. Các bộ lọc đã gạt bỏ ứng viên — ở đâu, gạt gì, xử lí sao

| Bộ lọc | Ở đâu | Đã gạt gì | Đề xuất |
|---|---|---|---|
| **Holm cộng dồn** (20.503 ô) | `v19–v32`, `tai_lieu/VONG_LAP.md` "Luật cứng" | **247/251 cấu hình MT5 lãi cả hai giai đoạn** (mục 2.1) bị ghi "0 qua" | **BỎ** |
| Alpha có ý nghĩa + placebo + FDR online | `nhan/cong.py` điều kiện 4, 5, 10 | **85/361 hệ** (24 %) FAIL chỉ vì 3 điều này (mục 2.4) | **BỎ khỏi phán quyết** |
| "Phải thắng mua-giữ" | `cong.py` điều kiện 1–3; `reports/GOP_KHONG_CHON_US500Cash.json` "MUA-GIU THANG" | hệ ghép US500 (mục 2.3) | **Hạ thành nhãn** (CFD mua-giữ chịu swap ~5,8 %/năm; trader không gồng mua-giữ) |
| `rr_thuc_te ≥ 0,2` | `cong.py` điều kiện 12 (`MAC_DINH`) | **mọi DCA / TP nhỏ / không SL** — đúng cách anh đánh | **BỎ** với hệ có quản lí; giữ làm nhãn "đuôi rủi ro" |
| `lãi ≥ 3× spread` | `cong.py` điều kiện 13 | scalp TP nhỏ | Thay bằng **lãi ròng sau phí THẬT > 0** |
| Đủ lệnh: `≥ 30`, `n ≥ 150`/ô, `≥ 2 lệnh/tuần`, `≥ 20 lệnh/năm` | `cong.py` đk 8; `v32`; SP500 tầng 0; `cham_diem` | hệ D1 ít lệnh (4–20 lệnh/năm) | **BỎ** — ghép nhiều hệ ít lệnh thì đủ lệnh |
| "Dương cả hai nửa" | `VONG_LAP.md` | hệ ăn theo chế độ | **Nhãn chế độ**, không loại |
| `CHAY_DUOC`: lãi ≥ 20 %/năm ở lot cố định | `nhan/cham_diem.py` | hệ lãi nhỏ ở lot thử | Vô nghĩa vì **lot co giãn được** → báo "%/năm ở mức sụt giảm anh chọn" |
| Bộ đọc EA chỉ giữ EA **dịch được** (3,6 %) | `nhan/doc_ma.py`, Seeker | ~96 % kho EA | **Chạy EA** để lấy lệnh, không dịch |
| `quan_tri.loc` (≥ 2 nút, có tham số số, ≥ 1 nút quản trị) | `nhan/quan_tri.py` | EA đơn giản | Đổi thành "ra lệnh đo được không" |
| `TRAN_SPREAD_BPS = 8` | `nhan/ho_so_symbol.py` | cặp phí cao | Giữ, nhưng theo **phí đo trên sàn của anh** |
| `NGUONG_PHAN_GIAI` (PMG) → CHƯA ĐO ĐƯỢC | `nhan/pmg_engine.py` | lưới bước hẹp hơn nến | **Giữ** (không đo được ≠ âm) |

Chỉ giữ ba thứ làm con số THẬT: **phí thật của sàn anh**, **không dùng dữ liệu tương lai**, **khớp MT5**.

## 2. "Nghĩa địa" — ứng viên có lãi đã bị gạt (xếp theo độ mạnh bằng chứng)

### 2.1 [MT5] Hai EA đơn giản trên D1 — 247/251 cấu hình lãi cả hai giai đoạn sau phí tester
Nguồn: `reports/mt5_lien_tuc/so_cai.jsonl` (630 lần chạy MT5, 13/10, máy nhà). EA có sẵn: `ea_demo/BRAIN_V24_MRZ_Trail_D1.mq5`, `ea_demo/BRAIN_V24_RSI_Trail_D1.mq5`. IS 2016–2022, OOS 2023–10/2026, lot cố định 0,01, vốn ~10.000.
"%/năm ở DD 20 %" = lấy nửa kém hơn (IS hay OOS), tăng lot tuyến tính tới khi sụt giảm tối đa 20 % (ước lượng thô).

| EA | Mã | Số cấu hình lãi cả hai | DD max (lot thử) | Lệnh/năm | PF OOS | ~%/năm ở DD 20 % |
|---|---|---|---|---|---|---|
| RSI | EURJPY | 39/39 | 0,8 % | 4 | 2,66 | ~8,6 |
| MRZ | EURGBP | 6/7 | 0,9 % | 20 | 1,99 | ~8,5 |
| MRZ | AUDUSD | 27/27 | 1,1 % | 7 | 2,50 | ~8,2 |
| RSI | GBPUSD | 75/75 | 0,9 % | 5 | 2,90 | ~7,2 |
| MRZ | GBPJPY | 6/6 | 2,2 % | 9 | 2,15 | ~6,1 |
| MRZ | GER40 | 27/27 | 4,4 % | 10 | 1,62 | ~5,2 |
| MRZ | GBPUSD | 40/42 | 1,1 % | 9 | 1,73 | ~5,1 |
| (thêm 8 họ nhỏ hơn) | | | | | | 2–5 |

Đọc đúng: **mỗi hệ một mình chỉ ~5–9 %/năm ở DD 20 %, ít lệnh** — chính vì thế cổng nào đòi "đủ lệnh / lãi lớn / có ý nghĩa" cũng gạt nó. Nhưng đây là **mảnh vào lệnh đã qua MT5 thật**, khác tài sản (FX, chỉ số Đức), khác giờ; **ghép 6–8 mảnh này** là đúng bài toán của anh. ⚠ Tài khoản XM Ultra Low `#` **tắt swap FX** → trên tài khoản micro/cent có swap, hệ giữ nhiều ngày sẽ kém hơn — **phải chạy lại trên tài khoản của anh** (mục 4).

### 2.2 [MT5] Lưới bán AUDCAD / NZDCAD — 3/15 ô MT5 sạch lãi
`hieu_chuan/p1_15o_tester.csv` (H1, 03–08/2019): ô 2 AUDCAD bán +9,4 %/năm DD 3,7 % · ô 8 AUDCAD bán +10,9 % DD 4,8 % · ô 15 NZDCAD bán +29,5 % DD 10,6 %. Cả ba đều **lưới chiều BÁN**; giai đoạn chỉ 6 tháng (AUDCAD giảm) → mảnh **theo chế độ**.

### 2.3 [MT5 → ghép] Hệ ghép US500 của The Brain cũ — bị gạt vì "mua-giữ thắng"
`_bo_ba.py`, `_ghep_holdout.py` (The Brain 07/09) cộng **đường vốn MT5** của từng chân (58 chân → 52 sau khử trùng):
- `reports/BOBA_RA_TIEN_US500Cash.json`: bộ ba chân **23,2 %/năm, DD 8,9 %** — so với chân đơn tốt nhất 16,5 %/năm DD 23,6 %. **Ghép làm DD giảm gần 3 lần.**
- `reports/GHEP_HOLDOUT_US500Cash.json` (cắt 06/2021): nhiều cặp lãi ở đoạn sau với DD < 1 % ở lot thử (vd `macd_crossover` + `dailyzonerecovery_sell__dao`).
- Nhiều chân là tín hiệu **ĐẢO CHIỀU** (`__dao`): tín hiệu thua đem đánh ngược — đúng loại "mảnh vô tình dùng được".
- Bị gạt ở `GOP_KHONG_CHON_US500Cash.json`: gộp đều 52 chân thua mua-giữ US500 (2021–2026 là thị trường tăng mạnh).

### 2.4 [MP] 85 hệ FAIL chỉ vì học thuật (thắng mua-giữ, phí đo được, đủ lệnh)
`reports/CHAM_LAI_THE_HE.json`: chủ yếu **hồi quy trên cặp chéo FX** (Bollinger về giữa, RSI đảo chiều, cuối tháng) — AUDCAD 20 · EURCAD 14 · AUDCHF 14 · EURGBP 13 · NZDCAD 10 · GBPCAD 8; khung D1/H4. Khớp với bản đồ PMG G0 14/09 (cặp chéo + vàng hồi quy mọi thang đo).

### 2.5 [THẬT] Người khác đang ra tiền bằng DCA AUDCAD
- Tín hiệu MQL5 `2023752` AUDCAD lưới: **+258 % trong ~3,1 năm, DD công bố 41,6 %** (`hieu_chuan/G06_KET_QUA.md`).
- `nhan/luoi.py`: **13/19 tài khoản DCA sống ≥ 2 năm** trên bảng xếp hạng MQL5 đánh AUDCAD.
Mô phỏng của brain2 không tái tạo được lãi đó (G06/G07) — nhưng **người thật làm được** nên đây là nguồn để **chép cách quản lí**, không phải để bác.

### 2.6 [MP] Các mảnh khác còn sống
- **IBS<0,2 US500 / US100** (vòng 29; `reports/so_sanh_san.md`, phí XM Standard): PF 1,57 / 1,21 (US500) và 1,43 / 1,49 (US100) hai nửa; DD ~14–19 % ở danh nghĩa 10.000. EA có sẵn: `ea_demo/BRAIN_IBS_Demo.mq5`.
- SP500 (ghi chú `the-brain/sp500/`): Pivot_H1_S1 phá lên (5 cấu hình), ZZ-V, mùa vụ "cửa sổ vàng"; ONL DCA (88,8 % rổ đóng ở tầng 1, tệ nhất ~−1.251 điểm × 3 tầng). EA mùa vụ có sẵn: `ea_demo/BRAIN_MuaVu_SPX.mq5`.
- Vòng Grok: RSI/MRZ trailing D1 gộp 54 tài sản (OOS dương 9/12), TRENDBREAKER H4 (8/10 chuỗi lãi OOS), PAXG_ST D1 (+6,6 %), GOLD_8PM vàng M5 (OOS +13,3 %), lọc W1 EMA20 (DD 1,9 %).
- **ONH/ONL** của chủ dự án (Claude đo H1 16/10, `reports/onh_h1_lan_dau.md`): chờ giá về thì 100 % rổ chạm TP; giá trị nằm ở xử lí lệnh kẹt.

## 3. Phí và độ giãn — đo được gì, CHƯA đo gì

**Đã đo (XM Ultra Low `#`, không phải tài khoản của anh):** `reports/mt5_v27/spread_gio/`, `reports/phi_xm_micro_that.csv` (tên file nhầm "micro", thật ra là Ultra Low).
- **Giãn lúc đổi ngày (00h server):** EURUSD 56 vs 11 điểm (×5) · GBPUSD 115 vs 13 (×9) · AUDCAD 164 vs 28 (×6) · GER40 800 vs 150 (×5). → **Không vào/chốt lệnh quanh 23h–02h server.**
- US500 ~0,5–0,55 điểm suốt ngày; swap mua US500 −1,26 /lot/đêm, GER40 −3,45; FX nhóm `#` **swap tắt**; lot tối thiểu chỉ số 0,1.

**[CHƯA ĐO] — đúng hai tài khoản anh đánh: Exness cent và XM micro.** Kho tick công khai Exness không truy cập được từ cloud (HTTP 000) → **phải đo trên máy nhà**.

## 4. Đề xuất: hệ ĐƠN GIẢN từ mảnh có sẵn (không xây máy mới)

1. **Đo phí 2 tài khoản của anh** (máy nhà, ~1 giờ): chạy `mt5tools/phi_xm.py` + `mt5tools/xuat_spread_gia_xm.py` trên terminal **Exness cent** và **XM micro** (sửa đường dẫn terminal/tên mã). Ra: spread theo giờ, **giãn lúc đổi ngày / tin lớn (NFP, CPI) / mở cửa đầu tuần**, swap mua/bán, ngày ×3, lot tối thiểu/bước, hợp đồng, margin, mức stop-out.
2. **Chạy lại đúng các EA đã có trên tài khoản của anh** (MT5 tester, máy nhà): `BRAIN_V24_MRZ_Trail_D1` và `BRAIN_V24_RSI_Trail_D1` với cấu hình tốt nhất ở mục 2.1 cho 6–8 mã; `BRAIN_IBS_Demo` cho US500/US100; bật ghi lệnh (`InpFileLog`, đọc bằng `do_phi_xm.py`) để dựng đường vốn từng mảnh. Không quét tham số — chỉ cấu hình đã có.
3. **Ghép bằng cộng đường vốn** (đã có `_bo_ba.py`): chọn 6–10 mảnh ít kẹt cùng lúc, chia lot theo **mức sụt giảm anh chọn**, báo một bảng: lãi/năm, sụt giảm, tháng tệ nhất, số lệnh/tháng.
4. **Chạy demo** trên tài khoản cent lot nhỏ. Anh thêm xử lí tay (DCA, gồng, hedge, gỡ) trên chính các lệnh đó; ghi lại để hệ học cách anh xử lí.
5. Song song: thêm mảnh ONH/ONL của anh, lưới bán cặp chéo, các chân `__dao` của US500 khi có EA.

**Tạm gác** (để không phức tạp thêm): engine tài khoản `nhan/tai_khoan.py` và phòng họp của Claude (16–17/10) — giữ lại, dùng sau nếu cần; vòng v33+, quét lưới, dịch EA.

## 5. Cần anh
1. Cho phép chạy bước 1–2 trên máy nhà (Grok hoặc anh bấm).
2. Vốn dự định và mức sụt giảm anh chấp nhận (để chia lot ở bước 3).
3. Mảnh nào anh muốn có ngay trong bộ ghép đầu (ví dụ ONH/ONL, IBS, MRZ GER40...).
