<div align="center">

# 🔥 AgentForge

**Intelligent AI Agent Orchestration Platform**

*Describe your needs → Get a team of specialized AI agents working for you*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

[Demo](#demo) • [Quick Start](#quick-start) • [Architecture](#architecture) • [Contributing](#contributing)

</div>

---

## 🚀 What is AgentForge?

AgentForge is an open-source platform that **analyzes your requirements** and automatically creates a **team of specialized AI agents**, each with a specific responsibility. Watch them work together in real-time through a beautiful live dashboard.

### How it works:

1. **📝 Describe** — Tell AgentForge what you need in plain language
2. **🧠 Analyze** — The orchestrator breaks down your request into tasks
3. **🏭 Forge** — Specialized agents are dynamically created for each task
4. **👀 Watch** — See your agents work in real-time through the live dashboard

### Key Features

- 🤖 **Dynamic Agent Creation** — Agents are designed on-the-fly based on your needs
- 🔌 **Provider Agnostic** — Use OpenAI, Gemini, Ollama, Anthropic, or any LLM
- 📡 **Live Dashboard** — Real-time WebSocket updates with beautiful animations
- 🎯 **Task Decomposition** — Intelligent breakdown of complex requirements
- 🔄 **Agent Collaboration** — Agents communicate and share results
- 🎨 **Beautiful UI** — Modern, responsive design with dark/light themes
- 🐳 **Docker Ready** — One-command deployment with Docker Compose

---

## 📸 Demo

<div align="center">

*Screenshots coming soon — Star the repo to stay updated!*

</div>

---

## 📋 Prerequisites & Installation Guide

Before running AgentForge, make sure you have the following installed on your machine. Everything listed below is free and takes only a few minutes to set up:

### 1. Git (Required to download the repository)
- **Windows**: Download the installer from [git-scm.com](https://git-scm.com/download/win).
- **macOS**: Open Terminal and run `xcode-select --install` (or `brew install git`).
- **Linux (Ubuntu/Debian)**: Run `sudo apt update && sudo apt install git -y`.
- **Verification**:
  ```bash
  git --version
  ```

### 2. Python (3.11 or newer)
Powers the AgentForge backend orchestrator, database, and autonomous agents.
- **Windows / macOS / Linux**: Download the installer from [python.org/downloads](https://www.python.org/downloads/) (select Python 3.11 or 3.12).
  > ⚠️ **Important for Windows Users**: Make sure to check the box **"Add python.exe to PATH"** on the first installation screen!
- **macOS (via Homebrew)**:
  ```bash
  brew install python@3.11
  ```
- **Verification**:
  ```bash
  python --version   # or python3 --version
  ```

### 3. Node.js (v18 or v20 LTS) & npm
Powers the Next.js real-time live dashboard.
- **Windows & macOS**: Download the **LTS (Long Term Support)** installer from [nodejs.org](https://nodejs.org/).
- **Linux (Ubuntu/Debian)**:
  ```bash
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt-get install -y nodejs
  ```
- **Verification**:
  ```bash
  node -v
  npm -v
  ```

### 4. Choose Your AI Brain / LLM (Pick at least ONE)

AgentForge is flexible and works with both local and cloud models. You only need **one** of the following options:

| Option | Cost & Privacy | Best For | How to Get & Setup |
|---|---|---|---|
| 🦙 **Ollama** | **100% Free** & Private | Offline local execution on your machine (No API key needed!) | 1. Download & install from [ollama.com](https://ollama.com/)<br>2. Open your terminal and pull a model: `ollama run llama3.2`<br>3. AgentForge connects to it automatically! |
| 💎 **Google Gemini API** | **Free tier available** | Ultra-fast responses with generous free limits | 1. Go to [Google AI Studio](https://aistudio.google.com/)<br>2. Sign in and click **"Get API key"** → **"Create API key"**<br>3. Paste it in your `.env` as `GEMINI_API_KEY` |
| 🟢 **OpenAI API** | Pay-as-you-go | GPT-4o intelligence | 1. Create an account at [platform.openai.com](https://platform.openai.com/api-keys)<br>2. Generate a secret key and paste it as `OPENAI_API_KEY` |
| 🟠 **Anthropic Claude** | Pay-as-you-go | Claude Sonnet reasoning | 1. Create an account at [console.anthropic.com](https://console.anthropic.com/)<br>2. Generate a key and paste it as `ANTHROPIC_API_KEY` |

---

## ⚡ Quick Start

> ⚠️ **IMPORTANT SECURITY RULE:** Never put real API keys in `.env.example`! Always copy it to `.env` and put your secret keys inside `.env`. The `.env` file is permanently ignored by Git and stays safe on your local computer.

Choose the setup guide for your operating system below:

---

### 🪟 Windows Setup Guide (Command Prompt or PowerShell)

#### Step 1: Clone & Configure
Open **Command Prompt (CMD)** or **PowerShell**:
```cmd
git clone https://github.com/Honiboll/agentforge.git
cd agentforge

:: Create your private .env file from template (Command Prompt)
copy .env.example .env

:: Or in PowerShell:
:: Copy-Item .env.example .env
```
*(Open `.env` in Notepad or VS Code and paste your API key if you're using Gemini or OpenAI).*

#### Step 2: Backend Setup & Run (Terminal 1)
In your Command Prompt:
```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
uvicorn agentforge.main:app --reload --port 8000
```
> 💡 **PowerShell Users:** If you see `cannot be loaded because running scripts is disabled`, run this once:  
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` then run `.\.venv\Scripts\Activate.ps1`.  
> 💡 **Python Launcher:** If `python` opens the Windows Store, run `py -3 -m venv .venv` instead.

#### Step 3: Frontend Setup & Run (Terminal 2)
Open a **new** Command Prompt window:
```cmd
cd agentforge\frontend
npm install
npm run dev
```
🎉 Open your browser at **[http://localhost:3000](http://localhost:3000)**!

---

### 🍎 macOS & 🐧 Linux Setup Guide (Terminal / Bash / Zsh)

#### Step 1: Clone & Configure
Open your Terminal:
```bash
git clone https://github.com/Honiboll/agentforge.git
cd agentforge

# Create your private .env file
cp .env.example .env
# Open .env and add your API key if using Gemini/OpenAI/Claude
```

#### Step 2: Backend Setup & Run (Terminal 1)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn agentforge.main:app --reload --port 8000
```
> Backend runs at [http://localhost:8000](http://localhost:8000) (Interactive Swagger Docs at `/docs`).

#### Step 3: Frontend Setup & Run (Terminal 2 - New Tab)
```bash
cd agentforge/frontend
npm install
npm run dev
```
🎉 Open your browser at **[http://localhost:3000](http://localhost:3000)**!

---

### 🐳 Option 3: Docker (All Operating Systems)

If you have Docker Desktop installed on Windows, Mac, or Linux:
```bash
git clone https://github.com/Honiboll/agentforge.git
cd agentforge

# Windows CMD:
copy .env.example .env
# Mac/Linux:
# cp .env.example .env

docker compose up
```
Open **[http://localhost:3000](http://localhost:3000)** 🎉

---

## 📖 How to Use AgentForge

### 1. Configure Your AI Provider
Open your `.env` file and choose your model:

* **Using Ollama (Local & Free, No API key needed):**
  ```env
  DEFAULT_LLM_PROVIDER=ollama
  OLLAMA_BASE_URL=http://localhost:11434
  OLLAMA_MODEL=llama3.2
  ```
* **Using Google Gemini:**
  ```env
  DEFAULT_LLM_PROVIDER=gemini
  GEMINI_API_KEY=your_gemini_api_key
  GEMINI_MODEL=gemini-2.0-flash
  ```
* **Using OpenAI:**
  ```env
  DEFAULT_LLM_PROVIDER=openai
  OPENAI_API_KEY=sk-your_openai_key
  OPENAI_MODEL=gpt-4o
  ```

### 2. Launch the Application
- Visit **[http://localhost:3000](http://localhost:3000)** for the web dashboard.
- Visit **[http://localhost:8000/docs](http://localhost:8000/docs)** for the interactive Swagger REST API documentation.

### 3. Describe Your Project
In the homepage input area:
1. Type a description of what you want to achieve (e.g. *"Build a secure REST API in Python with JWT authentication, rate limiting, and PostgreSQL"*).
2. Select your preferred LLM Provider (Ollama, OpenAI, Gemini, Anthropic).
3. Click **Forge Agents 🔥**.

### 4. Watch Agents Collaborate in Real-Time
The platform automatically:
1. **Analyzes & Plans**: Breaks down your request into ordered sub-tasks with dependencies.
2. **Spawns Specialized Agents**: Creates instances of `Researcher`, `Coder`, `Reviewer`, `Planner`, or `Writer`.
3. **Streams Execution**:
   - 🟡 **Thinking**: Agent is analyzing or querying the model (interactive pulsing animation).
   - 🔵 **Working**: Agent is writing code, generating documentation, or executing tasks.
   - 🟢 **Done**: Task finished successfully with output logged.
   - 📋 **Live Log**: Inspect individual console logs per agent in real time.
   - ⏱️ **Timeline**: Track project events chronologically over WebSockets.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────┐ │
│  │ Project  │ │  Agent   │ │    Live Dashboard     │ │
│  │  Setup   │ │  Cards   │ │  (WebSocket Stream)   │ │
│  └──────────┘ └──────────┘ └──────────────────────┘ │
└──────────────────────┬──────────────────────────────┘
                       │ WebSocket + REST
┌──────────────────────┴──────────────────────────────┐
│                   Backend (FastAPI)                  │
│  ┌──────────────────────────────────────────────┐   │
│  │              Orchestrator                     │   │
│  │  ┌────────────┐  ┌─────────────────────────┐ │   │
│  │  │  Analyzer   │  │    Agent Factory        │ │   │
│  │  └────────────┘  └─────────────────────────┘ │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ Agent 1  │ │ Agent 2  │ │ Agent N  │  ...       │
│  │Researcher│ │  Coder   │ │ Reviewer │            │
│  └──────────┘ └──────────┘ └──────────┘            │
│  ┌──────────────────────────────────────────────┐   │
│  │         LLM Providers (Pluggable)             │   │
│  │  OpenAI │ Gemini │ Ollama │ Anthropic │ ...   │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Core Components

| Component | Description |
|-----------|------------|
| **Orchestrator** | Coordinates the entire workflow from input to output |
| **Task Analyzer** | Breaks down user requirements into discrete tasks |
| **Agent Factory** | Dynamically creates specialized agents |
| **Base Agent** | Abstract class with lifecycle management |
| **Event System** | Real-time event broadcasting via WebSocket |
| **LLM Providers** | Pluggable adapters for any LLM service |

---

## 🔌 Supported LLM Providers

| Provider | Local | Cloud | Status |
|----------|-------|-------|--------|
| **Ollama** | ✅ | — | ✅ Ready |
| **OpenAI** | — | ✅ | ✅ Ready |
| **Google Gemini** | — | ✅ | ✅ Ready |
| **Anthropic** | — | ✅ | ✅ Ready |
| **Custom** | ✅ | ✅ | 🔧 Extensible |

---

## 🤝 Contributing

We love contributions! See [CONTRIBUTING.md](docs/contributing.md) for guidelines.

```bash
# Fork & clone
git clone https://github.com/Honiboll/agentforge.git
cd agentforge

# Create a branch
git checkout -b feature/amazing-feature

# Make your changes & test
cd backend && pytest
cd frontend && npm test

# Submit a PR
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ by the AgentForge community

</div>

