# 02 — Tiêu chí "phương pháp tốt" và phễu kiểm định đề xuất

Nhãn: **ĐỀ XUẤT, chưa duyệt.** Giữ nguyên mọi luật cứng của `CLAUDE.md` (canary trước, phí đo được, tiền đăng ký, xác nhận là hàm ý nguyên, CHƯA ĐO ĐƯỢC ≠ ÂM).
Thứ tự đọc: `01_CHAN_DOAN.md` → file này → `03_KE_HOACH_THU.md`. Mã mẫu: `ma_mau/kiem_hai_tang_mau.py` (7 test xanh).

## 1. Định nghĩa "tốt" theo tiền (một câu)

> Một phương pháp là **tốt** nếu **cận dưới** của tốc độ tăng trưởng log kỳ vọng `g` — ở đòn bẩy bị chặn bởi sụt giảm tối đa cho phép, sau phí đo được và stress ×1,5 spread + trượt 1 bps —
> **vẫn dương và hơn benchmark cùng rủi ro** (mua-giữ, và khi áp dụng được: carry, trend vol-target).

Cụ thể hoá để code được:

1. Chuỗi cơ sở = **PnL theo ngày** (không phải theo lệnh) của danh mục thật sự sẽ chạy (đã gộp lệnh chồng lấn, margin, swap).
2. `g(f) = E[ln(1 + f · r_ngày)]`, `f` = hệ số đòn bẩy. Chọn `f*` lớn nhất sao cho `P(maxDD > D_cap) ≤ ε` theo bootstrap khối của chính chuỗi (`D_cap`, `ε` do chủ dự án đặt; mặc định gợi ý 30 %, 5 %).
3. Cận dưới: phân vị 20 của `g(f*)` qua **stationary bootstrap** (≥ 2.000 lần; độ dài khối ≈ 2× thời gian giữ lệnh trung vị). Dùng cận dưới, không dùng điểm ước lượng.
4. "Cùng rủi ro" = cùng `f*` ứng với cùng `D_cap` cho benchmark; so `g_lower(hệ) − g(benchmark)` (hàm có sẵn: `nhan/cong.he_so_khop_rui_ro`, `khong_co_phan_bu_rui_ro`).
5. Chi phí: giữ nguyên ngưỡng đã có `edge_tren_spread_toi_thieu = 3`, `rr_thuc_te_toi_thieu = 0,2` (`config`/`MAC_DINH`).

Đây là Luật số 0 viết thành phép tính: **tiền ở cùng rủi ro**, p/MDE/placebo là nhãn kèm theo (xem 5).

## 2. Phễu 6 tầng

Mỗi tầng có: đầu vào, phép tính, tiêu chí qua, **loại sai chấp nhận** (để biết tầng nào nên chặt, tầng nào nên lỏng).

| Tầng | Việc | Phép tính | Qua khi | Sai chấp nhận |
|---|---|---|---|---|
| 0 Cơ chế | Gắn nhãn A/B/C: A = cơ chế kinh tế/hành vi rõ + bằng chứng ngoài mẫu dài (carry, trend đa tài sản, qua đêm/lịch); B = giả thuyết hợp lý; C = khai phá thuần | không chặn; chỉ đặt **prior** (xem 4.5) | luôn | — |
| 1 Sàng GĐ1 | Loại ô vô vọng, **xếp hạng**, chọn top-k | cạnh thô TRƯỚC phí ≥ 3× phí; hai nửa GĐ1 cùng dấu; n tối thiểu; xếp bằng ước lượng co rút (4.4), không dùng p | vào top-k (k ≤ 20/vòng, ghi trước) | lỏng: bỏ sót chấp nhận được |
| 2 Xác nhận GĐ2 | Kiểm đúng k ứng viên đã đăng ký trên dữ liệu chưa nhìn | `p_gom_cum` (4.1); hiệu chỉnh theo k (4.2); in MDE (4.3) | `p_hc < α` hoặc BH-FDR q | **FWER/FDR 5–20 %** |
| 3 Null cấp họ | Hỏi: "ô tốt nhất của CẢ lưới có hơn ô tốt nhất của lưới trên chuỗi chỉ-nhiễu?" | 4.6 | p_họ ≤ 0,10 (**nhãn**; không chặn) | nhãn |
| 4 MT5 tester | Tester TRƯỚC, Python SAU (luật cũ) | 4.8: khoảng dự đoán MT5 từ sổ cái 630 lần | cận dưới khoảng dự đoán 80 % của lãi ròng MT5 > 0 | trung bình |
| 5 Forward demo | Chạy thật trên tài khoản demo, **luật dừng định trước** | SPRT/e-process (4.9) | chạm biên chấp nhận, hoặc hết thời hạn → "chưa đủ" (không phải "âm") | **lỏng — demo rẻ** |

Nguyên tắc cân bằng sai lầm: vì demo không mất tiền thật và tầng 5 là trọng tài thật, **các tầng 2–4 nên dùng FDR 10–20 %**, không dùng FWER 5 % cộng dồn.
Một dương tính giả ở tầng 2 tốn vài tuần demo; một âm tính giả ở tầng 2 tốn cả một ý tưởng.

## 3. Hai điều kiện để hiệu chỉnh theo k (thay vì theo toàn bộ ô đã sàng) là hợp lệ

1. **Chọn chỉ bằng GĐ1**, danh sách k ứng viên + tham số + `plan_hash` ghi trước khi chạm GĐ2 (v31 đã làm đúng việc này).
2. **GĐ1 và GĐ2 đủ độc lập**: cắt có **embargo** ≥ thời gian giữ lệnh tối đa (v31: N = 24 nến) ở biên; lệnh mở ở GĐ1 không đóng ở GĐ2.

Nếu vẫn muốn "cộng dồn qua các vòng" thì cộng dồn **số phép kiểm xác nhận đã chạy trên cùng dữ liệu GĐ2** (vài trăm), không cộng số ô đã sàng (hàng chục nghìn).
Ở dạng dòng chảy vô hạn, dùng **LORD đã có trong `nhan/cong.py`** (`lord_v2`, ngân sách α hồi lại khi có phát hiện) thay vì Holm chia cho họ ngày càng lớn.
Ví dụ m = 300 → z = 3,59 (so với 4,57 của m = 20.503).

## 4. Thuật toán (công thức; cài đặt mẫu trong `ma_mau/kiem_hai_tang_mau.py`)

### 4.1 p gom cụm (thay `ttest_1samp` từng lệnh)
Cụm = tuần vào lệnh (hoặc ngày vào lệnh; **chọn cụm thô hơn khi lệnh kéo qua nhiều ngày**). Với `r_i` lệnh, `m = mean(r)`, `s_g = Σ_{i∈g}(r_i − m)`:

`SE = sqrt( G/(G−1) · Σ_g s_g² ) / n`,  `t = m/SE`,  `p = P(T_{G−1} > t)`  (một phía).

Khi mỗi cụm có đúng 1 lệnh, công thức trùng `scipy.stats.ttest_1samp` (có test). Báo thêm `deff = Var_cụm / Var_iid` — hệ số thổi phồng của t-test cũ.
Khi `G < 20`: dùng `p_boot` bootstrap theo cụm như `v24.py:76` làm kiểm chéo.

### 4.2 Hiệu chỉnh đa kiểm định
- Tầng 2: `holm_hai_tang(ps)` (Holm trên k ứng viên) hoặc `bh(ps, q)` (FDR). Mặc định gợi ý BH q = 0,10 cho tầng 2, Holm cho phát hiện cuối.
- Giữ cột `p_holm_cu` (họ 20.503) **song song** trong giai đoạn thử để so (xem 03).

### 4.3 MDE kèm mọi kết luận âm
`mde(sd, n, alpha, power, deff) = (z_α + z_β) · sd · sqrt(deff / n)`. Mỗi dòng "0 qua" in: n, sd, deff và MDE ở power 80 %.
Repo đã có đường đầy đủ hơn (`nhan/do_luc.py: mde_cua, luc_theo_do_dai, nam_can_de_thay`; `nhan/gop_lop.py: mde_gop`) — ưu tiên dùng chúng khi họ thuộc đường ống chuẩn, hàm mẫu chỉ cho các vòng `vNN.py` rời.
Nếu MDE > cạnh có thể tồn tại sau phí (≈ 10 bps tuỳ tài sản) → ghi **CHƯA ĐO ĐƯỢC (thiếu sức)**, không ghi "không có cạnh".

### 4.4 Xếp hạng co rút ở GĐ1 (thay xếp theo t thô)
Với ô `j` có trung bình `m_j`, sai số chuẩn `s_j` (gom cụm): ước lượng Bayes thực nghiệm `m̃_j = μ̂ + B_j (m_j − μ̂)`, `B_j = τ̂² / (τ̂² + s_j²)`,
`μ̂, τ̂²` ước theo DerSimonian–Laird trên các ô **cùng họ**. Ô có n nhỏ bị co mạnh về `μ̂` nên không thắng xếp hạng nhờ may mắn.
Quy tắc chọn top-k theo `m̃_j / sqrt(s_j² B_j)` hoặc theo `m̃_j` (ghi rõ trước).

### 4.5 Mô hình phân cấp theo tài sản (trả lời "cạnh có lan sang cặp anh em không", `KINH_NGHIEM.md` mục 16)
Với tài sản `a`: `m_a ~ N(μ, τ² + s_a²)`. Báo `μ̂`, `τ̂`, I² và `m̃_a`.
Đọc: μ̂ ≈ 0 và τ̂ lớn → cạnh riêng từng tài sản (AUDUSD kiểu may mắn một chuỗi); μ̂ > 0 và τ̂ nhỏ → cạnh chung, gộp n hợp lý.
**Prior theo nhãn cơ chế** (tầng 0): đặt `π_A, π_B, π_C` cho LORD có trọng số hoặc cho ngưỡng `nguong()`; giá trị gợi ý (chủ dự án chỉnh, mình chưa có căn cứ đo): 0,10 / 0,03 / 0,003.

### 4.6 Null cấp họ (max-statistic) — dùng đúng tốc độ mới
Thay vì Holm trên các ô phụ thuộc nhau: chạy **toàn bộ lưới** (cùng hàm sàng + cùng quy tắc chọn) trên N chuỗi null, lấy `max_j t_j` mỗi chuỗi, rồi
`p_họ = (1 + #{null ≥ that}) / (1 + N)` (`p_max_null`). Tự tính phụ thuộc giữa ô, không giả định độc lập.
Ghi chú tốc độ: `phan_tich_luoi_box.py` 38.736 ô D1 = 2,6 giây → N = 1.000 ≈ 45 phút. Với lưới H1 của v32 cần đo trước (việc T4).

**Null phải phá đúng bất đối xứng mà họ tuyên bố, giữ nguyên biến động và cấu trúc phí.** Bài học đã trả giá (`CLAUDE.md`, PMG): với tín hiệu hồi quy,
block bootstrap giữ trung bình khối nên nuốt mất tín hiệu → dùng **đảo dấu từng nến** (như G06) hoặc `nha_may_null.null_permute_time`; với tín hiệu xu hướng, đảo dấu cũng phá được.
Chọn null theo họ, ghi vào tiền đăng ký, KHÔNG đổi sau khi thấy kết quả.

### 4.7 Đánh giá cả họ bằng IC hạng (dừng quét khi họ trống)
`ic_hang(t_GĐ1, t_GĐ2)` = Spearman trên mọi ô có đủ lệnh ở cả hai giai đoạn. IC ≈ 0 và μ̂ ≈ 0 → xếp hạng GĐ1 không dự báo gì → **dừng cả họ**, không thêm ô.
IC > 0 có ý nghĩa nhưng không ô nào qua → có tín hiệu cấp họ, cần tăng n (gộp tài sản/khung) thay vì thêm lọc.
**Cảnh báo holdout**: tính IC trên mọi ô là *nhìn* GĐ2 của ô chưa đăng ký. Chỉ dùng làm **chẩn đoán họ đã đóng**; dữ liệu GĐ2 đó không được tái dùng để xác nhận (cần dữ liệu MỚI).

### 4.8 Mô phỏng → MT5 có độ bất định (dùng sổ cái 630 lần)
Từ `reports/mt5_lien_tuc/so_cai.jsonl` + `box_luoi_python.json` (589/630 khớp khoá; cùng dấu 93,9 %; tương quan PF 0,84): hồi quy
`net_MT5 = a + b · net_Python + ε`, báo `σ_ε`. Dự đoán MT5 cho ứng viên mới = **khoảng dự đoán**, không phải một số.
**Fit trên cả 630, không chỉ trên các ô được chọn vì tốt trong Python** (tránh hồi quy về trung bình bị bỏ sót). Kiểm hệ số b < 1 như dấu hiệu Python lạc quan (cùng hướng cảnh báo P1 của `nhan/luoi.py`).

### 4.9 Forward demo với luật dừng định trước
Chuỗi PnL ngày `x_t` của ứng viên trên demo; `σ` ước từ GĐ2; `e1` = cạnh nhỏ nhất đáng giao dịch (gợi ý: 2× phí lệnh); `α = 0,10`, `β = 0,20`.
SPRT: `Λ_t = Σ (e1/σ²)(x_s − e1/2)`; chấp nhận khi `Λ ≥ ln((1−β)/α)`, bác khi `Λ ≤ ln(β/(1−α))`; hết thời hạn trước khi chạm biên → "chưa đủ bằng chứng".
Giá trị gồm: giám sát liên tục không làm hỏng p (khác p-value cố định kích thước), và luật dừng khai báo trước. Lưu ý: SPRT giả định x_t độc lập — dùng chuỗi **ngày** và kiểm tự tương quan bậc 1.
Phương án thay thế khi cần chịu phụ thuộc/đọc liên tục: e-process (mixture martingale).

## 5. Vai trò của p, FDR, placebo, MDE sau đề xuất

| Cái gì | Vai trò |
|---|---|
| Lãi sau phí cùng rủi ro, cận dưới bootstrap (mục 1) | **Cổng cứng** — là câu hỏi tiền |
| Phí đo được, đủ lệnh, `rr ≥ 0,2`, cạnh ≥ 3× phí, không ăn khe giá | **Cổng cứng** (đã có) |
| p gom cụm + hiệu chỉnh theo k / BH | Cổng **xếp hạng/lọc tầng 2**, FDR lỏng |
| Null cấp họ (4.6), IC hạng (4.7), mô hình phân cấp (4.5) | **Nhãn + tín hiệu dừng/tiếp họ** |
| MDE | Bắt buộc **in kèm** mọi kết luận âm; kết luận thiếu sức = CHƯA ĐO ĐƯỢC |
| Forward demo (4.9) | **Trọng tài cuối** trước khi cân nhắc tiền thật |

## 6. Lưới / tỉa lệnh / martingale cần thước riêng
Payoff giống bán biến động (nhiều khoản lãi nhỏ, hiếm khoản lỗ rất lớn): Sharpe, Calmar, win-rate **chấm sai**. Với họ này bắt buộc:
CVaR 5 % của PnL ngày; thời gian dưới nước dài nhất; xác suất stop-out dưới stress (spread ×1,5, gap, biến động ×1,5) bằng `nhan/luoi_duong`;
và placebo **đảo dấu từng nến M1** (như G06 — đúng hướng). Ghi sẵn: P1 chỉ ra `luoi.chay` cũ lạc quan +1,1…+32,8 điểm %/năm ở ô có tỉa lệnh — mọi số lưới phải đến từ `luoi_duong`.

## 7. Cái KHÔNG đề xuất
- Không đổi cổng cứng về tiền, không nới `edge_tren_spread`, không bỏ stress ×1,5.
- Không đổi nhãn "MÔ PHỎNG" thành "ra tiền" trước tầng 4–5.
- Không áp thứ gì ở đây vào đường ống khi chủ dự án chưa duyệt (`README.md`).
