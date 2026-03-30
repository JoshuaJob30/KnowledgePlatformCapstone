# app/agents/finance_agent.py
from app.core.logging import logger
from app.services.groq_client import groq_client

async def run(query: str) -> str:
    try:
        system_prompt = (
            "You are a financial assistant. Provide factual, up-to-date information "
            "about stocks, currency exchange, or markets. Be concise."
        )
        return await groq_client.chat(
            "llama-3.1-8b-instant",
            [{"role":"system","content":system_prompt},
             {"role":"user","content":query}],
            temperature=0.2
        )
    except Exception as e:
        logger.error(f"[FinanceAgent] Error: {e}")
        return "Error: could not process finance query."
