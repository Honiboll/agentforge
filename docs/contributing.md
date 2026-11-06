# Contributing to AgentForge

Thank you for your interest in contributing! 🎉

## Getting Started

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/Honiboll/agentforge.git`
   `cd agentforge`
3. Create a **branch**: `git checkout -b feature/your-feature`
4. Make your changes
5. Run **tests**: `cd backend && pytest`
6. Submit a **Pull Request**

## Development Setup

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn agentforge.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Code Style

- **Python**: We use [Ruff](https://github.com/astral-sh/ruff) for linting. Run `ruff check .` before committing.
- **TypeScript**: Follow the existing patterns. Use TypeScript types.

## Adding a New Agent Type

1. Create a new file in `backend/agentforge/agents/`
2. Extend `BaseAgent` and implement the `execute` method
3. Register it in `backend/agentforge/agents/__init__.py`

## Adding a New LLM Provider

1. Create a new file in `backend/agentforge/providers/`
2. Extend `BaseLLMProvider` and implement the `generate` method
3. Add a case in `backend/agentforge/providers/provider_factory.py`

## Reporting Issues

- Use GitHub Issues
- Include steps to reproduce
- Include your environment (OS, Python version, Node version)

