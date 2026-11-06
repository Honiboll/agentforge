"""Writer agent — creates written content and documentation."""

from __future__ import annotations

from typing import Any

from agentforge.core.base_agent import BaseAgent, AgentStatus

SYSTEM_PROMPT = """\
You are a skilled technical writer. Produce clear, concise, and well-structured \
content. Use appropriate headings, lists, and formatting. Adapt your tone to \
the target audience."""


class WriterAgent(BaseAgent):
    agent_type = "writer"

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("system_prompt", SYSTEM_PROMPT)
        super().__init__(**kwargs)

    async def execute(self, task: str, context: dict[str, Any]) -> str:
        context_str = ""
        if context:
            context_str = "\n\nReference material:\n" + "\n".join(
                f"- {k}: {v[:500]}" for k, v in context.items()
            )
        prompt = f"Write the following content:\n\n{task}{context_str}"

        await self.update_status(AgentStatus.WORKING)
        await self.log("Writing content…")
        result = await self.think(prompt)
        await self.log(f"Produced {len(result.split())} words.")
        return result

