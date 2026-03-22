@echo off
echo ========================================
echo   Garage — Parking
echo ========================================
echo.

REM Проверяем Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker not found. Install Docker Desktop.
    pause
    exit /b 1
)

docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker not running. Start Docker Desktop.
    pause
    exit /b 1
)

echo [1/3] Stopping old containers...
docker-compose -p garage down 2>nul

echo [2/3] Starting containers...
docker-compose -p garage up -d

echo [3/3] Waiting...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   Project started!
echo   Opening http://localhost:8000
echo ========================================
start http://localhost:8000

echo.
echo To stop: run stop.bat
echo To view logs: run logs.bat
pause