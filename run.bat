@echo off
title J.A.R.V.I.S - Stark Industries Voice Assistant
cd /d "%~dp0"

echo ===================================================
echo     STARK INDUSTRIES - J.A.R.V.I.S OS LAUNCHER
echo     Design and built by Satyaa Yadav
echo ===================================================
echo.

:: Check for Python installation
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python is not detected in your PATH.
        echo Please install Python 3.10+ from https://www.python.org/
        echo Make sure to check "Add Python to PATH" during installation.
        echo.
        pause
        exit /b 1
    )
    set "PYTHON_CMD=py"
) else (
    set "PYTHON_CMD=python"
)

:: Create virtual environment if not present
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] First-time setup: Creating Python virtual environment...
    %PYTHON_CMD% -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [INFO] Installing required dependencies...
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [WARNING] Some dependencies failed to install. Continuing...
    )
) else (
    call venv\Scripts\activate.bat
)

:: Launch Jarvis
echo [INFO] Engaging Jarvis Voice Assistant Protocol...
echo.
python jarvis.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [INFO] Jarvis session ended.
)
