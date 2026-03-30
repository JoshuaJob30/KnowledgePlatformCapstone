# app/services/crew.py
import logging
from langsmith import traceable
from app.services.agents_core import (
    planner_agent,
    retriever_agent,
    answer_agent,
    critic_agent,
    memory_agent,
)

logger = logging.getLogger(__name__)

class CrewRole:
    def __init__(self, name, func, async_mode=True):
        self.name = name
        self.func = func
        self.async_mode = async_mode

    async def run(self, *args, **kwargs):
        if self.async_mode:
            result = await self.func(*args, **kwargs)
        else:
            # synchronous function
            result = self.func(*args, **kwargs)
        logger.info(f"[{self.name}] Output: {result}")
        return result

# Define roles
Planner = CrewRole("Planner", planner_agent, async_mode=True)
Retriever = CrewRole("Retriever", retriever_agent, async_mode=False)
Executor = CrewRole("Executor", answer_agent, async_mode=True)
Critic = CrewRole("Critic", critic_agent, async_mode=True)
Memory = CrewRole("Memory", memory_agent, async_mode=False)

@traceable(name="AutoGenCrewOrchestrator")
async def orchestrate(question: str, route: str, max_rounds: int = 3) -> str:
    """
    AutoGen-style orchestration:
    Planner, Executor, and Critic exchange messages dynamically until Critic approves
    or max_rounds is reached.
    """
    if route != "rag_doc":
        logger.info(f"[Crew] Non-doc route, handled by MCP: {route}")
        return None

    # Step 1: Planner proposes subtasks
    steps = await Planner.run(question, route)
    logger.info(f"[Crew] Planner steps: {steps}")

    # Step 2: Retriever provides evidence
    evidence = await Retriever.run(question)

    # Step 3: Loop between Executor and Critic
    draft = None
    for round_num in range(1, max_rounds + 1):
        logger.info(f"[Crew] Round {round_num} starting.")

        # Executor drafts answer
        draft = await Executor.run(question, evidence)

        # Critic evaluates
        critique = await Critic.run(evidence, draft)
        logger.info(f"[Crew] Critic evaluation: {critique}")

        if not critique.get("needs_retry", False):
            logger.info("[Crew] Critic approved draft.")
            break
        else:
            logger.info("[Crew] Critic requested retry, looping again.")

    # Step 4: Memory stores final interaction
    await Memory.run(question, draft, evidence)

    return draft
