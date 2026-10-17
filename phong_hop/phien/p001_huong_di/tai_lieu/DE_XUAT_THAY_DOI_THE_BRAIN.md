# ĐỀ XUẤT THAY ĐỔI THE BRAIN — của Claude, 17/10/2026

Nhãn: **ĐỀ XUẤT, chờ chủ dự án duyệt.** Viết sau khi chủ dự án nói: "cậu cũng phải tư duy đề xuất thay đổi cụ thể". Căn cứ: sơ đồ gốc (`SO_DO_HE_THONG.txt`), `CHI_THI_CHU_DU_AN.md`, và đọc code thật (liệt kê ở mục 1).
Claude chưa từng giao dịch; mọi chỗ về "cách trader xử lí" là bản hiểu từ lời chủ dự án, cần chủ dự án sửa.

## 1. Chẩn đoán bằng code (không phải cảm giác)

| Phát hiện | Chứng cứ |
|---|---|
| **Engine quản lí rổ lệnh đã có và rất giàu**, nhưng chỉ cho MỘT rổ trên MỘT tài sản | `mo_phong_v2.mo_phong(...)` ~40 tham số: bước + hệ số bước, lot theo nhóm, **cắt hoà** (ghép lệnh mới nhất với lệnh đầu, đóng cặp khi tổng ≥ ngưỡng), chốt cả rổ theo tiền, dừng lỗ cả rổ, **hedge** (`hedge_tu/hedge_ty/hedge_go`), trailing, kéo hoà vốn, cổng biến động, spread/swap/trượt thật, trả đường vốn |
| **Module "ghép" trong sơ đồ gốc chưa từng được xây** | `nhan/hephaestus.py` (Hephaestus = "ghép nút, sinh tổ hợp") **không có trong cả `brain2` lẫn `the-brain`**. `nhan/danh_muc.ghep` chỉ trộn các chuỗi lợi nhuận theo tỷ trọng (sau cổng), không ghép lệnh, vùng, hay gỡ chéo |
| **Thước đo theo tiền ở cấp tài khoản đã có** | `nhan/cham_diem.py`: lãi trên vốn phải bỏ ra · sụt giảm · vốn cần (kèm bản CENT) · bao nhiêu tháng hồi vốn · số lệnh/năm · nguy cơ cháy; ba mức CHAY_DUOC / MONG / BO |
| **Các vòng v19–v32 không dùng cái nào ở trên** | `grep` `quan_tri|pmg|cham_diem|danh_muc|mo_phong_v2|luoi_duong` trên `v19*…v32*.py`, `phan_tich_luoi_box.py` → không ra; chỉ `vong_thu_nghiem.py` gọi. v19–v32 chỉ quét **tín hiệu vào** rồi qua cổng Holm |
| **Nút thắt của Seeker nằm sai chỗ** | Bộ đọc EA dịch 3,57 % vì bắt dịch *điều kiện vào*. Phần *quản lí* thì đọc được từ `input`: `nhan/quan_tri.py` đã đếm 5.964 input trong 353 EA (trailing 87 · step 70 · multiplier 58 · level 53 · recovery 22 · partial 20 · breakeven 19 · hedge 17) — chưa được dùng |
| Thư viện cơ chế từng chỉ có **tín hiệu vào** | `quan_tri.py` docstring: 262 cơ chế, 2 cái có dấu hiệu quản trị vị thế; rìa kho đã có 61 hedge · 43 lưới · 43 DCA · 34 recovery · 33 martingale · 18 basket, "0 cái vào được thư viện" |

Kết luận: không thiếu ý tưởng hay engine. **Thiếu khâu lắp ráp và thiếu cách chọn tổ hợp.**

## 2. Sáu thay đổi

### 2.1 Đơn vị công việc = HỆ GHÉP (một file JSON), không phải ứng viên đơn
```
he_ghep = {
  nguon_lenh: [ {id, tai_san, khung, luat_vao, huong, lot_don_vi}, ... ],     # nhiều hệ chạy cùng lúc
  ban_do_vung: { moc: [ONH, ONL, PDH, PDL, gia_mo_phien, tron, pivot...] },    # dùng chung cho DCA / chốt
  quan_li: {
     tp_diem, keo_sl_duong_sau,
     cho_gia_ve: true,                                                         # không SL cứng
     dca: { kieu: 'theo_vung'|'buoc'|'atr', so_tang, he_so_lot },
     nhoi_theo_chieu: {...}, hedge: {khi, ty_le, go_khi},
     go_lenh: { cheo_he: true, nguong_net_diem }                               # lãi nổi của rổ này đóng lệnh kẹt của rổ kia
  },
  von: { so_du, don_vi_lot, don_bay }, san: 'exness_cent'|'xm_micro'
}
```
Mọi thứ phía sau (Seeker, ghép, chấm) nói chung một ngôn ngữ này.

### 2.2 Engine cấp TÀI KHOẢN: `nhan/tai_khoan.py` (Claude tự làm)
Không viết mới từ số 0: bọc và mở rộng `mo_phong_v2` (cùng luật chi phí, cùng cách tính spread/swap/trượt):
- **Nhiều rổ chung một tài khoản**, margin / stop-out chung, đường vốn thả nổi chung.
- **Gỡ chéo** = tổng quát hoá `cat_hoa` từ "ghép lệnh trong một rổ" thành "ghép lệnh kẹt của rổ A với lãi nổi của rổ B (khác hệ / khác tài sản), đóng cả cặp khi tổng ≥ ngưỡng".
- **DCA theo vùng**: tầng thêm đặt ở mốc trùng nhau của nhiều phương pháp (confluence), không chỉ bước cố định.
- Đầu ra: đường vốn → `cham_diem` (không thêm chỉ số học thuật).
- **Hiệu chuẩn trước khi tin**: chạy lại 15 ô MT5 sạch có sẵn (`hieu_chuan/p1_15o_tester.csv`). Độ khớp MT5 của `mo_phong_v2` chưa ai đo (P1 chỉ đo `luoi_duong`).

### 2.3 Cách tìm tổ hợp: suy luận về sự BÙ NHAU, không lưới tham số mù
1. Gắn **hồ sơ trạng thái** cho từng mảnh (nguồn lệnh, bộ quản lí): nó *ăn* khi nào và *kẹt* khi nào, theo (xu hướng tăng / giảm / đi ngang) × (biến động thấp / cao) × (phiên Á / Âu / Mỹ).
2. Điểm bù nhau (A, B) = phần trạng thái A kẹt mà B đang ăn − phần trạng thái cả hai cùng kẹt (thứ giết tài khoản: **kẹt cùng lúc**, như crash 2020 / 2025).
3. Lấy top-K cặp/bộ ba theo điểm bù nhau → mô phỏng cấp tài khoản → giữ cái cho thu nhập/tháng cao nhất trong giới hạn vốn chủ dự án chấp nhận.
4. Tách riêng việc chọn bộ quản lí: chạy từng bộ quản lí trên **dòng lệnh đơn giản** (mua mở phiên Mỹ mỗi ngày, ví dụ ONH của chủ dự án) để biết bộ nào hợp trạng thái nào, rồi mới cắm nguồn lệnh khác vào.

### 2.4 Seeker: THU MỌI NGUỒN VÀO LỆNH ĐƯỢC, quy về "dòng lệnh vào" — bộ lọc chỉ hỏi "ra lệnh được không?" (sửa 17/10 theo lời chủ dự án)
Chủ dự án: dùng bộ não + bộ lọc để **sưu tập tất cả hệ thống có thể vào lệnh**, rồi kết hợp; không tìm đơn hệ rồi lọc nặng học thuật. (Bản đầu của mục này ghi "thôi bắt dịch điều kiện vào" — sai ý; sửa lại như dưới.)
- **Giao diện chung = DÒNG LỆNH VÀO** `LenhVao(nguon, chi_so, gia, chieu)` (xem `nhan/tai_khoan.py`). Mọi nguồn — EA, chỉ báo mũi tên, luật DSL, lịch sử giao dịch (MQL5 signal, myfxbook), sự kiện ở mốc (ONH/ONL/PDH...) — đều quy về dòng này. **Không cần dịch logic của nguồn**, chỉ cần biết nó mở lệnh lúc nào, chiều nào, giá nào.
- Cách lấy dòng: (a) luật đã dịch được → chạy thẳng; (b) **EA chưa dịch được → CHẠY nó** một lần trên máy nhà (MT5 tester, không để chấm đạt/trượt, chỉ để xuất danh sách lệnh vào), thay vì cố dịch (tỉ lệ dịch chỉ 3,6 %); (c) lịch sử giao dịch → là dòng lệnh sẵn.
- **Bộ lọc của Seeker chỉ còn một câu: nguồn này có ra lệnh vào đo được không** (có giá, có chiều, chạy lại được, phí đo được). Không hỏi có edge không — chất lượng chỉ xét ở **hệ ghép** (mục 2.5).
- Song song vẫn rút **phần quản lí** từ `input`/`.set` (bộ quản lí cắm vào bất kỳ dòng lệnh nào).

### 2.5 Cổng duy nhất: `cham_diem` ở cấp tài khoản + một bài "ngày tận thế"
Không còn Holm / FDR / placebo làm cổng. Thêm một kiểm tra theo ngôn ngữ trader: *đặt hệ ghép vào đúng các đợt 2008 / 2020 / 2022 / 2025 (nếu có dữ liệu) với vốn X, tài khoản có sống không, lỗ treo bao nhiêu điểm, kẹt bao lâu.*

### 2.6 Dừng / đóng băng
`v19`–`v32` (vòng lặp quét tín hiệu), cổng Holm, quét lưới tham số, nhánh `de-xuat-cong-kiem-dinh`. Tài nguyên đó chuyển sang 2.2–2.4.

## 3. Chủ dự án sẽ nhận gì (một trang cho mỗi hệ ghép)
Với vốn X và lot Y: thu nhập ước tính mỗi tháng · lỗ treo tối đa (điểm và %) · kẹt lâu nhất · % thời gian đang có lệnh kẹt · tháng tệ nhất · kết cục ở 2020 / 2022 / 2025 · cặp mảnh nào bù nhau và vì sao · điều kiện nên tắt hệ (trạng thái thị trường nào).

## 4. Thứ tự và ai làm gì
| Gói | Việc | Ai | Xong khi |
|---|---|---|---|
| 1 | Schema `he_ghep` + `tai_khoan.py` (nhiều rổ, margin chung, gỡ chéo) + unit test + hiệu chuẩn 15 ô MT5 | **Claude** | chạy được ví dụ ONH + một hệ khác, cho thấy gỡ chéo đổi đường vốn ra sao (không phải để chọn tham số) |
| 2 | Hồ sơ trạng thái + điểm bù nhau (2.3) trên các mảnh đã có | **Claude** | bảng "mảnh nào bù mảnh nào" cho SP500 / NAS100 / vàng |
| 3 | Rút phần quản lí từ kho EA đã thu → thư viện bộ quản lí + gắn vai trò cho 79 mốc / các EA | Grok | file thư viện + thẻ; không chạy test |
| 4 | Chọn 2–3 hệ ghép cùng chủ dự án, chạy bài "ngày tận thế" | cùng chủ dự án | hồ sơ một trang mỗi hệ |

## 5. Chưa biết / rủi ro (nói thẳng)
- Độ khớp MT5 của `mo_phong_v2` chưa đo → số đầu ra mặc định nhãn "MÔ PHỎNG, có thể lạc quan" tới khi hiệu chuẩn xong.
- "Ghép theo bù nhau" là giả thuyết của Claude; có thể phát hiện ra các mảnh kẹt *cùng lúc* nhiều hơn dự kiến (tương quan đuôi), khi đó lợi ích ghép nhỏ.
- Dữ liệu phút (M1) chỉ có ở máy Grok; cloud chỉ có H1 của XM từ 2016.
- Không hứa có lãi. Đề xuất làm cho **câu hỏi đúng** (hệ ghép sống được với vốn của anh không, thu bao nhiêu) trả lời được bằng số.

## 6. Kết quả đầu tiên của engine tài khoản v1 (17/10, MÔ PHỎNG H1, 1 đơn vị/rổ, TP 5,5 điểm, spread 1,5, swap 5,77 %/năm)
`nhan/tai_khoan.py` (5 test xanh) + `mau_thu/tai_khoan_demo.py`: ba nguồn LONG trên US500Cash XM — ONH-retest, ONL-touch, IBS<0,2 — chạy riêng, ghép, ghép + gỡ chéo, ghép + DCA. Giai đoạn 2023–2026:

| Kịch bản | Số rổ | Tổng (điểm) | Lỗ treo xấu nhất của cả tài khoản (điểm) | Rổ mở cùng lúc tối đa | Rổ kẹt > 5 ngày |
|---|---|---|---|---|---|
| ONH riêng | 336 | 658 | 2.196 | 4 | 31 |
| ONL riêng | 548 | 1.189 | 3.595 | 5 | 42 |
| IBS riêng | 167 | 256 | 1.790 | 4 | 15 |
| **Ghép 3 nguồn** | 1.051 | 2.103 | **7.295** | 11 | 88 |
| Ghép 3 + gỡ chéo | 1.051 | 2.126 | 7.295 | 10 | 81 |

Ba điều rút ra (trong mẫu này, chưa hiệu chuẩn MT5):
1. **Nhìn từng lệnh đánh giá thấp rủi ro**: ONH riêng, lỗ treo của một lệnh tệ nhất 981 điểm, nhưng các rổ chồng lên nhau làm tài khoản treo tới 2.196 điểm.
2. **Ghép nhiều nguồn cùng chiều, cùng chỉ số ≈ một cược**: tổng gấp 3 nhưng lỗ treo cũng gấp 3 (tổng/lỗ treo 0,29 so với 0,30–0,33 của từng nguồn). Chúng kẹt cùng lúc — đúng điều lo ở mục 2.3.
3. **Gỡ chéo giữa các rổ cùng chiều không cứu được cú crash** (lúc đó không có rổ nào lãi để gỡ) và, trong 10 năm (2016–2026), làm giảm lãi 4.196 → 3.530 vì chốt lỗ những lệnh sau vẫn hồi. Chỉ giảm số rổ kẹt lâu (279 → 226).
→ Ghép chỉ có ích khi các mảnh **bù nhau thật**: khác chiều (bán, hedge), khác tài sản, khác trạng thái. Engine v1 còn **một tài sản**; bước tiếp: nhiều tài sản (repo có H1 XM của GER40, vàng) và lệnh bán/hedge làm nguồn.
