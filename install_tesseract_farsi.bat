@echo off
chcp 65001 >nul
title Install Persian/Dari OCR Engine (Tesseract 5)
cls

echo ===============================================================================
echo     Install and Configure Persian / Dari OCR Engine (Tesseract 5)
echo ===============================================================================
echo.

set "TESS_BIN=C:\Program Files\Tesseract-OCR\tesseract.exe"

if exist "%TESS_BIN%" (
    echo [OK] Tesseract detected at:
    echo   "%TESS_BIN%"
    goto :DOWNLOAD_MODELS
)

where tesseract >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] Tesseract detected in system PATH.
    goto :DOWNLOAD_MODELS
)

echo [1/2] Tesseract not found. Installing via winget...
winget install UB-Mannheim.TesseractOCR --accept-source-agreements --accept-package-agreements
if %ERRORLEVEL% equ 0 (
    echo   [OK] Tesseract installed successfully.
    goto :DOWNLOAD_MODELS
)

echo.
echo [INFO] Winget installation skipped. Downloading official installer...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Write-Host 'Downloading official 64-bit Tesseract installer...'; $url = 'https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.4.0.20240606.exe'; $out = 'tesseract_installer.exe'; (New-Object System.Net.WebClient).DownloadFile($url, $out); Write-Host 'Download complete. Running installer...'; Start-Process -FilePath $out -Wait"

if exist "%TESS_BIN%" (
    echo   [OK] Installation completed.
)

:DOWNLOAD_MODELS
echo.
echo [2/2] Downloading Persian, Arabic, and English trained models...

if not exist "tessdata" mkdir tessdata

powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $f='tessdata\fas.traineddata'; if (-not (Test-Path $f)) { Write-Host 'Downloading Persian model (fas.traineddata)...'; (New-Object System.Net.WebClient).DownloadFile('https://github.com/tesseract-ocr/tessdata_fast/raw/main/fas.traineddata', $f); Write-Host 'Persian model downloaded.' } else { Write-Host 'Persian model already exists.' }"

powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $f='tessdata\ara.traineddata'; if (-not (Test-Path $f)) { Write-Host 'Downloading Arabic model (ara.traineddata)...'; (New-Object System.Net.WebClient).DownloadFile('https://github.com/tesseract-ocr/tessdata_fast/raw/main/ara.traineddata', $f) } else { Write-Host 'Arabic model already exists.' }"

powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $f='tessdata\eng.traineddata'; if (-not (Test-Path $f)) { Write-Host 'Downloading English model (eng.traineddata)...'; (New-Object System.Net.WebClient).DownloadFile('https://github.com/tesseract-ocr/tessdata_fast/raw/main/eng.traineddata', $f) } else { Write-Host 'English model already exists.' }"

if exist "%TESS_BIN%" (
    copy /Y "tessdata\fas.traineddata" "C:\Program Files\Tesseract-OCR\tessdata\" >nul 2>&1
    copy /Y "tessdata\ara.traineddata" "C:\Program Files\Tesseract-OCR\tessdata\" >nul 2>&1
    copy /Y "tessdata\eng.traineddata" "C:\Program Files\Tesseract-OCR\tessdata\" >nul 2>&1
)

echo.
echo ===============================================================================
echo     Persian / Dari OCR Engine Activated Successfully!
echo ===============================================================================
echo.
pause
