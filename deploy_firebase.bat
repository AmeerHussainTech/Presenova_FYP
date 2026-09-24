@echo off
echo ===================================================
echo      Presenova: Firebase Hosting Deployment
echo ===================================================
echo.

echo [1/3] Verifying Firebase CLI...
call firebase --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Firebase CLI is not installed or not in PATH!
    echo Please install it first by running: npm install -g firebase-tools
    pause
    exit /b 1
)

echo [2/3] Checking Frontend Build in frontend/dist...
if not exist "frontend\dist\index.html" (
    echo [INFO] frontend\dist not found. Building frontend now...
    cd frontend
    call npm run build
    cd ..
) else (
    echo [OK] Production build found in frontend/dist!
)

echo.
echo [3/3] Deploying to Firebase Hosting...
echo Selected Project:
call firebase use
echo.
call firebase deploy --only hosting

echo.
echo ===================================================
echo Deployment completed! Check your Hosting URL above.
echo ===================================================
pause
