# Quy trình nối Seeker → Vòng 1 → Vòng 2 → Vòng 3 (chạy thật trên máy nhà)

Ngày soạn: 09/11/2026 (giờ Việt Nam, UTC+7). Người soạn: Grok Bot. Đây là **tài liệu thiết kế**, chưa sửa dòng code nào trong repo.
Nguồn đọc: `origin/main` commit `d8f721c2` và nhánh `origin/cursor/seeker-source-recovery-ca1f` (đọc bằng `git show`, chưa merge).
Mọi con số dưới đây chép từ file trong repo, có ghi đường dẫn. Chỗ nào là ước lượng thì ghi **ƯỚC**. Chỗ nào chưa có số thì ghi **CHƯA ĐO ĐƯỢC**.

---

## 0. Tóm tắt một trang

**Hiện trạng.** Brain2 chưa có hệ nào ĐẠT thật. 34 hệ "đạt" ở vòng 2 (`reports/VONG_2_HE_DAT_2026-11-05.md`) đều đo **in-sample**: CSV điểm vào chỉ phủ khoảng 01/2024–10/2026, và tester chạy đúng trong cửa sổ đó. Đợt kiểm toán 01/11 (`reports/kiem_toan_he_dat.md`) đã hạ cả 5 hệ từng báo đạt.

**Phát hiện mới khi rà lần này (đọc CSV trong repo):**

- CSV vào của `ghepe9b4` GBPNZD H4 có **3.599 dòng, tất cả là MUA**, trong khoảng 4.300 nến H4. CSV của `ghep60ff` GBPCAD H1 có **7.849 dòng, tất cả là MUA**. Tức là hai hệ này gần như "luôn mua rồi DCA". Lãi chủ yếu có thể đến từ xu hướng tăng của cặp trong 2024–2026, không phải từ điểm vào.
- Điểm vào của `ghep60ff` và `ghep0bf2` ("đóng > mở") được rút từ dòng `PositionsTotal()==0 /* and close>open*/`. Điều kiện close>open nằm **trong comment** của EA gốc (thẻ `sk_ea_44640140cc` trong `data/ong_dan/tho_box.sqlite`).
- Mọi job nâng lot đều có `InpMarginMin=0` (tắt chặn margin) và `InpGiuToiDaNen=0` (không giới hạn thời gian giữ) (`hang_doi/da_test/lot_*.json`).
- Job `v2qd_gian13_ghepe9b4…` ở k=1 cho **0 lệnh trong 62 giây** nhưng vẫn được ghi là kết quả đo, vì cổng `phan_xu_ket_qua` chỉ loại khi 0 lệnh **và** chạy dưới 60 giây (`mt5tools/an_toan_tester.py`).

**Quy trình mới, một dòng:** chỉ nhận nguồn có luật tái lập được → tái sinh điểm vào trên dữ liệu dài 2008–2026 → quản lý lệnh có trần thời gian giữ, swap thật và margin → **walk-forward 12/3 tối ưu riêng từng cặp**, đo OOS nối liền bằng MT5 → ĐẠT khi OOS sau phí và swap có DD < 80% và CAGR kép > 10%/năm → lên demo forward.

```
 SEEKER ──[Cổng S]──► V1 ──[Cổng 1]──► V2 ──[Cổng 2]──► V3 (máy nhà) ──[Cổng 3]──► DEMO FORWARD (chỉ demo)
   │                    │                 │                  │
   │ luật giải mã được  │ tái sinh điểm   │ quản lý lệnh,    │ WF 12 tháng train / 3 tháng test, tối ưu RIÊNG từng cặp,
   │ hoặc EA chạy được; │ vào 2008–2026,  │ trần giữ lệnh,   │ k lot chọn trong train, MT5 nối OOS, ≥99% real tick
   │ không nhận CSV/    │ phí XM thật,    │ swap XM, margin, │ cho đoạn 2024+, CAGR kép; nhãn: bootstrap DD,
   │ statement phát lại │ OOS ≠ 0 lệnh    │ mở ≤ cấu hình    │ so với vào ngẫu nhiên, độ nhạy, Py/MT5
   ▼                    ▼                 ▼                  ▼
 loai/ + lý do        loai/ + lý do     loai/ + lý do      TRƯỢT ghi sổ; giữ "mảnh tốt" (TRI_NHO/dac_diem_he)
```

**Danh sách V3 lần này** (§3): skea61c CADJPY H4 → brainxlmrz GBPUSD H4 → ghep_0bf2 GBPCAD H4 → nhóm ghepe9b4 GBPNZD H4 (gian13/adxngang/atrb2/catlo40) → ghep60ff GBPCAD H1 (catlo40/adxngang) → 2600ea39 GBPNZD H1 → 3279 EURGBP (chỉ sau khi giải mã) → mql5344 NZDUSD H1. Hai EA mới từ nhánh Seeker đi V1 trước: `na_1233d657c07b` EMA_Cross_Demo nhận vào V1, còn `na_2d4605e4e9a6` NewsTrader **trượt cổng S** (lý do ở §3.9).

**Chạy được ngay khi máy bật, không cần sửa code:** (1) brainxlmrz chạy lại native `InpVao=1` (không dùng CSV), cần lấy file .set gốc trên máy nhà; (2) V1 của EMA_Cross_Demo, sau khi job được đưa lên `main` (cần Anh duyệt). Mọi hệ chạy bằng CSV đều **chưa** chạy V3 được. Phải tái sinh CSV dài và lịch walk-forward trước (§4).

---

## 1. Quy trình HIỆN TẠI (theo code và tài liệu)

### 1.1 Seeker: tìm nguồn, EA, tín hiệu

- Mã: `tru/seeker.py`, `seeker_*.py`, `seeker/` (công khai: `seeker/cong_khai/`, file nguồn: `seeker/nguon_file/`, nạp EA gốc: `seeker/nap_ea_goc.py` trên nhánh Seeker). Tài liệu: `docs/SEEKER_V2.md`, `tai_lieu/ONG_DAN.md`.
- Hai làn (`TRI_NHO/QUYET_DINH.md`, 03/11):
  - **Làn A `co_ma_nguon`:** có EA, .set hoặc mã nguồn → MT5 chạy dài.
  - **Làn B `dich_phuong_phap`:** chỉ có mô tả và lịch sử lệnh → phải có `lich_su_dat` và `khop_vao_pct ≥ 70`. Cổng nằm ở `may_nha/hang_doi_git.kiem_spec`.
- Ống dẫn (`tai_lieu/ONG_DAN.md`, `nhan/ong_dan.py`): nhận → phân loại → quyết định đường dịch (`noi_bo | spec_dsl | llm | mt5_truc_tiep | bo_qua`) → tối ưu Python (`nhan/tai_khoan.chay_tk`, có lot thật, ký quỹ, stop-out, spread, swap) → lọc 65/15 → sinh `.set`, `.ini` và CSV vào (`xuat_csv_vao`) → MT5.
- Nhánh Seeker (07/11) thêm làn nạp EA gốc không cần dịch Python. Đã xếp 2 việc `hang_doi/can_test/na_*.json` **chỉ trên nhánh** (`docs/ban-giao/SEEKER_NGUON_ban_giao.md`). Ghi chú đi kèm: "heuristic OnTick + lời gọi lệnh không phải chứng minh", "CHUA_BIEN_DICH".
- Lỗ hổng: thẻ `sk_ea_3279057100` đi đường `mt5_truc_tiep` và **không có `tin_hieu`** trong `tho_box.sqlite`, nên CSV của nó không truy được ra luật. Thẻ `b0be91a35f43f34a` đi đường `llm` (trạng thái `LLM`), trên box cũng không có `tin_hieu`.

### 1.2 Vòng 1: chạy MT5 trên CSV vào, nâng lot

- Thợ máy nhà: `may_nha/tho_mt5.py`. Hàng đợi git: `hang_doi/can_test → dang_lam_<máy>_<slot> → da_test | loai`, sổ `hang_doi/so_cai.jsonl`.
- Chế độ chính `che_do = ong_dan_csv`: EA `ea_demo/BRAIN_XuLiLenh.mq5` với `InpVao=4` (VAO_CSV) đọc file vào trong `reports/phan_viec/viec_mt5/<thẻ>/od_<id>_XM_CSV_vao.csv`. Thợ nhân lot theo `he_so_lot` (k = 1…10).
- Tiêu chí: `DD_MAX, CAGR_MIN = 80.0, 10.0` (`tho_mt5.py` dòng 28). Hàm `danh_gia()` lấy **k tốt nhất trên chính cửa sổ đo**. CAGR tính kép (`cagr()`).
- Đầu ra: `hang_doi/da_test/lot_<hệ>_<TF>.json` (k_tot, CAGR, DD, PF, chất lượng tick), báo cáo `hang_doi/bao_cao/*.htm`, CSV lệnh và giá trong `hang_doi/ket_qua_csv/*.csv.gz`.
- Kết quả 03/11: 8 hệ "ĐẠT" (`TRI_NHO/TRANG_THAI.md`), tất cả trên cửa sổ CSV 12/2023–10/2026, riêng mql5344 từ 12/2017.

### 1.3 Vòng 2: đổi quản lý lệnh trên cùng CSV vào

- Thiết kế: `tai_lieu/VONG_2.md` §7–8. 38 việc `v2qd_*` (atrb1, atrb2, gian13, trailatr, catlo40) cộng các việc `v2cd_*` (adxngang, adxxh, atrpmax80, atrpmin20, tinnfp). Ưu tiên 88–90, cao hơn vòng 1 (≤ 55).
- Biến thể (`reports/VONG_2_HE_DAT_2026-11-05.md`):
  - `atrb1`: bước DCA 1×ATR14, TP 0,5×ATR14.
  - `atrb2`: bước 2×ATR, TP 1×ATR.
  - `gian13`: bước DCA giãn ×1,3 mỗi tầng.
  - `catlo40`: cắt cả rổ khi lỗ ≥ 40% số dư.
  - `trailatr`: trailing kích 1×ATR, trả 0,5×ATR.
  - `adxngang`: chỉ mở rổ mới khi ADX14 < 25.
- Kết quả: 34 hệ đạt, **in-sample**. Chính báo cáo đã ghi "thời gian giữ không thực tế".
- `nhan/vong2.py` có sẵn walk-forward 3 đoạn, block bootstrap 10 ngày, stress phí ×1,5 và equity tái dựng. Tất cả đều chạy **trên cùng cửa sổ CSV**.

### 1.4 Các lỗ hổng đã bị kiểm toán chỉ ra (có dẫn chứng)

| # | Lỗ hổng | Dẫn chứng |
|---|---|---|
| 1 | **In-sample trên span CSV**: tester chạy đúng cửa sổ CSV, và k cũng chọn trên cửa sổ đó | `kiem_toan_he_dat.md` (skea61c, ghep_0bf2); `VONG_2.md` §7.2 |
| 2 | **OOS stub 0 lệnh**: chạy "trước 2024" nhưng CSV không phủ đoạn đó, nên ra 0 lệnh | 3279: `v2r2oos_truoc_…` 0 lệnh; ghep_0bf2 dai19 = stub |
| 3 | **CAGR simple bị gọi là kép** | brainxlmrz báo 26,34% (simple), kép thật 13,3%; mql5344 báo ~12%, kép thật 3,5% |
| 4 | **Ôm lệnh hàng trăm ngày** | `VONG_2_HE_DAT`: giữ max 399 ngày (mql5e52), 809–818 ngày (mql5344) |
| 5 | **Swap**: tester XM áp swap **hiện tại** cho mọi năm, lịch sử swap CHƯA ĐO ĐƯỢC | `config/phi_xm_micro.json` `_nhan`; `DICH_NGUOC_VONG2_SWAP_VANG.md`: có swap là UV1 AUDCAD hết đạt |
| 6 | **Real ticks thấp** | brainxlmrz 25%; mql5344 31%; XM real tick chỉ dày từ khoảng 01/2024 (`tai_lieu/KINH_NGHIEM.md`) |
| 7 | **Mở vượt cấu hình**: số lệnh mở đồng thời đo được lớn hơn `InpMaxTang` | 2600ea39 4/5, skea154 4/6, mql5344 4/8, mql5e52 9/18 (`VONG_2_HE_DAT`) |
| 8 | **Điểm vào chưa giải mã** | 3279 (`mt5_truc_tiep`, không có `tin_hieu`); b0be91 (`llm`); skst299b là báo cáo backtest MACD Sample |
| 9 | (mới) **Điểm vào tầm thường**: luôn MUA | CSV ghepe9b4 3.599/3.599 MUA, ghep60ff 7.849/7.849 MUA; rule "close>open" lấy từ comment |
| 10 | (mới) **Margin tắt, giữ vô hạn** | `InpMarginMin=0`, `InpGiuToiDaNen=0` ở mọi `lot_*.json` |
| 11 | (mới) **0 lệnh vẫn được tính là kết quả** nếu chạy ≥ 60 s | `phan_xu_ket_qua()`; ví dụ `v2qd_gian13_ghepe9b4…` k=1 cho 0 lệnh trong 62 s |
| 12 | (mới) **Hai biến thể cho cùng chuỗi lệnh** | mql5e52 gian13 và catlo40 (111 lệnh); 2600ea39 catlo40 và gian13 (132 lệnh) — `VONG_2_HE_DAT` "Cần nghi" |
| 13 | Bug lot CSV ~100× trước 31/10 01:53 | `TRI_NHO/TRANG_THAI.md`; `CHIEN_LUOC_DA_LOC.md` gắn BỊ THAY THẾ |

---

## 2. Quy trình NỐI đề xuất, với cổng chặn ở mỗi bước

**Nguyên tắc chung (đã có quyết định của Anh trong `TRI_NHO/`):**

- Tiêu chí ĐẠT duy nhất: **DD < 80% và CAGR kép > 10%/năm**. Được nâng lot miễn DD < 80%.
- Chỉ phát lại CSV hoặc statement, hoặc chỉ in-sample → không tính ĐẠT.
- FDR, placebo, Holm, p-value chỉ là **nhãn**, không bao giờ là cổng (`QUYET_DINH.md` 16/10 và 02/11).
- Mới theo Anh (09/11): **không** khóa 2 năm holdout kiểu AI Pathways; **không** chạy nguội cùng tham số sang cặp khác. Mỗi cặp tối ưu riêng. Sau V3 mới lên demo forward.

> **Cần Anh chốt:** brief có ghi bootstrap, so với vào lệnh ngẫu nhiên và độ nhạy tham số. Theo `QUYET_DINH.md` thì những phép này **chỉ được làm nhãn**. Tài liệu này để chúng là **nhãn bắt buộc phải đo và in ra**, không làm cổng. Nếu Anh muốn biến "thắng vào ngẫu nhiên" thành cổng, cần ghi quyết định mới vào `QUYET_DINH.md`.

Có hai loại cổng:

- **Cổng hợp lệ:** số đo có đáng tin không. Trượt thì kết quả là CHƯA ĐO ĐƯỢC.
- **Cổng ĐẠT:** chỉ một, là DD < 80% và CAGR kép > 10% trên OOS.

### 2.1 Cổng S — Seeker (đầu vào của V1)
Nhận khi có **một** trong hai:

- (a) Luật vào/ra đã giải mã thành `tin_hieu` (spec DSL), tái sinh được trên OHLC bất kỳ.
- (b) EA `.mq5`/`.ex5` tự sinh lệnh trong tester (EA gốc, EA BRAIN native, hoặc Free Demo Market).

**Không nhận:**

- Chỉ có statement, CSV lệnh hoặc màn hình lịch sử. Những nguồn này chuyển sang làn B: phải `khop_vao_pct ≥ 70` rồi mới thành (a).
- EA cần dữ liệu ngoài không có trong tester (ví dụ lịch tin nhập tay), hoặc mặc định không giao dịch được.
- Luật lấy từ code đã bị comment, hay từ dòng điều kiện không chạy. Gặp trường hợp này thì gắn nhãn `luat_tu_comment` và quay về đọc lại mã nguồn.

Ghi kèm: URL, sha256, giấy phép, đường dịch, `kieu_ea`, có biên dịch được hay chưa. Trượt thì vào `hang_doi/loai/` kèm lý do.

### 2.2 Cổng 1 — V1: điểm vào gốc tái sinh được trên dữ liệu dài, phí XM thật

- **Dữ liệu:** từ 2008 (HistData M1 → H1/H4) hoặc lịch sử MT5 XM, nối tới 10/2026. Box đã có H1 2008–2023 cho GBPCAD, GBPNZD, USDCAD, NZDUSD, EURGBP, AUDNZD, EURCHF, NZDCAD, XAUUSD (`/workspace/du_lieu_fx/hd_dai/*_h1_2008_2023_ny7.csv`), cộng M5 2024–10/2026 (`/workspace/du_lieu_fx/hd28/`). **CADJPY trên box chỉ có 2024–2026.**
- **Tái sinh CSV vào** từ `tin_hieu` (cùng `nhan/ong_dan.xuat_csv_vao`) cho **toàn kỳ**, không chỉ 2024–2026. Hệ native hoặc EA gốc thì chạy thẳng trên toàn kỳ.
- **Phí:** spread, swap XM đo trong `config/phi_xm_micro.json`; hoa hồng XM micro đo được bằng 0. Python dùng `nhan/tai_khoan.chay_tk`; MT5 tự áp phí của symbol.
- **Hợp lệ:**
  - Mỗi năm có lệnh (không còn đoạn 0 lệnh do thiếu CSV).
  - Đối chiếu CSV mới với CSV cũ trên 2024–2026: trùng ≥ 95% timestamp. Thấp hơn thì luật giải mã sai.
  - Có cả hai chiều nếu luật có hai chiều. Ví dụ ghepe9b4: thẻ ghi 2 spec nhưng CSV chỉ có MUA, phải xác minh.
- **Đạt V1 (lọc thô, chưa phải ĐẠT):** tham số mặc định của tác giả, lot gốc, toàn kỳ, có lãi sau phí và swap, không stop-out. Không đòi 10%/năm ở đây, vì V3 mới chọn k.

### 2.3 Cổng 2 — V2: quản lý lệnh trong khuôn thực tế
Biến thể giữ như cũ (atrb1/atrb2/gian13/catlo40/trailatr/adxngang/…), nhưng **bắt buộc** đủ các điều kiện sau:

- **Trần thời gian giữ rổ:** `InpGiuToiDaNen` (EA đã có). Đề xuất mặc định 30 ngày (H4 = 180 nến, H1 = 720 nến), kèm 2 mức nhạy 15 và 60 ngày. **Ngưỡng cần Anh duyệt.**
- **Swap thật:** MT5 tự tính theo symbol; Python dùng `phi_xm_micro.json`. Báo tổng swap USD.
- **Margin:** bật `InpMarginMin` (mặc định của EA là 300%; mọi job cũ để 0). Stop-out tester theo tài khoản XM, có stop-out thì TRƯỢT.
- **Số lệnh mở thực tế ≤ cấu hình:** đo từ `_lenh_mt5.csv`. Mỗi chiều ≤ `InpMaxTang`, tổng ≤ 2×`InpMaxTang`. Vượt thì CHƯA ĐO ĐƯỢC, phải tìm nguyên nhân trong EA trước (hiện CHƯA RÕ).
- **Biến thể phải khác hành vi:** cùng chuỗi lệnh với gốc thì đánh dấu `trung_hanh_vi` và không đếm.
- **0 lệnh trong khi CSV có lệnh trong cửa sổ** → CHƯA ĐO ĐƯỢC, bất kể chạy bao nhiêu giây.
- V2 vẫn đo trên toàn kỳ dài. Ra một **danh sách ngắn ≤ 3 biến thể mỗi hệ** để đưa vào V3. Không chọn theo một cửa sổ đẹp.

### 2.4 Cổng 3 — V3: chạy thật trên máy nhà, OOS sạch
**Walk-forward 12/3, riêng từng cặp:**

- Cửa sổ train 12 tháng, test 3 tháng, trượt mỗi quý.
- Không holdout 2 năm cố định. Không bê tham số từ cặp khác sang.
- Mỗi quý chọn bộ tham số tốt nhất **chỉ trên 12 tháng train**. Không gian tìm gồm:
  - hệ số chu kỳ chỉ báo {0,5; 0,75; 1; 1,25; 1,5} (theo `VONG_2.md` §2.4);
  - quản lý: TP, bước DCA, số tầng, hệ số lot, biến thể V2;
  - **k lot**: chọn k lớn nhất mà DD train ≤ 60% (đề xuất, cần Anh duyệt). Áp k đó cho quý test.
- **Không được chọn k sau khi đã xem OOS**, vì đó chính là lỗi in-sample cũ.
- Điểm chọn: theo `VONG_2.md` §2.5, tức lãi/năm ÷ max(DD, 10) × cao nguyên. Train có ít hơn 20 rổ thì giữ bộ của quý trước.
- Rổ mở trong quý test được đóng theo tham số của quý đó, kể cả khi sang quý sau. Vì vậy cần lịch tham số trong EA (§4, việc E1).
- Bắt đầu OOS sớm nhất là 2009Q1. Python chạy từ 2008, MT5 tùy độ dài lịch sử XM có trên slot.

**Đo bằng MT5 (máy nhà):**

- **Lượt A, OOS dài nối liền:** một lần chạy liên tục 2009 (hoặc từ khi XM có lịch sử) → 10/2026, lịch tham số WF đã chốt. Ghi chất lượng mô hình (trước 2024 phần lớn là tick sinh từ M1).
- **Lượt B, real tick:** cùng lịch, chạy 2024-01 → 10/2026. **Bắt buộc ≥ 99% real ticks**; thấp hơn thì CHƯA ĐO ĐƯỢC.
- Python chạy song song cùng lịch. Tỉ lệ Python/MT5 là nhãn (khoảng tham chiếu 0,8–1,25 theo `VONG_2.md` §1.8).

**Cổng ĐẠT V3:**

- Trên **OOS nối** (Lượt A), sau phí và swap: DD equity < 80% **và** CAGR kép > 10%/năm.
- Lượt B không được cháy và DD < 80%. Báo CAGR riêng của Lượt B.
- Không stop-out. Hợp lệ theo Cổng 2.
- CAGR luôn là `(1+net/vốn)^(1/năm) − 1` (`tho_mt5.cagr`). Cấm số simple.

**Nhãn bắt buộc phải in (không phải cổng):**

1. **Block bootstrap 10 ngày** trên equity OOS: DD p50/p95 (`nhan/vong2.py`).
2. **So với vào lệnh ngẫu nhiên cùng quản lý:**
   - Python: 1.000 CSV ngẫu nhiên, cùng số rổ mỗi quý, cùng tỉ lệ MUA/BÁN, cùng lịch quản lý và k.
   - MT5: 10 CSV kiểm chéo.
   - In phân vị của hệ thật so với phân phối ngẫu nhiên. Với hệ "luôn mua" như ghepe9b4 và ghep60ff, đây là phép quan trọng nhất.
3. **Độ nhạy:** ±1 nấc quanh bộ được chọn nhiều nhất, tỉ lệ lân cận giữ ≥ 70% điểm (cao nguyên, `VONG_2.md` §2.5). MT5 kiểm 4–6 lân cận trên Lượt B.
4. Lãi theo năm, đoạn WF tệ nhất, giữ TB và max, số lệnh mở max, tổng swap, số lần cắt rổ hoặc chạm trần giữ.

### 2.5 Sau V3: demo forward

- Chỉ **tài khoản demo XM**, với tham số của quý hiện hành theo lịch WF. EA Market chỉ dùng bản **Free Demo**. Không live, không đặt lệnh thật.
- Theo dõi tối thiểu 1 quý (đề xuất). Lệch so với Python và MT5 cùng kỳ là nhãn. Live là quyết định riêng của Anh.

---

## 3. Danh sách chạy V3 lần này (xếp ưu tiên)

Thời gian chạy MT5 thật đo được (median từ `hang_doi/da_test/*.json`): H4 khoảng 3 năm real tick **543 s**/lần, H1 khoảng 3 năm **915 s**/lần. Lần chạy 9–11 năm (phần lớn là tick sinh) H1: 137–335 s. Máy chạy song song tối đa khoảng **5 test** vì giới hạn RAM (`may_nha/VAN_HANH_MAY_NHA.md`). Mọi thời gian bên dưới là **ƯỚC** từ các median này.

Dạng job V3 đề xuất: `hang_doi/can_test/v3a_<hệ>_<TF>.json` (Lượt A) và `v3b_<hệ>_<TF>.json` (Lượt B), `lan: co_ma_nguon`, `uu_tien ≥ 95` (trên v2 là 88–90), `he_so_lot: [k từ lịch]`, thêm trường `lich_wf` và `cua_so: "OOS"`.

| # | Hệ | Cặp/TF | Điểm vào | Dữ liệu dài | EA/set | Sẵn sàng? | ƯỚC MT5 |
|---|---|---|---|---|---|---|---|
| 1 | skea61c (`sk_ea_61c21a2049`) | CADJPY H4 | ĐÃ GIẢI MÃ: SMA10×SMA20 hai chiều (`tin_hieu` trong `tho_box.sqlite`) | **THIẾU** CADJPY 2008–2023 trên box | BRAIN_XuLiLenh VAO_CSV; Lot0 3, MaxTang 6, TP 0,2%, bước 0,8%, lot ×1,6 | Không: cần dữ liệu + CSV dài + lịch WF | A ~20 phút, B ~9 phút; nhãn ~2–3 giờ |
| 2 | brainxlmrz | GBPUSD H4 | ĐÃ GIẢI MÃ, native `InpVao=1` (MRZ, N=100, Z=2), không CSV | Lịch sử XM trên máy nhà (GBPUSD 2004–2015 chạy được nhưng 0% real tick) | BRAIN_XuLiLenh; Lot0 0,1, vốn 10k; **.set đầy đủ không có trong repo** (salvage tại `E:\brain2_grok\reports\mt5_lien_tuc\salvage\`) | **Gần sẵn**: chạy lại V1/V2 native được ngay khi có .set; WF cần lịch | ~10–20 phút/lần |
| 3 | ghep_0bf2 | GBPCAD H4 | Rule "close>open" (MUA), **lấy từ comment** của sk_ea_44640140cc; 1 lệnh/rổ, TP 0,1%, không SL | Có trên box (hd_dai + hd28) | VAO_CSV; Lot0 30 micro | Không: CSV dài + lịch WF; nên chạy so với ngẫu nhiên trước | A ~20, B ~9 phút |
| 4 | ghepe9b4 (gian13 / adxngang / atrb2 / catlo40) | GBPNZD H4 | `tin_hieu` có, nhưng **CSV toàn MUA** (3.599 dòng) → cần xác minh chiều BÁN | Có trên box | VAO_CSV; Lot0 10, MaxTang 6, TP 0,5%, bước 0,8% | Không: CSV dài + lịch; 4 biến thể | 4×(A+B) ~2 giờ |
| 5 | ghep60ff (catlo40 / adxngang) | GBPCAD H1 | close>open, **CSV toàn MUA** (7.849 dòng) | Có trên box | VAO_CSV; Lot0 3, MaxTang 4, TP 0,2%, bước 0,5%, lot ×1,3 | Không | 2×(A ~30 + B ~15 phút) |
| 6 | 2600ea39 | GBPNZD H1 | ĐÃ GIẢI MÃ: CCI/RSI/SMA (freqtrade SmoothOperator) | Có trên box | VAO_CSV; Lot0 3, MaxTang 4, TP 0,3%, bước 1,2% | Không; **mở vượt cấu hình 4/5** phải giải thích trước | A ~30, B ~15 phút |
| 7 | sk_ea_3279057100 | EURGBP H1 | **CHƯA GIẢI MÃ** (`mt5_truc_tiep`, không có `tin_hieu`) | Có trên box | Nguồn `autopendingbyrsi.mq4` có trên box (`data/seeker_da_nguon/tai_ve/github/GeneralTradingSarl__mql4_experts/…`) | **Chặn ở Cổng S**: dịch luật RSI-pending, đối chiếu từng timestamp với CSV 1.269 dòng | Chưa xếp |
| 8 | mql5344 | NZDUSD H1 | `tin_hieu` có (EMA20×EMA50 "xu hướng lớn") | Có trên box | VAO_CSV; Lot0 3, MaxTang 4; CSV hiện 2018–2026 (480 dòng); ticks 31% | Không: tái sinh từ 2008 + lịch; mở vượt cấu hình 4/8 | A ~30, B ~15 phút |
| 9a | `na_1233d657c07b` EMA_Cross_Demo | job ghi AUDCADmicro H1 2016–2026 | EA gốc tự sinh lệnh (EMA12/26, SL 2×ATR, RR 1,5) | Lịch sử XM máy nhà | `.mq5` tải từ mql5.com Code Base; sha256 `1233d657…` khớp bản trên box | **V1 chạy được** khi job có trên `main` | ~5–10 phút |
| 9b | `na_2d4605e4e9a6` NewsTrader | — | `NewsTime = -1` mặc định: một lần chạy chỉ một tin, cần thời điểm tin nhập tay; `MM=true` nên `Lots` không có tác dụng | — | — | **Trượt Cổng S** → `loai/` | 0 |

Chi tiết từng hệ:

**3.1 skea61c CADJPY H4.**

- Cần dữ liệu CADJPY M1 2008–2023: tải HistData theo `hd_dai/tai.py`, hoặc máy nhà xuất bằng `mt5tools/tai_lich_su_mt5.py`.
- Sau đó tái sinh CSV SMA10×20 2008–10/2026, WF Python, sinh lịch, rồi tạo job `v3a_skea61c21a2049_H4` và `v3b_skea61c21a2049_H4`.
- Job `can_test/lot_skea61c21a2049_H4.json` hiện có chạy trên CSV 2024–2026 (IS), nên **hoãn**.

**3.2 brainxlmrz GBPUSD H4.**

- Cặp USD, theo `QUYET_DINH.md` (01/11) là ưu tiên thấp. Brief của lần này xếp thứ 2 nên giữ thứ tự brief.
- Việc đầu khi máy bật: đọc `.set` gốc trong thư mục salvage (file cấu hình EA, không phải bí mật), chép vào `reports/v3/brainxlmrz/`.
- Sau đó chạy native hai lượt cố định: 2016.01–2026.10 (V1 lại) và 2024.01–2026.10 (≥ 99% tick).
- WF cần Python mô phỏng MRZ. `ea_demo/ea_logic_py.py` **không có** MRZ, nên phải viết thêm, hoặc chọn tham số bằng tối ưu MT5 trên từng cửa sổ train (`ini_ong_dan` hỗ trợ `Optimization`, nhưng thợ hiện chỉ đọc `.htm`, không đọc `.xml` tối ưu).
- Năm 2026 lỗ −4.967 (`TRI_NHO/dac_diem_he/brainxlmrz.md`), DD 78,8%. Kỳ vọng thấp.

**3.3 ghep_0bf2.**

- Trước khi tốn slot cho WF, chạy **so với vào ngẫu nhiên** bằng Python: luật "mua mọi nến tăng" gần như ngẫu nhiên.
- MC DD p95 92,3% (`CHIEN_LUOC_DA_LOC.md`). Kỳ vọng thấp.

**3.4 ghepe9b4 GBPNZD H4.**

- Swap GBPNZD XM: mua −3,55, bán −19,32 điểm/lot/ngày (`phi_xm_micro.json`). Ôm lệnh MUA sẽ bị trừ dần.
- 2008–2023 có những đợt GBPNZD giảm dài (dữ liệu trên box mở đầu 2008 ở 2,51, cuối 2023 ở 2,01). Đây là phép thử thật cho hệ "luôn mua".

**3.5 ghep60ff GBPCAD H1.** Như 3.4. Swap GBPCAD: mua +0,57, bán −16,22.

**3.6 2600ea39 GBPNZD H1.** Có hai chiều. Trước V3 cần giải thích vì sao catlo40 và gian13 cho cùng 132 lệnh.

**3.7 3279.** Không xếp V3. Dịch luật trước. Không khớp thì bỏ CSV.

**3.8 mql5344.** Kỳ vọng thấp: CAGR dài hạn 3,5% (`kiem_toan_he_dat.md`). Nhưng có thể nâng lot nếu DD còn dư.

**3.9 Hai EA từ nhánh Seeker.**

- **EMA_Cross_Demo** qua Cổng S (EA tự sinh lệnh). V1 = mặc định tác giả, lot 0,1, 2016–2026.
  - Nên thêm 1–2 cặp chéo hẹp theo ưu tiên của Anh (AUDCAD, AUDNZD, CADJPY). Mỗi cặp là một job riêng, **không** bê tham số tối ưu từ cặp này sang cặp kia.
  - Mã tải từ mql5.com trong `tai_ma_nguon()`. Nếu tải bị chặn, chép từ box `data/nguon_file/codebase/77653/EMA_Cross_Demo_EA.mq5` (sha256 khớp) vào slot.
- **NewsTrader** trượt Cổng S: mặc định không có tin nên tester gần như không có lệnh, và `Lots` bị MM ghi đè nên nâng lot không có tác dụng. Có thể giữ làm "mảnh" tránh tin, nhưng không test như một hệ.

**Ước tổng thời gian máy nhà** cho #1–#6, #8, #9a, mỗi hệ gồm A + B + nhãn MT5: khoảng 13 cặp hệ×biến thể × 3–5 giờ slot ≈ 40–65 giờ slot. Với 5 slot song song là **khoảng 8–13 giờ** đồng hồ (**ƯỚC**, chưa đo). Phần Python (tái sinh CSV, WF, 1.000 lần ngẫu nhiên) chạy trên box, chưa đo thời gian.

---

## 4. Việc code và config cần làm (CHƯA sửa — liệt kê để duyệt)

| # | File | Việc | Cần Anh duyệt? |
|---|---|---|---|
| E1 | `ea_demo/BRAIN_XuLiLenh.mq5` | Thêm `InpFileLich`: CSV "từ ngày → bộ tham số quản lý" cho rổ mở trong mỗi quý, để một lần chạy MT5 nối đủ OOS walk-forward. Thêm `InpNgungMoSau` (ngày dừng mở rổ mới). Cần biên dịch lại trên các slot | **Có** (đổi EA lõi) |
| E2 | `ea_demo/BRAIN_XuLiLenh.mq5` | Tìm và sửa nguyên nhân "mở vượt cấu hình" (4/5, 4/8, 9/18) | **Có** |
| E3 | `ea_demo/BRAIN_XuLiLenh.mq5` (tùy chọn) | Thêm `VAO_MA_CROSS` (SMA/EMA cắt) để skea61c, skea154, mql5344 chạy native, khỏi cần CSV | Có |
| T1 | `mt5tools/an_toan_tester.py` `phan_xu_ket_qua` | 0 lệnh khi CSV có lệnh trong cửa sổ → CHƯA ĐO ĐƯỢC (bỏ điều kiện "< 60 s") | Có (đổi cổng) |
| T2 | `may_nha/tho_mt5.py` | Đọc chất lượng tick. Job `v3b_*` dưới 99% → CHƯA ĐO ĐƯỢC. Với `v3*` bỏ chọn k trên cửa sổ đo trong `danh_gia()` (k lấy từ lịch). Xuất `_lenh_mt5.csv` cho cả chế độ native và `ea_goc` (hiện chỉ xuất khi `ong_dan_csv`). Tính giữ max, mở max, stop-out vào kết quả | Có |
| T3 | `may_nha/hang_doi_git.py` `kiem_spec` | Cổng S: từ chối `lan=co_ma_nguon` khi `kieu_ea` là heuristic mà EA cần input bắt buộc không có (vd `NewsTime`); từ chối `che_do=ong_dan_csv` khi CSV không phủ cửa sổ `tu…den` | Có |
| P1 | mới `nhan/v3_sinh_csv.py` | Tái sinh CSV vào từ `tin_hieu` trên dữ liệu 2008–2026 (dùng `BRAIN_ONG_DAN_DU_LIEU`, `xuat_csv_vao`). Đối chiếu ≥ 95% với CSV cũ 2024–2026. Ghi vào `reports/v3/<hệ>/` | Không (mã mới, không đổi lõi) — vẫn báo |
| P2 | mới `nhan/v3_wf.py` | Walk-forward 12/3 từng cặp bằng `nhan/tai_khoan.chay_tk` (phí và swap `phi_xm_micro.json`, margin, stop-out). Chọn tham số và k trên train, xuất `lich_wf.csv` | Quy tắc chọn k (DD train ≤ 60%) **cần duyệt** |
| P3 | mới `nhan/v3_cham.py` | Chấm OOS nối: CAGR kép, DD, lãi theo năm, nhãn bootstrap (tái dùng `nhan/vong2.py`), 1.000 lần ngẫu nhiên, độ nhạy, Py/MT5. Ra `reports/V3_KET_QUA_<ngày>.md` | Không |
| Q1 | mới `may_nha/seed_v3.py` | Gieo job `v3a_*`/`v3b_*` với `uu_tien ≥ 95` | Không |
| Q2 | `hang_doi/can_test/` | **Hoãn** các job chỉ IS: `v2cd_atrpmin20_*` (7), `v2cd_tinnfp_*` (8), `lot_skea61c21a2049_H4`, `lot_skst299b0817f66d4096_H1`. Chuyển sang thư mục mới `hang_doi/hoan/` hoặc hạ ưu tiên < 50 | **Có** (đụng hàng đợi trên `main`) |
| Q3 | `hang_doi/dang_lam_desktop-05pnlgf_g1..g5` | 5 job v2cd (atrpmin20/atrpmax80) đang dở từ 05/11. Thợ bật lại sẽ làm tiếp trước. Chọn: để chạy nốt (khoảng 10–30 phút mỗi job), hoặc trả về can_test hay hoãn | **Có** |
| G1 | nhánh `cursor/seeker-source-recovery-ca1f` | Đưa `hang_doi/can_test/na_1233d657c07b.json` (và nếu muốn `seeker/nap_ea_goc.py`) lên `main` bằng cherry-pick hoặc tạo lại file. Chuyển `na_2d4605e4e9a6` sang `loai/` | **Có** (đụng `main`) |
| D1 | dữ liệu ngoài repo | CADJPY M1 2008–2023 (HistData miễn phí) hoặc xuất từ MT5 máy nhà | Không (đọc công khai) |
| D2 | `.set` brainxlmrz | Chép `.set` gốc từ salvage máy nhà vào `reports/v3/brainxlmrz/` (chỉ tham số EA, không có bí mật) | Không |
| C1 | `config/` | Ghi ngưỡng V3 (trần giữ, MarginMin, ≥ 99% tick, quy tắc k) vào file mới `config/vong3.json`. Không dùng khóa `v3` cũ trong `config/tieu_chi.json` (bản 24/08 mang nghĩa khác, tránh nhầm) | **Có** (ngưỡng) |
| M1 | `tai_lieu/VONG_3.md`, `TRI_NHO/QUYET_DINH.md`, `TRI_NHO/TRANG_THAI.md` | Ghi quyết định của Anh 09/11: không holdout 2 năm, tối ưu riêng từng cặp, WF 12/3, bootstrap/ngẫu nhiên/độ nhạy là nhãn. Tên file nên dùng `VONG_3`/`v3*`, tránh trùng `reports/vong3*`…`vong32*` cũ | Ghi sau khi Anh chốt |
| M2 | (đã biết, còn mở) | Map `GBPCADmicro → GBPCAD#` (`BAN_GIAO_MAY_NHA.md` §6); dọn log Agent MT5 phình nhiều GB | Không |

Thứ tự làm đề xuất: Q2/Q3/G1 (Anh duyệt) → T1 → P1 → P2 → E1 (+E2) → T2 → Q1 → P3. Trong lúc chờ E1, có thể chạy V3 bằng **nhiều lần chạy theo từng quý**: không cần sửa EA nhưng rổ bị cắt ở cuối quý và tốn thời gian hơn. Chỉ nên dùng làm phương án tạm.

---

## 5. Quy tắc an toàn máy nhà (giữ nguyên trong mọi bước)

Nguồn: `TRI_NHO/00_DOC_TRUOC.md` §3, `may_nha/VAN_HANH_MAY_NHA.md` §2, `TRI_NHO/BAN_GIAO_MAY_NHA.md` §2, `docs/ban-giao/EVOLUTION_ban_giao.md` §2.7.

- **Không secret trong git hay chat.** Không commit `config/tai_khoan.json`, mật khẩu, token, số tài khoản live, log có mật khẩu MetaTester. Không đọc `E:\api.txt`.
- **`taskkill` chỉ theo đúng PID**, và chỉ cây tiến trình do thợ tự phóng (`CL.giet_cay`). Không kill theo tên. Không kill `claude.exe`, terminal XM chính (`C:\Program Files\XM Global MT5\terminal64.exe`, tài liệu EVO ghi `C:\Program Files\MetaTrader 5`) hay Riot/League. Không tắt máy.
- **Git trên máy nhà:** chỉ `git pull --no-rebase`. Không autostash, rebase, force push, `reset --hard`. Thợ tự commit `hang_doi`. Không chạy thợ trong `C:\Users\DUNG\brain2` (thợ từ chối), chỉ trong `D:\brain2_tho`.
- **Chỉ tài khoản demo** (Free Demo only). Không đặt lệnh live. Không mở tài khoản sàn. EA Market chỉ dùng bản Free Demo.
- **Không gửi Telegram** và không nhắn ra ngoài khi chưa được duyệt.
- **File không commit:** `config/ma_nguon_con_tro.json`, `config/ngan_sach_nhip.json`, `nhat_ky/kho_co_che_ghi.log`, `reports/EVO_SUC_KHOE.md`, `reports/VONG_DAY_DU.json`. Mã nguồn người khác chỉ để trong `data/` (gitignore).
- **RAM:** giữ ≥ 6 GB trống. Thợ chờ RAM trước mỗi lần phóng (`BRAIN_RAM_TRONG_MIN_GB`, máy nhà đặt 11 theo `VAN_HANH_MAY_NHA.md`; bàn giao 05/11 ghi 6). Giãn cách 180 s. Tối đa khoảng 5 test real tick cùng lúc. Ghi ổ E trước, rồi D, cuối cùng C.
- Không đụng cài đặt the-brain khác. Xin phép trước khi xóa thứ không do `brain2_grok` tạo. Không vượt captcha hay 429.
- Dịch LLM trả phí: TẮT.

### Runbook ngắn khi máy bật (chỉ đọc và khởi động, theo `BAN_GIAO_MAY_NHA.md` §2)

1. Kiểm tiến trình hiện có (chỉ liệt kê). Orch PID 17160 cũ gần như chắc đã mất sau khi tắt máy. Không kill gì ngoài PID do thợ tạo.
2. Trong `D:\brain2_tho`: `git pull --no-rebase`.
3. Anh quyết Q3 (5 job dang_lam), rồi mới bật thợ:

   ```
   cd D:\brain2_tho
   set PYTHONUTF8=1
   set PYTHONIOENCODING=utf-8
   set BRAIN_RAM_TRONG_MIN_GB=11
   python may_nha\tho_mt5.py --song-song --tran 5
   ```

   Gọi python trực tiếp, không redirect stdin qua cmd.

4. Lúc rảnh, đổi `Tester\Bases` của g1–g5 sang junction `E:\brain2_grok\shared_bases` (§3 bàn giao).
5. Việc đầu tiên cho V3: chép `.set` brainxlmrz (D2), chạy V1 của EMA_Cross_Demo (sau G1). Hàng V3 cho các hệ CSV chỉ xếp sau khi có P1, P2 và lịch WF.

---

## 6. Đường dẫn

- Tài liệu này: `/workspace/quy_trinh_v3/QUY_TRINH_VONG3_2026-11-09.md` và `.pdf` (nháp ngoài repo; parent copy vào `reports/`).
- Báo cáo nền: `reports/VONG_2_HE_DAT_2026-11-05.md`, `reports/kiem_toan_he_dat.md`, `reports/DICH_NGUOC_VONG2_SWAP_VANG.md`, `reports/CHIEN_LUOC_DA_LOC.md` (BỊ THAY THẾ), `reports/UNG_VIEN.md`, `tai_lieu/VONG_2.md`, `tai_lieu/ONG_DAN.md`, `TRI_NHO/*`, `docs/ban-giao/*`, các báo cáo 09/11 (`QUET_INTRADAY`, `ORB_JUDAS`, `AI_PATHWAYS_SL_PHI`, `SWAP_SAN`). Các báo cáo 09/11 cùng kết luận "không hệ nào sống qua phễu". Cách WF 12/3 và so với ngẫu nhiên ở đó là mẫu cho V3.
- Ghi chú: `HE_DANG_GIU.md` **không có** trong repo, và cũng không còn ở `/workspace/may_nha_toi_nay/` (đã kiểm 09/11). Nội dung dùng lại qua bảng §4.2 trong `docs/ban-giao/EVOLUTION_ban_giao.md`. `UNG_VIEN.md` nằm ở `reports/UNG_VIEN.md`, `CHIEN_LUOC_DA_LOC.md` nằm ở `reports/`.
