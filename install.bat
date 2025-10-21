@echo off
REM SSCS Weekly Tracker - Installation Script for Windows

echo ============================================================
echo SSCS Weekly Tracker - Installation
echo ============================================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python 3.8 or higher from python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found
echo.

REM Check pip
echo Checking pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip not found
    echo Please reinstall Python with pip
    pause
    exit /b 1
)
echo [OK] pip found
echo.

REM Install Python packages
echo Installing Python packages...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python packages
    pause
    exit /b 1
)
echo [OK] Python packages installed
echo.

REM Check Firefox
echo Checking Firefox...
where firefox >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Firefox not found
    echo Please download from: https://www.mozilla.org/firefox/
) else (
    echo [OK] Firefox found
)
echo.

REM Check geckodriver
echo Checking geckodriver...
where geckodriver >nul 2>&1
if errorlevel 1 (
    echo [WARNING] geckodriver not found
    echo Download from: https://github.com/mozilla/geckodriver/releases
    echo Extract geckodriver.exe to a folder in your PATH
) else (
    echo [OK] geckodriver found
)
echo.

REM Create .env if not exists
if not exist ".env" (
    echo Creating .env file...
    copy .env.template .env >nul
    echo [OK] .env created from template
    echo [WARNING] IMPORTANT: Edit .env and add your SSCS credentials!
) else (
    echo [OK] .env already exists
)
echo.

REM Create directories
echo Creating directories...
if not exist "exports" mkdir exports
if not exist "backups" mkdir backups
if not exist "logs" mkdir logs
echo [OK] Directories created (exports, backups, logs)
echo.

REM Check for Weekly Tracker
if not exist "Weekly Tracker.xlsx" (
    echo [WARNING] Weekly Tracker.xlsx not found
    echo Please place your tracker file in this folder before running
) else (
    echo [OK] Weekly Tracker.xlsx found
)
echo.

REM Test configuration
echo Testing configuration...
python test_week_calc.py
echo.

REM Summary
echo ============================================================
echo Installation Summary
echo ============================================================
echo.
echo Next Steps:
echo.
echo 1. Edit .env file with your credentials:
echo    notepad .env
echo.
echo 2. Place Weekly Tracker.xlsx in this folder
echo.
echo 3. Test the script:
echo    run_sscs_update.bat
echo.
echo 4. If test succeeds, set up scheduling:
echo    See SCHEDULER_SETUP.md for detailed instructions
echo.
echo ============================================================
echo Installation complete!
echo ============================================================
echo.
pause
