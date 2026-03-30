# app/agents/shopping_agent.py
from app.core.logging import logger
from app.services.groq_client import groq_client

async def run(query: str) -> str:
    try:
        system_prompt = (
            "You are a shopping assistant. Provide product recommendations, comparisons, "
            "and general shopping guidance. Be concise."
        )
        return await groq_client.chat(
            "llama-3.1-8b-instant",
            [{"role":"system","content":system_prompt},
             {"role":"user","content":query}],
            temperature=0.3
        )
    except Exception as e:
        logger.error(f"[ShoppingAgent] Error: {e}")
        return "Error: could not process shopping query."
