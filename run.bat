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
        echo Please install Python 3.12 from https://www.python.org/
        echo Or run: winget install Python.Python.3.12
        echo Make sure to check "Add Python to PATH" during installation.
        echo.
        pause
        exit /b 1
    )
    set "PYTHON_CMD=py"
) else (
    set "PYTHON_CMD=python"
)

:: Detect Python version
for /f "tokens=2 delims= " %%v in ('%PYTHON_CMD% --version 2^>^&1') do set "PY_VER=%%v"
echo [INFO] Detected Python version: %PY_VER%

:: Create virtual environment if not present
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] First-time setup: Creating Python virtual environment...
    %PYTHON_CMD% -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip

    echo [INFO] Installing required dependencies...
    pip install -r requirements.txt

    :: Attempt PyAudio install if not already installed (works out-of-the-box on Python 3.10-3.12)
    python -c "import pyaudio" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [INFO] Checking audio hardware drivers...
        pip install pyaudio >nul 2>&1
        python -c "import pyaudio" >nul 2>&1
        if %ERRORLEVEL% NEQ 0 (
            echo.
            echo [ADVISORY] Microphone driver (PyAudio) requires Python 3.12 on Windows.
            echo Jarvis Web UI, AI Brain, and System Automations will run smoothly.
            echo To enable live Voice Microphone input, install Python 3.12:
            echo    winget install Python.Python.3.12
            echo.
        )
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
