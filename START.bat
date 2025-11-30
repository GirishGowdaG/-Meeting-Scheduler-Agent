@echo off
echo ========================================
echo   SmartMeet AI Meeting Scheduler
echo ========================================
echo.
echo Starting Backend and Frontend...
echo.

REM Start Backend in new window
start "SmartMeet Backend" cmd /k "cd backend && .venv\Scripts\activate && uvicorn main:app --reload --port 8000"

REM Wait 3 seconds for backend to start
timeout /t 3 /nobreak > nul

REM Start Frontend in new window
start "SmartMeet Frontend" cmd /k "cd frontend && npm run dev"

REM Wait 3 seconds
timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo   SmartMeet is Starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Opening browser in 5 seconds...
echo.

REM Wait 5 seconds then open browser
timeout /t 5 /nobreak > nul
start http://localhost:3000

echo.
echo Press any key to close this window...
echo (Backend and Frontend will keep running)
pause > nul
