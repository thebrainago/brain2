# Tai du lieu dai tren MAY NHA. 1) MT5 XM (uu tien)  2) Dukascopy + histdata (du phong, cham, lich su)  3) gop + kiem tra.
# Moi buoc tu resume; log o data\du_lieu_dai\*.log. Dung: Ctrl+C (chay lai se tiep tuc).
param([string]$Terminal = "C:\Program Files\XM Global MT5\terminal64.exe", [switch]$BoDuPhong)
$ErrorActionPreference = "Continue"
Set-Location (Split-Path $PSScriptRoot -Parent)
New-Item -ItemType Directory -Force -Path data\du_lieu_dai | Out-Null
$env:PYTHONIOENCODING = "utf-8"
python mt5tools\tai_lich_su_mt5.py "$Terminal" 2>&1 | Tee-Object -Append data\du_lieu_dai\mt5.log
if (-not $BoDuPhong) {
  python -m nhan.tai_du_lieu --chi-histdata 2>&1 | Tee-Object -Append data\du_lieu_dai\tai_histdata.log
  python -m nhan.tai_du_lieu --chi-duka 2>&1 | Tee-Object -Append data\du_lieu_dai\tai_duka.log
}
python -m nhan.du_lieu_dai --dung 2>&1 | Tee-Object -Append data\du_lieu_dai\dung.log
python -m nhan.phi_dai 2>&1 | Tee-Object -Append data\du_lieu_dai\phi.log
Write-Host "XONG. Commit: reports\du_lieu_dai\ va config\phi_xm_micro.json (khong commit data\)."
