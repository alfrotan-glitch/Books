@echo off
setlocal EnableDelayedExpansion
title Setup - Digital Book Extraction Engine

echo ===============================================================================
echo    SETUP WIZARD - DIGITAL BOOK EXTRACTION ENGINE (WINDOWS)
echo ===============================================================================
echo.

:: 1. Create Workspace Directories
echo [1/4] Initializing folder structure...
if not exist "inbox" mkdir "inbox"
if not exist "output" mkdir "output"
if not exist "debug" mkdir "debug"
if not exist "logs" mkdir "logs"
if not exist "checkpoints" mkdir "checkpoints"
echo   [OK] inbox\, output\, debug\, logs\, checkpoints\ created.

:: 2. Locate System Python
echo.
echo [2/4] Detecting Python installation...
set SYSTEM_PYTHON=
where py >nul 2>nul
if !errorlevel! equ 0 (
    set "SYSTEM_PYTHON=py -3"
) else (
    where python >nul 2>nul
    if !errorlevel! equ 0 (
        set "SYSTEM_PYTHON=python"
    ) else (
        echo [ERROR] Python 3.10 or newer was not detected in PATH!
        echo Please download and install Python from: https://www.python.org/downloads/
        echo IMPORTANT: Check the box "Add Python to PATH" during installation.
        pause
        exit /b 1
    )
)
echo   [OK] Python detected: %SYSTEM_PYTHON%

:: 3. Create Virtual Environment
echo.
echo [3/4] Creating virtual environment (.venv)...
if exist ".venv" (
    echo   [INFO] Existing .venv directory found. Re-using environment.
) else (
    %SYSTEM_PYTHON% -m venv .venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create .venv virtual environment!
        pause
        exit /b 1
    )
    echo   [OK] Created .venv.
)

:: 4. Install Dependencies
echo.
echo [4/4] Installing dependencies from requirements.txt...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo [ERROR] Failed to install requirements!
    pause
    exit /b 1
)

echo.
echo [VERIFICATION] Verifying installed packages...
.venv\Scripts\python.exe -c "import pymupdf, rapidocr_onnxruntime, cv2, PIL, fastapi; print('  [OK] Core libraries verified successfully!')"
if !errorlevel! neq 0 (
    echo [ERROR] Verification failed!
    pause
    exit /b 1
)

echo.
echo ===============================================================================
echo    SETUP COMPLETED SUCCESSFULLY!
echo ===============================================================================
echo.
echo Next Steps:
echo   1. Drop any PDF book into the 'inbox\' folder.
echo   2. Double-click 'run.bat' to begin automated extraction.
echo   3. Find your completed .txt and report files in the 'output\' folder!
echo.
pause
exit /b 0
