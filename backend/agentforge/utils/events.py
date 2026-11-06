"""Event bus for real-time communication between agents and the frontend."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class Event(BaseModel):
    """A single event emitted by the system."""

    event: str
    project_id: str
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class EventBus:
    """Async publish/subscribe event bus scoped by project ID."""

    _instance: EventBus | None = None
    _subscribers: dict[str, list[asyncio.Queue[Event]]]

    def __new__(cls) -> EventBus:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers = {}
        return cls._instance

    def subscribe(self, project_id: str) -> asyncio.Queue[Event]:
        queue: asyncio.Queue[Event] = asyncio.Queue()
        self._subscribers.setdefault(project_id, []).append(queue)
        return queue

    def unsubscribe(self, project_id: str, queue: asyncio.Queue[Event]) -> None:
        if project_id in self._subscribers:
            try:
                self._subscribers[project_id].remove(queue)
            except ValueError:
                pass
            if not self._subscribers[project_id]:
                del self._subscribers[project_id]

    async def emit(self, project_id: str, event_name: str, data: dict[str, Any] | None = None) -> None:
        event = Event(event=event_name, project_id=project_id, data=data or {})
        for queue in self._subscribers.get(project_id, []):
            await queue.put(event)


event_bus = EventBus()

