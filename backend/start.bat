@echo off
REM ============================================================================
REM PROJECT THEMIS - FastAPI Backend Starter
REM Version: 1.0
REM ============================================================================

REM Set title
title PROJECT THEMIS - FastAPI Backend

REM Navigate to script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found
    pause
    exit /b 1
)

REM Install dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM Check if main.py exists
if not exist "main.py" (
    echo [ERROR] main.py not found
    pause
    exit /b 1
)

REM Load environment variables
if exist ".env" (
    echo [INFO] Loading .env file...
    for /f "tokens=1,* delims==" %%a in (.env) do (
        if not "%%a"=="" if not "%%a"=="#" (
            set "%%a=%%b"
        )
    )
    echo [OK] Environment variables loaded
)

REM Print banner
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo                    PROJECT THEMIS - FastAPI Backend
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo  Server  : http://localhost:8005
echo  Docs    : http://localhost:8005/docs
echo  ReDoc   : http://localhost:8005/redoc
echo  Health  : http://localhost:8005/api/v1/health
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Start FastAPI server with uvicorn
echo [INFO] Starting FastAPI server...
echo.
uvicorn main:app --host 0.0.0.0 --port 8005 --reload --log-level info

REM If server stops
echo.
echo [INFO] Server stopped
pause
