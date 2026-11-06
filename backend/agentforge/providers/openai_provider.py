"""OpenAI-compatible provider using raw httpx."""

from __future__ import annotations

import httpx

from agentforge.providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    name = "openai"

    def __init__(self, api_key: str, model: str = "gpt-4o") -> None:
        self.api_key = api_key.strip() if api_key else ""
        self.model = model
        self.base_url = "https://api.openai.com/v1"

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is missing. Please enter your API key in Settings or the Provider selector."
            )

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                    },
                )
                if resp.is_error:
                    err_msg = ""
                    try:
                        d = resp.json()
                        if "error" in d:
                            err_obj = d["error"]
                            if isinstance(err_obj, dict):
                                err_msg = err_obj.get("message") or err_obj.get("code") or str(err_obj)
                            else:
                                err_msg = str(err_obj)
                    except Exception:
                        err_msg = resp.text[:300]
                    raise RuntimeError(f"OpenAI API Error ({resp.status_code}): {err_msg or resp.reason_phrase}")

                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except httpx.ConnectError:
            raise RuntimeError(
                "Failed to connect to OpenAI API. Please check your internet connection or proxy."
            )
        except httpx.TimeoutException:
            raise RuntimeError(
                "Request to OpenAI timed out (120s)."
            )


