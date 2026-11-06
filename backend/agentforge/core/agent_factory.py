"""Agent Factory — dynamically creates agent instances from an analysis plan."""

from __future__ import annotations

from agentforge.core.agent_registry import registry
from agentforge.core.analyzer import AnalysisPlan, TaskSpec
from agentforge.core.base_agent import BaseAgent
from agentforge.providers.base import BaseLLMProvider
from agentforge.utils.events import event_bus
from agentforge.utils.logger import get_logger

logger = get_logger(__name__)


class AgentFactory:
    """Creates agent instances from task specifications."""

    def create_agent(
        self,
        agent_type: str,
        task: TaskSpec,
        provider: BaseLLMProvider,
        project_id: str,
    ) -> BaseAgent:
        agent_cls = registry.get(agent_type)
        agent = agent_cls(
            name=task.name,
            role=agent_type,
            description=task.description,
            provider=provider,
            project_id=project_id,
        )
        logger.info("Created %s agent: %s", agent_type, task.name)
        return agent

    async def create_agents_from_plan(
        self,
        plan: AnalysisPlan,
        provider: BaseLLMProvider,
        project_id: str,
    ) -> list[BaseAgent]:
        agents: list[BaseAgent] = []
        for task in plan.tasks:
            agent = self.create_agent(task.agent_type, task, provider, project_id)
            agents.append(agent)
            await event_bus.emit(
                project_id,
                "agent_created",
                {
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "agent_type": agent.agent_type,
                    "role": agent.role,
                    "description": agent.description,
                },
            )
        return agents

