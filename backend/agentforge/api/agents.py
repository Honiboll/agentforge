"""Agent API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from agentforge.core.agent_registry import registry

# We also need to make sure built-in agents are registered
import agentforge.agents  # noqa: F401

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/types")
async def list_agent_types() -> list[dict[str, str]]:
    """Return all registered agent types."""
    return [{"type": t} for t in registry.list_types()]

