"""Coder agent — writes clean, documented code."""

from __future__ import annotations

from typing import Any

from agentforge.core.base_agent import BaseAgent, AgentStatus

SYSTEM_PROMPT = """\
You are an expert software engineer. Write clean, well-documented, and \
production-quality code. Follow best practices for the language and framework \
being used. Include comments, type hints, and error handling."""


class CoderAgent(BaseAgent):
    agent_type = "coder"

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("system_prompt", SYSTEM_PROMPT)
        super().__init__(**kwargs)

    async def execute(self, task: str, context: dict[str, Any]) -> str:
        context_str = ""
        if context:
            context_str = "\n\nContext from previous agents:\n" + "\n".join(
                f"- {k}: {v[:500]}" for k, v in context.items()
            )
        prompt = f"Write code for the following task:\n\n{task}{context_str}"

        await self.update_status(AgentStatus.WORKING)
        await self.log("Writing code…")
        result = await self.think(prompt)
        await self.log("Code generation complete.")
        return result

