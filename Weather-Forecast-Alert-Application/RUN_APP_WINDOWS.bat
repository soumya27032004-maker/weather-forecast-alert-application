@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
%PY% --version >nul 2>nul
if errorlevel 1 (
 echo.
 echo Python is missing. Install it from https://www.python.org/downloads/
 echo IMPORTANT: tick "Add python.exe to PATH" before clicking Install.
 echo Restart your computer, then double-click this file again.
 pause
 exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
 echo Creating local Python environment...
 %PY% -m venv .venv
 if errorlevel 1 goto fail
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -m streamlit run dashboard.py
if errorlevel 1 goto fail
exit /b 0
:fail
echo Something failed. Open START_HERE.txt for help.
pause
exit /b 1
