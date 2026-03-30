import httpx, time
from app.core.config import settings
from app.core.logging import logger

class GroqClient:
    def __init__(self, base_url="https://api.groq.com/openai/v1", timeout=30.0, max_retries=4, backoff_base=2.0):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_base = backoff_base

    async def chat(self, model: str, messages, temperature: float = 0.0) -> str:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        last_err = None
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    r = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=self.timeout
                    )
                    r.raise_for_status()
                    return r.json()["choices"][0]["message"]["content"].strip()
            except Exception as e:
                last_err = e
                logger.warning(f"GROQ retry {attempt}: {e}")
                time.sleep(self.backoff_base ** attempt)
        raise last_err

groq_client = GroqClient()
