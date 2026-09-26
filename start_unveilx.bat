@echo off
setlocal
cd /d "%~dp0"
title UnveilX Forge - Launcher

echo ============================================================
echo             UNVEILX FORGE - STARTING
echo ============================================================
echo.

where py >nul 2>&1
if %errorlevel%==0 (set "PY=py") else (set "PY=python")

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Creating Python 3.13 virtual environment...
  %PY% -3.13 -m venv .venv
  if errorlevel 1 (
    echo Python 3.13 was not found. Trying the default Python installation...
    %PY% -m venv .venv
  )
  if errorlevel 1 goto :error
) else (
  echo [1/4] Existing virtual environment found.
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 goto :error

echo [2/4] Checking dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo [3/4] Starting local AI backend...
start "UnveilX Backend" cmd /k "cd /d "%~dp0backend" && call ..\.venv\Scripts\activate.bat && python -m uvicorn server:app --host 127.0.0.1 --port 8000"

timeout /t 5 /nobreak >nul

echo [4/4] Starting UnveilX Forge dashboard...
start "UnveilX Dashboard" cmd /k "cd /d "%~dp0" && call .venv\Scripts\activate.bat && python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false"

timeout /t 5 /nobreak >nul
start "" http://127.0.0.1:8501

echo.
echo ============================================================
echo   Dashboard: http://127.0.0.1:8501
echo   Backend:   http://127.0.0.1:8000/docs
echo   Keep both black command windows open.
echo ============================================================
pause
exit /b 0

:error
echo.
echo ============================================================
echo ERROR: Setup failed. Read the message above.
echo ============================================================
pause
exit /b 1
