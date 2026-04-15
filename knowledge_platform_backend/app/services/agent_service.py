# app/services/agent_service.py
import re, asyncio
from langsmith import traceable
from app.core.logging import logger
from app.guardrails.guardrails import guardrail_check
from app.services.mcp import mcp_call, AGENT_REGISTRY
from app.services.crew import orchestrate
from app.services.groq_client import groq_client
from app.services import memory_service, vector_service
from sentence_transformers import SentenceTransformer, util

_router_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

ROUTES = {
    "finance": "Questions about stocks, currency exchange, or markets",
    "healthcare": "Questions about medical conditions, symptoms, or prevention",
    "shopping": "Questions about buying products, deals, or recommendations",
    "code": "Questions about programming, code errors, or software development",
    "search": "General information or factual queries",
    "rag_doc": "Questions requiring uploaded document context",
    "general": "Casual conversation, greetings, or small talk",
    "date": "Questions asking about today's date or calendar date",
    "time": "Questions asking about the current time or time in a location",
    "memory": "Questions asking what was said earlier or recalling past queries"
}

def router_agent(question: str) -> list[tuple[str,str]]:
    q = question.lower().strip()
    routes = []
    parts = re.split(r"\band also\b|\band\b|,|;", q)

    for part in parts:
        part = part.strip()
        if not part:
            continue
        try:
            matches = vector_service.search_documents(part, k=1)
            if matches:
                routes.append(("rag_doc", part))
                continue
        except Exception:
            pass

        if re.fullmatch(r"[0-9\+\-\*\/\.\(\)\s]+", part) \
           or re.search(r"\b\d+\s*(times|plus|minus|divided by|x)\s*\d+", part) \
           or re.search(r"\b(calculate|compute|solve)\b", part):
            routes.append(("calculator", part))
        elif "http://" in part or "https://" in part:
            routes.append(("search", part))
        elif re.search(r"\btime\b", part):
            routes.append(("time", part))
        elif re.search(r"\b(date|today's date)\b", part):
            routes.append(("date", part))
        elif re.search(r"\bwho\b|\bceo\b|\bpresident\b|\bfounder\b|\bmanager\b", part):
            routes.append(("search", part))
        elif re.search(r"\bhello\b|\bhi\b|\bhey\b|\bthanks\b|\bgood morning\b|\bgood evening\b", part):
            routes.append(("general", part))

    if not routes:
        embeddings = _router_model.encode([q] + list(ROUTES.values()))
        query_emb = embeddings[0]
        route_embs = embeddings[1:]
        scores = util.cos_sim(query_emb, route_embs)[0]
        best_idx = scores.argmax().item()
        routes.append((list(ROUTES.keys())[best_idx], q))

    return routes

@traceable(name="AnswerQueryPipeline")
async def answer_query(question: str) -> dict:
    try:
        memory_service.stm_add(f"Q: {question}")

        if guardrail_check(question):
            logger.warning("[Guardrails] Query blocked by policy.")
            return {"answer": "Query blocked by safety policy.", "source": "guardrail"}

        route_pairs = router_agent(question)
        answers, sources = [], []

        for route, clause in route_pairs:
            if route in AGENT_REGISTRY:
                result = await mcp_call(route, clause)
                if result:
                    answers.append(str(result))
                    sources.append(route)
                    continue

            if route == "rag_doc":
                result = await orchestrate(clause, route)
                draft = result.get("draft")
                evidence = result.get("evidence")

                # Normalize draft to string
                if asyncio.iscoroutine(draft):
                    draft = await draft
                if draft is None:
                    draft = ""
                draft = str(draft)

                # Guard evidence check
                if not evidence or (isinstance(evidence, str) and evidence.strip() == "No relevant context.") or not draft.strip():
                    system_prompt = "You are a helpful assistant. Answer clearly and concisely."
                    answer = await groq_client.chat(
                        "llama-3.1-8b-instant",
                        [{"role":"system","content":system_prompt},
                         {"role":"user","content":clause}],
                        temperature=0.2
                    )
                    answers.append(str(answer))
                    sources.append("llm")
                else:
                    answers.append(draft)
                    sources.append("rag_doc")
                continue

            if route == "general":
                system_prompt = "You are a friendly assistant. Respond naturally to casual conversation."
                answer = await groq_client.chat(
                    "llama-3.1-8b-instant",
                    [{"role":"system","content":system_prompt},
                     {"role":"user","content":clause}],
                    temperature=0.7
                )
                answers.append(str(answer))
                sources.append("llm")
                continue

            system_prompt = "You are a helpful assistant. Answer clearly and concisely."
            answer = await groq_client.chat(
                "llama-3.1-8b-instant",
                [{"role":"system","content":system_prompt},
                 {"role":"user","content":clause}],
                temperature=0.2
            )
            answers.append(str(answer))
            sources.append("llm")

        logger.info(f"[Pipeline] Answer types: {[type(a) for a in answers]}")

        # Final normalization
        safe_answers = []
        for a in answers:
            if asyncio.iscoroutine(a):
                result = await a
                safe_answers.append(str(result))
            else:
                safe_answers.append(str(a))

        return {"answer": "\n\n".join(safe_answers), "source": ", ".join(sources)}

    except Exception as e:
        logger.error(f"[Pipeline] Error: {e}")
        return {"answer": f"Error while answering query: {str(e)}", "source": "error"}
