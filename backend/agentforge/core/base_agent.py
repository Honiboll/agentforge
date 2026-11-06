"""Base agent class — every specialised agent inherits from here."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from agentforge.utils.events import event_bus
from agentforge.utils.logger import get_logger

if TYPE_CHECKING:
    from agentforge.providers.base import BaseLLMProvider

logger = get_logger(__name__)


class AgentStatus(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    DONE = "done"
    ERROR = "error"
    WAITING = "waiting"


class AgentLog(BaseModel):
    message: str
    level: str = "info"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentResult(BaseModel):
    agent_id: str
    agent_name: str
    role: str
    output: str
    success: bool = True
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """Abstract base class for all AgentForge agents."""

    agent_type: str = "base"

    def __init__(
        self,
        name: str,
        role: str,
        description: str,
        provider: BaseLLMProvider,
        project_id: str,
        system_prompt: str = "",
    ) -> None:
        self.id = uuid.uuid4().hex
        self.name = name
        self.role = role
        self.description = description
        self.provider = provider
        self.project_id = project_id
        self.system_prompt = system_prompt
        self.status = AgentStatus.IDLE
        self.logs: list[AgentLog] = []
        self.created_at = datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run(self, task: str, context: dict[str, Any] | None = None) -> AgentResult:
        """Execute the agent's main task."""
        context = context or {}
        try:
            await self.update_status(AgentStatus.THINKING)
            await self.log(f"Starting task: {task[:120]}…")

            result_text = await self.execute(task, context)

            await self.update_status(AgentStatus.DONE)
            await self.log("Task completed successfully.")
            return AgentResult(
                agent_id=self.id,
                agent_name=self.name,
                role=self.role,
                output=result_text,
            )
        except Exception as exc:
            await self.update_status(AgentStatus.ERROR)
            await self.log(f"Error: {exc}", level="error")
            return AgentResult(
                agent_id=self.id,
                agent_name=self.name,
                role=self.role,
                output="",
                success=False,
                error=str(exc),
            )

    @abstractmethod
    async def execute(self, task: str, context: dict[str, Any]) -> str:
        """Subclasses implement their specific behaviour here."""
        ...

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def think(self, prompt: str) -> str:
        """Call the underlying LLM provider."""
        await self.update_status(AgentStatus.THINKING)
        await self.log("Thinking…")
        response = await self.provider.generate(prompt, system_prompt=self.system_prompt)
        return response

    async def log(self, message: str, level: str = "info") -> None:
        entry = AgentLog(message=message, level=level)
        self.logs.append(entry)
        logger.info("[%s] %s", self.name, message)
        await event_bus.emit(
            self.project_id,
            "agent_log",
            {"agent_id": self.id, "agent_name": self.name, "log": entry.model_dump()},
        )

    async def update_status(self, new_status: AgentStatus) -> None:
        old = self.status
        self.status = new_status
        await event_bus.emit(
            self.project_id,
            "agent_status_changed",
            {
                "agent_id": self.id,
                "agent_name": self.name,
                "old_status": old.value,
                "new_status": new_status.value,
            },
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "logs": [l.model_dump() for l in self.logs],
            "created_at": self.created_at.isoformat(),
        }

