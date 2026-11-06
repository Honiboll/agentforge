"""Provider management API routes with dynamic model and API key inspection."""

from __future__ import annotations

import logging
import time
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


# Default fallback models in case network is unreachable or keys are missing
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
        {"id": "o1", "name": "OpenAI o1", "description": "Advanced reasoning and problem-solving"},
        {"id": "o1-mini", "name": "OpenAI o1 Mini", "description": "Fast reasoning for math & code"},
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

# Cache for fetched models: provider -> (timestamp, models)
_model_cache: dict[str, tuple[float, list[ModelOption]]] = {}
CACHE_TTL = 300.0  # 5 minutes


async def _probe_ollama_models() -> tuple[bool, list[ModelOption]]:
    """Probe local Ollama daemon dynamically for any newly installed or pulled models."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
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
    return False, [ModelOption(**m) for m in DEFAULT_MODELS["ollama"]]


async def _fetch_gemini_models(api_key: str) -> list[ModelOption]:
    """Dynamically query Google Gemini API to discover newly released models."""
    if not api_key:
        return [ModelOption(**m) for m in DEFAULT_MODELS["gemini"]]

    now = time.time()
    if "gemini" in _model_cache and (now - _model_cache["gemini"][0]) < CACHE_TTL:
        return _model_cache["gemini"][1]

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(
                "https://generativelanguage.googleapis.com/v1beta/models",
                headers={"x-goog-api-key": api_key},
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("models", [])
                discovered: list[ModelOption] = []
                for item in items:
                    methods = item.get("supportedGenerationMethods", [])
                    if "generateContent" in methods:
                        raw_name = item.get("name", "").replace("models/", "")
                        # Filter for core generative models (exclude vision-only, embedding, etc.)
                        if "gemini" in raw_name and not any(x in raw_name for x in ["embedding", "aqa", "imagen"]):
                            discovered.append(
                                ModelOption(
                                    id=raw_name,
                                    name=item.get("displayName", raw_name),
                                    description=item.get("description", "Google generative AI model")[:90] + "…",
                                )
                            )
                if discovered:
                    # Sort so newest/flash models appear near the top
                    discovered.sort(key=lambda x: (not x.id.startswith("gemini-2"), not "flash" in x.id, x.id))
                    _model_cache["gemini"] = (now, discovered)
                    return discovered
    except Exception as exc:
        logger.warning("Could not dynamically fetch Gemini models: %s", exc)

    return [ModelOption(**m) for m in DEFAULT_MODELS["gemini"]]


async def _fetch_openai_models(api_key: str) -> list[ModelOption]:
    """Dynamically query OpenAI API to discover newly released models."""
    if not api_key:
        return [ModelOption(**m) for m in DEFAULT_MODELS["openai"]]

    now = time.time()
    if "openai" in _model_cache and (now - _model_cache["openai"][0]) < CACHE_TTL:
        return _model_cache["openai"][1]

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("data", [])
                valid_ids: list[str] = []
                for item in items:
                    mid = item.get("id", "")
                    # Filter for chat and reasoning models
                    if (
                        mid.startswith(("gpt-4", "gpt-3.5", "o1", "o3", "chatgpt"))
                        and not any(x in mid for x in ["audio", "realtime", "search", "transcription", "instruct"])
                    ):
                        valid_ids.append(mid)

                if valid_ids:
                    # Remove dated snapshots (e.g. gpt-4o-2024-05-13) unless canonical
                    canonical = [m for m in valid_ids if not any(c.isdigit() and len(c) == 8 for c in m.split("-"))]
                    if not canonical:
                        canonical = valid_ids[:10]

                    # Prioritize flagship
                    priority_order = ["gpt-4o", "gpt-4o-mini", "o1", "o1-mini", "o3-mini", "gpt-4-turbo"]
                    canonical.sort(key=lambda x: priority_order.index(x) if x in priority_order else 99)

                    discovered = [
                        ModelOption(
                            id=mid,
                            name=mid.upper().replace("-", " "),
                            description=f"OpenAI {mid} model",
                        )
                        for mid in canonical
                    ]
                    _model_cache["openai"] = (now, discovered)
                    return discovered
    except Exception as exc:
        logger.warning("Could not dynamically fetch OpenAI models: %s", exc)

    return [ModelOption(**m) for m in DEFAULT_MODELS["openai"]]


async def _fetch_anthropic_models(api_key: str) -> list[ModelOption]:
    """Dynamically query Anthropic API to discover newly released models."""
    if not api_key:
        return [ModelOption(**m) for m in DEFAULT_MODELS["anthropic"]]

    now = time.time()
    if "anthropic" in _model_cache and (now - _model_cache["anthropic"][0]) < CACHE_TTL:
        return _model_cache["anthropic"][1]

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(
                "https://api.anthropic.com/v1/models",
                headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("data", [])
                if items:
                    discovered = [
                        ModelOption(
                            id=item.get("id", ""),
                            name=item.get("display_name", item.get("id", "")),
                            description="Anthropic Claude model",
                        )
                        for item in items
                        if item.get("id")
                    ]
                    if discovered:
                        _model_cache["anthropic"] = (now, discovered)
                        return discovered
    except Exception as exc:
        logger.warning("Could not dynamically fetch Anthropic models: %s", exc)

    return [ModelOption(**m) for m in DEFAULT_MODELS["anthropic"]]


@router.get("/", response_model=list[ProviderInfo])
async def list_providers(refresh: bool = False) -> list[dict[str, Any]]:
    """Return all providers with dynamic real-time models queried directly from APIs."""
    if refresh:
        _model_cache.clear()

    has_gemini = bool(settings.gemini_api_key and settings.gemini_api_key.strip())
    has_openai = bool(settings.openai_api_key and settings.openai_api_key.strip())
    has_anthropic = bool(settings.anthropic_api_key and settings.anthropic_api_key.strip())

    # Probe all providers concurrently
    import asyncio
    ollama_task = _probe_ollama_models()
    gemini_task = _fetch_gemini_models(settings.gemini_api_key)
    openai_task = _fetch_openai_models(settings.openai_api_key)
    anthropic_task = _fetch_anthropic_models(settings.anthropic_api_key)

    (ollama_online, ollama_models), gemini_models, openai_models, anthropic_models = await asyncio.gather(
        ollama_task, gemini_task, openai_task, anthropic_task
    )

    return [
        {
            "name": "gemini",
            "label": "Google Gemini",
            "is_available": has_gemini,
            "requires_key": True,
            "has_key": has_gemini,
            "default_model": settings.gemini_model,
            "models": gemini_models,
        },
        {
            "name": "openai",
            "label": "OpenAI",
            "is_available": has_openai,
            "requires_key": True,
            "has_key": has_openai,
            "default_model": settings.openai_model,
            "models": openai_models,
        },
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
            "name": "anthropic",
            "label": "Anthropic",
            "is_available": has_anthropic,
            "requires_key": True,
            "has_key": has_anthropic,
            "default_model": settings.anthropic_model,
            "models": anthropic_models,
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

