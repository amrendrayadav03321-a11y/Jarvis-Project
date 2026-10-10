# J.A.R.V.I.S - Stark Industries Voice Assistant (PowerShell Launcher)
# Design and built by Satyaa Yadav

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "    STARK INDUSTRIES - J.A.R.V.I.S OS LAUNCHER" -ForegroundColor Yellow
Write-Host "    Design and built by Satyaa Yadav" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check for Python
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    $PythonCmd = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $PythonCmd) {
    Write-Host "[ERROR] Python is not detected in your PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.12: winget install Python.Python.3.12" -ForegroundColor Yellow
    Exit 1
}

$VenvPython = Join-Path $ScriptDir "venv\Scripts\python.exe"

# Create venv if missing
if (-not (Test-Path $VenvPython)) {
    Write-Host "[INFO] Creating Python virtual environment (venv)..." -ForegroundColor Cyan
    & $PythonCmd.Source -m venv venv
}

# Verify dependencies in venv
$check = & $VenvPython -c "import dotenv, rich, requests, psutil" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[INFO] Installing required dependencies..." -ForegroundColor Yellow
    & $VenvPython -m pip install --upgrade pip
    & $VenvPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        & $VenvPython -m pip install python-dotenv requests rich psutil edge-tts google-genai aiohttp tabulate Pillow SpeechRecognition
    }
}

# Launch Jarvis
Write-Host "[INFO] Engaging Jarvis Voice Assistant Protocol..." -ForegroundColor Green
Write-Host ""
& $VenvPython jarvis.py @args
