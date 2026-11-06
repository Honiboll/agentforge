<div align="center">

# 🔥 AgentForge

**Intelligent AI Agent Orchestration Platform**

*Describe your needs → Get a team of specialized AI agents working for you in real-time*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

[1-Click Run](#1-click-run) • [Prerequisites](#prerequisites) • [How to Use](#how-to-use) • [Architecture](#architecture) • [Updating](#updating) • [Contributing](#contributing)

</div>

---

## 🚀 What is AgentForge?

AgentForge is an open-source platform that **analyzes your requirements** and automatically designs, delegates, and coordinates a **team of specialized AI agents** (Researcher, Coder, Reviewer, Planner, Writer), each carrying out a dedicated part of your task. Watch them collaborate in real-time through a live reactive dashboard.

### How it works:

1. **📝 Describe** — Tell AgentForge what you need in plain English or your preferred language.
2. **🧠 Analyze** — The orchestrator decomposes your requirements into structured, dependent tasks.
3. **🏭 Forge** — Autonomous agents are dynamically created on-the-fly for each task.
4. **👀 Watch** — Follow thinking animations, status changes, and live streaming logs over WebSockets.

### Key Features

- 🤖 **Dynamic Agent Creation** — Agents are designed on-the-fly based on your specific requirements.
- ⚡ **Smart Key Auto-Detector** — Paste ANY API key (Gemini, OpenAI, Claude) and AgentForge will auto-identify the provider, verify the key, and unlock its models!
- 🔑 **In-Dashboard Key Setup** — Paste your API keys directly into the web UI—no manual file editing required!
- 🔄 **Live Model Discovery** — Automatically discovers newly released models from Google, OpenAI, and Ollama APIs.
- ✏️ **Custom Model Input** — Type in any brand-new or fine-tuned model name to use it immediately.
- 💬 **Persistent Chat & Project History** — Revisit past agent runs, review outputs, or remove old sessions.
- 🔌 **Provider Agnostic** — Connect Google Gemini, OpenAI, Anthropic Claude, or 100% free offline Ollama.
- 📡 **Real-time Streaming** — Live agent state changes (Idle, Thinking, Working, Done, Error) and live logs.
- 🚀 **1-Click Launchers** — Double-click launcher for Windows, single-command runner for Mac/Linux.
- 🐳 **Docker Ready** — Instant containerized deployment via Docker Compose.

---

## 📸 Demo

<div align="center">

*Screenshots coming soon — Star the repo to stay updated!*

</div>

---

<a id="prerequisites"></a>
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

<a id="1-click-run"></a>
### 🚀 1-Click / One-Command Startup (Recommended!)

We provide instant launcher scripts that automatically set up dependencies, launch both backend and frontend, and open your browser:

* **🪟 Windows Users:**  
  Just **double-click [`run.bat`](run.bat)** in File Explorer (or run `run.bat` in CMD / PowerShell)!
* **🍎 macOS & 🐧 Linux Users:**  
  Open Terminal and run:  
  ```bash
  ./run.sh
  ```
* **🐍 Any System with Python:**  
  Run in terminal:  
  ```bash
  python run.py
  ```
*(These scripts automatically handle `.env` creation, dependency checks, launch both servers, and open `http://localhost:3000` in your default browser).*

---

### 🛠️ Manual Terminal-by-Terminal Setup (Optional)

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

<a id="how-to-use"></a>
## 📖 How to Use AgentForge

### 1. Set Up Your AI Provider & API Key

AgentForge makes it effortless to connect your preferred AI models. You have two convenient options:

#### Option A: Smart Key Auto-Detector (Easiest & Fastest ⚡)
You don't even need to pick a provider manually:
1. Start AgentForge and open **[http://localhost:3000](http://localhost:3000)** (or go to **Settings**).
2. Paste any API key into the **"⚡ Smart Key Auto-Detector"** box.
3. Click **Detect & Add ⚡** (or press Enter).
4. AgentForge instantly identifies the provider (Google Gemini, OpenAI, or Anthropic Claude), verifies the key, saves it, and immediately unlocks all models!

#### Option B: Manual In-Dashboard Selection
1. Under **AI Provider**, select your service (e.g. Google Gemini, OpenAI, or Anthropic).
2. If an API key is required, an inline input box will appear immediately right below the selector.
3. Paste your API key and click **Save & Apply** (or manage keys under **Settings**).
4. Your key is verified, saved, and active instantly without restarting servers!

#### Option B: Local & Free with Ollama (No API Key Required)
1. Install [Ollama](https://ollama.com/) and run any model in your terminal (e.g. `ollama run llama3.2`).
2. Select **Ollama** in AgentForge—it connects to your local machine automatically!

#### Option C: Via `.env` Configuration File (Optional)
You can also set default keys directly in your root `.env` file:
* **Google Gemini:** `GEMINI_API_KEY=your_gemini_api_key`
* **OpenAI:** `OPENAI_API_KEY=sk-your_openai_key`
* **Anthropic Claude:** `ANTHROPIC_API_KEY=your_anthropic_key`

---

### 2. Live Model Discovery & Custom Models

AgentForge keeps you up to date with the latest AI breakthroughs:
- **Default Models:** Pre-configured with the most reliable models (e.g. `gemini-2.0-flash`, `gpt-4o`, `claude-3-5-sonnet`, `llama3.2`).
- 🔄 **Live Model Discovery:** Click **"🔄 Check for New Models"** next to the model dropdown. AgentForge will query the provider's official API using your configured key and automatically display all newly released and accessible models.
- ✏️ **Custom Model Name:** Click **"✏️ Custom Model Name"** to manually enter any brand-new or fine-tuned model identifier (such as `gemini-2.5-pro`, `o3-mini`, or a local Ollama tag like `deepseek-r1:8b`). AgentForge will use it immediately.

---

### 3. Describe Your Project & Forge Agents
1. On the home page, enter a description of what you want to build in plain English, Persian, or any language (e.g., *"Design an asynchronous microservice in Python with Redis caching and automated unit tests"*).
2. Choose your AI provider and model.
3. Click **Forge Agents 🔥**.

---

### 4. Watch Agents Collaborate in Real-Time
The platform's orchestrator takes over:
1. **Analyzes & Plans**: Breaks your request into structured sub-tasks with dependency graphs.
2. **Spawns Specialized Agents**: Dynamically instantiates specialized roles like `Researcher`, `Coder`, `Reviewer`, `Planner`, and `Writer`.
3. **Streams Live Execution**:
   - 🟡 **Thinking**: Dynamic pulsing animation while the agent queries the LLM and formulates its strategy.
   - 🔵 **Working**: Real-time progress while generating code, tests, or documentation.
   - 🟢 **Done**: Task completed successfully with structured output.
   - 📋 **Live Log**: Inspect individual console logs per agent in real time.
   - ⏱️ **Timeline**: Track project events chronologically over WebSockets.

---

### 5. Persistent Chat & Project History
Never lose track of your work:
- All generated projects and agent sessions are automatically saved in the local database.
- Browse the **"Previous Chats & Projects"** section on the homepage to resume, review, or inspect past agent deliverables and timeline history.
- Remove old or experimental sessions with a single click (**Delete**).

---

<a id="architecture"></a>
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
| **Custom** | ✅ | ✅ | ✅ Ready (DeepSeek, Groq, OpenRouter, vLLM) |

---

<a id="updating"></a>
## 🔄 Updating to the Latest Version

To update your local AgentForge installation with new features, agent roles, and model adapters:

### 1. Pull the Latest Code
```bash
cd agentforge
git pull origin main
```

### 2. Launch (Dependencies Auto-Update)
If you use the 1-click launchers, they will automatically verify and install any newly added packages:
- **Windows:** Double-click [`run.bat`](run.bat)
- **macOS / Linux:** Run `./run.sh`
- **Any System with Python:** Run `python run.py`

### Manual Update (If running via separate terminals)
```bash
# Update backend dependencies
cd backend
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"

# Update frontend dependencies
cd ../frontend
npm install
```

---

<a id="contributing"></a>
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

