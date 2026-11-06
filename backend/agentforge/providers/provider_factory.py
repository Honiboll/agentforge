"""Factory function to instantiate the right LLM provider from config."""

from __future__ import annotations

from agentforge.config import Settings
from agentforge.providers.base import BaseLLMProvider


def create_provider(provider_name: str, config: Settings, model: str | None = None) -> BaseLLMProvider:
    """Return a configured provider instance with optional model override."""

    match provider_name.lower():
        case "openai":
            from agentforge.providers.openai_provider import OpenAIProvider
            if not config.openai_api_key:
                raise ValueError("OpenAI API key is missing. Please enter your API key in Settings or the Provider selector.")
            return OpenAIProvider(api_key=config.openai_api_key, model=model or config.openai_model, base_url=config.openai_base_url)

        case "groq":
            from agentforge.providers.openai_provider import OpenAIProvider
            if not config.groq_api_key:
                raise ValueError("Groq API key is missing. Please enter your free Groq API key in Settings or the Provider selector.")
            return OpenAIProvider(
                api_key=config.groq_api_key,
                model=model or config.groq_model,
                base_url=config.groq_base_url or "https://api.groq.com/openai/v1",
            )

        case "custom" | "openai-compatible":
            from agentforge.providers.openai_provider import OpenAIProvider
            key = config.custom_api_key or config.openai_api_key
            if not key:
                raise ValueError("Custom provider API key is missing. Please enter your API key in Settings or the Provider selector.")
            base_url = config.custom_base_url or config.openai_base_url or "https://api.openai.com/v1"
            return OpenAIProvider(api_key=key, model=model or config.custom_model, base_url=base_url)

        case "gemini":
            from agentforge.providers.gemini_provider import GeminiProvider
            if not config.gemini_api_key:
                raise ValueError("Google Gemini API key is missing. Please enter your API key in Settings or the Provider selector.")
            return GeminiProvider(api_key=config.gemini_api_key, model=model or config.gemini_model)

        case "ollama":
            from agentforge.providers.ollama_provider import OllamaProvider
            return OllamaProvider(base_url=config.ollama_base_url, model=model or config.ollama_model)

        case "anthropic":
            from agentforge.providers.anthropic_provider import AnthropicProvider
            if not config.anthropic_api_key:
                raise ValueError("Anthropic API key is missing. Please enter your API key in Settings or the Provider selector.")
            return AnthropicProvider(api_key=config.anthropic_api_key, model=model or config.anthropic_model)

        case _:
            raise ValueError(
                f"Unknown provider: {provider_name!r}. "
                f"Choose from: openai, gemini, ollama, anthropic"
            )

