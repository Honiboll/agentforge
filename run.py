"""Cross-platform one-command runner for AgentForge (Windows, macOS, Linux).

Usage:
    python run.py
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"


def log(msg: str) -> None:
    print(f"\033[96m[*] {msg}\033[0m")


def main() -> None:
    print("\n\033[1;93m===================================================")
    print("           🔥 Starting AgentForge 🔥")
    print("===================================================\033[0m\n")

    # 1. Ensure .env exists
    env_file = ROOT_DIR / ".env"
    env_example = ROOT_DIR / ".env.example"
    if not env_file.exists() and env_example.exists():
        log("Creating .env from .env.example...")
        shutil.copyfile(env_example, env_file)

    # 2. Check virtualenv
    is_win = sys.platform == "win32"
    venv_dir = BACKEND_DIR / ".venv"
    python_bin = venv_dir / ("Scripts" if is_win else "bin") / ("python.exe" if is_win else "python")
    uvicorn_bin = venv_dir / ("Scripts" if is_win else "bin") / ("uvicorn.exe" if is_win else "uvicorn")

    if not venv_dir.exists() or not python_bin.exists():
        log("Setting up Python virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        log("Installing backend dependencies...")
        subprocess.run([str(python_bin), "-m", "pip", "install", "-e", "."], cwd=BACKEND_DIR, check=True)

    # 3. Check node_modules
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        log("Installing frontend dependencies (npm install)...")
        npm_cmd = "npm.cmd" if is_win else "npm"
        subprocess.run([npm_cmd, "install"], cwd=FRONTEND_DIR, check=True)

    # 4. Launch backend and frontend
    log("Starting Backend server on http://localhost:8000 ...")
    backend_proc = subprocess.Popen(
        [str(uvicorn_bin), "agentforge.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=BACKEND_DIR,
    )

    log("Starting Frontend dashboard on http://localhost:3000 ...")
    npm_cmd = "npm.cmd" if is_win else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=FRONTEND_DIR,
    )

    time.sleep(2.5)
    print("\n\033[1;92m===================================================")
    print("  AgentForge is running!")
    print("  - Dashboard: http://localhost:3000")
    print("  - API Docs:  http://localhost:8000/docs")
    print("  Press Ctrl+C to stop all servers.")
    print("===================================================\033[0m\n")

    try:
        webbrowser.open("http://localhost:3000")
    except Exception:
        pass

    def shutdown(sig, frame):
        print("\n\033[93mShutting down AgentForge servers...\033[0m")
        backend_proc.terminate()
        frontend_proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    if not is_win:
        signal.signal(signal.SIGTERM, shutdown)

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        shutdown(None, None)


if __name__ == "__main__":
    main()
