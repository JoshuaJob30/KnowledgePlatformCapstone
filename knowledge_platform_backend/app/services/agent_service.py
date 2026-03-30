import re
from langsmith import traceable
from app.core.logging import logger
from app.guardrails.guardrails import guardrail_check
from app.services.mcp import mcp_call, AGENT_REGISTRY
from app.services.crew import orchestrate
from app.services.groq_client import groq_client

def router_agent(question: str) -> str:
    q = question.lower()
    if "http://" in q or "https://" in q:
        return "search"
    elif any(tok in q for tok in ["time", "current time"]):
        return "time"
    elif any(tok in q for tok in ["date", "today"]):
        return "date"
    elif re.fullmatch(r"[0-9\+\-\*\/\.\(\)\s]+", q or ""):
        return "calculator"
    elif any(tok in q for tok in ["symptom","disease","medical","health"]):
        return "healthcare"
    elif any(tok in q for tok in ["stock","price","market","currency"]):
        return "finance"
    elif any(tok in q for tok in ["buy","shop","product","deal"]):
        return "shopping"
    elif any(tok in q for tok in ["python","java","error","code","programming"]):
        return "code"
    else:
        return "rag_doc"

@traceable(name="AnswerQueryPipeline")
async def answer_query(question: str) -> dict:
    try:
        # 1. Guardrails
        if guardrail_check(question):
            logger.warning("[Guardrails] Query blocked by policy.")
            return {"answer": "Query blocked by safety policy.", "source": "guardrail"}

        # 2. Route
        route = router_agent(question)

        # 3. Agent path
        if route in AGENT_REGISTRY:
            result = await mcp_call(route, question)
            if result:
                return {"answer": result, "source": route}

        # 4. Document path
        if route == "rag_doc":
            draft = await orchestrate(question, route)
            return {"answer": draft, "source": "rag_doc"}

        # 5. General fallback → direct LLM
        system_prompt = "You are a helpful assistant. Answer clearly and concisely."
        answer = await groq_client.chat(
            "llama-3.1-8b-instant",
            [{"role":"system","content":system_prompt},
             {"role":"user","content":question}],
            temperature=0.2
        )
        return {"answer": answer, "source": "llm"}

    except Exception as e:
        logger.error(f"[Pipeline] Error: {e}")
        return {"answer": f"Error while answering query: {str(e)}", "source": "error"}
