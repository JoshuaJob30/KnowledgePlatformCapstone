import pytest
from app.services import vector_service

def test_vector_add_and_search():
    chunks = ["This is a test chunk about AI.", "Another chunk about RAG pipelines."]
    filename = "test_doc.txt"

    # Add chunks
    vector_service.add_document(chunks, filename)

    # Search
    results = vector_service.search_documents("AI", k=2)
    assert isinstance(results, list)
    assert len(results) > 0
    assert "text" in results[0]
