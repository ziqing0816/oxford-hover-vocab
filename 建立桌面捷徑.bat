@echo off
REM ASCII only -- see make_shortcut.py for why.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" goto noenv
".venv\Scripts\python.exe" make_shortcut.py
if errorlevel 1 pause
exit /b %errorlevel%

:noenv
echo.
echo   Python environment not found. Please run setup.bat first.
pause
exit /b 1
