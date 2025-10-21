@echo off
REM SSCS Weekly Tracker Update - Windows Batch Script
REM Double-click this file to run the update manually

cd /d "%~dp0"

echo ============================================================
echo SSCS Weekly Tracker Update
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python or add it to your PATH
    echo.
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found
    echo Please copy .env.template to .env and add your credentials
    echo.
    pause
    exit /b 1
)

REM Check if Weekly Tracker exists
if not exist "Weekly Tracker.xlsx" (
    echo ERROR: Weekly Tracker.xlsx not found
    echo Please place your tracker file in this folder
    echo.
    pause
    exit /b 1
)

echo Starting update...
echo.

REM Run the main script
python main.py

echo.
echo ============================================================
echo Update completed. Check logs folder for details.
echo ============================================================
echo.
pause
