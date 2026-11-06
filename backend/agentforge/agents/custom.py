"""Custom agent — generic agent with user-provided system prompt."""

from __future__ import annotations

from typing import Any

from agentforge.core.base_agent import BaseAgent, AgentStatus


class CustomAgent(BaseAgent):
    agent_type = "custom"

    async def execute(self, task: str, context: dict[str, Any]) -> str:
        context_str = ""
        if context:
            context_str = "\n\nContext:\n" + "\n".join(
                f"- {k}: {v[:500]}" for k, v in context.items()
            )
        prompt = f"{task}{context_str}"

        await self.update_status(AgentStatus.WORKING)
        await self.log("Working on task…")
        result = await self.think(prompt)
        await self.log("Task complete.")
        return result

