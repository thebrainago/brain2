@echo off
chcp 65001 >nul
cd /d "%~dp0\.."
rem Tai lich su gia XM (MT5) + du phong Dukascopy/histdata. Chay lai bat ky luc nao: tu tiep tuc (resume).
rem Sua duong dan terminal XM neu khac:
set TERM_XM=C:\Program Files\XM Global MT5\terminal64.exe
if not "%~1"=="" set TERM_XM=%~1
rem Slot rieng MetaQuotes-Demo (xem tai_lieu\DU_LIEU_DAI_VA_PHI.md muc 6). Khong co thu muc -> bo qua.
set TERM_PHU=C:\MT5_lich_su_metaquotes\terminal64.exe
if not "%~2"=="" set TERM_PHU=%~2
if not exist "%TERM_PHU%" set TERM_PHU=
powershell -NoProfile -ExecutionPolicy Bypass -File "mt5tools\tai_lich_su.ps1" -Terminal "%TERM_XM%" -TerminalPhu "%TERM_PHU%"
pause
