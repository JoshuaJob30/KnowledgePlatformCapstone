import os
import pytest
from app.services import ingestion_service

TEST_DIR = "tests/sample_files"

@pytest.mark.parametrize("filename", [
    "sample.pdf",
    "sample.docx",
    "sample.csv",
    "sample.xlsx",
    "sample.txt"
])
def test_ingestion_extract_and_chunk(filename):
    filepath = os.path.join(TEST_DIR, filename)
    text = ingestion_service.extract_text(filepath)
    assert text, f"Failed to extract text from {filename}"

    chunks = ingestion_service.chunk_text(text)
    assert isinstance(chunks, list)
    assert len(chunks) > 0, f"No chunks generated for {filename}"
