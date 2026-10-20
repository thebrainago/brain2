#Requires -Version 5.1
<#
.SYNOPSIS
  Vòng nền của một phiên máy nhà (20/10/2026): mỗi ~60 phút viết báo cáo phiên và đẩy lên git, mỗi ~2 giờ chạy Seeker
  rồi ong_dan nhan / phan_loai / quyet_dinh.
  20/10/2026 09:31: Seeker không còn cố định 2 giờ - giao cho dieu_phoi_may_nha.py (xem config/dieu_phoi.json). Tới giờ -Den thì chạy báo cáo cuối phiên (doc_mt5 + báo cáo + dọn) rồi thoát.
  Chỉ đẩy reports/phien/PHIEN_*.md và reports/UNG_VIEN.md (bao_cao_phien.py tự git add đúng hai loại tệp đó).
  Không đọc, không in khoá. 20/10/2026 09:50: không giảm tải theo game; TAT_THE_BRAIN.co -> dừng êm.
#>
param(
    [string]$Repo = (Split-Path -Parent $PSScriptRoot),
    [string]$Python = "python",
    [string]$ThuMucLog = (Join-Path $PSScriptRoot "log"),
    [int]$PhutBaoCao = 60,
    [string]$Den = "07:00",
    [switch]$KhongPush
)
$ErrorActionPreference = "Continue"
$env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
New-Item -ItemType Directory -Force -Path $ThuMucLog | Out-Null
$log = Join-Path $ThuMucLog "vong_phien.log"
$nk = Join-Path $Repo "may_nha_toi_nay\NHAT_KY.md"
$khoa = Join-Path $ThuMucLog "ong_dan_chay.lock"      # chung với chay_toi_nay.ps1 bước 6 và dich_llm_nen.ps1

function Ghi([string]$s) {
    $d = "- " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + " [vòng phiên] " + $s
    Add-Content -Path $log -Value $d -Encoding UTF8
    try { Add-Content -Path $nk -Value $d -Encoding UTF8 } catch { }
}
Set-Content -Path (Join-Path $ThuMucLog "pid_vong_phien_ps.txt") -Value $PID
function Py([string[]]$a, [string]$ten, [int]$phut = 60) {
    $out = Join-Path $ThuMucLog "vp_$ten.out.txt"; $err = Join-Path $ThuMucLog "vp_$ten.err.txt"
    $p = Start-Process -FilePath $Python -ArgumentList ($a -join " ") -WorkingDirectory $Repo -NoNewWindow -PassThru `
        -RedirectStandardOutput $out -RedirectStandardError $err
    $null = $p.Handle
    try { $p.PriorityClass = "Normal" } catch { }
    if (-not $p.WaitForExit($phut * 60 * 1000)) { try { Stop-Process -Id $p.Id -Force } catch { }; Ghi "$ten QUÁ GIỜ $phut phút"; return -999 }
    $t = (Get-Content $out -Tail 2 -Encoding UTF8 -ErrorAction SilentlyContinue) -join " / "
    Ghi "$ten rc=$($p.ExitCode) $t"
    return $p.ExitCode
}
function LayKhoa {
    $bd = Get-Date
    while (Test-Path $khoa) {
        $pk = Get-Content $khoa -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not ($pk -and (Get-Process -Id ([int]$pk) -ErrorAction SilentlyContinue))) { Remove-Item $khoa -Force; break }
        if (((Get-Date) - $bd).TotalMinutes -gt 30) { return $false }
        Start-Sleep -Seconds 60
    }
    Set-Content $khoa $PID
    return $true
}

$han = [datetime]::ParseExact($Den, "HH:mm", $null)
if ($han -le (Get-Date)) { $han = $han.AddDays(1) }
$day = if ($KhongPush) { @() } else { @("--day") }
Ghi "BẮT ĐẦU tới $han (báo cáo mỗi $PhutBaoCao phút; Seeker/dich_llm do dieu_phoi_may_nha.py quyết theo tài nguyên)"
$lanBc = [datetime]::MinValue
# 20/10/2026 (chủ dự án 09:31): thay "Seeker mỗi 2 giờ" bằng bộ điều phối tài nguyên may_nha_toi_nay/dieu_phoi_may_nha.py
# (config/dieu_phoi.json): dich_llm chạy liên tục song song MT5; Seeker chỉ chạy khi hàng đầu vào sắp cạn và ổ còn chỗ;
# ghi muc_mt5.json cho chay_lien_tuc (số slot tầng 1/2 theo RAM, đang chơi game -> 1 việc nhẹ).
function KhoiDongDieuPhoi {
    $o = Join-Path $ThuMucLog "dieu_phoi.out.txt"; $e = Join-Path $ThuMucLog "dieu_phoi.err.txt"
    $env:BRAIN_LOG_DIR = $ThuMucLog
    $p = Start-Process -FilePath $Python -ArgumentList "may_nha_toi_nay/dieu_phoi_may_nha.py --den $Den" -WorkingDirectory $Repo `
        -NoNewWindow -PassThru -RedirectStandardOutput $o -RedirectStandardError $e
    try { $p.PriorityClass = "Normal" } catch { }
    Set-Content -Path (Join-Path $ThuMucLog "pid_dieu_phoi.txt") -Value $p.Id
    Ghi "dieu_phoi_may_nha.py pid $($p.Id)"
    return $p
}
$dp = KhoiDongDieuPhoi
$tat = Join-Path $PSScriptRoot "TAT_THE_BRAIN.co"
while ((Get-Date) -lt $han) {
    if (Test-Path $tat) { Ghi "thấy TAT_THE_BRAIN.co - dừng vòng phiên (báo cáo cuối vẫn chạy)"; break }
    if (((Get-Date) - $lanBc).TotalMinutes -ge $PhutBaoCao) {
        $null = Py (@("mt5tools/bao_cao_phien.py") + $day) "bao_cao" 20
        $lanBc = Get-Date
    }
    if ($dp -and $dp.HasExited -and ((Get-Date) -lt $han.AddMinutes(-10))) {
        Ghi "dieu_phoi_may_nha.py thoát sớm rc=$($dp.ExitCode) - khởi động lại"; $dp = KhoiDongDieuPhoi
    }
    Start-Sleep -Seconds 300
}
# cuối phiên: chờ hàng MT5 (chay_lien_tuc tự dừng tại -Den + 20 phút) rồi doc_mt5 + báo cáo + dọn + đẩy
$fp = Join-Path $ThuMucLog "pid_mt5.txt"
if (Test-Path $fp) {
    $pm = [int](Get-Content $fp | Select-Object -First 1)
    $bd = Get-Date
    while ((Get-Process -Id $pm -ErrorAction SilentlyContinue) -and (((Get-Date) - $bd).TotalMinutes -lt 45)) { Start-Sleep -Seconds 60 }
}
if ($KhongPush) { Ghi "-KhongPush: báo cáo cuối vẫn commit cục bộ qua bao_cao_phien --ket_thuc (không thể tắt push riêng) - bỏ qua --ket_thuc, chỉ ghi báo cáo"; $null = Py @("mt5tools/bao_cao_phien.py") "bao_cao_cuoi" 60 }
else { $null = Py @("mt5tools/bao_cao_phien.py", "--ket_thuc") "bao_cao_cuoi" 60 }
Ghi "HẾT PHIÊN"
