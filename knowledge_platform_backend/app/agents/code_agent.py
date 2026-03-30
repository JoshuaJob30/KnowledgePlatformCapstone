# app/agents/code_agent.py
from app.core.logging import logger
from app.services.groq_client import groq_client

async def run(query: str) -> str:
    try:
        system_prompt = (
            "You are a programming assistant. Explain code errors, provide fixes, "
            "and suggest best practices. Keep answers concise and clear."
        )
        return await groq_client.chat(
            "llama-3.1-8b-instant",
            [{"role":"system","content":system_prompt},
             {"role":"user","content":query}],
            temperature=0.2
        )
    except Exception as e:
        logger.error(f"[CodeAgent] Error: {e}")
        return "Error: could not process programming query."
