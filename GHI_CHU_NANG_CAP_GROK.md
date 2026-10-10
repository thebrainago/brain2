# Ghi chú nâng cấp (Grok trên brain2) — cập nhật 2026-10-11 (rạng sáng, giờ VN)

## Vòng "G07 — G-b: CHỌN TÀI SẢN (lưới có lãi trên tài sản hồi quy, không trên chỉ số?)" (sau d43e1f56) — 11/10/2026
**KẾ HOẠCH ĐÓNG BĂNG TRƯỚC KHI CÓ SỐ:** `hieu_chuan/G07_KE_HOACH.json` sha `eddb7e748b7924e9`. Không đổi cổng. Mọi số sẽ là MÔ PHỎNG.
- Gợi ý the-brain (PMG 14/09: AUDCAD/EURGBP 8/8, vàng 7/8, US100 0/8) chỉ là GỢI Ý — đo lại trên brain2.
- Cùng MỘT bộ luật lưới G06 (2023752: bước 21,2 pip ×1,2, lot cộng 0,25, TP 7,6, tỉa lệnh, 5 tầng, hai chiều), `luoi_duong`
  thứ tự `gan_open` trên M1 HistData (EST → giờ Helsinki), từng năm 2018–2025, vốn 10.000 USD mới mỗi năm.
- Tài sản: hồi quy = AUDCAD, EURGBP, XAUUSD; chỉ số = NSXUSD (NASDAQ 100), SPXUSD (S&P 500) — đều HistData miễn phí.
- Chuyển tham số (không tối ưu): giá nhân k_y = R_AUDCAD(y−1)/R_tài sản(y−1), R = trung vị biên độ ngày NĂM TRƯỚC (không nhìn
  trước); spread nhân cùng k. AUDCAD k = 1 (kiểm chéo với G06 từng năm).
- Phí: spread thấp/cao (AUDCAD 1,5/2,8 pip; EURGBP 1/2 pip; vàng 0,2/0,4 USD; NAS 1/2 điểm; SPX 0,4/0,8 điểm) + swap tháng
  (AUDCAD như G06; EURGBP r_EUR−r_GBP FRED + markup FXCE 22/08/2026; vàng ∓r_USD + markup FXCE; chỉ số GIẢ ĐỊNH ∓(r_USD±2,5 %),
  bỏ cổ tức). Biến thể chỉ báo: spread thấp không swap.
- Nhiễu: 20 chuỗi đảo dấu từng nến M1 / tài sản / năm (spread cao + swap); p hơn/kém nhiễu trên tổng các năm.
- Luật: LAI = tổng lãi biến thể xấu nhất > 0, mọi năm maxDD < 80 %, không stop-out. G-b ỦNG HỘ nếu mọi tài sản hồi quy LAI và hơn
  nhiễu (p ≤ 0,05) và không chỉ số nào LAI; BÁC BỎ nếu không tài sản hồi quy nào LAI hoặc không cái nào hơn nhiễu; còn lại MỘT PHẦN.
  Năm thiếu > 10 % nến so với trung vị bị loại; tài sản < 5 năm hợp lệ → CHƯA ĐO ĐƯỢC.
- **KẾT QUẢ (sau khi chạy, 805 lần, 29 phút; chi tiết `hieu_chuan/G07_KET_QUA.md`, `g07_ket_qua.json`): G-b BÁC BỎ (mô phỏng).**
  7 năm hợp lệ (2023 loại: HistData thiếu ~13 % nến). Năm lãi (xấu nhất có swap): AUDCAD 0/7 (trung vị −2,13 %/năm), EURGBP 1/7
  (−5,33), vàng 0/7 (−3,89), NAS100 0/7 (−5,11), S&P 0/7 (−11,97). maxDD ≤ 24 %, 0 stop-out. Luật chủ: 0/5 tài sản đạt.
  Hướng đúng nhưng yếu: cặp chéo hơn nhiễu (p 0,14 / 0,095), chỉ số kém nhiễu (S&P p 0,048); phần lợi < phí (AUDCAD không swap
  +0,21 %/năm). Vàng KHÔNG giống cặp chéo (kém nhiễu, 2025 −18,6 %). AUDCAD 2018 = G06 từng số (kiểm chéo).
- **Đọc cho việc tiếp:** swap + spread là thứ ăn hết phần hồi quy; muốn lưới cặp chéo ra tiền cần (a) chi phí thấp hơn đo được
  (sàn swap thấp / ECN — CHƯA ĐO ĐƯỢC, cần số sàn thật) hoặc (b) bộ luật quản lí khác (G-a / bóc thêm từ lịch sử lệnh 31 người thắng,
  cần chủ đăng nhập MQL5). Không nới cổng.

## Vòng "G06 — GIẢ THUYẾT CÓ CHỦ ĐÍCH: LÀM LẠI TÍN HIỆU AUDCAD 2023752" (sau 9c508edf) — rạng sáng 11/10/2026
Chi tiết: `hieu_chuan/G06_KET_QUA.md`. **Không đổi cổng.** Mọi số là MÔ PHỎNG.
- **Chọn:** trong 3 giả thuyết của 06 (G-a entry không quan trọng; G-b chọn tài sản hồi quy; G-c làm lại hệ đang lãi) chọn G-c
  trên tín hiệu 2023752 — luật đã được the-brain bóc sẵn (R6), không cần MT5/đăng nhập; G-c cho 31 ID khác cần chủ đăng nhập MQL5.
  Đối chứng nhiễu đảo dấu M1 = phép thử G-b ("hồi quy AUDCAD có giúp lưới không").
- **Đóng băng trước:** `G06_KE_HOACH.json` sha `c8c69e0f8483859b`, commit `07d2edcc` trước khi chạy.
- **Mã:** `luoi_duong.chay_duong(swap_nam=...)` swap theo lot mở qua rollover (mặc định tắt = giống hệt P1; `test_g06_swap_duong.py`
  3 test + 7 test cũ xanh); `config/lai_suat_aud_cad_thang.csv` (FRED); `hieu_chuan/g06_audcad_2023752.py` → `g06_ket_qua.json`.
- **Số (AUDCAD M1 HistData):** khám phá 2018-01→2023-07 lỗ ở cả 8 biến thể **−2,9…−3,4 %/năm** (không swap, spread 1,5: −1,07 %/năm),
  DD ≤ 19 %, 6/6 năm lỗ; 40 chuỗi nhiễu đều lỗ, p = 0,44 (không hơn nhiễu). Xác nhận 2023-07→2025-02 (trong đời tín hiệu) lãi
  +0,5…+2,3 %/năm. the-brain R6 báo +8,45 %/năm khám phá — **không tái lập được**.
- **Kết luận đóng băng: CHƯA ĐO ĐƯỢC** (HistData 2023 tháng 2–7 thiếu ~22 % phút); phần sạch 2018–2022 lỗ mọi năm → cài đặt này
  không phải cơ chế bền; ủng hộ "gặp may / hợp chế độ 2023–2026".
- **Việc tiếp:** muốn đi tiếp G-c thật cần lịch sử lệnh đầy đủ (chủ đăng nhập MQL5) để bóc luật còn thiếu; G-a để sau (không hướng tiền).


## Vòng "P3 — SWAP THEO TỪNG LỆNH + PHÍ ĐÚNG THỜI KỲ" (sau dc074dab) — rạng sáng 11/10/2026
Chi tiết + bảng: `hieu_chuan/P3_KET_QUA.md`. **Không đổi cổng duyệt.** Mọi số là MÔ PHỎNG, không phải tiền.
- **Sửa (mặc định trong `vong_thu_nghiem`, `--phi-cu` = mô hình cũ):** (1) swap chỉ tính cho lệnh còn mở qua rollover nửa đêm
  giờ server, thứ Tư ×3, T7/CN 0 (`chi_phi.dem_qua_dem`); (2) swap gắn vào TỪNG lệnh trong rổ (`chay_he`: vốn ròng = số dư +
  thả nổi − swap lệnh mở; stop-out chọn lệnh lỗ nhất tính cả swap) — đóng lỗi tồn "swap gắn số dư chung"; (3) tỉ lệ swap theo
  THÁNG = chênh lãi suất qua đêm USD−EUR (FRED, `config/lai_suat_qua_dem_thang.csv`) + markup XM đo 09/2026 (~1 %/năm mỗi chiều,
  GIẢ ĐỊNH không đổi); (4) spread theo NĂM khi bar có cột spread — dữ liệu EURUSD hiện có KHÔNG có → **CHƯA ĐO ĐƯỢC**, vẫn
  spread hôm nay cho 2003-2021 (lạc quan cho 2003-2010). Nhãn `mo_hinh_phi` trong JSON/báo cáo: `cp3` / `cp3+p3(...)`.
- **Kiểm:** mô hình cũ qua mã mới = giống hệt từng số dc074dab (tái cấu trúc trung tính). `test_p3_phi_thoi_ky.py` 16 test
  (×3 thứ Tư tính tay, lệnh trong ngày 0 swap, swap vào số dư khi đóng, stop-out do swap, phí tháng khớp phí sàn tháng đo…).
  20 file test liên quan: 289 xanh / 6 đỏ — 6 đỏ y hệt HEAD (`test_don_bay_va_carry`, thiếu nao.db).
- **Số đo EURUSD 2003-2021, phần kiểm 2016-2021:** Breakout5 lưới loi_log +6,67 → +7,57, vốn cuối 35.546 → 37.663 USD, DD vốn
  ròng 95,6 → 95,4 %, stop-out 9 → 7, p placebo 0,24 → 0,19 → **vẫn loại**; hedge B2/B3 swap 642 → 564 USD, lỗ −0,635 → −0,628;
  lệnh đơn đổi ≤ 0,005 log. **Giữ 0/6 trước và sau; đạt 25/09 0/6 trước và sau.** Mô hình mới hơi ít phí hơn → kết luận
  "không lợi thế sau phí" không đổi.
- **Chưa làm:** P4 (`hieu_chuan/p4_*`) đã đo bằng mô hình cũ — chưa chạy lại; `luoi_duong`/`luoi.chay` (P1) không có swap
  (so với tester vốn không ghi swap — đúng thước); quantlab/đường ống cũ vẫn `cp3`.
- **Việc tiếp:** giả thuyết 06 (gói the-brain); cài Đ1/Đ2 thành nhãn khi chủ dự án đồng ý; tìm nguồn spread lịch sử (Dukascopy
  ask/bid tick khi tải được) để đo spread theo năm.

## Vòng "P4 — ĐỐI CHỨNG NHIỄU + ĐỒNG DẤU VỚI MT5 + LUẬT LOẠI SỚM" (sau 22c68c55) — rạng sáng 11/10/2026
Chỉ ĐO + ĐỀ XUẤT. **Không đổi cổng duyệt.** Mọi số là MÔ PHỎNG (giá giả lập chỉ có nhiễu, hoặc so với tester MT5) — không phải tiền.
Chủ dự án (10/10): quan tâm DẤU (mô phỏng lãi mà MT5 lỗ = nguy hiểm), không quan tâm độ lớn.

- **Mã:** `hieu_chuan/p4_dau.py` (đồng dấu 15 ô P1 + luật loại sớm + đề xuất → `p4_dau.json`), `hieu_chuan/p4_nhieu.py`
  (A = đường ống `vong_thu_nghiem.chay_mot_file` thật trên 19 cơ chế `mau_thu` + `mo_rong`; B = quét lưới 72 ô kiểu the-brain,
  ô tốt nhất 60 % đầu → kiểm 40 % sau; R = luật R2 trên ô tốt nhất của B; ghi gộp, ghi nguyên tử → `p4_ket_qua.json`).
  `test_p4_nhieu.py` 6 test. Nhiễu: bước ngẫu nhiên ~5,5 %/năm (100 chuỗi, seed 1000–1099) + GARCH ~9 %/năm (50 chuỗi);
  A 9.600 bar H1, phí EURUSD thật, placebo 99 lần; B ~4 năm. A chạy lại 2 lần → kết quả GIỐNG HỆT (tất định).
- **Đồng dấu với MT5 (15 ô P1):** `luoi.chay` v3 25/30 biến thể cùng dấu, 5/30 ngược dấu — TẤT CẢ là lạc quan (mô phỏng lãi,
  tester lỗ; ô 1, 6, 11). `luoi_duong` 117/120 cùng dấu, 0 ô ngược dấu hoàn toàn; ô 4 lưng chừng (tester −0,1 %/năm ≈ 0).
- **Nhiễu lọt cổng (A, theo cơ chế):** cổng brain2 hiện tại 0/1900 (rw), 1/950 (garch; 016_CCI_2MAVG lệnh đơn, t 2,27/1,61).
  Nhãn 25/09 một mình: 434/1900 = 22,8 % (rw), 248/950 = 26,1 % (garch); **mỗi chuỗi nhiễu đều có ≥ 1 cơ chế “đạt 25/09”
  (100/100, 50/50)**. Theo loại: lưới (Breakout5) 72/100 và 31/50 đạt 25/09 trên nhiễu; hedge 104/300, 58/150; lệnh đơn
  258/1500, 159/750. Placebo p ≤ 0,05 một mình: 12/400 = 3 %, 7/200 = 3,5 % (≈ mức 5 % kỳ vọng). Lưới + placebo: 1/100, 0/50.
- **B (quét lưới kiểu the-brain):** ô tốt nhất qua 25/09 ngoài mẫu: luoi_duong 51/100 (rw), 19/50 (garch); v3 56/100, 31/50.
  Ô CHỌN BỪA: 44/100, 21/50 (duong) — **tối ưu ô không hơn chọn bừa** → lưới “qua” ngoài mẫu là đặc tính lưới, không phải lợi thế.
- **Luật loại sớm — số đo trên CẢ HAI nguồn:**
  | luật | 15 ô MT5 | nhiễu |
  |---|---|---|
  | R1 lãi mô phỏng ≥ 10 %/năm | v3 vẫn lọt ô 6 (ngược dấu) | 39/51, 52/56, 17/19, 31/31 ca “đạt” vẫn lọt → gần như không lọc |
  | R2 luoi_duong lãi > 0 ở biến thể XẤU NHẤT (4 thứ tự × spread 1,5/2,5) | giữ 2, 8, 15 = đúng 3 ô tester lãi; 0 lọt, 0 chặn oan | 51→44/100 (rw), 19→17/50 (garch): chỉ chặn ~12 % |
  | R3 maxDD mô phỏng ≤ 60 % | không loại ô nào (DD tester ≤ 33 %) | trong mẫu DD > 60 % → ngoài mẫu hỏng: 4/13 vs 36/87 (duong rw) — không nhất quán |
  | Placebo cùng cấu trúc p ≤ 0,05 (cổng brain2 đã có) | CHƯA ĐO ĐƯỢC (15 ô không có tín hiệu vào) | lưới 72→1/100, 31→0/50; hedge 104→11/300 |
- **ĐỀ XUẤT (chưa áp):** (Đ1) lưới: dùng luoi_duong, lãi ở biến thể xấu nhất > 0 — chống NGƯỢC DẤU với MT5 (bằng chứng 15 ô);
  (Đ2) lưới/hedge đạt 25/09 vẫn phải thắng placebo cùng cấu trúc — chống NHIỄU (bằng chứng nhiễu; Đ1 không làm được việc này);
  (Đ3) lệnh đơn: giữ ngưỡng t (25/09 một mình để lọt 17–21 % nhiễu, ngưỡng t ≤ 0,13 %). MT5 cho lệnh đơn: CHƯA ĐO ĐƯỢC.
  Không đề xuất R1/R3: số đo không ủng hộ. Kết luận cho chủ dự án: “25/09 một mình” để nhiễu lọt quá nhiều → không nên
  thay cổng hiện tại bằng 25/09; nên GIỮ 25/09 + thêm Đ1 + Đ2 khi có quyết.
- **Giới hạn:** chỉ 2 cặp × 6 tháng MT5 (15 ô, đều lưới ThamSo); nhiễu là giá giả lập — không có lợi thế thật để đo độ nhạy
  (luật chặn nhiễu cũng có thể chặn cái thật: CHƯA ĐO ĐƯỢC). `reports/VONG_DAY_DU.json` bị chạy đo làm bẩn → đã khôi phục.
- **Việc tiếp:** P3 (swap theo từng lệnh + phí đúng thời kỳ); cài Đ1/Đ2 thành nhãn trong `vong_thu_nghiem` khi chủ dự án đồng ý.

## Vòng "P1 — MÔ PHỎNG LƯỚI SO VỚI 15 Ô MT5 TESTER" (gói bàn giao the-brain, sau c94ed9e8) — khuya 10/10/2026
Chi tiết + bảng 15 ô: `hieu_chuan/P1_KET_QUA.md`. Không nới cổng giữ. Mọi số là MÔ PHỎNG so với TESTER, không phải tiền thật.

- **Vì sao (hướng tiền):** trước khi tin bất kỳ số lãi lưới nào của brain2 (đưa lên demo), phải biết mô phỏng lệch
  MT5 bao nhiêu. Đáp án có sẵn: 15 ô H1 sạch (AUDCAD 8 + NZDCAD 7, 2019-03..08) từ gói the-brain → `hieu_chuan/p1_15o_tester.csv`.
- **Giá:** HistData M1 BID công khai (EST cố định → giờ Helsinki), gộp H1; USDCAD để đổi CAD→USD từng nến. Dukascopy hôm
  nay hết thời gian TLS từ máy này → bỏ (ghi lại). Spread chưa đo được → chạy 1,5 và 2,5 pip.
- **Kết quả `nhan/luoi.chay` (v3, nguyên trạng):** lạc quan 11/15 ô; có tia **+1,1…+32,8** điểm %/năm (ô 6: tester −10,8 %/năm,
  v3 +12…+22 — lỗ thành lãi), không tia −5,1…+5,9 (trung vị +2,0); maxDD thấp hơn tester 13/15 ô; hạng Spearman 0,70.
  Hai nguyên nhân đo được: tia chốt ở CỰC TRỊ nến; lot hệ số < 1 không làm tròn 0,01 như MT5.
- **Mới: `nhan/luoi_duong.py`** (`test_luoi_duong.py` 7 test): luật EA lưới đầy đủ, khớp tại ngưỡng, spread một lần/lệnh,
  lot làm tròn, 4 thứ tự giá trong nến + chạy được trên M1. Chênh có tia −2,6…+4,3, không tia −9,5…+6,1 (trung vị ≈ +0,2),
  Spearman 0,96, maxDD/số lệnh gần tester. Thứ tự nến đổi ≤ 1,8 điểm; spread đổi tới 6,7 điểm (ô 7) → sai số chính là SPREAD.
- **Gắn cảnh báo:** `luoi.CANH_BAO_P1` + `chi_so()["canh_bao_mo_phong"]`; `vong_thu_nghiem` in dòng
  "mô phỏng lệch so với MT5: CHƯA ĐO ĐƯỢC cho rổ EA này" cạnh mọi hệ có rổ (Breakout5/hedge dùng `mo_phong.chay_he`, luật
  thoát khác 15 ô → chưa có đáp án MT5).
- **Nhãn 25/09 (chủ dự án chốt 10/10: lãi sau phí + maxDD < 80 %, đòn bẩy ổn nếu không cháy):** `vong_thu_nghiem.nhan_25_09`
  in "đạt tiêu chí 25/09?" cạnh mọi cơ chế; maxDD đòn bẩy 1 (lệnh đơn) hoặc tài khoản khai báo (rổ). CHỈ LÀ NHÃN —
  cổng t/placebo/cháy giữ nguyên vòng này (chưa có số đo P4 về tỉ lệ nhiễu lọt qua cổng 25/09). EURUSD Dukascopy 2003–2021,
  có phí: **0/6** cơ chế đạt 25/09 (Breakout5: maxDD 96 % + stop-out; còn lại lỗ sau phí) — cùng kết quả với cổng cũ.
- **Việc tiếp:** P4 (tỉ lệ chuỗi chỉ-nhiễu qua cổng 25/09 → quyết đổi cổng bằng số đo), P3 (swap theo từng lệnh), chuyển
  các script lưới cũ (`_luoi_audcad*`) sang `luoi_duong`.

## Vòng "CAUKHO TRONG dieu_phoi + NÂNG LỆNH VÀO LÊN CHỖ GỌI HÀM PHỤ" (sau 9aa53d77) — khuya 10/10/2026
Không nới cổng giữ, không đụng `_Point` của Breakout4. Bộ 160 EA Code Base dùng làm PHÉP ĐO, không phải đáp án.

### 1. Nối vào `dieu_phoi` — trụ mới `CAUKHO` (`tru/cau_kho.py`, `test_tru_cau_kho.py` 6 test)
- `dieu_phoi.TRU["CAUKHO"]`: ngân sách 360 s, chu kỳ 6 giờ, nhóm `kham_pha`, **lane riêng `ma_nguon`**
  (giới hạn 1) → chạy CẠNH SEEKER, không chiếm lượt `external` của SEEKER/NGHI, không dùng profile
  trình duyệt. EVO theo dõi sống/chết (`TRU_CAN_SONG`, hạn im lặng 18 giờ).
- KHÔNG cần `nao.db` có dữ liệu: nguồn chính là `tai_mql5` (bộ tải của SEEKER). Mỗi lượt tải trang 1
  (bài mới) + MỘT trang sâu theo con trỏ `TRANG_SAU.json` (kho lớn dần ngược thời gian, tới trang 60),
  trần thời gian tải `BRAIN_CAU_KHO_GIAY_TAI` (mặc định 180 s; `tai_mql5(han_giay=..)` dừng và ghi
  `het_gio`). Nếu sổ cái có artifact mã (máy Windows) thì gom thêm `--tu-so`.
- Đọc qua bộ nhớ đệm `bo_nho_doc.json` khoá theo vân tay NỘI DUNG + vân tay MÃ bộ đọc
  (`cau_kho_ma.phien_ban_bo_doc()` = sha1 của doc_ma/chot_mql/fss_mql/goi_ham_mql/ro_mql/ngu_phap/…):
  file cũ + bộ đọc cũ không đọc lại; sửa bộ đọc → đọc lại cả kho. Test: số đo qua bộ nhớ GIỐNG HỆT đọc lại.
- Ghi trong `data/cau_kho/` (git bỏ qua): `mql5/`, `BAO_CAO.md`, `lich_su.jsonl` (mỗi lượt một dòng
  phễu + tỷ lệ + phiên bản bộ đọc), `ea_ra_co_che/` + `NGUON.json` cho
  `python vong_thu_nghiem.py --mau data/cau_kho/ea_ra_co_che`; chỉ số `cau_kho_ty_le_dich` vào sổ cái.
- Mạng hỏng → `tai.loi` (dieu_phoi xếp `degraded`, không `error`), vẫn đo lại kho đang có.
- Đo thật trên box qua `dieu_phoi.chay_tru("CAUKHO")`: status `ok`, 13,4 s lượt đầu (liệt kê 2 trang
  thật từ mql5.com), 2,6 s lượt sau (117/117 từ bộ nhớ).
- `test_dieu_phoi_control` (scheduler): cửa sổ 0,06 → 0,1 phút vì 6 trụ / 3 worker / vòng 2 s.

### 2. Lỗi #1 "không tìm được guard": `nhan/goi_ham_mql.py` (`test_goi_ham_mql.py` 19 test)
Lệnh vào trong HÀM PHỤ (`void OpenBuy(){ trade.Buy(..); }` gọi từ `if(rsi<30) OpenBuy();`) được NÂNG
lên chỗ gọi, chỉ khi đồ thị gọi nhỏ và giải trọn vẹn: hàm tự do (tìm theo ngoặc, không theo regex kiểu
trả về), định nghĩa 1 lần, gọi từ ĐÚNG 1 chỗ dạng lệnh đơn (`F();`, `x=F();`, `if(F())`, `if(!F())`),
không trong for/while/switch/else, không return lồng có điều kiện, chuỗi ≤4 tầng tới `OnTick`
(OnChartEvent/OnTimer → từ chối). Điều kiện vào chỉ được ở MỘT tầng (if bao HOẶC thoát sớm); tầng khác
chỉ được là quản trị/kiểm lỗi API (ghi `bo_qua_quan_tri`) — hai tầng có điều kiện → từ chối (biến cục
bộ tầng này không giải được ở vị trí tầng kia). Dịch điều kiện dùng lại nguyên đường cũ của doc_ma.
Test tương đương: bản hàm phụ / hai tầng / chỉ thoát sớm trong `ulong DoBuy()` ra ĐÚNG `vao` như bản
viết thẳng trong OnTick. 11 test từ chối có lý do (2 chỗ gọi, else, vòng for, OnChartEvent, phương thức
lớp, hai tầng, biểu thức ghép, `?:`, overload, đệ quy, không có điều kiện vào).

Sửa kèm (đều tương đương logic hoặc sửa lỗi gán sai hàm, không nới):
- `_KHAI_HAM` thêm `ulong/uint/float/char/short/color/ENUM_*`: trước đó lệnh vào trong `ulong Open..()`
  bị gán cho HÀM TRƯỚC → `return(INIT_SUCCEEDED)` của OnInit biến nó thành "mã chết" SAI.
  `_ma_chet` còn kiểm thân hàm phải bao lệnh vào. Trên 160 EA: mã chết 7 → 4 (3 phân loại sai được gỡ).
- `if(A or B) return;` tách thành hai thoát sớm (tương đương logic) để vế quản trị (`HasOpenPosition()`)
  bỏ qua có ghi, vế tín hiệu dịch riêng. `mot_lenh_ngay` vẫn đọc dạng gốc (test Breakout1 giữ nguyên).
- Hàm của tác giả CHỈ hỏi vị thế/lệnh (`HasPos()`, `CountPositions(..)`: thân chỉ gọi Position*/Order*
  API, không giá/chỉ báo/đặt lệnh/hàm khác) = điều kiện quản trị như `cntBuy==0` (`_ham_hoi_vi_the`).

### Số đo (cùng 160 EA `/workspace/seeker_mau/mql5`, `reports/CAU_KHO_MA.md`)
| | trước (9aa53d77) | **bây giờ** |
|---|---|---|
| điểm vào dịch được | 1/240 = 0,4% | **1/240 = 0,4%** |
| mã chết | 7 | 4 (3 cái cũ là gán nhầm hàm) |
| "không tìm được guard" (lý do, theo file) | 63 | 20 (còn lại: chiều lệnh qua biến, lớp/struct, …) |
| `mau_thu` / `mo_rong` / gộp | 13/22 · 13/34 · 26/56 | **giống hệt** (toàn bộ `co_che` so JSON: chỉ khác chữ `bo_qua_quan_tri` tách `c1 == 0`, `c2 == 0`) |

Tỷ lệ KHÔNG tăng, nói thẳng: việc nâng thành công tới tầng điều kiện ở 8 điểm vào / 7 EA, nhưng cả 8 bị
từ chối Ở BƯỚC DỊCH vì lỗ khác (đúng — không đoán): getter chỉ báo bọc hàm (`GetRSI(1)` →
`ReadBufferValue` → CopyBuffer), biến bool từ hàm tín hiệu (`signal = SellSignal()`), giờ từ
`TimeToStruct(iTime(..,1))`, kiểm `EMPTY_VALUE`, giới hạn lỗ ngày/drawdown (`XP_CheckDailyLossLimit()`).
Các lệnh còn lại dừng ở lý do cụ thể hơn: gọi từ 2–5 chỗ (OR nhiều điều kiện, 15 lượt-file), điều kiện ở hai
tầng (11), return lồng (8), lớp/struct (3), else (5), vòng for (4) — đếm theo lý do×file. Ký quỹ (`!CheckMargin(..)`) vẫn
từ chối như ở đường trực tiếp (không coi là quản trị — giữ quy ước cũ).

### Còn chặn (ưu tiên vòng sau, theo số đo)
1. Getter chỉ báo bọc hàm (`double GetRSI(int s){ return Read(h,0,s); }`) — nội tuyến được khi thân
   chỉ là CopyBuffer một handle đã biết; mở khoá 77738 (RSI exhaustion) nếu kèm giờ `TimeToStruct`.
2. Hàm vào lệnh gọi từ nhiều chỗ với chiều khác nhau (`ExecuteTrade(ORDER_TYPE_BUY)` /
   `(ORDER_TYPE_SELL)`) — tách theo chiều như `_chuoi_chieu`, từ chối khi hai chỗ cùng chiều.
3. Nhánh `else` (17 + 4 qua chỗ gọi) — cần phủ định điều kiện chứng minh được.
4. Chạy `CAUKHO` trên máy Windows (có `--tu-so`, 1.308 bản mã) để có mẫu lớn hơn 160.


## Vòng "SEEKER → doc_ma: CẦU KHO MÃ" (sau 055ec9be) — khuya 10/10/2026
Không đổi `doc_ma`, không nới cổng giữ. Chỉ nối đầu vào.

### SEEKER đã làm gì (đọc từ repo, số trên máy Windows của chủ dự án — `nao.db` ở đây trống)
- `tru/seeker.py` (2.647 dòng, chạy trong `dieu_phoi` chu kỳ 900 s, ngân sách 420 s): quét ~20 nguồn
  (arxiv, OpenAlex, Crossref, Semantic Scholar, GitHub, MQL5 Code Base có phân trang + con trỏ,
  TradingView Pine qua suggest-json, StackExchange, HN, QuantConnect, FX Blue, eToro, RSS, trình duyệt CDP,
  Telegram), khử trùng theo vân tay, đọc toàn văn, ghi `DocumentArtifact`/`CodeArtifact` (hop_dong V2).
  Ranh giới V2: SEEKER không gọi LLM, không sinh cơ chế.
- `reports/SEEKER.md` (lần cuối commit 14/09/2026 20:49): mục lục **11.856** tài liệu (A 844, B 7.195,
  C 3.449), **7.975** bản đọc / 82,0 triệu ký tự, trong đó **1.308 bản `ma_nguon`** (27,6 tr ký tự);
  **8.095** DocumentArtifact; 1.682 chờ đọc; 231 không đọc được + 406 hỏng; **705** candidate chờ Quantlab
  (do tầng phân tích tạo). Commit cuối vào `tru/seeker.py`: 15/09/2026.
- Hạ nguồn của kho mã TRƯỚC vòng này chỉ có 2 đường: `bien_dich_ung_vien` (khớp TỪ KHOÁ vào mẫu có sẵn)
  và `boc_ma_llm` (LLM; `phan_loai_ma` đo 05/09: 389 artifact mã → 82 chiến lược, LLM ra cơ chế ~32%).
  **Bộ đọc cấu trúc `doc_ma` (59,1% / 38,2% trên mẫu) chưa từng chạy trên kho SEEKER**, và
  `vong_thu_nghiem.py` chỉ đọc `mau_thu/` → vòng "quét → bóc → kiểm → giữ" đứt ngay khâu đầu.

### Thay đổi: `nhan/cau_kho_ma.py` (+ `b cau-kho`, `test_cau_kho_ma.py` 10 test)
1. GOM: `--tu-so` (artifact `code` + `noi_dung` kiểu `ma_nguon*` có dấu hiệu MQL; chỉ ĐỌC nao.db),
   `--thu-muc DIR`, hoặc `--tai-mql5 DIR` = quét MQL5 Code Base bằng CHÍNH bộ tải của SEEKER
   (`ma_nguon.liet_ke_mql5/tai_ma_nguon`, file đơn, không zip), bỏ bài đã có, provenance `NGUON_TAI.json`
   → chạy được trên Linux/cloud không cần nao.db.
2. KHỬ TRÙNG theo vân tay NỘI DUNG (bỏ chú thích + khoảng trắng); file trùng `mau_thu/` không đếm lại.
3. PHÂN LÀN (`phan_loai_ma`) + bỏ MQL4 có ghi lý do + `doc_ma.doc_chien_luoc` trên mọi EA đặt lệnh;
   số đo CÙNG định nghĩa `do_moc` (test khớp đúng số gộp 26/56 của `do_moc_rong --gop`).
4. XUẤT EA ra ≥1 cơ chế sang `--xuat DIR` + `NGUON.json` → `python vong_thu_nghiem.py --mau DIR`.
   Lỗi bộ đọc (exception) được đếm riêng `loi_bo_doc`, không nuốt.

### Số đo THẬT trên đầu vào SEEKER (MQL5 Code Base, 160 EA mới nhất mục experts, tải 10/10/2026)
`reports/CAU_KHO_MA.md`. 160 file → 2 trùng nội dung → 158 duy nhất, 0 MQL4; làn: chiến lược 63,
quản trị 59, tiện ích 34, chỉ báo 2; 117 EA đặt lệnh, 95 có điểm vào, **240 điểm vào → dịch được 1
= 0,4%** (EMA_Cross_EA5, giao cắt EMA9/21 đúng chiều — đã kiểm tay mảng không-series). 120 EA đầu: 1/156 = 0,6%.
Lý do hàng đầu: 63× "không tìm được guard của lệnh vào" (lệnh nằm trong hàm phụ/biến trạng thái),
16× "lệnh vào trong nhánh else", 5× `type == ORDER_TYPE_BUY` (chiều qua biến), 5× mã chết.
Vòng có phí (EURUSD Dukascopy H1 2003–2021) trên 1 EA xuất ra: **giữ 0** (t tối ưu −1,3 / kiểm −1,7).
Kết luận trung thực: 59,1%/46,4% trên mẫu **không tổng quát hoá** sang EA hiện đại của Code Base
(0,4%). Đây giờ là thước đo tổng quát hoá chính cho `doc_ma` (không dùng làm đáp án để chỉnh cho vừa).

### Còn chặn
- Chưa chạy `b cau-kho` (= `--tu-so`) trên nao.db thật (1.308 bản mã) — cần chạy trên máy Windows.
- `doc_ma`: guard qua hàm phụ (`OpenBuy()` gọi từ `OnTick` theo biến tín hiệu), chiều lệnh qua biến
  (`trade.PositionOpen(_Symbol, type, ...)`), nhánh `else` — là ba lỗ lớn nhất trên đầu vào thật.
- ~~Chưa nối vào `dieu_phoi`~~ — đã nối (trụ `CAUKHO`, vòng sau). Bài tải hỏng không tự thử lại (ghi `ok:false`).
- `test_kien_truc::test_moi_thu_muc_that_deu_da_duoc_khai` đỏ do thư mục ngoài repo trong /workspace
  (venv, du_lieu_fx…) — môi trường box, có từ trước.


## Vòng "CHỐT TĨNH (016) + MẪU FOREX STRATEGY STUDIO (EMA Crossover)" (sau 074c67e7) — tối 10/10/2026
Không nới ngưỡng giữ (t ≥ 2,0 tối ưu / 1,5 kiểm, ≥47/≥20 lệnh). Chỉ dịch khi CHỨNG MINH được máy
trạng thái/lối ra; mọi trường hợp khác trả lý do vào `chua_dich` (không đoán).

### Số đo
| | trước (074c67e7) | **bây giờ** |
|---|---|---|
| `mau_thu` (10 EA, 22) | 13/22 = 59,1% | **13/22 = 59,1%** (đầu ra đọc giống hệt) |
| `mau_thu/mo_rong` (15 EA, 34) | 9/34 = 26,5% | **13/34 = 38,2%** (tín hiệu thành nến 12/33 = 36,4%) |
| gộp (25 EA, 56) | 22/56 = 39,3% | **26/56 = 46,4%** (tín hiệu thành nến 20/43 = 46,5%) |
| lối ra theo EA (mo_rong) | 10/10 | **14/14** (sltp 10, điều kiện ra 2, pip tick đầu 2) |
| lối ra theo EA (gộp) | 24/24 | **28/28** |

Minh bạch: EMA Crossover có 2 "điểm vào" trong mẫu số, nhưng điểm thứ 2 là `OrderSend` ĐÓNG lệnh trong
`closePosition` (đếm sai từ trước, giữ nguyên mẫu số) → tính `quan_ly_dich_duoc`. Tín hiệu vào mới
thật sự của vòng này: 016 mua+bán (2) + EMA Crossover mua+bán (1 điểm vào chung).

### 1. `chot_cap` + `nhan/chot_mql.py` (016_CCI_2MAVG)
- Mẫu: hai `static int A=0,B=0` gán ±1 trong các if sự kiện (trước điểm kiểm), cổng bar mới đã xác
  minh (static datetime + iTime), `if(A!=0 && A==B){ if(F(A)>0){A=0;B=0;} }` với F chỉ rẽ `p<0`/`p>0`.
  Bất kỳ lệch nào (for/while/else/return, gán ngoài if sự kiện, nhiều điểm gọi, biến không static...)
  → `{"loi": "chot: ..."}` → chua_dich.
- DSL: toán hạng `{"chi_bao":"chot_cap","dat":[{"bien","gt","khi"}...],"kiem":["a","b"]}` áp phép gán
  theo thứ tự nguồn mỗi bar, ra ±1 khi khớp rồi reset. `{"hang_co_dinh": v}` = hằng KHÔNG tối ưu
  (hằng số cứng của EA, tránh `_ung_vien` coi 0..23 là giờ).
- `CloseTrades(POSITION_TYPE_X)` trong if sự kiện (hàm đóng lọc đúng loại) → `ra` của chiều đó.
- Giả định ghi `gia_dinh`: vế so sánh tự đồng nhất của EA (`fastMA2 = MAVG2_Buffer[2]` → `<=` luôn
  đúng) bị bỏ như EA thực thi.
- Đối chiếu: cổng OnTick viết tay trên EURUSD H1 thật: vào 698/730, đóng 8728/8397, 0 lệch; thử cắt
  cụt (không nhìn trước).

### 2. `nhan/fss_mql.py` (EMA Crossover, mẫu Forex Strategy Studio) + chế độ `dong_mo_pip`
- Nhận mẫu bằng so khớp NGUYÊN VĂN (bỏ khoảng trắng/chú thích) các hàm khung (booleanToAction,
  actionAverage, ActionFromValue, calcMovingAvg đọc `shift+1` = bar đã đóng, decideIfClosePosition
  PIPS, openPosition không sl/tp, closePosition). Cấu hình tĩnh gán đúng 1 lần; phiếu mua/bán phải loại
  trừ nhau chứng minh được. Lệch → không nhận.
- Lối ra: `dong_mo_pip={"tp_pip":20,"sl_pip":100,"pip_theo_ten":[["JPY",0.01],["BITCOIN",0.1]],
  "pip_mac_dinh":0.0001}`; `mo_phong.chay_he` kiểm ở tick đầu bar (giá mở) so với giá khớp (mua
  khớp ASK), không vào lại cùng tick vừa đóng. `dong_mo_pip` không ghép với sltp/rổ/trong_bar/
  dong_mo_bar/ra. Giả định: Strategy Tester tính iMA đồng bộ.
- Đối chiếu cổng tham chiếu: 266/266 lệnh khớp (EURUSD pip 0,0001; USDJPY pip 0,01).

### 3. vòng CÓ phí — giữ 0
- mo_rong EURUSD H1 (17.127 bar): EMA Crossover t kiểm +1,2/−0,9; 016 bán −0,2/+0,7; 016 mua +0,1/−0,6.
- mo_rong Dukascopy 2003–2021 (116.175 bar): EMA Crossover −2,2/−2,1; 016 bán +0,4/−1,0; mua −0,4/−1,7.
  Cơ chế cũ không đổi số (013 mua −8,3/−7,4; 015 bán +1,9/+0,5).
- mau_thu H1: 7 đọc, 1 trùng, 6 chạy, giữ 0.

### 4. Test
`test_chot_cap.py` (12), `test_fss_mql.py` (7): đọc đúng, khớp từng bar/lệnh với cổng tham chiếu,
không nhìn trước, các ca TỪ CHỐI (shift+1→shift, tpValue gán lại, phiếu không loại trừ, closeType khác,
biến không static, else, gán ngoài if...). `test_ngu_phap_toan_hang` thêm mẫu đối số `chot_cap`.
Không có lỗi mới so với 074c67e7 (lỗi `test_van_con_phan_biet_duoc_hai_loai_thieu` có sẵn từ trước).
Đã thử bỏ phơi `giu` khi spec có `ra` (vô tác dụng trong `sinh_tu_spec`) nhưng test khoá hành vi cũ
→ hoàn lại; tối ưu `giu` vô hại vì bước toạ độ chỉ nhận cải thiện thực sự.

### 5. Bỏ qua có lý do (chưa dịch)
- **019 (iADX/DI±)**: mọi điều kiện đọc buffer [0] ở tick đầu bar mới (H=L=C=open) → cần đánh giá chỉ
  báo tại tick mở, ADX không đơn điệu; iADX MT5 = EMA 2/(n+1) của tỉ lệ DM/TR (không phải Wilder).
  Đề xuất: toán tử "tick đầu" — nhưng sẽ rò rỉ trong đường `sinh_tu_spec`/`MP.chay` chung, cần thiết kế riêng.
- **Box Breakout**: hộp giá dựng từ TimeCurrent/iBarShift; H1 barCount=1 → hộp là bar 03:00 còn sống
  03:30–04:00; `ask > high` kích bởi spread → phụ thuộc khung, cần tick.
- **Viprasol**: iADX MT5 + RSI + phiên + lọc spread theo `_Point` + hoà vốn/trailing theo điểm + khối
  lượng theo rủi ro + giới hạn lệnh/ngày.
- **018**: lệnh dừng theo ASK, reset chéo, đóng bar mới nếu lãi>0 hoặc tuổi ≥ OldBarIndex, không giới hạn vị thế.
- **05 / 014**: RSI(PRICE_OPEN)[0] sống + MA khung khác trong EA chỉ chạy bar mới — không giả.
- **Basic_Bollinger_Bands**: thiếu include Trail.mqh/NewC.mqh, input mặc định 0 (khối lượng 0), vào ở nhánh else cấu hình.
- **01_RSI_V1**: handle bị che (shadowed). **Breakout4**: vẫn không đoán `_Point`/PivotsDay.

### Còn chặn
Toán tử tick đầu (019/05/014), iADX kiểu MT5, khung thời gian/tick (Box Breakout), quản trị theo
điểm/rủi ro (Viprasol), lệnh dừng + nhiều vị thế (018), mẫu số đếm OrderSend đóng lệnh là điểm vào.

## (trước) Vòng "SL/TP ĐẶT TRỰC TIẾP Ở LỆNH VÀO (bộ mo_rong) + `--diem`" (sau 95a59074) — khuya 10/10/2026
Không nới ngưỡng giữ (t ≥ 2,0 tối ưu / 1,5 kiểm, ≥47/≥20 lệnh, cổng tài khoản/placebo/cháy).
Breakout4 vẫn bỏ qua (không đoán `_Point`/PivotsDay).

### Số đo
| | trước (95a59074) | **bây giờ** |
|---|---|---|
| `mau_thu` (10 EA, 22 điểm vào) | 13/22 = 59,1% | **13/22 = 59,1%** (đầu ra `doc_chien_luoc` giống hệt từng byte) |
| `mau_thu/mo_rong` (15 EA, 34) | 9/34 = 26,5% | **9/34 = 26,5%** |
| gộp (25 EA, 56) | 22/56 = 39,3% | **22/56 = 39,3%** |
| **lối ra theo EA** (mo_rong, 10 cơ chế) | 0/10 (giữ cố định `giu` bar) | **10/10** (sltp=10; đóng theo mức=2; giả định `_Point`=6) |
| lối ra theo EA (gộp, 24 cơ chế) | 14/24 | **24/24** (sltp=14, rổ=10) |

Tỷ lệ bóc tách điểm vào KHÔNG đổi — vòng này dịch LỐI RA (trước đây kết quả mo_rong chỉ là của điểm
vào + giữ N bar, không phải EA). `do_moc*.py` in thêm dòng "loi ra theo EA".

### 1. Đọc SL/TP trực tiếp (`nhan/doc_ma._sltp_truc_tiep`)
- `PositionOpen(.., gia, SL, TP, ..)` / `trade.Buy/Sell(lot, sym, gia, SL, TP)`; truy biến SL/TP về
  phép gán cuối trên đường đi (`_gan_tren_duong`, kể cả khối if/else-if gán chiều kiểu 015).
- Dạng nhận (chỉ khi chắc): `ASK/BID ± N*_Point` (`_Point`, `Point()`, `SYMBOL_POINT`; N = số/input)
  → `sl_diem/tp_diem` + `ref_sl/ref_tp` (giá gốc EA dùng: 011/013 lấy BID cho mua, 012 lấy ASK);
  `ASK/BID ± ATR*k` → `sl_kc/tp_kc` (chỉ ATR); SL = mức chỉ báo + `TP = gia + R*(gia - SL)` → `sl`
  mức + `tp` R (015). Khác → giữ `giu`, ghi lý do (không đoán).
- Chuẩn hoá thêm chế độ `tach_ask_bid` (token `_ask0_/_bid0_` CÙNG độ dài `_gia0_` để vị trí khớp).
- Đóng lệnh ở tick đầu bar (`_dong_mo_bar_mql`, 013): `if(cntBuy>0 && bid>=BB_Base[0]) ClosePositions(1)`
  sau lệnh vào cùng hàm, EA cổng IsNewBar, hàm đóng lọc đúng loại → khối `dong_mo_bar`.
- **Sửa lệch 1 bar** (`_toan_hang`): chỉ báo có dịch (`bands_shift`/`ma_shift` = s) đọc buffer bar 0
  = giá trị tính tại bar MQL5 s → trễ s−1 (trước: trễ s, tức bollinger(i−1) thay vì bollinger(i)).
  Test cũ khoá sai đã sửa trong `test_doc_ma_mo_rong.py`.

### 2. DSL + mô phỏng
- `ngu_phap`: `sltp.mt5` (≤1 kiểu SL, ≤1 kiểu TP, ref ASK/BID bắt buộc với khoảng cách), `dong_mo_bar`;
  `tham_so_cua` phơi `sltp_sl_diem/tp_diem` + mức đóng; `sinh_chan` truyền qua.
- `mo_phong.chay_he` chân `mt5`: giá dữ liệu = BID, ASK = BID + spread bar vào; lệnh BÁN đóng khi ASK
  chạm (quy về BID: mức − spread); MT5 từ chối lệnh khi SL/TP sai phía (STOPS_LEVEL giả định 0);
  không SL/TP/đóng-mức thì mới dùng `giu`. `dong_mo_bar` kiểm ở tick đầu, SAU lệnh vào cùng tick, và
  không vào lại cùng tick vừa đóng (như EA đếm cntBuy).

### 3. Vòng lặp (`vong_thu_nghiem.py`)
- `--diem` (mặc định 1e-5 = EURUSD 5 số — GIẢ ĐỊNH khai báo); in cảnh báo nếu mức giá gợi ý `_Point`
  khác; dòng kết quả ghi `[SL/TP theo _Point=..]`.
- Cơ chế có `sltp`/`dong_mo_bar` không nhóm → chạy riêng qua `chay_he` (trước bị `danh_gia` bỏ qua).
- Chỉ SIẾT tối ưu: không tối ưu độ trễ bar (`khoa_tre` — chỉ số bar trong mã, không phải input);
  buffer cùng một handle (bands dưới/trên/giữa) buộc chung chu kỳ. Ứng viên SL/TP điểm = ×0,5…2.

### 4. Vòng CÓ phí (EURUSD, spread 1,63 bps/chiều, trượt 0,41, qua đêm) — `--loc-file '**/*.mq5'`
- mo_rong, EURUSD H1 server (17.127 bar): 10 cơ chế, **giữ 0**. Tốt nhất 013 bán t −0,9/+0,6,
  012 bán −0,4/+0,5. Gốc (thông số EA) mọi chân âm (sh −2…−5,5 phần kiểm).
- mo_rong, Dukascopy 2003–2021 (116.175 bar): **giữ 0**. 013 mua t −8,3/−7,4 (lỗ rõ sau phí);
  015 bán t +1,9/+0,5 (gần nhất, vẫn dưới ngưỡng); 011 tối ưu chỉ còn 7–8 lệnh phần kiểm (bị loại vì ít lệnh).
- mau_thu (lối ra không đổi): EURUSD H1 và Dukascopy giữ 0, số giống hệt lần trước.
- So với mô hình cũ giữ N bar (cùng điểm vào): gốc thường bớt âm, nhưng không chân nào thành lợi thế.

### 5. Test
- Mới `test_sltp_truc_tiep.py` (21: đọc 011/012/013/015/017, từ chối khi không chắc, mô phỏng ASK/BID,
  từ chối sai phía, đóng tick đầu, không nhìn trước, DSL, vòng chạy qua `chay_he`) — xanh.
- 264 test đọc MQL5/SL-TP/thoát sớm xanh; 169 test vòng/rổ/lưới/stop-out/chi phí xanh. Đỏ còn lại
  (`test_loi_ra`, `test_ngu_phap_toan_hang`, `test_cua_vao` mỗi file 1–2) đỏ y hệt trên 95a59074;
  toàn bộ: 0 đỏ mới (2 test `test_sua_bang_llm` đỏ khi chạy cả bộ, xanh khi chạy riêng — phụ thuộc thứ tự/env).

### Còn chặn
- Hàm phụ/trạng thái lớp/cờ static (EMA Crossover, Box Breakout, Viprasol, 016 MACross); iADX MT5 (019).
- Chỉ báo sống trong EA cổng bar mới (05/014); 3 điểm vào nhánh `else`; 2 mâu thuẫn bar0~bar1.
- `_Point` thật theo broker/mã (đang giả định 1e-5 qua `--diem`); STOPS_LEVEL giả định 0.
- EA không giới hạn số vị thế (011/012…): mô phỏng MỘT vị thế mỗi chân (xấp xỉ, ghi `gia_dinh`).
- Breakout4 (PivotsDay, `_Point`) — vẫn không đoán.

## (trước) Vòng "THOÁT SỚM + CHỈ BÁO SỐNG TRONG BAR + MACD/STOCH + BUỘC THAM SỐ" (sau 56ee431e) — tối 10/10/2026
Không nới ngưỡng giữ (t ≥ 2,0 tối ưu / 1,5 kiểm, ≥47/≥20 lệnh, cổng tài khoản/placebo/cháy).
Không coi định danh lạ là close. iADX (không Wilder) vẫn bỏ qua có lý do.

### Số đo
| | trước (56ee431e) | **bây giờ** |
|---|---|---|
| `mau_thu` (10 EA, 22 điểm vào) | 13/22 = 59,1% | **13/22 = 59,1%** (dịch giống hệt; chỉ thêm `bo_qua_quan_tri`) |
| `mau_thu/mo_rong` (15 EA, 34) | 5/34 = 14,7% | **9/34 = 26,5%** (+011_RSI_V2 mua/bán, +012_MA_V1 mua/bán) |
| gộp (25 EA, 56) | 18/56 = 32,1% | **22/56 = 39,3%** |

### 1. Thoát sớm (`nhan/doc_ma.py`)
- `if(X) return;` / `{return;}` / `{Print(..); Comment(..); ...; return;}` đều nhận (bảng lệnh vô hại
  `Print/PrintFormat/Comment/Alert/ResetLastError/SendNotification/Sleep/PlaySound`); lệnh KHÁC trước
  return → vẫn nhận nhưng ghi `gia_dinh` "thoat som co lenh khac truoc return (chua mo phong)".
- Luật phạm vi: if phải nằm trong khối BAO điểm vào (độ sâu ngoặc từ if tới lệnh vào không âm);
  `else if(X) return;` bị loại (trước đây bắt nhầm). Sửa lệch vị trí trong `_cac_if_bao`.
- `return` trong khối lồng đã đóng trước lệnh vào = lọc có điều kiện → từ chối có lý do, TRỪ khi
  điều kiện đường đi là kiểm lỗi dữ liệu/API hoặc toàn quản trị.
- Kiểm lỗi dữ liệu = quản trị: biến chỉ gán bằng tổng `Copy*` so `!= N`/`< N`/`<= 0`/`== -1`;
  hàm `bool` phụ chỉ trả false trong `if(!API(..))` (vd `NormalizePrice`); `!SymbolInfo*/Copy*/...`.
- **Tỷ lệ KHÔNG đổi, vì sao**: trong 25 EA, thoát sớm có Print trước return chỉ nằm ở các guard dữ
  liệu (Bollinger 013) hoặc ở file đã không dịch được vì lý do khác (Viprasol: lộ thêm
  `FiltersAllowEntry/InSession/HasOpenPosition/g_tradesToday`, đều là lọc trạng thái). mau_thu chỉ
  thêm ghi chú `curTime == prevTime`. Sửa này để ĐÚNG NGHĨA (trước đây bỏ sót lọc ⇒ có thể dịch quá
  rộng), không để tăng số.

### 2. Chỉ báo sống trong bar (`muc_song`, `nhan/ngu_phap.py`)
- EA kiểm MỌI tick với `X[1]>=30 && X[0]<30`: X[0] đổi theo giá tick p. RSI, SMA/EMA/SMMA/WMA trên
  close đơn điệu theo p ⇒ điều kiện = mức giá P* tính được tại đóng bar i, dùng cho bar i+1 qua
  `trong_bar` (lệnh dừng trong bar, như `_GIA0`). Không nhìn trước: P* chỉ dùng dữ liệu ≤ i.
- RSI nghịch đảo chính xác bằng cùng ewm alpha=1/n như `mau.rsi` (sai số 1e-13). MA tuyến tính
  value = w·p + r[i] (sma 1/n, ema 2/(n+1), smma 1/n, wma 2/(n+1)); giao hai MA sống:
  P* = (rS−rF)/(wF−wS), hướng theo dấu (wF−wS); trọng số bằng nhau → từ chối.
- CHỈ áp khi EA kiểm mỗi tick; EA cổng tick đầu (IsNewBar) giữ quy ước cũ → bar0/bar1 vẫn báo
  "mâu thuẫn" (05_RSI_MA, 014_RSI_MA_V2: RSI PRICE_OPEN + MA khung khác).
- Test: `test_chi_bao_song.py` (13, gồm test CẮT CỤT dữ liệu sau i không đổi P*[i], và kiểm vét
  cạn khớp lệnh trong bar bằng thăm dò giá thấp).

### 3. iMACD / iStochastic
- iMACD: đường tín hiệu MT5 là SMA → `kieu_tin_hieu: "sma"`. iStochastic: %K có slowing =
  100·SUM(C−LL,s)/SUM(HH−LL,s), tín hiệu SMA(%K,D); chỉ nhận MODE_SMA + STO_LOWHIGH, khác → từ chối.
  Buffer 0/1 = chính/tín hiệu. Họ: macd→xu_huong, stochastic→quay_ve_trung_binh. `test_macd_stoch_mql5.py` (7).
- Chưa mở thêm điểm vào nào trong bộ hiện có (016 dùng cờ static MACross; 019 iADX).

### 4. Buộc tham số trong `vong_thu_nghiem.py` (chỉ SIẾT)
- Phát hiện: tối ưu tách rời các khoá cùng MỘT input EA (rsi chu kỳ 42 ở vế này, 26 ở vế sống;
  ngưỡng 24 vs 33) = chiến lược khác + thêm bậc tự do. `buoc_tham_so(spec)` buộc: (a) `n` của các
  nút chỉ báo giống hệt (không buộc `n` của `tre`); (b) ngưỡng `muc_song` với hằng tương ứng của
  điều kiện cùng chỉ báo. `toi_uu` tối ưu khoá đại diện, trả dict đủ khoá. `test_buoc_tham_so.py` (4).
- Hệ quả rõ: 015 bán trên Dukascopy trước buộc t +3,7/+0,8 → sau buộc t −0,2/−2,7 (cái +3,7 là do
  tách khoá, quá khớp).

### 5. Vòng lặp CÓ phí (EURUSD, spread 1,63 bps/chiều, trượt 0,41, qua đêm)
- mo_rong, EURUSD H1 server (17.127 bar): 10 cơ chế, **giữ 0**; tất cả âm ở phần kiểm (tốt nhất
  012 bán t −0,3/+0,4). 011 gốc tick đầu 0 lệnh (khớp: tín hiệu chỉ có TRONG bar).
- mo_rong, Dukascopy 2003–2021 (116.175 bar): **giữ 0**; mọi t phần kiểm âm.
- mau_thu (sau buộc): EURUSD H1 giữ 0; Dukascopy giữ 0 (số giống hệt lần trước).
- SL/TP của mo_rong chưa dịch (`_Point`, ATR×hệ số) → chỉ giữ cố định `giu`; kết quả là của ĐIỂM VÀO.

### 6. Test
- Mới: 13 + 13 + 7 + 4 = 37 test, đều xanh; 133 test liên quan vong/cổng xanh.
- Toàn bộ `test_*.py`: 84 đỏ / 2037 xanh / 17 lỗi thu thập (thiếu scipy, dữ liệu ngoài, OCR...).
  Chạy lại 84 đỏ trên HEAD cũ: 80 đỏ y hệt; 4 còn lại (`test_chay_that`) xanh khi chạy riêng ở bản
  mới (phụ thuộc thứ tự) ⇒ **0 đỏ mới**.

### Còn chặn
- Hàm phụ/trạng thái lớp/cờ static (EMA Crossover cây quyết định, Box Breakout, Viprasol, 016 MACross).
- SL/TP mo_rong (`_Point`, ATR), Breakout4 `_Point`.
- iADX MT5 (không Wilder) + DI± (019).
- Chỉ báo sống trong EA cổng bar mới (05/014: RSI PRICE_OPEN, MA khung khác).
- 3 điểm vào trong nhánh `else`; 2 mâu thuẫn; `rsi[0] > 30` đơn lẻ; cờ sl/tp Basic_Bollinger.


## Vòng "BỘ EA MỞ RỘNG — ĐO TỶ LỆ BÓC TÁCH NGOÀI 10 FILE MẪU" (sau 129f6a62) — khuya 10/10/2026
Không đoán `_Point` của Breakout4. Không đụng ngưỡng giữ của vòng lặp (t ≥ 2,0/1,5, số lệnh,
cổng tài khoản/placebo/cháy). Chỉ sửa lớp đọc MQL5 ở chỗ SAI NGHĨA hoặc THIẾU tổng quát.

### 1. Kiểm kê .mq5/.mqh
- Repo: 10 EA trong `mau_thu/` + 1 `.mqh` cache `/tmp/MultiPivots.mqh`; ngoài ra 7 `.mq5` khác
  KHÔNG phải EA ngoài: `ea_MeanRevZ5.mq5`, `ea_QuanTriBench.mq5`, `xem_ghep.mq5` (do THE BRAIN
  tự sinh), `reports/…` (bản ghép quản trị + 1 EA Wizard dùng lớp tín hiệu chuẩn + 1 stub). → Repo
  chỉ có `mau_thu` để đo → làm bước 3 (lấy EA công khai).
- Thêm `mau_thu/mo_rong/`: **15 EA MIT một file** (11 santiago-cruzlopez/MQL5, terencebeauj,
  forexstrategystudio, Viprasol-Tech, je-zhou). Nguồn/commit/bản quyền: `mau_thu/mo_rong/NGUON.md`;
  LICENSE trong từng thư mục. Bỏ khung lớn (geraked/metatrader5 dùng `EAUtils.mqh` chung).
- Đo: `python mau_thu/do_moc_rong.py` (`--gop` = gộp với mau_thu). Cùng chỉ số trung thực với
  `do_moc.py` (điểm vào dịch được / dich_duoc / hedge / ma_chet / chua_dich), không coi định danh
  lạ là `close`. `do_moc.do(files=None)` nhận danh sách file; số chính của mau_thu không đổi.

### 2. Số đo
| | trước (129f6a62) | **bây giờ** |
|---|---|---|
| `mau_thu` (10 EA, 22 điểm vào) | 13/22 = 59,1% | **13/22 = 59,1%** — đầu ra `doc_chien_luoc` trên 10 file GIỐNG HỆT từng byte (đã diff JSON) |
| `mau_thu/mo_rong` (15 EA, 34 điểm vào) | 1/34 = 2,9% — **và cái 1 đó SAI** | **5/34 = 14,7%** (6 cơ chế), cả 5 đã đọc tay đối chiếu mã EA |
| gộp (25 EA, 56 điểm vào) | 14/56 = 25,0% | **18/56 = 32,1%** |
- Cái "1 dịch được" cũ (`01_RSI_V1`: bán khi rsi14 > 30) là NÓI DỐI: EA khai `int rsiHandle = iRSI(..)`
  CỤC BỘ trong OnInit, che biến toàn cục cùng tên → OnTick đọc handle 0, EA không đọc được RSI.
  Giờ bộ đọc từ chối (handle bị che).
- 5 điểm vào dịch được (đọc tay): `013_Bollinger` mua `close <= BB_dưới(21, 2.0, ddof 0) trễ 1`
  / bán `close >= BB_trên … trễ 1` (bands_shift=1 → trễ 1; cổng IsNewBar); `015_Triple_MA` mua
  `ema30>ema60 và ema10 trễ1 < ema30 trễ1 và ema10 >= ema30` / bán đối xứng (chuỗi if/else-if gán
  `orderType`, `else return;`); `017_Ichi_ATR` mua `tenkan>kijun và tenkan trễ1 <= kijun trễ1` / bán
  đối xứng (CopyBuffer start 1, mảng không đảo). SL/TP (điểm `_Point`, ATR×hệ số, mức MA) và lệnh
  đóng theo dải giữa CHƯA dịch — cơ chế chỉ là ĐIỂM VÀO.
- 29 chưa dịch, lý do chính: 4 **mâu thuẫn sau quy ước chỉ số bar** (RSI_V2, MA_V1, RSI_MA, RSI_MA_V2:
  `X[1]>=30 && X[0]<30` — bar 0 ≈ bar 1 ở tick đầu, EA thật bắt giao cắt GIỮA bar khi chỉ báo
  bar 0 đổi theo tick → DSL không nói được), 3 vào lệnh trong hàm phụ có trạng thái lớp/bộ lọc
  (`EMA Crossover` sinh tự động dạng cây quyết định, `Box Breakout` theo `activeRange` lớp,
  `Viprasol` qua `FiltersAllowEntry`), 3 nhánh `else`, `016_CCI_2MAVG` cờ `static` nhớ qua nhiều
  bar, `018_Price_Action` lệnh dừng tự quản theo giá vào, `019_ADX` iADX của MT5 (không phải Wilder)
  + DI±, `MA[0]>MA[1]` thành so với chính nó, `Basic_Bollinger_Bands` cờ sl/tp trạng thái.

### 3. Sửa trong `nhan/doc_ma.py` (lớp MQL5) + `nhan/ngu_phap.py`
Mở khoá (tổng quát, đúng nghĩa):
- Đối số chỉ báo là **input** của tác giả (`iRSI(..,RSI_Period,..)`, `input int RSI_Period=14;`)
  → giá trị mặc định (input MQL5 là hằng, không gán lại được). Input số trong vế so sánh
  (`(100-RSI_Level)`) → hằng; số học hằng tính bằng `ast` (không eval).
- Chỉ báo **nhiều buffer**: `iBands` 0/1/2 = giữa/trên/dưới, `iIchimoku` 0/1 = tenkan/kijun; tên
  hằng buffer (`UPPER_BAND`, `TENKANSEN_LINE`…). Bollinger thêm `ddof` (0 = độ lệch dân số như
  iBands MT5 `sqrt(sum/period)`; mặc định cũ 1 giữ nguyên cho mọi cơ chế cũ).
- `ma_shift`/`bands_shift` = s > 0 → `trễ s` (đường vẽ dịch phải s bar, chỉ đọc quá khứ).
- `MqlTick tk` + `SymbolInfoTick(_Symbol,tk)` → `tk.ask/bid/last` = giá bar 0 (token `_GIA0` như cũ).
- Guard VÀ trộn tín hiệu + quản trị (`cntBuy==0 && rsi<30 && openTime!=iTime(..)`): bỏ VẾ quản trị
  (ghi `bo_qua_quan_tri`), giữ vế tín hiệu; chỉ khi không có `or` mức ngoài. Quản trị mới: so với
  `iTime(..)` (một lệnh/bar), `SymbolInfoTick`, `Count*Positions`, biến ĐẾM VỊ THẾ (tham chiếu
  `int &c` được `c++` trong hàm duyệt `PositionsTotal`/`PositionGet*`, hoặc `x++` trong
  `for(..PositionsTotal()..)`), so sánh hai biến `datetime` (cổng bar mới tự viết).
- Chuỗi `if(A){t=ORDER_TYPE_BUY} else if(B){t=ORDER_TYPE_SELL} else return; PositionOpen(..,t,..)`
  → hai cơ chế, CHỈ khi A và B loại trừ nhau chứng minh được (nếu không, nhánh hai là `B and not A`
  → từ chối, có lý do).
- Họ: `ichimoku` → `xu_huong`; giá vs dải Bollinger: mua dưới dải dưới = `quay_ve_trung_binh`,
  mua trên dải trên = `pha_vo` (cùng hướng mới gán).
Siết (trước đó dịch SAI, nay từ chối hoặc dịch đúng):
- **Khung thời gian**: chỉ khung biểu đồ (`_Period/PERIOD_CURRENT/0/Period()`); trước đó đối số
  khung bị BỎ QUA (`iMA(..,PERIOD_D1,..)` thành sma trên H1).
- **Giá áp dụng**: PRICE_OPEN/HIGH/LOW/MEDIAN/TYPICAL → `cot`; WEIGHTED → từ chối (trước: rsi của
  OPEN đọc thành rsi của CLOSE). `iCCI` theo đối số giá (DSL mặc định hlc3).
- **Phương pháp MA**: MODE_SMMA → `smma`, MODE_LWMA → `wma` (trước: SMMA thành ema, LWMA thành sma).
- `iATR` → `kieu: sma` (iATR MT5 = trung bình cộng TR, không phải Wilder).
- **Handle bị che** bởi khai báo cục bộ cùng tên trong hàm khác → không dịch.
- **Mâu thuẫn**: hai điều kiện cùng cặp toán hạng, chiều ngược (một phép chặt) → tập rỗng, từ chối;
  so sánh toán hạng với chính nó → từ chối. Trên mau_thu không có trường hợp nào (đầu ra giữ nguyên).

### 4. Test
- Mới `test_doc_ma_mo_rong.py` (13): bands dưới + input + dịch = trễ, ddof 0/1 tính tay, hàm chỉ báo
  (giá/phương pháp/khung/biến/shift), số học hằng (không eval chuỗi lạ), bỏ vế quản trị + biến đếm,
  handle bị che, giao cắt bar0/bar1 = mâu thuẫn, so với chính nó, biến đếm KHÔNG duyệt vị thế thì
  không bỏ, chuỗi if/else-if loại trừ / không loại trừ, `do_moc_rong` 15 file/34 điểm ≥5 + mau_thu 13/22.
- 73 file test liên quan: **1109 xanh / 40 đỏ / 9 lỗi — 0 đỏ mới** so với HEAD (worktree HEAD đỏ 50
  do thiếu file dữ liệu chưa track; tập đỏ của bản mới là tập con). Chạy lại 48 file chạm
  doc_ma/ngu_phap sau chỉnh cuối: 0 đỏ mới.

### 5. Chặn còn lại (vòng sau)
1. **Giao cắt trong bar** (4/34 trên bộ rộng): EA kiểm mỗi tick, chỉ báo bar 0 đổi theo tick. Muốn
   dịch trung thực cần toán hạng "chỉ báo với giá đóng thay bằng giá tick" + kích hoạt trong bar
   (như khối `trong_bar` cho giá) — không làm bằng cách dời trễ 1 bar (đó là chiến lược khác).
2. Hàm phụ / trạng thái lớp / cờ `static` qua nhiều bar → DSL không có biến trạng thái.
3. `if(!X){ Print(..); return; }` (có lệnh trước `return`) KHÔNG được `_thoat_som` bắt — bộ lọc tín
   hiệu viết kiểu này sẽ bị BỎ SÓT (lỏng hơn bản gốc). Trên 5 điểm vào đã nhận chỉ có lọc quản trị
   kiểu đó (đã đọc tay), nhưng phải sửa trước khi chạy trên kho lớn.
4. iADX MT5 (làm mượt EMA, khác Wilder) + DI±; iStochastic/iMACD nhiều buffer chưa ánh xạ.
5. SL/TP theo `_Point`/ATR×hệ số/mức chỉ báo của bộ mở rộng chưa dịch; vòng lặp chưa chạy với các
   cơ chế mới (`vong_thu_nghiem` mới đọc mau_thu).



## Vòng "RỔ HEDGE QUA CỔNG TÀI KHOẢN + SYMBOL_VOLUME_MAX" (sau 951e157a) — tối 10/10/2026
Ngưỡng cũ KHÔNG nới (t ≥ 2,0/1,5, ≥47/≥20 lệnh, sống sót tài khoản, lời ròng kiểm > 0, placebo
p ≤ 0,05, P(cháy/năm) ≤ 5%). Chỉ mở rộng phạm vi cổng (siết thêm) + thêm giới hạn khối lượng sàn.

### 1. Rổ hedge Breakout2/2-2/3 qua CÙNG cổng tài khoản (`vong_thu_nghiem`, docstring mục 9)
- Mới `la_ro(specs)`: MỌI hệ có `ro` (rổ hedge lẫn lưới) chạy với tài khoản khai báo
  (10.000 USD, 1:100, stop-out 50%, lot max 100) và qua cổng a–d (sống sót / lời ròng kiểm > 0 /
  thắng placebo cùng cấu trúc / P(cháy/năm)). Trước: chỉ hệ `ro.luoi`. JSON thêm `loai_ro`
  (`hedge`|`luoi`); in "CỔNG RỔ HEDGE" / "CỔNG LƯỚI".
- `mo_phong.chay_he` đã áp ký quỹ / stop-out từng lệnh lỗ nhất trước / từ chối thiếu ký quỹ cho
  MỌI chân có `ro` (kể cả lệnh hedge) — chỉ là vòng lặp trước không truyền `tai_khoan` cho rổ hedge.
  Chuỗi `loi` không đổi (đã so: Sharpe/t/số lệnh Breakout2/2-2/3 y hệt bản trước trên Dukascopy).
- **Placebo**: chân Breakout2/2-2/3 vào lệnh ở tick đầu theo `cho` (không có `muc`/`co`, tức không
  phải lệnh dừng trong bar), có cả hai chiều → `chan_placebo` chạy được nguyên vẹn (đồng xu thay
  chiều lệnh đầu; hedge theo điểm/tiền, chốt đỉnh, cắt lỗ, tài khoản giữ nguyên). Không cần bỏ qua.
- Hệ `ro` có chân lệnh dừng trong bar (hiện KHÔNG có hệ nào): `chan_placebo` vẫn
  `NotImplementedError` → vòng lặp bắt, ghi `cong_luoi.placebo_bo_qua` (lý do), BỎ điều kiện (c),
  vẫn áp (a) sống sót, (b) lời ròng kiểm > 0, (d) P(cháy/năm) chỉ từ hệ thật, và ngưỡng t cũ.
  Ghi rõ: đây là chỗ cổng YẾU hơn — khi gặp hệ như vậy cần làm null cho lệnh dừng trong bar
  (vd. dời mức ngẫu nhiên cùng phân phối khoảng cách) trước khi tin kết quả giữ.

### 2. SYMBOL_VOLUME_MAX / SYMBOL_VOLUME_LIMIT (`mo_phong.chay_he`, chỉ khi có `tai_khoan`)
- `tai_khoan["lot_max"]` (= SYMBOL_VOLUME_MAX, lot/lệnh) và `tai_khoan["lot_tong_max"]` (=
  SYMBOL_VOLUME_LIMIT, tổng lot đang mở CÙNG chiều + lệnh mới). None/0 = không giới hạn.
- Hành vi: sàn MT5 trả INVALID_VOLUME / LIMIT_VOLUME và KHÔNG khớp; EA Breakout2/3/5 không chia
  lệnh, không xử lý lỗi → lệnh bị **TỪ CHỐI nguyên vẹn** (không cắt lot). Áp cho lệnh đầu rổ, lệnh
  hedge, lệnh lưới. Lệnh lưới bị từ chối: chuỗi lot không tiến, thử lại bar sau (cùng giả định như
  từ chối ký quỹ) → nếu lot bước đó > lot_max thì lưới **kẹt** ở bước đó. Đếm `tu_choi_lot_max`.
- Mặc định vòng lặp: `--lot-max 100` (mức phổ biến cho EURUSD tài khoản chuẩn/ECN; sàn đặt 50–500;
  tài khoản micro/cent thấp hơn nhiều tính theo lot chuẩn) — **GIẢ ĐỊNH, chưa đọc từ sàn thật**;
  `--lot-tong-max 0` (không giới hạn, mặc định MT5). Lot lớn nhất Breakout5 thấy được 3,80 → mức 100
  không ràng buộc trên mọi bộ hiện có.
- Test mới `test_lot_max_va_cong_ro.py` (9, số tính tay): không giới hạn = y hệt cũ; lot_max 0,035
  → 0,02 + 0,03 qua, 0,04 bị từ chối 3 bar liền (lưới kẹt, 0 từ chối ký quỹ); lot_max 0,01 → lệnh
  đầu bị từ chối, 0 lệnh, chuỗi lời 0; lot_tong_max 0,05 → 0,02+0,03 = 0,05 qua, +0,04 bị từ chối;
  0,0499 → cả 0,03 bị từ chối (4 bar); hedge 0,4 lot Breakout2 tại 1,0970 bị từ chối khi lot_max
  0,3 (vốn ròng min = 10.000 − 35 USD = lỗ thả nổi 0,1 lot × 35 pip); Breakout2 qua cổng có placebo;
  NotImplementedError → `placebo_bo_qua`, không nới (a)/(b).

### 3. Số đo — EURUSD Dukascopy 2003-05 → 2021-12 (116.175 bar H1, kiểm ~5,6 năm 2016-2021), CÓ PHÍ
| hệ | t tối ưu/kiểm | trước (951e157a) | **bây giờ** |
|---|---|---|---|
| Breakout2 | +0,8/−2,8 | loại vì t (không qua cổng) | loại: t; **cổng RỔ HEDGE**: 0 stop-out, KQ min 1.959%, vốn 10.000 → 9.036 USD (trượt 3.134 + qua đêm 642 USD); loi_log kiểm −0,635 vs placebo TB −0,522 (q95 −0,272, dương 0%, sống 100%), **p 0,81**; P(cháy/năm) 0% (0/553 năm-mẫu) |
| Breakout2-2 | +0,2/−2,4 | loại vì t | loại: t; cổng: 0 stop-out, KQ min 2.347%, vốn → 8.741 USD; −0,499 vs TB −0,570, **p 0,37**; cháy 0% |
| Breakout3 | +0,8/−2,8 | loại vì t | loại: y hệt Breakout2 (cùng số đến từng chữ số — reset đỉnh khác nhau không đổi kết quả trên bộ này) |
| Breakout5(-2-2) | +1,3/+1,2 | loại (cổng lưới) | loại y hệt: 9 stop-out kiểm, p 0,24, cháy 89,8%/năm; `tu_choi_lot_max` 0 (lot max 3,80 < 100) |
| Breakout1, Template | — | loại vì t | không đổi (không có rổ) |
| **giữ lại** | | **0/6** | **0/6** |
- Rổ hedge an toàn về tài khoản (lot cố định 0,1 + 0,3/0,4, ký quỹ thấp, cắt lỗ −120 USD) nhưng
  **lỗ ròng sau phí và không thắng đồng xu**: placebo cùng cấu trúc cũng lỗ 100% số lần → cấu trúc
  chốt-đỉnh/hedge tự nó ăn phí, chiều vào của EA không thêm gì.
- Độ nhạy `--lot-max 1` (Breakout5, tài khoản kiểu micro tính theo lot chuẩn): KHÔNG cứu được —
  lưới kẹt ở bước > 1 lot (6.664 lệnh bị từ chối vì lot, 16.373 vì ký quỹ), phần kiểm 11 stop-out,
  vốn 10.000 → **11 USD**, loi_log −5,53 vs placebo TB −4,18, p 0,77, P(cháy/năm) 38,8%. Giới hạn
  khối lượng làm martingale mất đường thoát (không gấp lot được để kéo hoà vốn) chứ không giảm đuôi.
- `mau_thu/do_moc.py`: 13/22 = 59,1% (không đổi lớp đọc).
- Test (73 file chạm mo_phong/vong/doc_ma/ngu_phap/chi_phi/ro_mql): **1109 xanh / 40 đỏ / 9 lỗi — 0 đỏ mới** (trước 1100/40/9; +9 test mới; tập đỏ so với worktree HEAD: không có đỏ nào mới).
Kết quả: `/workspace/du_lieu_fx/vong_eurusd_duka_cong_ro.{json,txt}` (~6 phút),
`/workspace/du_lieu_fx/vong_eurusd_duka_b5_lotmax1.{json,txt}`.

    python vong_thu_nghiem.py --csv /workspace/du_lieu_fx/eurusd_h1_duka_jw_server.csv
    python vong_thu_nghiem.py --csv /workspace/du_lieu_fx/eurusd_h1_duka_jw_server.csv --loc-file '*Breakout5*' --lot-max 1

### Vấn đề mở (cập nhật)
1. ~~SYMBOL_VOLUME_MAX~~ đã mô hình (giả định 100 lot; cần đọc SYMBOL_VOLUME_MAX/LIMIT thật của sàn
   người dùng qua MT5 khi có máy Windows/MT5 — `_von_va_lot.py` đã đọc volume_min/step).
2. ~~Rổ hedge chưa qua cổng tài khoản~~ xong; placebo chạy được cho cả 3 hệ.
3. Null cho chân lệnh dừng trong bar vẫn chưa có — hiện không hệ `ro` nào cần; hệ lệnh đơn trong bar
   (Breakout1) vẫn chỉ qua ngưỡng t (đã có `--gia-lap-duong` làm placebo dữ liệu).
4. Breakout4 — vẫn bỏ qua (không đoán `_Point`, logic đầu ngày, trigger trong nến).
5. Dukascopy kéo đủ 2003-2026 + thêm cặp: chạy `tai_dukascopy_h1.py` qua đêm (bị 429 khi gọi dồn).
6. Các xấp xỉ cũ: ~~swap gắn số dư chung (không từng lệnh) khi chọn lệnh "lỗ nhất"~~ (P3 11/10: đã gắn từng
   lệnh); ký quỹ chỉ đúng xxxUSD; phí hiện tại áp cho 2003-2010 (P3: swap đã theo tháng; spread theo năm CHƯA ĐO ĐƯỢC).

---

## (trước) Vòng "ĐUÔI MARTINGALE + STOP-OUT KIỂU MT5" (sau de92b9ef) — tối 10/10/2026
Ngưỡng cũ KHÔNG nới (t ≥ 2,0/1,5, ≥47/≥20 lệnh, sống sót tài khoản, lời ròng kiểm > 0, placebo p ≤ 0,05).
Chỉ thêm một cổng SIẾT và làm mô phỏng tài khoản sát MT5 hơn.

### 1. Stop-out kiểu MT5 (`mo_phong.chay_he`, chỉ khi có `tai_khoan`)
- Trước: chạm stop-out → đóng CẢ rổ một lúc. Bây giờ: đóng lệnh **LỖ NHẤT trước, từng lệnh một**,
  tính lại mức ký quỹ sau mỗi lệnh, dừng khi mức ký quỹ > stop_out. Lệnh còn lại tiếp tục (EA vẫn
  quản lý: chốt đỉnh theo lời của các lệnh còn lại, hedge theo `postotal` mới, lưới giữ chuỗi lot).
  Hết lệnh → rổ đóng `ly_do="stop_out"`. Nhật ký: `stop_out_le` (bar, giá, chiều, lot, lời tiền).
- `so_stop_out` = số LẦN chạm ngưỡng; mới: `so_lenh_stop_out` = số lệnh bị sàn đóng.
- **Trượt giá + qua đêm giờ trừ thẳng vào số dư** (mới: `phi_truot_usd`, `phi_qua_dem_usd`): trượt
  lot×hợp đồng×giá×`truot_gia_frac` lúc mở VÀ lúc đóng mỗi lệnh; qua đêm cuối mỗi bar theo chiều từng
  lệnh (cùng công thức `phi_giu_mang` như chuỗi `loi`). Không đưa vào `_loi_ro` (EA chỉ đọc
  POSITION_PROFIT để chốt đỉnh/hedge). EURUSD Yahoo phần kiểm: trượt 788 USD, qua đêm 108 USD.
- `tai_khoan=None` → y hệt trước (test: tài khoản 1e12 cho chuỗi `loi` giống từng bit, kể cả có phí).
- Test mới `test_stop_out_mt5.py` (7): đóng 0,04 lot lỗ nhất trước, rổ 2 lệnh còn lại chạy tiếp,
  von 150 → 106 tính tay; gap sâu → đóng 0,04 rồi 0,03 rồi lệnh cuối (cháy); bảo toàn số dư; trượt/qua
  đêm vào số dư khớp tính tay; Poisson/stop-out đầu; cổng chỉ siết thêm.

### 2. Cổng mới: XÁC SUẤT CHÁY THEO NĂM (`vong_thu_nghiem.ti_le_chay_nam`, `--p-chay-nam` 0,05)
- Đếm **stop-out ĐẦU TIÊN** mỗi lần chạy (sau đó tài khoản đã tan; stop-out từng lệnh lặp lại không
  phải rủi ro mới), phơi nhiễm = đến bar stop-out đầu. λ = số lần cháy / tổng năm phơi nhiễm,
  P(cháy trong 1 năm) = 1 − e^(−λ). Tính cho hệ THẬT và 99 placebo cùng cấu trúc (phần kiểm);
  dùng **max(thật, placebo)**. Loại khi P > 5%/năm. Lý do lấy placebo: cấu trúc rổ/lưới giống hệt,
  99 × năm kiểm cho nhiều năm-mẫu hơn một đường giá; một "chiều có edge" trên vài năm kiểm không đủ
  bằng chứng xoá rủi ro đuôi của chính cấu trúc. Chỉ siết (đặt 1,0 = tắt, chỉ để đo độ nhạy).
- Bản đầu đếm MỌI lần stop-out (stop-out từng lệnh lặp lại) → 49,7%/năm trên EURUSD Yahoo, sai nghĩa;
  đã sửa thành stop-out đầu (4,9%/năm).

### 3. Dữ liệu dài hơn + nhiều cặp (ngoài repo, `/workspace/du_lieu_fx/`)
| bộ | nguồn | khoảng (giờ server Helsinki) | bar | phần kiểm |
|---|---|---|---|---|
| EURUSD Yahoo (cũ) | yfinance `EURUSD=X` 1h | 2023-12-26 → 2026-10-09 | 17.127 | ~0,82 năm |
| GBP/AUD/NZD-USD Yahoo | yfinance 1h, 730 ngày | 2023-12-25 → 2026-10-10 | ~17.130 | ~0,82 năm |
| **EURUSD Dukascopy** | github.com/JWalker242/FX-Data (Dukascopy BID H1, GMT, bỏ bar volume 0) → Helsinki | **2003-05-05 → 2021-12-09** | **116.175** | **~5,6 năm (2016-2021)** |
| EUR/GBP/AUD-USD MT5 | github.com/komo135/forex-historical-data (H1 sàn MT5, giá ×1e5, giờ server) | 2012-11-16 → 2022-03-04 | ~57.580 | ~2,8 năm |
- Kiểm chéo: giải mã file Dukascopy gốc tháng 1/2015 bằng `tai_dukascopy_h1.py` = JWalker **khớp
  tuyệt đối** (504/504 bar, sai 0); komo EURUSD vs JWalker→Helsinki: trung vị |Δclose| 0,3 pip ở lệch
  0 giờ (lệch ±1 giờ: 3,2–5,1 pip) → komo là giờ server UTC+2/+3 như giả định.
- Tải thẳng `datafeed.dukascopy.com` bị **429 / lỗi TLS** khi gọi dồn. `tai_dukascopy_h1.py` (mới)
  tải tuần tự, nghỉ giữa lần, lùi lại khi lỗi, đệm từng tháng ra đĩa — chưa tải hết được trong vòng
  này nên dùng bản sao JWalker (đã kiểm khớp).
- Phí: mô hình phí HIỆN TẠI của sàn (spread XM đo, trượt 1/4 spread, qua đêm sàn) áp cho cả 2003-2021
  → lạc quan cho giai đoạn spread rộng hơn (2003-2010).

### 4. Số đo (CÓ PHÍ, tài khoản 10.000 USD 1:100 stop-out 50%)
| | de92b9ef (trước) | **bây giờ** |
|---|---|---|
| EURUSD Yahoo, giữ lại | 0/6 | **0/6** |
| Breakout5 EURUSD Yahoo kiểm | KQ min 180%; loi_log +1,146 vs placebo TB +1,170 (sống 96%); p 0,93 | KQ min 172,9%; +1,146 vs TB **+1,084** (sống 96%); p **0,93**; P(cháy/năm) placebo **4,9%** (4 cháy / 79,9 năm-mẫu; cận trên 95% 10,3%) — **vừa dưới ngưỡng 5%** → loại vì p |
| Random walk seed 1-10 (lưới) | giữ 0/10; stop-out ≥1 phần 6/10 | giữ **0/10**; stop-out ≥1 phần **7/10**; cổng cháy/năm **tự nó loại 7/10** |
| Test (72 file chạm mo_phong/vong/doc_ma/ngu_phap/chi_phi/ro_mql) | 1093 xanh / 40 đỏ / 9 lỗi | **1100 xanh / 40 đỏ / 9 lỗi — 0 đỏ mới** (40 đỏ đúng y danh sách bản gốc; 2 đỏ `test_sua_bang_llm` phụ thuộc thứ tự) |
| `mau_thu/do_moc.py` | 13/22 = 59,1% | 13/22 = 59,1% (không đổi lớp đọc) |

Breakout5(-2-2) trên các bộ khác (cổng lưới; tất cả các hệ khác cũng giữ 0):
| bộ | t tối ưu/kiểm | stop-out tối ưu/kiểm | loi_log kiểm vs placebo TB | placebo sống | p | P(cháy/năm) | giữ |
|---|---|---|---|---|---|---|---|
| GBPUSD Yahoo | −1,9/+0,7 | 14/0 | +1,29 vs +0,82 | 83% | 0,42 | 21,6% | 0 |
| AUDUSD Yahoo | −1,5/+0,3 | 27/0 | +1,61 vs −1,54 | 57% | 0,44 | 57,0% | 0 |
| NZDUSD Yahoo | +0,1/+0,1 | 0/0 | +0,32 vs −2,68 | 72% | 0,20 | 36,4% | 0 |
| EURUSD MT5 2012-22 | −0,8/+0,6 | 18/1 | +4,18 vs +6,33 | 96% | 0,96 | 42,0% (thật; placebo 1,5%) | 0 |
| GBPUSD MT5 2012-22 | **+2,5**/−1,5 | 0/**31** | −4,95 vs −2,72 | 2% | 0,91 | 99,6% | 0 |
| AUDUSD MT5 2012-22 | −1,3/−1,1 | 15/15 | −9,26 vs −5,95 | 8% | 0,54 | 96,4% | 0 |
| **EURUSD Dukascopy 2003-21** | +1,3/+1,2 | 4/9 | +6,67 vs −0,97 (q95 +13,19) | **6%** | 0,24 | **89,8%** (thật: stop-out đầu sau ~0,44 năm; placebo **61,3%**: 93/99 cháy trong 98 năm-mẫu) | 0 |
- EURUSD Dukascopy phần kiểm (2016-2021): số dư 10.000 → 35.546 USD nhưng **vốn ròng thấp nhất 435 USD**,
  9 lần stop-out, rổ tối đa 15 lệnh / 3,80 lot, lỗ thả nổi 8.277 USD, 522 lệnh lưới bị từ chối vì ký quỹ.
  Số dư cuối dương KHÔNG phải edge: p 0,24 vs placebo, và đường vốn đã chạm gần 0.
- GBPUSD MT5: phần tối ưu t = +2,5 (QUA ngưỡng t cũ) → phần kiểm 31 stop-out, lỗ. Đúng kiểu
  "thắng nhỏ đều rồi cháy" mà Sharpe/t không bắt được.

**Kết luận**: cấu trúc lưới Breakout5 có xác suất bị stop-out **~20–100%/năm** trên mọi bộ dài/nhiều cặp;
cửa sổ Yahoo 0,8 năm cho **4,9%/năm** — đánh giá thấp đuôi hơn 10 lần so với 5,6 năm EURUSD 2016-2021
(61%/năm, cùng cấu trúc). Không có edge; giữ lại 0 ở mọi bộ. Đây đúng là lý do phải có cổng cháy/năm
và dữ liệu dài: cửa sổ ngắn suýt cho lưới qua phần "đuôi".
Kết quả: `/workspace/vong_eurusd_so_mt5.{json,txt}`, `/workspace/du_lieu_fx/vong_*.{json,txt}`,
`/workspace/scratch/pl2/s{1..10}.{json,txt}`.

Lệnh tái lập:

    python vong_thu_nghiem.py --csv /workspace/du_lieu_fx/eurusd_h1_duka_jw_server.csv      # ~5,5 phút
    python vong_thu_nghiem.py --csv /workspace/du_lieu_fx/gbpusd_h1_komo_server.csv --ma GBPUSD --loc-file '*Breakout5*'

### Vấn đề mở (cập nhật)
1. `SYMBOL_VOLUME_MAX` chưa mô phỏng (lot lớn nhất thấy được 3,80 — dưới mức tối đa thường gặp nhưng
   phụ thuộc sàn).
2. Thứ tự "lỗ nhất" dùng lời giá − spread; MT5 tính cả swap/hoa hồng của TỪNG lệnh (ở đây qua đêm trừ
   vào số dư chung, không gắn từng lệnh) — xấp xỉ nhỏ.
3. Ký quỹ chỉ đúng cho xxxUSD tài khoản USD (cặp khác → `canh_bao`); kiểu hedging "chân lớn hơn".
4. Phí hiện tại áp cho 2003-2021 (lạc quan cho giai đoạn đầu); giờ server giả định Helsinki.
5. Placebo cho chân lệnh dừng trong bar chưa có; rổ hedge Breakout2/2-2/3 chưa qua cổng tài khoản.
6. Tải Dukascopy trực tiếp bị giới hạn tốc độ — chạy `tai_dukascopy_h1.py` qua đêm để có 2003-2026 và
   thêm cặp (dữ liệu JWalker dừng ở 2021-12, komo ở 2022-03).
7. Breakout4 — vẫn bỏ qua (3 chướng ngại cũ không đổi, không đoán `_Point`).

---

## (trước) Vòng "CỔNG GIỮ CHO LƯỚI/MARTINGALE" (sau 57657761) — Sharpe/t không còn đủ để giữ hệ lưới
Vấn đề (vòng trước): lưới Breakout5 trên random walk CÓ phí cho Sharpe kiểm DƯƠNG 10/10 seed →
Sharpe/t là phép thử SAI cho martingale (thắng nhỏ đều, đuôi phá sản hiếm). Ngưỡng KHÔNG nới;
thêm một cổng riêng, chỉ có thể SIẾT THÊM.

### Luật giữ mới cho hệ có `ro.luoi` (`vong_thu_nghiem._chay_nhom` → `cong_luoi`)
Giữ khi qua ĐỦ: **(0)** ngưỡng cũ (t ≥ 2,0 tối ưu / 1,5 kiểm, ≥47/≥20 lệnh, kiểm cú pháp) — giữ
nguyên, VÀ
1. **Sống sót với tài khoản KHAI BÁO** (mặc định 10.000 USD, đòn bẩy 1:100, stop-out 50%;
   `--von/--don-bay/--stop-out`): 0 stop-out, không cháy, ở CẢ phần tối ưu lẫn kiểm.
   Bộ tối ưu chấm `-1e9` cho bộ tham số làm tài khoản stop-out.
2. **Lời ròng phần kiểm > 0** (sau phí thật).
3. **Thắng giả dược cùng cấu trúc** trên CHÍNH phần kiểm: `chan_placebo` giữ nguyên mọi thứ của
   `sinh_chan` (rổ, lưới, chốt đỉnh, chuỗi lot, cổng mở bar, vào lại giữa bar, luật ngày, tài khoản)
   và THỜI ĐIỂM được phép vào (hợp `cho` các chân), chỉ thay CHIỀU bằng tung đồng xu mỗi bar.
   Thước đo khai báo: `loi_log` ròng phần kiểm. p một phía = (1 + #placebo ≥ thật)/(N+1),
   N = 99 (`--n-placebo`), giữ khi p ≤ 0,05 (`--p-placebo`). Seed placebo cố định (0) → tái lập.
   Chân lệnh dừng trong bar (`muc`/`co`) → `NotImplementedError` (chưa có null tương ứng; hiện
   không hệ lưới nào dùng).
Hệ KHÔNG lưới: không đổi gì (số liệu Breakout1/2/2-2/3/Template y hệt trước — đã so).

### Mô hình tài khoản (`mo_phong.chay_he(tai_khoan=...)`, chỉ cho chân có `ro`)
- Số dư cộng lời/lỗ TIỀN của rổ khi đóng (`_loi_ro`, đã trừ spread; trượt + qua đêm chỉ nằm trong
  chuỗi `loi`, không trong số dư — ghi nhận).
- Ký quỹ = hợp đồng × giá / đòn bẩy × max(Σlot mua, Σlot bán) (hedging, "chân lớn hơn"; đúng cho
  xxxUSD tài khoản USD, cặp khác → `canh_bao`).
- **Stop-out**: vốn ròng ≤ stop_out × ký quỹ → đóng CẢ rổ tại giá đó (MT5 đóng từng lệnh lỗ nhất
  trước — đóng cả rổ là xấp xỉ). Trên đoạn đơn điệu `vốn + N·p + K0 − so·a·p` tuyến tính → mức
  stop-out tìm CHÍNH XÁC trong bar; gap qua → khớp ở open.
- Lệnh mới (đầu / hedge / lưới) bị **từ chối** khi vốn ròng < ký quỹ sau khi thêm
  (`tu_choi_ky_quy`); lệnh lưới bị từ chối thử lại bar sau (chuỗi lot không tiến — giả định, EA
  không có mã xử lý lỗi PositionOpen). Vốn ≤ 0 → cháy, không vào nữa.
- `tai_khoan=None` → hành vi cũ y hệt (test: tài khoản 1e12 cho `loi` giống từng bit).

### Số đo
| | 57657761 (trước) | **bây giờ** |
|---|---|---|
| EURUSD H1 có phí, giữ lại | 0/6 | **0/6** |
| Breakout5(-2-2) EURUSD kiểm | Sharpe +1,06 / 465 rổ, t +1,4/+1,0 → loại vì t | Sharpe +1,06, t +1,3/+1,0; tài khoản 10k: 0 stop-out (tối ưu: 11 lệnh lưới bị từ chối vì ký quỹ, lot max 7,99 → 3,80), mức KQ min kiểm 180%; **loi_log kiểm +1,146 vs placebo TB +1,170, q95 +1,511 → p = 0,93** → loại (cũng loại theo t) |
| — độ nhạy 1.000 USD 1:500 stop-out 20% | — | phần kiểm **3 stop-out**, vốn 1.000 → 2,34 USD, loi_log −0,45; placebo sống sót 15% → loại (stop-out, lỗ, p = 0,33) |
| Placebo random walk `--gia-lap-duong` seed 1-10, CÓ phí | Sharpe kiểm lưới dương **10/10**; giữ 0/10 (chỉ nhờ t) | Sharpe kiểm dương 8/10 (seed 1, 2 stop-out phần kiểm); **stop-out ở ít nhất một phần: 6/10 seed**; p placebo 0,16–0,91 (không seed nào ≤ 0,05); **giữ 0/10**, và cổng lưới tự nó loại 10/10 |
| Test | 165 lõi xanh; 71 file liên quan 1081 xanh | **+12 test** (`test_cong_luoi.py`); 71 file: **1093 xanh / 40 đỏ / 9 lỗi — 0 đỏ mới** (đỏ/lỗi giống hệt bản gốc; worktree sạch có thêm 10 đỏ do thiếu file dữ liệu cục bộ) |

Bảng placebo (random walk, tài khoản mặc định; t tối ưu/kiểm; stop-out tối ưu/kiểm; loi_log kiểm vs TB placebo; placebo sống sót; p):
| seed | sh kiểm | t | stop-out | loi_log | TB placebo | sống | p |
|---|---|---|---|---|---|---|---|
| 1 | −2,21 | +1,4/−1,5 | 0/1 | −3,58 | −1,66 | 67% | 0,76 |
| 2 | −2,75 | +0,2/−1,9 | 0/2 | −3,84 | −2,59 | 15% | 0,73 |
| 3 | +0,65 | +0,5/+0,4 | 0/0 | +1,06 | +0,93 | 100% | 0,16 |
| 4 | +1,21 | −1,4/+0,8 | 4/0 | +0,74 | +0,77 | 100% | 0,53 |
| 5 | +1,16 | +0,4/+0,8 | 0/0 | +0,56 | +0,50 | 98% | 0,63 |
| 6 | +0,32 | +0,8/+0,2 | 0/0 | +0,77 | +0,85 | 100% | 0,91 |
| 7 | +1,74 | +0,7/+1,2 | 0/0 | +0,86 | +0,80 | 100% | 0,21 |
| 8 | +2,35 | −0,9/+1,6 | 1/0 | +0,97 | −0,94 | 42% | 0,19 |
| 9 | +1,72 | −1,7/+1,2 | 3/0 | +1,27 | +0,76 | 93% | 0,18 |
| 10 | +0,83 | −2,4/+0,6 | 4/0 | +0,59 | −0,73 | 64% | 0,50 |
Seed 8: Sharpe kiểm +2,35 (đúng loại "thắng nhỏ đều" từng đánh lừa Sharpe) — cổng mới loại vì
stop-out phần tối ưu VÀ không thắng placebo (p 0,19).

**Kết luận**: không có edge. Breakout5 EURUSD +1,06 KHÔNG phân biệt được với tung đồng xu cùng
cấu trúc lưới (96% placebo cũng dương; p = 0,93) — chỉ là đặc tính martingale.
Kết quả: `/workspace/vong_eurusd_cong_luoi.json`, `/workspace/vong_eurusd_cong_luoi_1000.json`,
`/workspace/scratch/pl/s{1..10}.json`.

### Vấn đề mở
1. Placebo cho chân lệnh dừng trong bar (null cho mức giá) — chưa có; rổ hedge Breakout2/2-2/3
   chưa đi qua cổng tài khoản (không phải lưới; ngưỡng t cũ vẫn chặn).
2. Sống sót trên ~0,8 năm phần kiểm là phép thử YẾU cho đuôi martingale (placebo EURUSD sống 96%):
   cần chuỗi dài hơn / nhiều cặp, hoặc ước xác suất cháy theo năm từ placebo.
3. `SYMBOL_VOLUME_MAX`, stop-out từng lệnh kiểu MT5, số dư chưa trừ trượt/qua đêm.
4. Breakout4 (PivotsDay R1/S1) — vẫn bỏ qua có lý do (xem dưới).

---

## (trước) Vòng "LƯỚI MARTINGALE" (sau 54c8597e) — Breakout5 / Breakout5-2-2 dịch đúng như EA
### 1. Đọc (`nhan/ro_mql.py`: `doc_luoi` + trình thông dịch MQL nhỏ `_ThongDich`)
Hàm đóng của hai EA: cập nhật đỉnh `peakwin=MathMax(peakwin,profits)` (không về 0 khi lỗ) →
`if(peakwin>=E && profits<=peakwin*0.7) CloseAll()` → **cổng bar** `if(curTime==prevTime) return;`
→ khối lưới: `up = initup && giá <= S`, `down = !initup && giá >= S` → thêm lệnh **CÙNG chiều**,
`S = BID ∓ 30 point`, `volume = round2(lastvolume × 1.45)`, `peakwin=0`. KHÔNG giới hạn số lệnh.
- Khối lệnh không đọc bằng regex từng dòng: được **chạy thử** bằng một trình thông dịch tập con
  MQL5 (khai báo, gán, `if/else`, `SymbolInfoDouble(BID|ASK)`, `_Point`, `MathRound`,
  `NormalizeDouble`, hàm thuần chỉ phụ thuộc input như `GetStartVolume()`), cho cả hai trường hợp
  lệnh đầu mua / bán. Biến không rõ trong điều kiện, hàm lạ có thể có tác dụng phụ, điều kiện phụ
  thuộc số lệnh (ngoài `postotal>0`) → `_Kh` → **không dịch** (không đoán).
- Chuỗi lot lấy bằng cách chạy THẬT phép gán `lastvolume` 54 bước (không đoán công thức):
  0.02 → 0.03, 0.04, 0.06, 0.09, 0.13, 0.19, 0.28, 0.41, … (Breakout5 `MathRound(x*100)/100` và
  5-2-2 `NormalizeDouble(x,2)` + `if(volume<0.02)` cho cùng chuỗi — test kiểm).
- 5-2-2: `expectation = takeprofitamountperstartvolume × GetStartVolume() = 250×0.02 = 5` (tính từ
  input); lọc magic (`PosTotal`, `IsTRadeOpen`, `GetProfits`, `CloseAll(all=true)`) → giả định tài
  khoản chỉ có EA này (ghi `gia_dinh`). Nhánh `else if(zonesequence!=0)` (hedge vùng) **không tới
  được với input mặc định** `hedgeatlevel=0` → mã chết; đổi `hedgeatlevel=3` → KHÔNG dịch (test).
  Ở input mặc định 5-2-2 ≡ Breakout5 (khóa `ro` giống hệt → vòng lặp bỏ trùng).
- Hàm mở: `prevTime` chỉ gán SAU khi mở lệnh → **mở tối đa 1 lần/bar nhưng ở BẤT KỲ tick nào**
  khi đang không có lệnh (`ro.cong_mo_bar`). Cặp mua `giá < pivot giờ` / bán `giá >= pivot` bù nhau
  → khi rổ chốt GIỮA bar, EA vào lại ngay theo giá lúc đó (`vao_lai_giua_bar` → `muc_lai` ở
  `ngu_phap.sinh_chan`; `doc_ma._vao_lai_giua_bar` chỉ gắn khi chắc: 2 chân ngược chiều, một điều
  kiện `close <phép> M` cùng M, hai phép bù nhau, có cổng mở bar).
- Đột biến kiểm (test): `volumefactor=2` → lot 0.04/0.08/0.16; `HedgeRange=50` → ±50 point;
  `takeprofit…=500` → mốc 10$; bỏ cổng bar, chèn hàm lạ, `hedgeatlevel=3`, hoa hồng > 0,
  khối lượng theo vốn (`AccountInfoDouble`) → đều KHÔNG dịch.
### 2. Mô phỏng (`mo_phong.chay_he`, khóa `ro.luoi`)
- Lưới chỉ xét ở **lần gọi hàm đóng ĐẦU TIÊN của mỗi bar** (cổng `prevTime` toàn cục của hàm
  đóng — cả khi lần gọi đó là tick ngay sau lệnh mở), tại giá lúc đó (≈ open); không thêm giữa bar.
- Chốt đỉnh giữa bar tìm CHÍNH XÁC trên từng đoạn đơn điệu (như rổ hedge). Thêm lệnh khi vừa
  `CloseAll` cùng tick (`postotal` cũ) → đếm `ro_bat_thuong`, không mở.
- Chẩn đoán mới `chi_tiet["luoi"]`: số lệnh / lot lớn nhất một rổ, lỗ thả nổi lớn nhất ($).
  **KHÔNG mô phỏng** ký quỹ / stop-out / `SYMBOL_VOLUME_MAX` của sàn (phụ thuộc tài khoản & sàn,
  không có trong mã) — đây là giới hạn lớn nhất của kết quả lưới.
### Số đo
| | 54c8597e | bây giờ |
|---|---|---|
| Điểm vào dịch được (`do_moc.py`) | 11/22 = 50,0% | **13/22 = 59,1%** (8 tín hiệu + 3 hedge + **2 lệnh thêm của lưới**) |
| Phân loại | dịch 8+3 · quản lý vị thế 4 · mã chết 5 · chưa dịch 2 | dịch 8+5 · quản lý vị thế **1** (hedge Breakout4) · mã chết **6** (+ nhánh hedge vùng 5-2-2 ở input mặc định) · chưa dịch 2 |
| Thoát lệnh đúng EA | B1, B2, B2-2, B3, Template | + **Breakout5, 5-2-2 (lưới + chốt đỉnh 5$)** — không còn hệ nào thoát theo `giu` N bar trong mẫu |
| Test lõi + mới | 152 xanh | **165 xanh** (`test_luoi_martingale.py` 13; 1 kỳ vọng cũ sửa: 5-2-2 có 2 điểm vào dịch được) |
| 70 file test chạm `doc_ma/ngu_phap/mo_phong/vong/chi_phi/ro_mql` | 1068 xanh / 40 đỏ / 9 lỗi | **1081 xanh / 40 đỏ / 9 lỗi — 0 đỏ mới** (đỏ cũ giống hệt bản gốc trên cùng tập file; 2 đỏ `test_sua_bang_llm` chỉ hiện khi chạy cả bộ — phụ thuộc thứ tự, chạy riêng xanh ở cả hai bản) |

### Vòng lặp EURUSD H1 (`/workspace/eurusd_h1_server.csv`, 17.127 bar) — CÓ PHÍ THẬT
`7 bóc được, 1 trùng (Breakout5 = 5-2-2), 6 chạy được → **giữ lại: 0**` (`/workspace/vong_eurusd_luoi.json`).
Ngưỡng KHÔNG đổi: t ≥ 2,0 tối ưu / 1,5 kiểm, ≥47 / ≥20 lệnh, phí thật.
| hệ | trước (giu N bar, riêng từng chân), kiểm | **bây giờ** (lưới đúng EA), kiểm | t (tối ưu/kiểm) |
|---|---|---|---|
| Breakout5-2-2 (= Breakout5) | mua −1,65/49 · bán +0,39/93 | **+1,06 / 465 rổ** (842 lệnh thêm) | **+1,4 / +1,0** → không giữ |
| các hệ khác | — | không đổi so với 54c8597e | — |
- Lưới trên EURUSD: phần tối ưu tối đa **17 lệnh/rổ, lot 7,99, lỗ thả nổi 6.086 $** (lệnh đầu 0,02 lot);
  phần kiểm 13 lệnh, 1,81 lot, 1.431 $. Mọi rổ đóng bằng chốt đỉnh (không có cắt lỗ).
- **PLACEBO (random walk `--gia-lap-duong`, CÓ phí, seed 1-10): lưới cho Sharpe kiểm DƯƠNG 10/10
  seed (+0,16 … +2,35, trung bình ≈ +1,1)** — đúng đặc tính martingale (thắng nhỏ đều, đuôi phá sản
  hiếm, không xảy ra trong mẫu hữu hạn và không mô phỏng ký quỹ). Nên Sharpe +1,06 trên EURUSD
  **KHÔNG phân biệt được với giả dược → KHÔNG phải bằng chứng edge**. Giữ lại 0/10 seed placebo.
- **Kết luận vẫn như các vòng trước: edge sau phí được giữ = 0.** Dịch đúng hơn tăng độ trung thực
  (thoát lệnh, khối lượng, vào lại giữa bar) nhưng không tạo ra cơ chế qua ngưỡng.

### Breakout4 (PivotsDay R1/S1) — BỎ QUA có ghi lý do (không đoán)
Có mã `MultiPivots.mqh` (/tmp, peterthomet), nhưng dịch chắc chắn cần cả ba thứ chưa có:
1. **`±5*_Point`** quanh R1/S1 (`PivotsIsPivotRange(close+5pt, close−5pt, …)`): phụ thuộc symbol;
   DSL `toan_hang` không biết `_Point` → phải thêm tham số tường minh `diem` vào lớp tín hiệu
   (hiện chỉ mô phỏng biết `diem`). Không tự gán 1e-5.
2. **Biên ngày của pivot**: `PivotsFindWeekDayStart` tự dò giờ đầu ngày từ khe cuối tuần (>86400 s)
   trên giờ máy chủ, `PivotsCalculatePivotRange(DAY)` + `PivotsCleanupWeeekendAndDaysGaps` — cần
   dịch nguyên văn (Chủ nhật / ngày lễ) mới đúng; `PivotsDayList[1]` là ngày nào phải kiểm tay.
3. **Vào lệnh MỖI tick** (cổng `prevTime` đã bị comment) khi giá rơi VÀO DẢI [L−5pt, L+5pt] →
   mô phỏng cần kiểu kích hoạt "dải" trong bar (chưa có). Kèm luật 1 lệnh/ngày + rổ hedge (đã đọc được).
→ Breakout4 vẫn `co_che=0`; hedge của nó vẫn `quan_ly_vi_the` ("lệnh đầu của rổ chưa dịch").

### Vấn đề mở (ưu tiên vòng sau)
1. ~~**Cổng giữ cho lưới/martingale**~~ (ĐÃ LÀM ở vòng sau — xem đầu file): Sharpe/t không phải phép thử hợp lệ (placebo dương 10/10). Cần
   mô hình ký quỹ/stop-out với vốn & đòn bẩy KHAI BÁO, hoặc so với phân phối placebo cùng cấu trúc,
   trước khi một hệ lưới được phép "giữ". (Chưa đổi ngưỡng — chỉ ghi lại.)
2. `SYMBOL_VOLUME_MAX` / ký quỹ: tham số hóa tường minh (`lot_toi_da`, vốn) khi có thông số sàn.
3. Breakout4: ba mục trên. CurrencyStrength1 (`CSValues[s1]`, iCustom), Pivots1: chưa dịch.
4. (cũ) ngưỡng tiền theo USD; `MinStopDistance`; đường giá trong bar nên kiểm bằng M1.

---

## (trước) Vòng "RỔ HEDGE + SL/TP ATR" (sau 21cc69dc) — thoát lệnh Breakout2/2-2/3 và Template đúng như EA
### 1. Rổ lệnh Breakout2/2-2/3 (`nhan/ro_mql.py` mới, gắn vào `doc_ma`)
Trước: ba EA này đóng lệnh sau `giu` bar — một hệ KHÁC hẳn. Mã thật: `OnTick` gọi
`checkForClose()` MỖI tick khi có vị thế, hàm đó làm việc trên TỔNG lời lỗ (tiền) của cả rổ:
`profits=GetProfits()` → cập nhật đỉnh `peakwin` → `if(peakwin>=45 && profits<peakwin*0.9) CloseAll()`
→ `if(profits<=-120) CloseAll()` → hedge NGƯỢC chiều khi số lệnh == 1.
- `doc_ro(vb)` đọc đúng các dạng đó, câu lệnh lạ trong phần mã sống → trả `None` + lý do
  (không đoán). Phần sau `return;` vô điều kiện bỏ qua (mã chết). Kết quả = khoá DSL `ro`:
| EA | đỉnh | cắt lỗ | hedge |
|---|---|---|---|
| Breakout2 | ≥45$, đóng khi <0,9·đỉnh; đỉnh về 0 khi lời ≤0 | −120$ | 0,4 lot khi BID chạm ASK_vào − 300 point (mua) / BID_vào + 300 (bán) |
| Breakout2-2 | như trên | −120$ | 0,3 lot khi lời ≤ −30$ |
| Breakout3 | ≥45$; đỉnh = max từ lúc vào/hedge (về 0 khi vào lệnh và khi hedge) | −120$ | 0,4 lot, khoảng = input `HedgeRange`=300 |
- Khối `if(postotal==22)` (Breakout2/3/4): KHÔNG BAO GIỜ tới được — lệnh đầu chỉ mở khi không có
  vị thế, mỗi khối hedge thêm đúng 1 lệnh → số lệnh ∈ {1,2}. Xếp `ma_chet` (giả định tài khoản chỉ có EA này).
- Breakout2 ≡ Breakout3 về hành vi (số đo giống hệt): đỉnh chỉ có tác dụng khi ≥45, mà lời rơi
  từ ≥45 sẽ bị chốt trước khi về ≤0, nên hai cách reset đỉnh cho cùng kết quả — kiểm chứng tốt.
- Giả định ghi trong `gia_dinh`: lời lỗ tính bằng tiền yết giá (USD cho EURUSD), hợp đồng
  100.000/lot, tài khoản HEDGING, `_Point`=1e-5 (ước từ giá, có cảnh báo).
### 2. Mô phỏng rổ (`mo_phong.chay_he`, chân có `ro`)
- Lời lỗ EA = Σ lot·100000·(chiều·(giá−giá_vào)) − 1 spread mỗi lệnh (giá là BID như biểu đồ MT5).
  Trên mỗi đoạn đơn điệu của đường giá trong bar lời lỗ TUYẾN TÍNH theo giá → mức chốt đỉnh /
  cắt lỗ / hedge tìm được CHÍNH XÁC (không lấy mẫu). Thứ tự trong một tick y hệt mã: cập nhật
  đỉnh → chốt → cắt lỗ → hedge (với `postotal` đọc trước khi đóng). Gap qua mức → khớp ở open.
  Ca EA mở hedge “mồ côi” ngay sau CloseAll (chỉ khi gap) → đếm `ro_bat_thuong` (EURUSD: 0).
- Lợi suất theo vốn danh nghĩa LỆNH ĐẦU (hedge 0,4 lot = trọng số 4); phí spread/trượt theo
  khối lượng từng lệnh; qua đêm tính RIÊNG lệnh mua và lệnh bán (tài khoản hedging trả cả hai).
- `so_lenh` = số rổ (đơn vị độc lập để đếm đủ lệnh); số hedge báo riêng.
### 3. SL/TP ATR của Template (`ro_mql.doc_sltp_kc`) — form chắc chắn nên đã dịch
`OpenTrade(sig>0?BUY:SELL, atr*InpSlAtrMult, atr*InpTpAtrMult)`; trong `OpenTrade`:
`slDist=MathMax(slDist,MinStopDistance())`, `sl=price−dir·slDist`, `tp=price+dir·tpDist`,
`lot=LotsForRisk(slDist)` (1% vốn mỗi SL), `atr` = `CopyBuffer(iATR(...,InpAtrPeriod),0,1,1,v)`.
- `sltp: {sl_kc: 2×ATR14, tp_kc: 3×ATR14, sl_kc_min_spread: 3, rui_ro: 0.01}`; ATR kiểu MT5 =
  trung bình CỘNG của TR (`{"chi_bao":"atr","kieu":"sma"}` mới — DSL cũ là Wilder); bar 1 → trễ 0.
- `MinStopDistance`: STOPS/FREEZE level phụ thuộc sàn → GIẢ ĐỊNH = 0 (→ 3×spread), ghi `gia_dinh`.
- Trọng số lệnh = rui_ro·giá/khoảng_SL (khối lượng theo rủi ro). `SpreadOK()` (≤30 point) → lọc
  bằng spread theo giờ của mô hình chi phí. `CountMyPositions()>0` → một vị thế một lúc (chạy
  NHÓM qua `nhom_he`); hai điều kiện này bỏ khỏi `bo_qua_quan_tri` vì đã mô hình hoá.
- Tham số EA phơi cho tối ưu: `sltp_atr_n`, `sltp_sl_he`, `sltp_tp_he` (ứng viên ×0,5…×2).
- Đột biến mã (ATR ở bar 0, SL dạng khác) → KHÔNG dịch (test).
### Số đo
| | 21cc69dc | bây giờ |
|---|---|---|
| Điểm vào dịch được (`do_moc.py`) | 8/22 = 36,4% | **11/22 = 50,0%** = 8 tín hiệu thanh nến + **3 lệnh hedge mô phỏng đúng trong `ro`** |
| Phân loại 22 điểm vào | dịch 8 · quản lý vị thế 10 · mã chết 2 · chưa dịch 2 | dịch 8 + hedge dịch 3 · quản lý vị thế 4 (Breakout4 hedge vì lệnh đầu chưa dịch; lưới martingale Breakout5/5-2-2) · mã chết 5 (+3 khối `postotal==22` không tới được) · chưa dịch 2 |
| Tín hiệu thanh nến | 8/10 | 8/10 (không đổi — không nới gì ở phần tín hiệu) |
| Thoát lệnh đúng EA | Breakout1 | Breakout1 + **Breakout2, 2-2, 3 (rổ)** + **Template (SL/TP ATR)**; còn `giu` N bar: Breakout5-2-2 (lưới) |
| Test lõi (`test_doc_ma*`, `test_trong_bar`, `test_sltp_he`, `test_toan_hang_tuyen_tinh`) + mới | 122 xanh | **152 xanh** (`test_ro_hedge.py` 20, `test_sltp_atr.py` 10; 3 test cũ sửa kỳ vọng phân loại) |
| 69 file test chạm `doc_ma/ngu_phap/mo_phong/vong/chi_phi` | worktree sạch 21cc69dc: 1028 xanh / 50 đỏ / 9 lỗi thu thập | **1068 xanh / 40 đỏ / 9 lỗi — 0 đỏ mới** (10 đỏ chỉ ở worktree sạch: thiếu file dữ liệu cục bộ) |
| Placebo `--gia-lap-duong` (7 dòng/seed) | — | CÓ phí seed 1-12: **giữ 0/84**; KHÔNG phí seed 1-20: giữ 2/140 (1,4%: Template seed 5, Breakout5-2-2 bán seed 20) |

### Vòng lặp EURUSD H1 (`/workspace/eurusd_h1_server.csv`, 17.127 bar) — CÓ PHÍ (mặc định)
`9 bóc được, 2 trùng (Breakout5=5-2-2), 7 chạy được → **giữ lại: 0**`. Kết quả `/workspace/vong_eurusd_ro.json`.
| cơ chế | trước (21cc69dc) kiểm sau tối ưu, t | **bây giờ**: kiểm gốc → sau tối ưu | t (tối ưu/kiểm) | ghi chú |
|---|---|---|---|---|
| HỆ Breakout1 | −2,36/187, −1,3/−2,1 | −4,10/204 → −2,36/187 | −1,3/−2,1 | không đổi |
| HỆ Breakout2-2 (rổ, hedge theo lời −30) | −3,03/217 (giữ N bar), −1,4/−2,8 | −3,07/93 → −1,67/88 (24+37 hedge) | −1,6/−1,5 | giờ 8→9 |
| HỆ Breakout2 (=Breakout3) (rổ, hedge 300 point) | (trùng 2-2 vì cùng điểm vào) | −3,29/110 → −2,07/112 (38+36 hedge) | −0,2/−1,9 | giờ 8→11 |
| HỆ Template (SL/TP ATR, rủi ro 1%, 1 vị thế) | mua −1,60/50 · bán +0,43/39 (riêng, giữ N bar) | −4,31/359 → −0,33/53 | −0,7/−0,3 | ATR 10, SL 2,5×, TP 12× |
| Breakout5-2-2 mua / bán | −1,65/49 · +0,39/93 | không đổi | −0,6/−1,5 · −1,1/+0,3 | thoát vẫn `giu` (lưới martingale chưa dịch) |
Toàn kỳ (không chia), có phí: Breakout2 427 rổ = 285 chốt đỉnh + 141 cắt lỗ −120$, giữ trung vị
15 bar; lời TB/rổ trước phí ngoài spread ≈ −2,5$ → spread (0,47 log) ăn hết. Kết luận vẫn như vòng
trước: mô hình thoát lệnh đúng hơn KHÔNG làm xuất hiện edge sau phí.

### Vấn đề mở (ưu tiên vòng sau)
1. Breakout5 / 5-2-2: lưới martingale (`stepprice`, `volumefactor`, `hedgeatlevel`, `zonesequence`,
   cổng `prevTime` mỗi bar) — chưa dịch, vẫn `giu` N bar. Breakout4: lệnh đầu cần `PivotsDay` R1/S1.
2. Ngưỡng tiền (45/−120/−30$) chỉ đúng cho cặp yết giá USD + tài khoản USD; cặp khác cần quy đổi.
3. `MinStopDistance` giả định STOPS/FREEZE level = 0; nên đọc từ dữ liệu sàn khi có.
4. Đường giá trong bar vẫn là giả định (gần open trước); rổ hedge nhạy với thứ tự chạm → nên kiểm
   bằng M1 (cũ). Tối ưu Template 4 tham số → t tối ưu trên placebo thường >2; phần KIỂM là chốt chặn.
5. (cũ) `PivotsDay`, `SellLimit/BuyLimit`, kho .mq5 lớn, bộ chọn sàn.

---

## (trước) Vòng 10/10 đêm — SL/TP + KÉO SL + MỘT LỆNH/NGÀY + MÔ PHỎNG CẢ HỆ (phí thật)
### 1. Đọc từ mã EA (`nhan/doc_ma.py`)
- **SL/TP** (`_sltp_mql`): từ `PositionOpen(sym, type, vol, price, sl, tp)` tìm phép gán
  trong nhánh `if(upbreakout){...}`: `price = SymbolInfoDouble(_Symbol,SYMBOL_ASK|BID)`,
  `sl = <mức>` (phải dịch được thành mức CỐ ĐỊNH trong bar), `tp = price ± ((price−sl)·k)`
  với k là hằng/input (`TPFactor`). Breakout1: SL mua = đáy phiên 5-8h, SL bán = đỉnh
  phiên, TP = 1R. Mẫu khác (TP hằng số pip, `price−calculateDistance`) → KHÔNG đoán, ghi
  `gia_dinh`, giữ `giu` như cũ. Breakout2/2-2/3/5 mở lệnh `NULL, NULL` → không có SL/TP.
- **Kéo SL** (`_keo_sl_mql`): `sl = MathMax(sl, lowrange)` + `PositionModify` trong khối
  `if(posType==POSITION_TYPE_BUY)` (MathMin cho SELL), `sl` đọc từ `POSITION_SL`, hàm gọi
  từ `OnTick` → Breakout1: kéo theo `thap_nhat(low,3)` / `cao_nhat(high,3)` (3 bar đã đóng).
- **Sửa lỗi kèm** (`_bang_mql`): mảng `highs/lows` được `Copy*` ở NHIỀU hàm; bản cũ giữ lần
  Copy CUỐI trong file nên `lowrange` của `checkForClose` bị dịch thành đáy PHIÊN. Giờ lấy
  lần Copy gần nhất TRƯỚC phép gán. (JSON 14 cơ chế trước/sau giống hệt ngoài khoá mới.)
- **Một lệnh/ngày** (`_mot_lenh_ngay_mql`): `if(a==dt.day || b==dt.day) return;` trước lệnh
  + `if(up) a=dt.day;` sau lệnh → `"mot_lenh_ngay": {"nhom", "chan_boi", "dat"}`; guard bỏ
  khỏi `bo_qua_quan_tri` (giờ được mô hình hoá). Có ở Breakout1, 2, 2-2, 3.
- **Cờ vs lọc** (`trong_bar.loc`): `bool up = current[0].high > H;` là CỜ (cực trị bar đang
  chạy, bật là giữ suốt bar); `if(up && close<MA) return;` là LỌC gắn với cờ. Đo trên
  EURUSD: 42/682 lệnh (6%) của mô hình độc lập là lệnh EA KHÔNG vào được (giá đã xuyên
  biên kia trong cùng bar → hai lọc MA trái nhau → `return` hết bar).
### 2. DSL (`nhan/ngu_phap.py`)
- Khoá mới: `"sltp": {"sl": toán hạng, "tp": hệ số R | null, "keo": toán hạng | null}`,
  `"mot_lenh_ngay"`, `trong_bar.loc`; `kiem_khai_bao` kiểm cả ba.
- `sinh_chan(spec, df)` → mảng biết tại close bar i (cho/mức/SL/kéo/cờ/lọc).
- `tham_so_cua`: có `sltp` thì KHÔNG phơi `giu` (EA không đóng theo giờ) mà phơi `sltp_tp`
  (TPFactor) và `sltp_keo_n`; `ap_tham_so` đặt ngược được.
### 3. Mô phỏng (`nhan/mo_phong.chay_he`)
Một tài khoản, nhiều chân: một vị thế một lúc (`if(PositionSelect) checkForClose(); else
checkForOpen();`), luật ngày theo NGÀY-TRONG-THÁNG như EA, tick đầu: hết giờ/gap qua SL/TP
→ đóng ở open, rồi kéo SL (chỉ siết, bỏ nếu mức mới vượt giá hiện tại – MT5 từ chối).
Đường giá trong bar: O → cực trị GẦN open hơn → cực trị kia → C (cùng quy tắc dự án ở
`chay_tpsl`, không mặc định SL). Đóng giữa bar xong vẫn có thể vào lại (EA chạy mọi tick).
Chặn chéo cờ/lọc như trên. `nhat_ky=` ghi từng lệnh để soát tay. Không nhìn trước: test cắt.
### 4. Vòng lặp (`vong_thu_nghiem.py`)
- Các chân cùng `mot_lenh_ngay.nhom` chạy CHUNG (`danh_gia_nhom`), một dòng kết quả “HE …”,
  in thêm từng chân + mô hình cũ (riêng, giữ N bar) để so.
- Tối ưu cả hệ (`toi_uu_nhom`): tham số có mặt ở mọi chân với CÙNG giá trị là MỘT input của
  EA (giờ, chu kỳ MA, TPFactor, kéo SL) → buộc chung; ứng viên TPFactor {0.5…3}R.
- Ngưỡng giữ KHÔNG đổi: t ≥ 2,0 tối ưu / 1,5 kiểm, ≥47 lệnh tối ưu & ≥20 lệnh kiểm, phí thật.
- `--he-so-spread F`: chỉ là ĐỘ NHẠY (nhân spread đo được), mặc định 1 = phí thật.

### Số đo
| | 9c39b674 | bây giờ |
|---|---|---|
| Điểm vào dịch được (`do_moc.py`) | 8/22 = 36,4% | **8/22 = 36,4%** (vòng này sửa ĐỘ ĐÚNG mô phỏng, không đổi tỷ lệ) |
| Cơ chế có SL/TP thật / luật ngày | 0 / 0 | **2 (Breakout1) / 8 chân (Breakout1, 2, 2-2, 3)** |
| `test_sltp_he.py` (mới) | — | **18 xanh** (đọc SL/TP/kéo/luật ngày + 5 đột biến mã EA, khớp giá tay: TP, gap SL, kéo SL, luật ngày bán chặn mua, một vị thế, chặn chéo cờ/lọc, phép cắt, placebo) |
| `test_doc_ma*`, `test_trong_bar`, `test_toan_hang_tuyen_tinh` | 104 xanh | 104 xanh (2 test sửa kỳ vọng: Breakout1 giờ là 1 dòng NHÓM 2 chân) |
| 54 file test chạm `doc_ma`/`ngu_phap`/`mo_phong`/`vong` | (worktree sạch 9c39b674) 920 xanh / 46 đỏ / 5 lỗi | **948 xanh / 36 đỏ / 5 lỗi, 0 đỏ mới** (10 đỏ chỉ ở worktree sạch – thiếu file dữ liệu cục bộ; đỏ còn lại có sẵn: scipy, nao.db…) |
| Placebo `--gia-lap-duong` seed 1-16, KHÔNG phí | — | **giữ 0/16** (hệ Breakout1: Sharpe kiểm gốc TB +0,28; t tối ưu thường >2 – quá khớp trong mẫu, phần kiểm chặn được) |

### Vòng lặp EURUSD H1 (`/workspace/eurusd_h1_server.csv`, 17.127 bar) — CÓ PHÍ (mặc định)
Spread 1,63 bps/chiều (XM), trượt 0,41 bps, qua đêm mua +2,48%/bán −0,45%/năm.
`10 bóc được, 4 trùng, 6 chạy được → **giữ lại: 0**`. Kết quả: `/workspace/vong_eurusd_sltp.json`.
| cơ chế | tối ưu: gốc → tốt nhất (sh/lệnh) | kiểm sau tối ưu | t (tối ưu/kiểm) | ghi chú |
|---|---|---|---|---|
| **HỆ Breakout1** (mua+bán, SL/TP/kéo/1 lệnh ngày) | −3,12/474 → −0,96/426 | −2,36/187 (mua −1,61/88, bán −1,72/99) | −1,3/−2,1 | tham số chọn: TP 3R, kéo 4 bar, giờ 9-14, SMA 19 trễ 20 |
| (cũ, cùng phí) Breakout1 mua / bán riêng, giữ 1 bar | | −1,01/124 · −0,50/113 | −1,0/−0,9 · −0,1/−0,5 | mô hình SAI (không SL/TP, không luật ngày) |
| HỆ Breakout2-2 (=2=3; giu, luật ngày) | −10,1/508 → −0,98/507 | −3,03/217 | −1,4/−2,8 | thoát vẫn `giu` (lưới hedge chưa dịch) |
| Breakout5-2-2 mua / bán | | −1,65/49 · +0,39/93 | −0,6/−1,5 · −1,1/+0,3 | không đổi |
| Template mua / bán | | −1,60/50 · +0,43/39 | −0,5/−1,4 · −0,9/+0,4 | không đổi |
So sánh: **không phí** hệ Breakout1 GIỮ (kiểm +1,75/194, t +2,9/+1,6); **spread ×0,33** (~ECN,
chưa cộng hoa hồng) vẫn 0 giữ (hệ Breakout1 kiểm −0,45, t +0,7/−0,4). Biên lợi thô ~1 bps/lệnh
(682 lệnh, thắng 47,5%, giữ TB 2,1 bar) < phí khứ hồi ~4 bps → không có edge giao dịch được.

### Lựa chọn mở (chưa làm, không chặn)
- **Sàn/tài khoản**: spread hiện đo từ XM micro (1,63 bps/chiều). Tài khoản ECN rẻ hơn ~3 lần
  về spread nhưng có hoa hồng (~0,3 bps/chiều EURUSD). Nên thêm bộ chọn sàn (spread + hoa
  hồng + qua đêm theo sàn) khi có số liệu sàn thật; tạm thời `--he-so-spread` để đo độ nhạy.

### Vấn đề mở (ưu tiên vòng sau)
1. Breakout2/2-2/3: thoát vẫn là `giu` N bar — lệnh hedge/lưới (`Tradesinfo.*`) trong
   `checkForClose` chưa dịch, nên hệ này vẫn là xấp xỉ.
2. Template: SL/TP theo ATR (`InpSlAtrMult`/`InpTpAtrMult`, `g_trade.Buy(lot,_Symbol,0,sl,tp)`)
   chưa đọc — mẫu `price ± dir*slDist` với `slDist` từ ATR.
3. Đường giá trong bar là giả định (gần open trước); với H1 có thể kiểm bằng dữ liệu M1.
4. Chỉ báo bar 0 đổi theo tick (cũ); `PivotsDay`, `SellLimit/BuyLimit`, kho .mq5 lớn (cũ).
5. Tối ưu cả hệ có 6 tham số → t tối ưu trên placebo thường > 2; ngưỡng phần KIỂM là chốt chặn
   thật. Nếu thêm tham số nên cân nhắc hiệu chỉnh đa phép thử (không nới ngưỡng).

---

## (trước) Ghi chú nâng cấp (Grok trên brain2) — cập nhật 2026-10-10 (khuya, giờ VN)

## Vòng 10/10 khuya (2) — LỆNH DỪNG TRONG BAR + ĐỦ LỆNH HAI PHẦN + **PHÍ THẬT**
### 0. Lỗi lớn tìm ra: vòng lặp chạy KHÔNG PHÍ từ trước tới giờ
`vong_thu_nghiem.danh_gia` gọi `CP.MoHinhChiPhi(ma="EURUSD")` — constructor trần, spread =
trượt = phí qua đêm = 0. Mọi bảng số vòng lặp bên dưới (kể cả "Breakout1 mua t=+1.5/+2.3")
là **không phí** dù ghi chú nói "sau phí". Đã sửa: `mo_hinh_chi_phi()` = `chi_phi.tu_du_lieu`
(EURUSD: spread 1,63 bps/chiều đo từ bar H1 XM, trượt 0,41 bps, qua đêm mua +2,48 %/năm,
bán −0,45 %/năm, `do_tin=SAN`). `--khong-phi` chỉ để so với số cũ.

### 1. EA kiểm lại MỖI tick → lệnh dừng trong bar (`nhan/doc_ma.py`)
- Giá sống bar 0 (`current[0].high/low/close`, `iClose(..,0)`) giờ đi qua token nội bộ
  `_gia0_` → toán hạng `close` có dấu `_bar0` (bóc ra trước khi trả co_che; nghĩa DSL cũ
  KHÔNG đổi — so JSON 14 cơ chế trước/sau: giống hệt, chỉ thêm khoá mới).
- `_kiem_moi_tick`: đi chuỗi gọi từ hàm chứa lệnh vào ngược lên `OnTick`, tìm cổng bar mới
  CÓ HIỆU LỰC: `if(!IsNewBar()) return;`, `if(dt.min!=0) return;` (phút đầu), `if(curTime==
  prevTime) return;` CHỈ KHI `prevTime=curTime;` đứng trước mọi `return` sau cổng; lời gọi
  nằm trong `if(IsNewBar…)`.
- Phân loại điều kiện: KÍCH HOẠT (`giá_sống ? mức`, mức cố định trong bar) / CHO PHÉP (không
  dùng giá sống) / phức tạp. Kết quả:
| file | phát hiện | xử lý |
|---|---|---|
| Breakout1 (mua/bán) | mỗi tick (prevTime gán sau lệnh) | `trong_bar` `>`/`<`, kích = biên phiên 5-8h + lọc MA; giờ 9-17 là cho phép |
| Breakout2, 2-2, 3 | mỗi tick (bỏ cổng) | **cặp bù nhau** (giá > giữa / giá < giữa cùng mức): tick đầu luôn kích một chiều → dịch tick đầu là ĐÚNG, không đổi |
| Breakout5, 5-2-2 | cổng `dt.min!=0` | không đổi |
| Template | `if(!IsNewBar()) return;` ở OnTick | không đổi |
- DSL (`ngu_phap.py`): khoá tuỳ chọn `"trong_bar": {"huong": ">"|"<", "kich": [chỉ số vao]}`,
  `sinh_trong_bar(spec, df)` → (cho_phep, muc, huong) biết tại close bar i; `kiem_khai_bao`
  kiểm khoá này. `vao` giữ bản xấp xỉ tick đầu (vân tay/tham số không đổi; tối ưu `vao[k].phai`
  đổi luôn mức khớp).
- Khớp lệnh (`mo_phong.chay_dung_trong_bar`): bar j=i+1, `>`: open>mức → khớp open (gap),
  high>mức → khớp ở mức; giữ tới open bar j+giu; phí spread+trượt mỗi lần vào/ra. Không nhìn
  trước: chỉ dùng O/H/L của chính bar j (lệnh chờ nằm sẵn) + cho_phep/muc bar ≤ i (test cắt).
- Placebo đúng cho lệnh trong bar: `du_lieu_gia_lap_duong` (bar dựng từ 240 bước con — râu
  nến là cực trị THẬT; giả lập cũ vẽ râu bằng nhiễu độc lập nên sai cho lệnh dừng).
  20 seed × 8 cơ chế, không phí: giữ 3/160 (1,9%), Sharpe gốc kiểm trung bình của cơ chế
  `trong_bar` +0,07 (≈0, đúng định lý dừng tuỳ chọn). Có phí: giữ 0/160.

### 2. Đủ lệnh ở CẢ HAI phần (`vong_thu_nghiem.py`)
- Phần kiểm ≥ `--lenh-toi-thieu` (20); phần tối ưu ≥ `lenh_min_phan_tu` = ⌈20·70/30⌉ = **47**
  (cùng mật độ lệnh — bộ tối ưu không được nhìn phần kiểm nên đòi mật độ thay vì đòi số lệnh
  kiểm). Bộ tối ưu chỉ chấp nhận tham số đạt 47; thiếu ở phần nào → `it_lenh`, không giữ.
- Breakout5-2-2 mua: trước chọn `giu=8` (20 lệnh tối ưu, phơi nhiễm 99,6% ≈ mua-giữ, 5 lệnh
  kiểm); giờ chọn tham số có 49 lệnh kiểm.

### Số đo
| | 890ba3e4 | bây giờ |
|---|---|---|
| Điểm vào dịch được (`do_moc.py`) | 8/22 = 36,4% | **8/22 = 36,4%** (không đổi; thêm mô hình trong bar cho 2 cơ chế) |
| `test_doc_ma*` + `test_toan_hang_tuyen_tinh` | 90 xanh | 90 xanh |
| `test_trong_bar.py` (mới) | — | **14 xanh** (phát hiện, cổng prevTime/IsNewBar, khớp giá, cắt không nhìn trước, placebo, đủ lệnh, phí ≠ 0) |
| 52 file test chạm `doc_ma`/`ngu_phap`/`vong`/`mo_phong` (worktree sạch, + test_trong_bar) | 906 xanh / 46 đỏ / 5 lỗi thu thập | **920 xanh / 46 đỏ / 5 lỗi — cùng đúng tập đỏ, 0 đỏ mới** (tập đỏ có sẵn ở 890ba3e4, không liên quan thay đổi này) |

### Vòng lặp EURUSD H1 (`/workspace/eurusd_h1_server.csv`, 17.127 bar)
| cơ chế | không phí, tick đầu (cũ) | không phí, trong bar | **CÓ PHÍ** (thật), trong bar | t có phí (tối ưu/kiểm) |
|---|---|---|---|---|
| Breakout1 mua | kiểm gốc +1,06/103 l | +1,57/214 → tối ưu +2,54/189, t +2,6/+2,3 (GIỮ) | gốc −2,82/214 → tối ưu −1,01/124 | −1,0/−0,9 |
| Breakout1 bán | −0,69/140 | +2,39/229 → +2,40/160, t +3,5/+2,2 (GIỮ) | −2,25/229 → −0,50/113 | −0,1/−0,5 |
| Breakout2-2 mua/bán | | | −9,0 / −7,9 gốc → −2,7 / −1,7 | âm |
| Breakout5-2-2 mua/bán | | | −15,4 / −14,4 gốc → −1,65/49 l / +0,39/93 l | −0,6/−1,5 · −1,1/+0,3 |
| Template mua/bán | | | −17,0 / −16,1 gốc → −1,6/50 l / +0,43/39 l | âm |
**Giữ lại (luật trung thực, có phí): 0.** Không phí thì mô hình trong bar giữ 2 (Breakout1 cả
hai chiều) — nhưng biên lợi nhuận đó nhỏ hơn spread+trượt (~4 bps khứ hồi), nên không phải
edge giao dịch được. Kết quả ghi `/workspace/vong_eurusd_tb.json` (có phí) và
`/workspace/vong_eurusd_tb--khong-phi.json`.

### Vấn đề mở
1. Chỉ báo đọc ở bar 0 (`MaValues[last]`) cũng đổi theo tick — hiện coi là cố định (tre 0);
   Breakout1 dùng phần tử cũ nhất nên không ảnh hưởng.
2. "1 lệnh/ngày" (`lastupday/lastdownday`) vẫn bỏ qua (quản trị) — trong bar, chiều kia
   khớp trước sẽ chặn chiều này cả ngày; chưa mô hình hoá.
3. SL/TP của EA (Breakout1: SL = biên đối diện, TP = R·TPFactor) chưa dịch — vẫn `giu` N bar.
4. Spread EURUSD lấy từ XM micro (1,63 bps/chiều) — tài khoản ECN rẻ hơn ~3 lần; nên thêm
   lựa chọn sàn khi chạy vòng lặp.
5. (cũ) `PivotsDay`, `SellLimit/BuyLimit`, kho .mq5 lớn.

---

## (trước) Vòng 10/10 khuya — SỬA LỆCH MỘT BAR trong quy ước chỉ số MQL5

### Quy ước mới (ghi ở `nhan/doc_ma.py`, khối chú thích trên `_ten_bar_mql`)
Mô phỏng quyết định ở ĐÓNG bar i, vào lệnh ở OPEN bar i+1. EA MQL5 chạy ở TICK ĐẦU
của bar mới (`IsNewBar`, `curTime!=prevTime`, `dt.min==0`) = đúng lúc mở bar i+1.
| MQL5 | DSL (mới) | bản cũ |
|---|---|---|
| `iClose(...,k)`, `arr[k]` với k ≥ 1 (bar đã đóng) | `tre k−1` (`iClose(..,1)` = `close`) | `tre k` (trễ thừa 1 bar) |
| bar 0 `current[0].open/high/low/close` (mới có 1 tick) | `close` (giá tick đầu ≈ close bar i) | `high`/`low`/`close` của bar i |
| chỉ báo ở bar 0 (`MaValues` phần tử mới nhất) | `tre 0` | `tre 0` (nhưng các phần tử cũ hơn lệch 1) |
| `CopyHigh(..,a,b,..)` số | `cao_nhat(high,b) tre a−1` (a=0 → b−1 bar, tre 0) | `tre a` |
| `dt.hour`, `dt.day_of_week` | `gio`/`ngay_trong_tuan` với `"luc": "dong"` = giờ ĐÓNG bar i (= giờ mở bar i+1; đóng vào T7/CN → 00:00 Thứ Hai) | giờ MỞ bar i |
| khung phiên `CopyHigh(starttime,endtime)` | `cao_trong_gio` `"luc": "dong"`: có giá trị khi giờ đóng bar i > `gio_den` (bar `gio_den` vừa đóng là đủ) | cần giờ mở bar i > `gio_den` (trễ 1 bar) |
| pivot giờ (MultiPivots `PivotsHour`) | `(high+low+close)/3` của bar i | của bar i−1 |
Không nhìn trước: mọi thứ chỉ dùng bar ≤ i (test `kiem_khong_nhin_truoc` cho MỌI cơ chế mẫu).
Pine KHÔNG đổi (script Pine chạy ở đóng bar, `x[1]` = 1 bar trước là đúng).
`ngu_phap.py`: thêm `_luc_dong(df)` + tuỳ chọn `"luc": "dong"` cho `gio`,
`ngay_trong_tuan`, `cao_trong_gio`/`thap_trong_gio` (mặc định giữ nghĩa cũ).
Sửa kèm: biến bí danh cột giá trần (`double c1 = iClose(..,1)` → `c1 = close`) trước
đây rơi vì `_tuyen_tinh` từ chối định danh trần; `_ho_gia_thuan` chấp nhận mốc CÙNG
bar nếu là tổ hợp nhiều cột (giá tick đầu so với pivot của bar vừa đóng).

### Số đo
| | ff1f94a8 | bây giờ |
|---|---|---|
| Điểm vào dịch được (`do_moc.py`) | 8/22 = 36.4% | **8/22 = 36.4%** (cùng cơ chế, căn bar đúng) |
| Cơ chế / qua `kiem_khai_bao` | 14 / 14 | 14 / 14 |
| `test_doc_ma*.py` + `test_toan_hang_tuyen_tinh.py` | 83 xanh | **90 xanh** (7 test mới: ánh xạ k→k−1, khớp EA từng bar, CopyHigh số, giờ lúc đóng + cuối tuần, khung phiên, không nhìn trước toàn bộ mẫu) |
| 38 file test chạm `doc_ma`/`ngu_phap`/`vong_thu_nghiem` | 20 đỏ | 20 đỏ, **0 đỏ mới** (cùng tập lỗi môi trường; `test_sua_bang_llm` đỏ khi chạy chung là phụ thuộc thứ tự, chạy riêng xanh ở cả hai bản) |

### Vòng lặp EURUSD H1 thật (`/workspace/eurusd_h1_server.csv`, 17.127 bar)
14 bóc được, 6 trùng, 8 chạy được → **giữ lại: 0** (ngưỡng t ≥ 2.0 tối ưu / 1.5 kiểm).
| cơ chế | kiểm gốc | kiểm sau tối ưu | t (tối ưu/kiểm) |
|---|---|---|---|
| Breakout1 mua | +1.06 / 103 | +2.54 / 94 | **+1.5 / +2.3** (gần nhất, rớt vì t tối ưu < 2.0) |
| Breakout1 bán | −0.69 / 140 | −0.34 / 159 | +0.4 / −0.3 |
| Breakout2-2 mua | −1.18 / 97 | −1.18 / 97 | +0.6 / −1.1 |
| Breakout2-2 bán | −0.54 / 121 | −0.17 / 122 | +1.0 / −0.2 |
| Breakout5-2-2 mua | −0.07 / 1310 | −0.78 / 5 | +0.5 / −0.7 |
| Breakout5-2-2 bán | +1.06 / 1310 | +1.59 / 375 | +0.0 / +1.4 |
| Template mua (c1>c2) | −1.29 / 1287 | −1.30 / 115 | +0.6 / −1.2 |
| Template bán | −0.23 / 1314 | +1.15 / 158 | −0.3 / +1.1 |
Placebo (dữ liệu ngẫu nhiên, seed 1-5, 8 cơ chế/seed): giữ 1/40 (~2.5%), đúng mức kỳ vọng.

### Vấn đề mở (ưu tiên vòng sau)
1. **EA kiểm lại mỗi tick** (Breakout1: `prevTime` chỉ cập nhật SAU khi vào lệnh, nhánh
   không phá vỡ `return` trước đó; Breakout2/2-2/3 bỏ hẳn cổng bar mới) → thực chất là
   lệnh dừng TRONG bar. Dịch theo tick đầu bar là xấp xỉ; cần tự phát hiện + gắn
   `gia_dinh`, hoặc thêm toán hạng "phá vỡ trong bar" vào DSL (vào tại mức giá).
2. Tối ưu chọn tham số cho 5 lệnh trên phần kiểm (Breakout5-2-2 mua, `giu=8`):
   `lenh_min` chỉ áp lên phần tối ưu — cân nhắc áp cả phần kiểm khi báo cáo.
3. `PivotsDay` (R1/S1/P ngày) qua `moc_ky`; `±5*_Point` cần giả định symbol.
4. Bắt `SellLimit`/`BuyLimit` làm điểm vào (lệnh chờ tại mức giá).
5. Chạy `doc_chien_luoc` trên kho .mq5 lớn để đo tỷ lệ thật ngoài 10 file mẫu.

---

## Vòng 10/10 tối — SỐ ĐO THẬT (`python mau_thu/do_moc.py`)
| | 908075c0 (chiều) | bây giờ |
|---|---|---|
| **Điểm vào dịch được (số chính)** | 6/22 = 27.3% | **8/22 = 36.4%** |
| Cơ chế rút ra | 10 | 14 |
| Qua `kiem_khai_bao` | 8/10 (2 họ `khac`) | **14/14** |
| Tín hiệu thanh nến (bỏ hedge/lưới + mã chết khỏi mẫu số) | không đo | 8/10 = 80% |
| `test_doc_ma.py` + `test_doc_ma_mql5.py` + `test_toan_hang_tuyen_tinh.py` | 72 xanh | **83 xanh** (11 test mới) |
| Bộ test chạm `doc_ma`/`ngu_phap`/`vong_thu_nghiem` (38 file) | 30 đỏ trước đó | 20 đỏ, **0 đỏ mới** (đỏ còn lại do môi trường: thiếu scipy, nao.db...) |

### Phân loại 22 điểm vào (`phan_loai_vao_lenh` trong `doc_chien_luoc`)
- `dich_duoc` 8 — Breakout1, 2, 2-2, 3, 5, 5-2-2 (lệnh đầu), Template mua+bán.
- `quan_ly_vi_the` 10 — hedge/lưới/nhồi lệnh theo `Tradesinfo.*`, `postotal`,
  `profits`: phụ thuộc GIÁ VÀO LỆNH / số lệnh đang mở, không phải tín hiệu bar.
- `ma_chet` 2 — Pivots1 và CurrencyStrength1: khối breakout + PositionOpen nằm
  SAU `return;` vô điều kiện (tác giả đặt SellLimit tại R1 rồi return). Bản cũ
  đếm chúng như tín hiệu chưa dịch; dịch chúng ra là gán cho tác giả chiến lược
  họ KHÔNG chạy.
- `chua_dich` 2 — Breakout4 (`PivotsIsPivotRange` R1/S1 ngày ±5·`_Point`, phụ thuộc
  symbol) và CurrencyStrength1 (`iCustom` CSValues, không có mã).
- Số chính VẪN là 8/22 (mẫu số đủ 22). Dòng "tín hiệu thanh nến" chỉ để biết còn
  bao nhiêu tín hiệu thật chưa dịch. Lưu ý: `_VAO_LENH` không bắt `SellLimit`/
  `BuyLimit`, nên 2 lệnh chờ ĐANG CHẠY thật (SellLimit R1 ở Pivots1/CurrencyStrength1)
  không nằm trong 22 — nếu thêm thì mẫu số thành 24.

### Đã làm (nhan/doc_ma.py)
1. **Pivot giờ theo mã thật của `MultiPivots.mqh`** (lấy từ
   github.com/peterthomet/MetaTrader-5-and-4-Tools/Include/MultiPivots.mqh):
   `PivotsIsAbovePivot(x, pd.PivotsHour, "P")` = `x >= P`, P = (H+L+C)/3 của thanh
   H1 đã đóng ngay trước (TRADITIONAL/CLASSIC/FIBONACCI cùng P). Chỉ dịch khi file
   bật `Settings.PivotTypeHour` loại đó VÀ có gọi `.Calculate(` (không thì struct = 0).
   Cơ chế mang `gia_dinh` ("đúng khi chạy trên dữ liệu H1"). PivotsDay/R1/S1 chưa dịch.
2. **Gập `if` chỉ phụ thuộc cấu hình** (`_gap_hang_cau_hinh`): `if(ReverseEntry)` với
   `input bool ReverseEntry=false`, `if(startmanual!=0){...}` trong
   `checkForOpen(int startmanual=0)` (chỉ gọi có đối số từ `OnChartEvent` = bấm phím
   tay). Trước đó bảng bool lấy phép gán CUỐI theo văn bản = `upbreakout=true` trong
   nhánh không bao giờ chạy → sai. Chỉ `input` (không `extern`); tham số bị gán lại
   trong thân hàm thì không coi là hằng. Test: đổi `ReverseEntry=true` → chiều đảo.
3. **Họ cho cơ chế chỉ so giá với mốc giá cũ hơn** (`_ho_gia_thuan`) — tự quyết theo
   quyền được giao: mua khi giá mới TRÊN mốc cũ (bán khi dưới) = `xu_huong`
   (động lượng); mua khi DƯỚI (bán khi trên) = `quay_ve_trung_binh`. Template
   `close[1] > close[2]` → `xu_huong`; Breakout5 (mua dưới pivot) → `quay_ve_trung_binh`.
   Chỉ gán khi MỌI điều kiện đều là giá thô bên trái, mốc cũ hơn bên phải, cùng hướng.
4. **Bỏ điều kiện trùng/bị kéo theo** (`_bo_trung_dieu_kien`): nhánh bán Template từ
   `c1<c2 và c1<=c2 và c1<=c2` → `c1<c2` (cùng tập bar).
5. **Mã chết** (`_ma_chet`) và **phân loại điểm vào** (`_phu_thuoc_vi_the`).
6. `tuyen_tinh` lồng `(a+b+c)/3` được làm phẳng (chỉ chế độ MQL5; Pine giữ dạng lồng
   để `mult` của Bollinger vẫn là tham số riêng).

### Vòng lặp trên dữ liệu H1 THẬT
Repo không có CSV giá. Đã tải EURUSD H1 từ Yahoo (yfinance, 2023-12-26 → 2026-10-09,
17.127 bar sau khi bỏ bar phẳng), đổi sang giờ server ước lượng `Europe/Helsinki`
(UTC+2/+3 — bộ lọc giờ của EA viết theo giờ server). File để ngoài repo:
`/workspace/eurusd_h1_server.csv`; kết quả `/workspace/vong_eurusd.json`.

    python vong_thu_nghiem.py --csv /workspace/eurusd_h1_server.csv

Kết quả: 14 bóc được, 6 trùng, 8 chạy được → **giữ lại: 0**.
| cơ chế | kiểm gốc | kiểm sau tối ưu | t (tối ưu/kiểm) |
|---|---|---|---|
| Breakout1 mua | sh −0.58 / 145 lệnh | +1.26 / 106 | +1.5 / +1.1 |
| Breakout1 bán | +0.02 / 164 | −0.02 / 138 | +0.4 / −0.0 |
| Breakout2-2 mua | +1.50 / 98 | +0.28 / 101 | +1.4 / +0.2 |
| Breakout2-2 bán | −0.18 / 120 | +0.31 / 116 | +1.1 / +0.3 |
| Breakout5-2-2 mua (dưới pivot) | −0.05 / 1090 | −0.05 / 1090 | +1.4 / −0.1 |
| Breakout5-2-2 bán (trên pivot) | +1.05 / 1090 | +1.05 / 1090 | +0.7 / +0.9 |
| Template mua (c1>c2) | −2.39 / 1287 | −2.39 / 1287 | +0.6 / −2.2 |
| Template bán (c1<c2) | −0.52 / 1313 | −0.11 / 685 | +0.1 / −0.1 |
Không cơ chế nào qua ngưỡng t ≥ 2.0 / 1.5. Đó là kết quả trung thực: các EA mẫu
này là bộ khung hedge/lưới, phần tín hiệu vào lệnh đơn thuần không có edge sau phí.

### Vấn đề mở (ưu tiên vòng sau)
1. ~~**Lệch một bar trong quy ước chỉ số MQL5.**~~ (ĐÃ SỬA ở vòng 10/10 khuya, xem trên) EA chạy ở tick ĐẦU của bar mới (cổng
   `curTime!=prevTime`, `dt.min==0`), nên `current[0].close` ≈ close bar vừa đóng,
   còn chỉ số MQL5 k≥1 ứng với trễ k−1 trong DSL (quyết định lúc đóng bar). Quy ước
   hiện tại ánh xạ thẳng k → trễ k (cũng áp cho pivot giờ để nhất quán). Không nhìn
   trước (mốc cũ hơn 1 bar) nhưng không khớp tuyệt đối với EA — cần quyết định
   rồi sửa đồng loạt + test.
2. `PivotsDay` (R1/S1/P ngày) qua `moc_ky`; `±5*_Point` cần giả định symbol.
3. Bắt `SellLimit`/`BuyLimit` làm điểm vào (lệnh chờ tại mức giá).
4. Chạy `doc_chien_luoc` trên kho .mq5 lớn để đo tỷ lệ thật ngoài 10 file mẫu.

---

## Vòng 10/10 chiều (908075c0)

## Trạng thái hiện tại — SỐ ĐO THẬT (`python mau_thu/do_moc.py`)
| | trước (c5d5fcd9) | bây giờ |
|---|---|---|
| Cơ chế rút ra / 22 điểm vào | 10 (45.5%) — **phần lớn sai nghĩa** | **10 (45.5%) — đúng nghĩa** |
| Điểm vào dịch được thật | không đo | **6/22 = 27.3%** |
| `test_doc_ma.py` | **19/36 đỏ** | **36/36 xanh** |
| Qua `kiem_khai_bao` + không nhìn trước | — | 8/10 (2 cái họ `khac`) |

### Vì sao con số 45.5% cũ phải bỏ
Các commit 8cfa3f8b → 700d395a đạt 13.6% → 45.5% bằng cách làm SAI nghĩa và
làm đỏ 18-19 test của `test_doc_ma.py` (trước đó 36/36 xanh):
- Coi mọi định danh lạ là `close` → `Tradesinfo.hedgeprice` thành `close`, ra cơ
  chế `close >= close` (luôn đúng → `phoi_nhiem=0.996`, tức mua-giữ).
- Tách `or` như thể là `and`.
- Giữ cơ chế khi một vế không dịch được — trái nguyên tắc đã ghi trong
  `doc_chien_luoc` ("bỏ một vế làm điều kiện LỎNG hơn bản gốc ... là nói dối").

Đã khôi phục `doc_ma.py` về bản c2fe17a0 (36/36 xanh) rồi làm lại đúng cách.

## Việc đã làm (lớp đọc MQL5 trong `nhan/doc_ma.py`)
- `&&`/`||` → `and`/`or`; `iClose(_Symbol,_Period,k)` → `close[k]`.
- Mảng dữ liệu: `current[0].close` sau `CopyRates(...,0,1,current)`, `MaValues[0]`
  sau `CopyBuffer(MaHandle,0,0,10,MaValues)` — mảng KHÔNG đảo chiều thì phần tử 0
  là bar CŨ NHẤT (ra `sma(50) trễ 9`, đúng như code tác giả chạy).
- `(_Point*margin)` với `margin = BOMargin = 0` → 0.
- Biên phiên: `highs[ArrayMaximum(highs)]` sau `CopyHigh` theo khung giờ dựng từ
  `dt.hour=H` + `StructToTime` → toán hạng DSL mới `cao_trong_gio`/`thap_trong_gio`
  (thêm vào `nhan/ngu_phap.py`, chỉ có giá trị khi giờ > `gio_den` → không nhìn trước).
  `CopyHigh(...,1,3,highs)` (số) → `cao_nhat(high,3) trễ 1`.
- Vế so sánh là biểu thức số học (`close < lowrange+((highrange-lowrange)/2)`).
- Guard tìm theo KHỐI `{}` bao lệnh vào (bản cũ vớ `if(downbreakout){..}` đã đóng).
- `if(up||down){ if(up){type=BUY} if(down){type=SELL} ... PositionOpen(type) }`
  → tách đúng 2 cơ chế mua/bán.
- Bộ lọc thoát sớm `if(dt.hour<9||dt.hour>17) return;` → `gio>=9 và gio<=17`;
  `if(up && close<MA) return;` → nhánh mua thêm `close >= MA`.
- Hàm tín hiệu: `OpenTrade(sig>0 ? BUY : SELL)` + `sig=GetSignal()` +
  `if(c1>c2) return 1;` → điều kiện của từng chiều.
- Điều kiện QUẢN TRỊ (Copy* lỗi, 1 lệnh/ngày, đã có vị thế, giá trị <= 0) được bỏ
  qua nhưng ghi rõ ở `bo_qua_quan_tri`. Lệnh hedge/lưới theo `Tradesinfo.*`
  (giá vào lệnh) và hàm include không có mã (`PivotsIs*`, `iCustom`) KHÔNG dịch.
- Test mới: `test_doc_ma_mql5.py` (8 test: nghĩa, chiều, bộ lọc, không nhìn trước,
  vòng thử nghiệm).

## Trần của bộ mẫu `mau_thu/` (vì sao chưa đạt ≥40% theo điểm vào)
22 điểm vào = 6 dịch được + 10 lệnh hedge/lưới phụ thuộc giá vào lệnh (không
phải tín hiệu bar) + 5 phụ thuộc `MultiPivots.mqh`/`iCustom` không có trong repo
+ 1 nhánh `else` thủ công. Muốn vượt 27.3% theo điểm vào cần mã của
`MultiPivots.mqh` hoặc bộ mẫu rộng hơn — không thể "dịch" đúng thứ không có mã.

## Vòng lặp `vong_thu_nghiem.py`
- Dữ liệu H1 giả lập (hoặc `--csv` dữ liệu thật), chia thời gian 70% tối ưu / 30% kiểm.
- Tối ưu thật: dò từng toạ độ trên `ngu_phap.tham_so_cua` (chu kỳ, ngưỡng, giữ), 2 lượt.
- Dùng đúng `chieu` (bản cũ bỏ qua → lệnh bán chạy như mua).
- Giữ lại khi t = Sharpe×√năm ≥ 2.0 (tối ưu) và ≥ 1.5 (kiểm), đủ ≥20 lệnh, qua kiểm cú pháp.
- Bỏ trùng vân tay (Breakout2/2-2/3 cùng điều kiện).
- Placebo trên dữ liệu ngẫu nhiên: ngưỡng cũ "Sharpe kiểm > 0" giữ 3-5/6 mỗi seed;
  ngưỡng mới giữ 3 lần trên 20 seed × 4 cơ chế đủ điều kiện (~4%).

## Ưu tiên tiếp
1. Chạy vòng lặp trên dữ liệu H1 thật (EURUSD...) bằng `--csv`.
2. ~~Họ cho cơ chế `close[1] > close[2]`~~ — đã gán `xu_huong` ở vòng 10/10 tối.
3. Nếu có `MultiPivots.mqh`: dịch pivot ngày bằng `moc_ky` (cao/thấp/đóng trước).
4. Chạy `doc_chien_luoc` trên kho .mq5 lớn để đo tỷ lệ thật ngoài 10 file mẫu.
