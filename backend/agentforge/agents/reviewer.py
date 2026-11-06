"""Reviewer agent — reviews and provides quality assurance."""

from __future__ import annotations

from typing import Any

from agentforge.core.base_agent import BaseAgent, AgentStatus

SYSTEM_PROMPT = """\
You are a meticulous reviewer and QA specialist. Analyse the given work for \
correctness, completeness, quality, and potential improvements. Provide \
specific, actionable feedback organised by severity (critical, major, minor)."""


class ReviewerAgent(BaseAgent):
    agent_type = "reviewer"

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("system_prompt", SYSTEM_PROMPT)
        super().__init__(**kwargs)

    async def execute(self, task: str, context: dict[str, Any]) -> str:
        context_str = ""
        if context:
            context_str = "\n\nContent to review:\n" + "\n".join(
                f"--- {k} ---\n{v[:1000]}" for k, v in context.items()
            )
        prompt = f"Review the following and provide detailed feedback:\n\n{task}{context_str}"

        await self.update_status(AgentStatus.WORKING)
        await self.log("Reviewing…")
        result = await self.think(prompt)
        await self.log("Review complete.")
        return result

