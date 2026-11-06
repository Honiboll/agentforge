"""Tests for the agent system."""

import pytest

from agentforge.core.base_agent import AgentStatus
from agentforge.core.agent_registry import registry

# Ensure built-in agents are registered
import agentforge.agents  # noqa: F401


def test_registry_has_builtin_types():
    types = registry.list_types()
    assert "researcher" in types
    assert "coder" in types
    assert "reviewer" in types
    assert "writer" in types
    assert "planner" in types
    assert "custom" in types


def test_registry_get_unknown_raises():
    with pytest.raises(KeyError):
        registry.get("nonexistent_agent_type")


class FakeProvider:
    name = "fake"

    async def generate(self, prompt, system_prompt=None, temperature=0.7):
        return "Fake LLM response"


@pytest.mark.asyncio
async def test_agent_run():
    cls = registry.get("researcher")
    agent = cls(
        name="Test Researcher",
        role="researcher",
        description="A test agent",
        provider=FakeProvider(),
        project_id="test-project",
    )
    assert agent.status == AgentStatus.IDLE

    result = await agent.run("Test task")
    assert result.success is True
    assert result.output == "Fake LLM response"
    assert agent.status == AgentStatus.DONE
    assert len(agent.logs) > 0


@pytest.mark.asyncio
async def test_all_agent_types_can_run():
    for agent_type in registry.list_types():
        cls = registry.get(agent_type)
        agent = cls(
            name=f"Test {agent_type}",
            role=agent_type,
            description=f"Testing {agent_type}",
            provider=FakeProvider(),
            project_id="test-project",
        )
        result = await agent.run("Do something")
        assert result.success is True

