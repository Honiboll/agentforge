"""WebSocket endpoint for live event streaming."""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from agentforge.utils.events import event_bus
from agentforge.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{project_id}")
async def project_ws(websocket: WebSocket, project_id: str) -> None:
    await websocket.accept()
    queue = event_bus.subscribe(project_id)
    logger.info("WebSocket connected for project %s", project_id)

    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                await websocket.send_text(json.dumps(event.model_dump()))
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                await websocket.send_text(json.dumps({"event": "heartbeat", "project_id": project_id, "data": {}}))
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for project %s", project_id)
    finally:
        event_bus.unsubscribe(project_id, queue)

