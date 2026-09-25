@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
title Create Windows Desktop Shortcut

echo ===============================================================================
echo     CREATE DESKTOP SHORTCUT - DIGITAL BOOK TEXT EXTRACTION ENGINE
echo ===============================================================================
echo.

set "TARGET_BAT=%~dp0run.bat"
set "WORKING_DIR=%~dp0"
set "ICON_FILE=%~dp0assets\app_icon.ico"
set "SHORTCUT_PATH=%USERPROFILE%\Desktop\Book Text Extractor.lnk"

echo Creating shortcut on Windows Desktop...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ws = New-Object -ComObject WScript.Shell; " ^
    "$s = $ws.CreateShortcut('%SHORTCUT_PATH%'); " ^
    "$s.TargetPath = '%TARGET_BAT%'; " ^
    "$s.WorkingDirectory = '%WORKING_DIR%'; " ^
    "if (Test-Path '%ICON_FILE%') { $s.IconLocation = '%ICON_FILE%' }; " ^
    "$s.Description = 'Digital Book Text Extraction Engine (GUI & Automation)'; " ^
    "$s.Save();"

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Desktop shortcut created successfully:
    echo   %SHORTCUT_PATH%
    echo.
    echo You can now launch the application directly from your Desktop!
) else (
    echo.
    echo [ERROR] Failed to create desktop shortcut automatically.
)

echo.
pause
exit /b 0
