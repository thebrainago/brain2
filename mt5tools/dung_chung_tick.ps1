# 21/10/2026 Grok: KHO TICK CHUNG cho moi slot tester: <Slot>\Tester\bases -> junction toi E:\mt5_tick_chung\bases.
# AN TOAN: tu choi terminal XM giao dich (C:\Program Files\XM Global MT5); KHONG XOA file nao: file da co trong kho chung
# (cung ten, cung kich thuoc) -> chuyen sang E:\mt5_tick_chung\_trung\<slot>\ ; khac -> giu ban MOI HON trong kho, ban kia
# sang _trung. Thu muc bases cu (da rong) doi ten bases_cu_<ngay> roi moi tao junction. Chi chay khi slot KHONG co
# terminal64/metatester64 dang chay tu thu muc do.
# Dung:  powershell -File mt5tools\dung_chung_tick.ps1 -Slot D:\mt5_tester\p1 [-Kho E:\mt5_tick_chung] [-Thu]
param([Parameter(Mandatory)][string]$Slot, [string]$Kho = "E:\mt5_tick_chung", [switch]$Thu)
$ErrorActionPreference = 'Stop'
$s = (Resolve-Path $Slot).Path.TrimEnd('\')
if ($s -like "C:\Program Files\XM Global MT5*" -or $s -like "*XM Global MT5*") { "TU CHOI: $s la terminal XM giao dich"; exit 2 }
if (-not (Test-Path "$s\terminal64.exe")) { "TU CHOI: $s khong phai slot MT5 (khong co terminal64.exe)"; exit 2 }
$dang = Get-Process terminal64, metatester64 -ErrorAction SilentlyContinue | ? { $_.Path -and $_.Path.StartsWith($s, 'OrdinalIgnoreCase') }
if ($dang) { "TU CHOI: slot dang chay ($($dang.Count) tien trinh) - doi viec xong / TAT_THE_BRAIN"; exit 3 }
$b = "$s\Tester\bases"; $kb = "$Kho\bases"; $trung = "$Kho\_trung\" + (($s -replace '[:\\]+','_').Trim('_'))
New-Item -ItemType Directory -Force -Path $kb, "$Kho\khoa", "$Kho\da_co" | Out-Null
if (Test-Path $b) {
  $it = Get-Item $b -Force
  if ($it.Attributes -band [IO.FileAttributes]::ReparsePoint) { "DA LA JUNCTION: $b -> $($it.Target)"; exit 0 }
  $fs = Get-ChildItem $b -Recurse -File -Force
  "slot $s : $($fs.Count) file, {0:N2} GB" -f (($fs | Measure Length -Sum).Sum / 1GB)
  foreach ($f in $fs) {
    $rel = $f.FullName.Substring($b.Length).TrimStart('\'); $dst = Join-Path $kb $rel
    if ($Thu) { continue }
    New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
    if (-not (Test-Path $dst)) { Move-Item -LiteralPath $f.FullName -Destination $dst; continue }
    $d = Get-Item $dst -Force
    $bk = Join-Path $trung $rel; New-Item -ItemType Directory -Force -Path (Split-Path $bk) | Out-Null
    if ($f.LastWriteTime -gt $d.LastWriteTime -and $f.Length -ne $d.Length) {
      Move-Item -LiteralPath $dst -Destination $bk -Force; Move-Item -LiteralPath $f.FullName -Destination $dst
    } else { Move-Item -LiteralPath $f.FullName -Destination $bk -Force }
  }
  if ($Thu) { "(-Thu: khong chuyen gi)"; exit 0 }
  $con = @(Get-ChildItem $b -Recurse -File -Force).Count
  if ($con -gt 0) { "DUNG: con $con file chua chuyen duoc trong $b - khong tao junction"; exit 4 }
  Rename-Item $b ("bases_cu_" + (Get-Date -Format yyyyMMdd_HHmmss))
}
New-Item -ItemType Junction -Path $b -Target $kb | Out-Null
"JUNCTION: $b -> $kb"
