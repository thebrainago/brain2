# KINH NGHIỆM VẬN HÀNH — máy nhà + box cloud (brain2)

Cập nhật 13/10/2026. Bài học vận hành khi chạy brain2 trên **máy nhà** và **box cloud** song song.
Không chứa mật khẩu, token, cookie hay số điện thoại. Xem thêm: `tai_lieu/DIEU_PHOI.md`, `tai_lieu/HANG_CHO_MAY_NHA.md`, `tai_lieu/VAN_HANH_MAY_NHA.md`, `tai_lieu/KINH_NGHIEM.md` (bài học chiến lược, khác tệp này).

---

## 1. Máy nhà

| Mục | Giá trị |
|---|---|
| Tên máy | `DESKTOP-05PNLGF` |
| User Windows | `C:\Users\DUNG` |
| MT5 gốc (XM) | `C:\Program Files\XM Global MT5` |
| Vai trò | Tester MT5 demo, trình duyệt đã đăng nhập, IP nhà (nguồn bị chặn trên box) |

Máy nhà và box chạy **cùng lúc**, chia việc theo `mt5tools/dieu_phoi_song_song.py`. Box không chạy MT5.

---

## 2. Ổ đĩa — không để tester phình ổ C

- Dữ liệu Strategy Tester / Agent / `bases` lịch sử **KHÔNG BAO GIỜ** để trên ổ **C:** — ổ C đầy làm máy nhà chậm rõ (lag cả UI).
- Đặt slot portable và cache trên **D:**, **E:**, hoặc **RAM disk** khi có (vd. `D:\mt5_tester\p1…`, `E:\mt5_tester\p3…`, `R:\mt5_tester`).
- Junction `%APPDATA%\MetaQuotes\Tester\<id>` sang ổ D/E nếu terminal gốc vẫn ghi AppData.
- **Sau mỗi lần chạy / cuối ca**: xoá `Tester\Agent-*`, `bases\*\history`, `bases\*\ticks`, báo cáo tạm; ghi lại dung lượng đã giải phóng.
- Mỗi mã mới tải lịch sử ~0,3–0,6 GB/slot; chạy qua đêm cần dọn khi ổ còn dưới ~6 GB (`don_neu_day` trong `chay_lien_tuc.py`).

---

## 3. Tác vụ the-brain phải để Disabled

Ba tác vụ Windows Task Scheduler sau **phải giữ Disabled** trên máy nhà:

- `TheBrainCauChay`
- `TheBrainCauChayBoot`
- `TheBrainSongSong`

Chúng tự phóng lại MT5 / hàng song song của the-brain, đụng slot tester brain2 và làm máy nặng ngoài ý muốn. Chỉ bật lại khi chủ dự án yêu cầu rõ.

---

## 4. Slot MT5 portable — `accounts.dat` và fail-fast

- Slot portable mới chép mà **thiếu** `config\accounts.dat` (và nên kèm `common.ini`) → lỗi *"tester not started because the account is not specified"*, terminal tắt sau ~12 s; vòng lặp phóng job kế → MT5 **mở/đóng liên tục (nhấp nháy)** trước mặt chủ dự án.
- Luôn chép `config\accounts.dat` + `common.ini` từ terminal gốc; nhớ chép cả `MQL5\Profiles\Tester\*.set` (`robocopy /XD Tester` bỏ qua cả `Profiles\Tester`).
- **Dừng khẩn (fail-fast)**: job chạy **< 90 giây** mà không có báo cáo → **xoá hết hàng đợi** slot đó, ghi `FAIL-FAST` (xem `chay_mt5_slot.ps1`).
- Mỗi slot một **cổng agent riêng** (không dùng chung Agent port giữa các terminal).
- Một terminal portable chỉ một phiên: gọi `MetaTrader5.initialize(path=slot)` khi slot đang test sẽ làm hỏng job — dùng slot riêng (vd. `E:\mt5_tester\p5`) cho xuất dữ liệu.

---

## 5. Điều phối CPU — 4 mức (MAX / CAO / VUA / THẤP)

Mã: `mt5tools/dieu_phoi_song_song.py`. Tên tiếng Anh tương đương: MAX / HIGH / MEDIUM / LOW.

| Mức | Khi nào | CPU mục tiêu | MT5 song song |
|---|---|---|---|
| **MAX** | Không game, CPU người dùng thấp | tới ~90 % | 4 |
| **CAO** (HIGH) | CPU người dùng vừa | ~75 % | 3 |
| **VUA** (MEDIUM) | CPU người dùng cao | ~50 % | 2 |
| **THẤP** (LOW) | Đang chơi game hoặc cửa sổ trước **toàn màn hình** | ~15 % | 0 |

- Phát hiện game / fullscreen → hạ mức ngay; không phóng MT5 mới; job đang chạy giữ Idle đến khi xong (không giết giữa chừng).
- Chạy **4 MT5 cùng lúc** làm lag game → khi chơi game phải về THẤP.
- Đo CPU trên Windows: loại `System Idle Process` (pid 0) — psutil có thể báo ~100 % idle giả.

---

## 6. Tài khoản và dữ liệu XM

- Tài khoản dùng cho tester/demo: **XM demo Standard**, mã có hậu tố **`#`** (vd. `GBPUSD#`, `AUDUSD#`). **Không** dùng Micro cho hàng tester này.
- Spread XM lúc **00h server** (mở nến D1) đắt khoảng **2–5×** (có lúc đo tới 5–10×) so với giữa ngày → vào lệnh D1 nên lệch giờ, thường **02h** (`InpGioVao=2`).
- **Lịch sử M1 thiếu trước ~2018-05** với AUD/NZD (và một số cặp liên quan) trên XM `#` → tester chỉ còn tick thưa (thường 00h) → so sánh giờ vào phải cùng giai đoạn có M1.
- **Chỉ số CFD** (index) thiếu dữ liệu lịch sử đầy đủ trên XM — **không tự sinh** được lịch sử; cache tick có thể phình **11–21 GB** nếu cố tải — tránh, dọn ngay.
- **GOLD / XAUUSD 2016–2026** với agent: từng làm agent **treo** — không để hàng đợi chạy dài trên khoảng đó khi chưa có biện pháp; ưu tiên đoạn/khung đã ổn định.
- Real ticks XM thường chỉ dày từ ~2024-01 (giai đoạn dài hơn có % real ticks thấp hoặc 0 %).

---

## 7. Hàng đợi không bao giờ cạn

- Máy nhà: hết việc bảng → `python mt5tools/chay_lien_tuc.py --den <giờ hết ca − ~35′>` (sinh việc liên tục).
- Sinh việc: `mt5tools/sinh_viec.py` (lưới tham số/mã/khung, near-miss, IS→OOS, Holm, chống trùng; ưu tiên ứng viên Python từ box).
- Box khi chờ máy nhà: `phan_tich_luoi_box.py` + `sinh_viec.py tong-ket` trên sổ cái — xem `tai_lieu/VONG_LAP.md` mục «KHÔNG BAO GIỜ CẠN VIỆC».
- Sổ cái máy nhà: `reports/mt5_lien_tuc/so_cai.jsonl` (máy nhà ghi; box tránh commit tệp này để giảm xung đột pull).

---

## 8. Lịch ca máy nhà

| Ca | Giờ (máy nhà) | Ghi chú |
|---|---|---|
| Ca ngày mặc định | **7h30 – 15h** hằng ngày | Chạy tester + Seeker đọc; hết ca dọn cache, không tắt máy |
| Tối / đêm | **Chỉ sau khi hỏi chủ dự án** | Không tự mở ca ngoài lịch |
| Ngoại lệ đã duyệt | Đêm **13/10/2026** | Chủ dự án cho phép chạy suốt đêm |

Kết thúc ca: đẩy báo cáo cần thiết, xoá tester/cache, đóng MT5, **không** tắt máy trừ khi được bảo.

---

## 9. Trình duyệt Chrome thebrainago (máy nhà)

- Hồ sơ: thư mục kiểu `D:\browser_thebrain` (hoặc `.browser_thebrain`), CDP cổng **9224**.
- Google: `thebrainago@gmail.com`. Khi 2FA hiện **prompt số trên iPhone**: **đọc số trên trang và nói cho chủ dự án** (không đoán, không ghi số điện thoại vào repo).
- Nhiều site đã đăng nhập tay trên hồ sơ này — ưu tiên tái dùng phiên, không tự đăng ký mới.
- **TradingView** và **MQL5** thường **bị chặn / mất phiên** trên hồ sơ AI CDP — dùng Chrome thật Profile người dùng hoặc thao tác màn hình theo `tai_lieu/VAN_HANH_MAY_NHA.md` khi cần.
- **cTrader**: đăng ký/xác minh cần **SĐT không phải VN** — không tự làm; chờ chủ dự án.
- **QuantPedia**: đăng nhập từng thất bại — ghi CHƯA ĐO ĐƯỢC / chờ người, không vượt captcha.
- Chi tiết bảo mật bàn giao (không mật khẩu trong git): `tai_lieu/VAN_HANH_MAY_NHA.md`.

---

## 10. Seeker và mạng xã hội

- **Seeker**: chỉ **đọc** + được phép **follow** nguồn đã duyệt. **Không** đăng bài, like, nhắn tin, join nhóm/diễn đàn.
- **Box**: đọc được **X công khai** (giới hạn khoảng **1000 lần đọc/ngày** — tôn trọng hạn mức API/công cụ).
- Không Telegram tự join, không mua gì, không vượt Cloudflare bằng công cụ lách.

---

## 11. Box bị Cloudflare — việc phải về máy nhà

Box bị chặn (403 / Cloudflare / tương tự) trên ít nhất:

- TradingView
- fxblue
- QuantPedia
- SSRN

→ Đọc / xuất bằng trình duyệt trên **máy nhà** (IP nhà), lưu tóm tắt + URL vào `reports/seeker_may_nha/`. Box không cố vượt.

---

## 12. Shell trên máy nhà (PowerShell)

- Biến `$...` truyền **inline** qua lớp shell từ xa / công cụ agent dễ **bị cắt hoặc biến dạng**. Đưa lệnh phức tạp vào **file script** `.ps1` rồi gọi file.
- **Chỉ giết tiến trình của phiên/job mình**. Từng có lần giết `python` hàng loạt làm chết tiến trình của chủ dự án — không `taskkill` / `Stop-Process` theo tên chung toàn máy.
- Path giữa ổ (E:→D:): `Path.replace` có thể thất bại → dùng `shutil.move`.
- Git trên máy nhà/box dùng chung repo: `git pull --rebase` cẩn thận; không `--force`; stash việc đang dở của job khác trước khi rebase.

---

## 13. Checklist nhanh đầu / cuối ca

**Đầu ca máy nhà**

1. `git pull --rebase` (stash nếu có thay đổi local của job khác).
2. Kiểm Task Scheduler: ba tác vụ TheBrain* vẫn Disabled.
3. Slot D/E (hoặc RAM) còn chỗ; có `accounts.dat` trên mỗi portable.
4. Hỏi chủ dự án nếu muốn chạy ngoài 7h30–15h.

**Cuối ca**

1. Sao lưu / commit sổ cái + báo cáo cần thiết (không bí mật).
2. Xoá cache tester trên D/E/R; kiểm ổ C không phình.
3. Đóng MT5; cập nhật `HANG_CHO_MAY_NHA.md` / `GHI_CHU_NANG_CAP_GROK.md` nếu có kết quả mới.
4. `git push` thường (không force).

---

*Tệp này = kinh nghiệm vận hành. Bài học chiến lược/backtest → `tai_lieu/KINH_NGHIEM.md`. Vòng lặp nghiên cứu box → `tai_lieu/VONG_LAP.md`.*
