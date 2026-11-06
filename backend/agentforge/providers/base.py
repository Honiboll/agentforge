"""Abstract base class for LLM providers."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """Every LLM provider adapter implements this interface."""

    name: str = "base"

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate a plain-text completion."""
        ...

    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Generate a response conforming to a JSON schema."""
        schema_str = json.dumps(schema, indent=2)
        full_prompt = (
            f"{prompt}\n\n"
            f"Respond ONLY with valid JSON matching this schema:\n{schema_str}"
        )
        raw = await self.generate(full_prompt, system_prompt=system_prompt, temperature=0.3)
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[: text.rfind("```")]
        return json.loads(text.strip())

