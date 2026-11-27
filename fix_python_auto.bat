@echo off
REM ============================================================
REM AUTOMATIC FIX: Windows AppStore Python to Official Python
REM ============================================================
REM This script removes AppStore Python 3.13 and installs official Python 3.11
REM Run as Administrator

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo Automatic Python Installation Fix
echo ============================================================
echo.
echo This will:
echo 1. Uninstall AppStore Python 3.13
echo 2. Download official Python 3.11.9
echo 3. Install it with PATH configured
echo.
pause

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run this script as Administrator
    echo Right-click Command Prompt or PowerShell and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/4] Uninstalling AppStore Python 3.13...
REM Try to uninstall via winget (if available)
winget uninstall Python.Python.3.13 -e --silent 2>nul
if errorlevel 1 (
    echo WARNING: Could not auto-uninstall AppStore Python
    echo Please manually uninstall:
    echo   Settings ^> Apps ^> Installed apps ^> Search "Python" ^> Uninstall
    echo.
    pause
)

echo.
echo [2/4] Downloading official Python 3.11.9...
cd /d "%TEMP%"

REM Download Python installer
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python-3.11.9-amd64.exe'" 2>nul

if not exist python-3.11.9-amd64.exe (
    echo ERROR: Failed to download Python
    echo Please download manually from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Downloaded successfully!

echo.
echo [3/4] Installing official Python 3.11.9...
echo Please follow the installer:
echo   - CHECK "Add Python to PATH" (CRITICAL!)
echo   - Click "Install Now"
echo.
pause

REM Run installer
python-3.11.9-amd64.exe /quiet PrependPath=1

REM Wait for installation
timeout /t 15

echo.
echo [4/4] Verifying installation...
python --version

REM Check if installation successful
python --version 2>nul | find "3.11" >nul
if errorlevel 1 (
    echo.
    echo WARNING: Python 3.11 not found in PATH
    echo Please verify installation and restart Command Prompt
    pause
    exit /b 1
)

echo.
echo ============================================================
echo SUCCESS! Python 3.11.9 installed!
echo ============================================================
echo.
echo Next steps:
echo 1. CLOSE THIS WINDOW
echo 2. OPEN NEW PowerShell/Command Prompt
echo 3. Run these commands:
echo.
echo cd D:\agent\snowflake_query_optimizer
echo rmdir /s /q venv
echo python -m venv venv
echo venv\Scripts\activate
echo pip install -r requirements.txt
echo python main.py health-check
echo.
pause
