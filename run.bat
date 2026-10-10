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
if errorlevel 1 goto find_py
set "PYTHON_CMD=python"
goto python_found

:find_py
where py >nul 2>&1
if errorlevel 1 goto no_python
set "PYTHON_CMD=py"
goto python_found

:no_python
echo [ERROR] Python is not installed or not in PATH.
echo Please install Python from https://www.python.org/
echo Or run in PowerShell: winget install Python.Python.3.12
echo Make sure to check Add Python to PATH during installation.
echo.
pause
exit /b 1

:python_found
:: 2. Create virtual environment if missing
if exist "venv\Scripts\python.exe" goto venv_ready
echo [INFO] Creating Python virtual environment...
%PYTHON_CMD% -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

:venv_ready
set "VENV_PYTHON=venv\Scripts\python.exe"

:: 3. Verify packages are installed in venv
%VENV_PYTHON% -c "import dotenv, rich, requests, psutil" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing required dependencies into virtual environment...
    %VENV_PYTHON% -m pip install --upgrade pip
    %VENV_PYTHON% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [INFO] Installing core packages directly...
        %VENV_PYTHON% -m pip install python-dotenv requests rich psutil edge-tts google-genai aiohttp tabulate Pillow SpeechRecognition
    )
    %VENV_PYTHON% -c "import pyaudio" >nul 2>&1
    if errorlevel 1 (
        %VENV_PYTHON% -m pip install pyaudio >nul 2>&1
    )
)

:: 4. Launch Jarvis using the venv python directly
echo [INFO] Engaging Jarvis Voice Assistant Protocol...
echo.
%VENV_PYTHON% jarvis.py %*

if errorlevel 1 (
    echo.
    echo [INFO] Jarvis session ended.
)
