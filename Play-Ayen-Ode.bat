@echo off
title Ayen-Ode Launcher
setlocal EnableDelayedExpansion

:: Set console output to UTF-8 for smooth line art rendering
chcp 65001 >nul

:: Define ANSI Escape Codes for Premium UI Styling
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do set "ESC=%%b"
set "GOLD=%ESC%[38;5;214m"
set "SLATE=%ESC%[38;5;244m"
set "DARK=%ESC%[38;5;238m"
set "CYAN=%ESC%[36m"
set "GREEN=%ESC%[32m"
set "RED=%ESC%[31m"
set "RESET=%ESC%[0m"
set "BOLD=%ESC%[1m"

cls
echo %SLATE%───────────────────────────────────────────────────────────────────%RESET%
echo %GOLD%%BOLD%
echo    █████╗ ██╗   ██╗███████╗███╗   ██╗     ██████╗ ██████╗ ███████╗
echo   ██╔══██╗╚██╗ ██╔╝██╔════╝████╗  ██║    ██╔═══██╗██╔══██╗██╔════╝
echo   ███████║ ╚████╔╝ █████╗  ██╔██╗ ██║    ██║   ██║██║  ██║█████╗  
echo   ██╔══██║  ╚██╔╝  ██╔══╝  ██║╚██╗██║    ██║   ██║██║  ██║██╔══╝  
echo   ██║  ██║   ██║   ███████╗██║ ╚████║    ╚██████╔╝██████╔╝███████╗
echo   ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═══╝     ╚═════╝ ╚═════╝ ╚══════╝
echo %RESET%
echo %SLATE%   Narrative RPG Engine %DARK%·%SLATE% High-Fidelity Desktop Client
echo ───────────────────────────────────────────────────────────────────%RESET%
echo.

:: Check Environment and Select Launch Target
if exist "dist\Ayen-Ode.exe" (
    echo %GOLD%[+] Found Standalone Executable:%RESET% %SLATE%dist\Ayen-Ode.exe%RESET%
    echo %SLATE%    Launching packaged production application...%RESET%
    echo.
    start "" "dist\Ayen-Ode.exe"
    goto success
)

if exist ".venv\Scripts\python.exe" (
    echo %GOLD%[+] Found Virtual Environment:%RESET% %SLATE%Local Python Developer Environment%RESET%
    echo %SLATE%    Booting Starlette app and opening WebView client...%RESET%
    echo.
    start "" ".venv\Scripts\python.exe" -m ayen_ode.desktop_launcher
    goto success
)

:: Error State: Missing Environment
echo %RED%%BOLD%[!] Error: Application Launch Environment Not Found%RESET%
echo.
echo %SLATE%To configure the project, please run setup first:%RESET%
echo   %CYAN%powershell -ExecutionPolicy Bypass -File scripts\setup.ps1%RESET%
echo.
pause
exit /b 1

:success
echo %GREEN%%BOLD%[✓] Ayen-Ode started successfully.%RESET%
echo %SLATE%    (This console window can now be safely closed)%RESET%
echo ───────────────────────────────────────────────────────────────────%RESET%
timeout /t 3 >nul
exit /b 0
