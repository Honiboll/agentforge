"""Ollama local provider using raw httpx."""

from __future__ import annotations

import httpx

from agentforge.providers.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    name = "ollama"

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2") -> None:
        self.base_url = base_url.rstrip("/")
        m = (model or "llama3.2").strip().strip('"').strip("'")
        if m.startswith("ollama/"):
            m = m[len("ollama/"):]
        self.model = m or "llama3.2"

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient(timeout=300) as client:
                resp = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": {"temperature": temperature},
                    },
                )
                if resp.is_error:
                    err_msg = ""
                    try:
                        err_msg = resp.json().get("error", "")
                    except Exception:
                        err_msg = resp.text[:300]
                    raise RuntimeError(f"Ollama Error ({resp.status_code}): {err_msg or resp.reason_phrase}")

                data = resp.json()
                return data["message"]["content"]
        except httpx.ConnectError:
            raise RuntimeError(
                f"Cannot connect to Ollama at {self.base_url}. Please ensure Ollama is installed and running on your machine (e.g. run 'ollama run {self.model}' in your terminal)."
            )
        except httpx.TimeoutException:
            raise RuntimeError(
                f"Request to Ollama timed out (300s). The model '{self.model}' may be too large or slow for your hardware."
            )


