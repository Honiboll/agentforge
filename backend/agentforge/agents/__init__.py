"""Built-in agent types — auto-registered on import."""

from agentforge.agents.researcher import ResearcherAgent
from agentforge.agents.coder import CoderAgent
from agentforge.agents.reviewer import ReviewerAgent
from agentforge.agents.writer import WriterAgent
from agentforge.agents.planner import PlannerAgent
from agentforge.agents.custom import CustomAgent
from agentforge.core.agent_registry import registry

registry.register("researcher", ResearcherAgent)
registry.register("coder", CoderAgent)
registry.register("reviewer", ReviewerAgent)
registry.register("writer", WriterAgent)
registry.register("planner", PlannerAgent)
registry.register("custom", CustomAgent)

__all__ = [
    "ResearcherAgent",
    "CoderAgent",
    "ReviewerAgent",
    "WriterAgent",
    "PlannerAgent",
    "CustomAgent",
]

