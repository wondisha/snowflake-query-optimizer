@echo off
REM Automated Python Installation Script for Snowflake Query Optimizer
REM This script will download and install official Python from python.org

echo ============================================================
echo Installing Official Python for Snowflake Query Optimizer
echo ============================================================
echo.

REM Step 1: Check if Python is installed
echo [STEP 1] Checking current Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    goto :error
)

REM Step 2: Download Python 3.11.9 (stable, no AppStore restrictions)
echo.
echo [STEP 2] Downloading Official Python 3.11.9...
echo Note: You will need to install this manually from the downloaded file
echo Downloading to: %USERPROFILE%\Downloads\python-3.11.9-amd64.exe
echo.

curl -L https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe -o "%USERPROFILE%\Downloads\python-3.11.9-amd64.exe"

if exist "%USERPROFILE%\Downloads\python-3.11.9-amd64.exe" (
    echo.
    echo [SUCCESS] Downloaded Python installer
    echo.
    echo ============================================================
    echo NEXT STEPS (Manual):
    echo ============================================================
    echo.
    echo 1. Open: %USERPROFILE%\Downloads\python-3.11.9-amd64.exe
    echo.
    echo 2. When installer opens:
    echo    - CHECK "Add Python to PATH" (important!)
    echo    - Click "Install Now"
    echo.
    echo 3. After installation, RESTART PowerShell/Command Prompt
    echo.
    echo 4. Run these commands in snowflake_query_optimizer directory:
    echo    rmdir /s venv
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo    pip install -r requirements.txt
    echo.
    echo 5. Test with:
    echo    python main.py health-check
    echo.
    echo ============================================================
    echo.
    pause
) else (
    echo ERROR: Failed to download Python installer
    echo.
    echo Manual download: https://www.python.org/downloads/
    echo Select: Python 3.11.9 Windows Installer (64-bit)
    goto :error
)

goto :end

:error
echo.
echo INSTALLATION FAILED
echo.
echo Manual steps:
echo 1. Visit https://www.python.org/downloads/
echo 2. Download Python 3.11.9 (Windows Installer, 64-bit)
echo 3. Install with "Add Python to PATH" checked
echo 4. Run: python -m venv venv
echo.
pause
exit /b 1

:end
echo Done!
pause
