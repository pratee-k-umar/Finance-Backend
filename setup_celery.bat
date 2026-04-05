@echo off
REM Quick Celery Setup and Run Script for Windows

echo.
echo ========================================
echo Finance Dashboard - Celery Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo Virtual environment created!
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install/Update dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Check if Redis is installed
redis-cli --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Redis is not installed or not in PATH
    echo Please install Redis from: https://github.com/microsoftarchive/redis/releases
    echo.
    pause
) else (
    echo Redis is installed!
)

REM Display instructions
echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the application with Celery:
echo.
echo 1. Start Redis Server (in a new terminal):
echo    redis-server
echo.
echo 2. Start Celery Worker (in a new terminal):
echo    celery -A project_settings worker -l info
echo.
echo 3. Start Celery Beat (in a new terminal):
echo    celery -A project_settings beat -l info
echo.
echo 4. Start Django Server (this terminal):
echo    python manage.py runserver
echo.
echo For more information, see CELERY_SETUP.md
echo.
pause
