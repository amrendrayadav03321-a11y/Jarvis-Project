@echo off
title J.A.R.V.I.S - Stark Industries Voice Assistant
cd /d "%~dp0"

echo ===================================================
echo     STARK INDUSTRIES - J.A.R.V.I.S OS LAUNCHER
echo     Design and built by Satyaa Yadav
echo ===================================================
echo.

:: 1. Detect Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python is not installed or not in PATH.
        echo Please install Python from https://www.python.org/
        echo Or run in PowerShell: winget install Python.Python.3.12
        echo Make sure to check "Add Python to PATH" during installation.
        echo.
        pause
        exit /b 1
    )
    set "PYTHON_CMD=py"
) else (
    set "PYTHON_CMD=python"
)

:: 2. Create virtual environment if missing
if not exist "venv\Scripts\python.exe" (
    echo [INFO] Creating Python virtual environment (venv)...
    %PYTHON_CMD% -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

set "VENV_PYTHON=venv\Scripts\python.exe"

:: 3. Verify packages are installed (auto-repair if previous install failed)
%VENV_PYTHON% -c "import dotenv, rich, requests, psutil" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Installing required dependencies into virtual environment...
    %VENV_PYTHON% -m pip install --upgrade pip
    
    :: Install from requirements.txt
    %VENV_PYTHON% -m pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [INFO] Installing core packages directly...
        %VENV_PYTHON% -m pip install python-dotenv requests rich psutil edge-tts google-genai aiohttp tabulate Pillow SpeechRecognition
    )

    :: Check audio driver
    %VENV_PYTHON% -c "import pyaudio" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        %VENV_PYTHON% -m pip install pyaudio >nul 2>&1
    )
)

:: 4. Launch Jarvis using the venv python directly
echo [INFO] Engaging Jarvis Voice Assistant Protocol...
echo.
%VENV_PYTHON% jarvis.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [INFO] Jarvis session ended.
)
