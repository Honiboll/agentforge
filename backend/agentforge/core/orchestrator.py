"""Orchestrator — coordinates the full pipeline from request to result."""

from __future__ import annotations

import asyncio
from typing import Any

from pydantic import BaseModel, Field

from agentforge.core.agent_factory import AgentFactory
from agentforge.core.analyzer import AnalysisPlan, TaskAnalyzer
from agentforge.core.base_agent import AgentResult, BaseAgent
from agentforge.config import settings
from agentforge.providers.base import BaseLLMProvider
from agentforge.providers.provider_factory import create_provider
from agentforge.utils.events import event_bus
from agentforge.utils.logger import get_logger

logger = get_logger(__name__)


class ProjectResult(BaseModel):
    project_id: str
    title: str
    summary: str
    agent_results: list[AgentResult] = Field(default_factory=list)
    success: bool = True


class Orchestrator:
    """Receives a user request, analyses it, creates agents, and runs them."""

    def __init__(self, provider: BaseLLMProvider | None = None) -> None:
        self.provider = provider or create_provider(settings.default_llm_provider, settings)
        self.analyzer = TaskAnalyzer(self.provider)
        self.factory = AgentFactory()

    async def process_request(self, project_id: str, user_request: str) -> ProjectResult:
        await event_bus.emit(project_id, "project_started", {"request": user_request[:200]})

        # 1. Analyze
        try:
            plan: AnalysisPlan = await self.analyzer.analyze(user_request, project_id)
        except Exception as exc:
            err_msg = str(exc)
            logger.error("Analysis failed for project %s: %s", project_id, err_msg)
            await event_bus.emit(
                project_id,
                "project_failed",
                {"error": f"Analysis failed: {err_msg}", "phase": "analysis"},
            )
            raise

        # 2. Create agents
        try:
            agents = await self.factory.create_agents_from_plan(plan, self.provider, project_id)
        except Exception as exc:
            err_msg = str(exc)
            logger.error("Agent creation failed for project %s: %s", project_id, err_msg)
            await event_bus.emit(
                project_id,
                "project_failed",
                {"error": f"Agent creation failed: {err_msg}", "phase": "factory"},
            )
            raise

        # 3. Run agents respecting dependencies
        results = await self._run_agents(agents, plan, project_id)

        all_success = all(r.success for r in results)
        if not all_success:
            failed_agents = [f"{r.agent_name}: {r.error or 'Task failed'}" for r in results if not r.success]
            err_summary = "; ".join(failed_agents)
            await event_bus.emit(
                project_id,
                "project_failed",
                {"error": f"Execution failed in one or more agents: {err_summary}", "title": plan.project_title},
            )
        else:
            await event_bus.emit(project_id, "project_completed", {"title": plan.project_title})

        return ProjectResult(
            project_id=project_id,
            title=plan.project_title,
            summary=plan.summary,
            agent_results=results,
            success=all_success,
        )

    # ------------------------------------------------------------------

    async def _run_agents(
        self,
        agents: list[BaseAgent],
        plan: AnalysisPlan,
        project_id: str,
    ) -> list[AgentResult]:
        results: list[AgentResult | None] = [None] * len(agents)
        completed: set[int] = set()

        sem = asyncio.Semaphore(settings.max_concurrent_agents)

        async def _run_one(index: int) -> None:
            task_spec = plan.tasks[index]

            # Wait for dependencies
            while not all(d in completed for d in task_spec.dependencies):
                await asyncio.sleep(0.3)

            # Build context from dependency results
            context: dict[str, Any] = {}
            for dep_idx in task_spec.dependencies:
                dep_result = results[dep_idx]
                if dep_result:
                    context[f"dep_{dep_idx}_{plan.tasks[dep_idx].name}"] = dep_result.output

            async with sem:
                await event_bus.emit(
                    project_id,
                    "task_started",
                    {"agent_id": agents[index].id, "task": task_spec.name},
                )
                result = await agents[index].run(task_spec.description, context)
                results[index] = result
                completed.add(index)
                await event_bus.emit(
                    project_id,
                    "task_completed",
                    {"agent_id": agents[index].id, "task": task_spec.name, "success": result.success},
                )

        await asyncio.gather(*[_run_one(i) for i in range(len(agents))])
        return [r for r in results if r is not None]

