@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
title Digital Book Text Extractor - Web Dashboard

call "%~dp0run.bat" %*
