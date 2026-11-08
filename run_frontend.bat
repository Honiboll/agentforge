@echo off
title AgentForge - Frontend Server
echo ===================================================
echo           🔥 Starting AgentForge Frontend 🔥
echo ===================================================
cd /d "%~dp0\frontend"

if not exist node_modules (
    echo [*] Installing frontend dependencies...
    call npm install
)

echo [*] Starting Next.js Dev Server on http://localhost:3000 ...
npm run dev
pause
