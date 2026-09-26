@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"
title نصب و راه‌اندازی سامانه استخراج هوشمند کتاب

echo ===============================================================================
echo     نصب و راه‌اندازی سامانه استخراج و بازسازی متن کتاب (محیط ویندوز)
echo ===============================================================================
echo.

:: ۱. ساخت پوشه‌های کاری
echo [۱/۴] در حال ساخت ساختار پوشه‌های کاری...
if not exist "inbox" mkdir "inbox"
if not exist "output" mkdir "output"
if not exist "debug" mkdir "debug"
if not exist "logs" mkdir "logs"
if not exist "checkpoints" mkdir "checkpoints"
echo   [تأیید] پوشه‌های inbox، output، logs و checkpoints آماده شدند.

:: ۲. بررسی پایتون سیستم (جستجوی صریح پایتون ۳.۱۳، ۳.۱۲ و ۳.۱۱ پایدار)
echo.
echo [۲/۴] در حال بررسی نسخه پایتون...
set SYSTEM_PYTHON=

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set "SYSTEM_PYTHON="%LOCALAPPDATA%\Programs\Python\Python313\python.exe""
) else if exist "C:\Program Files\Python313\python.exe" (
    set "SYSTEM_PYTHON="C:\Program Files\Python313\python.exe""
) else if exist "%ProgramFiles%\Python313\python.exe" (
    set "SYSTEM_PYTHON="%ProgramFiles%\Python313\python.exe""
) else if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
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
        py -3.13 -V >nul 2>nul
        if !errorlevel! equ 0 (
            set "SYSTEM_PYTHON=py -3.13"
        ) else (
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
        )
    ) else (
        where python >nul 2>nul
        if !errorlevel! equ 0 (
            set "SYSTEM_PYTHON=python"
        ) else (
            echo.
            echo [خطا] پایتون روی این سیستم ویندوز یافت نشد!
            echo لطفاً نسخه پایتون را از نشانی https://www.python.org/downloads/ نصب نمایید.
            pause
            exit /b 1
        )
    )
)
echo   [تأیید] پایتون شناسایی شد: %SYSTEM_PYTHON%

:: ۳. ایجاد محیط مجازی
echo.
echo [۳/۴] راه‌اندازی محیط مجازی اختصاصی (.venv)...
if exist ".venv" (
    echo   [اطلاع] بازسازی محیط مجازی با نسخه بهینه پایتون...
    rmdir /s /q ".venv" >nul 2>&1
)
%SYSTEM_PYTHON% -m venv .venv
if !errorlevel! neq 0 (
    echo [خطا] ساخت محیط مجازی ناموفق بود!
    pause
    exit /b 1
)
echo   [تأیید] محیط مجازی .venv ایجاد شد.

:: ۴. نصب کتابخانه‌ها
echo.
echo [۴/۴] در حال نصب پیش‌نیازها و ماژول‌های پردازش اسناد...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo در حال نصب موتور هوش مصنوعی RapidOCR و OnnxRuntime...
.venv\Scripts\python.exe -m pip install onnxruntime >nul 2>&1
.venv\Scripts\python.exe -m pip install --ignore-requires-python "rapidocr-onnxruntime>=1.3.0" >nul 2>&1

:: بررسی وضعیت RapidOCR
.venv\Scripts\python.exe -c "import rapidocr_onnxruntime" >nul 2>&1
if !errorlevel! equ 0 (
    echo   [تأیید] موتور هوش مصنوعی RapidOCR با موفقیت فعال شد.
) else (
    echo.
    echo -------------------------------------------------------------------------------
    echo [اطلاع در مورد OCR]
    echo اجزای استخراج متن، خوانش، جدول‌ها، دشارژ و وب‌سرور با موفقیت نصب شدند.
    echo در پایتون ۳.۱۳، موتور RapidOCR فعال است؛ در پایتون ۳.۱۴ (نسخه آزمایشی)،
    echo چرخ‌های OnnxRuntime هنوز توسط مایکروسافت ارائه نشده است.
    echo -------------------------------------------------------------------------------
    echo.
)

:: ۵. ایجاد خودکار آیکون روی دسکتاپ
echo.
echo [میانبر] ایجاد میانبر مستقیم برنامه روی دسکتاپ ویندوز...
set "TARGET_BAT=%~dp0شروع_برنامه.bat"
set "WORKING_DIR=%~dp0"
set "ICON_FILE=%~dp0assets\app_icon.ico"
set "SHORTCUT_FA=%USERPROFILE%\Desktop\سامانه استخراج کتاب.lnk"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ws = New-Object -ComObject WScript.Shell; " ^
    "$s = $ws.CreateShortcut('%SHORTCUT_FA%'); " ^
    "$s.TargetPath = '%TARGET_BAT%'; " ^
    "$s.WorkingDirectory = '%WORKING_DIR%'; " ^
    "if (Test-Path '%ICON_FILE%') { $s.IconLocation = '%ICON_FILE%' }; " ^
    "$s.Description = 'سامانه هوشمند استخراج متن کتاب از PDF'; " ^
    "$s.Save();" >nul 2>&1

echo.
echo ===============================================================================
echo     راه‌اندازی با موفقیت کامل به پایان رسید!
echo ===============================================================================
echo.
echo نحوه استفاده:
echo   ۱. روی آیکون «سامانه استخراج کتاب» روی دسکتاپ خود دوبار کلیک کنید
echo      یا فایل «شروع_برنامه.bat» را اجرا نمایید.
echo   ۲. فایل‌های PDF خود را داخل پوشه inbox بیندازید یا از طریق محیط وب آپلود کنید.
echo   ۳. خروجی متن شسته‌رفته و گزارش کیفیت در پوشه output در دسترس شما خواهد بود.
echo.
pause
exit /b 0
