@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
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

:: 2. Locate System Python (explicitly look for Python 3.12 / 3.11 first)
echo.
echo [2/4] Detecting Python installation...
set SYSTEM_PYTHON=

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "SYSTEM_PYTHON="%LOCALAPPDATA%\Programs\Python\Python312\python.exe""
) else if exist "C:\Program Files\Python312\python.exe" (
    set "SYSTEM_PYTHON="C:\Program Files\Python312\python.exe""
) else if exist "%ProgramFiles%\Python312\python.exe" (
    set "SYSTEM_PYTHON="%ProgramFiles%\Python312\python.exe""
) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "SYSTEM_PYTHON="%LOCALAPPDATA%\Programs\Python\Python311\python.exe""
) else if exist "C:\Program Files\Python311\python.exe" (
    set "SYSTEM_PYTHON="C:\Program Files\Python311\python.exe""
) else (
    where py >nul 2>nul
    if !errorlevel! equ 0 (
        py -3.12 -V >nul 2>nul
        if !errorlevel! equ 0 (
            set "SYSTEM_PYTHON=py -3.12"
        ) else (
            py -3.11 -V >nul 2>nul
            if !errorlevel! equ 0 (
                set "SYSTEM_PYTHON=py -3.11"
            ) else (
                set "SYSTEM_PYTHON=py -3"
            )
        )
    ) else (
        where python >nul 2>nul
        if !errorlevel! equ 0 (
            set "SYSTEM_PYTHON=python"
        ) else (
            echo [ERROR] Python was not detected in PATH!
            echo Please install Python 3.12 from: https://www.python.org/downloads/
            pause
            exit /b 1
        )
    )
)
echo   [OK] Python detected: %SYSTEM_PYTHON%

:: 3. Create Virtual Environment
echo.
echo [3/4] Creating virtual environment (.venv)...
if exist ".venv" (
    echo   [INFO] Re-creating .venv with detected Python (%SYSTEM_PYTHON%)...
    rmdir /s /q ".venv" >nul 2>&1
)
%SYSTEM_PYTHON% -m venv .venv
if !errorlevel! neq 0 (
    echo [ERROR] Failed to create .venv virtual environment!
    pause
    exit /b 1
)
echo   [OK] Created .venv.

:: 4. Install Dependencies
echo.
echo [4/4] Installing dependencies...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt

:: Check if rapidocr installed or if Python 3.14 was used
.venv\Scripts\python.exe -c "import rapidocr_onnxruntime" >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo -------------------------------------------------------------------------------
    echo [NOTE ON PYTHON VERSION]
    echo Core extraction, reading order, and dashboard installed successfully!
    echo RapidOCR requires Python 3.10 - 3.12. If running on Python 3.14 (pre-release),
    echo onnxruntime wheels are not yet published by Microsoft for Python 3.14.
    echo To enable scanned book OCR, please install Python 3.12:
    echo https://www.python.org/downloads/
    echo -------------------------------------------------------------------------------
    echo.
)

echo.
echo [VERIFICATION] Verifying installed packages...
.venv\Scripts\python.exe -c "import pymupdf, cv2, PIL, fastapi; print('  [OK] Core libraries verified successfully!')"
if !errorlevel! neq 0 (
    echo [ERROR] Verification failed!
    pause
    exit /b 1
)

:: 5. Create Desktop Shortcut
echo.
echo [SHORTCUT] Creating desktop shortcut...
set "TARGET_BAT=%~dp0run.bat"
set "WORKING_DIR=%~dp0"
set "ICON_FILE=%~dp0assets\app_icon.ico"
set "SHORTCUT_PATH=%USERPROFILE%\Desktop\Book Text Extractor.lnk"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ws = New-Object -ComObject WScript.Shell; " ^
    "$s = $ws.CreateShortcut('%SHORTCUT_PATH%'); " ^
    "$s.TargetPath = '%TARGET_BAT%'; " ^
    "$s.WorkingDirectory = '%WORKING_DIR%'; " ^
    "if (Test-Path '%ICON_FILE%') { $s.IconLocation = '%ICON_FILE%' }; " ^
    "$s.Description = 'Digital Book Text Extraction Engine'; " ^
    "$s.Save();" >nul 2>&1

if exist "%SHORTCUT_PATH%" (
    echo   [OK] Desktop shortcut created: %SHORTCUT_PATH%
)

echo.
echo ===============================================================================
echo    SETUP COMPLETED SUCCESSFULLY!
echo ===============================================================================
echo.
echo Next Steps:
echo   1. Double-click the 'Book Text Extractor' icon on your Desktop or run 'run.bat'
echo   2. Drop any PDF book into the 'inbox\' folder (or upload via Web UI)
echo   3. Click 'Start Extraction' and view text / reports in real time!
echo.
pause
exit /b 0
