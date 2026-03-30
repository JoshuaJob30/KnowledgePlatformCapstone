# app/services/ingestion_service.py
import os
from pypdf import PdfReader
from docx import Document
import docx2txt
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.logging import logger
from app.services import vector_service
from app.core.config import settings

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_file(filename: str, content: bytes) -> str:
    """Save uploaded file to disk."""
    filepath = os.path.join(UPLOAD_DIR, filename)
    try:
        with open(filepath, "wb") as f:
            f.write(content)
        logger.info(f"File saved: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error saving file {filename}: {e}")
        raise

def _extract_pdf(filepath: str) -> str:
    reader = PdfReader(filepath)
    text = " ".join([page.extract_text() or "" for page in reader.pages])
    return text.strip()

def _extract_docx(filepath: str) -> str:
    try:
        doc = Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    except Exception:
        return docx2txt.process(filepath).strip()

def _extract_csv(filepath: str) -> str:
    df = pd.read_csv(filepath)
    if len(df) > 200:
        df = df.head(200)
    return df.to_string(index=False)

def _extract_excel(filepath: str) -> str:
    excel = pd.ExcelFile(filepath)
    text_chunks = []
    for sheet in excel.sheet_names:
        df = excel.parse(sheet)
        if len(df) > 200:
            df = df.head(200)
        text_chunks.append(df.to_string(index=False))
    return "\n".join(text_chunks).strip()

def _extract_txt(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()

def extract_text(filepath: str) -> str:
    """Extract text from supported file formats."""
    try:
        if filepath.lower().endswith(".pdf"):
            return _extract_pdf(filepath)
        elif filepath.lower().endswith(".docx"):
            return _extract_docx(filepath)
        elif filepath.lower().endswith(".csv"):
            return _extract_csv(filepath)
        elif filepath.lower().endswith((".xls", ".xlsx")):
            return _extract_excel(filepath)
        else:
            return _extract_txt(filepath)
    except Exception as e:
        logger.error(f"Error extracting text from {filepath}: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100) -> list[str]:
    """Split text into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    docs = splitter.create_documents([text])
    return [doc.page_content for doc in docs]

def ingest_and_index(filepath: str, filename: str) -> int:
    text = extract_text(filepath)
    if not text:
        return 0

    chunks = chunk_text(text)

    # Enforce chunk limit from settings
    if len(chunks) > settings.MAX_CHUNKS:
        chunks = chunks[:settings.MAX_CHUNKS]

    vector_service.add_document(chunks, filename)
    return len(chunks)

