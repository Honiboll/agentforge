@echo off
title AgentForge - Backend Server
echo ===================================================
echo           🔥 Starting AgentForge Backend 🔥
echo ===================================================
cd /d "%~dp0\backend"

if not exist .venv (
    echo [*] Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
echo [*] Checking dependencies...
pip install -e .

echo [*] Starting Uvicorn on http://127.0.0.1:8000 ...
uvicorn agentforge.main:app --host 0.0.0.0 --port 8000 --reload
pause
