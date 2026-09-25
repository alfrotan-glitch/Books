@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"
title ایجاد میانبر برنامه روی دسکتاپ (Windows Desktop Shortcut)

echo ===============================================================================
echo        ایجاد میانبر «سامانه استخراج متن کتاب» روی دسکتاپ ویندوز
echo ===============================================================================
echo.

set "TARGET_BAT=%~dp0شروع_برنامه.bat"
set "WORKING_DIR=%~dp0"
set "ICON_FILE=%~dp0assets\app_icon.ico"
set "SHORTCUT_FA=%USERPROFILE%\Desktop\سامانه استخراج کتاب.lnk"
set "SHORTCUT_EN=%USERPROFILE%\Desktop\Book Text Extractor.lnk"

echo در حال ساخت آیکون میانبر روی دسکتاپ...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ws = New-Object -ComObject WScript.Shell; " ^
    "$s = $ws.CreateShortcut('%SHORTCUT_FA%'); " ^
    "$s.TargetPath = '%TARGET_BAT%'; " ^
    "$s.WorkingDirectory = '%WORKING_DIR%'; " ^
    "if (Test-Path '%ICON_FILE%') { $s.IconLocation = '%ICON_FILE%' }; " ^
    "$s.Description = 'سامانه هوشمند استخراج متن کتاب از PDF'; " ^
    "$s.Save(); " ^
    "$s2 = $ws.CreateShortcut('%SHORTCUT_EN%'); " ^
    "$s2.TargetPath = '%TARGET_BAT%'; " ^
    "$s2.WorkingDirectory = '%WORKING_DIR%'; " ^
    "if (Test-Path '%ICON_FILE%') { $s2.IconLocation = '%ICON_FILE%' }; " ^
    "$s2.Description = 'Digital Book Text Extraction Engine'; " ^
    "$s2.Save();"

if %errorlevel% equ 0 (
    echo.
    echo [موفقیت] میانبر با موفقیت روی دسکتاپ شما ایجاد شد:
    echo   - Desktop\سامانه استخراج کتاب.lnk
    echo   - Desktop\Book Text Extractor.lnk
    echo.
    echo از این پس می‌توانید مستقیماً با دوبار کلیک روی این آیکون در دسکتاپ،
    echo برنامه را اجرا و محیط وب را باز کنید.
) else (
    echo.
    echo [خطا] در ایجاد خودکار میانبر خطایی رخ داد.
)

echo.
pause
exit /b 0
