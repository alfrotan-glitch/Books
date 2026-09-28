@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
title Check OCR Engines and Language Status
cls

echo ===============================================================================
echo     CHECK OCR ENGINES AND LANGUAGE MODELS STATUS
echo ===============================================================================
echo.

if exist ".venv\Scripts\python.exe" (
    set "PY_BIN=.venv\Scripts\python.exe"
) else (
    set "PY_BIN=python"
)

"%PY_BIN%" -m src.cli check-ocr

echo.
pause
