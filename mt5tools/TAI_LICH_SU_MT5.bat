@echo off
chcp 65001 >nul
cd /d "%~dp0\.."
rem Tai lich su gia XM (MT5) + du phong Dukascopy/histdata. Chay lai bat ky luc nao: tu tiep tuc (resume).
rem Sua duong dan terminal XM neu khac:
set TERM_XM=C:\Program Files\XM Global MT5\terminal64.exe
if not "%~1"=="" set TERM_XM=%~1
powershell -NoProfile -ExecutionPolicy Bypass -File "mt5tools\tai_lich_su.ps1" -Terminal "%TERM_XM%"
pause
