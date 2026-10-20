@echo off
rem BAT_THE_BRAIN.bat - BAT The Brain het suc tren may nha (20/10/2026).
rem Xoa co TAT_THE_BRAIN.co roi chay chay_toi_nay.bat (moi buoc, ca bo dieu phoi). Tham so chuyen tiep, vd:
rem    BAT_THE_BRAIN.bat -Den "07:00"
chcp 65001 >nul
cd /d "%~dp0.."
if exist "%~dp0TAT_THE_BRAIN.co" del /q "%~dp0TAT_THE_BRAIN.co"
echo [The Brain] BAT - chay het suc (uu tien Normal, MT5 theo RAM). Tat bang TAT_THE_BRAIN.bat
call "%~dp0chay_toi_nay.bat" %*
