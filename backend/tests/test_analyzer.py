"""Tests for the task analyzer."""

import pytest

from agentforge.core.analyzer import TaskAnalyzer, AnalysisPlan


class FakeProvider:
    name = "fake"

    async def generate(self, prompt, system_prompt=None, temperature=0.7):
        return """{
  "project_title": "Test Project",
  "summary": "A test project for unit testing.",
  "tasks": [
    {
      "name": "Research best practices",
      "description": "Look into testing patterns",
      "agent_type": "researcher",
      "dependencies": [],
      "priority": 1
    },
    {
      "name": "Write code",
      "description": "Implement the solution",
      "agent_type": "coder",
      "dependencies": [0],
      "priority": 2
    }
  ]
}"""


@pytest.mark.asyncio
async def test_analyzer_produces_valid_plan():
    analyzer = TaskAnalyzer(provider=FakeProvider())
    plan = await analyzer.analyze("Build a todo app")

    assert isinstance(plan, AnalysisPlan)
    assert plan.project_title == "Test Project"
    assert len(plan.tasks) == 2
    assert plan.tasks[0].agent_type == "researcher"
    assert plan.tasks[1].dependencies == [0]


@pytest.mark.asyncio
async def test_analyzer_handles_malformed_json():
    class BrokenProvider:
        name = "broken"
        async def generate(self, prompt, system_prompt=None, temperature=0.7):
            return "This is not JSON at all."

    analyzer = TaskAnalyzer(provider=BrokenProvider())
    plan = await analyzer.analyze("Do something")

    # Should fall back to a single custom task
    assert isinstance(plan, AnalysisPlan)
    assert len(plan.tasks) == 1
    assert plan.tasks[0].agent_type == "custom"

