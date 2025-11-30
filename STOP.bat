@echo off
echo ========================================
echo   Stopping SmartMeet Services
echo ========================================
echo.

REM Kill Node.js processes (Frontend)
echo Stopping Frontend (Node.js)...
taskkill /F /IM node.exe /T 2>nul
if %errorlevel% equ 0 (
    echo Frontend stopped successfully!
) else (
    echo No Frontend process found.
)

echo.

REM Kill Python/Uvicorn processes (Backend)
echo Stopping Backend (Python/Uvicorn)...
taskkill /F /IM python.exe /T 2>nul
if %errorlevel% equ 0 (
    echo Backend stopped successfully!
) else (
    echo No Backend process found.
)

echo.
echo ========================================
echo   All SmartMeet Services Stopped
echo ========================================
echo.
pause
