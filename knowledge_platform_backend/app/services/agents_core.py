# app/services/agents_core.py
import re, json
from langsmith import traceable
from app.services.groq_client import groq_client
from app.services import vector_service, memory_service
from app.core.config import settings
from app.core.logging import logger
from app.services.vector_service import cached_search

# Planner Agent
@traceable(name="PlannerAgent")
async def planner_agent(question: str, route: str) -> list[str]:
    if route != "rag_doc":
        logger.info(f"[Planner] Non-doc route, forced plan: {route}")
        return [route]
    prompt = (
        "Decompose the user's question into 1-3 subtasks.\n"
        "Allowed labels: 'rag_doc','rag_global','calculator','search','time','date','general'.\n"
        "Return ONLY JSON: {\"steps\": [\"...\"]}"
    )
    try:
        raw = await groq_client.chat(
            settings.MODEL_PLANNER,
            [{"role":"system","content":prompt},{"role":"user","content":question}],
            temperature=0.0
        )
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            logger.error("[Planner] No JSON object found in response.")
            return [route]
        obj = json.loads(match.group(0))
        steps = obj.get("steps", [])
        logger.info(f"[Planner] Steps: {steps}")
        return steps or [route]
    except Exception as e:
        logger.error(f"[Planner] Error parsing steps: {e}")
        return [route]

# Retriever Agent
def retriever_agent(question: str, k: int = 5) -> str:
    try:
        docs = cached_search(question, k=k)
        if not docs:
            logger.warning("[Retriever] No relevant context found.")
            return "No relevant context."
        logger.info(f"[Retriever] Retrieved {len(docs)} chunks.")
        return "\n\n".join([f"[doc-{i}] {doc['text']}" for i, doc in enumerate(docs)])
    except Exception as e:
        logger.error(f"[Retriever] Error: {e}")
        return "No relevant context."

# Answer Agent
@traceable(name="AnswerAgent")
async def answer_agent(question: str, evidence: str) -> str:
    system_prompt = (
        "You are a precise, grounded assistant. Use EVIDENCE strictly when present; "
        "do not invent facts. Summarize clearly and concisely."
    )
    user_prompt = f"Question: {question}\n\nEVIDENCE:\n{evidence}"
    try:
        answer = await groq_client.chat(
            settings.MODEL_ANSWER,
            [{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}],
            temperature=0.2
        )
        logger.info(f"[Answer] Draft generated. Length={len(answer)} chars.")
        return answer
    except Exception as e:
        logger.error(f"[Answer] Error: {e}")
        return "Error generating answer."

# Critic Agent
@traceable(name="CriticAgent")
async def critic_agent(evidence: str, draft: str) -> dict:
    prompt = (
        "Evaluate the DRAFT using EVIDENCE.\n"
        "Return JSON: {\"grounding\": 0-1, \"conciseness\": 0-1, \"needs_retry\": true/false}"
    )
    try:
        raw = await groq_client.chat(
            settings.MODEL_CRITIC,
            [{"role":"system","content":prompt},
             {"role":"user","content":f"EVIDENCE:\n{evidence}\n\nDRAFT:\n{draft}"}],
            temperature=0.0
        )
        obj = json.loads(re.search(r"\{.*\}", raw, re.DOTALL).group(0))
        logger.info(f"[Critic] Scores: grounding={obj.get('grounding')}, conciseness={obj.get('conciseness')}, retry={obj.get('needs_retry')}")
        return obj
    except Exception as e:
        logger.error(f"[Critic] Error: {e}")
        return {"grounding":1.0,"conciseness":1.0,"needs_retry":False}

@traceable(name="MemoryAgent")
async def memory_agent(question: str, answer: str, evidence: str) -> str:
    try:
        memory_service.stm_add(f"Q: {question}")
        memory_service.stm_add(f"A: {answer}")
        memory_service.epi_add(f"Interaction: {question} -> {answer}")
        memory_service.ltm_add_facts([f"Fact: {answer}"])
        logger.info("[Memory] Facts and episodes stored successfully.")
        return "Memory stored successfully."
    except Exception as e:
        logger.error(f"[Memory] Error storing memory: {e}")
        return f"Error storing memory: {e}"
