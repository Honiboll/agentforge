.PHONY: help dev backend frontend install test clean docker

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	cd backend && python -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"
	cd frontend && npm install

backend: ## Start backend dev server
	cd backend && . .venv/bin/activate && uvicorn agentforge.main:app --reload --port 8000

frontend: ## Start frontend dev server
	cd frontend && npm run dev

dev: ## Start both backend and frontend
	@echo "Starting AgentForge..."
	@make backend &
	@make frontend &
	@wait

test: ## Run all tests
	cd backend && . .venv/bin/activate && pytest
	cd frontend && npm test

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true

docker: ## Start with Docker Compose
	docker compose up --build

