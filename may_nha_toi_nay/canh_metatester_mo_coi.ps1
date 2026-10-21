# Canh metatester64 mo coi (cha terminal64 da chet) trong *\mt5_tester\* - giet dung PID sau 90 s. Grok Bot 20/10/2026.
$den = Get-Date '2026-10-21 07:30'
$log = 'D:\mt5_lien_tuc\canh_mo_coi.log'
function Ghi($t){ Add-Content -Path $log -Value ("{0:yyyy-MM-dd HH:mm:ss} {1}" -f (Get-Date), $t) }
Ghi "BAT DAU PID $PID"
$cho = @{}
while ((Get-Date) -lt $den) {
  try {
    $all = Get-CimInstance Win32_Process
    $byId = @{}; foreach ($p in $all) { $byId[[int]$p.ProcessId] = $p }
    $thay = @{}
    foreach ($m in ($all | Where-Object { $_.Name -eq 'metatester64.exe' -and $_.ExecutablePath -like '*\mt5_tester\*' })) {
      $id = [int]$m.ProcessId; $thay[$id] = 1
      $par = $byId[[int]$m.ParentProcessId]
      $mo = (-not $par) -or ($par.Name -ne 'terminal64.exe') -or ($par.CreationDate -gt $m.CreationDate)
      if ($mo) {
        if ($cho.ContainsKey($id)) {
          if (((Get-Date) - $cho[$id]).TotalSeconds -ge 90) {
            $mb = [int]($m.WorkingSetSize / 1MB)
            try { Stop-Process -Id $id -Force -ErrorAction Stop; Ghi "GIET metatester mo coi PID $id ($($m.ExecutablePath), $mb MB, cha $($m.ParentProcessId) da chet)" } catch { Ghi "LOI giet $id : $_" }
            $cho.Remove($id)
          }
        } else { $cho[$id] = Get-Date; Ghi "NGHI mo coi PID $id ($($m.ExecutablePath)), cho 90 s" }
      } elseif ($cho.ContainsKey($id)) { $cho.Remove($id) }
    }
    foreach ($k in @($cho.Keys)) { if (-not $thay.ContainsKey($k)) { $cho.Remove($k) } }
  } catch { Ghi "LOI vong: $_" }
  Start-Sleep -Seconds 30
}
Ghi "KET THUC"
