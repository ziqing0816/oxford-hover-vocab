@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\pythonw.exe" (
    echo The app is not installed yet. Please run setup.bat first.
    pause
    exit /b 1
)

start "" ".venv\Scripts\pythonw.exe" review_app.py
