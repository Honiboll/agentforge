"""Google Gemini provider using raw httpx."""

from __future__ import annotations

import httpx

from agentforge.providers.base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        self.api_key = api_key.strip() if api_key else ""
        m = (model or "gemini-2.0-flash").strip().strip('"').strip("'")
        if m.startswith("models/"):
            m = m[len("models/"):]
        if m.startswith("google/"):
            m = m[len("google/"):]
        self.model = m or "gemini-2.0-flash"

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        if not self.api_key:
            raise ValueError(
                "Google Gemini API key is missing. Please enter your API key in Settings or the Provider selector."
            )

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )

        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        body: dict = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature},
        }
        if system_prompt:
            body["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(url, headers=headers, json=body)
                if resp.is_error:
                    error_detail = ""
                    try:
                        err_json = resp.json()
                        if "error" in err_json:
                            e = err_json["error"]
                            code = e.get("code", resp.status_code)
                            status = e.get("status", "")
                            msg = e.get("message", "")
                            error_detail = f"[{status or code}] {msg}"
                    except Exception:
                        error_detail = resp.text[:300]

                    if not error_detail:
                        error_detail = f"Status {resp.status_code}: {resp.reason_phrase}"

                    # Provide contextual diagnosis
                    if "User location is not supported" in error_detail:
                        error_detail += " — Google Gemini is geographically restricted in your current IP location. Please connect through a supported VPN/Proxy (e.g. US/Europe) or switch to Ollama / OpenAI."
                    elif "not found" in error_detail.lower() or "is not supported for generatecontent" in error_detail.lower() or resp.status_code == 404:
                        error_detail += f" — The model '{self.model}' was not found in Google Gemini. Valid models include: gemini-2.0-flash, gemini-1.5-flash, gemini-1.5-pro."
                    elif "API key not valid" in error_detail or resp.status_code in (400, 401, 403):
                        error_detail += " — Verify your Gemini API key in Settings or get a new key from Google AI Studio."
                    elif "RESOURCE_EXHAUSTED" in error_detail or resp.status_code == 429:
                        error_detail += " — Gemini quota or rate limit exceeded. Please wait a minute or use another model."

                    raise RuntimeError(f"Google Gemini API Error: {error_detail}")

                data = resp.json()
                candidates = data.get("candidates", [])
                if not candidates or "content" not in candidates[0]:
                    block_reason = data.get("promptFeedback", {}).get("blockReason", "Safety filters triggered or no output")
                    raise RuntimeError(f"Gemini returned empty response: {block_reason}")
                return candidates[0]["content"]["parts"][0]["text"]

        except httpx.ConnectError:
            raise RuntimeError(
                "Failed to connect to Google Gemini API. Please check your internet connection, proxy, or VPN."
            )
        except httpx.TimeoutException:
            raise RuntimeError(
                "Request to Google Gemini timed out (120s). The service may be slow or overloaded."
            )


