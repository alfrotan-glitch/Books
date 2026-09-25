@echo off
setlocal EnableDelayedExpansion
title نرم‌افزار استخراج هوشمند متن کتاب از PDF

echo ===============================================================================
echo       سامانه هوشمند استخراج و بازسازی متن کتاب از PDF (محیط گرافیکی)
echo ===============================================================================
echo.
echo [1/3] در حال بررسی پیش‌نیازها و راه‌اندازی محیط...

:: 1. ایجاد پوشه‌های کاری
if not exist "inbox" mkdir "inbox"
if not exist "output" mkdir "output"
if not exist "debug" mkdir "debug"
if not exist "logs" mkdir "logs"
if not exist "checkpoints" mkdir "checkpoints"

:: 2. یافتن پایتون
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
            echo.
            echo [خطا] پایتون روی این سیستم ویندوز یافت نشد!
            echo لطفاً ابتدا پایتون را از آدرس https://www.python.org/downloads/ نصب نمایید
            echo و حتماً گزینه "Add Python to PATH" را هنگام نصب تیک بزنید.
            echo.
            pause
            exit /b 1
        )
    )
)

:: 3. راه‌اندازی اولیه در صورت عدم وجود محیط
if not exist ".venv\Scripts\python.exe" (
    echo [2/3] راه‌اندازی اولیه محیط مجازی اختصاصی...
    %PYTHON_EXE% -m venv .venv
    set "PYTHON_EXE=.venv\Scripts\python.exe"
    echo در حال نصب کتابخانه‌های لازم...
    "%PYTHON_EXE%" -m pip install --upgrade pip
    "%PYTHON_EXE%" -m pip install -r requirements.txt
    echo [تأیید] نصب کتابخانه‌ها با موفقیت انجام شد.
) else (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
)

:: 4. اجرای سرور محیط گرافیکی و باز کردن مرورگر برای کاربر
echo.
echo [3/3] در حال باز کردن محیط کاربری در مرورگر شما...
echo آدرس سامانه: http://localhost:8000
echo.

start http://localhost:8000
"%PYTHON_EXE%" -m src.cli serve --host 0.0.0.0 --port 8000

pause
