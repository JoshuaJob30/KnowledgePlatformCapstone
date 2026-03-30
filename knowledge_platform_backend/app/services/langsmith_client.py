# app/services/langsmith_client.py
from langsmith import Client
from app.core.config import settings
import os

# Initialize LangSmith client
langsmith_client = Client(api_key=settings.GROQ_API_KEY)
