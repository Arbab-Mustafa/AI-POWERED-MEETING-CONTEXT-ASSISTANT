@echo off
REM Quick start script for ContextMeet Frontend
REM Run this from the project root directory

echo =====================================
echo   ContextMeet Frontend Quick Start
echo =====================================
echo.

REM Navigate to frontend directory
cd frontend

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing dependencies...
    call npm install
)

REM Check if .env.local exists
if not exist ".env.local" (
    echo Creating .env.local file...
    echo NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 > .env.local
)

REM Start the development server
echo.
echo Starting frontend development server...
echo Frontend: http://localhost:3000
echo.
call npm run dev
