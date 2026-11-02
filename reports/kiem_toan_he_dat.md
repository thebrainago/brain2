# Kiểm toán nghiêm 5 hệ đang báo ĐẠT — 2026-11-01 (Asia/Bangkok)

Người kiểm: Grok Bot (box only; máy Windows nhà OFF).  
Thư mục: `/workspace/brain2`, `/workspace/may_nha_toi_nay`.  
Chuẩn pass người dùng: lãi sau phí, DD ≤ 80%, ≥ 10%/năm. **Không** dùng FDR/placebo/Holm làm cổng.  
Quy tắc mới: chỉ phát lại CSV statement/tín hiệu trader → **không** đạt (nhãn *CHƯA GIẢI MÃ ĐIỂM VÀO*); kết quả chỉ in-sample trên CSV nguồn → **không** đạt.  
Bối cảnh: skst299b đã lộ MACD Sample + overlay; lỗi lot CSV ~100× vá **2026-10-31 01:53** Asia/Bangkok (`status_overnight_0217.txt`).

**Cách tính %/năm trong báo cáo này:** lãi kép (CAGR) = `(1 + net/von)^(1/năm) − 1`. Số “simple” = `(net/von)/năm` chỉ để đối chiếu (salvage brainxlmrz dùng simple = 26.34%). `CHIEN_LUOC_DA_LOC.md` ghi “%/năm = lãi kép”.

---

## Bảng tóm tắt

| Hệ | Nguồn điểm vào | OOS thật? | %/năm trung thực (CAGR) | DD | Verdict | Lý do ngắn |
|---|---|---|---|---|---|---|
| brainxlmrz GBPUSD H4 | **Rule EA native** VAO_MRZ (`InpVao=1`, Z=2, N=100) — không CSV | **Không** (OOS stub/0 lệnh; salvage orphan) | **13.3%** kép (simple 26.3% — số báo PASS) | **78.81%** (sát trần 80%) | **HẠ XUỐNG ỨNG VIÊN / CẦN CHẠY LẠI** | DD sát 80%; 25% real ticks; salvage sau `qua_gio`; %/năm PASS dùng simple không phải kép; chưa OOS sạch |
| skea61c CADJPY H4 lot×4 | **Rule đã giải mã** SMA(10)×SMA(20) → CSV Python (`InpVao=4`) | **Yếu** — CSV chỉ 2024.01–2026.10 = đúng cửa sổ test; OOS “trước” không có tín hiệu | **13.3%** kép (×4, 2024.01.10–2026.10.01) | 10.74% | **HẠ XUỐNG ỨNG VIÊN** | Rule OK + lot×4 **sau** vá 01:53; nhưng cửa sổ = span CSV (IS); trước vá b120/dai19 phình ~100× |
| sk_ea_3279057100 EURGBP H1 | **CSV tín hiệu** — công thức **CHƯA RÕ** (mt5_truc_tiep; `CHIEN_LUOC` + kho trống) | **Không** — OOS trước 2024 = 0 lệnh (CSV không cover) | 12.2% kép trên IS b50 | 14.8% | **CHƯA GIẢI MÃ ĐIỂM VÀO** | Giống rủi ro skst299b; WF có đoạn −11%/năm; 1 đoạn gánh 77% lãi |
| mql5344 NZDUSD H1 | CSV từ rule khai báo EMA20×EMA50 (`InpVao=4`) | OOS 2025–2026 có nhưng **yếu** (+213) | Claimed ~12% **SAI**: CAGR dài hạn **3.5%**; lot×4 cửa sổ ngắn **8.5%** | 5.3% (dài) / 23.4% (×4 ngắn) | **HẠ XUỐNG ỨNG VIÊN** | %/năm báo cáo không trung thực; ×4 < ×1 dài hạn vì **khác kỳ**; 31% ticks; b80 lỗ |
| ghep_0bf2 GBPCAD H4 | Rule **đã giải mã** (nến đóng tăng) + QL sk_st; CSV 1840 dòng | **Không** — OOS trước CSV = 0 lệnh; verify lot01 = cùng span CSV | **10.3%** kép (sát sàn 10%) | 14.9% | **HẠ XUỐNG ỨNG VIÊN** | IS vs CSV (ghi rõ trong status 01:53); trước vá +307k; WF 1 đoạn gánh 61%; MC DD p95 92% |

**Không hệ nào trong 5 hệ giữ verdict GIỮ ĐẠT sau kiểm toán này.**

---

## 1. brainxlmrz — GBPUSD# H4 2016.01–2026.10

### Evidence
- Salvage: `/workspace/may_nha_toi_nay/salvage_gbpusd_brainxlmrz_summary.json` — net **+28 317.3**, PF 5.21, 1002 lệnh, DD **78.81%**, `pct_yr=26.34`, `pass=true`, report gốc `E:\brain2_grok\reports\mt5_lien_tuc\salvage\...` (không có HTM trên box).
- Ledger: `so_cai_from_nha_1845.jsonl` luc **2026-10-31T15:23:00** — `ghi_chu`: salvage orphan g3; trước đó **02:14:30** `loi=qua_gio`, **14:55:15** `khong_bao_cao`.
- `ts`: **`InpVao=1` (VAO_MRZ)**, `InpN=100`, `InpNguongZ=2`, `InpLot0=0.1`, **không** `InpFileCsv`. Enum: `ea_demo/BRAIN_XuLiLenh.mq5` dòng 34: `VAO_MRZ=1`, `VAO_CSV=4`.
- Chất lượng: **25% real ticks**.
- CAGR: von 10k, 10.749 năm → **13.31%** kép; simple 26.34% = đúng công thức salvage (không phải kép).

### Phân tích
- Điểm vào **rule-based trong EA** (mean-reversion Z), **không** phải phát lại statement — khác skst299b.
- Tên job `..._XM_KIEM_XM_CSV` gây hiểu nhầm; thực tế không đọc CSV.
- DD 78.81% gần như chạm trần 80% — một đoạn xấu là fail.
- Tick 25% → số net/DD không đáng tin cho live.
- Chưa có OOS sạch trên box/ledger (các job OOS stub M0/1970).

### Test để đạt lại
1. Chạy lại MT5 **99%+ real ticks** cùng set (InpVao=1, N=100, Z=2, lot 0.1) trên GBPUSD# H4.  
2. Holdout cứng (vd. train ≤2023 / test 2024–2026) **sinh tín hiệu trong EA**, không salvage.  
3. Nếu DD vẫn >~60–70% trên tick tốt → giảm lot / siết MaxTang trước khi xét ≥10%/năm kép.

---

## 2. skea61c (sk_ea_61c21a2049) — CADJPY H4 lot×4

### Evidence
- Rule: `CHIEN_LUOC_DA_LOC.md` A34 — **SMA(10) cắt SMA(20)** hai chiều; nguồn `nkanven/.../MA Crossover.mq5`; kiểu **spec**.
- CSV: `reports/phan_viec/viec_mt5/sk_ea_61c21a2049/od_skea61c21a2049_XM_CSV_vao.csv` — 189 dòng, lot=3.0, **2024.01.10–2026.10.08**.
- Lot×4 sau vá: ledger **2026-10-31T13:56:57** `od_v2lotscale_lotx4_full_...` net **+4039.2**, DD **10.74%**, 199 lệnh, **100% real ticks**, InpLot0=0.12, kỳ 2024.01.10–2026.10.01 → CAGR **13.3%**.
- Trước vá: **01:52:16** b120 **+101 545**; **23:49:01** dai19 **+121 350** (lỗi lot CSV — cùng class bug `status_overnight_0217.txt`).
- Relot/hs sau vá: ×1 khoảng +971…+1465, DD 4–7% — nhất quán hơn, nhưng **</** 10%/năm kép ở lot gốc.

### Phân tích
- Rule **đã giải mã** và có thể tái sinh — không phải statement trader mù.
- Vẫn chạy `InpVao=4` VAO_CSV: MT5 chỉ phát lại thời điểm Python đã ghi. Cửa sổ đo = span CSV → **in-sample theo định nghĩa quy tắc mới**.
- OOS “dai19” trước vá không đáng tin (lot phình); không thấy holdout trước 2024 với CSV tái sinh.

### Test để đạt lại
1. Tái sinh CSV SMA10×20 trên CADJPY H4 cho **toàn bộ** lịch sử có tick (vd. 2019–2026).  
2. Fit/chọn lot chỉ trên ≤2023; đo 2024–2026 (và ngược lại) với lot đã scale đúng (không cột lot micro 3.0 khi symbol `#`).  
3. Giữ 100% real ticks; báo cáo **CAGR** không simple.

---

## 3. sk_ea_3279057100 — EURGBP H1

### Evidence
- `CHIEN_LUOC_DA_LOC.md` A22 + mục “Khoảng trống dữ liệu”: **CHƯA RÕ trong mã**; nằm trong danh sách 19 hệ mất công thức; CSV do Python sinh, không còn trong thẻ/CSDL box.
- Nguồn repo gắn: `GeneralTradingSarl/mql4_experts :: autopendingbyrsi.mq4` — `CAN_EA_GHEP.md` xác nhận VAO_CSV; `tham: {}` trống.
- CSV: 1269 dòng 2024.01.02–2026.10.07 (box + feed nhà).
- PASS claimed: **2026-10-31T16:37:51** b50 **+3730.95**, DD 14.81%, 99% ticks, 2023.12.26–2026.10.01 → CAGR **12.2%**.
- OOS trước: **2026-10-31T00:40:23** `v2r2oos_truoc_...` **0 lệnh** (CSV không cover 2020–2023).
- Vòng 2: WF **147 / −11 / 44**; 1 đoạn gánh **77%** lãi; MC DD p95 **93.7%** (`KET_QUA_VONG2.md`).
- `HE_DANG_GIU.md` 2026-11-01 đã cảnh báo: giống skst299b — cần kiểm nguồn vào trước khi tính đạt.

### Phân tích
- Đúng case quy tắc mới: **entry chưa giải mã**, chỉ replay CSV. Không đạt dù số đẹp.
- Không thể tin OOS khi holdout trước cửa sổ CSV = 0 trade.

### Test để đạt lại
1. Đọc/dịch `autopendingbyrsi.mq4` (RSI pending logic) thành rule Python tái lập được trên OHLC.  
2. Đối chiếu CSV hiện tại với rule (từng timestamp). Nếu không khớp → coi CSV là artifact, bỏ PASS.  
3. Chỉ sau khi khớp: sinh lại tín hiệu OOS + MT5 tick thật.

---

## 4. mql5344 (mql5_344ed0d8ab12c7f0) — NZDUSD H1

### Evidence
- `HE_DANG_GIU.md`: “EMA20×EMA50 theo xu hướng lớn”; set `InpVao=4`, `InpFileCsv=od_mql5344..._vao.csv`.
- CSV feed nhà: 480 dòng **2018.01.02–2026.10.07**, lot 0.03 (đã scale `#`).
- Claimed PASS: **01:53:04** b120 **+3545.27**, DD 5.32%, **31% real ticks**, kỳ **2017.12.26–2026.10.01** (~8.76 năm).
  - CAGR thật: **3.52%** — **không** đạt 10%. Số “~12%/năm” trong HE_DANG_GIU **sai** (gần như chia nhầm cho ~3 năm thay vì ~8.8).
- Cùng lot cửa sổ ngắn: RT 2024–2026 **+610.81** (CAGR ~2.2%); OOS 2025–2026 **+212.53** (~1.2%); lot×4 2024–2026 **+2514.58** (CAGR **8.5%**, DD 23.4%).
- “×4 kiếm ít hơn ×1”: so **×4 ngắn (+2515)** với **×1 dài (+3545)** — **khác kỳ**, không chứng minh bug lot; nhưng cũng **không** cứu được ≥10%/năm kép trên cửa sổ gần.
- Robust: b80 **−307**; hs80 **−58**; 31% ticks lặp lại.

### Phân tích
- Rule khai báo có (EMA cross) nhưng mọi số “đạt” dựa CSV + toán %/năm sai.
- Dài hạn sau phí không đủ 10% kép; OOS gần yếu.

### Test để đạt lại
1. Tái sinh tín hiệu EMA20×EMA50 (đúng định nghĩa “xu hướng lớn”) trên NZDUSD H1, tách IS/OOS.  
2. MT5 **≥90% real ticks**, lot đúng, báo cáo CAGR trên từng cửa sổ.  
3. Chỉ PASS nếu OOS ≥10% kép và DD ≤80%.

---

## 5. ghep_0bf2c31fbfc9dea0 — GBPCAD H4

### Evidence
- Rule: MUA khi **đóng > mở**; ghép vào từ `sk_ea_44640140cc` + QL `sk_st_4a8b8b68d6ee79c0`; TP 0.1%, không SL (`CHIEN_LUOC` A17).
- CSV: 1840 dòng lot=30.0 (micro), 2024.01.02–2026.10.09 — gần như mọi nến tăng; EA lọc còn ~88 lệnh.
- Trước vá **01:27:32** b120 **+307 962** (lot CSV 30); sau vá **02:05:23** lot01 verify **+3079.62**, DD 14.89%, 100% ticks → CAGR **10.27%** (sát sàn).
- Status 01:53 **nói thẳng**: window ≈ full CSV span → **in-sample vs signal CSV**; dai19 OOS trước đó = stub 0 lệnh.
- Tập trung: WF 122/49/31 — **1 đoạn gánh 61% lãi**; MC DD p95 **92.3%** (`CHIEN_LUOC` / `KET_QUA_VONG2`).
- OOS cắt năm: y2025 +1289 (~7.2% CAGR trên 1.75 năm nếu coi độc lập); oos_h1 +679 — không đủ thay thế OOS trước khi sinh CSV.

### Phân tích
- Rule đơn giản **đã giải mã** (không phải statement bí ẩn) nhưng kết quả “đạt” đo trên đúng span CSV → dính quy tắc mới.
- CAGR chỉ ~10.3% — một chút phí/swap/tick xấu là dưới sàn.
- Không SL + TP rất sát → phụ thuộc chế độ thị trường (khớp WF tập trung).

### Test để đạt lại
1. Sinh lại tín hiệu close>open trên GBPCAD H4 **trước 2024** + sau; quản lý giống set.  
2. Chọn tham số chỉ trên IS; đo OOS 2024–2026 (và đảo).  
3. Thêm SL rổ / giảm phụ thuộc 1 đoạn WF; yêu cầu CAGR OOS ≥10% sau phí, tick ≥99%.

---

## Đối chiếu `HE_DANG_GIU.md` / `CHIEN_LUOC_DA_LOC.md`

| Nguồn | Ghi nhận kiểm toán |
|---|---|
| HE_DANG_GIU vẫn liệt kê ghep_0bf2, mql5344, skea61c (lot thấp), 3279057100 là đạt/ứng viên lot | Cập nhật theo bảng trên: **không giữ ĐẠT**; 3279 → chưa giải mã; mql5344 bỏ claim ~12%/năm |
| HE đã hạ skst299b (2026-11-01 00:58) và cảnh báo 3279/CSV | Đúng hướng; kiểm toán này **áp dụng cùng logic** trước khi user hỏi lại |
| CHIEN_LUOC: skea61c ✔ BỀN (micro 29%/năm kép) | Đo micro vốn 1k khác lot×4 vốn 10k; vẫn IS CSV |
| CHIEN_LUOC: 3279 “CHƯA RÕ”; ghep WF/MC xấu | Khớp kiểm toán |
| Lỗi lot 01:53 | ghep/skea b120 trước vá **không** dùng làm PASS; lot×4 skea và lot01 ghep **sau** vá thì số net OK nhưng vẫn IS |

---

## Việc không xác minh được (và vì sao)

1. **HTM salvage GBPUSD** — chỉ có summary JSON + path `E:\...` trên máy nhà (OFF); không đọc được deal list / top-trade concentration trên box.  
2. **Tái mô phỏng parquet** — có `GBPCAD_H1.parquet`, `EURGBP_H1.parquet` nhưng box thiếu `pyarrow`/`fastparquet`; không cài thêm để tránh phình RAM. Không có CADJPY/NZDUSD/GBPUSD H4 sẵn trong `/workspace/brain2/data`.  
3. **Mã dịch Python sinh CSV 3279057100** — không còn trong cache box (`SO_CO_CHE`: “chưa có trong cache box”).  
4. **Commission XM micro “thật”** — `CHIEN_LUOC` ghi hoa hồng báo cáo = 0, chỉ stress mô phỏng.  
5. **Máy Windows nhà** — không chạm (theo brief).

---

## Kết luận cứng (cho parent / user)

User nói đúng: *“Cứ tôi hỏi lại là ứng viên lại fail.”* Lần này fail **trước khi hỏi**, vì:

1. Hai hệ CSV mù / IS thuần (**3279**, **ghep**) dính đúng quy tắc mới sau skst299b.  
2. **mql5344** fail toán %/năm (3.5% ≠ 12%).  
3. **brainxlmrz** rule thật nhưng DD 78.8% + 25% ticks + salvage orphan.  
4. **skea61c×4** đẹp nhất về số sau vá, nhưng vẫn IS trên CSV span — hạ xuống ứng viên, không ĐẠT.

Ưu tiên chạy lại (khi máy nhà bật): **skea61c** (tái sinh SMA OOS) → **brainxlmrz** (tick tốt + holdout) → **ghep_0bf2** (OOS trước 2024) → dịch **3279** trước mọi lot-scale → **mql5344** chỉ sau sửa CAGR/OOS.
