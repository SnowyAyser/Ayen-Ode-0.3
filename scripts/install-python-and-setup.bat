@echo off
title Ayen-Ode Setup
echo.
echo  Installing Python 3.12 (this may take a minute)...
echo.
winget install Python.Python.3.12 --silent --accept-source-agreements --accept-package-agreements
echo.
echo  Python install complete. Running Ayen-Ode setup...
echo.
:: Refresh PATH so the new python is found in this shell session
set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts"
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\setup.ps1"
pause
