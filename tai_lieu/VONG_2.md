# VÒNG 2 — kiểm tra chặt, tối ưu tham số, ghép cùng cặp, danh mục

Ngày: 20/10/2026 (giờ Việt Nam/Bangkok, UTC+7). Mã: `nhan/vong2.py`, test: `test_vong2.py`. Kết quả: `reports/vong2/`.

**Nguyên tắc nhãn.** Số lấy từ báo cáo/lệnh MT5 real tick = **ĐO THẬT**. Equity theo giờ dựng lại từ lệnh MT5 + giá H1 của chính lần chạy MT5 = **TÁI DỰNG** (đo thật, đã đối chiếu với DD trong báo cáo). Stress phí, Monte Carlo, mọi số Python = **MÔ PHỎNG**. Vòng 2 **không gọi ai-box / LLM nào**: chỉ dùng thẻ đã dịch trong `data/ong_dan/trang_thai.sqlite`, EA trong `data/`, kết quả MT5 vòng 1.

## 0. Đầu vào

- Danh sách hệ: bảng “Tất cả” trong `reports/UNG_VIEN.md`, kết luận **ĐẠT** (XM micro, ~12/2023–10/2026, DD vốn ≤ 80 %, ≥ 10 %/năm kép sau phí).
- Lệnh MT5 thật: `reports/ong_dan/ket_qua_mt5/<id>_vao.csv_lenh_mt5.csv`, giá kèm theo: `<id>_vao.csv_gia.csv`.
- Thẻ Python: chỉ hệ có `tin_hieu` + phép thử tốt nhất trong cache box mới chạy được phần Python. Hệ dịch bằng LLM trên máy nhà (thẻ trên box thiếu tín hiệu) ghi **CHƯA ĐO ĐƯỢC trên box**.

## 1. Kiểm tra chặt hơn

### 1.1 Equity đúng nghĩa (sửa caveat “chỉ lệnh đóng”)
Mỗi position: hệ số `k = lãi giá / (giá ra − giá vào)` (USD trên một đơn vị giá — đã gồm cỡ hợp đồng và quy đổi tiền). Equity mỗi nến H1 = vốn + lãi đã đóng + Σ k·(giá − giá vào) của lệnh đang mở; bản “xấu” dùng giá bất lợi trong nến (low cho mua, high cho bán). Lệnh còn mở cuối kỳ (EA không ghi deal `out`) được đóng ở giá cuối; phần lệch còn lại so với lãi ròng báo cáo (thường là swap của lệnh mở) cộng vào nến cuối (`lech_net_khop_cuoi_ky`). Đối chiếu: DD equity tái dựng của 33 hệ nằm sát DD trong báo cáo (vd GBPCAD H1 #1: 43,6 % so với 45,8 %).

### 1.2 Walk-forward / ngoài mẫu
- MT5: chia kỳ thành **3 đoạn bằng nhau theo thời gian**, đo lãi kép %/năm và DD từng đoạn.
- Python: 30 % cuối dữ liệu là OOS (nhãn từ `danh_gia`), điểm lưới chỉ được chọn khi OOS > 0.

### 1.3 Lịch sử dài hơn
Dữ liệu trên box: AUDCAD từ 2008, NZDUSD và EURUSD (bản cũ) từ 2018, còn lại HistData 2024-01 → 2026-10. Python tự dùng hết dữ liệu từ `tu_ngay` = 2016-01-01. Việc MT5 vòng 2 đặt `FromDate` = max(2016.01.01, lệnh CSV đầu − 7 ngày), nên kỳ MT5 dài hơn chỉ có ở cặp có giá dài trên box. Muốn 2004/2015–2026 cho mọi cặp cần nạp thêm giá H1/M5 (Dukascopy) — **chưa làm** đêm nay.

### 1.4 Đa cặp
Cùng tín hiệu + quản lí, chạy Python trên mọi cặp có dữ liệu (27 mã). Chỉ số: tỉ lệ cặp khác **không lỗ và không stop-out**.

### 1.5 Monte Carlo
- Xáo thứ tự lãi/lỗ lệnh đóng (1.000 lần) + bootstrap có hoàn lại: ghi lại, nhưng với hệ DCA/không SL DD lệnh đóng ≈ 0 nên **không dùng làm cổng**.
- **Cổng:** block bootstrap 10 ngày trên **lợi suất equity ngày** (sau stress phí), giữ cả mức sụt thấp nhất trong ngày → phân phối DD equity, lấy p95. MÔ PHỎNG.

### 1.6 Stress phí
Mỗi lệnh: + 50 % spread lúc mở (spread x1,5; dòng spread hỏng trong `_gia.csv` thay bằng trung vị) + hoa hồng 7 USD / 100.000 USD danh nghĩa khứ hồi. Đo lại lãi kép và DD equity.

### 1.7 Python ↔ MT5
Lấy cột Py/MT5 của `UNG_VIEN.md`.

### 1.8 Ngưỡng tầng (thiếu số đo = chưa đạt)

| Tiêu chí | TẦNG A (vàng) | TẦNG B (bạc) |
|---|---|---|
| Lịch sử MT5 | ≥ 2,5 năm | ≥ 2,0 năm |
| Lãi kép sau stress phí | ≥ 15 %/năm | ≥ 10 %/năm |
| DD equity tái dựng sau stress | ≤ 60 % | ≤ 80 % |
| MC DD equity p95 (block 10 ngày) | ≤ 80 % | ≤ 95 % |
| Đoạn walk-forward tệ nhất (3 đoạn) | ≥ 5 %/năm | ≥ 0 %/năm |
| Số lệnh (position) | ≥ 100 | ≥ 30 |
| Python/MT5 | 0,8–1,25 | 0,7–1,4 |
| Đa cặp: tỉ lệ cặp khác không lỗ | ≥ 50 % | ≥ 30 % |
| OOS Python (30 % cuối) | ≥ 10 %/năm | ≥ 0 %/năm |
| Cao nguyên tham số gốc | ≥ 0,6 | ≥ 0,4 |
| Stop-out | 0 | 0 |

Không đạt B → **TẦNG C** (giữ theo dõi, không đưa tiền thật).

## 2. Tối ưu tham số (chống quá khớp)
1. **Mặc định tác giả**: lệnh vào giữ input gốc (thẻ `tham = {}` / hệ số chu kỳ 1,0) — luôn báo cáo song song.
2. **Khung**: H1 ↔ H4.
3. **Cặp**: như 1.4.
4. **Lưới thô** (ngân sách 90 phép thử/hệ): `tp_pct` {0,1–0,5 %}, `dca_buoc_pct` {0,2–1,2 %}, `dca_toi_da` {0,3,5,7}, `dca_he_so_lot` {1,0–2,0}; spec DSL thêm **hệ số chu kỳ chỉ báo** {0,5; 0,75; 1; 1,25; 1,5} nhân mọi `n` (trừ độ trễ, lịch). Lot **không** tối ưu (chỉ là đòn bẩy). Pha 1: hàng xóm ±1 của gốc + điểm ngẫu nhiên; pha 2: đo đủ hàng xóm của các điểm tốt nhất.
5. **Điểm** = lãi/năm ÷ max(DD, 10) (lãi < 10 %/năm → âm; stop-out/DD > 80 % → loại). **Cao nguyên** = tỉ lệ hàng xóm ±1 giữ ≥ 70 % điểm. Chọn: ≥ 2 hàng xóm đo được, cao nguyên ≥ 0,6, OOS > 0; xếp theo điểm × cao nguyên.
6. Điểm tốt nhất → việc MT5 (`V2_CAO_NGUYEN`); 2 cặp khác tốt nhất có OOS > 0 → `V2_DA_CAP`; khung khác có điểm dương → `V2_KHUNG`. Trình tối ưu di truyền MT5: **chưa bật** (tuỳ chọn; việc CSV lệnh vào không tối ưu được input chỉ báo trong MT5).

## 3. Ghép cùng cặp (B khác phong cách, chọn từ sổ cơ chế)
B lấy từ `reports/kho_co_che/so_co_che.jsonl`: chạy được Python, phong cách vào khác A, ưu tiên DAT_MT5 > DAT_PY > GAN_DAT, cùng cặp được ưu tiên; tối đa 3 B/hệ. Ba kiểu (thêm vào `nhan/ong_dan.py`):
- `xac_nhan`: lệnh A chỉ giữ khi B cùng chiều trong ≤ 3 nến (bộ lọc `xac_nhan`).
- `them_lenh`: A + B vào cùng tài khoản, gỡ chéo (`nguon_b`).
- `nguoc` (hedge): B chỉ vào **ngược** chiều A đang giữ (`kieu_b = "nguoc"`).
Ghép được đưa vào hàng chờ MT5 khi điểm > hệ gốc và OOS > 0. Lưu ý: EA BRAIN_XuLiLenh gộp một rổ mỗi chiều (nhãn `gan_dung` của `viec_csv`).

## 4. Danh mục
Lãi/lỗ ngày từ equity tái dựng (lệnh MT5 thật). Tham lam theo lãi/DD: thêm hệ nếu tương quan ngày với mọi hệ trong danh mục ≤ 0,3 và điểm danh mục tăng; tối đa 4 hệ, vốn 1.000 USD/hệ. **DD tính trên equity cộng theo giờ (gồm lệnh đang mở, giá bất lợi trong nến)** — thay cho DD lệnh đóng của `ghep_cheo.do_danh_muc`.

## 5. Hàng chờ MT5 vòng 2 và cách bật trên máy nhà
- Tệp: `reports/vong2/hang_cho_vong2.jsonl`; CSV lệnh vào + `.set` + `.ini`: `reports/vong2/viec/<thẻ>/`. Tên việc `od_v2<loại>_...` (không trùng sổ cái vòng 1), chỉ sàn XM micro.
- `mt5tools/sinh_viec.py::tu_vong2` — **mặc định TẮT**. Việc vẫn qua lọc hai tầng (OHLC M1 → real tick) như việc ống dẫn.
- Bật (phiên sau, sau khi `git pull`), trong cửa sổ chạy `chay_lien_tuc.py`:
  ```
  set BRAIN_VONG2=1
  set BRAIN_VONG2_UU_TIEN=1   (tuỳ chọn: chạy vòng 2 trước việc thường)
  python mt5tools\chay_lien_tuc.py --den 06:30
  ```
  Kết quả về `reports/ong_dan/ket_qua_mt5/od_v2*`; chạy lại `python -m nhan.vong2` để xếp tầng.

## 6. Giới hạn đã biết
- Equity tái dựng dùng giá H1 (bid) của lần chạy: sụt trong nến được tính bằng high/low nhưng không theo tick.
- Hoa hồng thật XM micro vẫn **CHƯA ĐO ĐƯỢC**; 7 USD/100k là giả định stress.
- Box thiếu thẻ đã dịch của nhiều hệ (dịch LLM trên máy nhà) → phần Python của các hệ đó chưa đo.

## 7. Vòng 2 cho 8 hệ ĐẠT vòng 1 MT5 (03/11/2026, Grok Bot)

Bối cảnh: 8 hệ trong `TRI_NHO/TRANG_THAI.md` ĐẠT ở bước nâng lot, nhưng CSV lệnh vào chỉ phủ ~12/2023–10/2026 (trừ mql5344 từ 12/2017) → **in-sample**. Ý chủ dự án: không đòi một bộ thông số cố định thắng mọi giai đoạn; quản lý lệnh (lot, bước DCA, thoát) phải **thích nghi** theo giai đoạn.

### 7.1 Đã sinh (hàng đợi git, máy nhà tự lấy)
38 việc `hang_doi/can_test/v2qd_<biến thể>_<hệ>.json`, `uu_tien` 90 (trên việc lot 80), cùng CSV vào + `BRAIN_XuLiLenh`, k = {1, k_tot}:
| Biến thể | Đổi | Mục đích |
|---|---|---|
| `atrb1` | bước DCA 1×ATR14, TP 0,5×ATR14 (tắt %) | thích nghi biến động (PMG `vol_adaptive`) |
| `atrb2` | bước 2×ATR14, TP 1×ATR14 | giãn khi biến động lớn |
| `gian13` | `InpGianBuoc` 1,3 (chỉ 6 hệ có DCA) | PMG `expanding` |
| `trailatr` | bỏ TP, trailing kích 1×ATR trả 0,5×ATR | thoát theo xu hướng |
| `catlo40` | cắt rổ khi lỗ ≥ 40 % số dư | phanh giai đoạn xấu |
Vẫn IN-SAMPLE; chỉ để xem quản lý nào giữ lãi đều hơn qua 2024/2025/2026 (`lai_theo_nam` trong kết quả), so với gốc `lot_<hệ>`.

### 7.2 Thiếu — cần làm trước khi coi là qua vòng 2 (ngưỡng §1.8)
1. **Ngoài mẫu trước 2024**: CSV vào do Python xuất trên giá 2024–2026. Phải xuất lại CSV từ thẻ Python trên giá dài. Box có HistData M1 2008–2023 chỉ cho AUDNZD, EURCHF, EURGBP, NZDCAD, XAUUSD (`/workspace/du_lieu_fx/hd_dai/`); **chưa có GBPNZD, GBPCAD, USDCAD, NZDUSD dài**. Lấy: HistData `DAT_ASCII_<CẶP>_M1_<năm>.zip` (như `hd_dai/tai.py`) hoặc Dukascopy; hoặc máy nhà xuất M1/H1 XM bằng `mt5tools/tai_lich_su_mt5.py`. Lịch sử XM đã ghi: AUD/NZD `#` không có M1 trước 2018-05; GBPUSD 2004–2015 chạy được nhưng "0 % real ticks"; mql5344 2017–2026 chỉ ~31 % real ticks → trước ~2023 tester XM dùng tick sinh từ M1, ghi rõ chất lượng mô hình.
   Hai hệ `mql5*` là lịch sử tín hiệu công khai → không có ngoài mẫu trước ngày tín hiệu tồn tại; chỉ có forward.
2. **Walk-forward 3 đoạn / Monte Carlo / stress phí ×1,5 / equity tái dựng**: có code (`nhan/vong2.py`) nhưng cần `<id>_vao.csv_lenh_mt5.csv` + `_gia.csv` của lần chạy lot từ máy nhà về repo.
3. **Đa cặp**: CSV vào gắn với một cặp → không chạy được trên cặp khác; cần thẻ Python tái sinh tín hiệu (`nhan/vong2.py` §1.4).
4. **Ghép**: GBPCAD có 3 hệ (ghep60ff H1, ghep0bf2 H4, skea154 H4), GBPNZD có 2 (ghepe9b41 H4, 2600ea H1) → ghép danh mục §4 bằng equity tái dựng (cần mục 2); EA gộp một rổ mỗi chiều nên ghép trong một EA chỉ `gan_dung`.
5. **Lọc chế độ ADX / regime / tin**: `BRAIN_XuLiLenh` **chưa có** input ADX, lọc chế độ hay lịch tin; chỉ có ATR (bước/TP/trailing), giờ cấm, spread tối đa. Cần thêm input (vd `InpAdxMax`, `InpAtrPctMin/Max`, file lịch tin CSV) và biên dịch trên máy nhà.
