@echo off
echo ========================================
echo Starting Robot Von Bismarck Application
echo ========================================
echo.
echo This will start:
echo   - Frontend (React) on http://localhost:3000
echo   - Backend (WebSocket) on ws://localhost:3001
echo.
echo Press Ctrl+C to stop both servers
echo.
cd frontend
npm run dev
