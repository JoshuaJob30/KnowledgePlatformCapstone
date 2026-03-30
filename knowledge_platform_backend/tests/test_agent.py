import pytest
import asyncio
from app.services.agent_service import answer_query

@pytest.mark.asyncio
async def test_agent_pipeline_general_query():
    question = "What is 2 + 2?"
    answer = await answer_query(question)
    assert "4" in answer or "four" in answer.lower()

@pytest.mark.asyncio
async def test_agent_pipeline_doc_query():
    # This assumes ingestion + vector store already has sample docs loaded
    question = "Summarize the sample document."
    answer = await answer_query(question)
    assert isinstance(answer, str)
    assert len(answer) > 0
