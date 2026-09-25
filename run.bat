@echo off
setlocal EnableDelayedExpansion
title Digital Book Extraction Engine - Windows Pipeline

echo ===============================================================================
echo    DIGITAL BOOK EXTRACTION ENGINE & FORENSICS PIPELINE (PRODUCTION-GRADE)
echo    Windows-First & Multi-Engine OCR ^| Correct Reading Order ^& Layout Recovery
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

:: 4. Parse Command-Line Arguments
if "%~1"=="--ui" goto launch_ui
if "%~1"=="--server" goto launch_ui
if "%~1"=="--benchmark" goto run_bench
if "%~1"=="--inspect" goto run_inspect

:: Check if user passed a specific PDF path
if not "%~1"=="" (
    if exist "%~1" (
        echo [INFO] Processing specified file: %~1
        "%PYTHON_EXE%" -m src.cli process "%~1"
        goto finish
    )
)

:: 5. Check inbox/ directory for PDFs
set INBOX_COUNT=0
for %%f in (inbox\*.pdf) do (
    set /a INBOX_COUNT+=1
)

if !INBOX_COUNT! gtr 0 (
    echo [INFO] Found !INBOX_COUNT! PDF file^(s^) in inbox\. Starting automated extraction...
    echo.
    "%PYTHON_EXE%" -m src.cli process
    goto finish
) else (
    echo [INFO] No PDF files detected in 'inbox\'.
    echo.
    echo Options:
    echo   1. Place one or more PDF books into the 'inbox\' folder and re-run run.bat
    echo   2. Or launch the Web Dashboard now to upload and process files in your browser.
    echo.
    set /p CHOICE="Launch Web Dashboard now? (Y/N, default=Y): "
    if /i "!CHOICE!"=="N" (
        echo.
        echo Please drop your PDF book into 'inbox\' and double-click run.bat!
        pause
        exit /b 0
    )
    goto launch_ui
)

:launch_ui
echo [INFO] Launching Web Dashboard on http://localhost:8000 ...
echo Press Ctrl+C in this console to stop the server.
start http://localhost:8000
"%PYTHON_EXE%" -m src.cli serve --host 0.0.0.0 --port 8000
goto finish

:run_bench
echo [INFO] Running internal benchmark test suite...
"%PYTHON_EXE%" -m src.cli benchmark
goto finish

:run_inspect
"%PYTHON_EXE%" -m src.cli inspect %2 %3 %4
goto finish

:finish
echo.
echo ===============================================================================
echo Processing finished. Deliverables are saved in the 'output\' directory.
echo ===============================================================================
pause
exit /b 0
