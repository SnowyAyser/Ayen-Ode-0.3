@echo off
title Ayen-Ode Server
cd /d "%~dp0"

:restart
echo.
echo  Starting Ayen-Ode...
echo  Press Ctrl+C to stop.
echo.
.venv\Scripts\python.exe -m ayen_ode

if %errorlevel% == 0 (
    echo.
    echo  Restarting...
    timeout /t 1 /nobreak >nul
    goto restart
)

echo.
echo  Server stopped (exit code %errorlevel%).
pause
