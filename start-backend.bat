@echo off
REM Quick start script for ContextMeet Backend
REM Run this from the project root directory

echo ====================================
echo   ContextMeet Backend Quick Start
echo ====================================
echo.

REM Navigate to backend directory
cd backend

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist "venv\Lib\site-packages\fastapi\" (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Check if .env exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please create .env file with your database credentials.
    echo Example:
    echo   DATABASE_URL=postgresql+asyncpg://user:password@localhost/contextmeet
    echo   SECRET_KEY=your-secret-key-here
    echo.
    pause
    exit /b 1
)

REM Start the backend server
echo.
echo Starting backend server on http://localhost:8000...
echo API Documentation: http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
