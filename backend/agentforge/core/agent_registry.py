"""Agent Registry — maps type names to agent classes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentforge.utils.logger import get_logger

if TYPE_CHECKING:
    from agentforge.core.base_agent import BaseAgent

logger = get_logger(__name__)


class AgentRegistry:
    """Singleton registry of agent type name → agent class."""

    _instance: AgentRegistry | None = None
    _registry: dict[str, type[BaseAgent]]

    def __new__(cls) -> AgentRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._registry = {}
        return cls._instance

    def register(self, name: str, agent_class: type[BaseAgent]) -> None:
        self._registry[name] = agent_class
        logger.info("Registered agent type: %s", name)

    def get(self, name: str) -> type[BaseAgent]:
        if name not in self._registry:
            raise KeyError(f"Unknown agent type: {name!r}. Available: {list(self._registry)}")
        return self._registry[name]

    def list_types(self) -> list[str]:
        return list(self._registry.keys())


registry = AgentRegistry()

