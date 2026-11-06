"""Tests for the orchestrator."""

import pytest

from agentforge.core.orchestrator import Orchestrator, ProjectResult

import agentforge.agents  # noqa: F401


class FakeProvider:
    name = "fake"

    async def generate(self, prompt, system_prompt=None, temperature=0.7):
        # If prompt looks like the analysis prompt, return a plan
        if "Respond ONLY with valid JSON" in prompt or "decompose" in prompt.lower():
            return """{
  "project_title": "Test Project",
  "summary": "Testing the orchestrator.",
  "tasks": [
    {
      "name": "Research",
      "description": "Research the topic",
      "agent_type": "researcher",
      "dependencies": [],
      "priority": 1
    },
    {
      "name": "Write",
      "description": "Write about findings",
      "agent_type": "writer",
      "dependencies": [0],
      "priority": 2
    }
  ]
}"""
        return "Fake agent output for: " + prompt[:80]


@pytest.mark.asyncio
async def test_orchestrator_end_to_end():
    orch = Orchestrator(provider=FakeProvider())
    result = await orch.process_request("test-project-001", "Build a simple app")

    assert isinstance(result, ProjectResult)
    assert result.success is True
    assert result.project_id == "test-project-001"
    assert len(result.agent_results) == 2
    assert result.agent_results[0].role == "researcher"
    assert result.agent_results[1].role == "writer"

