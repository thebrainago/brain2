@echo off
rem TAT_THE_BRAIN.bat - TAT EM The Brain (20/10/2026): dung phong viec moi, cho viec MT5 dang chay xong (toi da 20 phut),
rem roi chi dung dung cac PID ong dan da ghi trong thu muc log phien. KHONG dong terminal XM chinh, KHONG dong Claude.
rem    TAT_THE_BRAIN.bat            (cho toi da 30 phut)
rem    TAT_THE_BRAIN.bat -ChoPhut 5 (cho it hon)
chcp 65001 >nul
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0TAT_THE_BRAIN.ps1" %*
