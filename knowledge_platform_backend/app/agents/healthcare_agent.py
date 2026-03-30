# app/agents/healthcare_agent.py
from app.core.logging import logger
from app.services.groq_client import groq_client

async def run(query: str) -> str:
    try:
        system_prompt = (
            "You are a factual assistant. Provide general healthcare information "
            "about medical conditions, symptoms, or prevention. Do not give personal advice."
        )
        return await groq_client.chat(
            "llama-3.1-8b-instant",
            [{"role":"system","content":system_prompt},
             {"role":"user","content":query}],
            temperature=0.2
        )
    except Exception as e:
        logger.error(f"[HealthcareAgent] Error: {e}")
        return "Error: could not process healthcare query."
