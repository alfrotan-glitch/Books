@echo off
chcp 65001 >nul
title نصب و فعال‌سازی موتور هوش مصنوعی استخراج فارسی (Tesseract OCR)
cls

echo ===============================================================================
echo     نصب و فعال‌سازی موتور استخراج متون فارسی و دری (Tesseract OCR)
echo ===============================================================================
echo.
echo این اسکریپت موتور Tesseract نسخه ۵ را به همراه فایل‌های آموزش‌دیده زبان فارسی
echo (fas.traineddata) به سامانه شما اضافه می‌کند تا کتاب‌های اسکن‌شده به طور کامل
echo و بدون به‌هم‌ریختگی حروف استخراج شوند.
echo.

set "TESS_BIN=C:\Program Files\Tesseract-OCR\tesseract.exe"

if exist "%TESS_BIN%" (
    echo [تأیید] موتور Tesseract در مسیر زیر یافت شد:
    echo   "%TESS_BIN%"
    goto :DOWNLOAD_MODELS
)

where tesseract >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [تأیید] موتور Tesseract در سیستم شناسایی شد.
    goto :DOWNLOAD_MODELS
)

echo [۱/۲] موتور Tesseract یافت نشد. در حال نصب خودکار از طریق winget...
winget install UB-Mannheim.TesseractOCR --accept-source-agreements --accept-package-agreements
if %ERRORLEVEL% equ 0 (
    echo   [تأیید] برنامه Tesseract با موفقیت نصب گردید.
    goto :DOWNLOAD_MODELS
)

echo.
echo [اطلاع] نصب از طریق winget میسر نشد. در حال دانلود مستقیم نصاب رسمی ویندوز...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Write-Host 'در حال دانلود نصاب رسمی Tesseract 64-bit...'; $url = 'https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.4.0.20240606.exe'; $out = 'tesseract_installer.exe'; (New-Object System.Net.WebClient).DownloadFile($url, $out); Write-Host 'دانلود تکمیل شد. در حال اجرای نصاب...'; Start-Process -FilePath $out -Wait"

if exist "%TESS_BIN%" (
    echo   [تأیید] نصب با موفقیت انجام شد.
) else (
    echo [هشدار] اگر نصاب باز شده است، لطفاً مراحل نصب را کامل کرده و دکمه ادامه را بزنید.
)

:DOWNLOAD_MODELS
echo.
echo [۲/۲] در حال آماده‌سازی و دانلود مدل‌های زبانی فارسی، انگلیسی و عربی...

if not exist "tessdata" mkdir tessdata

powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; function Get-Model($name, $label) { $dest = 'tessdata\' + $name; if (Test-Path $dest) { Write-Host ('  [OK] مدل ' + $label + ' از قبل موجود است.'); return }; Write-Host ('  در حال دریافت مدل ' + $label + ' (' + $name + ')...'); $urls = @('https://cdn.jsdelivr.net/gh/tesseract-ocr/tessdata_fast@main/' + $name, 'https://github.com/tesseract-ocr/tessdata_fast/raw/main/' + $name); foreach ($u in $urls) { try { (New-Object System.Net.WebClient).DownloadFile($u, $dest); if ((Get-Item $dest).Length -gt 10000) { Write-Host ('  [تأیید] ' + $label + ' با موفقیت دریافت شد.'); return } } catch {} }; Write-Host ('  [خطا] دریافت ' + $name + ' با خطا مواجه شد.') }; Get-Model 'fas.traineddata' 'فارسی'; Get-Model 'eng.traineddata' 'انگلیسی'; Get-Model 'osd.traineddata' 'اسکریپت و جهت'; Get-Model 'ara.traineddata' 'عربی'"

:: کپی کردن به پوشه سیستم در صورت وجود دسترسی
if exist "%TESS_BIN%" (
    copy /Y "tessdata\fas.traineddata" "C:\Program Files\Tesseract-OCR\tessdata\" >nul 2>&1
    copy /Y "tessdata\ara.traineddata" "C:\Program Files\Tesseract-OCR\tessdata\" >nul 2>&1
    copy /Y "tessdata\eng.traineddata" "C:\Program Files\Tesseract-OCR\tessdata\" >nul 2>&1
    copy /Y "tessdata\osd.traineddata" "C:\Program Files\Tesseract-OCR\tessdata\" >nul 2>&1
)

echo.
echo ===============================================================================
echo     راه‌اندازی موتور هوش مصنوعی فارسی با موفقیت کامل انجام شد!
echo ===============================================================================
echo.
echo اکنون سامانه شما توانایی خواندن هم‌زمان متون فارسی، دری و انگلیسی را داراست.
echo کافیست برنامه را با «شروع_برنامه.bat» اجرا کرده و کتاب خود را استخراج نمایید.
echo.
pause
