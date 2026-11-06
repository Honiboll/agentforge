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
from agentforge.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])

# In-memory store for running orchestrations
_running: dict[str, asyncio.Task[Any]] = {}


class ProjectCreate(BaseModel):
    user_request: str
    provider: str = ""


class ProjectOut(BaseModel):
    id: str
    title: str
    user_request: str
    status: str
    provider_name: str
    created_at: str


@router.post("/", response_model=ProjectOut)
async def create_project(
    body: ProjectCreate,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    project_id = uuid.uuid4().hex
    provider_name = body.provider or settings.default_llm_provider
    project = ProjectModel(
        id=project_id,
        user_request=body.user_request,
        provider_name=provider_name,
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
    if project.status == "running":
        raise HTTPException(status_code=409, detail="Project already running")

    project.status = "running"
    await session.commit()

    provider = create_provider(project.provider_name, settings)
    orchestrator = Orchestrator(provider=provider)

    async def _run() -> None:
        try:
            result = await orchestrator.process_request(project_id, project.user_request)
            async with async_session() as s:
                p = await s.get(ProjectModel, project_id)
                if p:
                    p.status = "completed" if result.success else "error"
                    p.title = result.title
                    p.result = {
                        "summary": result.summary,
                        "agents": [r.model_dump() for r in result.agent_results],
                    }
                    await s.commit()
        except Exception as exc:
            logger.error("Project %s execution failed: %s", project_id, exc, exc_info=True)
            async with async_session() as s:
                p = await s.get(ProjectModel, project_id)
                if p:
                    p.status = "error"
                    p.result = {"error": "Execution failed. Check backend logs for details."}
                    await s.commit()

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

