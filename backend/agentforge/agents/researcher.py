"""Researcher agent — gathers and synthesises information."""

from __future__ import annotations

from typing import Any

from agentforge.core.base_agent import BaseAgent, AgentStatus

SYSTEM_PROMPT = """\
You are an expert researcher. Your job is to thoroughly investigate the given \
topic and provide comprehensive, well-structured findings. Include key facts, \
relevant details, and actionable insights. Organise your output with clear \
headings and bullet points."""


class ResearcherAgent(BaseAgent):
    agent_type = "researcher"

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("system_prompt", SYSTEM_PROMPT)
        super().__init__(**kwargs)

    async def execute(self, task: str, context: dict[str, Any]) -> str:
        context_str = ""
        if context:
            context_str = "\n\nContext from previous agents:\n" + "\n".join(
                f"- {k}: {v[:500]}" for k, v in context.items()
            )
        prompt = f"Research the following topic and provide detailed findings:\n\n{task}{context_str}"

        await self.update_status(AgentStatus.WORKING)
        await self.log("Researching topic…")
        result = await self.think(prompt)
        await self.log(f"Found {len(result.split())} words of research.")
        return result

