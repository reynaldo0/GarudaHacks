@echo off
REM ============================================================================
REM PROJECT THEMIS - FastAPI Backend Stopper
REM Version: 1.0
REM ============================================================================

echo [INFO] Stopping FastAPI server...

REM Kill uvicorn process
taskkill /F /IM uvicorn.exe >nul 2>&1

REM Also try to kill by window title
taskkill /F /FI "WINDOWTITLE eq PROJECT THEMIS*" >nul 2>&1

echo [OK] Server stopped
pause
