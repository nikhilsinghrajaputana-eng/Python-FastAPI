@echo off
setlocal EnableExtensions
cd /d "%~dp0"

title ECADS-v3
echo ============================================
echo  ECADS-v3  Early Compounder Discovery System
echo ============================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not on PATH.
    goto :end_fail
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create .venv
        goto :end_fail
    )
)

call ".venv\Scripts\activate.bat"

echo Installing API dependencies...
python -m pip install --upgrade pip
python -m pip install fastapi "uvicorn[standard]" pydantic pydantic-settings pyyaml polars eval_type_backport
if errorlevel 1 (
    echo ERROR: Could not install API packages.
    goto :end_fail
)

echo Installing remaining project packages (optional)...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Full requirements.txt did not install completely.
    echo The API can still start with the core packages above.
)

where docker >nul 2>&1
if not errorlevel 1 (
    if exist docker-compose.yml (
        echo Starting PostgreSQL and Redis...
        docker compose up -d
    )
)

echo.
echo Starting API at http://127.0.0.1:8000
echo Docs:          http://127.0.0.1:8000/docs
echo Health:        http://127.0.0.1:8000/health
echo Press Ctrl+C to stop.
echo.

python -m uvicorn ecads.api.main:app --reload --host 127.0.0.1 --port 8000
set EXITCODE=%ERRORLEVEL%
echo.
echo API stopped. Exit code: %EXITCODE%
if /I not "%~1"=="--nopause" pause
exit /b %EXITCODE%

:end_fail
if /I not "%~1"=="--nopause" pause
exit /b 1
