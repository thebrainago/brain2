@echo off
rem Tho MT5 may nha: tu tao clone rieng D:\brain2_tho (lan dau), keo ban moi (ff-only), chay vong lap lay viec.
rem Dung: may_nha\CHAY_THO_MT5.cmd [--song-song [N]] [--den-gio 22:00] [--gio-chay 10] [--slot D:\mt5_tester\p1]
setlocal
set THO=%BRAIN_THO_DIR%
if "%THO%"=="" set THO=D:\brain2_tho
if not exist "%THO%\.git" (
  for /f "delims=" %%u in ('git -C "%~dp0.." remote get-url origin') do git clone "%%u" "%THO%"
)
if not exist "%THO%\.tho_mt5_clone" echo clone rieng cua tho - khong sua tay> "%THO%\.tho_mt5_clone"
cd /d "%THO%"
git pull --ff-only
:lap
python may_nha\tho_mt5.py %*
if "%errorlevel%"=="3" goto het
echo Tho dung (ma %errorlevel%) - khoi dong lai sau 60 giay. Ctrl+C de thoat.
timeout /t 60 /nobreak >nul
git pull --ff-only
goto lap
:het
echo Het khung gio chay - tho dung han.
