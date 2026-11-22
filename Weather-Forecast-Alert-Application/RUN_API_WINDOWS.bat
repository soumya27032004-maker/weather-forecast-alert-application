@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Run RUN_APP_WINDOWS.bat first to install the project.
 pause
 exit /b 1
)
".venv\Scripts\python.exe" -m uvicorn api.app:app --host 127.0.0.1 --port 8000
pause
