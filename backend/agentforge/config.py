"""Application settings loaded from environment variables."""

from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def find_env_file() -> Path:
    candidates = [
        Path(".env"),
        Path("../.env"),
        REPO_ROOT / ".env",
        Path.cwd() / ".env",
    ]
    for c in candidates:
        if c.is_file():
            return c.resolve()
    return (REPO_ROOT / ".env").resolve()


def save_key_to_env(key_name: str, key_val: str) -> Path:
    """Save or update an API key in the discovered .env file."""
    env_path = find_env_file()
    lines: list[str] = []
    if env_path.is_file():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    updated = False
    new_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{key_name}=") or stripped.startswith(f"# {key_name}="):
            new_lines.append(f"{key_name}={key_val}")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f"{key_name}={key_val}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return env_path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", str(REPO_ROOT / ".env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- LLM Provider ---
    default_llm_provider: str = "ollama"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_base_url: str = "https://api.openai.com/v1"

    # Google Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # Ollama (local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Groq (Fast & Free)
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    # xAI Grok (Grok-2, Grok-beta)
    xai_api_key: str = ""
    xai_model: str = "grok-2-latest"
    xai_base_url: str = "https://api.x.ai/v1"

    # Custom / OpenAI-Compatible (DeepSeek, OpenRouter, vLLM, LM Studio)
    custom_api_key: str = ""
    custom_base_url: str = "https://api.openai.com/v1"
    custom_model: str = "gpt-4o"

    # --- Backend ---
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    database_url: str = "sqlite+aiosqlite:///./agentforge.db"
    secret_key: str = "change-me-to-a-random-string"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # --- Operational ---
    log_level: str = "INFO"
    max_concurrent_agents: int = 10
    agent_timeout_seconds: int = 300


settings = Settings()

