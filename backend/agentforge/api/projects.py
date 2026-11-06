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


def sanitize_model_name(provider: str, model_name: str | None) -> str | None:
    """Clean up and normalize model names across providers."""
    if not model_name:
        return None
    m = model_name.strip().strip('"').strip("'")
    p = provider.lower().strip()
    if p == "gemini":
        if m.startswith("models/"):
            m = m[len("models/"):]
        if m.startswith("google/"):
            m = m[len("google/"):]
    elif p in ("openai", "custom", "openai-compatible"):
        if m.startswith("openai/"):
            m = m[len("openai/"):]
    elif p == "anthropic":
        if m.startswith("anthropic/"):
            m = m[len("anthropic/"):]
    elif p == "ollama":
        if m.startswith("ollama/"):
            m = m[len("ollama/"):]
    return m or None


class ProjectCreate(BaseModel):
    user_request: str
    provider: str = ""
    model: str = ""
    api_key: str = ""
    base_url: str = ""


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
    model_name = sanitize_model_name(provider_name, body.model)

    # Auto-save API key if provided in request
    if body.api_key and body.api_key.strip():
        key_val = body.api_key.strip()
        p_key = provider_name.lower()
        from agentforge.config import save_key_to_env
        if p_key == "gemini":
            settings.gemini_api_key = key_val
            save_key_to_env("GEMINI_API_KEY", key_val)
        elif p_key == "openai":
            settings.openai_api_key = key_val
            save_key_to_env("OPENAI_API_KEY", key_val)
        elif p_key == "anthropic":
            settings.anthropic_api_key = key_val
            save_key_to_env("ANTHROPIC_API_KEY", key_val)
        elif p_key in ("custom", "openai-compatible"):
            settings.custom_api_key = key_val
            save_key_to_env("CUSTOM_API_KEY", key_val)
            if body.base_url and body.base_url.strip():
                settings.custom_base_url = body.base_url.strip()
                save_key_to_env("CUSTOM_BASE_URL", body.base_url.strip())

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
        clean_model = sanitize_model_name(project.provider_name, project.model_name)
        provider = create_provider(project.provider_name, settings, model=clean_model)
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

