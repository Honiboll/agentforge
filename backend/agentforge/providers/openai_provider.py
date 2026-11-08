"""OpenAI-compatible provider using raw httpx."""

from __future__ import annotations

import httpx

from agentforge.providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    name = "openai"

    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: str = "https://api.openai.com/v1") -> None:
        self.api_key = api_key.strip() if api_key else ""
        m = (model or "gpt-4o").strip().strip('"').strip("'")
        if m.startswith("openai/"):
            m = m[len("openai/"):]
        self.model = m or "gpt-4o"
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")

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
                    if not err_msg:
                        err_msg = resp.reason_phrase

                    if "model_not_found" in err_msg.lower() or "does not exist" in err_msg.lower() or resp.status_code == 404:
                        err_msg += f" — The model '{self.model}' was not found at {self.base_url}. Please check the exact model name or API provider."
                    elif resp.status_code == 401:
                        err_msg += f" — Authentication failed at {self.base_url}. If this key is from a third-party, reseller, or proxy service, please enter the service's API Base URL in the Custom Provider settings."

                    raise RuntimeError(f"OpenAI API Error ({resp.status_code}): {err_msg}")

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


