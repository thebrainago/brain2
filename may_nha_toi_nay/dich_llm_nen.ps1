#Requires -Version 5.1
<#
.SYNOPSIS
  Dịch nền toàn bộ hàng chờ bằng LLM trên máy nhà: gọi `python ong_dan.py dich_llm --gioi_han N` lặp lại tới khi hết.
  Chạy lại được bất cứ lúc nào: kết quả đã gọi nằm trong cache data/ong_dan/dich_llm/ (theo sha256 mã nguồn),
  trạng thái thẻ ghi vào trang_thai.sqlite ở cuối mỗi lượt (nên lượt nhỏ = mất ít nhất khi bị ngắt).
  Không đọc, không in khoá. Đang chơi game thì chờ.
#>
param(
    [string]$Repo = (Split-Path -Parent $PSScriptRoot),
    [string]$Python = "python",
    [string]$ThuMucLog = (Join-Path $PSScriptRoot "log"),
    [int]$GioiHan = 200,
    [int]$Luong = 4,
    [int]$ToiDaLuot = 60,
    [int]$ToiDaOngDan = 30,     # 19/10/2026: sau mỗi lượt có thẻ đạt -> `ong_dan.py chay --toi-da N` (0 = tắt)
    [string]$Den = ""           # "07:00": quá giờ này thì không mở lượt mới
)
$ErrorActionPreference = "Continue"
$env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
New-Item -ItemType Directory -Force -Path $ThuMucLog | Out-Null
$log = Join-Path $ThuMucLog "dich_llm_nen.log"
$xong = Join-Path $ThuMucLog "dich_llm_nen.xong.txt"
$nk = Join-Path $Repo "may_nha_toi_nay\NHAT_KY.md"
$game = @("valorant-win64-shipping.exe", "valorant.exe", "league of legends.exe", "leagueclientux.exe", "cs2.exe", "dota2.exe",
    "gta5.exe", "fortniteclient-win64-shipping.exe", "r5apex.exe", "overwatch.exe", "pubg-win64-shipping.exe", "eldenring.exe",
    "genshinimpact.exe")

function Ghi([string]$s) {
    $d = "- " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + " [dịch nền] " + $s
    Add-Content -Path $log -Value $d -Encoding UTF8
    try { Add-Content -Path $nk -Value $d -Encoding UTF8 } catch { }
}
function DangChoi {
    $ten = Get-Process -ErrorAction SilentlyContinue | ForEach-Object { ($_.ProcessName + ".exe").ToLower() }
    foreach ($g in $game) { if ($ten -contains $g) { return $true } }
    return $false
}

function ChayOngDan {
    # Tối ưu + lọc + sinh việc MT5 cho thẻ vừa dịch đạt. Khoá chung với bước 6 của chay_toi_nay.ps1 để không cùng ghi
    # trang_thai.sqlite; bước 6 đang chạy thì bỏ lượt này (lượt sau sẽ làm).
    if ($ToiDaOngDan -le 0) { return }
    $khoa = Join-Path $ThuMucLog "ong_dan_chay.lock"
    if (Test-Path $khoa) {
        $pk = Get-Content $khoa -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($pk -and (Get-Process -Id ([int]$pk) -ErrorAction SilentlyContinue)) { Ghi "ong_dan chay: bước 6 đang giữ khoá - để lượt sau"; return }
    }
    Set-Content $khoa $PID
    try {
        $o = & $Python ong_dan.py chay --toi-da $ToiDaOngDan 2>&1 | Out-String
        Add-Content -Path (Join-Path $ThuMucLog "ong_dan_nen.log") -Value $o -Encoding UTF8
        Ghi "ong_dan chay --toi-da $ToiDaOngDan rc=$LASTEXITCODE (việc MT5 mới vào hàng, hàng MT5 nền tự lấy)"
    } finally { Remove-Item $khoa -Force -ErrorAction SilentlyContinue }
}
$hetGio = $null
if ($Den) {
    $hetGio = [datetime]::ParseExact($Den, "HH:mm", $null)
    if ($hetGio -lt (Get-Date)) { $hetGio = $hetGio.AddDays(1) }
}

Set-Location $Repo
$rong = 0
$tongLam = 0; $tongDat = 0
for ($l = 1; $l -le $ToiDaLuot; $l++) {
    if ($hetGio -and (Get-Date) -ge $hetGio.AddMinutes(-30)) { Ghi "dừng: gần $Den"; break }
    while (DangChoi) { Start-Sleep -Seconds 300 }
    $soLuong = $(if (DangChoi) { 1 } else { $Luong })
    $out = & $Python ong_dan.py dich_llm --gioi_han $GioiHan --luong $soLuong 2>&1 | Out-String
    $rc = $LASTEXITCODE
    Add-Content -Path $log -Value $out -Encoding UTF8
    if ($out -match "CHUA CHAY DUOC") { Ghi "dừng: máy không có khoá"; Set-Content $xong "DỪNG - không có khoá" -Encoding UTF8; exit 0 }
    $m = [regex]::Matches($out, '(?ms)^\{\s*$.*?^\}\s*$')
    $d = $null
    if ($m.Count -gt 0) { try { $d = $m[$m.Count - 1].Value | ConvertFrom-Json } catch { } }
    if (-not $d) { Ghi "lượt $l lỗi rc=$rc (không đọc được kết quả)"; $rong++; if ($rong -ge 3) { break }; Start-Sleep -Seconds 60; continue }
    $tongLam += [int]$d.lam; $tongDat += [int]$d.dat
    if ([int]$d.dat -gt 0) { ChayOngDan }
    Ghi "lượt ${l}: chờ=$($d.cho) làm=$($d.lam) đạt=$($d.dat) hỏng=$($d.hong) lỗi_llm=$($d.loi_llm) gọi mới=$($d.goi_moi) cache=$($d.tu_cache)"
    $conLai = [int]$d.cho - [int]$d.thieu_ma - [int]$d.lam
    if ($conLai -le 0) { break }
    if ([int]$d.lam -eq 0) { $rong++ } else { $rong = 0 }
    if ($rong -ge 3) { Ghi "dừng: 3 lượt liền không làm được thẻ nào (hết quota / lỗi LLM?) - xem reports\ong_dan\DICH_LLM.md"; break }
    Start-Sleep -Seconds 10
}
Set-Content -Path $xong -Value "xong lúc $(Get-Date -Format 'yyyy-MM-dd HH:mm'): $tongLam thẻ đã kiểm, $tongDat đạt (lượt cuối $l)" -Encoding UTF8
Ghi "kết thúc: $tongLam thẻ đã kiểm, $tongDat đạt"
