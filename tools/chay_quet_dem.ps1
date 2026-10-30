# Brain2 nightly public-signal scan (BelowNormal). Temp on E:.
$ErrorActionPreference = "Continue"
$py = "E:\brain2_grok\venv\Scripts\python.exe"
$goc = "E:\brain2_grok"
$tin = "E:\brain2_grok_tin_hieu"
$log = Join-Path $tin ("logs\quet_dem_{0:yyyyMMdd_HHmm}.log" -f (Get-Date))
New-Item -ItemType Directory -Force -Path "$tin\logs","$tin\data\mql5_csv","$tin\data\myfxbook_csv","$tin\tmp","$tin\hang_cho_out","$tin\pw_profile" | Out-Null
$env:BRAIN_DATA = "$goc\data"
$env:BRAIN_TIN_HIEU = $tin
$env:BRAIN_MQL5_CSV = "$tin\data\mql5_csv"
$env:BRAIN_MYFX_CSV = "$tin\data\myfxbook_csv"
$env:BRAIN_PW_PROFILE = "$tin\pw_profile"
$env:BRAIN_LLM_PROVIDER = "hang_cho"
$env:BRAIN_HANG_CHO_MIRROR = "$tin\hang_cho_out"
$env:PYTHONPATH = "$goc;$tin\scripts"
$env:PYTHONUNBUFFERED = "1"
Set-Location $goc
# mute
$n = Join-Path $env:TEMP "nircmdc.exe"
if (Test-Path $n) { & $n mutesysvolume 1; & $n setsysvolume 0 }
try { (Get-Process -Id $PID).PriorityClass = "BelowNormal" } catch {}
# FXBlue mass + MQL5 list/PW + Myfxbook HTML History (seed) + profile login probe
& $py -u tools\quet_tin_hieu_dem.py `
  --nghi 5 `
  --toi-da-he 40 `
  --mql5-list `
  --mql5-pw `
  --mql5-toi-da 100 `
  --myfxbook-pw `
  --kiem-tra-mql5-profiles `
  --kho-gia "$goc\data" `
  --hang-viec "$goc\reports\vong2\hang_cho_tin_hieu.jsonl" *>> $log
# mirror outputs to xfer (E then C xfer)
Copy-Item -Force "$tin\hang_cho_out\*.json" "C:\Users\DUNG\brain2_grok_xfer\tin_hieu\" -EA SilentlyContinue
Copy-Item -Force "$goc\reports\vong2\hang_cho_tin_hieu.jsonl" "C:\Users\DUNG\brain2_grok_xfer\tin_hieu\" -EA SilentlyContinue
# delete non-essential tmp (keep pw_profile + csv data)
Get-ChildItem "$tin\tmp" -Recurse -EA SilentlyContinue | Remove-Item -Force -Recurse -EA SilentlyContinue
Get-ChildItem "$tin\logs\myfxbook_no_history_*.html","$tin\logs\myfxbook_captcha_*.html" -EA SilentlyContinue |
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-3) } | Remove-Item -Force -EA SilentlyContinue
