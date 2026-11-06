@echo off
title AgentForge Launcher
echo ===================================================
echo            🔥 Starting AgentForge 🔥
echo ===================================================
echo.

:: 1. Ensure .env exists
if not exist .env (
    echo [*] Creating .env from .env.example...
    copy .env.example .env >nul
)

:: 2. Setup backend virtual environment if missing
if not exist backend\.venv (
    echo [*] Creating Python virtual environment...
    cd backend
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo [*] Installing backend dependencies...
    pip install -e .
    cd ..
)

:: 3. Setup frontend dependencies if missing
if not exist frontend\node_modules (
    echo [*] Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

:: 4. Launch Backend in a background terminal
echo [*] Starting Backend server on http://localhost:8000 ...
start "AgentForge - Backend" cmd /k "cd backend && call .venv\Scripts\activate.bat && uvicorn agentforge.main:app --host 0.0.0.0 --port 8000 --reload"

:: 5. Launch Frontend in a background terminal
echo [*] Starting Frontend dashboard on http://localhost:3000 ...
start "AgentForge - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ===================================================
echo   AgentForge is running!
echo   - Web Dashboard: http://localhost:3000
echo   - API Swagger:   http://localhost:8000/docs
echo ===================================================
echo.

:: 6. Open default browser after a short delay
timeout /t 3 >nul
start http://localhost:3000

