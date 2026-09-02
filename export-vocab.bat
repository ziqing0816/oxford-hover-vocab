@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo The app is not installed yet. Please run setup.bat first.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" vocab_cli.py export
if errorlevel 1 (
    echo Export failed.
    pause
    exit /b 1
)

start "" "%~dp0exports"
echo Export complete. The exports folder has been opened.
pause
