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
set "YELLOW=%ESC%[33m"
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

:: Check if the virtual environment exists
if exist "%~dp0.venv\Scripts\pythonw.exe" (
    echo %GOLD%[+] Sweeping lingering background instances...%RESET%
    powershell -Command "Get-CimInstance Win32_Process -Filter 'Name = ''pythonw.exe'' or Name = ''python.exe''' -ErrorAction SilentlyContinue | Where-Object CommandLine -like '*ayen_ode*' | ForEach-Object { Stop-Process $_.ProcessId -Force }"
    
    echo %GOLD%[+] Launching Ayen-Ode from source...%RESET%
    echo %SLATE%    [Bypassing PyInstaller packaging extraction to prevent DLL bugs]%RESET%
    echo.
    
    rem Launch windowless Python loader and exit console instantly
    start "" "%~dp0.venv\Scripts\pythonw.exe" -m ayen_ode.desktop_launcher
    
    echo %GREEN%%BOLD%[✓] Launched successfully!%RESET%
    timeout /t 1 >nul
    exit /b 0
)

:no_environment
echo %RED%%BOLD%[!] Error: Application Launch Environment Not Found%RESET%
echo.
echo %SLATE%To configure the project, please run setup first:%RESET%
echo   %CYAN%powershell -ExecutionPolicy Bypass -File scripts\setup.ps1%RESET%
echo.
pause
exit /b 1
