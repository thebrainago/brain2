#Requires -Version 5.1
<#
.SYNOPSIS
  Chạy một mình qua đêm trên máy nhà (DESKTOP-05PNLGF): các bước 0-11 trong may_nha_toi_nay/GIAO_VIEC_CLAUDE.md.

.DESCRIPTION
  - Mỗi bước bọc try/catch: bước lỗi thì ghi NHAT_KY.md và chạy tiếp bước sau.
  - KHÔNG BAO GIỜ tắt máy, khởi động lại hay đăng xuất. Chỉ dừng tiến trình do chính script mở (theo PID).
  - Không đọc, không in khoá. Không đọc E:\api.txt. Bước 0 chỉ báo CÓ/KHÔNG.
  - Log chi tiết để ở D:\ hoặc E:\ (không làm phình ổ C). TEMP của tiến trình con cũng chuyển sang D:/E:.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File may_nha_toi_nay\chay_toi_nay.ps1
  powershell -ExecutionPolicy Bypass -File may_nha_toi_nay\chay_toi_nay.ps1 -Buoc "0,3,4"
  powershell -ExecutionPolicy Bypass -File may_nha_toi_nay\chay_toi_nay.ps1 -Buoc "5-8" -Den "06:30"
#>
[CmdletBinding()]
param(
    [string]$Buoc = "",                         # "0-11", "0,3,5", "3-6,8"; rỗng = tất cả
    [string]$Repo = $env:BRAIN_REPO,
    [string]$TheBrain = $env:THE_BRAIN_DIR,
    [string]$Python = $env:BRAIN_PY,
    [string]$Mt5Xm = $env:BRAIN_MT5_XM,
    [string]$Mt5Exness = $env:BRAIN_MT5_EXNESS,
    [string]$MetaEditor = $env:BRAIN_METAEDITOR,
    [string]$GoiZip = $env:BRAIN_GOI_ZIP,
    [string]$ThuMucLog = $env:BRAIN_LOG_DIR,
    [string]$Slots = $env:BRAIN_SLOTS,          # "D:\mt5_tester\p1;D:\mt5_tester\p2;..." - mặc định giống mt5tools/chay_lien_tuc.py
    [string]$Den = "07:00",                     # giờ dừng hàng MT5 (bước 7)
    [int]$GioiHanThu = 20,                      # bước 5: số thẻ dịch thử
    [int]$LuongLlm = 4,
    [int]$ToiDa = 30,                           # bước 6: số thẻ tối ưu mỗi lần
    [switch]$ChoDichXong,                       # bước 5: chờ dịch nền xong rồi mới sang bước 6
    [switch]$KhongPush
)

$ErrorActionPreference = "Continue"
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

# ---------------------------------------------------------------- đường dẫn
if (-not $Repo) { $Repo = Split-Path -Parent $PSScriptRoot }
$Repo = (Resolve-Path $Repo).Path
if (-not $TheBrain) { $TheBrain = "C:\Research SP500\lab" }
$ThuMucViec = Join-Path $Repo "may_nha_toi_nay"
$NhatKy = Join-Path $ThuMucViec "NHAT_KY.md"
$KetQuaSang = Join-Path $ThuMucViec "KET_QUA_SANG.md"
$Ngay = Get-Date -Format "yyyyMMdd"

function Noi([string]$a, [string]$b) { return [System.IO.Path]::Combine($a, $b) }   # không lỗi khi ổ chưa có

function OTrong([string]$o) {
    try { $d = Get-PSDrive -Name $o.Substring(0, 1) -ErrorAction Stop; return [math]::Round($d.Free / 1GB, 1) } catch { return -1 }
}
# ổ dữ liệu: D: nếu trống > 20 GB, rồi E:
$ODuLieu = $null
foreach ($o in @("D:\", "E:\")) { if ((Test-Path $o) -and ((OTrong $o) -gt 20)) { $ODuLieu = $o; break } }
if (-not $ODuLieu) { foreach ($o in @("D:\", "E:\")) { if (Test-Path $o) { $ODuLieu = $o; break } } }
if (-not $ThuMucLog) {
    if ($ODuLieu) { $ThuMucLog = Join-Path $ODuLieu "brain2_log\toi_nay_$Ngay" } else { $ThuMucLog = Join-Path $ThuMucViec "log" }
}
New-Item -ItemType Directory -Force -Path $ThuMucLog | Out-Null
$LogChung = Join-Path $ThuMucLog "chay_toi_nay.log"
if ($ODuLieu) {
    $TmpCon = Join-Path $ODuLieu "brain2_tmp"
    New-Item -ItemType Directory -Force -Path $TmpCon | Out-Null
    $env:TEMP = $TmpCon; $env:TMP = $TmpCon      # tiến trình con không ghi tạm vào C:
}
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$KetQua = [ordered]@{}

function Ghi([string]$s) {
    $d = "- " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + " " + $s
    Write-Host $d
    try { Add-Content -Path $NhatKy -Value $d -Encoding UTF8 } catch { }
    try { Add-Content -Path $LogChung -Value $d -Encoding UTF8 } catch { }
}

function TimPython {
    if ($Python -and (Test-Path $Python)) { return $Python }
    $ung = @(
        (Join-Path $Repo ".venv\Scripts\python.exe"),
        $(if ($env:LOCALAPPDATA) { Join-Path $env:LOCALAPPDATA "Python\pythoncore-3.14-64\python.exe" }),
        "C:\Users\SV STORE\AppData\Local\Python\pythoncore-3.14-64\python.exe",
        (Join-Path $TheBrain ".venv\Scripts\python.exe")
    )
    foreach ($p in $ung) { if ($p -and (Test-Path $p)) { return $p } }
    $g = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($g) { return $g.Source }
    return $null
}

function TimTerminal([string]$mau, [string]$uuTien) {
    $ds = @()
    foreach ($g in @("D:\mt5_tester", "E:\mt5_tester", "C:\Program Files", "D:\", "E:\")) {
        if (Test-Path $g) {
            $ds += Get-ChildItem -Path $g -Directory -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -match $mau -and (Test-Path (Join-Path $_.FullName "terminal64.exe")) } |
                ForEach-Object { Join-Path $_.FullName "terminal64.exe" }
        }
    }
    $u = $ds | Where-Object { $_ -match $uuTien } | Select-Object -First 1
    if ($u) { return $u }
    return ($ds | Select-Object -First 1)
}

$Py = TimPython
if (-not $Mt5Xm) { $Mt5Xm = TimTerminal "(?i)xm" "(?i)xm_micro" }
if (-not $Mt5Exness) { $Mt5Exness = TimTerminal "(?i)exness" "(?i)exness_cent" }
if ($Slots) { $DsSlot = $Slots.Split(";") | Where-Object { $_ } }
else { $DsSlot = @("D:\mt5_tester\p1", "D:\mt5_tester\p2", "E:\mt5_tester\p3", "E:\mt5_tester\p4") }

# ---------------------------------------------------------------- tiện ích chạy
function TrichDoi([string]$a) {
    if ($a -match '[\s"]') { return '"' + ($a -replace '"', '\"') + '"' }
    return $a
}

function ChayCon {
    # Chạy một chương trình con, chờ tối đa $phut phút (0 = chờ hết), log ra $ThuMucLog\<ten>.out/.err
    param([string]$exe, [string[]]$thamSo, [string]$ten, [int]$phut = 0, [string]$uuTien = "BelowNormal", [string]$cwd = $Repo)
    $out = Join-Path $ThuMucLog "$ten.out.txt"; $err = Join-Path $ThuMucLog "$ten.err.txt"
    $chuoi = ($thamSo | ForEach-Object { TrichDoi $_ }) -join " "
    Ghi ("  chạy: " + (Split-Path -Leaf $exe) + " " + $chuoi)
    $p = Start-Process -FilePath $exe -ArgumentList $chuoi -WorkingDirectory $cwd -NoNewWindow -PassThru `
        -RedirectStandardOutput $out -RedirectStandardError $err
    $null = $p.Handle                                  # giữ handle để đọc được ExitCode
    try { $p.PriorityClass = $uuTien } catch { }
    if ($phut -gt 0) {
        if (-not $p.WaitForExit($phut * 60 * 1000)) {
            Ghi "  QUÁ GIỜ ($phut phút) - dừng PID $($p.Id) (chỉ tiến trình này)"
            try { Stop-Process -Id $p.Id -Force -ErrorAction Stop } catch { }
            return -999
        }
    } else { $p.WaitForExit() }
    $p.WaitForExit()
    return $p.ExitCode
}

function ChayPy([string[]]$thamSo, [string]$ten, [int]$phut = 0, [string]$uuTien = "BelowNormal") {
    if (-not $Py) { throw "không tìm thấy python (đặt BRAIN_PY)" }
    $rc = ChayCon -exe $Py -thamSo $thamSo -ten $ten -phut $phut -uuTien $uuTien
    $out = Join-Path $ThuMucLog "$ten.out.txt"
    if (Test-Path $out) { Get-Content $out -Tail 6 -Encoding UTF8 | ForEach-Object { Ghi ("    | " + $_) } }
    $err = Join-Path $ThuMucLog "$ten.err.txt"
    if ($rc -ne 0 -and (Test-Path $err)) { Get-Content $err -Tail 6 -Encoding UTF8 | ForEach-Object { Ghi ("    ! " + $_) } }
    return $rc
}

function ChayNen([string]$exe, [string[]]$thamSo, [string]$ten, [string]$uuTien = "Idle") {
    # Tiến trình nền: không chờ. Ghi PID ra $ThuMucLog\pid_<ten>.txt để dừng đúng PID.
    $fp = Join-Path $ThuMucLog "pid_$ten.txt"
    if (Test-Path $fp) {
        $cu = Get-Content $fp -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($cu -and (Get-Process -Id ([int]$cu) -ErrorAction SilentlyContinue)) { Ghi "  $ten đã chạy nền (PID $cu) - không mở thêm"; return }
    }
    $out = Join-Path $ThuMucLog "$ten.out.txt"; $err = Join-Path $ThuMucLog "$ten.err.txt"
    $chuoi = ($thamSo | ForEach-Object { TrichDoi $_ }) -join " "
    $an = @{}
    if ($PSVersionTable.PSEdition -eq "Desktop" -or $IsWindows) { $an["WindowStyle"] = "Hidden" } else { $an["NoNewWindow"] = $true }
    $p = Start-Process -FilePath $exe -ArgumentList $chuoi -WorkingDirectory $Repo -PassThru @an `
        -RedirectStandardOutput $out -RedirectStandardError $err
    try { $p.PriorityClass = $uuTien } catch { }
    Set-Content -Path $fp -Value $p.Id
    Ghi "  nền: $ten PID $($p.Id) (ưu tiên $uuTien) - dừng bằng: Stop-Process -Id $($p.Id)"
}

$Game = @("valorant.exe", "valorant-win64-shipping.exe", "leagueclient.exe", "league of legends.exe", "cs2.exe", "csgo.exe",
    "dota2.exe", "fortniteclient-win64-shipping.exe", "gta5.exe", "pubg.exe", "tslgame.exe", "r5apex.exe", "overwatch.exe",
    "eldenring.exe", "cyberpunk2077.exe", "genshinimpact.exe", "starrail.exe", "rocketleague.exe", "fc24.exe", "fc25.exe",
    "steam.exe")
try {
    # dùng danh sách game của mt5tools/dieu_phoi_song_song.py nếu đọc được
    if ($Py) {
        $g2 = & $Py -c "import sys; sys.path.insert(0,'mt5tools'); import dieu_phoi_song_song as D; print(chr(10).join(sorted(D.GAME)))" 2>$null
        if ($LASTEXITCODE -eq 0 -and $g2) { $Game = @($g2 | Where-Object { $_ -and $_ -ne "steam.exe" }) }
    }
} catch { }

function DangChoiGame {
    $ten = Get-Process -ErrorAction SilentlyContinue | ForEach-Object { ($_.ProcessName + ".exe").ToLower() }
    foreach ($g in $Game) { if ($ten -contains $g.ToLower()) { return $g } }
    return $null
}

function ChoGame([int]$toiDaPhut = 120) {
    # Chủ dự án đang chơi game -> chờ (mỗi 5 phút xem lại), tối đa $toiDaPhut rồi chạy tiếp ở mức ưu tiên thấp
    $g = DangChoiGame
    if (-not $g) { return }
    Ghi "  đang chơi game ($g) - tạm chờ, giảm tải"
    $bd = Get-Date
    while ((DangChoiGame) -and (((Get-Date) - $bd).TotalMinutes -lt $toiDaPhut)) { Start-Sleep -Seconds 300 }
    Ghi "  hết chờ game sau $([int]((Get-Date) - $bd).TotalMinutes) phút"
}

function DocServer([string]$thuMucTerminal) {
    # Chỉ đọc dòng Server= trong config\common.ini (không đọc Login / mật khẩu)
    $f = Noi $thuMucTerminal "config\common.ini"
    if (-not (Test-Path $f)) { return "" }
    foreach ($enc in @("Unicode", "UTF8", "Default")) {
        try {
            $d = Get-Content $f -Encoding $enc -ErrorAction Stop | Where-Object { $_ -match "^\s*Server\s*=" } | Select-Object -First 1
            if ($d) { return ($d -split "=", 2)[1].Trim() }
        } catch { }
    }
    return ""
}

# ---------------------------------------------------------------- chọn bước
# 19/10/2026 (Claude): 7 (hàng MT5) mở NỀN ngay sau 4 (cần EA đã biên dịch) để tester chạy cả đêm song song với dịch/
# tối ưu Python; trước đây 7 chỉ bắt đầu sau 5+6 (tới 6 giờ). 8 chờ hàng MT5 kết thúc (giờ $Den + 20 phút) rồi mới đọc.
$ThuTu = @(0, 1, 2, 3, 4, 7, 5, 6, 9, 10, 8, 11)
function PhanTichBuoc([string]$s) {
    if (-not $s) { return $ThuTu }
    $chon = @()
    foreach ($m in $s.Split(",")) {
        $m = $m.Trim()
        if ($m -match "^(\d+)-(\d+)$") { $chon += [int]$Matches[1]..[int]$Matches[2] }
        elseif ($m -match "^\d+$") { $chon += [int]$m }
    }
    return @($ThuTu | Where-Object { $chon -contains $_ })
}
$Chon = PhanTichBuoc $Buoc

function Buoc([int]$so, [string]$ten, [scriptblock]$viec) {
    if ($Chon -notcontains $so) { return }
    Ghi "**Bước $so - $ten**: BẮT ĐẦU"
    $bd = Get-Date
    try {
        $r = & $viec
        if (-not $r) { $r = "XONG" }
        $KetQua["$so"] = "$ten | $r | $([int]((Get-Date) - $bd).TotalMinutes) phút"
        Ghi "**Bước $so**: $r"
    } catch {
        $KetQua["$so"] = "$ten | LỖI: $($_.Exception.Message) | $([int]((Get-Date) - $bd).TotalMinutes) phút"
        Ghi "**Bước $so**: LỖI - $($_.Exception.Message) (chạy tiếp bước sau)"
    }
}

# ---------------------------------------------------------------- mở đầu
if (-not (Test-Path $NhatKy)) { Set-Content -Path $NhatKy -Value "# Nhật ký máy nhà tối nay" -Encoding UTF8 }
Add-Content -Path $NhatKy -Value "" -Encoding UTF8
Ghi "## Phiên chay_toi_nay.ps1 trên $env:COMPUTERNAME - bước: $($Chon -join ',')"
Ghi "repo=$Repo | python=$Py | log=$ThuMucLog | XM=$Mt5Xm | Exness=$Mt5Exness | dừng MT5 lúc $Den"

# ---------------------------------------------------------------- 0. kiểm máy
Buoc 0 "Kiểm máy" {
    foreach ($o in @("C:\", "D:\", "E:\")) { if (Test-Path $o) { Ghi "  ổ $o trống $(OTrong $o) GB" } }
    if ((OTrong "C:\") -ge 0 -and (OTrong "C:\") -lt 15) { Ghi "  CẢNH BÁO: ổ C còn dưới 15 GB - không ghi gì thêm vào C" }
    if (-not $Py) { throw "không tìm thấy python" }
    $ts = @("may_nha_toi_nay/kiem_may.py", "--mt5")
    foreach ($t in @($Mt5Xm, $Mt5Exness)) { if ($t) { $ts += @("--terminal", $t) } }
    $rc = ChayCon -exe $Py -thamSo $ts -ten "b0_kiem_may" -phut 10
    if ($rc -ne 0) { throw "kiem_may.py rc=$rc - xem $ThuMucLog\b0_kiem_may.err.txt" }
    $f = Join-Path $ThuMucLog "b0_kiem_may.out.txt"
    $j = Get-Content $f -Raw -Encoding UTF8 | ConvertFrom-Json
    Ghi "  python $($j.python) | gói: $(($j.goi.PSObject.Properties | ForEach-Object { $_.Name + '=' + $_.Value }) -join ', ')"
    Ghi "  khoá LLM: AIBOX_API_KEY=$($j.khoa_llm.AIBOX_API_KEY), cc-switch aibox=$($j.khoa_llm.cc_switch_aibox), proxy=$($j.khoa_llm.BRAIN_LLM_PROXY)"
    foreach ($t in $j.terminal) {
        $tk = $t.tai_khoan
        if ($tk -and $tk.server) { Ghi "  MT5 $($t.duong_dan): server=$($tk.server), hedging=$($tk.hedging), demo=$($tk.demo), tiền=$($tk.tien)" }
        else { Ghi "  MT5 $($t.duong_dan): server cuối=$($t.server_cuoi) | $($tk.loi)" }
    }
    foreach ($s in $DsSlot) {
        if (Test-Path (Noi $s "terminal64.exe")) { Ghi "  slot tester $s : server=$(DocServer $s)" } else { Ghi "  slot tester $s : KHÔNG CÓ" }
    }
    if ($j.game_dang_chay.Count -gt 0) { Ghi "  game đang chạy: $($j.game_dang_chay -join ', ')" }
    "XONG (rc=$rc)"
}

# ---------------------------------------------------------------- 1. git pull
Buoc 1 "git pull brain2 + the-brain" {
    $r = @()
    $rc = ChayCon -exe "git" -thamSo @("-C", $Repo, "pull", "--rebase") -ten "b1_pull_brain2" -phut 15
    $r += "brain2 rc=$rc"
    if (Test-Path (Join-Path $TheBrain ".git")) {
        $rc2 = ChayCon -exe "git" -thamSo @("-C", $TheBrain, "pull", "--rebase") -ten "b1_pull_the_brain" -phut 15
        $r += "the-brain rc=$rc2"
    } else { $r += "the-brain: không thấy $TheBrain" }
    Get-Content (Join-Path $ThuMucLog "b1_pull_brain2.err.txt") -Tail 3 -ErrorAction SilentlyContinue | ForEach-Object { Ghi "    | $_" }
    ($r -join "; ")
}

# ---------------------------------------------------------------- 2. gói zip
Buoc 2 "Giải nén gói zip" {
    $z = $null
    if ($GoiZip -and (Test-Path $GoiZip)) { $z = $GoiZip }
    if (-not $z) {
        foreach ($g in @("D:\brain2_goi", "E:\brain2_goi", "$env:USERPROFILE\Downloads", (Join-Path $Repo "may_nha_toi_nay"))) {
            if ($g -and (Test-Path $g)) {
                $c = Get-ChildItem -Path $g -Filter "goi_ea_ngoai_*.zip" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
                if ($c) { $z = $c.FullName; break }
            }
        }
    }
    if (-not $z) { throw "không thấy goi_ea_ngoai_*.zip ở D:\brain2_goi, E:\brain2_goi, Downloads - CHƯA CHẠY ĐƯỢC (Grok Bot sẽ chép vào D:\brain2_goi khi máy nhà kết nối)" }
    Ghi "  gói: $z ($([math]::Round((Get-Item $z).Length / 1MB, 1)) MB)"
    $db = Join-Path $Repo "data\ong_dan\trang_thai.sqlite"
    if (Test-Path $db) {
        $bk = Join-Path $(if ($ODuLieu) { $ODuLieu } else { $ThuMucLog }) "brain2_backup"
        New-Item -ItemType Directory -Force -Path $bk | Out-Null
        $dich = Join-Path $bk ("trang_thai_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".sqlite")
        Copy-Item $db $dich -Force
        Ghi "  đã sao lưu trang_thai.sqlite -> $dich"
    }
    # giải nén ra thư mục tạm trên D:/E:, rồi chỉ chép cây data\ vào repo (không đè file mã nguồn)
    $tam = Join-Path $ThuMucLog "giai_nen"
    if (Test-Path $tam) { Remove-Item $tam -Recurse -Force }
    Expand-Archive -Path $z -DestinationPath $tam -Force
    if (Test-Path (Join-Path $tam "data")) {
        Copy-Item -Path (Join-Path $tam "data\*") -Destination (Join-Path $Repo "data") -Recurse -Force
    } else { throw "gói không có thư mục data\" }
    foreach ($f in @("HUONG_DAN.md", "MANIFEST.json")) {
        if (Test-Path (Join-Path $tam $f)) { Copy-Item (Join-Path $tam $f) (Join-Path $ThuMucLog $f) -Force }
    }
    $n = (Get-ChildItem -Path (Join-Path $tam "data") -Recurse -File).Count
    Remove-Item $tam -Recurse -Force
    "XONG: $n tệp vào data\ (gói KHÔNG được vào git)"
}

# ---------------------------------------------------------------- 3. đo phí sàn
Buoc 3 "Đo phí sàn thật (Exness cent, XM micro)" {
    ChoGame
    $r = @()
    foreach ($cap in @(@("Exness", $Mt5Exness), @("XM", $Mt5Xm))) {
        if (-not $cap[1]) { $r += "$($cap[0]): CHƯA ĐO ĐƯỢC (không thấy terminal)"; continue }
        $rc = ChayPy @("mt5tools/do_phi_san.py", $cap[1], "--ngay-tick", "14", "--tp-gia", "5", "--ngay-lich-su", "365") "b3_phi_$($cap[0])" 120
        if ($rc -eq 0) { $r += "$($cap[0]): ĐO xong" } else { $r += "$($cap[0]): CHƯA ĐO ĐƯỢC (rc=$rc - terminal chưa đăng nhập?)" }
    }
    Get-ChildItem (Join-Path $Repo "reports\phi_san") -Directory -ErrorAction SilentlyContinue | ForEach-Object { Ghi "  reports\phi_san\$($_.Name)" }
    ($r -join "; ")
}

# ---------------------------------------------------------------- 4. biên dịch EA
Buoc 4 "Biên dịch ea_demo\BRAIN_XuLiLenh.mq5" {
    ChoGame
    $nguon = Join-Path $Repo "ea_demo\BRAIN_XuLiLenh.mq5"
    if (-not (Test-Path $nguon)) { throw "không thấy $nguon" }
    $r = @()
    foreach ($s in $DsSlot) {
        $mql = Noi $s "MQL5"
        if (-not (Test-Path $mql)) { $r += "${s}: không có MQL5"; continue }
        $me = Noi $s "metaeditor64.exe"
        if (-not (Test-Path $me)) { $me = $MetaEditor }
        if (-not $me -or -not (Test-Path $me)) { $r += "${s}: không thấy metaeditor64.exe"; continue }
        $dichTm = Noi $mql "Experts\BRAIN"
        New-Item -ItemType Directory -Force -Path $dichTm | Out-Null
        Copy-Item $nguon $dichTm -Force
        $ex5 = Noi $dichTm "BRAIN_XuLiLenh.ex5"
        $truoc = $(if (Test-Path $ex5) { (Get-Item $ex5).LastWriteTime } else { [datetime]::MinValue })
        $logMe = Noi $dichTm "BRAIN_XuLiLenh.log"
        # BẪY: đường dẫn tuyệt đối -> rc=0 mà không làm gì. Phải dùng đường dẫn tương đối với cwd = MQL5.
        $ts = @("/compile:Experts\BRAIN\BRAIN_XuLiLenh.mq5", "/log:Experts\BRAIN\BRAIN_XuLiLenh.log")
        if ($me -ne (Noi $s "metaeditor64.exe")) { $ts += "/inc:$mql" } else { $ts += "/portable" }   # slot portable: thư viện chuẩn (Trade.mqh) của chính slot
        $null = ChayCon -exe $me -thamSo $ts -ten ("b4_bien_dich_" + (Split-Path -Leaf $s)) -phut 5 -cwd $mql
        # MetaEditor sinh tiến trình con rồi THOÁT TRƯỚC khi dịch xong (đo 06/09, chay_tester_kho.bien_dich): chờ .ex5 mới tối đa 120 s
        for ($i = 0; $i -lt 60; $i++) {
            if ((Test-Path $ex5) -and ((Get-Item $ex5).LastWriteTime -gt $truoc)) { break }
            Start-Sleep -Seconds 2
        }
        Start-Sleep -Seconds 2                                  # log ghi sau .ex5
        $loi = "?"
        if (Test-Path $logMe) {
            $dong = Get-Content $logMe -Encoding Unicode -ErrorAction SilentlyContinue
            if (-not $dong) { $dong = Get-Content $logMe -ErrorAction SilentlyContinue }
            Copy-Item $logMe (Join-Path $ThuMucLog ("b4_" + (Split-Path -Leaf $s) + "_metaeditor.log")) -Force
            $kq = $dong | Where-Object { $_ -match "(\d+) errors?, (\d+) warnings?" } | Select-Object -Last 1
            if ($kq) { $loi = $kq.Trim() }
            $dong | Where-Object { $_ -match ": error " } | Select-Object -First 15 | ForEach-Object { Ghi "    ! $_" }
        }
        $moi = (Test-Path $ex5) -and ((Get-Item $ex5).LastWriteTime -gt $truoc)
        $r += "$(Split-Path -Leaf $s): ex5 mới=$moi ($loi)"
    }
    ($r -join "; ")
}

# ---------------------------------------------------------------- 7. hàng MT5 (NỀN, chạy ngay sau bước 4)
Buoc 7 "Hàng MT5 nền tới $Den (mỗi slot lấy việc đúng sàn nó đăng nhập)" {
    $dang = Get-Process -Name terminal64, metatester64 -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*mt5_tester*" }
    if ($dang) { return "BỎ QUA: đã có phiên khác dùng tester (PID $(($dang | ForEach-Object { $_.Id }) -join ',')) - một phiên một lúc" }
    $san = @{}
    foreach ($s in $DsSlot) {
        if (-not (Test-Path (Noi $s "terminal64.exe"))) { continue }
        $sv = DocServer $s
        if ($sv -match "(?i)xm") { $san[$s] = "XM" } elseif ($sv -match "(?i)exness") { $san[$s] = "Exness" } else { $san[$s] = "?" }
        Ghi "  slot $s -> $($san[$s]) ($sv)"
    }
    $co = @($san.Values | Where-Object { $_ -ne "?" } | Sort-Object -Unique)
    if ($co.Count -eq 0) { return "CHƯA ĐO ĐƯỢC: không slot nào đăng nhập XM/Exness - chủ dự án cần đăng nhập slot" }
    if (@($san.Values | Where-Object { $_ -eq "?" }).Count -gt 0) { Ghi "  CẢNH BÁO: có slot chưa đăng nhập XM/Exness - slot đó chỉ chạy việc cũ V24" }
    # 19/10/2026: KHÔNG chia đôi đêm XM rồi Exness nữa. chay_lien_tuc.py đọc Server= của từng slot và lấy việc đúng sàn
    # (sinh_viec.lay_viec(san=...)), nên hai sàn chạy song song cả đêm; không xoá tick giữa đêm.
    Remove-Item Env:\BRAIN_SAN_TESTER -ErrorAction SilentlyContinue
    $env:BRAIN_UU_TIEN_CSV = "1"
    ChayNen $Py @("mt5tools/chay_lien_tuc.py", "--den", $Den) "mt5" "BelowNormal"
    "nền tới $Den (+20 phút gia hạn) - sàn: $($co -join ', ')"
}

# ---------------------------------------------------------------- 5. dịch bằng LLM
Buoc 5 "dich_llm thử $GioiHanThu thẻ rồi chạy nền hết" {
    ChoGame
    $rc = ChayPy @("ong_dan.py", "dich_llm", "--gioi_han", "$GioiHanThu", "--luong", "$LuongLlm") "b5_dich_thu" 120
    $out = Get-Content (Join-Path $ThuMucLog "b5_dich_thu.out.txt") -Raw -Encoding UTF8
    if ($out -match "CHUA CHAY DUOC") { return "CHƯA CHẠY ĐƯỢC: máy này không có khoá (AIBOX_API_KEY / cc-switch)" }
    # 19/10/2026: lượt thử quá giờ / lỗi vẫn mở dịch nền (cache theo sha256 nên không mất công đã gọi); chỉ dừng khi
    # chắc chắn LLM hỏng hết (bên dưới) hoặc không có khoá (bên trên)
    if ($rc -ne 0) { Ghi "  dịch thử rc=$rc - vẫn mở dịch nền (xem b5_dich_thu.err.txt)" }
    $dem = $null
    $m = [regex]::Matches($out, '(?ms)^\{\s*$.*?^\}\s*$')
    if ($m.Count -gt 0) { try { $dem = $m[$m.Count - 1].Value | ConvertFrom-Json } catch { } }
    if ($dem) {
        Ghi "  thử: chờ=$($dem.cho) làm=$($dem.lam) đạt=$($dem.dat) hỏng=$($dem.hong) lỗi_llm=$($dem.loi_llm) gọi mới=$($dem.goi_moi) cache=$($dem.tu_cache)"
        if ($dem.lam -eq 0 -and $dem.loi_llm -gt 0) { return "DỪNG: $($dem.loi_llm) lỗi LLM, 0 thẻ làm được - xem reports\ong_dan\DICH_LLM.md" }
    }
    $nen = Join-Path $ThuMucViec "dich_llm_nen.ps1"
    $psExe = (Get-Process -Id $PID).Path                  # cùng PowerShell đang chạy script này
    if (-not $psExe) { $psExe = "powershell.exe" }
    ChayNen $psExe @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $nen, "-Repo", $Repo, "-Python", $Py,
        "-ThuMucLog", $ThuMucLog, "-Luong", "$LuongLlm", "-ToiDaOngDan", "$ToiDa", "-Den", $Den) "dich_llm_nen" "BelowNormal"
    if ($ChoDichXong) {
        $xong = Join-Path $ThuMucLog "dich_llm_nen.xong.txt"
        while (-not (Test-Path $xong)) { Start-Sleep -Seconds 120 }
        return "XONG thử + nền: $(Get-Content $xong -Raw)"
    }
    "thử xong, phần còn lại chạy nền (chạy lại được, có cache)"
}

# ---------------------------------------------------------------- 6. ống dẫn
Buoc 6 "ong_dan.py chay" {
    ChoGame
    $khoa = Join-Path $ThuMucLog "ong_dan_chay.lock"           # chung với dich_llm_nen.ps1 (nó chạy ong_dan sau mỗi lượt dịch)
    while (Test-Path $khoa) {
        $pk = Get-Content $khoa -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not ($pk -and (Get-Process -Id ([int]$pk) -ErrorAction SilentlyContinue))) { Remove-Item $khoa -Force; break }
        Start-Sleep -Seconds 60
    }
    Set-Content $khoa $PID
    try { $rc = ChayPy @("ong_dan.py", "chay", "--toi-da", "$ToiDa") "b6_chay" 240 } finally { Remove-Item $khoa -Force -ErrorAction SilentlyContinue }
    if ($rc -ne 0) { throw "ong_dan chay rc=$rc" }
    "XONG (xem reports\ong_dan\TRANG_THAI.md)"
}

# ---------------------------------------------------------------- 9. Dukascopy nền
Buoc 9 "Tải Dukascopy nền (ổ D/E, ưu tiên thấp)" {
    if (-not $ODuLieu) { throw "không có ổ D:/E: - không tải vào C:" }
    $env:DU_LIEU_CHUAN = Join-Path $ODuLieu "du_lieu_chuan"
    New-Item -ItemType Directory -Force -Path $env:DU_LIEU_CHUAN | Out-Null
    ChayNen $Py @("tai_dukascopy_tick_m1.py", "--luong", "4") "dukascopy" "Idle"
    "nền -> $env:DU_LIEU_CHUAN (script tự dừng khi ổ trống < 15 GB)"
}

# ---------------------------------------------------------------- 10. Seeker từ máy nhà
Buoc 10 "Seeker: nguồn box bị chặn IP + E:\brain2_nhap" {
    ChoGame
    $ds = & $Py -c "import json; d=json.load(open('reports/SEEKER_BOX_DO.json',encoding='utf-8')); print(','.join(k for k,v in d.items() if not v.get('ok')))" 2>$null
    $r = @()
    if ($ds) {
        Ghi "  nguồn box không lấy được: $ds"
        $rc = ChayPy @("seeker_quet_nguon.py", "--chi", "$ds", "--ep") "b10_seeker" 120
        $r += "seeker rc=$rc"
    } else { $r += "không có danh sách nguồn lỗi" }
    if (Test-Path "E:\brain2_nhap") { Ghi "  E:\brain2_nhap: $((Get-ChildItem 'E:\brain2_nhap' -Recurse -File -ErrorAction SilentlyContinue).Count) tệp" }
    foreach ($b in @("nhan", "phan_loai", "quyet_dinh")) {
        $rc = ChayPy @("ong_dan.py", $b) "b10_$b" 60
        $r += "$b rc=$rc"
    }
    ($r -join "; ")
}

# ---------------------------------------------------------------- 8. đọc kết quả MT5
Buoc 8 "ong_dan.py doc_mt5" {
    $fp = Join-Path $ThuMucLog "pid_mt5.txt"
    if (Test-Path $fp) {
        $pm = [int](Get-Content $fp | Select-Object -First 1)
        $han = [datetime]::ParseExact($Den, "HH:mm", $null); if ($han -lt (Get-Date).AddHours(-1)) { $han = $han.AddDays(1) }
        while ((Get-Process -Id $pm -ErrorAction SilentlyContinue) -and ((Get-Date) -lt $han.AddMinutes(40))) { Start-Sleep -Seconds 60 }
        if (Get-Process -Id $pm -ErrorAction SilentlyContinue) { Ghi "  hàng MT5 (PID $pm) vẫn chạy sau $Den+40 phút - đọc kết quả đang có" }
    }
    $rc = ChayPy @("ong_dan.py", "doc_mt5") "b8_doc_mt5" 60
    $null = ChayPy @("ong_dan.py", "bao_cao") "b8_bao_cao" 30
    "rc=$rc"
}

# ---------------------------------------------------------------- 11. commit + tóm tắt sáng
Buoc 11 "Commit reports\ + KET_QUA_SANG.md" {
    $l = @("# Kết quả sáng $(Get-Date -Format 'dd/MM/yyyy') - máy nhà $env:COMPUTERNAME", "",
        "Tự động sinh bởi chay_toi_nay.ps1. Số liệu chỉ lấy từ báo cáo đo thật; phần chưa đo ghi CHƯA ĐO ĐƯỢC. Số Python là MÔ PHỎNG.", "",
        "| Bước | Việc | Kết quả | Thời gian |", "|---|---|---|---|")
    foreach ($k in $KetQua.Keys) { $p = $KetQua[$k].Split("|"); $l += "| $k | $($p[0].Trim()) | $($p[1].Trim()) | $($p[2].Trim()) |" }
    foreach ($f in @("reports\ong_dan\DICH_LLM.md", "reports\ong_dan\TRANG_THAI.md", "reports\ong_dan\DOI_CHIEU_MT5.md")) {
        $p = Join-Path $Repo $f
        if (Test-Path $p) { $l += ""; $l += "## Trích $f"; $l += ""; $l += (Get-Content $p -Encoding UTF8 | Select-Object -First 25) }
    }
    $nen = Join-Path $ThuMucLog "dich_llm_nen.xong.txt"
    $l += ""; $l += "Dịch nền: " + $(if (Test-Path $nen) { Get-Content $nen -Raw } else { "đang chạy hoặc chưa mở" })
    $l += "Log chi tiết: $ThuMucLog"
    Set-Content -Path $KetQuaSang -Value $l -Encoding UTF8
    Push-Location $Repo
    try {
        foreach ($f in @("reports", "may_nha_toi_nay/NHAT_KY.md", "may_nha_toi_nay/KET_QUA_SANG.md", "GHI_CHU_NANG_CAP_GROK.md", "GHI_CHU_NANG_CAP_CLAUDE.md")) {
            if (Test-Path (Join-Path $Repo $f)) { git add -- $f 2>&1 | ForEach-Object { Ghi "    | $_" } }
        }
        git reset -q -- data 2>&1 | Out-Null                       # mã người khác / gói zip không vào git
        $staged = git diff --cached --name-only
        if (-not $staged) { return "không có gì mới để commit" }
        $mau = '(sk-[A-Za-z0-9_\-]{16,}|AIBOX_API_KEY\s*=\s*\S{8,}|password\s*=|api\.txt)'
        $nghi = git diff --cached -U0 | Select-String -Pattern $mau
        if ($nghi) { git reset -q; return "DỪNG COMMIT: diff có chuỗi giống khoá/mật khẩu - kiểm tay" }
        git commit -q -m "Máy nhà tối ${Ngay}: báo cáo đo + nhật ký (chay_toi_nay.ps1)" 2>&1 | ForEach-Object { Ghi "    | $_" }
        if ($KhongPush) { return "commit xong, không push (-KhongPush)" }
        git pull --rebase -q 2>&1 | ForEach-Object { Ghi "    | $_" }
        git push -q 2>&1 | ForEach-Object { Ghi "    | $_" }
        if ($LASTEXITCODE -ne 0) { return "commit xong, push LỖI rc=$LASTEXITCODE" }
        "commit + push xong ($(@($staged).Count) tệp)"
    } finally { Pop-Location }
}

Ghi "## Hết phiên. Tóm tắt: $KetQuaSang | log: $ThuMucLog (máy KHÔNG tắt)"
foreach ($k in $KetQua.Keys) { Write-Host "  bước $k : $($KetQua[$k])" }
