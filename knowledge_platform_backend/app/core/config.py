import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "/app/vector_store")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    MAX_CHUNKS: int = int(os.getenv("MAX_CHUNKS", 200))
    MODEL_ROUTER: str = os.getenv("MODEL_ROUTER", "llama-3.1-8b-instant")
    MODEL_PLANNER: str = os.getenv("MODEL_PLANNER", "llama-3.1-8b-instant")
    MODEL_ANSWER: str = os.getenv("MODEL_ANSWER", "llama-3.1-8b-instant")
    MODEL_CRITIC: str = os.getenv("MODEL_CRITIC", "llama-3.1-8b-instant")
    MODEL_EXTRACT: str = os.getenv("MODEL_EXTRACT", "llama-3.1-8b-instant")
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")

settings = Settings()

