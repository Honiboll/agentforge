"""Factory function to instantiate the right LLM provider from config."""

from __future__ import annotations

from agentforge.config import Settings
from agentforge.providers.base import BaseLLMProvider


def create_provider(provider_name: str, config: Settings, model: str | None = None) -> BaseLLMProvider:
    """Return a configured provider instance with optional model override."""
    p = (provider_name or "").lower().strip()

    if p == "openai":
        from agentforge.providers.openai_provider import OpenAIProvider
        key = config.openai_api_key or config.custom_api_key
        if not key:
            raise ValueError("OpenAI API key is missing. Please enter your API key in Settings or the Provider selector.")
        return OpenAIProvider(api_key=key, model=model or config.openai_model, base_url=config.openai_base_url)

    elif p == "groq":
        from agentforge.providers.openai_provider import OpenAIProvider
        key = config.groq_api_key
        if not key:
            raise ValueError("Groq API key is missing. Please enter your free Groq API key in Settings or the Provider selector.")
        if key.startswith("xai-"):
            # Self-healing: User provided an xAI Grok key in Groq field
            return OpenAIProvider(
                api_key=key,
                model=model if model and not "llama" in model else "grok-2-latest",
                base_url="https://api.x.ai/v1",
            )
        return OpenAIProvider(
            api_key=key,
            model=model or config.groq_model,
            base_url=config.groq_base_url or "https://api.groq.com/openai/v1",
        )

    elif p in ("xai", "grok"):
        from agentforge.providers.openai_provider import OpenAIProvider
        key = config.xai_api_key or (config.groq_api_key if config.groq_api_key.startswith("xai-") else "")
        if not key:
            raise ValueError("xAI Grok API key is missing. Please enter your xAI API key (starts with 'xai-') in Settings or the Provider selector.")
        return OpenAIProvider(
            api_key=key,
            model=model or config.xai_model,
            base_url=config.xai_base_url or "https://api.x.ai/v1",
        )

    elif p == "gemini":
        from agentforge.providers.gemini_provider import GeminiProvider
        if not config.gemini_api_key:
            raise ValueError("Google Gemini API key is missing. Please enter your API key in Settings or the Provider selector.")
        return GeminiProvider(api_key=config.gemini_api_key, model=model or config.gemini_model)

    elif p == "anthropic":
        from agentforge.providers.anthropic_provider import AnthropicProvider
        if not config.anthropic_api_key:
            raise ValueError("Anthropic API key is missing. Please enter your API key in Settings or the Provider selector.")
        return AnthropicProvider(api_key=config.anthropic_api_key, model=model or config.anthropic_model)

    elif p == "ollama":
        from agentforge.providers.ollama_provider import OllamaProvider
        return OllamaProvider(base_url=config.ollama_base_url, model=model or config.ollama_model)

    elif p in ("custom", "openai-compatible", "universal"):
        from agentforge.providers.openai_provider import OpenAIProvider
        key = config.custom_api_key or config.openai_api_key or config.groq_api_key or config.xai_api_key
        if not key:
            raise ValueError("Universal / Custom provider API key is missing. Please enter your API key in Settings or the Provider selector.")
        base_url = config.custom_base_url or config.openai_base_url or "https://api.openai.com/v1"
        return OpenAIProvider(api_key=key, model=model or config.custom_model, base_url=base_url)

    else:
        from agentforge.providers.openai_provider import OpenAIProvider
        key = config.custom_api_key or config.openai_api_key or config.groq_api_key
        if not key:
            raise ValueError(f"Provider '{provider_name}' requires an API key. Please configure your key in Settings.")
        return OpenAIProvider(api_key=key, model=model or "gpt-4o", base_url=config.custom_base_url or "https://api.openai.com/v1")

