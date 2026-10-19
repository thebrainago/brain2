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
    [int]$ToiDaLuot = 60
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

Set-Location $Repo
$rong = 0
$tongLam = 0; $tongDat = 0
for ($l = 1; $l -le $ToiDaLuot; $l++) {
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
    Ghi "lượt ${l}: chờ=$($d.cho) làm=$($d.lam) đạt=$($d.dat) hỏng=$($d.hong) lỗi_llm=$($d.loi_llm) gọi mới=$($d.goi_moi) cache=$($d.tu_cache)"
    $conLai = [int]$d.cho - [int]$d.thieu_ma - [int]$d.lam
    if ($conLai -le 0) { break }
    if ([int]$d.lam -eq 0) { $rong++ } else { $rong = 0 }
    if ($rong -ge 3) { Ghi "dừng: 3 lượt liền không làm được thẻ nào (hết quota / lỗi LLM?) - xem reports\ong_dan\DICH_LLM.md"; break }
    Start-Sleep -Seconds 10
}
Set-Content -Path $xong -Value "xong lúc $(Get-Date -Format 'yyyy-MM-dd HH:mm'): $tongLam thẻ đã kiểm, $tongDat đạt (lượt cuối $l)" -Encoding UTF8
Ghi "kết thúc: $tongLam thẻ đã kiểm, $tongDat đạt"
