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

:: ─── Smart Auto-Rebuild Check ──────────────────────────────────────────
:: Compute a hash of all source and static files. If it differs from the
:: last build's hash, rebuild the .exe automatically before launching.

set "HASH_FILE=%~dp0.build_hash"
set "EXE_DIST=%~dp0dist\Ayen-Ode.exe"
set "EXE_ROOT=%~dp0Ayen-Ode.exe"
set "NEEDS_BUILD=0"

:: Check if exe exists at all
if not exist "%EXE_DIST%" (
    if not exist "%EXE_ROOT%" (
        :: No exe anywhere — check if we can build or fall back to source
        if exist "%~dp0.venv-build\Scripts\python.exe" (
            set "NEEDS_BUILD=1"
            echo %YELLOW%[!] No executable found. Building for the first time...%RESET%
        ) else if exist "%~dp0.venv\Scripts\python.exe" (
            echo %GOLD%[+] No executable found. Running from source instead.%RESET%
            goto run_from_source
        ) else (
            goto no_environment
        )
    )
)

:: Compute current source hash using the shared script (kept in lockstep with
:: the exe's self-update check in src\ayen_ode\updater.py).
echo %SLATE%    Checking for source changes...%RESET%
for /f "delims=" %%H in ('powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\source_hash.ps1" -RepoRoot "%~dp0."') do set "CURRENT_HASH=%%H"

if "%CURRENT_HASH%"=="ERROR" (
    echo %SLATE%    Could not compute source hash, skipping rebuild check.%RESET%
    goto skip_rebuild
)

:: Read the stored hash from the last build
set "STORED_HASH="
if exist "%HASH_FILE%" (
    set /p STORED_HASH=<"%HASH_FILE%"
)

:: Compare
if "%CURRENT_HASH%"=="%STORED_HASH%" (
    echo %GREEN%    No changes detected since last build. Skipping rebuild.%RESET%
    goto skip_rebuild
)

:: Hashes differ — need to rebuild
set "NEEDS_BUILD=1"
if defined STORED_HASH (
    echo %YELLOW%[~] Source files changed since last build. Auto-rebuilding...%RESET%
) else (
    echo %YELLOW%[~] No build hash found. Building to ensure exe is up to date...%RESET%
)

:skip_rebuild
if "%NEEDS_BUILD%"=="0" goto launch_exe

:: ─── Auto-Rebuild ──────────────────────────────────────────────────────
echo.
echo %GOLD%%BOLD%    ╭─────────────────────────────────────╮%RESET%
echo %GOLD%%BOLD%    │   Rebuilding Ayen-Ode.exe ...       │%RESET%
echo %GOLD%%BOLD%    ╰─────────────────────────────────────╯%RESET%
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\build_exe.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo %RED%%BOLD%[!] Build failed. Attempting to run from source instead...%RESET%
    echo.
    if exist "%~dp0.venv\Scripts\python.exe" goto run_from_source
    echo %RED%[!] No fallback available. Please fix build errors and try again.%RESET%
    pause
    exit /b 1
)

:: Store the new hash
echo %CURRENT_HASH%> "%HASH_FILE%"
echo.
echo %GREEN%%BOLD%[✓] Build complete. Hash saved.%RESET%
echo.

:: ─── Launch ────────────────────────────────────────────────────────────
:launch_exe
if exist "%EXE_DIST%" (
    echo %GOLD%[+] Launching:%RESET% %SLATE%dist\Ayen-Ode.exe%RESET%
    echo.
    start "" "%EXE_DIST%"
    goto success
)

if exist "%EXE_ROOT%" (
    echo %GOLD%[+] Launching:%RESET% %SLATE%Ayen-Ode.exe%RESET%
    echo.
    start "" "%EXE_ROOT%"
    goto success
)

:: Exe still missing after build — fall back to source
echo %YELLOW%[!] Exe not found after build. Falling back to source...%RESET%

:run_from_source
if exist "%~dp0.venv\Scripts\python.exe" (
    echo %GOLD%[+] Running from source:%RESET% %SLATE%.venv\Scripts\python.exe -m ayen_ode.desktop_launcher%RESET%
    echo.
    start "" "%~dp0.venv\Scripts\python.exe" -m ayen_ode.desktop_launcher
    goto success
)

:no_environment
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
