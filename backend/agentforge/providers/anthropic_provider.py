"""Anthropic provider using raw httpx."""

from __future__ import annotations

import httpx

from agentforge.providers.base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    name = "anthropic"

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514") -> None:
        self.api_key = api_key.strip() if api_key else ""
        self.model = model

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        if not self.api_key:
            raise ValueError(
                "Anthropic API key is missing. Please enter your API key in Settings or the Provider selector."
            )

        body: dict = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        if system_prompt:
            body["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json",
                    },
                    json=body,
                )
                if resp.is_error:
                    err_msg = ""
                    try:
                        d = resp.json()
                        if "error" in d:
                            e = d["error"]
                            err_msg = e.get("message") if isinstance(e, dict) else str(e)
                    except Exception:
                        err_msg = resp.text[:300]
                    raise RuntimeError(f"Anthropic Claude API Error ({resp.status_code}): {err_msg or resp.reason_phrase}")

                data = resp.json()
                return data["content"][0]["text"]
        except httpx.ConnectError:
            raise RuntimeError(
                "Failed to connect to Anthropic API. Please check your internet connection or proxy."
            )
        except httpx.TimeoutException:
            raise RuntimeError(
                "Request to Anthropic Claude timed out (120s)."
            )


