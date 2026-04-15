# app/services/crew.py
import logging
import asyncio
from langsmith import traceable
from app.services.agents_core import (
    planner_agent,
    retriever_agent,
    answer_agent,
    critic_agent,
    memory_agent,   # async memory agent from agents_core
)

logger = logging.getLogger(__name__)

class CrewRole:
    def __init__(self, name, func, async_mode=True):
        self.name = name
        self.func = func
        self.async_mode = async_mode

    async def run(self, *args, **kwargs):
        if self.async_mode:
            return await self.func(*args, **kwargs)
        else:
            return self.func(*args, **kwargs)

# Define roles
Planner   = CrewRole("Planner", planner_agent, async_mode=True)
Retriever = CrewRole("Retriever", retriever_agent, async_mode=False)  # retriever is sync
Executor  = CrewRole("Executor", answer_agent, async_mode=True)
Critic    = CrewRole("Critic", critic_agent, async_mode=True)
Memory    = CrewRole("Memory", memory_agent, async_mode=True)  # async memory agent

@traceable(name="AutoGenCrewOrchestrator")
async def orchestrate(question: str, route: str, max_rounds: int = 3) -> dict:
    if route != "rag_doc":
        logger.info(f"[Crew] Non-doc route, handled by MCP: {route}")
        return {"draft": None, "evidence": None, "critique": {}}

    steps = await Planner.run(question, route)
    logger.info(f"[Crew] Planner steps: {steps}")

    # Retriever is sync → no await
    evidence = Retriever.run(question)

    # Normalize evidence immediately
    if evidence is None:
        evidence = ""
    elif asyncio.iscoroutine(evidence):
        evidence = await evidence
    evidence = str(evidence)

    draft = None
    critique = {}
    for round_num in range(1, max_rounds + 1):
        draft = await Executor.run(question, evidence)
        critique = await Critic.run(evidence, draft)
        logger.info(f"[Crew] Critic evaluation: {critique}")
        if not critique.get("needs_retry", False):
            break

    # Normalize draft
    if draft is None:
        draft = ""
    elif asyncio.iscoroutine(draft):
        draft = await draft
    draft = str(draft)

    # Call async memory agent
    await Memory.run(question, draft, evidence)

    return {
        "draft": draft,
        "evidence": evidence,
        "critique": critique
    }
