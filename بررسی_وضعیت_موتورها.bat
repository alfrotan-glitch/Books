@echo off
chcp 65001 >nul
title بررسی وضعیت موتورهای هوش مصنوعی استخراج متن
cls

if exist ".venv\Scripts\python.exe" (
    set "PY_BIN=.venv\Scripts\python.exe"
) else (
    set "PY_BIN=python"
)

%PY_BIN% -m src.cli check-ocr

echo.
pause
