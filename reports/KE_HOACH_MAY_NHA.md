# Kế hoạch máy nhà (Windows) — tối 30/10/2026 (Asia/Bangkok)

Máy box cloud **không** tới được server XM MT5 (TLS chặn). Máy nhà Windows có MT5 (XM) + dữ liệu thật `F:/TheBrain_luu/data` (~189 file) — dùng **toàn quyền tonight** theo các việc dưới đây.

## Cấm tuyệt đối

- Chỉ dùng **demo `345930355`**. **Không** đụng live `342418441`.
- **Không** giao dịch live, không bật AlgoTrading trên live.
- **Không** commit / push `config/tai_khoan.json`, mật khẩu, cookie, session.
- Không `git push` lên `main`; không force-push.

## Chuẩn bị (một lần, ~10–15 phút)

```powershell
# 1) Repo
cd F:\TheBrain_luu   # hoặc nơi clone brain2
# Nếu chưa có nhánh reverse-eng:
git fetch origin
git checkout seeker/tin-hieu-cong-khai
git pull origin seeker/tin-hieu-cong-khai

# 2) Python venv (nếu chưa)
# .\venv\Scripts\Activate.ps1
$env:BRAIN_DATA = "F:\TheBrain_luu\data"
$env:BRAIN_CACHE = "F:\TheBrain_luu\data_khung"
$env:BRAIN_LLM_PROVIDER = "hang_cho"
# KHÔNG set biến chứa mật khẩu vào shell history nếu có thể tránh

# 3) MT5: mở terminal, đăng nhập DEMO 345930355 only, kiểm tra Market Watch
```

## Việc A — Đồng bộ dữ liệu XM → box (ưu tiên cao, ~30–90 phút)

Mục tiêu: box có cùng tick/H1/nao.db để QUANTLAB chạy sát thật.

```powershell
# A1. Kiểm tra số file dữ liệu
(Get-ChildItem "F:\TheBrain_luu\data\*.parquet").Count
# Kỳ vọng ~189

# A2. Đóng gói (KHÔNG gồm tai_khoan.json / *.ex5 nếu chứa key)
$stamp = Get-Date -Format "yyyyMMdd_HHmm"
$zip = "F:\TheBrain_luu\gui_box\xm_data_$stamp.zip"
New-Item -ItemType Directory -Force -Path "F:\TheBrain_luu\gui_box" | Out-Null
# Chỉ parquet + nao.db (nếu có) — bỏ secrets
Compress-Archive -Path `
  (Get-ChildItem "F:\TheBrain_luu\data\*_H1.parquet"), `
  (Get-ChildItem "F:\TheBrain_luu\data\*_M15.parquet" -ErrorAction SilentlyContinue) `
  -DestinationPath $zip -Force
# Nếu nao.db nằm ngoài data:
# Compress-Archive -Update -Path "F:\TheBrain_luu\nao.db" -DestinationPath $zip

# A3. Gửi về box — chọn MỘT cách:
#   (i)  Push nhánh data (LFS hoặc release asset) — khuyến nghị:
#        git checkout -b data/xm-sync-$stamp
#        # copy parquet cần thiết vào data/ (đã gitignore — dùng GitHub Release thay vì commit)
#   (ii) Upload zip lên chỗ box đọc được (Drive/OneDrive) rồi báo path
#   (iii) SCP/rsync qua Tailscale/SSH (xem mục "Vận hành lâu dài")
Write-Host "ZIP: $zip — gửi file này cho box / gắn vào chat"
```

**Trả về box:** file zip (hoặc link), danh sách symbol có trong zip, kích thước, thời gian Asia/Bangkok.

**Runtime:** nén 189 parquet H1 thường 5–20 phút tùy đĩa; upload phụ thuộc mạng nhà.

## Việc B — MT5 Strategy Tester trên ứng viên QUANTLAB (demo only, ~2–6 giờ)

Chỉ demo `345930355`. Dùng pipeline sẵn:

```powershell
cd <repo-brain2>
$env:BRAIN_DATA = "F:\TheBrain_luu\data"

# B1. An toàn tester (đòn bẩy đúng format, xóa báo cáo cũ)
python -c "from mt5tools.an_toan_tester import dong_don_bay; print(dong_don_bay(30))"

# B2. Lấy hàng việc MT5 (nếu có)
# Get-Content reports\ong_dan\hang_cho_mt5.jsonl -Tail 20

# B3. Chạy tester song song / slot (chỉnh path MT5 cho máy nhà)
# Ví dụ pattern có sẵn:
#   powershell -File mt5tools\chay_song_song.ps1
#   powershell -File mt5tools\chay_mt5_slot.ps1
# Chỉ chạy top ứng viên QUANTLAB đã lọc (DD hướng ≤80%, ≥10%/năm trên Python) —
# xem reports/ong_dan/ và DANH_SACH_HE_DAT nếu có.

# B4. Sau khi xong: đóng gói báo cáo
$stamp = Get-Date -Format "yyyyMMdd_HHmm"
Compress-Archive -Path "reports\ong_dan\ket_qua_mt5\*" `
  -DestinationPath "F:\TheBrain_luu\gui_box\mt5_ket_qua_$stamp.zip" -Force
```

**Trả về box:** `mt5_ket_qua_*.zip` + vài dòng tóm tắt (EA, symbol, net, DD, số lệnh, đòn bẩy đọc lại từ báo cáo).

**Runtime:** mỗi backtest tick XM thường 10–40 phút; kế hoạch tối: 4–8 cấu hình top.

## Việc C — Collector tín hiệu công khai (nếu box bị chặn / cần MQL5 login) (~20–40 phút)

Trên nhánh `seeker/tin-hieu-cong-khai`:

```powershell
cd <repo-brain2>
$env:BRAIN_DATA = "F:\TheBrain_luu\data"
$env:BRAIN_LLM_PROVIDER = "hang_cho"

# C1. FXBlue (thường box đã làm được; máy nhà bổ sung user mới)
python -m nhan.thu_thap_tin_hieu_cong_khai --users example fluidtrader-demo memberforex42 673

# C2. Dịch ngược + xếp hang_cho (Grok Bot trên cloud sẽ dịch)
python tools\dich_nguoc_tin_hieu.py --users example fluidtrader-demo

# C3. MQL5: đăng nhập trình duyệt máy nhà → mở signal → Export CSV history
# Lưu vào: $env:BRAIN_DATA\tin_hieu_cong_khai\mql5_csv\<signal_id>\raw.csv
# Rồi:
# python -c "from nhan.thu_thap_tin_hieu_cong_khai import doc_csv_mql5_statement, luu_he; t=doc_csv_mql5_statement(r'F:\...\raw.csv', he_id='2361673'); luu_he('mql5_csv','2361673', t)"
# python tools\dich_nguoc_tin_hieu.py --chi-xep mql5_csv 2361673

# C4. Myfxbook / site Cloudflare: chỉ thử nếu cần; không vượt captcha bằng bot
```

**Trả về box:**

- Thư mục `data/tin_hieu_cong_khai/**` (zip), và/hoặc
- Các file mới trong `hang_cho_llm/cho/*.json` (commit trên nhánh feature **được** vì gitignore bỏ qua — gửi zip / copy vào chat),
- Log số hệ / số lệnh thu được.

## Việc D — Nặng: backtest hàng loạt + đồng bộ kết quả (~cả đêm nếu rảnh)

```powershell
# Dùng mt5tools\chay_lien_tuc.py / chay_song_song.ps1 với danh sách từ QUANTLAB
# Giới hạn: chỉ demo; dừng nếu đĩa C/D gần đầy (EVO đã cảnh).
# Mỗi sáng: zip ket_qua + git status (không commit secrets) rồi gửi box.
```

## Thứ tự đề xuất tonight

1. **A2–A3** (zip data) — ngay, để box có giá XM.
2. **C1–C2** (collector + hang_cho) — song song lúc nén.
3. **B** (tester top QUANTLAB) — phần lớn thời gian.
4. **C3** (MQL5 CSV thủ công 2–3 signal top từ báo cáo §2) nếu còn giờ.
5. Gửi zip + tóm tắt về chat / Drive.

## Vận hành lâu dài — cách đơn giản nhất để box điều khiển máy nhà

**Khuyến nghị: Tailscale + OpenSSH (Windows) + agent thư mục việc.**

| Cách | Việc user cần làm | Ưu | Nhược |
|---|---|---|---|
| **A. Tailscale + OpenSSH** (khuyến nghị) | 1) Cài Tailscale trên Windows, login cùng account. 2) Optional Features → OpenSSH Server. 3) `Start-Service sshd`. 4) Firewall allow Tailscale. 5) Gửi cho bot: Tailscale IP/hostname + user Windows (không gửi mật khẩu trong chat — dùng khóa SSH: `ssh-keygen` + đưa pubkey vào `C:\Users\<you>\.ssh\authorized_keys`). | Box SSH được, scp zip, chạy PowerShell từ xa | Cần bật máy / không sleep |
| **B. Thư mục việc git** | Tạo nhánh `may-nha/viec`: box commit `viec/*.json` (lệnh an toàn); Task Scheduler máy nhà mỗi 15 phút `git pull` + chạy runner + push kết quả lên `may-nha/ket-qua` | Không mở SSH | Chậm hơn; user cài Task Scheduler 1 lần |
| **C. Cursor Remote / remote agent** | User cài agent trên máy nhà trỏ cùng repo | Tiện nếu đã dùng Cursor | Phụ thuộc phiên user |

**User cần làm tối thiểu để “toàn quyền” thật sự:**

1. Bật **Tailscale** (hoặc ZeroTier) trên máy nhà + box cùng tailnet.
2. Bật **OpenSSH Server**, thêm **SSH public key** của box (bot sẽ sinh key trên box và đưa pubkey — user chỉ paste vào `authorized_keys`).
3. Đặt Windows **không sleep** khi cắm điện; MT5 demo auto-login (sẵn có trong XM).
4. Xác nhận path: repo, `F:\TheBrain_luu\data`, terminal64.exe.
5. Một lần chạy thử: `ssh user@may-nha "hostname"` từ box.

Sau khi user xong bước 1–5, báo lại hostname Tailscale — bot sẽ tự kéo việc A/B/C mà không cần ngồi máy.

## Checklist gửi lại box (copy)

```
[ ] zip xm_data_*.zip (parquet H1/M15, không secrets) — path/link:
[ ] zip mt5_ket_qua_*.zip — tóm tắt net/DD/lenh:
[ ] tin_hieu_cong_khai zip hoặc số hệ/lệnh:
[ ] hang_cho_llm/cho mới (nếu có):
[ ] Xác nhận chỉ dùng demo 345930355:
[ ] Tailscale hostname / SSH sẵn sàng? (y/n):
```
