@echo off
rem chay_toi_nay.bat - goi chay_toi_nay.ps1 (cac buoc 0-11 cua GIAO_VIEC_CLAUDE.md). KHONG tat may.
rem Vi du:  chay_toi_nay.bat            (tat ca buoc)
rem          chay_toi_nay.bat -Buoc "0,3,4"
rem          chay_toi_nay.bat -Buoc "5-8" -Den "06:30"
chcp 65001 >nul
setlocal
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0chay_toi_nay.ps1" %*
set RC=%ERRORLEVEL%
endlocal & exit /b %RC%
