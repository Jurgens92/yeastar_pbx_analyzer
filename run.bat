@echo off
title Yeastar

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH!
    echo Please install Python and try again.
    pause
    exit /b 1
)

:: Clear screen and show header
cls
echo ============================================
echo    Yeastar - Launcher
echo ============================================
echo.

:: Check if main.py exists
if not exist "main.py" (
    echo ERROR: main.py not found in current directory!
    echo Please make sure main.py is in the same folder as this batch file.
    pause
    exit /b 1
)

:: Run the application
echo Starting...
echo.
python main.py

:: Pause after execution so you can see any error messages
echo.
echo ============================================
echo Application has ended.
pause