#Requires -Version 5.1
<#
.SYNOPSIS
  Tắt êm The Brain trên máy nhà (20/10/2026).
  1) Tạo cờ may_nha_toi_nay\TAT_THE_BRAIN.co:
     - chay_lien_tuc.py ngừng mở việc MT5 mới và cho việc đang chạy tối đa 20 phút để xong;
     - dieu_phoi_may_nha.py và vong_phien.ps1 thoát vòng.
  2) Chờ tối đa -ChoPhut phút cho các tiến trình đó tự thoát.
  3) Tiến trình nào còn sống thì CHỈ dừng đúng PID đã ghi trong log phiên (pid_*.txt, pid\*.pid). Trước khi dừng,
     kiểm tên tiến trình là python / powershell / pwsh. Không bao giờ dừng terminal64.exe (XM chính), claude, node, Cursor.
#>
param([int]$ChoPhut = 30)
$ErrorActionPreference = "Continue"
$goc = $PSScriptRoot
$co = Join-Path $goc "TAT_THE_BRAIN.co"
Set-Content -Path $co -Value (Get-Date -Format "yyyy-MM-dd HH:mm:ss") -Encoding UTF8
$nk = Join-Path $goc "NHAT_KY.md"
function Ghi([string]$s) {
    $d = "- " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + " [TẮT THE BRAIN] " + $s
    Write-Host $d
    try { Add-Content -Path $nk -Value $d -Encoding UTF8 } catch { }
}
$log = $null
$fp = Join-Path $goc "PHIEN_HIEN_TAI.txt"
if (Test-Path $fp) { $log = (Get-Content $fp -Encoding UTF8 | Select-Object -First 1).Trim() }
if (-not $log -or -not (Test-Path $log)) { $log = Join-Path $goc "log" }
Ghi "đã đặt cờ TAT_THE_BRAIN.co; log phiên: $log; chờ tối đa $ChoPhut phút"

$choPhep = @("python", "pythonw", "python3", "py", "powershell", "pwsh")
function DsPid {
    $ds = @()
    foreach ($f in @(Get-ChildItem -Path $log -Filter "pid_*.txt" -ErrorAction SilentlyContinue) +
                   @(Get-ChildItem -Path (Join-Path $log "pid") -Filter "*.pid" -ErrorAction SilentlyContinue)) {
        $v = (Get-Content $f.FullName -ErrorAction SilentlyContinue | Select-Object -First 1)
        if ($v -match '^\s*(\d+)\s*$') {
            $p = Get-Process -Id ([int]$Matches[1]) -ErrorAction SilentlyContinue
            if ($p -and ($choPhep -contains $p.ProcessName.ToLower()) -and $p.Id -ne $PID) { $ds += [pscustomobject]@{ Ten = $f.BaseName; P = $p } }
        }
    }
    return $ds
}
$bd = Get-Date
while (((Get-Date) - $bd).TotalMinutes -lt $ChoPhut) {
    $con = DsPid
    if (-not $con) { break }
    Write-Host ("  còn chạy: " + (($con | ForEach-Object { "$($_.Ten)=$($_.P.Id)" }) -join ", "))
    Start-Sleep -Seconds 30
}
foreach ($x in (DsPid)) {
    try { Stop-Process -Id $x.P.Id -ErrorAction Stop; Ghi "dừng $($x.Ten) PID $($x.P.Id) ($($x.P.ProcessName))" }
    catch { Ghi "không dừng được $($x.Ten) PID $($x.P.Id): $_" }
}
Ghi "XONG. Bật lại: BAT_THE_BRAIN.bat (tự xoá cờ)."
