# 21/10/2026 Grok: chuyen cache tick theo symbol cua slot SSD (C/D) sang E roi dat junction ve cho cu.
# Khong dung symbol dang test (doc tu .ini moi nhat cua slot) va thu muc co file sua trong 3 phut.
# Dung: powershell -File chuyen_tick_sang_E.ps1 -Slot D:\mt5_tester\p1 [-MinGB 0.1] [-Kho]
param([Parameter(Mandatory)][string]$Slot, [double]$MinGB = 0.1, [switch]$Kho)
$ErrorActionPreference = 'Continue'
$ten = ($Slot -replace '[:\\]+','_').Trim('_')
$goc = "E:\brain2_nguoi\tick_junction\$ten"
$ini = Get-ChildItem "$Slot\*.ini" | Sort LastWriteTime -Desc | Select -First 1
$dang = if ($ini) { ((Select-String -Path $ini.FullName -Pattern '^Symbol=').Line -replace '^Symbol=','').Trim() } else { '' }
"slot $Slot, symbol dang test: $dang (ini $($ini.Name))"
# Chi Tester\bases (cache cua agent): bases\*\ticks bi terminal64 giu file mo nen robocopy khong chuyen duoc (do 21/10 00:20).
$ds = @(Get-ChildItem "$Slot\Tester\bases\*\ticks\*" -Directory -ErrorAction SilentlyContinue)
$tong = 0
foreach ($d in $ds) {
  if ($d.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
  if ($d.Name -eq $dang) { "bo qua (dang test): $($d.FullName)"; continue }
  $fs = Get-ChildItem $d.FullName -Recurse -File -Force -ErrorAction SilentlyContinue
  $gb = ($fs | Measure Length -Sum).Sum / 1GB
  if ($gb -lt $MinGB) { continue }
  if ($fs | ? { $_.LastWriteTime -gt (Get-Date).AddMinutes(-3) }) { "bo qua (vua ghi): $($d.FullName)"; continue }
  $rel = $d.FullName.Substring($Slot.Length).TrimStart('\')
  $dst = Join-Path $goc $rel
  if ($Kho) { "{0:N2} GB -> {1}" -f $gb, $dst; $tong += $gb; continue }
  New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
  robocopy $d.FullName $dst /E /MOVE /R:0 /W:0 /NFL /NDL /NJH /NJS /NP | Out-Null
  $con = if (Test-Path $d.FullName) { @(Get-ChildItem $d.FullName -Recurse -File -Force -ErrorAction SilentlyContinue).Count } else { 0 }
  if ($con -gt 0) {
    robocopy $dst $d.FullName /E /MOVE /XC /XN /XO /R:2 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
    Remove-Item -LiteralPath $dst -Recurse -Force -ErrorAction SilentlyContinue   # ban sao trung file bi khoa (nguon van du)
    "TRA LAI (con $con file bi khoa): $($d.FullName)"; continue
  }
  if (Test-Path $d.FullName) { Remove-Item $d.FullName -Force -Recurse -ErrorAction SilentlyContinue }
  try { New-Item -ItemType Junction -Path $d.FullName -Target $dst -ErrorAction Stop | Out-Null; "{0:N2} GB chuyen + junction: {1}" -f $gb, $rel; $tong += $gb }
  catch { "LOI junction $($d.FullName): $_ (du lieu o $dst)" }
}
"tong {0:N2} GB" -f $tong

