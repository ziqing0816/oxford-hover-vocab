@echo off
REM ASCII only -- see install.py / make_shortcut.py for why.
REM The program prints its own Chinese startup banner.
cd /d "%~dp0"
title hover_translate
if not exist dict.db goto nodict
if not exist ".venv\Scripts\python.exe" goto noenv
".venv\Scripts\python.exe" hover_translate.py
if errorlevel 1 pause
exit /b %errorlevel%

:nodict
echo.
echo   Dictionary dict.db not found. Building it now...
echo.
if not exist ".venv\Scripts\python.exe" goto noenv
".venv\Scripts\python.exe" build_dict.py
if errorlevel 1 pause
exit /b %errorlevel%

:noenv
echo.
echo   Python environment not found. Please run setup.bat first.
pause
exit /b 1
