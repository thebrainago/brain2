# VẬN HÀNH MÁY NHÀ — bàn giao cho brain2 (13/10/2026)

Người bàn giao: phiên Claude Code chạy trên máy nhà. Người nhận: bất kỳ model/phiên nào làm việc trên `thebrainago/brain2`.
Repo này **PUBLIC**. File này chỉ ghi **tên, nơi lưu, cách dùng** của tài khoản/mật khẩu — **không bao giờ ghi giá trị**.
Mâu thuẫn với `BAN_GIAO_GROK.md` hoặc luật user trong gói `ban_giao_brain2/01` → luật user thắng.

## 0. Việc phải làm NGAY (người, không phải model) — xem mục 7
Phát hiện 13/10/2026: repo public từng chứa mật khẩu dạng rõ + dữ liệu mật khẩu Chrome đã giải mã. Đã gỡ khỏi nhánh `main` của brain2
nhưng **vẫn còn trong lịch sử git** và trong repo `the-brain`. Coi mọi mật khẩu đó là **đã lộ**; chủ dự án cần đổi.

## 1. Máy nhà là gì
- Windows 10 Pro, user `DUNG`, máy Xeon 10 nhân / 20 luồng. **Chỉ để đầu tư, không có dữ liệu cá nhân**; chủ dự án cho AI toàn quyền cài đặt/admin trên máy này.
- Mã dự án hiện chạy ở `C:\Research SP500\lab` (clone của `the-brain`, nhánh `claude/autonomous-trading-system-rzzt7h`). brain2 clone riêng: xem `tai_lieu/CHAY_MAY_NHA.md`.
- Việc chỉ máy nhà làm được: MT5 demo + tester (Windows), trình duyệt đã đăng nhập, IP nhà (một số nguồn chặn IP máy chủ). Việc nặng/dài khác → cloud.
- **Điện**: máy tốn điện. Chỉ thị mới nhất (07/10/2026) thắng chỉ thị cũ (03/10, 06/10): máy rảnh thì được chạy 90–100% CPU, chạy song song nhiều bộ. Khi chủ dự án đang chơi game (LoL) thì giữ máy nhẹ, việc nặng giao cloud.
- Chơi LoL: Vanguard chặn do ổ RAM `R:` (OSFMount) → `CHOI_BAT.cmd` để chơi, `CHOI_TAT.cmd` để dừng lại (nằm trong lab của the-brain).

## 2. Luật bất biến
1. Chỉ xóa/ghi đè trong thư mục dự án đang làm. Không xóa hàng loạt, không format, không đụng thư mục hệ thống.
2. **Không lệnh giao dịch thật, không thao tác tài khoản live.** Backtest/demo/phân tích thoải mái. Tk **XM micro là tk THẬT (tk trắng, không nạp tiền)**: chỉ đọc spread/swap/phí cho mô hình chi phí, **không thao tác**. Chỉ dùng **XM DEMO** (máy chủ `XMGlobal-MT5 10`).
3. **Không đưa bí mật vào git/log/báo cáo/thư**: mật khẩu, API key, token, số điện thoại, mã xác minh, cookie, file Login Data/Local State của Chrome.
4. Không tự join nhóm Telegram, không tự đăng ký/follow diễn đàn, không mua gì. Việc đó chủ dự án duyệt trước.
5. Bị chặn bởi đăng nhập → **thử thao tác màn hình (mục 3) trước** khi ghi BLOCKED. Không bắt chủ dự án đăng nhập lại.
6. Làm liên tục đến xong; kẹt một nhánh thì ghi `BLOCKED.md` rồi sang nhánh khác. Sửa thất bại 3 lần → đổi hướng.
7. Số phải đo được; chưa đo ghi CHƯA ĐO ĐƯỢC; mô phỏng ghi rõ MÔ PHỎNG. Kết quả đẹp bất thường thì nghi trước (look-ahead, phí, spread, trượt giá).

## 3. BỘ QUY TẮC MÔ PHỎNG THAO TÁC TAY (trang cần đăng nhập)
Bối cảnh: bản sao hồ sơ Chrome (CDP 9224, `.browser_thebrain`) **luôn mất đăng nhập** Google/MQL5 sau khi tắt Chrome (Chrome 154 gắn cookie với thư mục gốc).
Cách duy nhất đã chạy ổn định (chốt 04/10/2026): **thao tác màn hình như người dùng trên Chrome THẬT**, không "vào như AI".

**Công cụ:** `may_nha/lay_export_man_hinh.py` (pyautogui + pyperclip). Trên máy nhà dùng venv `C:\Research SP500\lab\.venv` (đã cài pyautogui, pyperclip, playwright).
Chrome thật: `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe --profile-directory="Profile 3"` (đăng nhập sẵn: MQL5, Gmail thebrainago, Telegram Web).

Quy tắc:
1. **Dùng Chrome thật `Profile 3`.** Không CDP, không sao chép/junction hồ sơ, không mở hồ sơ gốc bằng cờ debug. Cửa sổ Profile 3 phải ở **trước** (script tự mở `about:blank` để đưa lên).
2. **Dán, không gõ.** `pyperclip.copy(url)` → `Ctrl+L` → `Ctrl+V` → `Enter`. Gõ phím làm rơi ký tự. Mỗi bước nghỉ ~0,4 giây.
3. **Nhịp ≥ 5,5 giây giữa hai lần** (MQL5 cấm IP sau ~50–150 request). Danh sách nhiều trang: đọc tổng số trang rồi đi **lần lượt**, 3–5 giây/trang, **lưu mốc "đã tới trang N"** để lần sau làm tiếp.
4. **Chờ tải có kiểm chứng:** chờ tối đa ~40 giây tệp vào `~/Downloads` và hết đuôi `.crdownload`; rồi **đọc đầu tệp** (CSV MQL5 phải bắt đầu `Time;Type`). Không đúng → xóa tệp, báo lỗi.
5. **Gặp HTML/403/429/Cloudflare/captcha → DỪNG NGAY**, ghi mã lỗi, không thử dồn, không vượt captcha. Ghi mốc dừng để làm tiếp sau.
6. **Nhìn bằng ảnh:** `pyautogui.screenshot(...)` rồi `Read` ảnh để biết màn hình đang ở đâu trước khi bấm. Không bấm mù.
7. **Telegram Web** (`web.telegram.org/k/`): tìm bằng ô Tìm kiếm bên trái, dán `@tên` (dán URL `#@tên` không ổn định). Nút Join nằm ở menu ⋮ (nhóm diễn đàn) hoặc thanh dưới (SUBSCRIBE/JOIN) — **chỉ bấm khi chủ dự án đã duyệt nhóm**. **Không bấm "Yes it's me / No"** ở cảnh báo thiết bị mới. Quy trình nhóm → EA: `QUY_TRINH_NHOM_TELEGRAM.md` (trong the-brain, `lab/tai_lieu`).
8. **Không chiếm chuột/bàn phím lâu khi chủ dự án đang dùng máy.** Việc dài chạy lúc máy rảnh. (pyautogui có fail-safe: đưa chuột vào góc trên trái để dừng khẩn.)
9. **Kết quả thô không vào git:** CSV về `du_lieu_cao/mql5/` (gitignore). Chỉ commit dữ liệu đã làm sạch, không chứa tài khoản.
10. Trình duyệt CDP 9224 (`may_nha/mo_trinh_duyet_ai.cmd`) **chỉ còn dùng đọc trang CÔNG KHAI**, theo chuyển hướng cùng tên miền + https.
11. Gmail của Claude connector là `anhanh1799` — **không phải** `thebrainago`. Thư của `thebrainago` (mã xác minh…) chỉ đọc được trong trình duyệt đã đăng nhập.

Lệnh mẫu (PowerShell, trên máy nhà):
```powershell
cd "C:\Research SP500\lab"
.\.venv\Scripts\python lay_export_man_hinh.py <id_tin_hieu_1> <id_tin_hieu_2>
```

## 4. WARP (Cloudflare) — chỉ khi cần
- Cài tại `C:\Program Files\Cloudflare\Cloudflare WARP\warp-cli.exe`, đã `registration new`.
- Lệnh: `warp-cli connect` / `warp-cli disconnect` / `warp-cli status`.
- **Khi nào bật:** Myfxbook (và có thể vài trang khác) bị nhà mạng chặn DNS (`ERR_NAME_NOT_RESOLVED`). `mql5.com` vào được không cần WARP.
- **Quy trình:** bật → làm đúng việc cần → **tắt ngay**. WARP đổi IP có thể **hủy phiên MQL5** đang đăng nhập. Không để bật khi chạy `lay_export_man_hinh.py`.
- Kiểm trước khi làm việc MQL5: `warp-cli status` phải là Disconnected. (Lúc bàn giao, 13/10/2026, trạng thái là **Connected** — tắt nếu sắp lấy dữ liệu MQL5.)

## 5. TÀI KHOẢN VÀ MẬT KHẨU ĐANG CÓ — chỉ liệt kê tên + nơi lưu, KHÔNG có giá trị
| Thứ | Nơi lưu | Dùng cho | Quyền |
|---|---|---|---|
| Sổ bí mật `E:\api.txt` | máy nhà, ngoài repo; chủ dự án thêm vào, Claude đọc/ghi thêm | mọi mật khẩu/API/danh tính mặc định | Đọc khi cần; **không in ra chat/log/git** |
| Mật khẩu "tài khoản sử dụng" (mặc định) | `E:\api.txt` | đăng ký/đăng nhập tài khoản mới theo danh tính mặc định | Dùng khi được giao |
| Danh tính mặc định (id + mật khẩu mặc định) | `E:\api.txt` | `tu_dang_ky.py` tạo tk diễn đàn | Chủ dự án duyệt trước khi đăng ký |
| XM **DEMO** (máy chủ `XMGlobal-MT5 10`: login + mật khẩu) | `E:\api.txt` | MT5 tester/demo, đo phí | **Được dùng** |
| XM micro (tk trắng, không nạp tiền) | ghi chú trong `E:\api.txt` | chỉ đọc spread/swap/phí | **Không thao tác** |
| AI Box API key (`sk-...`); base `https://api.ai-box.vn/v1` (OpenAI-compatible) và `https://api.ai-box.vn` (anthropic-messages) | `E:\api.txt` + biến môi trường User `AIBOX_API_KEY`, `SO_SANH_{QWEN,DEEPSEEK}_{KHOA,URL,MO_HINH}` | gọi LLM (qwen3.8-max-0902, qwen3.8-flash, kimi-k3, glm-5.3, ds/deepseek-flash) | Dùng; đặt `max_tokens` lớn vì mô hình suy luận ăn token suy luận |
| Lấy khóa AI Box mới | `https://home.ai-box.vn/console/tokens` | khi khóa hết hạn | — |
| Gmail `thebrainago@gmail.com` | đăng nhập sẵn trong Chrome `Profile 3` và trình duyệt CDP 9224 | đọc mã xác minh, "Sign in with Google" | Chỉ qua trình duyệt |
| MQL5 (user `Vanh1799`) | phiên Chrome `Profile 3` | export lịch sử lệnh tín hiệu | Thao tác màn hình (mục 3) |
| Myfxbook (qua "Sign in with Google") | phiên trình duyệt CDP 9224 | đọc thống kê tk công khai | Cần WARP (mục 4) |
| Telegram Web | phiên Chrome `Profile 3` (số của chủ dự án; **không ghi số/mã vào repo**) | theo dõi 3 nhóm EA đã duyệt | Chỉ đọc; không tự join |
| GitHub `thebrainago` | Git Credential Manager (`git-credential-manager.exe`) | push `the-brain`, `brain2` | Push thường, **không `--force`** |

**Cách một model lấy giá trị:** đọc `E:\api.txt` trên máy nhà (chỉ máy nhà có). Phiên cloud **không** có file này → hỏi chủ dự án qua kênh riêng, **không** dán vào repo/thư public.
Một số dòng trong `E:\api.txt` không có nhãn (XM demo, mật khẩu "tài khoản sử dụng") — đọc theo thứ tự dòng, đừng đoán.

## 6. Quy trình vận hành hằng ngày (máy nhà)
1. Đầu phiên: đọc `PROGRESS.md`, `BLOCKED.md`, `GHI_CHU_NANG_CAP_GROK.md`; `git pull --rebase`.
2. Chạy hàng đợi song song (the-brain/lab): N hộp thư `C:\Research SP500\cau_hop_thu_pN` + `lab\chay_song_song.ps1 -N <n>` → N tiến trình `b.py cau chay --lien-tuc --nghi 20` (biến `CAU_HOP_THU`, `CAU_TEN=nha-pN`, `CAU_KHA_NANG=windows,data`). Trạng thái 07/10: 18 bộ p1–p18 + m1–m3 + `nha`; sau khởi động lại, tác vụ `TheBrainSongSong` → `lab\khoi_dong_song_song.ps1`. Dừng: tệp `CAU_DUNG`.
3. Tester MT5: slot mặc định chạy đúng; slot `s1–s3` HỎNG. Hết slot → `CHƯA_ĐO_ĐƯỢC (TesterDangBan)`, **không phải ÂM** → giao lại bằng id mới. Cache Tester đã junction sang `D:\MT5cache`; dữ liệu trên ổ RAM `R:` (OSFMount, `ramdisk_khoi_dong.ps1`).
4. Tin "ĐẠT" chỉ khi đọc trạng thái bên trong (không chỉ mã thoát 0); "tester sống" = có dòng `Tester` trong log terminal.
5. Bot `.ex5` tải về: **không dịch ngược/bẻ khóa**; chỉ lập hồ sơ hành vi bằng tester.
6. Cuối mốc: commit ngắn, `git push` (không `--force`); cập nhật `GHI_CHU_NANG_CAP_GROK.md`; báo chủ dự án 3–8 dòng tiếng Việt: xong / chưa / kẹt / cần người làm gì.
7. Việc dài qua đêm → cloud, không để máy nhà chạy nền ngoài lịch được duyệt.

## 7. SỰ CỐ BẢO MẬT 13/10/2026 (cần chủ dự án)
Tìm thấy trong repo public (cả `brain2` và `the-brain`, có từ ~30/08/2026):
- `reports/chrome_extract/chrome_saved_logins.txt` — mật khẩu Chrome **đã giải mã** (332 dòng, nhiều trang: sàn, ví, nhà môi giới…), cùng các file `*_LoginData` và `Local_State`.
- Ba script thử đăng nhập MT5 có **mật khẩu tài khoản MT5 dạng rõ**; một test dùng chính mật khẩu đó làm dữ liệu mẫu.

Đã làm trên brain2 `main` (commit thường): gỡ các file trên, thay dữ liệu mẫu của test, thêm vào `.gitignore`. **Chưa làm được bằng model:**
1. **Đổi tất cả mật khẩu đã lưu trong Chrome và mật khẩu tk MT5 liên quan** (chỉ người làm được). Xóa khỏi git không thu hồi được thứ đã lộ.
2. Xóa lịch sử git (`git filter-repo`/BFG + force-push, hoặc xóa và tạo lại repo) cho `brain2` và `the-brain`: **không đảo ngược**, cần chủ dự án đồng ý vì đụng cả phiên cloud đang làm trên `the-brain`.
3. `the-brain` vẫn còn các file đó ở `main` và nhánh `claude/autonomous-trading-system-rzzt7h`; chưa gỡ ở đó.
4. Bật GitHub secret scanning/push protection; đừng bao giờ chạy lại việc trích mật khẩu Chrome vào thư mục trong repo.
