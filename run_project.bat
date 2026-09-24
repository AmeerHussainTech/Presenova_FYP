@echo off
title AI Presentation Hub

echo ====================================================================
echo               AI Presentation Hub - Launcher                        
echo ====================================================================
echo.

:: 0. Clean any orphaned processes holding ports
echo Checking for orphaned processes on port 5000 and 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do (
    echo Releasing port 5000 (PID %%a)...
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    echo Releasing port 3000 (PID %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

:: 1. Start Flask Backend
echo [1/2] Starting Flask Backend Server (Port 5000)...
if exist "venv312\Scripts\python.exe" (
    start "AI Hub Backend (Port 5000)" cmd /k "venv312\Scripts\python.exe main.py"
) else if exist "venv\Scripts\python.exe" (
    start "AI Hub Backend (Port 5000)" cmd /k "venv\Scripts\python.exe main.py"
) else (
    start "AI Hub Backend (Port 5000)" cmd /k "python main.py"
)

:: 2. Start React Frontend
echo [2/2] Starting React Vite Frontend Server (Port 3000)...
start "AI Hub Frontend (Port 3000)" cmd /k "cd frontend && npm run dev"

echo.
echo ====================================================================
echo   Services launched!
echo   - Backend: http://localhost:5000
echo   - Frontend: http://localhost:3000 (usually opens automatically)
echo.
echo   Press any key in this window to close the launcher.
echo   (The backend/frontend terminal windows will remain running)
echo ====================================================================
pause
