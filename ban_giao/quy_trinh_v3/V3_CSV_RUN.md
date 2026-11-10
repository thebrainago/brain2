# V3 — chạy MT5 cho các hệ CSV (lập 2026-11-09, giờ Bangkok UTC+7)

Nguồn: `nhan/v3_wf.py` (WF 12/3, k chọn trên train), số Python ĐO trong `reports/v3/<hệ>/*_ket_qua_py.json`,
bảng tổng: `python3 /workspace/quy_trinh_v3/v3_bang.py`. Dữ liệu giá tới 2026-10-09.

## 0. Cái nào đáng chạy MT5

Cổng Python (thiết kế §4): Lượt A OOS DD < 80 % và CAGR > 10 %, không stop-out; Lượt B (vốn mới 2024) không cháy, DD < 80 %;
hệ toàn BUY phải thắng mua-giữ sau swap; cổng phí `loc_phi_nhanh` = PASS.

| Hệ / biến thể | TF | gui_mt5 |
|---|---|---|
| **ghep60ff adxngang** (GBPCAD) | H1 | **CÓ — duy nhất** |
| ghep60ff goc / catlo40 | H1 | không (goc: Lượt B cháy; catlo40: DD A 85,47 %, phí REJECT) — chỉ chạy nếu muốn đối chứng |
| ghep_0bf2, ghepe9b4 (goc/adxngang/catlo40), skea61c, 2600ea39, mql5344 | H4/H1 | không |

`ghepe9b4 gian13` KHÔNG có file: EA bỏ qua InpGianBuoc khi InpBuocPct > 0 → trùng `goc`. `atrb2` CHƯA ĐO (Python không mô phỏng ATR).

## 1. File cần chép sang máy nhà (ví dụ slot `E:\brain2_grok\mt5_slots\g12`)

Sau khi parent commit/push và máy nhà `git pull` (không autostash/rebase/reset):

1. **CSV lệnh vào** → `%APPDATA%\MetaQuotes\Terminal\Common\Files\` (KHÔNG phải `<slot>\MQL5\Files` — agent tester không đọc được;
   .set đã đặt `InpCsvChung=true`):
   - `reports\v3\ghep60ff\v3a_ghep60ff_adxngang_H1_vao_hash.csv` (13 758 dòng, cột lot đã là lot chuẩn 0,01 = 1 micro, mã `GBPCAD#`).
   - Lượt A và B dùng CHUNG một CSV (B chỉ bắt đầu từ 2024.01.01; các dòng trước đó EA bỏ qua theo thời gian).
2. **.set** → `<slot>\MQL5\Profiles\Tester\`: `v3a_ghep60ff_adxngang_H1.set`, `v3b_ghep60ff_adxngang_H1.set` (hai file giống hệt nhau).
3. **.ini** → để ở đâu cũng được, ví dụ `<slot>\v3\`: `v3a_ghep60ff_adxngang_H1.ini`, `v3b_ghep60ff_adxngang_H1.ini`.
4. EA `BRAIN\BRAIN_XuLiLenh.ex5`: dùng bản biên dịch từ `ea_demo/BRAIN_XuLiLenh.mq5` hiện tại (các input InpGiuToiDaNen / InpMarginMin có từ 17/10, InpAdxMax=0 nên bản cũ hơn cũng không lọc gì).

## 2. Thiết lập tester (đã có trong .ini/.set sinh sẵn)

| Mục | Lượt A | Lượt B |
|---|---|---|
| Expert | `BRAIN\BRAIN_XuLiLenh.ex5` | như A |
| Symbol | `GBPCAD#` | `GBPCAD#` |
| Period | H1 | H1 |
| Model | 4 (Every tick based on real ticks) | 4, **bắt buộc ≥ 99 % real ticks**, thấp hơn thì CHƯA ĐO ĐƯỢC |
| FromDate → ToDate | 2009.01.01 → 2026.10.10 | 2024.01.01 → 2026.10.10 |
| Deposit / Currency / Leverage | 10000 / USD / 1:500 | như A |
| ExecutionMode / Optimization | 0 / 0 | như A |

Các input quan trọng trong .set: `InpVao=4` (CSV), `InpFileCsv=v3a_ghep60ff_adxngang_H1_vao_hash.csv`, `InpCsvChung=true`,
`InpLot0=0.01` (lot thật lấy từ cột lot của CSV = k × lot0 theo lịch WF), `InpGiuToiDaNen=720` (30 ngày H1), `InpMarginMin=300`,
`InpAdxMax=0` (lọc ADX đã làm trong CSV bằng Wilder ADX14 < 25), `InpGioCamTu=23 / InpGioCamDen=2`, quản lí lệnh (TP 0,2 %, bước 0,5 %, ×1,3, 4 tầng) giữ cố định theo .set job V1.

Bảng cho các hệ KHÔNG đạt (chỉ để đối chứng nếu muốn; file đã sinh sẵn trong `reports\v3\<hệ>\`, cùng Model 4 / 10000 / 1:500 / ToDate 2026.10.10, A từ 2009.01.01, B từ 2024.01.01):

| Hệ | Symbol | TF | InpGiuToiDaNen | CSV (Common\Files) |
|---|---|---|---|---|
| ghep60ff goc / catlo40 | GBPCAD# | H1 | 720 | v3a_ghep60ff_<bt>_H1_vao_hash.csv |
| ghep_0bf2 goc | GBPCAD# | H4 | 180 | v3a_ghep_0bf2_goc_H4_vao_hash.csv |
| ghepe9b4 goc/adxngang/catlo40 | GBPNZD# | H4 | 180 | v3a_ghepe9b4_<bt>_H4_vao_hash.csv |
| skea61c goc | CADJPY# | H4 | 180 | v3a_skea61c_goc_H4_vao_hash.csv |
| 2600ea39 goc | GBPNZD# | H1 | 720 | v3a_2600ea39_goc_H1_vao_hash.csv |
| mql5344 goc | NZDUSD# | H1 | 720 | v3a_mql5344_goc_H1_vao_hash.csv |

## 3. Chạy

```
cd /d E:\brain2_grok\mt5_slots\g12
terminal64.exe /portable /config:E:\brain2_grok\mt5_slots\g12\v3\v3b_ghep60ff_adxngang_H1.ini
```
Chạy B trước (ngắn, có real tick), rồi A. Báo cáo ra `<slot>\v3b_ghep60ff_adxngang_H1.htm` (theo `Report=`).
Không đụng terminal XM chính và claude.exe; nếu phải dừng thì `taskkill /PID <pid>` đúng PID của terminal slot.

Cách khác (parent quyết): đưa `reports\v3\ghep60ff\v3a_/v3b_ghep60ff_adxngang_H1_viec.json` vào `hang_doi\can_test\` để thợ
chạy (`che_do=ong_dan_csv`, mã `GBPCADmicro`, CSV micro `_vao.csv`, `he_so_lot=[1.0]`, `uu_tien=95`). `tho_mt5.py` mới sẽ:
gắn cờ 0 lệnh bất kể thời lượng, gắn `chua_do_duoc_tick_that_<pct>_duoi_99` cho v3b < 99 % tick thật, và không chọn k trên cửa sổ đo (`k_tot="lich_wf"`).

## 4. Đọc kết quả — lưu ý

- Symbol `#` trên tài khoản demo: tester cho swap = 0 (xem báo cáo brainxlmrz) → lãi MT5 THIẾU swap; phải cộng swap ƯỚC sau
  (Python: swap đo XM của hệ này ≈ +1,48 USD/rổ trung bình, tức nhỏ so với lãi 87,7 USD/rổ — số Python, chưa đối chiếu MT5).
- Lượt A: dữ liệu real tick XM cho 2009–2023 có thể không đủ; tester sẽ tự sinh tick từ M1 → ghi rõ % real tick, chỉ dùng A để so hình dạng
  với Python (`*_py_lenh_mt5.csv`), không dùng làm số cổng nếu < 99 %.
- So khớp: số rổ, ngày mở, lãi/năm với `v3a_ghep60ff_adxngang_H1_ket_qua_py.json` (Python A: CAGR 12,81 %, DD 46,69 %; B: CAGR 63,82 %, DD 68,11 %).
- Ngày bắt đầu lịch sử và ToDate phụ thuộc slot: nếu slot chưa có GBPCAD# tới 2026.10.10 thì ToDate thực tế ngắn hơn — ghi lại.
- Free Demo only, không gửi Telegram, không commit file cấm.
