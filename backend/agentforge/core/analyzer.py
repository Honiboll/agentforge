"""Task Analyzer — uses LLM to decompose a user request into a structured plan."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field

from agentforge.providers.base import BaseLLMProvider
from agentforge.utils.events import event_bus
from agentforge.utils.logger import get_logger

logger = get_logger(__name__)

ANALYSIS_PROMPT = """\
You are an expert project analyst. Your job is to decompose a user's request \
into a list of discrete tasks. Each task should be assigned to one of these \
agent types: researcher, coder, reviewer, writer, planner, custom.

Respond ONLY with valid JSON matching this schema (no markdown fences):
{{
  "project_title": "short title",
  "summary": "one-paragraph summary",
  "tasks": [
    {{
      "name": "task name",
      "description": "what needs to be done",
      "agent_type": "one of the types above",
      "dependencies": [<indices of tasks this depends on>],
      "priority": <1-5, 1 is highest>
    }}
  ]
}}

User request:
{user_request}
"""


class TaskSpec(BaseModel):
    name: str
    description: str
    agent_type: str
    dependencies: list[int] = Field(default_factory=list)
    priority: int = 3


class AnalysisPlan(BaseModel):
    project_title: str
    summary: str
    tasks: list[TaskSpec]


class TaskAnalyzer:
    """Analyses a user request and produces a structured plan."""

    def __init__(self, provider: BaseLLMProvider) -> None:
        self.provider = provider

    async def analyze(self, user_request: str, project_id: str = "") -> AnalysisPlan:
        logger.info("Analyzing user request …")
        if project_id:
            await event_bus.emit(project_id, "analysis_started", {"request": user_request[:200]})

        prompt = ANALYSIS_PROMPT.format(user_request=user_request)
        raw = await self.provider.generate(
            prompt,
            system_prompt="You are a precise JSON-only analyst. Never output anything outside the JSON object.",
        )

        plan = self._parse_plan(raw)

        if project_id:
            await event_bus.emit(
                project_id,
                "analysis_completed",
                {"title": plan.project_title, "task_count": len(plan.tasks)},
            )

        return plan

    # ------------------------------------------------------------------

    @staticmethod
    def _parse_plan(raw: str) -> AnalysisPlan:
        """Robustly parse the LLM output into an AnalysisPlan."""
        text = raw.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[: text.rfind("```")]
        text = text.strip()

        try:
            data: dict[str, Any] = json.loads(text)
        except json.JSONDecodeError:
            # Fallback: create a single generic task
            return AnalysisPlan(
                project_title="User Project",
                summary=raw[:300],
                tasks=[
                    TaskSpec(
                        name="Complete the request",
                        description=raw[:500],
                        agent_type="custom",
                        priority=1,
                    )
                ],
            )

        return AnalysisPlan(**data)

