@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo        Cyber Kavasam (சைபர் கவசம்) - Startup
echo        Citizen Scam Detection & Reporting Assistant
echo ========================================================

cd /d "%~dp0"

echo [1/4] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH. Please install Python 3.12+
    pause
    exit /b 1
)

echo [2/4] Verifying and installing requirements...
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo Warning: Pip install had warnings or failed. Proceeding with installed packages...
)

echo [3/4] Checking machine learning model artifacts...
if not exist "models\kavasam.joblib" (
    echo Model not found. Training model and building dataset...
    python data\build_dataset.py
    python -m app.train
) else (
    echo Model artifact found at models\kavasam.joblib
)

echo [4/4] Starting Waitress production WSGI server on 127.0.0.1:5000...
start "" http://127.0.0.1:5000

python -m waitress --listen=127.0.0.1:5000 --call app.server:create_app

pause
