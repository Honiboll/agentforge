"""Planner agent — creates detailed structured plans."""

from __future__ import annotations

from typing import Any

from agentforge.core.base_agent import BaseAgent, AgentStatus

SYSTEM_PROMPT = """\
You are a strategic planner. Create detailed, actionable plans with clear \
milestones, timelines, dependencies, and resource requirements. Use numbered \
steps and structured formatting."""


class PlannerAgent(BaseAgent):
    agent_type = "planner"

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("system_prompt", SYSTEM_PROMPT)
        super().__init__(**kwargs)

    async def execute(self, task: str, context: dict[str, Any]) -> str:
        context_str = ""
        if context:
            context_str = "\n\nContext:\n" + "\n".join(
                f"- {k}: {v[:500]}" for k, v in context.items()
            )
        prompt = f"Create a detailed plan for:\n\n{task}{context_str}"

        await self.update_status(AgentStatus.WORKING)
        await self.log("Planning…")
        result = await self.think(prompt)
        await self.log("Plan created.")
        return result

