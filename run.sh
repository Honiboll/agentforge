#!/usr/bin/env bash
set -e

echo "==================================================="
echo "           🔥 Starting AgentForge 🔥"
echo "==================================================="
echo ""

# 1. Ensure .env exists
if [ ! -f .env ]; then
    echo "[*] Creating .env from .env.example..."
    cp .env.example .env
fi

# 2. Setup backend virtualenv if missing
if [ ! -d "backend/.venv" ]; then
    echo "[*] Setting up Python virtual environment..."
    cd backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e .
    cd ..
fi

# 3. Setup frontend dependencies if missing
if [ ! -d "frontend/node_modules" ]; then
    echo "[*] Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Cleanup on exit
cleanup() {
    echo ""
    echo "Stopping AgentForge..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

echo "[*] Starting Backend (http://localhost:8000)..."
(cd backend && source .venv/bin/activate && uvicorn agentforge.main:app --host 0.0.0.0 --port 8000 --reload) &

echo "[*] Starting Frontend (http://localhost:3000)..."
(cd frontend && npm run dev) &

echo ""
echo "==================================================="
echo "   AgentForge is running!"
echo "   - Web Dashboard: http://localhost:3000"
echo "   - API Swagger:   http://localhost:8000/docs"
echo "   Press Ctrl+C to stop all servers."
echo "==================================================="
echo ""

# Open browser
sleep 3
if command -v open > /dev/null; then
    open http://localhost:3000
elif command -v xdg-open > /dev/null; then
    xdg-open http://localhost:3000
fi

wait
