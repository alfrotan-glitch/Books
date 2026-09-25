@echo off
setlocal EnableDelayedExpansion
title Digital Book Extraction Engine - UI & Automation

echo ===============================================================================
echo    DIGITAL BOOK EXTRACTION ENGINE & FORENSICS PIPELINE (PRODUCTION-GRADE)
echo    Graphical Web Interface for Non-Technical Users ^& One-Click Execution
echo ===============================================================================
echo.

:: 1. Ensure required directories exist
if not exist "inbox" mkdir "inbox"
if not exist "output" mkdir "output"
if not exist "debug" mkdir "debug"
if not exist "logs" mkdir "logs"
if not exist "checkpoints" mkdir "checkpoints"

:: 2. Locate Python binary
set PYTHON_EXE=
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    where py >nul 2>nul
    if !errorlevel! equ 0 (
        set "PYTHON_EXE=py -3"
    ) else (
        where python >nul 2>nul
        if !errorlevel! equ 0 (
            set "PYTHON_EXE=python"
        ) else (
            echo [ERROR] Python is not installed or not in PATH!
            echo Please install Python 3.10+ from https://www.python.org/
            echo Make sure to check "Add Python to PATH" during installation.
            pause
            exit /b 1
        )
    )
)

:: 3. Check / Auto-Setup Virtual Environment if missing
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] First-time setup: Initializing virtual environment in .venv...
    %PYTHON_EXE% -m venv .venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    set "PYTHON_EXE=.venv\Scripts\python.exe"
    echo [INFO] Installing required dependencies from requirements.txt...
    "%PYTHON_EXE%" -m pip install --upgrade pip
    "%PYTHON_EXE%" -m pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo [ERROR] Dependency installation encountered errors!
        pause
        exit /b 1
    )
    echo [SUCCESS] Environment setup completed successfully!
    echo.
) else (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
)

:: 4. Check CLI arguments (for power users)
if "%~1"=="--cli" goto run_cli
if "%~1"=="--benchmark" goto run_bench
if "%~1"=="--inspect" goto run_inspect

:: 5. Default Non-Technical Mode: Launch Web Dashboard & Open Browser
echo [INFO] Launching Graphical Dashboard for non-technical users...
echo [INFO] Opening http://localhost:8000 in your browser...
echo.
start http://localhost:8000
"%PYTHON_EXE%" -m src.cli serve --host 0.0.0.0 --port 8000
goto finish

:run_cli
echo [INFO] Running in Command-Line Mode...
"%PYTHON_EXE%" -m src.cli process %2 %3
goto finish

:run_bench
echo [INFO] Running internal benchmark test suite...
"%PYTHON_EXE%" -m src.cli benchmark
goto finish

:run_inspect
"%PYTHON_EXE%" -m src.cli inspect %2 %3 %4
goto finish

:finish
pause
exit /b 0
