# 01 — Chẩn đoán: cổng kiểm định của các vòng v19–v32

Nhãn: **ĐỀ XUẤT, chưa duyệt.** Mọi số ở đây là MÔ PHỎNG hoặc tính tay từ code; số đo trên dữ liệu thật ghi rõ "CHƯA ĐO ĐƯỢC".
Soạn bởi Claude (phiên cloud, 16/10/2026) theo yêu cầu chủ dự án. Chỉ đọc code, không chạy pipeline thật.

## 1. Có HAI bộ tiêu chí đang cùng tồn tại và mâu thuẫn nhau

| | Cổng của the-brain | Cổng của các vòng v19–v32 |
|---|---|---|
| Ở đâu | `nhan/cong.py` + `config/nguong.json` | `v30.py:159`, `v31_moc.py:104,193`, `v32_luoi_moc.py:84,145` |
| Vai trò p/FDR | **Nhãn** (`che_do_cong = "nhan"`, `cong.py:98`). Chỉ chặn cứng thứ về tiền: thắng mua-giữ cùng rủi ro, phí đo được, đủ lệnh, `rr_thuc_te ≥ 0,2`, cạnh ≥ 3× spread (`cong.py:47-` `MAC_DINH`) | **Cổng cứng**: QUA = p_Holm < 0,05 (`tai_lieu/VONG_LAP.md` mục "Luật cứng") |
| Đa kiểm định | LORD — FDR cho chuỗi giả thuyết tăng dần (`cong.py:361 nguong_lord`, `:460 lord_v2`) | Holm với m = **mọi ô từng sàng** (20.503 sau v32) |
| Ngưỡng α | Suy được từ 3 số kinh tế của chủ dự án (`cong.py:108-125`), nhưng 3 số **chưa được điền** → đang chạy mặc định 0,05 "học thuật" (`MAC_DINH["_ghi_chu"]`) | cố định 0,05 sau Holm |
| Gốc quyết định | Chủ dự án 11/09 (nguyên văn, trích ở `cong.py` trên `NHAN_MEM`): *"khong phai nhung mo hinh kinh te hay quan tri quy de ma can de cao qua nhieu tieu chi hoc thuat hay cac chi tieu chat che. Muc dich cuoi cung la co tien chap nhan ca chi phi va rui ro cao"* | `KINH_NGHIEM.md` mục 4: "Không được nới cổng"; mục 10: cần p < ~4e-6 |

Hệ quả: các vòng gần đây không gọi `nhan/cong.py`, nên không dùng LORD, `rr_thuc_te`, `edge_tren_spread`, cũng không dùng
`nhan/do_luc.py` (MDE) hay `nhan/nha_may_null.py` (hiệu chuẩn hai chiều) — dù tất cả đã có sẵn trong repo.

## 2. Ba vấn đề thống kê của cổng v19–v32

### 2.1 Sai ở m (quá chặt)
`v31_moc.py:193` / `v32_luoi_moc.py:145` tính `p_holm = p × (HO − rank)` với HO = số ô **đã sàng** (6.050 ô ở v32, tổng cộng dồn 20.503).
Nhưng GĐ1 là dữ liệu **độc lập** với GĐ2 dùng để sàng. Sau sàng chỉ ≤ 20 ứng viên được kiểm trên GĐ2 (`v31_moc.py:138`: "tối đa 20"; v32: 0).
Với bước sàng đúng quy trình (chọn chỉ bằng GĐ1, danh sách đăng ký trước khi nhìn GĐ2), họ cần hiệu chỉnh là **ứng viên đã kiểm**, không phải ô đã sàng.
Holm còn coi các ô lân cận (79 mốc × 14 offset × 3 kiểu) là độc lập; thực tế chúng gần như cùng một chuỗi lệnh.

Ngưỡng z một phía tương ứng: 1,64 (1 phép thử) · 2,81 (k = 20) · **4,57** (m = 20.503).

### 2.2 Sai ở p (quá lỏng, ngược chiều)
`ttest_1samp` trên **từng lệnh** coi lệnh độc lập. Lệnh trong cùng tuần/ngày, 12 tài sản cùng chịu cú sốc USD, lệnh chồng lấn
→ n hiệu dụng < số lệnh → p quá nhỏ. `v24.py:68 p_cum` (gom cụm theo tuần) và `p_boot` từng xử lý đúng chuyện này; v30–v32 bỏ.

Đo bằng mô phỏng (không có cạnh nào, 150 lệnh = 30 tuần × 5 lệnh, 20.000 lần; `ma_mau/ket_qua_mo_phong.md` bảng A):

| ICC (rho) | deff | t-test từng lệnh @ 0,05 | gom cụm @ 0,05 | t-test từng lệnh @ 0,0025 | gom cụm @ 0,0025 |
|---|---|---|---|---|---|
| 0 | 1,01 | 0,049 | 0,049 | 0,0024 | 0,0027 |
| 0,1 | 1,43 | 0,084 | 0,052 | 0,0095 | 0,0027 |
| 0,3 | 2,21 | **0,131** | 0,049 | **0,0287** | 0,0026 |

`rho` là giả định. **Giá trị thật chưa đo** (việc T1 ở `03_KE_HOACH_THU.md`). Hai lỗi 2.1 và 2.2 triệt tiêu một phần nhau nhưng không theo cách có thể dự đoán.

### 2.3 Sức phát hiện (power): câu hỏi chưa được trả lời là "dữ liệu có đủ sức thấy cạnh không?"
Số lệnh cần để t-test một phía thấy cạnh e, sd 100 bps/lệnh (**giả định**), power 50 %:

| Cạnh thật | 1 phép thử | k = 20 | m = 20.503 |
|---|---|---|---|
| 5 bps | 1.082 | 3.151 | 8.353 |
| 10 bps | 270 | 787 | 2.088 |
| 20 bps | 67 | 196 | 522 |

Số lệnh GĐ2 thật mỗi ô ở v30/v31 là trung vị ~190–240 (xem mục 3), cùng cỡ với 150 trong bảng này. Với 150 lệnh/ô, cạnh nhỏ nhất thấy được là ≈ 13 / 23 / 37 bps. Cạnh còn lại sau phí trên FX/chỉ số thường 1–10 bps.
Vì vậy "0 qua" **không phân biệt được** "không có cạnh" với "mẫu quá nhỏ". Sổ vòng hiện không in MDE cạnh kết luận âm
(trong khi `CLAUDE.md` dòng 116: "Kết luận âm tính phải kèm MDE"). `grep -i mde` trên `v30.py`, `v31_moc.py`, `v32_luoi_moc.py` và `reports/vong30|31|32` không ra gì.

Đường ống đầy đủ (sàng GĐ1 → kiểm top-20 GĐ2; bảng B của `ket_qua_mo_phong.md`, 2.000 ô nhiễu + 10 ô cạnh thật, 2.000 lần):

| n/ô | cạnh | ô thật được chuyển sang GĐ2 (/10) | ô thật được nhận: Holm m=20.503 | Holm k=20 | ô giả được nhận (k=20) |
|---|---|---|---|---|---|
| 150 | 10 bps | 1,29 | 0,000 | 0,074 | 0,038 |
| 150 | 20 bps | 5,08 | 0,090 | 1,866 | 0,046 |
| 1.500 | 5 bps | 3,17 | 0,011 | 0,614 | 0,043 |
| 1.500 | 10 bps | 9,07 | 2,21 | **8,04** | 0,042 |
| 1.500 | 20 bps | 10,0 | 9,99 | 10,0 | 0,046 |

Đọc đúng: (a) cách hiệu chỉnh đáng kể — ở n = 1.500, cạnh 10 bps: Holm k = 20 bắt 8/10 ô thật, Holm m = 20.503 chỉ 2,2/10, mà tỉ lệ ô giả vẫn
≈ 0,04/lần (FWER ≈ 5 %); (b) **cỡ mẫu còn quan trọng hơn** — ở n = 150 cạnh ≤ 10 bps gần như không thể thấy dù hiệu chỉnh kiểu nào,
vì bước sàng GĐ1 đã không chọn được ô thật. Khớp `KINH_NGHIEM.md` mục 18: tăng n (gộp tài sản, khung nhỏ hơn, lịch sử dài hơn) thay vì thêm lọc.

## 3. Điều chẩn đoán KHÔNG nói

- **Không** nói kết luận "0 sống" của v30–v32 sai. Đọc từ `reports/vong30.json` và `reports/vong31_moc.json`: p GĐ2 nhỏ nhất là **0,108** (v30, 29 ô kiểm) và **0,241** (v31, 21 ô kiểm) —
  tức **không ô nào đạt 0,05 ngay cả khi chưa hiệu chỉnh gì**; chỉ 8/29 và 5/21 ô có trung bình GĐ2 dương. Số lệnh GĐ2 mỗi ô: trung vị 191 (v30) và 239 (v31), nhỏ nhất 38 và 26.
  v32: trung vị bps/lệnh phẳng −6,5…−7,3 ở mọi offset → cạnh thô ≈ 0, chi phí là toàn bộ câu chuyện; 0 ô được đăng ký.
  Kết luận đúng, chỉ là **cổng bảo vệ khỏi một lỗi (dương tính giả) trong khi lỗi lớn hơn của quy trình là thiếu sức phát hiện** (mục 2.3).
- **Không** nói cổng Holm không thể qua: IBS<0,2 US500/US100 (vòng 29) đã qua Holm 13.000 với p_Holm 0,003 / 0,0015 — cạnh đủ lớn thì vượt được.
  Vấn đề là cạnh *vừa phải* (5–20 bps) sẽ bị bỏ sót, và **kết quả phụ thuộc số ô đã quét** chứ không chỉ bằng chứng.
- **Không** nói bỏ kỷ luật. Mọi thứ trong `02_*` giữ: tiền đăng ký trước, không nhìn trước, phí đo được, stress ×1,5, placebo, nhãn CHƯA ĐO ĐƯỢC.

## 4. Còn lại chưa biết (cần Grok/box đo)
- ICC thật và deff của lệnh v31/v32 (gom theo tuần vào lệnh; gom theo ngày).
- sd thật mỗi lệnh theo từng họ ở v30–v32 → bảng power thật thay cho giả định 100 bps.
- Thời gian chạy lưới v32 (6.050 ô × 12 tài sản H1) trên 1 chuỗi null — quyết định có làm null tối đa 1.000 chuỗi được không.
