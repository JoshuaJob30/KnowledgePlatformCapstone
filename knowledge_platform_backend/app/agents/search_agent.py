# app/agents/search_agent.py
from app.services.groq_client import groq_client
from app.core.logging import logger

async def run(query: str) -> str:
    try:
        system_prompt = "You are a helpful assistant. Answer clearly and concisely."
        return await groq_client.chat(
            "llama-3.1-8b-instant",
            [{"role":"system","content":system_prompt},
             {"role":"user","content":query}],
            temperature=0.2
        )
    except Exception as e:
        logger.error(f"[SearchAgent] Error: {e}")
        return "Error: could not process search query."
