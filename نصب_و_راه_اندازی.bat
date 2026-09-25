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

:: ۲. بررسی پایتون سیستم (اولویت با نسخه‌های پایدار ۳.۱۲، ۳.۱۱ و ۳.۱۰)
echo.
echo [۲/۴] در حال بررسی نسخه پایتون...
set SYSTEM_PYTHON=
where py >nul 2>nul
if !errorlevel! equ 0 (
    py -3.12 -c "exit(0)" >nul 2>nul
    if !errorlevel! equ 0 (
        set "SYSTEM_PYTHON=py -3.12"
    ) else (
        py -3.11 -c "exit(0)" >nul 2>nul
        if !errorlevel! equ 0 (
            set "SYSTEM_PYTHON=py -3.11"
        ) else (
            py -3.10 -c "exit(0)" >nul 2>nul
            if !errorlevel! equ 0 (
                set "SYSTEM_PYTHON=py -3.10"
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
        echo لطفاً نسخه پایدار پایتون ۳.۱۲ را از نشانی زیر نصب نمایید:
        echo https://www.python.org/downloads/
        echo ** مهم: در مرحله اول نصب، حتماً گزینه "Add Python to PATH" را فعال کنید. **
        echo.
        pause
        exit /b 1
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

:: بررسی وضعیت RapidOCR
.venv\Scripts\python.exe -c "import rapidocr_onnxruntime" >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo -------------------------------------------------------------------------------
    echo [توجه در مورد نسخه پایتون]
    echo بخش‌های بازسازی متن، خوانش، جدول‌ها، دشارژ و وب‌سرور با موفقیت نصب شدند.
    echo پکیج RapidOCR نیازمند پایتون ۳.۱۰ تا ۳.۱۲ است. در پایتون ۳.۱۴ (نسخه پیش‌نمایش)
    echo چرخ‌های OnnxRuntime هنوز ارائه نشده است.
    echo برای استخراج کتاب‌های اسکن‌شده با OCR، پایتون ۳.۱۲ را نصب نمایید:
    echo https://www.python.org/downloads/
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
