# VẬN HÀNH MÁY NHÀ — đọc trước khi đụng máy nhà

> Mọi bot mới đọc file này là chạy được máy nhà, Anh không phải hướng dẫn lại. Nhật ký phiên: [`nhat_ky/van_hanh_may_nha.md`](../nhat_ky/van_hanh_may_nha.md). Chi tiết thợ: [`README_THO_MT5.md`](README_THO_MT5.md).
> Cập nhật 2026-11-03 15:35 (giờ Việt Nam, đã kiểm trên máy thật). Trước đó: Lúc ghi, máy nhà đang offline nên chưa kiểm lại trên máy thật; số liệu lấy từ phiên chạy cùng ngày.

## 1. Máy
- Hostname **DESKTOP-05PNLGF** (tài liệu cũ ghi DESKTOP-SPQ7908 là máy cũ), user **DUNG**.
- 10 nhân / 20 luồng, 32 GB RAM. Ổ trống khoảng: C ~27 GB, D ~21 GB, E ~65 GB.
- Repo của người dùng: `C:\Users\DUNG\brain2`. Thợ chạy trong **clone riêng** `D:\brain2_tho` (có file `.tho_mt5_clone`, đã đặt git user.name/email riêng).
- Python 3.12.
- Shell của Grok Bot: machineId `92c57ab1-1431-4e07-ac24-3433da8604d6`.

## 2. Giới hạn Anh cho phép (BẮT BUỘC)
- CPU 70–80% là thoải mái. Giữ **RAM trống ≥ 6 GB**.
- **RAM là nút thắt cứng (đo 03/11/2026 15:00–15:30):** mỗi `metatester64` (real ticks, model đã quy định) ngốn **~2–5,4 GB** (tăng dần khi nạp tick, đỉnh ~5 GB sau vài phút); `terminal64` chỉ ~170 MB. 5 test cùng lúc → RAM trống **5–8 GB**, CPU **~24–31%** (mỗi test ≈ 1 luồng ≈ 5% CPU). 6 test → RAM trống < 3 GB; 13 test → 0,58–0,74 GB (cấm).
- ⇒ Trên 32 GB **tối đa ~5 test đồng thời**; **không thể đạt CPU 70–80%** mà vẫn giữ RAM ≥ 6 GB khi chạy real ticks. Muốn CPU cao hơn chỉ có: thêm RAM, hoặc việc lọc nhanh `tang=1` (model OHLC M1, ít RAM — chỉ dùng cho tầng lọc đã quy định, không thay real ticks ở tầng chấm).
- **Chặn RAM trong thợ (bắt buộc, commit 5cb956d2 → d8e1d3bf):** trước **mỗi lần phóng tester** (cả việc dở và k tiếp theo) thợ chờ tới khi RAM trống > `BRAIN_RAM_TRONG_MIN_GB` (mặc định 8; **máy nhà đặt 11** = 6 GB giữ lại + ~5 GB một test) **và** đã qua `BRAIN_RAM_GIAN_CACH` giây (mặc định 180) kể từ lần phóng gần nhất của bất kỳ thợ nào trên máy (tệp `%TEMP%\brain_tho_moc_nhan.txt`) — vì metatester nạp tick dần nên đo ngay sau khi phóng sẽ sai. Nhờ vậy có thể mở cả 13 slot: thợ thừa tự ngồi chờ, không làm tụt RAM.
- Thợ còn tự đặt `[Charts] MaxBars=50000` trong `config\common.ini` của slot (`BRAIN_MAX_BARS`) và xoá tệp `Tester\cache` cũ > 2 ngày của slot đó. Hai việc này giảm RAM terminal/ổ đĩa, **không** giảm đáng kể RAM metatester (tick data mới là phần lớn). Không rút ngắn khoảng ngày, không đổi model tick.
- Một test đơn chỉ dùng 1 agent tester cục bộ của slot; không cần tắt agent.
- Máy chạy 8–12 h/ngày. **Không tắt máy.**
- Không đụng Riot/League, `claude.exe`, bản XM chính `C:\Program Files\XM Global MT5`.
- `taskkill` chỉ dùng với **PID chính xác** (không kill theo tên).
- Git: **không** rebase, autostash, force push, `reset --hard`.
- **Không đọc `E:\api.txt`.** Không đưa mật khẩu vào git.

## 3. Chạy thợ
- Luôn đặt `PYTHONUTF8=1` và `PYTHONIOENCODING=utf-8` (không có sẽ lỗi cp1252).
- Không chạy `tho_mt5.py` trong `C:\Users\DUNG\brain2` (thợ từ chối). Dùng `D:\brain2_tho` hoặc `may_nha\CHAY_THO_MT5.cmd`.
- Từ PowerShell gọi qua `cmd` thì không redirect stdin được (lỗi `Input redirection is not supported` → vòng lặp khởi động lại 60 s) → **gọi python trực tiếp**.
- Khởi động tách phiên bằng `Start-Process`; log ở `C:\Users\DUNG\tho_song_song*.log`.

Ví dụ (PowerShell):
```powershell
$env:PYTHONUTF8='1'; $env:PYTHONIOENCODING='utf-8'
$env:BRAIN_SLOTS='E:\brain2_grok\mt5_slots\g1;E:\brain2_grok\mt5_slots\g2;E:\mt5_tester\p5'
$env:BRAIN_TI_LE_CPU='0.8'; $env:BRAIN_RAM_TRONG_MIN_GB='11'; $env:BRAIN_RAM_GIAN_CACH='180'
Start-Process python -ArgumentList 'may_nha\tho_mt5.py','--song-song','--tran','12' `
  -WorkingDirectory 'D:\brain2_tho' -WindowStyle Hidden `
  -RedirectStandardOutput 'C:\Users\DUNG\tho_song_song.log' -RedirectStandardError 'C:\Users\DUNG\tho_song_song_err.log'
```

Tham số / biến:
- `BRAIN_SLOTS`: danh sách slot, ngăn bởi `;`.
- `--song-song`: chạy nhiều slot cùng lúc.
- `--tran N` hoặc `BRAIN_TRAN_SONG_SONG` (mặc định 10): trần số slot song song.
- `BRAIN_TI_LE_CPU=0.8`: tỉ lệ CPU tối đa.
- `--den-gio HH:MM`: chạy tới giờ đó thì dừng. `--mot-lan`: chạy một việc rồi thoát.
- `--slot`, `--may`: chọn slot / tên máy. `--tinh-trang`: in trạng thái.
- Việc HONG được trả về `can_test` (tăng `lan_hong`); hỏng 3 lần mới vào `da_test`.

## 4. Slot MT5 portable
- Đã đăng nhập XM: `E:\brain2_grok\mt5_slots\g1` … `g12` và `E:\mt5_tester\p5`.
- Rỗng (chưa đăng nhập): `D:\mt5_tester\p1` (chỉ có Bases), `p3`, `p4`, `p6`, `C:\MT5slots\s3`.
- Một thư mục portable chỉ chạy **1 terminal**.
- Danh sách terminal: `%APPDATA%\MetaQuotes\Terminal\*\origin.txt`.
- Tạo slot mới = chép nguyên thư mục một slot đã đăng nhập.
- Muốn CPU cao hơn khi RAM giới hạn: tăng số agent tester mỗi slot thay vì thêm terminal.

## 5. Mã giao dịch XM
- Tài khoản trong slot dùng mã đuôi `#` (`GBPNZD#`, `GOLD.i#`), **không có** `*micro`.
- Thợ tự đổi micro → `#` (lot chia 100) và đọc journal `symbol ... not exist` để chạy lại.

## 6. Mạng
- Cloudflare WARP đã cài sẵn: `warp-cli connect`. MT5 vẫn nối XM bình thường qua WARP.
- Mạng nhà không WARP chặn Myfxbook / Forex Factory / forex-station / LiteFinance ở DNS/TLS.
- Có WARP: Forex Factory, forex-station, LiteFinance vào được; Myfxbook trả 403 Cloudflare (bỏ qua, **không vượt**); Exness social không nối được.

## 7. Việc cần Anh
- Demo EA Market: Anh phải tự bấm **Free Demo** trong tab Market của slot (đang có 33 việc chờ).

## 8. Theo dõi
- Routine canh 30 phút/lần: xem CPU, RAM trống, log thợ, hàng đợi; ghi vào `nhat_ky/van_hanh_may_nha.md`.
- Nếu RAM trống < 6 GB kéo dài: kiểm tra thợ có chạy code cũ (khởi động trước commit d8e1d3bf, không có chặn RAM) không; dừng đúng PID thợ + terminal + metatester của slot đó, việc dở nằm ở `dang_lam_<may>_<slot>` sẽ được thợ cùng tên chạy lại khi khởi động.
