@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
%PY% --version >nul 2>nul
if errorlevel 1 (
 echo Please install Python from https://www.python.org/downloads/
 echo Tick Add Python to PATH when installing.
 pause
 exit /b 1
)
if not exist ".venv\Scripts\python.exe" %PY% -m venv .venv
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fail
".venv\Scripts\python.exe" main.py --mode demo --city Delhi
pause
exit /b 0
:fail
echo Setup failed. Read START_HERE.txt.
pause
exit /b 1
