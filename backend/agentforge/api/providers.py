"""Provider management API routes."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

import logging
from agentforge.config import settings
from agentforge.providers.provider_factory import create_provider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/providers", tags=["providers"])

PROVIDERS = [
    {"name": "openai", "label": "OpenAI", "requires_key": True},
    {"name": "gemini", "label": "Google Gemini", "requires_key": True},
    {"name": "anthropic", "label": "Anthropic", "requires_key": True},
    {"name": "ollama", "label": "Ollama (Local)", "requires_key": False},
]


@router.get("/")
async def list_providers() -> list[dict]:
    return PROVIDERS


class ProviderTest(BaseModel):
    provider: str


@router.post("/test")
async def test_provider(body: ProviderTest) -> dict:
    """Test connectivity to a provider by generating a short response."""
    try:
        provider = create_provider(body.provider, settings)
        response = await provider.generate("Say 'Hello from AgentForge!' in one sentence.")
        return {"success": True, "response": response}
    except Exception as e:
        logger.error("Provider test failed: %s", e)
        error_msg = str(e)
        # Redact any configured keys from error message before returning to client
        for key in [settings.openai_api_key, settings.gemini_api_key, settings.anthropic_api_key]:
            if key and len(key) > 6:
                error_msg = error_msg.replace(key, "[REDACTED]")
        return {"success": False, "error": error_msg}

