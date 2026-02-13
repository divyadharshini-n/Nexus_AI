@echo off
echo ====================================
echo AI PLC Platform - Quick Start
echo ====================================
echo.
echo This will start both Backend and Frontend servers
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press Ctrl+C in each window to stop the servers
echo.
pause

echo Starting Backend...
start "AI PLC Backend" cmd /c "%~dp0start-backend.bat"

timeout /t 3 /nobreak >nul

echo Starting Frontend...
start "AI PLC Frontend" cmd /c "%~dp0frontend\start-frontend.bat"

echo.
echo Both servers are starting in separate windows!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
pause
