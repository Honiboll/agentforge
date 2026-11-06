"""Factory function to instantiate the right LLM provider from config."""

from __future__ import annotations

from agentforge.config import Settings
from agentforge.providers.base import BaseLLMProvider


def create_provider(provider_name: str, config: Settings) -> BaseLLMProvider:
    """Return a configured provider instance."""

    match provider_name.lower():
        case "openai":
            from agentforge.providers.openai_provider import OpenAIProvider
            if not config.openai_api_key:
                raise ValueError("OPENAI_API_KEY is not set.")
            return OpenAIProvider(api_key=config.openai_api_key, model=config.openai_model)

        case "gemini":
            from agentforge.providers.gemini_provider import GeminiProvider
            if not config.gemini_api_key:
                raise ValueError("GEMINI_API_KEY is not set.")
            return GeminiProvider(api_key=config.gemini_api_key, model=config.gemini_model)

        case "ollama":
            from agentforge.providers.ollama_provider import OllamaProvider
            return OllamaProvider(base_url=config.ollama_base_url, model=config.ollama_model)

        case "anthropic":
            from agentforge.providers.anthropic_provider import AnthropicProvider
            if not config.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY is not set.")
            return AnthropicProvider(api_key=config.anthropic_api_key, model=config.anthropic_model)

        case _:
            raise ValueError(
                f"Unknown provider: {provider_name!r}. "
                f"Choose from: openai, gemini, ollama, anthropic"
            )

