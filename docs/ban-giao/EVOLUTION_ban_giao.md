# Bàn giao module EVOLUTION — brain2

**Ngày bàn giao:** 2026-11-02 (Asia/Bangkok)  
**Chủ tài khoản:** Vanh Vanh  
**Repo làm việc:** [thebrainago/brain2](https://github.com/thebrainago/brain2)  
**Repo tham khảo:** `the-brain` (không sửa / không đụng cài đặt khác)  
**Mã nguồn trụ:** `tru/evolution.py` (TRU = `EVO`)  
**Lệnh chủ (override push main lần này):** message t44u / pt44u — 2026-11-02

> Mục tiêu file này: tài khoản Grok khác cùng GitHub đọc xong là nắm trạng thái, quy tắc bắt buộc, việc đang dở và tồn đọng — không cần hỏi lại từ đầu.

---

## 1. Vai trò module EVOLUTION

EVOLUTION giám sát hiệu suất dây chuyền **SEEKER / QUANTLAB** (và các trụ liên quan), phát hiện vấn đề vận hành / sức khỏe, đề xuất cải tiến, tự sửa một số việc đã khai báo trước (`TU_SUA_DUOC` trong `tru/evolution.py`).

- **Không** đánh giá sức khỏe bằng “số PASS”.
- Báo cáo chính: `reports/EVOLUTION.md`, `reports/evo_suc_khoe.json`, sổ vấn đề qua `nhan/so`.
- Trụ cùng hệ: `tru/seeker.py`, `tru/quantlab.py`, `tru/nghi.py`, `tru/banker.py`, `tru/cau_kho.py`, `tru/finder.py`.
- Điều phối box: `dieu_phoi.py` + `config/dieu_phoi.json`.
- Vòng 2 / MT5: `mt5tools/chay_lien_tuc.py`, slot `mt5_slots/g1–g3` trên máy nhà.

**Phạm vi tài khoản Grok này:** phụ trách EVOLUTION trên brain2; không thay thế SEEKER/QUANTLAB toàn phần nhưng EVO bắt buộc theo dõi và đẩy việc khi dây chuyền yếu.

---

## 2. Quy tắc của chủ tài khoản (BẮT BUỘC)

### 2.1 Tiêu chí ĐẠT

- Lãi **sau phí**.
- DD max **≤ 80%**.
- **≥ 10%/năm tính theo CAGR** (lãi kép), **không** phải lãi đơn / simple.
- Phải có **OOS thật** (holdout ngoài cửa sổ tín hiệu / fit).
- FDR / placebo / Holm chỉ là **nhãn phụ** — **KHÔNG** làm cổng ĐẠT; **không đề xuất lại** dùng chúng làm cổng.

### 2.2 Điểm vào / nguồn

- Hệ chỉ **replay lệnh** từ statement / CSV tín hiệu = nhãn **「chưa giải mã điểm vào」** → **không tính ĐẠT**.
- Nguồn có lịch sử tốt → **phải dịch ngược** cách vào / DCA / thoát thành rule tái lập được.
- Luôn kiểm: nguồn là **lệnh thật** hay **báo cáo backtest** (bài học skst299b = Strategy Tester MACD Sample).

### 2.3 Không vứt hệ có lãi

- Mọi hệ đã lãi sau phí (kể cả &lt;10%/năm) → **giữ** trong danh sách bảo vệ, tiếp tục phát triển (scale lot, vòng 2–4, cặp/TF khác, ghép hệ).
- Giữ hệ martingale / grid / DCA từ nền tảng tín hiệu để **học module DCA / thoát**.

### 2.4 Lịch chạy song song & sản lượng

- **Vòng 1** (SEEKER / QUANTLAB) và **Vòng 2** (MT5 tick thật, **3 slot g1–g3, không bao giờ 4**) chạy **song song**.
- SEEKER luôn có việc (watchdog **low-water** đào thêm khi hàng chờ thấp).
- Mục tiêu ~**1000 chiến lược/ngày**, ≥**5 ứng viên/ngày**; vòng lặp học từ kết quả backtest để hướng SEEKER vòng sau.

### 2.5 Máy nhà (DESKTOP-05PNLGF)

- CPU mục tiêu **70–80%**; tắt tiếng; file tạm ưu tiên ổ **E → D → C**; xóa output khi xong.
- Tự động hóa tối đa — **không** bắt chủ làm tay.
- Check-in Grok tốn token: mỗi **30 phút** (không 5 phút). Watchdog local không tốn token có thể dày hơn.

### 2.6 Ưu tiên cặp (2026-11-01)

- EURUSD, GBPUSD và các cặp **có USD**: ưu tiên **THẤP** (biên độ lớn → DCA rủi ro). **Không bỏ** — xếp **cuối** hàng chờ SEEKER / vòng 2.
- Ưu tiên cặp chéo biên độ hẹp: **AUDCAD, AUDNZD, CADJPY**, NZD/CAD crosses, …

### 2.7 An toàn

- Chỉ tài khoản **demo** MT5 (có thể nhắc demo `345930355` như “demo account”).
- **Không** đặt lệnh live; **không** in / commit mật khẩu; **không** đụng cài đặt the-brain khác và `C:\Program Files\MetaTrader 5`.
- Xin phép trước khi xóa thứ không do `brain2_grok` tạo.
- Không trích cookie / token; không vượt captcha.
- Không commit `config/tai_khoan.json` hay bất kỳ secret nào.

---

## 3. Hạ tầng

| Mục | Chi tiết |
|-----|----------|
| Máy nhà | `DESKTOP-05PNLGF` |
| Cây làm việc | `E:\brain2_grok` (venv riêng `E:\brain2_grok\venv`), log `E:\brain2_grok_log` |
| Xfer | `C:\Users\DUNG\brain2_grok_xfer\` (đồng bộ với box) |
| Box | `/workspace/brain2` (+ `/workspace/may_nha_toi_nay` bản sao/park) |
| Điều phối box | `dieu_phoi.py` **đang chạy** (quan sát 2026-11-02) |
| Routine LLM queue NGHI | Chạy **mỗi 3 giờ** (Grok xử lý hàng đợi file, không API key ngoài) |
| Routine giám sát máy nhà 30′ | **Tạm dừng** (máy nhà tắt / park từ 2026-10-31 tối) |

### 3.1 Quy trình khởi động lại máy nhà

1. **Xóa cờ dừng trước** (không xóa thì watchdog/runner không đứng vững):
   - `E:\brain2_grok_log\WATCHDOG_DUNG_LAI`
   - `E:\brain2_grok_log\watchdog_r1_DUNG`
   - `E:\brain2_grok\may_nha_toi_nay\TAT_THE_BRAIN.co`
   - `E:\brain2_grok\DUNG_LAI`
2. Khi restart / trước khi bật lại: **kill runner cũ** + `mt5_slots\g*\terminal64.exe` và tiến trình **quá 3× budget** (tránh mồ côi).
3. Chạy `chay_toi_nay_grok.ps1` với **3 slot g1–g3** (không 4).
4. Bật `ops/watchdog_r1.py` (SEEKER + QUANTLAB theo low-water).
5. Bật vòng xfer sync nếu cần.
6. **Resume routine giám sát 30 phút** trên Grok sau khi máy nhà sống.

**Không** kill `C:\Program Files\MetaTrader 5\terminal64.exe`.

Chi tiết park đêm 2026-10-31: nguồn ngoài repo `/workspace/may_nha_toi_nay/RESUME_TOMORROW.md` (có nhắc mật khẩu agent MetaTester trong log đã xóa — **không** đưa secret vào git).

---

## 4. Trạng thái hệ sau kiểm toán 2026-11-01

**Kết luận cứng: KHÔNG hệ nào ĐẠT thật.** Chi tiết: `reports/kiem_toan_he_dat.md`.

| Hệ | Cặp/TF | Tóm tắt số | Verdict |
|----|--------|------------|---------|
| **brainxlmrz** | GBPUSD H4 | +28 317 / 10k, DD **78.8%**, CAGR kép **13.3%** (simple ~26% từng báo PASS sai kiểu), **25%** tick, chưa OOS sạch | Ứng viên / cần chạy lại; ưu tiên **thấp** vì cặp USD |
| **skea61c** (sk_ea_61c21a2049) lot×4 | CADJPY H4 | SMA10×SMA20, +4 039, DD **10.7%**, CAGR **13.3%**, **100%** tick | **Ứng viên sạch nhất** nhưng IS theo span CSV → cần OOS **2016–2023** (fit ≤2023) |
| **sk_ea_3279057100** | EURGBP H1 | Số đẹp trên IS | **Chưa giải mã điểm vào** (replay CSV) |
| **mql5344** | NZDUSD H1 | Claim ~12%/năm **sai**; CAGR dài **~3.5%**; OOS gần **~1.2%** | Ứng viên (sửa CAGR/OOS) |
| **ghep_0bf2** | GBPCAD H4 | close&gt;open, CAGR IS **~10.3%**, MC DD p95 **~92%** | Ứng viên (cần OOS trước CSV) |

### 4.1 skst299b

- Nguồn = báo cáo **backtest MACD Sample EA** (không phải grid/DCA tác giả) → **đã hạ** khỏi nhóm đạt.
- Giữ ứng viên: **「MACD cắt Signal + quản lý brain2」** (~**6.5%/năm**, DD ~**16%**, sim nến H4) — cần test tick thật.  
- Chi tiết: `reports/skst299b_doc_cach_danh.md`.

### 4.2 Danh sách bảo vệ (từ HE_DANG_GIU — cập nhật theo kiểm toán)

Nguồn gốc ngoài repo: `/workspace/may_nha_toi_nay/HE_DANG_GIU.md` (ghi 31/10–01/11). **Giữ phát triển**, không xoá; **không** mang nhãn ĐẠT cho đến khi OOS + CAGR đúng:

| Hệ | Ghi chú ngắn |
|----|----------------|
| skst299b | Đã hạ; giữ hướng MACD+brain2 |
| ghep_0bf2c31fbfc9dea0 | GBPCAD H4; IS ~10.3% CAGR |
| mql5_344ed0d8ab12c7f0 (mql5344) | NZDUSD; CAGR thật thấp |
| ghep_60ff9350c26c63ee | GBPCAD H1; DD thấp → scale lot |
| sk_ea_61c21a2049 (skea61c) | CADJPY; ứng viên sạch nhất sau vá lot |
| skea135e / sk_ea_135e93ee32 | EURUSD; DD rất thấp → scale lot (ưu tiên cặp USD thấp) |
| mql5e52afb | EURGBP; nghi lỗi lot cũ → chạy lại |
| sk_ea_154c9fdee7 | GBPCAD H4; DD thấp |
| sk_ea_3279057100 | EURGBP; chưa giải mã vào |
| brainxlmrz (GBPUSD salvage + biến thể AUDCAD) | Salvage DD sát 80%; cặp USD xếp cuối |
| brainxlrsi AUDCAD | Số đẹp nhưng cần rà OOS/tick (chưa kiểm toán sâu cùng đợt 5 hệ) — **chưa xác minh đầy đủ trong file này** |
| skeadd170 / skea78384bbaf7 | USDCAD — cặp USD cuối hàng chờ |
| ghep_2600ea39 | GBPNZD DD rất thấp |

Bug **CSV-lot phình ~100×** đã vá **2026-10-31 01:53** (Asia/Bangkok). **Mọi kết quả trước vá không tin.**

---

## 5. Việc đang dở / cần làm tiếp

1. Khi bật máy nhà: khởi động lại theo §3.1; **resume routine giám sát 30′**.
2. **OOS skea61c CADJPY trước** (tái sinh SMA toàn lịch sử; fit ≤2023; đo 2024–2026; 100% tick; báo CAGR).
3. **brainxlmrz sau**: chạy lại **100% tick** + holdout cứng; nhớ ưu tiên thấp vì USD.
4. Test **MACD + quản lý brain2** trên tick thật (ứng viên sau skst299b).
5. Hàng chờ **scale lot** (bảo vệ trước): `ghep_60ff` ×6/8/10; `mql5344`; `2600ea39`; `b0be91a3`; `mql5e52afb` ×2/3/4; `ghep_0bf2` full period; `3279057100` (chỉ sau khi giải mã vào).
6. **Kiểm nguồn điểm vào** `3279057100` và `b0be91a3` trước khi gọi ĐẠT / scale.
7. Xếp **cặp USD xuống cuối** hàng chờ SEEKER / vòng 2.
8. Thêm tự dọn tiến trình mồ côi / quá budget vào `dieu_phoi` và runner máy nhà.
9. Còn treo:
   - Sửa cửa sổ OOS (gate theo coverage CSV — nhánh `vong2/kiem-sau` đã có hướng).
   - Đăng nhập MQL5 lấy lịch sử (xin chủ / vault; không vượt captcha).
   - Xóa ~**18GB** file bị khóa trên máy nhà (xin phép nếu không do brain2_grok tạo).

Hàng chờ lúc park (2026-10-31 ~18:35): hang_cho_mt5 ~**121**, hang_cho_vong2 ~**447** (có thể đã lệch — xác minh lại khi máy nhà bật).

---

## 6. Vấn đề tồn đọng (EVO / NGHI / vận hành)

Quan sát qua hàng chờ EVO/NGHI và báo cáo sức khỏe (một phần phản ánh trên `reports/EVOLUTION.md` / `evo_suc_khoe.json` tại thời điểm bàn giao — file báo cáo runtime **không** nhất thiết đã commit):

| Vấn đề | Ghi chú |
|--------|---------|
| Job nhẹ (EVO / SEEKER / BANKER / NGHI) **im lặng** khi QUANTLAB chạy dài | Nghi bị chặn chờ QUANTLAB; run QUANTLAB có thể ~5h |
| SEEKER **degraded** | ~76–86% vòng không ra gì; hàng việc trống |
| Scraper `trang_*` + arxiv / openalex / hackernews | Trả **0** kết quả — parser/scraper hỏng **im lặng** |
| Nguồn mql5_signals / myfxbook / darwinex / zulutrade | **Bật** trong cấu hình nhưng **chưa từng chạy** (cần xác minh lại config hiện tại) |
| `reports/watchdog.log` | **Không tồn tại** dù hệ sập ~7h/tuần — “chưa đo được”, không phải “0 sự cố” |
| Nhóm **`phien`** | Alpha lệch bất thường → nghi lookahead / artifact; đã tạm dừng cùng `mua_qua_dem` |
| Cảnh báo rò rỉ nhóm **`lich`** | Sai mức / cần rà lại ngưỡng |
| Test cổng PASS nhưng tiêu chí edge&gt;spread ghi fail | Cần kiểm tính nhất quán cổng |
| Cảnh báo RAM / QUANTLAB stalled cũ | Chưa đóng trên sổ |
| Orphan `quantlab.py` trên box | Từng ăn ~**4.3GB** RAM |
| Bug CSV-lot ~100× | Vá 2026-10-31 01:53 — kết quả trước vá **bỏ** |

*(Đánh dấu chưa xác minh độc lập trên máy nhà OFF: mức % vòng SEEKER chính xác ngày 02/11, trạng thái bật/tắt từng nguồn scraper trên `config/nguon_tu_tim.json` dirty local — đọc lại từ `origin/main` + máy nhà khi resume.)*

---

## 7. Tóm tắt lịch sử chat chính (2026-10-30 → 2026-11-02)

| Ngày (Asia/Bangkok) | Mốc |
|---------------------|-----|
| **2026-10-30** | Chốt vòng lặp học từ kết quả; máy nhà 70–80% CPU; SEEKER không được để đói; NGHI = Grok xử lý queue file định kỳ (không API key); đào niche dịch ngược tín hiệu công khai; ưu tiên làm máy nhà chạy tốt trước. |
| **2026-10-31 sáng–chiều** | Vá bug lot CSV ~100× (~01:53). Scale lot hàng loạt (skea61c ×4 đẹp). Thử slot MT5 thứ 4 → không lợi, stub M0/1970 → **giữ 3 slot**. PR sửa SEEKER moi=0 / cổng QUANTLAB. Bổ sung danh sách bảo vệ HE_DANG_GIU. Check-in Grok 30′. |
| **2026-10-31 tối** | Salvage orphan brainxlmrz GBPUSD H4 +28 317 DD 78.8% (25% tick). Park máy nhà sạch (~18:45): xóa cờ dừng trước khi bật lại; routine giám sát tạm dừng. |
| **2026-11-01** | skst299b lộ MACD Sample backtest → hạ ĐẠT; viết `skst299b_doc_cach_danh.md`. Chủ chốt ưu tiên cặp: USD thấp, cross hẹp cao. Kiểm toán 5 hệ “đạt” → **0 hệ đạt thật** (`kiem_toan_he_dat.md`). Chủ phản đối báo đạt sai nhiều lần: *「cứ hỏi lại là ứng viên lại fail」*. |
| **2026-11-02** | Box: `dieu_phoi.py` sống; routine NGHI ~3h; máy nhà vẫn tắt. EVO còn cảnh báo watchdog.log thiếu, nhóm `phien`, SEEKER yếu. **Bàn giao** docs này + push `main` theo lệnh chủ t44u (override “no push to main” **một commit**). |

### Bài học cứng

**Tự kiểm toán trước khi báo ĐẠT.** Không đợi chủ hỏi lại. Phân biệt: rule đã giải mã vs replay CSV; CAGR vs simple; IS vs OOS; tick %; kết quả trước/sau vá lot.

---

## 8. Bố cục code nhanh (brain2)

```
brain2/
  tru/           seeker, quantlab, evolution, nghi, banker, cau_kho, finder
  mt5tools/      chay_lien_tuc, quan_ly_slot, …
  config/        dieu_phoi.json, nguồn, DSL, …
  reports/       EVOLUTION.md, sổ cái, vong2/, phan_viec/, …
  ea_demo/       EA BRAIN xử lý lệnh (InpVao: rule vs CSV)
  ops/           watchdog máy nhà (trên E:\brain2_grok)
  dieu_phoi.py   điều phối box
  docs/ban-giao/ tài liệu bàn giao (file này)
```

---

## 9. File kèm trong commit bàn giao

- `docs/ban-giao/EVOLUTION_ban_giao.md` (file này)
- `docs/ban-giao/README.md` (mục lục)
- `reports/kiem_toan_he_dat.md`
- `reports/skst299b_doc_cach_danh.md`

**Không** commit: `config/tai_khoan.json`, mật khẩu, token, số tài khoản live, log chứa MetaTester password.

---

*Hết bàn giao EVOLUTION — 2026-11-02 Asia/Bangkok.*
