"""AgentForge — FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agentforge import __version__
from agentforge.config import settings
from agentforge.models.database import init_db

# Ensure built-in agents are registered
import agentforge.agents  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup
    await init_db()
    yield
    # Shutdown (nothing to clean up for now)


app = FastAPI(
    title="AgentForge",
    description="Intelligent AI Agent Orchestration Platform",
    version=__version__,
    lifespan=lifespan,
)

# CORS configuration
origins = settings.cors_origins if settings.cors_origins else ["*"]
allow_all = "*" in origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---
from agentforge.api.projects import router as projects_router  # noqa: E402
from agentforge.api.agents import router as agents_router  # noqa: E402
from agentforge.api.websocket import router as ws_router  # noqa: E402
from agentforge.api.providers import router as providers_router  # noqa: E402

app.include_router(projects_router)
app.include_router(agents_router)
app.include_router(ws_router)
app.include_router(providers_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}

