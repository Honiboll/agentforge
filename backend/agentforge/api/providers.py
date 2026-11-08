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
    "groq": [
        {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B Versatile", "description": "Ultra-fast open weights with top-tier reasoning (Free & Recommended)"},
        {"id": "deepseek-r1-distill-llama-70b", "name": "DeepSeek R1 Distill 70B", "description": "High-speed deep reasoning on Groq LPUs"},
        {"id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B Instant", "description": "Blazing fast 800+ tokens/sec response time"},
        {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B", "description": "Fast mixture-of-experts 32k context"},
    ],
    "xai": [
        {"id": "grok-2-latest", "name": "Grok 2 Latest", "description": "Flagship multimodal & reasoning model by xAI (Recommended)"},
        {"id": "grok-2", "name": "Grok 2", "description": "State-of-the-art Grok 2 reasoning"},
        {"id": "grok-beta", "name": "Grok Beta", "description": "High-performance Grok beta intelligence"},
        {"id": "grok-2-vision-1212", "name": "Grok 2 Vision", "description": "Multimodal vision & document analysis"},
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
    "custom": [
        {"id": "gpt-4o", "name": "GPT-4o (Universal)", "description": "Default flagship model for OpenAI-compatible APIs"},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "description": "Fast and lightweight general model"},
        {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B", "description": "High-performance open weights reasoning"},
        {"id": "deepseek-chat", "name": "DeepSeek Chat", "description": "DeepSeek V3 / R1 reasoning (OpenAI-compatible)"},
        {"id": "mistral-large-latest", "name": "Mistral Large", "description": "Mistral AI flagship reasoning"},
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


async def _fetch_groq_models(api_key: str) -> list[ModelOption]:
    """Dynamically query Groq API to discover available models."""
    if not api_key:
        return [ModelOption(**m) for m in DEFAULT_MODELS["groq"]]

    now = time.time()
    if "groq" in _model_cache and (now - _model_cache["groq"][0]) < CACHE_TTL:
        return _model_cache["groq"][1]

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("data", [])
                valid_ids: list[str] = []
                for item in items:
                    mid = item.get("id", "")
                    # Filter out non-chat models (audio transcription, guard, vision-preview, etc.)
                    if not any(x in mid.lower() for x in ["whisper", "guard", "vision-preview", "tts", "embedding"]):
                        valid_ids.append(mid)

                if valid_ids:
                    # Prioritize versatile & reasoning models
                    priority_order = [
                        "llama-3.3-70b-versatile",
                        "deepseek-r1-distill-llama-70b",
                        "llama-3.1-8b-instant",
                        "mixtral-8x7b-32768",
                        "gemma2-9b-it",
                    ]
                    valid_ids.sort(key=lambda x: priority_order.index(x) if x in priority_order else 99)

                    discovered = [
                        ModelOption(
                            id=mid,
                            name=mid.replace("-", " ").title(),
                            description=f"Groq high-speed LPU model: {mid}",
                        )
                        for mid in valid_ids
                    ]
                    _model_cache["groq"] = (now, discovered)
                    return discovered
    except Exception as exc:
        logger.warning("Could not dynamically fetch Groq models: %s", exc)

    return [ModelOption(**m) for m in DEFAULT_MODELS["groq"]]


async def _fetch_xai_models(api_key: str) -> list[ModelOption]:
    """Dynamically query xAI Grok API to discover available models."""
    if not api_key:
        return [ModelOption(**m) for m in DEFAULT_MODELS["xai"]]

    now = time.time()
    if "xai" in _model_cache and (now - _model_cache["xai"][0]) < CACHE_TTL:
        return _model_cache["xai"][1]

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(
                "https://api.x.ai/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("data", [])
                valid_ids: list[str] = []
                for item in items:
                    mid = item.get("id", "")
                    if "grok" in mid.lower() and not any(x in mid.lower() for x in ["embedding"]):
                        valid_ids.append(mid)

                if valid_ids:
                    priority_order = ["grok-2-latest", "grok-2", "grok-beta", "grok-2-vision-1212"]
                    valid_ids.sort(key=lambda x: priority_order.index(x) if x in priority_order else 99)

                    discovered = [
                        ModelOption(
                            id=mid,
                            name=mid.replace("-", " ").title(),
                            description=f"xAI Grok model: {mid}",
                        )
                        for mid in valid_ids
                    ]
                    _model_cache["xai"] = (now, discovered)
                    return discovered
    except Exception as exc:
        logger.warning("Could not dynamically fetch xAI Grok models: %s", exc)

    return [ModelOption(**m) for m in DEFAULT_MODELS["xai"]]


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
    has_xai = bool(settings.xai_api_key and settings.xai_api_key.strip()) or bool(settings.groq_api_key and settings.groq_api_key.startswith("xai-"))
    has_groq = bool(settings.groq_api_key and settings.groq_api_key.strip() and not settings.groq_api_key.startswith("xai-"))
    has_openai = bool(settings.openai_api_key and settings.openai_api_key.strip())
    has_anthropic = bool(settings.anthropic_api_key and settings.anthropic_api_key.strip())

    # Probe all providers concurrently
    import asyncio
    xai_key_to_use = settings.xai_api_key or (settings.groq_api_key if settings.groq_api_key.startswith("xai-") else "")
    ollama_task = _probe_ollama_models()
    gemini_task = _fetch_gemini_models(settings.gemini_api_key)
    xai_task = _fetch_xai_models(xai_key_to_use)
    groq_task = _fetch_groq_models(settings.groq_api_key if not settings.groq_api_key.startswith("xai-") else "")
    openai_task = _fetch_openai_models(settings.openai_api_key)
    anthropic_task = _fetch_anthropic_models(settings.anthropic_api_key)

    (ollama_online, ollama_models), gemini_models, xai_models, groq_models, openai_models, anthropic_models = await asyncio.gather(
        ollama_task, gemini_task, xai_task, groq_task, openai_task, anthropic_task
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
            "name": "xai",
            "label": "xAI Grok",
            "is_available": has_xai,
            "requires_key": True,
            "has_key": has_xai,
            "default_model": settings.xai_model,
            "models": xai_models,
        },
        {
            "name": "groq",
            "label": "Groq (Fast & Free)",
            "is_available": has_groq,
            "requires_key": True,
            "has_key": has_groq,
            "default_model": settings.groq_model,
            "models": groq_models,
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
        {
            "name": "custom",
            "label": "Universal / Custom",
            "is_available": bool(settings.custom_api_key or settings.openai_api_key),
            "requires_key": True,
            "has_key": bool(settings.custom_api_key or settings.openai_api_key),
            "default_model": settings.custom_model,
            "models": [ModelOption(**m) for m in DEFAULT_MODELS["custom"]],
        },
    ]


class SaveKeyRequest(BaseModel):
    provider: str
    api_key: str
    base_url: str | None = None


@router.post("/key")
async def save_api_key(body: SaveKeyRequest) -> dict[str, Any]:
    """Save an API key directly from UI, update in-memory settings, and persist to .env."""
    provider_name = body.provider.lower().strip()
    key_val = body.api_key.strip()

    if not key_val:
        return {"success": False, "error": "API key cannot be empty"}

    # Auto-reroute if key prefix does not match provider selected
    if key_val.startswith("xai-") and provider_name in ("groq", "openai"):
        provider_name = "xai"
    elif key_val.startswith("gsk_") and provider_name in ("xai", "openai"):
        provider_name = "groq"

    key_map = {
        "gemini": "GEMINI_API_KEY",
        "xai": "XAI_API_KEY",
        "groq": "GROQ_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "custom": "CUSTOM_API_KEY",
        "universal": "CUSTOM_API_KEY",
    }

    if provider_name not in key_map:
        provider_name = "custom"

    env_var_name = key_map.get(provider_name, "CUSTOM_API_KEY")

    # 1. Update in-memory settings immediately
    if provider_name == "gemini":
        settings.gemini_api_key = key_val
    elif provider_name == "xai":
        settings.xai_api_key = key_val
        if settings.groq_api_key.startswith("xai-"):
            settings.groq_api_key = ""
    elif provider_name == "groq":
        settings.groq_api_key = key_val
    elif provider_name == "openai":
        settings.openai_api_key = key_val
    elif provider_name == "anthropic":
        settings.anthropic_api_key = key_val
    elif provider_name in ("custom", "universal"):
        settings.custom_api_key = key_val
        if not settings.openai_api_key:
            settings.openai_api_key = key_val
        if body.base_url and body.base_url.strip():
            settings.custom_base_url = body.base_url.strip()
            from agentforge.config import save_key_to_env
            save_key_to_env("CUSTOM_BASE_URL", body.base_url.strip())

    # 2. Invalidate model cache so fresh models are fetched right away
    _model_cache.pop(provider_name, None)

    # 3. Persist to .env file on disk
    from agentforge.config import save_key_to_env
    env_file = save_key_to_env(env_var_name, key_val)

    logger.info("Saved %s to %s via web UI", env_var_name, env_file)

    return {
        "success": True,
        "message": f"{provider_name.capitalize()} key saved and activated!",
        "provider": provider_name,
    }


class DetectKeyRequest(BaseModel):
    api_key: str


class DetectKeyResponse(BaseModel):
    success: bool
    provider: str | None = None
    provider_label: str | None = None
    message: str | None = None
    unlocked_models: list[str] = []
    error: str | None = None


@router.post("/detect-key", response_model=DetectKeyResponse)
async def auto_detect_and_save_key(body: DetectKeyRequest) -> dict[str, Any]:
    """Automatically detect which AI provider an API key belongs to, verify, and activate it."""
    raw_key = body.api_key.strip()
    if not raw_key:
        return {"success": False, "error": "Please paste an API key to detect."}

    # Clean quotes
    if (raw_key.startswith('"') and raw_key.endswith('"')) or (raw_key.startswith("'") and raw_key.endswith("'")):
        raw_key = raw_key[1:-1].strip()

    detected_provider: str | None = None
    detected_label: str | None = None
    discovered_models: list[str] = []

    # 1. Fast immediate match by key prefix (Instant zero-wait, no hanging network calls!)
    if raw_key.startswith("xai-"):
        detected_provider, detected_label, discovered_models = "xai", "xAI Grok", ["grok-2-latest", "grok-2", "grok-beta", "grok-2-vision-1212"]
    elif raw_key.startswith("gsk_"):
        detected_provider, detected_label, discovered_models = "groq", "Groq (Fast & Free)", ["llama-3.3-70b-versatile", "deepseek-r1-distill-llama-70b", "llama-3.1-8b-instant"]
    elif raw_key.startswith("AIzaSy"):
        detected_provider, detected_label, discovered_models = "gemini", "Google Gemini", ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    elif raw_key.startswith("sk-ant-"):
        detected_provider, detected_label, discovered_models = "anthropic", "Anthropic Claude", ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"]
    elif raw_key.startswith(("sk-proj-", "sk-admin-")):
        detected_provider, detected_label, discovered_models = "openai", "OpenAI", ["gpt-4o", "gpt-4o-mini", "o1-mini"]
    elif not raw_key.startswith("sk-"):
        # For ANY other custom, reseller, or proxy key (like coa_..., local token, etc.):
        # Instant zero-latency acceptance without network probe delays!
        detected_provider = "custom"
        detected_label = "Universal / Custom Key"
        discovered_models = ["gpt-4o", "gpt-4o-mini", "llama-3.3-70b-versatile", "deepseek-chat"]

    # 2. Only probe external APIs if it's a generic unconfirmed key (like legacy sk-...)
    if not detected_provider:
        # Probe 1: Google Gemini
        async def probe_gemini(key: str) -> tuple[bool, list[str]]:
            try:
                async with httpx.AsyncClient(timeout=1.5) as client:
                    resp = await client.get(
                        "https://generativelanguage.googleapis.com/v1beta/models",
                        headers={"x-goog-api-key": key},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        models = [
                            m.get("name", "").replace("models/", "")
                            for m in data.get("models", [])
                            if "generateContent" in m.get("supportedGenerationMethods", [])
                            and "gemini" in m.get("name", "")
                        ]
                        return True, models[:6]
            except Exception:
                pass
            return False, []

        # Probe 2: OpenAI
        async def probe_openai(key: str) -> tuple[bool, list[str]]:
            try:
                async with httpx.AsyncClient(timeout=1.5) as client:
                    resp = await client.get(
                        "https://api.openai.com/v1/models",
                        headers={"Authorization": f"Bearer {key}"},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        models = [
                            m.get("id", "")
                            for m in data.get("data", [])
                            if m.get("id", "").startswith(("gpt-4", "o1", "o3"))
                        ]
                        return True, models[:6]
            except Exception:
                pass
            return False, []

        import asyncio
        (gem_ok, gem_models), (oai_ok, oai_models) = await asyncio.gather(
            probe_gemini(raw_key), probe_openai(raw_key)
        )

        if gem_ok:
            detected_provider, detected_label, discovered_models = "gemini", "Google Gemini", gem_models
        elif oai_ok:
            detected_provider, detected_label, discovered_models = "openai", "OpenAI", oai_models
        else:
            detected_provider = "custom"
            detected_label = "Universal / Custom Key"
            discovered_models = ["gpt-4o", "gpt-4o-mini", "llama-3.3-70b-versatile", "deepseek-chat"]

    # Save and activate the key
    key_map = {
        "gemini": "GEMINI_API_KEY",
        "xai": "XAI_API_KEY",
        "groq": "GROQ_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "custom": "CUSTOM_API_KEY",
    }
    env_var_name = key_map.get(detected_provider, "CUSTOM_API_KEY")

    if detected_provider == "gemini":
        settings.gemini_api_key = raw_key
    elif detected_provider == "xai":
        settings.xai_api_key = raw_key
        if settings.groq_api_key.startswith("xai-"):
            settings.groq_api_key = ""
    elif detected_provider == "groq":
        settings.groq_api_key = raw_key
    elif detected_provider == "openai":
        settings.openai_api_key = raw_key
    elif detected_provider == "anthropic":
        settings.anthropic_api_key = raw_key
    elif detected_provider == "custom":
        settings.custom_api_key = raw_key
        if not settings.openai_api_key:
            settings.openai_api_key = raw_key

    _model_cache.pop(detected_provider, None)

    from agentforge.config import save_key_to_env
    env_file = save_key_to_env(env_var_name, raw_key)
    logger.info("Auto-detected and saved %s to %s via auto-detector", env_var_name, env_file)

    model_summary = f" ({len(discovered_models)} models unlocked)" if discovered_models else ""
    return {
        "success": True,
        "provider": detected_provider,
        "provider_label": detected_label,
        "message": f"Successfully activated as {detected_label}! Key saved and ready{model_summary}.",
        "unlocked_models": discovered_models,
    }


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
        for key in [settings.openai_api_key, settings.gemini_api_key, settings.groq_api_key, settings.xai_api_key, settings.anthropic_api_key]:
            if key and len(key) > 6:
                error_msg = error_msg.replace(key, "[REDACTED]")
        return {"success": False, "error": error_msg}

