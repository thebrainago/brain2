#Requires -Version 5.1
<#
.SYNOPSIS
  Kiểm trước khi chạy The Brain trên máy nhà (20/10/2026). In OK / LỖI / CẢNH BÁO cho từng mục, cuối cùng in tổng.
  Chỉ ĐỌC (không sửa gì), trừ mục quota: gửi MỘT lệnh LLM rất nhỏ (max_tokens 1) nếu có AIBOX_API_KEY.
  Không in khoá, không đọc E:\api.txt, không đọc Login/mật khẩu MT5 (chỉ dòng Server= trong common.ini).
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File may_nha_toi_nay\kiem_truoc_khi_chay.ps1
  powershell -ExecutionPolicy Bypass -File may_nha_toi_nay\kiem_truoc_khi_chay.ps1 -BoQuaQuota
#>
param(
    [switch]$BoQuaQuota,
    [double]$CToiThieuGb = 6, [double]$DToiThieuGb = 6, [double]$EToiThieuGb = 20, [double]$RamToiThieuGb = 4,
    [string]$SaoLuu = "E:\brain2_sao_luu\chay_lien_tuc.py.claude_23h45",
    [string[]]$SlotChinh = @("D:\mt5_tester\p1", "C:\mt5_tester\p7"),
    [string[]]$SlotE = @("E:\mt5_tester\p3", "E:\mt5_tester\p6", "E:\mt5_tester\p4")
)
$ErrorActionPreference = "Continue"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo
$script:soLoi = 0; $script:soCanh = 0
function Ok([string]$m)   { Write-Host ("OK         " + $m) -ForegroundColor Green }
function Loi([string]$m)  { Write-Host ("LỖI       " + $m) -ForegroundColor Red; $script:soLoi++ }
function Canh([string]$m) { Write-Host ("CẢNH BÁO  " + $m) -ForegroundColor Yellow; $script:soCanh++ }
function OTrong([string]$o) {
    try { return [math]::Round((Get-PSDrive -Name $o.Substring(0, 1) -ErrorAction Stop).Free / 1GB, 1) } catch { return -1 }
}
function DocServer([string]$t) {
    $f = Join-Path $t "config\common.ini"
    if (-not (Test-Path $f)) { return "" }
    foreach ($enc in @("Unicode", "UTF8", "Default")) {
        try {
            $d = Get-Content $f -Encoding $enc -ErrorAction Stop | Where-Object { $_ -match "^\s*Server\s*=" } | Select-Object -First 1
            if ($d) { return ($d -split "=", 2)[1].Trim() }
        } catch { }
    }
    return ""
}

# 1) git: nhánh, đã kéo bản mới, không còn sửa dở
$nhanh = (git rev-parse --abbrev-ref HEAD 2>$null)
if ($nhanh -eq "main") { Ok "git nhánh main" } else { Loi "git đang ở nhánh '$nhanh' (cần main)" }
git fetch -q origin 2>$null
$sau = (git rev-list --count "HEAD..origin/main" 2>$null)
if ("$sau" -eq "0") { Ok "git đã có bản mới nhất origin/main" } else { Loi "git thiếu $sau commit của origin/main -> git pull --rebase" }
$ban = @(git status --porcelain --untracked-files=no 2>$null)
if ($ban.Count -eq 0) { Ok "git không có tệp sửa dở" } else { Canh "git có $($ban.Count) tệp sửa dở: $((($ban | Select-Object -First 5) -join '; '))" }
$stash = @(git stash list 2>$null)
if ($stash.Count -gt 0) { Canh "git stash còn $($stash.Count) mục (đã so chay_lien_tuc.py chưa?)" }

# 2) chay_lien_tuc.py so với bản sao lưu của Claude
$cl = Join-Path $Repo "mt5tools\chay_lien_tuc.py"
if (-not (Test-Path $cl)) { Loi "không thấy mt5tools\chay_lien_tuc.py" }
elseif (-not (Test-Path $SaoLuu)) { Canh "không thấy bản sao lưu $SaoLuu (không so được)" }
else {
    $h1 = (Get-FileHash $cl -Algorithm SHA256).Hash; $h2 = (Get-FileHash $SaoLuu -Algorithm SHA256).Hash
    if ($h1 -eq $h2) { Ok "chay_lien_tuc.py giống hệt bản sao lưu 23h45" }
    else { Canh "chay_lien_tuc.py KHÁC bản sao lưu 23h45 -> đã so và gộp phần Claude sửa chưa? (git diff --no-index `"$SaoLuu`" `"$cl`")" }
}

# 3) python + psutil
$py = $null
foreach ($p in @((Join-Path $Repo ".venv\Scripts\python.exe"), "python", "py")) {
    try { $v = & $p -c "import sys;print(sys.version.split()[0])" 2>$null; if ($LASTEXITCODE -eq 0 -and $v) { $py = $p; break } } catch { }
}
if (-not $py) { Loi "không chạy được python" }
else {
    Ok "python $v ($py)"
    $ps = & $py -c "import psutil;print(psutil.__version__)" 2>$null
    if ($LASTEXITCODE -eq 0) { Ok "psutil $ps" } else { Loi "thiếu psutil -> $py -m pip install psutil" }
}

# 4) thư mục tải về Seeker nằm trên E: (junction)
$tv = Join-Path $Repo "data\seeker_da_nguon\tai_ve"
if (-not (Test-Path $tv)) { Loi "không có $tv (chưa mklink /J sang E:)" }
else {
    $it = Get-Item $tv -Force
    $dich = $null
    if ($it.LinkType -eq "Junction" -or $it.LinkType -eq "SymbolicLink") { $dich = @($it.Target)[0] }
    if ($dich -and $dich.ToUpper().StartsWith("E:")) { Ok "tai_ve là junction -> $dich" }
    elseif ($dich) { Loi "tai_ve trỏ sang $dich (cần ổ E:)" }
    else { Loi "tai_ve là thư mục thường trên ổ repo (chưa chuyển sang E: bằng mklink /J)" }
}

# 5) ổ đĩa + RAM
foreach ($c in @(@("C:", $CToiThieuGb), @("D:", $DToiThieuGb), @("E:", $EToiThieuGb))) {
    $g = OTrong $c[0]
    if ($g -lt 0) { Loi "không đọc được ổ $($c[0])" }
    elseif ($g -ge $c[1]) { Ok "ổ $($c[0]) trống $g GB (>= $($c[1]))" }
    else { Loi "ổ $($c[0]) chỉ trống $g GB (< $($c[1]) GB) -> dọn hoặc chuyển sang E:" }
}
try {
    $os_ = Get-CimInstance Win32_OperatingSystem
    $ram = [math]::Round($os_.FreePhysicalMemory / 1MB, 1); $tong = [math]::Round($os_.TotalVisibleMemorySize / 1MB, 1)
    if ($ram -ge $RamToiThieuGb) { Ok "RAM trống $ram / $tong GB" } else { Loi "RAM trống $ram GB (< $RamToiThieuGb) -> đóng bớt ứng dụng" }
} catch { Loi "không đọc được RAM" }

# 6) slot MT5 tester: p1 (D), p7 (C) bắt buộc; slot E dự phòng phải đăng nhập XM (tài khoản micro)
foreach ($s in $SlotChinh + $SlotE) {
    $batBuoc = $SlotChinh -contains $s
    if (-not (Test-Path (Join-Path $s "terminal64.exe"))) {
        if ($batBuoc) { Loi "slot $s không có terminal64.exe" } else { Canh "slot dự phòng $s không có (bỏ qua)" }
        continue
    }
    $sv = DocServer $s
    if (-not $sv) { if ($batBuoc) { Loi "slot $s chưa đăng nhập (không có Server= trong config\common.ini)" } else { Canh "slot dự phòng $s chưa đăng nhập" }; continue }
    $micro = @(Get-ChildItem -Path (Join-Path $s "bases\$sv\history") -Directory -Filter "*micro*" -ErrorAction SilentlyContinue).Count
    if ($sv -match "XM") {
        if ($micro -gt 0) { Ok "slot $s server=$sv, có $micro mã *micro" }
        else { Canh "slot $s server=$sv nhưng chưa thấy lịch sử mã *micro (tài khoản micro? mở terminal kiểm tay)" }
    } elseif ($s.ToUpper().StartsWith("E:")) { Loi "slot dự phòng $s đăng nhập $sv - cần XM micro" }
    else { Ok "slot $s server=$sv" }
}
$tt = @(Get-Process -Name terminal64 -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*mt5_tester*" })
if ($tt.Count -gt 0) { Canh "$($tt.Count) terminal tester đang chạy sẵn (phiên cũ chưa tắt?)" } else { Ok "không có terminal tester nào đang chạy sẵn" }
if (Test-Path (Join-Path $PSScriptRoot "TAT_THE_BRAIN.co")) { Canh "còn cờ TAT_THE_BRAIN.co (BAT_THE_BRAIN.bat sẽ tự xoá)" }

# 7) khoá + quota ai-box (một lệnh rất nhỏ; không in khoá)
if ($env:AIBOX_API_KEY) { Ok "có biến AIBOX_API_KEY (không in)" } else { Canh "không có AIBOX_API_KEY trong môi trường -> dich_llm chỉ kiểm lại cache" }
if ($BoQuaQuota) { Canh "bỏ qua kiểm quota (-BoQuaQuota)" }
elseif ($py -and $env:AIBOX_API_KEY) {
    $ma = "import sys;sys.path.insert(0,'.');from nhan import cau_llm as L;r=L.goi('ping',max_tokens=1,han_giay=60);print(r['trang_thai']+'|'+str(r.get('model'))+'|'+str(r.get('ghi_chu') or '')[:160])"
    $kq = (& $py -c $ma 2>$null | Select-Object -Last 1)
    if ("$kq" -like "OK|*") { Ok "quota ai-box còn: $kq" }
    elseif ("$kq" -match "403|402|quota") { Loi "ai-box HẾT QUOTA ($kq) -> dich_llm không gọi được; chủ dự án cần nạp" }
    else { Loi "gọi thử ai-box không được: $kq" }
}

Write-Host ""
if ($script:soLoi -eq 0) { Write-Host "TỔNG: OK ($script:soCanh cảnh báo) - chạy được BAT_THE_BRAIN.bat" -ForegroundColor Green; exit 0 }
Write-Host "TỔNG: $script:soLoi LỖI, $script:soCanh cảnh báo - sửa LỖI trước khi chạy" -ForegroundColor Red
exit 1
