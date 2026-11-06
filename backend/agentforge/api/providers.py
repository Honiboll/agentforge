"""Provider management API routes with dynamic model and API key inspection."""

from __future__ import annotations

import logging
from typing import Any
import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from agentforge.config import settings
from agentforge.providers.provider_factory import create_provider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/providers", tags=["providers"])


class ModelOption(BaseModel):
    id: str
    name: str
    description: str


class ProviderInfo(BaseModel):
    name: str
    label: str
    is_available: bool
    requires_key: bool
    has_key: bool
    default_model: str
    models: list[ModelOption]


# Available models metadata
DEFAULT_MODELS: dict[str, list[dict[str, str]]] = {
    "gemini": [
        {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "description": "Fastest & powerful multimodal reasoning (Recommended)"},
        {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "description": "High-efficiency general purpose model"},
        {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "description": "Deep thinking & complex coding"},
    ],
    "openai": [
        {"id": "gpt-4o", "name": "GPT-4o", "description": "Flagship multimodal intelligence"},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "description": "Affordable, lightweight & fast"},
        {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "High-accuracy code & reasoning"},
    ],
    "anthropic": [
        {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4", "description": "Next-gen code and agentic reasoning"},
        {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "description": "Industry leading coding and tool use"},
        {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku", "description": "Fast and concise assistance"},
    ],
    "ollama": [
        {"id": "llama3.2", "name": "Llama 3.2", "description": "Meta's state-of-the-art compact local model"},
        {"id": "mistral", "name": "Mistral 7B", "description": "Popular open-weight instruction model"},
        {"id": "deepseek-r1", "name": "DeepSeek R1", "description": "Advanced reasoning local model"},
        {"id": "qwen2.5", "name": "Qwen 2.5", "description": "Multilingual and coding specialist"},
    ],
}


async def _probe_ollama_models() -> tuple[bool, list[ModelOption]]:
    """Probe local Ollama daemon for installed models."""
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            resp = await client.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                raw_models = data.get("models", [])
                if raw_models:
                    parsed = [
                        ModelOption(
                            id=m.get("name", ""),
                            name=m.get("name", "").split(":")[0].capitalize(),
                            description=f"Local model ({round(m.get('size', 0) / (1024**3), 1)} GB)",
                        )
                        for m in raw_models
                        if m.get("name")
                    ]
                    return True, parsed
                return True, [ModelOption(**m) for m in DEFAULT_MODELS["ollama"]]
    except Exception:
        pass
    # Offline or unreachable
    return False, [ModelOption(**m) for m in DEFAULT_MODELS["ollama"]]


@router.get("/", response_model=list[ProviderInfo])
async def list_providers() -> list[dict[str, Any]]:
    """Return all providers with their real-time availability and individual models."""
    ollama_online, ollama_models = await _probe_ollama_models()

    has_gemini = bool(settings.gemini_api_key and settings.gemini_api_key.strip())
    has_openai = bool(settings.openai_api_key and settings.openai_api_key.strip())
    has_anthropic = bool(settings.anthropic_api_key and settings.anthropic_api_key.strip())

    return [
        {
            "name": "ollama",
            "label": "Ollama (Local)",
            "is_available": ollama_online,
            "requires_key": False,
            "has_key": True,
            "default_model": settings.ollama_model,
            "models": ollama_models,
        },
        {
            "name": "gemini",
            "label": "Google Gemini",
            "is_available": has_gemini,
            "requires_key": True,
            "has_key": has_gemini,
            "default_model": settings.gemini_model,
            "models": [ModelOption(**m) for m in DEFAULT_MODELS["gemini"]],
        },
        {
            "name": "openai",
            "label": "OpenAI",
            "is_available": has_openai,
            "requires_key": True,
            "has_key": has_openai,
            "default_model": settings.openai_model,
            "models": [ModelOption(**m) for m in DEFAULT_MODELS["openai"]],
        },
        {
            "name": "anthropic",
            "label": "Anthropic",
            "is_available": has_anthropic,
            "requires_key": True,
            "has_key": has_anthropic,
            "default_model": settings.anthropic_model,
            "models": [ModelOption(**m) for m in DEFAULT_MODELS["anthropic"]],
        },
    ]


class ProviderTest(BaseModel):
    provider: str
    model: str = ""


@router.post("/test")
async def test_provider(body: ProviderTest) -> dict:
    """Test connectivity to a provider and specific model."""
    try:
        provider = create_provider(body.provider, settings, model=body.model or None)
        response = await provider.generate("Say 'AgentForge is connected and working!' in one short sentence.")
        return {"success": True, "response": response}
    except Exception as e:
        logger.error("Provider test failed: %s", e)
        error_msg = str(e)
        for key in [settings.openai_api_key, settings.gemini_api_key, settings.anthropic_api_key]:
            if key and len(key) > 6:
                error_msg = error_msg.replace(key, "[REDACTED]")
        return {"success": False, "error": error_msg}

