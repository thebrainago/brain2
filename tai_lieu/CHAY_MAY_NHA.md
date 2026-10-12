# Chạy brain2 trên máy nhà (Windows 10)

Mục đích: chạy Seeker từ IP nhà (một số nguồn chặn IP máy chủ) và đo phí THẬT của XM từ EA demo.
Không lưu mật khẩu/token vào file nào trong repo. Không mua gì, không tham gia nhóm Telegram.

## 1. Cài một lần
1. Cài Python 3.11+ (python.org, tick "Add python.exe to PATH") và Git for Windows.
2. Mở **PowerShell** (không cần quyền admin):
```powershell
cd $HOME
git clone https://github.com/thebrainago/brain2.git
cd brain2
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # nếu báo lỗi ExecutionPolicy: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium  # chỉ cần nếu dùng nguồn trình duyệt
```
Gói `MetaTrader5` chỉ cài được trên Windows (đúng máy này). Nếu một gói tùy chọn lỗi (vd. `telethon`, `langchain`), có thể bỏ qua.

## 2. Cập nhật mã
```powershell
cd $HOME\brain2
git pull --rebase
.\.venv\Scripts\Activate.ps1
```

## 3. Chạy Seeker từ IP nhà
```powershell
python seeker_quet_nguon.py              # quét các nguồn đến hạn
python seeker_quet_nguon.py --ep         # quét lại tất cả, bỏ qua chu kỳ
python seeker_quet_nguon.py --chi ma1,ma2   # chỉ vài nguồn
```
Kết quả ghi vào thư mục dữ liệu Seeker trong repo (xem `TRANG_THAI.json`). Nguồn cần đăng nhập vẫn được đánh dấu, không tự đăng nhập.
Gửi kết quả về: `git add` thư mục kết quả rồi `git commit` + `git push` (không `--force`), hoặc nén lại gửi tay.

## 4. Đo phí thật XM từ EA demo
1. Cài EA theo `ea_demo/INSTALL_DEMO.md` trên tài khoản **DEMO** XM. EA ghi log vào
   `%APPDATA%\MetaQuotes\Terminal\<ID>\MQL5\Files\brain2_ibs_log.csv` và `brain2_muavu_log.csv`
   (MT5: File → Open Data Folder → MQL5\Files).
2. Sau vài ngày/tuần chạy:
```powershell
cd $HOME\brain2
.\.venv\Scripts\Activate.ps1
$F = "$env:APPDATA\MetaQuotes\Terminal\*\MQL5\Files"
python do_phi_xm.py (Get-ChildItem $F -Recurse -Filter "brain2_*_log.csv").FullName --ra reports\phi_xm_do_that.json
```
3. Kết quả: spread trung vị/p90 (giá và bps, theo giờ), trượt giá lúc vào lệnh, tổng swap, swap/lot/đêm, hoa hồng — theo từng mã.
   Đây là số đo trên demo (ước lượng phí thật), dùng để thay mô hình phí XM ×1,2 trong mô phỏng. Commit `reports\phi_xm_do_that.json` (không chứa thông tin tài khoản).
