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

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- An LLM API key (OpenAI, Gemini, Anthropic) OR Ollama installed locally

### Option 1: Docker (Recommended)

```bash
git clone https://github.com/YOUR_USERNAME/AgentForge.git
cd AgentForge
cp .env.example .env
# Edit .env with your LLM API key
docker compose up
```

Open [http://localhost:3000](http://localhost:3000) 🎉

### Option 2: Manual Setup

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/AgentForge.git
cd AgentForge

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn agentforge.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) 🎉

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
git clone https://github.com/YOUR_USERNAME/AgentForge.git

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

