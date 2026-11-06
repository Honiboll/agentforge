"""Project API routes."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agentforge.config import settings
from agentforge.core.orchestrator import Orchestrator
from agentforge.models.database import async_session, get_session
from agentforge.models.project import ProjectModel
from agentforge.providers.provider_factory import create_provider
from agentforge.utils.events import event_bus
from agentforge.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])

# In-memory store for running orchestrations
_running: dict[str, asyncio.Task[Any]] = {}


class ProjectCreate(BaseModel):
    user_request: str
    provider: str = ""
    model: str = ""


class ProjectOut(BaseModel):
    id: str
    title: str
    user_request: str
    status: str
    provider_name: str
    model_name: str | None = None
    error_message: str | None = None
    result: dict[str, Any] | None = None
    created_at: str


@router.post("/", response_model=ProjectOut)
async def create_project(
    body: ProjectCreate,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    project_id = uuid.uuid4().hex
    provider_name = body.provider or settings.default_llm_provider
    model_name = body.model.strip() if body.model else None
    project = ProjectModel(
        id=project_id,
        user_request=body.user_request,
        provider_name=provider_name,
        model_name=model_name,
        status="pending",
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return {
        "id": project.id,
        "title": project.title,
        "user_request": project.user_request,
        "status": project.status,
        "provider_name": project.provider_name,
        "model_name": project.model_name,
        "error_message": project.error_message,
        "result": project.result,
        "created_at": project.created_at.isoformat(),
    }


@router.get("/", response_model=list[ProjectOut])
async def list_projects(session: AsyncSession = Depends(get_session)) -> list[dict[str, Any]]:
    result = await session.execute(select(ProjectModel).order_by(ProjectModel.created_at.desc()))
    projects = result.scalars().all()
    return [
        {
            "id": p.id,
            "title": p.title,
            "user_request": p.user_request,
            "status": p.status,
            "provider_name": p.provider_name,
            "model_name": p.model_name,
            "error_message": p.error_message,
            "result": p.result,
            "created_at": p.created_at.isoformat(),
        }
        for p in projects
    ]


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    project = await session.get(ProjectModel, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "id": project.id,
        "title": project.title,
        "user_request": project.user_request,
        "status": project.status,
        "provider_name": project.provider_name,
        "model_name": project.model_name,
        "error_message": project.error_message,
        "result": project.result,
        "created_at": project.created_at.isoformat(),
    }


@router.post("/{project_id}/start")
async def start_project(
    project_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    project = await session.get(ProjectModel, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status == "running" and project_id in _running and not _running[project_id].done():
        raise HTTPException(status_code=409, detail="Project is already actively running")

    # Validate provider upfront
    try:
        provider = create_provider(project.provider_name, settings, model=project.model_name)
    except Exception as exc:
        err_msg = str(exc)
        project.status = "error"
        project.error_message = err_msg
        project.result = {"error": err_msg}
        await session.commit()
        await event_bus.emit(
            project_id,
            "project_failed",
            {"error": err_msg, "project_id": project_id},
        )
        raise HTTPException(status_code=400, detail=err_msg)

    project.status = "running"
    project.error_message = None
    await session.commit()

    orchestrator = Orchestrator(provider=provider)

    async def _run() -> None:
        try:
            result = await orchestrator.process_request(project_id, project.user_request)
            async with async_session() as s:
                p = await s.get(ProjectModel, project_id)
                if p:
                    p.status = "completed" if result.success else "error"
                    p.title = result.title
                    if not result.success:
                        failed = [f"{r.agent_name}: {r.error or 'Failed'}" for r in result.agent_results if not r.success]
                        p.error_message = "; ".join(failed) or "One or more tasks failed."
                    else:
                        p.error_message = None
                    p.result = {
                        "summary": result.summary,
                        "agents": [r.model_dump() for r in result.agent_results],
                    }
                    await s.commit()
        except Exception as exc:
            err_msg = str(exc)
            logger.error("Project %s execution failed: %s", project_id, err_msg, exc_info=True)
            async with async_session() as s:
                p = await s.get(ProjectModel, project_id)
                if p:
                    p.status = "error"
                    p.error_message = err_msg
                    p.result = {"error": err_msg}
                    await s.commit()
            await event_bus.emit(
                project_id,
                "project_failed",
                {"error": err_msg, "project_id": project_id},
            )

    task = asyncio.create_task(_run())
    _running[project_id] = task

    return {"status": "started", "project_id": project_id}


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    project = await session.get(ProjectModel, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project_id in _running:
        _running[project_id].cancel()
        del _running[project_id]
    await session.delete(project)
    await session.commit()
    return {"status": "deleted"}

